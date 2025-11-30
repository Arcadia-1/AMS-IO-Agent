from pathlib import Path
from typing import Optional, Dict, Any
import os
from smolagents import tool
from datetime import datetime
from time import sleep
import json
from .bridge_utils import (
    use_ramic_bridge,
    rb_exec,
    load_skill_file,
    save_current_cellview,
    ui_redraw,
    ui_zoom_absolute_scale,
    load_script_and_take_screenshot,
    load_script_and_take_screenshot_verbose,
    open_cell_view_by_type,
    ge_open_window,
)

@tool
def run_il_file(il_file_path: str, lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout") -> str:
    """
    Run il file using skillbridge library
    
    Args:
        il_file_path: Path to il file (can be relative or absolute path)
        lib: target library name (optional)
        cell: target cell name (optional)
        view: target view name (default: "layout")
        
    Returns:
        String description of the run result
    """
    try:
        # If lib/cell provided, open specified cellView and set as current edit view
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="w", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            # Open window to display the cellView
            window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
            if not window_ok:
                return f"❌ Error: Failed to open window for {lib}/{cell}/{view}"
            ui_redraw(timeout=10)
            sleep(0.5)
        else:
            # If lib/cell not provided, try to get current cellView and set cv variable
            # This is needed because IL files often use 'cv' variable
            try:
                cv_result = rb_exec('geGetEditCellView()', timeout=10)
                if not cv_result or cv_result.strip().lower() in {'nil', 'none', ''}:
                    return f"❌ Error: No cellView is currently open. Please specify --lib and --cell options, or open a cellView in Virtuoso first."
                # Set cv variable for IL file to use
                rb_exec('cv = geGetEditCellView()', timeout=10)
            except Exception as e:
                return f"❌ Error: Failed to get current cellView: {e}. Please specify --lib and --cell options."
        # Check if file exists
        skill_path = Path(il_file_path)
        
        # If file doesn't exist, try to find it in output directory
        if not skill_path.exists():
            output_path = Path("output") / skill_path.name
            if output_path.exists():
                skill_path = output_path
            else:
                return f"❌ Error: File {il_file_path} does not exist, also not found in output directory: {skill_path.name}"
        
        # Check file extension
        if skill_path.suffix.lower() not in ['.il', '.skill']:
            return f"❌ Error: File {skill_path} is not a valid il/skill file"
        
        # Use load command to execute SKILL file directly (avoids port forwarding truncation issues)
        abs_path = str(skill_path.resolve())
        escaped_path = abs_path.replace('\\', '\\\\').replace('"', '\\"')
        load_result = rb_exec(f'load("{escaped_path}")', timeout=60)
        
        # Check if load was successful (returns 't' or empty string on success)
        if load_result and load_result.strip().lower() in {'t', 't\n', ''}:
            return f"✅ il file [{skill_path.name}] executed successfully"
        else:
            # Return detailed error information
            if load_result:
                error_details = str(load_result).strip()
                # Clean up error message for better readability
                safe_error = error_details.replace('\n', ' ').replace('\r', ' ').strip()
                if safe_error and safe_error.lower() not in {'nil', 'none'}:
                    return f"❌ il file [{skill_path.name}] execution failed\n[Error Details]: {safe_error}"
            return f"❌ il file [{skill_path.name}] execution failed (empty result - check Virtuoso connection and file path)"
            
    except Exception as e:
        return f"❌ Error occurred while running il file: {e}"

@tool
def run_il_file_with_save(il_file_path: str, lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout") -> str:
    """
    Run il file and save the current cellview (for files that modify the design)
    
    Args:
        il_file_path: Path to il file (can be relative or absolute path)
        lib: target library name (optional)
        cell: target cell name (optional)
        view: target view name (default: "layout")
        
    Returns:
        String description of the run result
    """
    try:
        # If lib/cell provided, open specified cellView and set as current edit view
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="w", timeout=30)
            if not ok:
                return f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
            # Open window to display the cellView
            window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
            if not window_ok:
                return f"❌ Error: Failed to open window for {lib}/{cell}/{view}"
            ui_redraw(timeout=10)
            sleep(0.5)
        # Check if file exists
        skill_path = Path(il_file_path)
        
        # If file doesn't exist, try to find it in output directory
        if not skill_path.exists():
            output_path = Path("output") / skill_path.name
            if output_path.exists():
                skill_path = output_path
            else:
                return f"❌ Error: File {il_file_path} does not exist, also not found in output directory: {skill_path.name}"
        
        # Check file extension
        if skill_path.suffix.lower() not in ['.il', '.skill']:
            return f"❌ Error: File {skill_path} is not a valid il/skill file"
        
        # Use load command to execute SKILL file directly (avoids port forwarding truncation issues)
        abs_path = str(skill_path.resolve())
        escaped_path = abs_path.replace('\\', '\\\\').replace('"', '\\"')
        load_result = rb_exec(f'load("{escaped_path}")', timeout=60)
        
        # Check if load was successful (returns 't' or empty string on success)
        if load_result and load_result.strip().lower() in {'t', 't\n', ''}:
            # Save the current cellview after execution
            if save_current_cellview(timeout=30):
                return f"✅ il file {skill_path.name} executed and saved successfully"
            else:
                return f"✅ il file {skill_path.name} executed successfully but save failed"
        else:
            # Return detailed error information
            if load_result:
                error_details = str(load_result).strip()
                # Clean up error message for better readability
                safe_error = error_details.replace('\n', ' ').replace('\r', ' ').strip()
                if safe_error and safe_error.lower() not in {'nil', 'none'}:
                    return f"❌ il file {skill_path.name} execution failed\n[Error Details]: {safe_error}"
            return f"❌ il file {skill_path.name} execution failed (empty result - check Virtuoso connection and file path)"
            
    except Exception as e:
        return f"❌ Error occurred while running il file: {e}"

@tool
def list_il_files(directory: str = "output") -> str:
    """
    List all il files in the specified directory, sorted by timestamp in filename (latest shown last)
    
    Args:
        directory: Directory path to search, defaults to output directory
        
    Returns:
        String containing list of il files sorted by timestamp
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists():
            return f"❌ Error: Directory {directory} does not exist"
        
        # Collect all .il and .skill files
        il_files = list(dir_path.glob("*.il")) + list(dir_path.glob("*.skill"))
        
        if not il_files:
            return f"No il files found in directory {directory}"
        
        # Extract timestamp from filename and sort
        def extract_timestamp(file_path):
            # Try to extract timestamp from filename
            name = file_path.stem  # Get filename without extension
            try:
                # Find timestamp after last underscore
                parts = name.split('_')
                if len(parts) >= 2:
                    # Try to parse last two parts as date and time
                    date_time = f"{parts[-2]}_{parts[-1]}"
                    return datetime.strptime(date_time, "%Y%m%d_%H%M%S")
            except (ValueError, IndexError):
                # If timestamp cannot be parsed, return file modification time as fallback
                return datetime.fromtimestamp(file_path.stat().st_mtime)
            return datetime.fromtimestamp(file_path.stat().st_mtime)
        
        # Add time information to files and sort
        files_with_time = [(f, extract_timestamp(f)) for f in il_files]
        files_with_time.sort(key=lambda x: x[1])  # Sort by timestamp
        
        result = f"Found the following il files in directory {directory} (sorted by timestamp):\n"
        for i, (file, timestamp) in enumerate(files_with_time, 1):
            # Format time display
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            result += f"{i}. {file.name:<30} [Timestamp: {time_str}]\n"
        
        return result
        
    except Exception as e:
        return f"❌ Error occurred while listing il files: {e}" 

@tool
def run_il_with_screenshot(il_file_path: str, screenshot_path: Optional[str] = None, lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout") -> str:
    """
    Run il file using skillbridge library and save screenshot
    
    Args:
        il_file_path: Path to il file (can be relative or absolute path)
        screenshot_path: Optional absolute/relative path to save the screenshot. If None, will save to output/screenshots/virtuoso_<stem>_<timestamp>.png
        lib: target library name (optional)
        cell: target cell name (optional)
        view: target view name (default: "layout")
        
    Returns:
        JSON format string containing execution status, screenshot path and observation information
    """
    result_dict = {
        "status": "error",
        "message": "",
        "screenshot_path": None,
        "observations": []
    }
    
    try:
        # If lib/cell provided, open specified cellView and set as current edit view first
        if lib and cell:
            ok = open_cell_view_by_type(lib, cell, view=view, view_type=None, mode="w", timeout=30)
            if not ok:
                result_dict["message"] = f"❌ Error: Failed to open cellView {lib}/{cell}/{view}"
                return json.dumps(result_dict, ensure_ascii=False)
            # Open window to display the cellView
            window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
            if not window_ok:
                result_dict["message"] = f"❌ Error: Failed to open window for {lib}/{cell}/{view}"
                return json.dumps(result_dict, ensure_ascii=False)
            ui_redraw(timeout=10)
            sleep(0.5)
        else:
            # If lib/cell not provided, try to get current cellView and set cv variable
            # This is needed because IL files often use 'cv' variable
            try:
                cv_result = rb_exec('geGetEditCellView()', timeout=10)
                if not cv_result or cv_result.strip().lower() in {'nil', 'none', ''}:
                    result_dict["message"] = f"❌ Error: No cellView is currently open. Please specify --lib and --cell options, or open a cellView in Virtuoso first."
                    return json.dumps(result_dict, ensure_ascii=False)
                # Set cv variable for IL file to use
                rb_exec('cv = geGetEditCellView()', timeout=10)
            except Exception as e:
                result_dict["message"] = f"❌ Error: Failed to get current cellView: {e}. Please specify --lib and --cell options."
                return json.dumps(result_dict, ensure_ascii=False)

        # Check if file exists
        skill_path = Path(il_file_path)
        
        # If file doesn't exist, try to find it in output directory
        if not skill_path.exists():
            output_path = Path("output") / skill_path.name
            if output_path.exists():
                skill_path = output_path
            else:
                result_dict["message"] = f"❌ Error: File {il_file_path} does not exist, also not found in output directory: {skill_path.name}"
                return json.dumps(result_dict, ensure_ascii=False)
        
        # Check file extension
        if skill_path.suffix.lower() not in ['.il', '.skill']:
            result_dict["message"] = f"❌ Error: File {skill_path} is not a valid il/skill file"
            return json.dumps(result_dict, ensure_ascii=False)
        
        # Use load command to execute SKILL file directly (avoids port forwarding truncation issues)
        abs_path = str(skill_path.resolve())
        escaped_path = abs_path.replace('\\', '\\\\').replace('"', '\\"')
        load_result = rb_exec(f'load("{escaped_path}")', timeout=60)
        
        # Check if load was successful (returns 't' or empty string on success)
        if load_result and load_result.strip().lower() in {'t', 't\n', ''}:
            result_dict["observations"].append(f"✅ SKILL script {skill_path.name} executed successfully")
        else:
            # Return detailed error information
            result_dict["message"] = f"❌ il file {skill_path.name} execution failed"
            if load_result:
                error_details = str(load_result).strip()
                # Clean up error message for better readability
                safe_error = error_details.replace('\n', ' ').replace('\r', ' ').strip()
                if safe_error and safe_error.lower() not in {'nil', 'none'}:
                    result_dict["observations"].append(f"Error Details: {safe_error}")
                else:
                    result_dict["observations"].append("Failed to load SKILL file (check Virtuoso connection and file path)")
            else:
                result_dict["observations"].append("Failed to load SKILL file (empty result - check Virtuoso connection and file path)")
            return json.dumps(result_dict, ensure_ascii=False)
        # Save current cellview after load to persist generated content
        try:
            if save_current_cellview(timeout=30):
                result_dict["observations"].append("💾 CellView saved successfully after load")
            else:
                result_dict["observations"].append("❌ Failed to save CellView after load")
        except Exception as se:
            result_dict["observations"].append(f"❌ Exception during save: {se}")
        ui_redraw(timeout=10)
        ui_zoom_absolute_scale(0.9, timeout=10)
        sleep(2.0)
        # Determine screenshot save path (external path takes precedence)
        if screenshot_path:
            # Expand user (~) and convert to an absolute path; ensure parent exists
            save_path_obj = Path(screenshot_path).expanduser().resolve(strict=False)
            save_path_obj.parent.mkdir(parents=True, exist_ok=True)
            save_path = str(save_path_obj)
        else:
            save_dir = Path("output/screenshots")
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"virtuoso_{skill_path.stem}_{timestamp}.png"
            save_path = str(save_dir.resolve() / filename)
        # Expand user (~) and convert to an absolute path so downstream bridge helpers get a full path
        screenshot_script = str(Path("src/skill/screenshot.il").expanduser().resolve(strict=False))
        if load_script_and_take_screenshot(screenshot_script, save_path, timeout=20):
            result_dict["status"] = "success"
            result_dict["message"] = f"✅ il file {skill_path.name} executed successfully"
            result_dict["screenshot_path"] = save_path
            result_dict["observations"].append(f"📸 Screenshot saved: {save_path}")
        else:
            result_dict["message"] = "❌ Screenshot failed"
            
    except Exception as e:
        result_dict["message"] = f"❌ Error occurred while running il file: {e}"
        result_dict["observations"].append(f"❌ Exception occurred: {str(e)}")
    
    return json.dumps(result_dict, ensure_ascii=False) 

@tool
def clear_all_figures_in_window() -> str:
    """
    Clear all components in the current window, calls scripts/delete_all.il script.
    
    Returns:
        String description of execution result
    """
    try:
        # Check if script file exists
        script_path = Path("scripts/delete_all.il")
        if not script_path.exists():
            return f"❌ Error: Script {script_path} does not exist"

        # Load script via unified bridge helper (ramic_bridge or skillbridge)
        if load_skill_file(str(script_path.resolve()), timeout=30):
            return "✅ All components in the current window have been cleared"
        return "❌ Failed to clear components"
    except Exception as e:
        return f"❌ Error occurred while executing clear operation: {e}" 

@tool
def screenshot_current_window(lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout") -> str:
    """
    Take screenshot of current Virtuoso window only, without running IL file.
    If lib and cell are provided, opens the specified cellview window before taking screenshot.
    
    Args:
        lib: Library name (optional)
        cell: Cell name (optional)
        view: View name (default: layout)
    
    Returns:
        JSON string containing screenshot path, status and timestamp.
    """
    result = {
        "status": "error",
        "message": "",
        "screenshot_path": None,
        "timestamp": None
    }
    try:
        # If lib/cell provided, open window to display the cellView
        if lib and cell:
            window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
            if not window_ok:
                result["message"] = f"❌ Error: Failed to open window for {lib}/{cell}/{view}"
                return json.dumps(result, ensure_ascii=False)
            ui_redraw(timeout=10)
            sleep(0.5)
        
        # Redraw and zoom using unified helpers
        ui_redraw(timeout=10)
        ui_zoom_absolute_scale(0.9, timeout=10)
        sleep(2.0)

        # Prepare save path
        save_dir = Path("output/screenshots")
        save_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"virtuoso_window_{timestamp}.png"
        save_path = str(save_dir.resolve() / filename)

        # Take screenshot via unified helper (works for both bridges)
        screenshot_script_path = Path("src/skill/screenshot.il")
        screenshot_script = os.path.abspath(screenshot_script_path)
        ok, err = load_script_and_take_screenshot_verbose(screenshot_script, save_path, timeout=20)
        if ok:
            result["status"] = "success"
            result["message"] = f"✅ Screenshot saved: {save_path}"
            result["screenshot_path"] = save_path
            result["timestamp"] = timestamp
        else:
            result["message"] = f"❌ Screenshot failed: {err}"
    except Exception as e:
        result["message"] = f"❌ Exception occurred: {e}"
    return json.dumps(result, ensure_ascii=False) 

@tool
def get_current_cellview_info(lib: Optional[str] = None, cell: Optional[str] = None, view: str = "layout") -> str:
    """
    Get information about the currently open cellview.
    If lib and cell are provided, opens the specified cellview window before getting info.
    
    Args:
        lib: Library name (optional)
        cell: Cell name (optional)
        view: View name (default: layout)
    
    Returns:
        String containing library, cell, and view information
    """
    try:
        # If lib/cell provided, open window to display the cellView
        if lib and cell:
            window_ok = ge_open_window(lib, cell, view=view, view_type=None, mode="a", timeout=30)
            if not window_ok:
                return f"❌ Error: Failed to open window for {lib}/{cell}/{view}"
            ui_redraw(timeout=10)
            sleep(0.5)
        
        # Use SKILL tools manager
        from .skill_tools_manager import run_skill_tool
        return run_skill_tool("get_cellview_info")
            
    except Exception as e:
        return f"❌ Error getting cellview info: {e}"
