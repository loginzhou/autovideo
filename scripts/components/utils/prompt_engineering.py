# 专业提示词工程模块
# 包含影视专业术语库和提示词模板

# 影视专业术语库
CINEMATIC_TERMS = {
    # 镜头类型
    "shot_types": {
        "extreme_close_up": "Extreme close-up (ECU) - focuses on a small detail",
        "close_up": "Close-up (CU) - focuses on character's face",
        "medium_close_up": "Medium close-up (MCU) - shows character from chest up",
        "medium_shot": "Medium shot (MS) - shows character from waist up",
        "long_shot": "Long shot (LS) - shows full body and surroundings",
        "extreme_long_shot": "Extreme long shot (ELS) - shows vast environment",
        "two_shot": "Two-shot - shows two characters together",
        "group_shot": "Group shot - shows multiple characters",
        "over_the_shoulder": "Over-the-shoulder (OTS) - shot from behind one character",
        "point_of_view": "Point-of-view (POV) - shot from character's perspective",
        "push_in": "Push-in - camera moves towards subject",
        "pull_out": "Pull-out - camera moves away from subject",
        "tracking_shot": "Tracking shot - camera follows subject",
        "dolly_shot": "Dolly shot - camera moves on a track",
        "crane_shot": "Crane shot - camera moves up and down",
        "handheld": "Handheld shot - shaky, realistic movement",
        "static": "Static shot - no camera movement"
    },
    
    # 镜头角度
    "camera_angles": {
        "eye_level": "Eye level - natural, neutral perspective",
        "low_angle": "Low angle - makes subject appear powerful",
        "high_angle": "High angle - makes subject appear vulnerable",
        "dutch_angle": "Dutch angle - tilted, creates unease",
        "over_the_shoulder": "Over-the-shoulder - conversational perspective",
        "birdseye": "Bird's eye view - top-down perspective",
        "wormseye": "Worm's eye view - bottom-up perspective",
        "profile": "Profile - side view of subject",
        "three_quarter": "Three-quarter view - angled view",
        "frontal": "Frontal - direct view of subject"
    },
    
    # 灯光
    "lighting": {
        "natural": "Natural lighting - using available light",
        "studio": "Studio lighting - controlled artificial light",
        "dramatic": "Dramatic lighting - high contrast",
        "chiaroscuro": "Chiaroscuro - strong light/dark contrast",
        "backlit": "Backlit - light from behind subject",
        "side_lighting": "Side lighting - highlights texture and shape",
        "top_lighting": "Top lighting - harsh, unflattering",
        "under_lighting": "Under lighting - eerie, unnatural",
        "soft_lighting": "Soft lighting - diffused, gentle",
        "hard_lighting": "Hard lighting - direct, sharp shadows",
        "motivated_lighting": "Motivated lighting - appears to have natural source",
        "practical_lighting": "Practical lighting - visible light sources in scene"
    },
    
    # 运镜
    "camera_movement": {
        "pan": "Pan - horizontal camera movement",
        "tilt": "Tilt - vertical camera movement",
        "zoom": "Zoom - change in focal length",
        "dolly": "Dolly - camera moves towards/away from subject",
        "tracking": "Tracking - camera follows subject's movement",
        "crane": "Crane - camera moves up/down/sideways",
        "handheld": "Handheld - shaky, intimate movement",
        "steadicam": "Steadicam - smooth movement while walking",
        "dolly_zoom": "Dolly zoom - simultaneous dolly and zoom",
        "whip_pan": "Whip pan - fast horizontal movement"
    },
    
    # 转场
    "transitions": {
        "cut": "Cut - direct transition between shots",
        "fade_to_black": "Fade to black - gradual transition to black",
        "fade_in": "Fade in - gradual transition from black",
        "dissolve": "Dissolve - gradual transition between shots",
        "wipe": "Wipe - one shot replaces another with a line",
        "cross_fade": "Cross fade - simultaneous fade in/out",
        "match_cut": "Match cut - transition between similar shapes/movements",
        "j_cut": "J cut - audio from next shot starts before video",
        "l_cut": "L cut - video cuts but audio continues",
        "flash_cut": "Flash cut - rapid succession of shots",
        "smash_cut": "Smash cut - abrupt transition for effect"
    },
    
    # 蒙太奇
    "montage": {
        "parallel_montage": "Parallel montage - simultaneous events",
        "cross_cutting": "Cross-cutting - alternating between scenes",
        "metaphorical_montage": "Metaphorical montage - symbolic images",
        "rhythmic_montage": "Rhythmic montage - based on visual rhythm",
        "serial_montage": "Serial montage - linear sequence of events"
    },
    
    # 场景类型
    "scenes": {
        "indoor": "Indoor - inside a building or structure",
        "outdoor": "Outdoor - outside in natural environment",
        "urban": "Urban - city or town setting",
        "rural": "Rural - countryside or natural setting",
        "interior": "Interior - inside a specific space",
        "exterior": "Exterior - outside a specific structure"
    },
    
    # 情绪类型
    "emotions": {
        "happy": "Happy - positive, joyful",
        "sad": "Sad - melancholy, grief",
        "angry": "Angry - intense, hostile",
        "fearful": "Fearful - scared, anxious",
        "surprised": "Surprised - shocked, astonished",
        "disgusted": "Disgusted - repulsed, revolted",
        "neutral": "Neutral - calm, composed",
        "tense": "Tense - nervous, suspenseful",
        "romantic": "Romantic - loving, intimate",
        "epic": "Epic - grand, monumental"
    }
}

# 提示词模板
PROMPT_TEMPLATES = {
    # 视觉提示词模板
    "visual": "(Masterpiece:1.2), (ultra-detailed:1.2), 9:16 vertical composition, {subject}, {traits}, {scene}, {lens}, {lighting}, {camera_angle}, shot on ARRI Alexa Mini, cinematic lighting, professional color grading",
    
    # 视频提示词模板
    "video": "{visual_prompt}, {camera_movement}, motion_intensity: {motion_intensity}, motion_type: {motion_type}, {physics_effect}, {montage_type}, smooth transitions, professional cinematography",
    
    # 音频提示词模板
    "audio": {
        "Ambience": "{ambience}",
        "SFX": "{sfx}",
        "Music": "{music_style}, BPM {bpm}",
        "Dialogue": "{dialogue}, clear audio, professional recording"
    },
    
    # 场景特定提示词
    "scenes": {
        "action": "Fast-paced, dynamic, high energy, motion blur, realistic physics",
        "dialogue": "Intimate, focused, clear facial expressions, natural lighting",
        "emotional": "Dramatic lighting, close-ups, subtle movements, meaningful expressions",
        "epic": "Wide shots, grand scale, atmospheric, detailed environment"
    },
    
    # 风格特定提示词
    "styles": {
        "cinematic": "Cinematic, film grain, depth of field, color grading, professional lighting",
        "realistic": "Photorealistic, high detail, natural lighting, authentic textures",
        "stylized": "Stylized, artistic, unique color palette, creative composition",
        "dark": "Dark, moody, low key lighting, high contrast, atmospheric",
        "bright": "Bright, vibrant, high key lighting, saturated colors, cheerful"
    }
}

# 情绪-镜头映射
EMOTION_SHOT_MAPPING = {
    "happy": {
        "shot_type": ["medium_shot", "two_shot", "long_shot"],
        "camera_angle": ["eye_level", "slightly_high_angle"],
        "lighting": ["natural", "bright", "soft_lighting"],
        "camera_movement": ["smooth", "steady", "slow_pan"]
    },
    "sad": {
        "shot_type": ["close_up", "medium_close_up"],
        "camera_angle": ["high_angle"],
        "lighting": ["soft_lighting", "low_key"],
        "camera_movement": ["slow", "gentle", "static"]
    },
    "angry": {
        "shot_type": ["close_up", "extreme_close_up"],
        "camera_angle": ["low_angle"],
        "lighting": ["hard_lighting", "high_contrast"],
        "camera_movement": ["abrupt", "shaky", "fast"]
    },
    "fearful": {
        "shot_type": ["close_up", "point_of_view"],
        "camera_angle": ["dutch_angle", "high_angle"],
        "lighting": ["low_key", "chiaroscuro"],
        "camera_movement": ["slow", "tense", "steady"]
    },
    "surprised": {
        "shot_type": ["close_up", "medium_shot"],
        "camera_angle": ["eye_level"],
        "lighting": ["high_contrast", "dramatic"],
        "camera_movement": ["abrupt", "fast", "zoom"]
    }
}

# 场景-镜头映射
SCENE_SHOT_MAPPING = {
    "action": {
        "shot_type": ["medium_shot", "long_shot", "tracking_shot"],
        "camera_angle": ["eye_level", "low_angle"],
        "lighting": ["natural", "hard_lighting"],
        "camera_movement": ["dynamic", "fast", "shaky"]
    },
    "dialogue": {
        "shot_type": ["close_up", "medium_close_up", "over_the_shoulder"],
        "camera_angle": ["eye_level"],
        "lighting": ["soft_lighting", "natural"],
        "camera_movement": ["static", "slow_pan"]
    },
    "intimate": {
        "shot_type": ["close_up", "medium_close_up"],
        "camera_angle": ["eye_level", "slightly_low_angle"],
        "lighting": ["soft_lighting", "warm"],
        "camera_movement": ["slow", "gentle", "dolly"]
    },
    "epic": {
        "shot_type": ["long_shot", "extreme_long_shot", "crane_shot"],
        "camera_angle": ["birdseye", "low_angle"],
        "lighting": ["natural", "dramatic"],
        "camera_movement": ["slow", "steady", "crane"]
    }
}

def generate_visual_prompt(subject, traits, scene, lens, lighting, camera_angle, style="cinematic"):
    """生成视觉提示词"""
    prompt = PROMPT_TEMPLATES["visual"].format(
        subject=subject,
        traits=traits,
        scene=scene,
        lens=lens,
        lighting=lighting,
        camera_angle=camera_angle
    )
    if style in PROMPT_TEMPLATES["styles"]:
        prompt += ", " + PROMPT_TEMPLATES["styles"][style]
    prompt += " --ar 9:16"
    return prompt

def generate_video_prompt(visual_prompt, camera_movement, motion_intensity, motion_type, physics_effect, montage_type=""):
    """生成视频提示词"""
    prompt = PROMPT_TEMPLATES["video"].format(
        visual_prompt=visual_prompt.replace(" --ar 9:16", ""),
        camera_movement=camera_movement,
        motion_intensity=motion_intensity,
        motion_type=motion_type,
        physics_effect=physics_effect,
        montage_type=montage_type
    )
    prompt += " --ar 9:16"
    return prompt

def generate_audio_prompt(ambience, sfx, music_style, bpm, dialogue):
    """生成音频提示词"""
    return {
        "Ambience": PROMPT_TEMPLATES["audio"]["Ambience"].format(ambience=ambience),
        "SFX": PROMPT_TEMPLATES["audio"]["SFX"].format(sfx=sfx),
        "Music": PROMPT_TEMPLATES["audio"]["Music"].format(music_style=music_style, bpm=bpm),
        "Dialogue": PROMPT_TEMPLATES["audio"]["Dialogue"].format(dialogue=dialogue)
    }

def get_shot_parameters_by_emotion(emotion):
    """根据情绪获取镜头参数"""
    return EMOTION_SHOT_MAPPING.get(emotion, EMOTION_SHOT_MAPPING["neutral"])

def get_shot_parameters_by_scene(scene_type):
    """根据场景类型获取镜头参数"""
    return SCENE_SHOT_MAPPING.get(scene_type, SCENE_SHOT_MAPPING["dialogue"])
