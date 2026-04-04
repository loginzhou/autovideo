import os
import yaml
from typing import Dict, Any

class ConfigLoader:
    """
    统一配置加载器，所有脚本都通过这个类读取配置
    """
    _instance = None
    _config = None
    _config_path = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # 优先读取当前目录下的config.yaml，否则读取上级目录的
            current_dir_config = os.path.join(os.getcwd(), "config.yaml")
            parent_dir_config = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.yaml")
            if os.path.exists(current_dir_config):
                cls._config_path = current_dir_config
            elif os.path.exists(parent_dir_config):
                cls._config_path = parent_dir_config
            else:
                raise FileNotFoundError("未找到配置文件，请复制config.example.yaml为config.yaml并填写配置")
            cls._load_config()
        return cls._instance

    @classmethod
    def _load_config(cls):
        """加载配置文件"""
        try:
            with open(cls._config_path, 'r', encoding='utf-8') as f:
                cls._config = yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"配置文件加载失败：{str(e)}")

    @classmethod
    def get(cls, key_path: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分隔的路径，比如：
        ConfigLoader.get('llm.default_provider')
        ConfigLoader.get('comfyui.server_url', 'http://127.0.0.1:8188')
        """
        if not cls._config:
            cls()
        
        keys = key_path.split('.')
        value = cls._config
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @classmethod
    def get_llm_config(cls, provider: str = None) -> Dict:
        """获取指定LLM提供商的配置，不指定则使用默认提供商"""
        if not provider:
            provider = cls.get('llm.default_provider')
        return cls.get(f'llm.providers.{provider}', {})
    
    @classmethod
    def get_all_config(cls) -> Dict:
        """获取整个配置对象"""
        if not cls._config:
            cls()
        return cls._config

# 全局单例
config = ConfigLoader()

if __name__ == "__main__":
    # 测试配置加载
    print("配置加载测试：")
    print(f"默认LLM提供商：{config.get('llm.default_provider')}")
    print(f"ComfyUI地址：{config.get('comfyui.server_url')}")
    print(f"渲染是否开启：{config.get('basic.render_enabled')}")
    print("配置加载成功！")
