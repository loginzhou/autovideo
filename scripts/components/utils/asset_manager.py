# -*- coding: utf-8 -*-
"""
Intelligent Asset Management System V1.0 (智能资产库管理系统)
基于剧情内容智能推荐和管理视频生产资产
支持角色、场景、道具的智能匹配和版本控制
"""

import json
import os
import hashlib
from datetime import datetime
from config_center import config

# ==================== 资产类型定义 ====================
ASSET_TYPES = {
    "character": {
        "description": "角色资产（外观、服装、表情等）",
        "required_fields": [
            "name",           # 角色名称
            "identity",       # 身份/职业
            "visual_traits",   # 外观特征列表
            "personality",     # 性格描述
            "voice_type",      # 声音类型
            "default_emotion", # 默认情绪状态
            "age_range",       # 年龄范围
            "gender"          # 性别
        ],
        "optional_fields": [
            "catchphrase",     # 口头禅
            "special_abilities", # 特殊能力
            "relationships",    # 人物关系
            "character_arc",   # 角色成长弧线
            "visual_references", # 参考图片路径
            "face_id",         # AI人脸ID（用于一致性）
            "style_tags",      # 风格标签（古风/现代等）
            "appearance_variants", # 外观变体（不同场景）
            "emotion_ranges"   # 情绪表现范围
        ],
        "validation_rules": {
            "name": {"type": str, "min_length": 1, "max_length": 50},
            "visual_traits": {"type": list, "min_items": 1},
            "personality": {"type": str, "min_length": 10}
        }
    },
    
    "location": {
        "description": "场景资产（地点、环境、氛围）",
        "required_fields": [
            "name",           # 场景名称
            "type",            # 场景类型 (indoor/outdoor/fantasy)
            "environment",     # 环境描述
            "time_of_day",     # 默认时间
            "weather",         # 天气条件
            "atmosphere",      # 氛围基调
            "lighting_setup",  # 光照方案
            "color_palette"    # 主色调
        ],
        "optional_fields": [
            "associated_characters", # 常出现的人物
            "sound_profile",      # 声音特征
            "special_properties",  # 特殊属性（魔法等）
            "transition_hints",    # 转场提示
            "reference_images",     # 参考图片
            "variations_by_time",  # 不同时间的变化
            "mood_modifiers"       # 情绪修饰符
        ]
    },
    
    "prop": {
        "description": "道具资产（物品、武器、工具）",
        "required_fields": [
            "name",           # 道具名称
            "category",       # 类别 (weapon/tool/decoration/symbolic)
            "description",    # 描述
            "visual_style",   # 视觉风格
            "size",           # 大小
            "material"        # 材质
        ],
        "optional_fields": [
            "associated_character", # 所属角色
            "magical_properties",   # 魔法属性
            "usage_contexts",       # 使用场景
            "sound_cues",           # 音效提示
            "interaction_verbs",    # 交互动词
            "emotional_significance" # 情感意义
        ]
    },
    
    "style_template": {
        "description": "风格模板（视觉风格、色调、整体美学）",
        "required_fields": [
            "name",               # 模板名称
            "genre",              # 适用类型
            "visual_description", # 视觉描述
            "color_grading",      # 色彩分级
            "lighting_style",     # 灯光风格
            "camera_language",    # 镜头语言
            "audio_style"         # 音频风格
        ],
        "optional_fields": [
            "director_inspiration", # 导演灵感来源
            "reference_works",      # 参考作品
            "technical_specs",      # 技术规格
            "mood_board_tags",      # 情绪板标签
            "applicable_scenes"     # 适用场景
        ]
    }
}

# ==================== 智能推荐引擎 ====================
class AssetRecommendationEngine:
    """
    基于剧情内容智能推荐资产
    """
    
    def __init__(self):
        self.asset_database = {}
        self.load_assets()
        
        # 情境-资产关联规则
        self.context_rules = {
            "combat_situation": {
                "required_props": ["weapon", "armor", "shield"],
                "likely_locations": ["battlefield", "arena", "training_ground"],
                "character_states": ["determined", "aggressive", "focused"]
            },
            "romantic_moment": {
                "required_props": ["flower", "gift", "letter"],
                "likely_locations": ["garden", "rooftop", "beach", "cafe"],
                "character_states": ["nervous", "happy", "tender"]
            },
            "mystery_investigation": {
                "required_props": ["magnifying_glass", "notebook", "lantern"],
                "likely_locations": ["library", "old_mansion", "archive_room"],
                "character_states": ["curious", "cautious", "analytical"]
            },
            "celebration_festival": {
                "required_props": ["banner", "instrument", "food", "decoration"],
                "likely_locations": ["town_square", "palace_hall", "festival_grounds"],
                "character_states": ["joyful", "excited", "proud"]
            }
        }
        
        # 角色-场景兼容性矩阵
        self.character_location_compatibility = {
            ("royalty", "throne_room"): 0.95,
            ("royalty", "garden"): 0.8,
            ("merchant", "marketplace"): 0.9,
            ("merchant", "office"): 0.7,
            ("warrior", "battlefield"): 0.95,
            ("warrior", "training_ground"): 0.9,
            ("scholar", "library"): 0.95,
            ("scholar", "study_room"): 0.9,
            ("commoner", "village"): 0.85,
            ("commoner", "tavern"): 0.9
        }
    
    def load_assets(self):
        """加载所有资产数据"""
        asset_dir = os.path.join("output", "assets")
        
        for asset_type in ASSET_TYPES:
            type_dir = os.path.join(asset_dir, f"{asset_type}s")
            if os.path.exists(type_dir):
                self.asset_database[asset_type] = {}
                
                for file in os.listdir(type_dir):
                    if file.endswith('.json'):
                        with open(os.path.join(type_dir, file), 'r', encoding='utf-8') as f:
                            asset_data = json.load(f)
                        asset_id = asset_data.get('id', file.replace('.json', ''))
                        self.asset_database[asset_type][asset_id] = asset_data
    
    def recommend_characters(self, scene_content, emotion="neutral", existing_chars=None):
        """
        推荐适合当前场景的角色
        
        Args:
            scene_content: 场景内容文本
            emotion: 当前情绪
            existing_chars: 已经在场的角色ID列表
            
        Returns:
            list: 推荐的角色列表，包含匹配分数
        """
        recommendations = []
        existing_chars = existing_chars or []
        
        characters = self.asset_database.get("character", {})
        
        for char_id, char_data in characters.items():
            if char_id in existing_chars:
                continue
            
            score = 0.0
            reasons = []
            
            # 1. 检查角色性格是否与情绪匹配
            char_personality = char_data.get('personality', '').lower()
            emotion_keywords = {
                "joy": ["happy", "cheerful", "optimistic", "lively"],
                "sadness": ["melancholy", "quiet", "reflective", "gentle"],
                "anger": ["intense", "passionate", "strong-willed", "bold"],
                "fear": ["cautious", "careful", "anxious", "nervous"],
                "love": ["caring", "warm", "affectionate", "tender"]
            }
            
            if emotion in emotion_keywords:
                for kw in emotion_keywords[emotion]:
                    if kw in char_personality:
                        score += 0.3
                        reasons.append(f"性格匹配{emotion}情绪")
            
            # 2. 检查角色是否与场景内容相关
            char_name = char_data.get('name', '')
            char_identity = char_data.get('identity', '').lower()
            traits = [t.lower() for t in char_data.get('visual_traits', [])]
            
            all_text = f"{char_name} {char_identity} {' '.join(traits)}".lower()
            scene_lower = scene_content.lower()
            
            # 简单的关键词重叠检测
            shared_words = set(all_text.split()) & set(scene_lower.split())
            if shared_words:
                overlap_score = min(len(shared_words) * 0.1, 0.5)
                score += overlap_score
                reasons.append(f"内容相关度: {len(shared_words)}个共同词")
            
            # 3. 检查特殊能力是否适用于场景
            abilities = char_data.get('special_abilities', [])
            if isinstance(abilities, list):
                for ability in abilities:
                    if any(kw in scene_lower for kw in ability.lower().split()):
                        score += 0.2
                        reasons.append(f"能力'{ability}'可用于此场景")
            
            # 4. 角色关系检查（如果已有角色在场）
            relationships = char_data.get('relationships', {})
            if existing_chars and relationships:
                for existing_char_id in existing_chars:
                    if existing_char_id in relationships:
                        rel_type = relationships[existing_char_id]
                        if rel_type in ['ally', 'friend', 'lover', 'family']:
                            score += 0.15
                            reasons.append(f"与现有角色有{rel_type}关系")
            
            if score > 0.1:  # 只返回有意义的推荐
                recommendations.append({
                    "id": char_id,
                    "data": char_data,
                    "score": round(score, 3),
                    "reasons": reasons
                })
        
        # 按分数排序
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:5]  # 返回前5个推荐
    
    def recommend_location(self, characters_present, emotion="neutral", time_of_day="day"):
        """
        推荐适合的角色组合和情绪的场景
        
        Returns:
            list: 推荐的场景列表
        """
        recommendations = []
        
        locations = self.asset_database.get("location", {})
        
        for loc_id, loc_data in locations.items():
            score = 0.0
            reasons = []
            
            # 1. 角色兼容性评分
            compatibility_total = 0
            count = 0
            for char_data in characters_present:
                char_identity = char_data.get('identity', 'commoner').lower()
                loc_name = loc_data.get('name', '').lower().replace(' ', '_')
                
                key = (char_identity, loc_name)
                compat = self.character_location_compatibility.get(key, 0.5)
                compatibility_total += compat
                count += 1
            
            if count > 0:
                avg_compat = compatibility_total / count
                score += avg_compat * 0.4
                if avg_compat > 0.7:
                    reasons.append(f"高角色兼容性 ({avg_compat:.2f})")
            
            # 2. 情绪匹配
            loc_atmosphere = loc_data.get('atmosphere', '').lower()
            emotion_atmosphere_map = {
                "joy": ["bright", "cheerful", "warm", "lively", "festive"],
                "sadness": ["somber", "melancholy", "quiet", "peaceful", "serene"],
                "anger": ["tense", "harsh", "stormy", "chaotic", "hostile"],
                "fear": ["dark", "eerie", "mysterious", "ominous", "unsettling"],
                "love": ["romantic", "intimate", "beautiful", "peaceful", "soft"]
            }
            
            if emotion in emotion_atmosphere_map:
                for atm_kw in emotion_atmosphere_map[emotion]:
                    if atm_kw in loc_atmosphere:
                        score += 0.25
                        reasons.append(f"氛围匹配{emotion}")
                        break
            
            # 3. 时间匹配
            loc_time = loc_data.get('time_of_day', 'any')
            if loc_time == time_of_day or loc_time == 'any':
                score += 0.15
                reasons.append(f"时间适用")
            elif self._time_compatible(loc_time, time_of_day):
                score += 0.05
            
            if score > 0.2:
                recommendations.append({
                    "id": loc_id,
                    "data": loc_data,
                    "score": round(score, 3),
                    "reasons": reasons
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]
    
    def _time_compatible(self, loc_time, target_time):
        """检查时间兼容性"""
        compatible_pairs = [
            ('morning', 'dawn'), ('morning', 'day'),
            ('afternoon', 'day'), ('evening', 'dusk'), ('evening', 'night'),
            ('night', 'midnight'), ('day', 'golden_hour')
        ]
        return (loc_time, target_time) in compatible_pairs or (target_time, loc_time) in compatible_pairs
    
    def recommend_props(self, context_type, scene_content, character=None):
        """
        根据情境类型推荐道具
        """
        recommendations = []
        
        props = self.asset_database.get("prop", {})
        context_config = self.context_rules.get(context_type, {})
        required_categories = context_config.get("required_props", [])
        
        for prop_id, prop_data in props.items():
            score = 0.0
            reasons = []
            
            # 1. 检查是否属于需要的类别
            prop_category = prop_data.get('category', '')
            if prop_category in required_categories:
                score += 0.4
                reasons.append(f"类别匹配: {prop_category}")
            
            # 2. 内容相关性
            prop_desc = prop_data.get('description', '').lower()
            prop_name = prop_data.get('name', '').lower()
            scene_lower = scene_content.lower()
            
            if prop_name in scene_lower or any(word in scene_lower for word in prop_desc.split()):
                score += 0.3
                reasons.append("内容提及")
            
            # 3. 角色关联
            if character:
                associated = prop_data.get('associated_character', '')
                char_name = character.get('name', '')
                if associated == char_name or char_name in associated:
                    score += 0.3
                    reasons.append(f"专属道具")
            
            if score > 0.15:
                recommendations.append({
                    "id": prop_id,
                    "data": prop_data,
                    "score": round(score, 3),
                    "reasons": reasons
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:5]

# ==================== 资产版本管理 ====================
class AssetVersionManager:
    """
    资产版本控制和管理
    """
    
    def __init__(self):
        self.version_history = {}
        self.load_version_history()
    
    def load_version_history(self):
        """加载版本历史"""
        history_path = os.path.join("output", "assets", ".version_history.json")
        if os.path.exists(history_path):
            with open(history_path, 'r', encoding='utf-8') as f:
                self.version_history = json.load(f)
    
    def save_version_history(self):
        """保存版本历史"""
        history_path = os.path.join("output", "assets", ".version_history.json")
        os.makedirs(os.path.dirname(history_path), exist_ok=True)
        with open(history_path, 'w', encoding='utf-8') as f:
            json.dump(self.version_history, f, ensure_ascii=False, indent=2)
    
    def create_new_version(self, asset_type, asset_id, asset_data, change_description=""):
        """
        创建新版本的资产
        
        Returns:
            dict: 新版本信息
        """
        version_key = f"{asset_type}:{asset_id}"
        
        if version_key not in self.version_history:
            self.version_history[version_key] = {
                "current_version": 0,
                "versions": []
            }
        
        current_ver = self.version_history[version_key]["current_version"] + 1
        new_version = {
            "version_number": current_ver,
            "timestamp": datetime.now().isoformat(),
            "change_description": change_description,
            "data_hash": hashlib.md5(json.dumps(asset_data, sort_keys=True).encode()).hexdigest()[:12],
            "asset_data": asset_data
        }
        
        self.version_history[version_key]["versions"].append(new_version)
        self.version_history[version_key]["current_version"] = current_ver
        
        # 保存到文件
        version_dir = os.path.join("output", "assets", f"{asset_type}s", asset_id)
        os.makedirs(version_dir, exist_ok=True)
        
        version_file = os.path.join(version_dir, f"v{current_ver:03d}.json")
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(asset_data, f, ensure_ascii=False, indent=2)
        
        # 更新latest符号链接（或复制文件）
        latest_file = os.path.join(version_dir, "latest.json")
        with open(latest_file, 'w', encoding='utf-8') as f:
            json.dump(asset_data, f, ensure_ascii=False, indent=2)
        
        self.save_version_history()
        
        print(f"[Asset Manager] 创建新版本: {asset_type}/{asset_id} v{current_ver:03d}")
        
        return new_version
    
    def get_version(self, asset_type, asset_id, version_number=None):
        """
        获取指定版本的资产
        
        Args:
            version_number: 版本号，None表示最新版
        """
        version_key = f"{asset_type}:{asset_id}"
        
        if version_key not in self.version_history:
            return None
        
        if version_number is None:
            version_number = self.version_history[version_key]["current_version"]
        
        for ver in self.version_history[version_key]["versions"]:
            if ver["version_number"] == version_number:
                return ver["asset_data"]
        
        return None
    
    def rollback_to_version(self, asset_type, asset_id, target_version):
        """
        回滚到指定版本
        """
        version_key = f"{asset_type}:{asset_id}"
        
        if version_key not in self.version_history:
            return False, "资产不存在"
        
        current = self.version_history[version_key]["current_version"]
        if target_version >= current:
            return False, f"目标版本 v{target_version:03d} 不早于当前版本 v{current:03d}"
        
        target_data = self.get_version(asset_type, asset_id, target_version)
        if not target_data:
            return False, f"版本 v{target_version:03d} 数据不存在"
        
        # 创建回滚记录的新版本
        self.create_new_version(
            asset_type, asset_id, target_data,
            change_description=f"ROLLBACK from v{current:03d} to v{target_version:03d}"
        )
        
        return True, f"成功回滚到 v{target_version:03d}"
    
    def compare_versions(self, asset_type, asset_id, ver1, ver2):
        """
        比较两个版本的差异
        """
        data1 = self.get_version(asset_type, asset_id, ver1)
        data2 = self.get_version(asset_type, asset_id, ver2)
        
        if not data1 or not data2:
            return None
        
        diff = {}
        all_keys = set(data1.keys()) | set(data2.keys())
        
        for key in all_keys:
            val1 = data1.get(key)
            val2 = data2.get(key)
            
            if val1 != val2:
                diff[key] = {
                    "v1": val1,
                    "v2": val2,
                    "changed": True
                }
        
        return diff

# ==================== 全局实例 ====================
recommendation_engine = AssetRecommendationEngine()
version_manager = AssetVersionManager()

def get_smart_recommendations(scene_content, emotion="neutral", 
                              characters_present=None, context_type=None):
    """
    一站式获取智能推荐
    
    Returns:
        dict: 包含角色、场景、道具推荐的完整字典
    """
    result = {
        "characters": [],
        "locations": [],
        "props": [],
        "timestamp": datetime.now().isoformat()
    }
    
    # 推荐角色
    existing_char_ids = [c.get('id') for c in (characters_present or [])]
    result["characters"] = recommendation_engine.recommend_characters(
        scene_content, emotion, existing_char_ids
    )
    
    # 推荐场景
    result["locations"] = recommendation_engine.recommend_location(
        characters_present or [], emotion
    )
    
    # 推荐道具
    if context_type:
        main_char = characters_present[0] if characters_present else None
        result["props"] = recommendation_engine.recommend_props(
            context_type, scene_content, main_char
        )
    
    return result

if __name__ == "__main__":
    print("=" * 60)
    print("智能资产库管理系统测试")
    print("=" * 60)
    
    # 测试推荐引擎
    test_scene = "The warrior princess stood on the castle balcony, gazing at the enemy army approaching. Her hand gripped the hilt of her ancestral sword, heart pounding with determination."
    
    recs = get_smart_recommendations(
        scene_content=test_scene,
        emotion="determination",
        characters_present=[{"name": "Princess Aria", "identity": "royalty", "personality": "brave and determined"}],
        context_type="combat_situation"
    )
    
    print("\n📋 智能推荐结果:")
    print(f"\n👥 推荐角色 ({len(recs['characters'])}):")
    for char in recs['characters'][:3]:
        print(f"  • {char['data']['name']} ({char['data']['identity']}) - 分数: {char['score']} | {', '.join(char['reasons'][:2])}")
    
    print(f"\n🏰 推荐场景 ({len(recs['locations'])}):")
    for loc in recs['locations'][:3]:
        print(f"  • {loc['data']['name']} - 分数: {loc['score']} | {', '.join(loc['reasons'][:2])}")
    
    print(f"\n🎒 推荐道具 ({len(recs['props'])}):")
    for prop in recs['props'][:3]:
        print(f"  • {prop['data']['name']} ({prop['data']['category']}) - 分数: {prop['score']}")
