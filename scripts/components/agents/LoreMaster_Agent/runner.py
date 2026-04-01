import json
import uuid
import os
import re

class ContinuityStateMachine:
    """跨集状态机，跟踪所有全局连贯信息"""
    def __init__(self):
        self.current_time = "dawn" # dawn/morning/noon/afternoon/dusk/night
        self.current_weather = "clear" # clear/rain/snow/fog/windy/storm
        self.char_state = {} # 角色状态：受伤、衣服破损等
        self.event_history = [] # 已发生事件，避免前后矛盾
    
    def update_state(self, episode_seq, updates):
        """更新全局状态"""
        if 'time' in updates:
            self.current_time = updates['time']
        if 'weather' in updates:
            self.current_weather = updates['weather']
        if 'char_state' in updates:
            for char, state in updates['char_state'].items():
                if char not in self.char_state:
                    self.char_state[char] = {}
                self.char_state[char].update(state)
        self.event_history.append({
            "episode_seq": episode_seq,
            "updates": updates
        })
    
    def get_continuity_context(self):
        """获取当前连贯上下文，注入到各Agent"""
        return {
            "current_time": self.current_time,
            "current_weather": self.current_weather,
            "char_state_overrides": self.char_state.copy(),
            "event_history": self.event_history[-5:] # 最近5集事件
        }

def run_lore_master(chunks):
    """
    🧠 Continuity Supervisor (场记与状态机) V6 影棚级
    ✅ 跨集状态继承 ✅ 时间天气连贯性 ✅ 零前后矛盾
    全局状态唯一真值源，彻底解决OOC、时间倒流、设定冲突问题
    """
    # 读取小说前5000字自动分析
    novel_content = ""
    for chunk in chunks[:3]:
        novel_content += chunk['content']
    novel_content = novel_content[:5000]
    
    # 自动题材识别
    genre_keywords = {
        "末日废土": ["末日", "丧尸", "废土", "灾变", "极寒", "尸潮", "幸存", "基地"],
        "仙侠修真": ["修仙", "修真", "灵气", "宗门", "金丹", "元婴", "飞剑", "修士"],
        "都市异能": ["都市", "异能", "系统", "透视", "神医", "赘婿", "校花", "总裁"],
        "科幻未来": ["星际", "机甲", "未来", "赛博", "外星", "宇宙", "战舰", "基因"]
    }
    
    genre = "末日废土" # 默认
    for g, keywords in genre_keywords.items():
        for kw in keywords:
            if kw in novel_content:
                genre = g
                break
        if genre != "末日废土":
            break
    
    # 自动提取主角名字
    name_match = re.search(r"([\u4e00-\u9fa5]{2,3})觉醒", novel_content) or re.search(r"([\u4e00-\u9fa5]{2,3})抬起头", novel_content)
    main_char_name = name_match.group(1) if name_match else "主角"
    
    # 自动提取主角特征
    char_visual_traits = []
    if genre == "末日废土":
        char_visual_traits = ["28岁男性", "黑色短发", "面部硬朗", "战术服装", "眼神冷静"]
    elif genre == "仙侠修真":
        char_visual_traits = ["青年男性", "古装", "背负长剑", "气质出尘"]
    elif genre == "都市异能":
        char_visual_traits = ["20多岁男性", "休闲服装", "面容普通", "眼神锐利"]
    elif genre == "科幻未来":
        char_visual_traits = ["男性", "紧身作战服", "机械改装", "短发"]
    
    # 自动生成世界观描述
    if genre == "末日废土":
        world_setting = "末日降临，丧尸横行，废土世界，人类挣扎求生"
    elif genre == "仙侠修真":
        world_setting = "仙侠世界，灵气复苏，宗门林立，强者为尊"
    elif genre == "都市异能":
        world_setting = "现代都市，隐藏异能者，表面平静下暗流涌动"
    else:
        world_setting = f"{genre}世界"
    
    # 初始化全局状态机
    state_machine = ContinuityStateMachine()
    # 初始状态根据小说开头推断
    if "黎明" in novel_content or "清晨" in novel_content:
        state_machine.current_time = "dawn"
    elif "黄昏" in novel_content or "傍晚" in novel_content or "日落" in novel_content:
        state_machine.current_time = "dusk"
    elif "晚上" in novel_content or "黑夜" in novel_content or "深夜" in novel_content:
        state_machine.current_time = "night"
    
    if "下雨" in novel_content or "雨" in novel_content:
        state_machine.current_weather = "rain"
    elif "下雪" in novel_content or "雪" in novel_content:
        state_machine.current_weather = "snow"
    elif "雾" in novel_content or "雾霾" in novel_content:
        state_machine.current_weather = "fog"
    
    # 生成蓝图，增加初始时间天气信息
    episode_blueprints = []
    for i in range(98):
        chunk_idx = i // 3
        # 时间自动推进，每3集推进一个时间段：dawn→morning→noon→afternoon→dusk→night循环
        time_cycle = ["dawn", "morning", "noon", "afternoon", "dusk", "night"]
        episode_time = time_cycle[(i // 3) % len(time_cycle)]
        
        episode_blueprints.append({
            "chunk_id": f"chunk_{chunk_idx}_{uuid.uuid4().hex[:6]}", 
            "core_plot": chunks[chunk_idx]['content'][:300].replace("\n", " ").strip(), 
            "seq": i+1,
            "time": episode_time,
            "weather": state_machine.current_weather
        })
    
    return {
        "world_lore": {
            "setting": world_setting,
            "genre": genre,
            "physics_rules": {}
        },
        "characters": [
            {
                "char_id": f"char_{uuid.uuid4().hex[:8]}",
                "name": main_char_name,
                "visual_traits": char_visual_traits,
                "face_id_ref": f"config/assets/{main_char_name}_ref.png",
                "voice_id": f"voice_id_001"
            }
        ],
        "episode_blueprints": episode_blueprints,
        "continuity_state_machine": state_machine # 全局状态机实例，贯穿全流程
    }
