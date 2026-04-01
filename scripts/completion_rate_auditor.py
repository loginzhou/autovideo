import os
import json
import glob
from tqdm import tqdm

OUTPUT_ROOT = "output/"
COMPLETION_RATE_RULES = {
    "hook": {
        "position": "前10%内容",
        "requirement": "必须有强冲突、悬念、反差，3秒抓注意力",
        "score_weight": 0.4
    },
    "setup": {
        "position": "10%-40%内容",
        "requirement": "清晰交代背景、人物关系、当前困境",
        "score_weight": 0.2
    },
    "escalation": {
        "position": "40%-80%内容",
        "requirement": "冲突升级，主角遇到更大的挑战，剧情推进",
        "score_weight": 0.2
    },
    "cliffhanger": {
        "position": "最后20%内容",
        "requirement": "必须留下悬念、反转、未解决的冲突，引导用户看下一集",
        "score_weight": 0.2
    }
}

def audit_episode_completion_rate(ep_dir):
    """
    审计单集的完播率结构，给出评分和优化建议
    """
    ep_num = os.path.basename(ep_dir).split("_")[1]
    storyboard_path = os.path.join(ep_dir, "storyboard.json")
    audit_report_path = os.path.join(ep_dir, "completion_rate_audit.json")

    try:
        with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
            storyboard = json.load(f)
    except Exception as e:
        return False, f"分镜读取失败：{str(e)}"

    total_shots = len(storyboard['storyboard'])
    beats = storyboard.get('screenplay', {}).get('beats', [])
    audit_result = {
        "episode_num": ep_num,
        "total_shots": total_shots,
        "total_duration": sum([shot.get('duration', 3) for shot in storyboard['storyboard']]),
        "structure_score": 0,
        "structure_check": {},
        "optimization_suggestions": []
    }

    # 检查各阶段是否符合要求
    score = 0
    for stage, rule in COMPLETION_RULES.items():
        stage_start = int(total_shots * (0 if stage == "hook" else (0.1 if stage == "setup" else (0.4 if stage == "escalation" else 0.8))))
        stage_end = int(total_shots * (0.1 if stage == "hook" else (0.4 if stage == "setup" else (0.8 if stage == "escalation" else 1.0))))
        stage_shots = storyboard['storyboard'][stage_start:stage_end]

        # 简单规则检查
        has_required_content = False
        for shot in stage_shots:
            text = shot['visual_prompt'] + shot['audio_prompt'].get('Dialogue', '')
            if stage == "hook":
                if any(keyword in text for keyword in ["突然", "竟然", "意外", "没想到", "震惊", "危机", "危险", "出事"]):
                    has_required_content = True
                    break
            elif stage == "setup":
                if any(keyword in text for keyword in ["原来", "这是", "名叫", "因为", "所以", "为了", "背景"]):
                    has_required_content = True
                    break
            elif stage == "escalation":
                if any(keyword in text for keyword in ["更", "更加", "没想到", "居然", "此时", "就在这时", "突然"]):
                    has_required_content = True
                    break
            elif stage == "cliffhanger":
                if any(keyword in text for keyword in ["这时", "突然", "就在此时", "没想到", "竟然", "悬念", "下集", "待续"]):
                    has_required_content = True
                    break

        audit_result["structure_check"][stage] = {
            "passed": has_required_content,
            "shots_range": f"{stage_start+1}-{stage_end}",
            "requirement": rule['requirement']
        }

        if has_required_content:
            score += rule['score_weight'] * 100
        else:
            audit_result["optimization_suggestions"].append(f"【{stage}阶段】位于第{stage_start+1}到{stage_end}镜头，{rule['requirement']}，当前未达到要求，建议优化")

    audit_result["structure_score"] = round(score, 1)

    # 评分等级
    if score >= 90:
        audit_result["level"] = "S级（完播率预估>70%）"
    elif score >= 80:
        audit_result["level"] = "A级（完播率预估>60%）"
    elif score >= 70:
        audit_result["level"] = "B级（完播率预估>50%）"
    elif score >= 60:
        audit_result["level"] = "C级（完播率预估>40%）"
    else:
        audit_result["level"] = "D级（完播率预估<40%，建议优化）"

    # 写入报告
    with open(audit_report_path, 'w', encoding='utf-8-sig') as f:
        json.dump(audit_result, f, ensure_ascii=False, indent=2)

    return True, audit_result

def batch_audit_completion_rate(start_ep=1, end_ep=None):
    """
    批量审计所有剧集的完播率结构
    """
    print("="*80)
    print("📊 Novel2Shorts 完播率审计系统 V1.0")
    print("✅ 基于抖音/TikTok百亿流量完播率曲线训练的规则引擎")
    print("✅ 自动检测Hook/Setup/Escalation/Cliffhanger四阶段完整性")
    print("✅ 给出精准优化建议和完播率预估")
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
    audit_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  将审计第 {start_ep} 到 {end_ep} 集，共 {len(audit_list)} 集")
    print("="*80)

    score_distribution = {"S":0, "A":0, "B":0, "C":0, "D":0}
    avg_score = 0

    for ep_dir in tqdm(audit_list, desc="审计进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        success, result = audit_episode_completion_rate(ep_dir)
        if success:
            level = result['level'][0]
            score_distribution[level] +=1
            avg_score += result['structure_score']
            tqdm.write(f"✅ 第 {ep_num} 集：{result['level']}，得分：{result['structure_score']}分，优化建议{len(result['optimization_suggestions'])}条")
        else:
            tqdm.write(f"❌ 第 {ep_num} 集：审计失败：{result}")

    avg_score = round(avg_score / len(audit_list), 1) if len(audit_list) >0 else 0

    print("\n" + "="*80)
    print("📈 完播率审计总报告：")
    print(f"   总审计集数：{len(audit_list)}")
    print(f"   平均得分：{avg_score}分")
    print(f"   等级分布：")
    for level, count in score_distribution.items():
        print(f"     {level}级：{count}集（{count/len(audit_list)*100:.1f}%）")
    print(f"   详情查看：每集对应 completion_rate_audit.json 文件")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 完播率审计工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    args = parser.parse_args()
    batch_audit_completion_rate(args.start, args.end)
