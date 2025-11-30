from pathlib import Path
import os
import json
import subprocess
from typing import Optional, List, Dict, Union
from datetime import datetime
from smolagents import tool
import re
from collections import defaultdict
from .bridge_utils import get_current_design as _bridge_get_current_design, execute_csh_script, open_cell_view_by_type, ui_redraw

def get_current_design() -> tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Get current design information
    
    Returns:
        (lib, cell, view) tuple, returns (None, None, None) if failed to get
    """
    result = _bridge_get_current_design()
    return result

def parse_drc_summary(file_path):
    """
    Directly return all content after the line "RULECHECK RESULTS STATISTICS (BY CELL)", output as-is.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        start_idx = None
        for i, line in enumerate(lines):
            if "RULECHECK RESULTS STATISTICS (BY CELL)" in line:
                start_idx = i
                break
        if start_idx is None:
            return "DRC statistics section (BY CELL) not found."
        # Return this line and all content after it
        return "\nDRC original statistics content excerpt:\n" + ''.join(lines[start_idx:])
    except Exception as e:
        return f"Failed to extract DRC statistics content: {e}"

def generate_report(violations, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("DRC report\n")
            f.write("=" * 50 + "\n\n")
            if isinstance(violations, str):
                f.write(violations)
            else:
                # Compatible with old format, directly output stringified content
                f.write(str(violations))
        return True, f"Report generated: {output_file}"
    except Exception as e:
        return False, f"Error generating report: {str(e)}"

@tool
def run_drc_va(lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout", tech_node: str = "T28") -> str:
    """
    Run DRC check script and generate violation report.
    
    If lib/cell are provided, the tool will open that specific cellView (only open, not set current edit) and run DRC on it.
    Otherwise, it will attempt to infer (lib, cell) from the current design. A timestamped report is always generated.

    Args:
        lib: Target library name (optional). If None, use current design's library.
        cell: Target cell name (optional). If None, use current design's cell.
        view: Target view name (default: "layout"). Used to choose the viewType mapping when opening the cellView.
        tech_node: Technology node (default: "T28"). Must be "T28" or "T180". Do not mix different tech nodes.

    Returns:
        String description of the run result.
    """
    try:
        # Validate tech_node
        if tech_node not in ["T28", "T180"]:
            return f"❌ Error: Invalid tech_node '{tech_node}'. Must be 'T28' or 'T180'"
        
        # Get script path based on tech_node
        script_path = Path(f"src/scripts/calibre/{tech_node}/run_drc_{tech_node}.csh")
        
        # Check if script exists
        if not script_path.exists():
            return f"❌ Error: DRC script file not found: {script_path} (tech_node: {tech_node})"
        
        # Ensure script has execution permissions
        script_path.chmod(0o755)
        
        # If lib/cell provided, open specified cell first
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            ui_redraw(timeout=5)
        # Get current design if not explicitly specified
        if not lib or not cell:
            lib, cell, _ = get_current_design()
        if lib is None or cell is None:
            return "❌ Error: Cannot get current design information, please ensure the design is open"
        
        # Execute csh script using bridge_utils
        try:
            # Note: run_drc.csh expects arguments in order: <library> <topCell> [view]
            result = execute_csh_script(str(script_path), lib, cell, view, timeout=30)
            
            if result and not result.startswith("Remote csh execution failed"):
                # Generate report filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                drc_summary_file = f"output/drc/{cell}.drc.summary"
                report_file = f"output/{cell}_drc_report_{timestamp}.txt"
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(report_file), exist_ok=True)
                
                # Parse DRC report and generate report (even if no violations)
                violations = parse_drc_summary(drc_summary_file)
                success, msg = generate_report(violations, report_file)
                
                if success:
                    # Read generated report content
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        # Build simplified output information
                        output = [
                            "✅ DRC check completed!",
                            f"\nReport location: {report_file}",
                            "\nReport content:",
                            "=" * 50,
                            report_content,
                            "=" * 50
                        ]
                        
                        return "\n".join(output)
                    except Exception as e:
                        return f"✅ DRC check completed!\n{msg}\nNote: Cannot read report content: {str(e)}"
                else:
                    return f"✅ DRC check completed, but report generation failed: {msg}"
            else:
                return f"❌ DRC check failed"
            
        except subprocess.CalledProcessError as e:
            return f"❌ DRC check failed"
            
    except Exception as e:
        return f"❌ Error running DRC check: {e}" 

@tool
def run_drc(cell: Optional[str] = None, lib: Optional[str] = None, view: str = "layout", tech_node: str = "T28") -> str:
    """
    Run DRC check script and generate a report.
    - If cell/lib are not provided, automatically get them from the current open design (same behavior as run_drc_va).
    - Generates a timestamped report regardless of violations and echoes the report content.

    Args:
        cell: Layout cell name (optional). If None, will be obtained from the current design.
        lib:  Library name (optional). If None, will be obtained from the current design.
        view: Target view name (default: "layout"). Used to choose the viewType mapping when opening the cellView.
        tech_node: Technology node (default: "T28"). Must be "T28" or "T180". Do not mix different tech nodes.

    Returns:
        A string description of the run result.
    """
    try:
        # Validate tech_node
        if tech_node not in ["T28", "T180"]:
            return f"❌ Error: Invalid tech_node '{tech_node}'. Must be 'T28' or 'T180'"
        
        # Get script path based on tech_node
        script_path = Path(f"src/scripts/calibre/{tech_node}/run_drc_{tech_node}.csh")
        
        # Check if script exists
        if not script_path.exists():
            return f"❌ Error: DRC script file not found: {script_path} (tech_node: {tech_node})"

        # Ensure script is executable
        script_path.chmod(0o755)

        # If lib/cell provided, open specified cell first
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            ui_redraw(timeout=5)

        # Fetch lib/cell from current design if not provided
        if not cell or not lib:
            lib_auto, cell_auto, _ = get_current_design()
            if not lib:
                lib = lib_auto
            if not cell:
                cell = cell_auto

        if lib is None or cell is None:
            return "❌ Error: Cannot get current design information, please ensure the design is open or pass cell/lib explicitly"

        # Execute csh script for DRC (use a generous timeout)
        try:
            # Note: run_drc.csh expects arguments in order: <library> <topCell> [view]
            result = execute_csh_script(str(script_path), lib, cell, view, timeout=300)

            if result and not str(result).startswith("Remote csh execution failed"):
                # Generate timestamped report file
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                drc_summary_file = f"output/drc/{cell}.drc.summary"
                report_file = f"output/{cell}_drc_report_{timestamp}.txt"

                # Ensure output directory exists
                os.makedirs(os.path.dirname(report_file), exist_ok=True)

                # Parse and generate report (even if no violations)
                violations = parse_drc_summary(drc_summary_file)
                success, msg = generate_report(violations, report_file)

                if success:
                    # Echo report content
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()

                        output = [
                            "✅ DRC check completed!",
                            f"\nReport location: {report_file}",
                            "\nReport content:",
                            "=" * 50,
                            report_content,
                            "=" * 50
                        ]
                        return "\n".join(output)
                    except Exception as e:
                        return f"✅ DRC check completed!\n{msg}\nNote: Cannot read report content: {str(e)}"
                else:
                    return f"✅ DRC check completed, but report generation failed: {msg}"
            else:
                return "❌ DRC check failed"

        except subprocess.CalledProcessError:
            return "❌ DRC check failed"

    except Exception as e:
        return f"❌ Error running DRC check: {e}"