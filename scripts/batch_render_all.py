import os
import json
import glob
import time
from components.agents.Render_Ops_Agent.runner import run_render_ops
from tqdm import tqdm

OUTPUT_ROOT = "output/"
RENDER_INTERVAL = 2 # 每集渲染间隔，防止GPU过热

def batch_render_all_episodes(start_ep=1, end_ep=None):
    """
    批量渲染所有已生成分镜的剧集
    """
    print("="*80)
    print("🎬 Novel2Shorts 批量渲染引擎 V1.0")
    print("✅ 支持断点续渲、自动去重、GPU负载保护")
    print("="*80)

    # 获取所有已生成分镜的剧集
    episode_dirs = sorted(glob.glob(os.path.join(OUTPUT_ROOT, "episode_*")), key=lambda x: int(os.path.basename(x).split("_")[1]))
    if not episode_dirs:
        print("❌ 未找到任何已生成的剧集分镜，请先运行主流水线生成内容")
        return False

    total_episodes = len(episode_dirs)
    if end_ep is None:
        end_ep = total_episodes
    start_idx = max(0, start_ep - 1)
    end_idx = min(total_episodes, end_ep)
    render_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  找到 {total_episodes} 集，将渲染第 {start_ep} 到 {end_ep} 集，共 {len(render_list)} 集")
    print("="*80)

    success_count = 0
    fail_count = 0
    skip_count = 0

    for ep_dir in tqdm(render_list, desc="渲染进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        storyboard_path = os.path.join(ep_dir, "storyboard.json")
        render_mark_path = os.path.join(ep_dir, "render_success.mark")

        # 幂等性校验：已渲染成功的跳过
        if os.path.exists(render_mark_path):
            skip_count +=1
            tqdm.write(f"⏭️  第 {ep_num} 集已渲染成功，跳过")
            continue

        # 读取分镜
        try:
            with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
                storyboard = json.load(f)
        except Exception as e:
            fail_count +=1
            tqdm.write(f"❌ 第 {ep_num} 集分镜读取失败：{str(e)}")
            continue

        tqdm.write(f"\n🎨 正在渲染第 {ep_num} 集...")
        success, msg = run_render_ops(storyboard)

        if success:
            success_count +=1
            # 标记渲染成功
            with open(render_mark_path, 'w', encoding='utf-8') as f:
                f.write(f"渲染成功：{time.strftime('%Y-%m-%d %H:%M:%S')}\n输出路径：{msg}")
            tqdm.write(f"✅ 第 {ep_num} 集渲染成功：{os.path.basename(msg)}")
        else:
            fail_count +=1
            tqdm.write(f"❌ 第 {ep_num} 集渲染失败：{msg}")

        # GPU散热等待
        time.sleep(RENDER_INTERVAL)

    print("\n" + "="*80)
    print("📊 批量渲染完成统计：")
    print(f"   总任务数：{len(render_list)}")
    print(f"   渲染成功：{success_count} 集")
    print(f"   渲染失败：{fail_count} 集")
    print(f"   跳过已渲染：{skip_count} 集")
    print(f"   成功率：{success_count/(len(render_list)-skip_count)*100:.1f}%" if (len(render_list)-skip_count) >0 else "   无新渲染任务")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 批量渲染工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    args = parser.parse_args()
    batch_render_all_episodes(args.start, args.end)
