#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Statistics Tool - Tool statistics utility available to Agent
"""

from smolagents import tool
from src.app.utils.tool_usage_tracker import get_tracker


@tool
def get_tool_statistics(tool_name: str = None) -> str:
    """
    Get usage statistics for tools.
    
    Args:
        tool_name: Specific tool name to get stats for. If None, returns all tools.
        
    Returns:
        String containing tool usage statistics
        
    Examples:
        get_tool_statistics("run_il_file")  # Stats for specific tool
        get_tool_statistics()                # Stats for all tools
    """
    tracker = get_tracker()
    
    if tool_name:
        # Get statistics for specific tool
        stats = tracker.get_tool_stats(tool_name)
        
        if "error" in stats:
            return stats["error"]
        
        result = [f"📊 Statistics for '{tool_name}':"]
        result.append(f"  • Total calls: {stats['total_calls']}")
        result.append(f"  • Successful: {stats['successful_calls']}")
        result.append(f"  • Failed: {stats['failed_calls']}")
        result.append(f"  • Success rate: {stats['success_rate']}")
        result.append(f"  • Avg execution time: {stats['avg_execution_time']}")
        result.append(f"  • Last used: {stats['last_used']}")
        
        if stats['recent_errors']:
            result.append(f"  • Recent errors:")
            for err in stats['recent_errors']:
                result.append(f"    - {err['message'][:80]}")
        
        return "\n".join(result)
    else:
        # Get statistics for all tools
        all_stats = tracker.get_all_stats()
        
        if not all_stats:
            return "No tool usage statistics available yet."
        
        result = [f"📊 Tool Usage Statistics ({len(all_stats)} tools):"]
        result.append("")
        
        # Sort by call count
        sorted_tools = sorted(all_stats.items(), 
                             key=lambda x: x[1]['total_calls'], 
                             reverse=True)
        
        for tool_name, stats in sorted_tools[:10]:  # Show only top 10
            result.append(f"• {tool_name}:")
            result.append(f"  Calls: {stats['total_calls']}, "
                         f"Success: {stats['success_rate']}, "
                         f"Avg time: {stats['avg_execution_time']}")
        
        if len(all_stats) > 10:
            result.append(f"\n... and {len(all_stats) - 10} more tools")
        
        return "\n".join(result)


@tool
def get_top_used_tools(n: int = 5) -> str:
    """
    Get the top N most frequently used tools.
    
    Args:
        n: Number of top tools to return (default: 5)
        
    Returns:
        String listing the most used tools with statistics
    """
    tracker = get_tracker()
    top_tools = tracker.get_top_tools(n, by="calls")
    
    if not top_tools:
        return "No tool usage data available yet."
    
    result = [f"🔝 Top {len(top_tools)} Most Used Tools:"]
    result.append("")
    
    for i, tool in enumerate(top_tools, 1):
        result.append(f"{i}. {tool['name']}")
        result.append(f"   • Calls: {tool['calls']}")
        result.append(f"   • Success rate: {tool['success_rate']*100:.1f}%")
        result.append(f"   • Avg time: {tool['avg_time']:.2f}s")
        result.append("")
    
    return "\n".join(result)


@tool
def get_problematic_tools(threshold: float = 0.7) -> str:
    """
    Identify tools with low success rates that may need attention.
    
    Args:
        threshold: Success rate threshold (0-1). Tools below this are flagged (default: 0.7)
        
    Returns:
        String listing problematic tools with error information
    """
    tracker = get_tracker()
    problematic = tracker.get_problematic_tools(threshold)
    
    if not problematic:
        return f"✅ No problematic tools found (all tools have success rate >= {threshold*100:.0f}%)"
    
    result = [f"⚠️  Problematic Tools (success rate < {threshold*100:.0f}%):"]
    result.append("")
    
    for tool in problematic:
        result.append(f"• {tool['name']}")
        result.append(f"  Calls: {tool['calls']}, Success rate: {tool['success_rate']}")
        
        if tool['recent_errors']:
            result.append(f"  Recent errors:")
            for err in tool['recent_errors']:
                result.append(f"    - {err['message'][:100]}")
        result.append("")
    
    result.append("💡 Suggestion: Consider optimizing or replacing these tools.")
    
    return "\n".join(result)


@tool
def generate_tool_usage_report() -> str:
    """
    Generate a comprehensive tool usage report.
    
    Returns:
        String containing a detailed report of all tool usage statistics
    """
    tracker = get_tracker()
    report = tracker.generate_report()
    
    # Save report to file
    try:
        from pathlib import Path
        report_file = Path("output/logs/tool_usage_report.txt")
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        return f"{report}\n\n📄 Report saved to: {report_file}"
    except Exception as e:
        return f"{report}\n\n⚠️  Failed to save report: {e}"


@tool
def reset_tool_statistics() -> str:
    """
    Reset all tool usage statistics (use with caution).
    
    Returns:
        Confirmation message
    """
    tracker = get_tracker()
    
    # Clear statistics
    tracker.session_stats.clear()
    tracker.save_stats()
    
    return "✅ Tool usage statistics have been reset."

