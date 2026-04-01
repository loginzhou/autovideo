const fs = require('fs');
const splitResult = JSON.parse(fs.readFileSync('./output/split_result.json', 'utf8'));
console.log(`✅ 小说切块完成，总块数：${splitResult.chunk_count}`);
console.log(`📦 第一块ID：${splitResult.chunks[0].chunk_id}，大小：${splitResult.chunks[0].content.length} 字符`);
