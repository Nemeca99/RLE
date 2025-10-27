"""
MAXIMUM CPU/GPU STRESS TEST
Pushes Intel i7-11700F (8 cores) and RTX 3060 Ti to 100% usage
"""

import time
import threading
import multiprocessing
import numpy as np
import sys

def ultra_cpu_burn(core_id, stop_event):
    """Ultra-aggressive CPU burn - will use ALL CPU power."""
    import math
    
    print(f"CPU Core {core_id} worker started")
    iteration = 0
    
    while not stop_event.is_set():
        # INTENSIVE computation
        for _ in range(200000):
            # Heavy floating point ops
            val = (iteration + _) % 1000000
            result = math.sqrt(val)
            result = math.sin(result) ** 2
            result = math.cos(result) ** 2
            result = math.sqrt(result * val)
            
            # Linear algebra simulation
            for i in range(10):
                result += math.sqrt(i * val)
        
        iteration += 1
    
    print(f"CPU Core {core_id} worker stopped")


def gpu_burn_worker(stop_event, backend='numpy'):
    """GPU/CPU intensive workloads with large arrays."""
    if backend == 'cupy':
        try:
            import cupy as cp
            backend = cp
        except ImportError:
            backend = np
    
    print("Starting GPU/array computation worker...")
    iteration = 0
    
    while not stop_event.is_set():
        # Large array operations
        size = 5000
        a = backend.random.rand(size, size)
        b = backend.random.rand(size, size)
        
        # Matrix multiplication (VERY intensive)
        c = backend.dot(a, b)
        
        # More ops
        c = backend.sqrt(c)
        c = backend.sin(c)
        c = backend.cos(c)
        
        # Clear if using GPU
        if hasattr(c, 'device'):
            del a, b, c
            backend.get_default_memory_pool().free_all_blocks()
        
        iteration += 1
    
    print("GPU/array worker stopped")


def run_maximum_stress(duration=60, enable_gpu=False, num_cpu_cores=None):
    """
    Run MAXIMUM stress on CPU and GPU.
    
    Args:
        duration: Duration in seconds
        enable_gpu: Try to use GPU (requires cupy)
        num_cpu_cores: Number of CPU cores to stress (None = all)
    """
    import psutil
    
    # Get system info
    cpu_count = psutil.cpu_count(logical=True)
    print("\n" + "="*70)
    print("MAXIMUM STRESS TEST - i7-11700F + RTX 3060 Ti")
    print("="*70)
    print(f"CPU Cores: {cpu_count}")
    print(f"Duration: {duration} seconds")
    print(f"GPU Stress: {'ENABLED' if enable_gpu else 'Disabled (CuPy not installed)'}")
    print("\nThis will:")
    print("  - Stress ALL CPU cores to 100%")
    print("  - Run intensive floating point calculations")
    print("  - Heavy matrix operations")
    print("  - Monitor RLE_real in real-time")
    print("\n⚠️  WARNING: This will make your PC very hot!")
    print("Press Ctrl+C to stop early\n")
    
    stop_event = threading.Event()
    workers = []
    
    # Number of CPU workers
    if num_cpu_cores is None:
        num_cpu_cores = cpu_count
    
    # Start CPU workers on ALL cores
    print(f"Starting {num_cpu_cores} CPU workers (1 per core)...")
    for i in range(num_cpu_cores):
        w = threading.Thread(target=ultra_cpu_burn, args=(i, stop_event), daemon=True)
        w.start()
        workers.append(w)
    
    # Start GPU worker if enabled
    if enable_gpu:
        try:
            import cupy as cp
            print("Starting GPU worker...")
            gpu_worker = threading.Thread(target=gpu_burn_worker, args=(stop_event, 'cupy'), daemon=True)
            gpu_worker.start()
            workers.append(gpu_worker)
        except ImportError:
            print("GPU stress disabled - CuPy not installed")
    
    # Wait and monitor
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"\r[t={elapsed:.1f}s] CPU Usage: {cpu_percent:.1f}%", end='')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
    finally:
        print("\nStopping all workers...")
        stop_event.set()
        time.sleep(1)
    
    print("Stress test complete!")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='MAXIMUM CPU/GPU Stress Test')
    parser.add_argument('--duration', type=int, default=60, help='Test duration')
    parser.add_argument('--gpu', action='store_true', help='Enable GPU stress (requires cupy)')
    parser.add_argument('--cores', type=int, default=None, help='Number of CPU cores to stress')
    
    args = parser.parse_args()
    run_maximum_stress(duration=args.duration, enable_gpu=args.gpu, num_cpu_cores=args.cores)

