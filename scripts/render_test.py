import urllib.request
import json

prompt_text = """
{
 "3": {"class_type": "KSampler", "inputs": {"seed": 8888, "steps": 5, "cfg": 1.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1, "model": ["4", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0]}},
 "4": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "Juggernaut_RunDiffusionPhoto2_Lightning_4Steps.safetensors"}},
 "5": {"class_type": "EmptyLatentImage", "inputs": {"width": 720, "height": 1280, "batch_size": 1}},
 "6": {"class_type": "CLIPTextEncode", "inputs": {"text": "(Masterpiece, best quality:1.2), 1boy, solo, 28 years old man, Lin Yue, cold expression, short black hair, shallow scar on left cheek, wearing black distressed tactical windbreaker, carbon fiber shoulder pads, post-apocalyptic wasteland background", "clip": ["4", 1]}},
 "7": {"class_type": "CLIPTextEncode", "inputs": {"text": "(worst quality, low quality:1.4), deformed, bad anatomy, bad hands, missing fingers, mutated, blurry", "clip": ["4", 1]}},
 "8": {"class_type": "VAEDecode", "inputs": {"samples": ["3", 0], "vae": ["4", 2]}},
 "9": {"class_type": "SaveImage", "inputs": {"filename_prefix": "LinYue_Anchor", "images": ["8", 0]}}
}
"""
p = {"prompt": json.loads(prompt_text)}
data = json.dumps(p).encode('utf-8')
req = urllib.request.Request("http://127.0.0.1:8188/prompt", data=data)
urllib.request.urlopen(req)
print("API 请求已发送！ComfyUI 正在后台静默渲染...")
