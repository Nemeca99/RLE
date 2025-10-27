"""
CPU stress test to generate load for RLE_real monitoring.
This will create CPU load in a separate process.
"""

import multiprocessing
import time


def cpu_stress_loop(duration, intensity):
    """Run CPU-intensive computation to generate load."""
    end_time = time.time() + duration
    
    print("Starting CPU stress (intensity: {})...".format(intensity))
    
    while time.time() < end_time:
        # Perform CPU-intensive operations
        for _ in range(intensity * 10000):
            _ = sum(i*i for i in range(100))
        time.sleep(0.1)  # Small pause to allow other processes
    
    print("CPU stress complete")


if __name__ == '__main__':
    # Get system CPU count
    num_cores = multiprocessing.cpu_count()
    print("CPU cores available: {}".format(num_cores))
    
    # Ask user for parameters
    print("\nThis will create CPU load for RLE_real monitoring.")
    duration = int(input("Duration in seconds (suggest 40): ") or "40")
    intensity = int(input("Intensity level 1-5 (suggest 3): ") or "3")
    
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    cpu_stress_loop(duration, intensity)

