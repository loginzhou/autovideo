# Novel2Shorts V4.0 - AI-Powered Short Video Production Pipeline

<p align="center">
  <strong>Novel-to-Video AI Production System | Platform-Optimized for TikTok & Facebook</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-4.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/Python-3.10+-green" alt="Python">
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
</p>

---

## What is Novel2Shorts?

**Novel2Shorts** is an end-to-end AI production pipeline that converts **novels into platform-optimized short videos** (TikTok, Facebook Reels, Instagram Reels). It handles everything from novel ingestion to render-ready video packages with cinematic-quality storyboards, professional audio design, and dialogue generation.

### Target Audience
- **Primary**: Western female audiences (18-45) on TikTok/Facebook
- **Content Types**: Romance, Empowerment/Revenge, Mystery/Paranormal short dramas

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     WebUI (Vue3 + Element Plus)                  │
│   Platform Selector │ Strategy Picker │ Template System         │
└──────────────────────┬──────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────────┐
│                    Main Pipeline V3                              │
│                                                                 │
│  Novel → Chunking → Analysis → Blueprint → Episodes            │
│     ↓         ↓          ↓           ↓          ↓              │
│  Screenwriter V8  →  Dialogue  →  Director V8  →  Audio        │
│  (Platform-Optimized)  Master       (Cinematic)    Design       │
│                          ↓             ↓           ↓            │
│                   Video Render Packager (Sora/Runway/Pika/SVD)  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Modules (V4.0)

| Module | Version | Description |
|--------|---------|-------------|
| **Screenwriter Pro Agent** | V8 | Hollywood-grade prompt engineering with platform optimization |
| **Director AI Agent** | V8 | Cinematic shot language with emotion-driven + platform-aware cinematography |
| **Dialogue Master Agent** | V1 | Natural dialogue with emotion/subtext/delivery metadata |
| **Foley Sound Designer** | V2 | Professional spatial audio, emotional music mapping, psychoacoustic effects |
| **Video Render Packager** | V1 | Multi-format output (Sora/Runway/Pika/SVD) |
| **Western Female Platform Optimizer** | V1 | TikTok/FB Reels specs, content strategies, cultural adaptation |
| **Cinematic Language System** | V1 | 5 director styles (Nolan/Miyazaki/Wong/Spielberg/Fincher) |
| **Emotional Analysis System** | V1 | 3D VAD emotion model, 5 story arc templates |
| **Multimodal Consistency** | V1 | Cross-modality alignment checking |
| **Quality Assessor** | V1 | 16-dimension quality assessment (A-F grading) |

## Platform Optimization (V4.0 New)

### Supported Platforms
| Platform | Optimal Duration | Aspect Ratio | Key Rules |
|----------|-----------------|--------------|-----------|
| **TikTok** | 15-60 seconds | 9:16 vertical | 3-second hook critical, retention hooks every 5-8s |
| **Facebook Reels** | 30-90 seconds | 9:16 vertical | Deeper narrative allowed, slower pacing |
| **Universal** | Custom | Any | No platform-specific rules applied |

### Content Strategies
1. **Romance Domination** - Emotional rollercoaster: sweet→angsty→healing (Highest viral potential)
2. **Empowerment Revenge** - Underestimated force→quiet moves→public takedown (Highest shareability)
3. **Mystery Supernatural** - Impossible event→hidden powers→major sacrifice (Highest binge rate)

## Quick Start

### Prerequisites
- Python 3.10 or higher
- An LLM API key (SiliconFlow/OpenAI/Anthropic/Volcengine/Qwen/Zhipu)
- Git

### One-Click Installation (Windows)

```bash
# Option A: Use the installer script
install.bat

# Option B: Manual installation
pip install -r requirements.txt
```

### Running the WebUI

```bash
cd webui
python main.py
# Open http://localhost:8000 in browser
```

### Configuration

1. **Set up LLM Provider**: WebUI → API Configuration → Enter your API key
2. **Choose Platform**: Basic Config → Target Platform (TikTok/FB Reels/Universal)
3. **Select Strategy**: Content Strategy (Romance/Empowerment/Mystery)
4. **Upload Novel**: Upload your .txt novel file
5. **Click Start**: One-click workflow execution

## Project Structure

```
autovideo/
├── webui/
│   ├── main.py                    # FastAPI backend server
│   └── templates/index.html       # Vue3 frontend (WebUI)
├── scripts/
│   ├── main_pipeline_v3.py        # Main orchestration pipeline
│   ├── config_loader.py           # YAML configuration management
│   ├── config_center.py           # Runtime config access
│   ├── input/novel.txt            # Default novel input
│   └── components/
│       ├── agents/
│       │   ├── Screenwriter_Pro_Agent/     # V8 screenwriter
│       │   ├── Director_AI_Agent/          # V8 cinematographer
│       │   ├── Dialogue_Master_Agent/      # Dialogue generator
│       │   ├── Foley_Sound_Designer_Agent/ # Audio designer V2
│       │   └── Video_Render_Packager/      # Output packager
│       ├── upgrade/
│       │   └── novel_semantic_analyzer/    # V2 emotional analysis
│       └── utils/
│           ├── western_female_platform_optimizer.py  # Platform engine
│           ├── cinematic_language_system.py           # Director styles
│           ├── professional_audio_system.py           # Audio system
│           ├── professional_prompt_engineering.py    # Prompt engineering
│           ├── multimodal_consistency.py              # Consistency checker
│           ├── quality_assessor.py                    # Quality scoring
│           ├── asset_manager.py                       # Asset management
│           ├── llm_client.py                           # LLM API client
│           └── prompt_engineering.py                  # Visual/audio prompts
├── requirements.txt               # Python dependencies
├── install.bat                   # Windows one-click installer
└── INSTALLATION.md               # Detailed installation guide
```

## Output Format

Each generated episode produces:

```
output/
├── episode_001/
│   ├── screenplay.json           # Script with beats & metadata
│   ├── storyboard.json           # Shots with prompts (visual/video/audio)
│   ├── dialogue.json             # Generated dialogue per shot
│   ├── video_prompts.txt         # Ready for Sora/Runway/Pika
│   └── audio_prompts.txt         # Ready for audio generation
├── episode_002/
│   ...
└── cache/                        # Generation cache for speed
```

## LLM Provider Support

| Provider | Models | Notes |
|----------|--------|-------|
| SiliconFlow | DeepSeek-V3.2, Qwen, etc. | **Recommended** - Best value |
| OpenAI | GPT-4o, GPT-4-turbo | Premium quality |
| Anthropic | Claude-3-opus | Excellent writing |
| Volcengine | Doubao-seed-2.0-pro | Chinese-optimized |
| Zhipu | GLM-4 | Chinese models |
| Qwen | Qwen-max | Alibaba models |

## License

MIT License - Free for personal and commercial use.

## Credits

Built with love for creators who want to bring stories to life through AI.
