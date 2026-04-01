import json
import uuid
import re
from components.skills.audio_visual_logic_engine.index import AudioVisualLogicEngine

def run_director(screenplay, global_lore, dialogue_script=None, continuity_state=None):
    """
    🎬 Cinematographer (摄影指导) V6 影棚级
    ✅ 强制焦段物理学 ✅ 专业光影塑形 ✅ 标准运镜术语 ✅ 零笼统词汇
    完全符合好莱坞影视工业标准输出
    """
    # 变量池，替换为实际全局角色信息 + 连贯性状态注入
    main_char = global_lore['characters'][0]
    main_char_name = main_char['name']
    base_char_traits = "，".join(main_char['visual_traits'])
    # 注入跨集状态（如受伤、衣服破损等）
    if continuity_state and 'char_state_overrides' in continuity_state:
        override_traits = "，".join([f"{k}:{v}" for k,v in continuity_state['char_state_overrides'].items()])
        main_char_traits = f"{base_char_traits}, {override_traits}"
    else:
        main_char_traits = base_char_traits
    face_id_ref = main_char['face_id_ref']
    
    seq = screenplay['episode_seq']
    shot_types = ["extreme_close_up", "close_up", "medium_shot", "push_in", "static", "low_angle_shot"]
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
        for shot_num in range(1,7):
            shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
            dialogue_map[shot_id] = {
                "content": f"第{shot_num}个镜头默认对话内容",
                "speaker": "默认角色"
            }
    else:
        dialogue_map = {d['shot_id']: d for d in dialogue_script}

    storyboard = []
    for shot_num in range(1,7):
        shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
        beat_content = screenplay['beats'][shot_num%3]['content']
        shot_dialogue = dialogue_map.get(shot_id, {})
        dialogue_content = shot_dialogue.get('content', '')
        speaker = shot_dialogue.get('speaker', main_char_name)

        # 智能匹配专业参数，根据剧情内容自动分配
        beat_lower = beat_content.lower()
        # 匹配焦段
        if any(keyword in beat_lower for keyword in ["绝望", "宏大", "末日", "尸潮", "巨型"]):
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

        # 具象化音效
        specific_sfx = logic_engine.get_specific_sfx(dialogue_content, beat_content)
        audio_prompt = {
            "Ambience": "post apocalyptic wind howling, distant zombie roaring" if "outdoor" in current_location else "indoor ambient hum, faint distant rumble",
            "SFX": specific_sfx,
            "Music": "BPM 120, tense dark ambient score",
            "Dialogue": dialogue_content
        }

        storyboard.append({
            "shot_id": shot_id,
            "shot_type": shot_types[(seq + shot_num) % len(shot_types)],
            "camera_angle": camera_angles[(seq + shot_num) % len(camera_angles)],
            "lighting_setup": lightings[(seq + shot_num) % len(lightings)],
            "transition_effect": transitions[(seq + shot_num) % len(transitions)],
            "location": current_location,
            "visual_prompt": visual_prompt,
            "video_prompt": video_prompt,
            "audio_prompt": audio_prompt,
            "render_refs": {"face_id": face_id_ref}
        })
    
    return {
        "episode_seq": seq,
        "storyboard": storyboard
    }
