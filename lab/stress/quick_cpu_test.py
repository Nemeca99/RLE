#!/usr/bin/env python3
"""Quick 1-minute CPU test"""

import time
import threading
import math

def cpu_burn():
    result = 0
    for i in range(1000000):
        result += math.sqrt(i) * math.sin(i)
    return result

print("Starting 60-second CPU test...")
print("Monitoring will record this session")
print("="*70)

start = time.time()

# Test: 10s load, 60s idle
print("\n[0-10s] BURST phase")
burst_end = time.time() + 10
while time.time() < burst_end:
    cpu_burn()
    
print("\n[10-70s] COOLDOWN phase")
time.sleep(60)

elapsed = time.time() - start
print(f"\nTest complete: {elapsed:.1f}s")

