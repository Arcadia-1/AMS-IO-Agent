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
    return _bridge_get_current_design()

def parse_lvs_summary(file_path):
    """
    Parse LVS summary file, extract key LVS comparison result information.
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        
        # Find key sections
        overall_results = ""
        cell_summary = ""
        summary_section = ""
        # lvs_result = "unknown"  # LVS check result: CORRECT or INCORRECT
        
        in_overall_section = False
        in_cell_summary = False
        in_summary_section = False
        
        for i, line in enumerate(lines):
            # Find OVERALL COMPARISON RESULTS section
            if "OVERALL COMPARISON RESULTS" in line:
                in_overall_section = True
                overall_results += line
                continue
            elif in_overall_section:
                overall_results += line
                # Check if contains CORRECT or INCORRECT
                # if "INCORRECT" in line:
                #     lvs_result = "INCORRECT"
                # elif "CORRECT" in line:
                #     lvs_result = "CORRECT"
                # Stop collecting if next major section is encountered
                if "CELL  SUMMARY" in line or "LVS PARAMETERS" in line:
                    in_overall_section = False
            
            # Find CELL SUMMARY section
            if "CELL  SUMMARY" in line:
                in_cell_summary = True
                cell_summary += line
                continue
            elif in_cell_summary:
                cell_summary += line
                # Also check results in CELL SUMMARY section
                # if "INCORRECT" in line:
                #     lvs_result = "INCORRECT"
                # elif "CORRECT" in line:
                #     lvs_result = "CORRECT"
                # Stop collecting if next major section is encountered
                if "LVS PARAMETERS" in line or "SUMMARY" in line:
                    in_cell_summary = False
            
            # Find final SUMMARY section
            if "SUMMARY" in line and "Total CPU Time" in lines[i+1] if i+1 < len(lines) else False:
                in_summary_section = True
                summary_section += line
                continue
            elif in_summary_section and "Total Elapsed Time" in line:
                summary_section += line
                in_summary_section = False
            elif in_summary_section:
                summary_section += line
        
        # Combine results
        result = "LVS check result summary:\n"
        result += "=" * 50 + "\n\n"
        
        # Add LVS check result status
        # if lvs_result == "CORRECT":
        #     result += "✅ LVS check result: passed (CORRECT)\n\n"
        # elif lvs_result == "INCORRECT":
        #     result += "❌ LVS check result: failed (INCORRECT)\n\n"
        # else:
        #     result += "⚠️ LVS check result: unknown\n\n"
        
        if overall_results:
            result += "Overall comparison results:\n"
            result += overall_results + "\n"
        
        if cell_summary:
            result += "Cell summary:\n"
            result += cell_summary + "\n"
        
        if summary_section:
            result += "Execution summary:\n"
            result += summary_section + "\n"
        
        # If no key information is found, return the first 100 lines of the original content
        if not overall_results and not cell_summary and not summary_section:
            result = "LVS original summary content (first 100 lines):\n" + "=" * 50 + "\n"
            result += ''.join(lines[:100])
        
        return result
        
    except Exception as e:
        return f"Failed to parse LVS summary file: {e}"

def generate_report(lvs_results, output_file):
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("LVS report\n")
            f.write("=" * 50 + "\n\n")
            if isinstance(lvs_results, str):
                f.write(lvs_results)
            else:
                # Compatible with old format, directly output stringified content
                f.write(str(lvs_results))
        return True, f"Report generated: {output_file}"
    except Exception as e:
        return False, f"Error generating report: {str(e)}"

@tool
def run_lvs_va(lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout", tech_node: str = "T28") -> str:
    """
    Run LVS check script and generate violation report.
    
    If lib/cell are provided, the tool will open that specific cellView (only open, not set current edit) and run LVS on it.
    Otherwise, it will attempt to infer (lib, cell) from the current design. A timestamped report is always generated.

    Args:
        lib: Target library name (optional). If None, use current design's library.
        cell: Target cell name (optional). If None, use current design's cell.
        view: Target view name (default: "layout"). Used to choose the viewType mapping when opening the cellView.
        tech_node: Technology node (default: "T28"). Must be "T28" or "T180". Do not mix different tech nodes.
                   Note: T180 may not have LVS script.

    Returns:
        String description of the run result.
    """
    try:
        # Validate tech_node
        if tech_node not in ["T28", "T180"]:
            return f"❌ Error: Invalid tech_node '{tech_node}'. Must be 'T28' or 'T180'"
        
        # Get script path based on tech_node
        script_path = Path(f"src/scripts/calibre/{tech_node}/run_lvs_{tech_node}.csh")
        
        # Check if script exists
        if not script_path.exists():
            return f"❌ Error: LVS script file not found: {script_path} (tech_node: {tech_node})"
        
        # Ensure script has execution permissions
        script_path.chmod(0o755)
        
        # If lib/cell provided, open the specified cell first
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            ui_redraw(timeout=5)
        # Get current design information when not explicitly specified
        if not lib or not cell:
            lib, cell, _ = get_current_design()
        if lib is None or cell is None:
            return "❌ Error: Cannot get current design information, please ensure the design is open"
        
        # Execute csh script using bridge_utils
        try:
            # Note: run_lvs.csh expects arguments in order: <library> <topCell> [view]
            result = execute_csh_script(str(script_path), lib, cell, view, timeout=300)
            
            if result and not result.startswith("Remote csh execution failed"):
                # Generate report filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                lvs_summary_file = f"output/lvs/{cell}.lvs.summary"
                report_file = f"output/{cell}_lvs_report_{timestamp}.txt"
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(report_file), exist_ok=True)
                
                # Parse LVS report and generate report (even if no violations)
                lvs_results = parse_lvs_summary(lvs_summary_file)
                success, msg = generate_report(lvs_results, report_file)
                
                if success:
                    # Read generated report content
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        # Build simplified output information
                        output = [
                            "✅ LVS check completed!",
                            f"\nReport location: {report_file}",
                            "\nReport content:",
                            "=" * 50,
                            report_content,
                            "=" * 50
                        ]
                        
                        return "\n".join(output)
                    except Exception as e:
                        return f"✅ LVS check completed!\n{msg}\nNote: Cannot read report content: {str(e)}"
                else:
                    return f"✅ LVS check completed, but report generation failed: {msg}"
            else:
                return f"❌ LVS check failed"
            
        except subprocess.CalledProcessError as e:
            return f"❌ LVS check failed"
            
    except Exception as e:
        return f"❌ Error running LVS check: {e}" 

@tool
def run_lvs(cell: Optional[str] = None, lib: Optional[str] = None, view: str = "layout", tech_node: str = "T28") -> str:
    """
    Run LVS check script and generate violation report.
    
    If not given, it will use historical default lib/cell. Otherwise, the specified (lib, cell) is opened (only open) and used.
    A timestamped report is always generated.

    Args:
        cell: Layout cell name (optional). If None, use default.
        lib:  Library name (optional). If None, use default.
        view: Target view name (default: "layout"). Used to choose the viewType mapping when opening the cellView.
        tech_node: Technology node (default: "T28"). Must be "T28" or "T180". Do not mix different tech nodes.
                   Note: T180 may not have LVS script.

    Returns:
        String description of the run result.
    """
    try:
        # Validate tech_node
        if tech_node not in ["T28", "T180"]:
            return f"❌ Error: Invalid tech_node '{tech_node}'. Must be 'T28' or 'T180'"
        
        # Get script path based on tech_node
        script_path = Path(f"src/scripts/calibre/{tech_node}/run_lvs_{tech_node}.csh")
        
        # Check if script exists
        if not script_path.exists():
            return f"❌ Error: LVS script file not found: {script_path} (tech_node: {tech_node})"
        
        # Ensure script has execution permissions
        script_path.chmod(0o755)
        
        # If not given, keep the historical hardcoded default; otherwise use provided
        if not cell:
            cell = "test_v2"  # default
        if not lib:
            lib = "LLM_Layout_Design"  # default

        # Try to open the specified/default cell before running
        try:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            ui_redraw(timeout=5)
        except Exception:
            pass
        
        # Execute csh script using bridge_utils
        try:
            # Note: run_lvs.csh expects arguments in order: <library> <topCell> [view]
            result = execute_csh_script(str(script_path), lib, cell, view, timeout=300)
            
            if result and not result.startswith("Remote csh execution failed"):
                # Generate report filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                lvs_summary_file = f"output/lvs/{cell}.lvs.summary"
                report_file = f"output/{cell}_lvs_report_{timestamp}.txt"
                
                # Ensure output directory exists
                os.makedirs(os.path.dirname(report_file), exist_ok=True)
                
                # Parse LVS report and generate report (even if no violations)
                lvs_results = parse_lvs_summary(lvs_summary_file)
                success, msg = generate_report(lvs_results, report_file)
                
                if success:
                    # Read generated report content
                    try:
                        with open(report_file, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        # Build simplified output information
                        output = [
                            "✅ LVS check completed!",
                            f"\nReport location: {report_file}",
                            "\nReport content:",
                            "=" * 50,
                            report_content,
                            "=" * 50
                        ]
                        
                        return "\n".join(output)
                    except Exception as e:
                        return f"✅ LVS check completed!\n{msg}\nNote: Cannot read report content: {str(e)}"
                else:
                    return f"✅ LVS check completed, but report generation failed: {msg}"
            else:
                return f"❌ LVS check failed"
            
        except subprocess.CalledProcessError as e:
            return f"❌ LVS check failed"
            
    except Exception as e:
        return f"❌ Error running LVS check: {e}" 