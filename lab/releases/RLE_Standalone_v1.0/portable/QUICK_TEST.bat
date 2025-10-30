@echo off
setlocal ENABLEDELAYEDEXPANSION

REM 60s baseline (idle) + 120s test, with hardware scan

pushd %~dp0\..\..

where py >nul 2>nul && set PYCMD=py -3 || set PYCMD=python

if not exist venv (
  %PYCMD% -m venv venv || (echo Failed to create venv & pause & exit /b 1)
)

venv\Scripts\pip.exe install -r lab\requirements_lab.txt >nul 2>nul

echo [RLE] Scanning hardware...
venv\Scripts\python.exe lab\portable\hw_scan.py

echo [RLE] Collecting 60s idle baseline...
venv\Scripts\python.exe lab\start_monitor.py --mode cpu --sample-hz 1 --duration 60 --notes baseline

echo [RLE] Running 120s test session...
venv\Scripts\python.exe lab\start_monitor.py --mode cpu --sample-hz 1 --duration 120 --notes test

echo.
echo [RLE] Done. Check CSVs in lab\sessions\recent\ and hardware_snapshot.json in lab\portable\
pause

popd
endlocal


