## RLE Portable (Windows)

Purpose: run RLE on any Windows laptop/PC without global installs. Everything stays local to this folder.

What you get:
- Local Python virtual environment (auto-created)
- Lightweight dependencies only (no heavy GUI libs beyond Streamlit/Plotly)
- Safe CPU-first defaults; GPU is optional and gracefully handled

Quick start
1) Double‑click `RUN_PORTABLE.bat`
2) Wait for deps to install (first run only)
3) The monitor + dashboard will start

Fast validation (baseline + test)
- Double‑click `QUICK_TEST.bat`: performs hardware scan, 60s idle baseline, then 120s test

Notes for older laptops
- GPU optional: NVML missing is OK; CPU metrics still work
- If Streamlit doesn’t open automatically, browse to: http://localhost:8501

Artifacts
- CSV logs: `lab/sessions/recent/` (baseline and test are separated via `--notes` field)
- Reports: `lab/sessions/recent/REPORT_*.txt`
- Hardware snapshot: `lab/portable/hardware_snapshot.json`

Troubleshooting
- “python not found”: Install Python 3.10+ or install `pylauncher`; or edit `.bat` to point to your Python
- Port in use: If 8501 is busy, Streamlit will choose the next port; check the console output
- Slow first run: Dependency install happens once; subsequent runs are fast


