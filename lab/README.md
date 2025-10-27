# RLE Monitoring Lab

Hardware efficiency monitoring for GPU/CPU systems.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install psutil nvidia-ml-py3 pandas streamlit plotly
   # Or:
   pip install -r requirements_lab.txt
   ```

2. **Start monitoring (choose one):**

   **Option A - Monitoring only:**
   ```bash
   cd lab
   python start_monitor.py --mode gpu --sample-hz 1
   ```

   **Option B - Full suite (monitor + real-time graphs):**
   ```bash
   cd lab
   start_monitoring_suite.bat
   ```
   Opens two windows:
   - Terminal: Background logging
   - Browser: Live Streamlit dashboard

3. **Analyze session:**
   ```bash
   python analyze_session.py sessions/recent/rle_YYYYMMDD_HH.csv
   ```

## Structure

- `monitoring/` - Background daemons (hardware_monitor.py)
- `analysis/` - Post-session analysis tools
- `sessions/recent/` - Current session CSVs
- `sessions/archive/` - Historical data

## Features

- Rolling peak detection with decay
- Hysteresis-based collapse detection
- Thermal & power evidence requirements
- Split E_th/E_pw components for diagnosis
- Rotating hourly CSV logs

## Documentation

See `monitoring/README_monitor.md` for detailed usage.
