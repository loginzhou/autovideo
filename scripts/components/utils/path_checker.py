import os
import uuid

def check_write_permission(paths: list) -> bool:
    """
    路径校验补丁：Worktree启动前强制检测所有路径写权限
    无权限直接抛出异常终止任务
    """
    for path in paths:
        try:
            os.makedirs(path, exist_ok=True)
            test_file = os.path.join(path, f".write_test_{uuid.uuid4().hex[:8]}")
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write("permission_test")
            os.remove(test_file)
        except Exception as e:
            raise PermissionError(f"路径无写权限：{path}，错误信息：{str(e)}")
    return True

# 全局必填路径配置
REQUIRED_PATHS = [
    "C:\\Users\\tion\\.openclaw\\workspace\\novel2shorts\\sandbox",
    "C:\\Users\\tion\\.openclaw\\workspace\\novel2shorts\\output",
    "C:\\Users\\tion\\.openclaw\\workspace\\novel2shorts\\logs",
    "C:\\Users\\tion\\.openclaw\\workspace\\novel2shorts\\assets"
]
