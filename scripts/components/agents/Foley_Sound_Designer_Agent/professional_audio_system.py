# -*- coding: utf-8 -*-
"""
Professional Audio Design System V2.0 (专业音频设计系统)
空间声学设计、情绪音乐匹配、电影级音效工程
支持杜比全景声、环境音景构建、心理声学应用
"""

# ==================== 空间声学配置库 ====================
SPATIAL_AUDIO_CONFIGS = {
    "intimate_close": {
        "description": "亲密近距离，耳语级别",
        "reverb": {
            "type": "small_room",
            "rt60": 0.3,
            "pre_delay": 5,
            "damping": 0.8,
            "wet_level": -12
        },
        "panning": "centered, slight movement for naturalness",
        "distance_perception": "very close (0-1 meter)",
        "frequency_response": "full range with proximity effect boost"
    },
    
    "personal_space": {
        "description": "个人空间，对话距离",
        "reverb": {
            "type": "medium_room",
            "rt60": 0.6,
            "pre_delay": 10,
            "damping": 0.7,
            "wet_level": -8
        },
        "panning": "stereo spread 30 degrees",
        "distance_perception": "close (1-3 meters)",
        "frequency_response": "natural presence with slight warmth"
    },
    
    "social_distance": {
        "description": "社交距离，群体场景",
        "reverb": {
            "type": "large_room",
            "rt60": 1.2,
            "pre_delay": 15,
            "damping": 0.6,
            "wet_level": -4
        },
        "panning": "wide stereo field, positional audio",
        "distance_perception": "medium (3-7 meters)",
        "frequency_response": "natural room tone, slight high frequency roll-off"
    },
    
    "public_space": {
        "description": "公共空间，大厅/广场",
        "reverb": {
            "type": "hall",
            "rt60": 2.0,
            "pre_delay": 25,
            "damping": 0.5,
            "wet_level": 0
        },
        "panning": "immersive surround, height channels active",
        "distance_perception": "far (7+ meters)",
        "frequency_response": "room dominant, significant air absorption"
    },
    
    "outdoor_open": {
        "description": "户外开放空间",
        "reverb": {
            "type": "plate_simulation",
            "rt60": 1.5,
            "pre_delay": 20,
            "damping": 0.4,
            "wet_level": -6
        },
        "panning": "360 degree ambisonics",
        "distance_perception": "environmental context dependent",
        "frequency_response": "bright, natural outdoor character"
    }
}

# ==================== 情绪-音乐映射 ====================
EMOTIONAL_MUSIC_MAPPING = {
    # 正面情绪
    "joy": {
        "music_style": "uplifting major key orchestral",
        "tempo_range": [120, 140],
        "key_preference": ["C major", "G major", "D major"],
        "instrumentation": [
            "brass section (trumpets, horns)",
            "upright piano or bright synth",
            "strings pizzicato and legato",
            "light percussion (shaker, tambourine)"
        ],
        "dynamic_curve": "crescendo building to triumphant climax",
        "harmonic_rhythm": "frequent chord changes, circle of fifths",
        "production_techniques": [
            "bright EQ boost around 3-5kHz",
            "subtle reverb for space",
            "compression for punchy transients"
        ]
    },
    
    "love": {
        "music_style": "romantic tender ballad",
        "tempo_range": [60, 80],
        "key_preference": ["F major", "Bb major", "Eb major"],
        "instrumentation": [
            "grand piano or intimate acoustic guitar",
            "string quartet or solo cello",
            "soft pad synthesizer",
            "gentle harp or celesta accents"
        ],
        "dynamic_curve": "swelling and receding like breathing",
        "harmonic_rhythm": "slow harmonic rhythm, lush extensions",
        "production_techniques": [
            "warm analog saturation",
            "wide stereo imaging",
            "gentle sidechain compression to dialogue"
        ]
    },
    
    "triumph": {
        "music_style": "epic heroic orchestral",
        "tempo_range": [90, 110],
        "key_preference": ["D major", "E major", "B major"],
        "instrumentation": [
            "full orchestra with prominent brass",
            "timpani and percussion battery",
            "choir (SATB) for emotional weight",
            "French horns for nobility"
        ],
        "dynamic_curve": "starting soft, explosive crescendo",
        "harmonic_rhythm": "powerful root position chords, pedal tones",
        "production_techniques": [
            "massive dynamic range (pp to ff)",
            "hall reverb for grandeur",
            "subharmonic enhancement for impact"
        ]
    },
    
    # 负面情绪
    "anger": {
        "music_style": "aggressive dissonant industrial",
        "tempo_range": [130, 160],
        "key_preference": ["no clear key", "atonal clusters"],
        "instrumentation": [
            "distorted electric guitars",
            "industrial percussion (metal hits)",
            "synth bass with heavy distortion",
            "aggressive electronic drums"
        ],
        "dynamic_curve": "sustained high intensity with sudden drops",
        "harmonic_rhythm": "dissonant intervals, tritones, minor seconds",
        "production_techniques": [
            "heavy distortion and saturation",
            "sidechaining to kick drum",
            "extreme compression, parallel aggression"
        ]
    },
    
    "fear": {
        "music_style": "tense minimalist horror score",
        "tempo_range": [variable, "rubato with accelerations"],
        "key_preference": ["chromatic", "whole tone", "diminished"],
        "instrumentation": [
            "sul ponticello strings (scratchy bowing)",
            "prepared piano or toy piano",
            "waterphone or other metal percussion",
            "low frequency drones (40-80Hz)"
        ],
        "dynamic_curve": "sudden swells from pp to mp, then silence",
        "harmonic_rhythm": "ambiguous harmony, unresolved tensions",
        "production_techniques": [
            "extreme close miking for detail",
            "reverb with long decay in dark spaces",
            "subliminal low frequency rumble (infrasound)"
        ]
    },
    
    "sadness": {
        "music_style": "melancholic minor key adagio",
        "tempo_range": [50, 70],
        "key_preference": ["D minor", "B minor", "F# minor"],
        "instrumentation": [
            "solo cello or viola da gamba",
            "piano with una corda (soft pedal)",
            "English horn or bass clarinet",
            "glass harmonica or musical saw"
        ],
        "dynamic_curve": "gradual decrescendo into nothingness",
        "harmonic_rhythm": "slow, modal interchange, borrowed chords",
        "production_techniques": [
            "intimate close recording",
            "room tone captured for authenticity",
            "subtle pitch drift for human feel"
        ]
    },
    
    "despair": {
        "music_style": "empty void ambient drone",
        "tempo_range": [static or extremely slow],
        "key_preference": ["drone on single note", "gradual pitch descent"],
        "instrumentation": [
            "sustained synthesizer pads",
            "processed field recordings (wind, distant trains)",
            "tailed off piano notes",
            "subtle noise textures"
        ],
        "dynamic_curve": "nearly static with micro-fluctuations",
        "harmonic_rhythm": "minimal harmonic motion, stasis",
        "production_techniques": [
            "extreme processing and granular synthesis",
            "binaural spatialization",
            "psychoacoustic effects (binaural beats)"
        ]
    },
    
    # 复杂情绪
    "suspense": {
        "music_style": "building tension ostinato",
        "tempo_range": [accelerating from 80 to 120],
        "key_preference": ["minor keys with raised 4ths (lydian)"],
        "instrumentation": [
            "pulsing synthesizer ostinato",
            "tremolo strings (unmeasured)",
            "tick-tock percussion (metronome, clock)",
            "low brass swells"
        ],
        "dynamic_curve": "crescendo with false peaks",
        "harmonic_rhythm": "relentless repetition with gradual variation",
        "production_techniques": [
            "rhythmic gating effects",
            "dubstep-style wobble bass modulations",
            "reverse reverb tails building tension"
        ]
    },
    
    "mystery": {
        "music_style": "enigmatic impressionistic",
        "tempo_range": [70, 90, flexible rubato],
        "key_preference": ["modal (dorian, phrygian, mixolydian)"],
        "instrumentation": [
            "celesta or glockenspiel",
            "vibraphone with motor off",
            "muted trumpet or flugelhorn",
            "ethereal female choir (wordless)"
        ],
        "dynamic_curve": "mysterious swells, never fully resolving",
        "harmonic_rhythm": "impressionist parallelism, planing",
        "production_techniques": [
            "heavy reverb with modulation",
            "tape delay echoes",
            "filter sweeps revealing hidden layers"
        ]
    },
    
    "nostalgia": {
        "music_style": "warm vintage memory lane",
        "tempo_range": [75, 95],
        "key_preference": ["major keys with added 6ths and 9ths"],
        "instrumentation": [
            "vintage electric piano (Rhodes/Wurlitzer)",
            "acoustic guitar with fingerstyle",
            "mellotron strings or choir",
            "subtle vinyl crackle and hiss"
        ],
        "dynamic_curve": "gentle waves like memory fragments",
        "harmonic_rhythm": "jazz-influenced extensions, ii-V-I progressions",
        "production_techniques": [
            "analog tape emulation",
            "lo-fi degradation (bit reduction, sample rate reduction)",
            "warm tube saturation",
            "slight wow and flutter"
        ]
    }
}

# ==================== 电影级音效库 ====================
CINEMATIC_SFX_LIBRARY = {
    "impact_heavy": {
        "category": "physical_impact",
        "examples": ["punch_body", "kick_door", "car_crash", "explosion_distant"],
        "processing_chain": [
            "transient designer (attack +20ms, sustain -15dB)",
            "EQ: low shelf +4dB @ 80Hz, presence +2dB @ 4kHz",
            "compression: ratio 4:1, attack 5ms, release 50ms",
            "reverb: short room, predelay 5ms, for body"
        ],
        "layering_suggestion": [
            "layer 1: original recording (100%)",
            "layer 2: pitched down 1 octave (-6dB)",
            "layer 3: synthesized sub drop (-12dB, 40-80Hz)"
        ]
    },
    
    "whoosh_transition": {
        "category": "movement",
        "examples": ["fast_pass_by", "sword_swing", "magic_cast", "time_jump"],
        "processing_chain": [
            "pitch automation: rising 2 octaves over duration",
            "EQ sweep: starting dark, ending bright",
            "multiband compression for smoothness",
            "stereo widening for immersion"
        ],
        "design_variants": [
            "metallic (added harmonic content)",
            "windy (filtered noise layer)",
            "energy (synthesized power-up)"
        ]
    },
    
    "ambient_atmosphere": {
        "category": "environmental",
        "examples": ["forest_day", "city_night", "underwater", "spaceship_hum"],
        "processing_chain": [
            "noise reduction if needed",
            "EQ shaping for frequency balance",
            " gentle compression for consistency",
            "spatial placement (reverb/panning)",
            "loop point creation for seamless playback"
        ],
        "layering_philosophy": [
            "base layer: constant ambient bed (-18dB RMS)",
            "mid layer: occasional events (-12dB RMS)",
            "detail layer: foreground specific sounds (-6dB RMS)"
        ]
    },
    
    "creature_vocalizations": {
        "category": "character",
        "examples": ["dragon_roar", "alien_chatter", "beast_growl", "spirit_whisper"],
        "design_approach": [
            "start with animal vocalization base",
            "layer processed human vocals for intelligence",
            "add synthetic elements for otherworldliness",
            "apply formant shifting for size perception"
        ],
        "emotional_inflection_parameters": [
            "pitch variation range (anger = wide, calm = narrow)",
            "rhythm irregularity (wild = chaotic, domestic = steady)",
            "spectral content brightness (young = bright, old = dark)"
        ]
    },
    
    "magical_spells": {
        "category": "fantasy",
        "examples": ["fireball_cast", "healing_glow", "teleport_arrival", "shield_activate"],
        "core_components": [
            "whoosh/movement element",
            "tonal chord or cluster (defines spell type)",
            "impact/sustain tail",
            "ambient aftermath (lingering magic in air)"
        ],
        "elemental_variations": {
            "fire": {"brightness": "+20%", "distortion": "subtle", "sub_content": "crackle"},
            "ice": {"brightness": "-10%", "reverb": "large cold hall", "shimmer": "frozen"},
            "nature": {"organic_modulation": "LFO slow", "texture": "growing/vines", "tone": "earthy"},
            "shadow": {"low_freq_emphasis": "+10dB", "filter_sweep": "dark to darker", "delay": "echoing void"}
        }
    }
}

# ==================== 心理声学效果 ====================
PSYCHOACOUSTIC_EFFECTS = {
    "infrasound_dread": {
        "frequency_range": "18-22 Hz",
        "perceived_effect": "unease, pressure on chest, uneasiness",
        "application_scenes": ["haunted locations", "approaching doom", "supernatural presence"],
        "implementation": "subwoofer or dedicated subharmonic generator, very low level (-24dB)"
    },
    
    "binaural_beats_focus": {
        "frequency_pattern": "alpha waves (8-13 Hz difference between L/R)",
        "perceived_effect": "heightened focus, trance state",
        "application_scenes": ["investigation sequences", "concentration moments", "ritual preparation"],
        "implementation": "headphones required, subtle background layer"
    },
    
    "ASMR_intimacy": {
        "technique": "close-miked delicate sounds",
        "examples": ["whispering", "page turning", "fabric rustling", "tapping"],
        "perceived_effect": "tingles, relaxation, heightened awareness",
        "application_scenes": ["quiet moments", "reading letters", "preparation rituals"]
    },
    
    "doppler_approaching": {
        "physics": "pitch rises as source approaches",
        "exaggerated_for": "supernatural speed, unrealistic approach",
        "use_case": "something moving impossibly fast toward camera"
    },
    
    "haas_effect_width": {
        "technique": "same sound delayed 1-40ms in one channel",
        "perceived_effect": "sound image widens without level change",
        "application": "making mono sources feel wider, ghostly presence"
    }
}

def get_audio_design(emotion=None, scene_type="interior_domestic", intensity=7):
    """
    获取专业级音频设计方案
    
    Returns:
        dict: 完整的音频设计参数
    """
    design = {
        "emotion": emotion,
        "scene_type": scene_type,
        "intensity": intensity,
        
        # 空间声学
        "spatial_config": None,
        
        # 音乐设计
        "music_design": None,
        
        # 音效设计
        "sfx_design": [],
        
        # 对白处理
        "dialogue_processing": None,
        
        # 心理声学层
        "psychoacoustic_layer": None,
        
        # 最终混音参数
        "mix_parameters": None
    }
    
    # 1. 应用空间声学配置
    if scene_type in SPATIAL_AUDIO_CONFIGS:
        design["spatial_config"] = SPATIAL_AUDIO_CONFIGS[scene_type]
    
    # 2. 应用情绪音乐映射
    if emotion and emotion.lower() in EMOTIONAL_MUSIC_MAPPING:
        design["music_design"] = EMOTIONAL_MUSIC_MAPPING[emotion.lower()]
    
    # 3. 根据强度调整
    design = adjust_audio_intensity(design, intensity)
    
    # 4. 设置混音参数
    design["mix_parameters"] = get_mix_parameters(intensity)
    
    return design

def adjust_audio_intensity(design, intensity):
    """根据强度调整音频参数"""
    if intensity <= 3:
        # 低强度：安静、细腻
        design["dialogue_processing"] = {
            "presence": "+2dB",
            "compression": "light (2:1 ratio)",
            "de_esser": "gentle",
            "eq": "warmth +1dB @ 200Hz"
        }
        design["overall_dynamic_range"] = "wide (quiet scenes)"
        
    elif intensity <= 6:
        # 中等强度：平衡、自然
        design["dialogue_processing"] = {
            "presence": "+4dB",
            "compression": "moderate (3:1 ratio)",
            "de_esser": "standard",
            "eq": "presence +2dB @ 4kHz"
        }
        design["overall_dynamic_range"] = "normal film mix"
        
    elif intensity <= 8:
        # 高强度：动态、冲击
        design["dialogue_processing"] = {
            "presence": "+6dB",
            "compression": "aggressive (4:1 ratio)",
            "de_esser": "strong",
            "eq": "clarity +3dB @ 3kHz, punch +2dB @ 100Hz"
        }
        design["overall_dynamic_range": "compressed modern mix"]
        
    else:
        # 极高强度：极端、沉浸
        design["dialogue_processing"] = {
            "presence": "+8dB",
            "compression": "heavy (6:1 ratio)",
            "de_esser": "extreme",
            "eq": "aggressive presence, hyped lows and highs"
        }
        design["overall_dynamic_range"] = "highly compressed, loudness maximized"
        design["psychoacoustic_layer"] = PSYCHOACOUSTIC_EFFECTS["infrasound_dread"]
    
    return design

def get_mix_parameters(intensity):
    """获取最终混音参数"""
    base_params = {
        "loudness_target": -23 LUFS (streaming standard),
        "true_peak_max": -1.0 dBTP,
        "stereo_width": "natural",
        "low_frequency_extension": "full spectrum"
    }
    
    if intensity <= 3:
        base_params.update({
            "dynamic_range": "high (20dB+ crest factor)",
            "reverb_return_level": "audible but not dominating",
            "music_to_dialogue_ratio": "-12dB during dialogue"
        })
    elif intensity >= 8:
        base_params.update({
            "dynamic_range": "low (8-10dB crest factor)",
            "reverb_return_level": "prominent, part of the sound",
            "music_to_dialogue_ratio": "-6dB or competitive with dialogue"
        })
    
    return base_params

def generate_audio_prompt(audio_design, scene_description="", character_dialogue=""):
    """生成专业级音频提示词"""
    prompt_parts = []
    
    # 1. 空间信息
    if audio_design.get("spatial_config"):
        spatial = audio_design["spatial_config"]
        prompt_parts.append(f"SPACE: {spatial['description']}")
        prompt_parts.append(f"Reverb: {spatial['reverb']['type']} RT60={spatial['reverb']['rt60']}s")
    
    # 2. 音乐风格
    if audio_design.get("music_design"):
        music = audio_design["music_design"]
        prompt_parts.append(f"MUSIC: {music['music_style']}")
        prompt_parts.append(f"Tempo: {music['tempo_range']} BPM")
        prompt_parts.append(f"Instruments: {', '.join(music['instrumentation'][:3])}")
    
    # 3. 音效
    if audio_design.get("sfx_design"):
        sfx_list = ", ".join(audio_design["sfx_design"])
        prompt_parts.append(f"SFX: {sfx_list}")
    
    # 4. 对白处理
    if audio_design.get("dialogue_processing"):
        dialog_proc = audio_design["dialogue_processing"]
        prompt_parts.append(f"DIALOGUE PROCESSING: {dialog_proc}")
    
    # 5. 场景描述
    if scene_description:
        prompt_parts.append(f"SCENE: {scene_description}")
    if character_dialogue:
        prompt_parts.append(f"DIALOGUE: \"{character_dialogue}\"")
    
    return "\n".join(prompt_parts)

if __name__ == "__main__":
    print("=" * 60)
    print("专业音频设计系统测试")
    print("=" * 60)
    
    # 测试1: 恐惧场景的音频设计
    audio1 = get_audio_design(
        emotion="fear",
        scene_type="interior_domestic",
        intensity=9
    )
    print("\n测试1: 极度恐惧 - 密室恐怖")
    print(generate_audio_prompt(audio1, "Dark basement with single flickering bulb", "\"Is someone there?\""))
    
    # 测试2: 胜利时刻的音频设计
    audio2 = get_audio_design(
        emotion="triumph",
        scene_type="public_space",
        intensity=8
    )
    print("\n\n测试2: 胜利凯旋 - 广场欢呼")
    print(generate_audio_prompt(audio2, "Grand throne room with cheering crowds", "\"I claim this victory!\""))
