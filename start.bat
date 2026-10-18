@echo off
setlocal
cd /d "%~dp0"
py -3 -c "import sys" >nul 2>&1
if not errorlevel 1 (
    py -3 -m multiclick
) else (
    python -m multiclick
)
if errorlevel 1 (
    echo.
    echo Install Python 3 with Tcl/Tk support from python.org, then try again.
    pause
)
