@echo off
REM ========================================
REM RLE Monitoring Lab - One-Click Launcher
REM ========================================
REM
REM This script does everything:
REM   1. Checks Python is installed
REM   2. Installs dependencies
REM   3. Starts the monitor
REM   4. Starts the Streamlit dashboard
REM   5. Shows where CSV is being saved
REM
REM Just double-click to start!
REM ========================================

setlocal enabledelayedexpansion

title RLE Monitoring Lab Launcher

echo.
echo ========================================
echo   RLE Monitoring Lab - Starting...
echo ========================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found!
    echo   Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)
python --version
echo   OK: Python found!
echo.

REM Step 2: Install dependencies
echo [2/5] Installing dependencies...
echo   This may take a minute the first time...
pip install -q -r lab/requirements_lab.txt --disable-pip-version-check
if errorlevel 1 (
    echo   WARNING: Some dependencies may not have installed correctly
    echo   Continuing anyway...
) else (
    echo   OK: Dependencies installed!
)
echo.

REM Step 3: Create directories if needed
echo [3/5] Setting up directories...
if not exist "lab\sessions\recent" mkdir "lab\sessions\recent"
if not exist "validation_logs" mkdir "validation_logs"
echo   OK: Directories ready!
echo.

REM Step 4: Start monitor
echo [4/5] Starting hardware monitor...
echo   Monitor will write to: lab\sessions\recent\rle_YYYYMMDD_HH.csv
start "RLE Monitor" /MIN cmd /c "cd lab && python start_monitor.py --mode gpu --sample-hz 1 && pause"
timeout /t 3 /nobreak >nul
echo   OK: Monitor started!
echo.

REM Step 5: Start dashboard
echo [5/5] Starting Streamlit dashboard...
echo   Dashboard will open in your browser at http://localhost:8501
start "RLE Dashboard" cmd /c "cd lab\monitoring && streamlit run rle_streamlit.py --server.headless=false && pause"
echo   OK: Dashboard starting!
echo.

REM Show user what's happening
echo ========================================
echo   RLE Monitoring is NOW RUNNING!
echo ========================================
echo.
echo   Monitor Window:  (running in background)
echo   Dashboard:       (browser should open automatically)
echo   CSV Output:      lab\sessions\recent\rle_YYYYMMDD_HH.csv
echo.
echo   To stop:
echo     1. Close the browser tab (dashboard)
echo     2. Check taskbar for "RLE Monitor" window
echo     3. Close that window to stop the monitor
echo.
echo   Analyzing your session later:
echo     python lab\analyze_session.py
echo.
echo ========================================
echo.

REM Keep this window open so user can see status
echo Press any key to close this launcher window (monitoring continues)...
pause >nul
exit

