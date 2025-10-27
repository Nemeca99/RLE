#!/usr/bin/env python3
"""
Lab setup script for RLE monitoring
Creates proper directory structure and moves files
"""

import os
import shutil
from pathlib import Path

def setup_lab():
    base = Path(".")
    
    # Lab structure
    dirs = {
        "lab/monitoring": "Hardware monitoring daemons",
        "lab/analysis": "Post-session analysis tools",
        "lab/stress": "Stress test generators",
        "lab/sessions": "Raw session data",
        "lab/archive": "Old sessions and historical data"
    }
    
    print("Creating lab structure...")
    for d, desc in dirs.items():
        os.makedirs(d, exist_ok=True)
        print(f"  ✓ {d} - {desc}")
    
    # Move monitoring tools
    print("\nMoving monitoring tools...")
    for f in ["hardware_monitor.py", "tag_events.ahk", "README_monitor.md"]:
        if os.path.exists(f):
            shutil.move(f, f"lab/monitoring/{f}")
            print(f"  ✓ {f}")
    
    # Move session data
    print("\nMoving session data...")
    if os.path.exists("logs"):
        shutil.move("logs", "lab/sessions/recent")
        os.makedirs("lab/sessions/archive", exist_ok=True)
        print("  ✓ logs → lab/sessions/recent")
    
    # Move RLE analysis tools
    print("\nMoving RLE analysis tools...")
    for f in ["rle_real.py", "rle_real_live.py"]:
        if os.path.exists(f):
            shutil.move(f, f"lab/analysis/{f}")
            print(f"  ✓ {f}")
    
    # Move stress tests
    print("\nMoving stress test generators...")
    stress_files = [
        "simple_stress.py", "magic_stress_test.py", "max_stress_test.py",
        "MAX_STRESS.py", "nuclear_stress.py", "run_full_stress.py",
        "stress_cpu.py", "EXTENDED_STRESS.py", "magic_cpu_stress.py",
        "run_magic_stress_with_monitoring.py", "run_nuclear_stress_with_monitoring.py"
    ]
    for f in stress_files:
        if os.path.exists(f):
            shutil.move(f, f"lab/stress/{f}")
            print(f"  ✓ {f}")
    
    # Archive old PNGs
    print("\nArchiving screenshot data...")
    pngs = [f for f in os.listdir(".") if f.startswith("rle_real_live_") or f == "rle_real_simulation.png"]
    if pngs:
        os.makedirs("lab/sessions/archive/screenshots", exist_ok=True)
        for png in pngs:
            shutil.move(png, f"lab/sessions/archive/screenshots/{png}")
            print(f"  ✓ {png}")
    
    # Create entry point script
    print("\nCreating lab entry point...")
    create_entry_point()
    
    print("\n✓ Lab setup complete!")
    print("\nNext steps:")
    print("  cd lab/monitoring")
    print("  python hardware_monitor.py --mode gpu --sample-hz 1")
    
def create_entry_point():
    entry = """#!/usr/bin/env python3
\"\"\"
RLE Monitoring Lab - Quick Start
\"\"\"

import sys
import os

# Add lab paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'monitoring'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analysis'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'stress'))

print("RLE Monitoring Lab")
print("=" * 50)
print("\nQuick commands:")
print("  Start monitor:     cd monitoring && python hardware_monitor.py --mode gpu")
print("  Run analysis:      cd analysis && python rle_real.py")
print("  Generate stress:   cd stress && python simple_stress.py")
print("  View sessions:     ls sessions/recent/")
print("\nDocumentation:")
print("  - monitoring/README_monitor.md")
"""

    with open("lab/LAB_START.py", "w") as f:
        f.write(entry)
    print("  ✓ lab/LAB_START.py")

if __name__ == "__main__":
    setup_lab()

