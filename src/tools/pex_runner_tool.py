from pathlib import Path
import os
import subprocess
from typing import Optional
from datetime import datetime
from smolagents import tool
import re
from dotenv import load_dotenv
load_dotenv()
from .bridge_utils import get_current_design as _bridge_get_current_design, execute_csh_script, open_cell_view_by_type, ui_redraw
import shutil
import time

def get_current_design() -> tuple[Optional[str], Optional[str], Optional[str]]:
    return _bridge_get_current_design()

def parse_pex_capacitance(netlist_file: Path) -> str:
    """
    Directly extract all content between mgc_rve_cell_start and mgc_rve_cell_end in PEX netlist file, output as-is.
    """
    if not netlist_file.exists():
        return "PEX netlist file not found, unable to extract content."
    try:
        with open(netlist_file, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        in_cell = False
        cell_content = []
        for line in lines:
            if line.startswith('mgc_rve_cell_start'):
                in_cell = True
                cell_content.append(line)
                continue
            if line.startswith('mgc_rve_cell_end'):
                cell_content.append(line)
                in_cell = False
                break  # Only extract the first cell block
            if in_cell:
                cell_content.append(line)
        if not cell_content:
            return "No content found between mgc_rve_cell_start and mgc_rve_cell_end in PEX netlist."
        return "\nPEX main cell original content excerpt:\n" + ''.join(cell_content)
    except Exception as e:
        return f"Failed to extract PEX netlist content: {e}"

@tool
def run_pex(lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout", tech_node: str = "T28") -> str:
    """
    Run PEX extraction script and generate report.
    
    If lib/cell are provided, the tool will open that specific cellView (only open, not set current edit) and run PEX on it.
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
        
        # Use unified script at top level
        script_path = Path("src/scripts/calibre/run_pex.csh")
        
        # Check if script exists
        if not script_path.exists():
            return f"❌ Error: PEX script file not found: {script_path}"
        script_path.chmod(0o755)
        # If lib/cell provided, open the specified cell first
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="r", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            ui_redraw(timeout=5)
        # Fall back to current design if not explicitly provided
        if not lib or not cell:
            lib, cell, _ = get_current_design()
        if lib is None or cell is None:
            return "❌ Error: Cannot get current design information, please ensure the design is open"
        
        # Execute csh script using bridge_utils
        try:
            # Generate timestamped PEX directory to avoid conflicts in parallel runs
            # Use timestamp + process ID + microseconds for maximum uniqueness
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            microseconds = int(time.time() * 1000000) % 1000000
            process_id = os.getpid()
            pex_dir = Path(f"output/pex_{timestamp_str}_{process_id}_{microseconds}")
            # Note: run_pex.csh expects arguments in order: <library> <topCell> [view] [tech_node] [runDir]
            result = execute_csh_script(str(script_path), lib, cell, view, tech_node, str(pex_dir), timeout=300)
            print(f"PEX result: {result}")
            netlist_file = pex_dir / f"{cell}.pex.netlist"
            log_file = pex_dir / f"PIPO.LOG.{cell}"
            report_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = Path(f"output/{cell}_pex_report_{report_timestamp}.txt")
            os.makedirs(report_file.parent, exist_ok=True)
            # Generate report
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("PEX Extraction Report\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Design Library: {lib}\nDesign Cell: {cell}\n\n")
                f.write(f"PEX netlist path: {netlist_file if netlist_file.exists() else 'Not generated'}\n")
                f.write(f"PEX log file: {log_file if log_file.exists() else 'Not generated'}\n\n")
                if result and not result.startswith("Remote csh execution failed"):
                    f.write("✅ PEX extraction process executed successfully!\n\n")
                else:
                    f.write("❌ PEX extraction process execution failed!\n\n")
                    # Attempt to remove the pex output directory before returning
                    try:
                        if pex_dir.exists():
                            shutil.rmtree(pex_dir)
                    except Exception:
                        pass
                    return "PEX process failed"  # Terminate directly after process failure, no longer parse log files, return string to ensure type consistency
                     # Log summary
                if log_file.exists():
                    f.write("Log summary:\n")
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='replace') as lf:
                            lines = lf.readlines()
                            for line in lines[-2:]:
                                f.write(line)
                    except Exception as e:
                        f.write(f"Log reading failed: {e}\n")
                else:
                    f.write("PEX log file not found.\n")
                # Add capacitance parsing
                f.write("\n" + parse_pex_capacitance(netlist_file) + "\n")
                f.write("\n" + "=" * 50 + "\n")
            # Return report content
            try:
                with open(report_file, 'r', encoding='utf-8') as f:
                    report_content = f.read()
                # Attempt to remove the pex output directory before returning
                try:
                    if pex_dir.exists():
                        shutil.rmtree(pex_dir)
                except Exception:
                    pass
                return f"✅ PEX process completed!\nReport location: {report_file}\n\nReport content:\n{'='*50}\n{report_content}\n{'='*50}"
            except Exception as e:
                # Attempt to remove the pex output directory before returning
                try:
                    if pex_dir.exists():
                        shutil.rmtree(pex_dir)
                except Exception:
                    pass
                return f"✅ PEX process completed! Report generated but reading failed: {e}"
        except subprocess.CalledProcessError:
            # Attempt to remove the pex output directory before returning
            # Note: pex_dir may not be defined if error occurs before timestamp generation
            try:
                if 'pex_dir' in locals() and pex_dir.exists():
                    shutil.rmtree(pex_dir)
            except Exception:
                pass
            return f"❌ PEX process execution failed"
    except Exception as e:
        return f"❌ Error running PEX process: {e}" 