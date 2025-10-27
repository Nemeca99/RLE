@echo off
REM Simple monitor launcher - terminal only
cd lab
..\venv\Scripts\python.exe start_monitor.py --mode gpu --sample-hz 1
pause
