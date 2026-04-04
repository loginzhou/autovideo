# -*- coding: utf-8 -*-
"""
Dialogue Master Agent (台词大师)
基于剧本节拍生成专业级角色台词，确保台词符合角色性格、推动剧情发展
"""
import json
import os
import hashlib
import re
from config_center import config
from components.utils.llm_client import get_llm_response


def run_dialogue_master(screenplay, global_lore, continuity_state=None):
    """
    台词大师 V1.0
    为每个剧本节拍生成专业台词，包含情绪标记和表演指导
    """
    seq = screenplay['episode_seq']
    beats = screenplay['beats']
    characters = global_lore.get('characters', [])
    
    print(f"\n{'='*60}")
    print(f"台词大师启动 - 第{seq}集")
    print(f"{'='*60}")
    
    # 缓存检查
    cache_enabled = config.get("dialogue_master.cache_enabled", True)
    if cache_enabled:
        cache_key = hashlib.md5(f"{seq}_{json.dumps(beats)}_{json.dumps(characters)}".encode('utf-8')).hexdigest()
        cache_path = os.path.join("output/cache", f"dialogue_{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_dialogue = json.load(f)
            print(f"第{seq}集台词已缓存，直接加载")
            return cached_dialogue
    
    # 构建角色信息
    char_info = []
    main_char = characters[0] if characters else {"name": "主角", "personality": "坚强", "voice_type": "中性"}
    for char in characters[:3]:  # 只取前3个主要角色
        char_info.append({
            "name": char.get('name', '未知'),
            "personality": char.get('personality', ''),
            "voice_type": char.get('voice_type', '中性'),
            "speaking_style": char.get('speaking_style', ''),
            "catchphrase": char.get('catchphrase', '')
        })
    
    enable_ai_generation = config.get("dialogue_master.enable_ai_generation", True)
    dialogue_script = []
    
    if enable_ai_generation:
        # AI生成台词
        prompt = f"""
你是专业短剧台词编剧，擅长创作60-90秒竖屏短剧的精炼台词。

剧集信息：
第{seq}集
主要角色：{json.dumps(char_info, ensure_ascii=False)}
跨集状态：{json.dumps(continuity_state, ensure_ascii=False) if continuity_state else '无'}

剧本节拍：
{json.dumps(beats, ensure_ascii=False)}

台词创作原则：
1. **冰山法则**：能用动作和表情表达的，绝不用台词
2. **情绪优先**：台词要传递强烈情绪（愤怒、悲伤、震惊、喜悦）
3. **口语化**：避免书面语，使用日常口语和网络流行语
4. **短句为主**：每句不超过15字，节奏快
5. **冲突驱动**：台词推动冲突升级，制造张力
6. **角色区分**：不同角色有不同的说话风格和口头禅
7. **情绪标记**：每句台词标注情绪状态

输出严格为JSON格式：
{{
    "dialogues": [
        {{
            "shot_id": "ep{seq}_shot01",
            "speaker": "角色名",
            "content": "台词内容（不超过15字）",
            "emotion": "情绪标签（愤怒/悲伤/震惊/喜悦/恐惧/冷漠/嘲讽等）",
            "delivery": "表演指导（语气、语速、停顿）",
            "subtext": "潜台词/言外之意",
            "duration": 3.5
        }}
    ]
}}

注意：
- Hook部分（前3秒）：台词要爆炸性，直接冲突
- Setup部分：快速交代信息，台词简洁
- Escalation部分：冲突升级，情绪激烈
- Cliffhanger部分：悬念感强，引导下一集
"""
        try:
            response = get_llm_response(
                prompt,
                model=config.get("dialogue_master.model", "deepseek-ai/DeepSeek-V3.2"),
                task_type="dialogue",
                temperature=config.get("dialogue_master.temperature", 0.8),
                max_tokens=2000
            )
            result = json.loads(response)
            dialogue_script = result.get('dialogues', [])
            print(f"AI生成台词成功，共{len(dialogue_script)}句")
        except Exception as e:
            print(f"AI台词生成失败，使用规则生成：{str(e)}")
            enable_ai_generation = False
    
    if not enable_ai_generation:
        # 规则生成台词，作为fallback
        dialogue_script = generate_rule_based_dialogue(seq, beats, main_char)
    
    # 后处理：确保台词质量
    dialogue_script = post_process_dialogues(dialogue_script, beats)
    
    # 保存缓存
    if cache_enabled:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(dialogue_script, f, ensure_ascii=False, indent=2)
    
    print(f"台词生成完成，共{len(dialogue_script)}句")
    for d in dialogue_script[:3]:
        print(f"  [{d.get('speaker', '未知')}] {d.get('content', '')} ({d.get('emotion', '无情绪')})")
    
    return dialogue_script


def generate_rule_based_dialogue(seq, beats, main_char):
    """基于规则生成台词"""
    dialogues = []
    char_name = main_char.get('name', '主角')
    
    # 情绪模板库
    emotion_templates = {
        "hook": [
            {"content": "你再说一遍？！", "emotion": "愤怒"},
            {"content": "这不可能...", "emotion": "震惊"},
            {"content": "给我等着！", "emotion": "威胁"},
            {"content": "完了，全完了...", "emotion": "绝望"}
        ],
        "setup": [
            {"content": "事情是这样的...", "emotion": "平静"},
            {"content": "我查到了真相。", "emotion": "冷静"},
            {"content": "你听我解释。", "emotion": "急切"}
        ],
        "escalation": [
            {"content": "你竟敢骗我！", "emotion": "愤怒"},
            {"content": "我不会放过你！", "emotion": "威胁"},
            {"content": "这就是你的下场！", "emotion": "冷酷"},
            {"content": "住手！快住手！", "emotion": "惊恐"}
        ],
        "cliffhanger": [
            {"content": "你到底是谁？", "emotion": "震惊"},
            {"content": "这不可能...", "emotion": "难以置信"},
            {"content": "我们还会再见的。", "emotion": "神秘"}
        ]
    }
    
    shot_num = 1
    for beat in beats:
        beat_type = beat.get('beat_type', 'setup')
        templates = emotion_templates.get(beat_type, emotion_templates['setup'])
        
        # 每个节拍生成1-2句台词
        num_dialogues = 1 if beat_type in ['hook', 'cliffhanger'] else 2
        for i in range(num_dialogues):
            template = templates[(seq + shot_num + i) % len(templates)]
            dialogues.append({
                "shot_id": f"ep{seq}_shot{str(shot_num).zfill(2)}",
                "speaker": char_name,
                "content": template['content'],
                "emotion": template['emotion'],
                "delivery": "正常语速，情绪饱满",
                "subtext": "",
                "duration": 2.5
            })
            shot_num += 1
    
    return dialogues


def post_process_dialogues(dialogues, beats):
    """后处理台词，确保质量和一致性"""
    processed = []
    
    for i, d in enumerate(dialogues):
        # 清理台词
        content = d.get('content', '').strip()
        # 移除多余的标点
        content = re.sub(r'[。！？]{2,}', '！', content)
        # 确保台词长度合理
        if len(content) > 20:
            content = content[:18] + "..."
        
        # 标准化情绪标签
        emotion = d.get('emotion', '平静')
        emotion_map = {
            'angry': '愤怒', 'sad': '悲伤', 'happy': '喜悦',
            'shocked': '震惊', 'scared': '恐惧', 'cold': '冷漠',
            'mocking': '嘲讽', 'surprised': '惊讶'
        }
        emotion = emotion_map.get(emotion.lower(), emotion)
        
        # 计算合理时长（每秒约3-4个字）
        duration = max(1.5, min(5.0, len(content) / 3.5))
        
        processed.append({
            "shot_id": d.get('shot_id', f"shot_{i}"),
            "speaker": d.get('speaker', '主角'),
            "content": content,
            "emotion": emotion,
            "delivery": d.get('delivery', '正常语速'),
            "subtext": d.get('subtext', ''),
            "duration": round(duration, 1)
        })
    
    return processed
