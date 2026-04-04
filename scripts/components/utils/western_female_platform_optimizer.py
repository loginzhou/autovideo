# -*- coding: utf-8 -*-
"""
Western Female Audience TikTok/Facebook Optimization System V1.0
(欧美女性受众 TikTok/Facebook 短视频优化系统)

针对目标受众: 18-45岁欧美女性
主要平台: TikTok (15-60s), Facebook Reels (30-90s), Instagram Reels (30-90s)
核心需求: 情感共鸣、视觉美学、身份认同、社交分享性

内容策略:
- 浪漫/情感 (Romance/Emotional Drama) - 40%
- 奇幻/超自然 (Fantasy/Paranormal) - 25%  
- 都市/职场 (Urban/Career Woman) - 20%
- 悬疑/惊悚 (Suspense/Thriller) - 15%

文化适配要点:
- 西方叙事习惯 (Show Don't Tell, Character-Driven)
- 避免过度东方化表达 (No excessive Eastern tropes)
- 符合西方女性价值观 (Independence, Self-discovery, Empowerment)
- 视觉审美匹配 (Western beauty standards, diverse representation)
"""

# ==================== 平台特性分析 ====================
PLATFORM_SPECS = {
    "tiktok": {
        "name": "TikTok",
        "duration_optimal": [15, 60],        # 最佳时长(秒)
        "duration_max": 180,                # 最大时长
        "aspect_ratio": "9:16",            # 竖屏
        "fps": [24, 30, 60],
        
        # TikTok特有的节奏要求
        "rhythm_profile": {
            "hook_critical": True,           # 前1-3秒决定生死
            "beat_drop": 0.5,                # 节拍间隔(秒)
            "visual_changes_min": 8,         # 每8秒至少一个视觉变化
            "text_on_screen_max": 0.6,      # 字幕最多占60%时间
            "music_sync_essential": True,     # 必须与音乐节奏同步
            "trend_sensitivity": "high"       # 对趋势高度敏感
        },
        
        # TikTok热门内容模式
        "winning_patterns": [
            {
                "pattern": "Emotional Rollercoaster",
                "description": "情绪过山车：甜→虐→更虐→治愈",
                "structure": ["cute_opening", "sudden_twist", "emotional_climax", "hopeful_or_devastating_end"],
                "engagement_driver": "评论讨论剧情走向",
                "shareability": "high"
            },
            {
                "pattern": "Satisfying Revenge/Payoff",
                "description": "复仇/打脸爽文，压抑后爆发",
                "structure": ["oppression_buildup", "breaking_point", "powerful_climax", "triumphant_resolution"],
                "engagement_driver": "爽感释放",
                "shareability": "very_high"
            },
            {
                "pattern": "Mystery/Cliffhanger Loop",
                "description": "悬疑循环，每集结尾留大钩子",
                "structure": ["intriguing_setup", "clues_dropped", "shocking_reveal", "bigger_mystery"],
                "engagement_driver": "猜测讨论",
                "shareability": "high"
            },
            {
                "pattern": "Aesthetic/Vibes Focus",
                "description": "纯美学享受，氛围感强",
                "structure": ["visually_stunning", "mood_immersion", "subtle_narrative", "lingering_feeling"],
                "engagement_driver": "收藏/设为壁纸",
                "shareability": "medium-high"
            }
        ],
        
        # 音频要求
        "audio_requirements": {
            "music_trend_awareness": "CRITICAL",   # 必须用TikTok流行音乐或原创BGM
            "voiceover_style": "conversational/natural", # 自然对话式旁白
            "sound_effects": "trending_sounds",      # 使用平台流行音效
            "volume_music_balance": "music_60_voice_40" # 音乐略大于人声
        }
    },
    
    "facebook_reels": {
        "name": "Facebook Reels/Instagram Reels",
        "duration_optimal": [30, 90],
        "duration_max": 180,
        "aspect_ratio": "9:16",
        "fps": [24, 30],
        
        "rhythm_profile": {
            "hook_critical": True,
            "beat_drop": 2,                  # 比TikTok慢一些
            "visual_changes_min": 5,          # 可以稍慢
            "text_on_screen_max": 0.7,
            "music_sync_important": True,
            "narrative_depth": "deeper"           # 可以承载更深的故事
        },
        
        "winning_patterns": [
            {
                "pattern": "Character Study",
                "description": "深度角色刻画，心理描写",
                "engagement_driver": "情感共鸣+认同"
            },
            {
                "pattern": "Lifestyle Aspiration",
                "description": "理想生活展示，激励人心",
                "engagement_driver": "向往+收藏"
            }
        ],
        
        "audio_requirements": {
            "music_trend_awareness": "moderate",
            "voiceover_style": "cinematic/polished",
            "sound_effects": "professional_grade",
            "volume_music_balance": "balanced"
        }
    }
}

# ==================== 欧美女性受众偏好分析 ====================
AUDIENCE_PREFERENCES = {
    "demographics": {
        "core_age_range": [18, 35],
        "secondary_age_range": [36, 45],
        "geographic_focus": "US, UK, Canada, Australia, Western Europe",
        "language": "English (primary), Spanish (growing)",
        "education_level": "college-educated majority",
        "income_level": "middle to upper-middle class"
    },
    
    "psychographics": {
        "values_prioritized": [
            "independence & self-reliance",     # 独立自主
            "authenticity & vulnerability",     # 真实脆弱性
            "empowerment & growth",            # 成长赋能
            "connection & community",           # 连接与社群
            "aesthetic appreciation",           # 审美欣赏
            "social consciousness"               # 社会意识
        ],
        
        "fears_triggers": [
            "being judged or criticized",        # 被评判
            "missing out (FOMO)",                 # 错失恐惧
            "losing control",                    # 失去控制
            "abandonment/rejection",             # 被抛弃
            "failure to achieve goals"           # 目标失败
        ],
        
        "aspirations": [
            "finding true love/connection",     # 找到真爱
            "career success on own terms",       # 事业成功
            "personal transformation",            # 个人转变
            "making a difference",              # 有意义的影响
            "living authentically"              # 真实地活着
        ]
    },
    
    "content_consumption_habits": {
        "peak_times": ["lunch break (12-2pm)", "commute (5-7pm)", "bedtime wind-down (9-11pm)"],
        "device_preference": "mobile-first (smartphone)",
        "attention_span": "short (scroll-fast, decide in <3 seconds to watch)",
        "sharing_motivations": [
            "this represents me/my feelings",   # 代表我的感受
            "my friends need to see this",       # 朋友必须看
            "this is so aesthetically pleasing", # 太好看了
            "I want to remember this moment"     # 记住这一刻
        ]
    },
    
    "genre_preferences_tier1": {  # 最受欢迎
        "romance_contemporary": {"appeal": "emotional_connection", "viral_potential": "very_high"},
        "paranormal_romance": {"appeal": "escapism_fantasy", "viral_potential": "high"},
        "urban_professional_woman": {"appeal": "aspiration_identification", "viral_potential": "high"},
        "dark_academia_romance": {"appeal": "intellectual_emotional_mix", "viral_potential": "medium-high"}
    },
    
    "genre_preferences_tier2": {
        "mystery_thriller": {"appeal": "curiosity_engagement", "viral_potential": "high"},
        "fantasy_epic": {"appeal": "wonder_scale", "viral_potential": "medium"},
        "historical_romance": {"appeal": "nostalgia_beauty", "viral_potential": "medium"}
    },
    
    "visual_aesthetic_preferences": {
        "color_palette": {
            "warm_golden_hour": {"popularity": "very_high", "mood": "romantic_nostalgic"},
            "cool_moody_blues": {"popularity": "high", "mood": "melancholic_introspective"},
            "soft_pastels": {"popularity": "high", "mood": "gentle_dreamy"},
            "neon_vibrant": {"popularity": "medium", "mood": "energetic_modern"},
            "dark_moody": {"popularity": "medium-high", "mood": "dramatic_intense"}
        },
        
        "character_design": {
            "diverse_representation": "ESSENTIAL",  # 多样化至关重要
            "realistic_body_types": "preferred over idealized",  # 真实体型优于完美化
            "fashion_conscious": "characters should look stylish/current",  # 时尚意识
            "distinctive_features": "memorable faces/features help recognition"  # 特征鲜明易识别
        },
        
        "setting_environments": {
            "aesthetic_interiors": {"appeal": "aspiration_living_spaces", "examples": ["loft_apartment", "cozy_cafe", "boutique_hotel"]},
            "natural_scenic": {"appeal": "peaceful_escape", "examples": ["flower_fields", "ocean_sunsets", "forest_paths"]},
            "urban_chic": {"appeal": "modern_aspiration", "examples": ["rooftop_bars", "art_galleries", "design_offices"]}
        }
    }
}

# ==================== 内容策略模板 ====================
CONTENT_STRATEGIES = {
    "romance_domination_strategy": {
        "name": "浪漫征服策略 (Romance Domination)",
        "target_emotion": "butterflies_excitement_longing",
        "character_archetypes": {
            "female_lead": {
                "type": "relatable_but_aspiring",
                "traits": ["independent", "slightly_flawed", "emotionally_available", "has_secret_strength"],
                "flaws_that_make_her_relatable": ["trust_issues_from_past", "workaholic_tendencies", "afraid_of_vulnerability"]
            },
            "male_lead": {
                "type": "compelling_but_problematic",
                "traits": ["mysterious", "successful", "emotionally_guarded", "unexpectedly_tender"],
                "initial_flaw": ["arrogant", "emotionally_unavailable", "has_dark_secret"]
            }
        },
        "beat_structure": {
            "hook": "Meet-cute or confrontation with high tension chemistry",
            "setup": "Forced proximity (work together, stuck somewhere, fake dating)",
            "escalation_1": "Unexpected tenderness breaks through walls",
            "escalation_2": "Almost connection, then betrayal/misunderstanding",
            "climax": "Grand gesture of love OR devastating revelation",
            "cliffhanger": "He's at her door / She saw something / A letter arrives..."
        },
        "visual_language": {
            "lighting": "golden hour warmth, soft bokeh, intimate framing",
            "color_grading": "warm amber and rose tones, film-like grain",
            "camera_work": "close-ups on eyes/hands, slow motion emotional moments",
            "fashion": "current trends, character-defining outfits"
        },
        "audio_language": {
            "music": "acoustic guitar, piano ballads, lo-fi beats, trending TikTok sounds",
            "ambience": "cafe ambiance, city at night, rain on window",
            "voiceover": "soft female narrator or internal monologue style"
        }
    },
    
    "empowerment_revenge_strategy": {
        "name": "逆袭打脸策略 (Empowerment Payoff)",
        "target_emotion": "satisfaction_justice_served",
        "character_archetypes": {
            "female_lead": {
                "type": "underestimated_force",
                "traits": ["quietly_capable", "patiently_waiting", "strategic", "hidden_depth"],
                "initial_state": "underappreciated, underestimated, held_back"
            },
            "antagonist": {
                "type": "arrogant_obstacle",
                "traits": ["condescending", "underestimates_protagonist", "has_power_over_her"]
            }
        },
        "beat_structure": {
            "hook": "Public humiliation or injustice that makes viewers angry FOR her",
            "setup": "Show her competence being dismissed, building frustration",
            "escalation_1": "She starts making quiet moves, small wins",
            "escalation_2": "Antagonist gets nervous, tries to stop her",
            "climax": "PUBLIC takedown or reveal of her true power - satisfying",
            "cliffhanger": "The fallout begins / Someone new takes notice / Bigger threat emerges"
        },
        "visual_language": {
            "lighting": "dramatic contrast, spotlight moments, shadows clearing",
            "color_grading": "cool blues transitioning to warm golds as she rises",
            "camera_work": "low angles becoming eye-level, power poses, confident movement"
        },
        "audio_language": {
            "music": "building orchestral drops, bass-heavy beats, empowering anthems",
            "ambience": "silence before storm, crowd murmurs, tension building",
            "voiceover": "firm resolve, inner strength voice"
        }
    },
    
    "mystery_paranormal_strategy": {
        "name": "奇幻悬疑策略 (Mystery Supernatural)",
        "target_emotion": "intrigue_curiosity_addiction",
        "character_archetypes": {
            "female_lead": {
                "type": "ordinary_person_in_extraordinary_situation",
                "traits": ["curious", "brave", "practical", "suddenly_special"],
                "discovery": "She has hidden abilities/heritage she didn't know about"
            },
            "love_interest": {
                "type": "enigmatic_protector_or_threat",
                "traits": "mysterious, powerful, connected_to_supernatural_world"
            }
        },
        "beat_structure": {
            "hook": "Something impossible happens - she sees/does something unexplainable",
            "setup": "Trying to understand what's happening, meeting the supernatural world",
            "escalation_1": "Learning her powers, first victories, first real dangers",
            "escalation_2": "The threat becomes personal, someone she loves is in danger",
            "climax": "Major power reveal or sacrifice required - huge stakes",
            "cliffhanger": "The cost of her power becomes clear / A darker force notices her..."
        },
        "visual_language": {
            "lighting": "ethereal glows, magical particle effects, shadowy figures",
            "color_grading": "deep purples and teals, silver accents, mystical atmosphere",
            "camera_work": "floating camera effects, supernatural POV shots, transformation sequences"
        },
        "audio_language": {
            "music": "ethereal choirs, haunting melodies, otherworldly sound design",
            "ambience": "wind chimes, whispers, unexplained sounds, silence with presence",
            "voiceover": "wonder mixed with fear, discovery narration"
        }
    }
}

# ==================== TikTok特定优化规则 ====================
TIKTOK_OPTIMIZATION_RULES = {
    "the_first_3_seconds": {
        "importance": "CRITICAL - This determines if they keep scrolling",
        "do": [
            "Start with HIGH visual impact (beautiful face, shocking action, stunning location)",
            "Use trending audio hook (first 3 seconds of popular song)",
            "Create immediate question: 'Wait, what just happened?' or 'Who is this?'",
            "Show the protagonist's face with strong emotion (tears, shock, determination)"
        ],
        "dont": [
            "Slow environment setup (no panning across empty rooms)",
            "Text-heavy opening (no title cards, no long exposition)",
            "Boring conversation starts (jump INTO the action)",
            "Generic music that doesn't grab attention"
        ]
    },
    
    "retention_hooks": {
        "every_5_8_seconds": [
            "Micro-twists (small surprises)",
            "Visual changes (new angle, new location, costume change)",
            "Audio shifts (music drop, beat change, sound effect)",
            "Text overlays that ask questions or make statements"
        ],
        "comment_inducers": [
            "Controversial choices (make viewers debate in comments)",
            "Unresolved questions (What would YOU do?)",
            "Relatable moments (This is literally me)",
            "Aesthetic moments so beautiful they screenshot"
        ]
    },
    
    "ending_for_shares_and_follows": {
        "cliffhanger_types": [
            "SHOCK twist (everything you knew was wrong)",
            "CUTE moment (unexpected softness from tough character)",
            "QUESTION (end on a question that needs answering)",
            "CALL TO ACTION (follow for part 2, link in bio)",
            "REPEATABLE (so satisfying they watch again)"
        ],
        "final_frame_importance": "Last frame should be iconic - this is what they remember and share"
    },
    
    "text_overlay_rules": {
        "style": "casual_handwritten_font or clean_sans_serif",
        "timing": "appear AFTER visual is established (not over important visuals)",
        "length": "MAX 6 words per text block, 2-3 seconds visible",
        "placement": "lower third of screen, never cover faces",
        "animation": "fade_in_not_pop (gentle appearance)"
    },
    
    "music_strategy": {
        "options": [
            "Use trending TikTok sounds (check Creative Center weekly)",
            "Original compositions that match trending genres (phonk, house, lo-fi, hyperpop)",
            "Popular songs with cleared sections (instrumental drops work best)",
            "Silence with strategic sound effects (can be more impactful than constant music)"
        ],
        "sync_points": [
            "Cut/change on BEAT drop (music drives editing)",
            "Slow-mo on emotional lyric moments",
            "Speed up during action sequences",
            "Freeze frame on key lyrics or words"
        ]
    }
}

# ==================== 文化适配指南 ====================
WESTERN_CULTURAL_ADAPTATION = {
    "narrative_conventions": {
        "show_dont_tell": "CRITICAL - Western audiences prefer visual storytelling over exposition",
        "character_first": "Character-driven plots preferred over plot-driven",
        "emotional_authenticity": "Vulnerability = strength (unlike some Eastern traditions where hiding emotion is virtue)",
        "subtext_over_text": "What's NOT said matters as much as what IS said",
        "internal_conflict": "Man vs Self is often more compelling than Man vs External Force"
    },
    
    "dialogue_style": {
        "naturalistic": "Should sound like REAL people talking, not theatrical",
        "subtext_heavy": "Characters rarely say exactly what they mean",
        "cultural_references": "Use Western cultural touchstones (movies, books, songs, history)",
        "avoid": [
            "Excessively formal or poetic language (unless character is specifically that way)",
            "Eastern proverbs or idioms that don't translate",
            "Honorifics or formal address patterns unfamiliar to Westerners",
            "Over-explanation (trust audience intelligence)"
        ]
    },
    
    "relationship_dynamics": {
        "western_romantic_norms": [
            "Eye contact = intimacy indicator",
            "Physical touch progression has meaning (hand → arm → shoulder → face)",
            "Vulnerability shown through actions not just words",
            "Conflict expressed through tension, not avoidance (confrontation culture)"
        ],
        "friendship norms": [
            "Banter and teasing = affection",
            "Shared activities > verbal expressions of friendship",
            "Being there without asking = ultimate loyalty proof"
        ]
    },
    
    "beauty_and_fashion_standards": {
        "diversity_is_beauty": "Include various skin tones, body types, hair textures",
        "current_fashion_matters": "Characters should look like they belong to THIS decade",
        "makeup_should_match_character": "Natural/no-makeup look for 'girl next door', glamorous for 'fashionista'",
        "avoid_stereotypes": "No exaggerated features unless specifically that character's trait",
        "male_gaze_avoidance": "Female characters exist for themselves, not male consumption (unless that's the point)"
    },
    
    "themes_that_resonate": {
        "universal_human_experiences": [
            "First love / heartbreak",
            "Finding one's identity",
            "Family expectations vs personal dreams",
            "Friendship betrayals and reconciliations",
            "Career ambition vs personal life",
            "Learning to trust after being hurt",
            "Mother/daughter dynamics",
            "Self-worth journey"
        ],
        "currently_trending_topics": [
            "Mental health awareness (therapy is okay, boundaries are healthy)",
            "Body positivity and self-acceptance",
            "Career pivots and 'quarter-life crisis'",
            "Choosing oneself over others' expectations",
            "Female friendships as primary relationships (not just romantic)",
            "Financial independence and empowerment",
            "Social media impact on self-image",
            "Sustainable living and conscious consumerism"
        ]
    }
}

def generate_platform_optimized_prompt(episode_info, global_lore, 
                                    platform="tiktok",
                                    strategy="romance_domination",
                                    target_audience="western_female_18_35"):
    """
    生成针对特定平台和受众的优化Prompt
    
    Returns:
        tuple: (prompt_str, optimization_metadata)
    """
    platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS["tiktok"])
    content_strategy = CONTENT_STRATEGIES.get(strategy, CONTENT_STRATEGIES["romance_domination_strategy"])
    audience_prefs = AUDIENCE_PREFERENCES
    
    prompt_parts = []
    
    # ====== 第一部分：平台与受众定义 ======
    prompt_parts.append(f"""【目标平台与受众】
**发布平台**: {platform_spec['name']}
**最佳时长**: {platform_spec['duration_optimal'][0]}-{platform_spec['duration_optimal'][1]}秒 (最大{platform_spec['duration_max']}秒)
**画面比例**: {platform_spec['aspect_ratio']} 竖屏

**核心受众**: {target_audience}
- 年龄: {audience_prefs['demographics']['core_age_range'][0]}-{audience_prefs['demographics']['core_age_range'][1]}岁为主
- 地区: {', '.join(audience_prefs['demographics']['geographic_focus'][:5])}等
- 语言: {audience_prefs['demographics']['language'].split()[0]}

**受众价值观优先级**:
""")
    for i, value in enumerate(audience_prefs['psychographics']['values_prioritized'][:5]):
        prompt_parts.append(f"  {i+1}. {value.replace('_', ' ').title()}")
    
    prompt_parts.append(f"""
**受众恐惧触发点**(要善用但不要滥用):
""")
    for fear in audience_prefs['psychographics']['fears_triggers'][:4]:
        prompt_parts.append(f"  ⚠️ {fear.replace('_', ' ').title()}")
    
    # ====== 第二部分：内容策略应用 ======
    strategy_data = content_strategy
    prompt_parts.append(f"""
【本次使用的内容策略: {strategy_data['name']}】
**目标情绪**: {strategy_data['target_emotion']}
**病毒潜力**: {list(content_strategy.values())[-1].get('shareability', 'medium') if isinstance(list(content_strategy.values())[-1], dict) else 'medium'}

**角色设定**:
""")

    if 'character_archetypes' in strategy_data:
        archetypes = strategy_data['character_archetypes']
        for role_type, char_info in archetypes.items():
            prompt_parts.append(f"""
**{role_type.title()}**:
• 类型: {char_info['type']}
• 核心特质: {', '.join(char_info['traits'][:4])}
• 初始缺陷: {', '.join(char_info.get('flaws_that_make_her_relatable', [])[:3]) if 'flaws_that_make_her_relatable' in char_info else 'N/A'}
""")
    
    prompt_parts.append("""
**推荐节拍结构**:
""")
    if 'beat_structure' in strategy_data:
        for beat_name, beat_desc in strategy_data['beat_structure'].items():
            prompt_parts.append(f"  • {beat_name.upper()}: {beat_desc}")
    
    # ====== 第三部分：视觉语言规范 ======
    if 'visual_language' in strategy_data:
        vis = strategy_data['visual_language']
        prompt_parts.append(f"""
【视觉语言规范 - 匹配{platform_spec['name']}风格】

**光影方案**:
  {vis.get('lighting', 'warm cinematic lighting')}
**色彩分级**: 
  {vis.get('color_grading', 'cinematic color grading')}
**镜头语言**:
  {vis.get('camera_work', 'dynamic camera movement matching content rhythm')}
**时尚/造型**:
  {vis.get('fashion', 'contemporary stylish fashion appropriate to characters')}
""")
    
    # ====== 第四部分：音频设计规范 ======
    if 'audio_language' in strategy_data:
        aud = strategy_data['audio_language']
        audio_req = platform_spec.get('audio_requirements', {})
        
        prompt_parts.append(f"""
【音频设计规范 - {platform_spec['name']}适配】

**音乐风格**:
  {aud.get('music', 'trending and emotionally appropriate')}
**环境音**:
  {aud.get('ambience', 'atmospheric and immersive')}
**旁白风格**:
  {aud.get('voiceover', 'natural conversational tone')}

**平台特定音频要求**:
  • 音乐趋势敏感度: {audio_req.get('music_trend_awareness', 'moderate')}
  • 人声/音乐平衡: {audio_req.get('volume_music_balance', 'balanced')}
  • 音效质量: {audio_req.get('sound_effects', 'standard')}
""")
    
    # ====== 第五部分：TikTok/社交平台特殊规则 ======
    if platform == "tiktok":
        tiktok_rules = TIKTOK_OPTIMIZATION_RULES
        prompt_parts.append(f"""
【{platform_spec['name']}平台专项优化规则】

**前3秒生死线 (THE HOOK)**:
  ✅ 必须: {' | '.join(tiktok_rules['the_first_3_seconds']['do'][:4])}
  ❌ 避免: {' | '.join(tiktok_rules['the_first_3_seconds']['dont'][:4])}

**留存钩子 (Retention Hooks)**:
  每5-8秒必须有微反转或视觉变化
  评论诱导: 使用{' | '.join(tiktok_rules['retention_hooks']['comment_inducers'][:2])}

**结尾设计 (Ending for Shares)**:
  推荐结尾类型: {' | '.join(tiktok_rules['ending_for_shares_and_follows']['cliffhanger_types'][:3])}
  最终帧必须是标志性画面（这是他们记住和分享的）

**文字叠加规则**:
  风格: {tiktok_rules['text_overlay_rules']['style']}
  时长: 每块文字≤{tiktok_rules['text_overlay_rules']['length'].split()[1]}秒
  位置: {tiktok_rules['text_overlay_rules']['placement']}

**音乐策略**:
  {' | '.join(tiktok_rules['music_strategy']['options'][:2])}
  剪辑节点: {' | '.join(tiktok_rules['music_strategy']['sync_points'][:3])}
""")
    
    # ====== 第六部分：文化适配指南 ======
    culture_guide = WESTERN_CULTURAL_ADAPTATION
    prompt_parts.append(f"""
【西方文化适配指南 - 关键差异注意】

**叙事习惯**:
  • Show Don't Tell (西方观众偏好视觉叙事)
  • 角色驱动剧情 (Character-driven > Plot-driven)
  • 脆弱即力量 (Vulnerability = Strength)
  • 潜台词比台词更重要 (Subtext > Text)
  • 内心冲突往往比外部冲突更有张力

**对话风格**:
  • 自然真实 (像真人说话，非戏剧腔)
  • 包含潜台词 (Characters rarely say exactly what they mean)
  • 使用西方文化参照 (电影/书籍/歌曲/历史)
  • 避免过度正式/诗意化语言 (除非角色特点如此)

**关系动态**:
  • 眼神接触 = 亲密指标
  • 身体触碰递进有含义
  • 通过行动而非回避来表达冲突 (对抗性文化)
  • 友谊通过共同活动和默契展现

**当前流行主题** (2024-2025趋势):
""")
    for topic in culture_guide['themes_that_resonate']['currently_trending_topics'][:5]:
        prompt_parts.append(f"  ✓ {topic}")
    
    prompt_parts.append("""

**审美标准**:
  • 多样化即美 (各种肤色/体型/发质都要有)
  • 时尚要符合时代 (角色看起来属于这个年代)
  • 避免男性凝视 (女性角色为自己存在，非为男性消费)
  • 真实体型优于完美化 (Real body types > Idealized)
""")
    
    # ====== 第七部分：输出格式 ======
    prompt_parts.append("""
【输出格式要求】
严格输出JSON格式，包含以下增强字段：

{
    "episode_seq": <集数>,
    "platform_optimized_for": "{platform}",
    "target_audience": "{target_audience}",
    "content_strategy": "{strategy}",
    
    "beats": [
        {{
            "beat_type": "hook/setup/escalation/climax/cliffhanger",
            "content": "<详细描述>",
            
            // 新增：平台优化字段
            "visual_description": "<符合平台风格的画面描述>",
            "audio_cue": "<音频提示>",
            "text_overlay": "<如果有文字叠加，写在这里（否则为null）>",
            "tiktok_hook_strength": "<1-10分 这段作为Hook有多强>",
            "comment诱导元素": "<这段会让观众想评论什么?>",
            "shareability_factor": "<1-10分 这段被分享的可能性>",
            "duration": <秒>,
            "emotional_target": "<目标情绪>"
        }}
    ],
    
    "metadata": {{
        "total_duration": <总时长>,
        "avg_hook_strength": <平均Hook强度>,
        "optimization_notes": "<针对平台的特别调整>"
    }}
}""")
    
    final_prompt = "\n\n".join(prompt_parts)
    
    metadata = {
        "platform": platform,
        "strategy": strategy,
        "audience": target_audience,
        "theories_used": ["Platform-Specific Optimization", "Content Strategy Framework", "Western Cultural Adaptation", "TikTok Virality Mechanics"],
        "prompt_length": len(final_prompt)
    }
    
    return final_prompt, metadata


if __name__ == "__main__":
    print("=" * 70)
    print("欧美女性受众 TikTok/Facebook 优化系统测试")
    print("=" * 70)
    
    test_episode = {
        "seq": 1,
        "core_plot": "Emma, a 26-year-old marketing manager, discovers her new client Alexander is the same man who disappeared after their one-night stand three years ago. He doesn't recognize her, but he's now engaged to her manipulative sister.",
        "hook": "Alexander's hand touches Emma's during a presentation - electric recognition flashes in his eyes but he can't place why.",
        "climax": "Emma finally confronts Alexander with the truth - he remembers everything, and chooses her over her sister.",
        "ending_suspense": "Emma's sister vows revenge, while Emma finds a mysterious letter from Alexander's late wife suggesting his past holds darker secrets...",
        "main_characters": ["Emma", "Alexander", "Sarah(sister)"]
    }
    
    test_lore = {
        "genre": "Contemporary Romance",
        "core_theme": "Second chance love and finding courage to choose yourself",
        "characters": [
            {
                "name": "Emma",
                "identity": "Marketing Manager / Hidden Romantic",
                "personality": "Professional exterior, secretly yearns for deep connection, afraid of being hurt again",
                "visual_traits": ["hazel eyes", "shoulder-length auburn hair", "elegant but approachable style", "subtle freckles"],
                "relationships": {"Alexander": "past lover/current client", "Sarah": "competitive sister"}
            },
            {
                "name": "Alexander",
                "identity": "CEO / Mysterious Billionaire",
                "personality": "Coldly composed publicly, haunted privately, fiercely protective when he cares",
                "visual_traits": ["sharp jawline", "storm-grey eyes", "tailored perfection", "scar on left hand"],
                "relationships": {"Emma": "forgotten lover/client", "Sarah": "fiancée (unhappy)"}
            }
        ]
    }
    
    # 生成TikTok优化的Prompt
    prompt, meta = generate_platform_optimized_prompt(
        test_episode, 
        test_lore,
        platform="tiktok",
        strategy="romance_domination",
        target_audience="western_female_18_35"
    )
    
    print(f"\n📱 平台: {meta['platform']}")
    print(f"🎯 策略: {meta['strategy']}")
    print(f"👥 受众: {meta['audience']}")
    print(f"📝 Prompt长度: {len(prompt)}字符")
    print(f"\n📄 Prompt预览 (前800字符):")
    print("-" * 70)
    print(prompt[:800])
    print("...")
