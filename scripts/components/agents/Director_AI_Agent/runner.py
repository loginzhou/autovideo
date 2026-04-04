import json
import uuid
import re
import os
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response
from components.utils.prompt_engineering import (
    generate_visual_prompt, generate_video_prompt, generate_audio_prompt,
    get_shot_parameters_by_emotion, get_shot_parameters_by_scene
)
from .cinematic_language_system import (
    get_cinematic_shot, 
    generate_cinematic_prompt,
    DIRECTOR_STYLES,
    EMOTIONAL_SHOT_MAPPING,
    SCENE_TYPE_RULES
)
from components.upgrade.novel_semantic_analyzer.emotional_analysis_system import (
    analyze_scene_emotion,
    calculate_complex_emotion,
    EMOTION_DIMENSIONS,
    BASIC_EMOTIONS
)
from components.utils.multimodal_consistency import (
    check_multimodal_consistency,
    generate_consistency_fix_suggestions,
    MODALITY_MAPPING_RULES
)
from components.utils.western_female_platform_optimizer import (
    PLATFORM_SPECS,
    CONTENT_STRATEGIES,
    TIKTOK_OPTIMIZATION_RULES,
    AUDIENCE_PREFERENCES,
    WESTERN_CULTURAL_ADAPTATION
)

def run_director(screenplay, global_lore, dialogue_script=None, continuity_state=None):
    """
    Cinematographer (摄影指导) V7 电影级智能版
    集成电影级镜头语言系统 + 情绪分析 + 多模态一致性
    支持导演风格模拟、情绪曲线驱动、跨模态对齐
    """
    seq = screenplay['episode_seq']
    beats = screenplay['beats']
    
    # 缓存检查
    cache_enabled = config.get("director.cache_enabled", True)
    if cache_enabled:
        cache_key = hashlib.md5(f"{seq}_{json.dumps(beats)}_{json.dumps(continuity_state)}".encode('utf-8')).hexdigest()
        cache_path = os.path.join("output/cache", f"storyboard_{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_storyboard = json.load(f)
            print(f"第{seq}集分镜已缓存，直接加载")
            return cached_storyboard
    
    # 变量池，替换为实际全局角色信息 + 连贯性状态注入
    characters_list = global_lore.get('characters', [])
    if not characters_list:
        print("[Director V8] ⚠️ global_lore中没有角色信息，使用默认角色")
        characters_list = [{"name": "主角", "visual_traits": [], "face_id": ""}]
    main_char = characters_list[0]
    main_char_name = main_char['name']
    base_char_traits = "，".join(main_char.get('visual_traits', []))
    # 注入跨集状态（如受伤、衣服破损等）
    if continuity_state and 'char_state_overrides' in continuity_state:
        override_traits = "，".join([f"{k}:{v}" for k,v in continuity_state['char_state_overrides'].items()])
        main_char_traits = f"{base_char_traits}, {override_traits}"
    else:
        main_char_traits = base_char_traits
    face_id_ref = main_char.get('face_id', '')
    
    # 扩展镜头类型
    shot_types = ["extreme_close_up", "close_up", "medium_shot", "medium_close_up", "long_shot", "extreme_long_shot", "two_shot", "group_shot", "over_the_shoulder", "point_of_view", "push_in", "pull_out", "tracking_shot", "dolly_shot", "crane_shot", "handheld", "static"]
    
    # 扩展镜头角度
    camera_angles = ["eye_level", "low_angle", "high_angle", "dutch_angle", "over_the_shoulder", "birdseye", "wormseye", "profile", "three_quarter", "frontal"]
    
    # 扩展灯光类型
    lightings = ["natural", "studio", "dramatic", "chiaroscuro", "backlit", "side_lighting", "top_lighting", "under_lighting", "soft_lighting", "hard_lighting", "motivated_lighting", "practical_lighting"]
    
    # 扩展转场效果
    transitions = ["Cut", "Fade_to_black", "Fade_in", "Glitch_effect", "Wipe", "Cross_fade", "Flash_cut", "Match_cut", "J cut", "L cut", "Dissolve", "Iris", "Smash_cut"]
    
    # 动态镜头参数
    motion_intensities = [3, 5, 6, 8, 4, 7, 9, 2, 10]
    motion_types = ["smooth", "jittery", "steady", "fluid", "abrupt"]
    
    # 物理效果
    physics_effects = ["sparks flying", "screen shake", "debris floating", "wind blowing", "rain droplets", "dust particles", "snowflakes", "leaves falling", "water splashing", "smoke billowing"]
    
    # 蒙太奇手法
    montage_types = ["parallel_montage", "cross_cutting", "metaphorical_montage", "rhythmic_montage", "serial_montage"]
    
    # ==================== V6 强制专业规则 ====================
    # 焦段物理学规则
    LENS_RULES = {
        "desperate/grand": "14mm wide angle, deep depth of field",
        "dialogue/closeup": "85mm portrait lens, shallow depth of field, bokeh",
        "action": "24mm prime lens, medium depth of field",
        "intimate/melancholy": "50mm standard lens, shallow depth of field",
        "suspense/mystery": "35mm wide angle, deep depth of field",
        "epic/landscape": "16mm ultra wide angle, deep depth of field",
        "dynamic/fast": "28mm prime lens, medium depth of field"
    }
    
    # 光影塑形规则
    LIGHTING_RULES = {
        "villain/insidious": "Split lighting, high contrast chiaroscuro",
        "holy/high_energy": "Volumetric god rays, rim light, backlit",
        "tense/dramatic": "Hard key light, high contrast, hard shadows",
        "calm/romantic": "Soft key light, fill light, low contrast",
        "mystery/suspense": "Low key lighting, high contrast, limited fill",
        "happy/bright": "High key lighting, soft shadows, even illumination",
        "nostalgic/warm": "Warm color temperature, soft golden hour lighting",
        "cold/sterile": "Cool color temperature, flat lighting, high key"
    }
    
    # 运镜术语规则
    CAMERA_MOVEMENT_RULES = {
        "unease/anxiety": "Dutch angle, slow pan",
        "shock/surprise": "Dolly zoom, fast push in",
        "tension/chase": "Handheld tracking, shaky cam",
        "epic/reveal": "Crane shot, slow pull back",
        "dialogue": "Static, over the shoulder",
        "intimate/melancholy": "Slow dolly in, shallow focus",
        "mystery/suspense": "Steady tracking, slow pan",
        "dynamic/action": "Fast dolly, whip pan",
        "romantic/tender": "Smooth crane shot, slow movement"
    }

    # 对话映射表
    if dialogue_script is None:
        # 没有传入对话脚本，生成默认占位
        dialogue_map = {}
        for shot_num in range(1, len(beats)+2):
            shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
            dialogue_map[shot_id] = {
                "content": f"第{shot_num}个镜头默认对话内容",
                "speaker": main_char_name
            }
    else:
        dialogue_map = {d['shot_id']: d for d in dialogue_script}

    enable_ai_generation = config.get("director.enable_ai_generation", False)
    storyboard = []
    
    if enable_ai_generation:
        # AI生成分镜
        prompt = f"""
你是好莱坞顶级摄影指导，现在需要为竖屏短剧第{seq}集生成专业分镜，一共{len(beats)}个镜头，对应以下剧本节拍：
{json.dumps(beats, ensure_ascii=False)}

主要角色：{main_char_name}，外貌特征：{main_char_traits}
跨集状态：{json.dumps(continuity_state, ensure_ascii=False) if continuity_state else '无'}

严格遵循以下专业规则输出：
1. 每个镜头包含完整专业参数：景别、运镜、灯光、构图、时长、视觉提示词
2. 视觉提示词要包含焦段、光影、运镜、场景、角色，最后加--ar 9:16，适配9:16竖屏
3. 生成的提示词要同时兼容Stable Diffusion、MidJourney、Sora等所有主流生图/生视频模型
4. 输出严格为JSON格式，不要任何其他内容，格式如下：
{{
    "storyboard": [
        {{
            "shot_id": "ep{seq}_shot01",
            "shot_type": "镜头类型",
            "camera_angle": "镜头角度",
            "lighting_setup": "灯光方案",
            "transition_effect": "转场效果",
            "location": "场景位置",
            "visual_prompt": "AI绘画提示词，包含所有专业参数，--ar 9:16结尾",
            "video_prompt": "AI生视频提示词，包含运镜和动态效果，--ar 9:16结尾",
            "audio_prompt": {{
                "Ambience": "环境音效",
                "SFX": "特殊音效",
                "Music": "背景音乐风格",
                "Dialogue": "角色台词"
            }},
            "render_refs": {{"face_id": "{face_id_ref}"}}
        }}
    ]
}}
        """
        try:
            response = get_llm_response(
                prompt,
                model=config.get("director.model", "deepseek-ai/DeepSeek-V3.2"),
                task_type="storyboard",
                temperature=config.get("director.temperature", 0.4),
                max_tokens=2000
            )
            result = json.loads(response)
            storyboard = result['storyboard']
        except Exception as e:
            print(f"AI分镜生成失败，使用规则生成：{str(e)}")
            enable_ai_generation = False
    
    if not enable_ai_generation:
        # V8: 电影级智能分镜生成（集成情绪分析+导演风格+平台优化）
        director_style = config.get("director.default_style", "nolan")
        story_type = global_lore.get("genre", "rags_to_riches")
        
        # ====== V8: 平台优化配置读取 ======
        target_platform = config.get("basic.target_platform", "universal")
        content_strategy_key = config.get("basic.content_strategy", "romance_domination_strategy")
        
        platform_spec = PLATFORM_SPECS.get(target_platform, {})
        content_strategy = CONTENT_STRATEGIES.get(content_strategy_key, {})
        use_platform_rules = bool(platform_spec) and bool(content_strategy)
        
        if use_platform_rules:
            print(f"[Director V8] 🌍 平台优化已启用:")
            print(f"   平台: {platform_spec.get('name', target_platform)}")
            print(f"   策略: {content_strategy.get('name', content_strategy_key)}")
            print(f"   节奏要求: 每{platform_spec.get('rhythm_profile', {}).get('beat_drop', 5)}秒一个节拍变化")
        
        print(f"[Director V8] 使用导演风格: {director_style} | 故事类型: {story_type}")
        
        for shot_num in range(1, len(beats)+2):
            shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
            beat_idx = (shot_num - 1) % len(beats)
            beat = beats[beat_idx]
            beat_content = beat['content']
            beat_type = beat.get('beat_type', 'setup')
            
            shot_dialogue = dialogue_map.get(shot_id, {})
            dialogue_content = shot_dialogue.get('content', '')
            speaker = shot_dialogue.get('speaker', main_char_name)
            dialogue_emotion = shot_dialogue.get('emotion', '')
            
            # ====== 核心升级：使用情绪分析系统 ======
            scene_analysis = analyze_scene_emotion(beat_content)
            primary_emotion = scene_analysis["primary_emotion"]
            emotion_intensity = scene_analysis["intensity"]
            
            # 如果台词有明确情绪，优先使用
            if dialogue_emotion and dialogue_emotion in BASIC_EMOTIONS:
                primary_emotion = dialogue_emotion
                emotion_intensity = min(1.0, emotion_intensity + 0.2)
            
            # 根据剧情位置调整强度（弧线中段更强）
            arc_position = seq / max(global_lore.get('recommended_episode_count', 98), 1)
            if 0.4 <= arc_position <= 0.8:  # 故事中段
                emotion_intensity = min(1.0, emotion_intensity * 1.2)
            
            # ====== 场景类型智能识别 ======
            scene_type_detected = "interior_domestic"
            for scene_type_key, rules in SCENE_TYPE_RULES.items():
                indicators = rules.get("indicators", [])
                if any(indicator in beat_content for indicator in indicators):
                    scene_type_detected = scene_type_key
                    break
            
            # ====== 调用电影级镜头语言系统 ======
            cinematic_config = get_cinematic_shot(
                emotion=primary_emotion,
                scene_type=scene_type_detected,
                director_style=director_style,
                intensity=int(round(emotion_intensity * 10))
            )
            
            # 从配置中提取参数
            shot_type = cinematic_config.get("shot_type", "medium_shot")
            camera_movement_raw = cinematic_config.get("camera_movement", "static")
            camera_angle = camera_movement_raw.split()[0] if camera_movement_raw else "eye_level"
            lighting_setup = cinematic_config.get("lighting_setup", "natural")
            lens_info = cinematic_config.get("lens", "50mm standard lens")
            
            # ====== V8: 平台视觉语言覆盖 ======
            platform_visual_overrides = {}
            if use_platform_rules and 'visual_language' in content_strategy:
                vis_lang = content_strategy['visual_language']
                
                # 覆盖光影方案（使用策略指定的风格）
                if 'lighting' in vis_lang:
                    platform_visual_overrides['lighting'] = vis_lang['lighting']
                    # 将策略描述转换为具体灯光值
                    if 'golden' in vis_lang['lighting'].lower() or 'warm' in vis_lang['lighting'].lower():
                        lighting_setup = "warm golden hour, soft key light, low contrast"
                    elif 'dramatic' in vis_lang['lighting'].lower() or 'contrast' in vis_lang['lighting'].lower():
                        lighting_setup = "hard key light, high contrast, dramatic shadows"
                    elif 'ethereal' in vis_lang['lighting'].lower() or 'glow' in vis_lang['lighting'].lower():
                        lighting_setup = "ethereal glow, volumetric light, rim lighting"
                
                # 覆盖色彩分级
                if 'color_grading' in vis_lang:
                    platform_visual_overrides['color_grading'] = vis_lang['color_grading']
                
                # 覆盖运镜偏好
                if 'camera_work' in vis_lang:
                    platform_visual_overrides['camera_work'] = vis_lang['camera_work']
                    # 根据策略调整镜头类型
                    if 'close-up' in vis_lang['camera_work'].lower() and beat_type in ['hook', 'climax']:
                        shot_type = "extreme_close_up"
                    elif 'wide' in vis_lang['camera_work'].lower() and beat_type == 'cliffhanger':
                        shot_type = "long_shot"
            
            # V8: 计算平台特定指标
            platform_metrics = {}
            if use_platform_rules:
                # Hook强度评估（第一个镜头或hook类型节拍得分更高）
                is_hook_shot = (shot_num == 1) or (beat_type == 'hook')
                hook_strength = 9 if is_hook_shot else max(3, 10 - shot_num)
                
                # 分享性评估（情绪强烈+视觉冲击=高分享性）
                shareability = min(10, int(emotion_intensity * 8) + (5 if beat_type in ['climax', 'cliffhanger'] else 2))
                
                # 评论诱导元素
                comment_inducers = []
                if beat_type == 'cliffhanger':
                    comment_inducers.append("悬念结尾-猜测剧情走向")
                if primary_emotion in ['love', 'anger', 'sadness']:
                    comment_inducers.append(f"强{primary_emotion}情绪共鸣")
                if 'twist' in beat_content.lower() or 'shock' in beat_content.lower():
                    comment_inducers.append("意外反转")
                
                # TikTok文字叠加建议
                text_overlay_suggestion = None
                if target_platform == "tiktok" and beat_type in ['setup', 'escalation']:
                    if len(beat_content) > 20:
                        text_overlay_suggestion = beat_content[:40] + "..."
                
                platform_metrics = {
                    "hook_strength": hook_strength,
                    "shareability_factor": shareability,
                    "comment_inducers": comment_inducers,
                    "text_overlay_suggestion": text_overlay_suggestion,
                    "beat_position_for_retention": f"{shot_num}/{len(beats)+1}"
                }
            
            current_location = "outdoor" if any(kw in beat_content for kw in ["室外", "天台", "外面", "野外", "街道"]) else "indoor"
            
            # ====== 生成专业级提示词（使用新系统）=====
            visual_prompt = generate_cinematic_prompt(
                cinematic_config,
                scene_description=f"{current_location} - {beat_content[:100]}",
                character_action=f"{speaker}: {dialogue_content[:50] if dialogue_content else 'observing'}"
            )
            
            # 视频提示词（保留原有逻辑但增强）
            motion_intensity = motion_intensities[min(int(emotion_intensity * 10), len(motion_intensities)-1)]
            motion_type = motion_types[(seq + shot_num) % len(motion_types)]
            physics_effect = physics_effects[(seq + shot_num) % len(physics_effects)]
            
            video_prompt = generate_video_prompt(
                visual_prompt=visual_prompt,
                camera_movement=camera_movement_raw,
                motion_intensity=motion_intensity,
                motion_type=motion_type,
                physics_effect=physics_effect,
                montage_type=montage_type
            )

            # ====== 音频设计（使用专业系统 + 平台优化）=====
            from components.agents.Foley_Sound_Designer_Agent.professional_audio_system import get_audio_design, generate_audio_prompt as gen_pro_audio_prompt
            
            audio_design = get_audio_design(
                emotion=primary_emotion,
                scene_type=scene_type_detected,
                intensity=int(round(emotion_intensity * 10))
            )
            
            # V8: 平台音频策略覆盖
            if use_platform_rules and 'audio_language' in content_strategy:
                aud_lang = content_strategy['audio_language']
                audio_req = platform_spec.get('audio_requirements', {})
                
                # 覆盖音乐风格
                if 'music' in aud_lang:
                    audio_design['music'] = {
                        **audio_design.get('music', {}),
                        "platform_style": aud_lang['music'],
                        "trend_awareness": audio_req.get('music_trend_awareness', 'moderate')
                    }
                
                # 覆盖环境音
                if 'ambience' in aud_lang:
                    audio_design['ambience'] = aud_lang['ambience']
                
                # 调整音量平衡（TikTok要求音乐略大于人声）
                if target_platform == "tiktok":
                    audio_design['mix_balance'] = "music_60_voice_40"
                elif target_platform == "facebook_reels":
                    audio_design['mix_balance'] = "balanced"
            
            audio_prompt = gen_pro_audio_prompt(
                audio_design,
                scene_description=f"{current_location} - {beat_content[:80]}",
                character_dialogue=dialogue_content
            )

            # 构建增强的storyboard条目（包含完整元数据）
            storyboard_entry = {
                "shot_id": shot_id,
                "shot_type": shot_type,
                "camera_angle": camera_angle,
                "lighting_setup": lighting_setup,
                "transition_effect": transitions[(seq + shot_num) % len(transitions)],
                "location": current_location,
                "visual_prompt": visual_prompt,
                "video_prompt": video_prompt,
                "audio_prompt": audio_prompt,
                "render_refs": {"face_id": face_id_ref},
                
                # V7 新增：完整的台词信息
                "dialogue": {
                    "speaker": speaker,
                    "content": dialogue_content,
                    "emotion": primary_emotion,
                    "delivery": shot_dialogue.get('delivery', '正常语速'),
                    "subtext": shot_dialogue.get('subtext', ''),
                    "duration": shot_dialogue.get('duration', 2.5)
                },
                
                # V7 新增：电影级元数据
                "cinematic_metadata": {
                    "director_style": director_style,
                    "primary_emotion": primary_emotion,
                    "emotion_intensity": emotion_intensity,
                    "emotion_vector": calculate_complex_emotion(primary_emotion),
                    "scene_type": scene_type_detected,
                    "lens_config": lens_info,
                    "color_grading": platform_visual_overrides.get('color_grading', cinematic_config.get("color_grading", "")),
                    "movement_curve": cinematic_config.get("movement_curve", "")
                },
                
                # V7 新增：剧情位置信息
                "narrative_context": {
                    "episode_position": seq,
                    "total_episodes": global_lore.get('recommended_episode_count', 98),
                    "beat_type": beat_type,
                    "beat_index": beat_idx + 1,
                    "total_beats": len(beats),
                    "is_climax_beat": beat_type in ["climax", "escalation"]
                },
                
                # V8 新增：平台优化元数据
                "platform_optimization": {
                    "target_platform": target_platform if use_platform_rules else "universal",
                    "hook_strength": platform_metrics.get("hook_strength", 0),
                    "shareability_factor": platform_metrics.get("shareability_factor", 0),
                    "comment_inducers": platform_metrics.get("comment_inducers", []),
                    "text_overlay_suggestion": platform_metrics.get("text_overlay_suggestion"),
                    "visual_language_applied": platform_visual_overrides
                } if use_platform_rules else None
            }
            
            storyboard.append(storyboard_entry)
        
        # ====== V8: 多模态一致性检查 ======
        print(f"[Director V8] 执行多模态一致性检查...")
        
        consistency_report = check_multimodal_consistency(
            visual_config={
                "director_style": director_style,
                "color_temperature": lighting_setup,
                "lighting_setup": lighting_setup,
                "camera_movement": camera_angle
            },
            audio_config=audio_design if 'audio_design' in locals() else {},
            text_analysis={
                "primary_emotion": primary_emotion if 'primary_emotion' in dir() else "neutral",
                "intensity": emotion_intensity if 'emotion_intensity' in dir() else 0.5
            }
        )
        
        if consistency_report["overall_score"] < 0.7:
            print(f"[Director V8] ⚠️ 一致性得分较低: {consistency_report['overall_score']:.2f}")
            suggestions = generate_consistency_fix_suggestions(consistency_report)
            for suggestion in suggestions[:3]:  # 只显示前3个建议
                print(f"   💡 {suggestion['suggestion']}")
        else:
            print(f"[Director V8] ✅ 多模态一致性检查通过 (得分: {consistency_report['overall_score']:.2f})")
    
    storyboard_result = {
        "episode_seq": seq,
        "storyboard": storyboard
    }
    
    # 保存缓存
    if cache_enabled:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(storyboard_result, f, ensure_ascii=False, indent=2)
    
    # 人工审核分镜
    from components.utils.human_review_manager import human_review
    if config.get("director.enable_review", True):
        if not human_review.request_review("storyboard", storyboard_result, seq):
            # 审核被驳回，删除缓存重新生成
            if os.path.exists(cache_path):
                os.remove(cache_path)
            raise Exception(f"第{seq}集分镜审核被驳回")
    
    return storyboard_result
