import os
import json
import time
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.LoreMaster_Agent.runner import run_lore_master
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.agents.Render_Ops_Agent.runner import run_render_ops
from components.agents.Screenwriter_Pro_Agent.dialogue_generator import generate_dialogue_script

OUTPUT_ROOT = "output/"
RENDER_ENABLED = False # 暂时关闭渲染，先生成所有内容，ComfyUI启动后再打开

# ===================== 自检阶段 =====================
print("="*50)
print("全自动化短剧流水线启动自检...")
print("="*50)

# 1. 端口连通性校验（仅渲染模式需要）
if RENDER_ENABLED:
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:8188", timeout=2)
        print("ComfyUI端口8188连通正常")
    except Exception as e:
        print(f"ComfyUI端口连接失败：{str(e)}")
        exit(1)
else:
    print("渲染模式已关闭，跳过ComfyUI端口检测")

# 2. 输入源校验
INPUT_NOVEL = "input/novel.txt"
if not os.path.exists(INPUT_NOVEL):
    print(f"❌ 输入文件不存在：{INPUT_NOVEL}")
    exit(1)

file_size = os.path.getsize(INPUT_NOVEL)
if file_size == 0:
    print(f"输入文件为空：{INPUT_NOVEL}")
    exit(1)

# 检查编码
try:
    with open(INPUT_NOVEL, 'r', encoding='utf-8') as f:
        f.read(1000)
    print(f"输入源校验通过，文件大小：{file_size/1024/1024:.2f}MB，编码UTF-8")
except Exception as e:
    print(f"输入文件编码错误，不是UTF-8：{str(e)}")
    exit(1)

# 3. 路径与权限校验
try:
    check_write_permission(REQUIRED_PATHS)
    print("所有路径权限校验通过")
except Exception as e:
    print(f"路径权限校验失败：{str(e)}")
    exit(1)

print("="*50)
print("全环境自检通过，启动主流水线！")
print("="*50)

# ===================== 主流程阶段 =====================
global_state = {}

# 阶段1：小说智能切块
print("\n阶段1：小说智能切块中...")
chunks = novel_sliding_window_chunker(INPUT_NOVEL, overlap_ratio=0.05)
print(f"切块完成，共 {len(chunks)} 个Chunk")

# 阶段2：LoreMaster提取全局世界观
print("\n阶段2：全局世界观提取中...")
lore_result = run_lore_master(chunks)
with open("output/world_lore.json", 'w', encoding='utf-8-sig') as f:
    json.dump(lore_result, f, ensure_ascii=False, indent=2)
print(f"全局世界观提取完成，共识别 {len(lore_result['characters'])} 个核心角色")

# 阶段3：逐集生成+渲染
total_episodes = len(lore_result['episode_blueprints'])
print(f"\n阶段3：逐集生成+渲染启动，总集数：{total_episodes}")

for idx, episode_blueprint in enumerate(lore_result['episode_blueprints']):
    episode_seq = idx + 1
    episode_output_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
    storyboard_path = os.path.join(episode_output_dir, "storyboard.json")
    
    # Rule_3_Atomic_Idempotency 幂等性校验：文件存在且非空直接跳过
    if os.path.exists(storyboard_path) and os.path.getsize(storyboard_path) > 0:
        print(f"\n===== 第 {episode_seq}/{total_episodes} 集已存在，跳过 =====")
        continue
    
    print(f"\n===== 正在处理第 {episode_seq}/{total_episodes} 集，Chunk ID: {episode_blueprint['chunk_id']} =====")
    
    # 生成剧本
    screenplay = run_screenwriter(episode_blueprint, lore_result)
    print("剧本生成完成")
    
    # 生成分镜
    storyboard = run_director(screenplay, lore_result)
    print("分镜生成完成")
    
    # 确保输出目录存在
    os.makedirs(episode_output_dir, exist_ok=True)
    os.makedirs(os.path.join(episode_output_dir, "prompt_package"), exist_ok=True)
    
    # 写入分镜文件
    with open(storyboard_path, 'w', encoding='utf-8-sig') as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    
    # 写入提示词包
    img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in storyboard['storyboard']])
    vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['shot_type']}, {shot['lighting_setup']}, {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in storyboard['storyboard']])
    aud_prompts = "\n".join([f"[{shot['shot_id']}] {shot['audio_prompt']}" for shot in storyboard['storyboard']])
    
    with open(os.path.join(episode_output_dir, "prompt_package", "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(img_prompts)
    with open(os.path.join(episode_output_dir, "prompt_package", "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(vid_prompts)
    with open(os.path.join(episode_output_dir, "prompt_package", "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
        f.write(aud_prompts)
    
    # 渲染+资产回收（可选，ComfyUI启动后开启）
    if RENDER_ENABLED:
        render_success, asset_path = run_render_ops(storyboard)
        if render_success:
            print(f"2060显卡渲染状态：成功，资产回收：{os.path.basename(asset_path)} 入库成功")
        else:
            print(f"渲染失败：{asset_path}")
    else:
        print("分镜生成完成，渲染步骤已跳过，启动ComfyUI后可单独执行批量渲染")
    
    # 每10集汇报进度
    if episode_seq % 10 == 0:
        print(f"\n===== 进度简报：已完成 {episode_seq}/{total_episodes} 集 =====")
    
    # 清理内存
    del screenplay, storyboard
    time.sleep(1) # 给显卡散热

print("\n" + "="*50)
print("全流水线执行完成！所有内容已写入output目录")
print("="*50)
