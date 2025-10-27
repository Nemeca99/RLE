@echo off
REM Batch script to safely run magic_gpu.py overnight in PowerShell, looping forever with small batch sizes
REM This script is designed to be run outside of VS Code for maximum stability

REM Change to the script directory
cd /d %~dp0

REM Launch PowerShell and run the PowerShell overnight script
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "run_magic_gpu_overnight.ps1"

REM Pause at the end so you can see any final messages
pause
