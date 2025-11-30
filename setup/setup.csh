#!/bin/csh -f
# Auto Setup Script for AMS-IO-Agent (csh)
# Author: AMS-IO-Agent Team
# Version: 2.0.0 - Modular version

# Exit on error
set exit_on_error

# Logging functions
alias print_info 'echo "[INFO]" \!*'
alias print_success 'echo "[SUCCESS]" \!*'
alias print_error 'echo "[ERROR]" \!*'

# Get project root directory (script is in setup/ subdirectory)
set CURPWD = `pwd`
set SCRIPT_DIR = `dirname $0`

# Get absolute path of script directory
if ("$SCRIPT_DIR" == ".") then
    set SCRIPT_ABS = "$CURPWD"
else
    cd $SCRIPT_DIR
    set SCRIPT_ABS = "`pwd`"
    cd $CURPWD
endif

# Project root is parent of script directory (since script is in setup/)
cd "$SCRIPT_ABS/.."
set PROJECT_ROOT = "`pwd`"
cd $CURPWD

main:
    echo ""
    echo "================================="
    echo "  AMS-IO-Agent Auto Setup Script"
    echo "  See /setup/README.md for more details"
    echo "  v2.0.0"
    echo "================================="
    echo ""
    
    cd "$PROJECT_ROOT"    
    goto check_requirements

check_requirements:
    if (`uname -s` != "Linux") then
        print_error "Only Linux is supported, current system: `uname -s`"
        exit 1
    endif
    
    if (`which git` == "") then
        print_error "Git not detected, please install it first"
        exit 1
    endif
    
    print_success "System check [✓ Linux] [✓ Git]"
    goto install_uv

install_uv:
    if (`which uv` != "") then
        print_info "[uv] Already installed"
        goto create_venv
    endif
    
    print_info "[uv] Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    setenv PATH "$HOME/.cargo/bin:$PATH"
    echo 'setenv PATH "$HOME/.cargo/bin:$PATH"' >> ~/.cshrc
    print_success "[uv] Installation complete"
    goto create_venv

create_venv:
    if (-d ".venv") then
        print_info "[venv] Already exists"
        goto install_dependencies
    endif
    
    print_info "[venv] Creating Python 3.11..."
    uv venv --python 3.11.11 .venv
    print_success "[venv] Creation complete"
    goto install_dependencies

install_dependencies:
    if (! -f ".venv/bin/activate.csh") then
        print_error "[venv] Activation script not found"
        exit 1
    endif
    
    source .venv/bin/activate.csh
    
    if (! -f "requirements.txt") then
        print_error "[dependencies] requirements.txt not found"
        exit 1
    endif
    
    print_info "[dependencies] Installing Python packages..."
    uv pip install -r requirements.txt
    print_success "[dependencies] Installation complete"
    goto setup_utf8_env

setup_utf8_env:
    echo ""
    print_info "[UTF-8] Configuring encoding environment variables..."
    
    # Check if ~/.cshrc already contains UTF-8 configuration
    set utf8_marker = "# AMS-IO-Agent UTF-8 Encoding Setup"
    if (`grep -c "$utf8_marker" ~/.cshrc` == 0) then
        # Append to ~/.cshrc
        echo "" >> ~/.cshrc
        echo "$utf8_marker" >> ~/.cshrc
        echo "setenv PYTHONIOENCODING utf-8" >> ~/.cshrc
        echo "setenv LC_ALL en_US.UTF-8" >> ~/.cshrc
        echo "setenv LANG en_US.UTF-8" >> ~/.cshrc
        print_success "[UTF-8] Added to ~/.cshrc, all new csh sessions will automatically enable UTF-8"
    else
        print_info "[UTF-8] Configuration already exists, skipping"
    endif
    
    # Apply to current session immediately
    setenv PYTHONIOENCODING utf-8
    setenv LC_ALL en_US.UTF-8
    setenv LANG en_US.UTF-8
    print_success "[UTF-8] Current session enabled"
    goto generate_env_config

generate_env_config:
    echo ""
    print_info "[1/2] Generating .env configuration..."
    $PROJECT_ROOT/setup/generate_env_config.csh
    goto generate_virtuoso_setup

generate_virtuoso_setup:
    echo ""
    print_info "[2/2] Generating virtuoso_setup.il..."
    
    # Bridge type selection (default: RAMIC Bridge for cross-server, change to 2 for skillbridge same-server)
    set bridge_choice = "1"
    
    # Initialize virtuoso_setup status (0 = success, 1 = failed)
    set virtuoso_setup_status = 0
    
    # Store bridge type and setup file path for final message
    set bridge_type = ""
    set virtuoso_setup_path = ""
    
    if ("$bridge_choice" == "1") then
        set bridge_type = "RAMIC"
        $PROJECT_ROOT/setup/generate_virtuoso_ramicbridge.csh
        set gen_status = $status
        if ($gen_status == 0) then
            set virtuoso_setup_path = "$PROJECT_ROOT/virtuoso_setup.il"
        endif
    else
        set bridge_type = "skillbridge"
        $PROJECT_ROOT/setup/generate_virtuoso_skillbridge.csh
        set gen_status = $status
        if ($gen_status == 0) then
            set virtuoso_setup_path = "$PROJECT_ROOT/virtuoso_setup.il"
        endif
    endif
    
    # Check if generation failed
    if ($gen_status != 0) then
        print_error "Failed to generate virtuoso_setup.il (exit code: $gen_status)"
        print_info "You can manually configure Virtuoso bridge later"
        set virtuoso_setup_status = 1
        # Continue anyway - virtuoso_setup.il is optional
    endif
    
    goto show_completion_info

show_completion_info:
    # Build completion message based on virtuoso_setup status
    if ($virtuoso_setup_status == 0) then
        print_success "Setup complete [✓ venv] [✓ dependencies] [✓ UTF-8] [✓ .env] [✓ virtuoso_setup.il]"
    else
        print_success "Setup complete [✓ venv] [✓ dependencies] [✓ UTF-8] [✓ .env] [✗ virtuoso_setup.il]"
    endif
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env file to add your API keys:"
    echo "     nano .env"
    echo ""
    echo "  2. Configure config.yaml (optional):"
    echo "     nano config.yaml"
    echo ""
    if ($virtuoso_setup_status == 0 && "$virtuoso_setup_path" != "") then
        echo "  3. Setup Virtuoso bridge:"
        if ("$bridge_type" == "RAMIC") then
            echo "     a) For cross-server connection, set up SSH port forwarding:"
            echo "        ssh -N -L 65432:127.0.0.1:65432 user@virtuoso-server"
            echo "     b) In Virtuoso CIW, execute:"
            /bin/printf '        load("%s")\n' "$virtuoso_setup_path"
        else
            echo "     In Virtuoso CIW, execute:"
            /bin/printf '     load("%s")\n' "$virtuoso_setup_path"
        endif
        echo ""
        echo "  4. Activate virtual environment:"
    else
        echo "  3. Activate virtual environment:"
    endif
    echo "     source .venv/bin/activate.csh"
    echo ""
    echo "  5. Start the agent:"
    echo "     python main.py"
    echo ""
    echo "Note: UTF-8 encoding has been added to ~/.cshrc"
    echo "      All new csh sessions will automatically enable UTF-8 encoding"
    echo ""
    exit 0

goto main