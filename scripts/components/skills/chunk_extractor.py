import json
from openclaw import llm_call

# 轻量级模型配置（仅用于Map阶段摘要提取）
MODEL = "volcengine/doubao-seed-2-0-lite-260215"
PROMPT_TEMPLATE = """
你是短剧提取助手，处理小说片段，输出严格JSON格式，不要额外内容：
1. 摘要：当前片段核心剧情，不超过300字
2. 角色：片段中出现的角色，包含姓名、当前状态、视觉特征（穿搭/外貌/道具，适合AI生图的关键词）
3. 列车升级：当前片段中无敌列车的升级内容/外观变化，没有则为空字符串

小说片段：
{chunk_content}

输出JSON格式：
{{
  "summary": "string",
  "characters": [{{"name": "string", "state": "string", "visual_traits": "array<string>"}}],
  "train_upgrade": "string"
}}
"""

def extract_chunk_info(chunk_content: str) -> dict:
    prompt = PROMPT_TEMPLATE.format(chunk_content=chunk_content[:2000]) # 截断避免Token超限
    response = llm_call(model=MODEL, prompt=prompt, response_format="json")
    return json.loads(response)
