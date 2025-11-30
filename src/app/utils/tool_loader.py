"""
Dynamic Tool Loader - Load tools from configuration instead of hardcoding
"""

import yaml
from pathlib import Path
from typing import List, Dict, Any
import importlib

# Tool registry mapping: tool_name -> (module_path, function_name)
TOOL_REGISTRY = {
    # Tool management (meta-tools)
    "list_registered_tools": ("src.tools.tool_manager", "list_registered_tools"),
    "get_tool_info": ("src.tools.tool_manager", "get_tool_info"),
    "check_tool_availability": ("src.tools.tool_manager", "check_tool_availability"),
    "export_tools_snapshot": ("src.tools.tool_manager", "export_tools_snapshot"),
    "get_tools_summary": ("src.tools.tool_manager", "get_tools_summary"),
    
    # Knowledge loading (dynamic prompt loading)
    "scan_knowledge_base": ("src.tools.knowledge_loader_tool", "scan_knowledge_base"),
    "search_knowledge": ("src.tools.knowledge_loader_tool", "search_knowledge"),
    "load_domain_knowledge": ("src.tools.knowledge_loader_tool", "load_domain_knowledge"),
    "refresh_knowledge_index": ("src.tools.knowledge_loader_tool", "refresh_knowledge_index"),
    "add_knowledge_directory": ("src.tools.knowledge_loader_tool", "add_knowledge_directory"),
    "export_knowledge_index": ("src.tools.knowledge_loader_tool", "export_knowledge_index"),
    
    # Virtuoso execution
    "run_il_file": ("src.tools.il_runner_tool", "run_il_file"),
    "list_il_files": ("src.tools.il_runner_tool", "list_il_files"),
    "run_il_with_screenshot": ("src.tools.il_runner_tool", "run_il_with_screenshot"),
    "clear_all_figures_in_window": ("src.tools.il_runner_tool", "clear_all_figures_in_window"),
    "screenshot_current_window": ("src.tools.il_runner_tool", "screenshot_current_window"),
    
    # SKILL tools management (small utility scripts)
    "list_skill_tools": ("src.tools.skill_tools_manager", "list_skill_tools"),
    "run_skill_tool": ("src.tools.skill_tools_manager", "run_skill_tool"),
    "create_skill_tool": ("src.tools.skill_tools_manager", "create_skill_tool"),
    "update_skill_tool": ("src.tools.skill_tools_manager", "update_skill_tool"),
    "delete_skill_tool": ("src.tools.skill_tools_manager", "delete_skill_tool"),
    
    # Python helper tools (reusable code snippets)
    "create_python_helper": ("src.tools.python_tool_creator", "create_python_helper"),
    "list_python_helpers": ("src.tools.python_tool_creator", "list_python_helpers"),
    "update_python_helper": ("src.tools.python_tool_creator", "update_python_helper"),
    "delete_python_helper": ("src.tools.python_tool_creator", "delete_python_helper"),
    "view_python_helper_code": ("src.tools.python_tool_creator", "view_python_helper_code"),
    
    # Verification
    "run_drc": ("src.tools.drc_runner_tool", "run_drc"),
    "run_lvs": ("src.tools.lvs_runner_tool", "run_lvs"),
    "run_pex": ("src.tools.pex_runner_tool", "run_pex"),
    
    # IO Ring
    "generate_io_ring_schematic": ("src.tools.io_ring_generator_tool", "generate_io_ring_schematic"),
    "validate_intent_graph": ("src.tools.io_ring_generator_tool", "validate_intent_graph"),
    "generate_io_ring_layout": ("src.tools.io_ring_generator_tool", "generate_io_ring_layout"),
    
    # User profile management (write-only, profile is pre-loaded in system prompt)
    "update_user_profile": ("src.tools.user_profile_tool", "update_user_profile"),
    
    # Tool usage statistics
    "get_tool_statistics": ("src.tools.tool_stats_tool", "get_tool_statistics"),
    "get_top_used_tools": ("src.tools.tool_stats_tool", "get_top_used_tools"),
    "get_problematic_tools": ("src.tools.tool_stats_tool", "get_problematic_tools"),
    "generate_tool_usage_report": ("src.tools.tool_stats_tool", "generate_tool_usage_report"),
    "reset_tool_statistics": ("src.tools.tool_stats_tool", "reset_tool_statistics"),
    
    # Task history and analysis
    "view_recent_tasks": ("src.tools.task_query_tool", "view_recent_tasks"),
    "analyze_task_failures": ("src.tools.task_query_tool", "analyze_task_failures"),
    "get_task_summary": ("src.tools.task_query_tool", "get_task_summary"),
    "compare_with_tool_stats": ("src.tools.task_query_tool", "compare_with_tool_stats"),
    
    # System health check
    "run_health_check": ("src.tools.health_check_tool", "run_health_check"),
    "check_virtuoso_connection": ("src.tools.health_check_tool", "check_virtuoso_connection"),
    "quick_diagnostic": ("src.tools.health_check_tool", "quick_diagnostic"),
}


def load_tool_config(config_path: str = "config/tools_config.yaml") -> Dict[str, Any]:
    """
    Load tool configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing tool configuration
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        print(f"⚠️  Tool config not found at {config_path}, using defaults")
        return get_default_config()
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def get_default_config() -> Dict[str, Any]:
    """
    Get default tool configuration when config file is not available.
    This should match the structure in tools_config.yaml.
    
    Returns:
        Default configuration dictionary
    """
    # Core tools: tool management + knowledge base + health check
    core_tools = [
        # Tool management (meta-tools)
        "list_registered_tools",
        "get_tool_info",
        "check_tool_availability",
        "export_tools_snapshot",
        "get_tools_summary",
        # Knowledge loading
        "scan_knowledge_base",
        "search_knowledge",
        "load_domain_knowledge",
        "refresh_knowledge_index",
        "add_knowledge_directory",
        "export_knowledge_index",
        # System health check
        "run_health_check",
        "check_virtuoso_connection",
        "quick_diagnostic",
    ]
    
    # Tool groups: organized by functionality
    tool_groups = {
        "virtuoso": {
            "enabled": True,
            "tools": [
                "run_il_file",
                "list_il_files",
                "run_il_with_screenshot",
                "clear_all_figures_in_window",
                "screenshot_current_window",
            ]
        },
        "skill_tools": {
            "enabled": True,
            "tools": [
                "list_skill_tools",
                "run_skill_tool",
                "create_skill_tool",
                "update_skill_tool",
                "delete_skill_tool",
            ]
        },
        "python_helpers": {
            "enabled": True,
            "tools": [
                "create_python_helper",
                "list_python_helpers",
                "update_python_helper",
                "delete_python_helper",
                "view_python_helper_code",
            ]
        },
        "verification": {
            "enabled": True,
            "tools": [
                "run_drc",
                "run_lvs",
                "run_pex",
            ]
        },
        "io_ring": {
            "enabled": True,
            "tools": [
                "generate_io_ring_schematic",
                "validate_intent_graph",
                "generate_io_ring_layout",
            ]
        },
        "user_profile": {
            "enabled": True,
            "tools": [
                "update_user_profile",
            ]
        },
    }
    
    return {
        "core_tools": core_tools,
        "tool_groups": tool_groups,
        "loading_strategy": {
            "mode": "eager",
            "auto_discover": False
        }
    }


def load_tool_from_registry(tool_name: str):
    """
    Dynamically import and return a tool by its name.
    
    Args:
        tool_name: Name of the tool to load
        
    Returns:
        Tool function/object
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Tool '{tool_name}' not found in registry")
    
    module_path, func_name = TOOL_REGISTRY[tool_name]
    
    try:
        module = importlib.import_module(module_path)
        tool = getattr(module, func_name)
        return tool
    except Exception as e:
        raise ImportError(f"Failed to load tool '{tool_name}': {e}")


def load_tools_from_config(config_path: str = "config/tools_config.yaml") -> List:
    """
    Load tools based on configuration file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        List of tool objects ready to be passed to Agent
    """
    config = load_tool_config(config_path)
    tools = []
    
    # Load core tools (always loaded)
    core_tool_names = config.get("core_tools", [])
    print(f"📦 Loading {len(core_tool_names)} core tools...")
    for tool_name in core_tool_names:
        try:
            tool = load_tool_from_registry(tool_name)
            tools.append(tool)
            print(f"  ✅ {tool_name}")
        except Exception as e:
            print(f"  ❌ Failed to load {tool_name}: {e}")
    
    # Load tool groups (conditional)
    tool_groups = config.get("tool_groups", {})
    for group_name, group_config in tool_groups.items():
        if not group_config.get("enabled", True):
            print(f"⏭️  Skipping disabled group: {group_name}")
            continue
        
        group_tools = group_config.get("tools", [])
        print(f"📦 Loading {len(group_tools)} tools from group '{group_name}'...")
        for tool_name in group_tools:
            try:
                tool = load_tool_from_registry(tool_name)
                tools.append(tool)
                print(f"  ✅ {tool_name}")
            except Exception as e:
                print(f"  ❌ Failed to load {tool_name}: {e}")
    
    print(f"\n✨ Total tools loaded: {len(tools)}")
    return tools


def get_tools_for_agent(config_path: str = "config/tools_config.yaml") -> List:
    """
    Main entry point for getting tools to pass to Agent.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        List of tool objects
    """
    try:
        return load_tools_from_config(config_path)
    except Exception as e:
        print(f"⚠️  Error loading tools from config: {e}")
        print("📦 Falling back to default tool set...")
        return load_tools_from_config()  # Use default config


# For backward compatibility - export individual tools
def get_all_tools_dict() -> Dict[str, Any]:
    """
    Get all available tools as a dictionary.
    
    Returns:
        Dictionary of {tool_name: tool_object}
    """
    tools_dict = {}
    for tool_name in TOOL_REGISTRY.keys():
        try:
            tools_dict[tool_name] = load_tool_from_registry(tool_name)
        except Exception:
            pass
    return tools_dict

