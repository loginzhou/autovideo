import json
import uuid

def generate_dialogue_script(storyboard, global_lore):
    """
    自动生成对话脚本，影视化重写，匹配voice_id
    """
    # 加载角色库
    char_map = {}
    for char in global_lore['characters']:
        char_map[char['name']] = {
            "voice_id": char['voice_id'],
            "default_emotion": "calm"
        }
    # 临时voice_id分配，新角色自动分配
    temp_voice_counter = 2
    
    # 第1集预设对话，匹配原著剧情
    preset_dialogues = {
        "ep1_shot01": {
            "speaker": "林现",
            "content": "还有一个半小时天黑，该准备关闸门了。",
            "emotion": "calm",
            "pacing": 1.0
        },
        "ep1_shot02": {
            "speaker": "温先生",
            "content": "异想天开的东西，谁会管这些穷鬼的死活！",
            "emotion": "contemptuous",
            "pacing": 0.9
        },
        "ep1_shot03": {
            "speaker": "机长",
            "content": "失速了！我们被什么东西吸上去了！",
            "emotion": "terrified",
            "pacing": 1.5
        },
        "ep1_shot04": {
            "speaker": "女主",
            "content": "那是什么东西？！",
            "emotion": "horrified",
            "pacing": 1.6
        },
        "ep1_shot05": {
            "speaker": "林现",
            "content": "来了啊，比预计早了三天。",
            "emotion": "calm",
            "pacing": 1.1
        },
        "ep1_shot06": {
            "speaker": "系统",
            "content": "吞噬成功，机械源点+1，力量+1。",
            "emotion": "neutral",
            "pacing": 0.8
        }
    }
    
    dialogue_script = []
    for shot in storyboard['storyboard']:
        shot_id = shot['shot_id']
        preset = preset_dialogues.get(shot_id, {
            "speaker": "旁白",
            "content": "",
            "emotion": "neutral",
            "pacing": 1.0
        })
        
        # 匹配voice_id，新角色自动分配
        speaker = preset['speaker']
        if speaker in char_map:
            voice_id = char_map[speaker]['voice_id']
        else:
            # 新角色分配临时voice_id并更新全局库
            voice_id = f"temp_voice_{temp_voice_counter}"
            temp_voice_counter +=1
            char_map[speaker] = {"voice_id": voice_id, "default_emotion": preset['emotion']}
            # 同步更新到资产库
            with open("output/voice_library.json", 'w', encoding='utf-8-sig') as f:
                json.dump(char_map, f, ensure_ascii=False, indent=2)
        
        dialogue_script.append({
            "shot_id": shot_id,
            "speaker": speaker,
            "voice_id": voice_id,
            "content": preset['content'],
            "emotion": preset['emotion'],
            "pacing": preset['pacing']
        })
    
    return dialogue_script
