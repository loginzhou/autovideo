"""
断点续跑状态管理器
记录每个环节的完成状态，任务中断后重启可以从失败位置继续，不用重新跑全流程
"""
import os
import json
from typing import Dict, Any, Optional

class PipelineStateManager:
    def __init__(self, state_file: str = "output/runtime/pipeline_state.json"):
        self.state_file = state_file
        os.makedirs(os.path.dirname(state_file), exist_ok=True)
        self.state = self._load_state()
    
    def _load_state(self) -> Dict[str, Any]:
        """加载已有的状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                # 文件损坏，重置状态
                return self._init_state()
        return self._init_state()
    
    def _init_state(self) -> Dict[str, Any]:
        """初始化空状态"""
        return {
            "global_stage": {
                "novel_chunker": False,
                "semantic_analysis": False,
                "character_manager_init": False,
                "episode_splitter": False
            },
            "episodes": {},
            "last_updated": 0
        }
    
    def is_stage_completed(self, stage_name: str) -> bool:
        """检查全局阶段是否完成"""
        return self.state["global_stage"].get(stage_name, False)
    
    def mark_stage_completed(self, stage_name: str, data: Optional[Any] = None):
        """标记全局阶段完成，可选保存阶段产出数据"""
        self.state["global_stage"][stage_name] = True
        if data is not None:
            self.state[f"{stage_name}_data"] = data
        self._save_state()
        print(f"阶段[{stage_name}]已标记完成，已保存断点状态")
    
    def get_stage_data(self, stage_name: str) -> Optional[Any]:
        """获取阶段保存的产出数据"""
        return self.state.get(f"{stage_name}_data", None)
    
    def is_episode_stage_completed(self, episode_seq: int, stage_name: str) -> bool:
        """检查单集的某个阶段是否完成"""
        episode_key = f"episode_{episode_seq}"
        if episode_key not in self.state["episodes"]:
            return False
        return self.state["episodes"][episode_key].get(stage_name, False)
    
    def mark_episode_stage_completed(self, episode_seq: int, stage_name: str, data: Optional[Any] = None):
        """标记单集的某个阶段完成"""
        episode_key = f"episode_{episode_seq}"
        if episode_key not in self.state["episodes"]:
            self.state["episodes"][episode_key] = {}
        self.state["episodes"][episode_key][stage_name] = True
        if data is not None:
            self.state["episodes"][episode_key][f"{stage_name}_data"] = data
        self._save_state()
        print(f"第{episode_seq}集[{stage_name}]阶段已标记完成，已保存断点状态")
    
    def get_episode_stage_data(self, episode_seq: int, stage_name: str) -> Optional[Any]:
        """获取单集阶段保存的产出数据"""
        episode_key = f"episode_{episode_seq}"
        if episode_key not in self.state["episodes"]:
            return None
        return self.state["episodes"][episode_key].get(f"{stage_name}_data", None)
    
    def reset_episode(self, episode_seq: int):
        """重置单集的所有状态，用于重新生成某一集"""
        episode_key = f"episode_{episode_seq}"
        if episode_key in self.state["episodes"]:
            del self.state["episodes"][episode_key]
            self._save_state()
            print(f"第{episode_seq}集状态已重置，将重新生成")
    
    def reset_all(self):
        """重置所有状态，重新跑全流程"""
        self.state = self._init_state()
        self._save_state()
        print("所有状态已重置，将重新执行全流程")
    
    def _save_state(self):
        """保存状态到文件"""
        import time
        self.state["last_updated"] = int(time.time())
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(self.state, f, ensure_ascii=False, indent=2)

# 全局单例
pipeline_state = PipelineStateManager()
