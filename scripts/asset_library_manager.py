"""
统一素材库管理器
全局管理角色LoRA、BGM、音效、场景素材，所有项目复用，减少重复生成成本
"""
import os
import json
import shutil
from typing import List, Dict, Any, Optional
from config_center import config

class AssetLibraryManager:
    def __init__(self, library_root: str = "asset_library"):
        self.library_root = library_root
        self.asset_types = ["lora", "bgm", "sfx", "scenes", "font", "filter"]
        
        # 创建素材库目录结构
        os.makedirs(library_root, exist_ok=True)
        for asset_type in self.asset_types:
            os.makedirs(os.path.join(library_root, asset_type), exist_ok=True)
        
        # 加载素材索引
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """加载素材索引"""
        index_path = os.path.join(self.library_root, "asset_index.json")
        if os.path.exists(index_path):
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return self._init_index()
        return self._init_index()
    
    def _init_index(self) -> Dict[str, Any]:
        """初始化空索引"""
        index = {t: {} for t in self.asset_types}
        index['metadata'] = {
            "total_assets": 0,
            "last_updated": ""
        }
        return index
    
    def _save_index(self):
        """保存素材索引"""
        index_path = os.path.join(self.library_root, "asset_index.json")
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, ensure_ascii=False, indent=2)
    
    def add_asset(self, asset_type: str, name: str, file_path: str, tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """添加素材到素材库
        返回素材ID
        """
        if asset_type not in self.asset_types:
            raise ValueError(f"不支持的素材类型：{asset_type}，支持类型：{','.join(self.asset_types)}")
        
        # 生成素材ID
        import hashlib
        file_hash = hashlib.md5(open(file_path, 'rb').read()).hexdigest()[:8]
        asset_id = f"{asset_type}_{file_hash}_{name.replace(' ', '_')}"
        
        # 复制文件到素材库
        ext = os.path.splitext(file_path)[1]
        target_path = os.path.join(self.library_root, asset_type, f"{asset_id}{ext}")
        shutil.copy2(file_path, target_path)
        
        # 添加到索引
        self.index[asset_type][asset_id] = {
            "id": asset_id,
            "name": name,
            "file_path": target_path,
            "tags": tags or [],
            "metadata": metadata or {},
            "usage_count": 0
        }
        self.index['metadata']['total_assets'] += 1
        self._save_index()
        
        print(f"素材添加成功：{name} -> {asset_id}")
        return asset_id
    
    def get_asset(self, asset_type: str, asset_id: str) -> Optional[Dict[str, Any]]:
        """获取素材信息"""
        if asset_type not in self.index or asset_id not in self.index[asset_type]:
            return None
        # 更新使用次数
        self.index[asset_type][asset_id]['usage_count'] += 1
        self._save_index()
        return self.index[asset_type][asset_id]
    
    def search_assets(self, asset_type: str, keyword: str = "", tags: List[str] = None) -> List[Dict[str, Any]]:
        """搜索素材，支持关键词和标签筛选"""
        if asset_type not in self.index:
            return []
        
        results = []
        for asset in self.index[asset_type].values():
            # 关键词匹配
            if keyword and keyword.lower() not in asset['name'].lower() and not any(keyword.lower() in tag.lower() for tag in asset['tags']):
                continue
            # 标签匹配
            if tags and not all(tag in asset['tags'] for tag in tags):
                continue
            results.append(asset)
        
        # 按使用次数排序，常用的优先
        results.sort(key=lambda x: x['usage_count'], reverse=True)
        return results
    
    def get_random_asset(self, asset_type: str, tags: List[str] = None) -> Optional[Dict[str, Any]]:
        """随机获取符合标签的素材"""
        candidates = self.search_assets(asset_type, tags=tags)
        if not candidates:
            return None
        import random
        return random.choice(candidates)
    
    def delete_asset(self, asset_type: str, asset_id: str) -> bool:
        """删除素材"""
        if asset_type not in self.index or asset_id not in self.index[asset_type]:
            return False
        
        asset = self.index[asset_type][asset_id]
        # 删除文件
        if os.path.exists(asset['file_path']):
            os.remove(asset['file_path'])
        # 删除索引
        del self.index[asset_type][asset_id]
        self.index['metadata']['total_assets'] -= 1
        self._save_index()
        print(f"素材删除成功：{asset_id}")
        return True
    
    def list_all_assets(self, asset_type: str = None) -> Dict[str, Any]:
        """列出所有素材"""
        if asset_type:
            return self.index.get(asset_type, {})
        return self.index

# 全局单例
asset_library = AssetLibraryManager()
