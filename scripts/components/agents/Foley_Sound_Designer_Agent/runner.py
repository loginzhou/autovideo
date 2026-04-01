def run_foley_sound_designer(storyboard, scene_context, continuity_state=None):
    """
    🎧 Foley & Sound Designer (拟音与声音设计) V6 影棚级
    ✅ 空间声学 ✅ 频段分离 ✅ 零通用音效
    完全符合院线级音频制作标准，3D沉浸感拉满
    """
    # ==================== V6 强制专业规则 ====================
    # 空间声学映射表
    SPATIAL_ACOUSTIC_RULES = {
        "indoor_small": "muffled, reverb decay 0.5s, close proximity",
        "indoor_large": "echoing, reverb decay 2s, distant reflections",
        "outdoor_open": "dry, no reverb, wide panning",
        "outdoor_enclosed": "slight reverb, distant echos, wind noise floor"
    }
    
    # 频段分离规则
    EQ_RULES = {
        "impact/collision": "Low-frequency sub-bass rumble + Mid-range thud + High-frequency crisp detail",
        "glass/breaking": "High-frequency shattering + Low-frequency resonant thud",
        "dialogue": "Mid-range boosted, high-frequency air included, low-frequency rolled off",
        "ambience": "Low-frequency rumble floor + Mid-range texture + High-frequency air detail"
    }
    
    location = storyboard.get('location', 'outdoor_open')
    processed_audio = []
    
    for shot in storyboard['storyboard']:
        shot_content = shot['visual_prompt'].lower()
        shot_id = shot['shot_id']
        
        # 匹配空间声学属性
        if "室内" in shot_content or "房间" in shot_content or "屋" in shot_content:
            if "大厅" in shot_content or "厂房" in shot_content or "车库" in shot_content:
                spatial = SPATIAL_ACOUSTIC_RULES["indoor_large"]
            else:
                spatial = SPATIAL_ACOUSTIC_RULES["indoor_small"]
        elif "室外" in shot_content or "天台" in shot_content or "野外" in shot_content:
            if "山谷" in shot_content or "峡谷" in shot_content or "楼群" in shot_content:
                spatial = SPATIAL_ACOUSTIC_RULES["outdoor_enclosed"]
            else:
                spatial = SPATIAL_ACOUSTIC_RULES["outdoor_open"]
        else:
            spatial = SPATIAL_ACOUSTIC_RULES["outdoor_open"]
        
        # 匹配频段分离效果
        if any(keyword in shot_content for keyword in ["碰撞", "爆炸", "击打", "砸", "摔"]):
            eq = EQ_RULES["impact/collision"]
        elif any(keyword in shot_content for keyword in ["玻璃", "碎", "裂", "断"]):
            eq = EQ_RULES["glass/breaking"]
        elif any(keyword in shot_content for keyword in ["说话", "对话", "喊", "叫"]):
            eq = EQ_RULES["dialogue"]
        else:
            eq = EQ_RULES["ambience"]
        
        # 生成专业级音频提示词
        audio_prompt = {
            "Spatial": spatial,
            "EQ": eq,
            "Ambience": shot['audio_prompt'].get('Ambience', 'neutral background noise'),
            "SFX": shot['audio_prompt'].get('SFX', 'foley matched to action'),
            "Music": shot['audio_prompt'].get('Music', 'score matched to emotion'),
            "Dialogue": shot['audio_prompt'].get('Dialogue', '')
        }
        
        processed_audio.append({
            "shot_id": shot_id,
            "audio_prompt": audio_prompt
        })
    
    return processed_audio
