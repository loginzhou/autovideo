import os
import json
import uuid
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from openclaw import sessions_spawn
from components.utils.path_checker import check_write_permission, REQUIRED_PATHS

# 路径校验补丁：启动前强制检测所有路径写权限，无权限直接终止
check_write_permission(REQUIRED_PATHS)

# 加载全局配置
CONFIG_PATH = "config/model_routing.json"
BLUEPRINT_PATH = "output/global_blueprint_sample.json"
OUTPUT_ROOT = "output/"
SANDBOX_ROOT = "sandbox/"

# 并发数控制
MAX_WORKERS = 3
MAX_RETRIES = 3

# 加载全局只读配置
global_config = {
    "vertical_screen": json.load(open("config/vertical_screen_spec.json", 'r', encoding='utf-8')),
    "character_schema": json.load(open("config/character_schema.json", 'r', encoding='utf-8')),
    "storyboard_schema": json.load(open("config/storyboard_schema.json", 'r', encoding='utf-8')),
    "model_routing": json.load(open("config/model_routing.json", 'r', encoding='utf-8'))
}

def runEpisodeSandbox(episode_blueprint, current_global_state):
    episodeUuid = uuid.uuid4().hex[:8]
    sandboxDir = os.path.join(SANDBOX_ROOT, episodeUuid)
    os.makedirs(sandboxDir, exist_ok=True)
    
    # 写入沙盒输入（只读）
    inputPayload = {
        "global_config": global_config,
        "episode_blueprint": episode_blueprint,
        "current_state": current_global_state
    }
    
    try:
        # 调用OpenClaw创建隔离沙盒，关闭长期记忆，用完即毁
        sandboxSession = sessions_spawn({
            "task": f"""生成单集竖屏分镜，严格遵循input.json中的全局配置和列车拍摄规则，输出符合storyboard_schema的JSON：
1. 所有镜头必须9:16竖屏居中构图
2. 列车严禁拍侧面全景，必须用极低仰拍车头/尖刺排障器特写/车轮碾压特写/内部纵深镜头
3. 分镜每镜头时长2-8秒
4. 输出纯JSON，不要额外内容""",
            "runtime": "subagent",
            "mode": "run",
            "cleanup": "delete", # 运行完成自动销毁沙盒
            "model": global_config['model_routing']['agent_routing']['EpisodeSandbox'],
            "thinking": "off",
            "attachments": [
                {"name": "input.json", "content": json.dumps(inputPayload, ensure_ascii=False), "encoding": "utf8"}
            ]
        })
        
        # 解析输出
        sandboxOutput = json.loads(sandboxSession.result)
        return {
            "success": True,
            "episode_id": episodeUuid,
            "sandbox_dir": sandboxDir,
            "output": sandboxOutput
        }
        
    except Exception as err:
        # 异常时清理沙盒
        if os.path.exists(sandboxDir):
            os.rmdir(sandboxDir)
        return {
            "success": False,
            "error": str(err)
        }

def load_blueprint():
    with open(BLUEPRINT_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def process_episode(episode_blueprint, global_state, retry_count=0):
    episode_seq = episode_blueprint['seq']
    print(f"开始生成第 {episode_seq} 集，重试次数：{retry_count}")
    
    try:
        result = runEpisodeSandbox(episode_blueprint, global_state)
        if not result['success']:
            if retry_count < MAX_RETRIES:
                print(f"第 {episode_seq} 集生成失败，重试中...")
                return process_episode(episode_blueprint, global_state, retry_count + 1)
            else:
                print(f"第 {episode_seq} 集生成失败，超过最大重试次数")
                return False, episode_seq, None
        
        # 保存输出
        episode_dir = os.path.join(OUTPUT_ROOT, f"episode_{episode_seq}")
        os.makedirs(episode_dir, exist_ok=True)
        
        with open(os.path.join(episode_dir, "storyboard.json"), 'w', encoding='utf-8') as f:
            json.dump(result['output'], f, ensure_ascii=False, indent=2)
        
        # 更新全局状态
        global_state.update(result['output']['state_delta'])
        with open(os.path.join(OUTPUT_ROOT, "state_history.json"), 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "episode_seq": episode_seq,
                "timestamp": int(time.time()),
                "state_delta": result['output']['state_delta']
            }, ensure_ascii=False) + "\n")
        
        print(f"第 {episode_seq} 集生成完成")
        return True, episode_seq, result['output']
    
    except Exception as e:
        print(f"第 {episode_seq} 集生成异常：{str(e)}")
        if retry_count < MAX_RETRIES:
            return process_episode(episode_blueprint, global_state, retry_count + 1)
        return False, episode_seq, None

def main():
    blueprint = load_blueprint()
    episodes = blueprint['episode_blueprints']
    total_episodes = blueprint['total_episodes']
    print(f"开始生成全集，总集数：{total_episodes}")
    
    global_state = {}
    completed = 0
    failed = []
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(process_episode, ep, global_state.copy()) for ep in episodes]
        for future in as_completed(futures):
            success, seq, output = future.result()
            if success:
                completed += 1
                # 每完成10集报告进度
                if completed % 10 == 0:
                    print(f"进度：{completed}/{total_episodes} 集已完成")
            else:
                failed.append(seq)
    
    print(f"生成完成，成功：{completed} 集，失败：{len(failed)} 集")
    if failed:
        print(f"失败集数：{failed}")
    return completed, failed

if __name__ == "__main__":
    main()
