import json
import os
from config_center import config

class CharacterConsistencyManager:
    """
    角色一致性管理模块 V2.0
    全局统一管理所有角色的人设、视觉特征、声音ID，跨集生成自动校验，避免人设崩坏
    支持自定义人设导入、自动校验修正、参数自动注入
    """
    def __init__(self, full_analysis_result):
        self.characters = full_analysis_result['characters']
        self.char_map = {char['name']: char for char in self.characters}
        self.face_id_map = {}
        self.voice_id_map = {}
        self.custom_character_path = config.get("character_manager.custom_character_path", "config/custom_characters.json")
        
        # 加载自定义人设，覆盖AI分析结果
        self._load_custom_characters()
        self._init_ids()
        self._generate_character_reference_sheet()
        
        # 人工审核角色设定
        from components.utils.human_review_manager import human_review
        if human_review.request_review("character_settings", self.characters):
            print("角色设定审核通过")
        else:
            raise Exception("角色设定审核被驳回，终止执行")
    
    def _load_custom_characters(self):
        """加载自定义人设，覆盖AI自动分析的结果"""
        if os.path.exists(self.custom_character_path):
            try:
                with open(self.custom_character_path, 'r', encoding='utf-8') as f:
                    custom_chars = json.load(f)
                for custom_char in custom_chars:
                    char_name = custom_char['name']
                    if char_name in self.char_map:
                        # 合并自定义字段到现有角色
                        self.char_map[char_name].update(custom_char)
                        print(f"加载自定义人设：{char_name}")
                    else:
                        # 新增自定义角色
                        self.char_map[char_name] = custom_char
                        self.characters.append(custom_char)
                        print(f"新增自定义角色：{char_name}")
            except Exception as e:
                print(f"加载自定义人设失败：{str(e)}，使用AI分析结果")
    
    def _init_ids(self):
        """为每个角色分配唯一的face_id和voice_id"""
        for idx, char in enumerate(self.characters):
            char_name = char['name']
            self.face_id_map[char_name] = f"face_id_{idx+1:03d}_{char_name}"
            self.voice_id_map[char_name] = f"voice_id_{idx+1:03d}_{char.get('voice_type', '中性').replace(' ', '_')}"
            char['face_id'] = self.face_id_map[char_name]
            char['voice_id'] = self.voice_id_map[char_name]
        
        # 保存ID映射表
        os.makedirs("output/analysis", exist_ok=True)
        with open("output/analysis/character_id_map.json", 'w', encoding='utf-8-sig') as f:
            json.dump({
                "face_id_map": self.face_id_map,
                "voice_id_map": self.voice_id_map,
                "characters": self.characters
            }, f, ensure_ascii=False, indent=2)
    
    def _generate_character_reference_sheet(self):
        """生成角色定妆参考表，方便AI生成时保持一致性"""
        ref_sheet = "# 角色定妆参考表\n\n"
        for char in self.characters:
            ref_sheet += f"## {char['name']}\n"
            ref_sheet += f"- 身份：{char.get('identity', '未知')}\n"
            ref_sheet += f"- 性格：{char.get('personality', '未知')}\n"
            ref_sheet += f"- 外貌特征：{'，'.join(char.get('visual_traits', []))}\n"
            ref_sheet += f"- 声音类型：{char.get('voice_type', '中性')}\n"
            ref_sheet += f"- Face ID：{char.get('face_id', '')}\n"
            ref_sheet += f"- Voice ID：{char.get('voice_id', '')}\n"
            ref_sheet += f"- 重要程度：{char.get('importance', '次要')}\n\n"
        
        os.makedirs("output/assets", exist_ok=True)
        with open("output/assets/character_reference_sheet.md", 'w', encoding='utf-8-sig') as f:
            f.write(ref_sheet)
    
    def get_character_info(self, character_name):
        """获取角色完整信息，不存在返回默认主角信息"""
        if character_name in self.char_map:
            return self.char_map[character_name]
        # 没有匹配到返回第一个核心角色
        for char in self.characters:
            if char.get('importance', '') == '核心':
                return char
        return self.characters[0] if self.characters else {}
    
    def validate_character_consistency(self, episode_content):
        """校验单集内容中的角色是否符合人设，返回修正后的内容"""
        if not config.get("character_manager.enable_validation", True):
            return episode_content
            
        # 校验逻辑：检查角色说话风格、行为是否符合设定，不符合则自动修正
        for char_name in self.char_map:
            char = self.char_map[char_name]
            personality = char.get('personality', '').lower()
            if not personality:
                continue
                
            # 基于性格的自动修正规则
            if "活泼" in personality or "开朗" in personality:
                replace_map = {
                    f"{char_name}沉默寡言": f"{char_name}开朗地笑着说",
                    f"{char_name}面无表情": f"{char_name}笑容满面",
                    f"{char_name}冷淡": f"{char_name}热情"
                }
                for old, new in replace_map.items():
                    if old in episode_content:
                        episode_content = episode_content.replace(old, new)
            
            if "冷酷" in personality or "沉稳" in personality or "冷漠" in personality:
                replace_map = {
                    f"{char_name}嬉皮笑脸": f"{char_name}面无表情地说",
                    f"{char_name}大笑": f"{char_name}嘴角微扬",
                    f"{char_name}热情": f"{char_name}冷淡"
                }
                for old, new in replace_map.items():
                    if old in episode_content:
                        episode_content = episode_content.replace(old, new)
            
            if "温柔" in personality or "善良" in personality:
                replace_map = {
                    f"{char_name}凶狠地说": f"{char_name}轻声说",
                    f"{char_name}怒骂": f"{char_name}无奈地说"
                }
                for old, new in replace_map.items():
                    if old in episode_content:
                        episode_content = episode_content.replace(old, new)
        
        return episode_content
    
    def inject_character_params(self, prompt, character_names):
        """向提示词中注入角色统一参数，保证生成一致性"""
        if not character_names:
            return prompt
            
        char_params = []
        for name in character_names:
            char = self.get_character_info(name)
            visual_traits = char.get('visual_traits', [])
            if visual_traits:
                char_params.append(f"{name}，{'，'.join(visual_traits)}")
        
        if char_params:
            prompt = prompt.replace("{{characters}}", "，".join(char_params))
        
        main_char = self.get_character_info(character_names[0])
        prompt = prompt.replace("{{face_id}}", main_char.get('face_id', ''))\
                     .replace("{{voice_id}}", main_char.get('voice_id', ''))
        
        return prompt
