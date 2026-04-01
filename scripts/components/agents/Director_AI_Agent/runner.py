import json
import uuid
import re
import os
import hashlib
from config_center import config
from components.utils.llm_client import get_llm_response

def run_director(screenplay, global_lore, dialogue_script=None, continuity_state=None):
    """
    Cinematographer (摄影指导) V6 影棚级
    强制焦段物理学 专业光影塑形 标准运镜术语 零笼统词汇
    完全符合好莱坞影视工业标准输出
    新增AI生成、缓存、多模型兼容、人工审核功能
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
    main_char = global_lore['characters'][0]
    main_char_name = main_char['name']
    base_char_traits = "，".join(main_char.get('visual_traits', []))
    # 注入跨集状态（如受伤、衣服破损等）
    if continuity_state and 'char_state_overrides' in continuity_state:
        override_traits = "，".join([f"{k}:{v}" for k,v in continuity_state['char_state_overrides'].items()])
        main_char_traits = f"{base_char_traits}, {override_traits}"
    else:
        main_char_traits = base_char_traits
    face_id_ref = main_char.get('face_id', '')
    
    shot_types = ["extreme_close_up", "close_up", "medium_shot", "push_in", "static", "low_angle_shot"]
    camera_angles = ["eye_level", "low_angle", "high_angle", "dutch_angle", "over_the_shoulder"]
    lightings = ["natural", "studio", "dramatic", "chiaroscuro", "backlit"]
    transitions = ["Cut", "Fade_to_black", "Glitch_effect", "Wipe", "Cross_fade", "Flash_cut"]
    motion_intensities = [3, 5, 6, 8, 4, 7]
    physics_effects = ["sparks flying", "screen shake", "debris floating", "wind blowing", "rain droplets", "dust particles"]
    
    # ==================== V6 强制专业规则 ====================
    # 焦段物理学规则
    LENS_RULES = {
        "desperate/grand": "14mm wide angle, deep depth of field",
        "dialogue/closeup": "85mm portrait lens, shallow depth of field, bokeh",
        "action": "24mm prime lens, medium depth of field"
    }
    
    # 光影塑形规则
    LIGHTING_RULES = {
        "villain/insidious": "Split lighting, high contrast chiaroscuro",
        "holy/high_energy": "Volumetric god rays, rim light, backlit",
        "tense/dramatic": "Hard key light, high contrast, hard shadows",
        "calm/romantic": "Soft key light, fill light, low contrast"
    }
    
    # 运镜术语规则
    CAMERA_MOVEMENT_RULES = {
        "unease/anxiety": "Dutch angle, slow pan",
        "shock/surprise": "Dolly zoom, fast push in",
        "tension/chase": "Handheld tracking, shaky cam",
        "epic/reveal": "Crane shot, slow pull back",
        "dialogue": "Static, over the shoulder"
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
                temperature=config.get("director.temperature", 0.4),
                max_tokens=2000
            )
            result = json.loads(response)
            storyboard = result['storyboard']
        except Exception as e:
            print(f"AI分镜生成失败，使用规则生成：{str(e)}")
            enable_ai_generation = False
    
    if not enable_ai_generation:
        # 规则生成分镜，作为fallback
        for shot_num in range(1, len(beats)+2):
            shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
            beat_idx = (shot_num - 1) % len(beats)
            beat_content = beats[beat_idx]['content']
            shot_dialogue = dialogue_map.get(shot_id, {})
            dialogue_content = shot_dialogue.get('content', '')
            speaker = shot_dialogue.get('speaker', main_char_name)

            # 智能匹配专业参数，根据剧情内容自动分配
            beat_lower = beat_content.lower()
            # 匹配焦段
            if any(keyword in beat_lower for keyword in ["绝望", "宏大", "末日", "巨型", "全景"]):
                lens = LENS_RULES["desperate/grand"]
            elif any(keyword in beat_lower for keyword in ["对话", "特写", "表情", "说话", "脸"]):
                lens = LENS_RULES["dialogue/closeup"]
            else:
                lens = LENS_RULES["action"]
            
            # 匹配灯光
            if any(keyword in beat_lower for keyword in ["反派", "阴险", "坏", "敌人", "恐怖"]):
                lighting = LIGHTING_RULES["villain/insidious"]
            elif any(keyword in beat_lower for keyword in ["升级", "异能", "发光", "神圣", "高能"]):
                lighting = LIGHTING_RULES["holy/high_energy"]
            elif any(keyword in beat_lower for keyword in ["紧张", "冲突", "打斗", "战斗"]):
                lighting = LIGHTING_RULES["tense/dramatic"]
            else:
                lighting = LIGHTING_RULES["calm/romantic"]
            
            # 匹配运镜
            if any(keyword in beat_lower for keyword in ["不安", "诡异", "奇怪", "不对劲"]):
                camera_movement = CAMERA_MOVEMENT_RULES["unease/anxiety"]
            elif any(keyword in beat_lower for keyword in ["震惊", "突然", "爆炸", "出现"]):
                camera_movement = CAMERA_MOVEMENT_RULES["shock/surprise"]
            elif any(keyword in beat_lower for keyword in ["紧张", "追逐", "逃跑", "打斗"]):
                camera_movement = CAMERA_MOVEMENT_RULES["tension/chase"]
            elif any(keyword in beat_lower for keyword in [" reveal", "出现", "宏大", "全景"]):
                camera_movement = CAMERA_MOVEMENT_RULES["epic/reveal"]
            else:
                camera_movement = CAMERA_MOVEMENT_RULES["dialogue"]
            
            # 定位
            current_location = "outdoor" if "室外" in beat_content or "天台" in beat_content or "外面" in beat_content or "野外" in beat_content else "indoor"
            
            # 生成专业级视觉提示词，零笼统词汇
            visual_prompt = f"(Masterpiece:1.2), (ultra-detailed:1.2), 9:16 vertical composition, {main_char_name}, {main_char_traits}, {beat_content[:100]}, {lens}, {lighting}, shot on ARRI Alexa Mini"
            
            # 专业级视频提示词，强制加入运镜术语
            motion_intensity = motion_intensities[(seq + shot_num) % len(motion_intensities)]
            physics_effect = physics_effects[(seq + shot_num) % len(physics_effects)]
            video_prompt = f"{visual_prompt}, {camera_movement}, motion_intensity: {motion_intensity}, {physics_effect} --ar 9:16"
            visual_prompt += " --ar 9:16"

            # 具象化音效
            sfx_map = {
                "打斗": "fist punching sound, body impact",
                "爆炸": "explosion sound, debris flying",
                "下雨": "rain sound, thunder",
                "对话": "clear dialogue, slight room reverb",
                "跑步": "footsteps running, heavy breathing"
            }
            specific_sfx = "ambient sound"
            for keyword, sfx in sfx_map.items():
                if keyword in beat_content:
                    specific_sfx = sfx
                    break

            audio_prompt = {
                "Ambience": "post apocalyptic wind howling, distant roaring" if "outdoor" in current_location else "indoor ambient hum, faint distant rumble",
                "SFX": specific_sfx,
                "Music": "BPM 120, tense dark ambient score",
                "Dialogue": dialogue_content
            }

            storyboard.append({
                "shot_id": shot_id,
                "shot_type": shot_types[(seq + shot_num) % len(shot_types)],
                "camera_angle": camera_angles[(seq + shot_num) % len(camera_angles)],
                "lighting_setup": lighting,
                "transition_effect": transitions[(seq + shot_num) % len(transitions)],
                "location": current_location,
                "visual_prompt": visual_prompt,
                "video_prompt": video_prompt,
                "audio_prompt": audio_prompt,
                "render_refs": {"face_id": face_id_ref}
            })
    
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
