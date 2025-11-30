import sys
from pathlib import Path
from smolagents import OpenAIServerModel
from smolagents.gradio_ui import GradioUI

# Import default tools from smolagents
try:
    from smolagents.default_tools import UserInputTool
except ImportError:
    # Fallback if default_tools is not available
    UserInputTool = None

from src.tools.il_runner_tool import (
    run_il_file, 
    list_il_files,
    run_il_with_screenshot, 
    clear_all_figures_in_window,
    screenshot_current_window
)
from src.tools.drc_runner_tool import run_drc
from src.tools.lvs_runner_tool import run_lvs
from src.tools.pex_runner_tool import run_pex
# from src.tools.example_search_tool import code_example_search
from src.tools.io_ring_generator_tool import generate_io_ring_schematic, validate_intent_graph, generate_io_ring_layout
from src.tools.knowledge_loader_tool import (
    scan_knowledge_base, 
    load_domain_knowledge, 
    search_knowledge,
    refresh_knowledge_index,
    add_knowledge_directory,
    export_knowledge_index
)
from src.tools.tool_manager import (
    list_registered_tools, 
    get_tool_info, 
    check_tool_availability,
    export_tools_snapshot,
    get_tools_summary,
    set_agent_instance
)
from src.tools.user_profile_tool import (
    load_user_profile,
    update_user_profile,
    append_to_user_profile,
    get_user_preference,
    list_user_profiles,
    clear_user_profile_section
)
from src.tools.skill_tools_manager import (
    list_skill_tools,
    run_skill_tool,
    create_skill_tool,
    update_skill_tool,
    delete_skill_tool
)
from src.app.utils.agent_utils import TokenLimitedCodeAgent
from src.app.utils.custom_logger import MinimalOutputLogger

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

def create_agent(model, final_instructions, show_code_execution: bool = False):
    """
    Create and configure the CodeAgent with dynamic knowledge loading.
    
    Args:
        model: The LLM model instance
        final_instructions: System prompt for the agent
        show_code_execution: If True, show "Executing parsed code" blocks (default: False)
        
    Returns:
        Configured agent instance
    """
    # Create custom logger: shows Thought and Observation, but hides code execution details
    logger = MinimalOutputLogger() if not show_code_execution else None
    
    agent = TokenLimitedCodeAgent(
        tools=[
            # Tool management (meta-tools)
            list_registered_tools,
            get_tool_info,
            check_tool_availability,
            export_tools_snapshot,
            get_tools_summary,
            
            # Knowledge loading tools (dynamic prompt loading)
            scan_knowledge_base,
            search_knowledge,
            load_domain_knowledge,
            refresh_knowledge_index,
            add_knowledge_directory,
            export_knowledge_index,
            
            # Virtuoso execution tools
            run_il_file,
            list_il_files,
            run_il_with_screenshot,
            clear_all_figures_in_window,
            screenshot_current_window,
            
            # SKILL tools management (small utility scripts)
            list_skill_tools,
            run_skill_tool,
            create_skill_tool,
            update_skill_tool,
            delete_skill_tool,
            
            # Verification tools
            run_drc,
            run_lvs,
            run_pex,
            
            # IO Ring generation tools
            generate_io_ring_schematic,
            validate_intent_graph,
            generate_io_ring_layout,
            
            # User profile management
            load_user_profile,
            update_user_profile,
            append_to_user_profile,
            get_user_preference,
            list_user_profiles,
            clear_user_profile_section,
        ] + ([UserInputTool()] if UserInputTool is not None else []),
        model=model,
        instructions=final_instructions,
        stream_outputs=True,  # Keep streaming for Thought and Observation
        logger=logger,  # Custom logger to filter out code execution
        additional_authorized_imports=['os', 'pathlib', 'io', 'sys', 'subprocess', 'typing', 'posixpath', 'importlib', 'glob', 'json'],
        executor_kwargs={"additional_functions": {"open": open, "exec": exec}},
        max_steps=100
    )
    
    # Set agent instance for dynamic tool management
    set_agent_instance(agent)
    
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

def run_cli_interface(agent):
    """Run the command line interface"""
    from .banner import print_logo
    print_logo()
    
    ORANGE = '\033[33m'
    RESET = '\033[0m'

    is_first_turn = True
    first_user_input = None
    interrupted = False

    try:
        while True:
            try:
                user_input = input("\n[User prompt]: ")
                if is_first_turn:
                    first_user_input = user_input

                agent_response = agent.run(task=user_input, reset=is_first_turn)

                if is_first_turn:
                    is_first_turn = False

            except KeyboardInterrupt:
                interrupted = True
                print("\n[Agent]: Goodbye!")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                break
    finally:
        pass  # Cleanup if needed
    
    return first_user_input, interrupted 