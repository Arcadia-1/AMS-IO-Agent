#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Profile Management Tool
Allows AI to modify user preferences across sessions
"""

import os
from pathlib import Path
from typing import Optional
from smolagents import tool

PROJECT_ROOT = Path(__file__).parent.parent.parent
PROFILE_DIR = PROJECT_ROOT / "user_data"
PROFILE_DIR.mkdir(exist_ok=True)


def get_profile_path(username: Optional[str] = None) -> Path:
    """Get the path to user profile file."""
    env_path = os.getenv("USER_PROFILE_PATH", "").strip()
    if env_path and env_path.lower() not in ["", "none", "null"]:
        profile_path = Path(env_path)
        if not profile_path.is_absolute():
            profile_path = PROJECT_ROOT / profile_path
        return profile_path
    
    # Try default_user_profile.md first (if exists), then username-based profile
    default_profile = PROFILE_DIR / "default_user_profile.md"
    if default_profile.exists():
        return default_profile
    
    if username is None:
        username = os.getenv("USER_PROFILE_NAME", "default_user")
    return PROFILE_DIR / f"{username}_profile.md"


def read_profile(username: Optional[str] = None) -> str:
    """Read user profile content, create from default if not exists"""
    profile_path = get_profile_path(username)
    
    if not profile_path.exists():
        default_profile_path = PROFILE_DIR / "default_user_profile.md"
        
        if default_profile_path.exists() and profile_path != default_profile_path:
            try:
                import shutil
                shutil.copy(default_profile_path, profile_path)
                print(f"⚠️  Profile not found, copied from default: {profile_path}")
            except Exception as e:
                print(f"⚠️  Failed to copy default profile: {e}")
                return ""
        else:
            # Show warning if profile file doesn't exist
            print(f"⚠️  Warning: User profile file not found: {profile_path}")
            if not default_profile_path.exists():
                print(f"   Default profile also not found: {default_profile_path}")
                print(f"   You can create a profile file at: {profile_path}")
            return ""
    
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"⚠️  Error reading profile file {profile_path}: {e}")
        return ""


@tool
def update_user_profile(new_content: str, username: Optional[str] = None) -> str:
    """
    Update user profile by writing new content.
    
    You can:
    1. Read current profile (it's already in your system prompt)
    2. Modify the content as needed
    3. Write back the full updated content
    
    Args:
        new_content: Complete new profile content in markdown format
        username: Username for the profile (default: from .env)
    
    Returns:
        Success message
        
    Example:
        # Agent reads current profile from system prompt
        # Agent modifies it (add/remove/change entries)
        # Agent writes back complete content
        update_user_profile(modified_content)
    """
    profile_path = get_profile_path(username)
    
    try:
        with open(profile_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return f"✅ User profile updated: {profile_path}"
    except Exception as e:
        return f"❌ Failed to update profile: {e}"

__all__ = ['update_user_profile']
