#!/usr/bin/env python3
"""
Dynamic RLE Scaling Controller
Adjusts target power based on ambient temperature to maintain optimal efficiency
"""

import pandas as pd
import numpy as np
import argparse
from pathlib import Path

def compute_temperature_scaling(temp_ambient, base_temp=25.0, power_reduction_rate=0.02):
    """
    Calculate power scaling factor based on ambient temperature
    
    Args:
        temp_ambient: Current ambient temperature (°C)
        base_temp: Reference temperature for baseline (default: 25°C)
        power_reduction_rate: Power reduction per °C above base (default: 2%/°C)
    
    Returns:
        Scaling factor (0-1) for power target
    """
    temp_delta = temp_ambient - base_temp
    
    if temp_delta <= 0:
        # Below base temp: can increase power slightly
        return 1.0 + (abs(temp_delta) * 0.01)
    else:
        # Above base temp: reduce power to maintain efficiency
        reduction = temp_delta * power_reduction_rate
        return max(0.5, 1.0 - reduction)

def analyze_temperature_effects(df):
    """Analyze how temperature affects efficiency"""
    
    print("="*70)
    print("DYNAMIC SCALING ANALYSIS")
    print("="*70)
    
    # Filter for data with temperature
    if 'temp_c' in df.columns and 'rle_norm' in df.columns:
        valid = df['temp_c'].notna() & df['rle_norm'].notna()
        
        if valid.sum() > 0:
            temp_data = df.loc[valid, 'temp_c']
            rle_data = df.loc[valid, 'rle_norm']
            
            print(f"\nTemperature data available: {len(temp_data)} samples")
            print(f"Temperature range: {temp_data.min():.1f}°C - {temp_data.max():.1f}°C")
            
            # Group by temperature bins
            temp_bins = pd.cut(temp_data, bins=5)
            grouped = pd.DataFrame({'temp': temp_data, 'rle': rle_data, 'bin': temp_bins})
            
            print("\n" + "="*70)
            print("EFFICIENCY BY TEMPERATURE")
            print("="*70)
            print(f"{'Temp Range':<20} {'Samples':<12} {'Mean RLE':<15} {'Std RLE':<15}")
            print("-"*70)
            
            for bin_val in sorted(temp_bins.unique(), key=lambda x: x.mid):
                subset = grouped[grouped['bin'] == bin_val]
                print(f"{str(bin_val):<20} {len(subset):<12} {subset['rle'].mean():<15.4f} {subset['rle'].std():<15.4f}")
            
            # Compute scaling function
            print("\n" + "="*70)
            print("DYNAMIC SCALING PARAMETERS")
            print("="*70)
            
            # Find baseline temp (highest efficiency)
            baseline_temp_idx = grouped.groupby('bin')['rle'].mean().idxmax()
            baseline_temp = baseline_temp_idx.mid
            
            print(f"Baseline temperature: {baseline_temp:.1f}°C")
            print(f"\nRecommended power adjustments:")
            
            temp_values = [20, 25, 30, 35, 40, 45, 50]
            for temp in temp_values:
                scale = compute_temperature_scaling(temp, baseline_temp)
                power_target = 15.0 * scale  # Example: 15W base target
                print(f"  {temp:2d}°C: scale={scale:.3f} → target power={power_target:.1f}W")
            
            return baseline_temp
        else:
            print("No temperature data available for analysis")
            return None
    else:
        print("Temperature or RLE data not available")
        return None

def generate_scaling_curve(output_dir):
    """Generate visualization of dynamic scaling"""
    
    import matplotlib.pyplot as plt
    
    temps = np.linspace(15, 55, 100)
    scales = [compute_temperature_scaling(t) for t in temps]
    
    plt.figure(figsize=(10, 6))
    plt.plot(temps, scales, linewidth=2)
    plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
    plt.axvline(x=25, color='green', linestyle='--', alpha=0.7, label='Baseline: 25°C')
    plt.fill_between(temps, 0.5, scales, alpha=0.3, color='red', label='Power reduction zone')
    
    plt.xlabel('Ambient Temperature (°C)', fontsize=12)
    plt.ylabel('Power Scaling Factor', fontsize=12)
    plt.title('Dynamic Power Scaling Based on Ambient Temperature', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'{output_dir}/dynamic_scaling_curve.png', dpi=150)
    print(f"✓ Saved: {output_dir}/dynamic_scaling_curve.png")
    plt.close()

def main():
    parser = argparse.ArgumentParser(description="Dynamic power scaling based on temperature")
    parser.add_argument("csv", help="Path to CSV file")
    parser.add_argument("--plot", action="store_true", help="Generate visualization")
    
    args = parser.parse_args()
    
    print(f"Loading: {args.csv}")
    df = pd.read_csv(args.csv)
    
    # Clean data
    df = df.dropna(subset=['timestamp'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True, errors='coerce')
    df = df.drop_duplicates(subset=['timestamp', 'device'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Run analysis
    baseline_temp = analyze_temperature_effects(df)
    
    # Generate plots
    if args.plot:
        output_dir = Path("lab/sessions/archive/plots")
        output_dir.mkdir(parents=True, exist_ok=True)
        generate_scaling_curve(output_dir)
    
    print("\n" + "="*70)
    print("DYNAMIC SCALING ANALYSIS COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()

