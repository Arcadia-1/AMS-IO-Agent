#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MinimalOutputLogger directly
"""

from pathlib import Path
import sys
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.app.utils.custom_logger import MinimalOutputLogger

def test_logger_thought():
    """Test logging thought messages"""
    logger = MinimalOutputLogger()
    print("Test 1: Thought (should be CYAN)")
    logger.log("Thought: The user is testing the logger functionality...")
    # Logger should not raise exceptions
    assert True

def test_logger_final_answer():
    """Test logging final answer"""
    logger = MinimalOutputLogger()
    print("\nTest 2: Final answer (should be GREEN)")
    logger.log("Final answer: The logger is working correctly with colors!")
    assert True

def test_logger_step_timing():
    """Test logging step timing"""
    logger = MinimalOutputLogger()
    print("\nTest 3: Step timing (should be YELLOW)")
    logger.log("[Step 1: Duration 5.23 seconds | Input tokens: 1,234 | Output tokens: 567]")
    assert True

def test_logger_observation():
    """Test logging observations"""
    logger = MinimalOutputLogger()
    print("\nTest 4: Observation (should be default color)")
    logger.log("Observation: Test completed successfully")
    assert True

def test_logger_code_execution():
    """Test logging code execution"""
    logger = MinimalOutputLogger()
    print("\nTest 5: Code execution (should be HIDDEN)")
    logger.log("─ Executing parsed code:")
    assert True

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("Testing MinimalOutputLogger")
    print("=" * 70 + "\n")
    
    test_logger_thought()
    test_logger_final_answer()
    test_logger_step_timing()
    test_logger_observation()
    test_logger_code_execution()
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70 + "\n")

