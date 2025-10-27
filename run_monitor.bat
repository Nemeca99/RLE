@echo off
REM RLE Monitor - Direct Python launcher
REM Uses absolute path to avoid PATH issues

set PYTHON_PATH=C:\Users\nemec\AppData\Local\Programs\Python\Python311\python.exe

echo Starting RLE Monitor...
echo.

cd lab
"%PYTHON_PATH%" start_monitor.py --mode gpu --sample-hz 1

pause

