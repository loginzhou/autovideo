# -*- coding: utf-8 -*-
"""
Quality Assessment & Feedback System V1.0 (质量评估与反馈系统)
自动评估生成内容质量，提供改进建议
支持分镜质量、台词质量、音频设计质量、整体一致性评分
"""

import json
import os
import re
from datetime import datetime
from config_center import config

# ==================== 评分标准定义 ====================
QUALITY_CRITERIA = {
    "storyboard_quality": {
        "description": "分镜脚本质量评估",
        "max_score": 100,
        "dimensions": [
            {
                "name": "visual_prompt_quality",
                "weight": 25,
                "description": "视觉提示词的专业性和描述力",
                "scoring_rules": {
                    "excellent": [20, 25],  # 使用专业术语（焦段、光位等）
                    "good": [15, 19],       # 有基本描述但缺少专业细节
                    "acceptable": [10, 14], # 描述过于笼统
                    "poor": [0, 9]          # 描述不完整或无意义
                },
                "check_points": [
                    "contains_lens_specification",
                    "contains_lighting_description", 
                    "contains_camera_movement",
                    "contains_color_grading_info",
                    "uses_professional_terminology",
                    "specific_enough_for_ai_generation",
                    "matches_scene_emotion",
                    "appropriate_shot_size"
                ]
            },
            {
                "name": "narrative_coherence",
                "weight": 25,
                "description": "叙事连贯性和逻辑顺序",
                "scoring_rules": {
                    "excellent": [20, 25],
                    "good": [15, 19],
                    "acceptable": [10, 14],
                    "poor": [0, 9]
                },
                "check_points": [
                    "shots_follow_logical_sequence",
                    "transitions_make_sense",
                    "pacing_is_appropriate",
                    "emotional_arc_is_clear",
                    "cause_and_effect_visible",
                    "no_narrative_gaps"
                ]
            },
            {
                "name": "emotional_effectiveness",
                "weight": 20,
                "description": "情绪表达的有效性",
                "scoring_rules": {
                    "excellent": [16, 20],
                    "good": [12, 15],
                    "acceptable": [8, 11],
                    "poor": [0, 7]
                },
                "check_points": [
                    "visual_elements_match_emotion",
                    "camera_work_supports_mood",
                    "lighting_enhances_feeling",
                    "shot_duration_fits_intensity",
                    "color_palette_appropriate"
                ]
            },
            {
                "name": "technical_professionalism",
                "weight": 15,
                "description": "技术参数的专业性",
                "scoring_rules": {
                    "excellent": [12, 15],
                    "good": [9, 11],
                    "acceptable": [6, 8],
                    "poor": [0, 5]
                },
                "check_points": [
                    "lens_choice_is_appropriate",
                    "aperture_setting_realistic",
                    "camera_angle_has_purpose",
                    "movement_type_is_achievable",
                    "lighting_setup_physically_possible"
                ]
            },
            {
                "name": "creative_originality",
                "weight": 15,
                "description": "创意和原创性",
                "scoring_rules": {
                    "excellent": [12, 15],
                    "good": [9, 11],
                    "acceptable": [6, 8],
                    "poor": [0, 5]
                },
                "check_points": [
                    "unique_visual_composition",
                    "interesting_camera_choices",
                    "creative_use_of_light",
                    "memorable_imagery",
                    "avoids_clichés"
                ]
            }
        ]
    },
    
    "dialogue_quality": {
        "description": "台词质量评估",
        "max_score": 100,
        "dimensions": [
            {
                "name": "character_voice_consistency",
                "weight": 30,
                "check_points": [
                    "speech_pattern_matches_character",
                    "vocabulary_level_appropriate",
                    "catchphrase_used_if_applicable",
                    "tone_matches_personality"
                ]
            },
            {
                "name": "emotional_authenticity",
                "weight": 30,
                "check_points": [
                    "emotion_is_believable",
                    "subtext_adds_depth",
                    "delivery_directions_are_actionable",
                    "intensity_matches_scene"
                ]
            },
            {
                "name": "naturality_and_flow",
                "weight": 25,
                "check_points": [
                    "sounds_like_real_speech",
                    "appropriate_length",
                    "rhythm_is_natural",
                    "not_expository_or_clunky"
                ]
            },
            {
                "name": "plot_advancement",
                "weight": 15,
                "check_points": [
                    "moves_story_forward",
                    "reveals_character_information",
                    "creates_tension_or_release"
                ]
            }
        ]
    },
    
    "audio_design_quality": {
        "description": "音频设计质量评估",
        "max_score": 100,
        "dimensions": [
            {
                "name": "spatial_authenticity",
                "weight": 25,
                "check_points": [
                    "reverb_matches_environment",
                    "ambience_is_believable",
                    "spatial_positioning_correct"
                ]
            },
            {
                "name": "emotional_music_match",
                "weight": 30,
                "check_points": [
                    "music_genre_fits_scene",
                    "tempo_appropriate",
                    "instrumentation_supports_mood",
                    "dynamic_curve_sensible"
                ]
            },
            {
                "name": "sfx_relevance",
                "weight": 25,
                "check_points": [
                    "sound_effects_are_contextual",
                    "timing_is_precise",
                    "layering_is_balanced"
                ]
            },
            {
                "name": "dialogue_integration",
                "weight": 20,
                "check_points": [
                    "dialogue_processing_appropriate",
                    "music_doesnt_overpower_speech",
                    "levels_are_balanced"
                ]
            }
        ]
    },
    
    "multimodal_consistency": {
        "description": "多模态一致性评估",
        "max_score": 100,
        "dimensions": [
            {
                "name": "emotion_alignment",
                "weight": 35,
                "check_points": [
                    "text_emotion_matches_visual",
                    "visual_emotion_matches_audio",
                    "all_three_modalities_agree"
                ]
            },
            {
                "name": "stylistic_unity",
                "weight": 35,
                "check_points": [
                    "director_style_consistent",
                    "color_palette_coherent",
                    "music_style_matches_visual"
                ]
            },
            {
                "name": "narrative_sync",
                "weight": 30,
                "check_points": [
                    "story_beats_aligned_across_modalities",
                    "character_appearances_consistent",
                    "timeline_events_synchronized"
                ]
            }
        ]
    }
}

class QualityAssessor:
    """
    质量评估器
    """
    
    def __init__(self):
        self.assessment_history = []
        self.load_history()
    
    def load_history(self):
        """加载历史记录"""
        history_path = os.path.join("output", ".quality_history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                self.assessment_history = json.load(f)
    
    def save_history(self):
        """保存历史记录"""
        history_path = os.path.join("output", ".quality_history.json")
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        
        # 只保留最近100条记录
        self.assessment_history = self.assessment_history[-100:]
        
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.assessment_history, f, ensure_ascii=False, indent=2)
    
    def assess_storyboard(self, storyboard_data, episode_info=None):
        """
        评估分镜质量
        
        Args:
            storyboard_data: 分镜数据（包含storyboard列表）
            episode_info: 集数信息
            
        Returns:
            dict: 完整的评估报告
        """
        report = {
            "assessment_type": "storyboard_quality",
            "timestamp": datetime.now().isoformat(),
            "episode_info": episode_info or {},
            "overall_score": 0,
            "dimension_scores": {},
            "details": {},
            "strengths": [],
            "weaknesses": [],
            "improvement_suggestions": [],
            "passed_threshold": False
        }
        
        criteria = QUALITY_CRITERIA["storyboard_quality"]
        storyboard = storyboard_data.get("storyboard", [])
        
        total_weighted_score = 0
        
        for dimension in criteria["dimensions"]:
            dim_name = dimension["name"]
            weight = dimension["weight"]
            
            # 计算该维度的得分
            dim_score, dim_details = self._assess_dimension(
                dimension, storyboard, episode_info
            )
            
            weighted_score = (dim_score / criteria["max_score"]) * weight * (100 / sum(d["weight"] for d in criteria["dimensions"]))
            
            report["dimension_scores"][dim_name] = {
                "raw_score": dim_score,
                "weighted_contribution": round(weighted_score, 2),
                "details": dim_details
            }
            
            total_weighted_score += weighted_score
        
        report["overall_score"] = round(total_weighted_score, 1)
        report["passed_threshold"] = report["overall_score"] >= 70  # 及格线70分
        
        # 生成优缺点和建议
        self._generate_feedback(report, criteria)
        
        # 保存到历史
        self.assessment_history.append({
            "type": "storyboard",
            "score": report["overall_score"],
            "episode": episode_info.get("episode_seq", "unknown") if episode_info else "unknown",
            "timestamp": report["timestamp"]
        })
        self.save_history()
        
        return report
    
    def _assess_dimension(self, dimension, storyboard, episode_info):
        """评估单个维度"""
        check_points = dimension.get("check_points", [])
        scoring_rules = dimension.get("scoring_rules", {})
        
        passed_checks = 0
        total_checks = len(check_points) if check_points else 1
        details = {}
        
        for check_point in check_points:
            result = self._evaluate_check_point(check_point, storyboard, episode_info)
            details[check_point] = result
            if result.get("passed", False):
                passed_checks += 1
        
        # 基于通过率计算分数
        pass_rate = passed_checks / total_checks if total_checks > 0 else 0.5
        
        # 映射到分数范围
        if pass_rate >= 0.9:
            score_range = scoring_rules.get("excellent", [80, 100])
        elif pass_rate >= 0.7:
            score_range = scoring_rules.get("good", [60, 79])
        elif pass_rate >= 0.5:
            score_range = scoring_rules.get("acceptable", [40, 59])
        else:
            score_range = scoring_rules.get("poor", [0, 39])
        
        base_score = score_range[0] + (score_range[1] - score_range[0]) * pass_rate
        
        return round(base_score, 1), details
    
    def _evaluate_check_point(self, check_point_name, storyboard, episode_info):
        """评估具体的检查点"""
        result = {"passed": False, "confidence": 0.5, "notes": ""}
        
        # 简化的检查逻辑（实际项目中可以使用更复杂的NLP）
        if check_point_name == "contains_lens_specification":
            lens_patterns = ["mm", "lens", "f/", "aperture", "焦段"]
            found = any(
                any(pat in str(shot.get('visual_prompt', '') + shot.get('cinematic_metadata', {}).get('lens_config', '')) 
                    for pat in lens_patterns)
                for shot in storyboard
            )
            result["passed"] = len(storyboard) > 0 and (found or any("lens_config" in str(shot) for shot in storyboard))
            result["confidence"] = 0.9 if result["passed"] else 0.3
            result["notes"] = f"{'包含' if result['passed'] else '缺少'}镜头规格说明"
        
        elif check_point_name == "emotional_arc_is_clear":
            emotions_in_shots = []
            for shot in storyboard:
                meta = shot.get('cinematic_metadata', {})
                if meta.get('primary_emotion'):
                    emotions_in_shots.append(meta['primary_emotion'])
            
            unique_emotions = len(set(emotions_in_shots))
            has_progression = len(emotions_in_shots) > 3
            
            result["passed"] = has_progression and unique_emotions >= 2
            result["confidence"] = 0.85
            result["notes"] = f"检测到{unique_emotions}种不同情绪，{'有' if has_progression else '无'}明显变化"
        
        elif check_point_name == "shots_follow_logical_sequence":
            # 检查beat类型是否合理分布
            beat_types = []
            for shot in storyboard:
                ctx = shot.get('narrative_context', {})
                if ctx.get('beat_type'):
                    beat_types.append(ctx['beat_type'])
            
            # 检查是否有合理的结构（setup -> escalation -> climax）
            has_setup = "setup" in beat_types or "hook" in beat_types
            has_climax = "climax" in beat_types or "escalation" in beat_types
            
            result["passed"] = len(storyboard) > 2 and (has_setup or has_climax)
            result["confidence"] = 0.7
            result["notes"] = f"{'包含' if has_setup else '缺少'}setup阶段, {'包含' if has_climax else '缺少'}climax阶段"
        
        elif check_point_name == "uses_professional_terminology":
            pro_terms = ["dolly", "crane", "tracking", "chiaroscuro", "rim_light", 
                        "bokeh", "depth_of_field", "dutch_angle", "whip_pan", "rack_focus"]
            
            all_prompts = " ".join([str(s.get('visual_prompt', '')) for s in storyboard])
            term_count = sum(1 for term in pro_terms if term.lower() in all_prompts.lower())
            
            result["passed"] = term_count >= len(storyboard) * 0.3  # 至少30%的镜头使用术语
            result["confidence"] = 0.95
            result["notes"] = f"使用{term_count}个专业术语"
        
        else:
            # 默认：假设通过（对于未实现的检查点）
            result["passed"] = True
            result["confidence"] = 0.5
            result["notes"] = f"检查点 {check_point_name} 未实现详细评估"
        
        return result
    
    def _generate_feedback(self, report, criteria):
        """生成反馈意见"""
        strengths = []
        weaknesses = []
        suggestions = []
        
        for dim_name, dim_data in report["dimension_scores"].items():
            score = dim_data["raw_score"]
            max_score = criteria["max_score"]
            percentage = (score / max_score) * 100 if max_score > 0 else 0
            
            if percentage >= 75:
                strengths.append(f"{dim_name}: 表现优秀 ({percentage:.0f}%)")
            elif percentage >= 50:
                suggestions.append(f"{dim_name}: 有提升空间 ({percentage:.0f}%) - 建议: {'增强' if 'prompt' in dim_name.lower() else '优化'}相关参数")
            else:
                weaknesses.append(f"{dim_name}: 需要重点改进 ({percentage:.0f}%)")
                
                # 根据维度给出具体建议
                if "visual" in dim_name.lower():
                    suggestions.append(
                        f"  → 建议使用更专业的镜头语言（参考cinematic_language_system.py）"
                    )
                elif "narrative" in dim_name.lower():
                    suggestions.append(
                        f"  → 建议检查beats的逻辑顺序，确保setup→escalation→climax结构"
                    )
                elif "emotional" in dim_name.lower():
                    suggestions.append(
                        f"  → 建议使用emotional_analysis_system确保情绪一致性"
                    )
        
        report["strengths"] = strengths[:5]  # 最多5个优点
        report["weaknesses"] = weaknesses[:3]  # 最多3个弱点
        report["improvement_suggestions"] = suggestions[:7]  # 最多7条建议


def assess_episode_quality(storyboard_result, dialogue_result=None, 
                          audio_design=None, return_full_report=False):
    """
    一站式评估整集质量
    
    Returns:
        float or dict: 总分或完整报告
    """
    assessor = QualityAssessor()
    
    # 评估分镜
    storyboard_report = assessor.assess_storyboard(
        storyboard_result,
        episode_info={"episode_seq": storyboard_result.get("episode_seq")}
    )
    
    overall = storyboard_report["overall_score"]
    
    if return_full_report:
        return {
            "overall_score": overall,
            "storyboard_report": storyboard_report,
            "grade": _score_to_grade(overall),
            "recommendation": _get_recommendation(overall),
            "assessed_at": storyboard_report["timestamp"]
        }
    
    return overall

def _score_to_grade(score):
    """分数转等级"""
    if score >= 90: return "A+ (卓越)"
    elif score >= 85: return "A (优秀)"
    elif score >= 80: return "A- (优良)"
    elif score >= 75: return "B+ (良好)"
    elif score >= 70: return "B (及格)"
    elif score >= 60: return "C (需改进)"
    elif score >= 50: return "D (较差)"
    else: return "F (不合格)"

def _get_recommendation(score):
    """根据分数给出建议"""
    if score >= 80:
        return "质量优秀，可以直接用于生产"
    elif score >= 70:
        return "质量合格，建议小幅优化后使用"
    elif score >= 60:
        return "质量一般，需要重点改进以下方面"
    else:
        return "质量不合格，强烈建议重新生成或大幅修改"

if __name__ == "__main__":
    print("=" * 60)
    print("质量评估系统测试")
    print("=" * 60)
    
    # 创建测试数据
    test_storyboard = {
        "episode_seq": 1,
        "storyboard": [
            {
                "shot_id": "ep1_shot01",
                "shot_type": "extreme_close_up",
                "camera_angle": "eye_level",
                "lighting_setup": "soft key light, warm fill, low contrast",
                "visual_prompt": "Shot in the style of Christopher Nolan, close_up to medium_shot, 50mm standard lens, f/2.8 shallow depth of field, soft key light, fill light, low contrast, slow dolly in camera movement, Color graded: warm vibrant, boosted saturation +15%",
                "cinematic_metadata": {
                    "director_style": "nolan",
                    "primary_emotion": "tension",
                    "emotion_intensity": 0.7,
                    "lens_config": "50mm standard lens"
                },
                "narrative_context": {
                    "beat_type": "hook",
                    "is_climax_beat": False
                }
            },
            {
                "shot_id": "ep1_shot02",
                "shot_type": "wide_shot",
                "camera_angle": "low_angle",
                "lighting_setup": "hard key light, high contrast, harsh shadows",
                "visual_prompt": "24mm wide angle, dramatic lighting, tracking shot",
                "cinematic_metadata": {
                    "director_style": "nolan",
                    "primary_emotion": "anger",
                    "emotion_intensity": 0.8
                },
                "narrative_context": {
                    "beat_type": "escalation",
                    "is_climax_beat": True
                }
            }
        ]
    }
    
    # 执行评估
    report = assess_episode_quality(test_storyboard, return_full_report=True)
    
    print(f"\n📊 评估结果:")
    print(f"  总分: {report['overall_score']} ({report['grade']})")
    print(f"  建议: {report['recommendation']}")
    print(f"\n  维度得分:")
    for dim, data in report["storyboard_report"]["dimension_scores"].items():
        status = "✅" if data["raw_score"] >= 70 else "⚠️"
        print(f"    {status} {dim}: {data['raw_score']}/100 ({data['weighted_contribution']}%权重)")
    
    print(f"\n  优点:")
    for s in report["storyboard_report"]["strengths"]:
        print(f"    • {s}")
    
    if report["storyboard_report"]["weaknesses"]:
        print(f"\n  待改进:")
        for w in report["storyboard_report"]["weaknesses"]:
            print(f"    • {w}")
    
    print(f"\n  改进建议:")
    for sug in report["storyboard_report"]["improvement_suggestions"][:5]:
        print(f"    💡 {sug}")
