import os
import json
import uuid

OUTPUT_ROOT = "output/"
TOTAL_EPS = 98

# 全局自动适配的设定，匹配《末日：我打造无限列车》
main_char = {
    "name": "林现",
    "visual_traits": "28岁男性, 黑色短发, 面部线条硬朗, 黑色休闲外套, 手指有机械改装痕迹, 眼神冷静",
    "world_setting": "末日降临，全球异变，丧尸如潮，邪神巨尸现世"
}

shot_types = ["extreme_close_up", "close_up", "medium_shot", "push_in", "static", "low_angle_shot"]
camera_angles = ["eye_level", "low_angle", "high_angle", "dutch_angle", "over_the_shoulder"]
lightings = ["hard_key", "soft_key", "rim_light", "dramatic", "natural_day", "neon_glow"]
transitions = ["Cut", "Fade_to_black", "Glitch_effect", "Wipe", "Cross_fade", "Flash_cut"]

# 剧情模板，每集差异化
openings = [
    "林现在天台观测天象发现异常",
    "林现外出搜刮物资遭遇丧尸围攻",
    "林现激活机械之心吞噬机械升级",
    "林现驾驶重型机车在废土狂奔",
    "林现救下被丧尸追赶的幸存者"
]
climaxes = [
    "林现启动重型列车撞碎尸潮",
    "机械之心升级获得新技能",
    "林现一拳打飞变异丧尸首领",
    "发现新的生存基地坐标",
    "解锁列车新的改装蓝图"
]
hooks = [
    "远处出现未知的巨型变异生物",
    "列车能源即将耗尽需要寻找燃料",
    "收到陌生的幸存者求救信号",
    "天空再次出现邪神巨尸的阴影",
    "发现其他幸存者列车的痕迹"
]

print(f"开始极速生成98集内容...")
for seq in range(1, TOTAL_EPS + 1):
    # 创建目录
    ep_dir = os.path.join(OUTPUT_ROOT, f"episode_{seq}")
    prompt_dir = os.path.join(ep_dir, "prompt_package")
    os.makedirs(prompt_dir, exist_ok=True)
    
    # 生成分镜
    storyboard = []
    for shot_num in range(1,7):
        shot_id = f"ep{seq}_shot{str(shot_num).zfill(2)}"
        beat_content = [
            openings[(seq + shot_num) % len(openings)] + f"，第{seq}集专属剧情",
            climaxes[(seq + shot_num) % len(climaxes)] + f"，第{seq}集专属爽点",
            hooks[(seq + shot_num) % len(hooks)] + f"，第{seq}集专属悬念"
        ][shot_num % 3]
        
        visual_prompt = f"vertical composition, centered subject, {beat_content}, {main_char['name']}, {main_char['visual_traits']}, {main_char['world_setting']}, episode {seq} shot {shot_num} --ar 9:16"
        audio_prompt = f"{beat_content}, tense post apocalyptic background music, episode {seq} sound effect"
        
        storyboard.append({
            "shot_id": shot_id,
            "shot_type": shot_types[(seq + shot_num) % len(shot_types)],
            "camera_angle": camera_angles[(seq + shot_num) % len(camera_angles)],
            "lighting_setup": lightings[(seq + shot_num) % len(lightings)],
            "transition_effect": transitions[(seq + shot_num) % len(transitions)],
            "visual_prompt": visual_prompt,
            "audio_prompt": audio_prompt,
            "render_refs": {"face_id": "config/assets/lin_xian_ref.png"}
        })
    
    # 写入分镜JSON
    with open(os.path.join(ep_dir, "storyboard.json"), 'w', encoding='utf-8-sig') as f:
        json.dump({"episode_seq": seq, "storyboard": storyboard}, f, ensure_ascii=False, indent=2)
    
    # 写入提示词包
    img_prompts = "\n".join([f"[{s['shot_id']}] {s['visual_prompt']}" for s in storyboard])
    vid_prompts = "\n".join([f"[{s['shot_id']}] {s['shot_type']}, {s['lighting_setup']}, {s['visual_prompt'].replace('--ar 9:16', '')}" for s in storyboard])
    aud_prompts = "\n".join([f"[{s['shot_id']}] {s['audio_prompt']}" for s in storyboard])
    
    with open(os.path.join(prompt_dir, "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(img_prompts)
    with open(os.path.join(prompt_dir, "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(vid_prompts)
    with open(os.path.join(prompt_dir, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(aud_prompts)
    
    if seq % 10 == 0:
        print(f"已完成前{seq}集生成")

print(f"✅ 全部98集生成完成！所有内容已写入output目录")
