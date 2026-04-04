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
import os

# 使用相对路径，相对于项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REQUIRED_PATHS = [
    os.path.join(PROJECT_ROOT, "sandbox"),
    os.path.join(PROJECT_ROOT, "output"),
    os.path.join(PROJECT_ROOT, "logs"),
    os.path.join(PROJECT_ROOT, "assets")
]
