import os
import uuid
import re
from config_center import config

# 章节匹配正则，支持常见的章节标题格式
CHAPTER_PATTERN = re.compile(
    r'^\s*(第[一二三四五六七八九十百千零\d]+章|Chapter\s*\d+|第\d+集|卷[一二三四五六七八九十百千零\d]+)\s*.*$', 
    re.MULTILINE
)

# 无关内容匹配正则
UNWANTED_CONTENT_PATTERN = re.compile(
    r'^\s*(作者有话说|求月票|求推荐|感谢打赏|公告|正文开始|ps：|PS：).*$',
    re.MULTILINE | re.IGNORECASE
)

def novel_sliding_window_chunker(file_path, overlap_ratio=None, chunk_size_kb=None):
    """
    智能流式文本切块，大文件不爆内存，确保段落完整性，不生硬截断对话
    优先按章节分割，自动清洗无关内容，适配长篇小说生成短剧场景
    """
    # 从配置中心读取参数，没有配置用默认值
    if overlap_ratio is None:
        overlap_ratio = config.get("novel_chunker.overlap_ratio", 0.05)
    if chunk_size_kb is None:
        chunk_size_kb = config.get("novel_chunker.chunk_size_kb", 25)
    
    chunk_size = chunk_size_kb * 1024
    overlap_size = int(chunk_size * overlap_ratio)
    buffer = ""
    chunks = []
    chunk_index = 0
    current_offset = 0
    
    print(f"小说切块参数：块大小={chunk_size_kb}KB，重叠率={overlap_ratio*100}%")
    
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
                # 优先寻找章节分隔位置
                chapter_matches = list(CHAPTER_PATTERN.finditer(buffer[:end_idx]))
                if chapter_matches:
                    # 取最后一个章节标题的位置作为分割点
                    last_chapter = chapter_matches[-1]
                    end_idx = last_chapter.start()
                else:
                    # 没有章节分隔，寻找段落/句子结尾
                    safe_end = buffer.rfind('\n', 0, end_idx)
                    if safe_end == -1:
                        safe_end = buffer.rfind('。', 0, end_idx)
                    if safe_end != -1 and safe_end > 0:
                        end_idx = safe_end + 1
                
                chunk_text = buffer[:end_idx].strip()
                if chunk_text:
                    # 清洗无关内容
                    chunk_text = UNWANTED_CONTENT_PATTERN.sub('', chunk_text).strip()
                    if not chunk_text:
                        # 清洗后为空，跳过本块
                        buffer = buffer[end_idx - overlap_size:]
                        current_offset += end_idx
                        continue
                    
                    chunks.append({
                        "chunk_id": f"chunk_{chunk_index}_{uuid.uuid4().hex[:6]}",
                        "content": chunk_text,
                        "start_offset": current_offset,
                        "end_offset": current_offset + end_idx,
                        "contains_chapter": len(chapter_matches) > 0
                    })
                    chunk_index +=1
                
                # 保留重叠部分
                buffer = buffer[end_idx - overlap_size:]
                current_offset += end_idx
    
    # 处理剩余缓冲区
    if buffer.strip():
        # 清洗无关内容
        chunk_text = UNWANTED_CONTENT_PATTERN.sub('', buffer.strip()).strip()
        if chunk_text:
            chunks.append({
                "chunk_id": f"chunk_{chunk_index}_{uuid.uuid4().hex[:6]}",
                "content": chunk_text,
                "start_offset": current_offset,
                "end_offset": current_offset + len(buffer),
                "contains_chapter": bool(CHAPTER_PATTERN.search(chunk_text))
            })
    
    # 去重相邻重复块
    if config.get("novel_chunker.deduplicate", True):
        unique_chunks = []
        last_content_hash = ""
        for chunk in chunks:
            content_hash = hash(chunk["content"][:100])
            if content_hash != last_content_hash:
                unique_chunks.append(chunk)
                last_content_hash = content_hash
        chunks = unique_chunks
        print(f"切块完成，去重后共 {len(chunks)} 个有效Chunk")
    else:
        print(f"切块完成，共 {len(chunks)} 个Chunk")
    
    return chunks
