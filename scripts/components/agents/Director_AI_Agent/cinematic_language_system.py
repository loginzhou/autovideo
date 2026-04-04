# -*- coding: utf-8 -*-
"""
Cinematic Language System V2.0 (电影级镜头语言系统)
好莱坞专业级镜头语言、光影塑形、运镜设计
支持多种电影风格：诺兰、宫崎骏、王家卫等
"""

# ==================== 电影导演风格库 ====================
DIRECTOR_STYLES = {
    "nolan": {
        "name": "克里斯托弗·诺兰",
        "description": "非线性叙事、IMAX摄影、实拍特效",
        "visual_characteristics": {
            "lens_preference": ["35mm", "70mm IMAX"],
            "depth_of_field": "deep to medium",
            "color_grading": "desaturated, high contrast, cool tones",
            "lighting_style": "practical lighting, naturalistic, high dynamic range",
            "camera_movement": ["dolly zoom", "tracking shot", "static composition"],
            "signature_techniques": [
                "cross-cutting between time periods",
                "practical effects over CGI",
                "in-camera effects",
                "long takes with complex blocking"
            ]
        },
        "emotional_mapping": {
            "tension": {
                "shot_type": "close_up to medium_shot",
                "lens": "50mm standard lens",
                "lighting": "low key, high contrast, single source",
                "movement": "slow dolly in, handheld subtle shake",
                "color": "cool blue/grey tones"
            },
            "revelation": {
                "shot_type": "wide shot to close_up (dolly zoom)",
                "lens": "24mm wide angle transitioning to 85mm portrait",
                "lighting": "dramatic key light, rim separation",
                "movement": "Vertigo effect (dolly zoom)",
                "color": "warm reveal from cold setup"
            },
            "action": {
                "shot_type": "medium shot, over the shoulder",
                "lens": "35mm prime, deep focus",
                "lighting": "high contrast, practical sources",
                "movement": "handheld tracking, steady cam follows",
                "color": "naturalistic, slightly desaturated"
            }
        }
    },
    
    "miyazaki": {
        "name": "宫崎骏",
        "description": "手绘美学、自然主义、飞行场景",
        "visual_characteristics": {
            "lens_preference": ["24mm", "35mm"],
            "depth_of_field": "deep focus for backgrounds",
            "color_grading": "vibrant greens and blues, warm golden hour",
            "lighting_style": "soft natural light, volumetric god rays",
            "camera_movement": ["crane shot", "aerial tracking", "smooth dolly"],
            "signature_techniques": [
                "ma (negative space/pause)",
                "detailed background artistry",
                "natural movement animation",
                "environmental storytelling"
            ]
        },
        "emotional_mapping": {
            "wonder": {
                "shot_type": "wide establishing shot, slow push in",
                "lens": "24mm wide angle, deep depth of field",
                "lighting": "golden hour, soft volumetric rays",
                "movement": "slow crane descent, gentle tracking",
                "color": "vibrant warm palette, rich greens"
            },
            "friendship": {
                "shot_type": "two shot, medium close up",
                "lens": "50mm standard, medium depth of field",
                "lighting": "soft diffused daylight, warm tones",
                "movement": "subtle dolly, static intimate moments",
                "color": "pastel warmth, soft saturation"
            },
            "conflict": {
                "shot_type": "dynamic angles, low and high perspectives",
                "lens": "35mm, variable depth of field",
                "lighting": "dramatic shadows, contrasting warm/cool",
                "movement": "dynamic tracking, quick cuts",
                "color": "intense saturated colors, high contrast"
            }
        }
    },
    
    "wong_kar_wai": {
        "name": "王家卫",
        "description": "碎片化叙事、抽帧技术、霓虹美学",
        "visual_characteristics": {
            "lens_preference": ["50mm", "85mm"],
            "depth_of_field": "extremely shallow",
            "color_grading": "saturated neon, green/magenta shifts",
            "lighting_style": "neon practical lights, colored gels",
            "camera_movement": ["step printing", "slow motion", "handheld"],
            "signature_techniques": [
                "step-printing (staccato movement)",
                "shallow focus isolation",
                "reflections and mirrors",
                "non-linear time structure"
            ]
        },
        "emotional_mapping": {
            "loneliness": {
                "shot_type": "extreme close up, isolated figure",
                "lens": "85mm portrait, extremely shallow DOF",
                "lighting": "single neon source, heavy shadow",
                "movement": "step-printed slow motion",
                "color": "green/magenta split, neon glow"
            },
            "longing": {
                "shot_type": "over shoulder through obstacles",
                "lens": "50mm, soft focus foreground",
                "lighting": "warm interior vs cool exterior",
                "movement": "slow tracking, voyeuristic angle",
                "color": "warm amber interior, blue exterior"
            },
            "melancholy": {
                "shot_type": "wide shot with small figure",
                "lens": "35mm, deep focus background",
                "lighting": "overcast flat light, muted tones",
                "movement": "static or very slow dolly",
                "color": "desaturated, slight color shift"
            }
        }
    },
    
    "spielberg": {
        "name": "史蒂文·斯皮尔伯格",
        "description": "经典好莱坞、情感共鸣、标志性镜头",
        "visual_characteristics": {
            "lens_preference": ["21mm", "35mm", "50mm"],
            "depth_of_field": "variable, often deep focus",
            "color_grading": "warm cinematic, film emulation",
            "lighting_style": "three-point lighting, motivated sources",
            "camera_movement": ["dolly in/out", "crane shots", "steadicam"],
            "signature_techniques": [
                "dolly into close-up for emotional beats",
                "foreground framing (over the shoulder objects)",
                "beam of light through darkness",
                "long takes with multiple actions"
            ]
        },
        "emotional_mapping": {
            "awe/wonder": {
                "shot_type": "low angle looking up, slow reveal",
                "lens": "21mm ultra wide, deep focus",
                "lighting": "backlit silhouette, rim light halo",
                "movement": "slow dolly back + crane rise",
                "color": "warm golden, cinematic film look"
            },
            "terror/fear": {
                "shot_type": "extreme close up of eyes, then wide",
                "lens": "50mm to 21mm pull back",
                "lighting": "single source, heavy shadows",
                "movement": "slow push in, then abrupt cut wide",
                "color": "cool desaturated, high contrast"
            },
            "joy/triumph": {
                "shot_type": "medium shot, hero centered",
                "lens": "35mm, balanced depth of field",
                "lighting": "bright key light, warm fill",
                "movement": "circular dolly around subject",
                "color": "vibrant saturated, warm tones"
            }
        }
    },
    
    "fincher": {
        "name": "大卫·芬奇",
        "description": "黑暗美学、精密控制、数字创新",
        "visual_characteristics": {
            "lens_preference": ["50mm", "85mm"],
            "depth_of_field": "precise control, often shallow",
            "color_grading": "teal/orange, desaturated skin tones",
            "lighting_style": "motivated practicals, low key",
            "camera_movement": ["micro-movements", "precision dolly", "static"],
            "signature_techniques": [
                "attenuated zoom (subtle digital zoom during take)",
                "split diopter (dual focus planes)",
                "precise camera movements",
                "dark atmospheric environments"
            ]
        },
        "emotional_mapping": {
            "paranoia": {
                "shot_type": "tight close ups, claustrophobic framing",
                "lens": "85mm, extremely shallow DOF",
                "lighting": "single overhead fluorescent, harsh shadows",
                "movement": "imperceptible micro-movements",
                "color": "cold teal/green, sickly skin tones"
            },
            "obsession": {
                "shot_type": "repetitive framing, ritualistic",
                "lens": "50mm, precise focus pulls",
                "lighting": "controlled studio, minimal variation",
                "movement": "mechanical precision, almost robotic",
                "color": "monochromatic shifts, selective color"
            },
            "violence": {
                "shot_type": "wide context then brutal detail",
                "lens": "24mm establishing to 85mm impact",
                "lighting": "harsh flash photography style",
                "movement": "abrupt cuts, jarring continuity",
                "color": "bleached, high contrast, clinical"
            }
        }
    }
}

# ==================== 高级情绪-镜头映射 ====================
EMOTIONAL_SHOT_MAPPING = {
    # 正面情绪
    "joy": {
        "primary_shot": "medium_close_up with smile",
        "alternative_shots": ["wide shot showing celebration", "two shot with friends"],
        "lens": "50mm standard, f/2.8",
        "lighting": "bright high key, warm 3200K, soft fill",
        "movement": "gentle circular dolly, handheld energy",
        "color_grade": "warm vibrant, boosted saturation +15%",
        "transition": "quick cut or match action"
    },
    "love": {
        "primary_shot": "close_up on eyes, then two shot",
        "alternative_shots": ["over shoulder through hair", "reflection in eyes"],
        "lens": "85mm portrait, f/1.4 extreme shallow DOF",
        "lighting": "soft key light, warm rim light, practical candles",
        "movement": "slow dolly in, breath-like micro-movements",
        "color_grade": "romantic warm, soft bloom, pastel tint",
        "transition": "dissolve or soft cut"
    },
    "triumph": {
        "primary_shot": "hero centered medium shot, arms raised",
        "alternative_shots": ["low angle heroic pose", "wide crowd reaction"],
        "lens": "35mm cinematic, f/4 balanced DOF",
        "lighting": "dramatic backlight, rim separation, god rays",
        "movement": "slow crane rise, triumphant push in",
        "color_grade": "golden hour warmth, cinematic contrast",
        "transition": "smash cut to celebration"
    },
    
    # 负面情绪
    "anger": {
        "primary_shot": "intense close_up, veins visible",
        "alternative_shots": ["low angle threatening", "POV smashing object"],
        "lens": "50mm compressed, f/2.8",
        "lighting": "hard side light, deep shadows, red undertone",
        "movement": "handheld aggressive, quick pans",
        "color_grade": "red/orange shift, high contrast, crushed blacks",
        "transition": "jump cut or glitch effect"
    },
    "fear": {
        "primary_shot": "ECU eyes darting, then what they see",
        "alternative_shots": ["subjective POV", "shadowy figure reveal"],
        "lens": "24mm wide for environment, 85mm for face",
        "lighting": "single source, harsh shadows, unknown darkness",
        "movement": "unsteady handheld, rapid breathing rhythm",
        "color_grade": "cold blue/green, desaturated, low key",
        "transition": "hard cut or shock flash"
    },
    "sadness": {
        "primary_shot": "profile close_up, tear track",
        "alternative_shots": ["isolated figure in wide space", "hands clutching"],
        "lens": "85mm portrait, f/1.8 shallow isolating",
        "lighting": "soft top light, gentle fill, melancholic grey",
        "movement": "almost static, imperceptible drift",
        "color_grade": "muted desaturated, cool blue bias, film grain",
        "transition": "slow dissolve or fade"
    },
    "despair": {
        "primary_shot": "wide shot, small figure overwhelmed",
        "alternative_shots": ["birdseye looking down", "crumbling close_up"],
        "lens": "16mm ultra wide, deep focus showing isolation",
        "lighting": "flat overcast, no direction, lifeless",
        "movement": "static or slow pull away (abandonment)",
        "color_grade": "heavily desaturated, near monochrome",
        "transition": "fade to black or prolonged hold"
    },
    
    # 复杂情绪
    "suspense": {
        "primary_shot": "off-center composition, negative space",
        "alternative_shots": ["door frame framing", "mirror reflection"],
        "lens": "35mm, f/5.6 deep focus for environment detail",
        "lighting": "low key, limited sources, shadows dominate",
        "movement": "slow creeping dolly, tension-building pan",
        "color_grade": "teal/orange split, high contrast",
        "transition": "prolonged hold then sudden cut"
    },
    "mystery": {
        "primary_shot": "partial reveal, obstruction in foreground",
        "alternative_shots": ["through curtain/blinds", "out of focus to sharp"],
        "lens": "50mm, rack focus from foreground to subject",
        "lighting": "chiaroscuro, smoke/haze, single beam",
        "movement": "deliberate slow, investigative feel",
        "color_grade": "sepia tint or selective color",
        "transition": "match cut or iris"
    },
    "nostalgia": {
        "primary_shot": "soft focus memory, dreamlike quality",
        "alternative_shots": ["super 8mm grain overlay", "sun-dappled childhood"],
        "lens": "vintage Cooke S4, f/2 warm softness",
        "lighting": "golden hour magic hour, lens flare welcome",
        "movement": "gentle floaty, slightly ethereal",
        "color_grade": "warm amber lift, faded highlights, soft contrast",
        "transition": "cross dissolve with light leak"
    }
}

# ==================== 场景类型智能匹配 ====================
SCENE_TYPE_RULES = {
    "interior_domestic": {
        "indicators": ["房间", "家", "客厅", "卧室", "厨房", "浴室"],
        "default_setup": {
            "lens": "35-50mm",
            "lighting": "practical lamps, window light",
            "movement": "natural handheld or smooth dolly",
            "color_temp": "warm 3000-4000K"
        },
        "emotional_variants": {
            "cozy": {"lighting": "warm tungsten, soft shadows", "movement": "gentle"},
            "tense": {"lighting": "harsh overhead, stark", "movement": "static tense"}
        }
    },
    
    "office_professional": {
        "indicators": ["办公室", "公司", "会议室", "写字楼"],
        "default_setup": {
            "lens": "50mm standard",
            "lighting": "fluorescent panels, cool white",
            "movement": "static or controlled dolly",
            "color_temp": "cool 4500-5500K"
        },
        "emotional_variants": {
            "power": {"angle": "low angle authority", "lighting": "key light from above"},
            "oppressed": {"angle": "high angle diminutive", "lighting": "fluorescent flicker"}
        }
    },
    
    "urban_exterior": {
        "indicators": ["街道", "城市", "广场", "建筑外"],
        "default_setup": {
            "lens": "24-35mm wide",
            "lighting": "available light, mixed sources",
            "movement": "tracking or steadicam",
            "color_temp": "variable 3200-6500K"
        },
        "time_of_day": {
            "golden_hour": {"lighting": "warm directional long shadows", "color": "amber gold"},
            "night": {"lighting": "neon signs, streetlights", "color": "neon saturated"},
            "overcast": {"lighting": "flat soft diffuse", "color": "cool neutral"}
        }
    },
    
    "nature_wilderness": {
        "indicators": ["森林", "山", "河", "野外", "自然"],
        "default_setup": {
            "lens": "24mm landscape or 70-200mm telephoto",
            "lighting": "natural sunlight, dappled canopy",
            "movement": "crane or drone, sweeping reveals",
            "color_temp": "variable with weather"
        },
        "weather_conditions": {
            "clear": {"lighting": "bright direct sun, hard shadows", "color": "vibrant saturated"},
            "rain": {"lighting": "diffused overcast, wet reflections", "color": "cool desaturated"},
            "fog": {"lighting": "flat mysterious, atmospheric haze", "color": "muted grey-blue"}
        }
    },
    
    "fantastical_magical": {
        "indicators": ["魔法", "仙境", "异世界", "超能力"],
        "default_setup": {
            "lens": "varies with scale, often wide for scope",
            "lighting": "supernatural sources, bioluminescence",
            "movement": "ethereal floating, impossible moves",
            "color_temp": "fantasy palette, non-realistic"
        },
        "magic_types": {
            "fire_magic": {"lighting": "warm orange/red glow, embers", "effects": "particles, heat distortion"},
            "ice_magic": {"lighting": "cool blue/cyan, frost particles", "effects": "breath fog, ice crystals"},
            "nature_magic": {"lighting": "green organic glow, vines", "effects": "floating pollen, growth"}
        }
    }
}

# ==================== 镜头运动曲线库 ====================
MOVEMENT_CURVES = {
    "linear_constant": {
        "description": "匀速直线运动，稳定客观",
        "use_cases": ["documentary observation", "surveillance feel", "clinical precision"],
        "easing_function": "none (constant velocity)"
    },
    
    "ease_in_slow": {
        "description": "慢入加速，建立紧张感",
        "use_cases": ["approaching threat", "building revelation", "drawing attention"],
        "easing_function": "quadratic ease-in"
    },
    
    "ease_out_slow": {
        "description": "快出减速，强调到达",
        "use_cases": ["arriving at destination", "settling on subject", "gentle landing"],
        "easing_function": "quadratic ease-out"
    },
    
    "ease_in_out_smooth": {
        "description": "平滑加减速，自然有机",
        "use_cases": ["following character", "emotional moments", "conversational"],
        "easing_function": "cubic ease-in-out"
    },
    
    "overshoot_bounce": {
        "description": "过冲回弹，活力动感",
        "use_cases": ["comedic timing", "energetic characters", "youthful exuberance"],
        "easing_function": "elastic overshoot"
    },
    
    "exponential_dramatic": {
        "description": "指数加速，戏剧性冲击",
        "use_cases": ["action climax", "sudden realization", "shock moments"],
        "easing_function": "exponential curve"
    },
    
    "sinusoidal_organic": {
        "description": "正弦波动，呼吸节奏",
        "use_cases": ["meditative scenes", "natural observation", "dream sequences"],
        "easing_function": "sine wave modulation"
    },
    
    "jitter_nervous": {
        "description": "随机抖动，不安焦虑",
        "use_cases": ["paranoia", "drug effects", "nervousness", "handheld reality"],
        "easing_function": "random noise overlay"
    }
}

def get_cinematic_shot(emotion=None, scene_type=None, director_style="nolan", intensity=7):
    """
    获取电影级镜头参数
    
    Args:
        emotion: 情绪标签 (joy, fear, anger, etc.)
        scene_type: 场景类型 (interior_domestic, urban_exterior, etc.)
        director_style: 导演风格 (nolan, miyazaki, wong_kar_wai, etc.)
        intensity: 强度等级 1-10
    
    Returns:
        dict: 完整的镜头参数配置
    """
    shot_config = {
        "director_style": director_style,
        "emotion": emotion,
        "scene_type": scene_type,
        "intensity": intensity,
        
        # 基础参数（会被后续覆盖）
        "shot_type": None,
        "lens": None,
        "aperture": None,
        "focal_length": None,
        "lighting_setup": None,
        "color_temperature": None,
        "camera_movement": None,
        "movement_curve": None,
        "color_grading": None,
        "transition": None,
        "special_effects": [],
        "audio_cues": []
    }
    
    # 1. 应用导演风格基础
    if director_style in DIRECTOR_STYLES:
        style = DIRECTOR_STYLES[director_style]
        shot_config["style_name"] = style["name"]
        shot_config["visual_characteristics"] = style["visual_characteristics"]
        
        # 如果有对应情绪，应用导演的情绪映射
        if emotion and emotion.lower() in style.get("emotional_mapping", {}):
            emotion_config = style["emotional_mapping"][emotion.lower()]
            shot_config.update(emotion_config)
    
    # 2. 应用通用情绪映射（如果导演风格没有覆盖）
    if not shot_config.get("shot_type") and emotion and emotion.lower() in EMOTIONAL_SHOT_MAPPING:
        emotion_shot = EMOTIONAL_SHOT_MAPPING[emotion.lower()]
        shot_config["shot_type"] = emotion_shot["primary_shot"]
        shot_config["lens"] = emotion_shot.get("lens")
        shot_config["lighting_setup"] = emotion_shot.get("lighting")
        shot_config["camera_movement"] = emotion_shot.get("movement")
        shot_config["color_grading"] = emotion_shot.get("color_grade")
        shot_config["transition"] = emotion_shot.get("transition")
    
    # 3. 应用场景类型规则
    if scene_type and scene_type in SCENE_TYPE_RULES:
        scene_rules = SCENE_TYPE_RULES[scene_type]
        default_setup = scene_rules.get("default_setup", {})
        
        # 合并场景默认设置（不覆盖已设置的值）
        for key, value in default_setup.items():
            if not shot_config.get(key):
                shot_config[key] = value
    
    # 4. 根据强度调整参数
    shot_config = adjust_for_intensity(shot_config, intensity)
    
    return shot_config

def adjust_for_intensity(shot_config, intensity):
    """
    根据强度等级调整镜头参数
    强度 1-10: 1最温和，10最极端
    """
    if intensity <= 3:
        # 低强度：平静、稳定、柔和
        if not shot_config.get("aperture"):
            shot_config["aperture"] = f"f/{4 + (3-intensity)}"
        shot_config["movement_curve"] = "ease_in_out_smooth"
        shot_config["special_effects"].append("subtle_film_grain")
        
    elif intensity <= 6:
        # 中等强度：正常、平衡
        if not shot_config.get("aperture"):
            shot_config["aperture"] = "f/2.8"
        shot_config["movement_curve"] = "linear_constant"
        
    elif intensity <= 8:
        # 高强度：动态、对比强烈
        if not shot_config.get("aperture"):
            shot_config["aperture"] = "f/2.0"
        shot_config["movement_curve"] = "ease_in_slow"
        shot_config["contrast_boost"] = "+20%"
        
    else:
        # 极高强度：极端、冲击力强
        if not shot_config.get("aperture"):
            shot_config["aperture"] = "f/1.4"
        shot_config["movement_curve"] = "exponential_dramatic"
        shot_config["contrast_boost"] = "+40%"
        shot_config["saturation_shift"] = "+25%"
        if intensity >= 9:
            shot_config["special_effects"].extend(["lens_flare", "motion_blur"])
    
    return shot_config

def generate_cinematic_prompt(shot_config, scene_description="", character_action=""):
    """
    生成电影级视觉提示词
    """
    prompt_parts = []
    
    # 1. 导演风格描述
    if shot_config.get("style_name"):
        prompt_parts.append(f"Shot in the style of {shot_config['style_name']}")
    
    # 2. 镜头类型和焦段
    if shot_config.get("shot_type"):
        prompt_parts.append(f"{shot_config['shot_type']}")
    if shot_config.get("lens"):
        prompt_parts.append(f"{shot_config['lens']}")
    if shot_config.get("aperture"):
        prompt_parts.append(f"{shot_config['aperture']}")
    
    # 3. 光影设置
    if shot_config.get("lighting_setup"):
        prompt_parts.append(f"{shot_config['lighting_setup']}")
    if shot_config.get("color_temperature"):
        prompt_parts.append(f"{shot_config['color_temperature']} color temperature")
    
    # 4. 运镜方式
    if shot_config.get("camera_movement"):
        prompt_parts.append(f"{shot_config['camera_movement']} camera movement")
    if shot_config.get("movement_curve"):
        prompt_parts.append(f"{shot_config['movement_curve']} easing")
    
    # 5. 色彩分级
    if shot_config.get("color_grading"):
        prompt_parts.append(f"Color graded: {shot_config['color_grading']}")
    
    # 6. 场景内容
    if scene_description:
        prompt_parts.append(scene_description)
    if character_action:
        prompt_parts.append(character_action)
    
    # 7. 特殊效果
    if shot_config.get("special_effects"):
        effects_str = ", ".join(shot_config["special_effects"])
        prompt_parts.append(f"Visual effects: {effects_str}")
    
    # 组合提示词
    full_prompt = ", ".join(prompt_parts)
    
    # 添加质量后缀
    full_prompt += " --ar 9:16 --v 6.0 --style raw --q 2"
    
    return full_prompt

if __name__ == "__main__":
    # 测试示例
    print("=" * 60)
    print("电影级镜头语言系统测试")
    print("=" * 60)
    
    # 测试1: 诺兰风格的紧张场景
    shot1 = get_cinematic_shot(
        emotion="suspense",
        scene_type="urban_exterior",
        director_style="nolan",
        intensity=8
    )
    print("\n测试1: 诺兰风格 - 紧张悬疑")
    print(generate_cinematic_prompt(shot1, "Rain-soaked alleyway at night", "Detective cautiously approaching door"))
    
    # 测试2: 宫崎骏风格的 wonder 场景
    shot2 = get_cinematic_shot(
        emotion="wonder",
        scene_type="nature_wilderness",
        director_style="miyazaki",
        intensity=5
    )
    print("\n\n测试2: 宫崎骏风格 - 奇迹 wonder")
    print(generate_cinematic_prompt(shot2, "Ancient forest with floating islands", "Young girl discovering magical creatures"))
    
    # 测试3: 王家卫风格的孤独
    shot3 = get_cinematic_shot(
        emotion="loneliness",
        scene_type="interior_domestic",
        director_style="wong_kar_wai",
        intensity=7
    )
    print("\n\n测试3: 王家卫风格 - 孤独")
    print(generate_cinematic_prompt(shot3, "Small apartment room at 3am", "Man sitting alone by window watching rain"))
