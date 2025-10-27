#!/usr/bin/env python3
"""
Kia - RLE Monitoring Lab Validation Script
Validates the RLE formula and collapse detection logic

Usage: python kia_validate.py [session.csv]
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import deque

def compute_stability(util_history):
    """Compute stability from utilization history"""
    if len(util_history) < 5:
        return 1.0 / (1.0 + 0.0)  # No variation
    stddev = np.std(util_history)
    return 1.0 / (1.0 + stddev)

def recompute_rle(util_pct, a_load, t_sustain):
    """Recompute RLE using the documented formula"""
    if t_sustain <= 0:
        t_sustain = 0.1  # Avoid division by zero
    stability = 1.0  # Simplified for single sample
    denominator = a_load * (1.0 + 1.0 / t_sustain)
    rle = (util_pct / 100.0 * stability) / denominator
    return rle

def validate_rle_formula(csv_path):
    """Validate RLE formula by recomputing for sample rows"""
    print("=" * 70)
    print("Kia Validation: RLE Formula Check")
    print("=" * 70)
    print(f"Analyzing: {csv_path.name}\n")
    
    df = pd.read_csv(csv_path)
    
    # Test first 10 rows
    print("Testing RLE recomputation (first 10 rows):")
    print("-" * 70)
    print(f"{'Row':<6} {'util%':<8} {'a_load':<8} {'t_sus':<8} {'Logged RLE':<12} {'Recalc':<12} {'Match':<6}")
    print("-" * 70)
    
    util_window = deque(maxlen=5)
    matches = 0
    total = 0
    
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        util_pct = row['util_pct']
        a_load = row['a_load']
        t_sustain = row['t_sustain_s']
        logged_rle = row['rle_raw']
        
        util_window.append(util_pct)
        stability = compute_stability(list(util_window))
        
        # Recompute RLE with window-based stability
        denominator = a_load * (1.0 + 1.0 / max(t_sustain, 0.1))
        recalc_rle = (util_pct / 100.0 * stability) / denominator
        
        diff = abs(logged_rle - recalc_rle)
        match = "✓" if diff < 0.01 else "✗"
        
        if diff < 0.01:
            matches += 1
        total += 1
        
        print(f"{i+1:<6} {util_pct:<8.1f} {a_load:<8.3f} {t_sustain:<8.1f} "
              f"{logged_rle:<12.6f} {recalc_rle:<12.6f} {match:<6}")
    
    print("-" * 70)
    print(f"\nMatch rate: {matches}/{total} ({matches/total*100:.1f}%)")
    
    if matches == total:
        print("✅ RLE formula validation: PASSED")
        print("   All recalculations match logged values")
    else:
        print(f"⚠️  RLE formula validation: {matches/total*100:.1f}% match")
        print("   Some discrepancies detected (may be due to windowing)")
    
    # Check for missing columns
    print("\n" + "=" * 70)
    print("CSV Schema Check:")
    print("-" * 70)
    required_cols = [
        'timestamp', 'device', 'rle_smoothed', 'rle_raw', 'temp_c',
        'power_w', 'util_pct', 'a_load', 't_sustain_s', 'collapse'
    ]
    
    missing = []
    for col in required_cols:
        if col not in df.columns:
            missing.append(col)
        else:
            print(f"✓ {col}")
    
    if missing:
        print(f"\n✗ Missing columns: {', '.join(missing)}")
    else:
        print("\n✅ All required columns present")
    
    # Summary stats
    print("\n" + "=" * 70)
    print("Summary Statistics:")
    print("-" * 70)
    print(f"Rows: {len(df)}")
    print(f"Duration: {(pd.to_datetime(df.iloc[-1]['timestamp']) - pd.to_datetime(df.iloc[0]['timestamp'])).total_seconds() / 60:.1f} min")
    print(f"Max RLE: {df['rle_smoothed'].max():.4f}")
    print(f"Mean RLE: {df['rle_smoothed'].mean():.4f}")
    print(f"Collapse events: {df['collapse'].sum()}")
    print(f"Collapse rate: {df['collapse'].sum() / len(df) * 100:.1f}%")
    print(f"Max temp: {df['temp_c'].max():.1f}°C")
    print(f"Max power: {df['power_w'].max():.1f}W")
    
    print("\n" + "=" * 70)
    print("Validation complete!")
    print("=" * 70)
    
    return matches == total

def main():
    if len(sys.argv) < 2:
        # Find latest CSV
        sessions = Path(__file__).parent / "lab" / "sessions" / "recent"
        if sessions.exists():
            csvs = sorted(sessions.glob("rle_*.csv"), reverse=True)
            if csvs:
                print(f"No file specified, using latest: {csvs[0].name}\n")
                return validate_rle_formula(csvs[0])
        
        print("Usage: python kia_validate.py <session.csv>")
        print("\nOr place a session CSV in lab/sessions/recent/ to auto-validate latest")
        return 1
    
    csv_path = Path(sys.argv[1])
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return 1
    
    success = validate_rle_formula(csv_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())

