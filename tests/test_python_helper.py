#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Python Helper Tool Creation
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.python_tool_creator import (
    create_python_helper,
    list_python_helpers,
    view_python_helper_code,
    delete_python_helper
)

def test_create_read_il_helper():
    """Test creating helper to read IL files"""
    print("\n" + "="*80)
    print("Test 1: Create 'read_il_file_content' helper")
    print("="*80)
    
    result = create_python_helper(
        tool_name="read_il_file_content",
        description="Read IL file and return its content as a string",
        function_body='''
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()
return content
''',
        parameters='{"file_path": "str"}',
        return_type="str"
    )
    
    print(result)


def test_create_parse_il_comments():
    """Test creating helper to parse IL comments"""
    print("\n" + "="*80)
    print("Test 2: Create 'parse_il_comments' helper")
    print("="*80)
    
    result = create_python_helper(
        tool_name="parse_il_comments",
        description="Extract all comments from IL file content",
        function_body='''
import re
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all ;; style comments
comments = re.findall(r';;(.*)$', content, re.MULTILINE)
return '\\n'.join(comment.strip() for comment in comments)
''',
        parameters='{"file_path": "str"}',
        return_type="str"
    )
    
    print(result)


def test_list_helpers():
    """Test listing all helpers"""
    print("\n" + "="*80)
    print("Test 3: List all Python helpers")
    print("="*80)
    
    result = list_python_helpers()
    print(result)


def test_view_helper_code():
    """Test viewing helper code"""
    print("\n" + "="*80)
    print("Test 4: View 'read_il_file_content' code")
    print("="*80)
    
    result = view_python_helper_code("read_il_file_content")
    print(result)


def test_cleanup():
    """Clean up test-created helpers"""
    print("\n" + "="*80)
    print("Cleanup: Delete test helpers")
    print("="*80)
    
    for tool_name in ["read_il_file_content", "parse_il_comments"]:
        result = delete_python_helper(tool_name)
        print(f"  {result}")


if __name__ == "__main__":
    print("\n🧪 Testing Python Helper Tool Creation System\n")
    
    try:
        # Create test helpers
        test_create_read_il_helper()
        test_create_parse_il_comments()
        
        # List all helpers
        test_list_helpers()
        
        # View code
        test_view_helper_code()
        
        # Cleanup
        test_cleanup()
        
        print("\n" + "="*80)
        print("✅ All tests completed successfully!")
        print("="*80 + "\n")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

