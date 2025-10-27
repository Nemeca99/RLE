"""
NUCLEAR STRESS TEST - Pushes ALL CPU cores to 100%
"""

import time
import threading
import math
import sys

# Store in global to avoid issue
stop_event_global = threading.Event()

def nuclear_cpu_burn(stop_event):
    """Nuclear CPU burn - pure computation, no I/O."""
    iteration = 0
    while not stop_event.is_set():
        # MASSIVE computation
        for _ in range(500000):
            val = iteration + _
            # Heavy floating point
            result = math.sqrt(val)
            result = math.sin(result)
            result = math.cos(result)
            result = math.sqrt(result * val)
            # More operations
            for i in range(5):
                result += math.sqrt(i * val)
                result += math.sin(i * val)
        
        iteration += 1


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥 NUCLEAR CPU STRESS TEST 🔥")
    print("="*70)
    print("\nTarget: Intel i7-11700F (16 threads)")
    print("This will peg CPU to 100%!")
    
    duration = 60
    print(f"\nDuration: {duration} seconds")
    print("Press Ctrl+C to stop\n")
    
    # Get CPU count
    import multiprocessing as mp
    cpu_count = mp.cpu_count()
    print(f"Starting {cpu_count} CPU workers (100% utilization)...\n")
    
    # Start all workers
    workers = []
    for i in range(cpu_count):
        w = threading.Thread(target=nuclear_cpu_burn, args=(stop_event_global,))
        w.daemon = True
        w.start()
        workers.append(w)
    
    print("All workers started! CPU should be at 100% now.\n")
    
    # Monitor
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            import psutil
            cpu_percent = psutil.cpu_percent(interval=0.5)
            print(f"\r[t={elapsed:.1f}s] CPU: {cpu_percent:.1f}%", end='', flush=True)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        print("\nStopping...")
        stop_event_global.set()
        time.sleep(0.5)
        print("Done!")

