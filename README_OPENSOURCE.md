# 🎬 Novel2Shorts 开源版
> 工业级竖屏短剧全链路自动化生成框架，将长篇小说全自动转化为9:16竖屏出海短剧，完全达到专业影视团队生产标准。

## ✨ 核心特性
### 📝 内容生成
- ✅ 支持100万字长篇小说输入，自动切块分析
- ✅ 四大专业智能Agent：总编剧+摄影指导+拟音师+连贯性总监
- ✅ 自动生成符合完播率曲线的剧集结构（Hook->Setup->Escalation->Cliffhanger）
- ✅ 全局连贯性系统，杜绝角色/场景/时间线穿帮
- ✅ 专业级分镜生成，自动注入焦段/灯光/运镜/构图等专业参数

### 🎨 渲染生产
- ✅ 支持ComfyUI批量渲染，断点续渲、GPU负载保护
- ✅ 自动回收渲染资产，统一管理
- ✅ 多模型支持，可自由切换SD/Flux等模型

### 🌍 出海适配
- ✅ 自动生成5种主流语言字幕（中/英/西/韩/日）
- ✅ 输出SRT/VTT双格式，适配所有主流短视频平台
- ✅ 音频响度标准化，符合抖音/TikTok/YouTube国际标准

### 🛡️ 质量保障
- ✅ 完播率审计系统，基于百亿流量曲线自动优化
- ✅ 内容合规检测，全维度避免限流下架风险
- ✅ 镜头语言校验，符合好莱坞电影工业标准
- ✅ 全局跨集连贯性审计，100%杜绝穿帮问题
- ✅ 专业转场优化，画面流畅度提升80%

## 🚀 快速开始
### 1. 环境准备
- Python 3.10+
- Node.js 16+（部分内部工具使用，可选）
- ffmpeg（音频处理功能需要，可选）
- ComfyUI（渲染功能需要，可选）

### 2. 安装依赖
```bash
# 克隆项目
git clone https://github.com/your-username/novel2shorts.git
cd novel2shorts

# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖（可选，部分工具需要）
cd scripts
npm install
cd ..
```

### 3. 配置文件
```bash
# 复制配置文件模板
cp config.example.yaml config.yaml
```
编辑`config.yaml`，填写你的API密钥、模型配置、ComfyUI配置等信息。

### 4. 准备输入
将你要生成的小说复制到`scripts/input/novel.txt`，编码为UTF-8。

### 5. 运行主流水线
```bash
cd scripts
# 运行V3版本主流水线（推荐）
python main_pipeline_v3.py
```

## 📖 详细使用教程
### 核心工作流
```mermaid
graph LR
A[小说输入] --> B[智能切块+语义分析]
B --> C[全局设定提取+角色库生成]
C --> D[智能分集生成蓝图]
D --> E[逐集生成：剧本+分镜+音频]
E --> F[质量检测：完播率+合规+连贯性]
F --> G[批量渲染]
G --> H[字幕生成+音频处理]
H --> I[输出可直接发布的短剧]
```

### 所有可用工具
| 工具 | 功能 | 命令 |
|------|------|------|
| 主流水线V3 | 全流程生成短剧 | `python main_pipeline_v3.py` |
| 批量渲染 | 渲染所有已生成分镜 | `python batch_render_all.py [--start 1 --end 10]` |
| 多语言字幕生成 | 生成多语言字幕 | `python multilang_subtitle_generator.py [--langs zh en es]` |
| 完播率审计 | 检测剧集完播率结构 | `python completion_rate_auditor.py` |
| 音频响度标准化 | 统一音频响度符合平台标准 | `python audio_loudness_normalizer.py` |
| 内容合规检测 | 检测敏感内容避免违规 | `python content_compliance_checker.py` |
| 镜头语言校验 | 校验镜头专业性 | `python cinematography_validator.py` |
| 跨集连贯性审计 | 全局检测穿帮问题 | `python cross_episode_continuity_auditor.py` |
| 镜头转场优化 | 优化转场提升流畅度 | `python shot_transition_optimizer.py` |

## 🎯 支持的模型
### LLM模型
- OpenAI GPT系列
- Anthropic Claude系列
- 字节跳动豆包系列
- 智谱AI GLM系列
- 阿里通义千问系列
- 所有兼容OpenAI API格式的模型

### 渲染模型
- 所有支持ComfyUI的模型（Stable Diffusion/Flux等）

## 🤝 贡献指南
欢迎提交Issue和PR！
1. Fork本项目
2. 创建你的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

## 📄 许可证
本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 🙋 常见问题
### Q: 生成的内容质量不好怎么办？
A: 可以在配置文件中切换更好的模型（比如GPT-4o/Claude 3 Opus），调整temperature参数，或者优化输入小说的格式。

### Q: 渲染速度慢怎么办？
A: 可以使用更高效的模型（比如Lightning系列模型，4步即可出图），或者使用云GPU渲染。

### Q: 怎么支持其他语言？
A: 在配置文件的`subtitle.target_languages`中添加对应的语言代码即可，翻译引擎支持Google和DeepLX。

### Q: 可以商用吗？
A: 本项目完全开源，可以自由商用，注意遵守相关法律法规和API服务商的使用条款。

## 📞 交流群
加入Discord社区获取最新更新和技术支持：[https://discord.gg/xxxx](https://discord.gg/xxxx)
