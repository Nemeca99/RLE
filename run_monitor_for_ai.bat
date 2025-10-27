@echo off
REM ========================================
REM RLE Monitor for AI Workloads
REM ========================================
REM
REM This starts the monitor, then you can:
REM   - Run LM Studio (load a model, generate text)
REM   - Or run the AI stress test: python lab\stress\ai_sim_load.py
REM
REM The monitor will capture all GPU usage automatically
REM

title RLE Monitor - AI Workload Session

echo.
echo ========================================
echo   RLE Monitor for AI/AI Workloads
echo ========================================
echo.
echo Starting monitor...
echo.

REM Start monitor in a separate window so user can see progress
start "RLE Monitor" cmd /c "cd /d %~dp0lab && C:\Users\nemec\AppData\Local\Programs\Python\Python311\python.exe start_monitor.py --mode gpu --sample-hz 1 && pause"

timeout /t 3 /nobreak >nul

echo.
echo Monitor is now running!
echo.
echo What to do next:
echo.
echo Option 1 - Use LM Studio:
echo   1. Open LM Studio
echo   2. Load a model (any size)
echo   3. Generate some text - this will load the GPU
echo   4. The monitor is capturing everything
echo.
echo Option 2 - Synthetic AI Load:
echo   Run: python lab\stress\ai_sim_load.py --duration 30
echo   This simulates AI workload without needing LM Studio
echo.
echo When done:
echo   Press Ctrl+C in the monitor window to stop
echo   A REPORT_rle_YYYYMMDD_HH.txt will be generated automatically
echo.
echo ========================================
echo.

pause

