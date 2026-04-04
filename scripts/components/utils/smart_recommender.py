# -*- coding: utf-8 -*-
"""
Smart Recommender V2.0 - Two-Phase Intelligent Recommendation System
(智能推荐系统 V2.0 - 两阶段智能推荐)

Phase 1 (Quick): After novel upload, before analysis
  - Text feature extraction (length, chapters, density, keywords)
  - Quick genre detection via keyword frequency + pattern matching
  - Initial episode estimate based on content structure

Phase 2 (Precise): After semantic analysis completes  
  - Uses full_analysis_result (characters, scenes, genre, emotional arcs)
  - Uses episode_blueprints (actual split results)
  - Platform-aware optimization (TikTok vs FB Reels)
  - Strategy-aware recommendations (romance/empowerment/mystery)
"""

import os
import re
import json
import math


def quick_recommend(novel_path, platform="tiktok", strategy="romance_domination_strategy"):
    """
    Phase 1: Quick recommendation after upload (no LLM needed)
    Returns basic recommendations based on text features only.
    """
    if not os.path.exists(novel_path):
        return {"status": "error", "message": "Novel file not found"}
    
    with open(novel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total_chars = len(content)
    total_lines = content.count('\n')
    
    # ====== 1. 章节结构分析 ======
    chapter_patterns = [
        r'第[一二三四五六七八九十百千零\d]+[章节回集部卷]',  
        r'Chapter\s*\d+',
        r'CHAPTER\s*\d+',
        r'^\s*[\d]+\.[\s\S]',  
        r'^\s*[【\[].{1,10}[】\]]', 
    ]
    chapter_count = 0
    for pattern in chapter_patterns:
        matches = re.findall(pattern, content, re.MULTILINE | re.IGNORECASE)
        if len(matches) > chapter_count:
            chapter_count = len(matches)
    
    if chapter_count == 0:
        avg_chapter_len = total_chars / max(1, total_lines / 50)  
    else:
        avg_chapter_len = total_chars / chapter_count
    
    # ====== 2. 对话密度分析 ======
    dialogue_pattern = r'[「『"“][^」』"”]+[」』""]|"[^"]+"'
    dialogue_matches = re.findall(dialogue_pattern, content)
    dialogue_chars = sum(len(m) for m in dialogue_matches)
    dialogue_ratio = dialogue_chars / max(1, total_chars)
    
    # ====== 3. 角色名检测（启发式）=====
    name_patterns = [
        r'(?:叫|是|的|和|对|向|给|跟|与)([A-Z][a-z]{1,15})',
        r'([一-龥]{2,4})(?:说|道|问|答|喊|叫|想|看|听|笑|哭|怒)',
    ]
    potential_names = set()
    for pattern in name_patterns:
        matches = re.findall(pattern, content)
        for m in matches:
            if isinstance(m, tuple):
                m = m[0]
            if len(m) >= 2 and len(m) <= 4:
                potential_names.add(m)
    
    estimated_characters = min(len(potential_names), 50)
    
    # ====== 4. 题材关键词加权检测 ======
    genre_keywords = {
        "ancient_wuxia": {
            "keywords": ["武功", "江湖", "侠客", "剑", "内功", "修仙", "门派", "掌门", "轻功", "真气", "丹药", "法宝", "宗师", "少侠", "大侠", "武林", "江湖", "朝廷", "王爷", "妃子"],
            "weight": 3.0
        },
        "modern_urban": {
            "keywords": ["公司", "总裁", "职场", "都市", "手机", "电脑", "办公室", "会议", "合同", "签约", "面试", "升职", "辞职", "咖啡", "酒吧", "公寓", "别墅", "跑车", "名牌"],
            "weight": 2.5
        },
        "scifi_fantasy": {
            "keywords": ["飞船", "机器人", "AI", "未来", "太空", "科技", "星球", "外星", "基因", "克隆", "虚拟", "系统", "穿越时空", "量子", "纳米", "全息"],
            "weight": 2.0
        },
        "romance": {
            "keywords": ["喜欢", "爱", "心动", "表白", "约会", "浪漫", "吻", "拥抱", "结婚", "求婚", "初恋", "暗恋", "热恋", "分手", "复合", "心动", "脸红", "害羞"],
            "weight": 3.0
        },
        "suspense_mystery": {
            "keywords": ["谋杀", "侦探", "线索", "真相", "谜团", "秘密", "尸体", "凶手", "证据", "嫌疑", "推理", "阴谋", "失踪", "绑架", "威胁", "恐吓"],
            "weight": 2.0
        },
        "paranormal": {
            "keywords": ["鬼", "魂", "灵", "妖", "魔", "神", "诅咒", "预言", "前世", "来世", "转世", "阴阳", "道士", "符咒", "驱鬼", "附身"],
            "weight": 2.5
        },
        "campus_youth": {
            "keywords": ["学校", "大学", "考试", "宿舍", "食堂", "图书馆", "同学", "老师", "班长", "校花", "校草", "毕业", "社团", "军训", "运动会"],
            "weight": 1.8
        },
        "historical": {
            "keywords": ["皇帝", "皇后", "太子", "公主", "将军", "尚书", "丞相", "后宫", "朝堂", "边疆", "战事", "和亲", "赐婚", "册封", "废黜"],
            "weight": 2.2
        }
    }
    
    genre_scores = {}
    for genre_id, info in genre_keywords.items():
        score = 0
        for kw in info["keywords"]:
            count = content.count(kw)
            score += count * info["weight"]
        if score > 0:
            genre_scores[genre_id] = int(score)
    
    detected_genres = sorted(genre_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    
    # ====== 5. 情绪密度分析 ======
    emotion_keywords = {
        "joy": ["开心", "快乐", "幸福", "笑", "高兴", "喜悦", "甜蜜", "温馨", "满足", "兴奋"],
        "sadness": ["哭", "泪", "悲伤", "难过", "心痛", "痛苦", "失落", "绝望", "孤独", "寂寞"],
        "anger": ["怒", "恨", "气", "愤怒", "暴怒", "恼火", "不甘", "怨恨", "复仇", "报复"],
        "fear": ["怕", "恐惧", "害怕", "紧张", "担心", "焦虑", "惊慌", "颤抖", "冷汗", "危险"],
        "love": ["爱", "喜欢", "恋", "心动", "迷恋", "深情", "挚爱", "眷恋", "思念", "渴望"],
        "surprise": ["惊", "意外", "震惊", "没想到", "居然", "竟然", "突然", "忽然", "出乎意料"]
    }
    
    emotion_density = {}
    for emotion, words in emotion_keywords.items():
        count = sum(content.count(w) for w in words)
        emotion_density[emotion] = count
    
    total_emotion_markers = sum(emotion_density.values())
    emotion_intensity = total_emotion_markers / max(1, total_chars / 1000)  # per 1000 chars
    
    # ====== 6. 冲突/转折频率 ======
    conflict_markers = ["但是", "然而", "不料", "突然", "竟然", "居然", "没想到", "谁知", "岂料", "偏偏", "危机", "危险", "困境", "绝境"]
    conflict_count = sum(content.count(m) for m in conflict_markers)
    conflict_density = conflict_count / max(1, total_chars / 1000)
    
    # ====== 7. 集数智能估算 ======
    base_episodes = _calculate_episode_estimate(
        total_chars=total_chars,
        chapter_count=max(chapter_count, 1),
        character_count=estimated_characters,
        dialogue_ratio=dialogue_ratio,
        conflict_density=conflict_density,
        emotion_intensity=emotion_intensity,
        platform=platform,
        strategy=strategy
    )
    
    # ====== 8. 构建推荐结果 ======
    primary_genre = detected_genres[0][0] if detected_genres else "unknown"
    genre_name_map = {
        "ancient_wuxia": "古风武侠/仙侠",
        "modern_urban": "现代都市/职场",
        "scifi_fantasy": "科幻未来",
        "romance": "言情/情感",
        "suspense_mystery": "悬疑/推理",
        "paranormal": "奇幻/超自然",
        "campus_youth": "校园青春",
        "historical": "古代权谋/宫斗"
    }
    
    recommendations = {
        "phase": 1,
        "phase_label": "快速预估（基于文本特征）",
        "text_stats": {
            "total_chars": total_chars,
            "total_lines": total_lines,
            "detected_chapters": chapter_count,
            "avg_chapter_length": int(avg_chapter_len),
            "estimated_characters": estimated_characters,
            "dialogue_ratio": round(dialogue_ratio * 100, 1),
            "conflict_density": round(conflict_density, 2),
            "emotion_intensity": round(emotion_intensity, 2),
        },
        "episodes": {
            "recommended": base_episodes["value"],
            "range": base_episodes["range"],
            "reason": base_episodes["reason"],
            "confidence": base_episodes["confidence"],
            "factors": base_episodes["factors"]
        },
        "genre": {
            "primary": genre_name_map.get(primary_genre, primary_genre),
            "all_detected": [(genre_name_map.get(g, g), s) for g, s in detected_genres],
            "confidence": "高" if detected_genres and detected_genres[0][1] > 50 else ("中" if detected_genres else "低")
        },
        "style_recommendation": {
            "suggested_template": _map_genre_to_template(primary_genre),
            "suggested_director_style": _map_genre_to_director(primary_genre),
            "suggested_tone": _map_genre_to_tone(primary_genre, emotion_density)
        },
        "platform_optimization": {
            "target_platform": platform,
            "suggested_episode_duration": _get_platform_episode_duration(platform, strategy),
            "pacing_note": _get_pacing_note(conflict_density, emotion_intensity, platform)
        }
    }
    
    return {"status": "success", "recommendations": recommendations}


def precise_recommend(full_analysis_result=None, episode_blueprints=None, platform="tiktok", strategy="romance_domination_strategy"):
    """
    Phase 2: Precise recommendation after semantic analysis completes.
    Uses real analysis data from the pipeline.
    """
    if not full_analysis_result:
        return {"status": "error", "message": "No analysis data available yet"}
    
    # 从语义分析结果中提取真实数据
    characters = full_analysis_result.get('characters', [])
    scenes = full_analysis_result.get('scenes', [])
    genre = full_analysis_result.get('genre', 'unknown')
    original_recommended = full_analysis_result.get('recommended_episode_count', 0)
    core_themes = full_analysis_result.get('core_themes', [])
    tone = full_analysis_result.get('tone', {})
    narrative_arc = full_analysis_result.get('narc_structure', {})
    
    actual_episode_count = len(episode_blueprints) if episode_blueprints else original_recommended
    
    # 分析角色复杂度
    main_characters = [c for c in characters if c.get('role') in ['protagonist', 'main', '主角', '主要']]
    supporting_characters = [c for c in characters if c.get('role') in ['supporting', '配角', '次要']]
    character_complexity_score = (
        len(main_characters) * 10 +
        len(supporting_characters) * 3 +
        len(characters) * 1
    )
    
    # 分析每集蓝图的信息密度
    blueprint_complexity = []
    if episode_blueprints:
        for bp in episode_blueprints[:min(20, len(episode_blueprints))]:
            bp_text = str(bp.get('summary', '')) + str(bp.get('core_plot', ''))
            blueprint_complexity.append(len(bp_text))
        avg_blueprint_len = sum(blueprint_complexity) / max(1, len(blueprint_complexity))
    else:
        avg_blueprint_len = 0
    
    # 平台感知调整
    platform_adjustments = _get_platform_adjustments(
        platform=platform,
        strategy=strategy,
        character_count=len(characters),
        scene_count=len(scenes),
        avg_blueprint_len=avg_blueprint_len
    )
    
    # 最终推荐集数（基于实际分集结果 + 平台调整）
    final_recommendation = platform_adjustments.get(
        'adjusted_episodes',
        actual_episode_count or original_recommended
    )
    
    # 构建策略建议
    strategy_advice = _build_strategy_advice(
        strategy=strategy,
        character_count=len(characters),
        scene_count=len(scenes),
        genre=genre,
        platform=platform
    )
    
    recommendations = {
        "phase": 2,
        "phase_label": "精准推荐（基于语义分析结果）",
        "analysis_data_available": True,
        
        "episodes": {
            "semantic_analyzer_original": original_recommended,
            "actual_split_result": actual_episode_count,
            "platform_adjusted": final_recommendation,
            "adjustment_reason": platform_adjustments.get('reason', ''),
            "confidence": "很高" if actual_episode_count > 0 else "高"
        },
        
        "characters_analysis": {
            "total_characters": len(characters),
            "main_characters": len(main_characters),
            "supporting_characters": len(supporting_characters),
            "complexity_score": character_complexity_score,
            "complexity_level": "高" if character_complexity_score > 50 else ("中" if character_complexity_score > 20 else "低"),
            "per_episode_capacity": max(1, 3 // max(1, len(main_characters)))
        },
        
        "world_building": {
            "total_scenes": len(scenes),
            "unique_locations": len(set(s.get('location', '') for s in scenes)),
            "genre_classification": genre,
            "core_themes": core_themes[:5] if core_themes else [],
            "tone_profile": tone
        },
        
        "strategy_advice": strategy_advice,
        
        "platform_optimization": {
            "target_platform": platform,
            "target_strategy": strategy,
            "optimal_episode_duration": platform_adjustments.get('duration_range', '30-60s'),
            "recommended_hooks_per_episode": platform_adjustments.get('hooks_per_episode', 3),
            "climax_position": platform_adjustments.get('climax_position', '75-85%'),
            "pacing_strategy": platform_adjustments['pacing_strategy']
        },
        
        "quality_predictions": {
            "storyboard_quality_potential": _predict_quality(character_complexity_score, len(scenes), avg_blueprint_len),
            "engagement_prediction": _predict_engagement(genre, strategy, platform),
            "viral_potential": _predict_viral_potential(genre, strategy, emotion_density={})
        }
    }
    
    return {"status": "success", "recommendations": recommendations}


# ==================== 内部计算函数 ====================

def _calculate_episode_estimate(total_chars, chapter_count, character_count, dialogue_ratio, conflict_density, emotion_intensity, platform, strategy):
    """基于多维度特征的集数估算"""
    
    # 基础：按字符量
    if total_chars < 30000:
        base = 8
        reason_base = "短篇小说"
    elif total_chars < 80000:
        base = 18
        reason_base = "中短篇"
    elif total_chars < 150000:
        base = 35
        reason_base = "标准长度"
    elif total_chars < 300000:
        base = 60
        reason_base = "长篇小说"
    elif total_chars < 500000:
        base = 85
        reason_base = "超长篇"
    else:
        base = 98
        reason_base = "巨著级"
    
    # 调整因子
    factors = []
    adjustment = 0
    
    # 章节调整：章节数多 → 可以更多集
    if chapter_count >= 50:
        adj = 15
        factors.append(f"+{adj} 检测到{chapter_count}个章节，适合细分为多集")
        adjustment += adj
    elif chapter_count >= 30:
        adj = 8
        factors.append(f"+{adj} {chapter_count}个章节，可适度细分")
        adjustment += adj
    elif chapter_count >= 15:
        adj = 3
        factors.append(f"+{adj} {chapter_count}个章节")
        adjustment += adj
    
    # 对话密度调整：对话多 → 每集信息量大 → 可减少集数
    if dialogue_ratio > 0.4:
        adj = -8
        factors.append(f"{adj} 对话占比高({dialogue_ratio*100:.0f}%)，每集信息密度大，适当减少集数")
        adjustment += adj
    elif dialogue_ratio > 0.25:
        adj = -3
        factors.append(f"{adj} 对话较多({dialogue_ratio*100:.0f}%)")
        adjustment += adj
    
    # 冲突密度调整：冲突多 → 剧情紧凑 → 可承载更多集
    if conflict_density > 5:
        adj = 12
        factors.append(f"+{adj} 高冲突密度({conflict_density:.1f}/千字)，情节丰富可支撑更多集")
        adjustment += adj
    elif conflict_density > 2.5:
        adj = 5
        factors.append(f"+{adj} 中等冲突密度")
        adjustment += adj
    elif conflict_density < 1:
        adj = -5
        factors.append(f"{adj} 低冲突密度，节奏偏慢，建议精简集数")
        adjustment += adj
    
    # 情绪强度调整：情绪词密集 → 适合短视频平台多集快节奏
    if emotion_intensity > 8:
        adj = 10
        factors.append(f"+{adj} 高情绪强度({emotion_intensity:.1f}/千字)，情绪驱动型叙事适合多集短剧")
        adjustment += adj
    elif emotion_intensity > 4:
        adj = 4
        factors.append(f"+{adj} 中等情绪强度")
        adjustment += adj
    
    # 角色数量调整
    if character_count > 15:
        adj = 8
        factors.append(f"+{adj} 多角色({character_count}人)，需要足够篇幅展开人物线")
        adjustment += adj
    elif character_count > 8:
        adj = 3
        factors.append(f"+{adj} 较多角色({character_count}人)")
        adjustment += adj
    
    # 平台特定调整
    if platform == "tiktok":
        tiktok_adj = -round(base * 0.1)
        factors.append(f"{tiktok_adj} TikTok平台优化：每集15-60s，建议比通用模式减少约10%集数以控制总时长")
        adjustment += tiktok_adj
    elif platform == "facebook_reels":
        fb_adj = round(base * 0.05)
        factors.append(f"+{fb_adj} Facebook Reels：支持更长单集内容(30-90s)，可适当增加集数")
        adjustment += fb_adj
    
    # 策略特定调整
    if "empowerment" in strategy:
        strat_adj = -round(base * 0.08)
        factors.append(f"{strat_adj} 逆袭策略：快节奏爽感释放，不宜拖沓，建议精简集数")
        adjustment += strat_adj
    elif "mystery" in strategy:
        strat_adj = round(base * 0.1)
        factors.append(f"+{strat_adj} 悬疑策略：需要足够的铺垫和反转空间，建议增加集数")
        adjustment += strat_adj
    
    final_episodes = max(5, min(98, base + adjustment))
    
    range_low = max(3, int(final_episodes * 0.7))
    range_high = min(98, int(final_episodes * 1.3))
    
    confidence = "高" if chapter_count > 10 else ("中" if total_chars > 50000 else "低(仅基于字符数)")
    
    return {
        "value": final_episodes,
        "range": f"{range_low}-{range_high}",
        "reason": f"{reason_base}(基础{base}集) + 综合调整({adjustment:+d}集) = {final_episodes}集",
        "confidence": confidence,
        "factors": factors
    }


def _map_genre_to_template(genre_id):
    mapping = {
        "ancient_wuxia": "ancient",
        "modern_urban": "modern",
        "scifi_fantasy": "scifi",
        "romance": "tiktok_romance",
        "suspense_mystery": "suspense",
        "paranormal": "tiktok_mystery",
        "campus_youth": "modern",
        "historical": "ancient"
    }
    return mapping.get(genre_id, "modern")


def _map_genre_to_director(genre_id):
    mapping = {
        "ancient_wuxia": "miyazaki",
        "modern_urban": "spielberg",
        "scifi_fantasy": "nolan",
        "romance": "wong_kar_wai",
        "suspense_mystery": "fincher",
        "paranormal": "nolan",
        "campus_youth": "spielberg",
        "historical": "miyazaki"
    }
    return mapping.get(genre_id, "nolan")


def _map_genre_to_tone(genre_id, emotion_density):
    top_emotion = max(emotion_density.items(), key=lambda x: x[1])[0] if emotion_density else "neutral"
    
    tone_map = {
        "ancient_wuxia": "史诗感强，气势恢宏",
        "modern_urban": "都市精致，节奏明快",
        "scifi_fantasy": "未来感，科技美学",
        "romance": "温暖浪漫，情感细腻",
        "suspense_mystery": "紧张悬疑，氛围压抑",
        "paranormal": "神秘诡谲，氛围感强",
        "campus_youth": "青春活力，清新明亮",
        "historical": "厚重深沉，古典雅致"
    }
    return tone_map.get(genre_id, "平衡中性")


def _get_platform_episode_duration(platform, strategy):
    durations = {
        "tiktok": {
            "romance_domination_strategy": "25-45秒/集（甜虐交替节奏）",
            "empowerment_revenge_strategy": "20-35秒/集（快节奏打脸）",
            "mystery_paranormal_strategy": "35-55秒/集（悬念铺垫需要时间）"
        },
        "facebook_reels": {
            "romance_domination_strategy": "45-75秒/集（更细腻的情感表达）",
            "empowerment_revenge_strategy": "35-55秒/集（完整情节弧线）",
            "mystery_paranormal_strategy": "60-80秒/集（深度叙事）"
        }
    }
    return durations.get(platform, {}).get(strategy, "30-60秒/集")


def _get_pacing_note(conflict_density, emotion_intensity, platform):
    if conflict_density > 3 and emotion_intensity > 5:
        return "高冲突+高情绪：建议采用'爆发式'节奏，每集设置至少1个小高潮"
    elif conflict_density > 2:
        return "中等冲突：建议采用'波浪式'节奏，张弛有度"
    elif platform == "tiktok":
        return "TikTok适配：前3秒必须有Hook，每5-8秒一个变化点"
    return "标准节奏：平稳推进，关键节点设置高潮"


def _get_platform_adjustments(platform, strategy, character_count, scene_count, avg_blueprint_len):
    adjustments = {
        "pacing_strategy": "balanced"
    }
    
    if platform == "tiktok":
        adjustments.update({
            "duration_range": "15-60s",
            "hooks_per_episode": 3,
            "climax_position": "70-80%",
            "reason": "TikTok竖屏短剧优化：控制单集时长，强化Hook设计"
        })
        if "empowerment" in strategy:
            adjustments["pacing_strategy"] = "fast_burn"
            adjustments["adjusted_episodes"] = None  # 不强制修改，由用户决定
        elif "romance" in strategy:
            adjustments["pacing_strategy"] = "slow_burn_with_peaks"
        elif "mystery" in strategy:
            adjustments["pacing_strategy"] = "tension_build"
            
    elif platform == "facebook_reels":
        adjustments.update({
            "duration_range": "30-90s",
            "hooks_per_episode": 2,
            "climax_position": "75-85%",
            "reason": "Facebook Reels优化：允许更长的叙事空间"
        })
        adjustments["pacing_strategy"] = "cinematic"
    
    return adjustments


def _build_strategy_advice(strategy, character_count, scene_count, genre, platform):
    advices = {
        "romance_domination_strategy": {
            "beat_structure": "甜→微虐→更甜→大虐→治愈（情绪过山车）",
            "character_focus": "女主视角为主，男主神秘感逐步揭开",
            "visual_priority": "眼神特写、手部动作、光影变化传达情绪",
            "audio_priority": "acoustic guitar, lo-fi beats, trending sounds",
            "hook_design": "每集结尾留悬念式情感转折",
            "climax_frequency": "每3-4集一个大情感高潮"
        },
        "empowerment_revenge_strategy": {
            "beat_structure": "被低估→暗中积蓄→第一次反击→更大挑战→终极打脸",
            "character_focus": "女主成长弧线为核心，反派鲜明但不过度脸谱化",
            "visual_priority": "power pose构图、从低角度到平视的镜头语言变化",
            "audio_priority": "building orchestral drops, empowering anthems",
            "hook_design": "每次反击后的满足感+下一个更大的危机预告",
            "climax_frequency": "每2-3集一个小爽点，每5集一个大爽点"
        },
        "mystery_paranormal_strategy": {
            "beat_structure": "日常→异常事件→调查→发现线索→更大的谜团→部分真相",
            "character_focus": "女主好奇心+勇气为主线，超自然元素逐步揭露",
            "visual_priority": "异常光影、悬浮镜头效果、超现实色彩渐变",
            "audio_priority": "ethereal choirs, haunting melodies, ambient drones",
            "hook_design": "每个答案引出2个新问题（信息阶梯式递进）",
            "climax_frequency": "每集一个小反转，每4集一个大揭秘"
        }
    }
    base = advices.get(strategy, advices["romance_domination_strategy"])
    
    base["character_count_note"] = f"当前检测{character_count}个角色，{'角色丰富度高，注意主次分配' if character_count > 8 else '角色适中，可充分展开'}"
    base["scene_diversity_note"] = f"当前{scene_count}个场景，{'场景多样性好' if scene_count > 5 else '建议增加场景多样性'}"
    
    return base


def _predict_quality(char_complexity, scene_count, avg_bp_len):
    score = 0
    if char_complexity > 40:
        score += 25
    elif char_complexity > 20:
        score += 18
    else:
        score += 10
        
    if scene_count > 8:
        score += 20
    elif scene_count > 4:
        score += 14
    else:
        score += 8
        
    if avg_bp_len > 200:
        score += 20
    elif avg_bp_len > 100:
        score += 14
    else:
        score += 7
        
    score += 15  # baseline
    
    if score >= 80:
        return "A (优秀)", score
    elif score >= 65:
        return "B+ (良好)", score
    elif score >= 50:
        return "B (合格)", score
    elif score >= 35:
        return "C (一般)", score
    else:
        return "D (需优化)", score


def _predict_engagement(genre, strategy, platform):
    engagement_matrix = {
        ("romance", "romance_domination", "tiktok"): 92,
        ("romance", "romance_domination", "facebook_reels"): 85,
        ("modern_urban", "empowerment_revenge", "tiktok"): 88,
        ("modern_urban", "empowerment_revenge", "facebook_reels"): 78,
        ("paranormal", "mystery_paranormal", "tiktok"): 86,
        ("paranormal", "mystery_paranormal", "facebook_reels"): 80,
    }
    key = (genre.split('_')[0] if '_' in genre else genre, strategy.replace('_strategy', ''), platform)
    score = engagement_matrix.get(key, 70)
    
    if score >= 85:
        return "极高 (预计完播率>65%)", score
    elif score >= 75:
        return "高 (预计完播率50-65%)", score
    elif score >= 60:
        return "中等 (预计完播率35-50%)", score
    else:
        return "待优化", score


def _predict_viral_potential(genre, strategy, emotion_density):
    viral_scores = {
        "romance_domination_strategy": 90,
        "empowerment_revenge_strategy": 85,
        "mystery_paranormal_strategy": 78
    }
    base = viral_scores.get(strategy, 70)
    
    genre_bonus = {
        "romance": 10, "modern_urban": 8, "paranormal": 7,
        "ancient_wuxia": 5, "suspense_mystery": 8, "campus_youth": 6
    }.get(genre.split('_')[0] if '_' in genre else genre, 0)
    
    final = min(99, base + genre_bonus)
    
    if final >= 85:
        return "极高 (易引发转发和讨论)", final
    elif final >= 72:
        return "高 (有较好的分享性)", final
    elif final >= 55:
        return "中等", final
    else:
        return "较低", final
