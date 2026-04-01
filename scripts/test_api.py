import requests
import os

API_KEY = os.getenv("DOUBAO_API_KEY", "your_api_key_here")
ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

payload = {
    "model": "deepseek-ai/DeepSeek-V3.2",
    "messages": [{"role": "user", "content": "你好，只需要回复一句话测试"}],
    "temperature": 0.7,
    "max_tokens": 100
}

try:
    print("正在测试硅基流动API连接...")
    response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=30)
    print(f"状态码：{response.status_code}")
    response.raise_for_status()
    result = response.json()
    print(f"返回消息：{result['choices'][0]['message']['content']}")
    print("✅ API连接正常！")
except Exception as e:
    print(f"❌ API调用失败：{str(e)}")
    print(f"响应内容：{response.text if 'response' in locals() else '无响应'}")
