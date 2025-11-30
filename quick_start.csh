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

# Run setup.csh (use absolute path to avoid issues)
set SETUP_SCRIPT = "$SCRIPT_DIR/setup/setup.csh"
if (! -x "$SETUP_SCRIPT") then
    echo "❌ Error: $SETUP_SCRIPT is not executable"
    exit 1
endif

# Execute the setup script
$SETUP_SCRIPT
set SETUP_EXIT_CODE = $status

if ($SETUP_EXIT_CODE == 0) then
    # Setup script already displays next steps, no need to repeat here
    exit 0
else
    echo ""
    echo "========================================"
    echo "  Setup Failed (exit code: $SETUP_EXIT_CODE)"
    echo "========================================"
    echo ""
    echo "Please check the error messages above and try again."
    exit $SETUP_EXIT_CODE
endif

