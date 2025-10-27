#!/usr/bin/env python3
"""
Quick session analysis - prints summary statistics
Usage: python analyze_session.py [session.csv]
"""

import sys
import pandas as pd
from pathlib import Path

def analyze_session(csv_path):
    """Analyze an RLE session CSV"""
    df = pd.read_csv(csv_path)
    
    print("=" * 70)
    print(f"RLE Session Analysis: {csv_path.name}")
    print("=" * 70)
    
    # Basic stats
    print(f"\n📅 Session Duration")
    start = pd.to_datetime(df.iloc[0]['timestamp'])
    end = pd.to_datetime(df.iloc[-1]['timestamp'])
    duration = (end - start).total_seconds() / 60
    print(f"   Start: {start}")
    print(f"   End:   {end}")
    print(f"   Duration: {duration:.1f} minutes ({len(df)} samples)")
    
    # Power analysis
    print(f"\n⚡ Power Consumption")
    print(f"   Max:  {df['power_w'].max():.2f}W")
    print(f"   Min:  {df['power_w'].min():.2f}W")
    print(f"   Mean: {df['power_w'].mean():.2f}W")
    print(f"   Median: {df['power_w'].median():.2f}W")
    
    # Temperature analysis
    print(f"\n🌡️  Temperature")
    print(f"   Max:  {df['temp_c'].max():.2f}°C")
    print(f"   Min:  {df['temp_c'].min():.2f}°C")
    print(f"   Mean: {df['temp_c'].mean():.2f}°C")
    
    # Utilization
    print(f"\n💪 GPU Utilization")
    print(f"   Max:  {df['util_pct'].max():.2f}%")
    print(f"   Mean: {df['util_pct'].mean():.2f}%")
    print(f"   Median: {df['util_pct'].median():.2f}%")
    
    # Load analysis
    print(f"\n📊 Load Analysis (A_load)")
    print(f"   Max:  {df['a_load'].max():.3f}")
    print(f"   Mean: {df['a_load'].mean():.3f}")
    print(f"   Samples over 0.95: {(df['a_load'] > 0.95).sum()} ({(df['a_load'] > 0.95).sum()/len(df)*100:.1f}%)")
    
    # RLE stats
    print(f"\n📈 RLE Efficiency")
    print(f"   Max smoothed:  {df['rle_smoothed'].max():.4f}")
    print(f"   Mean smoothed: {df['rle_smoothed'].mean():.4f}")
    print(f"   Median:        {df['rle_smoothed'].median():.4f}")
    
    # Split components (if available)
    if 'E_th' in df.columns and 'E_pw' in df.columns:
        print(f"\n🔬 Split Components")
        print(f"   E_th (thermal):  mean {df['E_th'].mean():.4f}")
        print(f"   E_pw (power):     mean {df['E_pw'].mean():.4f}")
    
    # Collapse analysis
    print(f"\n⚠️  Efficiency Collapses")
    collapse_count = df['collapse'].sum()
    collapse_pct = collapse_count / len(df) * 100
    print(f"   Total collapse events: {collapse_count}")
    print(f"   Percentage: {collapse_pct:.1f}% of samples")
    
    if collapse_count > 0:
        collapsed = df[df['collapse'] == 1]
        if len(collapsed) > 0:
            print(f"   Avg temp during collapse: {collapsed['temp_c'].mean():.2f}°C")
            print(f"   Avg power during collapse: {collapsed['power_w'].mean():.2f}W")
    
    # Thermal sustainability
    print(f"\n🕐 Thermal Sustainability (t_sustain)")
    print(f"   Mean:  {df['t_sustain_s'].mean():.1f}s")
    print(f"   Min:   {df['t_sustain_s'].min():.1f}s")
    print(f"   Samples <60s: {(df['t_sustain_s'] < 60).sum()} (warning: close to limit)")
    
    # Alerts
    print(f"\n🚨 Safety Alerts")
    alerts = df[df['alerts'].notna() & (df['alerts'] != '')]
    if len(alerts) == 0:
        print("   None - system stayed within safe limits ✅")
    else:
        print(f"   Alert events: {len(alerts)}")
        for alert_type in alerts['alerts'].unique():
            count = alerts[alerts['alerts'] == alert_type].shape[0]
            print(f"   - {alert_type}: {count}")
    
    print("\n" + "=" * 70)
    
    # Health assessment
    print("\n💡 Health Assessment:")
    
    if df['temp_c'].max() < 70:
        print("   ✅ Temperature: Excellent (below 70°C)")
    elif df['temp_c'].max() < 80:
        print("   ✅ Temperature: Good (below 80°C)")
    else:
        print("   ⚠️  Temperature: Hot (approaching limits)")
    
    if collapse_pct < 5:
        print(f"   ✅ Collapse rate: Very low ({collapse_pct:.1f}%) - healthy operation")
    elif collapse_pct < 15:
        print(f"   ⚠️  Collapse rate: Moderate ({collapse_pct:.1f}%) - check thermal/cooling")
    else:
        print(f"   🔴 Collapse rate: High ({collapse_pct:.1f}%) - system overstressed")
    
    if df['a_load'].max() > 1.05:
        print(f"   🔴 Power: Exceeding rated capacity (max {df['a_load'].max():.3f})")
    elif df['a_load'].max() > 0.95:
        print(f"   ⚠️  Power: Operating near limit (max {df['a_load'].max():.3f})")
    else:
        print(f"   ✅ Power: Well within limits")
    
    print("\n" + "=" * 70)
    print("Analysis complete!")
    print("=" * 70)

def main():
    if len(sys.argv) < 2:
        # Find latest CSV
        sessions = Path(__file__).parent / "sessions" / "recent"
        csvs = sorted(sessions.glob("rle_*.csv"), reverse=True)
        
        if csvs:
            print(f"No file specified, using latest: {csvs[0].name}\n")
            analyze_session(csvs[0])
        else:
            print("Usage: python analyze_session.py <session.csv>")
            print("\nOr place a session CSV in sessions/recent/ to auto-analyze latest")
            sys.exit(1)
    else:
        csv_path = Path(sys.argv[1])
        if not csv_path.exists():
            print(f"Error: {csv_path} not found")
            sys.exit(1)
        
        analyze_session(csv_path)

if __name__ == "__main__":
    main()
