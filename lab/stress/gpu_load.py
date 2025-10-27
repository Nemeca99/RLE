#!/usr/bin/env python3
"""
GPU Load Tester - Actually uses the GPU
Runs compute-heavy operations on GPU to stress it
"""

import time
import argparse

def gpu_load_test(duration_minutes=30, target_util=90):
    """
    Generate actual GPU load using CUDA operations
    
    Args:
        duration_minutes: How long to run
        target_util: Target GPU utilization percentage (0-100)
    """
    try:
        import torch
        print("PyTorch available, using GPU compute")
        use_pytorch = True
    except ImportError:
        print("PyTorch not available, using CUDA via cupy")
        use_pytorch = False
        try:
            import cupy as cp
        except ImportError:
            print("ERROR: Need either PyTorch OR CuPy installed")
            print("Install one of:")
            print("  pip install torch")
            print("  pip install cupy-cuda11x  # or cupy-cuda12x for CUDA 12")
            return
    
    import pynvml
    import numpy as np
    
    print("="*70)
    print("GPU Load Tester - Real GPU Workload")
    print("="*70)
    print(f"Duration: {duration_minutes} minutes")
    print(f"Target GPU utilization: {target_util}%")
    print("="*70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Initialize NVML
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(0)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    sample = 0
    print(f"\nRunning until {time.ctime(end_time)}...\n")
    
    try:
        while time.time() < end_time:
            elapsed = time.time() - start_time
            
            # Generate GPU load
            if use_pytorch:
                # PyTorch GPU operations
                a = torch.randn(2000, 2000, device='cuda')
                b = torch.randn(2000, 2000, device='cuda')
                
                # Matrix multiplication on GPU
                result = torch.matmul(a, b)
                
                # Extra work to hit target utilization
                for _ in range(2):
                    result = torch.matmul(result, a)
            else:
                # CuPy GPU operations
                a_cpu = np.random.rand(2000, 2000).astype(np.float32)
                b_cpu = np.random.rand(2000, 2000).astype(np.float32)
                
                # Transfer to GPU and compute
                a_gpu = cp.asarray(a_cpu)
                b_gpu = cp.asarray(b_cpu)
                result_gpu = cp.matmul(a_gpu, b_gpu)
                
                # Extra work
                for _ in range(2):
                    result_gpu = cp.matmul(result_gpu, a_gpu)
                
                # Synchronize to ensure work completes
                cp.cuda.Stream.null.synchronize()
            
            # Monitor GPU usage
            util = pynvml.nvmlDeviceGetUtilizationRates(handle).gpu
            
            # Progress update every minute
            if sample % 60 == 0:
                temp = pynvml.nvmlDeviceGetTemperature(handle, 0)
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
                fan = pynvml.nvmlDeviceGetFanSpeed(handle)
                
                elapsed_min = elapsed / 60
                remaining_min = (end_time - time.time()) / 60
                
                print(f"[{elapsed_min:.1f}/{duration_minutes:.1f} min] "
                      f"GPU: {util:5.1f}% | Temp: {temp:5.1f}°C | "
                      f"Power: {power:5.1f}W | Fan: {fan:3.0f}%")
            
            sample += 1
            
            # Adjust to target utilization
            if util < target_util * 0.8:
                # Too low, add more work
                if use_pytorch:
                    for _ in range(3):
                        result = torch.matmul(result, a)
                else:
                    for _ in range(3):
                        result_gpu = cp.matmul(result_gpu, a_gpu)
                    cp.cuda.Stream.null.synchronize()
            elif util > target_util * 1.1:
                # Too high, reduce work
                time.sleep(0.02)
    
    except KeyboardInterrupt:
        print("\n\nStopping GPU load test...")
    
    print(f"\nCompleted {sample} workload samples")
    print(f"Elapsed: {(time.time() - start_time)/60:.1f} minutes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GPU Load Tester - Real GPU workload")
    parser.add_argument("--duration", type=int, default=30, help="Duration in minutes")
    parser.add_argument("--util", type=int, default=90, help="Target GPU utilization % (0-100)")
    
    args = parser.parse_args()
    
    gpu_load_test(args.duration, args.util)

