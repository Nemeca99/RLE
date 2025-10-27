#!/usr/bin/env python3
import sys
sys.path.insert(0, 'F:\\RLE\\lab')
from monitoring.hardware_monitor import monitor, parse_args

print("Testing NVML initialization...")

args = parse_args()
args.mode = 'gpu'
args.sample_hz = 1

try:
    print("Starting monitor...")
    # Run for just 5 seconds
    import time
    import threading
    
    def run():
        monitor(args)
    
    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    time.sleep(5)
    print("Test complete - monitor ran for 5 seconds")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

