"""
EXTENDED STRESS TEST - Varying load over time
Tests if RLE_real actually responds meaningfully to changing conditions
"""

import multiprocessing as mp
import time
import math
import psutil
import numpy as np
from rle_real_live import run_live_test


def variable_cpu_burn(core_id, duration, intensity_pattern):
    """
    Burn CPU with variable intensity pattern.
    intensity_pattern: list of (start_time, end_time, intensity_multiplier)
    """
    start_time = time.time()
    current_intensity = 1.0
    iteration = 0
    
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        
        # Update intensity based on pattern
        for start, end, mult in intensity_pattern:
            if start <= elapsed <= end:
                current_intensity = mult
                break
        
        # Compute based on current intensity
        base_work = 100000
        work_amount = int(base_work * current_intensity)
        
        for _ in range(work_amount):
            val = iteration + _
            result = math.sqrt(val)
            result = math.sin(result)
            result = math.cos(result)
            result = result ** 2
            result = math.sqrt(result)
            
            for i in range(10):
                result += math.sqrt(i * val)
                result += math.sin(i * val)
        
        iteration += 1


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥🔥🔥 EXTENDED STRESS TEST - VALIDATING RLE_REAL 🔥🔥🔥")
    print("="*70)
    print("\nTesting RLE_real with varying CPU load:")
    print("  - 0-30s:  LOW load (baseline)")
    print("  - 30-60s: MEDIUM load")
    print("  - 60-90s: HIGH load")
    print("  - 90-120s: MAXIMUM load")
    print("  - 120-150s: MEDIUM load (cooling)")
    print("  - 150-180s: LOW load (recovery)")
    
    duration = 180  # 3 minutes
    print(f"\nDuration: {duration} seconds (3 minutes)")
    print("\n🔬 This will test if RLE_real actually changes meaningfully")
    print("   with varying load conditions...")
    print("\n⚠️  WARNING: Your PC will get VERY HOT!")
    print("Press Ctrl+C to stop early\n")
    
    import multiprocessing as mp
    cpu_count = mp.cpu_count()
    
    # Define intensity pattern (time, intensity_multiplier)
    # This creates: low → med → high → MAX → med → low
    intensity_pattern = [
        (0, 30, 0.2),      # Low
        (30, 60, 0.5),     # Medium
        (60, 90, 1.0),     # High
        (90, 120, 2.0),    # MAXIMUM
        (120, 150, 0.7),   # Medium (cooling)
        (150, 180, 0.3),  # Low (recovery)
    ]
    
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    print(f"\n🚀 Starting {cpu_count} variable-intensity processes...\n")
    
    # Start processes
    processes = []
    for i in range(cpu_count):
        p = mp.Process(target=variable_cpu_burn, args=(i, duration, intensity_pattern))
        p.daemon = True
        p.start()
        processes.append(p)
    
    print(f"✅ {cpu_count} processes started!")
    print("📊 Starting RLE_real monitoring...\n")
    time.sleep(1)
    
    try:
        # Monitor with shorter interval for more data points
        run_live_test(duration=duration, interval=0.5, auto_stress=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user!")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\n🛑 Stopping all processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join(timeout=2)
        print("✅ Done!")
        print("\n📊 Check the plot to see if RLE_real responded to load changes!")

