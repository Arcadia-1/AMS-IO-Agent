#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SKILL Tools Manager
Dynamic management of SKILL tool scripts
"""

import os
from pathlib import Path
from typing import List, Dict, Optional
from smolagents import tool
from .bridge_utils import rb_exec

# SKILL tools directory - use absolute path based on project root
_project_root = Path(__file__).parent.parent.parent
SKILL_TOOLS_DIR = _project_root / "src" / "skill"

@tool
def list_skill_tools() -> str:
    """
    List all available SKILL tools in skill_tools/ directory.
    These are small, reusable SKILL utility scripts that can be called directly.
    
    Available tools include:
    - get_cellview_info: Get current cellview library/cell/view information
    - screenshot: Take a screenshot of current window
    - delete_all: Delete all shapes in current cellview
    - And more...
    
    Returns:
        String containing list of available tools with descriptions
    """
    try:
        if not SKILL_TOOLS_DIR.exists():
            return "❌ SKILL tools directory does not exist"
        
        tools = sorted(SKILL_TOOLS_DIR.glob("*.il"))
        if not tools:
            return "No SKILL tools found"
        
        result = "📦 Available SKILL tools:\n\n"
        for i, tool_path in enumerate(tools, 1):
            # Read first comment line as description
            try:
                with open(tool_path, 'r') as f:
                    first_line = f.readline().strip()
                    desc = first_line[2:].strip() if first_line.startswith(';;') else "No description"
            except:
                desc = "No description"
            
            result += f"{i}. {tool_path.stem}: {desc}\n"
        
        result += f"\n💡 Use run_skill_tool(tool_name) to execute a tool"
        return result
        
    except Exception as e:
        return f"❌ Error listing tools: {e}"

@tool
def run_skill_tool(tool_name: str) -> str:
    """
    Run a specific SKILL tool by name and capture its return value.
    
    Common tools:
    - get_cellview_info: Returns current library/cell/view as "lib/cell/view"
    - screenshot: Takes screenshot and returns confirmation
    - delete_all: Deletes all shapes in current cellview
    
    Args:
        tool_name: Name of the tool (without .il extension)
        
    Returns:
        String containing execution result and return value from SKILL script
    """
    try:
        tool_path = SKILL_TOOLS_DIR / f"{tool_name}.il"
        
        if not tool_path.exists():
            return f"❌ Tool '{tool_name}' not found. Use list_skill_tools() to see available tools."
        
        # Read and execute the tool with progn wrapper to capture return value
        with open(tool_path, 'r') as f:
            skill_content = f.read()
        
        # Wrap with progn to ensure proper evaluation
        wrapped_skill = f"(progn\n{skill_content}\n)"
        
        # Execute and capture output
        result = rb_exec(wrapped_skill, timeout=30)
        
        if result is not None:
            return f"✅ Tool '{tool_name}' executed successfully\nOutput: {result}"
        else:
            return f"❌ Tool '{tool_name}' execution failed"
            
    except Exception as e:
        return f"❌ Error running tool '{tool_name}': {e}"

@tool
def create_skill_tool(tool_name: str, skill_code: str) -> str:
    """
    Create a new SKILL tool script and make it immediately available.
    
    The tool will be automatically available for use via run_skill_tool() without restarting.
    
    Args:
        tool_name: Name of the tool (without .il extension)
        skill_code: SKILL code content (should start with ;; description comment)
        
    Returns:
        String description of creation result
        
    Example:
        create_skill_tool("my_tool", ";; My custom tool\\nprintf(\\\"Hello\\\")\\n\\\"Done\\\"")
    """
    try:
        # Ensure directory exists
        SKILL_TOOLS_DIR.mkdir(exist_ok=True)
        
        tool_path = SKILL_TOOLS_DIR / f"{tool_name}.il"
        
        # Check if tool already exists
        if tool_path.exists():
            return f"❌ Tool '{tool_name}' already exists. Use update_skill_tool() to modify it."
        
        # Write the tool
        with open(tool_path, 'w') as f:
            f.write(skill_code)
        
        return f"✅ Tool '{tool_name}' created successfully!\n💡 Use run_skill_tool('{tool_name}') to execute it immediately."
        
    except Exception as e:
        return f"❌ Error creating tool: {e}"

@tool
def update_skill_tool(tool_name: str, skill_code: str) -> str:
    """
    Update an existing SKILL tool script. Changes take effect immediately.
    
    Args:
        tool_name: Name of the tool (without .il extension)
        skill_code: New SKILL code content
        
    Returns:
        String description of update result
    """
    try:
        tool_path = SKILL_TOOLS_DIR / f"{tool_name}.il"
        
        if not tool_path.exists():
            return f"❌ Tool '{tool_name}' not found. Use create_skill_tool() to create it."
        
        # Update the tool
        with open(tool_path, 'w') as f:
            f.write(skill_code)
        
        return f"✅ Tool '{tool_name}' updated successfully!\n💡 The updated version will be used on next run_skill_tool('{tool_name}') call."
        
    except Exception as e:
        return f"❌ Error updating tool: {e}"

@tool
def delete_skill_tool(tool_name: str) -> str:
    """
    Delete a SKILL tool script.
    
    Args:
        tool_name: Name of the tool (without .il extension)
        
    Returns:
        String description of deletion result
    """
    try:
        tool_path = SKILL_TOOLS_DIR / f"{tool_name}.il"
        
        if not tool_path.exists():
            return f"❌ Tool '{tool_name}' not found"
        
        # Delete the tool
        tool_path.unlink()
        
        return f"✅ Tool '{tool_name}' deleted successfully"
        
    except Exception as e:
        return f"❌ Error deleting tool: {e}"
