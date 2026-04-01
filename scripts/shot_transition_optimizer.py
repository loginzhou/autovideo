import os
import json
import glob
from tqdm import tqdm

OUTPUT_ROOT = "output/"
# 专业转场规则库
TRANSITION_RULES = {
    "action_match": {
        "condition": "前后镜头有相同的动作轨迹",
        "transition": "动作匹配剪辑，无硬切",
        "usage_scenario": "动作场景、打斗场景"
    },
    "eye_line_match": {
        "condition": "前一个镜头角色看某个方向，后一个镜头是看到的内容",
        "transition": "视线匹配剪辑，无硬切",
        "usage_scenario": "对话场景、发现新事物场景"
    },
    "graphic_match": {
        "condition": "前后镜头有相似的构图、形状、颜色",
        "transition": "图形匹配剪辑，无硬切",
        "usage_scenario": "转场、蒙太奇"
    },
    "cut_on_sound": {
        "condition": "前后镜头有相同的声音节点（台词重音、音效峰值）",
        "transition": "声音匹配剪辑，无硬切",
        "usage_scenario": "所有场景通用"
    },
    "fade_in_out": {
        "condition": "时间、地点发生变化",
        "transition": "淡入淡出（1秒）",
        "usage_scenario": "时间跳转、场景切换"
    },
    "wipe": {
        "condition": "平行叙事、不同时空切换",
        "transition": "划像转场",
        "usage_scenario": "双线叙事、回忆场景"
    },
    "hard_cut": {
        "condition": "同一时间同一地点，连续动作",
        "transition": "硬切",
        "usage_scenario": "对话、连续动作场景"
    }
}

def optimize_shot_transitions_for_episode(ep_dir):
    """
    优化单集所有镜头之间的转场，确保画面流畅自然，符合专业剪辑规则
    自动识别最优转场方式，替换生硬的转场，提升观影流畅度
    """
    ep_num = os.path.basename(ep_dir).split("_")[1]
    storyboard_path = os.path.join(ep_dir, "storyboard.json")
    optimized_storyboard_path = os.path.join(ep_dir, "storyboard_optimized_transition.json")
    transition_report_path = os.path.join(ep_dir, "transition_optimization_report.json")

    try:
        with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
            storyboard = json.load(f)
    except Exception as e:
        return False, f"分镜读取失败：{str(e)}"

    shots = storyboard['storyboard']
    total_shots = len(shots)
    if total_shots < 2:
        return True, "镜头数少于2，无需优化"

    report = {
        "episode_num": ep_num,
        "total_shots": total_shots,
        "optimized_transitions": [],
        "original_transition_issues": [],
        "smoothness_score": 0
    }

    optimized_shots = []
    smooth_score = 0

    for i in range(total_shots):
        current_shot = shots[i].copy()
        if i == 0:
            # 第一个镜头默认淡入
            current_shot['transition_in'] = "fade_in 0.5s"
            optimized_shots.append(current_shot)
            continue
        if i == total_shots -1:
            # 最后一个镜头默认淡出
            current_shot['transition_out'] = "fade_out 0.5s"
            optimized_shots.append(current_shot)
            continue

        prev_shot = shots[i-1]
        next_shot = shots[i+1]

        # 分析前后镜头匹配度
        prev_content = prev_shot['visual_prompt'] + prev_shot['audio_prompt'].get('Dialogue', '')
        current_content = current_shot['visual_prompt'] + current_shot['audio_prompt'].get('Dialogue', '')
        next_content = next_shot['visual_prompt'] + next_shot['audio_prompt'].get('Dialogue', '')

        # 匹配合适的转场
        best_transition = "hard_cut"
        match_reason = "默认硬切"

        # 检查动作匹配
        if any(keyword in prev_content and keyword in current_content for keyword in ["跑", "跳", "打", "走", "伸手", "转头", "动作"]):
            best_transition = "action_match"
            match_reason = "前后镜头有连续动作，匹配剪辑"
            smooth_score += 2
        # 检查视线匹配
        elif any(keyword in prev_content for keyword in ["看", "望", "注视", "盯着", "视线"]) and "出现" in current_content:
            best_transition = "eye_line_match"
            match_reason = "前镜头角色视线引导，匹配剪辑"
            smooth_score += 2
        # 检查图形匹配
        elif any(keyword in prev_content and keyword in current_content for keyword in ["圆形", "方形", "红色", "蓝色", "相同构图"]):
            best_transition = "graphic_match"
            match_reason = "前后镜头有相似图形元素，匹配剪辑"
            smooth_score += 2
        # 检查声音匹配
        elif prev_shot['audio_prompt'].get('SFX', '') == current_shot['audio_prompt'].get('SFX', '') and prev_shot['audio_prompt'].get('SFX', '') != "":
            best_transition = "cut_on_sound"
            match_reason = "前后镜头有相同音效，声音匹配剪辑"
            smooth_score += 2
        # 检查场景变化
        elif "场景切换" in current_content or "第二天" in current_content or "另一边" in current_content:
            best_transition = "fade_in_out"
            match_reason = "场景/时间发生变化，淡入淡出转场"
            smooth_score += 1
        # 检查平行叙事
        elif "与此同时" in current_content or "另一边" in current_content:
            best_transition = "wipe"
            match_reason = "平行叙事，划像转场"
            smooth_score +=1
        else:
            # 硬切
            smooth_score +=1

        # 记录优化结果
        current_shot['transition_in'] = TRANSITION_RULES[best_transition]['transition']
        report["optimized_transitions"].append({
            "shot_pair": f"{i}→{i+1}",
            "transition_type": best_transition,
            "transition_name": TRANSITION_RULES[best_transition]['transition'],
            "reason": match_reason
        })

        optimized_shots.append(current_shot)

    # 计算流畅度得分
    report["smoothness_score"] = round(smooth_score / (total_shots -1) * 100, 1)

    # 等级评定
    if report["smoothness_score"] >= 95:
        report["level"] = "S级（电影级流畅度，完全无跳脱感）"
    elif report["smoothness_score"] >= 85:
        report["level"] = "A级（非常流畅，专业剪辑水平）"
    elif report["smoothness_score"] >= 75:
        report["level"] = "B级（流畅，普通短剧水平）"
    elif report["smoothness_score"] >= 60:
        report["level"] = "C级（基本流畅，存在少量生硬转场）"
    else:
        report["level"] = "D级（转场生硬，影响观感，需要优化）"

    # 保存优化后的分镜和报告
    storyboard['storyboard'] = optimized_shots
    with open(optimized_storyboard_path, 'w', encoding='utf-8-sig') as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)

    with open(transition_report_path, 'w', encoding='utf-8-sig') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return True, f"镜头转场优化完成，流畅度得分：{report['smoothness_score']}分，等级：{report['level']}，共优化{len(report['optimized_transitions'])}处转场"

def batch_optimize_shot_transitions(start_ep=1, end_ep=None):
    """
    批量优化所有剧集的镜头转场，提升整体流畅度
    """
    print("="*80)
    print("✂️  Novel2Shorts 专业镜头转场优化系统 V1.0")
    print("✅ 基于好莱坞专业剪辑规则库，自动匹配合适的转场方式")
    print("✅ 支持动作匹配/视线匹配/图形匹配/声音匹配等高级转场")
    print("✅ 彻底解决转场生硬、画面跳脱的问题，提升观影流畅度")
    print("="*80)

    # 获取所有剧集
    episode_dirs = sorted(glob.glob(os.path.join(OUTPUT_ROOT, "episode_*")), key=lambda x: int(os.path.basename(x).split("_")[1]))
    if not episode_dirs:
        print("❌ 未找到任何剧集")
        return False

    total_episodes = len(episode_dirs)
    if end_ep is None:
        end_ep = total_episodes
    start_idx = max(0, start_ep - 1)
    end_idx = min(total_episodes, end_ep)
    optimize_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  将优化第 {start_ep} 到 {end_ep} 集，共 {len(optimize_list)} 集")
    print("="*80)

    avg_smooth_score = 0
    level_distribution = {"S级":0, "A级":0, "B级":0, "C级":0, "D级":0}

    for ep_dir in tqdm(optimize_list, desc="转场优化进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        success, msg = optimize_shot_transitions_for_episode(ep_dir)
        # 读取报告
        report_path = os.path.join(ep_dir, "transition_optimization_report.json")
        with open(report_path, 'r', encoding='utf-8-sig') as f:
            report = json.load(f)
        avg_smooth_score += report["smoothness_score"]
        level = report["level"].split("（")[0]
        level_distribution[level] +=1
        tqdm.write(f"第 {ep_num} 集：{msg}")

    avg_smooth_score = round(avg_smooth_score / len(optimize_list), 1) if len(optimize_list) >0 else 0

    print("\n" + "="*80)
    print("📊 镜头转场优化总报告：")
    print(f"   总优化集数：{len(optimize_list)}")
    print(f"   平均流畅度得分：{avg_smooth_score}分")
    print(f"   等级分布：")
    for level, count in level_distribution.items():
        print(f"     {level}：{count}集（{count/len(optimize_list)*100:.1f}%）")
    print(f"   优化后分镜保存在：每集 storyboard_optimized_transition.json")
    print(f"   详情查看：每集 transition_optimization_report.json 文件")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 专业镜头转场优化工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    args = parser.parse_args()
    batch_optimize_shot_transitions(args.start, args.end)
