@echo off
REM RLE Full Suite - Monitor + Dashboard
REM Uses absolute path to avoid PATH issues

set PYTHON_PATH=C:\Users\nemec\AppData\Local\Programs\Python\Python311\python.exe

echo ========================================
echo   RLE Monitoring Suite
echo ========================================
echo.

echo [1/2] Starting monitor...
start "RLE Monitor" cmd /c "cd /d %~dp0lab && %PYTHON_PATH% start_monitor.py --mode gpu --sample-hz 1 && pause"
timeout /t 3 /nobreak >nul

echo [2/2] Starting dashboard...
start "RLE Dashboard" cmd /k "cd /d %~dp0lab\monitoring && %PYTHON_PATH% -m streamlit run rle_streamlit.py --server.headless=false"

echo.
echo ========================================
echo   Both windows should be open now!
echo   - Terminal: Monitor (logging)
echo   - Browser: Dashboard (graphs)
echo.
echo Press any key to close this window...
pause >nul

