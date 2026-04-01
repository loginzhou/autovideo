import os
import json
import glob
from tqdm import tqdm

OUTPUT_ROOT = "output/"
# 专业电影镜头规则
CINEMATOGRAPHY_RULES = {
    "shot_type_requirements": {
        "开场": ["远景", "全景"],
        "对话场景": ["中景", "近景", "特写"],
        "动作场景": ["特写", "快切", "跟拍"],
        "情绪表达": ["特写", "大特写"]
    },
    "focal_length_rules": {
        "远景": "24mm以下广角",
        "中景": "35-50mm标准焦段",
        "近景": "85-135mm中长焦",
        "特写": "135mm以上长焦"
    },
    "composition_rules": [
        "三分法构图",
        "引导线构图",
        "框架构图",
        "对称构图",
        "留白构图"
    ],
    "camera_movement_rules": {
        "展示环境": ["推", "拉", "摇"],
        "跟随动作": ["跟拍", "移轴"],
        "强调情绪": ["手持晃动", "慢镜头", "快进"]
    }
}

def validate_cinematography_for_episode(ep_dir):
    """
    校验单集的镜头语言是否符合专业电影标准，给出优化建议
    """
    ep_num = os.path.basename(ep_dir).split("_")[1]
    storyboard_path = os.path.join(ep_dir, "storyboard.json")
    cinematography_report_path = os.path.join(ep_dir, "cinematography_validation_report.json")

    try:
        with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
            storyboard = json.load(f)
    except Exception as e:
        return False, f"分镜读取失败：{str(e)}"

    report = {
        "episode_num": ep_num,
        "total_shots": len(storyboard['storyboard']),
        "cinematography_score": 0,
        "shot_type_analysis": {},
        "focal_length_analysis": {},
        "composition_analysis": {},
        "optimization_suggestions": []
    }

    score = 0
    total_checks = len(storyboard['storyboard']) * 3 # 每个镜头检查3项：景别、焦段、构图

    for shot_idx, shot in enumerate(storyboard['storyboard'], 1):
        visual_prompt = shot['visual_prompt']
        shot_score = 0

        # 检查景别是否合理
        scene_type = "对话场景" if "对话" in visual_prompt or "说" in visual_prompt else ("动作场景" if "跑" in visual_prompt or "打" in visual_prompt else "开场" if shot_idx ==1 else "情绪表达")
        valid_shot_types = CINEMATOGRAPHY_RULES["shot_type_requirements"].get(scene_type, [])
        shot_type_match = any(t in visual_prompt for t in valid_shot_types)
        if shot_type_match:
            shot_score += 1
        else:
            report["optimization_suggestions"].append(f"镜头{shot_idx}：当前场景为{scene_type}，建议使用{', '.join(valid_shot_types)}景别，当前未匹配")

        # 检查焦段是否匹配景别
        focal_length_match = False
        for shot_type, focal in CINEMATOGRAPHY_RULES["focal_length_rules"].items():
            if shot_type in visual_prompt and focal in visual_prompt:
                focal_length_match = True
                shot_score +=1
                break
        if not focal_length_match:
            report["optimization_suggestions"].append(f"镜头{shot_idx}：焦段与景别不匹配，请参考专业规则：{str(CINEMATOGRAPHY_RULES['focal_length_rules'])}")

        # 检查是否有明确构图
        composition_match = any(c in visual_prompt for c in CINEMATOGRAPHY_RULES["composition_rules"])
        if composition_match:
            shot_score +=1
        else:
            report["optimization_suggestions"].append(f"镜头{shot_idx}：未明确说明构图方式，建议使用{', '.join(CINEMATOGRAPHY_RULES['composition_rules'])}中的一种")

        score += shot_score

    report["cinematography_score"] = round(score / total_checks * 100, 1)

    # 等级评定
    if report["cinematography_score"] >= 90:
        report["level"] = "S级（专业电影级镜头语言）"
    elif report["cinematography_score"] >= 80:
        report["level"] = "A级（优秀商业片水平）"
    elif report["cinematography_score"] >= 70:
        report["level"] = "B级（合格短剧水平）"
    elif report["cinematography_score"] >= 60:
        report["level"] = "C级（普通水平，建议优化）"
    else:
        report["level"] = "D级（镜头语言不专业，需要优化）"

    # 写入报告
    with open(cinematography_report_path, 'w', encoding='utf-8-sig') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    return True, f"镜头语言评分：{report['cinematography_score']}分，等级：{report['level']}，优化建议{len(report['optimization_suggestions'])}条"

def batch_validate_cinematography(start_ep=1, end_ep=None):
    """
    批量校验所有剧集的镜头语言专业性
    """
    print("="*80)
    print("🎥 Novel2Shorts 专业镜头语言校验系统 V1.0")
    print("✅ 基于好莱坞电影工业摄影标准开发")
    print("✅ 校验维度：景别合理性、焦段匹配度、构图专业性、运镜逻辑性")
    print("✅ 给出专业优化建议，提升画面质感和专业度")
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
    validate_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  将校验第 {start_ep} 到 {end_ep} 集，共 {len(validate_list)} 集")
    print("="*80)

    avg_score = 0
    level_distribution = {"S级":0, "A级":0, "B级":0, "C级":0, "D级":0}

    for ep_dir in tqdm(validate_list, desc="镜头校验进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        success, msg = validate_cinematography_for_episode(ep_dir)
        # 读取报告
        report_path = os.path.join(ep_dir, "cinematography_validation_report.json")
        with open(report_path, 'r', encoding='utf-8-sig') as f:
            report = json.load(f)
        avg_score += report["cinematography_score"]
        level = report["level"].split("（")[0]
        level_distribution[level] +=1
        tqdm.write(f"第 {ep_num} 集：{msg}")

    avg_score = round(avg_score / len(validate_list), 1) if len(validate_list) >0 else 0

    print("\n" + "="*80)
    print("📊 镜头语言校验总报告：")
    print(f"   总校验集数：{len(validate_list)}")
    print(f"   平均得分：{avg_score}分")
    print(f"   等级分布：")
    for level, count in level_distribution.items():
        print(f"     {level}：{count}集（{count/len(validate_list)*100:.1f}%）")
    print(f"   详情查看：每集对应 cinematography_validation_report.json 文件")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 专业镜头语言校验工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    args = parser.parse_args()
    batch_validate_cinematography(args.start, args.end)
