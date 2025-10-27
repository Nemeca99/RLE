#!/usr/bin/env python3
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
    print(f"\nSession: {csv.name}")
    print(f"  Samples: {len(df)}")
    print(f"  Max Power: {df['power_w'].max():.1f}W")
    print(f"  Max Temp: {df['temp_c'].max():.1f}°C")
    print(f"  Collapse Events: {df['collapse'].sum()}")
