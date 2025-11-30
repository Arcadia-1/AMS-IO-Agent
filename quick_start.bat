@echo off
REM Quick Start Script for AMS-IO-Agent (Windows CMD)
REM This script automatically checks and runs the setup process
REM Usage: quick_start.bat

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ========================================
echo   AMS-IO-Agent Quick Start
echo ========================================
echo.

REM Step 1: Check setup scripts
echo [1/3] Checking setup scripts...
if not exist "setup\setup_cmd.bat" (
    echo [ERROR] setup\setup_cmd.bat not found
    exit /b 1
)
echo [SUCCESS] Setup scripts found
echo.

REM Step 2: Check if setup has already been run
if exist ".venv" if exist ".env" (
    echo [2/3] Setup already completed
    echo [SUCCESS] Virtual environment exists
    echo [SUCCESS] Configuration file (.env) exists
    echo.
    echo Note: If you want to re-run setup, delete .venv and .env first
    echo.
    
    REM Ask if user wants to continue anyway
    set /p answer="Do you want to run setup again? (y/N): "
    if /i not "!answer!"=="y" (
        echo.
        echo Setup skipped. You can now:
        echo   .venv\Scripts\activate.bat  # Activate virtual environment
        echo   python main.py               # Start the agent
        exit /b 0
    )
    echo.
)

REM Step 3: Run the actual setup script
echo [3/3] Running setup script...
echo.

REM Execute the setup script
call "setup\setup_cmd.bat"
set SETUP_EXIT_CODE=%ERRORLEVEL%

if %SETUP_EXIT_CODE% equ 0 (
    REM Setup script already displays next steps, no need to repeat here
    exit /b 0
) else (
    echo.
    echo ========================================
    echo   Setup Failed (exit code: %SETUP_EXIT_CODE%)
    echo ========================================
    echo.
    echo Please check the error messages above and try again.
    exit /b %SETUP_EXIT_CODE%
)

