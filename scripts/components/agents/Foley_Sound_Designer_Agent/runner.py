import json
import os
import hashlib
import requests
from config_center import config

def run_foley_sound_designer(storyboard, scene_context, continuity_state=None):
    """
    Foley & Sound Designer (拟音与声音设计) V6 影棚级
    空间声学 频段分离 零通用音效
    完全符合院线级音频制作标准，3D沉浸感拉满
    新增TTS自动配音、缓存、人工审核功能
    """
    seq = storyboard['episode_seq']
    
    # 缓存检查
    cache_enabled = config.get("foley.cache_enabled", True)
    if cache_enabled:
        cache_key = hashlib.md5(f"{seq}_{json.dumps(storyboard['storyboard'])}".encode('utf-8')).hexdigest()
        cache_path = os.path.join("output/cache", f"audio_design_{cache_key}.json")
        if os.path.exists(cache_path):
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_audio = json.load(f)
            print(f"第{seq}集音频设计已缓存，直接加载")
            return cached_audio
    
    # ==================== V6 强制专业规则 ====================
    # 空间声学映射表
    SPATIAL_ACOUSTIC_RULES = {
        "indoor_small": "muffled, reverb decay 0.5s, close proximity",
        "indoor_large": "echoing, reverb decay 2s, distant reflections",
        "outdoor_open": "dry, no reverb, wide panning",
        "outdoor_enclosed": "slight reverb, distant echos, wind noise floor"
    }
    
    # 频段分离规则
    EQ_RULES = {
        "impact/collision": "Low-frequency sub-bass rumble + Mid-range thud + High-frequency crisp detail",
        "glass/breaking": "High-frequency shattering + Low-frequency resonant thud",
        "dialogue": "Mid-range boosted, high-frequency air included, low-frequency rolled off",
        "ambience": "Low-frequency rumble floor + Mid-range texture + High-frequency air detail"
    }
    
    # BGM情绪匹配规则
    MUSIC_RULES = {
        "tense": "tense suspenseful score, BPM 120, dark ambient",
        "action": "high energy action score, BPM 140, strong percussion",
        "emotional": "emotional piano score, BPM 80, soft strings",
        "happy": "upbeat happy score, BPM 100, bright instruments",
        "scary": "horror suspense score, BPM 90, dissonant sounds"
    }
    
    processed_audio = []
    
    # 自动生成配音（如果开启）
    enable_tts = config.get("foley.enable_tts", False)
    tts_api_key = config.get("foley.tts_api_key", "")
    tts_endpoint = config.get("foley.tts_endpoint", "https://api.siliconflow.cn/v1/audio/speech")
    
    for idx, shot in enumerate(storyboard['storyboard']):
        shot_content = shot['visual_prompt'].lower()
        shot_id = shot['shot_id']
        dialogue = shot['audio_prompt'].get('Dialogue', '')
        
        # 匹配空间声学属性
        if "室内" in shot_content or "房间" in shot_content or "屋" in shot_content:
            if "大厅" in shot_content or "厂房" in shot_content or "车库" in shot_content:
                spatial = SPATIAL_ACOUSTIC_RULES["indoor_large"]
            else:
                spatial = SPATIAL_ACOUSTIC_RULES["indoor_small"]
        elif "室外" in shot_content or "天台" in shot_content or "野外" in shot_content:
            if "山谷" in shot_content or "峡谷" in shot_content or "楼群" in shot_content:
                spatial = SPATIAL_ACOUSTIC_RULES["outdoor_enclosed"]
            else:
                spatial = SPATIAL_ACOUSTIC_RULES["outdoor_open"]
        else:
            spatial = SPATIAL_ACOUSTIC_RULES["outdoor_open"]
        
        # 匹配频段分离效果
        if any(keyword in shot_content for keyword in ["碰撞", "爆炸", "击打", "砸", "摔"]):
            eq = EQ_RULES["impact/collision"]
        elif any(keyword in shot_content for keyword in ["玻璃", "碎", "裂", "断"]):
            eq = EQ_RULES["glass/breaking"]
        elif any(keyword in shot_content for keyword in ["说话", "对话", "喊", "叫", "说"]):
            eq = EQ_RULES["dialogue"]
        else:
            eq = EQ_RULES["ambience"]
        
        # 匹配BGM风格
        if any(keyword in shot_content for keyword in ["紧张", "害怕", "危机", "悬疑"]):
            music = MUSIC_RULES["tense"]
        elif any(keyword in shot_content for keyword in ["打斗", "战斗", "追逐", "爆炸"]):
            music = MUSIC_RULES["action"]
        elif any(keyword in shot_content for keyword in ["感动", "伤心", "哭", "回忆"]):
            music = MUSIC_RULES["emotional"]
        elif any(keyword in shot_content for keyword in ["开心", "笑", "幸福", "甜蜜"]):
            music = MUSIC_RULES["happy"]
        elif any(keyword in shot_content for keyword in ["恐怖", "吓人", "鬼", "诡异"]):
            music = MUSIC_RULES["scary"]
        else:
            music = shot['audio_prompt'].get('Music', 'neutral ambient score')
        
        # 自动生成配音
        audio_path = ""
        if enable_tts and tts_api_key and dialogue:
            try:
                headers = {
                    "Authorization": f"Bearer {tts_api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": config.get("foley.tts_model", "speech_tts"),
                    "input": dialogue,
                    "voice": config.get("foley.default_voice", "female_young")
                }
                response = requests.post(tts_endpoint, headers=headers, json=payload, timeout=30)
                if response.status_code == 200:
                    # 保存音频文件
                    audio_dir = os.path.join("output", f"episode_{seq}", "audio")
                    os.makedirs(audio_dir, exist_ok=True)
                    audio_path = os.path.join(audio_dir, f"{shot_id}_dialogue.mp3")
                    with open(audio_path, 'wb') as f:
                        f.write(response.content)
                    print(f"第{seq}集{shot_id}配音生成成功：{audio_path}")
            except Exception as e:
                print(f"配音生成失败：{str(e)}")
        
        # 生成专业级音频提示词
        audio_prompt = {
            "Spatial": spatial,
            "EQ": eq,
            "Ambience": shot['audio_prompt'].get('Ambience', 'neutral background noise'),
            "SFX": shot['audio_prompt'].get('SFX', 'foley matched to action'),
            "Music": music,
            "Dialogue": dialogue,
            "dialogue_audio_path": audio_path
        }
        
        processed_audio.append({
            "shot_id": shot_id,
            "audio_prompt": audio_prompt
        })
    
    # 保存缓存
    if cache_enabled:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(processed_audio, f, ensure_ascii=False, indent=2)
    
    # 人工审核音频设计
    from components.utils.human_review_manager import human_review
    if config.get("foley.enable_review", False):
        if not human_review.request_review("audio_design", processed_audio, seq):
            # 审核被驳回，删除缓存重新生成
            if os.path.exists(cache_path):
                os.remove(cache_path)
            raise Exception(f"第{seq}集音频设计审核被驳回")
    
    return processed_audio
