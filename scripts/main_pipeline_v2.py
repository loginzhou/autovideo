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
RENDER_ENABLED = False # 暂时关闭渲染，先生成所有内容，ComfyUI启动后再打开

# ===================== 自检阶段 =====================
print("="*70)
print("🚀 Novel2Shorts V2.1 全自主专业级短剧流水线启动（适配DeepSeek V3.2 160K上下文）")
print("✅ 禁止fallback模拟数据，纯真实API驱动，自动token溢出防护")
print("="*70)

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

print("="*70)
print("✅ 全环境自检通过，启动全自主生产流水线！")
print("="*70)

# ===================== 升级模块阶段 =====================
global_state = {}

# 阶段0：小说智能切块
print("\n📦 阶段0：小说智能切块中...")
chunks = novel_sliding_window_chunker(INPUT_NOVEL, overlap_ratio=0.05)
print(f"✅ 切块完成，共 {len(chunks)} 个Chunk")
global_state['chunks'] = chunks

# 阶段1：全量小说语义深度分析
print("\n🔍 阶段1：全量小说语义分析中...")
full_analysis_result = run_novel_semantic_analyzer(INPUT_NOVEL)
global_state['full_analysis'] = full_analysis_result
print(f"✅ 语义分析完成，识别题材：{full_analysis_result['genre']}，推荐集数：{full_analysis_result['recommended_episode_count']}")

# 阶段2：角色一致性管理初始化
print("\n👤 阶段2：角色一致性系统初始化...")
char_manager = CharacterConsistencyManager(full_analysis_result)
global_state['char_manager'] = char_manager
print(f"✅ 角色系统初始化完成，共管理 {len(full_analysis_result['characters'])} 个角色")

# 阶段3：专业级智能分集
print("\n🎬 阶段3：专业级智能分集中...")
episode_blueprints = run_intelligent_episode_splitter(full_analysis_result, chunks)
global_state['episode_blueprints'] = episode_blueprints
total_episodes = min(3, len(episode_blueprints)) # 测试模式只生成前3集
print(f"✅ 智能分集完成，总集数：{total_episodes}")

# 自动暂停等待人工确认分集方案（可配置关闭）
print("\n⏸️  测试模式自动跳过人工确认，直接开始生成...")
# input()

# ===================== 逐集生成阶段 =====================
print(f"\n🚀 阶段4：逐集生成+渲染启动，总集数：{total_episodes}")

for idx, episode_blueprint in enumerate(episode_blueprints):
    episode_seq = episode_blueprint['seq']
    episode_output_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
    storyboard_path = os.path.join(episode_output_dir, "storyboard.json")
    
    # Rule_3_Atomic_Idempotency 幂等性校验：文件存在且非空直接跳过
    if os.path.exists(storyboard_path) and os.path.getsize(storyboard_path) > 0:
        print(f"\n===== 第 {episode_seq}/{total_episodes} 集已存在，跳过 =====")
        continue
    
    print(f"\n===== 正在处理第 {episode_seq}/{total_episodes} 集，Chunk ID: {episode_blueprint['chunk_id']} =====")
    
    # 生成剧本（注入角色一致性校验）
    screenplay = run_screenwriter(episode_blueprint, full_analysis_result)
    # 校验角色一致性
    screenplay['beats'] = [
        {"beat_type": b['beat_type'], "content": char_manager.validate_character_consistency(b['content'])} 
        for b in screenplay['beats']
    ]
    print("✅ 剧本生成完成")
    
    # 生成分镜（注入角色统一参数）
    storyboard = run_director(screenplay, full_analysis_result)
    # 替换所有角色占位符为统一参数
    for shot in storyboard['storyboard']:
        shot['visual_prompt'] = char_manager.inject_character_params(shot['visual_prompt'], episode_blueprint['main_characters'])
        shot['render_refs']['face_id'] = char_manager.get_character_info(episode_blueprint['main_characters'][0])['face_id']
    print("✅ 分镜生成完成")
    
    # 确保输出目录存在
    os.makedirs(episode_output_dir, exist_ok=True)
    os.makedirs(os.path.join(episode_output_dir, "prompt_package"), exist_ok=True)
    
    # 写入分镜文件
    with open(storyboard_path, 'w', encoding='utf-8-sig') as f:
        json.dump(storyboard, f, ensure_ascii=False, indent=2)
    
    # 写入提示词包
    img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in storyboard['storyboard']])
    vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['shot_type']}, {shot['lighting_setup']}, {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in storyboard['storyboard']])
    aud_prompts = ""
    for shot in storyboard['storyboard']:
        aud = shot['audio_prompt']
        voice_id = char_manager.get_character_info(episode_blueprint['main_characters'][0])['voice_id']
        aud_prompts += f"[{shot['shot_id']}]\n[Ambience] {aud['Ambience']}\n[SFX] {aud['SFX']}\n[Music] {aud['Music']}\n[Dialogue] {aud['Dialogue']} | voice_id: {voice_id}\n\n"
    
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
    
    # 每10集汇报进度
    if episode_seq % 10 == 0:
        print(f"\n===== 进度简报：已完成 {episode_seq}/{total_episodes} 集 =====")
    
    # 清理内存
    del screenplay, storyboard
    time.sleep(1) # 给显卡散热

print("\n" + "="*70)
print("🎉 全流水线执行完成！所有内容已写入output目录")
print("📊 生产统计：")
print(f"   总集数：{total_episodes}")
print(f"   核心角色：{len(full_analysis_result['characters'])}个")
print(f"   题材：{full_analysis_result['genre']}")
print(f"   所有输出可直接用于渲染成片")
print("="*70)
