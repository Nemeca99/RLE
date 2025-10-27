@echo off
REM ========================================
REM RLE Monitor + LM Studio
REM ========================================
REM
REM This runs the monitor while you use LM Studio
REM Just open LM Studio and load a model - the monitor will capture the GPU usage
REM

echo.
echo Starting RLE Monitor for LM Studio session...
echo.
echo Usage:
echo   1. This monitor will capture GPU usage
echo   2. Open LM Studio in another window
echo   3. Load a model and generate text
echo   4. Watch the GPU usage get logged
echo   5. Press Ctrl+C here when done
echo.

REM Start the monitor
cd lab
C:\Users\nemec\AppData\Local\Programs\Python\Python311\python.exe start_monitor.py --mode gpu --sample-hz 1

pause

