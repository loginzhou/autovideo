import os
import json
import sys
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.LoreMaster_Agent.runner import run_lore_master
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.agents.Screenwriter_Pro_Agent.dialogue_generator import generate_dialogue_script

OUTPUT_ROOT = "output/"

def generate_episode(seq, lore_result):
    print(f"正在生成第 {seq} 集...")
    ep_blueprint = lore_result['episode_blueprints'][seq-1]
    ep_dir = os.path.join(OUTPUT_ROOT, f"episode_{seq}")
    prompt_dir = os.path.join(ep_dir, "prompt_package")
    os.makedirs(prompt_dir, exist_ok=True)
    
    # 生成剧本、分镜、对话脚本
    screenplay = run_screenwriter(ep_blueprint, lore_result)
    # 先临时生成对话脚本用于逻辑校验
    from components.agents.Screenwriter_Pro_Agent.dialogue_generator import generate_dialogue_script
    dialogue_script = generate_dialogue_script({"storyboard":[]}, lore_result)
    storyboard = run_director(screenplay, lore_result, dialogue_script)
    
    # 生成对话脚本
    dialogue_script = generate_dialogue_script(storyboard, lore_result)
    
    # 写入所有文件
    with open(os.path.join(ep_dir, "storyboard.json"), 'w', encoding='utf-8-sig') as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    with open(os.path.join(ep_dir, "dialogue_script.json"), 'w', encoding='utf-8-sig') as f:
        json.dump(dialogue_script, f, ensure_ascii=False, indent=2)
    
    # 写入提示词包
    img_prompts = "\n".join([f"[{s['shot_id']}] {s['visual_prompt']}" for s in storyboard['storyboard']])
    vid_prompts = "\n".join([f"[{s['shot_id']}] {s['video_prompt']}" for s in storyboard['storyboard']])
    aud_prompts = ""
    for d in dialogue_script:
        aud_prompts += f"[{d['shot_id']}]\n"
        aud_prompts += "[Ambience] post apocalyptic wind howling, distant zombie roaring\n"
        aud_prompts += "[SFX] generic action sound effects\n"
        aud_prompts += "[Music] BPM 120, tense dark ambient score\n"
        aud_prompts += f"[Dialogue] {d['content']} | emotion: {d['emotion']} | voice_id: {d['voice_id']} | pacing: {d['pacing']}\n\n"
    
    with open(os.path.join(prompt_dir, "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(img_prompts)
    with open(os.path.join(prompt_dir, "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(vid_prompts)
    with open(os.path.join(prompt_dir, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(aud_prompts)
    
    print(f"第 {seq} 集生成完成！")
    return True

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"开始生成前 {count} 集...")
    
    # 全局数据只加载一次
    chunks = novel_sliding_window_chunker("input/novel.txt", 0.05)
    lore_result = run_lore_master(chunks)
    
    for seq in range(1, count + 1):
        generate_episode(seq, lore_result)
    
    print(f"✅ 前 {count} 集全部生成完成！已保存到output目录")
