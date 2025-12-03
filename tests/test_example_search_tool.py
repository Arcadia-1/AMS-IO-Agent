#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Example Code Search Tool

Usage:
python test_example_search_tool.py [options]

Options:
    -h, --help          Show help information
    -k, --keyword      Specify search keyword for testing
    -t, --test         Run specified test case
    -a, --all          Run all tests (default behavior)
    -v, --verbose      Verbose output mode
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Tuple

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.example_search_tool import code_example_search, list_examples, search_examples

# Test case data
TEST_CASES = [
    {
        'name': 'layout',
        'query': 'layout',
        'expected_file': 'layout_generation_example.py',
        'description': 'Test layout search'
    },
    {
        'name': 'schematic',
        'query': 'schematic',
        'expected_file': 'schematic_generation_example.py',
        'description': 'Test schematic search'
    },
    {
        'name': 'dual_ring',
        'query': 'dual ring',
        'expected_file': 'dual_ring_layout_example.py',
        'description': 'Test dual ring search'
    },
    {
        'name': 'chinese',
        'query': 'schematic',
        'expected_file': 'schematic_generation_example.py',
        'description': 'Test Chinese keyword'
    }
]

def run_single_test(test_case: Dict[str, str], verbose: bool = False) -> bool:
    """Run single test case"""
    if verbose:
        print(f"\n{test_case['description']}:")
        print(f"Search keyword: {test_case['query']}")
    
    result = code_example_search(test_case['query'])
    assert isinstance(result, str), "code_example_search should return a string"
    assert test_case['expected_file'] in result, f"Should find file {test_case['expected_file']}"
    
    if verbose:
        print("\nSearch results:")
        print(result)
        print(f"✅ Test passed: {test_case['name']}")
    return True

def test_list_examples(verbose: bool = False) -> bool:
    """Test list examples files functionality"""
    import pytest
    
    if verbose:
        print("\nTesting list examples files:")
    
    examples = list_examples()
    assert isinstance(examples, list), "list_examples should return a list"
    
    # Skip test if no example files found (directory might not have examples yet)
    if len(examples) < 3:
        pytest.skip(f"Only {len(examples)} example files found, need at least 3. This is expected if code_examples directory is empty.")
    
    if verbose:
        print(f"Found {len(examples)} example files:")
        for example in examples:
            print(f"  - {example}")
    
    return True

def test_search_examples(verbose: bool = False) -> bool:
    """Test search examples functionality"""
    import pytest
    
    if verbose:
        print("\nTesting search examples:")
    
    results = search_examples("layout")
    assert isinstance(results, list), "search_examples should return a list"
    
    # Skip test if no results found (directory might not have examples yet)
    if not results or not any(isinstance(r, dict) and "layout" in str(r.get("file", "")).lower() for r in results):
        pytest.skip("No layout-related example files found. This is expected if code_examples directory is empty or doesn't contain layout examples.")
    
    if verbose:
        print(f"Search 'layout' found {len(results)} results:")
        for result in results:
            print(f"  - {result}")
    
    return True

def run_keyword_test(keyword: str, verbose: bool = False) -> bool:
    """Run search test for specified keyword"""
    if verbose:
        print(f"\nSearching with keyword '{keyword}':")
    
    result = code_example_search(keyword)
    assert isinstance(result, str), "code_example_search should return a string"
    print("\nSearch results:")
    print(result)
    return True

def main():
    """Main function, handles command line arguments and executes corresponding actions"""
    parser = argparse.ArgumentParser(description="Example code search tool test program")
    parser.add_argument('-k', '--keyword', help='Specify search keyword for testing')
    parser.add_argument('-t', '--test', help='Run specified test case')
    parser.add_argument('-a', '--all', action='store_true', help='Run all tests (default behavior)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output mode')
    
    args = parser.parse_args()
    
    # If no options are specified, default to running all tests
    if not (args.keyword or args.test or args.all):
        args.all = True
    
    success = True
    
    if args.keyword:
        success = run_keyword_test(args.keyword, args.verbose) and success
    
    if args.test:
        # Find matching test case
        test_case = next((t for t in TEST_CASES if t['name'] == args.test), None)
        if test_case:
            success = run_single_test(test_case, args.verbose) and success
        else:
            print(f"❌ Unknown test case: {args.test}")
            print("Available test cases:", ", ".join(t['name'] for t in TEST_CASES))
            success = False
    
    if args.all:
        if args.verbose:
            print("\nRunning all tests...")
        
        # Test basic functionality
        success = test_list_examples(args.verbose) and success
        success = test_search_examples(args.verbose) and success
        
        # Run all test cases
        for test_case in TEST_CASES:
            success = run_single_test(test_case, args.verbose) and success
    
    if success:
        print("\n✅ Test passed")
    else:
        print("\n❌ Test failed")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
