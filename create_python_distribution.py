#!/usr/bin/env python3
"""
Create a Python source distribution for Windows deployment.
This creates a package that can run directly on Windows without building an executable.
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_python_distribution():
    """Create a Python source distribution package."""
    
    print("🚀 Creating Python Source Distribution for Windows")
    print("=" * 50)
    
    # Define distribution directory
    dist_dir = Path("dist/WorkplanAnalysis-Python")
    
    # Clean and create distribution directory
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Files and directories to include
    include_files = [
        "main.py",
        "requirements.txt",
        "README.md",
        "sample_workplan.csv",
        "sample_workplan_small.csv", 
        "sample_workplan_medium.csv",
        "sample_resources.yml",
        "core/",
        "gui/"
    ]
    
    # Copy files to distribution
    copied_files = []
    for item in include_files:
        source_path = Path(item)
        if source_path.exists():
            dest_path = dist_dir / item
            
            if source_path.is_file():
                # Copy file
                dest_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_path, dest_path)
                copied_files.append(item)
                print(f"✅ Copied file: {item}")
            elif source_path.is_dir():
                # Copy directory
                shutil.copytree(source_path, dest_path)
                copied_files.append(item)
                print(f"✅ Copied directory: {item}")
        else:
            print(f"⚠️  Not found: {item}")
    
    # Create Windows installation script
    create_windows_installer(dist_dir)
    
    # Create user instructions
    create_user_instructions(dist_dir)
    
    # Create ZIP package
    create_zip_package(dist_dir)
    
    # Get package size
    total_size = sum(f.stat().st_size for f in dist_dir.rglob('*') if f.is_file())
    size_mb = total_size / (1024 * 1024)
    
    print(f"\n✅ Python distribution created successfully!")
    print(f"📁 Location: {dist_dir}")
    print(f"📊 Size: {size_mb:.1f} MB")
    print(f"📦 ZIP: dist/WorkplanAnalysis-Python.zip")
    print(f"📄 Files included: {len(copied_files)}")
    
    return True

def create_windows_installer(dist_dir):
    """Create Windows installation batch file."""
    
    installer_content = """@echo off
echo Workplan Analysis - Python Installation
echo =======================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo Python found! Installing dependencies...
echo.

REM Install required packages
pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo ✅ Installation completed successfully!
echo.
echo To run the application:
echo   1. Double-click "run_app.bat"
echo   2. OR run: python main.py
echo.
pause
"""
    
    installer_path = dist_dir / "install.bat"
    with open(installer_path, "w") as f:
        f.write(installer_content)
    
    print(f"✅ Created Windows installer: {installer_path.name}")

def create_user_instructions(dist_dir):
    """Create comprehensive user instructions."""
    
    # Create run script
    run_script = """@echo off
echo Starting Workplan Analysis...
python main.py
if errorlevel 1 (
    echo.
    echo ERROR: Failed to start application
    echo Make sure you have run install.bat first
    pause
)
"""
    
    run_path = dist_dir / "run_app.bat"
    with open(run_path, "w") as f:
        f.write(run_script)
    
    # Create detailed instructions
    instructions = """# Workplan Analysis - Python Version

## Quick Start (Windows 11)

### Step 1: Install Python
1. Download Python 3.8 or later from: https://www.python.org/downloads/
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your computer after installation

### Step 2: Install Application
1. Extract this folder to your desired location
2. Double-click `install.bat` to install dependencies
3. Wait for installation to complete

### Step 3: Run Application
- Double-click `run_app.bat` to start the application
- OR open Command Prompt in this folder and run: `python main.py`

## Sample Files Included
- `sample_workplan.csv` - Example workplan data
- `sample_workplan_small.csv` - Smaller example for testing
- `sample_workplan_medium.csv` - Medium-sized example
- `sample_resources.yml` - Example resource configuration

## Getting Started
1. Click "File" → "New Project..." to create a new project
2. Select one of the sample CSV files to get started
3. Configure resources in the "Resources" tab
4. Run analysis from the "Analysis" menu

## Troubleshooting

### "Python is not recognized"
- Python is not installed or not in PATH
- Reinstall Python and check "Add Python to PATH"
- Restart your computer

### "pip is not recognized"
- Usually fixed by reinstalling Python with PATH option
- Or install pip manually

### Application won't start
- Make sure you ran `install.bat` first
- Check that all dependencies installed successfully
- Try running from Command Prompt to see error messages

### Dependencies fail to install
- Check internet connection
- Try running Command Prompt as Administrator
- Update pip: `python -m pip install --upgrade pip`

## System Requirements
- Windows 10 or Windows 11
- Python 3.8 or later
- Internet connection (for initial setup only)
- ~100 MB free disk space

## Advantages of Python Version
- Much smaller download (~50MB vs 646MB for executable)
- Easier to update and modify
- Better compatibility across different Windows versions
- Can see error messages for troubleshooting

## Support
If you encounter issues:
1. Check this README file
2. Ensure Python is properly installed
3. Try running commands manually in Command Prompt
4. Check that all sample files are present

---
*This is the Python source version of Workplan Analysis*
*For the standalone executable version, build on a Windows PC using PyInstaller*
"""
    
    readme_path = dist_dir / "README_WINDOWS.txt"
    with open(readme_path, "w") as f:
        f.write(instructions)
    
    print(f"✅ Created user instructions: {readme_path.name}")
    print(f"✅ Created run script: {run_path.name}")

def create_zip_package(dist_dir):
    """Create ZIP package for easy distribution."""
    
    zip_path = Path("dist/WorkplanAnalysis-Python.zip")
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dist_dir.rglob('*'):
            if file_path.is_file():
                # Create relative path for ZIP
                relative_path = file_path.relative_to(dist_dir.parent)
                zipf.write(file_path, relative_path)
    
    # Get ZIP size
    zip_size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"✅ Created ZIP package: {zip_path} ({zip_size_mb:.1f} MB)")

if __name__ == "__main__":
    create_python_distribution()
