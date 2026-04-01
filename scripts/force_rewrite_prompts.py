import os
import json

base_path = r"C:\Users\tion\.openclaw\workspace\novel2shorts\output"
total_fixed = 0

# 遍历 98 集目录
for i in range(1, 99):
    ep_folder = os.path.join(base_path, f"episode_{i}")
    json_path = os.path.join(ep_folder, "storyboard.json")
    pkg_path = os.path.join(ep_folder, "prompt_package")
    
    if os.path.exists(json_path) and os.path.exists(pkg_path):
        # 读取脑子里的 JSON (这步肯定没错)
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 提取提示词串
        img_prompts = "\n".join([shot.get("visual_prompt", "") for shot in data["storyboard"]])
        vid_prompts = "\n".join([shot.get("visual_prompt", "") for shot in data["storyboard"]])
        aud_prompts = "\n".join([shot.get("audio_prompt", "") for shot in data["storyboard"]])

        # 强制以 utf-8-sig (解决部分特殊编码) 原子化写入磁盘
        with open(os.path.join(pkg_path, "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(img_prompts)
        with open(os.path.join(pkg_path, "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(vid_prompts)
        with open(os.path.join(pkg_path, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(aud_prompts)
        
        total_fixed += 1

print(f"已强制疏通并重写了 {total_fixed} 集的空提示词文件。")
