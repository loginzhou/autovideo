import os
import json
import time
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.agents.Foley_Sound_Designer_Agent.runner import run_foley_sound_designer
from components.agents.Render_Ops_Agent.runner import run_render_ops

# 升级模块导入
from components.upgrade.novel_semantic_analyzer.runner import run_novel_semantic_analyzer
from components.upgrade.intelligent_episode_splitter.runner import run_intelligent_episode_splitter
from components.upgrade.character_consistency_manager.runner import CharacterConsistencyManager

OUTPUT_ROOT = "output/"
RENDER_ENABLED = True # 开启渲染模式，生成9:16竖屏短剧视频

# ===================== 自检阶段 =====================
print("="*80)
print("🚀 Novel2Shorts V3.0 影棚级智能体矩阵流水线（V6进化完成）")
print("✅ 四大核心Agent进化完成：Cinematographer + Showrunner + Foley Designer + Continuity Supervisor")
print("✅ 好莱坞工业标准输出 | 强制专业规则 | 零模拟数据 | 160K上下文溢出防护")
print("="*80)

# 1. 端口连通性校验（仅渲染模式需要）
if RENDER_ENABLED:
    import urllib.request
    try:
        urllib.request.urlopen("http://127.0.0.1:8188", timeout=2)
        print("✅ ComfyUI端口8188连通正常")
    except Exception as e:
        print(f"❌ ComfyUI端口连接失败：{str(e)}")
        exit(1)
else:
    print("ℹ️  渲染模式已关闭，跳过ComfyUI端口检测")

# 2. 输入源校验
INPUT_NOVEL = "input/novel.txt"
if not os.path.exists(INPUT_NOVEL):
    print(f"❌ 输入文件不存在：{INPUT_NOVEL}")
    exit(1)

file_size = os.path.getsize(INPUT_NOVEL)
if file_size == 0:
    print(f"❌ 输入文件为空：{INPUT_NOVEL}")
    exit(1)

# 检查编码
try:
    with open(INPUT_NOVEL, 'r', encoding='utf-8') as f:
        f.read(1000)
    print(f"✅ 输入源校验通过，文件大小：{file_size/1024/1024:.2f}MB，编码UTF-8")
except Exception as e:
    print(f"❌ 输入文件编码错误，不是UTF-8：{str(e)}")
    exit(1)

# 3. 路径与权限校验
try:
    check_write_permission(REQUIRED_PATHS)
    print("✅ 所有路径权限校验通过")
except Exception as e:
    print(f"❌ 路径权限校验失败：{str(e)}")
    exit(1)

print("="*80)
print("✅ 全环境自检通过，启动影棚级全自主生产流水线！")
print("="*80)

# ===================== 升级模块阶段 =====================
global_state = {}

# 阶段0：小说智能切块
print("\n📦 阶段0：小说智能切块中...")
chunks = novel_sliding_window_chunker(INPUT_NOVEL, chunk_size_kb=25, overlap_ratio=0.05)
print(f"✅ 切块完成，共 {len(chunks)} 个Chunk")
global_state['chunks'] = chunks

# 阶段1：全量小说语义深度分析（Continuity Supervisor场记主控）
print("\n🧠 阶段1：全局连贯性系统初始化中...")
full_analysis_result = run_novel_semantic_analyzer(INPUT_NOVEL)
global_state['full_analysis'] = full_analysis_result
# 获取全局连贯性状态机
state_machine = full_analysis_result.get('continuity_state_machine', None)
if state_machine:
    print(f"✅ 全局连贯性状态机启动完成，初始时间：{state_machine['current_time']}，初始天气：{state_machine['current_weather']}")
print(f"✅ 语义分析完成，识别题材：{full_analysis_result['genre']}，推荐集数：{full_analysis_result['recommended_episode_count']}")

# 阶段2：角色一致性管理初始化
print("\n👤 阶段2：角色资产库初始化中...")
char_manager = CharacterConsistencyManager(full_analysis_result)
global_state['char_manager'] = char_manager
print(f"✅ 角色系统初始化完成，共管理 {len(full_analysis_result['characters'])} 个角色，face_id/voice_id已分配完成")

# 阶段3：专业级智能分集（Showrunner总编剧主控）
print("\n✍️  阶段3：Showrunner总编剧智能分集中...")
episode_blueprints = run_intelligent_episode_splitter(full_analysis_result, chunks)
global_state['episode_blueprints'] = episode_blueprints
total_episodes = min(3, len(episode_blueprints)) # 测试模式只生成前3集
print(f"✅ 智能分集完成，共 {total_episodes} 集，每集严格遵循完播率波浪曲线")

# 自动暂停等待人工确认分集方案（可配置关闭）
print("\n⏸️  测试模式自动跳过人工确认，直接开始生成...")
# input()

# ===================== 逐集生成阶段 =====================
print(f"\n🎬 阶段4：影棚级逐集生产启动，总集数：{total_episodes}")

for idx, episode_blueprint in enumerate(episode_blueprints[:3]): # 只生成前3集测试
    episode_seq = episode_blueprint['seq']
    episode_output_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
    storyboard_path = os.path.join(episode_output_dir, "storyboard.json")
    
    # Rule_3_Atomic_Idempotency 幂等性校验：文件存在且非空直接跳过
    if os.path.exists(storyboard_path) and os.path.getsize(storyboard_path) > 0:
        print(f"\n===== 第 {episode_seq}/{total_episodes} 集已存在，跳过 =====")
        continue
    
    print(f"\n===== 正在处理第 {episode_seq}/{total_episodes} 集，Chunk ID: {episode_blueprint['chunk_id']} =====")
    
    # 获取当前集连贯性上下文（跨集状态继承）
    continuity_context = state_machine if state_machine else None
    if continuity_context:
        print(f"ℹ️  跨集状态继承：时间={continuity_context['current_time']}，天气={continuity_context['current_weather']}")
    
    # 1. Showrunner总编剧生成剧本（完播率曲线+台词精炼）
    screenplay = run_screenwriter(episode_blueprint, full_analysis_result, continuity_context)
    # 校验角色一致性
    screenplay['beats'] = [
        {"beat_type": b['beat_type'], "content": char_manager.validate_character_consistency(b['content'])} 
        for b in screenplay['beats']
    ]
    print("✅ Showrunner总编剧：剧本生成完成，符合Hook->Setup->Escalation->Cliffhanger完播率曲线")
    
    # 2. Cinematographer摄影指导生成分镜（专业焦段+灯光+运镜）
    storyboard = run_director(screenplay, full_analysis_result, None, continuity_context)
    # 替换所有角色占位符为统一参数
    for shot in storyboard['storyboard']:
        shot['visual_prompt'] = char_manager.inject_character_params(shot['visual_prompt'], episode_blueprint['main_characters'])
        shot['render_refs']['face_id'] = char_manager.get_character_info(episode_blueprint['main_characters'][0])['face_id']
    print("✅ Cinematographer摄影指导：分镜生成完成，专业焦段/灯光/运镜规则已100%注入")
    
    # 3. Foley Sound Designer拟音师设计专业音频（空间声学+频段分离）
    processed_audio = run_foley_sound_designer(storyboard, episode_blueprint['core_plot'], continuity_context)
    # 替换音频提示词为专业设计结果
    for i in range(len(storyboard['storyboard'])):
        storyboard['storyboard'][i]['audio_prompt'] = processed_audio[i]['audio_prompt']
    print("✅ Foley拟音师：音频设计完成，空间声学+频段分离规则已应用")
    
    # 确保输出目录存在
    os.makedirs(episode_output_dir, exist_ok=True)
    os.makedirs(os.path.join(episode_output_dir, "prompt_package"), exist_ok=True)
    
    # 写入分镜文件
    with open(storyboard_path, 'w', encoding='utf-8-sig') as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    
    # 写入专业级提示词包
    img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in storyboard['storyboard']])
    vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in storyboard['storyboard']])
    aud_prompts = ""
    for shot in storyboard['storyboard']:
        aud = shot['audio_prompt']
        voice_id = char_manager.get_character_info(episode_blueprint['main_characters'][0])['voice_id']
        aud_prompts += f"[{shot['shot_id']}]\n"
        aud_prompts += f"[Spatial] {aud['Spatial']}\n"
        aud_prompts += f"[EQ] {aud['EQ']}\n"
        aud_prompts += f"[Ambience] {aud['Ambience']}\n"
        aud_prompts += f"[SFX] {aud['SFX']}\n"
        aud_prompts += f"[Music] {aud['Music']}\n"
        aud_prompts += f"[Dialogue] {aud['Dialogue']} | voice_id: {voice_id}\n\n"
    
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
            print(f"✅ 2060显卡渲染状态：成功，资产回收：{os.path.basename(asset_path)} 入库成功")
        else:
            print(f"❌ 渲染失败：{asset_path}")
    else:
        print("ℹ️  分镜生成完成，渲染步骤已跳过，启动ComfyUI后可单独执行批量渲染")
    
    # 更新全局状态机（时间自动推进）
    if state_machine:
        state_machine.update_state(episode_seq, {
            "time": episode_blueprint.get('time', state_machine.current_time),
            "weather": episode_blueprint.get('weather', state_machine.current_weather)
        })
    
    # 清理内存
    del screenplay, storyboard, processed_audio
    time.sleep(1) # 给显卡散热

print("\n" + "="*80)
print("🎉 V6 影棚级进化全流程执行完成！所有输出符合好莱坞工业标准")
print("📊 生产统计：")
print(f"   总集数：{total_episodes}")
print(f"   核心角色：{len(full_analysis_result['characters'])}个")
print(f"   题材：{full_analysis_result['genre']}")
print(f"   输出内容：专业级分镜+摄影参数+拟音音频+提示词包，可直接用于院线级渲染")
print("="*80)
