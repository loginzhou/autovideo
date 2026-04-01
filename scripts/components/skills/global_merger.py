import json
from openclaw import llm_call

# 推理级模型配置（用于Reduce阶段全局汇总）
MODEL = "volcengine/doubao-seed-2-0-pro-260215"
PROMPT_TEMPLATE = """
你是短剧全局架构师，处理所有小说片段的提取结果，输出严格JSON格式：
1. global_outline：全局剧情大纲，分幕，核心冲突，关键转折点
2. character_library：去重后的角色库，每个角色包含char_id(随机uuid8位)、name、visual_traits(竖屏生图专用关键词，如废土防风镜、机械义肢等)、initial_state
3. train_upgrade_log：无敌列车所有升级阶段，包含阶段名称、外观特征、功能升级
4. core_selling_points：短剧核心爽点/悬念点列表

所有提取结果汇总：
{all_map_results}

输出JSON格式：
{{
  "global_outline": "array<{{\"act\": \"number\", \"title\": \"string\", \"summary\": \"string\"}}>",
  "character_library": "array<{{\"char_id\": \"string\", \"name\": \"string\", \"visual_traits\": \"array<string>\", \"initial_state\": \"string\"}}>",
  "train_upgrade_log": "array<{{\"stage\": \"number\", \"name\": \"string\", \"visual_features\": \"array<string>\", \"upgrade_content\": \"string\"}}>",
  "core_selling_points": "array<string>"
}}
"""

def merge_global_info(all_map_results: list) -> dict:
    prompt = PROMPT_TEMPLATE.format(all_map_results=json.dumps(all_map_results, ensure_ascii=False))
    response = llm_call(model=MODEL, prompt=prompt, response_format="json")
    return json.loads(response)
