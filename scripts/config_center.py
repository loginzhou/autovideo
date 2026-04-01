"""
集中配置中心
所有可配置参数统一管理，不需要修改代码，直接编辑配置文件即可调整全流程行为
完全人工可控，符合专业生产流程需求
"""
import os
import yaml
from typing import Dict, Any

class ConfigCenter:
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则生成默认配置"""
        default_config = {
            # 基础配置
            "base": {
                "input_novel_path": "input/novel.txt",
                "output_root": "output/",
                "max_episodes": 3, # 最多生成集数，测试用
                "render_enabled": False, # 是否开启视频渲染
            },
            # 大模型配置
            "llm": {
                "api_key": os.getenv("DOUBAO_API_KEY", ""),
                "endpoint": "https://api.siliconflow.cn/v1/chat/completions",
                "default_model": "deepseek-ai/DeepSeek-V3.2",
                "fast_model": "deepseek-ai/DeepSeek-V3-Lite",
                "max_context_tokens": 150000,
                "max_output_tokens": 8192,
                "temperature": 0.7,
                "retry_count": 3,
            },
            # 生图配置
            "image_generation": {
                "backend_priority": ["comfyui_local", "siliconflow_api"], # 生图后端优先级
                "comfyui_endpoint": "http://127.0.0.1:8188",
                "siliconflow_api_key": os.getenv("SILICONFLOW_API_KEY", ""),
                "default_width": 720,
                "default_height": 1280, # 9:16竖屏比例
                "steps": 20,
                "cfg_scale": 7,
                "batch_size": 2, # 同时生成图片数量
            },
            # 人工审核配置
            "human_review": {
                "enabled": True, # 全局审核开关
                "stages": {
                    "episode_blueprint": True, # 分集方案审核
                    "screenplay": True, # 剧本审核
                    "storyboard": True, # 分镜审核
                    "final_video": False, # 成品视频审核
                }
            },
            # 小说切块配置
            "novel_chunker": {
                "chunk_size_kb": 25, # 单块大小，单位KB
                "overlap_ratio": 0.05, # 块重叠比例
                "deduplicate": True, # 是否去重相邻重复块
            },
            # 语义分析配置
            "semantic_analysis": {
                "cache_enabled": True, # 是否开启缓存，同一本小说不用重复分析
                "chunk_size_char": 20000, # 单分析块字符数（1万汉字约2万字符）
                "overlap_ratio": 0.05, # 块重叠比例
                "max_retries": 2, # 分析失败最大重试次数
                "model": "deepseek-ai/DeepSeek-V3.2", # 分析用模型
                "temperature": 0.1, # 分析温度，越低越稳定
            },
            # 角色一致性管理配置
            "character_manager": {
                "custom_character_path": "config/custom_characters.json", # 自定义人设文件路径
                "enable_validation": True, # 是否开启角色一致性自动校验修正
            },
            # 智能分集配置
            "episode_splitter": {
                "cache_enabled": True, # 是否开启缓存，同一本小说不用重新分集
                "max_episodes": 100, # 最多生成分集数量
                "min_quality_score": 8, # 最低质量评分，低于此分数自动重写
                "max_retries": 2, # 生成分集失败最大重试次数
                "model": "deepseek-ai/DeepSeek-V3.2", # 分集用模型
                "temperature": 0.3, # 分集温度，越低越稳定
                "rules": {
                    "opening_hook": "前3秒必须出现钩子（冲突/悬念/反常点）",
                    "first_15s": "第15秒必须出现第一个爽点/冲突爆发",
                    "mid_point": "中间必须有1次剧情反转",
                    "ending": "结尾必须留强悬念，引导用户看下一集",
                    "episode_length": "每集对应剧情内容长度控制在1000-1500字，对应正片时长60-90秒"
                }
            },
            # 剧本生成配置
            "screenwriter": {
                "cache_enabled": True, # 是否开启缓存
                "enable_ai_generation": True, # 是否开启AI生成剧本，关闭则使用规则生成
                "enable_review": True, # 是否开启人工审核
                "model": "deepseek-ai/DeepSeek-V3.2", # 剧本生成用模型
                "temperature": 0.7, # 剧本生成温度
            },
            # 分镜生成配置
            "director": {
                "cache_enabled": True, # 是否开启缓存
                "enable_ai_generation": False, # 是否开启AI生成分镜，默认关闭使用专业规则生成
                "enable_review": True, # 是否开启人工审核
                "model": "deepseek-ai/DeepSeek-V3.2", # 分镜生成用模型
                "temperature": 0.4, # 分镜生成温度，越低越稳定
            },
            # 功能开关
            "features": {
                "token_saving": True, # 是否开启token优化节省
                "breakpoint_resume": True, # 是否开启断点续跑
                "auto_multi_language": False, # 是否自动生成多语言字幕
                "auto_publish": False, # 是否自动发布到平台
            },
            # 视频渲染配置
            "render": {
                "fps": 24,
                "bitrate": "5M",
                "resolution": "720x1280",
                "subtitle_font": "微软雅黑",
                "subtitle_font_size": 36,
                "subtitle_color": "#FFFFFF",
                "subtitle_outline_color": "#000000",
            }
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    user_config = yaml.safe_load(f)
                # 合并用户配置和默认配置
                return self._merge_config(default_config, user_config)
            except Exception as e:
                print(f"⚠️  配置文件加载失败，使用默认配置：{str(e)}")
                return default_config
        else:
            # 生成默认配置文件
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    yaml.dump(default_config, f, allow_unicode=True, sort_keys=False)
                print(f"✅ 已生成默认配置文件：{self.config_path}")
            except Exception as e:
                print(f"⚠️  生成默认配置文件失败：{str(e)}")
            return default_config
    
    def _merge_config(self, default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
        """递归合并用户配置和默认配置"""
        for k, v in user.items():
            if isinstance(v, dict) and k in default and isinstance(default[k], dict):
                default[k] = self._merge_config(default[k], v)
            else:
                default[k] = v
        return default
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """获取配置，支持点分隔路径，比如 llm.default_model"""
        keys = key_path.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """动态修改配置"""
        keys = key_path.split(".")
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        # 保存到文件
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, allow_unicode=True, sort_keys=False)
        print(f"✅ 配置已更新：{key_path} = {value}")

# 全局单例
config = ConfigCenter()
