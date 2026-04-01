import os
import glob
import shutil

# 源目录配置
SOURCE_DIR = r"D:\AI_Render\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output"
# 目标目录配置
TARGET_DIR = r"C:\Users\tion\.openclaw\workspace\novel2shorts\config\assets"
TARGET_FILENAME = "lin_yue_ref.png"

# 1. 找到最新生成的图片
image_extensions = ['*.png', '*.jpg', '*.jpeg']
all_images = []
for ext in image_extensions:
    all_images.extend(glob.glob(os.path.join(SOURCE_DIR, ext)))

if not all_images:
    print("未找到任何图片文件")
    exit(1)

# 按修改时间排序，取最新的
latest_image = max(all_images, key=os.path.getmtime)
print(f"找到最新图片：{os.path.basename(latest_image)}，修改时间：{os.path.getmtime(latest_image)}")

# 2. 确保目标目录存在
os.makedirs(TARGET_DIR, exist_ok=True)

# 3. 移动并重命名
target_path = os.path.join(TARGET_DIR, TARGET_FILENAME)
shutil.copy2(latest_image, target_path)

# 4. 校验结果
if os.path.exists(target_path):
    file_size = os.path.getsize(target_path) / 1024
    print(f"✅ 图片已成功入库！大小：{file_size:.2f}KB，路径：{target_path}")
else:
    print("❌ 图片移动失败")
