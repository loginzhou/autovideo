import os
import json
import time
import sys
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.LoreMaster_Agent.runner import run_lore_master
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.agents.Render_Ops_Agent.runner import run_render_ops

OUTPUT_ROOT = "output/"

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法：python run_single_episode.py <集数>")
        exit(1)
    
    target_episode = int(sys.argv[1])
    
    print("="*50)
    print(f"生成第 {target_episode} 集用于定妆审批")
    print("="*50)
    
    # 自检
    check_write_permission(REQUIRED_PATHS)
    INPUT_NOVEL = "input/novel.txt"
    
    # 切块
    chunks = novel_sliding_window_chunker(INPUT_NOVEL, overlap_ratio=0.05)
    
    # 加载全局世界观
    lore_result = run_lore_master(chunks)
    
    # 找到目标集
    episode_blueprint = None
    for ep in lore_result['episode_blueprints']:
        if ep['seq'] == target_episode:
            episode_blueprint = ep
            break
    
    if not episode_blueprint:
        print(f"找不到第 {target_episode} 集配置")
        exit(1)
    
    episode_seq = episode_blueprint['seq']
    episode_output_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
    storyboard_path = os.path.join(episode_output_dir, "storyboard.json")
    
    # 幂等校验
    if os.path.exists(storyboard_path) and os.path.getsize(storyboard_path) > 0:
        print(f"第 {episode_seq} 集已存在，跳过生成")
    else:
        print(f"\n正在生成第 {episode_seq} 集...")
        # 生成剧本
        screenplay = run_screenwriter(episode_blueprint, lore_result)
        print("剧本生成完成")
        
        # 生成分镜
        storyboard = run_director(screenplay, lore_result)
        print("分镜生成完成")
        
        # 写入文件
        os.makedirs(episode_output_dir, exist_ok=True)
        os.makedirs(os.path.join(episode_output_dir, "prompt_package"), exist_ok=True)
        
        with open(storyboard_path, 'w', encoding='utf-8-sig') as f:
            json.dump(storyboard, f, ensure_ascii=False, indent=2)
        
        # 写入提示词包
        img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in storyboard['storyboard']])
        vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['shot_type']}, {shot['lighting_setup']}, {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in storyboard['storyboard']])
        aud_prompts = "\n".join([f"[{shot['shot_id']}] {shot['audio_prompt']}" for shot in storyboard['storyboard']])
        
        with open(os.path.join(episode_output_dir, "prompt_package", "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(img_prompts)
        with open(os.path.join(episode_output_dir, "prompt_package", "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(vid_prompts)
        with open(os.path.join(episode_output_dir, "prompt_package", "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(aud_prompts)
    
    # 渲染
    print("\n正在渲染第1个镜头（林越苏醒画面）用于定妆...")
    # 修改payload只渲染第一个镜头
    from components.skills.comfyui_sync_dispatcher.index import comfyui_sync_dispatcher
    first_shot = storyboard['storyboard'][0]
    
    render_payload = {
        "3": {"class_type": "KSampler", "inputs": {"seed": 8888, "steps": 5, "cfg": 1.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Juggernaut_RunDiffusionPhoto2_Lightning_4Steps.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 720, "height": 1280, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": first_shot['visual_prompt'], "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "(worst quality, low quality:1.4), deformed, bad anatomy", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": f"ep{episode_seq}_shot01_LinYue", "images": ["8", 0]}}
    }
    
    render_success, msg = comfyui_sync_dispatcher(render_payload, {})
    if render_success:
        print("第1个镜头渲染完成！请到output/episode_1/和ComfyUI output目录查看shot_1.png（林越苏醒画面），确认定妆效果")
    else:
        print(f"渲染失败：{msg}")
