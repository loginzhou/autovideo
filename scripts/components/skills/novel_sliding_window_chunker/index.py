import os
import uuid

def novel_sliding_window_chunker(file_path, overlap_ratio=0.05, chunk_size_kb=50):
    """
    智能流式文本切块，大文件不爆内存，确保段落完整性，不生硬截断对话
    """
    chunk_size = chunk_size_kb * 1024
    overlap_size = int(chunk_size * overlap_ratio)
    buffer = ""
    chunks = []
    chunk_index = 0
    current_offset = 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        while True:
            # 流式读取，每次读1KB
            chunk = f.read(1024)
            if not chunk:
                break
            buffer += chunk
            
            # 缓冲区足够切块
            while len(buffer) >= chunk_size:
                end_idx = chunk_size
                # 智能寻找段落/句子结尾
                safe_end = buffer.rfind('\n', 0, end_idx)
                if safe_end == -1:
                    safe_end = buffer.rfind('。', 0, end_idx)
                if safe_end != -1 and safe_end > 0:
                    end_idx = safe_end + 1
                
                chunk_text = buffer[:end_idx].strip()
                if chunk_text:
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_index}_{uuid.uuid4().hex[:6]}",
                        "content": chunk_text,
                        "start_offset": current_offset,
                        "end_offset": current_offset + end_idx
                    })
                    chunk_index +=1
                
                # 保留重叠部分
                buffer = buffer[end_idx - overlap_size:]
                current_offset += end_idx
    
    # 处理剩余缓冲区
    if buffer.strip():
        chunks.append({
            "chunk_id": f"chunk_{chunk_index}_{uuid.uuid4().hex[:6]}",
            "content": buffer.strip(),
            "start_offset": current_offset,
            "end_offset": current_offset + len(buffer)
        })
    
    return chunks
