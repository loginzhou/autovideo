# -*- coding: utf-8 -*-
"""
Emotional Analysis System V2.0 (情绪分析系统)
剧情情绪曲线分析、节奏控制、情感弧线设计
支持多维度情绪识别和预测
"""

# ==================== 情绪维度定义 ====================
EMOTION_DIMENSIONS = {
    "valence": {
        "description": "愉悦度 (negative to positive)",
        "range": [-1, 1],
        "labels": {
            -1.0: "极度痛苦",
            -0.7: "悲伤/绝望",
            -0.4: "焦虑/紧张",
            0.0: "中性/平静",
            0.4: "满足/愉快",
            0.7: "喜悦/兴奋",
            1.0: "狂喜/极乐"
        }
    },
    
    "arousal": {
        "description": "激活度 (calm to excited)",
        "range": [0, 1],
        "labels": {
            0.0: "沉睡/无意识",
            0.2: "放松/困倦",
            0.4: "平静/专注",
            0.6: "警觉/感兴趣",
            0.8: "激动/活跃",
            1.0: "狂躁/极度兴奋"
        }
    },
    
    "dominance": {
        "description": "支配度 (submissive to dominant)",
        "range": [-1, 1],
        "labels": {
            -1.0: "完全无助",
            -0.7: "恐惧/顺从",
            -0.3: "不安/犹豫",
            0.0: "中性/平等",
            0.3: "自信/掌控",
            0.7: "权威/强势",
            1.0: "全能/主宰"
        }
    }
}

# ==================== 基础情绪类型 ====================
BASIC_EMOTIONS = {
    "joy": {"valence": 0.8, "arousal": 0.7, "dominance": 0.3},
    "trust": {"valence": 0.7, "arousal": 0.3, "dominance": 0.2},
    "fear": {"valence": -0.7, "arousal": 0.8, "dominance": -0.6},
    "surprise": {"valence": 0.2, "arousal": 0.9, "dominance": -0.2},
    "sadness": {"valence": -0.8, "arousal": 0.2, "dominance": -0.5},
    "disgust": {"valence": -0.8, "arousal": 0.4, "dominance": -0.3},
    "anger": {"valence": -0.6, "arousal": 0.8, "dominance": 0.6},
    "anticipation": {"valence": 0.3, "arousal": 0.5, "dominance": 0.1}
}

# ==================== 复合情绪（Plutchik's Wheel扩展） ====================
COMPLEX_EMOTIONS = {
    # 正面复合
    "love": ["joy", "trust"],
    "optimism": ["anticipation", "joy"],
    "aggression": ["anger", "anticipation"],
    "pride": ["anger", "dominance"],  # dominance不是基础情绪，这里用anger+trust近似
    
    # 负面复合
    "submission": ["fear", "trust"],
    "awe": ["fear", "surprise"],
    "disapproval": ["sadness", "anger"],
    "remorse": ["disgust", "sadness"],
    
    # 中性/混合
    "curiosity": ["surprise", "anticipation"],
    "contempt": ["disgust", "anger"],  # 实际是disgust+anger的变体
    "nostalgia": ["sadness", "joy"],  # 苦乐参半
    "hope": ["anticipation", "trust"]
}

def calculate_complex_emotion(emotion_name):
    """计算复合情绪的三维值"""
    if emotion_name in BASIC_EMOTIONS:
        return BASIC_EMOTIONS[emotion_name]
    
    if emotion_name in COMPLEX_EMOTIONS:
        components = COMPLEX_EMOTIONS[emotion_name]
        result = {"valence": 0, "arousal": 0, "dominance": 0}
        
        for component in components:
            if component in BASIC_EMOTIONS:
                for dim in result:
                    result[dim] += BASIC_EMOTIONS[component][dim]
        
        # 平均化
        for dim in result:
            result[dim] /= len(components)
        
        return result
    
    return {"valence": 0, "arousal": 0.5, "dominance": 0}

# ==================== 剧情情绪曲线模板 ====================
EMOTIONAL_ARC_TEMPLATES = {
    "rags_to_riches": {
        "description": "从低谷到高峰的经典成功故事",
        "arc_shape": [
            {"position": 0.0, "emotion": "sadness", "intensity": 0.7},
            {"position": 0.15, "emotion": "hope", "intensity": 0.5},
            {"position": 0.3, "emotion": "anticipation", "intensity": 0.6},
            {"position": 0.45, "emotion": "fear", "intensity": 0.8},  # 第一次危机
            {"position": 0.6, "emotion": "courage", "intensity": 0.7},
            {"position": 0.75, "emotion": "despair", "intensity": 0.9},  # 至暗时刻
            {"position": 0.9, "emotion": "triumph", "intensity": 1.0},
            {"position": 1.0, "emotion": "joy", "intensity": 0.8}
        ],
        "key_moments": [
            "call to adventure (15%)",
            "first threshold crossing (30%)",
            "major obstacle/crisis (45%)",
            "dark night of the soul (75%)",
            "climax/victory (90%)"
        ]
    },
    
    "tragedy": {
        "description": "从高点跌落的悲剧故事",
        "arc_shape": [
            {"position": 0.0, "emotion": "joy", "intensity": 0.6},
            {"position": 0.2, "emotion": "pride", "intensity": 0.7},
            {"position": 0.35, "emotion": "hubris", "intensity": 0.8},
            {"position": 0.5, "emotion": "fear", "intensity": 0.6},  # 预感
            {"position": 0.65, "emotion": "anger", "intensity": 0.7},
            {"position": 0.8, "emotion": "despair", "intensity": 0.9},
            {"position": 0.95, "emotion": "grief", "intensity": 1.0},
            {"position": 1.0, "emotion": "acceptance", "intensity": 0.4}
        ],
        "key_moments": [
            "height of power (20-35%)",
            "fatal flaw revealed (50%)",
            "catastrophe begins (65%)",
            "complete fall (80-95%)"
        ]
    },
    
    "man_in_a_hole": {
        "description": "陷入困境后爬出的故事",
        "arc_shape": [
            {"position": 0.0, "emotion": "neutral", "intensity": 0.3},
            {"position": 0.1, "emotion": "comedy", "intensity": 0.6},  # 开场轻松
            {"position": 0.25, "emotion": "shock", "intensity": 0.9},  # 突发事件
            {"position": 0.4, "emotion": "struggle", "intensity": 0.8},
            {"position": 0.55, "emotion": "hope", "intensity": 0.5},
            {"position": 0.7, "emotion": "setback", "intensity": 0.7},  # 二次打击
            {"position": 0.85, "emotion": "determination", "intensity": 0.8},
            {"position": 1.0, "emotion": "relief_joy", "intensity": 0.7}
        ]
    },
    
    "icarus": {
        "description": "飞得太高后坠落的故事",
        "arc_shape": [
            {"position": 0.0, "emotion": "ambition", "intensity": 0.6},
            {"position": 0.2, "emotion": "success", "intensity": 0.7},
            {"position": 0.4, "emotion": "overconfidence", "intensity": 0.8},
            {"position": 0.55, "emotion": "warning_ignored", "intensity": 0.6},
            {"position": 0.7, "emotion": "fall_begins", "intensity": 0.9},
            {"position": 0.85, "emotion": "panic_despair", "intensity": 1.0},
            {"position": 1.0, "emotion": "lesson_learned", "intensity": 0.5}
        ]
    },
    
    "odyssey": {
        "description": "漫长旅程与回归",
        "arc_shape": [
            {"position": 0.0, "emotion": "restlessness", "intensity": 0.5},
            {"position": 0.15, "emotion": "adventure_calls", "intensity": 0.7},
            {"position": 0.3, "emotion": "challenges_met", "intensity": 0.6},
            {"position": 0.45, "emotion": "temptation", "intensity": 0.7},
            {"position": 0.6, "emotion": "crisis_of_faith", "intensity": 0.8},
            {"position": 0.75, "emotion": "transformation", "intensity": 0.7},
            {"position": 0.9, "emotion": "return_home", "intensity": 0.6},
            {"position": 1.0, "emotion": "wisdom_peace", "intensity": 0.8}
        ]
    }
}

# ==================== 节奏控制参数 ====================
PACING_PARAMETERS = {
    "slow_burn": {
        "description": "慢热型，逐步建立张力",
        "shot_duration_range": [4, 8],  # 秒
        "cut_frequency": "low (every 6-10 seconds)",
        "dialogue_density": "sparse, meaningful pauses",
        "music_tempo": "60-75 BPM",
        "information_reveal_rate": "gradual",
        "tension_buildup": "exponential curve over long duration"
    },
    
    "moderate_pacing": {
        "description": "中等节奏，平衡发展",
        "shot_duration_range": [3, 5],
        "cut_frequency": "medium (every 3-5 seconds)",
        "dialogue_density": "conversational flow",
        "music_tempo": "85-100 BPM",
        "information_reveal_rate": "steady",
        "tension_buildup": "linear progression with occasional peaks"
    },
    
    "fast_paced": {
        "description": "快节奏，高能量推进",
        "shot_duration_range": [1.5, 3],
        "cut_frequency": "high (every 1.5-3 seconds)",
        "dialogue_density": "rapid-fire exchanges",
        "music_tempo": "120-150 BPM",
        "information_reveal_rate": "quick, multiple threads",
        "tension_buildup": "staircase pattern with frequent releases"
    },
    
    "frantic_chaos": {
        "description": "混乱失控，极端紧迫",
        "shot_duration_range": [0.5, 2],
        "cut_frequency": "very high (subliminal cuts possible)",
        "dialogue_density": "overlapping, interruptions",
        "music_tempo": "160+ BPM or arrhythmic",
        "information_reveal_rate": "overwhelming",
        "tension_buildup": "sustained peak with no release"
    }
}

def analyze_scene_emotion(scene_text):
    """
    分析场景文本的情绪内容
    
    Args:
        scene_text: 场景描述文本
        
    Returns:
        dict: 包含情绪三维值、主导情绪、强度等
    """
    import re
    
    # 简单的关键词匹配（实际项目中应使用NLP模型）
    emotion_scores = {}
    
    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0
        for keyword, weight in keywords:
            count = len(re.findall(keyword, scene_text, re.IGNORECASE))
            score += count * weight
        emotion_scores[emotion] = score
    
    # 找出主导情绪
    if emotion_scores:
        primary_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = min(1.0, emotion_scores[primary_emotion] / 5.0)  # 归一化
    else:
        primary_emotion = "neutral"
        intensity = 0.3
    
    # 计算三维值
    emotion_vector = calculate_complex_emotion(primary_emotion)
    
    return {
        "primary_emotion": primary_emotion,
        "intensity": intensity,
        "emotion_vector": emotion_vector,
        "all_scores": emotion_scores
    }

# 情绪关键词库（简化版）
EMOTION_KEYWORDS = {
    "joy": [("happy", 2), ("laugh", 2), ("smile", 1.5), ("celebrate", 2), ("delighted", 2)],
    "sadness": [("cry", 2), ("tears", 2), ("sad", 1.5), ("heartbroken", 2), ("grief", 2)],
    "anger": [("angry", 2), ("rage", 2), ("furious", 2), ("shout", 1.5), ("hate", 2)],
    "fear": [("afraid", 2), ("terrified", 2), ("scary", 1.5), ("horror", 2), ("panic", 2)],
    "surprise": [("shocked", 2), ("amazed", 1.5), ("unexpected", 1), ("sudden", 1), ("wow", 1.5)],
    "love": [("love", 2), ("adore", 2), ("cherish", 1.5), ("passion", 2), ("romantic", 1.5)],
    "hope": [("hope", 2), ("believe", 1.5), ("dream", 1), ("future", 1), ("optimistic", 2)]
}

def generate_emotional_arc(story_type="rags_to_riches", total_episodes=98):
    """
    生成完整的情绪曲线
    
    Returns:
        list: 每集的情绪状态
    """
    if story_type not in EMOTIONAL_ARC_TEMPLATES:
        story_type = "rags_to_riches"  # 默认
    
    template = EMOTIONAL_ARC_TEMPLATES[story_type]
    arc_points = template["arc_shape"]
    
    # 插值生成每集的情绪
    episode_emotions = []
    
    for ep in range(1, total_episodes + 1):
        position = ep / total_episodes
        
        # 找到当前位置两侧的控制点
        prev_point = None
        next_point = None
        
        for i, point in enumerate(arc_points):
            if point["position"] <= position:
                prev_point = point
            if point["position"] >= position and next_point is None:
                next_point = point
                break
        
        if prev_point and next_point:
            # 线性插值
            t = (position - prev_point["position"]) / (next_point["position"] - prev_point["position"])
            
            interpolated_intensity = prev_point["intensity"] + t * (next_point["intensity"] - prev_point["intensity"])
            
            # 选择主要情绪（简单策略：选择强度更高的）
            if prev_point["intensity"] > next_point["intensity"]:
                primary_emotion = prev_point["emotion"]
            else:
                primary_emotion = next_point["emotion"]
            
            episode_emotions.append({
                "episode": ep,
                "position": position,
                "emotion": primary_emotion,
                "intensity": round(interpolated_intensity, 2),
                "vector": calculate_complex_emotion(primary_emotion)
            })
        elif prev_point:
            episode_emotions.append({
                "episode": ep,
                "position": position,
                "emotion": prev_point["emotion"],
                "intensity": prev_point["intensity"],
                "vector": calculate_complex_emotion(prev_point["emotion"])
            })
        else:
            episode_emotions.append({
                "episode": ep,
                "position": position,
                "emotion": "neutral",
                "intensity": 0.3,
                "vector": {"valence": 0, "arousal": 0.3, "dominance": 0}
            })
    
    return {
        "story_type": story_type,
        "total_episodes": total_episodes,
        "arc_template": template["description"],
        "episodes": episode_emotions,
        "key_moments": template.get("key_moments", [])
    }

def get_pacing_for_episode(episode_data, base_pacing="moderate_pacing"):
    """根据情绪状态调整节奏"""
    pacing = PACING_PARAMETERS[base_pacing].copy()
    
    intensity = episode_data.get("intensity", 0.5)
    emotion = episode_data.get("emotion", "neutral")
    
    # 高强度场景加快节奏
    if intensity > 0.7:
        if emotion in ["fear", "anger", "surprise"]:
            pacing["cut_frequency"] = "very high"
            pacing["shot_duration_range"] = [x * 0.7 for x in pacing["shot_duration_range"]]
        elif emotion in ["joy", "triumph"]:
            pacing["music_tempo"] = f"{int(pacing['music_tempo'].split('-')[0]) + 20}-{int(pacing['music_tempo'].split('-')[1]) + 20} BPM"
    
    # 低强度场景放慢节奏
    elif intensity < 0.4:
        if emotion in ["sadness", "contemplation", "peace"]:
            pacing["cut_frequency"] = "very low"
            pacing["shot_duration_range"] = [x * 1.5 for x in pacing["shot_duration_range"]]
            pacing["dialogue_density"] = "minimal, emphasis on visual storytelling"
    
    return pacing

if __name__ == "__main__":
    print("=" * 60)
    print("情绪分析系统测试")
    print("=" * 60)
    
    # 测试1：生成完整情绪曲线
    arc = generate_emotional_arc("rags_to_riches", 20)
    print(f"\n故事类型: {arc['story_type']}")
    print(f"总集数: {arc['total_episodes']}")
    print("\n关键情节点:")
    for moment in arc['key_moments']:
        print(f"  • {moment}")
    
    print("\n前10集情绪:")
    for ep in arc['episodes'][:10]:
        print(f"  第{ep['episode']:2d}集: {ep['emotion']:12s} | 强度: {ep['intensity']:.2f} | 维度: V={ep['vector']['valence']:+.2f} A={ep['arousal']:.2f} D={ep['dominance']:+.2f}")
    
    # 测试2：场景情绪分析
    test_scene = "The hero stood on the cliff edge, tears streaming down his face as he watched the enemy army approach. His heart pounded with fear, but deep down, a spark of hope remained."
    analysis = analyze_scene_emotion(test_scene)
    print(f"\n\n场景分析:")
    print(f"  主导情绪: {analysis['primary_emotion']}")
    print(f"  强度: {analysis['intensity']:.2f}")
    print(f"  三维向量: {analysis['emotion_vector']}")
