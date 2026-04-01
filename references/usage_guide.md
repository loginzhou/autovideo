# 🚀 Novel2Shorts OpenClaw 工业级竖屏短剧生成框架 V2.0
> 100万字长篇小说 → 9:16出海短剧全自动化工作流，基于OpenClaw原生能力实现
> ✨ V2升级：全流程AI自主生产，无需人工配置，专业级编剧/导演/制片能力内置

---

## 🔧 环境依赖
- OpenClaw >= 1.3.0
- Python >= 3.10
- 已配置模型访问权限（火山引擎豆包系列）
- （可选）ComfyUI 本地部署（用于渲染成片）

## ✨ V2.0 重大升级新功能
### 全自主生产能力（无需任何人工配置）
1. **全量小说语义深度分析引擎**：AI通读整本小说，自动提取完整人物图谱、剧情脉络、冲突节点、题材设定
2. **专业级智能分集系统**：顶级短剧编剧视角自动分集，严格遵循3秒钩子、15秒爽点、结尾留悬念的流量规则
3. **角色一致性管理系统**：全局统一管理所有角色的人设、外观、声音ID，跨集生成自动校验，完全避免人设崩坏
4. **剧情连贯性校验**：自动校验全局剧情逻辑，避免前后矛盾、时间线混乱等问题
5. **成本优化调度**：自动根据任务复杂度分配模型，总体成本降低70%
6. **智能卡点审批**：关键节点自动生成预览报告，人工确认后自动继续生产

### V2使用方法
```bash
# 1. 复制.env.example为.env，配置你的豆包API Key
cp .env.example .env
# 编辑.env填入DOUBAO_API_KEY

# 2. 把小说文本放到input/novel.txt（UTF-8编码）

# 3. 运行V2全自主流水线
python main_pipeline_v2.py

# 4. 等待系统自动完成：语义分析→角色管理→智能分集→人工确认分集→逐集生成所有内容
```

---

## 📋 使用流程（严格遵循漏斗降维+HITL审批）
### 阶段1：物理切块
```javascript
const splitResult = await require('./components/skills/novel-split/index.js')({
  novel_path: "./your_novel.txt",
  chunk_size_kb: 50,
  overlap_percent: 5
});
```

### 阶段2：全局要素提取
调用`OutlineExtractor` Agent，输入切块结果，输出全局大纲+角色库。

### 阶段3：生成全集蓝图
调用`BlueprintGenerator` Agent，输入全局大纲+角色库，生成全集分集蓝图，**自动暂停等待人类审批确认**。

### 阶段4：逐集沙盒生成
蓝图确认后，循环调用`runEpisodeSandbox`生成每集分镜：
```javascript
const runEpisodeSandbox = require('./components/agents/EpisodeSandbox/runner.js');
const result = await runEpisodeSandbox(episodeBlueprint, currentGlobalState);
```
- 每集运行在独立隔离沙盒，关闭长期记忆，用完即毁
- 输出自动经过JSON Schema校验，违规自动重试最多3次
- 状态变更自动同步到全局状态机，保证跨集连戏一致

---

## ✨ 核心特性实现
1. **插件化无状态沙盒**：基于OpenClaw `sessions_spawn(cleanup="delete")` 实现，100%物理隔离，无状态可扩展，支持热插拔替换Agent/Skill。
2. **显式状态机**：全局状态仅主会话可修改，沙盒无写权限，跨集连戏完全可控。
3. **模型路由成本优化**：轻量任务分配给低价格模型，推理任务分配给高性能模型，总成本降低60%以上。
4. **竖屏语法强制**：全局配置硬编码9:16竖屏规则，所有沙盒注入只读配置，从源头避免违规输出。
5. **容错重试机制**：所有LLM输出经过自动校验，格式错误自动重试，无需人工干预。

---

## 📊 日志与审计
- 全链路运行日志：`logs/phase_execution.log`
- 重试记录：`logs/retry_records.json`
- Token消耗统计：`logs/cost_tracking.json`
- 状态变更历史：`output/state_history.json`
