@echo off
REM Workplan Analysis - Dependency Installation Script
REM This script installs all required Python dependencies

echo Workplan Analysis - Dependency Installation
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.9 or later from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

REM Install dependencies
echo Installing required dependencies...
echo This may take a few minutes...
echo.

python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo Error: Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
) else (
    echo.
    echo Success! All dependencies have been installed.
    echo You can now run the application using start_app.bat
    echo.
)

pause
