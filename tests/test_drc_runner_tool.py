"""
DRC Check Tool Test Module

Usage:
python test_drc_runner_tool.py [options]

Options:
    -h, --help          Show help information
    -i, --info         Show only current design information
    -r, --run          Run DRC check
    -a, --all          Show design information and run DRC check (default behavior)
    -q, --quiet        Quiet mode, show only error messages
    --lib LIB          Target library name (optional)
    --cell CELL        Target cell name (optional)
    --view VIEW        Target view name (default: layout)
    --tech TECH        Technology node: T28 or T180 (default: T28)

Examples:
    # Run DRC on specific design with T28
    python test_drc_runner_tool.py --lib LLM_Layout_Design --cell test1 --tech T28
    
    # Run DRC on specific design with T180
    python test_drc_runner_tool.py --lib LLM_Layout_Design --cell test1 --tech T180
    
    # Show help
    python test_drc_runner_tool.py --help
"""

import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os
import argparse

# Add project root directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.drc_runner_tool import get_current_design, run_drc

def show_design_info(quiet=False, lib=None, cell=None, view="layout"):
    """Show target/current design information.
    If lib/cell is provided, report target directly without querying current window.
    """
    if not quiet:
        print("\n1. Getting design information:")

    if lib and cell:
        if not quiet:
            print(f"Target Library: {lib}")
            print(f"Target Cell: {cell}")
            print(f"Target View: {view}")
        return True

    # Fallback to current edit view info
    lib2, cell2, view2 = get_current_design()
    if lib2 is None or cell2 is None:
        print("❌ Error: Cannot get design information, please ensure design is open")
        return False
    if not quiet:
        print(f"Library: {lib2}")
        print(f"Cell: {cell2}")
        print(f"View: {view2}")
    return True

def run_drc_check(quiet=False, lib=None, cell=None, view="layout", tech_node="T28"):
    """Run DRC check"""
    if not quiet:
        print("\n2. Running DRC check:")
    
    # If lib/cell/view provided, run on the specified cellView; otherwise fall back to current design
    if lib and cell:
        result = run_drc(cell=cell, lib=lib, view=view, tech_node=tech_node)
    else:
        result = run_drc(tech_node=tech_node)
    print(result)
    
    # Check if DRC execution failed
    if "❌" in result or "Remote csh execution failed" in result or "Error" in result:
        return False
    return True

def main():
    """Main function, handle command line arguments and execute corresponding operations"""
    parser = argparse.ArgumentParser(description="DRC Check Tool Test Program")
    parser.add_argument('-i', '--info', action='store_true', help='Show only current design information')
    parser.add_argument('-r', '--run', action='store_true', help='Run DRC check')
    parser.add_argument('-a', '--all', action='store_true', help='Show design information and run DRC check (default behavior)')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet mode, show only error messages')
    parser.add_argument('--lib', dest='lib', default=None, help='Target library name to run on (optional)')
    parser.add_argument('--cell', dest='cell', default=None, help='Target cell name to run on (optional)')
    parser.add_argument('--view', dest='view', default='layout', help='Target view name (default: layout)')
    parser.add_argument('--tech', dest='tech_node', default='T28', choices=['T28', 'T180'], help='Technology node (default: T28)')
    
    args = parser.parse_args()
    
    # If no option is specified, execute all steps by default
    if not (args.info or args.run or args.all):
        args.all = True
    
    if not args.quiet:
        print("Starting DRC tool test...")
    
    success = True
    
    # Show design information
    if args.info or args.all:
        success = show_design_info(args.quiet, lib=args.lib, cell=args.cell, view=args.view) and success
    
    # Run DRC check
    if args.run or args.all:
        if success:  # Only run DRC if design information was successfully obtained
            success = run_drc_check(args.quiet, lib=args.lib, cell=args.cell, view=args.view, tech_node=args.tech_node) and success
    
    if not args.quiet:
        if success:
            print("\n✅ Test completed!")
        else:
            print("\n❌ Errors occurred during testing")
    
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())
