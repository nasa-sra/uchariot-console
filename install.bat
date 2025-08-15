@echo off
REM Get the folder where this .bat file is located
set "BASE_DIR=%~dp0"

REM Run pip install using the portable Python executable
"%BASE_DIR%portable_python\WPy64-39100\python-3.9.10.amd64\python.exe" -m pip install -r "%BASE_DIR%requirements.txt"

echo.
pause
