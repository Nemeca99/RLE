#!/usr/bin/env python3
"""
Create clean lab structure without moving Magic folder files
"""
import os
import shutil
from pathlib import Path

BASE = Path(".")
LAB = BASE / "lab"

def setup():
    print("RLE Monitoring Lab Setup")
    print("=" * 50)
    
    # Create lab structure
    dirs = {
        "monitoring": "Background monitoring daemons",
        "analysis": "Post-session analysis & plotting",
        "sessions": {
            "recent": "Current session data (CSV logs)",
            "archive": "Historical sessions"
        },
        "scripts": "Helper scripts"
    }
    
    print("\nCreating structure...")
    for name, desc in dirs.items():
        path = LAB / name
        if isinstance(desc, dict):
            path.mkdir(parents=True, exist_ok=True)
            for sub, subdesc in desc.items():
                (path / sub).mkdir(parents=True, exist_ok=True)
                print(f"  ✓ {path/sub} - {subdesc}")
        else:
            path.mkdir(parents=True, exist_ok=True)
            print(f"  ✓ {path} - {desc}")
    
    # Copy essential files
    print("\nOrganizing files...")
    
    essential = [
        ("hardware_monitor.py", "monitoring"),
        ("tag_events.ahk", "monitoring"),
        ("README_monitor.md", "monitoring"),
    ]
    
    for src, dst in essential:
        if (BASE / src).exists():
            shutil.copy2(BASE / src, LAB / dst / src)
            print(f"  ✓ {src} → lab/{dst}/")
    
    # Move session logs
    if (BASE / "logs").exists():
        if list((BASE / "logs").glob("*.csv")):
            for csv in (BASE / "logs").glob("*.csv"):
                shutil.copy2(csv, LAB / "sessions" / "recent" / csv.name)
            print(f"  ✓ logs/*.csv → lab/sessions/recent/")
    
    # Create entry scripts
    print("\nCreating entry scripts...")
    
    (LAB / "start_monitor.py").write_text('''#!/usr/bin/env python3
"""Start RLE monitor daemon"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from monitoring.hardware_monitor import monitor, parse_args
import argparse

if __name__ == "__main__":
    args = parse_args()
    monitor(args)
''')
    
    (LAB / "analyze_session.py").write_text('''#!/usr/bin/env python3
"""Analyze a session CSV"""
import sys
import pandas as pd
from pathlib import Path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_session.py <session.csv>")
        sys.exit(1)
    
    csv = Path(sys.argv[1])
    if not csv.exists():
        print(f"Error: {csv} not found")
        sys.exit(1)
    
    df = pd.read_csv(csv)
    print(f"\\nSession: {csv.name}")
    print(f"  Samples: {len(df)}")
    print(f"  Max Power: {df['power_w'].max():.1f}W")
    print(f"  Max Temp: {df['temp_c'].max():.1f}°C")
    print(f"  Collapse Events: {df['collapse'].sum()}")
''')
    
    # Create main README
    (LAB / "README.md").write_text('''# RLE Monitoring Lab

Hardware efficiency monitoring for GPU/CPU systems.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install psutil nvidia-ml-py3 pandas
   ```

2. **Start monitoring:**
   ```bash
   cd lab
   python start_monitor.py --mode gpu --sample-hz 1
   ```

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
''')
    
    print("  ✓ start_monitor.py")
    print("  ✓ analyze_session.py")
    print("  ✓ README.md")
    
    print("\n✓ Lab setup complete!")
    print("\nRun: cd lab && python start_monitor.py --mode gpu")

if __name__ == "__main__":
    setup()

