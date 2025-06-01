@echo off
REM Workplan Analysis - Windows Application Launcher
REM This script starts the Workplan Analysis application on Windows

echo Starting Workplan Analysis...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or later and try again
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if required dependencies are installed
echo Checking dependencies...
python -c "import PyQt6.QtWidgets" >nul 2>&1
if errorlevel 1 (
    echo Installing required dependencies...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Error: Failed to install dependencies
        echo Please run: python -m pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM Start the application
echo.
echo Launching Workplan Analysis GUI...
python main.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error
    pause
)
