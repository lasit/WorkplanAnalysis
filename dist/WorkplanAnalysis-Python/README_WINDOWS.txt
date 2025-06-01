# Workplan Analysis - Python Version

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
