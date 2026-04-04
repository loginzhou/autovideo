# -*- coding: utf-8 -*-
"""
Multimodal Consistency System V1.0 (多模态一致性系统)
确保文本、视觉、音频三个模态的内容保持一致性和协调性
支持跨模态语义对齐、情绪同步、风格统一
"""

# ==================== 模态间映射规则 ====================
MODALITY_MAPPING_RULES = {
    # 文本 -> 视觉
    "text_to_visual": {
        "emotion_keywords": {
            "joy": {
                "visual_elements": ["bright lighting", "warm colors", "open compositions", "upward angles"],
                "color_palette": ["warm yellows", "soft oranges", "sky blues", "fresh greens"],
                "lighting_quality": "high key, soft shadows, golden hour warmth"
            },
            "sadness": {
                "visual_elements": ["dim lighting", "cool tones", "closed/contained framing", "downward gazes"],
                "color_palette": ["muted blues", "greys", "desaturated earth tones"],
                "lighting_quality": "low key, flat light, overcast quality"
            },
            "anger": {
                "visual_elements": ["harsh shadows", "red/orange accents", "tight framing", "dynamic angles"],
                "color_palette": ["saturated reds", "deep oranges", "contrasting blacks"],
                "lighting_quality": "hard key light, high contrast, dramatic chiaroscuro"
            },
            "fear": {
                "visual_elements": ["deep shadows", "unknown spaces", "off-center composition", "limited visibility"],
                "color_palette": ["dark blues", "murky greens", "near-black shadows"],
                "lighting_quality": "single source, heavy shadows, unknown darkness"
            },
            "love": {
                "visual_elements": ["soft focus", "warm glow", "intimate framing", "gentle movements"],
                "color_palette": ["romantic pinks", "warm ambers", "soft purples"],
                "lighting_quality": "soft diffused, practical candles, warm fill"
            }
        },
        
        "action_to_camera": {
            "running_chase": {
                "camera_movement": "tracking shot, handheld energy, following subject",
                "shot_size": "medium to wide, showing environment context",
                "frame_rate": "normal or slight speed ramp for intensity"
            },
            "quiet_introspection": {
                "camera_movement": "static or imperceptible drift, slow dolly",
                "shot_size": "close up or medium close up, intimate distance",
                "frame_rate": "normal, emphasis on subtle performance"
            },
            "explosive_action": {
                "camera_movement": "shaky cam, quick pans, whip movements",
                "shot_size": "variable, cutting between wide impact and tight reaction",
                "frame_rate": "normal with speed ramps on impacts"
            },
            "tender_moment": {
                "camera_movement": "slow push in, gentle arc around subjects",
                "shot_size": "two shot transitioning to close up",
                "frame_rate": "slight slow motion (48fps) for dreamy quality"
            }
        }
    },
    
    # 文本 -> 音频
    "text_to_audio": {
        "emotion_to_music": {
            "triumph": {"genre": "epic orchestral", "tempo": "90-110 BPM", "key": "major", "dynamics": "crescendo to fortissimo"},
            "tension": {"genre": "minimalist suspense", "tempo": "accelerating 60-120 BPM", "key": "minor or dissonant", "dynamics": "building crescendo"},
            "tenderness": {"genre": "intimate chamber", "tempo": "60-75 BPM", "key": "major with extensions", "dynamics": "gentle swells"},
            "terror": {"genre": "horror atonal", "tempo": "irregular/rubato", "key": "chromatic or whole tone", "dynamics": "sudden bursts from silence"}
        },
        
        "environment_to_ambience": {
            "forest": {"base_ambient": "birds, wind through trees, leaves rustling", "reverb": "natural outdoor, medium decay"},
            "city_night": {"base_ambient": "distant traffic, occasional sirens, hum of city", "reverb": "urban canyon, longer decay"},
            "interior_room": {"base_ambient": "HVAC hum, electrical buzz, room tone", "reverb": "small room, short decay"},
            "underwater": {"base_ambient": "muffled bubbles, deep pressure, distant echoes", "reverb": "dense medium, unusual reflections"}
        },
        
        "dialogue_processing_by_emotion": {
            "whisper_intimacy": {"presence": "+4dB", "compression": "light", "proximity_effect": "emphasized", "breath audible": True},
            "shout_anger": {"presence": "+6dB", "compression": "heavy", "distortion_slight": "acceptable", "room_reflections": "audible"},
            "fear_trembling": {"presence": "+2dB", "compression": "moderate", "pitch_variation": "increased", "breathing": "rapid and audible"}
        }
    },
    
    # 视觉 -> 音频（反向验证）
    "visual_to_audio": {
        "lighting_to_audio": {
            "bright_daylight": {"eq": "bright and open, high frequency presence", "ambience_level": "higher, more active"},
            "dim_interior": {"eq": "warm and intimate, low-mid emphasis", "ambience_level": "lower, more contained"},
            "neon_night": {"eq": "synthetic highs, sub bass emphasis", "ambience_level": "medium, urban character"},
            "candlelit": {"eq": "very warm, rolled off highs", "ambience_level": "very low, intimate"}
        },
        
        "camera_movement_to_sound_design": {
            "static_composition": {"sound_field": "stable, centered focus", "movement_in_sound": "minimal"},
            "slow_dolly": {"sound_field": "gentle evolution, subtle perspective shift", "movement_in_sound": "smooth transitions"},
            "handheld_shaky": {"sound_field": "unstable, micro-fluctuations", "movement_in_sound": "subtle image wobble in reverb tail"},
            "fast_tracking": {"sound_field": "dynamic, doppler effects possible", "movement_in_sound": "whooshes, wind by mic"}
        }
    }
}

# ==================== 一致性检查规则 ====================
CONSISTENCY_CHECKS = {
    "emotion_alignment": {
        "description": "检查文本情绪与视觉/音频情绪是否一致",
        "threshold": 0.7,  # 相似度阈值
        "check_points": [
            "text_emotion vs visual_color_temperature",
            "text_emotion vs music_key_mode",
            "text_emotion vs camera_movement_energy",
            "text_emotion vs dialogue_delivery_style"
        ]
    },
    
    "narrative_continuity": {
        "description": "确保叙事元素在各模态中保持连贯",
        "check_points": [
            "character_appearance_consistency across shots",
            "location_details_match_between_visual_and_audio",
            "time_of_day_matches_lighting_and_ambience",
            "weather_conditions_coherent_across_modalities"
        ]
    },
    
    "stylistic_unity": {
        "description": "确保整体风格在所有模态中统一",
        "check_points": [
            "visual_grading_matches_music_production_style",
            "editing_rhythm_matches_musical_tempo",
            "transition_type_matches_audio_transition",
            "genre_conventions_respected_all_modalities"
        ]
    },
    
    "technical_sync": {
        "description": "技术层面的同步检查",
        "check_points": [
            "lip_sync_accuracy",
            "footstep_sync_with_movement",
            "action_impact_sync_with_sound_effects",
            "music_cue_timing_with_visual_beats"
        ]
    }
}

def check_multimodal_consistency(visual_config, audio_config, text_analysis):
    """
    检查多模态一致性
    
    Args:
        visual_config: 视觉配置字典
        audio_config: 音频配置字典  
        text_analysis: 文本分析结果
        
    Returns:
        dict: 包含一致性评分和问题列表
    """
    consistency_report = {
        "overall_score": 0,
        "details": {},
        "issues": [],
        "suggestions": []
    }
    
    scores = []
    
    # 1. 情绪一致性检查
    text_emotion = text_analysis.get("primary_emotion", "neutral")
    visual_emotion = extract_visual_emotion(visual_config)
    audio_emotion = extract_audio_emotion(audio_config)
    
    emotion_score = calculate_emotion_similarity(text_emotion, visual_emotion, audio_emotion)
    scores.append(emotion_score)
    consistency_report["details"]["emotion_alignment"] = {
        "score": emotion_score,
        "text": text_emotion,
        "visual": visual_emotion,
        "audio": audio_emotion
    }
    
    if emotion_score < CONSISTENCY_CHECKS["emotion_alignment"]["threshold"]:
        consistency_report["issues"].append(
            f"情绪不一致: 文本={text_emotion}, 视觉={visual_emotion}, 音频={audio_emotion}"
        )
    
    # 2. 风格一致性检查
    style_score = check_stylistic_consistency(visual_config, audio_config)
    scores.append(style_score)
    consistency_report["details"]["stylistic_unity"] = {"score": style_score}
    
    # 计算总体分数
    if scores:
        consistency_report["overall_score"] = sum(scores) / len(scores)
    
    return consistency_report

def extract_visual_emotion(visual_config):
    """从视觉配置中提取情绪信息"""
    if not visual_config:
        return "neutral"
    
    color_temp = str(visual_config.get("color_temperature", "")).lower()
    lighting = str(visual_config.get("lighting_setup", "")).lower()
    movement = str(visual_config.get("camera_movement", "")).lower()
    
    emotion_indicators = {
        "joy": ["warm", "bright", "golden", "happy", "uplifting"],
        "sadness": ["cool", "dim", "blue", "grey", "melancholy"],
        "anger": ["hard", "red", "contrast", "harsh", "aggressive"],
        "fear": ["dark", "shadow", "unknown", "suspense", "tense"],
        "love": ["soft", "warm", "intimate", "gentle", "romantic"]
    }
    
    scores = {}
    for emotion, keywords in emotion_indicators.items():
        score = sum(1 for kw in keywords if kw in f"{color_temp} {lighting} {movement}")
        scores[emotion] = score
    
    if scores and max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "neutral"

def extract_audio_emotion(audio_config):
    """从音频配置中提取情绪信息"""
    if not audio_config:
        return "neutral"
    
    music_style = str(audio_config.get("music_design", {}).get("music_style", "")).lower()
    tempo_range = audio_config.get("music_design", {}).get("tempo_range", [0, 0])
    
    emotion_indicators = {
        "joy": ["uplift", "major", "bright", "happy", "celebrat"],
        "sadness": ["sad", "minor", "slow", "mournful", "melanchol"],
        "anger": ["aggress", "dissonant", "fast", "harsh", "industrial"],
        "fear": ["horror", "suspense", "tension", "dark", "ominous"],
        "love": ["romant", "tender", "intimate", "soft", "gentle"]
    }
    
    scores = {}
    for emotion, keywords in emotion_indicators.items():
        score = sum(1 for kw in keywords if kw in music_style)
        scores[emotion] = score
    
    if scores and max(scores.values()) > 0:
        return max(scores, key=scores.get)
    return "neutral"

def calculate_emotion_similarity(text_emotion, visual_emotion, audio_emotion):
    """计算三模态情绪相似度"""
    similarity_matrix = {
        ("joy", "joy"): 1.0,
        ("joy", "love"): 0.8,
        ("joy", "triumph"): 0.7,
        ("sadness", "sadness"): 1.0,
        ("sadness", "nostalgia"): 0.7,
        ("anger", "anger"): 1.0,
        ("anger", "fear"): 0.5,
        ("fear", "fear"): 1.0,
        ("fear", "suspense"): 0.9,
        ("love", "love"): 1.0,
        ("love", "joy"): 0.8,
        ("neutral", "neutral"): 0.8
    }
    
    tv = similarity_matrix.get((text_emotion, visual_emotion), 0.3)
    ta = similarity_matrix.get((text_emotion, audio_emotion), 0.3)
    va = similarity_matrix.get((visual_emotion, audio_emotion), 0.3) if visual_emotion != audio_emotion else 1.0
    
    return (tv + ta + va) / 3

def check_stylistic_consistency(visual_config, audio_config):
    """检查风格一致性"""
    if not visual_config or not audio_config:
        return 0.7  # 默认中等分数
    
    director_style = visual_config.get("director_style", "")
    music_genre = audio_config.get("music_design", {}).get("music_style", "")
    
    # 风格匹配表（简化）
    style_matches = {
        "nolan": ["epic", "tense", "dramatic", "orchestral"],
        "miyazaki": ["orchestral", "whimsical", "gentle", "nature"],
        "wong_kar_wai": ["ambient", "nostalgic", "intimate", "mysterious"],
        "spielberg": ["orchestral", "emotional", "cinematic", "heroic"],
        "fincher": ["industrial", "electronic", "dark", "minimalist"]
    }
    
    matching_genres = style_matches.get(director_style.lower(), [])
    
    if matching_genres:
        match_score = sum(1 for genre in matching_genres if genre in music_genre.lower())
        return 0.5 + (match_score / len(matching_genres)) * 0.5
    
    return 0.6

def generate_consistency_fix_suggestions(consistency_report):
    """根据一致性报告生成修复建议"""
    suggestions = []
    
    for issue in consistency_report.get("issues", []):
        if "情绪不一致" in issue:
            suggestions.append({
                "type": "emotion_alignment",
                "priority": "high",
                "suggestion": "调整视觉色彩或音乐风格以匹配文本情绪",
                "specific_actions": [
                    "修改color_grade参数以匹配目标情绪",
                    "更换音乐为匹配情绪的genre和key",
                    "调整camera_movement的能量水平"
                ]
            })
    
    details = consistency_report.get("details", {})
    
    if details.get("stylistic_unity", {}).get("score", 1) < 0.6:
        suggestions.append({
            "type": "style_unification",
            "priority": "medium",
            "suggestion": "统一各模态的风格特征",
            "specific_actions": [
                "确认导演风格在各模态中的体现",
                "调整音乐制作风格以匹配视觉风格",
                "添加统一的后期处理特征"
            ]
        })
    
    return suggestions

if __name__ == "__main__":
    print("=" * 60)
    print("多模态一致性系统测试")
    print("=" * 60)
    
    # 测试一致性检查
    test_visual = {
        "director_style": "nolan",
        "color_temperature": "cool blue",
        "lighting_setup": "low key, high contrast",
        "camera_movement": "slow dolly in"
    }
    
    test_audio = {
        "music_design": {
            "music_style": "tense minimalist horror score",
            "tempo_range": [80, 100]
        }
    }
    
    test_text = {
        "primary_emotion": "suspense",
        "intensity": 0.8
    }
    
    report = check_multimodal_consistency(test_visual, test_audio, test_text)
    
    print(f"\n一致性报告:")
    print(f"  总体得分: {report['overall_score']:.2f}")
    print(f"  情绪对齐: {report['details']['emotion_alignment']}")
    
    if report["issues"]:
        print(f"\n发现的问题:")
        for issue in report["issues"]:
            print(f"  ⚠️ {issue}")
    
    suggestions = generate_consistency_fix_suggestions(report)
    if suggestions:
        print(f"\n修复建议:")
        for sug in suggestions:
            print(f"  💡 [{sug['priority'].upper()}] {sug['suggestion']}")
