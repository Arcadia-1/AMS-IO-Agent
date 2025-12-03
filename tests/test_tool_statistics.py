#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Tool Usage Statistics
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.app.utils.tool_usage_tracker import ToolUsageTracker, track_tool_execution
import time


def test_basic_tracking():
    """Test basic tracking functionality"""
    print("=" * 60)
    print("Test 1: Basic Tracking")
    print("=" * 60)
    
    tracker = ToolUsageTracker(stats_file="logs/test_tool_stats.json")
    
    # Simulate some tool calls
    print("\nSimulating tool calls...")
    tracker.track_call("run_il_file", True, 1.2)
    tracker.track_call("run_il_file", True, 1.5)
    tracker.track_call("run_il_file", False, 0.8, "File not found")
    tracker.track_call("run_il_file", True, 1.0)
    
    tracker.track_call("scan_knowledge_base", True, 0.3)
    tracker.track_call("scan_knowledge_base", True, 0.2)
    
    tracker.track_call("load_domain_knowledge", True, 0.5)
    tracker.track_call("load_domain_knowledge", False, 0.4, "Domain not found")
    
    # Get statistics
    print("\nGetting run_il_file statistics:")
    stats = tracker.get_tool_stats("run_il_file")
    assert stats['total_calls'] == 4, "Should have 4 calls"
    assert stats['success_rate'] == 0.75, "Success rate should be 0.75"
    assert stats['avg_execution_time'] > 0, "Average execution time should be positive"
    print(f"  Total calls: {stats['total_calls']}")
    print(f"  Success rate: {stats['success_rate']}")
    print(f"  Avg time: {stats['avg_execution_time']}")
    
    print("\n✅ Test 1 passed")


def test_top_tools():
    """Test getting most used tools"""
    print("\n" + "=" * 60)
    print("Test 2: Top Tools")
    print("=" * 60)
    
    tracker = ToolUsageTracker(stats_file="logs/test_tool_stats.json")
    
    top_tools = tracker.get_top_tools(3, by="calls")
    assert isinstance(top_tools, list), "get_top_tools should return a list"
    assert len(top_tools) > 0, "Should have at least one tool"
    
    print("\nTop 3 most used tools:")
    for i, tool in enumerate(top_tools, 1):
        assert 'name' in tool, "Tool should have 'name' field"
        assert 'calls' in tool, "Tool should have 'calls' field"
        assert 'success_rate' in tool, "Tool should have 'success_rate' field"
        print(f"{i}. {tool['name']}: {tool['calls']} calls, "
              f"{tool['success_rate']*100:.1f}% success")
    
    print("\n✅ Test 2 passed")


def test_problematic_tools():
    """Test problematic tool detection"""
    print("\n" + "=" * 60)
    print("Test 3: Problematic Tools")
    print("=" * 60)
    
    tracker = ToolUsageTracker(stats_file="logs/test_tool_stats.json")
    
    problematic = tracker.get_problematic_tools(0.7)
    assert isinstance(problematic, list), "get_problematic_tools should return a list"
    
    if problematic:
        print("\n⚠️  Problematic tools (success rate < 70%):")
        for tool in problematic:
            assert 'name' in tool, "Tool should have 'name' field"
            assert 'success_rate' in tool, "Tool should have 'success_rate' field"
            assert tool['success_rate'] < 0.7, "Problematic tools should have success rate < 0.7"
            print(f"  • {tool['name']}: {tool['success_rate']}")
    else:
        print("\n✅ No problematic tools found")
    
    print("\n✅ Test 3 passed")


def test_report_generation():
    """Test report generation"""
    print("\n" + "=" * 60)
    print("Test 4: Report Generation")
    print("=" * 60)
    
    tracker = ToolUsageTracker(stats_file="logs/test_tool_stats.json")
    
    report = tracker.generate_report()
    assert isinstance(report, str), "generate_report should return a string"
    assert len(report) > 0, "Report should not be empty"
    print("\n" + report)
    
    print("\n✅ Test 4 passed")


def test_decorator():
    """Test decorator"""
    print("\n" + "=" * 60)
    print("Test 5: Decorator")
    print("=" * 60)
    
    @track_tool_execution("test_function")
    def test_function(should_fail=False):
        time.sleep(0.1)
        if should_fail:
            raise ValueError("Test error")
        return "Success"
    
    # Successful call
    print("\nCalling test_function (success)...")
    result = test_function(False)
    assert result == "Success", "Function should return 'Success'"
    print(f"Result: {result}")
    
    # Failed call
    print("\nCalling test_function (failure)...")
    try:
        test_function(True)
        assert False, "Function should have raised ValueError"
    except ValueError:
        print("Caught expected error")
    
    # Check statistics
    from src.app.utils.tool_usage_tracker import get_tracker
    tracker = get_tracker()
    stats = tracker.get_tool_stats("test_function")
    assert stats['total_calls'] >= 2, "Should have at least 2 calls"
    print(f"\ntest_function statistics:")
    print(f"  Total calls: {stats['total_calls']}")
    print(f"  Success rate: {stats['success_rate']}")
    
    print("\n✅ Test 5 passed")


if __name__ == "__main__":
    print("\n🧪 Testing Tool Usage Statistics\n")
    
    try:
        test_basic_tracking()
        test_top_tools()
        test_problematic_tools()
        test_report_generation()
        test_decorator()
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

