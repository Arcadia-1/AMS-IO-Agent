#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.tools.health_check_tool import run_health_check, check_virtuoso_connection, quick_diagnostic

def test_quick_diagnostic():
    """Test quick diagnostic functionality"""
    print("\n🔍 Testing Health Check Tools\n")
    
    try:
        # Quick diagnostic includes both system health and connection check
        result = quick_diagnostic()
        assert isinstance(result, str), "quick_diagnostic should return a string"
        assert len(result) > 0, "Diagnostic result should not be empty"
        print(result)
        
        print("\n[test_health_check.py] ✅ All health check tests completed!\n")
    except Exception as e:
        print(f"\n[test_health_check.py] ❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_quick_diagnostic()
