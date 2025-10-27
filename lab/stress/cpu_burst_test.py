#!/usr/bin/env python3
"""
CPU Burst Stress Test
10-second CPU bursts followed by 60-second cooldowns
Perfect for testing thermal recovery and monitoring systems
"""

import time
import threading
import math

def cpu_burn():
    """Burn CPU cycles with heavy computation"""
    result = 0
    for i in range(1000000):
        result += math.sqrt(i) * math.sin(i) * math.cos(i)
    return result

def burst_cycle(cycle_num, duration_hours):
    """Run one burst cycle: 10s load + 60s cooldown"""
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    
    while time.time() < end_time:
        cycle_start = time.time()
        elapsed_total = (time.time() - start_time) / 3600
        
        # GPU BURST phase (10 seconds)
        print(f"\n[Cycle {cycle_num}] BURST - {elapsed_total:.3f}h elapsed")
        print("="*70)
        
        burst_end = time.time() + 10.0
        while time.time() < burst_end:
            cpu_burn()
            time.sleep(0.001)  # Tiny sleep to prevent lockup
        
        # Read CPU stats during burst
        try:
            import psutil
            temp = psutil.sensors_temperatures()
            if 'coretemp' in temp:
                max_temp = max([x.current for x in temp['coretemp']])
                print(f"Peak temp during burst: {max_temp:.1f}°C")
        except:
            pass
        
        # COOLDOWN phase (60 seconds)
        print(f"\nCOOLDOWN - monitoring recovery...")
        cooldown_end = time.time() + 60.0
        progress_samples = 0
        
        while time.time() < cooldown_end:
            if progress_samples % 10 == 0:
                elapsed = time.time() - cycle_start
                remaining = 70 - elapsed
                print(f"Progress: {elapsed:.1f}s | Remaining: {remaining:.1f}s", end="\r")
            time.sleep(0.5)
            progress_samples += 1
        
        cycle_num += 1
        elapsed_total = (time.time() - start_time) / 3600
        print(f"\n[End Cycle {cycle_num-1}] Total elapsed: {elapsed_total:.3f}h\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CPU burst stress test")
    parser.add_argument("--hours", type=float, default=8.0, help="Duration in hours (default: 8)")
    parser.add_argument("--threads", type=int, default=8, help="Number of CPU threads to use (default: 8)")
    
    args = parser.parse_args()
    
    print("="*70)
    print("CPU BURST STRESS TEST")
    print("="*70)
    print(f"Duration: {args.hours} hours")
    print(f"Pattern: 10s load → 60s cooldown")
    print(f"Threads: {args.threads}")
    print(f"Expected cycles: ~{int(args.hours * 3600 / 70)} cycles")
    print("="*70)
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Start stress threads
    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=burst_cycle, args=(i, args.hours), daemon=True)
        t.start()
        threads.append(t)
    
    # Let threads run
    time.sleep(args.hours * 3600)
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()

