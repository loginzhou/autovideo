# -*- coding: utf-8 -*-
"""
Professional Screenplay Prompt Engineering System V1.0 (专业剧本提示词工程系统)
基于好莱坞编剧理论构建专业级Prompt模板
支持：三幕式/英雄之旅/救猫咪/丹·哈蒙故事原子等经典结构
集成：角色弧线设计、情绪曲线控制、视觉化节拍描述
"""

# ==================== 经典编剧理论模板 ====================

SCREENPLAY_THEORIES = {
    "three_act_structure": {
        "name": "三幕式结构 (Three-Act Structure)",
        "description": "最经典的戏剧结构，由亚里士多德提出，好莱坞广泛采用",
        "acts": [
            {
                "name": "第一幕 (Act I: Setup)",
                "percentage": 25,
                "key_moments": [
                    {"position": 0, "name": "开场场景 (Opening Image)", "description": "建立基调、展示主角现状"},
                    {"position": 5, "name": "激励事件 (Inciting Incident)", "description": "打破平衡，引发变化"},
                    {"position": 12, "name": "第一幕高潮 (Plot Point 1)", "description": "主角被迫进入新世界"}
                ],
                "purpose": "建立世界、介绍人物、触发事件"
            },
            {
                "name": "第二幕 (Act II: Confrontation)",
                "percentage": 50,
                "key_moments": [
                    {"position": 25, "name": "B故事开始 (B Story)", "description": "副线展开"},
                    {"position": 37.5, "name": "中点 (Midpoint)", "description": "假胜利或假失败，方向改变"},
                    {"position": 50, "name": "一无所有 (All Is Lost)", "description": "至暗时刻，最大危机"}
                ],
                "purpose": "冲突升级、障碍重重、考验成长"
            },
            {
                "name": "第三幕 (Act III: Resolution)",
                "percentage": 25,
                "key_moments": [
                    {"position": 75, "name": "灵魂黑夜后的黎明", "description": "吸取教训，准备最终决战"},
                    {"position": 90, "name": "高潮 (Climax)", "description": "终极对决，核心冲突解决"},
                    {"position": 98, "name": "终场画面 (Final Image)", "description": "与开场呼应，展示转变"}
                ],
                "purpose": "解决冲突、完成转变、收束主题"
            }
        ]
    },
    
    "heros_journey": {
        "name": "英雄之旅 (Hero's Journey / Monomyth)",
        "description": "约瑟夫·坎贝尔提出的普世神话结构",
        "phases": [
            # 第一阶段：启程
            {"phase": "平凡世界", "type": "setup", "description": "展示主角日常，建立对比基准"},
            {"phase": "冒险召唤", "type": "inciting", "description": "收到任务/挑战/邀请"},
            {"phase": "拒绝召唤", "type": "resistance", "description": "犹豫、恐惧、自我怀疑"},
            {"phase": "遇见导师", "type": "mentor", "description": "获得智慧/工具/鼓励"},
            {"phase": "跨越第一道门槛", "type": "commitment", "description": "正式进入特殊世界"},
            
            # 第二阶段：考验
            {"phase": "考验、盟友、敌人", "type": "trials", "description": "学习规则、结识伙伴、面对敌人"},
            {"phase": "接近洞穴深处", "type": "approach", "description": "接近目标，风险增大"},
            {"phase": "磨难/至暗时刻", "type": "ordeal", "description": "面对最大恐惧，濒临死亡（象征性）"},
            {"phase": "奖赏/宝剑", "type": "reward", "description": "获得所需之物（知识/物品/力量）"},
            
            # 第三阶段：回归
            {"phase": "回归之路", "type": "return", "description": "带着奖赏返回，追兵逼近"},
            {"phase": "复活/蜕变", "type": "transformation", "description": "最终考验，证明已改变"},
            {"phase": "回归万能药", "type": "resolution", "description": "用所学解决原问题，世界变好"}
        ]
    },
    
    "save_the_cat": {
        "name": "救猫咪 (Save the Cat)",
        "description": "布莱克·斯奈德的实用编剧法，强调观众共情",
        "beats": [
            {"beat": "开场画面", "template": "展示主角生活状态的一帧快照，让观众知道这是谁、在哪、做什么"},
            {"beat": "主题呈现", "template": "通过对话或事件暗示本集的核心主题"},
            {"beat": "铺垫", "template": "建立主角的世界、关系、日常，让观众喜欢TA"},
            {"beat": "推动/催化剂", "template": "打破平衡的事件发生（不一定是大事）"},
            {"beat": "辩论", "template": "主角犹豫是否接受冒险，展示内心挣扎"},
            {"beat": "进入第二幕/B故事", "template": "主角决定行动，副线展开"},
            {"beat": "游戏与乐趣", "template": "在新世界中探索，展现主角的能力和魅力"},
            {"beat": "中点", "template": "假胜利或假失败， stakes提高"},
            {"beat": "坏家伙逼近", "template": "压力增大，内部外部威胁同时出现"},
            {"beat": "一无所有", "template": "失去一切，触底时刻"},
            {"beat": "灵魂黑夜", "template": "绝望中的反思，找到真正的答案"},
            {"beat": "进入第三幕/破釜沉舟", "template": "带着新的理解，最后冲刺"},
            {"beat": "结局", "template": "最终对决，主题得到验证"},
            {"beat": "终场画面", "template": "与开场呼应，展示改变"}
        ]
    },
    
    "story_atoms_dan_harmon": {
        "name": "丹·哈蒙故事原子 (Story Atoms)",
        "description": "8个基本叙事单元，可灵活组合成任何长度故事",
        "atoms": [
            {"atom": "引入 (Setup)", "duration_ratio": 0.15, "elements": ["who", "where", "when", "what's at stake"]},
            {"atom": "反应 (Reaction)", "duration_ratio": 0.10, "elements": ["emotional response", "decision point"]},
            {"atom": "行动 (Action)", "duration_ratio": 0.20, "elements": ["attempt", "obstacle encountered"]},
            {"atom": "对抗 (Opposition)", "duration_ratio": 0.15, "elements": ["conflict escalation", "stakes raised"]},
            {"atom": "转折 (Twist/Turn)", "duration_ratio": 0.10, "elements": ["unexpected event", "new information"]},
            {"atom": "高潮 (Climax)", "duration_ratio": 0.10, "elements": ["peak tension", "critical choice"]},
            {"atom": "解决 (Resolution)", "duration_ratio": 0.15, "elements": ["outcome revealed", "consequences shown"]},
            {"atom": "余韵 (Aftermath)", "duration_ratio": 0.05, "elements": ["new status quo", "hook for next"]}
        ]
    },
    
    "kisho_ketsu": {
        "name": "起承转合 (Kishōketsu)",
        "description": "东亚传统四段式结构，简洁有力",
        "phases": [
            {"phase": "起 (Ki)", "description": "开端、引入、铺陈背景"},
            {"phase": "承 (Shō)", "description": "承接、发展、情节推进"},
            {"phase": "转 (Ten)", "description": "转折、突变、高潮爆发"},
            {"phase": "合 (Ketsu)", "description": "收束、结局、余韵悠长"}
        ]
    }
}

# ==================== 竖屏短剧专用结构 ====================

VERTICAL_DRAMA_STRUCTURE = {
    "name": "竖屏短剧黄金结构 (Golden 60-90s Structure)",
    "total_duration_target": [60, 90],
    "beats": [
        {
            "beat_name": "HOOK (钩子)",
            "time_range": [0, 3],
            "purpose": "前3秒必须抓住注意力",
            "techniques": [
                "直接抛出冲突/反常点",
                "从动作中间开始(in media res)",
                "制造悬念或震惊",
                "强烈的视觉冲击"
            ],
            "what_to_avoid": [
                "缓慢的环境描写",
                "冗长的旁白",
                "平淡的日常开场",
                "没有明确焦点的镜头"
            ],
            "emotion_target": "curiosity/surprise/shock",
            "dialogue_rule": "台词不超过10字，最好无台词，纯视觉冲击"
        },
        {
            "beat_name": "SETUP (铺垫)",
            "time_range": [3, 18],
            "purpose": "快速交代必要信息，建立共情",
            "techniques": [
                "用动作展示而非告诉",
                "只交代绝对必要的信息(5W中的2-3个)",
                "建立主角的可爱之处(Save the Cat moment)",
                "暗示潜在冲突"
            ],
            "what_to_avoid": [
                "信息倾倒(exposition dump)",
                "无关的角色介绍",
                "过长的背景说明",
                "与主线无关的支线"
            ],
            "emotion_target": "connection/empathy/investment",
            "dialogue_rule": "台词不超过12字，每句都有推进作用"
        },
        {
            "beat_name": "ESCALATION (升级)",
            "time_range": [18, 55],
            "purpose": "冲突升级，爽点密集，情绪爬升",
            "techniques": [
                "每15秒一个小反转",
                "压力阶梯式上升",
                "内外部冲突交织",
                "角色面临艰难选择",
                "冰山法则：能用动作就不用台词"
            ],
            "what_to_avoid": [
                "节奏松散",
                "重复相同的冲突模式",
                "角色行为不符合逻辑",
                "缺乏情感层次"
            ],
            "emotion_target": "tension/excitment/frustration → building to release",
            "dialogue_rule": "台词不超过15字，短促有力，充满潜台词"
        },
        {
            "beat_name": "CLIMAX (高潮)",
            "time_range": [55, 78],
            "purpose": "核心冲突爆发，情绪最高点",
            "techniques": [
                "最大的赌注在此刻",
                "角色必须做出不可逆的选择",
                "视觉和听觉达到峰值",
                "主题得到最强表达"
            ],
            "what_to_avoid": [
                "高潮不够高(anti-climax)",
                "轻易解决的困境",
                "缺乏情感冲击力",
                "与前面铺垫脱节"
            ],
            "emotion_target": "catharsis/triumph/devastation",
            "dialogue_rule": "台词不超过8字，最好是标志性金句或无声胜有声"
        },
        {
            "beat_name": "CLIFFHANGER (悬念)",
            "time_range": [78, 90],
            "purpose": "强制留钩子，引导观看下一集",
            "techniques": [
                "新危机突然出现",
                "意想不到的反转",
                "关键信息揭露",
                "角色面临更大困境",
                "开放式结尾但有方向性"
            ],
            "what_to_avoid": [
                "完全封闭的结局",
                "悬念太弱不值得等待",
                "与下一集无法连接",
                "破坏角色一致性"
            ],
            "emotion_target": "anticipation/despair/hope mixed with dread",
            "dialogue_rule": "台词不超过8字，最好是无声的画面+音效"
        }
    ]
}

# ==================== 角色弧线模板 ====================

CHARACTER_ARCS = {
    "positive_change": {
        "name": "正向转变弧 (Positive Change Arc)",
        "description": "角色从缺陷走向完整",
        "stages": [
            {"stage": "flawed_state", "description": "初始状态，有明显弱点/错误信念"},
            {"stage": "call_to_change", "description": "被要求改变，最初抗拒"},
            {"stage": "struggle", "description": "在尝试中失败，旧习惯难以打破"},
            {"stage": "rock_bottom", "description": "必须改变的临界点"},
            {"stage": "transformation", "description": "真正接受改变，付出代价"},
            {"stage": "new_equilibrium", "description": "以新状态解决问题"}
        ]
    },
    "negative_change": {
        "name": "负向堕落弧 (Negative Change Arc / Tragic Flaw)",
        "description": "角色因致命弱点而毁灭",
        "stages": [
            {"stage": "potential", "description": "有潜力但已有隐患"},
            {"stage": "temptation", "description": "诱惑出现，开始走偏"},
            {"stage": "compromise", "description": "为达目的逐步妥协"},
            {"stage": "justification", "description": "为错误行为找借口"},
            {"stage": "crisis", "description": "后果显现，但可能为时已晚"},
            {"stage": "fall", "description": "因未改变而遭受命运惩罚"}
        ]
    },
    "flat_arc": {
        "name": "平坦弧 (Flat Arc / Steadfast Character)",
        "description": "角色本身不变，但改变了周围世界",
        "stages": [
            {"stage": "establish_belief", "description": "确立角色的核心价值观"},
            {"stage": "world_resists", "description": "世界挑战这个价值观"},
            {"stage": "pressure_mounts", "description": "压力增大，动摇但不屈服"},
            {"stage": "climax_test", "description": "终极考验，证明价值观正确"},
            {"stage": "world_changes", "description": "因为角色的坚持，世界变得更好"}
        ]
    }
}

# ==================== 专业Prompt构建器 ====================

class ProfessionalPromptBuilder:
    """
    专业级Prompt构建器
    根据不同需求组合各种编剧理论和技巧
    """
    
    def __init__(self):
        self.theories = SCREENPLAY_THEORIES
        self.vertical_structure = VERTICAL_DRAMA_STRUCTURE
        self.character_arcs = CHARACTER_ARCS
    
    def build_screenplay_prompt(self, episode_info, global_lore, config_options=None):
        """
        构建专业级剧本生成Prompt
        
        Args:
            episode_info: 集数信息 {seq, core_plot, hook, climax, ending_suspense, main_characters}
            global_lore: 全局设定 {characters, story_rules, genre...}
            config_options: 配置选项 {structure_type, arc_type, tone_style...}
        
        Returns:
            str: 完整的专业级Prompt
        """
        options = config_options or {}
        seq = episode_info['seq']
        
        # 选择结构类型
        structure_type = options.get("structure_type", "vertical_drama_golden")
        arc_type = options.get("arc_type", "positive_change")
        tone_style = options.get("tone_style", "intense")
        
        # 构建Prompt各部分
        prompt_parts = []
        
        # ====== 第一部分：角色定义 ======
        prompt_parts.append(self._build_role_definition())
        
        # ====== 第二部分：理论框架 ======
        prompt_parts.append(self._build_framework_section(structure_type))
        
        # ====== 第三部分：剧集特定信息 ======
        prompt_parts.append(self._build_episode_specifics(episode_info, global_lore))
        
        # ====== 第四部分：角色弧线指导 ======
        prompt_parts.append(self._build_character_arc_guidance(arc_type, global_lore))
        
        # ====== 第五部分：技术约束 ======
        prompt_parts.append(self._build_technical_constraints(tone_style))
        
        # ====== 第六部分：输出格式 ======
        prompt_parts.append(self._build_output_format())
        
        return "\n\n".join(prompt_parts)
    
    def _build_role_definition(self):
        """构建角色定义部分"""
        return f"""【你的身份】
你是一位拥有20年经验的**好莱坞A级编剧**，精通以下所有编剧理论：
• 三幕式结构 (Three-Act Structure) - 亚里士多德/悉德·菲尔德
• 英雄之旅 (Hero's Journey) - 约瑟夫·坎贝尔/克里斯托弗·沃格勒  
• 救猫咪 (Save the Cat) - 布莱克·斯奈德
• 丹·哈蒙故事原子 (Story Atoms) - Dan Harmon
• 起承转合 (Kishōketsu) - 东亚古典结构

你擅长创作**60-90秒竖屏短剧**，深知：
• 完播率Retention Rate是生命线
• 前3秒(Hook)决定生死
• 冰山法则：能用动作表达的绝不用台词
• 台词必须精炼到每个字都有存在的意义"""
    
    def _build_framework_section(self, structure_type):
        """构建理论框架部分"""
        if structure_type == "vertical_drama_golden":
            structure = self.vertical_structure
            framework_text = f"""【本次使用的结构框架】
**{structure['name']}**
目标时长: {structure['total_duration_target'][0]}-{structure['total_duration_target'][1]}秒

**五段式节拍要求**:
"""
            for beat in structure["beats"]:
                framework_text += f"""
▶ {beat['beat_name']} ({beat['time_range'][0]}-{beat['time_range'][1]}秒)
   目的: {beat['purpose']}
   技巧: {' | '.join(beat['techniques'][:3])}
   避免: {' | '.join(beat['what_to_avoid'][:2])}
   情绪目标: {beat['emotion_target']}
   台词规则: {beat['dialogue_rule']}
"""
            return framework_text
        
        elif structure_type in self.theories:
            theory = self.theories[structure_type]
            framework_text = f"""【本次使用的结构框架】
**{theory['name']}**
{theory['description']}

"""
            if "acts" in theory:
                for act in theory["acts"]:
                    framework_text += f"\n**{act['name']}** ({act['percentage']}%):\n"
                    for moment in act.get("key_moments", []):
                        framework_text += f"  • {moment['position']}% {moment['name']}: {moment['description']}\n"
                    framework_text += f"  目的: {act['purpose']}\n"
            
            if "phases" in theory:
                for phase in theory["phases"]:
                    framework_text += f"  {phase['phase'].ljust(20)} [{phase['type']}]: {phase['description']}\n"
            
            if "beats" in theory:
                for beat in theory["beats"]:
                    framework_text += f"  • {beat['beat']}: {beat['template']}\n"
            
            return framework_text
        
        return ""
    
    def _build_episode_specifics(self, episode_info, global_lore):
        """构建剧集特定信息部分"""
        seq = episode_info['seq']
        main_chars = episode_info.get('main_characters', [])
        characters_data = global_lore.get('characters', [])
        
        # 找出主要角色的详细信息
        main_char_details = []
        for char_name in main_chars[:3]:
            for char in characters_data:
                if char.get('name') == char_name:
                    main_char_details.append(char)
                    break
        
        specifics = f"""【剧集特定信息】

**第{seq}集基本信息**:
• 核心剧情: {episode_info.get('core_plot', 'N/A')}
• 开头钩子(Hook): {episode_info.get('hook', 'N/A')}  
• 核心爽点(Climax): {episode_info.get('climax', 'N/A')}
• 结尾悬念(Cliffhanger): {episode_info.get('ending_suspense', 'N/A')}

**主要角色**:
"""
        
        for i, char in enumerate(main_char_details[:3], 1):
            specifics += f"""角色{i}: {char.get('name', '未知')}
  - 身份: {char.get('identity', 'N/A')}
  - 性格: {char.get('personality', 'N/A')}
  - 外观特征: {', '.join(char.get('visual_traits', [])[:5])}
  - 声音类型: {char.get('voice_type', 'N/A')}
  - 本集角色目标: (根据剧情推断)
  - 本集情感状态: (根据剧情推断)
  - 与其他角色的关系: {json.dumps(char.get('relationships', {}), ensure_ascii=False)[:100]}

"""
        
        # 全局设定
        story_rules = global_lore.get('story_rules', {})
        genre = global_lore.get('genre', '未知')
        theme = global_lore.get('core_theme', '')
        
        specifics += f"""**全局世界观设定**:
• 类型/题材: {genre}
• 核心主题: {theme}
• 世界观规则: {story_rules.get('power_system', story_rules.get('world_setting', '通用'))}
• 常识设定: {story_rules.get('common_sense', '现代地球类似')}
"""
        
        return specifics
    
    def _build_character_arc_guidance(self, arc_type, global_lore):
        """构建角色弧线指导"""
        if arc_type not in self.character_arcs:
            return ""
        
        arc = self.character_arcs[arc_type]
        guidance = f"""【角色弧线指导 - {arc['name']}】
{arc['description']}

本集在弧线中的位置建议:
"""
        stages = arc.get("stages", [])
        total_stages = len(stages)
        
        for i, stage in enumerate(stages):
            progress = (i + 1) / total_stages * 100
            guidance += f"  {stage['stage'].ljust(25)} → {stage['description']}"
            guidance += f" (进度: ~{progress:.0f}%)\n"
        
        guidance += """
请确保本集的内容能够推进角色在这个弧线上的发展。
"""
        return guidance
    
    def _build_technical_constraints(self, tone_style):
        """构建技术约束"""
        tone_map = {
            "intense": "紧张激烈、快节奏、高冲突密度",
            "melancholic": "忧郁内省、慢节奏、情感深沉",
            "romantic": "浪漫温馨、柔和节奏、情感流动",
            "mysterious": "神秘悬疑、中等节奏、信息渐进释放",
            "epic": "史诗宏大、节奏张弛有度、格局宏大"
        }
        
        constraints = f"""【技术约束与质量标准】

**整体风格**: {tone_map.get(tone_style, '标准商业短剧风格')}

**冰山法则严格执行**:
• 对话只能露出水面上的10%，90%是潜台词和动作
• 如果一个意思可以用表情/动作表达，绝不能用台词
• 台词必须是角色"不得不说"的话，而不是"想说"的话

**台词精炼标准**:
• Hook段: ≤10字，最好0字（纯视觉）
• Setup段: ≤12字，每句必须有信息量
• Escalation段: ≤15字，短促有力，充满张力
• Climax段: ≤8字，最好是标志性金句或沉默
• Cliffhanger段: ≤8字，最好是无声的画面

**视觉化写作要求**:
• 每个beat必须包含明确的视觉元素描述
• 注明镜头语言暗示（特写/全景/推拉摇移）
• 注明光影氛围（明亮/阴暗/冷暖色调）
• 注明声音设计要点（环境音/音乐情绪）

**完播率优化**:
• 每5秒必须有一个"微钩子"(mini-hook)维持注意
• 避免超过3秒的无变化镜头
• 信息密度要高但不能过载
• 结尾必须让人产生"接下来会怎样"的强烈好奇
"""
        return constraints
    
    def _build_output_format(self):
        """构建输出格式"""
        return """【输出格式要求】

严格输出JSON格式，不要任何解释、markdown标记或额外文字。
直接输出JSON对象：

{
    "episode_seq": <集数>,
    "structure_used": "<使用的结构名称>",
    "theme_statement": "<本集的主题陈述(一句话)>",
    "character_arcs_progress": {
        "<角色名>": "<该角色在本集的弧线进展>"
    },
    "retention_curve_analysis": {
        "hook_strength": "<1-10分>",
        "escalation_pace": "<适中/快/慢>",
        "climax_impact": "<1-10分>",
        "cliffhanger_strength": "<1-10分>"
    },
    "beats": [
        {
            "beat_type": "hook/setup/escalation/climax/cliffhanger",
            "content": "<详细的节拍内容描述，包含视觉、动作、对白>",
            "visual_description": "<画面描述：构图、光线、色彩、运动>",
            "audio_cue": "<音频提示：环境音、音乐情绪、音效重点>",
            "dialogue_limit": <字数限制>,
            "duration": <预计时长(秒)>,
            "emotional_target": "<目标情绪>",
            "narrative_function": "<这个节拍在故事中的作用>",
            "micro_hooks": [<每5-8秒的小钩子列表>]
        }
    ],
    "total_duration": <总时长>,
    "quality_check": {
        "iceberg_compliance": true/false,
        "dialogue_density": "<低/中/高>",
        "visual_storytelling_score": "<1-10>"
    }
}"""

# ==================== 自适应Prompt优化器 ====================

class AdaptivePromptOptimizer:
    """
    自适应Prompt优化器
    根据历史生成质量和反馈动态调整Prompt
    """
    
    def __init__(self):
        self.performance_history = {}
        self.optimization_rules = {
            "low_retention": {
                "symptoms": ["hook_weak", "slow_start", "no_surprise"],
                "adjustments": [
                    "增加Hook段的冲击力要求",
                    "强调in media res(从中间开始)技巧",
                    "添加具体的反常/冲突示例"
                ]
            },
            "weak_climax": {
                "symptoms": ["climax_flat", "low_stakes", "rushed"],
                "adjustments": [
                    "强化Climax段的赌注(stakes)描述",
                    "要求更长的Climax时长分配",
                    "添加'必须做出不可逆选择'的要求"
                ]
            },
            "weak_cliffhanger": {
                "symptoms": ["ending_closed", "no_curiosity", "predictable"],
                "adjustments": [
                    "强调开放式结尾的方向性",
                    "添加'新危机突然出现'的强制要求",
                    "要求最后一秒的反转"
                ]
            },
            "too_expository": {
                "symptoms": ["heavy_dialogue", "info_dump", "tell_not_show"],
                "adjustments": [
                    "强化冰山法则约束",
                    "降低dialogue_limit",
                    "添加'用动作替代台词'的具体示例"
                ]
            }
        }
    
    def analyze_and_optimize(self, base_prompt, quality_metrics=None, user_feedback=None):
        """
        分析质量问题并优化Prompt
        
        Args:
            base_prompt: 原始Prompt
            quality_metrics: 质量指标字典 {retention_score, climax_score, ...}
            user_feedback: 用户反馈文本
            
        Returns:
            str: 优化后的Prompt
        """
        issues_detected = []
        optimizations_to_add = []
        
        # 基于质量指标检测问题
        if quality_metrics:
            retention = quality_metrics.get("retention_score", 0)
            climax = quality_metrics.get("climax_score", 0)
            cliffhanger = quality_metrics.get("cliffhanger_score", 0)
            dialogue_quality = quality_metrics.get("dialogue_quality_score", 0)
            
            if retention < 7:
                issues_detected.append("low_retention")
            if climax < 7:
                issues_detected.append("weak_climax")
            if cliffhanger < 7:
                issues_detected.append("weak_cliffhanger")
            if dialogue_quality < 6:
                issues_detected.append("too_expository")
        
        # 收集需要的优化
        for issue in issues_detected:
            if issue in self.optimization_rules:
                optimizations_to_add.extend(
                    self.optimization_rules[issue]["adjustments"]
                )
        
        # 如果有优化内容，添加到Prompt末尾
        if optimizations_to_add:
            optimization_section = "\n\n【⚠️ 动态优化指令 - 基于历史表现】\n"
            optimization_section += "针对之前生成内容的改进要求:\n"
            for opt in optimizations_to_add:
                optimization_section += f"• {opt}\n"
            
            return base_prompt + optimization_section
        
        return base_prompt


def generate_professional_screenplay_prompt(episode_info, global_lore, 
                                          structure="vertical_drama_golden",
                                          arc_type="positive_change",
                                          tone="intense",
                                          enable_adaptive=False,
                                          quality_history=None):
    """
    一站式生成专业级剧本Prompt
    
    Returns:
        tuple: (prompt_str, metadata_dict)
    """
    builder = ProfessionalPromptBuilder()
    
    # 构建基础Prompt
    prompt = builder.build_screenplay_prompt(episode_info, global_lore, {
        "structure_type": structure,
        "arc_type": arc_type,
        "tone_style": tone
    })
    
    # 可选：自适应优化
    if enable_adaptive and quality_history:
        optimizer = AdaptivePromptOptimizer()
        prompt = optimizer.analyze_and_optimize(prompt, quality_history)
    
    metadata = {
        "structure_used": structure,
        "arc_type": arc_type,
        "tone_style": tone,
        "prompt_length": len(prompt),
        "theories_referenced": [
            "Three-Act Structure",
            "Hero's Journey", 
            "Save the Cat",
            "Story Atoms",
            "Kishōketsu",
            "Iceberg Principle",
            "Vertical Drama Golden Structure"
        ]
    }
    
    return prompt, metadata

if __name__ == "__main__":
    print("=" * 70)
    print("专业剧本提示词工程系统测试")
    print("=" * 70)
    
    test_episode = {
        "seq": 1,
        "core_plot": "废柴少年意外获得上古传承，发现家族灭门真相，踏上复仇之路",
        "hook": "少年在垃圾堆中发现一把生锈的古剑，剑身浮现血色符文",
        "climax": "少年觉醒第一丝灵力，一剑斩杀前来灭口的仇敌",
        "ending_suspense": "远处传来熟悉的气息，那个传说中的存在正在靠近...",
        "main_characters": ["叶辰", "苏清歌"]
    }
    
    test_global_lore = {
        "genre": "玄幻修真",
        "core_theme": "弱者的逆袭与守护",
        "characters": [
            {
                "name": "叶辰",
                "identity": "废柴少爷/隐藏血脉继承者",
                "personality": "外表懒散内心坚韧，重情重义",
                "visual_traits": ["清秀面容", "瘦削身材", "眼中偶尔闪过锋芒"],
                "voice_type": "年轻男声，平时慵懒，认真时冷峻",
                "relationships": {"苏清歌": "青梅竹马/暗恋对象"}
            },
            {
                "name": "苏清歌",
                "identity": "天才少女/宗门圣女",
                "personality": "外冷内热，傲娇护短",
                "visual_traits": ["绝美容颜", "冰蓝色长裙", "清冷气质"],
                "voice_type": "清冷女声，对叶辰时带一丝温柔",
                "relationships": {"叶辰": "在意的人/未来的依靠"}
            }
        ],
        "story_rules": {
            "power_system": "灵力修炼体系：炼体→聚气→凝元→化神→渡劫→飞升",
            "world_setting": "苍澜大陆，强者为尊，宗门林立",
            "common_sense": "实力至上，弱肉强食，但也有情义存在"
        }
    }
    
    # 生成Prompt
    prompt, meta = generate_professional_screenplay_prompt(
        test_episode, 
        test_global_lore,
        structure="vertical_drama_golden",
        arc_type="positive_change",
        tone="intense"
    )
    
    print(f"\n📝 生成的Prompt元数据:")
    print(f"  结构: {meta['structure_used']}")
    print(f"  弧线: {meta['arc_type']}")
    print(f"  风格: {meta['tone_style']}")
    print(f"  长度: {len(prompt)} 字符")
    print(f"  引用理论: {len(meta['theories_referenced'])} 种")
    
    print(f"\n📄 Prompt预览 (前500字符):")
    print("-" * 50)
    print(prompt[:500])
    print("...")
    print("-" * 50)
