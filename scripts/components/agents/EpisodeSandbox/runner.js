const fs = require('fs');
const path = require('path');
const { v4: uuidv4 } = require('uuid');
const { sessions_spawn } = require('openclaw:core');

const SANDBOX_ROOT = path.resolve(__dirname, '../../../../sandbox/');
const CONFIG_ROOT = path.resolve(__dirname, '../../../../config/');

// 加载全局只读配置
const globalConfig = {
  vertical_screen: JSON.parse(fs.readFileSync(path.join(CONFIG_ROOT, 'vertical_screen_spec.json'), 'utf8')),
  character_schema: JSON.parse(fs.readFileSync(path.join(CONFIG_ROOT, 'character_schema.json'), 'utf8')),
  storyboard_schema: JSON.parse(fs.readFileSync(path.join(CONFIG_ROOT, 'storyboard_schema.json'), 'utf8')),
  model_routing: JSON.parse(fs.readFileSync(path.join(CONFIG_ROOT, 'model_routing.json'), 'utf8'))
};

async function runEpisodeSandbox(episodeBlueprint, currentGlobalState) {
  const episodeUuid = uuidv4();
  const sandboxDir = path.join(SANDBOX_ROOT, episodeUuid);
  fs.mkdirSync(sandboxDir, { recursive: true });
  
  // 写入沙盒输入（只读）
  const inputPayload = {
    global_config: Object.freeze(globalConfig), // 冻结防止修改
    episode_blueprint: episodeBlueprint,
    current_state: Object.freeze(currentGlobalState)
  };
  fs.writeFileSync(path.join(sandboxDir, 'input.json'), JSON.stringify(inputPayload, null, 2));
  
  try {
    // 调用OpenClaw创建隔离沙盒，关闭长期记忆，用完即毁
    const sandboxSession = await sessions_spawn({
      task: `生成单集分镜，严格遵循input.json中的全局配置和竖屏规则，输出符合storyboard_schema的JSON到output.json`,
      runtime: "subagent",
      mode: "run",
      cleanup: "delete", // 运行完成自动销毁沙盒
      model: globalConfig.model_routing.agent_routing.EpisodeSandbox,
      thinking: "off",
      attachments: [
        { name: "input.json", content: JSON.stringify(inputPayload), encoding: "utf8" }
      ]
    });
    
    // 等待沙盒运行完成，获取输出
    const sandboxOutput = JSON.parse(sandboxSession.result);
    
    // 校验输出格式
    const validateResult = await require('../../skills/json-validate/index.js')({
      payload: sandboxOutput,
      schema_path: "storyboard_schema.json"
    });
    
    if (!validateResult.valid && validateResult.retry_allowed) {
      // 重试逻辑
      return runEpisodeSandbox(episodeBlueprint, currentGlobalState, validateResult.retry_count + 1);
    }
    
    if (!validateResult.valid) {
      throw new Error(`分镜校验失败，超过最大重试次数：${JSON.stringify(validateResult.errors)}`);
    }
    
    // 保存输出到沙盒目录
    fs.writeFileSync(path.join(sandboxDir, 'output.json'), JSON.stringify(sandboxOutput, null, 2));
    
    return {
      success: true,
      episode_id: episodeUuid,
      sandbox_dir: sandboxDir,
      output: sandboxOutput
    };
    
  } catch (err) {
    // 异常时清理沙盒
    fs.rmSync(sandboxDir, { recursive: true, force: true });
    return {
      success: false,
      error: err.message
    };
  }
}

module.exports = runEpisodeSandbox;
