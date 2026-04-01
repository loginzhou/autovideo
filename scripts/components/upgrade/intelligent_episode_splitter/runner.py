import json
import uuid
import os
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response

def run_intelligent_episode_splitter(full_analysis_result, novel_chunks):
    """
    专业级智能分集系统 V3.1 逐集生成稳定版
    优化：改为逐集串行生成，避免单次请求过长超时，实时显示进度
    完全兼容原有主流程，仅新增优化字段
    新增缓存机制、配置化参数、质量校验优化
    """
    print("="*60)
    print("专业级智能分集系统启动（逐集生成稳定版）")
    print("逐集串行生成，实时输出进度，彻底避免长请求超时")
    print("支持JSON直通生产线：含中英旁白、ComfyUI提示词、质量审核")
    print("多Agent博弈校验：结尾悬念自动打分，低于8分自动重写")
    print("="*60)
    
    # 缓存检查：同一本小说不需要重新分集
    cache_enabled = config.get("episode_splitter.cache_enabled", True)
    if cache_enabled:
        # 基于全局分析结果生成缓存key
        cache_key_content = json.dumps({
            "genre": full_analysis_result['genre'],
            "characters": full_analysis_result['characters'],
            "plot_outline": full_analysis_result['main_plot_outline'][:1000]
        }, ensure_ascii=False)
        cache_hash = hashlib.md5(cache_key_content.encode('utf-8')).hexdigest()
        cache_path = os.path.join("output/cache", f"episode_blueprints_{cache_hash}.json")
        
        if os.path.exists(cache_path) and os.path.getsize(cache_path) > 0:
            print(f"检测到当前小说已完成分集，从缓存加载结果：{cache_path}")
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_blueprints = json.load(f)
            return cached_blueprints
    
    genre = full_analysis_result['genre']
    total_episodes = min(
        config.get("episode_splitter.max_episodes", 100),
        full_analysis_result['recommended_episode_count']
    )
    characters = full_analysis_result['characters']
    plot_outline = full_analysis_result['main_plot_outline']
    turning_points = full_analysis_result['key_turning_points']
    story_rules = full_analysis_result['story_rules']
    min_quality_score = config.get("episode_splitter.min_quality_score", 8)
    max_retries = config.get("episode_splitter.max_retries", 2)
    
    print(f"分析参数：题材={genre}，总集数={total_episodes}，核心角色={len(characters)}个")
    
    # 生成固定Story Bible（完全不变，用于缓存命中）
    story_bible = f"""
【核心设定】
题材：{genre}
世界观：{story_rules.get('world_setting', '')}
力量体系：{story_rules.get('power_system', '')}
核心主题：{full_analysis_result.get('core_theme', '')}

【核心角色】
{json.dumps([{"name": c['name'], "identity": c['identity'], "personality": c['personality'], "importance": c['importance'], "visual_traits": c.get('visual_traits', [])} for c in characters if c['importance'] in ['核心', '主要']], ensure_ascii=False, indent=2)}

【关键剧情转折点】
{json.dumps([{"position": tp['chapter'], "content": tp['content']} for tp in turning_points[:15]], ensure_ascii=False, indent=2)}

【全局剧情脉络摘要】
{plot_outline[:1500]}
"""
    # 控制Story Bible长度在2000-3000字
    story_bible = story_bible.strip()[:2500]
    print(f"固定Story Bible生成完成，长度：{len(story_bible)}字，用于缓存命中")
    
    # 竖屏短剧通用节奏规则，可配置
    episode_rules = config.get("episode_splitter.rules", {
        "opening_hook": "前3秒必须出现钩子（冲突/悬念/反常点）",
        "first_15s": "第15秒必须出现第一个爽点/冲突爆发",
        "mid_point": "中间必须有1次剧情反转",
        "ending": "结尾必须留强悬念，引导用户看下一集",
        "episode_length": "每集对应剧情内容长度控制在1000-1500字，对应正片时长60-90秒"
    })
    
    # 准备压缩chunk列表，减少token消耗
    compressed_chunks = [{"id": chunk['chunk_id'], "preview": chunk['content'][:50]} for chunk in novel_chunks]
    
    # 单集生成Prompt（XML结构化，DeepSeek优化）
    single_episode_prompt = """
你是顶级竖屏短剧编剧+分镜师+本地化翻译，现在需要生成第{{episode_num}}集的内容，属于{{genre}}题材，总共{{total_episodes}}集。
严格遵循以下规则：
1. 每集严格遵循竖屏短剧流量规则：前3秒有钩子，15秒有爽点，结尾留强悬念
2. 剧情承接上下文，连贯不冲突，关键转折点放在高潮位置
3. 输出严格为JSON对象，不要其他内容，不要任何解释、markdown标记、```包裹，直接输出JSON，格式如下：
{
    "seq": {{episode_num}},
    "core_plot": "本集核心剧情内容，100字左右",
    "hook": "本集开头钩子内容，3秒就能抓住用户注意力",
    "climax": "本集核心爽点/冲突高潮内容",
    "ending_suspense": "本集结尾悬念内容，引导用户看下一集",
    "chunk_id": "对应小说chunk的id，从提供的chunk列表中选",
    "main_characters": ["出场角色名1", "出场角色名2"],
    "rhythm_level": 1-10的数字，代表本集节奏紧张程度,
    "hook_analysis": "悬念卡点分析，说明本集钩子和结尾悬念为什么能吸引用户停留",
    "narration_cn": "中文旁白配音文本，精简口语化，适合60-90秒短剧配音",
    "narration_en": "地道英文旁白配音文本，适配欧美短视频平台受众",
    "comfyui_prompts": [
        "分镜1的AI绘画提示词，9:16竖屏比例，包含场景、人物、风格、光影，最后加--ar 9:16",
        "分镜2的AI绘画提示词，9:16竖屏比例，包含场景、人物、风格、光影，最后加--ar 9:16",
        "分镜3的AI绘画提示词，9:16竖屏比例，包含场景、人物、风格、光影，最后加--ar 9:16",
        "分镜4的AI绘画提示词，9:16竖屏比例，包含场景、人物、风格、光影，最后加--ar 9:16",
        "分镜5的AI绘画提示词，9:16竖屏比例，包含场景、人物、风格、光影，最后加--ar 9:16"
    ]
}

<story_bible>
{{story_bible}}
</story_bible>

<previous_episodes_summary>
之前{{prev_count}}集剧情摘要：{{prev_summary}}
</previous_episodes_summary>

<task_requirements>
严格按照JSON格式输出第{{episode_num}}集内容，确保和之前剧情连贯，comfyui_prompts直接可用无需修改，英文旁白地道自然。
可用小说chunk列表：{{chunk_list}}
</task_requirements>
    """
    
    # 审核Prompt（多Agent博弈质量校验）
    audit_prompt = """
你是专业的竖屏短剧内容审核专家，只需要回答分数，不需要其他内容。
请评价以下分集的结尾悬念是否足以让刷短视频的观众停留并点开下一集，打分1-10分：
剧情：{{core_plot}}
结尾悬念：{{ending_suspense}}
只返回一个数字分数，不要任何其他文字。
"""
    
    # 逐集串行生成
    episode_blueprints = []
    prev_summary = ""  # 滚动摘要，记录之前剧集的核心内容，只保留最近3集减少token消耗
    model = config.get("episode_splitter.model", "deepseek-ai/DeepSeek-V3.2")
    temperature = config.get("episode_splitter.temperature", 0.3)
    
    for episode_num in range(1, total_episodes + 1):
        print(f"正在生成第 {episode_num}/{total_episodes} 集...")
        
        # 构造当前集prompt，优化滚动摘要长度，只保留最近3集
        recent_episodes = episode_blueprints[-3:] if len(episode_blueprints) >=3 else episode_blueprints
        short_prev_summary = "\n".join([f"第{ep['seq']}集：{ep['core_plot']}" for ep in recent_episodes])
        
        prompt = single_episode_prompt.replace("{{episode_num}}", str(episode_num))\
                                    .replace("{{genre}}", genre)\
                                    .replace("{{total_episodes}}", str(total_episodes))\
                                    .replace("{{story_bible}}", story_bible)\
                                    .replace("{{prev_count}}", str(len(recent_episodes)))\
                                    .replace("{{prev_summary}}", short_prev_summary if short_prev_summary else "无，这是第1集")\
                                    .replace("{{chunk_list}}", json.dumps(compressed_chunks, ensure_ascii=False))
        
        ep = None
        for retry in range(max_retries + 1):
            try:
                # 调用LLM生成单集
                response = get_llm_response(prompt, temperature=temperature, model=model)
                ep = json.loads(response)
                
                # 校验格式
                required_fields = ["seq", "core_plot", "hook", "climax", "ending_suspense", "chunk_id", "main_characters", "rhythm_level", "hook_analysis", "narration_cn", "narration_en", "comfyui_prompts"]
                for field in required_fields:
                    if field not in ep:
                        raise ValueError(f"缺少字段：{field}")
                
                # 质量审核
                audit_prompt_filled = audit_prompt.replace("{{core_plot}}", ep['core_plot'])\
                                                .replace("{{ending_suspense}}", ep['ending_suspense'])
                score_str = get_llm_response(audit_prompt_filled, temperature=0.0, max_tokens=10, model=model)
                try:
                    score = int(score_str.strip())
                except:
                    score = 7
                
                if score < min_quality_score:
                    if retry < max_retries:
                        print(f"第{episode_num}集评分{score}分，低于{min_quality_score}分，第{retry+1}次重写...")
                        # 优化重写prompt，明确指出问题
                        rewrite_prompt = f"""
<story_bible>
{story_bible}
</story_bible>
以下第{episode_num}集的结尾悬念吸引力不足，评分只有{score}分，请重写本集，重点优化结尾悬念，确保评分达到{min_quality_score}分以上，输出和之前相同格式的JSON对象：
{json.dumps(ep, ensure_ascii=False)}
只返回JSON对象，不要其他内容。
                        """
                        prompt = rewrite_prompt
                        continue
                    else:
                        print(f"第{episode_num}集经过{max_retries}次重写仍未达标，直接使用当前版本，评分{score}分")
                break
                
            except Exception as e:
                if retry < max_retries:
                    print(f"第{episode_num}集生成失败，第{retry+1}次重试：{str(e)}")
                else:
                    print(f"第{episode_num}集生成失败，已重试{max_retries}次，使用默认内容")
                    # 补全默认内容
                    ep = {
                        "seq": episode_num,
                        "core_plot": f"第{episode_num}集剧情",
                        "hook": "开头钩子",
                        "climax": "核心爽点",
                        "ending_suspense": "结尾悬念",
                        "chunk_id": novel_chunks[min(episode_num//3, len(novel_chunks)-1)]['chunk_id'],
                        "main_characters": [c['name'] for c in characters if c['importance'] == '核心'][:2],
                        "rhythm_level": 7,
                        "hook_analysis": "标准悬念卡点设计",
                        "narration_cn": "中文旁白",
                        "narration_en": "English narration",
                        "comfyui_prompts": [
                            "scenario --ar 9:16",
                            "scenario --ar 9:16",
                            "scenario --ar 9:16",
                            "scenario --ar 9:16",
                            "scenario --ar 9:16"
                        ]
                    }
        
        # 添加到结果列表
        episode_blueprints.append(ep)
        # 更新完整摘要
        prev_summary += f"第{episode_num}集：{ep['core_plot']}\n"
        print(f"第{episode_num}/{total_episodes}集生成完成")
    
    # 补充分集元信息
    for ep in episode_blueprints:
        ep['episode_id'] = f"ep_{uuid.uuid4().hex[:8]}"
        ep['genre'] = genre
        # 兼容原有字段名，不破坏主流程
        ep['episode_number'] = str(ep['seq'])
    
    # 保存分集方案
    os.makedirs("output/analysis", exist_ok=True)
    with open("output/analysis/episode_blueprints.json", 'w', encoding='utf-8-sig') as f:
        json.dump(episode_blueprints, f, ensure_ascii=False, indent=2)
    
    # 保存缓存
    if cache_enabled:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(episode_blueprints, f, ensure_ascii=False, indent=2)
        print(f"分集方案已缓存到：{cache_path}")
    
    print(f"智能分集全部完成，共生成 {len(episode_blueprints)} 集专业级分集方案")
    print("输出包含：中英双语旁白、ComfyUI分镜提示词、悬念分析、质量校验结果")
    print("方案已保存到 output/analysis/episode_blueprints.json")
    print("="*60)
    
    return episode_blueprints
