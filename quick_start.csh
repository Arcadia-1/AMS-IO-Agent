#!/bin/csh -f
# Quick Start Script for AMS-IO-Agent (csh version)
# This script automatically fixes permissions and runs the setup process
# Usage: ./quick_start.csh

# Get script directory
set SCRIPT_DIR = `dirname $0`
if ("$SCRIPT_DIR" == ".") then
    set SCRIPT_DIR = `pwd`
else
    cd "$SCRIPT_DIR"
    set SCRIPT_DIR = `pwd`
    cd -
endif

cd "$SCRIPT_DIR"

echo ""
echo "========================================"
echo "  AMS-IO-Agent Quick Start"
echo "========================================"
echo ""

# Step 1: Fix executable permissions
echo "[1/3] Checking and fixing executable permissions..."
chmod +x setup/*.csh >& /dev/null
chmod +x setup/*.sh >& /dev/null
chmod +x verify_imports.py >& /dev/null
echo "✅ Permissions fixed"
echo ""

# Step 2: Check if setup has already been run
if (-d ".venv" && -f ".env") then
    echo "[2/3] Setup already completed"
    echo "✅ Virtual environment exists"
    echo "✅ Configuration file (.env) exists"
    echo ""
    echo "Note: If you want to re-run setup, delete .venv and .env first"
    echo ""
    
    # Ask if user wants to continue anyway
    echo -n "Do you want to run setup again? (y/N): "
    set answer = $<
    if ("$answer" != "y" && "$answer" != "Y") then
        echo ""
        echo "Setup skipped. You can now:"
        echo "  source .venv/bin/activate.csh  # Activate virtual environment"
        echo "  python main.py                  # Start the agent"
        exit 0
    endif
    echo ""
endif

# Step 3: Check if csh is available (for setup.csh)
if (! -f "setup/setup.csh") then
    echo "❌ Error: setup/setup.csh not found"
    exit 1
endif

# Step 4: Run the actual setup script
echo "[3/3] Running setup script..."
echo ""

# Run setup.csh
csh setup/setup.csh
set SETUP_EXIT_CODE = $status

if ($SETUP_EXIT_CODE == 0) then
    echo ""
    echo "========================================"
    echo "  Setup Completed Successfully!"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "  1. Edit .env file to add your API keys:"
    echo "     nano .env"
    echo ""
    echo "  2. Configure config.yaml (optional):"
    echo "     nano config.yaml"
    echo ""
    echo "  3. Activate virtual environment:"
    echo "     source .venv/bin/activate.csh"
    echo ""
    echo "  4. Start the agent:"
    echo "     python main.py"
    echo ""
else
    echo ""
    echo "========================================"
    echo "  Setup Failed (exit code: $SETUP_EXIT_CODE)"
    echo "========================================"
    echo ""
    echo "Please check the error messages above and try again."
    exit $SETUP_EXIT_CODE
endif

