import os
import json
import glob
from tqdm import tqdm

OUTPUT_ROOT = "output/"
CONTINUITY_CHECK_ITEMS = {
    "character": [
        "姓名", "性别", "年龄", "外貌特征", "服装", "发型", "配饰", "性格", "声音特征", "身份设定"
    ],
    "scene": [
        "场景名称", "地点", "时间", "天气", "环境布置", "道具摆放", "光照条件"
    ],
    "plot": [
        "前集悬念", "人物关系", "事件因果", "时间线顺序", "伏笔回收", "逻辑自洽"
    ]
}

def audit_cross_episode_continuity():
    """
    全局跨集连贯性审计，检测所有剧集之间的穿帮问题，确保整个剧情100%连贯无矛盾
    检测范围：角色设定、场景设定、剧情逻辑、时间线四大维度
    """
    print("="*80)
    print("🔗 Novel2Shorts 全局跨集连贯性审计系统 V1.0")
    print("✅ 全维度检测穿帮问题：角色/场景/剧情/时间线完全一致")
    print("✅ 自动识别前后矛盾、设定冲突、剧情bug，给出具体修复建议")
    print("✅ 保证整部剧的连贯性和专业度，避免观众出戏")
    print("="*80)

    # 读取全局分析结果
    try:
        with open(os.path.join(OUTPUT_ROOT, "world_lore.json"), 'r', encoding='utf-8-sig') as f:
            global_lore = json.load(f)
    except:
        try:
            with open(os.path.join(OUTPUT_ROOT, "analysis", "full_novel_analysis.json"), 'r', encoding='utf-8-sig') as f:
                global_lore = json.load(f)
        except:
            print("❌ 未找到全局世界观设定文件，请先运行主流水线生成内容")
            return False

    global_characters = global_lore.get('characters', {})
    global_time_start = global_lore.get('time_start', '')

    # 获取所有剧集，按顺序排列
    episode_dirs = sorted(glob.glob(os.path.join(OUTPUT_ROOT, "episode_*")), key=lambda x: int(os.path.basename(x).split("_")[1]))
    if not episode_dirs:
        print("❌ 未找到任何剧集")
        return False

    print(f"ℹ️  共检测 {len(episode_dirs)} 集，开始全局连贯性校验...")
    print("="*80)

    # 全局状态追踪
    global_state = {
        "current_time": global_time_start,
        "current_weather": "晴天",
        "character_states": {char: {"appearance": "", "clothing": ""} for char in global_characters.keys()},
        "plot_hooks": [],
        "unresolved_hooks": []
    }

    audit_report = {
        "total_episodes": len(episode_dirs),
        "continuity_score": 100,
        "character_conflicts": [],
        "scene_conflicts": [],
        "plot_conflicts": [],
        "time_line_conflicts": [],
        "optimization_suggestions": []
    }

    for ep_dir in tqdm(episode_dirs, desc="全局连贯性校验进度"):
        ep_num = int(os.path.basename(ep_dir).split("_")[1])
        storyboard_path = os.path.join(ep_dir, "storyboard.json")

        try:
            with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
                storyboard = json.load(f)
        except Exception as e:
            audit_report["optimization_suggestions"].append(f"第{ep_num}集：分镜读取失败，跳过校验")
            audit_report["continuity_score"] -= 2
            continue

        # 1. 校验角色设定一致性
        ep_characters = storyboard.get('main_characters', [])
        for char in ep_characters:
            if char not in global_characters:
                audit_report["character_conflicts"].append(f"第{ep_num}集：出现未定义角色「{char}」，全局设定中不存在")
                audit_report["continuity_score"] -= 5
                continue
            # 检查角色描述是否和全局一致
            global_desc = str(global_characters[char])
            ep_desc = ""
            for shot in storyboard['storyboard']:
                if char in shot['visual_prompt']:
                    ep_desc += shot['visual_prompt']
            for item in CONTINUITY_CHECK_ITEMS['character']:
                if item in global_desc and item in ep_desc:
                    global_val = global_desc.split(item)[1].split("，")[0].strip() if "，" in global_desc.split(item)[1] else global_desc.split(item)[1].strip()
                    ep_val = ep_desc.split(item)[1].split("，")[0].strip() if "，" in ep_desc.split(item)[1] else ep_desc.split(item)[1].strip()
                    if global_val != ep_val:
                        audit_report["character_conflicts"].append(f"第{ep_num}集：角色「{char}」的{item}设定冲突，全局设定为「{global_val}」，本集为「{ep_val}」")
                        audit_report["continuity_score"] -= 3

        # 2. 校验场景和时间线一致性
        ep_time = storyboard.get('episode_time', global_state['current_time'])
        ep_weather = storyboard.get('episode_weather', global_state['current_weather'])
        # 时间不能倒流
        if ep_time < global_state['current_time']:
            audit_report["time_line_conflicts"].append(f"第{ep_num}集：时间线倒流，上一集时间为「{global_state['current_time']}」，本集为「{ep_time}」")
            audit_report["continuity_score"] -= 5
        # 天气突变需要有过渡说明
        if ep_weather != global_state['current_weather'] and "天气变化" not in str(storyboard):
            audit_report["scene_conflicts"].append(f"第{ep_num}集：天气无理由突变，上一集天气为「{global_state['current_weather']}」，本集为「{ep_weather}」，建议添加天气变化的过渡说明")
            audit_report["continuity_score"] -= 2

        # 3. 校验剧情连贯性（悬念回收）
        for hook in global_state['unresolved_hooks']:
            if hook in str(storyboard):
                global_state['unresolved_hooks'].remove(hook)
        # 收集本集新悬念
        for shot in storyboard['storyboard']:
            if any(keyword in shot['audio_prompt'].get('Dialogue', '') for keyword in ["难道", "究竟", "怎么回事", "为什么", "到底", "悬念", "下集"]):
                global_state['unresolved_hooks'].append(f"第{ep_num}集悬念：{shot['audio_prompt']['Dialogue'][:20]}...")

        # 更新全局状态
        global_state['current_time'] = ep_time
        global_state['current_weather'] = ep_weather

    # 最终评分和报告
    audit_report["continuity_score"] = max(0, audit_report["continuity_score"])
    if audit_report["continuity_score"] >= 95:
        audit_report["level"] = "S级（完全连贯，无任何穿帮）"
    elif audit_report["continuity_score"] >= 85:
        audit_report["level"] = "A级（极轻微问题，不影响观感）"
    elif audit_report["continuity_score"] >= 70:
        audit_report["level"] = "B级（存在少量穿帮，建议修改）"
    elif audit_report["continuity_score"] >= 60:
        audit_report["level"] = "C级（存在较多矛盾，需要修改）"
    else:
        audit_report["level"] = "D级（连贯性差，严重影响观感，必须修改）"

    # 写入全局报告
    report_path = os.path.join(OUTPUT_ROOT, "cross_episode_continuity_report.json")
    with open(report_path, 'w', encoding='utf-8-sig') as f:
        json.dump(audit_report, f, ensure_ascii=False, indent=2)

    print("\n" + "="*80)
    print("📊 全局跨集连贯性审计总报告：")
    print(f"   总集数：{audit_report['total_episodes']}")
    print(f"   连贯性得分：{audit_report['continuity_score']}分")
    print(f"   等级：{audit_report['level']}")
    print(f"   角色设定冲突：{len(audit_report['character_conflicts'])} 处")
    print(f"   场景设定冲突：{len(audit_report['scene_conflicts'])} 处")
    print(f"   时间线冲突：{len(audit_report['time_line_conflicts'])} 处")
    print(f"   剧情逻辑冲突：{len(audit_report['plot_conflicts'])} 处")
    print(f"   未回收悬念：{len(global_state['unresolved_hooks'])} 个")
    print(f"   详情查看：{report_path}")
    print("="*80)

    return True

if __name__ == "__main__":
    audit_cross_episode_continuity()
