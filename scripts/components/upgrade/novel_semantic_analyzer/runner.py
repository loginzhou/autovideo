import os
import json
import re
import time
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response
from components.utils.state_manager import pipeline_state

def run_novel_semantic_analyzer(novel_path):
    """
    全量小说语义深度分析引擎 V2.0 优化版（基于Gemini高效处理逻辑）
    采用"全局设定+滚动总结+当前分块"策略，避免上下文溢出和超时
    新增缓存机制、结果校验、自动重试，提升准确率和稳定性
    """
    print("="*60)
    print("全量小说语义分析引擎启动（优化版）")
    print("采用滚动摘要+1万字分块策略，避免超时和中间遗忘效应")
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
    
    # 1. 读取完整小说
    with open(novel_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    total_length = len(full_content)
    print(f"读取小说完成，总字数：{total_length//2} 字")
    
    # 2. 分块处理，参数从配置中心读取
    chunk_size_char = config.get("semantic_analysis.chunk_size_char", 20000)  # 1万汉字约2万字符
    overlap_ratio = config.get("semantic_analysis.overlap_ratio", 0.05)
    overlap = int(chunk_size_char * overlap_ratio)
    max_retries = config.get("semantic_analysis.max_retries", 2)
    
    chunks = []
    for i in range(0, total_length, chunk_size_char - overlap):
        chunk = full_content[i:i+chunk_size_char]
        chunks.append(chunk)
    print(f"小说分块完成，共 {len(chunks)} 个分析块（单块最大{chunk_size_char//2}汉字，最优token区间）")
    
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
        print(f"正在分析第 {idx+1}/{len(chunks)} 块...")
        # 构造当前prompt，带上前情提要
        prompt = analyze_prompt.replace("{{prev_summary}}", prev_summary).replace("{{chunk_content}}", chunk)
        
        # 重试机制
        chunk_result = None
        for retry in range(max_retries + 1):
            try:
                # 调用LLM，max_tokens设为4000，确保输出完整
                response = get_llm_response(prompt, model=model, temperature=temperature, max_tokens=4000)
                # 尝试解析JSON
                chunk_result = json.loads(response)
                # 校验必要字段是否存在
                required_fields = ["genre", "summary", "characters", "story_rules"]
                for field in required_fields:
                    if field not in chunk_result:
                        raise ValueError(f"缺少必要字段：{field}")
                break
            except Exception as e:
                if retry < max_retries:
                    print(f"第{idx+1}块分析失败，第{retry+1}次重试：{str(e)}")
                    time.sleep(1)
                else:
                    print(f"第{idx+1}块分析失败，已重试{max_retries}次，跳过本块")
                    continue
        
        if chunk_result:
            all_results.append(chunk_result)
            # 更新滚动摘要，供下一块使用
            prev_summary = chunk_result.get("summary", "无摘要")
            print(f"第{idx+1}块分析完成，摘要：{prev_summary[:50]}...")
    
    # 5. 合并所有分块结果，智能去重整合（避免重复内容）
    print("正在整合全量分析结果...")
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
                # 合并信息
                existing = char_map[char_name]
                existing['visual_traits'] = list(set(existing.get('visual_traits', []) + char.get('visual_traits', [])))
                if not existing.get('character_arc', ''):
                    existing['character_arc'] = char.get('character_arc', '')
                if not existing.get('voice_type', ''):
                    existing['voice_type'] = char.get('voice_type', '中性')
    final_result['characters'] = list(char_map.values())
    
    # 推荐集数取所有块的平均值
    ep_counts = [res.get("recommended_episode_count", 30) for res in all_results if res.get("recommended_episode_count", 0) > 0]
    if ep_counts:
        final_result['recommended_episode_count'] = int(sum(ep_counts) / len(ep_counts))
    
    # 保存缓存
    if cache_enabled:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(final_result, f, ensure_ascii=False, indent=2)
        print(f"语义分析结果已缓存到：{cache_path}")
    
    # 人工审核语义分析结果
    from components.utils.human_review_manager import human_review
    if human_review.request_review("semantic_analysis", final_result):
        print("语义分析结果审核通过")
        return final_result
    else:
        # 审核被驳回，从状态中删除，下次重新分析
        pipeline_state.mark_stage_completed("semantic_analysis", None)
        raise Exception("语义分析结果审核被驳回，终止执行")
