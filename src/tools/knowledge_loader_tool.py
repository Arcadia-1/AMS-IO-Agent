#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dynamic Knowledge Loader Tool
Allows AI to discover and load specialized knowledge on-demand

Notes for usage:
- Always load the KB index of a knowledge base before loading its modules.
- KB index files (KB_INDEX.md) describe required module combinations and should be treated as the entry point.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from smolagents import tool

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Knowledge base auto-discovery directories
# Comprehensive reorganized structure (2025-11-22)
KNOWLEDGE_DIRECTORIES = {
    # Meta knowledge
    "00_META": "Knowledge_Base/00_META",

    # Core foundational knowledge
    "KB_Agent": "Knowledge_Base/01_CORE/KB_Agent",
    "KB_Virtuoso": "Knowledge_Base/01_CORE/KB_Virtuoso",
    "KB_SKILL": "Knowledge_Base/01_CORE/KB_SKILL",

    # Technology nodes
    "Tech_28nm": "Knowledge_Base/02_TECHNOLOGY/28nm",
    "Tech_180nm": "Knowledge_Base/02_TECHNOLOGY/180nm",
    "Tech_Config": "Knowledge_Base/02_TECHNOLOGY",

    # Design blocks
    "CDAC": "Knowledge_Base/03_DESIGN_BLOCKS/CDAC",
    "CDAC_Core": "Knowledge_Base/03_DESIGN_BLOCKS/CDAC/Core",
    "CDAC_Shapes": "Knowledge_Base/03_DESIGN_BLOCKS/CDAC/Shapes",
    "IO_Ring": "Knowledge_Base/03_DESIGN_BLOCKS/IO_Ring",
    "IO_Ring_Core": "Knowledge_Base/03_DESIGN_BLOCKS/IO_Ring/Core",

    # Verification knowledge
    "DRC": "Knowledge_Base/04_VERIFICATION/DRC",
    "LVS": "Knowledge_Base/04_VERIFICATION/LVS",
    "PEX": "Knowledge_Base/04_VERIFICATION/PEX",

    # Examples
    "Examples_CDAC": "Knowledge_Base/05_EXAMPLES/cdac_examples",
    "Examples_IO_Ring": "Knowledge_Base/05_EXAMPLES/io_ring_examples",

    # Error knowledge base
    "Errors": "Knowledge_Base/06_ERRORS",
    "Errors_CDAC": "Knowledge_Base/06_ERRORS/cdac_errors",
    "Errors_IO_Ring": "Knowledge_Base/06_ERRORS/io_ring_errors",
    "Errors_Verification": "Knowledge_Base/06_ERRORS/verification_errors",
}

# Files/directories to skip during knowledge discovery
# Files matching these patterns are considered human-readable documentation, not AI knowledge
SKIP_PATTERNS = {
    "exact_names": {"README.md"},  # Exact filename matches
    "name_prefixes": {".README"},  # Filenames starting with these
    "stem_names": set(),  # Filenames without extension (can be configured per installation)
}

def should_skip_file(file_path: Path) -> bool:
    """Determine if a file should be skipped during knowledge discovery.
    
    Args:
        file_path: Path to the file to check
        
    Returns:
        True if the file should be skipped, False otherwise
    """
    name = file_path.name
    stem = file_path.stem
    
    # Check exact name matches
    if name in SKIP_PATTERNS["exact_names"]:
        return True
    
    # Check name prefixes
    for prefix in SKIP_PATTERNS["name_prefixes"]:
        if name.startswith(prefix):
            return True
    
    # Check stem names
    if stem in SKIP_PATTERNS["stem_names"]:
        return True
    
    return False

def auto_discover_knowledge():
    """Automatically discover all markdown files in knowledge directories (including subdirectories)
    
    Avoids duplicate scanning: if a file is in a subdirectory that's also listed as a separate category,
    it will only be scanned once (using the more specific category).
    """
    knowledge_index = {}
    scanned_files = set()  # Track files that have already been scanned to avoid duplicates
    
    # Sort categories by path depth (deeper paths first) to prioritize more specific categories
    sorted_categories = sorted(KNOWLEDGE_DIRECTORIES.items(), 
                              key=lambda x: len(Path(x[1]).parts), 
                              reverse=True)
    
    for category, directory in sorted_categories:
        dir_path = PROJECT_ROOT / directory
        if not dir_path.exists():
            continue
        
        # Find all .md files recursively in subdirectories
        for md_file in dir_path.rglob("*.md"):
            # Skip documentation files (for humans, not AI)
            if should_skip_file(md_file):
                continue
            
            # Skip if this file has already been scanned by a more specific category
            file_path_str = str(md_file.relative_to(PROJECT_ROOT))
            if file_path_str in scanned_files:
                continue
            
            # Mark this file as scanned
            scanned_files.add(file_path_str)
            
            # Calculate relative path from the category directory
            rel_path = md_file.relative_to(dir_path)
            
            # Generate a key: category prefix + relative path (with / replaced by _)
            # This prevents conflicts when same filename exists in different knowledge bases or subdirectories
            key_parts = [category]  # Start with category prefix to namespace by knowledge base
            key_parts.extend(rel_path.parts[:-1])  # All parent directories
            key_parts.append(rel_path.stem)       # Filename without extension
            key = "_".join(key_parts)
            
            # Example: KB_Capacitor/00_Core_Principles.md -> Capacitor_KB_00_Core_Principles
            # Example: KB_Capacitor/03_Shape_Specifics/H_Shape/03_01_H_Shape_Structure.md -> Capacitor_KB_03_Shape_Specifics_H_Shape_03_01_H_Shape_Structure
            
            # Try to extract description from first line of file
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    first_line = f.readline().strip()
                    # If first line is a markdown header, use it as description
                    if first_line.startswith('#'):
                        description = first_line.lstrip('#').strip()
                    else:
                        description = f"Knowledge from {md_file.name}"
            except:
                description = f"Knowledge from {md_file.name}"
            
            knowledge_index[key] = {
                "path": file_path_str,
                "category": category,
                "description": description,
                "size": md_file.stat().st_size,
                "subpath": str(rel_path.parent) if rel_path.parent != Path(".") else None  # Subdirectory path for display
            }
    
    return knowledge_index

# Auto-discover knowledge at module import time (for backward compatibility)
KNOWLEDGE_INDEX = auto_discover_knowledge()

@tool
def scan_knowledge_base(rescan: bool = False) -> str:
    """Scan and list all available specialized knowledge domains.
    
    Use this tool to discover what knowledge is available before loading.
    Returns a categorized list of all knowledge files with descriptions.
    
    Args:
        rescan: If True, re-scan the file system for new/deleted knowledge files (default: False)
    
    Returns:
        Formatted list of available knowledge domains
    """
    global KNOWLEDGE_INDEX
    
    # Re-scan if requested (dynamic discovery)
    if rescan:
        KNOWLEDGE_INDEX = auto_discover_knowledge()
    
    if not KNOWLEDGE_INDEX:
        return "❌ No knowledge files found"
    
    # Group by category
    by_category = {}
    for key, info in KNOWLEDGE_INDEX.items():
        category = info['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append((key, info))
    
    # Format output
    output = ["📚 Available Knowledge Domains:", ""]
    
    for category, items in sorted(by_category.items()):
        output.append(f"【{category.upper()}】")
        for key, info in sorted(items):
            size_kb = info['size'] / 1024
            output.append(f"  • {key}")
            output.append(f"    - {info['description']}")
            # Show subdirectory path if file is in a subdirectory
            if info.get('subpath'):
                output.append(f"    - Location: {info['subpath']}/{Path(info['path']).name} ({size_kb:.1f} KB)")
            else:
                output.append(f"    - File: {info['path']} ({size_kb:.1f} KB)")
        output.append("")
    
    output.append(f"Total: {len(KNOWLEDGE_INDEX)} knowledge domains")
    output.append("")
    output.append("💡 Use load_domain_knowledge(domain_name) to load specific knowledge")
    
    return "\n".join(output)

@tool
def load_domain_knowledge(domain: str) -> str:
    """Load specific domain knowledge from documentation files.
    
    This tool dynamically loads knowledge from automatically discovered markdown files.
    The knowledge base is scanned at module import time and can be refreshed at runtime.
    
    **IMPORTANT**:
    - Always use scan_knowledge_base() first to discover available domains.
    - For any knowledge base, load its KB index (KB_INDEX.md) FIRST to understand required module combinations.
    - After calling this tool, you MUST print the returned content into the conversation context so the model can actually consume the knowledge. Do NOT only log status.
    Domain names are auto-generated from file paths (subdirectories joined with underscores).
    Available domains depend on the configured KNOWLEDGE_DIRECTORIES and may vary between installations.
    
    Args:
        domain: The knowledge domain name (obtained from scan_knowledge_base() output)
        
    Returns:
        The complete content of the knowledge documentation with metadata:
        - Description (from first line header)
        - File path
        - File size
        
    Example workflow:
        1. Call scan_knowledge_base() to see all available domains
        2. Load the KB index first, and PRINT its content
        3. Use search_knowledge(keyword) if you need to find domains by keyword
        4. Call load_domain_knowledge(domain_name) with the desired domain, and PRINT the returned content
    """
    if domain not in KNOWLEDGE_INDEX:
        # Dynamically show a sample of available domains (up to 10, or all if less than 10)
        available_keys = sorted(KNOWLEDGE_INDEX.keys())
        sample_size = min(10, len(available_keys))
        available_sample = ', '.join(available_keys[:sample_size])
        total_count = len(available_keys)
        
        if total_count == 0:
            return f"""❌ Unknown domain: '{domain}'

💡 Tip: No knowledge domains found. Use refresh_knowledge_index() to re-scan directories.
"""
        elif total_count <= sample_size:
            return f"""❌ Unknown domain: '{domain}'

💡 Tip: Use scan_knowledge_base() to see all available domains

Available domains ({total_count}): {available_sample}
"""
        else:
            return f"""❌ Unknown domain: '{domain}'

💡 Tip: Use scan_knowledge_base() to see all {total_count} available domains

Sample domains: {available_sample}...
"""
    
    knowledge = KNOWLEDGE_INDEX[domain]
    filepath = PROJECT_ROOT / knowledge["path"]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        size_kb = len(content) / 1024
        
        return f"""✅ Loaded domain: {domain}

📄 Description: {knowledge['description']}
📁 File: {knowledge['path']}
📊 Size: {size_kb:.1f} KB ({len(content)} chars)

{'='*60}
{content}
{'='*60}

✅ Knowledge loaded successfully. You can now answer based on this knowledge.
"""
    except FileNotFoundError:
        return f"❌ Knowledge file not found: {knowledge['path']}"
    except Exception as e:
        return f"❌ Failed to load {domain}: {e}"

@tool
def refresh_knowledge_index() -> str:
    """
    Refresh the knowledge index by re-scanning all knowledge directories.
    
    Use this when you've added new knowledge files or modified existing ones.
    This will update the internal index without restarting the program.
    
    Returns:
        Summary of the refreshed knowledge index
    """
    global KNOWLEDGE_INDEX
    
    old_count = len(KNOWLEDGE_INDEX)
    KNOWLEDGE_INDEX = auto_discover_knowledge()
    new_count = len(KNOWLEDGE_INDEX)
    
    result = f"🔄 Knowledge index refreshed!\n\n"
    result += f"📊 Before: {old_count} knowledge files\n"
    result += f"📊 After: {new_count} knowledge files\n"
    
    if new_count > old_count:
        result += f"✅ Added {new_count - old_count} new knowledge file(s)\n"
    elif new_count < old_count:
        result += f"❌ Removed {old_count - new_count} knowledge file(s)\n"
    else:
        result += f"✓ No changes detected\n"
    
    # Show current categories
    categories = {}
    for info in KNOWLEDGE_INDEX.values():
        cat = info['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    result += f"\n📂 Current categories:\n"
    for cat, count in categories.items():
        result += f"  • {cat}: {count} files\n"
    
    return result


@tool
def add_knowledge_directory(directory_path: str, category_name: str = "custom") -> str:
    """
    Dynamically add a new knowledge directory to scan.
    
    This allows you to add knowledge from external directories at runtime.
    
    Args:
        directory_path: Path to the directory containing .md knowledge files
        category_name: Category name for this knowledge source (default: "custom")
    
    Returns:
        Success message with discovered files count
    """
    global KNOWLEDGE_DIRECTORIES, KNOWLEDGE_INDEX
    
    # Validate path
    dir_path = Path(directory_path)
    if not dir_path.exists():
        return f"❌ Directory not found: {directory_path}"
    
    if not dir_path.is_dir():
        return f"❌ Not a directory: {directory_path}"
    
    # Add to directories
    KNOWLEDGE_DIRECTORIES[category_name] = str(dir_path.relative_to(PROJECT_ROOT) if dir_path.is_relative_to(PROJECT_ROOT) else dir_path)
    
    # Re-scan
    KNOWLEDGE_INDEX = auto_discover_knowledge()
    
    # Count files in new category
    new_files = sum(1 for info in KNOWLEDGE_INDEX.values() if info['category'] == category_name)
    
    return f"✅ Added knowledge directory: {directory_path}\n" \
           f"📂 Category: {category_name}\n" \
           f"📄 Found {new_files} knowledge file(s)"


@tool
def search_knowledge(keyword: str) -> str:
    """Search for knowledge domains related to a keyword.
    
    Use this when you're not sure which domain to load.
    Searches in domain names, descriptions, and file paths.
    Case-insensitive partial matching.
    
    Args:
        keyword: Search term (any text that might appear in domain names, descriptions, or paths)
    
    Returns:
        List of relevant knowledge domains matching the keyword
    """
    keyword_lower = keyword.lower()
    matches = []
    
    for key, info in KNOWLEDGE_INDEX.items():
        # Search in key name and description
        if (keyword_lower in key.lower() or 
            keyword_lower in info['description'].lower() or
            keyword_lower in info['path'].lower()):
            matches.append((key, info))
    
    if not matches:
        return f"❌ No knowledge domains found for keyword: '{keyword}'\n\n💡 Use scan_knowledge_base() to see all available domains"
    
    # Format results
    output = [f"🔍 Found {len(matches)} knowledge domain(s) for '{keyword}':", ""]
    
    for key, info in sorted(matches):
        size_kb = info['size'] / 1024
        output.append(f"  • {key}")
        output.append(f"    - {info['description']}")
        # Show subdirectory path if file is in a subdirectory
        if info.get('subpath'):
            output.append(f"    - Location: {info['subpath']}/{Path(info['path']).name} ({size_kb:.1f} KB)")
        else:
            output.append(f"    - {info['path']} ({size_kb:.1f} KB)")
        output.append("")
    
    output.append("💡 Use load_domain_knowledge(domain_name) to load")
    
    return "\n".join(output)

@tool
def export_knowledge_index(output_path: str = None) -> str:
    """
    Export the current knowledge index to a JSON file.
    
    Useful for inspecting what knowledge files are currently indexed,
    or for backup/documentation purposes.
    
    Args:
        output_path: Path to save the JSON file. If None, uses a timestamped file
                     in output/logs/ directory
    
    Returns:
        Success message with file path
    """
    try:
        # Generate default path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"output/logs/knowledge_index_{timestamp}.json"
        
        # Prepare output
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create export data
        export_data = {
            "metadata": {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_files": len(KNOWLEDGE_INDEX),
                "directories": KNOWLEDGE_DIRECTORIES
            },
            "knowledge_files": KNOWLEDGE_INDEX
        }
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        abs_path = output_file.resolve()
        return f"✅ Knowledge index exported to: {abs_path}\n" \
               f"📊 Total knowledge files: {len(KNOWLEDGE_INDEX)}"
    
    except Exception as e:
        return f"❌ Failed to export knowledge index: {e}"


# Export available tools
__all__ = [
    'scan_knowledge_base', 
    'load_domain_knowledge', 
    'search_knowledge',
    'refresh_knowledge_index',
    'add_knowledge_directory',
    'export_knowledge_index'
]

