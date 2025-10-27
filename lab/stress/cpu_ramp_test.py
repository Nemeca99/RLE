#!/usr/bin/env python3
"""
CPU Ramp Stress Test
Gradual 60-second ramp up, followed by 60-second cooldown
This should create a visible efficiency curve in RLE monitoring
"""

import time
import threading
import math

def cpu_burn(intensity):
    """Burn CPU cycles with controlled intensity"""
    result = 0
    iterations = int(intensity * 1000000)
    for i in range(iterations):
        result += math.sqrt(i) * math.sin(i)
    return result

def ramp_cycle(thread_id, duration_hours):
    """Run one ramp cycle: 60s ramp up, 60s cooldown"""
    start_time = time.time()
    end_time = start_time + (duration_hours * 3600)
    cycle_num = 0
    
    while time.time() < end_time:
        cycle_start = time.time()
        elapsed_total = (time.time() - start_time) / 3600
        
        # RAMP UP phase (60 seconds, 6 ramps of 10 seconds each)
        print(f"\n[Thread {thread_id} Cycle {cycle_num}] RAMP UP - {elapsed_total:.3f}h elapsed")
        print("="*70)
        
        # 6 ramps of 10 seconds each = 60 seconds total
        for ramp in range(6):
            ramp_start = time.time()
            ramp_duration = 10.0
            intensity = (ramp + 1) / 6.0  # Intensity 0.17, 0.33, 0.5, 0.67, 0.83, 1.0
            
            print(f"Ramp {ramp+1}/6: {intensity*100:.0f}% load...", end=" ")
            
            while time.time() - ramp_start < ramp_duration:
                cpu_burn(intensity)
                time.sleep(0.001)  # Prevent lockup
            
            print("✓")
        
        # Read peak stats during ramp
        try:
            import psutil
            temp_readings = psutil.sensors_temperatures()
            if 'coretemp' in temp_readings:
                max_temp = max([x.current for x in temp_readings['coretemp']])
                print(f"Peak temp: {max_temp:.1f}°C during ramp")
        except:
            pass
        
        # COOLDOWN phase (60 seconds)
        print(f"\nCOOLDOWN - monitoring thermal recovery...")
        cooldown_start = time.time()
        cooldown_end = time.time() + 60.0
        progress_samples = 0
        
        while time.time() < cooldown_end:
            if progress_samples % 10 == 0:
                elapsed = time.time() - cooldown_start
                remaining = 60.0 - elapsed
                print(f"Cooldown: {elapsed:.1f}s / 60.0s remaining", end="\r")
            time.sleep(0.5)
            progress_samples += 1
        
        cycle_num += 1
        elapsed_total = (time.time() - start_time) / 3600
        print(f"\n[End Cycle {cycle_num-1}] Total: {elapsed_total:.3f}h\n")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="CPU ramp stress test")
    parser.add_argument("--hours", type=float, default=8.0, help="Duration in hours (default: 8)")
    parser.add_argument("--threads", type=int, default=4, help="Number of CPU threads to use (default: 4)")
    
    args = parser.parse_args()
    
    print("="*70)
    print("CPU RAMP STRESS TEST")
    print("="*70)
    print(f"Duration: {args.hours} hours")
    print(f"Pattern: 60s gradual ramp (6 steps) → 60s cooldown")
    print(f"Threads: {args.threads}")
    print(f"Expected cycles: ~{int(args.hours * 3600 / 120)} cycles")
    print("="*70)
    print("\nThis will test thermal efficiency and collapse detection!")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    # Start stress threads
    threads = []
    for i in range(args.threads):
        t = threading.Thread(target=ramp_cycle, args=(i, args.hours), daemon=True)
        t.start()
        threads.append(t)
    
    try:
        # Run for specified duration
        time.sleep(args.hours * 3600)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    
    print("\nTest complete!")

if __name__ == "__main__":
    main()

