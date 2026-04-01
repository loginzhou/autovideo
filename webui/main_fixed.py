from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import sys
import json
import asyncio
from subprocess import Popen, PIPE, STDOUT
import yaml

app = FastAPI(title="Novel2Shorts WebUI")
# 绝对路径定位模板
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# 全局变量
task_running = False
task_process = None
task_logs = []
config = {}
CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config.yaml")
EXAMPLE_CONFIG_PATH = os.path.join(os.path.dirname(BASE_DIR), "config.example.yaml")

# 加载配置
def load_config():
    global config
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        # 复制示例配置
        with open(EXAMPLE_CONFIG_PATH, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True)

load_config()
output_dir = config.get('basic', {}).get('output_root', 'output/')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "config": config})

@app.post("/api/upload_novel")
async def upload_novel(file: UploadFile = File(...)):
    content = await file.read()
    input_path = os.path.join(os.path.dirname(BASE_DIR), "scripts", "input", "novel.txt")
    with open(input_path, "wb") as f:
        f.write(content)
    return {"status": "success", "message": f"小说上传成功，大小：{len(content)}字节"}

@app.post("/api/start_task")
async def start_task():
    global task_running, task_process, task_logs
    if task_running:
        return {"status": "error", "message": "已有任务正在运行"}
    task_logs = []
    task_running = True
    # 启动主流水线
    script_path = os.path.join(os.path.dirname(BASE_DIR), "scripts", "main_pipeline_v3.py")
    task_process = Popen(
        [sys.executable, script_path],
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
        encoding='utf-8',
        cwd=os.path.dirname(BASE_DIR)
    )
    asyncio.create_task(read_task_logs())
    return {"status": "success", "message": "任务启动成功"}

async def read_task_logs():
    global task_running, task_logs, task_process
    while True:
        line = task_process.stdout.readline()
        if not line and task_process.poll() is not None:
            break
        if line:
            task_logs.append(line.strip())
    task_running = False

@app.get("/api/get_logs")
async def get_logs():
    return {"logs": task_logs, "running": task_running}

@app.get("/api/download_output")
async def download_output():
    # 打包输出目录
    import shutil
    output_full_path = os.path.join(os.path.dirname(BASE_DIR), output_dir)
    zip_path = os.path.join(os.path.dirname(BASE_DIR), "output_package.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', output_full_path)
    return FileResponse(zip_path, filename="novel2shorts_output.zip", media_type="application/zip")

@app.get("/api/get_config")
async def get_config():
    return config

@app.post("/api/save_config")
async def save_config(new_config: dict):
    global config
    # 保存配置到config.yaml
    config = new_config
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True)
    return {"status": "success", "message": "配置保存成功"}

if __name__ == "__main__":
    # 自动打开浏览器
    import webbrowser
    webbrowser.open("http://localhost:8989")
    uvicorn.run(app, host="0.0.0.0", port=8989)
