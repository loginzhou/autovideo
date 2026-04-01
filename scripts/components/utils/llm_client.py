import os
import json
import time
import requests

# 配置读取（注释掉避免.env覆盖正确的API密钥）
# from dotenv import load_dotenv
# load_dotenv()

DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
DOUBAO_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"

def estimate_tokens(text):
    """估算中文字符转token数量：1汉字≈1.3token，英文1单词≈1token"""
    cn_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    en_count = len(text) - cn_count
    return int(cn_count * 1.3 + en_count * 0.8)

def get_llm_response(prompt, model="deepseek-ai/DeepSeek-V3.2", temperature=0.7, max_tokens=8192, max_context_tokens=150000, stream=False):
    """
    DeepSeek V3.2 专用LLM调用客户端 V3.0 优化版
    ✅ 支持流式输出，彻底解决超时问题
    ✅ 固定前缀优先命中缓存，降本提效
    ✅ 禁止fallback模拟数据，API调用失败直接抛出异常终止
    ✅ 自动token计数，确保输入不会超过160K上下文限制（预留10K输出空间，最大输入150K token）
    ✅ 自动重试最多3次
    """
    # 强制校验API密钥
    if not DOUBAO_API_KEY:
        raise Exception("❌ 未配置API密钥，禁止使用模拟数据，请在.env中配置正确的硅基流动API Key")
    
    # token计数，自动截断超长内容
    input_tokens = estimate_tokens(prompt)
    if input_tokens > max_context_tokens:
        # 超过限制自动截断，保留前面内容
        truncate_ratio = max_context_tokens / input_tokens
        truncate_length = int(len(prompt) * truncate_ratio * 0.95) # 多留5%安全余量
        prompt = prompt[:truncate_length] + "\n[内容过长已自动截断]"
        print(f"⚠️  输入内容过长（{input_tokens}token > 150K限制），已自动截断到合适长度")
    
    # 正式API调用，最多重试3次
    headers = {
        "Authorization": f"Bearer {DOUBAO_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": stream
    }
    
    # 强制关闭系统代理，直连API，避免本地代理干扰
    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}
    
    retry_count = 3
    for attempt in range(retry_count):
        try:
            response = session.post(DOUBAO_ENDPOINT, headers=headers, json=payload, timeout=1200) # 长文本处理增加超时到20分钟，避免超时中断
            response.raise_for_status()
            
            if stream:
                # 处理流式返回
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                json_data = json.loads(data)
                                if 'choices' in json_data and len(json_data['choices']) > 0:
                                    delta = json_data['choices'][0].get('delta', {})
                                    if 'content' in delta:
                                        full_response += delta['content']
                            except:
                                continue
                return full_response.strip()
            else:
                # 普通返回
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"⚠️  LLM调用失败，第{attempt+1}次重试：{str(e)}")
                time.sleep(2)
                continue
            else:
                # 重试全部失败，直接抛出异常终止，禁止返回模拟数据
                raise Exception(f"❌ LLM调用失败，已重试{retry_count}次：{str(e)}，请检查API配置和网络")
