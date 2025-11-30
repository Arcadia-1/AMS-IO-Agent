# Quick Start Script for AMS-IO-Agent (Windows PowerShell)
# This script automatically fixes permissions and runs the setup process
# Usage: .\quick_start.ps1

# Strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Logging functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "  AMS-IO-Agent Quick Start" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Step 1: Fix executable permissions (not needed on Windows, but check script exists)
Write-Info "[1/3] Checking setup scripts..."

$setupScript = Join-Path $ScriptDir "setup\setup_powershell.ps1"
if (-not (Test-Path $setupScript)) {
    Write-Error "setup\setup_powershell.ps1 not found"
    exit 1
}
Write-Success "Setup scripts found"
Write-Host ""

# Step 2: Check if setup has already been run
if ((Test-Path ".venv") -and (Test-Path ".env")) {
    Write-Info "[2/3] Setup already completed"
    Write-Success "Virtual environment exists"
    Write-Success "Configuration file (.env) exists"
    Write-Host ""
    Write-Host "Note: If you want to re-run setup, delete .venv and .env first"
    Write-Host ""
    
    # Ask if user wants to continue anyway
    $answer = Read-Host "Do you want to run setup again? (y/N)"
    if ($answer -ne "y" -and $answer -ne "Y") {
        Write-Host ""
        Write-Host "Setup skipped. You can now:"
        Write-Host "  .venv\Scripts\Activate.ps1  # Activate virtual environment"
        Write-Host "  python main.py              # Start the agent"
        exit 0
    }
    Write-Host ""
}

# Step 3: Run the actual setup script
Write-Info "[3/3] Running setup script..."
Write-Host ""

# Execute the setup script
try {
    & $setupScript
    $setupExitCode = $LASTEXITCODE
    
    if ($setupExitCode -eq 0) {
        # Setup script already displays next steps, no need to repeat here
        exit 0
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "  Setup Failed (exit code: $setupExitCode)" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please check the error messages above and try again."
        exit $setupExitCode
    }
} catch {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  Setup Failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""
    Write-Error "Error: $_"
    exit 1
}

