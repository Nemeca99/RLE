@echo off
REM Run 30-minute sustained CPU stress test with monitoring

echo ======================================================================
echo RLE STRESS TEST - 30-MINUTE SUSTAINED LOAD
echo ======================================================================
echo.
echo This will:
echo   1. Start monitoring (both CPU and GPU)
echo   2. Run 30-minute 100%% CPU stress test
echo   3. Capture collapse events for model validation
echo.
echo WARNING: This will push your CPU to thermal limits!
echo Monitor temperatures closely. Make sure cooling is adequate.
echo.
pause

REM Start monitor in background
echo Starting monitoring daemon...
start /B cmd /c "venv\Scripts\python.exe start_monitor.py --mode both --sample-hz 1"

REM Wait for monitor to initialize
timeout /t 5 /nobreak

REM Run stress test
echo.
echo ======================================================================
echo STARTING STRESS TEST
echo ======================================================================
echo.
venv\Scripts\python.exe stress\max_sustained_load.py --duration 30 --threads 8

echo.
echo ======================================================================
echo STRESS TEST COMPLETE
echo ======================================================================
echo.
echo Data saved to: sessions\recent\rle_*.csv
echo.
echo Next: Analyze the data with collapse detector
echo    python analysis\analyze_collapses.py sessions\recent\rle_*.csv
echo.

REM Kill monitor
taskkill /F /FI "WINDOWTITLE eq start_monitor.py*" >nul 2>&1

pause

