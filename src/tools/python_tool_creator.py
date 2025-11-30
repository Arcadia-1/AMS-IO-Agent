#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python Tool Creator - Create reusable tools from code snippets

Allows Agent to encapsulate frequently used code snippets into tools, avoiding repetitive code writing.
"""

import os
import re
import json
from pathlib import Path
from typing import Optional
from smolagents import tool
from datetime import datetime

# Python tools storage directory
PYTHON_TOOLS_DIR = Path("src/tools/python_helpers")

# Tool registry (in-memory)
_custom_tools_registry = {}

def _ensure_tools_dir():
    """Ensure tools directory exists"""
    PYTHON_TOOLS_DIR.mkdir(parents=True, exist_ok=True)


@tool
def create_python_helper(
    tool_name: str,
    description: str,
    function_body: str,
    parameters: str = "{}",
    return_type: str = "str"
) -> str:
    """
    Create a reusable Python helper tool from code snippet.
    
    This allows you to convert frequently used code patterns into reusable tools,
    so you don't have to write the same code repeatedly.
    
    Args:
        tool_name: Name of the helper tool (e.g., "read_il_file_content")
        description: What this tool does (e.g., "Read IL file and return content as string")
        function_body: Python code for the function body (without def line)
        parameters: JSON string defining parameters, e.g., '{"file_path": "str"}'
        return_type: Return type annotation (default: "str")
        
    Returns:
        Success message with usage example
        
    Example:
        create_python_helper(
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
    """
    try:
        _ensure_tools_dir()
        
        # Parse parameters
        params_dict = json.loads(parameters)
        
        # Build parameter list
        param_list = []
        for param_name, param_type in params_dict.items():
            param_list.append(f"{param_name}: {param_type}")
        params_str = ", ".join(param_list)
        
        # Build complete tool code
        tool_code = f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-generated Python helper tool
Created: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from smolagents import tool

@tool
def {tool_name}({params_str}) -> {return_type}:
    """
    {description}
    
    Args:
{_generate_param_docs(params_dict)}
        
    Returns:
        {return_type}: Result of the operation
    """
{_indent_code(function_body, 4)}
'''
        
        # Save to file
        tool_file = PYTHON_TOOLS_DIR / f"{tool_name}.py"
        with open(tool_file, 'w', encoding='utf-8') as f:
            f.write(tool_code)
        
        # Dynamically load tool
        success = _load_tool_from_file(tool_file, tool_name)
        
        if success:
            usage_example = f"{tool_name}({', '.join(f'{k}=...' for k in params_dict.keys())})"
            return f"""✅ Python helper tool '{tool_name}' created successfully!

📁 File: {tool_file}
📝 Description: {description}

💡 Usage (Use as Agent Tool - Recommended):
   result = {usage_example}
   
   ✅ The tool is registered and available immediately!
   ✅ Just call it directly - no import needed!
   ✅ Use as Agent tool, not in code execution blocks with import!

⚠️  IMPORTANT: 
   - DO NOT import in code execution: from src.tools.python_helpers.{tool_name} import ...
   - USE directly as Agent tool: {usage_example}
   - Python helpers are Agent tools, not regular Python imports!

🔄 The tool is registered and available immediately!
"""
        else:
            return f"⚠️ Tool file created at {tool_file}, but failed to load dynamically. Restart may be required."
            
    except json.JSONDecodeError as e:
        return f"❌ Invalid parameters JSON: {e}"
    except Exception as e:
        return f"❌ Failed to create tool: {e}"


@tool
def list_python_helpers() -> str:
    """
    List all custom Python helper tools.
    
    Returns:
        List of available Python helper tools with descriptions
    """
    try:
        _ensure_tools_dir()
        
        tool_files = sorted(PYTHON_TOOLS_DIR.glob("*.py"))
        
        if not tool_files:
            return "📦 No Python helper tools found.\n\n💡 Use create_python_helper() to create your first tool!"
        
        result = f"📦 Available Python Helper Tools ({len(tool_files)}):\n\n"
        
        for i, tool_file in enumerate(tool_files, 1):
            # Read file to get description
            try:
                with open(tool_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Extract function docstring
                    match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                    if match:
                        desc_lines = match.group(1).strip().split('\n')
                        desc = desc_lines[0] if desc_lines else "No description"
                    else:
                        desc = "No description"
            except:
                desc = "No description"
            
            result += f"{i}. {tool_file.stem}\n"
            result += f"   └─ {desc}\n"
        
        result += f"\n💡 Use the tool name directly to call it"
        return result
        
    except Exception as e:
        return f"❌ Error listing tools: {e}"


@tool
def update_python_helper(tool_name: str, function_body: str) -> str:
    """
    Update an existing Python helper tool's function body.
    
    Args:
        tool_name: Name of the tool to update
        function_body: New function body code
        
    Returns:
        Success message
    """
    try:
        tool_file = PYTHON_TOOLS_DIR / f"{tool_name}.py"
        
        if not tool_file.exists():
            return f"❌ Tool '{tool_name}' not found. Use create_python_helper() to create it first."
        
        # Read existing file
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find function body and replace
        # Match content from def line to end of file
        pattern = r'(def\s+\w+\([^)]*\)\s*->\s*\w+:\s*""".*?""")(.*)'
        match = re.search(pattern, content, re.DOTALL)
        
        if not match:
            return f"❌ Failed to parse tool file structure"
        
        # Replace function body
        new_content = content[:match.end(1)] + '\n' + _indent_code(function_body, 4)
        
        # Save
        with open(tool_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        # Reload
        _load_tool_from_file(tool_file, tool_name)
        
        return f"✅ Tool '{tool_name}' updated successfully!\n💡 Changes take effect immediately."
        
    except Exception as e:
        return f"❌ Failed to update tool: {e}"


@tool
def delete_python_helper(tool_name: str) -> str:
    """
    Delete a Python helper tool.
    
    Args:
        tool_name: Name of the tool to delete
        
    Returns:
        Success message
    """
    try:
        tool_file = PYTHON_TOOLS_DIR / f"{tool_name}.py"
        
        if not tool_file.exists():
            return f"❌ Tool '{tool_name}' not found"
        
        # Delete file
        tool_file.unlink()
        
        # Remove from registry
        if tool_name in _custom_tools_registry:
            del _custom_tools_registry[tool_name]
        
        return f"✅ Tool '{tool_name}' deleted successfully"
        
    except Exception as e:
        return f"❌ Failed to delete tool: {e}"


@tool
def view_python_helper_code(tool_name: str) -> str:
    """
    View the source code of a Python helper tool.
    
    Args:
        tool_name: Name of the tool to view
        
    Returns:
        Source code of the tool
    """
    try:
        tool_file = PYTHON_TOOLS_DIR / f"{tool_name}.py"
        
        if not tool_file.exists():
            return f"❌ Tool '{tool_name}' not found"
        
        with open(tool_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return f"📄 Source code of '{tool_name}':\n\n```python\n{content}\n```"
        
    except Exception as e:
        return f"❌ Failed to read tool: {e}"


# ============================================================================
# Helper Functions
# ============================================================================

def _generate_param_docs(params_dict: dict) -> str:
    """Generate parameter documentation"""
    docs = []
    for param_name, param_type in params_dict.items():
        docs.append(f"        {param_name} ({param_type}): Description of {param_name}")
    return '\n'.join(docs)


def _indent_code(code: str, spaces: int) -> str:
    """Add indentation to code"""
    indent = ' ' * spaces
    lines = code.strip().split('\n')
    return '\n'.join(indent + line if line.strip() else '' for line in lines)


def _load_tool_from_file(tool_file: Path, tool_name: str) -> bool:
    """
    Dynamically load tool to Agent (using importlib instead of exec)
    
    Args:
        tool_file: Tool file path
        tool_name: Tool name
        
    Returns:
        Whether loading succeeded
    """
    try:
        import sys
        import importlib.util
        
        # Construct module name
        module_name = f"src.tools.python_helpers.{tool_name}"
        
        # Dynamically import module
        spec = importlib.util.spec_from_file_location(module_name, tool_file)
        if spec is None or spec.loader is None:
            return False
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Get tool function
        if not hasattr(module, tool_name):
            return False
        
        tool_func = getattr(module, tool_name)
        _custom_tools_registry[tool_name] = tool_func
        
        # Try to register to Agent (if Agent is initialized)
        try:
            from .tool_manager import _agent_instance
            
            if _agent_instance is not None:
                # 1. Register to Agent's tools dictionary
                _agent_instance.tools[tool_name] = tool_func
                
                # 2. Try to add to code executor's additional_functions so it's available in code execution blocks
                try:
                    # Check if python_executor attribute exists (CodeAgent uses python_executor)
                    if hasattr(_agent_instance, 'python_executor') and _agent_instance.python_executor is not None:
                        executor = _agent_instance.python_executor
                        # Access additional_functions dictionary and add tool
                        if hasattr(executor, 'additional_functions') and executor.additional_functions is not None:
                            # Ensure additional_functions is a dict, not None
                            if isinstance(executor.additional_functions, dict):
                                executor.additional_functions[tool_name] = tool_func
                                # Important: need to update static_tools, because function checking uses static_tools
                                # static_tools is updated in send_tools, but we need to update manually
                                if hasattr(executor, 'static_tools') and executor.static_tools is not None:
                                    if isinstance(executor.static_tools, dict):
                                        executor.static_tools[tool_name] = tool_func
                                print(f"✅ Dynamically loaded tool '{tool_name}' into Agent (both tools and code executor)")
                            else:
                                print(f"✅ Dynamically loaded tool '{tool_name}' into Agent (tools only, additional_functions is not a dict: {type(executor.additional_functions)})")
                        else:
                            print(f"✅ Dynamically loaded tool '{tool_name}' into Agent (tools only, additional_functions not found or None)")
                    else:
                        print(f"✅ Dynamically loaded tool '{tool_name}' into Agent (tools only, python_executor not found)")
                except Exception as e:
                    # If cannot add to code executor, at least ensure tool is registered
                    print(f"✅ Dynamically loaded tool '{tool_name}' into Agent (tools only, failed to add to executor: {e})")
                
                return True
            else:
                # Agent not initialized, but tool is saved, will auto-load after restart
                return True
        except ImportError:
            # tool_manager doesn't exist, but tool is saved
            return True
        
    except Exception as e:
        print(f"Warning: Failed to load tool dynamically: {e}")
        import traceback
        traceback.print_exc()
        return False


def load_all_python_helpers():
    """
    Load all Python helper tools at startup
    Should be called in agent_factory.py
    """
    try:
        _ensure_tools_dir()
        
        tool_files = PYTHON_TOOLS_DIR.glob("*.py")
        loaded_count = 0
        
        for tool_file in tool_files:
            tool_name = tool_file.stem
            if _load_tool_from_file(tool_file, tool_name):
                loaded_count += 1
        
        if loaded_count > 0:
            print(f"✅ Loaded {loaded_count} Python helper tool(s)")
        
    except Exception as e:
        print(f"Warning: Failed to load Python helpers: {e}")

