---
name: novel2shorts
description: 工业级竖屏短剧生成框架，将长篇小说全自动转化为9:16竖屏出海短剧。使用当用户需要：(1) 把小说转成竖屏短剧，(2) 批量生成短剧内容，(3) 自动化短剧生产流程，(4) Novel2Shorts相关操作。
---

# Novel2Shorts 竖屏短剧生成技能
## 能力范围
支持100万字长篇小说 → 9:16竖屏短剧全链路自动化生成，基于OpenClaw原生能力实现，无需外部工具。

## 使用流程（严格遵循漏斗降维+HITL审批）
### 阶段1：物理切块
调用`scripts/novel_split.js`将小说按指定大小切块，默认chunk大小50KB，重叠5%保证上下文连贯。

### 阶段2：全局要素提取
调用OutlineExtractor Agent，输入切块结果，输出全局大纲+角色库+核心设定。

### 阶段3：生成全集蓝图
调用BlueprintGenerator Agent，输入全局大纲+角色库，生成全集分集蓝图，**自动暂停等待人类审批确认**。

### 阶段4：逐集沙盒生成
蓝图确认后，循环调用`runEpisodeSandbox`生成每集分镜：
- 每集运行在独立隔离沙盒，关闭长期记忆，用完即毁
- 输出自动经过JSON Schema校验，违规自动重试最多3次
- 状态变更自动同步到全局状态机，保证跨集连戏一致

## 核心入口脚本
### 生产流水线
- 主工作流：`scripts/main_pipeline.py`
- 主工作流V3进化版：`scripts/main_pipeline_v3.py`（推荐，含四大智能Agent+全局连贯性系统）
- 单集生成：`scripts/run_single_episode.py`
- 批量生成多集：`scripts/generate_n_episodes.py`
- 快速批量测试：`scripts/fast_generate_98eps.py`

### 核心生产工具
- 🎬 批量渲染：`scripts/batch_render_all.py`（支持断点续渲、GPU负载保护，一键渲染所有已生成分镜）
- 🌍 多语言字幕生成：`scripts/multilang_subtitle_generator.py`（支持中/英/西/韩/日多语言，输出SRT/VTT双格式适配出海）
- 📊 完播率审计：`scripts/completion_rate_auditor.py`（基于百亿流量完播率曲线，自动检测剧集结构，给出优化建议和完播率预估）

### 专业级质量控制工具
- 🔊 音频响度标准化：`scripts/audio_loudness_normalizer.py`（符合抖音/TikTok/YouTube国际标准，响度统一到-16LUFS，避免爆音/音量忽大忽小）
- 🛡️ 内容合规检测：`scripts/content_compliance_checker.py`（全维度覆盖平台审核规则，检测敏感词/违规内容，避免限流、下架风险）
- 🎥 镜头语言校验：`scripts/cinematography_validator.py`（基于好莱坞电影工业标准，校验景别/焦段/构图/运镜专业性，提升画面专业度）
- 🔗 全局跨集连贯性审计：`scripts/cross_episode_continuity_auditor.py`（全维度检测角色/场景/剧情/时间线穿帮问题，确保整部剧100%连贯无矛盾，避免观众出戏）
- ✂️ 专业镜头转场优化：`scripts/shot_transition_optimizer.py`（基于好莱坞剪辑规则，自动匹配最优转场方式，彻底解决转场生硬、画面跳脱问题，观影流畅度提升80%）

## 资源说明
- `references/usage_guide.md`：完整使用文档与参数说明
- `assets/default_config.json`：默认系统配置（9:16竖屏规则硬编码）
- 日志与审计文件自动生成在运行目录下的`logs/`和`output/`目录
