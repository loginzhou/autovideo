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
from scripts.config_loader import config

app = FastAPI(title="Novel2Shorts WebUI")
templates = Jinja2Templates(directory="webui/templates")

# 全局变量
task_running = False
task_process = None
task_logs = []
output_dir = config.get('basic.output_root', 'output/')

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "config": config._config})

@app.post("/api/upload_novel")
async def upload_novel(file: UploadFile = File(...)):
    content = await file.read()
    with open("scripts/input/novel.txt", "wb") as f:
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
    task_process = Popen(
        [sys.executable, "scripts/main_pipeline_v3.py"],
        stdout=PIPE,
        stderr=STDOUT,
        text=True,
        encoding='utf-8'
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
    shutil.make_archive("output_package", 'zip', output_dir)
    return FileResponse("output_package.zip", filename="novel2shorts_output.zip", media_type="application/zip")

@app.get("/api/get_config")
async def get_config():
    return config._config

@app.post("/api/save_config")
async def save_config(new_config: dict):
    # 保存配置到config.yaml
    import yaml
    with open("config.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(new_config, f, allow_unicode=True)
    # 重新加载配置
    config._load_config()
    return {"status": "success", "message": "配置保存成功"}

if __name__ == "__main__":
    # 自动打开浏览器
    import webbrowser
    webbrowser.open("http://localhost:8989")
    uvicorn.run(app, host="0.0.0.0", port=8989)
