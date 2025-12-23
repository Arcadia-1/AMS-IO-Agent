#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple IL File Runner using RAMIC Bridge

NOTE: This script uses RAMIC Bridge, NOT skillbridge.
It requires the RAMIC system to be properly configured.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.il_runner_tool import run_il_file

def test_run_il_file_simple_return():
    """Test 1: Simple return value"""
    import pytest
    test_file = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/test_return.il"
    if not Path(test_file).exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    result1 = run_il_file(test_file, lib="TestLib", cell="TestCell")
    assert isinstance(result1, str), "run_il_file should return a string"
    print(f"[Test 1 - Simple Return]: {result1}\n")

def test_run_il_file_cellview_info():
    """Test 2: Get cellview info (may return nil if no cellview is open)"""
    import pytest
    test_file = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/get_cellview_info.il"
    if not Path(test_file).exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    result2 = run_il_file(test_file, lib="TestLib", cell="TestCell")
    assert isinstance(result2, str), "run_il_file should return a string"
    print(f"[Test 2 - Cellview Info]: {result2}\n")

def test_run_il_file_simple_test():
    """Test 3: Simple test from output folder"""
    import pytest
    test_file = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/simple_test.il"
    if not Path(test_file).exists():
        pytest.skip(f"Test file not found: {test_file}")
    
    result3 = run_il_file(test_file, lib="TestLib", cell="TestCell")
    assert isinstance(result3, str), "run_il_file should return a string"
    print(f"[Test 3 - Simple Test]: {result3}")

def main():
    # Test 1: Simple return value
    test_file1 = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/test_return.il"
    if Path(test_file1).exists():
        result1 = run_il_file(test_file1, lib="TestLib", cell="TestCell")
        print(f"[Test 1 - Simple Return]: {result1}\n")
    
    # Test 2: Get cellview info (may return nil if no cellview is open)
    test_file2 = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/get_cellview_info.il"
    if Path(test_file2).exists():
        result2 = run_il_file(test_file2, lib="TestLib", cell="TestCell")
        print(f"[Test 2 - Cellview Info]: {result2}\n")
    
    # Test 3: Simple test from output folder
    test_file3 = "/home/zhangz/RAMIC/AMS-IO-Agent/skill_tools/simple_test.il"
    if Path(test_file3).exists():
        result3 = run_il_file(test_file3, lib="TestLib", cell="TestCell")
        print(f"[Test 3 - Simple Test]: {result3}")

if __name__ == "__main__":
    main()
