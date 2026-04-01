"""
多后端生图调度器
支持本地ComfyUI、第三方生图API自动切换，自动降级重试，降低成本提升稳定性
"""
import os
import json
import requests
import time
from typing import Optional, Dict, List

# 生图后端配置
IMAGE_BACKENDS = [
    # 优先级从高到低，优先用成本最低的本地模型
    {
        "name": "comfyui_local",
        "type": "comfyui",
        "endpoint": os.getenv("COMFYUI_ENDPOINT", "http://127.0.0.1:8188"),
        "enabled": True,
        "retry": 3,
        "timeout": 60
    },
    {
        "name": "siliconflow_api",
        "type": "api",
        "endpoint": "https://api.siliconflow.cn/v1/image/generations",
        "api_key": os.getenv("SILICONFLOW_API_KEY", ""),
        "model": "stabilityai/stable-diffusion-xl-base-1.0",
        "enabled": bool(os.getenv("SILICONFLOW_API_KEY", "")),
        "retry": 2,
        "timeout": 30
    }
]

class ImageGenerator:
    def __init__(self):
        self.active_backend = None
        self._select_best_backend()
    
    def _select_best_backend(self):
        """选择最优可用的生图后端，优先本地模型成本最低"""
        for backend in IMAGE_BACKENDS:
            if not backend["enabled"]:
                continue
            # 检查后端连通性
            try:
                if backend["type"] == "comfyui":
                    requests.get(f"{backend['endpoint']}/system_stats", timeout=2)
                elif backend["type"] == "api":
                    if not backend["api_key"]:
                        continue
                self.active_backend = backend
                print(f"✅ 选择生图后端：{backend['name']}")
                return
            except Exception as e:
                print(f"ℹ️  生图后端{backend['name']}不可用：{str(e)}")
                continue
        raise Exception("❌ 所有生图后端都不可用，请检查配置")
    
    def generate(self, prompt: str, negative_prompt: str = "", width: int = 720, height: int = 1280, **kwargs) -> str:
        """生成图片，自动重试和降级"""
        if not self.active_backend:
            self._select_best_backend()
        
        for retry in range(self.active_backend["retry"]):
            try:
                if self.active_backend["type"] == "comfyui":
                    return self._generate_comfyui(prompt, negative_prompt, width, height, **kwargs)
                elif self.active_backend["type"] == "api":
                    return self._generate_api(prompt, negative_prompt, width, height, **kwargs)
            except Exception as e:
                print(f"⚠️  生图失败（第{retry+1}次重试）：{str(e)}")
                time.sleep(2)
                if retry == self.active_backend["retry"] - 1:
                    # 降级到下一个后端
                    print(f"🔄 后端{self.active_backend['name']}多次失败，尝试降级")
                    current_index = next(i for i, b in enumerate(IMAGE_BACKENDS) if b["name"] == self.active_backend["name"])
                    if current_index < len(IMAGE_BACKENDS) - 1:
                        self.active_backend = IMAGE_BACKENDS[current_index + 1]
                        return self.generate(prompt, negative_prompt, width, height, **kwargs)
                    raise Exception(f"❌ 所有后端都失败，生图失败：{str(e)}")
    
    def _generate_comfyui(self, prompt: str, negative_prompt: str, width: int, height: int, **kwargs) -> str:
        """调用本地ComfyUI生成图片"""
        # 这里可以接入你现有的ComfyUI工作流调用逻辑
        # 示例代码，根据你的实际工作流调整
        workflow = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "steps": 20,
            "cfg_scale": 7
        }
        response = requests.post(
            f"{self.active_backend['endpoint']}/prompt",
            json={"prompt": workflow},
            timeout=self.active_backend["timeout"]
        )
        response.raise_for_status()
        # 等待生成完成并获取图片URL，这里省略轮询逻辑，可以根据你的现有代码补全
        return "generated_image_path.png"
    
    def _generate_api(self, prompt: str, negative_prompt: str, width: int, height: int, **kwargs) -> str:
        """调用第三方API生成图片"""
        headers = {
            "Authorization": f"Bearer {self.active_backend['api_key']}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.active_backend["model"],
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "width": width,
            "height": height,
            "num_inference_steps": 20,
            "guidance_scale": 7,
            "num_images": 1
        }
        response = requests.post(
            self.active_backend["endpoint"],
            headers=headers,
            json=payload,
            timeout=self.active_backend["timeout"]
        )
        response.raise_for_status()
        result = response.json()
        return result["data"][0]["url"]

# 全局单例
image_generator = ImageGenerator()
