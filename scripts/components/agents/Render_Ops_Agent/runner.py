import os
import shutil
import glob
from components.skills.comfyui_sync_dispatcher.index import comfyui_sync_dispatcher

def run_render_ops(storyboard):
    """
    Render_Ops_Agent：调度GPU渲染，自动回收资产
    """
    # 模拟渲染调用
    payload = {
        "3": {"class_type": "KSampler", "inputs": {"seed": 8888, "steps": 5, "cfg": 1.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Juggernaut_RunDiffusionPhoto2_Lightning_4Steps.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 720, "height": 1280, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "{{prompt}}", "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "(worst quality, low quality:1.4), deformed", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "ep{{seq}}_shot", "images": ["8", 0]}}
    }
    
    dynamic_vars = {
        "prompt": storyboard['storyboard'][0]['visual_prompt'],
        "seq": str(storyboard['episode_seq'])
    }
    
    success, msg = comfyui_sync_dispatcher(payload, dynamic_vars)
    
    if success:
        # 自动回收最新渲染的资产
        source_dir = r"D:\AI_Render\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output"
        target_dir = "output/assets/episodes"
        os.makedirs(target_dir, exist_ok=True)
        
        # 找最新的图片
        all_images = glob.glob(os.path.join(source_dir, "*.png"))
        if all_images:
            latest_image = max(all_images, key=os.path.getmtime)
            target_name = f"ep{storyboard['episode_seq']}_render.png"
            target_path = os.path.join(target_dir, target_name)
            shutil.copy2(latest_image, target_path)
            return True, target_path
    
    return False, msg
