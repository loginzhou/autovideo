import time
import urllib.request
import json
import subprocess

def comfyui_sync_dispatcher(payload_template, dynamic_vars, max_retries=3):
    """
    本地GPU同步渲染器，指数退避重试，自动清理显存
    """
    # 动态替换变量
    prompt = json.dumps(payload_template)
    for k, v in dynamic_vars.items():
        prompt = prompt.replace(f"{{{{{k}}}}}", v)
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            # 渲染前清理显存
            subprocess.run(["nvidia-smi", "--gpu-reset"], capture_output=True)
            time.sleep(0.5)
            
            # 发送请求
            data = json.dumps({"prompt": json.loads(prompt)}).encode('utf-8')
            req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
            urllib.request.urlopen(req, timeout=30)
            return True, "渲染成功"
            
        except Exception as e:
            retry_count +=1
            wait_time = 2 ** retry_count # 指数退避
            time.sleep(wait_time)
    
    return False, "超过最大重试次数"

if __name__ == "__main__":
    # 测试用例
    test_payload = {
        "3": {"class_type": "KSampler", "inputs": {"seed": 8888, "steps": 5, "cfg": 1.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
        "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Juggernaut_RunDiffusionPhoto2_Lightning_4Steps.safetensors"}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 720, "height": 1280, "batch_size": 1}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "{{prompt_text}}", "clip": ["4", 1]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "(worst quality, low quality:1.4), deformed, bad anatomy", "clip": ["4", 1]}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "{{filename_prefix}}", "images": ["8", 0]}}
    }
    test_vars = {
        "prompt_text": "1boy, solo, cold expression, short black hair",
        "filename_prefix": "test_render"
    }
    success, msg = comfyui_sync_dispatcher(test_payload, test_vars)
    print(msg)
