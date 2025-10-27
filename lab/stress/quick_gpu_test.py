#!/usr/bin/env python3
"""
Quick GPU load test - simple matrix multiplication
Tests if GPU monitoring is working with load
"""

import time
import ctypes
import ctypes.util

try:
    import pynvml
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    print("NVML initialized")
except Exception as e:
    print(f"NVML init failed: {e}")
    raise

print("\nStarting GPU load test (1 minute)...")
print("="*70)

start = time.time()
end = start + 60  # 1 minute
sample = 0

try:
    while time.time() < end:
        # Generate some work
        import random
        size = 1000
        a = [[random.random() for _ in range(size)] for _ in range(size)]
        b = [[random.random() for _ in range(size)] for _ in range(size)]
        
        # Simple multiplication
        result = [[sum(a[i][k] * b[k][j] for k in range(size)) for j in range(size)] for i in range(size)]
        
        # Monitor GPU
        if sample % 10 == 0:
            temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
            power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            
            elapsed = time.time() - start
            print(f"[{elapsed:.1f}s] GPU: {util:5.1f}% | Temp: {temp:5.1f}°C | Power: {power:5.1f}W")
        
        sample += 1
        
except KeyboardInterrupt:
    print("\nStopping...")
    
print(f"\nCompleted {sample} iterations in {time.time() - start:.1f}s")

