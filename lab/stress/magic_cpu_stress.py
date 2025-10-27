"""
Magic Square CPU Stress Test
Runs CPU-intensive magic square search to stress test the system
"""

import numpy as np
import time
import threading
import itertools
import sys

# Simple magic square search functions
def check_magic_square(grid):
    """Check if a 3x3 grid is a magic square."""
    # Check rows
    for row in grid:
        if sum(row) != sum(grid[0]):
            return False
    
    # Check columns
    for j in range(3):
        if sum(grid[i][j] for i in range(3)) != sum(grid[0]):
            return False
    
    # Check diagonals
    diag1 = sum(grid[i][i] for i in range(3))
    diag2 = sum(grid[i][2-i] for i in range(3))
    
    return diag1 == diag2 == sum(grid[0])


def magic_square_search_worker(numbers, start_idx, end_idx, results, stop_event):
    """
    Worker thread for searching magic squares.
    
    Args:
        numbers: List of numbers to search
        start_idx: Starting index in the list
        end_idx: Ending index in the list
        results: List to store results
        stop_event: Threading event to signal stop
    """
    import math
    checked = 0
    while not stop_event.is_set():
        # MORE CPU-intensive: generate and check way more combinations
        for _ in range(1000):  # Do 1000 batches
            if stop_event.is_set():
                break
            
            # CPU-intensive computations
            for i in range(5000):
                # Generate some numbers
                val = numbers[start_idx % len(numbers)]
                
                # Heavy computation
                result = math.sqrt(val) ** 2
                math.sin(result)
                math.cos(result)
                
                # Reshape and check (this part checks magic squares)
                combo = tuple(numbers[(start_idx + i) % len(numbers):(start_idx + i + 9) % len(numbers)])
                if len(combo) == 9:
                    grid = np.array(combo).reshape(3, 3)
                    if check_magic_square(grid):
                        with threading.Lock():
                            results.append(combo)
            
            checked += 5000
            if checked % 100000 == 0:
                # Reduced print frequency to avoid overhead
                pass


def run_magic_cpu_stress(duration=60, num_workers=4):
    """
    Run CPU-intensive magic square search.
    
    Args:
        duration: How long to run (seconds)
        num_workers: Number of worker threads
    """
    print("\n" + "="*60)
    print("MAGIC SQUARE CPU STRESS TEST")
    print("="*60)
    print("Duration: {} seconds".format(duration))
    print("Workers: {}".format(num_workers))
    print("\nThis will search for magic squares using CPU...")
    print("Press Ctrl+C to stop early\n")
    
    # Generate numbers to search
    numbers = list(range(1, 100))  # 1 to 100
    
    # Initialize
    results = []
    stop_event = threading.Event()
    
    # Calculate work per worker
    total = len(numbers)
    chunk_size = total // num_workers
    
    # Start workers
    workers = []
    for i in range(num_workers):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_workers - 1 else total
        
        w = threading.Thread(
            target=magic_square_search_worker,
            args=(numbers, start, end, results, stop_event)
        )
        w.daemon = True
        w.start()
        workers.append(w)
    
    # Run for specified duration
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            elapsed = time.time() - start_time
            print(f"\rt={elapsed:.1f}s | Results: {len(results)}", end='')
            time.sleep(1.0)
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        stop_event.set()
        time.sleep(0.5)
    
    print(f"\n\nTest complete!")
    print(f"Found {len(results)} magic squares")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Magic Square CPU Stress Test')
    parser.add_argument('--duration', type=int, default=60, help='Test duration in seconds')
    parser.add_argument('--workers', type=int, default=4, help='Number of worker threads')
    
    args = parser.parse_args()
    run_magic_cpu_stress(duration=args.duration, num_workers=args.workers)

