#!/usr/bin/env python3
"""Start RLE monitor daemon"""
import sys
import os
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))

from monitoring.hardware_monitor import monitor, parse_args
import argparse

if __name__ == "__main__":
    args = parse_args()
    
    try:
        monitor(args)
    except KeyboardInterrupt:
        # Generate report on shutdown
        print("\n[Monitor] Generating session report...")
        
        # Find latest CSV
        sessions_dir = Path(__file__).parent / "sessions" / "recent"
        if sessions_dir.exists():
            csvs = sorted(sessions_dir.glob("rle_*.csv"), reverse=True)
            if csvs:
                latest_csv = csvs[0]
                try:
                    from monitoring.generate_report import save_report
                    report_path = save_report(latest_csv)
                    print(f"[Monitor] ✓ Report saved: {report_path}")
                    print("\n" + "="*70)
                    print("To view the report:")
                    print(f"  notepad {report_path}")
                    print("="*70 + "\n")
                except Exception as e:
                    print(f"[Monitor] Could not generate report: {e}")
        raise  # Re-raise to exit properly
