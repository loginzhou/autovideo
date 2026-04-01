import re

class AudioVisualLogicEngine:
    """
    短剧工业化逻辑引擎：负责空间一致性校验与视听对齐
    """
    def __init__(self, main_char_name, main_char_traits):
        self.main_char = main_char_name
        self.traits = main_char_traits
        self.current_location = "rooftop/outdoor" # 默认初始位置

    def refine_pipeline(self, shot_data):
        """
        shot_data 包含: shot_id, dialogue, raw_image_prompt, speaker
        """
        dialogue = shot_data.get('dialogue', '')
        speaker = shot_data.get('speaker', '')
        raw_prompt = shot_data.get('raw_image_prompt', '')

        # 1. 空间锚定逻辑 (Spatial Anchoring) 
        # 检测对话中隐含的空间信息，自动修正 image_prompts 里的环境描述
        if any(kw in dialogue for kw in ["门", "闸", "室内", "屋", "关闸门"]):
            self.current_location = "safehouse interior, heavy steel gate in background"
        elif any(kw in dialogue for kw in ["直升机", "天", "云", "吸上来"]):
            self.current_location = "rooftop, post-apocalyptic city skyline"

        # 2. 角色焦点对齐 (Character Focus)
        # 如果说话的人不是主角，画面应切换至 NPC 或环境大全景，而非死盯着主角
        if speaker != self.main_char and speaker not in ["系统", "旁白"]:
            subject_focus = f"mysterious antagonist, {speaker}, cold expression"
        elif "吞噬成功" in dialogue or "系统" in dialogue or "机械源点" in dialogue:
            # 针对系统音的特殊视觉处理
            subject_focus = f"extreme close up of {self.main_char}'s face, glowing eyes, holographic UI 'Mechanical Points +1' overlay"
        else:
            subject_focus = f"{self.main_char}, {self.traits}"

        # 3. 噪声过滤 (Noise Filtering)
        # 剔除 (10:1.1) 等无效的解析残留
        clean_prompt = re.sub(r'\(\d+:\d+\.\d+\)', '', raw_prompt)

        # 4. 最终指令合成 (Final Prompt Assembly)
        optimized_prompt = (
            f"(Masterpiece:1.2), (ultra-detailed:1.2), vertical composition, "
            f"centered subject, {subject_focus}, {self.current_location}, cinematic lighting"
        )
        
        return optimized_prompt.strip()

    def get_specific_sfx(self, dialogue, shot_content):
        """音效具象化：根据画面和对话输出具体物理音效描述"""
        if any(word in dialogue + shot_content for word in ["关闸门", "关门", "金属门"]):
            return "heavy metal gate sliding clank, hydraulic seal hissing sound"
        elif any(word in dialogue + shot_content for word in ["系统", "吞噬成功", "升级", "机械源点"]):
            return "digital chime, holographic UI beep, faint electrical crackle"
        elif any(word in dialogue + shot_content for word in ["直升机", "螺旋桨", "飞"]):
            return "helicopter rotor whooshing, distant wind howling"
        elif any(word in dialogue + shot_content for word in ["坠毁", "爆炸", "碎裂"]):
            return "metal crushing explosion, debris scattering impact sounds"
        elif any(word in dialogue + shot_content for word in ["丧尸", "嘶吼", "怪物"]):
            return "zombie gurgling roar, distant human screaming"
        else:
            return "faint wind rustling, distant low ambient rumble"
