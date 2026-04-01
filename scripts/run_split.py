import json
from components.skills.novel_split import execute_novel_split

payload = {
    "novel_path": "C:\\Users\\tion\\.openclaw\\workspace\\novel2shorts\\novel_raw.txt",
    "chunk_size_kb": 50,
    "overlap_percent": 0.05
}

result = execute_novel_split(payload)

with open("output/split_result.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("小说切块完成，总块数：{}".format(result['chunk_count']))
print("结果已保存到 output/split_result.json")
