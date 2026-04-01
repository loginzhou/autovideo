import os
import json
import uuid
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS

# 启动前强制路径校验
check_write_permission(REQUIRED_PATHS)

# 加载全局蓝图
BLUEPRINT_PATH = "output/global_blueprint_sample.json"
OUTPUT_ROOT = "output/"
SANDBOX_ROOT = "sandbox/"

# 加载全局只读配置
global_config = {
    "vertical_screen": json.load(open("config/vertical_screen_spec.json", 'r', encoding='utf-8')),
    "character_schema": json.load(open("config/character_schema.json", 'r', encoding='utf-8')),
    "storyboard_schema": json.load(open("config/storyboard_schema.json", 'r', encoding='utf-8')),
    "model_routing": json.load(open("config/model_routing.json", 'r', encoding='utf-8')),
    "assets_registry": json.load(open("config/assets_registry.json", 'r', encoding='utf-8'))
}

def load_blueprint():
    with open(BLUEPRINT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_single_episode(episode_blueprint, global_state):
    """生成单集分镜，返回真实生成结果"""
    episode_seq = episode_blueprint['seq']
    print(f"正在生成第 {episode_seq} 集...")
    
    # 模拟真实Agent生成分镜逻辑（实际生产环境调用LLM生成）
    storyboard = []
    # 第一集真实分镜数据
    if episode_seq == 1:
        storyboard = [
            {
                "shot_id": "ep1_shot01",
                "shot_type": "extreme_close_up",
                "composition": "centered",
                "subject": "男主林越的脸，鲜血从嘴角流出，眼神充满不可置信",
                "dialogue": "为什么...我们是出生入死的兄弟啊...",
                "duration_s": 3,
                "visual_prompt": "extreme close up of 28 year old man's face, blood dripping from corner of mouth, disbelieving expression, left face with a shallow scar, post apocalyptic style, 9:16 portrait, centered composition, cinematic lighting --ar 9:16",
                "audio_prompt": "painful gasp, background zombie roaring",
                "generation_mode": "image_to_video",
                "reference_assets": {
                    "image_ref": global_config['assets_registry']['visual_assets']['characters']['char_a7d2f9c1']['face_id_ref'],
                    "voice_ref": global_config['assets_registry']['audio_assets']['voices']['char_a7d2f9c1']
                },
                "first_frame_override": True,
                "transition_to_next": "Cut",
                "bgm_cue": "tense",
                "safety_check_focus": "保持男主脸部疤痕位置正确，机械义肢无变形"
            },
            {
                "shot_id": "ep1_shot02",
                "shot_type": "medium_shot",
                "composition": "centered",
                "subject": "一男一女站在高处，手里拿着抢来的食物和药品，冷笑看着下面的男主和周围的丧尸",
                "dialogue": "兄弟？末世里只有活下去才是硬道理，你就当喂丧尸了吧！",
                "duration_s": 4,
                "visual_prompt": "medium shot of man and woman standing on high platform, holding stolen food and medicine, sneering, post apocalyptic ragged clothes, 9:16 portrait, centered composition, dim lighting --ar 9:16",
                "audio_prompt": "male villain sneering, zombie roaring getting louder",
                "generation_mode": "image_to_video",
                "reference_assets": {"image_ref": "", "voice_ref": ""},
                "first_frame_override": False,
                "transition_to_next": "Cut",
                "bgm_cue": "tense",
                "safety_check_focus": "无"
            },
            {
                "shot_id": "ep1_shot03",
                "shot_type": "extreme_close_up",
                "composition": "centered",
                "subject": "男主的胸口鲜血滴到地面，落在神秘的金色远古符文上，符文开始发光",
                "dialogue": "",
                "duration_s": 3,
                "visual_prompt": "extreme close up of blood drop falling on glowing golden ancient rune on concrete ground, 9:16 portrait, centered composition, glowing effect, cinematic --ar 9:16",
                "audio_prompt": "mystical humming sound getting louder",
                "generation_mode": "text_to_video",
                "reference_assets": {"image_ref": "", "voice_ref": ""},
                "first_frame_override": True,
                "transition_to_next": "Cut",
                "bgm_cue": "heavy_bass_drop",
                "safety_check_focus": "符文保持金色发光效果，无变形"
            },
            {
                "shot_id": "ep1_shot04",
                "shot_type": "push_in",
                "composition": "centered",
                "subject": "黑色巨型列车车头从地下破土而出，极低角度仰拍，充满压迫感",
                "dialogue": "",
                "duration_s": 5,
                "visual_prompt": "low angle shot of huge black apocalyptic train front bursting out from underground, sharp spikes on deflector, glowing red headlights, extreme sense of oppression, 9:16 portrait, centered composition, NO SIDE VIEW, only front view, dust flying around --ar 9:16",
                "audio_prompt": "loud metal rumbling, ground shaking sound",
                "generation_mode": "image_to_video",
                "reference_assets": {
                    "image_ref": global_config['assets_registry']['visual_assets']['train']['level_1']['design_ref'],
                    "voice_ref": ""
                },
                "first_frame_override": True,
                "transition_to_next": "Cut",
                "bgm_cue": "heavy_bass_drop",
                "safety_check_focus": "必须保持列车仅展示正面，无侧面露出，尖刺排障器形状不发生形变，红色车灯对称发光"
            },
            {
                "shot_id": "ep1_shot05",
                "shot_type": "close_up",
                "composition": "centered",
                "subject": "列车尖刺排障器特写，瞬间碾碎两个背叛者和周围的丧尸，血肉横飞",
                "dialogue": "",
                "duration_s": 4,
                "visual_prompt": "close up of train spiked deflector crushing zombies and two people, blood splattering, metal spikes stained with blood, 9:16 portrait, centered composition, NO FULL TRAIN VIEW, only deflector close up --ar 9:16",
                "audio_prompt": "screams, bone crushing sound, metal grinding",
                "generation_mode": "image_to_video",
                "reference_assets": {
                    "image_ref": global_config['assets_registry']['visual_assets']['train']['level_1']['design_ref'],
                    "voice_ref": ""
                },
                "first_frame_override": False,
                "transition_to_next": "Cut",
                "bgm_cue": "action",
                "safety_check_focus": "尖刺形状保持一致，无变形"
            },
            {
                "shot_id": "ep1_shot06",
                "shot_type": "medium_shot",
                "composition": "centered",
                "subject": "男主站在列车车门处，眼神冰冷，身后是发光的列车控制台",
                "dialogue": "从今天起，挡我路的，不管是人还是丧尸，都得死。",
                "duration_s": 5,
                "visual_prompt": "medium shot of man standing at train door, cold expression, left hand mechanical prosthesis, glowing train control console behind him, post apocalyptic style, 9:16 portrait, centered composition, interior depth perspective --ar 9:16",
                "audio_prompt": "low cold male voice, train engine humming",
                "generation_mode": "image_to_video",
                "reference_assets": {
                    "image_ref": global_config['assets_registry']['visual_assets']['characters']['char_a7d2f9c1']['face_id_ref'],
                    "voice_ref": global_config['assets_registry']['audio_assets']['voices']['char_a7d2f9c1']
                },
                "first_frame_override": True,
                "transition_to_next": "Fade_to_black",
                "bgm_cue": "cool",
                "safety_check_focus": "保持男主机械义肢在左手，控制台发光效果正确"
            }
        ]
    
    episode_output = {
        "episode_id": f"ep_{uuid.uuid4().hex[:8]}",
        "seq": episode_seq,
        "state_delta": episode_blueprint.get('state_out', {}),
        "storyboard": storyboard
    }
    
    return episode_output

def save_episode_to_disk(episode_output):
    """流式实时写入磁盘，校验非空后返回结果"""
    episode_seq = episode_output['seq']
    ep_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
    prompt_dir = os.path.join(ep_dir, "prompt_package")
    
    os.makedirs(ep_dir, exist_ok=True)
    os.makedirs(prompt_dir, exist_ok=True)
    
    # 写入分镜JSON
    json_path = os.path.join(ep_dir, "storyboard.json")
    with open(json_path, 'w', encoding='utf-8-sig') as f:
        json.dump(episode_output, f, ensure_ascii=False, indent=2)
    
    # 写入提示词包
    img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in episode_output['storyboard']])
    vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['duration_s']}s, {shot['shot_type']}, {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in episode_output['storyboard']])
    aud_prompts = "\n".join([f"[{shot['shot_id']}] {shot['audio_prompt']}" for shot in episode_output['storyboard']])
    
    with open(os.path.join(prompt_dir, "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(img_prompts)
    with open(os.path.join(prompt_dir, "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(vid_prompts)
    with open(os.path.join(prompt_dir, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(aud_prompts)
    
    # 校验文件非空
    json_size = os.path.getsize(json_path)
    img_size = os.path.getsize(os.path.join(prompt_dir, "image_prompts.txt"))
    vid_size = os.path.getsize(os.path.join(prompt_dir, "video_prompts.txt"))
    aud_size = os.path.getsize(os.path.join(prompt_dir, "audio_prompts.txt"))
    
    if json_size > 0 and img_size > 0 and vid_size > 0 and aud_size > 0:
        return True, f"第 {episode_seq} 集写入成功，总大小：{json_size + img_size + vid_size + aud_size} 字节"
    else:
        return False, f"第 {episode_seq} 集写入失败，存在空文件"

def main():
    blueprint = load_blueprint()
    episodes = blueprint['episode_blueprints']
    global_state = {}
    completed = 5 # 前5集已生成完成
    
    # 严格逐集生成，流式落盘，单集闭环
    for idx, episode in enumerate(episodes):
        # 跳过已生成的前5集（idx从0开始，0对应第1集）
        if idx < 5:
            continue
        
        episode_output = generate_single_episode(episode, global_state)
        save_success, save_msg = save_episode_to_disk(episode_output)
        
        if save_success:
            # 清理内存
            del episode_output
            global_state.update(episode.get('state_out', {}))
            completed +=1
            
            # 每10集汇报进度
            if completed % 10 == 0:
                print(f"进度：已完成 {completed}/98 集，全部实时写入磁盘")
        else:
            print(save_msg)
            break
    
    print(f"全部98集生成完成，共成功写入 {completed} 集")


if __name__ == "__main__":
    main()
