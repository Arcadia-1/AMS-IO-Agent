#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test User Profile Management Tools"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.user_profile_tool import update_user_profile, read_profile

def test_read_profile():
    """Test reading user profile"""
    os.environ["USER_PROFILE_PATH"] = "user_data/test_profile.md"
    
    print("[Test 1]: Read current profile")
    current = read_profile()
    assert isinstance(current, str), "read_profile should return a string"
    print(current)

def test_update_profile():
    """Test updating user profile"""
    os.environ["USER_PROFILE_PATH"] = "user_data/test_profile.md"
    
    print("\n[Test 2]: Create initial profile")
    initial = read_profile()
    modified = initial + "\n- Likes [script_name] in output\n"
    result = update_user_profile(modified)
    assert isinstance(result, str), "update_user_profile should return a string"
    print(result)

def test_read_updated_profile():
    """Test reading updated profile"""
    os.environ["USER_PROFILE_PATH"] = "user_data/test_profile.md"
    
    print("\n[Test 3]: Read again")
    current = read_profile()
    assert isinstance(current, str), "read_profile should return a string"
    assert len(current) > 0, "Profile should not be empty"
    print(current)

if __name__ == "__main__":
    test_read_profile()
    test_update_profile()
    test_read_updated_profile()
    print("\n✅ All tests passed!\n")
