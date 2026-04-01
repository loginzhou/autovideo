import os
import json

base_path = r"C:\Users\tion\.openclaw\workspace\novel2shorts\output"
# 强制创建第 1 集目录并写入
ep1_path = os.path.join(base_path, "episode_1")
os.makedirs(ep1_path, exist_ok=True)

test_data = {"status": "physical_write_test", "msg": "If you see this, the bridge is built."}
with open(os.path.join(ep1_path, "storyboard.json"), "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False)

# 验证结果
exists_result = os.path.exists(os.path.join(ep1_path, "storyboard.json"))
print(f"os.path.exists 返回结果：{exists_result}")
if exists_result:
    print("✅ 物理写入成功，桥梁已打通，现在开始全量同步98集内容到物理磁盘")
else:
    print("❌ 物理写入失败")
