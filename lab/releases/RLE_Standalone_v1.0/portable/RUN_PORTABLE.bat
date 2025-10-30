@echo off
setlocal ENABLEDELAYEDEXPANSION

REM Portable launcher for RLE (Windows)
REM Creates venv locally if missing, installs deps, launches monitor + dashboard

pushd %~dp0\..\..

REM Prefer local Python via py launcher, fallback to python
where py >nul 2>nul && set PYCMD=py -3 || set PYCMD=python

if not exist venv (
  echo [RLE] Creating virtual environment...
  %PYCMD% -m venv venv || (
    echo [RLE] Failed to create venv. Ensure Python 3.10+ is installed.
    pause & exit /b 1
  )
)

echo [RLE] Upgrading pip...
venv\Scripts\python.exe -m pip install --upgrade pip >nul

echo [RLE] Installing requirements (first run may take a minute)...
venv\Scripts\pip.exe install -r lab\requirements_lab.txt || (
  echo [RLE] Requirements install failed.
  pause & exit /b 1
)

echo [RLE] Starting monitor and dashboard...
start "RLE Dashboard" cmd /c "venv\Scripts\python.exe lab\monitoring\rle_streamlit.py"
venv\Scripts\python.exe lab\start_monitor.py --mode cpu --sample-hz 1 --duration 0

popd
endlocal


