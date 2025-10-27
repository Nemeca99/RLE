@echo off
REM ========================================
REM RLE Test Session - Automated Workload Tests
REM ========================================
REM
REM Runs a sequence of GPU workloads to generate data for RLE refinement
REM

title RLE Test Session

echo.
echo ========================================
echo   RLE GPU Test Workload Session
echo ========================================
echo.

REM Check if monitor is already running
tasklist | find /i "python" >nul
if %errorlevel% == 0 (
    echo   Note: Python process detected (monitor likely running)
    echo.
) else (
    echo   WARNING: Monitor doesn't seem to be running!
    echo   Start the monitor first with: start_monitor_simple.bat
    echo.
    pause
    exit /b 1
)

echo   This will run 3 workload patterns (15 minutes total)
echo.
echo   Workload 1/3: Steady load (85-95% GPU, 5 min)
echo   Workload 2/3: Bursty load (40-100% GPU, 5 min)  
echo   Workload 3/3: Ramp-up load (50-95% GPU, 5 min)
echo.
pause

cd lab\stress

echo.
echo   [1/3] Starting steady load test...
python ai_sim_load.py --duration 5 --pattern steady

echo.
echo   Waiting 30 seconds between tests...
timeout /t 30 /nobreak >nul

echo.
echo   [2/3] Starting bursty load test...
python ai_sim_load.py --duration 5 --pattern bursty

echo.
echo   Waiting 30 seconds between tests...
timeout /t 30 /nobreak >nul

echo.
echo   [3/3] Starting ramp-up test...
python ai_sim_load.py --duration 5 --pattern ramp

echo.
echo ========================================
echo   Test session complete!
echo ========================================
echo.
echo   Next steps:
echo   1. Stop the monitor (Ctrl+C in its window)
echo   2. Analyze: python lab\analyze_session.py sessions\recent\LATEST.csv
echo   3. Check collapse rate (should be <5%)
echo.
pause

