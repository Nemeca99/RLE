"""
MAXIMUM STRESS TEST - Hammers CPU to 100%
Uses multiprocessing to bypass GIL and truly stress all cores
"""

import multiprocessing as mp
import time
import math
import psutil
import sys
from rle_real_live import run_live_test

def hammer_cpu(core_id, duration):
    """
    Hammer a single CPU core with intensive computation.
    This runs in separate process to bypass GIL.
    """
    start_time = time.time()
    iteration = 0
    
    while time.time() - start_time < duration:
        # HUGE computation blocks
        for _ in range(1000000):
            val = iteration + _
            # Heavy math
            result = math.sqrt(val)
            result = math.sin(result)
            result = math.cos(result)
            result = result ** 2
            result = math.sqrt(result)
            
            # More computation
            for i in range(10):
                result += math.sqrt(i * val)
                result += math.sin(i * val)
                result += math.cos(i * val)
        
        iteration += 1


if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥🔥🔥 MAXIMUM STRESS TEST - PUSHING TO THE LIMIT 🔥🔥🔥")
    print("="*70)
    print("\nTarget: Intel i7-11700F (8 cores, 16 threads)")
    print("RTX 3060 Ti")
    print("\nThis WILL make your PC HOT! 🔥")
    
    duration = 60
    print(f"\nDuration: {duration} seconds")
    print("\n⚡ HAMMERING ALL CPU CORES TO 100% ⚡")
    print("Press Ctrl+C in THIS terminal to stop early\n")
    print("Starting in 2 seconds...")
    time.sleep(2)
    
    # Get physical cores (not threads)
    cpu_count = mp.cpu_count()
    print(f"\n🚀 Starting {cpu_count} CPU hammer processes...")
    print("   (Using multiprocessing to bypass Python GIL)")
    print("   (This will truly peg CPU to 100%)\n")
    
    # Start processes
    processes = []
    for i in range(cpu_count):
        p = mp.Process(target=hammer_cpu, args=(i, duration))
        p.daemon = True
        p.start()
        processes.append(p)
    
    print(f"✅ {cpu_count} processes started!")
    print("\n📊 Starting RLE_real monitoring...\n")
    time.sleep(1)
    
    try:
        # Now start monitoring (this happens in main process)
        run_live_test(duration=duration, interval=0.5, auto_stress=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user!")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        # Terminate all processes
        print("\n🛑 Stopping all CPU hammer processes...")
        for p in processes:
            p.terminate()
        for p in processes:
            p.join(timeout=2)
        print("✅ Cleanup complete!")

