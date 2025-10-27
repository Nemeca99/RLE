#!/usr/bin/env python3
"""
Sustained High-Load Test for Collapse Detection
Forces CPU to 100% utilization to validate RLE collapse detector
"""

import time
import threading
import math
import argparse

def burn_cpu(intensity=1.0):
    """Generate CPU load"""
    result = 0
    iterations = int(intensity * 2000000)
    for i in range(iterations):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result

def sustained_load_test(duration_minutes=30, threads=8):
    """Run sustained 100% CPU load test"""
    
    print("="*70)
    print("SUSTAINED HIGH-LOAD STRESS TEST")
    print("="*70)
    print(f"Duration: {duration_minutes} minutes")
    print(f"Threads: {threads}")
    print(f"Target: 100% CPU utilization")
    print("="*70)
    print("\n⚠ WARNING: This will push your CPU to thermal limits!")
    print("Make sure cooling is adequate. Monitor temperatures closely.\n")
    print("Starting in 3 seconds...")
    time.sleep(3)
    
    start_time = time.time()
    end_time = start_time + (duration_minutes * 60)
    
    def stress_worker():
        """Worker thread that burns CPU"""
        while time.time() < end_time:
            burn_cpu(1.0)  # Maximum intensity
    
    # Start worker threads
    worker_threads = []
    for i in range(threads):
        t = threading.Thread(target=stress_worker, daemon=True)
        t.start()
        worker_threads.append(t)
        print(f"Started thread {i+1}/{threads}")
    
    print("\nStress test running...")
    print("\nMonitor RLE in real-time - collapse events should appear at high temp/power")
    print("="*70)
    
    # Progress updates
    sample = 0
    while time.time() < end_time:
        elapsed = (time.time() - start_time) / 60
        remaining = (end_time - time.time()) / 60
        
        if sample % 60 == 0:  # Every minute
            print(f"[{elapsed:.1f}/{duration_minutes:.1f} min] Stress test in progress... "
                  f"{remaining:.1f} min remaining")
        
        sample += 1
        time.sleep(1)
    
    print(f"\n\nTest complete! Check monitoring data for collapse events.")
    print(f"Expected: Collapses at sustained high load with thermal evidence")
    print(f"Duration: {elapsed:.1f} minutes")

def main():
    parser = argparse.ArgumentParser(description="Sustained CPU stress test for collapse detection")
    parser.add_argument("--duration", type=int, default=30, help="Duration in minutes (default: 30)")
    parser.add_argument("--threads", type=int, default=8, help="Number of stress threads (default: 8)")
    
    args = parser.parse_args()
    
    sustained_load_test(args.duration, args.threads)

if __name__ == "__main__":
    main()

