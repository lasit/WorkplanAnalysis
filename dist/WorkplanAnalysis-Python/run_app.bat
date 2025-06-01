@echo off
echo Starting Workplan Analysis...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Make sure you have run install.bat first
    pause
)
