#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check Tool - System health check

Quickly check if critical system components are available, without detailed testing.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from smolagents import tool

# Load environment variables from .env file
load_dotenv()


@tool
def run_health_check() -> str:
    """
    Quick system health check (NOT comprehensive testing).
    
    Checks:
    - Critical tools are registered
    - Environment variables are set
    - Key configuration files exist
    - Knowledge base is accessible
    
    Returns:
        Detailed health report with status of each component
    """
    issues = []
    warnings = []
    tool_details = []
    env_details = []
    file_details = []
    
    project_root = Path(__file__).parent.parent.parent
    
    # 1. Check if critical tools are registered
    from ..utils.tool_loader import TOOL_REGISTRY
    
    critical_tools = [
        "run_il_file",
        "scan_knowledge_base",
        "load_domain_knowledge",
        "list_skill_tools",
        "run_skill_tool",
        "run_health_check",
        "check_virtuoso_connection",
        "quick_diagnostic"
    ]
    
    for tool_name in critical_tools:
        if tool_name in TOOL_REGISTRY:
            module_path, func_name = TOOL_REGISTRY[tool_name]
            tool_details.append(f"  ✅ {tool_name:<35} [{module_path}.{func_name}]")
        else:
            issues.append(f"Tool '{tool_name}' not registered")
            tool_details.append(f"  ❌ {tool_name:<35} [NOT FOUND]")
    
    # 2. Check environment variables
    required_env = ["USE_RAMIC_BRIDGE"]
    optional_env = ["DEEPSEEK_API_KEY", "WANDOU_API_KEY", "RB_HOST", "RB_PORT"]
    
    for var in required_env:
        value = os.getenv(var)
        if value:
            env_details.append(f"  ✅ {var:<35} = {value}")
        else:
            issues.append(f"Environment variable '{var}' not set")
            env_details.append(f"  ❌ {var:<35} [NOT SET]")
    
    for var in optional_env:
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "KEY" in var or "TOKEN" in var:
                masked = value[:8] + "..." if len(value) > 8 else "***"
                env_details.append(f"  ✅ {var:<35} = {masked}")
            else:
                env_details.append(f"  ✅ {var:<35} = {value}")
        else:
            warnings.append(f"Optional env '{var}' not set")
            env_details.append(f"  ⚠️  {var:<35} [NOT SET - Optional]")
    
    # 3. Check critical configuration files
    critical_files = [
        "knowledge_base/system_prompt.md",
        "config/tools_config.yaml",
        ".env"
    ]
    
    for file in critical_files:
        file_path = project_root / file
        if file_path.exists():
            size = file_path.stat().st_size
            file_details.append(f"  ✅ {file:<35} ({size} bytes)")
        else:
            issues.append(f"File '{file}' missing")
            file_details.append(f"  ❌ {file:<35} [NOT FOUND]")
    
    # 4. Check knowledge base
    kb_dir = project_root / "knowledge_base"
    if not kb_dir.exists():
        issues.append("Knowledge base directory missing")
        file_details.append(f"  ❌ {'knowledge_base/':<35} [NOT FOUND]")
    else:
        kb_files = list(kb_dir.glob("*.md"))
        file_details.append(f"  ✅ {'knowledge_base/':<35} ({len(kb_files)} .md files)")
        if len(kb_files) < 2:
            warnings.append(f"Knowledge base has only {len(kb_files)} file(s)")
    
    # 5. Check SKILL tools directory
    skill_tools_dir = project_root / "skill_tools"
    if not skill_tools_dir.exists():
        warnings.append("SKILL tools directory missing")
        file_details.append(f"  ⚠️  {'skill_tools/':<35} [NOT FOUND - Optional]")
    else:
        skill_files = list(skill_tools_dir.glob("*.il"))
        file_details.append(f"  ✅ {'skill_tools/':<35} ({len(skill_files)} .il files)")
    
    # 6. Check output directory
    output_dir = project_root / "output"
    if not output_dir.exists():
        warnings.append("Output directory missing (will be created on first use)")
        file_details.append(f"  ⚠️  {'output/':<35} [Will be created on first use]")
    else:
        # Check subdirectories
        logs_dir = output_dir / "logs"
        generated_dir = output_dir / "generated"
        screenshots_dir = output_dir / "screenshots"
        
        subdirs_status = []
        if logs_dir.exists():
            subdirs_status.append("logs")
        if generated_dir.exists():
            subdirs_status.append("generated")
        if screenshots_dir.exists():
            subdirs_status.append("screenshots")
        
        status_str = f"({', '.join(subdirs_status)})" if subdirs_status else "[empty]"
        file_details.append(f"  ✅ {'output/':<35} {status_str}")
    
    # Generate report
    report = []
    
    if not issues and not warnings:
        report.append("[run_health_check] ✅ System Health: EXCELLENT")
    elif issues:
        report.append("[run_health_check] ❌ System Health: ISSUES FOUND")
    else:
        report.append("[run_health_check] ✅ System Health: OK (with warnings)")
    
    report.append("\n1. Critical Tools:")
    report.extend(tool_details)
    
    report.append("\n2. Environment Variables:")
    report.extend(env_details)
    
    report.append("\n3. Files & Directories:")
    report.extend(file_details)
    
    if issues:
        report.append(f"\n❌ Critical Issues ({len(issues)}):")
        for issue in issues:
            report.append(f"  • {issue}")
    
    if warnings:
        report.append(f"\n⚠️  Warnings ({len(warnings)}):")
        for warning in warnings:
            report.append(f"  • {warning}")
    
    return "\n".join(report)


@tool
def check_virtuoso_connection() -> str:
    """
    Check if Virtuoso connection is available.
    
    Tests if the bridge (RAMIC Bridge or skillbridge) can connect to Virtuoso
    and execute simple SKILL commands.
    
    Returns:
        Connection status report with detailed test results
    """
    report = []
    
    # Check which Bridge is used
    use_ramic = os.getenv("USE_RAMIC_BRIDGE", "false").lower() in ["true", "1", "yes"]
    
    if use_ramic:
        report.append("Bridge Type: RAMIC Bridge")
        
        # Check RAMIC Bridge connection
        try:
            from ..tools.bridge_utils import rb_exec
            
            # Simple test: execute a harmless SKILL command
            test_command = "(1+1)"
            result = rb_exec(test_command, timeout=5)
            
            report.append(f"Test Command: {test_command}; Test Result: {result}\n")
            
            if result == "2":
                report.append("✅ Virtuoso Connection: OK")
            else:
                report.append("⚠️  Virtuoso Connection: UNCERTAIN")
                report.append(f"• Bridge responded: {result}")
                report.append("• Expected: 2")
                report.append("Connection may be working but response format unexpected")
                
        except Exception as e:
            report.append(f"Error: {str(e)}\n")
            report.append("❌ Virtuoso Connection: FAILED")
            report.append("Check if RAMIC Bridge daemon is running")
            report.append("Check RB_HOST and RB_PORT in .env")
    
    else:
        report.append("Bridge Type: skillbridge")
        
        # Check skillbridge connection
        try:
            import skillbridge
            
            report.append("Attempting to connect to Virtuoso...\n")
            
            # Try to connect
            ws = skillbridge.Workspace.open()
            
            # Simple test
            test_command = "(1+1)"            
            result = ws.eval(test_command)
            
            report.append(f"Test Command: {test_command}, Test Result: {result}")
            
            if result == 2: 
                report.append("✅ Virtuoso Connection: OK")
            else:
                report.append("⚠️  Virtuoso Connection: UNCERTAIN")
                report.append(f"• Connected, result: {result}")
                report.append(f"• Expected: 2")
                
        except Exception as e:
            report.append(f"Error: {str(e)}\n")
            report.append("[check_virtuoso_connection] ❌ Virtuoso Connection: FAILED")
            report.append(f"[check_virtuoso_connection]  • Check if Virtuoso is running")
            report.append(f"[check_virtuoso_connection]  • Check if python server is loaded in CIW")
            report.append(f"[check_virtuoso_connection]  • Run in CIW: load(\"<skillbridge_path>/skill/python_server.il\")")
    
    return "\n".join(report)


@tool
def quick_diagnostic() -> str:
    """
    Perform a quick combined diagnostic of system health and Virtuoso connection.
    
    Returns:
        A comprehensive diagnostic report
    """
    report = []
    report.append("=" * 60)
    report.append("[quick_diagnostic] Quick Diagnostic Report")
    report.append("=" * 60 )
    
    report.append("\n[quick_diagnostic] PART 1: System Health Check\n")
    report.append(run_health_check())
    
    report.append("\n[quick_diagnostic] PART 2: Virtuoso Connection Check\n")
    report.append(check_virtuoso_connection())
    
    return "\n".join(report)