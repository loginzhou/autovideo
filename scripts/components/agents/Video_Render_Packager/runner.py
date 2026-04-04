# -*- coding: utf-8 -*-
"""
Video Render Packager (视频渲染打包器)
整合分镜、台词、音频等所有信息，生成可直接用于视频渲染的标准化输出
支持多种视频生成模型：Sora、Runway、Pika、Stable Video Diffusion等
"""
import json
import os
from config_center import config


def run_video_render_packager(storyboard_result, global_lore, output_format="universal"):
    """
    视频渲染打包器 V1.0
    生成标准化的视频渲染包，可直接交给视频生成模型
    
    Args:
        storyboard_result: 分镜结果
        global_lore: 全局设定
        output_format: 输出格式 (universal/sora/runway/pika/svd)
    """
    seq = storyboard_result['episode_seq']
    storyboard = storyboard_result['storyboard']
    
    print(f"\n{'='*60}")
    print(f"视频渲染打包器启动 - 第{seq}集")
    print(f"输出格式: {output_format}")
    print(f"{'='*60}")
    
    # 构建渲染包
    render_package = {
        "metadata": {
            "episode_seq": seq,
            "total_shots": len(storyboard),
            "total_duration": sum(shot.get('dialogue', {}).get('duration', 2.5) for shot in storyboard),
            "aspect_ratio": "9:16",
            "resolution": "1080x1920",
            "fps": 24,
            "output_format": output_format
        },
        "global_settings": {
            "characters": global_lore.get('characters', []),
            "story_rules": global_lore.get('story_rules', {}),
            "genre": global_lore.get('genre', '未知'),
            "core_theme": global_lore.get('core_theme', '')
        },
        "shots": []
    }
    
    # 处理每个镜头
    for i, shot in enumerate(storyboard):
        dialogue = shot.get('dialogue', {})
        audio = shot.get('audio_prompt', {})
        
        # 构建标准化的镜头信息
        shot_package = {
            "shot_id": shot['shot_id'],
            "sequence": i + 1,
            
            # 视觉信息
            "visual": {
                "prompt": shot.get('visual_prompt', ''),
                "video_prompt": shot.get('video_prompt', ''),
                "shot_type": shot.get('shot_type', 'medium_shot'),
                "camera_angle": shot.get('camera_angle', 'eye_level'),
                "lighting": shot.get('lighting_setup', 'natural'),
                "location": shot.get('location', 'indoor'),
                "transition": shot.get('transition_effect', 'Cut')
            },
            
            # 台词信息
            "dialogue": {
                "speaker": dialogue.get('speaker', '主角'),
                "text": dialogue.get('content', ''),
                "emotion": dialogue.get('emotion', '平静'),
                "delivery": dialogue.get('delivery', '正常语速'),
                "subtext": dialogue.get('subtext', ''),
                "duration_seconds": dialogue.get('duration', 2.5)
            },
            
            # 音频信息
            "audio": {
                "ambience": audio.get('Ambience', ''),
                "sfx": audio.get('SFX', ''),
                "music": {
                    "style": audio.get('Music', ''),
                    "bpm": audio.get('BPM', 120)
                },
                "dialogue_processing": {
                    "noise_reduction": True,
                    "normalization": True,
                    "reverb": "slight_room"
                }
            },
            
            # 渲染参考
            "render_refs": shot.get('render_refs', {}),
            
            # 时间信息
            "timing": {
                "start_time": sum(storyboard[j].get('dialogue', {}).get('duration', 2.5) for j in range(i)),
                "duration": dialogue.get('duration', 2.5),
                "end_time": sum(storyboard[j].get('dialogue', {}).get('duration', 2.5) for j in range(i + 1))
            }
        }
        
        render_package["shots"].append(shot_package)
    
    # 根据输出格式生成特定格式的提示词
    if output_format == "sora":
        render_package = format_for_sora(render_package)
    elif output_format == "runway":
        render_package = format_for_runway(render_package)
    elif output_format == "pika":
        render_package = format_for_pika(render_package)
    elif output_format == "svd":
        render_package = format_for_svd(render_package)
    else:
        render_package = format_universal(render_package)
    
    # 保存渲染包
    output_dir = os.path.join("output", f"episode_{seq:03d}")
    os.makedirs(output_dir, exist_ok=True)
    
    render_package_path = os.path.join(output_dir, f"render_package_{output_format}.json")
    with open(render_package_path, 'w', encoding='utf-8') as f:
        json.dump(render_package, f, ensure_ascii=False, indent=2)
    
    # 生成简化的提示词列表（用于批量生成）
    prompts_path = os.path.join(output_dir, f"video_prompts_{output_format}.txt")
    with open(prompts_path, 'w', encoding='utf-8') as f:
        for shot in render_package["shots"]:
            f.write(f"[{shot['shot_id']}]\n")
            f.write(f"Visual: {shot['visual']['prompt']}\n")
            f.write(f"Video: {shot['visual']['video_prompt']}\n")
            f.write(f"Dialogue: [{shot['dialogue']['emotion']}] {shot['dialogue']['speaker']}: {shot['dialogue']['text']}\n")
            f.write(f"Duration: {shot['timing']['duration']}s\n")
            f.write("-" * 60 + "\n")
    
    # 生成音频提示词列表
    audio_prompts_path = os.path.join(output_dir, f"audio_prompts_{output_format}.txt")
    with open(audio_prompts_path, 'w', encoding='utf-8') as f:
        for shot in render_package["shots"]:
            f.write(f"[{shot['shot_id']}]\n")
            f.write(f"Ambience: {shot['audio']['ambience']}\n")
            f.write(f"SFX: {shot['audio']['sfx']}\n")
            f.write(f"Music: {shot['audio']['music']['style']} ({shot['audio']['music']['bpm']} BPM)\n")
            f.write(f"Dialogue: {shot['dialogue']['text']} ({shot['dialogue']['emotion']})\n")
            f.write("-" * 60 + "\n")
    
    print(f"渲染包生成完成:")
    print(f"  - 总镜头数: {len(storyboard)}")
    print(f"  - 总时长: {render_package['metadata']['total_duration']:.1f}秒")
    print(f"  - 渲染包: {render_package_path}")
    print(f"  - 视频提示词: {prompts_path}")
    print(f"  - 音频提示词: {audio_prompts_path}")
    
    return render_package


def format_universal(package):
    """通用格式，兼容所有模型"""
    for shot in package["shots"]:
        # 确保提示词包含所有必要元素
        visual_prompt = shot["visual"]["prompt"]
        if "--ar" not in visual_prompt:
            visual_prompt += " --ar 9:16"
        if "--v" not in visual_prompt and "--version" not in visual_prompt:
            visual_prompt += " --v 6.0"
        shot["visual"]["prompt"] = visual_prompt
        
        # 视频提示词增强
        video_prompt = shot["visual"]["video_prompt"]
        if "camera" not in video_prompt.lower():
            video_prompt = f"{shot['visual']['camera_angle']} camera angle, {video_prompt}"
        shot["visual"]["video_prompt"] = video_prompt
    
    return package


def format_for_sora(package):
    """Sora格式 - OpenAI Sora*/"""
    sora_prompts = []
    
    for shot in package["shots"]:
        # Sora使用统一提示词格式
        prompt = f"""
{shot['visual']['video_prompt']}

DIALOGUE: {shot['dialogue']['speaker']}: {shot['dialogue']['text']}
EMOTION: {shot['dialogue']['emotion']}
DURATION: {shot['timing']['duration']} seconds
ASPECT RATIO: {package['metadata']['aspect_ratio']}
"""
        sora_prompts.append({
            "shot_id": shot["shot_id"],
            "prompt": prompt.strip(),
            "duration": shot["timing"]["duration"]
        })
    
    package["sora_output"] = {
        "prompts": sora_prompts,
        "total_duration": package["metadata"]["total_duration"],
        "aspect_ratio": package["metadata"]["aspect_ratio"]
    }
    
    return package


def format_for_runway(package):
    """Runway Gen-2格式"""
    runway_shots = []
    
    for shot in package["shots"]:
        runway_shots.append({
            "image_prompt": shot["visual"]["prompt"],
            "text_prompt": shot["visual"]["video_prompt"],
            "duration": shot["timing"]["duration"],
            "dialogue": f"{shot['dialogue']['speaker']}: {shot['dialogue']['text']} ({shot['dialogue']['emotion']})"
        })
    
    package["runway_output"] = runway_shots
    return package


def format_for_pika(package):
    """Pika Labs格式"""
    pika_script = []
    
    for shot in package["shots"]:
        pika_script.append({
            "prompt": f"{shot['visual']['video_prompt']} --ar {package['metadata']['aspect_ratio']}",
            "dialogue": f"[{shot['dialogue']['emotion']}] {shot['dialogue']['speaker']}: {shot['dialogue']['text']}",
            "frame_duration": shot["timing"]["duration"]
        })
    
    package["pika_output"] = {
        "script": pika_script,
        "version": "1.0"
    }
    
    return package


def format_for_svd(package):
    """Stable Video Diffusion格式"""
    svd_output = []
    
    for shot in package["shots"]:
        svd_output.append({
            "prompt": shot["visual"]["prompt"],
            "negative_prompt": "blurry, low quality, distorted",
            "duration": int(shot["timing"]["duration"] * 24),  # SVD uses frames
            "fps": 24,
            "dialogue": shot["dialogue"]
        })
    
    package["svd_output"] = svd_output
    return package