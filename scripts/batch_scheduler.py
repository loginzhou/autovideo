"""
批量生产调度系统
支持多项目排队执行，自动调度资源，24小时不间断生产，产能最大化
"""
import os
import json
import time
import threading
from queue import Queue
from typing import List, Dict, Any, Optional
from project_manager import project_manager
from config_center import config

class BatchScheduler:
    def __init__(self):
        self.task_queue = Queue()
        self.running = False
        self.current_task: Optional[Dict[str, Any]] = None
        self.completed_tasks: List[Dict[str, Any]] = []
        self.failed_tasks: List[Dict[str, Any]] = []
        self.max_concurrent_tasks = config.get("batch_scheduler.max_concurrent_tasks", 1) # 目前单卡单项目并行，后续支持多卡多并行
        self.worker_thread = None
        
        # 加载持久化队列
        self._load_queue()
    
    def _load_queue(self):
        """加载持久化任务队列，重启后任务不丢失"""
        queue_path = "output/batch_queue.json"
        if os.path.exists(queue_path):
            try:
                with open(queue_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for task in data.get('pending', []):
                        self.task_queue.put(task)
                    self.completed_tasks = data.get('completed', [])
                    self.failed_tasks = data.get('failed', [])
                print(f"加载任务队列成功：待执行{self.task_queue.qsize()}个，已完成{len(self.completed_tasks)}个，失败{len(self.failed_tasks)}个")
            except:
                pass
    
    def _save_queue(self):
        """持久化任务队列"""
        queue_path = "output/batch_queue.json"
        os.makedirs(os.path.dirname(queue_path), exist_ok=True)
        
        # 把队列中的任务转成列表
        pending_tasks = []
        while not self.task_queue.empty():
            task = self.task_queue.get()
            pending_tasks.append(task)
            self.task_queue.put(task)
        
        data = {
            "pending": pending_tasks,
            "completed": self.completed_tasks,
            "failed": self.failed_tasks,
            "current": self.current_task
        }
        
        with open(queue_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_project_task(self, project_id: str, priority: int = 5) -> str:
        """添加项目到生产队列，priority越低优先级越高"""
        task_id = f"task_{int(time.time())}_{project_id}"
        task = {
            "task_id": task_id,
            "project_id": project_id,
            "priority": priority,
            "status": "pending",
            "create_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "start_time": None,
            "end_time": None,
            "error": None
        }
        
        # 按优先级插入队列
        # 先取出所有任务
        tasks = []
        while not self.task_queue.empty():
            tasks.append(self.task_queue.get())
        # 插入新任务
        tasks.append(task)
        # 按优先级排序
        tasks.sort(key=lambda x: x['priority'])
        # 重新放入队列
        for t in tasks:
            self.task_queue.put(t)
        
        self._save_queue()
        print(f"项目已加入生产队列：{project_id}，任务ID：{task_id}，优先级：{priority}")
        return task_id
    
    def _run_task(self, task: Dict[str, Any]) -> bool:
        """执行单个任务"""
        try:
            project_id = task['project_id']
            print(f"\n开始执行任务：{task['task_id']}，项目：{project_id}")
            task['start_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.current_task = task
            self._save_queue()
            
            # 加载项目
            project_meta = project_manager.load_project(project_id)
            
            # 调用主流程生成项目
            # 这里导入主流程函数执行
            import sys
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from main_pipeline_v3 import run_pipeline
            success = run_pipeline(project_meta)
            
            if success:
                task['status'] = "completed"
                task['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
                self.completed_tasks.append(task)
                print(f"任务完成：{task['task_id']}，项目：{project_id}")
            else:
                raise Exception("主流程执行失败")
            
            return True
            
        except Exception as e:
            task['status'] = "failed"
            task['error'] = str(e)
            task['end_time'] = time.strftime("%Y-%m-%d %H:%M:%S")
            self.failed_tasks.append(task)
            print(f"任务失败：{task['task_id']}，错误：{str(e)}")
            return False
        finally:
            self.current_task = None
            self._save_queue()
    
    def _worker(self):
        """工作线程，循环执行任务"""
        while self.running:
            if not self.task_queue.empty():
                task = self.task_queue.get()
                self._run_task(task)
                self.task_queue.task_done()
            else:
                # 队列空，休息10秒再检查
                time.sleep(10)
    
    def start(self):
        """启动调度器"""
        if self.running:
            print("调度器已经在运行中")
            return
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker, daemon=True)
        self.worker_thread.start()
        print("批量生产调度器已启动，等待任务...")
    
    def stop(self):
        """停止调度器"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join()
        self._save_queue()
        print("批量生产调度器已停止")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态"""
        return {
            "pending_count": self.task_queue.qsize(),
            "completed_count": len(self.completed_tasks),
            "failed_count": len(self.failed_tasks),
            "running": self.running,
            "current_task": self.current_task,
            "pending_tasks": list(self.task_queue.queue) if hasattr(self.task_queue, 'queue') else []
        }
    
    def retry_failed_task(self, task_id: str) -> bool:
        """重试失败的任务"""
        for i, task in enumerate(self.failed_tasks):
            if task['task_id'] == task_id:
                # 从失败列表移除，重新加入队列
                failed_task = self.failed_tasks.pop(i)
                failed_task['status'] = 'pending'
                failed_task['error'] = None
                failed_task['start_time'] = None
                failed_task['end_time'] = None
                self.add_project_task(failed_task['project_id'], failed_task['priority'])
                print(f"失败任务已重新加入队列：{task_id}")
                return True
        print(f"找不到失败任务：{task_id}")
        return False
    
    def cancel_pending_task(self, task_id: str) -> bool:
        """取消待执行的任务"""
        tasks = []
        found = False
        while not self.task_queue.empty():
            task = self.task_queue.get()
            if task['task_id'] != task_id:
                tasks.append(task)
            else:
                found = True
        
        # 重新放入队列
        for t in tasks:
            self.task_queue.put(t)
        
        self._save_queue()
        if found:
            print(f"任务已取消：{task_id}")
        else:
            print(f"找不到待执行任务：{task_id}")
        return found

# 全局单例
batch_scheduler = BatchScheduler()
