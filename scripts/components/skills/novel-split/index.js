const fs = require('fs');

async function main(input) {
  const { novel_path, chunk_size_kb = 50, overlap_percent = 5 } = input;
  const chunk_size = chunk_size_kb * 1024;
  const overlap_size = Math.floor(chunk_size * (overlap_percent / 100));
  
  const content = fs.readFileSync(novel_path, 'utf8');
  const total_length = content.length;
  const chunks = [];
  
  let offset = 0;
  let chunkIndex = 0;
  while (offset < total_length) {
    const end = Math.min(offset + chunk_size, total_length);
    const chunk_content = content.slice(offset, end);
    chunks.push({
      chunk_id: `chunk_${chunkIndex}`,
      content: chunk_content,
      start_offset: offset,
      end_offset: end
    });
    chunkIndex++;
    offset = end - overlap_size;
    if (offset < 0) offset = 0;
  }
  
  return {
    chunk_count: chunks.length,
    chunks: chunks
  };
}

// 从标准输入读取参数，运行后输出结果到标准输出
if (require.main === module) {
  const input = JSON.parse(fs.readFileSync(0, 'utf8'));
  main(input).then(result => {
    console.log(JSON.stringify(result, null, 2));
    process.exit(0);
  }).catch(err => {
    console.error(JSON.stringify({error: err.message}, null, 2));
    process.exit(1);
  });
}

module.exports = main;
