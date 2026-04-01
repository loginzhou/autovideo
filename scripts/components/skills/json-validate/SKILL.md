# Skill: json-validate
## 用途
校验LLM输出是否符合指定JSON Schema，违规自动标记重试。
## 输入参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| payload | object | 是 | 待校验的LLM输出对象 |
| schema_path | string | 是 | 对应JSON Schema文件路径（相对config目录） |
| max_retries | number | 否 | 最大重试次数，默认3 |
## 输出格式
```json
{
  "valid": "boolean",
  "errors": "array<string>",
  "retry_allowed": "boolean",
  "retry_count": "number"
}
```
## 调用示例
```json
{"payload": {"episode_id": "xxx"}, "schema_path": "storyboard_schema.json", "max_retries": 3}
```