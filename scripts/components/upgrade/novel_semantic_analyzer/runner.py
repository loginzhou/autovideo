import os
import json
import re
import time
from components.utils.llm_client import get_llm_response

def run_novel_semantic_analyzer(novel_path):
    """
    全量小说语义深度分析引擎 V2.0 优化版（基于Gemini高效处理逻辑）
    采用"全局设定+滚动总结+当前分块"策略，避免上下文溢出和超时
    """
    print("="*60)
    print("📚 全量小说语义分析引擎启动（Gemini优化版）")
    print("✅ 采用滚动摘要+1万字分块策略，避免超时和中间遗忘效应")
    print("="*60)
    
    # 1. 读取完整小说
    with open(novel_path, 'r', encoding='utf-8') as f:
        full_content = f.read()
    
    total_length = len(full_content)
    print(f"✅ 读取小说完成，总字数：{total_length//2} 字")
    
    # 2. 分块处理（1万汉字/块≈2万字符，符合8000-15000token最优区间）
    chunk_size = 20000  # 1万汉字约2万字符，适配大模型最优输入长度
    overlap = int(chunk_size * 0.05)
    chunks = []
    for i in range(0, total_length, chunk_size - overlap):
        chunk = full_content[i:i+chunk_size]
        chunks.append(chunk)
    print(f"✅ 小说分块完成，共 {len(chunks)} 个分析块（单块最大1万汉字，最优token区间）")
    
    # 3. Prompt模板
    # 基础分析Prompt
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
    
    for idx, chunk in enumerate(chunks):
        print(f"🔍 正在分析第 {idx+1}/{len(chunks)} 块...")
        # 构造当前prompt，带上前情提要
        prompt = analyze_prompt.replace("{{prev_summary}}", prev_summary).replace("{{chunk_content}}", chunk)
        # 调用LLM，max_tokens设为4000，确保输出完整
        response = get_llm_response(prompt, temperature=0.1, max_tokens=4000)
        try:
            chunk_result = json.loads(response)
            all_results.append(chunk_result)
            # 更新滚动摘要，供下一块使用
            prev_summary = chunk_result.get("summary", "无摘要")
            print(f"✅ 第{idx+1}块分析完成，摘要：{prev_summary[:50]}...")
        except Exception as e:
            print(f"⚠️  第{idx+1}块解析失败，跳过：{str(e)}，原始返回：{response[:100]}...")
            continue
    
    # 5. 合并所有分块结果，智能去重整合（避免重复内容）
    print("🔄 正在整合全量分析结果...")
    if not all_results:
        # 所有块都失败，直接抛出异常，禁止fallback
        raise Exception("❌ 所有小说分析块调用API失败，无有效分析结果，请检查API配置后重试")
    
    final_result = {
        "genre": all_results[0]['genre'],
        "core_theme": all_results[0]['core_theme'],
        "main_plot_outline": "",
        "key_turning_points": [],
        "climax_distribution": [],
        "characters": [],
        "story_rules": all_results[0]['story_rules'],
        "recommended_episode_count": all_results[0]['recommended_episode_count'],
        "rhythm_suggestion": all_results[0]['rhythm_suggestion']
    }
    
    # 合并剧情脉络（智能去重，保留不重复内容）
    seen_plot_content = set()
    for res in all_results:
        plot_lines = res['main_plot_outline'].split("\n")
        for line in plot_lines:
            line = line.strip()
            if line and line[:50] not in seen_plot_content:
                seen_plot_content.add(line[:50])
                final_result['main_plot_outline'] += line + "\n"
    
    # 合并角色（去重）
    char_map = {}
    for res in all_results:
        for char in res['characters']:
            if char['name'] not in char_map:
                char_map[char['name']] = char
            else:
                # 合并信息
                existing = char_map[char['name']]
                existing['visual_traits'] = list(set(existing['visual_traits'] + char['visual_traits']))
                if len(char['character_arc']) > len(existing['character_arc']):
                    existing['character_arc'] = char['character_arc']
    final_result['characters'] = list(char_map.values())
    
    # 合并转折点和高潮
    seen_points = set()
    for res in all_results:
        for point in res['key_turning_points']:
            key = point['content'][:50]
            if key not in seen_points:
                seen_points.add(key)
                final_result['key_turning_points'].append(point)
        for climax in res['climax_distribution']:
            key = climax['content'][:50]
            if key not in seen_points:
                seen_points.add(key)
                final_result['climax_distribution'].append(climax)
    
    # 保存分析结果
    os.makedirs("output/analysis", exist_ok=True)
    with open("output/analysis/full_novel_analysis.json", 'w', encoding='utf-8-sig') as f:
        json.dump(final_result, f, ensure_ascii=False, indent=2)
    
    print("✅ 全量小说语义分析完成！结果已保存到 output/analysis/full_novel_analysis.json")
    print(f"📊 识别结果：题材={final_result['genre']}，推荐集数={final_result['recommended_episode_count']}，核心角色={len(final_result['characters'])}个")
    print("="*60)
    
    # 生成连贯性状态机
    final_result["continuity_state_machine"] = {
        "current_time": "第一章开头",
        "current_weather": "正常",
        "current_location": final_result["story_rules"].get("world_setting", "未知世界"),
        "seen_characters": [c["name"] for c in final_result["characters"]]
    }
    
    return final_result
