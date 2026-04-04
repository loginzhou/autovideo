@echo off
chcp 65001 >nul 2>&1
title Novel2Shorts V4.0 - One-Click Installer
color 0A

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║        Novel2Shorts V4.0 - Windows One-Click Installer       ║
echo ║     AI-Powered Short Video Production Pipeline                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: ==================== 检查Python ====================
echo [1/6] Checking Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Please install Python 3.10+ first.
    echo         Download: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [OK] Python %PYVER% found

:: 检查版本是否 >= 3.10
python -c "import sys; exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Python version may be too old. Recommended: 3.10+
)

echo.

:: ==================== 创建虚拟环境 ====================
echo [2/6] Creating virtual environment...
if exist "venv" (
    echo [SKIP] Virtual environment already exists
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created at .\venv
)

echo.

:: ==================== 激活虚拟环境并安装依赖 ====================
echo [3/6] Installing dependencies...
call venv\Scripts\activate.bat

pip install --upgrade pip >nul 2>&1

echo     Installing core dependencies...
pip install pyyaml>=6.0 >nul 2>&1
pip install tqdm>=4.65.0 >nul 2>&1
pip install requests>=2.31.0 >nul 2>&1
pip install openai>=1.0.0 >nul 2>&1
pip install fastapi>=0.100.0 >nul 2>&1
pip install uvicorn>=0.23.0 >nul 2>&1
pip install python-multipart>=0.0.6 >nul 2>&1
pip install numpy>=1.24.0 >nul 2>&1

echo     Installing optional dependencies...
pip install ffmpeg-python>=0.2.0 >nul 2>&1
pip install pandas>=2.0.0 >nul 2>&1

echo     Installing WebUI dependencies...
pip install aiofiles>=23.0.0 >nul 2>&1

echo [OK] All dependencies installed
echo.

:: ==================== 创建必要目录 ====================
echo [4/6] Creating directories...
if not exist "output" mkdir output
if not exist "output\cache" mkdir output\cache
if not exist "scripts\input" mkdir scripts\input
if not exist "assets" mkdir assets
if not exist "assets\library" mkdir assets\library
echo [OK] Directories created
echo.

:: ==================== 创建配置文件 ====================
echo [5/6] Creating default configuration...
if not exist "config.yaml" (
    (
        echo basic:
        echo   test_mode_episodes: 3
        echo   render_enabled: false
        echo   target_platform: tiktok
        echo   content_strategy: romance_domination_strategy
        echo   target_audience: western_female_18_35
        echo.
        echo llm:
        echo   default_provider: siliconflow
        echo   siliconflow:
        echo     api_key: YOUR_API_KEY_HERE
        echo     base_url: https://api.siliconflow.cn/v1
        echo     model: deepseek-ai/DeepSeek-V3.2
        echo.
        echo screenwriter:
        echo   enable_ai_generation: true
        echo   model: deepseek-ai/DeepSeek-V3.2
        echo   temperature: 0.75
        echo   cache_enabled: true
        echo   structure_type: vertical_drama_golden
        echo   arc_type: positive_change
        echo.
        echo director:
        echo   enable_ai_generation: false
        echo   default_style: nolan
        echo   cache_enabled: true
        echo.
        echo audio_design:
        echo   provider: siliconflow
        echo   model: deepseek-ai/DeepSeek-V3.2
    ) > config.yaml
    echo [OK] Default config.yaml created
) else (
    echo [SKIP] config.yaml already exists
)
echo.

:: ==================== 完成 ====================
echo [6/6] Installation complete!
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                    Installation Complete!                   ║
echo ╠══════════════════════════════════════════════════════════════╣
echo ║                                                                ║
echo ║  Next Steps:                                                   ║
echo ║  1. Edit config.yaml - Add your LLM API key                  ║
echo ║  2. Run: start.bat                                             ║
echo ║  3. Open: http://localhost:8000                                ║
echo ║                                                                ║
echo ║  Quick Start Commands:                                         ║
echo ║    start.bat          - Launch WebUI                           ║
echo ║    start_pipeline.bat  - Run pipeline directly                  ║
echo ║                                                                ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.

:: 创建启动脚本
(
    echo @echo off
    echo chcp 65001 ^>nul 2^>^&1
    echo title Novel2Shorts V4.0 - WebUI
    echo call venv\Scripts\activate.bat
    echo cd webui
    echo python main.py
    echo pause
) > start.bat

(
    echo @echo off
    echo chcp 65001 ^>nul 2^>^&1
    echo title Novel2Shorts V4.0 - Pipeline
    echo call venv\Scripts\activate.bat
    echo python scripts/main_pipeline_v3.py
    echo pause
) > start_pipeline.bat

echo [OK] Created start.bat and start_pipeline.bat
echo.

pause
