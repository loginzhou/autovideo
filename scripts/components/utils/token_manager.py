"""
Token 管理与节省系统
全局统计token消耗，自动优化上下文，降低API成本
"""
import os
import json
from typing import Optional, Dict, Any

# 全局token计数器
global_token_usage = {
    "total_prompt_tokens": 0,
    "total_completion_tokens": 0,
    "total_cost": 0,
    "per_module": {}
}

# 模型计费配置（单位：元/千token）
MODEL_PRICING = {
    "doubao-seed-2-0-pro": {"prompt": 0.008, "completion": 0.02},
    "doubao-light": {"prompt": 0.001, "completion": 0.002},
    "deepseek-v3": {"prompt": 0.001, "completion": 0.002}
}

def count_tokens(module_name: str, prompt_tokens: int, completion_tokens: int, model: str = "doubao-seed-2-0-pro"):
    """统计token消耗"""
    global global_token_usage
    
    # 累计全局消耗
    global_token_usage["total_prompt_tokens"] += prompt_tokens
    global_token_usage["total_completion_tokens"] += completion_tokens
    
    # 计算成本
    price = MODEL_PRICING.get(model, {"prompt": 0.01, "completion": 0.02})
    cost = (prompt_tokens / 1000 * price["prompt"]) + (completion_tokens / 1000 * price["completion"])
    global_token_usage["total_cost"] += cost
    
    # 按模块统计
    if module_name not in global_token_usage["per_module"]:
        global_token_usage["per_module"][module_name] = {"prompt": 0, "completion": 0, "cost": 0}
    global_token_usage["per_module"][module_name]["prompt"] += prompt_tokens
    global_token_usage["per_module"][module_name]["completion"] += completion_tokens
    global_token_usage["per_module"][module_name]["cost"] += cost
    
    # 打印消耗
    print(f"模块[{module_name}]消耗：prompt={prompt_tokens}，completion={completion_tokens}，本环节成本：¥{cost:.4f}")
    print(f"累计总消耗：prompt={global_token_usage['total_prompt_tokens']}，completion={global_token_usage['total_completion_tokens']}，总成本：¥{global_token_usage['total_cost']:.4f}")

def optimize_context(context: Any, max_length: int = 8000) -> Any:
    """优化上下文，截断冗余内容，减少token消耗"""
    if isinstance(context, str):
        # 字符串截断
        if len(context) > max_length * 2: # 粗略估计1token≈2个汉字
            return context[:int(max_length * 1.8)] + "\n[内容已截断，仅保留核心信息]"
        return context
    elif isinstance(context, dict):
        # 字典精简，只保留必要字段
        optimized = {}
        for k, v in context.items():
            if k in ["core_plot", "characters", "genre", "summary", "main_characters", "seq"]:
                optimized[k] = optimize_context(v, max_length=int(max_length/2))
        return optimized
    elif isinstance(context, list):
        # 列表截断
        if len(context) > 20:
            return context[:20]
        return [optimize_context(item, max_length=int(max_length/len(context))) for item in context]
    return context

def save_token_usage(output_path: str = "output/analysis/token_usage.json"):
    """保存token消耗统计"""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(global_token_usage, f, ensure_ascii=False, indent=2)
    print(f"Token消耗统计已保存到：{output_path}，总成本：¥{global_token_usage['total_cost']:.4f}")
