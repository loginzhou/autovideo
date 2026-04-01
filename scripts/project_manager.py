"""
项目管理器：每本小说对应一个独立项目，所有输出、缓存、配置独立存储，避免混淆
"""
import os
import json
import shutil
from datetime import datetime
from typing import Optional, Dict, Any

class ProjectManager:
    def __init__(self, projects_root: str = "projects"):
        self.projects_root = projects_root
        os.makedirs(projects_root, exist_ok=True)
        self.current_project: Optional[str] = None
        self.current_project_dir: Optional[str] = None
    
    def create_project(self, novel_name: str, novel_path: str) -> str:
        """创建新项目，每本小说对应一个项目
        返回项目ID
        """
        # 生成项目ID：时间戳+小说名缩写
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_novel_name = "".join([c for c in novel_name if c.isalnum() or c in ('_', '-')])[:20]
        project_id = f"{timestamp}_{safe_novel_name}"
        project_dir = os.path.join(self.projects_root, project_id)
        
        # 创建项目目录结构
        os.makedirs(project_dir, exist_ok=True)
        os.makedirs(os.path.join(project_dir, "input"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "output"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "cache"), exist_ok=True)
        os.makedirs(os.path.join(project_dir, "config"), exist_ok=True)
        
        # 复制小说到项目目录
        novel_ext = os.path.splitext(novel_path)[1]
        target_novel_path = os.path.join(project_dir, "input", f"novel{novel_ext}")
        shutil.copy2(novel_path, target_novel_path)
        
        # 生成项目元数据
        project_meta = {
            "project_id": project_id,
            "novel_name": novel_name,
            "create_time": timestamp,
            "status": "created",
            "input_novel_path": target_novel_path,
            "output_dir": os.path.join(project_dir, "output"),
            "cache_dir": os.path.join(project_dir, "cache"),
            "config_dir": os.path.join(project_dir, "config")
        }
        
        with open(os.path.join(project_dir, "project_meta.json"), 'w', encoding='utf-8') as f:
            json.dump(project_meta, f, ensure_ascii=False, indent=2)
        
        print(f"新项目创建成功：{project_id}，目录：{project_dir}")
        self.current_project = project_id
        self.current_project_dir = project_dir
        
        # 复制默认配置到项目目录
        default_config_path = "config.yaml"
        target_config_path = os.path.join(project_dir, "config", "config.yaml")
        if os.path.exists(default_config_path):
            shutil.copy2(default_config_path, target_config_path)
        
        return project_id
    
    def load_project(self, project_id: str) -> Dict[str, Any]:
        """加载已存在的项目"""
        project_dir = os.path.join(self.projects_root, project_id)
        if not os.path.exists(project_dir):
            raise ValueError(f"项目不存在：{project_id}")
        
        with open(os.path.join(project_dir, "project_meta.json"), 'r', encoding='utf-8') as f:
            project_meta = json.load(f)
        
        self.current_project = project_id
        self.current_project_dir = project_dir
        
        print(f"项目加载成功：{project_id} - {project_meta['novel_name']}")
        return project_meta
    
    def list_projects(self, limit: int = 20) -> list:
        """列出所有项目，按创建时间倒序"""
        projects = []
        for dirname in sorted(os.listdir(self.projects_root), reverse=True):
            dirpath = os.path.join(self.projects_root, dirname)
            if os.path.isdir(dirpath) and os.path.exists(os.path.join(dirpath, "project_meta.json")):
                try:
                    with open(os.path.join(dirpath, "project_meta.json"), 'r', encoding='utf-8') as f:
                        meta = json.load(f)
                        projects.append(meta)
                        if len(projects) >= limit:
                            break
                except:
                    continue
        return projects
    
    def get_project_path(self, sub_path: str = "") -> str:
        """获取当前项目下的路径"""
        if not self.current_project_dir:
            raise ValueError("没有选择当前项目")
        return os.path.join(self.current_project_dir, sub_path)
    
    def get_output_path(self, sub_path: str = "") -> str:
        """获取当前项目输出目录下的路径"""
        return self.get_project_path(os.path.join("output", sub_path))
    
    def get_cache_path(self, sub_path: str = "") -> str:
        """获取当前项目缓存目录下的路径"""
        return self.get_project_path(os.path.join("cache", sub_path))
    
    def update_project_status(self, status: str):
        """更新项目状态"""
        if not self.current_project_dir:
            return
        meta_path = os.path.join(self.current_project_dir, "project_meta.json")
        if not os.path.exists(meta_path):
            return
        with open(meta_path, 'r', encoding='utf-8') as f:
            meta = json.load(f)
        meta['status'] = status
        meta['update_time'] = datetime.now().strftime("%Y%m%d_%H%M%S")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

# 全局单例
project_manager = ProjectManager()
