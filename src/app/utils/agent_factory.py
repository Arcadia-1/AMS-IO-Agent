"""
Agent Factory - Configuration-driven tool loading
"""

import sys
from pathlib import Path
from smolagents import OpenAIServerModel
from smolagents.gradio_ui import GradioUI

from src.app.utils.tool_loader import get_tools_for_agent
from src.tools.tool_manager import set_agent_instance
from src.app.utils.agent_utils import TokenLimitedCodeAgent
from src.app.utils.custom_logger import MinimalOutputLogger

# Import default tools from smolagents
try:
    from smolagents.default_tools import UserInputTool
except ImportError:
    # Fallback if default_tools is not available
    UserInputTool = None

def create_model(model_config):
    """Create and configure the AI model"""
    return OpenAIServerModel(
        model_id=model_config["model_id"],
        api_base=model_config["api_base"],
        api_key=model_config["api_key"],
        flatten_messages_as_text=True,
        max_tokens=8192,
        temperature=model_config.get("temperature", 0.7)
    )


def create_agent(model, final_instructions, show_code_execution: bool = False, config_path: str = "config/tools_config.yaml"):
    """
    Create and configure the CodeAgent with dynamic tool loading from config.
    
    Args:
        model: The LLM model instance
        final_instructions: System prompt for the agent
        show_code_execution: If True, show "Executing parsed code" blocks (default: False)
        config_path: Path to tool configuration file (optional)
        
    Returns:
        Configured agent instance
    """
    # Create custom logger: shows Thought and Observation, but hides code execution details
    logger = MinimalOutputLogger() if not show_code_execution else None
    
    # Load tools from configuration instead of hardcoding
    tools = get_tools_for_agent(config_path)
    
    # Add default tools from smolagents (like user_input)
    if UserInputTool is not None:
        tools.append(UserInputTool())
    
    agent = TokenLimitedCodeAgent(
        tools=tools,
        model=model,
        instructions=final_instructions,
        # logger=logger,
        stream_outputs=True,
        additional_authorized_imports=[
            'os', 'pathlib', 'io', 'sys', 'subprocess', 
            'typing', 'posixpath', 'ntpath', 'importlib', 'glob', 'json'
        ],
        executor_kwargs={
            "additional_functions": {
                "open": open, 
                "exec": exec,
                "locals": locals,
                "globals": globals,
                "vars": vars
            }
        },
        max_steps=100
    )
    
    # Set agent instance for dynamic tool management
    set_agent_instance(agent)
    
    # Load all existing Python helper tools (hot-reload support)
    try:
        from ..tools.python_tool_creator import load_all_python_helpers
        load_all_python_helpers()
    except Exception as e:
        print(f"Warning: Failed to load Python helpers: {e}")
    
    return agent


def start_web_ui(agent):
    """Start the Gradio web interface"""
    try:
        print("\nStarting Web UI, please wait...")
        gradio_ui = GradioUI(agent, file_upload_folder="uploads", reset_agent_memory=True)
        gradio_ui.launch()
        return True
    except ImportError:
        print("Gradio dependencies not installed, please run: pip install 'smolagents[gradio]'")
        sys.exit(1)
    except Exception as e:
        print(f"Failed to start web UI: {e}")
        return False


def _load_config_from_file(config_file):
    """
    Load configuration from a single file.
    
    Args:
        config_file: Path to YAML or JSON config file (Path object or string)
        
    Returns:
        Dictionary with config data, or None if failed
    """
    import os
    import json
    from pathlib import Path
    
    # Convert to Path object if it's a string
    if isinstance(config_file, str):
        config_file = Path(config_file)
    
    if not config_file.exists():
        return None
    
    # Get file extension
    file_ext = config_file.suffix.lower()
    file_str = str(config_file)
    
    # Try to import yaml, but it's optional
    try:
        import yaml
        has_yaml = True
    except ImportError:
        has_yaml = False
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            # Try YAML first if available
            if file_ext in ['.yaml', '.yml'] and has_yaml:
                config = yaml.safe_load(f)
            elif file_ext == '.json':
                config = json.load(f)
            else:
                # Try YAML first, then JSON
                if has_yaml:
                    try:
                        f.seek(0)
                        config = yaml.safe_load(f)
                    except:
                        f.seek(0)
                        config = json.load(f)
                else:
                    # No yaml, try JSON
                    f.seek(0)
                    config = json.load(f)
            
            if config and isinstance(config, dict):
                return config
    except Exception as e:
        print(f"⚠️  Warning: Failed to load prompt config from {file_str}: {e}")
    
    return None


def _get_config_files(config_path):
    """
    Get list of config files from a directory path.
    If a file path is provided, uses its parent directory.
    
    Args:
        config_path: Path to directory (or file, in which case its parent directory is used)
        
    Returns:
        List of config file paths (YAML/JSON files in the directory)
    """
    from pathlib import Path
    
    path_obj = Path(config_path)
    
    # If it's a file, use its parent directory
    if path_obj.is_file():
        search_dir = path_obj.parent
    # If it's a directory, use it directly
    elif path_obj.is_dir():
        search_dir = path_obj
    # If it doesn't exist, assume it's a directory path
    else:
        search_dir = path_obj
    
    # Find all YAML/JSON files in the directory
    config_files = []
    if search_dir.exists() and search_dir.is_dir():
        config_files.extend(search_dir.glob('*.yaml'))
        config_files.extend(search_dir.glob('*.yml'))
        config_files.extend(search_dir.glob('*.json'))
    
    # Remove duplicates and sort
    config_files = sorted(set(config_files))
    return config_files


def load_prompt_from_config(prompt_key, config_file="user_prompt"):
    """
    Load prompt from configuration files in a directory by key.
    If a file path is provided, searches in its parent directory.
    
    Args:
        prompt_key: Key to look up in the config files
        config_file: Path to directory (or file, in which case its parent directory is used)
                    All YAML/JSON files in the directory will be searched
        
    Returns:
        Prompt string if found, None otherwise
        (searches files in alphabetical order, returns first match)
    """
    config_files = _get_config_files(config_file)
    
    # Search through all config files in order
    for config_path in config_files:
        config = _load_config_from_file(config_path)
        if config and prompt_key in config:
            return config[prompt_key]
    
    return None


def list_available_prompts(config_file="user_prompt"):
    """
    List all available prompt keys from configuration files in a directory.
    If a file path is provided, searches in its parent directory.
    
    Args:
        config_file: Path to directory (or file, in which case its parent directory is used)
                    All YAML/JSON files in the directory will be scanned
        
    Returns:
        Dictionary mapping file paths to lists of prompt keys, or empty dict if no files found
    """
    config_files = _get_config_files(config_file)
    result = {}
    
    for config_path in config_files:
        config = _load_config_from_file(config_path)
        if config and isinstance(config, dict):
            result[str(config_path)] = list(config.keys())
    
    return result


def list_all_prompt_keys(config_file="user_prompt"):
    """
    List all unique prompt keys from all configuration files in a directory.
    If a file path is provided, searches in its parent directory.
    
    Args:
        config_file: Path to directory (or file, in which case its parent directory is used)
                    All YAML/JSON files in the directory will be scanned
        
    Returns:
        List of all unique prompt keys across all files
    """
    all_keys = set()
    prompts_by_file = list_available_prompts(config_file)
    
    for keys in prompts_by_file.values():
        all_keys.update(keys)
    
    return sorted(all_keys)


def run_cli_interface(agent, prompt_key=None, prompt_text=None, prompt_config_file="user_prompt"):
    """
    Run the command line interface
    
    Args:
        agent: The agent instance
        prompt_key: Optional prompt key to load from config files
        prompt_text: Optional direct prompt text (takes precedence over prompt_key)
        prompt_config_file: Path to directory containing YAML/JSON prompt files.
                          If a file path is provided, its parent directory will be used.
                          All YAML/JSON files in the directory will be searched.
    """
    import os
    from .banner import print_logo
    from .simple_task_logger import get_task_logger
    
    print_logo()
    
    task_logger = get_task_logger()
    is_first_turn = True
    first_user_input = None
    interrupted = False
    
    # Track Ctrl-C timing for double Ctrl-C exit
    import time
    last_interrupt_time = None
    INTERRUPT_EXIT_THRESHOLD = 2.0  # Exit if two Ctrl-C within 2 seconds
    
    # Track if previous task was interrupted (to notify model on next input)
    previous_task_interrupted = False
    interrupted_task_prompt = None
    
    # Priority: 1. Direct prompt text, 2. Command line prompt key, 3. Config file prompt, 4. user_prompt.txt, 5. Interactive input
    auto_prompt = None
    
    # 1. Use direct prompt text if provided (highest priority)
    if prompt_text:
        auto_prompt = prompt_text
        print(f"\n📄 Using direct prompt text")
        print(f"   Prompt: {auto_prompt[:100]}{'...' if len(auto_prompt) > 100 else ''}\n")
    
    # 2. Try loading from config file by key (if provided and no direct text)
    if not auto_prompt and prompt_key:
        auto_prompt = load_prompt_from_config(prompt_key, prompt_config_file)
        if auto_prompt:
            # Find which file contained the prompt
            config_files = _get_config_files(prompt_config_file)
            found_in = None
            for config_path in config_files:
                config = _load_config_from_file(config_path)
                if config and prompt_key in config:
                    found_in = str(config_path)
                    break
            
            if found_in:
                print(f"\n📄 Loaded prompt from: {found_in} (key: '{prompt_key}')")
            else:
                print(f"\n📄 Loaded prompt from config: {prompt_config_file} (key: '{prompt_key}')")
            print(f"   Prompt: {auto_prompt[:100]}{'...' if len(auto_prompt) > 100 else ''}\n")
        else:
            all_keys = list_all_prompt_keys(prompt_config_file)
            prompts_by_file = list_available_prompts(prompt_config_file)
            
            if all_keys:
                print(f"⚠️  Warning: Prompt key '{prompt_key}' not found in any config file")
                print(f"   Searched in: {', '.join(prompts_by_file.keys())}")
                print(f"   Available keys: {', '.join(all_keys[:20])}{'...' if len(all_keys) > 20 else ''}")
            else:
                print(f"⚠️  Warning: No config files found or all are empty")
                print(f"   Searched in: {prompt_config_file}")
            print("   Falling back to interactive input or user_prompt.txt\n")
    
    # 3. If no prompt from config key, try user_prompt.txt (backward compatibility)
    if not auto_prompt:
        user_prompt_file = os.getenv("USER_PROMPT_FILE", "user_prompt.txt")
        if os.path.exists(user_prompt_file):
            try:
                with open(user_prompt_file, 'r', encoding='utf-8') as f:
                    auto_prompt = f.read().strip()
                if auto_prompt:
                    print(f"\n📄 Auto-loaded prompt from: {user_prompt_file}")
                    print(f"   Prompt: {auto_prompt[:100]}{'...' if len(auto_prompt) > 100 else ''}\n")
            except Exception as e:
                print(f"⚠️  Warning: Failed to load prompt from {user_prompt_file}: {e}")

    try:
        while True:
            try:
                # Use auto-loaded prompt for first turn if available
                if is_first_turn and auto_prompt:
                    user_input = auto_prompt
                    print(f"[User prompt]: {user_input}")
                else:
                    user_input = input("\n[User prompt]: ").strip()

                # Skip empty inputs (can happen after Ctrl-C on Windows)
                if not user_input:
                    continue

                if user_input.lower() in ["quit", "exit"]:
                    print("\n[Agent]: Goodbye!")
                    break

                # Add interruption notice if previous task was interrupted
                if previous_task_interrupted:
                    interruption_notice = f"[Note: Your previous task was interrupted. If the user asks about it, acknowledge the interruption.]\n\n"
                    user_input = interruption_notice + user_input
                    previous_task_interrupted = False
                    interrupted_task_prompt = None

                # Start task logging
                task_logger.start_task(user_input)

                try:
                    agent.run(task=user_input, reset=is_first_turn)
                    # Task succeeded - clear interruption flag
                    task_logger.end_task("success")
                    previous_task_interrupted = False
                    interrupted_task_prompt = None
                except KeyboardInterrupt:
                    # Ctrl-C during agent.run() - check for double Ctrl-C exit
                    current_time = time.time()
                    if last_interrupt_time and (current_time - last_interrupt_time) < INTERRUPT_EXIT_THRESHOLD:
                        # Double Ctrl-C within threshold - exit
                        print("\n\n⚠️  Double Ctrl-C detected - exiting...")
                        interrupted = True
                        break
                    
                    # Single Ctrl-C - just stop current generation
                    last_interrupt_time = current_time
                    task_logger.end_task("interrupted")
                    print("\n\n⚠️  Generation interrupted by user (Ctrl-C)")
                    print("   Type 'quit' or 'exit' to end session, or press Ctrl-C again quickly to exit.")
                    # Mark that this task was interrupted (will notify model on next input)
                    previous_task_interrupted = True
                    interrupted_task_prompt = user_input[:100] + ("..." if len(user_input) > 100 else "")
                    # Don't break - continue the loop for next input
                    if is_first_turn:
                        first_user_input = user_input
                        is_first_turn = False
                        auto_prompt = None
                    continue
                except Exception as e:
                    # Task failed
                    task_logger.end_task("failed", str(e))
                    raise

                if is_first_turn:
                    first_user_input = user_input
                    is_first_turn = False
                    # Clear auto_prompt after first use
                    auto_prompt = None

            except KeyboardInterrupt:
                # Ctrl-C during input() - check for double Ctrl-C exit
                current_time = time.time()
                if last_interrupt_time and (current_time - last_interrupt_time) < INTERRUPT_EXIT_THRESHOLD:
                    # Double Ctrl-C within threshold - exit
                    print("\n\n⚠️  Double Ctrl-C detected - exiting...")
                    interrupted = True
                    break
                
                # Single Ctrl-C - clear any pending input on Windows
                last_interrupt_time = current_time
                print("")
                try:
                    import msvcrt
                    while msvcrt.kbhit():
                        msvcrt.getch()
                except (ImportError, Exception):
                    pass
                continue
            except EOFError:
                # Ctrl-D (EOF) - just continue
                print("")
                continue
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                # Don't break on errors - allow user to continue
                continue
    finally:
        pass
    
    return first_user_input, interrupted

