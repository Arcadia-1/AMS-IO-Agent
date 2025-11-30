#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from .config_utils import load_instructions_from_file
from src.tools.user_profile_tool import get_profile_path

project_root = Path(__file__).parent.parent.parent.parent

def load_system_prompt_with_profile() -> str:
    """Load system prompt and append user profile if exists"""
    # Load system prompt from the correct path
    system_prompt_path = project_root / "Knowledge_Base" / "01_CORE" / "KB_Agent" / "system_prompt_no_ir.md"
    base_prompt = load_instructions_from_file(str(system_prompt_path))
    
    # Load user profile (will show warning if not found)
    profile_path = get_profile_path()
    user_profile = load_instructions_from_file(str(profile_path))
    
    if user_profile:
        return f"{base_prompt}\n\n---\n\n## User Profile\n\n{user_profile}"
    return base_prompt


if __name__ == "__main__":
    prompt = load_system_prompt_with_profile()
    print(f"{'=' * 80}\n{prompt}\n{'=' * 80}\nTotal: {len(prompt)} chars")
