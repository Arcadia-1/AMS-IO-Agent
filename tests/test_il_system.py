#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test IL File Running System

Usage:
python test_il_system.py [options]

Options:
    -h, --help          Show help information
    -l, --list         List all IL files
    -r, --run          Run the latest IL file
    -i, --interactive  Interactive selection and run IL file
    -a, --all          List files and run latest file (default behavior)
    -q, --quiet        Quiet mode
"""

import sys
import argparse
import json
from pathlib import Path
from datetime import datetime

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.il_runner_tool import run_il_file, list_il_files, run_il_with_screenshot, clear_all_figures_in_window, screenshot_current_window

def find_latest_il_file():
    """Find the latest IL file"""
    dir_path = Path("output")
    
    # Recursively find all timestamp directories
    timestamp_dirs = []
    if dir_path.exists():
        # Recursively search for all directories that match timestamp format
        for item in dir_path.rglob("*"):
            if item.is_dir() and item.name.replace('_', '').isdigit():
                # Check if it's a timestamp format directory
                try:
                    datetime.strptime(item.name, "%Y%m%d_%H%M%S")
                    timestamp_dirs.append(item)
                except ValueError:
                    continue
    
    if not timestamp_dirs:
        print("   ⚠️  No timestamp directories found")
        return None
    
    # Sort by timestamp, get the latest directory
    timestamp_dirs.sort(key=lambda x: datetime.strptime(x.name, "%Y%m%d_%H%M%S"))
    latest_dir = timestamp_dirs[-1]
    
    # Find IL files in the latest directory
    il_files = list(latest_dir.glob("*.il")) + list(latest_dir.glob("*.skill"))
    
    if not il_files:
        print(f"   ⚠️  No IL files found in latest directory {latest_dir.name}")
        return None
    
    # Return the latest IL file
    return il_files[0]  # Usually there's only one IL file per directory

def list_all_files(quiet=False):
    """List all IL files recursively"""
    if not quiet:
        print("\n1. Listing all IL files (recursively)...")
    
    dir_path = Path("output")
    all_il_files = []
    
    # Recursively find all IL files in the output directory
    if dir_path.exists():
        il_files = list(dir_path.rglob("*.il")) + list(dir_path.rglob("*.skill"))
        all_il_files.extend(il_files)
    
    if not all_il_files:
        print("   ⚠️  No IL files found")
        return False
    
    # Sort by timestamp
    def extract_timestamp(file_path):
        # Try to extract timestamp from parent directory name
        dir_name = file_path.parent.name
        try:
            return datetime.strptime(dir_name, "%Y%m%d_%H%M%S")
        except ValueError:
            # If not in timestamp directory, use file modification time
            return datetime.fromtimestamp(file_path.stat().st_mtime)
    
    all_il_files.sort(key=extract_timestamp, reverse=True)
    
    print(f"   📁 Found {len(all_il_files)} IL files:")
    for i, file_path in enumerate(all_il_files, 1):
        timestamp = extract_timestamp(file_path)
        # Show relative path from output directory
        try:
            rel_path = file_path.relative_to(dir_path)
            print(f"   {i}. {rel_path} (Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        except ValueError:
            print(f"   {i}. {file_path} (Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
    
    return True

def test_list_all_files():
    """Test list_all_files function"""
    result = list_all_files(quiet=True)
    assert isinstance(result, bool), "list_all_files should return a boolean"

def run_latest_file(quiet=False, lib=None, cell=None, view="layout"):
    """Run the latest IL file"""
    if not quiet:
        print("\n2. Running the latest IL file...")
    try:
        latest_file = find_latest_il_file()
        
        if latest_file:
            if not quiet:
                print(f"   📄  Running latest file: {latest_file.parent.name}/{latest_file.name}")
            if lib and cell:
                result = run_il_file(str(latest_file), lib=lib, cell=cell, view=view)
            else:
                # Use default values when lib and cell are not provided
                result = run_il_file(str(latest_file), lib="TestLib", cell="TestCell", view=view)
            assert isinstance(result, str), "run_il_file should return a string"
            print(f"   🚀 {result}")
            return True
        else:
            print("   ⚠️  No valid IL file found")
            return False
            
    except Exception as e:
        print(f"   ❌  Error occurred while running latest IL file: {e}")
        return False

def test_run_latest_file():
    """Test run_latest_file function"""
    import pytest
    try:
        result = run_latest_file(quiet=True)
        assert isinstance(result, bool), "run_latest_file should return a boolean"
    except Exception as e:
        pytest.skip(f"run_latest_file requires IL files and Virtuoso: {e}")

def run_latest_file_with_screenshot(quiet=False, lib=None, cell=None, view="layout"):
    """Run the latest IL file and save screenshot"""
    if not quiet:
        print("\n3. Running the latest IL file and saving screenshot...")
    try:
        latest_file = find_latest_il_file()
        
        if latest_file:
            if not quiet:
                print(f"   📄  Running latest file: {latest_file.parent.name}/{latest_file.name}")
            if lib and cell:
                result = run_il_with_screenshot(str(latest_file), lib=lib, cell=cell, view=view)
            else:
                # Use default values when lib and cell are not provided
                result = run_il_with_screenshot(str(latest_file), lib="TestLib", cell="TestCell", view=view)
            
            # Parse JSON result
            if not isinstance(result, str):
                print("   ❌  Incorrect result type")
                return False
            result_data = json.loads(result)
            
            # Print execution status
            status_emoji = "✅" if result_data["status"] == "success" else "❌"
            print(f"   {status_emoji} {result_data['message']}")
            
            # Print screenshot path (if any)
            if result_data["screenshot_path"]:
                print(f"   📸  Screenshot path: {result_data['screenshot_path']}")
            
            # Print detailed observation records
            if not quiet and result_data["observations"]:
                print("\n   📝  Detailed execution record:")
                for obs in result_data["observations"]:
                    print(f"      {obs}")
            
            return result_data["status"] == "success"
        else:
            print("   ⚠️  No valid IL file found")
            return False
            
    except Exception as e:
        print(f"   ❌  Error occurred while running latest IL file: {e}")
        return False

def run_selected_file(file_path, quiet=False, lib=None, cell=None, view="layout"):
    """Run the selected IL file"""
    if not quiet:
        print(f"\n   📄  Running selected file: {Path(file_path).name}")
    if lib and cell:
        result = run_il_file(str(file_path), lib=lib, cell=cell, view=view)
    else:
        # Use default values when lib and cell are not provided
        result = run_il_file(str(file_path), lib="TestLib", cell="TestCell", view=view)
    print(f"   🚀 {result}")
    return True

def interactive_select_and_run(quiet=False):
    """Interactive selection and run IL file"""
    if not quiet:
        print("\nSelect IL file to run...")
    try:
        dir_path = Path("output")
        all_il_files = []
        
        # Recursively find all IL files in the output directory
        if dir_path.exists():
            il_files = list(dir_path.rglob("*.il")) + list(dir_path.rglob("*.skill"))
            all_il_files.extend(il_files)
        
        if not all_il_files:
            print("   ⚠️  No IL files found")
            return False
            
        # Extract timestamp and sort
        def extract_timestamp(file_path):
            # Try to extract timestamp from parent directory name
            dir_name = file_path.parent.name
            try:
                return datetime.strptime(dir_name, "%Y%m%d_%H%M%S")
            except ValueError:
                # If not in timestamp directory, use file modification time
                return datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Sort by timestamp
        files_with_time = [(f, extract_timestamp(f)) for f in all_il_files]
        files_with_time.sort(key=lambda x: x[1], reverse=True)
        
        # Display file list
        print("\nAvailable IL files:")
        for idx, (file, timestamp) in enumerate(files_with_time, 1):
            # Show relative path from output directory
            try:
                rel_path = file.relative_to(dir_path)
                print(f"{idx}. {rel_path} (Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
            except ValueError:
                print(f"{idx}. {file} (Created: {timestamp.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Get user choice
        while True:
            try:
                choice = input("\nPlease select the file number to run (1-{0}): ".format(len(files_with_time)))
                idx = int(choice) - 1
                if 0 <= idx < len(files_with_time):
                    selected_file = files_with_time[idx][0]
                    return run_selected_file(selected_file, quiet)
                else:
                    print("❌ Invalid choice, please enter a number between 1-{0}".format(len(files_with_time)))
            except ValueError:
                print("❌ Please enter a valid number")
            except KeyboardInterrupt:
                print("\nSelection cancelled")
                return False
            
    except Exception as e:
        print(f"   ❌  Error occurred during interactive selection: {e}")
        return False

def clear_figures_in_window(quiet=False):
    """Clear all components in the current window"""
    if not quiet:
        print("\n  Clearing all components in the current window...")
    try:
        result = clear_all_figures_in_window()
        print(f"   {result}")
        if isinstance(result, str) and "✅" in result:
            return True
        else:
            return False
    except Exception as e:
        print(f"   ❌  Error occurred while clearing components: {e}")
        return False

def test_clear_figures_in_window():
    """Test clear_figures_in_window function"""
    import pytest
    try:
        result = clear_figures_in_window(quiet=True)
        assert isinstance(result, bool), "clear_figures_in_window should return a boolean"
    except Exception as e:
        pytest.skip(f"clear_figures_in_window requires Virtuoso: {e}")

def screenshot_window_only(quiet=False):
    """Take a screenshot of the current Virtuoso window only, without running IL file"""
    if not quiet:
        print("\n4. Taking screenshot of the current Virtuoso window only...")
    try:
        result = screenshot_current_window()
        if not isinstance(result, str):
            print("   ❌  Incorrect result type")
            return False
        result_data = json.loads(result)
        status_emoji = "✅" if result_data["status"] == "success" else "❌"
        print(f"   {status_emoji} {result_data['message']}")
        if result_data["screenshot_path"]:
            print(f"   📸  Screenshot path: {result_data['screenshot_path']}")
        return result_data["status"] == "success"
    except Exception as e:
        print(f"   ❌  Error occurred while taking screenshot: {e}")
        return False

def main():
    """Main function, handles command line arguments and executes corresponding operations"""
    parser = argparse.ArgumentParser(description="IL File System Test Program")
    parser.add_argument('-l', '--list', action='store_true', help='List all IL files')
    parser.add_argument('-r', '--run', action='store_true', help='Run the latest IL file')
    parser.add_argument('-s', '--screenshot', action='store_true', help='Run the latest IL file and save screenshot')
    parser.add_argument('-i', '--interactive', action='store_true', help='Interactive selection and run IL file')
    parser.add_argument('-a', '--all', action='store_true', help='Execute all steps (default behavior)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode')
    parser.add_argument('-c', '--clear', action='store_true', help='Clear all components in the current window')
    parser.add_argument('-S', '--only-screenshot', action='store_true', help='Take screenshot of the current Virtuoso window only, without running IL file (use -S)')
    parser.add_argument('--lib', dest='lib', default=None, help='Target library name to run on (optional)')
    parser.add_argument('--cell', dest='cell', default=None, help='Target cell name to run on (optional)')
    parser.add_argument('--view', dest='view', default='layout', help='Target view name (default: layout)')
    
    args = parser.parse_args()

    # If only clear, execute and return
    if args.clear:
        if not args.quiet:
            print("\nExecuting clear current window components test...")
        success = clear_figures_in_window(args.quiet)
        if not args.quiet:
            if success:
                print("\n✅ Clear test completed!")
            else:
                print("\n❌ Clear test failed")
        return 0 if success else 1

    # Only screenshot current window
    if args.only_screenshot:
        result = screenshot_window_only(args.quiet)
        return 0 if result else 1

    # If no options are specified, default to executing all steps
    if not (args.list or args.run or args.screenshot or args.interactive or args.all):
        args.all = True

    if not args.quiet:
        print("Starting IL system test...")

    success = True

    # List files
    if args.list or args.all:
        success = list_all_files(args.quiet) and success

    # Interactive selection and run
    if args.interactive:
        success = interactive_select_and_run(args.quiet) and success
        return 0 if success else 1

    # Run latest file
    if args.run or args.all:
        success = run_latest_file(args.quiet, lib=args.lib, cell=args.cell, view=args.view) and success

    # Run latest file and save screenshot
    if args.screenshot or args.all:
        success = run_latest_file_with_screenshot(args.quiet, lib=args.lib, cell=args.cell, view=args.view) and success

    if not args.quiet:
        if success:
            print("\n✅ Test completed!")
        else:
            print("\n❌ Error occurred during test")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 