# Novel2Shorts V4.0 - Windows Installation Guide

## System Requirements

| Requirement | Minimum | Recommended |
|-------------|---------|-------------|
| **OS** | Windows 10 (64-bit) | Windows 11 (64-bit) |
| **Python** | 3.10+ | 3.11 or 3.12 |
| **RAM** | 8 GB | 16 GB |
| **Disk Space** | 2 GB free | 5 GB free |
| **Network** | Internet (for LLM API) | Stable broadband |

---

## Method 1: One-Click Install (Recommended)

### Step 1: Download or Clone

```bash
git clone https://github.com/loginzhou/autovideo.git
cd autovideo
```

Or download the ZIP from GitHub and extract.

### Step 2: Run Installer

Double-click `install.bat` (right-click → Run as Administrator if needed)

The installer will automatically:
1. ✅ Check Python installation
2. ✅ Create virtual environment (`venv/`)
3. ✅ Install all Python dependencies
4. ✅ Create necessary directories (`output/`, `scripts/input/`, etc.)
5. ✅ Generate default `config.yaml`
6. ✅ Create convenience scripts (`start.bat`, `start_pipeline.bat`)

### Step 3: Configure API Key

Edit `config.yaml` and replace `YOUR_API_KEY_HERE` with your actual API key:

```yaml
llm:
  siliconflow:
    api_key: sk-your-real-api-key-here    # <-- CHANGE THIS
```

**Recommended LLM Providers for Western content:**

| Provider | Cost | Quality | Signup URL |
|----------|------|---------|------------|
| SiliconFlow | $ (Cheapest) | Very Good | https://cloud.siliconflow.cn |
| OpenAI | $$$ | Excellent | https://platform.openai.com |
| Anthropic | $$$ | Best Writing | https://console.anthropic.com |

> **Tip**: For Chinese users, SiliconFlow offers domestic models at very low cost with good English generation quality.

### Step 4: Launch WebUI

Double-click `start.bat`, then open browser to:

```
http://localhost:8000
```

---

## Method 2: Manual Installation

If the one-click installer doesn't work, follow these steps:

### Step 1: Install Python

1. Download from https://www.python.org/downloads/
2. **CRITICAL**: Check "Add Python to PATH" during installation
3. Verify: open Command Prompt, type `python --version`

### Step 2: Create Virtual Environment

```bash
cd autovideo
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
pip install fastapi uvicorn python-multipart aiofiles
```

### Step 4: Create Directories

```bash
mkdir output output\cache scripts\input assets\library
```

### Step 5: Create Config File

Copy the default config or create `config.yaml`:

```yaml
basic:
  test_mode_episodes: 3
  target_platform: tiktok
  content_strategy: romance_domination_strategy
  target_audience: western_female_18_35

llm:
  default_provider: siliconflow
  siliconflow:
    api_key: YOUR_API_KEY_HERE
    base_url: https://api.siliconflow.cn/v1
    model: deepseek-ai/DeepSeek-V3.2

screenwriter:
  enable_ai_generation: true
  model: deepseek-ai/DeepSeek-V3.2
  temperature: 0.75

director:
  enable_ai_generation: false
  default_style: nolan
```

### Step 6: Run

```bash
cd webui
python main.py
```

---

## Method 3: Portable Version (Transfer to Another PC)

### Creating a Portable Package

On the source machine where everything is installed:

```bash
# 1. Activate the venv
call venv\Scripts\activate.bat

# 2. Export dependencies (for reference)
pip freeze > requirements_locked.txt

# 3. Create portable package (exclude venv - too large)
# Use 7-Zip or WinRAR to create a ZIP of the entire folder
# EXCLUDE these folders from the ZIP:
#   - venv\          (virtual environment - will be recreated)
#   - __pycache__\   (Python cache)
#   - output\        (generated outputs)
#   - .git\          (Git metadata)
```

### Installing on Target Machine

1. Extract the ZIP to any folder (e.g., `D:\autovideo`)
2. Double-click `install.bat` - it will recreate venv and install deps
3. Edit `config.yaml` with your API key
4. Double-click `start.bat`

---

## Troubleshooting

### Problem: `python is not recognized`

**Solution**: Python not in PATH. Either:
- Reinstall Python with "Add to PATH" checked
- Or use full path: `C:\Python311\python.exe`

### Problem: ModuleNotFoundError: No module named 'xxx'

**Solution**: Virtual environment not activated. Run:
```bash
venv\Scripts\activate
pip install -r requirements.txt
```

### Problem: Port 8000 already in use

**Solution**: Edit `webui/main.py`, change port number:
```python
uvicorn(app, host="0.0.0.0", port=8001)  # Change to 8001
```

### Problem: LLM API connection error

**Solution**: Check your API key and base URL in config.yaml. Test with:
```bash
python -c "from components.utils.llm_client import get_llm_response; print(get_llm_response('say hi', task_type='test'))"
```

### Problem: Chinese characters display as garbled text

**Solution**: Ensure terminal UTF-8 encoding:
```bash
chcp 65001
```
All `.bat` files include this command automatically.

---

## File Transfer Checklist (Moving to Another PC)

When transferring this project to another Windows computer, you need:

- [ ] The entire project folder (or ZIP archive)
- [ ] Python 3.10+ installed on target machine
- [ ] Run `install.bat` on target machine (creates venv + installs deps)
- [ ] Edit `config.yaml` with new API key
- [ ] Run `start.bat`

**Total transfer size**: ~5 MB (excluding venv and output)

**What gets auto-created by install.bat**:
- `venv/` (~200 MB - Python packages, don't transfer)
- `config.yaml` (default template)
- `start.bat`, `start_pipeline.bat` (launch scripts)
- `output/`, `scripts/input/`, `assets/library/` (directories)

---

## Quick Reference

| Action | Command / Click |
|--------|----------------|
| Install all dependencies | Double-click `install.bat` |
| Start WebUI | Double-click `start.bat` |
| Run pipeline directly | Double-click `start_pipeline.bat` |
| Update dependencies | `pip install -r requirements.txt` |
| Check Python version | `python --version` |
| Clear cache | Delete `output/cache/*` |
| Reset config | Delete `config.yaml`, restart |

---

## Performance Tips

1. **Enable caching** (default ON): Generated episodes are cached, re-running skips completed steps
2. **Test mode**: Set `test_mode_episodes: 3` to only generate 3 episodes for testing
3. **Rule-based mode**: Set `director.enable_ai_generation: false` for faster storyboard generation (uses rules instead of LLM)
4. **Use SiliconFlow**: Much cheaper than OpenAI for similar quality on short video content
