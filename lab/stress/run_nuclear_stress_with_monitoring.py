"""
Run NUCLEAR CPU stress + RLE_real monitoring
"""

import threading
import time
import math
import subprocess
import sys

stop_event = threading.Event()

def nuclear_worker(stop_event):
    """Nuclear worker - burns CPU hard."""
    iteration = 0
    while not stop_event.is_set():
        for _ in range(300000):
            val = (iteration + _) % 1000000
            result = math.sqrt(val)
            result = math.sin(result)
            result = math.cos(result)
            result = math.sqrt(result * val)
            for i in range(10):
                result += math.sqrt(i * val)
                result += math.sin(i * val)
        iteration += 1


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥 NUCLEAR STRESS + RLE_REAL MONITORING 🔥")
    print("="*70)
    print("\nThis will:")
    print("  1. Start 16 CPU workers (ALL cores to 100%)")
    print("  2. Monitor with RLE_real in real-time")
    print("  3. Show temperature rise and efficiency collapse")
    
    duration = 60
    print(f"\nDuration: {duration} seconds")
    print("\nStarting in 3 seconds...\n")
    time.sleep(3)
    
    # Import psutil and get CPU count
    import psutil
    cpu_count = psutil.cpu_count(logical=True)
    print(f"Starting {cpu_count} nuclear CPU workers...")
    
    # Start workers
    workers = []
    for i in range(cpu_count):
        w = threading.Thread(target=nuclear_worker, args=(stop_event,))
        w.daemon = True
        w.start()
        workers.append(w)
    
    print(f"{cpu_count} workers started! CPU should spike to 100%.\n")
    time.sleep(1)
    
    try:
        # Now start monitoring
        from rle_real_live import run_live_test
        run_live_test(duration=duration, interval=0.5, auto_stress=False)
    except KeyboardInterrupt:
        print("\nStopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("\nStopping all workers...")
        stop_event.set()
        time.sleep(0.5)
        print("Done!")

