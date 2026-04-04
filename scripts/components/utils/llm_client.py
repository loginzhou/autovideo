import os
import json
import time
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from .token_manager import count_tokens, optimize_context
from config_center import config

# 配置读取（注释掉避免.env覆盖正确的API密钥）
# from dotenv import load_dotenv
# load_dotenv()

# 从配置文件加载模型配置
def load_model_configs():
    """从配置文件加载模型配置"""
    # 基础配置
    model_configs = {
        "openai": {
            "api_key": "",
            "base_url": "https://api.openai.com/v1",
            "models": {
                "gpt-4o": {"context_window": 128000, "strengths": ["creative", "detailed", "multimodal"]},
                "gpt-4-turbo": {"context_window": 128000, "strengths": ["balanced", "reliable"]},
                "gpt-3.5-turbo": {"context_window": 16000, "strengths": ["fast", "cost-effective"]}
            }
        },
        "anthropic": {
            "api_key": "",
            "base_url": "https://api.anthropic.com",
            "models": {
                "claude-3-opus-20240229": {"context_window": 200000, "strengths": ["creative", "detailed", "long_context"]},
                "claude-3-sonnet-20240229": {"context_window": 200000, "strengths": ["balanced", "fast"]},
                "claude-3-haiku-20240229": {"context_window": 200000, "strengths": ["fast", "cost-effective"]}
            }
        },
        "volcengine": {
            "api_key": "",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "models": {
                "doubao-seed-2-0-pro-260215": {"context_window": 128000, "strengths": ["chinese", "creative"]},
                "doubao-pro-1-5": {"context_window": 128000, "strengths": ["chinese", "balanced"]}
            }
        },
        "zhipu": {
            "api_key": "",
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "models": {
                "glm-4": {"context_window": 128000, "strengths": ["chinese", "balanced"]},
                "glm-4-flash": {"context_window": 128000, "strengths": ["chinese", "fast"]}
            }
        },
        "qwen": {
            "api_key": "",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "models": {
                "qwen-max": {"context_window": 128000, "strengths": ["chinese", "balanced"]},
                "qwen-plus": {"context_window": 128000, "strengths": ["chinese", "fast"]}
            }
        },
        "siliconflow": {
            "api_key": "",
            "base_url": "https://api.siliconflow.cn/v1",
            "models": {
                "deepseek-ai/DeepSeek-V3.2": {"context_window": 160000, "strengths": ["coding", "technical"]},
                "meta-llama/Llama-3.1-70B-Instruct": {"context_window": 128000, "strengths": ["balanced"]}
            }
        }
    }
    
    # 从配置文件加载
    llm_config = config.get("llm", {})
    providers = llm_config.get("providers", {})
    
    # 支持扁平配置结构 (llm.provider.api_key)
    for provider in model_configs.keys():
        api_key_key = f"llm.{provider}.api_key"
        base_url_key = f"llm.{provider}.base_url"
        
        if config.get(api_key_key):
            model_configs[provider]["api_key"] = config.get(api_key_key)
        if config.get(base_url_key):
            model_configs[provider]["base_url"] = config.get(base_url_key)
    
    # 同时支持嵌套配置结构 (llm.providers.provider.api_key) - 向后兼容
    for provider, provider_config in providers.items():
        if provider in model_configs:
            if "api_key" in provider_config:
                model_configs[provider]["api_key"] = provider_config["api_key"]
            if "base_url" in provider_config:
                model_configs[provider]["base_url"] = provider_config["base_url"]
    
    # 特殊处理siliconflow，确保base_url正确设置
    if "siliconflow" in model_configs:
        if not model_configs["siliconflow"]["base_url"]:
            model_configs["siliconflow"]["base_url"] = "https://api.siliconflow.cn/v1"
    
    return model_configs

# 模型配置
MODEL_CONFIGS = load_model_configs()

# 任务类型配置
TASK_TYPES = {
    "screenplay": {
        "description": "剧本生成",
        "required_strengths": ["creative", "detailed", "chinese"],
        "recommended_models": ["gpt-4o", "claude-3-opus-20240229", "doubao-seed-2-0-pro-260215"]
    },
    "storyboard": {
        "description": "分镜生成",
        "required_strengths": ["creative", "detailed", "visual"],
        "recommended_models": ["gpt-4o", "claude-3-opus-20240229", "glm-4"]
    },
    "audio_design": {
        "description": "音频设计",
        "required_strengths": ["creative", "detailed"],
        "recommended_models": ["claude-3-opus-20240229", "gpt-4o", "doubao-seed-2-0-pro-260215"]
    },
    "semantic_analysis": {
        "description": "语义分析",
        "required_strengths": ["long_context", "detailed"],
        "recommended_models": ["claude-3-opus-20240229", "gpt-4o", "deepseek-ai/DeepSeek-V3.2"]
    },
    "episode_splitting": {
        "description": "智能分集",
        "required_strengths": ["creative", "detailed", "chinese"],
        "recommended_models": ["doubao-seed-2-0-pro-260215", "gpt-4o", "claude-3-opus-20240229"]
    }
}

def estimate_tokens(text):
    """估算中文字符转token数量：1汉字≈1.3token，英文1单词≈1token"""
    cn_count = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
    en_count = len(text) - cn_count
    return int(cn_count * 1.3 + en_count * 0.8)

def get_available_models():
    """获取可用的模型列表"""
    available_models = []
    for provider, config in MODEL_CONFIGS.items():
        if config["api_key"]:
            for model_name in config["models"]:
                available_models.append(f"{provider}/{model_name}")
    return available_models

def get_available_providers():
    """获取有API密钥的可用提供商列表"""
    available_providers = []
    for provider, cfg in MODEL_CONFIGS.items():
        if cfg["api_key"]:
            available_providers.append(provider)
    return available_providers

def select_model(task_type):
    """根据任务类型选择最优模型，智能回退到有API密钥的提供商"""
    # 获取所有可用的提供商
    available_providers = get_available_providers()
    
    if not available_providers:
        raise Exception("未配置任何可用的模型API密钥，请先在WebUI中配置至少一个提供商的API密钥")
    
    # 首先检查任务类型特定配置
    task_configs = config.get("llm.task_configs", {})
    if task_type and task_type in task_configs:
        task_config = task_configs[task_type]
        provider = task_config.get("provider")
        model = task_config.get("model")
        if provider and model:
            # 检查该提供商是否有API密钥
            if provider in available_providers:
                return f"{provider}/{model}"
            else:
                # 任务配置的提供商没有API密钥，尝试使用默认提供商
                print(f"⚠️  任务'{task_type}'配置的提供商'{provider}'没有API密钥，将尝试使用其他可用提供商")
    
    # 获取配置的默认提供商
    default_provider = config.get("llm.default_provider", "siliconflow")
    default_model = config.get(f"llm.{default_provider}.model", "")
    
    # 检查默认提供商是否有API密钥
    if default_provider in available_providers and default_model:
        return f"{default_provider}/{default_model}"
    
    # 默认提供商不可用，尝试使用第一个可用的提供商
    if available_providers:
        fallback_provider = available_providers[0]
        # 获取该提供商的第一个模型
        fallback_model = list(MODEL_CONFIGS[fallback_provider]["models"].keys())[0]
        print(f"⚠️  默认提供商不可用，使用回退提供商: {fallback_provider}/{fallback_model}")
        return f"{fallback_provider}/{fallback_model}"
    
    # 根据任务类型选择模型
    if task_type in TASK_TYPES:
        recommended_models = TASK_TYPES[task_type]["recommended_models"]
        required_strengths = TASK_TYPES[task_type]["required_strengths"]
        
        # 检查推荐模型是否可用
        for model_name in recommended_models:
            for provider in available_providers:
                if model_name in MODEL_CONFIGS[provider]["models"]:
                    model_info = MODEL_CONFIGS[provider]["models"][model_name]
                    # 检查模型是否满足所有必需的能力
                    if all(strength in model_info["strengths"] for strength in required_strengths):
                        return f"{provider}/{model_name}"
    
    # 最终回退：使用第一个可用提供商的第一个模型
    fallback_provider = available_providers[0]
    fallback_model = list(MODEL_CONFIGS[fallback_provider]["models"].keys())[0]
    return f"{fallback_provider}/{fallback_model}"

# 模型调用缓存
@lru_cache(maxsize=1000)
def cached_llm_response(prompt, model, temperature, max_tokens, max_context_tokens, response_format=None):
    """缓存的模型调用"""
    # 这里不包含task_type和stream参数，因为它们不影响缓存
    return _get_llm_response(prompt, model=model, temperature=temperature, max_tokens=max_tokens, max_context_tokens=max_context_tokens, stream=False, response_format=response_format)

# 批量处理线程池
executor = ThreadPoolExecutor(max_workers=5)

def get_llm_response(prompt, model=None, task_type=None, temperature=0.7, max_tokens=8192, max_context_tokens=150000, stream=False, response_format=None):
    """
    多模型协同LLM调用客户端 V4.0
    支持多个模型提供商，根据任务类型自动选择最优模型
    支持流式输出，彻底解决超时问题
    固定前缀优先命中缓存，降本提效
    禁止fallback模拟数据，API调用失败直接抛出异常终止
    自动token计数，确保输入不会超过上下文限制
    自动重试最多3次
    生成参数限制，确保生成内容质量
    模型调用缓存，提高性能
    批量处理，并行执行多个模型调用
    """
    # 生成参数限制
    if temperature < 0 or temperature > 1:
        temperature = 0.7
        print("⚠️  温度参数超出范围，已自动调整为0.7")
    
    if max_tokens < 1 or max_tokens > 32768:
        max_tokens = 8192
        print("⚠️  最大token数超出范围，已自动调整为8192")
    
    if max_context_tokens < 1 or max_context_tokens > 200000:
        max_context_tokens = 150000
        print("⚠️  最大上下文token数超出范围，已自动调整为150000")
    
    # 选择模型
    if not model:
        model = select_model(task_type)
    
    # 非流式输出使用缓存
    if not stream:
        try:
            return cached_llm_response(prompt, model, temperature, max_tokens, max_context_tokens, response_format)
        except Exception as e:
            print(f"缓存调用失败，使用普通调用并支持重试：{str(e)}")
            # 添加重试机制
            import time
            max_retries = 2
            for retry in range(max_retries + 1):
                try:
                    return _get_llm_response(prompt, model=model, task_type=task_type, temperature=temperature, max_tokens=max_tokens, max_context_tokens=max_context_tokens, stream=stream, response_format=response_format)
                except Exception as retry_e:
                    if retry < max_retries:
                        wait_time = 2 ** retry  # 指数退避：1秒、2秒、4秒
                        print(f"第{retry+1}次重试失败，{wait_time}秒后重试：{str(retry_e)}")
                        time.sleep(wait_time)
                    else:
                        print(f"已重试{max_retries}次，最终失败")
                        raise
    else:
        return _get_llm_response(prompt, model=model, task_type=task_type, temperature=temperature, max_tokens=max_tokens, max_context_tokens=max_context_tokens, stream=stream, response_format=response_format)

def batch_llm_response(prompts, model=None, task_type=None, temperature=0.7, max_tokens=8192, max_context_tokens=150000, response_format=None):
    """
    批量处理模型调用
    """
    futures = []
    for prompt in prompts:
        future = executor.submit(get_llm_response, prompt, model, task_type, temperature, max_tokens, max_context_tokens, False, response_format)
        futures.append(future)
    
    # 等待所有任务完成
    results = []
    for future in futures:
        try:
            results.append(future.result())
        except Exception as e:
            results.append(f"错误: {str(e)}")
    
    return results

def _get_llm_response(prompt, model=None, task_type=None, temperature=0.7, max_tokens=8192, max_context_tokens=150000, stream=False, response_format=None):
    """
    实际的模型调用函数
    """
    # 选择模型
    if not model:
        model = select_model(task_type)
    
    # 解析模型名称
    if "/" in model:
        parts = model.split("/")
        if len(parts) >= 2:
            potential_provider = parts[0]
            # 如果第一个部分是已知provider，使用它，否则默认为siliconflow
            if potential_provider in MODEL_CONFIGS:
                provider = potential_provider
                model_name = "/".join(parts[1:])
            else:
                # 第一个部分不是provider，假设是siliconflow的模型
                provider = "siliconflow"
                model_name = model
        else:
            provider = "siliconflow"
            model_name = model
    else:
        provider = "siliconflow"
        model_name = model
    
    # 检查模型配置
    if provider not in MODEL_CONFIGS:
        raise Exception(f"不支持的模型提供商：{provider}")
    
    provider_config = MODEL_CONFIGS[provider]
    if not provider_config["api_key"]:
        raise Exception(f"未配置{provider}的API密钥")
    
    if model_name not in provider_config["models"]:
        raise Exception(f"不支持的模型：{model_name}")
    
    # 优化上下文，减少token消耗
    prompt = optimize_context(prompt)
    
    # token计数，自动截断超长内容
    input_tokens = estimate_tokens(prompt)
    model_context_window = provider_config["models"][model_name]["context_window"]
    actual_max_context = min(max_context_tokens, model_context_window - 10000) # 预留10K输出空间
    
    if input_tokens > actual_max_context:
        # 超过限制自动截断，保留前面内容
        truncate_ratio = actual_max_context / input_tokens
        truncate_length = int(len(prompt) * truncate_ratio * 0.95) # 多留5%安全余量
        prompt = prompt[:truncate_length] + "\n[内容过长已自动截断]"
        print(f"⚠️  输入内容过长（{input_tokens}token > {actual_max_context}限制），已自动截断到合适长度")
    
    # 构建API请求
    headers = {
        "Authorization": f"Bearer {provider_config['api_key']}",
        "Content-Type": "application/json"
    }
    
    # 根据提供商构建payload
    if provider == "anthropic":
        # Anthropic API格式
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        endpoint = f"{provider_config['base_url']}/messages"
    else:
        # OpenAI兼容格式
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        endpoint = f"{provider_config['base_url']}/chat/completions"
    
    # 强制关闭系统代理，直连API，避免本地代理干扰
    session = requests.Session()
    session.trust_env = False
    session.proxies = {"http": None, "https": None}
    
    retry_count = 3
    for attempt in range(retry_count):
        try:
            # 根据官方文档，stream模式下requests也需要设置stream=True
            response = session.post(endpoint, headers=headers, json=payload, timeout=300, stream=stream)
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
                output_tokens = estimate_tokens(full_response)
                count_tokens(module_name="llm_call", prompt_tokens=input_tokens, completion_tokens=output_tokens, model=model)
                return full_response.strip()
            else:
                # 普通返回
                result = response.json()
                if provider == "anthropic":
                    output_content = result['content'][0]['text'].strip()
                else:
                    output_content = result['choices'][0]['message']['content'].strip()
                output_tokens = estimate_tokens(output_content)
                count_tokens(module_name="llm_call", prompt_tokens=input_tokens, completion_tokens=output_tokens, model=model)
                return output_content
            
        except Exception as e:
            if attempt < retry_count - 1:
                print(f"⚠️  LLM调用失败，第{attempt+1}次重试：{str(e)}")
                time.sleep(2)
                continue
            else:
                # 重试全部失败，直接抛出异常终止，禁止返回模拟数据
                raise Exception(f"LLM调用失败，已重试{retry_count}次：{str(e)}，请检查API配置和网络")
