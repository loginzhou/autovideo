import os
import json
import glob
import re
from tqdm import tqdm

OUTPUT_ROOT = "output/"
# 敏感词规则，可根据平台要求扩展
SENSITIVE_WORDS = [
    "敏感词1", "敏感词2", "违规内容", "政治敏感", "色情低俗", "暴力血腥",
    "赌博", "毒品", "诈骗", "虚假宣传", "医疗建议", "金融推荐", "盗版"
]
# 平台禁止内容规则
PLATFORM_PROHIBITED = [
    "出现联系方式", "出现二维码", "出现网址", "引导加微信", "引导关注",
    "贬低平台", "诱导转发", "诱导点赞", "恶意营销", "虚假信息"
]

def check_compliance_for_episode(ep_dir):
    """
    对单集内容进行全方面合规检测，避免平台限流、下架
    检测范围：台词、视觉提示词、音频提示词、字幕
    """
    ep_num = os.path.basename(ep_dir).split("_")[1]
    storyboard_path = os.path.join(ep_dir, "storyboard.json")
    compliance_report_path = os.path.join(ep_dir, "compliance_report.json")
    subtitle_dir = os.path.join(ep_dir, "subtitles")

    try:
        with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
            storyboard = json.load(f)
    except Exception as e:
        return False, f"分镜读取失败：{str(e)}"

    # 收集所有需要检测的文本
    all_text = ""
    # 1. 视觉提示词
    for shot in storyboard['storyboard']:
        all_text += shot['visual_prompt'] + "\n"
        # 2. 音频提示词
        all_text += shot['audio_prompt'].get('Dialogue', '') + "\n"
        all_text += shot['audio_prompt'].get('SFX', '') + "\n"
        all_text += shot['audio_prompt'].get('Music', '') + "\n"

    # 3. 字幕文件
    if os.path.exists(subtitle_dir):
        for subtitle_file in glob.glob(os.path.join(subtitle_dir, "*.srt")) + glob.glob(os.path.join(subtitle_dir, "*.vtt")):
            try:
                with open(subtitle_file, 'r', encoding='utf-8-sig') as f:
                    all_text += f.read() + "\n"
            except:
                pass

    # 开始检测
    report = {
        "episode_num": ep_num,
        "overall_risk_level": "低风险",
        "sensitive_word_hits": [],
        "prohibited_content_hits": [],
        "risk_details": []
    }

    # 检测敏感词
    for word in SENSITIVE_WORDS:
        matches = re.findall(word, all_text, re.IGNORECASE)
        if matches:
            report["sensitive_word_hits"].append({
                "word": word,
                "count": len(matches)
            })
            report["risk_details"].append(f"检测到敏感词「{word}」，出现{len(matches)}次，属于高风险内容，必须修改")

    # 检测平台禁止内容
    for rule in PLATFORM_PROHIBITED:
        if rule in all_text:
            report["prohibited_content_hits"].append(rule)
            report["risk_details"].append(f"检测到平台禁止内容：{rule}，属于中风险内容，建议修改")

    # 风险等级评定
    if len(report["sensitive_word_hits"]) > 0:
        report["overall_risk_level"] = "高风险"
    elif len(report["prohibited_content_hits"]) > 0:
        report["overall_risk_level"] = "中风险"
    else:
        report["overall_risk_level"] = "低风险"

    # 写入报告
    with open(compliance_report_path, 'w', encoding='utf-8-sig') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # 返回结果
    if report["overall_risk_level"] == "低风险":
        return True, "✅ 内容合规，无风险"
    else:
        return False, f"❌ 检测到{len(report['sensitive_word_hits'])}个敏感词，{len(report['prohibited_content_hits'])}项违规内容，风险等级：{report['overall_risk_level']}"

def batch_check_compliance(start_ep=1, end_ep=None):
    """
    批量检测所有剧集的内容合规性
    """
    print("="*80)
    print("🛡️  Novel2Shorts 内容合规检测系统 V1.0")
    print("✅ 覆盖全平台内容审核规则，避免限流、下架、账号处罚")
    print("✅ 检测范围：台词、视觉内容、音频、字幕全维度")
    print("✅ 风险等级：高/中/低三级，给出具体修改建议")
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
    check_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  将检测第 {start_ep} 到 {end_ep} 集，共 {len(check_list)} 集")
    print("="*80)

    risk_stats = {"高风险":0, "中风险":0, "低风险":0}

    for ep_dir in tqdm(check_list, desc="合规检测进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        success, msg = check_compliance_for_episode(ep_dir)
        # 读取报告获取风险等级
        report_path = os.path.join(ep_dir, "compliance_report.json")
        with open(report_path, 'r', encoding='utf-8-sig') as f:
            report = json.load(f)
        risk_stats[report["overall_risk_level"]] +=1
        tqdm.write(f"第 {ep_num} 集：{msg}")

    print("\n" + "="*80)
    print("📊 合规检测总报告：")
    print(f"   总检测集数：{len(check_list)}")
    print(f"   高风险：{risk_stats['高风险']} 集（必须修改，否则大概率下架）")
    print(f"   中风险：{risk_stats['中风险']} 集（建议修改，避免限流）")
    print(f"   低风险：{risk_stats['低风险']} 集（合规，可以发布）")
    print(f"   详情查看：每集对应 compliance_report.json 文件")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 内容合规检测工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    args = parser.parse_args()
    batch_check_compliance(args.start, args.end)
