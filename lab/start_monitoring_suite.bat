@echo off
REM RLE Monitoring Suite - Starts monitor + Streamlit visualization
echo ========================================
echo  RLE Monitoring Suite
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "monitoring\hardware_monitor.py" (
    echo Error: Run this from lab\ directory
    pause
    exit /b 1
)

echo [1/2] Starting hardware monitor...
start "RLE Monitor" cmd /c "py start_monitor.py --mode gpu --sample-hz 1"
timeout /t 3 /nobreak >nul

echo [2/2] Starting Streamlit visualization...
start "RLE Streamlit" cmd /k "cd monitoring && py -m streamlit run rle_streamlit.py --server.headless=false"

echo.
echo ========================================
echo  Both windows should be open now!
echo.
echo  - Terminal: Hardware monitor (logging)
echo  - Browser: Real-time graphs
echo.
echo  Press any key to exit this launcher...
echo ========================================
pause >nul

