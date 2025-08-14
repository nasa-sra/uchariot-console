@echo off
REM Go to the directory of this script (USB root)
cd /d %~dp0

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python main.py

REM Pause so the console stays open if run by double-click
pause
