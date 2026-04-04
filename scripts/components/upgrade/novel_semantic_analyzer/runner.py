import os
import json
import re
import time
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response
from components.utils.state_manager import pipeline_state
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker

def run_novel_semantic_analyzer(novel_path):
    """
    全量小说语义深度分析引擎 V2.1 - 智能切块优化版
    采用"全局设定+滚动总结+当前分块"策略，避免上下文溢出和超时
    复用小说切块器，保证章节边界和语义连贯性
    新增缓存机制、结果校验、自动重试，提升准确率和稳定性
    """
    print("="*60)
    print("全量小说语义分析引擎启动（智能切块优化版）")
    print("采用章节感知切块 + 滚动摘要策略，避免超时和中间遗忘效应")
    print("="*60)
    
    # 先检查缓存：同一本小说不需要重复分析
    cache_enabled = config.get("semantic_analysis.cache_enabled", True)
    if cache_enabled:
        # 计算小说文件的哈希值作为缓存key
        hasher = hashlib.md5()
        with open(novel_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        file_hash = hasher.hexdigest()
        cache_path = os.path.join("output/cache", f"semantic_analysis_{file_hash}.json")
        os.makedirs("output/cache", exist_ok=True)
        
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            print(f"检测到当前小说已分析过，从缓存加载结果：{cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_result = json.load(f)
            return cached_result
    
    # 1. 读取完整小说并计算哈希
    with open(novel_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    total_length = len(full_content)
    print(f"读取小说完成，总字数：{total_length//2} 字")
    
    # 2. 分块处理，优先复用小说切块逻辑，保证章节边界和语义连贯性
    chunk_size_char = config.get("semantic_analysis.chunk_size_char", 10000)  # 1万汉字约2万字符
    overlap_ratio = config.get("semantic_analysis.overlap_ratio", 0.05)
    max_retries = config.get("semantic_analysis.max_retries", 2)
    
    # 将字符数转换为KB（假设1汉字=2字节）
    semantic_chunk_size_kb = max(10, int(chunk_size_char * 2 / 1024))
    
    print(f"\n>>> 开始智能切块（复用小说切块器）...")
    print(f"    目标块大小：{chunk_size_char} 字符（约{semantic_chunk_size_kb}KB）")
    print(f"    重叠率：{overlap_ratio*100}%")
    
    semantic_chunks = novel_sliding_window_chunker(
        novel_path, 
        chunk_size_kb=semantic_chunk_size_kb, 
        overlap_ratio=overlap_ratio
    )
    
    if semantic_chunks:
        chunks = [chunk_obj["content"] for chunk_obj in semantic_chunks]
        # 打印切块统计信息
        chapter_chunks = sum(1 for c in semantic_chunks if c.get("contains_chapter", False))
        print(f"\n>>> 切块完成统计：")
        print(f"    总块数：{len(chunks)}")
        print(f"    包含章节边界的块：{chapter_chunks}")
        print(f"    平均每块字数：{sum(len(c) for c in chunks)//len(chunks)//2}")
    else:
        # 退回到简单文本切分，避免空块失败
        print(f"\n⚠️  警告：智能切块失败，退回到简单文本切分")
        overlap = int(chunk_size_char * overlap_ratio)
        chunks = [full_content[i:i+chunk_size_char] for i in range(0, total_length, chunk_size_char - overlap)]
        print(f"    简单切分共 {len(chunks)} 个块")
    
    print(f"\n>>> 开始语义分析...")
    
    # 3. Prompt模板
    analyze_prompt = """
严格按照要求输出：只返回JSON格式内容，不要任何解释、说明、markdown标记，不要用```包裹，不要任何额外文字，直接输出JSON。
【前情提要】：{{prev_summary}}
【当前小说内容】：{{chunk_content}}
分析内容输出以下结构的JSON：
{"genre":"类型","core_theme":"主题","summary":"本块内容200字以内摘要","main_plot_outline":"当前块剧情脉络","key_turning_points":[{"chapter":"位置","content":"内容","impact":"影响"}],"climax_distribution":[{"position":"百分比","content":"内容"}],"characters":[{"name":"名字","identity":"身份","personality":"性格","visual_traits":[],"character_arc":"成长","importance":"核心/主要/次要","voice_type":"声音类型"}],"story_rules":{"power_system":"","world_setting":"","common_sense":""},"recommended_episode_count":98,"rhythm_suggestion":""}
    """
    
    # 4. 分块分析并合并结果（滚动摘要模式）
    all_results = []
    prev_summary = "无，这是小说开头部分"  # 滚动摘要，每次处理完更新
    model = config.get("semantic_analysis.model", "deepseek-ai/DeepSeek-V3.2")
    temperature = config.get("semantic_analysis.temperature", 0.1)
    
    for idx, chunk in enumerate(chunks):
        chunk_start_time = time.time()
        print(f"\n正在分析第 {idx+1}/{len(chunks)} 块...")
        print(f"    块大小：{len(chunk)//2} 字")
        print(f"    开始时间：{time.strftime('%H:%M:%S', time.localtime(chunk_start_time))}")
        
        # 构造当前prompt，带上前情提要
        prompt = analyze_prompt.replace("{{prev_summary}}", prev_summary).replace("{{chunk_content}}", chunk)
        
        # 重试机制
        chunk_result = None
        for retry in range(max_retries + 1):
            try:
                # 调用LLM，max_tokens设为4000，确保输出完整
                print(f"    调用LLM，模型：{model}，温度：{temperature}")
                response = get_llm_response(
                    prompt, 
                    model=model, 
                    temperature=temperature, 
                    max_tokens=4000, 
                    response_format="json",
                    task_type="semantic_analysis"
                )
                print(f"    LLM调用成功，响应长度：{len(response)} 字符")
                
                # 尝试解析JSON
                chunk_result = json.loads(response)
                
                # 校验必要字段是否存在
                required_fields = ["genre", "summary", "characters", "story_rules"]
                for field in required_fields:
                    if field not in chunk_result:
                        raise ValueError(f"缺少必要字段：{field}")
                
                print(f"    ✓ 第{idx+1}块分析成功")
                break
                
            except Exception as e:
                if retry < max_retries:
                    print(f"    ✗ 第{idx+1}块分析失败，第{retry+1}次重试：{str(e)}")
                    time.sleep(1)
                else:
                    print(f"    ✗ 第{idx+1}块分析失败，已重试{max_retries}次，跳过本块：{str(e)}")
                    continue
        
        if chunk_result:
            all_results.append(chunk_result)
            # 更新滚动摘要，供下一块使用
            prev_summary = chunk_result.get("summary", "无摘要")
            print(f"    摘要：{prev_summary[:50]}...")
        
        # 显示进度和预估时间
        elapsed = time.time() - chunk_start_time
        progress = (idx + 1) / len(chunks) * 100
        remaining_chunks = len(chunks) - (idx + 1)
        if remaining_chunks > 0:
            estimated_remaining = elapsed * remaining_chunks
            print(f"    进度：{progress:.1f}% | 预估剩余时间：{estimated_remaining//60:.0f}分{estimated_remaining%60:.0f}秒")
    
    # 5. 合并所有分块结果，智能去重整合（避免重复内容）
    print("\n" + "="*60)
    print("正在整合全量分析结果...")
    print("="*60)
    
    if not all_results:
        # 所有块都失败，直接抛出异常，禁止fallback
        raise Exception("所有小说分析块调用API失败，无有效分析结果，请检查API配置后重试")
    
    final_result = {
        "genre": all_results[0].get("genre", "未知"),
        "core_theme": all_results[0].get("core_theme", "未知"),
        "main_plot_outline": "",
        "key_turning_points": [],
        "climax_distribution": [],
        "characters": [],
        "story_rules": all_results[0].get("story_rules", {}),
        "recommended_episode_count": all_results[0].get("recommended_episode_count", 30),
        "rhythm_suggestion": all_results[0].get("rhythm_suggestion", "")
    }
    
    # 合并剧情脉络（智能去重，保留不重复内容）
    seen_plot_content = set()
    for res in all_results:
        plot_lines = res.get("main_plot_outline", "").split("\n")
        for line in plot_lines:
            line = line.strip()
            if line and line[:50] not in seen_plot_content:
                seen_plot_content.add(line[:50])
                final_result['main_plot_outline'] += line + "\n"
    
    # 合并转折点
    seen_turning_points = set()
    for res in all_results:
        for tp in res.get("key_turning_points", []):
            tp_key = tp.get("content", "")[:50]
            if tp_key and tp_key not in seen_turning_points:
                seen_turning_points.add(tp_key)
                final_result['key_turning_points'].append(tp)
    
    # 合并高潮点
    seen_climax = set()
    for res in all_results:
        for climax in res.get("climax_distribution", []):
            climax_key = climax.get("content", "")[:50]
            if climax_key and climax_key not in seen_climax:
                seen_climax.add(climax_key)
                final_result['climax_distribution'].append(climax)
    
    # 合并角色（去重）
    char_map = {}
    for res in all_results:
        for char in res.get("characters", []):
            char_name = char.get("name", "")
            if not char_name:
                continue
            if char_name not in char_map:
                char_map[char_name] = char
            else:
                # 合并信息 - 添加类型检查防止转换错误
                existing = char_map[char_name]
                # 安全地合并visual_traits，只处理列表类型的元素
                existing_traits = existing.get('visual_traits', [])
                new_traits = char.get('visual_traits', [])
                if isinstance(existing_traits, list) and isinstance(new_traits, list):
                    merged_traits = [t for t in existing_traits + new_traits if isinstance(t, str)]
                    existing['visual_traits'] = list(dict.fromkeys(merged_traits))  # 保持顺序去重
                if not existing.get('character_arc', ''):
                    existing['character_arc'] = char.get('character_arc', '')
                if not existing.get('voice_type', ''):
                    existing['voice_type'] = char.get('voice_type', '中性')
    final_result['characters'] = list(char_map.values())
    
    # 推荐集数取所有块的平均值
    ep_counts = [res.get("recommended_episode_count", 30) for res in all_results if res.get("recommended_episode_count", 0) > 0]
    if ep_counts:
        final_result['recommended_episode_count'] = int(sum(ep_counts) / len(ep_counts))
    
    print(f"\n>>> 整合完成：")
    print(f"    成功分析块数：{len(all_results)}/{len(chunks)}")
    print(f"    识别角色数：{len(final_result['characters'])}")
    print(f"    识别转折点：{len(final_result['key_turning_points'])}")
    print(f"    推荐集数：{final_result['recommended_episode_count']}")
    
    # 保存缓存
    if cache_enabled:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        print(f"\n>>> 语义分析结果已缓存到：{cache_path}")
    
    # 人工审核语义分析结果
    from components.utils.human_review_manager import human_review
    if human_review.request_review("semantic_analysis", final_result):
        print("\n✓ 语义分析结果审核通过")
        return final_result
    else:
        # 审核被驳回，从状态中删除，下次重新分析
        pipeline_state.mark_stage_completed("semantic_analysis", None)
        raise Exception("语义分析结果审核被驳回，终止执行")
