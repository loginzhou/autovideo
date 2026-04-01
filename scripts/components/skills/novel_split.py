import os
import json
import uuid

def execute_novel_split(payload: dict) -> dict:
    """
    Skill: novel-split 小说物理切块
    输入参数解析自 payload JSON，支持任何小说的动态传入。
    """
    novel_path = payload.get("novel_path")
    chunk_size_kb = payload.get("chunk_size_kb", 50) # 默认 50KB 约等于 1.5 万个中文字符
    overlap_percent = payload.get("overlap_percent", 0.05) # 默认 5% 重叠度
    
    if not os.path.exists(novel_path):
        return {"error": f"找不到小说文件: {novel_path}"}
    
    # 计算目标字符数 (1KB 粗略计为 300 个中文字符)
    target_char_count = chunk_size_kb * 300
    overlap_char_count = int(target_char_count * overlap_percent)
    
    chunks_output = []
    
    with open(novel_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total_length = len(content)
    current_idx = 0
    
    while current_idx < total_length:
        # 计算当前块的结束位置
        end_idx = min(current_idx + target_char_count, total_length)
        
        # 为了不把一句话切断，向后寻找最近的段落换行符或句号
        if end_idx < total_length:
            safe_end = content.rfind('\n', current_idx, end_idx)
            if safe_end == -1:
                safe_end = content.rfind('。', current_idx, end_idx)
            if safe_end != -1 and safe_end > current_idx:
                end_idx = safe_end + 1
        
        chunk_text = content[current_idx:end_idx].strip()
        
        if chunk_text:
            chunks_output.append({
                "chunk_id": f"chk_{uuid.uuid4().hex[:8]}",
                "content": chunk_text,
                "start_offset": current_idx,
                "end_offset": end_idx
            })
        
        # 移动游标，减去 overlap 保证剧情连贯
        current_idx = end_idx - overlap_char_count
        
        # 防止死循环
        if overlap_char_count >= (end_idx - current_idx):
            current_idx = end_idx

    return {
        "chunk_count": len(chunks_output),
        "chunks": chunks_output
    }

# 本地测试代码 (仅用于验证，实际由 OpenClaw 调用)
if __name__ == "__main__":
    # 您可以把任何小说的路径传进来测试
    test_payload = {
        "novel_path": "../../data_input/test_novel.txt", 
        "chunk_size_kb": 20,
        "overlap_percent": 0.05
    }
    # 假设创建一个空文件用于测试
    os.makedirs("../../data_input", exist_ok=True)
    with open("../../data_input/test_novel.txt", "w", encoding="utf-8") as f:
        f.write("这里是测试小说的内容。" * 1000)
    
    result = execute_novel_split(test_payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
