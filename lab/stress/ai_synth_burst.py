#!/usr/bin/env python3
"""
AI-like GPU burst load simulator
Generates 10-second GPU bursts followed by 60-second cooldowns
Perfect for testing thermal recovery and RLE collapse detection
"""

import time
import argparse
import random

def generate_burst_workload(duration_hours=8):
    """
    Generate alternating GPU burst and cooldown periods
    
    Args:
        duration_hours: Total test duration in hours
    """
    import pynvml
    
    print("="*70)
    print("AI Burst Load Generator - Thermal Recovery Test")
    print("="*70)
    print(f"Duration: {duration_hours} hours")
    print(f"Pattern: 10s GPU burst → 60s cooldown")
    print("="*70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Initialize NVML
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    cycle_count = 0
    
    # GPU-intensive matrices
    size = 3000  # Large enough to stress GPU
    a = np.random.rand(size, size).astype(np.float32)
    b = np.random.rand(size, size).astype(np.float32)
    
    # Store GPU state
    state = {"burst_active": False, "temp_peak": 0, "power_peak": 0}
    
    try:
        while time.time() < end_time:
            cycle_start = time.time()
            cycle_count += 1
            
            # Check if we should be in burst or cooldown
            cycle_elapsed = time.time() - cycle_start
            in_burst = cycle_elapsed < 10.0  # First 10 seconds = burst
            
            if in_burst and not state["burst_active"]:
                # Starting new burst
                state["burst_active"] = True
                print(f"\n[CYCLE {cycle_count}] Starting GPU burst...")
            
            if not in_burst and state["burst_active"]:
                # Burst ended, entering cooldown
                state["burst_active"] = False
                elapsed_hr = (time.time() - start_time) / 3600
                print(f"[{elapsed_hr:.2f}h] Cooldown started - Peak: {state['temp_peak']:.1f}°C, {state['power_peak']:.1f}W")
                state["temp_peak"] = 0
                state["power_peak"] = 0
            
            # Generate GPU work during burst
            if in_burst:
                # Heavy matrix operations
                result = a @ b
                result = result @ a
                result = result @ b
                
                # Monitor GPU state
                temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                
                if temp > state["temp_peak"]:
                    state["temp_peak"] = temp
                if power > state["power_peak"]:
                    state["power_peak"] = power
                
                # Slight sleep to prevent Python from spinning too hard
                time.sleep(0.01)
            else:
                # Cooldown period - minimal work
                time.sleep(0.5)
            
            # Print progress every cycle
            if cycle_elapsed < 0.5:  # Only at cycle start
                elapsed_hr = (time.time() - start_time) / 3600
                temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                
                print(f"[{elapsed_hr:.2f}h] Cycle {cycle_count} - Idle: {temp:.1f}°C, {power:.1f}W", end="\r")
            
            # Regenerate matrices occasionally to vary workload
            if cycle_count % 100 == 0:
                a = np.random.rand(size, size).astype(np.float32)
                b = np.random.rand(size, size).astype(np.float32)
    
    except KeyboardInterrupt:
        print("\n\nStopping load generator...")
    
    elapsed_hr = (time.time() - start_time) / 3600
    print(f"\n\nCompleted {cycle_count} cycles")
    print(f"Elapsed: {elapsed_hr:.2f} hours")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI burst load generator")
    parser.add_argument("--hours", type=float, default=8.0, help="Duration in hours (default: 8)")
    
    args = parser.parse_args()
    generate_burst_workload(args.hours)

