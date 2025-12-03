#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple IL File Runner

NOTE: This script can ONLY run with skillbridge, NOT with RAMIC Bridge.
It requires Cadence Virtuoso to be running and skillbridge library installed.

// can be largly simplified
"""

import sys
from pathlib import Path

def run_il_file(il_file_path):
    """
    Run IL file
    
    Args:
        il_file_path: IL file path
    """
    # Import skillbridge
    from skillbridge import Workspace
    
    # Open workspace and execute
    print(f"🔄 Running IL file: {Path(il_file_path).name}")
    ws = Workspace.open()
    
    # Load and execute IL file
    ws['load'](il_file_path)
    cv = ws['geGetEditCellView']()
    ws['dbSave'](cv)
    print(f"✅ IL file {Path(il_file_path).name} executed successfully")
    ws.close()
    return True

def test_run_il_file():
    """Test running IL file with skillbridge"""
    # This test requires skillbridge and Virtuoso
    import pytest
    try:
        from skillbridge import Workspace
    except ImportError:
        pytest.skip("skillbridge not available")
    
    # Test requires a valid IL file path
    # For pytest compatibility, we'll skip if no file is provided
    if len(sys.argv) < 2:
        pytest.skip("No IL file provided for testing")
    
    il_file_path = sys.argv[1]
    success = run_il_file(il_file_path)
    assert success, "run_il_file should return True on success"

def main():
    """Main function"""
    if len(sys.argv) != 2:
        print("Usage: python simple_il_runner.py <il_file_path>")
        print("Example: python simple_il_runner.py output/test.il")
        sys.exit(1)
    
    il_file_path = sys.argv[1]
    success = run_il_file(il_file_path)
    
    if success:
        print("[Program execution completed]")

if __name__ == "__main__":
    main() 