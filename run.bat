@echo off
REM run-main-debug.bat — saves output to run.log and pauses so you can read it
cd /d "%~dp0"

set "SCRIPT=%~dp0main.py"
set "WINPY=%~dp0portable_python\WPy64-39100\python-3.9.10.amd64\python.exe"
set "VENV_PY=%~dp0venv\Scripts\python.exe"

echo ==== Debug launcher ====
echo Script: "%SCRIPT%"
echo.

if exist "%WINPY%" (
  echo Using WinPython: "%WINPY%"
  "%WINPY%" -V
  echo.
  echo Running script and saving output to run.log...
  "%WINPY%" "%SCRIPT%" %* > "%~dp0run.log" 2>&1
  echo.
  echo Exit code: %ERRORLEVEL%
  echo.
  echo ----- run.log -----
  type "%~dp0run.log"
  echo -------------------
  goto :pause
)

if exist "%VENV_PY%" (
  echo Using venv python: "%VENV_PY%"
  "%VENV_PY%" -V
  echo.
  echo Running script and saving output to run.log...
  "%VENV_PY%" "%SCRIPT%" %* > "%~dp0run.log" 2>&1
  echo.
  echo Exit code: %ERRORLEVEL%
  echo.
  echo ----- run.log -----
  type "%~dp0run.log"
  echo -------------------
  goto :pause
)

echo No bundled WinPython or venv python found.
where py >nul 2>nul
if %ERRORLEVEL%==0 (
  echo Using py launcher
  py -3 -V
  py -3 "%SCRIPT%" %* > "%~dp0run.log" 2>&1
  echo Exit code: %ERRORLEVEL%
  echo.
  type "%~dp0run.log"
  goto :pause
)

where python >nul 2>nul
if %ERRORLEVEL%==0 (
  echo Using python from PATH
  python -V
  python "%SCRIPT%" %* > "%~dp0run.log" 2>&1
  echo Exit code: %ERRORLEVEL%
  echo.
  type "%~dp0run.log"
  goto :pause
)

echo ERROR: No python interpreter found.
echo - Put WinPython at portable_python\WPy64-39100 or recreate venv with --copies.
echo.

:pause
pause
