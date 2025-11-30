#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Task Logger - Minimal task logging

Only record key information: user input, status, duration, tools used, error messages
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any


class SimpleTaskLogger:
    """Minimal task logger"""
    
    def __init__(self, log_file: str = "output/logs/task_history.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Current task
        self.current_task = None
        self.task_start_time = None
        
        # Load history
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load historical tasks"""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_history(self):
        """Save historical tasks"""
        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Failed to save task history: {e}")
    
    def start_task(self, user_input: str) -> str:
        """
        Start new task
        
        Args:
            user_input: User input
            
        Returns:
            Task ID
        """
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_task = {
            "task_id": task_id,
            "user_input": user_input,
            "start_time": datetime.now().isoformat(),
            "status": "running",
            "tools_used": [],
            "duration": 0,
            "error": None
        }
        
        self.task_start_time = time.time()
        return task_id
    
    def log_tool_usage(self, tool_name: str):
        """Log tool usage"""
        if self.current_task and tool_name not in self.current_task["tools_used"]:
            self.current_task["tools_used"].append(tool_name)
    
    def end_task(self, status: str = "success", error: Optional[str] = None):
        """
        结束任务
        
        Args:
            status: 任务状态 (success, failed, interrupted)
            error: 错误信息（如果失败）
        """
        if not self.current_task:
            return
        
        # 计算时长
        duration = time.time() - self.task_start_time if self.task_start_time else 0
        
        # 更新任务信息
        self.current_task["status"] = status
        self.current_task["duration"] = round(duration, 2)
        self.current_task["end_time"] = datetime.now().isoformat()
        
        if error:
            self.current_task["error"] = str(error)[:500]  # Limit length
        
        # Add to history
        self.history.append(self.current_task)
        
        # Keep only last 100 tasks
        if len(self.history) > 100:
            self.history = self.history[-100:]
        
        # Save
        self._save_history()
        
        # Clear current task
        self.current_task = None
        self.task_start_time = None
    
    def get_recent_tasks(self, n: int = 10) -> List[Dict]:
        """Get recent N tasks"""
        return self.history[-n:]
    
    def get_failed_tasks(self, n: int = 10) -> List[Dict]:
        """Get recent failed tasks"""
        failed = [t for t in self.history if t["status"] == "failed"]
        return failed[-n:]
    
    def get_task_stats(self) -> Dict[str, Any]:
        """Get task statistics"""
        if not self.history:
            return {
                "total_tasks": 0,
                "success_count": 0,
                "failed_count": 0,
                "success_rate": 0,
                "avg_duration": 0
            }
        
        total = len(self.history)
        success = sum(1 for t in self.history if t["status"] == "success")
        failed = sum(1 for t in self.history if t["status"] == "failed")
        avg_duration = sum(t["duration"] for t in self.history) / total
        
        return {
            "total_tasks": total,
            "success_count": success,
            "failed_count": failed,
            "interrupted_count": total - success - failed,
            "success_rate": f"{success/total*100:.1f}%",
            "avg_duration": f"{avg_duration:.1f}s"
        }
    
    def get_most_used_tools(self, n: int = 5) -> List[tuple]:
        """Get most used tools"""
        tool_count = {}
        for task in self.history:
            for tool in task["tools_used"]:
                tool_count[tool] = tool_count.get(tool, 0) + 1
        
        # Sort
        sorted_tools = sorted(tool_count.items(), key=lambda x: x[1], reverse=True)
        return sorted_tools[:n]
    
    def analyze_failures(self) -> Dict[str, Any]:
        """Analyze failed tasks"""
        failed = [t for t in self.history if t["status"] == "failed"]
        
        if not failed:
            return {"message": "No failed tasks found"}
        
        # Count tools used in failed tasks
        failed_tools = {}
        for task in failed:
            for tool in task["tools_used"]:
                failed_tools[tool] = failed_tools.get(tool, 0) + 1
        
        # Common errors
        errors = [t["error"] for t in failed if t["error"]]
        
        return {
            "total_failures": len(failed),
            "failure_rate": f"{len(failed)/len(self.history)*100:.1f}%",
            "tools_in_failed_tasks": sorted(failed_tools.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)[:5],
            "recent_errors": errors[-3:] if errors else []
        }


# Global instance
_logger_instance = None

def get_task_logger() -> SimpleTaskLogger:
    """Get global task logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = SimpleTaskLogger()
    return _logger_instance


if __name__ == "__main__":
    # Test
    logger = SimpleTaskLogger(log_file="output/logs/test_task_history.json")
    
    # Simulate task 1
    logger.start_task("设计一个28nm电容")
    logger.log_tool_usage("scan_knowledge_base")
    logger.log_tool_usage("load_domain_knowledge")
    logger.log_tool_usage("create_skill_tool")
    time.sleep(0.5)
    logger.end_task("success")
    
    # 模拟任务 2（失败）
    logger.start_task("运行DRC检查")
    logger.log_tool_usage("run_drc")
    time.sleep(0.3)
    logger.end_task("failed", "DRC rule file not found")
    
    # 模拟任务 3
    logger.start_task("生成IO ring")
    logger.log_tool_usage("scan_knowledge_base")
    logger.log_tool_usage("generate_io_ring_schematic")
    time.sleep(0.4)
    logger.end_task("success")
    
    # 查看统计
    print("=" * 60)
    print("Task Statistics:")
    print("=" * 60)
    stats = logger.get_task_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("Most Used Tools:")
    print("=" * 60)
    for tool, count in logger.get_most_used_tools(5):
        print(f"{tool}: {count} times")
    
    print("\n" + "=" * 60)
    print("Failure Analysis:")
    print("=" * 60)
    analysis = logger.analyze_failures()
    for key, value in analysis.items():
        print(f"{key}: {value}")
    
    print("\n" + "=" * 60)
    print("Recent Tasks:")
    print("=" * 60)
    for task in logger.get_recent_tasks(3):
        print(f"• {task['user_input']}")
        print(f"  Status: {task['status']}, Duration: {task['duration']}s")
        print(f"  Tools: {', '.join(task['tools_used'])}")

