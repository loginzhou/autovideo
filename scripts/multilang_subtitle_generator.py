import os
import json
import glob
from googletrans import Translator # 或使用DeepLX本地部署，避免API限制
from tqdm import tqdm

OUTPUT_ROOT = "output/"
SUPPORT_LANGUAGES = {
    "zh": "中文",
    "en": "English",
    "es": "Español",
    "ko": "한국어",
    "ja": "日本語"
}

translator = Translator()

def generate_subtitles_for_episode(ep_dir, target_langs=["zh", "en"]):
    """
    为单集生成多语言字幕
    """
    ep_num = os.path.basename(ep_dir).split("_")[1]
    storyboard_path = os.path.join(ep_dir, "storyboard.json")
    subtitle_dir = os.path.join(ep_dir, "subtitles")
    os.makedirs(subtitle_dir, exist_ok=True)

    try:
        with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
            storyboard = json.load(f)
    except Exception as e:
        return False, f"分镜读取失败：{str(e)}"

    # 提取所有台词
    dialogue_list = []
    timestamp = 0
    for shot in storyboard['storyboard']:
        duration = shot.get('duration', 3) # 默认每镜头3秒
        dialogue = shot['audio_prompt'].get('Dialogue', '')
        if dialogue:
            dialogue_list.append({
                "start": timestamp,
                "end": timestamp + duration,
                "text": dialogue
            })
        timestamp += duration

    if not dialogue_list:
        return False, "无台词内容"

    # 生成各语言字幕
    for lang in target_langs:
        if lang not in SUPPORT_LANGUAGES:
            continue
        srt_path = os.path.join(subtitle_dir, f"subtitle_{lang}.srt")
        vtt_path = os.path.join(subtitle_dir, f"subtitle_{lang}.vtt")

        # 翻译
        translated = []
        for item in dialogue_list:
            if lang == "zh":
                translated_text = item['text']
            else:
                try:
                    translated_text = translator.translate(item['text'], dest=lang).text
                except Exception as e:
                    translated_text = item['text'] # 翻译失败用原文
            translated.append({
                "start": item['start'],
                "end": item['end'],
                "text": translated_text
            })

        # 生成SRT格式
        srt_content = ""
        for idx, item in enumerate(translated, 1):
            start_h = int(item['start'] // 3600)
            start_m = int((item['start'] % 3600) // 60)
            start_s = int(item['start'] % 60)
            end_h = int(item['end'] // 3600)
            end_m = int((item['end'] % 3600) // 60)
            end_s = int(item['end'] % 60)
            srt_content += f"{idx}\n"
            srt_content += f"{start_h:02d}:{start_m:02d}:{start_s:02d},000 --> {end_h:02d}:{end_m:02d}:{end_s:02d},000\n"
            srt_content += f"{item['text']}\n\n"

        with open(srt_path, 'w', encoding='utf-8-sig') as f:
            f.write(srt_content)

        # 生成VTT格式
        vtt_content = "WEBVTT\n\n"
        for idx, item in enumerate(translated, 1):
            start_h = int(item['start'] // 3600)
            start_m = int((item['start'] % 3600) // 60)
            start_s = int(item['start'] % 60)
            end_h = int(item['end'] // 3600)
            end_m = int((item['end'] % 3600) // 60)
            end_s = int(item['end'] % 60)
            vtt_content += f"{start_h:02d}:{start_m:02d}:{start_s:02d}.000 --> {end_h:02d}:{end_m:02d}:{end_s:02d}.000\n"
            vtt_content += f"{item['text']}\n\n"

        with open(vtt_path, 'w', encoding='utf-8-sig') as f:
            f.write(vtt_content)

    return True, f"已生成 {len(target_langs)} 种语言字幕"

def batch_generate_subtitles(start_ep=1, end_ep=None, langs=["zh", "en"]):
    """
    批量为所有剧集生成多语言字幕
    """
    print("="*80)
    print("🌍 Novel2Shorts 多语言字幕生成引擎 V1.0")
    print(f"✅ 支持语言：{', '.join([f'{k}({v})' for k,v in SUPPORT_LANGUAGES.items()])}")
    print(f"✅ 输出格式：SRT / VTT 双格式，适配所有主流短视频平台")
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
    process_list = episode_dirs[start_idx:end_idx]

    print(f"ℹ️  将为第 {start_ep} 到 {end_ep} 集，共 {len(process_list)} 集生成字幕")
    print(f"🎯 目标语言：{', '.join(langs)}")
    print("="*80)

    success_count = 0
    fail_count = 0

    for ep_dir in tqdm(process_list, desc="字幕生成进度"):
        ep_num = os.path.basename(ep_dir).split("_")[1]
        success, msg = generate_subtitles_for_episode(ep_dir, langs)
        if success:
            success_count +=1
            tqdm.write(f"✅ 第 {ep_num} 集：{msg}")
        else:
            fail_count +=1
            tqdm.write(f"❌ 第 {ep_num} 集：{msg}")

    print("\n" + "="*80)
    print("📊 字幕生成完成统计：")
    print(f"   总任务数：{len(process_list)}")
    print(f"   成功：{success_count} 集")
    print(f"   失败：{fail_count} 集")
    print(f"   输出目录：每集对应 subtitles/ 文件夹")
    print("="*80)

    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Novel2Shorts 多语言字幕生成工具")
    parser.add_argument("--start", type=int, default=1, help="起始集数，默认1")
    parser.add_argument("--end", type=int, default=None, help="结束集数，默认全部")
    parser.add_argument("--langs", nargs="+", default=["zh", "en"], help="目标语言列表，默认zh en")
    args = parser.parse_args()
    batch_generate_subtitles(args.start, args.end, args.langs)
