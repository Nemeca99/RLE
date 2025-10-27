#!/usr/bin/env python3
"""Quick 2-minute ramp test"""

import time
import threading
import math

def cpu_burn(intensity):
    result = 0
    iterations = int(intensity * 100000)
    for i in range(iterations):
        result += math.sqrt(i)
    return result

print("="*70)
print("Quick CPU Ramp Test (2 minutes)")
print("Pattern: 60s ramp up (6 steps) → 60s cooldown")
print("="*70)
print("\nStarting...")

start = time.time()

# RAMP UP: 6 steps of 10 seconds
print("\n[RAMP UP - 60 seconds]")
for ramp in range(6):
    ramp_start = time.time()
    intensity = (ramp + 1) / 6.0
    duration = 10.0
    
    print(f"Step {ramp+1}/6: {intensity*100:.0f}% load", end=" ")
    
    while time.time() - ramp_start < duration:
        cpu_burn(intensity)
    
    print("✓")
    print(f"Temp: checking...")

print("\n[COOLDOWN - 60 seconds]")
for i in range(6):
    print(f"Cooldown progress: {i*10}s / 60s")
    time.sleep(10)

elapsed = time.time() - start
print(f"\nTest complete: {elapsed:.1f}s")
print("\nCheck the monitoring CSV for efficiency curves!")

