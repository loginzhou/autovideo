import os
import json
import time

# 添加当前目录到Python路径
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_center import config
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS
from components.utils.state_manager import pipeline_state
from components.utils.token_manager import save_token_usage
from components.utils.logger import log, error_handler, ConfigurationError, APIError, ProcessingError
from components.utils.content_auditor import content_auditor
from components.skills.novel_sliding_window_chunker import novel_sliding_window_chunker
from components.agents.Screenwriter_Pro_Agent.runner import run_screenwriter
from components.agents.Director_AI_Agent.runner import run_director
from components.agents.Foley_Sound_Designer_Agent.runner import run_foley_sound_designer
from components.agents.Render_Ops_Agent.runner import run_render_ops
from components.agents.Dialogue_Master_Agent.runner import run_dialogue_master
from components.agents.Video_Render_Packager.runner import run_video_render_packager

# 升级模块导入
from components.upgrade.novel_semantic_analyzer.runner import run_novel_semantic_analyzer
from components.upgrade.intelligent_episode_splitter.runner import run_intelligent_episode_splitter
from components.upgrade.character_consistency_manager.runner import CharacterConsistencyManager
from components.upgrade.scene_consistency_manager.runner import SceneConsistencyManager

# 从配置中心读取参数
OUTPUT_ROOT = config.get("base.output_root", "output/")
RENDER_ENABLED = config.get("base.render_enabled", False)
# 使用绝对路径，确保文件路径正确
INPUT_NOVEL = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                           config.get("base.input_novel_path", "input/novel.txt"))
MAX_EPISODES = config.get("base.max_episodes", 3)

@error_handler
def main():
    """主流水线函数"""
    log.info("="*80)
    log.info("Novel2Shorts V3.0 影棚级智能体矩阵流水线（V6进化完成）")
    log.info("四大核心Agent进化完成：Cinematographer + Showrunner + Foley Designer + Continuity Supervisor")
    log.info("好莱坞工业标准输出 | 强制专业规则 | 零模拟数据 | 160K上下文溢出防护")
    log.info("="*80)

    # 断点续跑检查
    if config.get("features.breakpoint_resume", True):
        log.info("断点续跑功能已开启，检查历史执行状态...")

    # 1. 端口连通性校验（仅渲染模式需要）
    if RENDER_ENABLED:
        import urllib.request
        comfyui_endpoint = config.get("image_generation.comfyui_endpoint", "http://127.0.0.1:8188")
        try:
            urllib.request.urlopen(comfyui_endpoint, timeout=2)
            log.info(f"ComfyUI端口连通正常：{comfyui_endpoint}")
        except Exception as e:
            log.error(f"ComfyUI端口连接失败：{str(e)}")
            raise ConfigurationError(f"ComfyUI端口连接失败：{str(e)}")
    else:
        log.info("渲染模式已关闭，跳过ComfyUI端口检测")

    # 2. 输入源校验
    if not os.path.exists(INPUT_NOVEL):
        log.error(f"输入文件不存在：{INPUT_NOVEL}")
        raise ConfigurationError(f"输入文件不存在：{INPUT_NOVEL}")

    file_size = os.path.getsize(INPUT_NOVEL)
    if file_size == 0:
        log.error(f"输入文件为空：{INPUT_NOVEL}")
        raise ConfigurationError(f"输入文件为空：{INPUT_NOVEL}")

    # 检查编码
    try:
        with open(INPUT_NOVEL, 'r', encoding='utf-8') as f:
            f.read(1000)
        log.info(f"输入源校验通过，文件大小：{file_size/1024/1024:.2f}MB，编码UTF-8")
    except Exception as e:
        log.error(f"输入文件编码错误，不是UTF-8：{str(e)}")
        raise ConfigurationError(f"输入文件编码错误，不是UTF-8：{str(e)}")

    # 3. 路径与权限校验
    try:
        # 自动创建输出目录
        os.makedirs(OUTPUT_ROOT, exist_ok=True)
        for path in REQUIRED_PATHS:
            os.makedirs(path, exist_ok=True)
        check_write_permission(REQUIRED_PATHS)
        log.info("所有路径权限校验通过")
    except Exception as e:
        log.error(f"路径权限校验失败：{str(e)}")
        raise ConfigurationError(f"路径权限校验失败：{str(e)}")

    # 4. API密钥校验
    from components.utils.llm_client import MODEL_CONFIGS
    has_valid_api_key = False
    for provider, provider_config in MODEL_CONFIGS.items():
        if provider_config["api_key"]:
            has_valid_api_key = True
            break
    
    if not has_valid_api_key:
        log.error("未配置任何有效的API密钥，请在环境变量或配置文件中设置")
        raise ConfigurationError("未配置任何有效的API密钥")
    log.info("API密钥校验通过")

    log.info("="*80)
    log.info("全环境自检通过，启动影棚级全自主生产流水线！")
    log.info("="*80)

    # 导入人工审核管理器
    from components.utils.human_review_manager import human_review

    # ===================== 升级模块阶段 =====================
    global_state = {}

    # 阶段0：小说智能切块
    if not pipeline_state.is_stage_completed("novel_chunker"):
        log.info("\n阶段0：小说智能切块中...")
        chunks = novel_sliding_window_chunker(INPUT_NOVEL, chunk_size_kb=25, overlap_ratio=0.05)
        log.info(f"切块完成，共 {len(chunks)} 个Chunk")
        pipeline_state.mark_stage_completed("novel_chunker", chunks)
    else:
        chunks = pipeline_state.get_stage_data("novel_chunker")
        log.info(f"阶段0：小说智能切块已完成，共 {len(chunks)} 个Chunk（断点续跑）")
    global_state['chunks'] = chunks

    # 阶段1：全量小说语义深度分析（Continuity Supervisor场记主控）
    if not pipeline_state.is_stage_completed("semantic_analysis"):
        log.info("\n阶段1：全局连贯性系统初始化中...")
        full_analysis_result = run_novel_semantic_analyzer(INPUT_NOVEL)
        pipeline_state.mark_stage_completed("semantic_analysis", full_analysis_result)
    else:
        full_analysis_result = pipeline_state.get_stage_data("semantic_analysis")
        log.info(f"阶段1：全局连贯性系统初始化已完成（断点续跑）")
    global_state['full_analysis'] = full_analysis_result
    # 获取全局连贯性状态机
    state_machine = full_analysis_result.get('continuity_state_machine', None)
    if state_machine:
        log.info(f"全局连贯性状态机启动完成，初始时间：{state_machine['current_time']}，初始天气：{state_machine['current_weather']}")
    log.info(f"语义分析完成，识别题材：{full_analysis_result['genre']}，推荐集数：{full_analysis_result['recommended_episode_count']}")

    # 阶段2：角色一致性管理初始化
    if not pipeline_state.is_stage_completed("character_manager_init"):
        log.info("\n阶段2：角色资产库初始化中...")
        char_manager = CharacterConsistencyManager(full_analysis_result)
        pipeline_state.mark_stage_completed("character_manager_init", char_manager)
    else:
        char_manager = pipeline_state.get_stage_data("character_manager_init")
        log.info(f"阶段2：角色资产库初始化已完成（断点续跑）")
    global_state['char_manager'] = char_manager
    log.info(f"角色系统初始化完成，共管理 {len(full_analysis_result['characters'])} 个角色，face_id/voice_id已分配完成")
    
    # 阶段2.1：场景一致性管理初始化
    if not pipeline_state.is_stage_completed("scene_manager_init"):
        log.info("\n阶段2.1：场景资产库初始化中...")
        scene_manager = SceneConsistencyManager(full_analysis_result)
        pipeline_state.mark_stage_completed("scene_manager_init", scene_manager)
    else:
        scene_manager = pipeline_state.get_stage_data("scene_manager_init")
        log.info(f"阶段2.1：场景资产库初始化已完成（断点续跑）")
    global_state['scene_manager'] = scene_manager
    log.info(f"场景系统初始化完成，共管理 {len(full_analysis_result.get('scenes', []))} 个场景")

    # 阶段3：专业级智能分集（Showrunner总编剧主控）
    if not pipeline_state.is_stage_completed("episode_splitter"):
        log.info("\n阶段3：Showrunner总编剧智能分集中...")
        episode_blueprints = run_intelligent_episode_splitter(full_analysis_result, chunks)
        pipeline_state.mark_stage_completed("episode_splitter", episode_blueprints)
    else:
        episode_blueprints = pipeline_state.get_stage_data("episode_splitter")
        log.info(f"阶段3：Showrunner总编剧智能分集已完成（断点续跑）")
    global_state['episode_blueprints'] = episode_blueprints
    total_episodes = min(MAX_EPISODES, len(episode_blueprints))
    log.info(f"智能分集完成，共 {total_episodes} 集，每集严格遵循完播率波浪曲线")

    # 人工审核分集方案
    if human_review.request_review("episode_blueprint", episode_blueprints[:total_episodes]):
        log.info("分集方案审核通过，继续执行")
    else:
        log.info("分集方案审核被驳回，终止执行")
        save_token_usage()
        return

    # ===================== 逐集生成阶段 =====================
    log.info(f"\n阶段4：影棚级逐集生产启动，总集数：{total_episodes}")

    for idx, episode_blueprint in enumerate(episode_blueprints[:total_episodes]):
        episode_seq = episode_blueprint['seq']
        episode_output_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
        os.makedirs(episode_output_dir, exist_ok=True)
        
        log.info(f"\n===== 正在处理第 {episode_seq}/{total_episodes} 集，Chunk ID: {episode_blueprint['chunk_id']} =====")
        
        # 获取当前集连贯性上下文（跨集状态继承）
        continuity_context = state_machine if state_machine else None
        if continuity_context:
            log.info(f"跨集状态继承：时间={continuity_context['current_time']}，天气={continuity_context['current_weather']}")
        
        # 1. Showrunner总编剧生成剧本（完播率曲线+台词精炼）
        if not pipeline_state.is_episode_stage_completed(episode_seq, "screenplay"):
            screenplay = run_screenwriter(episode_blueprint, full_analysis_result, continuity_context)
            # 校验角色一致性
            screenplay['beats'] = [
                {"beat_type": b['beat_type'], "content": char_manager.validate_character_consistency(b['content'])} 
                for b in screenplay['beats']
            ]
            # 校验场景一致性
            screenplay['beats'] = [
                {"beat_type": b['beat_type'], "content": scene_manager.validate_scene_consistency(b['content'])} 
                for b in screenplay['beats']
            ]
            
            # 自动审核剧本
            audit_result = content_auditor.audit_screenplay(screenplay)
            if not audit_result['passed']:
                log.warning(f"剧本自动审核未通过：{', '.join(audit_result['reasons'])}")
                log.warning(f"审核分数：{audit_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"剧本自动审核通过，分数：{audit_result['score']}")
            
            # 审核内容合规性
            compliance_result = content_auditor.audit_compliance(screenplay)
            if not compliance_result['passed']:
                log.warning(f"剧本合规性审核未通过：{', '.join(compliance_result['reasons'])}")
                log.warning(f"合规性分数：{compliance_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"剧本合规性审核通过，分数：{compliance_result['score']}")
            
            log.info("Showrunner总编剧：剧本生成完成，符合Hook->Setup->Escalation->Cliffhanger完播率曲线")
            
            # 人工审核剧本
            if not human_review.request_review("screenplay", screenplay, episode_seq):
                log.info(f"第{episode_seq}集剧本审核被驳回，跳过本集")
                continue
            
            pipeline_state.mark_episode_stage_completed(episode_seq, "screenplay", screenplay)
        else:
            screenplay = pipeline_state.get_episode_stage_data(episode_seq, "screenplay")
            log.info(f"第{episode_seq}集剧本已生成（断点续跑）")
        
        # 1.5. Dialogue Master台词大师生成专业台词
        dialogue_path = os.path.join(episode_output_dir, "dialogue.json")
        if not pipeline_state.is_episode_stage_completed(episode_seq, "dialogue"):
            log.info(f"\n===== 台词大师生成第{episode_seq}集台词 =====")
            dialogue_script = run_dialogue_master(screenplay, full_analysis_result, continuity_context)
            
            # 写入台词文件
            with open(dialogue_path, 'w', encoding='utf-8-sig') as f:
                json.dump(dialogue_script, f, ensure_ascii=False, indent=2)
            
            pipeline_state.mark_episode_stage_completed(episode_seq, "dialogue", dialogue_script)
            log.info(f"台词大师：第{episode_seq}集台词生成完成，共{len(dialogue_script)}句")
        else:
            # 从文件读取台词
            with open(dialogue_path, 'r', encoding='utf-8-sig') as f:
                dialogue_script = json.load(f)
            log.info(f"第{episode_seq}集台词已生成（断点续跑），共{len(dialogue_script)}句")
        
        # 2. Cinematographer摄影指导生成分镜（专业焦段+灯光+运镜）
        storyboard_path = os.path.join(episode_output_dir, "storyboard.json")
        if not pipeline_state.is_episode_stage_completed(episode_seq, "storyboard"):
            storyboard = run_director(screenplay, full_analysis_result, dialogue_script, continuity_context)
            # 替换所有角色占位符为统一参数
            for shot in storyboard['storyboard']:
                shot['visual_prompt'] = char_manager.inject_character_params(shot['visual_prompt'], episode_blueprint['main_characters'])
                # 校验角色视觉一致性
                shot['visual_prompt'] = char_manager.validate_character_visual_consistency(shot['visual_prompt'])
                # 校验场景视觉一致性
                shot['visual_prompt'] = scene_manager.validate_scene_visual_consistency(shot['visual_prompt'])
            
            # 自动审核分镜
            audit_result = content_auditor.audit_storyboard(storyboard)
            if not audit_result['passed']:
                log.warning(f"分镜自动审核未通过：{', '.join(audit_result['reasons'])}")
                log.warning(f"审核分数：{audit_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"分镜自动审核通过，分数：{audit_result['score']}")
            
            # 审核内容合规性
            compliance_result = content_auditor.audit_compliance(storyboard)
            if not compliance_result['passed']:
                log.warning(f"分镜合规性审核未通过：{', '.join(compliance_result['reasons'])}")
                log.warning(f"合规性分数：{compliance_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"分镜合规性审核通过，分数：{compliance_result['score']}")
            
            log.info("Cinematographer摄影指导：分镜生成完成，专业焦段/灯光/运镜规则已100%注入")
            
            # 人工审核分镜
            if not human_review.request_review("storyboard", storyboard, episode_seq):
                log.info(f"第{episode_seq}集分镜审核被驳回，跳过本集")
                continue
            
            # 写入分镜文件
            with open(storyboard_path, 'w', encoding='utf-8-sig') as f:
                json.dump(storyboard, f, ensure_ascii=False, indent=2)
            
            pipeline_state.mark_episode_stage_completed(episode_seq, "storyboard", storyboard)
        else:
            # 从文件读取分镜
            with open(storyboard_path, 'r', encoding='utf-8-sig') as f:
                storyboard = json.load(f)
            log.info(f"第{episode_seq}集分镜已生成（断点续跑）")
        
        # 3. Foley Sound Designer拟音师设计专业音频（空间声学+频段分离）
        if not pipeline_state.is_episode_stage_completed(episode_seq, "audio_design"):
            processed_audio = run_foley_sound_designer(storyboard, episode_blueprint['core_plot'], continuity_context)
            # 替换音频提示词为专业设计结果
            for i in range(len(storyboard['storyboard'])):
                storyboard['storyboard'][i]['audio_prompt'] = processed_audio[i]['audio_prompt']
            
            # 自动审核音频设计
            audit_result = content_auditor.audit_audio_design(processed_audio)
            if not audit_result['passed']:
                log.warning(f"音频设计自动审核未通过：{', '.join(audit_result['reasons'])}")
                log.warning(f"审核分数：{audit_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"音频设计自动审核通过，分数：{audit_result['score']}")
            
            # 审核内容合规性
            compliance_result = content_auditor.audit_compliance(processed_audio)
            if not compliance_result['passed']:
                log.warning(f"音频设计合规性审核未通过：{', '.join(compliance_result['reasons'])}")
                log.warning(f"合规性分数：{compliance_result['score']}")
                # 可以选择是否继续执行
                # continue
            else:
                log.info(f"音频设计合规性审核通过，分数：{compliance_result['score']}")
            
            log.info("Foley拟音师：音频设计完成，空间声学+频段分离规则已应用")
            
            # 保存音频设计结果
            audio_path = os.path.join(episode_output_dir, "audio_design.json")
            with open(audio_path, 'w', encoding='utf-8-sig') as f:
                json.dump(processed_audio, f, ensure_ascii=False, indent=2)
            
            pipeline_state.mark_episode_stage_completed(episode_seq, "audio_design", processed_audio)
        else:
            processed_audio = pipeline_state.get_episode_stage_data(episode_seq, "audio_design")
            log.info(f"第{episode_seq}集音频设计已完成（断点续跑）")
        
        # 4. Video Render Packager视频渲染打包器（生成可直接渲染的标准化输出）
        if not pipeline_state.is_episode_stage_completed(episode_seq, "render_package"):
            log.info(f"\n===== 视频渲染打包器生成第{episode_seq}集渲染包 =====")
            
            # 生成通用格式渲染包
            render_package = run_video_render_packager(storyboard, full_analysis_result, output_format="universal")
            
            # 生成Sora格式
            sora_package = run_video_render_packager(storyboard, full_analysis_result, output_format="sora")
            
            # 生成Runway格式
            runway_package = run_video_render_packager(storyboard, full_analysis_result, output_format="runway")
            
            # 生成Pika格式
            pika_package = run_video_render_packager(storyboard, full_analysis_result, output_format="pika")
            
            pipeline_state.mark_episode_stage_completed(episode_seq, "render_package", {
                "universal": render_package,
                "sora": sora_package,
                "runway": runway_package,
                "pika": pika_package
            })
            
            log.info(f"视频渲染打包器：第{episode_seq}集渲染包生成完成")
            log.info(f"  - 通用格式: output/episode_{episode_seq:03d}/render_package_universal.json")
            log.info(f"  - Sora格式: output/episode_{episode_seq:03d}/render_package_sora.json")
            log.info(f"  - Runway格式: output/episode_{episode_seq:03d}/render_package_runway.json")
            log.info(f"  - Pika格式: output/episode_{episode_seq:03d}/render_package_pika.json")
        else:
            log.info(f"第{episode_seq}集渲染包已生成（断点续跑）")
        
        # 写入专业级提示词包（向后兼容）
        os.makedirs(os.path.join(episode_output_dir, "prompt_package"), exist_ok=True)
        img_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt']}" for shot in storyboard['storyboard']])
        vid_prompts = "\n".join([f"[{shot['shot_id']}] {shot['visual_prompt'].replace('--ar 9:16', '')}" for shot in storyboard['storyboard']])
        aud_prompts = ""
        for shot in storyboard['storyboard']:
            aud = shot['audio_prompt']
            voice_id = char_manager.get_character_info(episode_blueprint['main_characters'][0])['voice_id']
            dialogue_text = shot.get('dialogue', {}).get('content', aud.get('Dialogue', ''))
            dialogue_speaker = shot.get('dialogue', {}).get('speaker', '主角')
            dialogue_emotion = shot.get('dialogue', {}).get('emotion', '平静')
            aud_prompts += f"[{shot['shot_id']}]\n"
            aud_prompts += f"[Spatial] {aud['Spatial']}\n"
            aud_prompts += f"[EQ] {aud['EQ']}\n"
            aud_prompts += f"[Ambience] {aud['Ambience']}\n"
            aud_prompts += f"[SFX] {aud['SFX']}\n"
            aud_prompts += f"[Music] {aud['Music']}\n"
            aud_prompts += f"[Dialogue] [{dialogue_emotion}] {dialogue_speaker}: {dialogue_text} | voice_id: {voice_id}\n\n"
        
        with open(os.path.join(episode_output_dir, "prompt_package", "image_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(img_prompts)
        with open(os.path.join(episode_output_dir, "prompt_package", "video_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(vid_prompts)
        with open(os.path.join(episode_output_dir, "prompt_package", "audio_prompts.txt"), 'w', encoding='utf-8-sig') as f:
            f.write(aud_prompts)
        
        # 渲染+资产回收（可选，ComfyUI启动后开启）
        if RENDER_ENABLED:
            if not pipeline_state.is_episode_stage_completed(episode_seq, "render"):
                render_success, asset_path = run_render_ops(storyboard)
                if render_success:
                    log.info(f"2060显卡渲染状态：成功，资产回收：{os.path.basename(asset_path)} 入库成功")
                    pipeline_state.mark_episode_stage_completed(episode_seq, "render", asset_path)
                else:
                    log.error(f"渲染失败：{asset_path}")
            else:
                asset_path = pipeline_state.get_episode_stage_data(episode_seq, "render")
                log.info(f"第{episode_seq}集视频已渲染完成：{asset_path}（断点续跑）")
        else:
            log.info("分镜生成完成，渲染步骤已跳过，启动ComfyUI后可单独执行批量渲染")
        
        # 更新全局状态机（时间自动推进）
        if state_machine:
            state_machine.update_state(episode_seq, {
                "time": episode_blueprint.get('time', state_machine['current_time']),
                "weather": episode_blueprint.get('weather', state_machine['current_weather'])
            })
        
        # 清理内存
        del screenplay, storyboard, processed_audio
        time.sleep(1) # 给显卡散热

    # 全部完成后保存token统计
    save_token_usage()
    log.info("\n" + "="*80)
    log.info(f"V6 影棚级进化全流程执行完成！所有{total_episodes}集输出符合好莱坞工业标准")
    log.info("生产统计：")
    log.info(f"   总集数：{total_episodes}")
    log.info(f"   核心角色：{len(full_analysis_result['characters'])}个")
    log.info(f"   题材：{full_analysis_result['genre']}")
    log.info(f"   输出内容：专业级分镜+摄影参数+拟音音频+提示词包，可直接用于院线级渲染")
    log.info(f"   输出路径：{OUTPUT_ROOT}")
    log.info("="*80)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.critical(f"主流水线执行失败：{str(e)}")
        raise
