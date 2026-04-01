import os
import json
from components.agents.LoreMaster_Agent.runner import run_lore_master
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.Screenwriter_Pro_Agent.dialogue_generator import generate_dialogue_script

# 加载全局数据
chunks = novel_sliding_window_chunker("input/novel.txt", 0.05)
lore_result = run_lore_master(chunks)

# 加载已有的第1集分镜
with open("output/episode_1/storyboard.json", 'r', encoding='utf-8-sig') as f:
    storyboard = json.load(f)

# 生成对话脚本
dialogue_script = generate_dialogue_script(storyboard, lore_result)

# 保存dialogue_script.json
output_dir = "output/episode_1/"
with open(os.path.join(output_dir, "dialogue_script.json"), 'w', encoding='utf-8-sig') as f:
    json.dump(dialogue_script, f, ensure_ascii=False, indent=2)

# 更新音频提示词，指向对话脚本内容
prompt_dir = os.path.join(output_dir, "prompt_package")
aud_prompts = ""
for d in dialogue_script:
    aud_prompts += f"[{d['shot_id']}]\n"
    aud_prompts += "[Ambience] post apocalyptic wind howling, distant zombie roaring\n"
    aud_prompts += "[SFX] telescope adjusting sound, helicopter rotor noise\n"
    aud_prompts += "[Music] BPM 120, tense dark ambient score\n"
    aud_prompts += f"[Dialogue] {d['content']} | emotion: {d['emotion']} | voice_id: {d['voice_id']} | pacing: {d['pacing']}\n\n"

with open(os.path.join(prompt_dir, "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
    f.write(aud_prompts)

print("第1集对话脚本生成完成！")
