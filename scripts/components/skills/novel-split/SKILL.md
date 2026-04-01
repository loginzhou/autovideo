# Skill: novel-split
## 用途
将长篇中文小说物理切块，保证上下文重叠度，避免断章取义。
## 输入参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| novel_path | string | 是 | 本地小说文件路径 |
| chunk_size_kb | number | 否 | 单块大小，默认50KB |
| overlap_percent | number | 否 | 上下文重叠度，默认5% |
## 输出格式
```json
{
  "chunk_count": "number",
  "chunks": [
    {
      "chunk_id": "string(uuid)",
      "content": "string",
      "start_offset": "number",
      "end_offset": "number"
    }
  ]
}
```
## 调用示例
```json
{"novel_path": "./novel.txt", "chunk_size_kb": 50, "overlap_percent": 5}
```