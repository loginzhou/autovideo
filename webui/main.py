# -*- coding: utf-8 -*-
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
import json
import asyncio
import time
from subprocess import Popen, PIPE, STDOUT

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

app = FastAPI(title="Novel2Shorts WebUI")

# 全局变量
task_running = False
task_process = None
task_logs = []
is_paused = False
read_task_logs_task = None

# 获取项目根目录
BASE_DIR = project_root

# 动态加载配置
def get_output_dir():
    try:
        from scripts.config_loader import config
        return config.get('basic', {}).get('output_root', 'output/')
    except:
        return 'output/'

output_dir = get_output_dir()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    # 直接读取HTML文件并返回
    template_path = os.path.join(BASE_DIR, "webui", "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.post("/api/upload_novel")
async def upload_novel(file: UploadFile = File(...)):
    content = await file.read()
    
    # 尝试检测编码并转换为UTF-8
    try:
        # 首先尝试UTF-8
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        try:
            # 尝试GBK
            text = content.decode('gbk')
        except UnicodeDecodeError:
            try:
                # 尝试GB2312
                text = content.decode('gb2312')
            except UnicodeDecodeError:
                try:
                    # 尝试GB18030
                    text = content.decode('gb18030')
                except UnicodeDecodeError:
                    return {"status": "error", "message": "无法识别文件编码，请确保文件为UTF-8、GBK、GB2312或GB18030编码"}
        
        # 转换为UTF-8
        content = text.encode('utf-8')
    
    # 使用绝对路径
    novel_path = os.path.join(BASE_DIR, "scripts", "input", "novel.txt")
    os.makedirs(os.path.dirname(novel_path), exist_ok=True)
    with open(novel_path, "wb") as f:
        f.write(content)
    return {"status": "success", "message": f"小说上传成功，大小：{len(content)}字节"}

@app.post("/api/start_task")
async def start_task():
    global task_running, task_process, task_logs, read_task_logs_task
    if task_running:
        return {"status": "error", "message": "已有任务正在运行"}
    
    # 终止之前的进程（如果有的话）
    if task_process and task_process.poll() is None:
        try:
            task_process.terminate()
            task_process.wait(timeout=5)
        except:
            pass
    
    # 取消之前的读取日志协程（如果有的话）
    if read_task_logs_task:
        try:
            read_task_logs_task.cancel()
        except:
            pass
    
    # 清空日志列表
    task_logs = []
    task_running = True
    
    try:
        # 检查main_pipeline_v3.py文件是否存在
        script_path = os.path.join(BASE_DIR, "scripts", "main_pipeline_v3.py")
        print(f"[WebUI] Project root: {BASE_DIR}")
        print(f"[WebUI] Pipeline path: {script_path}")
        print(f"[WebUI] Pipeline file exists: {os.path.exists(script_path)}")
        
        # 检查输入文件
        input_path = os.path.join(BASE_DIR, "scripts", "input", "novel.txt")
        print(f"[WebUI] Input file exists: {os.path.exists(input_path)}")
        
        # 启动主流水线 - 使用二进制模式以处理各种编码
        print("[WebUI] Starting task process...")
        task_process = Popen(
            [sys.executable, script_path],
            stdout=PIPE,
            stderr=STDOUT,
            cwd=BASE_DIR,
            bufsize=1  # 行缓冲
        )
        print(f"[WebUI] Task process started with PID: {task_process.pid}")
        
        # 检查进程是否真的启动了
        time.sleep(0.5)
        process_status = task_process.poll()
        print(f"[WebUI] Process status after 0.5 second: {process_status}")
        
        if process_status is not None:
            # 进程立即结束，读取错误信息
            error_output, _ = task_process.communicate()
            error_msg = f"进程启动失败: {error_output}" if error_output else "进程立即退出"
            print(f"[WebUI] Error: {error_msg}")
            task_running = False
            task_logs.append(error_msg)
            return {"status": "error", "message": error_msg}
        
        # 创建新的读取日志协程
        read_task_logs_task = asyncio.create_task(read_task_logs())
        print("[WebUI] Read task logs coroutine created")
        
        return {"status": "success", "message": "任务启动成功"}
    except Exception as e:
        # 处理异常，确保task_running被设置为False
        print(f"[WebUI] Error starting task: {str(e)}")
        import traceback
        traceback.print_exc()
        task_running = False
        task_logs.append(f"启动任务失败：{str(e)}")
        return {"status": "error", "message": f"启动任务失败：{str(e)}"}

async def read_task_logs():
    global task_running, task_logs, task_process
    log_file_path = None
    
    try:
        # 确保日志目录存在
        log_dir = os.path.join(BASE_DIR, output_dir, "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 创建日志文件
        log_file_name = f"task_{time.strftime('%Y%m%d_%H%M%S')}.log"
        log_file_path = os.path.join(log_dir, log_file_name)
        print(f"[WebUI] Log file: {log_file_path}")
        
        with open(log_file_path, 'w', encoding='utf-8', errors='replace') as log_file:
            while True:
                # 读取二进制数据（因为Popen使用binary mode）
                line_bytes = task_process.stdout.readline()
                if not line_bytes:
                    # 检查进程是否结束
                    if task_process.poll() is not None:
                        break
                    # 短暂等待以避免CPU占用过高
                    await asyncio.sleep(0.1)
                    continue
                
                # 解码字节流，使用容错编码解析
                # 尝试多种编码方式，最后使用replace错误处理
                try:
                    # 优先尝试UTF-8
                    line = line_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        # 尝试GBK（Windows中文编码）
                        line = line_bytes.decode('gbk')
                    except UnicodeDecodeError:
                        try:
                            # 尝试GB2312
                            line = line_bytes.decode('gb2312')
                        except UnicodeDecodeError:
                            try:
                                # 尝试GB18030
                                line = line_bytes.decode('gb18030')
                            except UnicodeDecodeError:
                                # 最后使用latin-1（总是成功的）
                                line = line_bytes.decode('latin-1', errors='replace')
                
                # 保存到本地文件
                log_file.write(line)
                log_file.flush()
                
                # 添加到日志列表
                log_line = line.strip()
                if log_line:
                    task_logs.append(log_line)
                    print(f"[WebUI] {log_line}")
        
        # 读取进程返回码
        return_code = task_process.poll()
        completion_msg = f"[WebUI] Task completed with return code: {return_code}"
        print(completion_msg)
        task_logs.append(completion_msg)
        
    except asyncio.CancelledError:
        print("[WebUI] Read task logs cancelled")
        pass
    except Exception as e:
        error_msg = f"[WebUI] Error reading logs: {str(e)}"
        print(error_msg)
        task_logs.append(error_msg)
        import traceback
        traceback.print_exc()
    finally:
        task_running = False
        if log_file_path:
            print(f"[WebUI] Logs saved to: {log_file_path}")

@app.get("/api/get_logs")
async def get_logs():
    return {"logs": task_logs, "running": task_running, "is_paused": is_paused}

@app.get("/api/download_output")
async def download_output():
    # 打包输出目录
    import shutil
    output_full_path = os.path.join(BASE_DIR, output_dir)
    zip_path = os.path.join(BASE_DIR, "output_package.zip")
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
    
    if os.path.exists(output_full_path):
        shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', output_full_path)
        return FileResponse(zip_path, filename="novel2shorts_output.zip", media_type="application/zip")
    else:
        return JSONResponse(status_code=404, content={"status": "error", "message": "输出目录不存在"})

@app.get("/api/get_config")
async def get_config():
    """获取当前配置"""
    try:
        from scripts.config_loader import config
        return config._config if hasattr(config, '_config') else config.get_all_config()
    except Exception as e:
        print(f"[WebUI] 获取配置失败: {e}")
        return {"status": "error", "message": f"获取配置失败: {str(e)}"}

@app.post("/api/save_config")
async def save_config(new_config: dict):
    """保存配置到config.yaml"""
    try:
        import yaml
        # 使用绝对路径保存配置
        config_path = os.path.join(BASE_DIR, "config.yaml")
        print(f"[WebUI] 保存配置到: {config_path}")
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(new_config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"[WebUI] 配置已保存，重新加载...")
        # 重新加载配置
        from scripts.config_loader import config
        config._load_config()
        
        return {"status": "success", "message": "配置保存成功"}
    except Exception as e:
        error_msg = f"配置保存失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.get("/api/get_api_config")
async def get_api_config():
    """获取API配置（LLM提供商配置）"""
    try:
        import yaml
        config_path = os.path.join(BASE_DIR, "config.yaml")
        
        # 如果配置文件不存在，返回默认配置
        if not os.path.exists(config_path):
            return {
                "status": "success",
                "config": {
                    "llm": {
                        "default_provider": "siliconflow",
                        "siliconflow": {
                            "api_key": "",
                            "model": "deepseek-ai/DeepSeek-V3.2",
                            "base_url": "https://api.siliconflow.cn/v1"
                        },
                        "openai": {
                            "api_key": "",
                            "model": "gpt-4o",
                            "base_url": "https://api.openai.com/v1"
                        },
                        "anthropic": {
                            "api_key": "",
                            "model": "claude-3-opus-20240229",
                            "base_url": "https://api.anthropic.com/v1"
                        },
                        "volcengine": {
                            "api_key": "",
                            "model": "doubao-seed-2-0-pro-260215",
                            "base_url": "https://ark.cn-beijing.volces.com/api/v3"
                        },
                        "zhipu": {
                            "api_key": "",
                            "model": "glm-4",
                            "base_url": "https://open.bigmodel.cn/api/paas/v4"
                        },
                        "qwen": {
                            "api_key": "",
                            "model": "qwen-max",
                            "base_url": "https://dashscope.aliyuncs.com/api/v1"
                        }
                    }
                }
            }
        
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # 只返回llm配置
        llm_config = full_config.get("llm", {})
        
        return {"status": "success", "config": {"llm": llm_config}}
    except Exception as e:
        error_msg = f"获取API配置失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.post("/api/save_api_config")
async def save_api_config(api_config: dict):
    """保存API配置到config.yaml"""
    try:
        import yaml
        config_path = os.path.join(BASE_DIR, "config.yaml")
        
        # 读取现有配置
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f) or {}
        else:
            full_config = {}
        
        # 更新llm配置
        full_config["llm"] = api_config.get("llm", {})
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(full_config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"[WebUI] API配置已保存到: {config_path}")
        
        # 重新加载配置
        try:
            from scripts.config_loader import config
            config._load_config()
        except:
            pass
        
        return {"status": "success", "message": "API配置保存成功"}
    except Exception as e:
        error_msg = f"API配置保存失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.get("/api/get_render_config")
async def get_render_config():
    """获取渲染配置"""
    try:
        import yaml
        config_path = os.path.join(BASE_DIR, "config.yaml")
        
        # 如果配置文件不存在，返回默认配置
        if not os.path.exists(config_path):
            return {
                "status": "success",
                "config": {
                    "basic": {
                        "render_enabled": False,
                        "render_mode": "comfyui",
                        "output_root": "output/"
                    },
                    "comfyui": {
                        "server_url": "http://127.0.0.1:8188",
                        "workflow_template": "workflow_api.json",
                        "timeout": 300
                    }
                }
            }
        
        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            full_config = yaml.safe_load(f)
        
        # 返回渲染相关配置
        render_config = {
            "basic": {
                "render_enabled": full_config.get("basic", {}).get("render_enabled", False),
                "render_mode": full_config.get("basic", {}).get("render_mode", "comfyui"),
                "output_root": full_config.get("basic", {}).get("output_root", "output/")
            },
            "comfyui": full_config.get("comfyui", {
                "server_url": "http://127.0.0.1:8188",
                "workflow_template": "workflow_api.json",
                "timeout": 300
            })
        }
        
        return {"status": "success", "config": render_config}
    except Exception as e:
        error_msg = f"获取渲染配置失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.post("/api/save_render_config")
async def save_render_config(render_config: dict):
    """保存渲染配置到config.yaml"""
    try:
        import yaml
        config_path = os.path.join(BASE_DIR, "config.yaml")
        
        # 读取现有配置
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                full_config = yaml.safe_load(f) or {}
        else:
            full_config = {}
        
        # 更新basic配置
        if "basic" in render_config:
            if "basic" not in full_config:
                full_config["basic"] = {}
            full_config["basic"].update(render_config["basic"])
        
        # 更新comfyui配置
        if "comfyui" in render_config:
            full_config["comfyui"] = render_config["comfyui"]
        
        # 保存配置
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(full_config, f, allow_unicode=True, default_flow_style=False)
        
        print(f"[WebUI] 渲染配置已保存到: {config_path}")
        
        # 重新加载配置
        try:
            from scripts.config_loader import config
            config._load_config()
        except:
            pass
        
        return {"status": "success", "message": "渲染配置保存成功"}
    except Exception as e:
        error_msg = f"渲染配置保存失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.post("/api/test_api_connection")
async def test_api_connection(test_config: dict):
    """测试API连接"""
    try:
        provider = test_config.get("provider", "siliconflow")
        api_key = test_config.get("api_key", "")
        base_url = test_config.get("base_url", "")
        model = test_config.get("model", "")
        
        if not api_key:
            return {"status": "error", "message": "API密钥不能为空"}
        
        print(f"[WebUI] 测试 {provider} API连接...")
        
        # 根据提供商类型测试连接
        if provider == "siliconflow":
            # SiliconFlow使用OpenAI兼容接口
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url or "https://api.siliconflow.cn/v1"
                )
                # 发送一个简单的测试请求
                response = client.chat.completions.create(
                    model=model or "deepseek-ai/DeepSeek-V3.2",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print(f"[WebUI] SiliconFlow连接测试成功")
                return {"status": "success", "message": "SiliconFlow连接测试成功"}
            except Exception as e:
                error_msg = str(e)
                print(f"[WebUI] SiliconFlow连接测试失败: {error_msg}")
                return {"status": "error", "message": f"连接测试失败: {error_msg}"}
        
        elif provider == "openai":
            try:
                from openai import OpenAI
                client = OpenAI(
                    api_key=api_key,
                    base_url=base_url or "https://api.openai.com/v1"
                )
                response = client.chat.completions.create(
                    model=model or "gpt-4o",
                    messages=[{"role": "user", "content": "Hello"}],
                    max_tokens=5
                )
                print(f"[WebUI] OpenAI连接测试成功")
                return {"status": "success", "message": "OpenAI连接测试成功"}
            except Exception as e:
                error_msg = str(e)
                print(f"[WebUI] OpenAI连接测试失败: {error_msg}")
                return {"status": "error", "message": f"连接测试失败: {error_msg}"}
        
        elif provider == "anthropic":
            try:
                import anthropic
                client = anthropic.Anthropic(
                    api_key=api_key,
                    base_url=base_url or "https://api.anthropic.com"
                )
                response = client.messages.create(
                    model=model or "claude-3-opus-20240229",
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hello"}]
                )
                print(f"[WebUI] Anthropic连接测试成功")
                return {"status": "success", "message": "Anthropic连接测试成功"}
            except Exception as e:
                error_msg = str(e)
                print(f"[WebUI] Anthropic连接测试失败: {error_msg}")
                return {"status": "error", "message": f"连接测试失败: {error_msg}"}
        
        else:
            # 其他提供商，返回提示信息
            return {"status": "success", "message": f"{provider} 配置已保存，请在实际使用中验证连接"}
    
    except Exception as e:
        error_msg = f"API连接测试失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.get("/api/get_episodes")
async def get_episodes():
    """获取所有生成的剧集信息"""
    episodes = []
    output_full_path = os.path.join(BASE_DIR, output_dir)
    if os.path.exists(output_full_path):
        for item in os.listdir(output_full_path):
            if item.startswith("episode_"):
                episode_path = os.path.join(output_full_path, item)
                if os.path.isdir(episode_path):
                    # 读取分镜文件
                    storyboard_path = os.path.join(episode_path, "storyboard.json")
                    if os.path.exists(storyboard_path):
                        try:
                            with open(storyboard_path, 'r', encoding='utf-8') as f:
                                storyboard = json.load(f)
                            episodes.append({
                                "id": item,
                                "seq": storyboard.get("episode_seq", 0),
                                "shot_count": len(storyboard.get("storyboard", []))
                            })
                        except Exception as e:
                            print(f"读取分镜文件失败：{e}")
    return {"episodes": episodes}

@app.get("/api/get_storyboard/{episode_id}")
async def get_storyboard(episode_id: str):
    """获取指定剧集的分镜信息"""
    output_full_path = os.path.join(BASE_DIR, output_dir)
    episode_path = os.path.join(output_full_path, episode_id)
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    if not os.path.exists(storyboard_path):
        return JSONResponse(status_code=404, content={"status": "error", "message": "分镜文件不存在"})
    
    try:
        with open(storyboard_path, 'r', encoding='utf-8') as f:
            storyboard = json.load(f)
        return {"status": "success", "storyboard": storyboard}
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": f"读取分镜文件失败：{str(e)}"})

@app.get("/api/get_preview/{episode_id}")
async def get_preview(episode_id: str):
    """获取预览数据"""
    output_full_path = os.path.join(BASE_DIR, output_dir)
    episode_path = os.path.join(output_full_path, episode_id)
    preview_data = {
        "storyboard": None,
        "image_prompts": [],
        "audio_prompts": []
    }
    
    # 读取分镜文件
    storyboard_path = os.path.join(episode_path, "storyboard.json")
    if os.path.exists(storyboard_path):
        try:
            with open(storyboard_path, 'r', encoding='utf-8') as f:
                preview_data["storyboard"] = json.load(f)
        except Exception as e:
            print(f"读取分镜文件失败：{e}")
    
    # 读取提示词文件
    prompt_package_path = os.path.join(episode_path, "prompt_package")
    if os.path.exists(prompt_package_path):
        # 读取图像提示词
        image_prompts_path = os.path.join(prompt_package_path, "image_prompts.txt")
        if os.path.exists(image_prompts_path):
            try:
                with open(image_prompts_path, 'r', encoding='utf-8') as f:
                    preview_data["image_prompts"] = f.readlines()
            except Exception as e:
                print(f"读取图像提示词失败：{e}")
        
        # 读取音频提示词
        audio_prompts_path = os.path.join(prompt_package_path, "audio_prompts.txt")
        if os.path.exists(audio_prompts_path):
            try:
                with open(audio_prompts_path, 'r', encoding='utf-8') as f:
                    preview_data["audio_prompts"] = f.readlines()
            except Exception as e:
                print(f"读取音频提示词失败：{e}")
    
    return {"status": "success", "data": preview_data}

@app.get("/api/get_assets")
async def get_assets():
    """获取资产库信息"""
    try:
        from scripts.components.utils.asset_library import asset_library
        characters = asset_library.list_characters()
        scenes = asset_library.list_scenes()
        props = asset_library.list_props()
        styles = asset_library.list_styles()
        return {
            "status": "success",
            "data": {
                "characters": characters,
                "scenes": scenes,
                "props": props,
                "styles": styles
            }
        }
    except Exception as e:
        print(f"获取资产库信息失败：{e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/save_style")
async def save_style(style_data: dict):
    """保存风格模板"""
    try:
        from scripts.components.utils.asset_library import asset_library
        style_name = style_data.get("name")
        style_content = style_data.get("content")
        if not style_name or not style_content:
            return {"status": "error", "message": "缺少风格名称或内容"}
        success = asset_library.save_style(style_name, style_content)
        if success:
            return {"status": "success", "message": "风格模板保存成功"}
        else:
            return {"status": "error", "message": "风格模板保存失败"}
    except Exception as e:
        print(f"保存风格模板失败：{e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/get_style/{style_name}")
async def get_style(style_name: str):
    """获取风格模板"""
    try:
        from scripts.components.utils.asset_library import asset_library
        style = asset_library.get_style(style_name)
        if style:
            return {"status": "success", "data": style}
        else:
            return {"status": "error", "message": "风格模板不存在"}
    except Exception as e:
        print(f"获取风格模板失败：{e}")
        return {"status": "error", "message": str(e)}

@app.get("/api/get_audit_results/{episode_id}")
async def get_audit_results(episode_id: str):
    """获取审核结果"""
    try:
        # 这里可以添加获取审核结果的逻辑
        return {"status": "success", "data": {"audit_results": []}}
    except Exception as e:
        print(f"获取审核结果失败：{e}")
        return {"status": "error", "message": str(e)}

@app.post("/api/pause_task")
async def pause_task():
    """暂停任务"""
    global is_paused
    is_paused = True
    return {"status": "success", "message": "任务已暂停"}

@app.post("/api/resume_task")
async def resume_task():
    """继续任务"""
    global is_paused
    is_paused = False
    return {"status": "success", "message": "任务已继续"}

@app.post("/api/stop_task")
async def stop_task():
    """停止任务"""
    global task_running, task_process, is_paused
    if task_process:
        task_process.terminate()
        task_process = None
    task_running = False
    is_paused = False
    return {"status": "success", "message": "任务已停止"}

@app.get("/api/export_config")
async def export_config():
    """导出配置"""
    try:
        import yaml
        config_path = os.path.join(BASE_DIR, "config.yaml")
        
        if not os.path.exists(config_path):
            return JSONResponse(status_code=404, content={"status": "error", "message": "配置文件不存在"})
        
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
        
        return FileResponse(
            config_path,
            filename="config.yaml",
            media_type="application/x-yaml"
        )
    except Exception as e:
        error_msg = f"导出配置失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

@app.post("/api/import_config")
async def import_config(file: UploadFile = File(...)):
    """导入配置"""
    try:
        content = await file.read()
        
        # 验证文件内容是否为有效的YAML
        import yaml
        try:
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            return {"status": "error", "message": f"无效的YAML文件: {str(e)}"}
        
        # 保存配置文件
        config_path = os.path.join(BASE_DIR, "config.yaml")
        with open(config_path, 'wb') as f:
            f.write(content)
        
        print(f"[WebUI] 配置已导入到: {config_path}")
        
        # 重新加载配置
        try:
            from scripts.config_loader import config
            config._load_config()
        except:
            pass
        
        return {"status": "success", "message": "配置导入成功"}
    except Exception as e:
        error_msg = f"导入配置失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

# 工作流状态管理
workflow_state = {
    "running": False,
    "current_step": 0,
    "detailed_progress": [],
    "overall_progress": {
        "current": 0,
        "total": 0,
        "status": ""
    },
    "estimated_time": 0,
    "completed": False,
    "start_time": None
}

@app.post("/api/start_full_workflow")
async def start_full_workflow(request: Request):
    """启动一键生成完整工作流"""
    global task_running, task_process, is_paused, workflow_state
    
    try:
        data = await request.json()
        template_id = data.get("template_id")
        episodes_count = data.get("config")
        
        if task_running:
            return {"status": "error", "message": "任务正在运行中，请先停止当前任务"}
        
        print(f"[WebUI] 启动完整工作流，模板: {template_id}, 集数: {episodes_count}")
        
        # 初始化工作流状态
        workflow_state = {
            "running": True,
            "current_step": 1,  # 从第2步开始（上传已完成）
            "detailed_progress": [],
            "overall_progress": {
                "current": 0,
                "total": int(episodes_count) if episodes_count else 98,
                "status": "初始化工作流"
            },
            "estimated_time": 0,
            "completed": False,
            "start_time": time.time()
        }
        
        # 启动任务
        task_running = True
        is_paused = False
        
        # 在后台线程中运行主流程
        import threading
        def run_pipeline():
            global task_running, workflow_state
            try:
                print("[WebUI] 开始运行主流程...")
                
                # 更新步骤：语义分析
                workflow_state["current_step"] = 2
                workflow_state["overall_progress"]["status"] = "语义分析中"
                add_detailed_progress(workflow_state, "语义分析", 0, "进行中")
                
                # 这里应该调用实际的主流程
                # from scripts.main_pipeline_v3 import main as run_main_pipeline
                # run_main_pipeline()
                
                # 模拟进度更新（实际使用时替换为真实逻辑）
                total_episodes = workflow_state["overall_progress"]["total"]
                for i in range(1, min(total_episodes + 1, 6)):  # 模拟前5集
                    if not task_running:
                        break
                    
                    workflow_state["current_step"] = 3  # 分集生成
                    workflow_state["detailed_progress"] = []
                    
                    for step_name in ["分集生成", "剧本创作", "台词生成", "分镜设计", "音频设计", "渲染打包"]:
                        if not task_running:
                            break
                        
                        add_detailed_progress(
                            workflow_state, 
                            f"第{i}集 - {step_name}", 
                            50 * (i / total_episodes),
                            "进行中"
                        )
                        
                        workflow_state["overall_progress"]["current"] = i
                        workflow_state["overall_progress"]["status"] = f"正在处理第{i}集"
                        
                        # 计算预计时间
                        elapsed = time.time() - workflow_state["start_time"]
                        if i > 0:
                            avg_time_per_episode = elapsed / i
                            remaining = (total_episodes - i) * avg_time_per_episode
                            workflow_state["estimated_time"] = remaining
                        
                        time.sleep(2)  # 模拟处理时间
                
                # 完成
                workflow_state["completed"] = True
                workflow_state["running"] = False
                workflow_state["overall_progress"]["status"] = "已完成"
                workflow_state["current_step"] = 8  # 所有步骤完成
                task_running = False
                
                print("[WebUI] 主流程执行完成")
                
            except Exception as e:
                print(f"[WebUI] 主流程执行失败: {str(e)}")
                workflow_state["running"] = False
                workflow_state["overall_progress"]["status"] = "失败"
                task_running = False
        
        thread = threading.Thread(target=run_pipeline)
        thread.daemon = True
        thread.start()
        
        return {"status": "success", "message": "工作流已启动"}
    
    except Exception as e:
        error_msg = f"启动工作流失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        return {"status": "error", "message": error_msg}


def add_detailed_progress(state, name, percentage, status):
    """添加详细进度项"""
    progress_item = {
        "name": name,
        "percentage": percentage,
        "status": status
    }
    
    # 更新或添加进度项
    found = False
    for i, item in enumerate(state["detailed_progress"]):
        if item["name"] == name:
            state["detailed_progress"][i] = progress_item
            found = True
            break
    
    if not found:
        state["detailed_progress"].append(progress_item)


@app.get("/api/get_detailed_progress")
async def get_detailed_progress():
    """获取详细进度信息"""
    return {
        "status": "success",
        "data": {
            "current_step": workflow_state["current_step"],
            "detailed_progress": workflow_state["detailed_progress"],
            "overall_progress": workflow_state["overall_progress"],
            "estimated_time": workflow_state["estimated_time"],
            "completed": workflow_state["completed"]
        }
    }

@app.get("/api/smart_recommend")
async def smart_recommend():
    """智能配置推荐 - 根据小说内容和模板推荐最佳配置"""
    try:
        # 检查是否有上传的小说
        novel_path = os.path.join(BASE_DIR, "input", "novel.txt")
        
        recommendations = {}
        
        if os.path.exists(novel_path):
            # 读取小说内容进行分析
            with open(novel_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的文本分析（实际项目中可以使用更复杂的NLP）
            content_length = len(content)
            
            # 根据内容长度推荐集数
            if content_length < 50000:
                episodes = 10
                reason = "小说较短，建议生成10集短剧"
            elif content_length < 100000:
                episodes = 30
                reason = "中等长度，建议生成30集"
            elif content_length < 200000:
                episodes = 60
                reason = "较长小说，建议生成60集"
            else:
                episodes = 98
                reason = "长篇小说，建议生成98集完整系列"
            
            recommendations["episodes"] = {
                "name": "推荐集数",
                "value": f"{episodes}集",
                "reason": reason
            }
            
            # 检测关键词推荐风格
            keywords = {
                "古风": ["武功", "江湖", "侠客", "剑", "内功", "修仙"],
                "现代": ["公司", "总裁", "职场", "都市", "手机", "电脑"],
                "科幻": ["飞船", "机器人", "AI", "未来", "太空", "科技"],
                "言情": ["喜欢", "爱", "心动", "表白", "约会", "浪漫"],
                "悬疑": ["谋杀", "侦探", "线索", "真相", "谜团", "秘密"]
            }
            
            best_style = None
            max_count = 0
            
            for style, words in keywords.items():
                count = sum(1 for word in words if word in content)
                if count > max_count:
                    max_count = count
                    best_style = style
            
            if best_style:
                style_map = {
                    "古风": "ancient",
                    "现代": "modern", 
                    "科幻": "scifi",
                    "言情": "romance",
                    "悬疑": "suspense"
                }
                
                recommendations["style"] = {
                    "name": "推荐风格模板",
                    "value": f"{best_style}风格",
                    "reason": f"检测到{max_count}个相关关键词"
                }
                
                recommendations["template"] = {
                    "name": "推荐使用模板",
                    "value": style_map.get(best_style, "modern"),
                    "reason": "根据小说内容自动匹配最佳模板"
                }
            
            # 推荐模型配置
            recommendations["model"] = {
                "name": "推荐LLM模型",
                "value": "SiliconFlow (DeepSeek-V3.2)",
                "reason": "性价比高，中文理解能力强"
            }
            
            # 推荐渲染设置
            recommendations["render"] = {
                "name": "渲染模式",
                "value": "ComfyUI (本地渲染)",
                "reason": "本地渲染更稳定，无网络依赖"
            }
        
        return {
            "status": "success",
            "recommendations": recommendations
        }
    
    except Exception as e:
        error_msg = f"智能推荐失败: {str(e)}"
        print(f"[WebUI] {error_msg}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": error_msg}

if __name__ == "__main__":
    # 自动打开浏览器
    import webbrowser
    webbrowser.open("http://localhost:8989")
    uvicorn.run(app, host="0.0.0.0", port=8989)
