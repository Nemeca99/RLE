"""
Run Magic Square Stress Test with RLE_real Monitoring
This orchestrates both the stress test and the monitoring
"""

import subprocess
import sys
import time
import threading

def cpu_burn_worker(stop_event, intensity_func):
    """CPU burning worker that runs continuously."""
    import math
    i = 0
    while not stop_event.is_set():
        intensity = intensity_func()
        # Run lots of math operations
        for _ in range(int(intensity * 100000)):
            val = i % 10000
            math.sqrt(val)
            math.sin(val)
            math.cos(val)
            math.sqrt(val ** 2 + 1)
        i += 1


def run_combined():
    """
    Run magic square stress test in background while monitoring with RLE_real.
    """
    print("="*70)
    print("MAGIC SQUARE STRESS TEST + RLE_REAL MONITORING")
    print("="*70)
    print("\nThis will:")
    print("  1. Start CPU stress test (magic square computation)")
    print("  2. Monitor your hardware with RLE_real live monitoring")
    print("  3. Capture CPU temperature, usage, and efficiency metrics")
    print("\nDuration: 60 seconds")
    print("\nPress Ctrl+C to stop early\n")
    
    import threading
    
    # Create intensity function
    start_time = time.time()
    def get_intensity():
        elapsed = time.time() - start_time
        if elapsed < 10:
            return 0.5  # Low baseline
        elif elapsed < 40:
            return 0.5 + (elapsed - 10) / 30 * 2.5  # Ramp up
        else:
            return 3.0  # Maximum
    
    # Start CPU stress workers
    stop_event = threading.Event()
    workers = []
    for _ in range(4):  # 4 threads for 4 cores
        w = threading.Thread(target=cpu_burn_worker, args=(stop_event, get_intensity))
        w.daemon = True
        w.start()
        workers.append(w)
    
    print("Starting CPU stress...")
    time.sleep(1)
    
    try:
        # Import and run live monitoring
        from rle_real_live import run_live_test
        run_live_test(duration=60, interval=1.0, auto_stress=False)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")
    except Exception as e:
        print("Error during monitoring: {}".format(e))
    finally:
        # Stop stress workers
        stop_event.set()
        time.sleep(0.5)
        print("\nStopped CPU stress")


if __name__ == '__main__':
    run_combined()

