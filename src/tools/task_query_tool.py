#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Task Query Tool - Task query utility available to Agent
"""

from smolagents import tool
from src.app.utils.simple_task_logger import get_task_logger


@tool
def view_recent_tasks(n: int = 5) -> str:
    """
    View recent tasks with their status and details.
    
    Args:
        n: Number of recent tasks to show (default: 5)
        
    Returns:
        String listing recent tasks with status, duration, and tools used
    """
    logger = get_task_logger()
    tasks = logger.get_recent_tasks(n)
    
    if not tasks:
        return "No tasks found in history."
    
    result = [f"📋 Recent {len(tasks)} Tasks:"]
    result.append("")
    
    for i, task in enumerate(reversed(tasks), 1):
        status_icon = "✅" if task["status"] == "success" else "❌" if task["status"] == "failed" else "⏸️"
        
        result.append(f"{i}. {status_icon} {task['user_input'][:60]}")
        result.append(f"   Status: {task['status']}, Duration: {task['duration']}s")
        
        if task['tools_used']:
            result.append(f"   Tools: {', '.join(task['tools_used'][:5])}")
        
        if task.get('error'):
            result.append(f"   Error: {task['error'][:80]}")
        
        result.append("")
    
    return "\n".join(result)


@tool
def analyze_task_failures() -> str:
    """
    Analyze failed tasks to identify common issues.
    
    Returns:
        String containing failure analysis with common tools and errors
    """
    logger = get_task_logger()
    analysis = logger.analyze_failures()
    
    if "message" in analysis:
        return "✅ " + analysis["message"]
    
    result = ["⚠️  Task Failure Analysis:"]
    result.append("")
    result.append(f"Total failures: {analysis['total_failures']}")
    result.append(f"Failure rate: {analysis['failure_rate']}")
    result.append("")
    
    if analysis['tools_in_failed_tasks']:
        result.append("Tools frequently used in failed tasks:")
        for tool, count in analysis['tools_in_failed_tasks']:
            result.append(f"  • {tool}: {count} times")
        result.append("")
    
    if analysis['recent_errors']:
        result.append("Recent errors:")
        for error in analysis['recent_errors']:
            result.append(f"  • {error[:100]}")
        result.append("")
    
    result.append("💡 Suggestion: Review these tools and errors to identify patterns.")
    
    return "\n".join(result)


@tool
def get_task_summary() -> str:
    """
    Get overall task statistics summary.
    
    Returns:
        String containing task statistics including success rate and most used tools
    """
    logger = get_task_logger()
    stats = logger.get_task_stats()
    
    if stats["total_tasks"] == 0:
        return "No tasks recorded yet."
    
    result = ["📊 Task Summary:"]
    result.append("")
    result.append(f"Total tasks: {stats['total_tasks']}")
    result.append(f"Successful: {stats['success_count']}")
    result.append(f"Failed: {stats['failed_count']}")
    result.append(f"Interrupted: {stats['interrupted_count']}")
    result.append(f"Success rate: {stats['success_rate']}")
    result.append(f"Avg duration: {stats['avg_duration']}")
    result.append("")
    
    # Most used tools
    top_tools = logger.get_most_used_tools(5)
    if top_tools:
        result.append("Most used tools:")
        for tool, count in top_tools:
            result.append(f"  • {tool}: {count} times")
    
    return "\n".join(result)


@tool
def compare_with_tool_stats() -> str:
    """
    Compare task-level statistics with tool-level statistics for insights.
    
    Returns:
        String containing comparison insights
    """
    from ..utils.tool_usage_tracker import get_tracker
    
    task_logger = get_task_logger()
    tool_tracker = get_tracker()
    
    # Task-level statistics
    task_stats = task_logger.get_task_stats()
    
    # Tool-level statistics
    tool_stats = tool_tracker.get_all_stats()
    
    if task_stats["total_tasks"] == 0:
        return "No task data available for comparison."
    
    result = ["🔍 Task vs Tool Statistics Comparison:"]
    result.append("")
    result.append(f"Task level:")
    result.append(f"  • Total tasks: {task_stats['total_tasks']}")
    result.append(f"  • Success rate: {task_stats['success_rate']}")
    result.append("")
    
    if tool_stats:
        result.append(f"Tool level:")
        result.append(f"  • Total tools tracked: {len(tool_stats)}")
        
        # Find tools frequently used in failed tasks
        failure_analysis = task_logger.analyze_failures()
        if "tools_in_failed_tasks" in failure_analysis:
            result.append("")
            result.append("⚠️  Tools frequently involved in failures:")
            for tool, count in failure_analysis["tools_in_failed_tasks"][:3]:
                if tool in tool_stats:
                    tool_success_rate = tool_stats[tool].get("success_rate", "N/A")
                    result.append(f"  • {tool}: appears in {count} failed tasks, "
                                f"tool success rate: {tool_success_rate}")
    
    return "\n".join(result)

