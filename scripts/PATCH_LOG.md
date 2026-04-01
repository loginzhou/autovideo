# 架构补丁记录
---
## 2026-03-28 补丁1：工业级控制字段补丁
- 新增Phase0资产注册中枢`assets_registry.json`，锁定所有视觉/声音资产ID
- 更新分镜Schema，新增`generation_mode/reference_assets/first_frame_override/transition_to_next/bgm_cue/safety_check_focus`全量工业级控制字段
- 实现四重校验机制：格式校验→规则校验→连戏校验→资产绑定校验

## 2026-03-28 补丁2：原子化写入+路径校验补丁
- 新增路径校验模块，任务启动前强制检测所有路径写权限，无权限直接终止
- 取消内存缓存机制，所有Agent任务完成后必须先写入物理磁盘，再返回结果
- 彻底杜绝内容丢失/写入失败问题
