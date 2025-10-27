#!/usr/bin/env python3
"""
Verify CPU/GPU Instrumentation
Confirms sensors are reporting data correctly
"""

import pandas as pd
import numpy as np
import argparse

def verify_instrumentation(df):
    """Check that all sensors are reporting correctly"""
    
    print("="*70)
    print("INSTRUMENTATION VERIFICATION")
    print("="*70)
    
    # Separate by device
    devices = df['device'].unique()
    
    for device in devices:
        if pd.isna(device):
            continue
            
        device_df = df[df['device'] == device].copy()
        
        print(f"\n{'='*70}")
        print(f"{device.upper()} INSTRUMENTATION")
        print(f"{'='*70}")
        
        # Check for required columns
        required_cols = ['util_pct', 'power_w', 'rle_smoothed']
        optional_cols = ['temp_c', 'vram_temp_c', 'rle_norm']
        
        print(f"\nRequired metrics:")
        for col in required_cols:
            if col in device_df.columns:
                valid = device_df[col].notna()
                coverage = valid.sum() / len(device_df) * 100
                mean_val = device_df[col].mean()
                
                status = "✓" if coverage > 80 else "⚠" if coverage > 0 else "✗"
                print(f"  {status} {col:<20} Coverage: {coverage:>6.1f}%  Mean: {mean_val:>10.4f}")
            else:
                print(f"  ✗ {col:<20} Missing column")
        
        print(f"\nOptional metrics:")
        for col in optional_cols:
            if col in device_df.columns:
                valid = device_df[col].notna()
                coverage = valid.sum() / len(device_df) * 100
                mean_val = device_df[col].mean() if valid.any() else "N/A"
                
                if coverage > 0:
                    print(f"  ✓ {col:<20} Coverage: {coverage:>6.1f}%  Mean: {mean_val}")
                else:
                    print(f"  - {col:<20} No data")
            else:
                print(f"  - {col:<20} Not available")
        
        # Validation checks
        print(f"\nValidation:")
        
        # Check 1: Utilization in valid range
        if 'util_pct' in device_df.columns:
            util_valid = device_df['util_pct'].notna()
            if util_valid.any():
                util_range = (device_df.loc[util_valid, 'util_pct'] >= 0) & (device_df.loc[util_valid, 'util_pct'] <= 100)
                util_pct_valid = util_range.sum() / util_valid.sum() * 100
                print(f"  Utilization range (0-100%): {util_pct_valid:.1f}% valid")
        
        # Check 2: Power reasonable
        if 'power_w' in device_df.columns:
            power_valid = device_df['power_w'].notna()
            if power_valid.any():
                power_min = device_df.loc[power_valid, 'power_w'].min()
                power_max = device_df.loc[power_valid, 'power_w'].max()
                print(f"  Power range: {power_min:.1f}W - {power_max:.1f}W")
                
                if power_max > 1000:
                    print(f"  ⚠ WARNING: Unrealistic max power (>1000W)")
        
        # Check 3: RLE computed
        if 'rle_smoothed' in device_df.columns:
            rle_valid = device_df['rle_smoothed'].notna()
            if rle_valid.any():
                rle_mean = device_df.loc[rle_valid, 'rle_smoothed'].mean()
                print(f"  RLE computed: {rle_valid.sum()} samples, mean: {rle_mean:.4f}")
        
        # Check 4: Normalized RLE
        if 'rle_norm' in device_df.columns:
            norm_valid = device_df['rle_norm'].notna()
            if norm_valid.any():
                norm_mean = device_df.loc[norm_valid, 'rle_norm'].mean()
                norm_in_range = ((device_df.loc[norm_valid, 'rle_norm'] >= 0) & 
                                 (device_df.loc[norm_valid, 'rle_norm'] <= 1)).sum()
                norm_pct = norm_in_range / norm_valid.sum() * 100
                print(f"  Normalized RLE: {norm_pct:.1f}% in [0,1] range, mean: {norm_mean:.4f}")
        
        # Check 5: Temperature if available
        if 'temp_c' in device_df.columns:
            temp_valid = device_df['temp_c'].notna()
            if temp_valid.any():
                temp_mean = device_df.loc[temp_valid, 'temp_c'].mean()
                temp_max = device_df.loc[temp_valid, 'temp_c'].max()
                print(f"  Temperature: {temp_valid.sum()} samples, range: {temp_mean:.1f}°C (max: {temp_max:.1f}°C)")
            else:
                print(f"  ⚠ Temperature: Not available (HWiNFO not connected)")
    
    # Overall health verdict
    print("\n" + "="*70)
    print("OVERALL VERDICT")
    print("="*70)
    
    cpu_df = df[df['device'] == 'cpu']
    gpu_df = df[df['device'] == 'gpu']
    
    cpu_ok = len(cpu_df) > 0 and cpu_df['util_pct'].notna().any()
    gpu_ok = len(gpu_df) > 0 and gpu_df['util_pct'].notna().any()
    
    if cpu_ok and gpu_ok:
        print("✓ Both CPU and GPU instrumentation functional")
    elif cpu_ok:
        print("⚠ Only CPU instrumentation functional")
    elif gpu_ok:
        print("⚠ Only GPU instrumentation functional")
    else:
        print("✗ Instrumentation not functional")
    
    # Temporal alignment check
    print("\n" + "="*70)
    print("TEMPORAL ALIGNMENT")
    print("="*70)
    
    if len(cpu_df) > 0 and len(gpu_df) > 0:
        # Check if timestamps align
        cpu_times = pd.to_datetime(cpu_df['timestamp'], errors='coerce')
        gpu_times = pd.to_datetime(gpu_df['timestamp'], errors='coerce')
        
        cpu_valid = cpu_times.notna()
        gpu_valid = gpu_times.notna()
        
        print(f"CPU samples: {cpu_valid.sum()}")
        print(f"GPU samples: {gpu_valid.sum()}")
        
        if cpu_valid.sum() > 0 and gpu_valid.sum() > 0:
            # Check overlap in time
            cpu_min = cpu_times.min()
            cpu_max = cpu_times.max()
            gpu_min = gpu_times.min()
            gpu_max = gpu_times.max()
            
            overlap_start = max(cpu_min, gpu_min)
            overlap_end = min(cpu_max, gpu_max)
            overlap_duration = (overlap_end - overlap_start).total_seconds() if overlap_end > overlap_start else 0
            
            print(f"Temporal overlap: {overlap_duration:.0f}s")
            
            if overlap_duration > 0:
                print("✓ CPU and GPU data temporally aligned")
            else:
                print("⚠ CPU and GPU data from different time periods")
    else:
        print("⚠ Cannot check alignment - missing device data")

def main():
    parser = argparse.ArgumentParser(description="Verify instrumentation")
    parser.add_argument("csv", help="Path to CSV file")
    
    args = parser.parse_args()
    
    print(f"Loading: {args.csv}")
    df = pd.read_csv(args.csv)
    
    # Clean data
    df = df.dropna(subset=['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.drop_duplicates(subset=['timestamp', 'device'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    verify_instrumentation(df)
    
    print("\n" + "="*70)
    print("DIAGNOSTIC COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

