#!/bin/bash

# Workplan Analysis - Application Launcher
# This script starts the Workplan Analysis application

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the application directory
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "Error: Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    read -p "Press any key to exit..."
    exit 1
fi

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
elif [ -d ".venv" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
fi

# Check if requirements are installed
echo "Checking dependencies..."
$PYTHON_CMD -c "import PyQt6" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required dependencies..."
    $PYTHON_CMD -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies"
        echo "Please run: pip install -r requirements.txt"
        read -p "Press any key to exit..."
        exit 1
    fi
fi

# Start the application
echo "Starting Workplan Analysis..."
$PYTHON_CMD main.py

# Keep terminal open if there was an error
if [ $? -ne 0 ]; then
    echo "Application exited with an error"
    read -p "Press any key to exit..."
fi
