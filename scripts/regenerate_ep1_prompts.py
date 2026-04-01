import os
import json
from components.agents.LoreMaster_Agent.runner import run_lore_master
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker

# 加载全局数据
chunks = novel_sliding_window_chunker("input/novel.txt", 0.05)
lore_result = run_lore_master(chunks)
ep_blueprint = lore_result['episode_blueprints'][0]
screenplay = run_screenwriter(ep_blueprint, lore_result)
storyboard = run_director(screenplay, lore_result)

# 覆盖原有文件
output_dir = "output/episode_1/"
prompt_dir = os.path.join(output_dir, "prompt_package")
os.makedirs(prompt_dir, exist_ok=True)

# 写入新分镜
with open(os.path.join(output_dir, "storyboard.json"), 'w', encoding='utf-8-sig') as f:
    json.dump(storyboard, f, ensure_ascii=False, indent=2)

# 写入新提示词包
img_prompts = "\n".join([f"[{s['shot_id']}] {s['visual_prompt']}" for s in storyboard['storyboard']])
vid_prompts = "\n".join([f"[{s['shot_id']}] motion_intensity: {s['video_prompt'].split('motion_intensity: ')[1].split(',')[0]}, {s['video_prompt']}" for s in storyboard['storyboard']])
aud_prompts = ""
for s in storyboard['storyboard']:
    aud = s['audio_prompt']
    aud_prompts += f"[{s['shot_id']}]\n[Ambience] {aud['Ambience']}\n[SFX] {aud['SFX']}\n[Music] {aud['Music']}\n[Dialogue] {aud['Dialogue']}\n\n"

with open(os.path.join(prompt_dir, "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
    f.write(img_prompts)
with open(os.path.join(prompt_dir, "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
    f.write(vid_prompts)
with open(os.path.join(prompt_dir, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
    f.write(aud_prompts)

print("第1集V2版提示词已覆盖完成！")
