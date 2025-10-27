"""Simple CPU stress test that gradually increases load."""

import time
import threading


def cpu_burn(intensity):
    """Burn CPU cycles at given intensity."""
    import math
    for _ in range(int(intensity * 1000000)):
        math.sqrt(_)


def run_stress_test(duration=60):
    """Run gradual CPU stress test."""
    start = time.time()
    
    def stress_loop():
        t = 0
        while t < duration:
            # Calculate intensity
            if t < 15:
                intensity = 0.5
            elif t < 45:
                intensity = 0.5 + (t - 15) / 30 * 4.5
            else:
                intensity = 5.0
            
            # Burn CPU
            cpu_burn(intensity)
            time.sleep(0.5)
            t = time.time() - start
    
    # Run on multiple threads
    threads = []
    for _ in range(4):
        t = threading.Thread(target=stress_loop)
        t.daemon = True
        t.start()
        threads.append(t)
    
    # Wait
    stress_loop()


if __name__ == '__main__':
    print("Starting CPU stress test...")
    run_stress_test(60)

