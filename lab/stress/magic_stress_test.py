"""
Magic Square Stress Test + RLE_real Monitoring
Uses GPU-accelerated magic square search to stress CPU/GPU while monitoring RLE_real
"""

import subprocess
import threading
import time
import sys
from rle_real_live import run_live_test

# Import magic GPU code
sys.path.insert(0, 'Magic')
try:
    import magic_gpu
    from magic_gpu import get_backend, GPU_AVAILABLE
    print("GPU module loaded")
    print("GPU available: {}".format(GPU_AVAILABLE))
except ImportError as e:
    print("Error loading magic_gpu module: {}".format(e))
    sys.exit(1)


def run_magic_stress(duration=60, use_gpu=True, batch_size=100000):
    """
    Run magic square GPU stress test.
    
    Args:
        duration: How long to run stress test (seconds)
        use_gpu: Whether to use GPU acceleration
        batch_size: Batch size for processing
    """
    print("\n" + "="*60)
    print("MAGIC SQUARE STRESS TEST")
    print("="*60)
    print("Duration: {} seconds".format(duration))
    print("GPU enabled: {}".format(use_gpu and GPU_AVAILABLE))
    print("Batch size: {}".format(batch_size))
    print("\nThis will search for magic squares while monitoring RLE_real...")
    print("Press Ctrl+C to stop early\n")
    
    # Get appropriate backend
    backend = get_backend(use_gpu)
    if use_gpu and GPU_AVAILABLE:
        print("Using CUDA/GPU acceleration")
    else:
        print("Using CPU/NumPy")
    
    # Create magic square search configuration
    numbers = list(range(30, 81))  # roots from 30 to 80
    numbers_squared = [n**2 for n in numbers]
    
    start_time = time.time()
    iteration = 0
    
    try:
        while time.time() - start_time < duration:
            # Create batches and process
            # Simulating intensive computation
            batch_data = backend.array([numbers_squared] * batch_size)
            
            # Do some computational work
            result = backend.sum(batch_data**2)
            backend.sqrt(result)  # Extra computation
            
            # Generate combinations to stress test
            if iteration % 10 == 0:
                elapsed = time.time() - start_time
                print("Stress test: t={:.1f}s | Iteration={} | Result={:.2e}".format(
                    elapsed, iteration, float(backend.asnumpy(result)) if hasattr(backend, 'asnumpy') else float(result)
                ))
            
            iteration += 1
            time.sleep(0.1)  # Don't completely saturate CPU
            
    except KeyboardInterrupt:
        print("\nStress test stopped by user")
    except Exception as e:
        print("Error in stress test: {}".format(e))


def run_combined_test(monitor_duration=60, use_gpu=True):
    """
    Run RLE_real monitoring while stressing with magic square search.
    
    Args:
        monitor_duration: Duration of monitoring (seconds)
        use_gpu: Whether to use GPU for magic square stress
    """
    print("\n" + "="*60)
    print("COMBINED MAGIC SQUARE STRESS + RLE_REAL MONITORING")
    print("="*60)
    print("\nThis will:")
    print("1. Start magic square GPU stress test in background")
    print("2. Monitor your hardware with RLE_real")
    print("3. Track CPU/GPU usage, temperature, and system efficiency")
    print("\nMonitoring duration: {} seconds\n".format(monitor_duration))
    
    # Start stress test in background
    stress_thread = threading.Thread(
        target=run_magic_stress,
        args=(monitor_duration, use_gpu),
        daemon=True
    )
    stress_thread.start()
    
    # Small delay to let stress start
    time.sleep(2)
    
    # Run live monitoring (this will handle all the plotting)
    try:
        run_live_test(duration=monitor_duration, interval=1.0, auto_stress=False)
    except KeyboardInterrupt:
        print("\nTest stopped by user")
    except Exception as e:
        print("Error during monitoring: {}".format(e))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Magic Square Stress Test with RLE_real monitoring')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds (default: 60)')
    parser.add_argument('--no-gpu', action='store_true', help='Disable GPU acceleration')
    parser.add_argument('--gpu-only', action='store_true', help='Use GPU only (no magic square stress)')
    
    args = parser.parse_args()
    
    use_gpu = not args.no_gpu
    
    if args.gpu_only:
        print("Running GPU-only magic square stress test")
        run_magic_stress(duration=args.duration, use_gpu=use_gpu)
    else:
        print("Running combined stress test + monitoring")
        run_combined_test(monitor_duration=args.duration, use_gpu=use_gpu)

