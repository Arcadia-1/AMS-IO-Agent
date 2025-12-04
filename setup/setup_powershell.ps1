# ================================================
# AMS-IO-Agent Auto Setup Script (Windows PowerShell)
# Version: 2.0.0
# ================================================

# Strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Get project root directory (script is in setup/ subdirectory)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# Logging functions
function Write-Info { param($Message) Write-Host "[INFO] $Message" -ForegroundColor Cyan }
function Write-Success { param($Message) Write-Host "[SUCCESS] $Message" -ForegroundColor Green }
function Write-Error { param($Message) Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Write-Warning { param($Message) Write-Host "[WARNING] $Message" -ForegroundColor Yellow }

# ================================================
# Main Script
# ================================================

Write-Host ""
Write-Host "=================================" -ForegroundColor Yellow
Write-Host "  AMS-IO-Agent Auto Setup Script" -ForegroundColor Yellow
Write-Host "  Windows PowerShell Edition" -ForegroundColor Yellow
Write-Host "  v2.0.0" -ForegroundColor Yellow
Write-Host "=================================" -ForegroundColor Yellow
Write-Host ""

Write-Info "Project Root: $ProjectRoot"
Set-Location $ProjectRoot

# ================================================
# Step 1: Check Requirements
# ================================================
Write-Host ""
Write-Info "[1/5] Checking system requirements..."

# Check if Git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Info "Git: $gitVersion"
} catch {
    Write-Error "Git is not installed. Please install Git first."
    Write-Host "Download from: https://git-scm.com/download/win"
    exit 1
}

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Info "Python: $pythonVersion"
} catch {
    Write-Error "Python is not installed. Please install Python 3.11+ first."
    Write-Host "Download from: https://www.python.org/downloads/"
    exit 1
}

Write-Success "System check passed"

# ================================================
# Step 2: Install uv (Python package manager)
# ================================================
Write-Host ""
Write-Info "[2/5] Setting up uv package manager..."

$uvInstalled = $false
try {
    $uvVersion = uv --version 2>&1
    Write-Info "uv already installed: $uvVersion"
    $uvInstalled = $true
} catch {
    Write-Info "uv not found, installing..."
}

if (-not $uvInstalled) {
    try {
        Write-Info "Installing uv via PowerShell..."
        irm https://astral.sh/uv/install.ps1 | iex

        # Refresh PATH
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path", "User")

        # Also add common uv installation path
        $uvPath = "$env:USERPROFILE\.cargo\bin"
        if (Test-Path $uvPath) {
            $env:Path = "$uvPath;$env:Path"
        }

        # Alternative path for uv
        $uvPathAlt = "$env:LOCALAPPDATA\uv\bin"
        if (Test-Path $uvPathAlt) {
            $env:Path = "$uvPathAlt;$env:Path"
        }

        Write-Success "uv installed successfully"
    } catch {
        Write-Warning "Failed to install uv automatically."
        Write-Host "Please install uv manually:"
        Write-Host "  Option 1: pip install uv"
        Write-Host "  Option 2: winget install --id=astral-sh.uv -e"
        Write-Host "  Option 3: Visit https://docs.astral.sh/uv/getting-started/installation/"

        # Try pip as fallback
        Write-Info "Attempting to install uv via pip..."
        try {
            pip install uv
            Write-Success "uv installed via pip"
        } catch {
            Write-Error "Could not install uv. Please install it manually and re-run this script."
            exit 1
        }
    }
}

# ================================================
# Step 3: Create Virtual Environment
# ================================================
Write-Host ""
Write-Info "[3/5] Creating Python virtual environment..."

$venvPath = Join-Path $ProjectRoot ".venv"

if (Test-Path $venvPath) {
    Write-Info "Virtual environment already exists at: $venvPath"
} else {
    Write-Info "Creating virtual environment with Python 3.11..."
    try {
        uv venv --python 3.11 .venv
        Write-Success "Virtual environment created"
    } catch {
        Write-Warning "Failed with Python 3.11, trying default Python..."
        try {
            uv venv .venv
            Write-Success "Virtual environment created with default Python"
        } catch {
            Write-Error "Failed to create virtual environment"
            exit 1
        }
    }
}

# ================================================
# Step 4: Activate venv and Install Dependencies
# ================================================
Write-Host ""
Write-Info "[4/5] Installing dependencies..."

# Activate virtual environment
$activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Info "Activating virtual environment..."
    . $activateScript
} else {
    Write-Error "Virtual environment activation script not found: $activateScript"
    exit 1
}

# Check for requirements.txt
$requirementsFile = Join-Path $ProjectRoot "requirements.txt"
if (Test-Path $requirementsFile) {
    Write-Info "Installing packages from requirements.txt..."
    uv pip install -r $requirementsFile
    Write-Success "Dependencies installed"
} else {
    Write-Warning "requirements.txt not found. Installing common dependencies..."

    # Install common dependencies for this project
    $commonPackages = @(
        "python-dotenv",
        "smolagents",
        "openai",
        "gradio",
        "pyyaml",
        "pandas",
        "openpyxl",
        "requests"
    )

    foreach ($pkg in $commonPackages) {
        Write-Info "Installing $pkg..."
        try {
            uv pip install $pkg
        } catch {
            Write-Warning "Failed to install $pkg, continuing..."
        }
    }
    Write-Success "Common dependencies installed"
}

# ================================================
# Step 5: Generate .env Configuration
# ================================================
Write-Host ""
Write-Info "[5/5] Generating configuration files..."

$envFile = Join-Path $ProjectRoot ".env"
$envBackup = Join-Path $ProjectRoot ".env.backup"

if (Test-Path $envFile) {
    Write-Info ".env file already exists, overwriting"
    Write-Info "Backing up current configuration file to .env.backup"
    Copy-Item $envFile $envBackup -Force
}

# Generate .env file
$defaultCds = "$env:USERPROFILE\TSMC28\TEST\cds.lib"
$defaultCds180 = "$env:USERPROFILE\TSMC180\TEST\cds.lib"

$envContent = @"
# ================================================
# AMS-IO-Agent Environment Configuration
# Auto-generated by setup_powershell.ps1 (Windows)
# ================================================

# ================================================
# MODEL CONFIGURATION
# ================================================
# To add a model, configure these three variables:
#   MODELNAME_API_BASE=https://api.provider.com/v1
#   MODELNAME_MODEL_ID=model-id
#   MODELNAME_API_KEY=your_api_key_here
#
# Example: DeepSeek (default, uncomment to use)

# DeepSeek
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL_ID=deepseek-chat
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Virtuoso Bridge Selection (true/1/yes to enable RAMIC Bridge, otherwise use skillbridge)
USE_RAMIC_BRIDGE=true

# RAMIC Bridge Connection (only used when RAMIC Bridge is enabled)
RB_HOST=127.0.0.1
RB_PORT=65432

# CDS Library Paths (Modify these paths according to your environment)
CDS_LIB_PATH=$defaultCds
CDS_LIB_PATH_180=$defaultCds180

# Logging Configuration
ENABLE_LOGGING=true
LOG_LEVEL=INFO

# User Profile Configuration
# Path to user profile markdown file (relative to project root)
USER_PROFILE_PATH=user_data/default_user_profile.md
# Set to empty or 'none' to disable user profile loading
# USER_PROFILE_PATH=
"@

Set-Content -Path $envFile -Value $envContent -Encoding UTF8
Write-Success ".env configuration file generated"

# ================================================
# Create necessary directories
# ================================================
$directories = @(
    "logs",
    "user_data",
    "user_prompt"
)

foreach ($dir in $directories) {
    $dirPath = Join-Path $ProjectRoot $dir
    if (-not (Test-Path $dirPath)) {
        New-Item -ItemType Directory -Path $dirPath -Force | Out-Null
        Write-Info "Created directory: $dir"
    }
}

# ================================================
# Completion Summary
# ================================================
Write-Host ""
Write-Host "=================================" -ForegroundColor Green
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

Write-Success "Configuration completed:"
Write-Host "  [OK] Python virtual environment (.venv)" -ForegroundColor Green
Write-Host "  [OK] Dependencies installed" -ForegroundColor Green
Write-Host "  [OK] .env configuration file" -ForegroundColor Green
Write-Host "  [OK] Required directories" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Edit .env file and fill in your API keys:" -ForegroundColor White
Write-Host "     - DEEPSEEK_API_KEY" -ForegroundColor Gray
Write-Host "     - WANDOU_API_KEY" -ForegroundColor Gray
Write-Host "     - OPENAI_API_KEY (if using OpenAI)" -ForegroundColor Gray
Write-Host ""
Write-Host "  2. Activate virtual environment:" -ForegroundColor White
Write-Host "     .\.venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Run the application:" -ForegroundColor White
Write-Host "     python main.py" -ForegroundColor Cyan
Write-Host ""

Write-Host "Note: Virtuoso integration is only available on Linux." -ForegroundColor Yellow
Write-Host "This Windows setup is for development and testing purposes." -ForegroundColor Yellow
Write-Host ""
