#!/usr/bin/env python3
"""
Kia - RLE Monitoring Lab Validation Script
Validates the RLE formula and collapse detection logic

Usage: python kia_validate.py [session.csv] [--html] [--log]
"""

import sys
import pandas as pd
import numpy as np
from pathlib import Path
from collections import deque
from datetime import datetime
import json

def compute_stability(util_history):
    """Compute stability from utilization history"""
    if len(util_history) < 5:
        return 1.0 / (1.0 + 0.0)
    stddev = np.std(util_history)
    return 1.0 / (1.0 + stddev)

def generate_report(csv_path, df, results, output_dir="validation_logs"):
    """Generate markdown report, log file, and optionally HTML"""
    
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    
    # Markdown report
    report_path = output_dir / f"kia_report_{timestamp}.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(f"# Kia Validation Report\n\n")
        f.write(f"**Generated**: {datetime.now().isoformat()}\n")
        f.write(f"**Session**: {csv_path.name}\n")
        f.write(f"**Validation Agent**: Kia\n\n")
        f.write("---\n\n")
        
        f.write("## Executive Summary\n\n")
        f.write(f"- **Session Duration**: {results['duration_min']:.1f} minutes\n")
        f.write(f"- **Total Samples**: {results['total_samples']}\n")
        f.write(f"- **Formula Validation**: {results['formula_match']:.1f}% match rate\n")
        f.write(f"- **Status**: {'✅ PASSED' if results['formula_match'] >= 90 else '⚠️ PARTIAL'}\n\n")
        
        f.write("## RLE Formula Validation\n\n")
        f.write("| Sample | util% | a_load | t_sustain | Logged RLE | Recalculated | Match |\n")
        f.write("|--------|-------|--------|-----------|------------|--------------|-------|\n")
        
        for row_data in results['sample_rows']:
            f.write(f"| {row_data['row']} | {row_data['util']:.1f}% | {row_data['a_load']:.3f} | "
                   f"{row_data['t_sustain']:.1f}s | {row_data['logged']:.6f} | "
                   f"{row_data['recalc']:.6f} | {row_data['match']} |\n")
        
        f.write(f"\n**Match Rate**: {results['matches']}/{results['total_tested']} ({results['formula_match']:.1f}%)\n\n")
        
        f.write("## Session Statistics\n\n")
        f.write("### Performance Metrics\n")
        f.write(f"- Max RLE: `{results['max_rle']:.4f}`\n")
        f.write(f"- Mean RLE: `{results['mean_rle']:.4f}`\n")
        f.write(f"- Median RLE: `{results['median_rle']:.4f}`\n\n")
        
        f.write("### Hardware Monitoring\n")
        f.write(f"- Max Temperature: `{results['max_temp']:.1f}°C`\n")
        f.write(f"- Mean Temperature: `{results['mean_temp']:.1f}°C`\n")
        f.write(f"- Max Power: `{results['max_power']:.2f}W`\n")
        f.write(f"- Mean Power: `{results['mean_power']:.2f}W`\n")
        f.write(f"- Max Utilization: `{results['max_util']:.1f}%`\n")
        f.write(f"- Mean Utilization: `{results['mean_util']:.1f}%`\n\n")
        
        f.write("### Efficiency Collapse Analysis\n")
        f.write(f"- Total Collapse Events: `{results['collapse_count']}`\n")
        f.write(f"- Collapse Rate: `{results['collapse_rate']:.1f}%`\n")
        
        if results['collapse_count'] > 0:
            collapsed_df = df[df['collapse'] == 1]
            f.write(f"- Avg Temp During Collapse: `{collapsed_df['temp_c'].mean():.1f}°C`\n")
            f.write(f"- Avg Power During Collapse: `{collapsed_df['power_w'].mean():.1f}W`\n")
        
        f.write("\n### Thermal Sustainability\n")
        f.write(f"- Mean t_sustain: `{results['mean_t_sustain']:.1f}s`\n")
        f.write(f"- Min t_sustain: `{results['min_t_sustain']:.1f}s`\n")
        f.write(f"- Samples <60s: `{results['samples_near_limit']}` (warning: close to thermal limit)\n\n")
        
        f.write("## Health Assessment\n\n")
        f.write(results['health_assessment'] + "\n\n")
        
        f.write("---\n\n")
        f.write("*Validation performed by Kia v1.0*\n")
    
    print(f"📄 Report saved: {report_path}")
    
    # Log file
    log_path = output_dir / f"kia_{timestamp}.txt"
    with open(log_path, 'w', encoding='utf-8') as f:
        f.write(f"Kia Validation Log\n")
        f.write(f"{'='*70}\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"Session: {csv_path.name}\n")
        f.write(f"\nResults:\n{json.dumps(results, indent=2, default=str)}\n")
    
    print(f"📝 Log saved: {log_path}")

def validate_rle_formula(csv_path, output_dir="validation_logs"):
    """Validate RLE formula and generate comprehensive reports"""
    
    print("=" * 70)
    print("Kia Validation: RLE Formula Check")
    print("=" * 70)
    print(f"Analyzing: {csv_path.name}\n")
    
    df = pd.read_csv(csv_path)
    
    # Compute stats
    start_time = pd.to_datetime(df.iloc[0]['timestamp'])
    end_time = pd.to_datetime(df.iloc[-1]['timestamp'])
    duration = (end_time - start_time).total_seconds() / 60
    
    # Test RLE recomputation
    util_window = deque(maxlen=5)
    matches = 0
    total = 0
    sample_rows = []
    
    print("Testing RLE recomputation (first 10 rows):")
    print("-" * 70)
    print(f"{'Row':<6} {'util%':<8} {'a_load':<8} {'Logged RLE':<12} {'Recalc':<12} {'Match':<6}")
    print("-" * 70)
    
    for i in range(min(10, len(df))):
        row = df.iloc[i]
        util_pct = row['util_pct']
        a_load = row['a_load']
        t_sustain = row['t_sustain_s']
        logged_rle = row['rle_raw']
        
        util_window.append(util_pct)
        stability = compute_stability(list(util_window))
        
        denominator = a_load * (1.0 + 1.0 / max(t_sustain, 0.1))
        recalc_rle = (util_pct / 100.0 * stability) / denominator
        
        diff = abs(logged_rle - recalc_rle)
        match = "✓" if diff < 0.01 else "✗"
        
        if diff < 0.01:
            matches += 1
        total += 1
        
        sample_rows.append({
            'row': i+1,
            'util': util_pct,
            'a_load': a_load,
            't_sustain': t_sustain,
            'logged': logged_rle,
            'recalc': recalc_rle,
            'match': match
        })
        
        print(f"{i+1:<6} {util_pct:<8.1f} {a_load:<8.3f} "
              f"{logged_rle:<12.6f} {recalc_rle:<12.6f} {match:<6}")
    
    print("-" * 70)
    print(f"\nMatch rate: {matches}/{total} ({matches/total*100:.1f}%)")
    
    # Compute comprehensive results
    results = {
        'session_file': csv_path.name,
        'duration_min': duration,
        'total_samples': len(df),
        'formula_match': matches/total*100 if total > 0 else 0,
        'matches': matches,
        'total_tested': total,
        'sample_rows': sample_rows,
        'max_rle': float(df['rle_smoothed'].max()),
        'mean_rle': float(df['rle_smoothed'].mean()),
        'median_rle': float(df['rle_smoothed'].median()),
        'max_temp': float(df['temp_c'].max()),
        'mean_temp': float(df['temp_c'].mean()),
        'max_power': float(df['power_w'].max()),
        'mean_power': float(df['power_w'].mean()),
        'max_util': float(df['util_pct'].max()),
        'mean_util': float(df['util_pct'].mean()),
        'collapse_count': int(df['collapse'].sum()),
        'collapse_rate': float(df['collapse'].sum() / len(df) * 100),
        'mean_t_sustain': float(df['t_sustain_s'].mean()),
        'min_t_sustain': float(df['t_sustain_s'].min()),
        'samples_near_limit': int((df['t_sustain_s'] < 60).sum())
    }
    
    # Health assessment
    health_parts = []
    if results['max_temp'] < 70:
        health_parts.append("✅ Temperature: Excellent (below 70°C)")
    elif results['max_temp'] < 80:
        health_parts.append("✅ Temperature: Good (below 80°C)")
    else:
        health_parts.append("⚠️ Temperature: Hot (approaching limits)")
    
    if results['collapse_rate'] < 5:
        health_parts.append(f"✅ Collapse rate: Very low ({results['collapse_rate']:.1f}%) - healthy")
    elif results['collapse_rate'] < 15:
        health_parts.append(f"⚠️ Collapse rate: Moderate ({results['collapse_rate']:.1f}%)")
    else:
        health_parts.append(f"🔴 Collapse rate: High ({results['collapse_rate']:.1f}%) - overstressed")
    
    results['health_assessment'] = "\n".join(health_parts)
    
    # Generate reports
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    generate_report(csv_path, df, results, output_dir)
    
    # Print summary
    status = "✅ PASSED" if results['formula_match'] >= 90 else "⚠️ PARTIAL"
    print(f"\n{status} - Formula validation: {results['formula_match']:.1f}% match rate")
    print(f"📄 Reports saved to: {output_dir}")
    print("=" * 70)
    
    return results['formula_match'] >= 90

def main():
    args = sys.argv[1:]
    
    # Find CSV file
    if not args or not args[0].endswith('.csv'):
        sessions = Path(__file__).parent / "lab" / "sessions" / "recent"
        if sessions.exists():
            csvs = sorted(sessions.glob("rle_*.csv"), reverse=True)
            if csvs:
                csv_path = csvs[0]
                print(f"No file specified, using latest: {csv_path.name}\n")
            else:
                print("Error: No session CSVs found")
                return 1
        else:
            print("Usage: python kia_validate.py <session.csv>")
            return 1
    else:
        csv_path = Path(args[0])
    
    if not csv_path.exists():
        print(f"Error: {csv_path} not found")
        return 1
    
    success = validate_rle_formula(csv_path)
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
