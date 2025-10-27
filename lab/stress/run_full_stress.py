"""
Full Stress Test with RLE_real Monitoring
Pushes CPU and GPU to MAX while monitoring with RLE_real
"""

import sys
import time
import threading
from run_magic_stress_with_monitoring import cpu_burn_worker
from rle_real_live import run_live_test, get_cpu_metrics
import psutil

def run_full_stress_with_monitoring(duration=60):
    """
    Run MAXIMUM stress while monitoring with RLE_real.
    """
    print("\n" + "="*70)
    print("FULL SYSTEM STRESS TEST + RLE_REAL MONITORING")
    print("="*70)
    print("\n🔥 PUSHING YOUR SYSTEM TO THE LIMIT 🔥")
    print(f"  - Intel i7-11700F: ALL 8 cores to 100%")
    print(f"  - RTX 3060 Ti: GPU computation")
    print(f"  - Duration: {duration} seconds")
    print(f"\n⚠️  This will make your PC VERY HOT and load to the MAX!")
    print("Press Ctrl+C to stop anytime\n")
    print("Starting in 3...")
    time.sleep(1)
    print("2...")
    time.sleep(1)
    print("1...")
    time.sleep(1)
    print("GO!\n")
    
    stop_event = threading.Event()
    
    # Intensity function - ramps up aggressively
    start_time = time.time()
    def get_intensity():
        elapsed = time.time() - start_time
        if elapsed < 10:
            return 2.0  # Start high at 200% intensity
        elif elapsed < 40:
            return 2.0 + (elapsed - 10) / 30 * 3.0  # Ramp to 500%
        else:
            return 5.0  # MAXIMUM intensity
    
    # Start many CPU workers
    num_workers = psutil.cpu_count(logical=True)
    print(f"Starting {num_workers} CPU workers on {num_workers} cores...")
    
    workers = []
    for i in range(num_workers):
        w = threading.Thread(target=cpu_burn_worker, args=(get_intensity, stop_event), daemon=True)
        w.start()
        workers.append(w)
    
    # Also add intensive GPU/array worker if numpy works
    try:
        gpu_worker = threading.Thread(
            target=lambda: intensive_array_ops(stop_event),
            daemon=True
        )
        gpu_worker.start()
        workers.append(gpu_worker)
        print("GPU/array worker started")
    except:
        pass
    
    print("All workers started!\n")
    time.sleep(1)
    
    try:
        # Run RLE_real monitoring
        run_live_test(duration=duration, interval=0.5, auto_stress=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        print("\nStopping all stress workers...")
        stop_event.set()
        time.sleep(0.5)
        print("Done!\n")


def intensive_array_ops(stop_event):
    """Heavy array operations to stress memory and CPU."""
    print("Starting intensive array operations...")
    iteration = 0
    
    while not stop_event.is_set():
        # Large arrays
        size = 2000
        a = np.random.rand(size, size)
        b = np.random.rand(size, size)
        
        # Matrix multiplication
        c = np.dot(a, b)
        
        # More operations
        c = np.sqrt(c)
        c = np.sin(c)
        c = np.cos(c)
        
        iteration += 1
        if iteration % 100 == 0:
            pass  # Don't print too often
    
    print("Array worker stopped")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Full System Stress Test with RLE_real monitoring')
    parser.add_argument('--duration', type=int, default=60, help='Duration in seconds')
    
    args = parser.parse_args()
    run_full_stress_with_monitoring(duration=args.duration)

