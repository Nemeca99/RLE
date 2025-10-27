#!/usr/bin/env python3
"""
Batch analysis of multiple RLE session files
Usage: python batch_analyze.py [directory]
"""

import sys
import pandas as pd
from pathlib import Path
from datetime import datetime

def summarize_session(csv_path):
    """Return summary stats for a session CSV"""
    df = pd.read_csv(csv_path)
    
    start = pd.to_datetime(df.iloc[0]['timestamp'])
    end = pd.to_datetime(df.iloc[-1]['timestamp'])
    duration = (end - start).total_seconds() / 60
    
    return {
        'file': csv_path.name,
        'duration_min': duration,
        'samples': len(df),
        'max_power_w': df['power_w'].max(),
        'mean_power_w': df['power_w'].mean(),
        'max_temp_c': df['temp_c'].max(),
        'mean_temp_c': df['temp_c'].mean(),
        'max_rle': df['rle_smoothed'].max(),
        'mean_rle': df['rle_smoothed'].mean(),
        'collapse_count': int(df['collapse'].sum()),
        'collapse_pct': df['collapse'].sum() / len(df) * 100,
        'alerts': int(df['alerts'].notna().sum()),
        'max_a_load': df['a_load'].max(),
        'mean_util_pct': df['util_pct'].mean(),
    }

def batch_analyze(directory):
    """Analyze all CSVs in a directory"""
    dir_path = Path(directory)
    
    # Find all CSVs
    csvs = sorted(dir_path.glob("rle_*.csv"))
    
    if not csvs:
        print(f"No CSV files found in {directory}")
        return
    
    print("=" * 100)
    print(f"Batch Analysis: {len(csvs)} sessions")
    print(f"Directory: {directory}")
    print("=" * 100)
    
    # Analyze each session
    summaries = []
    for csv in csvs:
        try:
            summary = summarize_session(csv)
            summaries.append(summary)
        except Exception as e:
            print(f"Error analyzing {csv.name}: {e}")
            continue
    
    if not summaries:
        print("No valid sessions found")
        return
    
    # Create comparison DataFrame
    df_summary = pd.DataFrame(summaries)
    
    # Print comparison table
    print("\n📊 Comparison Table")
    print("=" * 100)
    print(f"{'File':<30} {'Duration':<12} {'Max RLE':<10} {'Mean RLE':<10} {'Max Temp':<10} {'Collapse%':<12}")
    print("-" * 100)
    
    for _, row in df_summary.iterrows():
        print(f"{row['file']:<30} {row['duration_min']:>5.1f}m      "
              f"{row['max_rle']:>8.4f}    {row['mean_rle']:>8.4f}    "
              f"{row['max_temp_c']:>7.1f}°C   {row['collapse_pct']:>6.1f}%")
    
    # Overall statistics
    print("\n" + "=" * 100)
    print("📈 Aggregate Statistics")
    print("=" * 100)
    print(f"Total sessions analyzed: {len(df_summary)}")
    print(f"Total duration: {df_summary['duration_min'].sum():.1f} minutes")
    print(f"Total samples: {df_summary['samples'].sum()}")
    print(f"\nPower:")
    print(f"  Max across all: {df_summary['max_power_w'].max():.2f}W")
    print(f"  Mean across all: {df_summary['mean_power_w'].mean():.2f}W")
    print(f"\nTemperature:")
    print(f"  Peak temp: {df_summary['max_temp_c'].max():.2f}°C")
    print(f"  Mean peak: {df_summary['max_temp_c'].mean():.2f}°C")
    print(f"\nEfficiency (RLE):")
    print(f"  Best max: {df_summary['max_rle'].max():.4f}")
    print(f"  Average max: {df_summary['max_rle'].mean():.4f}")
    print(f"  Worst mean: {df_summary['mean_rle'].min():.4f}")
    print(f"\nCollapse Events:")
    print(f"  Total collapses: {df_summary['collapse_count'].sum()}")
    print(f"  Average rate: {df_summary['collapse_pct'].mean():.1f}%")
    print(f"  Worst session: {df_summary['collapse_pct'].max():.1f}%")
    
    print("\n" + "=" * 100)
    
    # Health recommendations
    print("\n💡 Health Analysis:")
    
    if df_summary['max_temp_c'].max() > 80:
        hot_sessions = df_summary[df_summary['max_temp_c'] > 80]
        print(f"  🔴 {len(hot_sessions)} sessions exceeded 80°C (check cooling)")
    
    if df_summary['collapse_pct'].mean() > 15:
        print(f"  ⚠️  High collapse rate ({df_summary['collapse_pct'].mean():.1f}%) - thermal issues")
    elif df_summary['collapse_pct'].mean() > 5:
        print(f"  ⚠️  Moderate collapse rate ({df_summary['collapse_pct'].mean():.1f}%) - monitor closely")
    else:
        print(f"  ✅ Low collapse rate ({df_summary['collapse_pct'].mean():.1f}%) - healthy")
    
    if df_summary['max_a_load'].max() > 1.05:
        print(f"  🔴 Power limit exceeded in {df_summary[df_summary['max_a_load'] > 1.05].shape[0]} sessions")
    
    print("\n" + "=" * 100)

def main():
    if len(sys.argv) < 2:
        # Default to sessions/recent
        dir_path = Path(__file__).parent.parent / "sessions" / "recent"
        print(f"No directory specified, using: {dir_path}")
    else:
        dir_path = Path(sys.argv[1])
    
    if not dir_path.exists():
        print(f"Error: {dir_path} does not exist")
        sys.exit(1)
    
    if not dir_path.is_dir():
        print(f"Error: {dir_path} is not a directory")
        sys.exit(1)
    
    batch_analyze(dir_path)

if __name__ == "__main__":
    main()

