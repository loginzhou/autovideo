import json
import uuid
from openclaw import llm_call

# 推理级模型配置（用于蓝图生成）
MODEL = "volcengine/doubao-seed-2-0-pro-260215"
PROMPT_TEMPLATE = """
你是爆款竖屏短剧制片人，根据全局剧情生成短剧蓝图，输出严格JSON格式：
1. 总集数：按照每集1.5分钟，每集必须有1个升级爽点/生存危机悬念，动态测算
2. 单集蓝图：每集包含seq(序号)、episode_id(uuid8位)、core_plot(核心剧情，100字以内)、state_in(本集前置状态)、state_out(本集结束后状态变化)、key_selling_point(本集爽点/悬念)

全局配置：
- 总大纲：{global_outline}
- 角色库：{character_library}
- 列车升级记录：{train_upgrade_log}
- 核心爽点：{core_selling_points}

输出JSON格式：
{{
  "total_episodes": "number",
  "total_runtime_min": "number",
  "episode_blueprints": "array<{{\"seq\": \"number\", \"episode_id\": \"string\", \"core_plot\": \"string\", \"state_in\": \"object\", \"state_out\": \"object\", \"key_selling_point\": \"string\"}}>"
}}
"""

def generate_blueprint(global_info: dict) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        global_outline=json.dumps(global_info['global_outline'], ensure_ascii=False),
        character_library=json.dumps(global_info['character_library'], ensure_ascii=False),
        train_upgrade_log=json.dumps(global_info['train_upgrade_log'], ensure_ascii=False),
        core_selling_points=json.dumps(global_info['core_selling_points'], ensure_ascii=False)
    )
    response = llm_call(model=MODEL, prompt=prompt, response_format="json")
    return json.loads(response)
