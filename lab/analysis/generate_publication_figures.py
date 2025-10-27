#!/usr/bin/env python3
"""
Generate Publication-Ready Figures
Extract key graphs from session data for paper submission
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import glob

def load_session(filepath):
    """Load CSV with error handling"""
    import csv
    
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        line_num = 0
        col_names = None
        
        for line in reader:
            line_num += 1
            if line_num == 1:
                col_names = line
                expected_cols = len(col_names)
                rows.append(line)
            else:
                if len(line) == expected_cols:
                    rows.append(line)
    
    df = pd.DataFrame(rows[1:], columns=rows[0])
    
    # Clean data
    for col in ['rle_smoothed', 'power_w', 'temp_c', 'util_pct']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    df = df.dropna(subset=['timestamp', 'device', 'rle_smoothed'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.dropna(subset=['timestamp'])
    
    # Create unified timeline
    if 'timestamp' in df.columns:
        start_time = df['timestamp'].min()
        df['seconds'] = (df['timestamp'] - start_time).dt.total_seconds()
    
    return df

def extract_knee_points(sessions, output_dir):
    """Extract knee points from multiple sessions"""
    
    knee_data = []
    
    for session_file in sessions:
        df = load_session(session_file)
        
        for device in ['cpu', 'gpu']:
            device_df = df[df['device'] == device].copy()
            
            if len(device_df) == 0:
                continue
            
            # Compute cycles_per_joule
            device_df['cycles_per_joule'] = device_df['util_pct'] / (device_df['power_w'] + 1e-3) * 100
            
            # Smooth
            device_df['cycles_smooth'] = device_df['cycles_per_joule'].rolling(window=30, center=True).mean()
            device_df['power_smooth'] = device_df['power_w'].rolling(window=30, center=True).mean()
            
            # Find knee
            device_df['cycles_slope'] = device_df['cycles_smooth'].diff()
            device_df['power_slope'] = device_df['power_smooth'].diff()
            
            knee_mask = (device_df['cycles_slope'] < -0.01) & (device_df['power_slope'] > 0.1)
            knees = device_df[knee_mask]
            
            if len(knees) > 0:
                # Find first major knee (>20% drop from peak)
                cycles_peak = device_df['cycles_per_joule'].max()
                for idx in knees.index:
                    cycles = device_df.loc[idx, 'cycles_per_joule']
                    if cycles < cycles_peak * 0.8:
                        knee_data.append({
                            'session': Path(session_file).stem,
                            'device': device,
                            'power_w': device_df.loc[idx, 'power_w'],
                            'rle': device_df.loc[idx, 'rle_smoothed'],
                            'util_pct': device_df.loc[idx, 'util_pct']
                        })
                        break
    
    # Plot knee boundary map
    if len(knee_data) > 0:
        fig, ax = plt.subplots(figsize=(10, 8))
        
        knee_df = pd.DataFrame(knee_data)
        
        for device in knee_df['device'].unique():
            device_knees = knee_df[knee_df['device'] == device]
            ax.scatter(device_knees['power_w'], device_knees['rle'], 
                      label=device.upper(), s=200, alpha=0.7, edgecolors='black', linewidth=1.5)
        
        ax.set_xlabel('Power (W)', fontsize=12, fontweight='bold')
        ax.set_ylabel('RLE', fontsize=12, fontweight='bold')
        ax.set_title('Knee Point Boundary Map Across Sessions\n(Dont Operate Past This Line)', 
                     fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        plt.savefig(f'{output_dir}/knee_boundary_map.png', dpi=200, bbox_inches='tight')
        print(f"\nSaved: {output_dir}/knee_boundary_map.png")
        plt.close()

def plot_efficiency_ceiling(sessions, output_dir):
    """Plot maximum sustainable RLE vs session duration"""
    
    ceiling_data = []
    
    for session_file in sessions:
        df = load_session(session_file)
        
        for device in ['cpu', 'gpu']:
            device_df = df[df['device'] == device].copy()
            
            if len(device_df) == 0:
                continue
            
            duration_hours = device_df['seconds'].max() / 3600
            max_rle = device_df['rle_smoothed'].max()
            mean_rle = device_df['rle_smoothed'].mean()
            
            ceiling_data.append({
                'session': Path(session_file).stem,
                'device': device,
                'duration_h': duration_hours,
                'max_rle': max_rle,
                'mean_rle': mean_rle
            })
    
    if len(ceiling_data) == 0:
        return
    
    fig, ax = plt.subplots(figsize=(12, 8))
    
    ceiling_df = pd.DataFrame(ceiling_data)
    
    for device in ceiling_df['device'].unique():
        device_data = ceiling_df[ceiling_df['device'] == device]
        ax.scatter(device_data['duration_h'], device_data['mean_rle'], 
                  label=f'{device.upper()} Mean RLE', s=200, alpha=0.6, edgecolors='black', linewidth=1.5)
        ax.scatter(device_data['duration_h'], device_data['max_rle'], 
                  label=f'{device.upper()} Peak RLE', s=150, alpha=0.6, marker='^', 
                  edgecolors='black', linewidth=1.5)
    
    ax.set_xlabel('Session Duration (hours)', fontsize=12, fontweight='bold')
    ax.set_ylabel('RLE', fontsize=12, fontweight='bold')
    ax.set_title('Efficiency Ceiling vs Session Duration', fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/efficiency_ceiling.png', dpi=200, bbox_inches='tight')
    print(f"Saved: {output_dir}/efficiency_ceiling.png")
    plt.close()

def plot_cross_device_coupling(sessions, output_dir):
    """Plot CPU-GPU thermal coupling"""
    
    coupling_data = []
    
    for session_file in sessions:
        df = load_session(session_file)
        
        cpu_df = df[df['device'] == 'cpu'].copy()
        gpu_df = df[df['device'] == 'gpu'].copy()
        
        if len(cpu_df) == 0 or len(gpu_df) == 0:
            continue
        
        # Align by timestamp
        cpu_df['seconds'] = (pd.to_datetime(cpu_df['timestamp'], utc=True) - pd.to_datetime(cpu_df['timestamp'], utc=True).min()).dt.total_seconds()
        gpu_df['seconds'] = (pd.to_datetime(gpu_df['timestamp'], utc=True) - pd.to_datetime(gpu_df['timestamp'], utc=True).min()).dt.total_seconds()
        
        # Sample at 1-minute intervals
        cpu_df['minute'] = cpu_df['seconds'] // 60
        gpu_df['minute'] = gpu_df['seconds'] // 60
        
        cpu_avg = cpu_df.groupby('minute')['temp_c'].mean()
        gpu_avg = gpu_df.groupby('minute')['temp_c'].mean()
        
        common_minutes = set(cpu_avg.index) & set(gpu_avg.index)
        
        for minute in common_minutes:
            coupling_data.append({
                'minute': minute,
                'cpu_temp': cpu_avg.loc[minute],
                'gpu_temp': gpu_avg.loc[minute]
            })
    
    if len(coupling_data) == 0:
        return
    
    coupling_df = pd.DataFrame(coupling_data)
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    ax.scatter(coupling_df['cpu_temp'], coupling_df['gpu_temp'], alpha=0.5, s=50)
    ax.set_xlabel('CPU Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_ylabel('GPU Temperature (°C)', fontsize=12, fontweight='bold')
    ax.set_title('Cross-Device Thermal Coupling', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, linestyle='--')
    
    # Add diagonal reference
    min_temp = min(coupling_df['cpu_temp'].min(), coupling_df['gpu_temp'].min())
    max_temp = max(coupling_df['cpu_temp'].max(), coupling_df['gpu_temp'].max())
    ax.plot([min_temp, max_temp], [min_temp, max_temp], 'r--', alpha=0.5, label='Identical')
    ax.legend()
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/thermal_coupling.png', dpi=200, bbox_inches='tight')
    print(f"Saved: {output_dir}/thermal_coupling.png")
    plt.close()

def main():
    print("\n" + "="*70)
    print("GENERATING PUBLICATION FIGURES")
    print("="*70)
    
    # Find all session files
    session_files = glob.glob("sessions/recent/rle_*.csv")
    
    if len(session_files) == 0:
        print("No session files found")
        return
    
    print(f"\nFound {len(session_files)} session files")
    
    output_dir = Path("sessions/archive/plots")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate figures
    print("\n1. Extracting knee points...")
    extract_knee_points(session_files, output_dir)
    
    print("\n2. Plotting efficiency ceiling...")
    plot_efficiency_ceiling(session_files, output_dir)
    
    print("\n3. Analyzing thermal coupling...")
    plot_cross_device_coupling(session_files, output_dir)
    
    print("\n" + "="*70)
    print("GENERATION COMPLETE")
    print("="*70)
    print(f"\nFigures saved to: {output_dir}/")

if __name__ == "__main__":
    main()

