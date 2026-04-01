import json
import os
# 临时注释PIL依赖，测试流程用
# from PIL import Image, ImageDraw, ImageFont

class CharacterConsistencyManager:
    """
    角色一致性管理模块 V1.0
    全局统一管理所有角色的人设、视觉特征、声音ID，跨集生成自动校验，避免人设崩坏
    """
    def __init__(self, full_analysis_result):
        self.characters = full_analysis_result['characters']
        self.char_map = {char['name']: char for char in self.characters}
        self.face_id_map = {}
        self.voice_id_map = {}
        self._init_ids()
        self._generate_character_reference_sheet()
    
    def _init_ids(self):
        """为每个角色分配唯一的face_id和voice_id"""
        for idx, char in enumerate(self.characters):
            char_name = char['name']
            self.face_id_map[char_name] = f"face_id_{idx+1:03d}_{char_name}"
            self.voice_id_map[char_name] = f"voice_id_{idx+1:03d}_{char.get('voice_type', '中性').replace(' ', '_')}"
            char['face_id'] = self.face_id_map[char_name]
            char['voice_id'] = self.voice_id_map[char_name]
        
        # 保存ID映射表
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
            ref_sheet += f"- 身份：{char['identity']}\n"
            ref_sheet += f"- 性格：{char['personality']}\n"
            ref_sheet += f"- 外貌特征：{'，'.join(char['visual_traits'])}\n"
            ref_sheet += f"- 声音类型：{char['voice_type']}\n"
            ref_sheet += f"- Face ID：{char['face_id']}\n"
            ref_sheet += f"- Voice ID：{char['voice_id']}\n"
            ref_sheet += f"- 重要程度：{char['importance']}\n\n"
        
        os.makedirs("output/assets", exist_ok=True)
        with open("output/assets/character_reference_sheet.md", 'w', encoding='utf-8-sig') as f:
            f.write(ref_sheet)
        
        # 生成可视化参考图（简单版，后续可对接AI绘图自动生成定妆照）
        # try:
        #     img = Image.new('RGB', (1200, 300 * len(self.characters)), color='white')
        #     draw = ImageDraw.Draw(img)
        #     font = ImageFont.truetype("msyh.ttc", 24)
            
        #     y_offset = 50
        #     for char in self.characters:
        #         draw.text((50, y_offset), f"{char['name']}（{char['identity']}）", font=font, fill='black')
        #         y_offset += 40
        #         draw.text((80, y_offset), f"外貌：{'，'.join(char['visual_traits'])}", font=font, fill='gray')
        #         y_offset += 40
        #         draw.text((80, y_offset), f"声音：{char['voice_type']}", font=font, fill='gray')
        #         y_offset += 80
            
        #     img.save("output/assets/character_reference_sheet.png")
        # except Exception as e:
        #     print(f"⚠️  生成可视化参考图失败：{str(e)}，跳过")
    
    def get_character_info(self, character_name):
        """获取角色完整信息，不存在返回默认主角信息"""
        return self.char_map.get(character_name, self.char_map[list(self.char_map.keys())[0]])
    
    def validate_character_consistency(self, episode_content):
        """校验单集内容中的角色是否符合人设，返回修正后的内容"""
        # 校验逻辑：检查角色说话风格、行为是否符合设定，不符合则自动修正
        for char_name in self.char_map:
            char = self.char_map[char_name]
            # 简单校验：如果出现和性格相反的描述，自动替换
            if "活泼开朗" in char['personality'] and f"{char_name}沉默寡言" in episode_content:
                episode_content = episode_content.replace(f"{char_name}沉默寡言", f"{char_name}开朗地笑着说")
            if "冷酷沉稳" in char['personality'] and f"{char_name}嬉皮笑脸" in episode_content:
                episode_content = episode_content.replace(f"{char_name}嬉皮笑脸", f"{char_name}面无表情地说")
        
        return episode_content
    
    def inject_character_params(self, prompt, character_names):
        """向提示词中注入角色统一参数，保证生成一致性"""
        char_params = []
        for name in character_names:
            char = self.get_character_info(name)
            char_params.append(f"{name}，{'，'.join(char['visual_traits'])}")
        
        return prompt.replace("{{characters}}", "，".join(char_params))\
                     .replace("{{face_id}}", self.face_id_map.get(character_names[0], ""))\
                     .replace("{{voice_id}}", self.voice_id_map.get(character_names[0], ""))

print("角色一致性管理模块加载完成")
