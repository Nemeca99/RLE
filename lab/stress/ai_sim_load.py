#!/usr/bin/env python3
"""
AI-like GPU load simulator
Generates synthetic workload that mimics LLM inference patterns
Use this to test RLE monitoring without gaming or LM Studio
"""

import time
import numpy as np
from pathlib import Path

def generate_ai_like_load(duration_minutes=30, utilization_pattern="steady"):
    """
    Generate AI-like workload on GPU
    
    Args:
        duration_minutes: How long to run (default 30 min)
        utilization_pattern: "steady" (80-100%), "bursty" (variable), "ramp" (slow ramp up)
    """
    import pynvml
    
    print("="*70)
    print("AI Simulation Load Generator")
    print("="*70)
    print(f"Duration: {duration_minutes} minutes")
    print(f"Pattern: {utilization_pattern}")
    print("="*70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Initialize NVML
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    sample = 0
    
    try:
        while time.time() < end_time:
            elapsed = time.time() - start_time
            
            # Select pattern
            if utilization_pattern == "steady":
                # Steady 85-95% utilization
                target_util = 90.0 + (np.sin(elapsed * 0.1) * 5.0)
            elif utilization_pattern == "bursty":
                # Bursts between 40-100%
                target_util = 70.0 + (np.sin(elapsed * 0.5) * 30.0)
            elif utilization_pattern == "ramp":
                # Slow ramp from 50% to 95%
                target_util = 50.0 + min(45.0, elapsed / 60.0 * 5.0)
            else:
                target_util = 80.0
            
            # Generate GPU work using matrix operations
            # This keeps the GPU busy without needing actual ML code
            a = np.random.rand(1000, 1000).astype(np.float32)
            b = np.random.rand(1000, 1000).astype(np.float32)
            
            # Matrix multiply to generate load
            result = a @ b
            
            # Adjust to target utilization
            if sample % 10 == 0:
                current_util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                if current_util < target_util * 0.9:
                    # Increase workload
                    for _ in range(3):
                        result = result @ a
                elif current_util > target_util * 1.1:
                    time.sleep(0.01)  # Back off slightly
            
            # Progress update
            if sample % 60 == 0:
                temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                fan = pynvml.nvmlDeviceGetFanSpeed(handle)
                util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
                
                elapsed_min = elapsed / 60
                remaining_min = (end_time - time.time()) / 60
                
                print(f"[{elapsed_min:.1f}/{duration_minutes:.1f} min] "
                      f"GPU: {util:5.1f}% | Temp: {temp:5.1f}°C | "
                      f"Power: {power:5.1f}W | Fan: {fan:3.0f}%")
            
            sample += 1
            time.sleep(0.1)  # 10 Hz workload generation
    
    except KeyboardInterrupt:
        print("\n\nStopping load generator...")
    
    print(f"\nCompleted {sample} workload samples")
    print(f"Elapsed: {(time.time() - start_time)/60:.1f} minutes")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI-like GPU load simulator")
    parser.add_argument("--duration", type=int, default=30, help="Duration in minutes (default: 30)")
    parser.add_argument("--pattern", choices=["steady", "bursty", "ramp"], 
                       default="steady", help="Utilization pattern (default: steady)")
    
    args = parser.parse_args()
    
    generate_ai_like_load(args.duration, args.pattern)

