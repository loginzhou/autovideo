"""
人工审核管理器
在生产关键节点加入人工确认环节，支持预览、修改、驳回重生成，完全符合专业短剧生产流程
"""
import os
import json
from typing import Dict, Any, Optional, List

class HumanReviewManager:
    def __init__(self, review_dir: str = "output/review"):
        self.review_dir = review_dir
        os.makedirs(review_dir, exist_ok=True)
        # 可配置是否开启审核，默认开启生产模式
        self.review_enabled = os.getenv("HUMAN_REVIEW_ENABLED", "true").lower() == "true"
        # 审核节点配置，可以单独开关某个环节的审核
        self.review_stages = {
            "episode_blueprint": os.getenv("REVIEW_EPISODE_BLUEPRINT", "true").lower() == "true",
            "screenplay": os.getenv("REVIEW_SCREENPLAY", "true").lower() == "true",
            "storyboard": os.getenv("REVIEW_STORYBOARD", "true").lower() == "true",
            "final_video": os.getenv("REVIEW_FINAL_VIDEO", "false").lower() == "true"
        }
    
    def request_review(self, stage_name: str, content: Any, episode_seq: Optional[int] = None) -> bool:
        """发起人工审核请求
        返回True表示审核通过，False表示需要重生成
        """
        if not self.review_enabled or not self.review_stages.get(stage_name, False):
            # 审核关闭，直接通过
            return True
        
        # 生成审核文件
        if episode_seq:
            review_file = os.path.join(self.review_dir, f"episode_{episode_seq}_{stage_name}_review.json")
            preview_file = os.path.join(self.review_dir, f"episode_{episode_seq}_{stage_name}_preview.md")
            title = f"第{episode_seq}集 {stage_name} 审核"
        else:
            review_file = os.path.join(self.review_dir, f"global_{stage_name}_review.json")
            preview_file = os.path.join(self.review_dir, f"global_{stage_name}_preview.md")
            title = f"全局 {stage_name} 审核"
        
        # 保存原始内容
        with open(review_file, "w", encoding="utf-8") as f:
            json.dump({
                "stage": stage_name,
                "episode_seq": episode_seq,
                "content": content,
                "status": "pending",
                "review_comments": ""
            }, f, ensure_ascii=False, indent=2)
        
        # 生成易读的预览文件
        self._generate_preview(preview_file, title, content)
        
        print(f"\n【人工审核节点】{title} 等待审核")
        print(f"预览文件：{preview_file}")
        print(f"审核文件：{review_file}")
        print("操作说明：")
        print("   1. 查看预览文件确认内容是否符合要求")
        print("   2. 如需修改，直接编辑审核文件中的content字段，或者填写review_comments驳回重生成")
        print("   3. 将status字段改为approved表示通过，改为rejected表示驳回重生成")
        print("   4. 保存文件后程序会自动继续执行\n")
        
        # 轮询等待审核结果
        while True:
            try:
                with open(review_file, "r", encoding="utf-8") as f:
                    review_data = json.load(f)
                status = review_data.get("status", "pending")
                if status == "approved":
                    print(f"{title} 审核通过")
                    return True
                elif status == "rejected":
                    comments = review_data.get("review_comments", "无审核意见")
                    print(f"{title} 审核驳回，意见：{comments}")
                    return False
            except Exception as e:
                print(f"读取审核文件失败：{str(e)}，重试中...")
            import time
            time.sleep(5)
    
    def _generate_preview(self, preview_path: str, title: str, content: Any):
        """生成易读的Markdown预览文件"""
        preview = f"# {title}\n\n"
        
        if isinstance(content, list) and all(isinstance(item, dict) and "seq" in item for item in content):
            # 分集方案预览
            preview += "## 分集方案\n"
            for ep in content:
                preview += f"### 第{ep['seq']}集\n"
                preview += f"- 核心剧情：{ep.get('core_plot', '无')[:200]}...\n"
                preview += f"- 主要角色：{', '.join(ep.get('main_characters', []))}\n"
                preview += f"- 亮点：{ep.get('highlight', '无')}\n\n"
        elif isinstance(content, dict) and "beats" in content:
            # 剧本预览
            preview += "## 剧本内容\n"
            for idx, beat in enumerate(content["beats"]):
                preview += f"### {idx+1}. {beat['beat_type'].upper()}\n"
                preview += f"内容：{beat['content']}\n"
                preview += f"台词限制：{beat.get('dialogue_limit', '无')}字\n\n"
        elif isinstance(content, dict) and "storyboard" in content:
            # 分镜预览
            preview += "## 分镜内容\n"
            for idx, shot in enumerate(content["storyboard"]):
                preview += f"### 镜头{idx+1}\n"
                preview += f"- 景别：{shot.get('shot_type', '无')}\n"
                preview += f"- 画面描述：{shot.get('visual_prompt', '无')}\n"
                preview += f"- 台词：{shot.get('dialogue', '无')}\n"
                preview += f"- 时长：{shot.get('duration', '无')}秒\n\n"
        else:
            # 通用预览
            preview += "## 内容详情\n```json\n"
            preview += json.dumps(content, ensure_ascii=False, indent=2)[:5000] + "\n```\n"
        
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(preview)

# 全局单例
human_review = HumanReviewManager()
