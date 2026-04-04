import json
import os
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response
from .professional_prompt_engineering import (
    generate_professional_screenplay_prompt,
    ProfessionalPromptBuilder,
    AdaptivePromptOptimizer
)
from components.utils.western_female_platform_optimizer import (
    generate_platform_optimized_prompt,
    PLATFORM_SPECS,
    CONTENT_STRATEGIES,
    TIKTOK_OPTIMIZATION_RULES,
    AUDIENCE_PREFERENCES
)

def run_screenwriter(episode_blueprint, global_lore, continuity_state=None):
    """
    Showrunner (总编剧/制片人) V7 专业级
    集成好莱坞编剧理论 + 自适应Prompt优化 + 质量反馈循环
    支持: 三幕式/英雄之旅/救猫咪/故事原子/起承转合
    新增: 角色弧线驱动、视觉化节拍、自适应优化
    """
    seq = episode_blueprint['seq']
    core_plot = episode_blueprint['core_plot']
    hook = episode_blueprint['hook']
    climax = episode_blueprint['climax']
    ending_suspense = episode_blueprint['ending_suspense']
    main_characters = episode_blueprint['main_characters']
    
    # 缓存检查
    cache_enabled = config.get("screenwriter.cache_enabled", True)
    if cache_enabled:
        cache_key = hashlib.md5(f"{seq}_{core_plot}_{json.dumps(continuity_state)}".encode('utf-8')).hexdigest()
        cache_path = os.path.join("output/cache", f"screenplay_{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_screenplay = json.load(f)
            print(f"第{seq}集剧本已缓存，直接加载")
            return cached_screenplay
    
    enable_ai_generation = config.get("screenwriter.enable_ai_generation", True)
    if enable_ai_generation:
        # ====== V7: 使用专业级Prompt工程系统 ======
        print(f"[Screenwriter V7] 使用专业Prompt工程生成第{seq}集剧本")
        
        # 获取配置选项
        structure_type = config.get("screenwriter.structure_type", "vertical_drama_golden")
        arc_type = config.get("screenwriter.arc_type", "positive_change") 
        tone_style = config.get("screenwriter.tone_style", "intense")
        enable_adaptive = config.get("screenwriter.enable_adaptive_optimization", False)
        
        # ====== V8: 平台优化集成 ======
        target_platform = config.get("basic.target_platform", "universal")
        content_strategy = config.get("basic.content_strategy", "romance_domination_strategy")
        target_audience = config.get("basic.target_audience", "western_female_18_35")
        
        use_platform_optimization = (target_platform in PLATFORM_SPECS) and (content_strategy in CONTENT_STRATEGIES)
        
        if use_platform_optimization:
            print(f"[Screenwriter V8] 🌍 启用平台优化: 平台={target_platform}, 策略={content_strategy}, 受众={target_audience}")
            
            # 生成平台优化的基础Prompt（包含完整的平台/受众/策略信息）
            platform_prompt, platform_meta = generate_platform_optimized_prompt(
                episode_info=episode_blueprint,
                global_lore=global_lore,
                platform=target_platform,
                strategy=content_strategy,
                target_audience=target_audience
            )
            
            # 将平台优化Prompt作为基础，再叠加专业编剧理论
            professional_prompt, prompt_metadata = generate_professional_screenplay_prompt(
                episode_info=episode_blueprint,
                global_lore=global_lore,
                structure=structure_type,
                arc_type=arc_type,
                tone=tone_style,
                enable_adaptive=enable_adaptive
            )
            
            # 合并两个Prompt：平台优化在前（定义受众和策略），专业理论在后（定义结构和技术）
            final_prompt = f"""{platform_prompt}

---

【专业编剧技术层 - 叠加应用】
{professional_prompt}

**重要**: 以上两部分必须同时遵守。平台优化规则定义了WHO(给谁看)和WHERE(在哪发布)，专业编剧技术定义了HOW(怎么写好)。
输出格式以平台优化部分的JSON格式为准，但beats内容需融合两部分的全部要求。
"""
            prompt_metadata.update(platform_meta)
            prompt_metadata["prompt_version"] = "V8 Platform-Optimized"
            
        else:
            # 无平台优化时使用标准V7流程
            final_prompt, prompt_metadata = generate_professional_screenplay_prompt(
                episode_info=episode_blueprint,
                global_lore=global_lore,
                structure=structure_type,
                arc_type=arc_type,
                tone=tone_style,
                enable_adaptive=enable_adaptive
            )
        
        print(f"[Screenwriter V8] Prompt配置: 结构={structure_type}, 弧线={arc_type}, 风格={tone_style}, 平台={target_platform}")
        
        try:
            response = get_llm_response(
                final_prompt, 
                model=config.get("screenwriter.model", "deepseek-ai/DeepSeek-V3.2"),
                task_type="screenplay",
                temperature=config.get("screenwriter.temperature", 0.75),  # 稍微提高以获得更多创意
                max_tokens=2000  # 增加token限制以容纳更详细的输出
            )
            result = json.loads(response)
            
            # V7: 处理增强的输出格式
            beats = result.get('beats', [])
            
            # 提取质量检查信息（如果有）
            quality_check = result.get('quality_check', {})
            if quality_check:
                print(f"[Screenwriter V7] 自检结果:")
                print(f"  冰山法则合规: {'✅' if quality_check.get('iceberg_compliance') else '⚠️'}")
                print(f"  台词密度: {quality_check.get('dialogue_density', 'N/A')}")
                print(f"  视觉叙事评分: {quality_check.get('visual_storytelling_score', 'N/A')}/10")
            
            # 提取完播率分析（如果有）
            retention_analysis = result.get('retention_curve_analysis', {})
            if retention_analysis:
                print(f"[Screenwriter V7] 完播率预估:")
                for key, value in retention_analysis.items():
                    print(f"  {key}: {value}")
            
            # 保存元数据到screenplay中
            screenplay_metadata = {
                "prompt_version": prompt_metadata.get("prompt_version", "V7 Professional"),
                "structure_used": structure_type,
                "arc_type": arc_type,
                "theme_statement": result.get('theme_statement', ''),
                "character_arcs": result.get('character_arcs_progress', {}),
                "prompt_metadata": prompt_metadata,
                # V8 新增：平台优化元数据
                "platform_optimization": {
                    "target_platform": target_platform if use_platform_optimization else "universal",
                    "content_strategy": content_strategy if use_platform_optimization else "none",
                    "target_audience": target_audience if use_platform_optimization else "general",
                    "platform_specs_applied": use_platform_optimization
                }
            }
            
        except Exception as e:
            print(f"[Screenwriter V8] AI剧本生成失败，回退到V6模式：{str(e)}")
            # 回退到V6简单模式
            prompt = f"""
你是专业竖屏短剧总编剧，擅长创作60-90秒高完播率短剧剧本。
严格遵循完播率波浪理论：Hook(前3秒) -> Setup(铺垫) -> Escalation(冲突升级) -> Cliffhanger(结尾悬念)
每部分严格控制时长，台词精炼，符合冰山法则，能用动作表达就不用台词。

剧集信息：
第{seq}集
核心剧情：{core_plot}
开头钩子：{hook}
核心爽点：{climax}
结尾悬念：{ending_suspense}
主要角色：{','.join(main_characters)}
跨集上下文：{json.dumps(continuity_state, ensure_ascii=False) if continuity_state else '无'}

输出严格为JSON格式，不要任何其他内容，格式如下：
{{
    "beats": [
        {{
            "beat_type": "hook",
            "content": "前3秒钩子内容，直接抛出冲突，台词不超过10字",
            "dialogue_limit": 10,
            "duration": 3
        }},
        {{
            "beat_type": "setup",
            "content": "背景铺垫内容，快速交代信息，台词不超过12字",
            "dialogue_limit": 12,
            "duration": 12
        }},
        {{
            "beat_type": "escalation",
            "content": "冲突升级爽点内容，动作优先，台词不超过15字",
            "dialogue_limit": 15,
            "duration": 30
        }},
        {{
            "beat_type": "cliffhanger",
            "content": "结尾悬念内容，引导看下一集，台词不超过8字",
            "dialogue_limit": 8,
            "duration": 15
        }}
    ]
}}
            """
            try:
                response = get_llm_response(
                    prompt, 
                    model=config.get("screenwriter.model", "deepseek-ai/DeepSeek-V3.2"),
                    task_type="screenplay",
                    temperature=config.get("screenwriter.temperature", 0.7),
                    max_tokens=1000
                )
                result = json.loads(response)
                beats = result['beats']
                screenplay_metadata = {"prompt_version": "V6 Fallback"}
            except Exception as e2:
                print(f"V6模式也失败: {str(e2)}")
                enable_ai_generation = False
    
    if not enable_ai_generation:
        # 规则生成剧本，作为fallback
        beats = []
        
        # 1. Hook钩子：前3秒必须抓眼球，直接抛出冲突/反常点
        hook_content = hook if hook else core_plot[:50].strip()
        beats.append({
            "beat_type": "hook",
            "content": f"{hook_content} | 直接抛出核心冲突，3秒抓眼球",
            "dialogue_limit": 10, # 台词不超过10字
            "duration": 3
        })
        
        # 2. Setup铺垫：交代背景信息，快速推进
        setup_content = core_plot[50:150].strip()
        beats.append({
            "beat_type": "setup",
            "content": f"{setup_content} | 快速交代背景，无冗余信息",
            "dialogue_limit": 12,
            "duration": 12
        })
        
        # 3. Escalation冲突升级：核心爽点爆发，符合冰山理论
        climax_content = climax if climax else core_plot[150:250].strip()
        beats.append({
            "beat_type": "escalation",
            "content": f"{climax_content} | 核心冲突爆发，动作优先于对话",
            "dialogue_limit": 15, # 最长不超过15字
            "duration": 30
        })
        
        # 4. Cliffhanger结尾悬念：强制留钩子，引导下一集
        suspense_content = ending_suspense if ending_suspense else (core_plot[250:300].strip() if len(core_plot) > 250 else "新的危机突然出现，主角脸色骤变")
        beats.append({
            "beat_type": "cliffhanger",
            "content": f"{suspense_content} | 结尾强悬念，用户忍不住点下一集",
            "dialogue_limit": 8,
            "duration": 15
        })
    
    # 台词精炼：所有对白自动截断到对应字数限制，动作优先
    for beat in beats:
        # 移除多余对话，能用动作表达绝不写字
        beat['content'] = beat['content'].replace("说：", "").replace("说道：", "").replace("：“", " ").replace("”", "")
        # 截断超长内容
        if len(beat['content']) > beat.get('dialogue_limit', 15) * 2:
            beat['content'] = beat['content'][:beat.get('dialogue_limit', 15) * 2] + "..."
        
        # V7: 确保beats有必要的字段
        if 'visual_description' not in beat:
            beat['visual_description'] = ""
        if 'audio_cue' not in beat:
            beat['audio_cue'] = ""
        if 'emotional_target' not in beat:
            beat['emotional_target'] = "neutral"
        if 'narrative_function' not in beat:
            beat['narrative_function'] = "advance_plot"
    
    # 构建screenplay输出
    # 初始化V7元数据（如果不存在）
    if 'screenplay_metadata' not in locals():
        screenplay_metadata = {
            "prompt_version": "V6 Basic",
            "structure_used": "basic_hook_setup_escalation_cliffhanger",
            "arc_type": "undefined",
            "theme_statement": "",
            "character_arcs": {},
            "prompt_metadata": {}
        }
    
    screenplay = {
        "episode_seq": seq,
        "core_plot": f"第{seq}集：{core_plot[:100]}",
        "beats": beats,
        "retention_curve": "Hook->Setup->Escalation->Cliffhanger",
        "bpm_pacing": 120 + seq % 10,
        "conflict_density": 0.9 + (seq % 20)/100,
        "total_duration": sum(beat.get('duration', 15) for beat in beats),
        
        # V7 新增：专业级元数据
        "metadata": screenplay_metadata
    }
    
    # 保存缓存
    if cache_enabled:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(screenplay, f, ensure_ascii=False, indent=2)
    
    # 人工审核剧本
    from components.utils.human_review_manager import human_review
    if config.get("screenwriter.enable_review", True):
        if not human_review.request_review("screenplay", screenplay, seq):
            # 审核被驳回，删除缓存重新生成
            if os.path.exists(cache_path):
                os.remove(cache_path)
            raise Exception(f"第{seq}集剧本审核被驳回")
    
    return screenplay
