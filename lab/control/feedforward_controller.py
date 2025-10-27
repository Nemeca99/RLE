#!/usr/bin/env python3
"""
Feed-Forward RLE Controller
Automatically adjusts workload scheduling based on RLE predictions
Backs off heavy tasks before instability occurs
"""

import time
import psutil
import argparse

class RLEFeedforwardController:
    def __init__(self, 
                 rle_warning_threshold=0.5,
                 rle_critical_threshold=0.3,
                 backoff_factor=0.8,
                 recovery_factor=1.1):
        """
        Args:
            rle_warning_threshold: RLE level to start backing off (0-1)
            rle_critical_threshold: RLE level for aggressive backoff (0-1)
            backoff_factor: CPU frequency multiplier when backing off
            recovery_factor: CPU frequency multiplier when recovering
        """
        self.warning_threshold = rle_warning_threshold
        self.critical_threshold = rle_critical_threshold
        self.backoff_factor = backoff_factor
        self.recovery_factor = recovery_factor
        self.current_state = "normal"
        
    def get_current_rle_from_csv(self, csv_path, lookback=10):
        """Read latest RLE from monitoring CSV"""
        try:
            import pandas as pd
            
            df = pd.read_csv(csv_path)
            if len(df) < lookback:
                return None
            
            # Get CPU data from last N samples
            cpu_df = df[df['device'] == 'cpu'].tail(lookback)
            
            if len(cpu_df) == 0:
                return None
            
            # Average of recent RLE values
            rle_smoothed = cpu_df['rle_smoothed'].mean()
            rle_norm = cpu_df['rle_norm'].mean() if 'rle_norm' in cpu_df.columns else None
            
            return rle_smoothed, rle_norm
        except Exception as e:
            print(f"Failed to read RLE: {e}")
            return None
    
    def adjust_cpu_governor(self, scaling_factor):
        """
        Adjust CPU frequency governor (Linux only)
        
        Args:
            scaling_factor: 0.5-2.0, multiplier for max frequency
        """
        try:
            import subprocess
            
            # Get current max freq
            with open('/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq', 'r') as f:
                max_freq = int(f.read().strip())
            
            target_freq = int(max_freq * scaling_factor)
            
            # Set max frequency
            for cpu in range(psutil.cpu_count()):
                with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_max_freq', 'w') as f:
                    f.write(str(target_freq))
            
            return True
        except:
            return False
    
    def control_decision(self, rle_norm):
        """Make control decision based on RLE"""
        
        if rle_norm is None:
            return "unknown", "continue"
        
        if rle_norm < self.critical_threshold:
            state = "critical"
            action = "aggressive_backoff"
        elif rle_norm < self.warning_threshold:
            state = "warning"
            action = "backoff"
        else:
            state = "normal"
            action = "continue"
        
        self.current_state = state
        return state, action
    
    def apply_action(self, action):
        """Apply control action"""
        if action == "aggressive_backoff":
            print("🚨 CRITICAL: Aggressive backoff - reducing load by 50%")
            # Reduce CPU priority for all processes
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    p = psutil.Process(proc.pid)
                    if p.nice() < 15:  # Not already low priority
                        p.nice(psutil.HIGH_PRIORITY_CLASS if os.name == 'nt' else 15)
                except:
                    pass
            return 0.5  # 50% backoff
        
        elif action == "backoff":
            print("⚠ WARNING: Backing off - reducing load by 20%")
            # Slightly reduce priority
            return 0.8  # 20% backoff
        
        else:  # continue or recover
            if self.current_state == "critical":
                print("✓ Recovering from critical state")
            return 1.0  # Full speed

def monitor_and_control(csv_path, check_interval=5):
    """Monitor RLE and apply feed-forward control"""
    
    print("="*70)
    print("RLE FEED-FORWARD CONTROLLER")
    print("="*70)
    print(f"Monitoring CSV: {csv_path}")
    print(f"Check interval: {check_interval}s")
    print("="*70)
    print("\nController thresholds:")
    print(f"  Warning: RLE < 0.5 (start backing off)")
    print(f"  Critical: RLE < 0.3 (aggressive backoff)")
    print("\nStarting feed-forward control...")
    
    controller = RLEFeedforwardController()
    
    try:
        while True:
            # Read latest RLE
            rle_data = controller.get_current_rle_from_csv(csv_path)
            
            if rle_data:
                rle_smoothed, rle_norm = rle_data
                
                print(f"\n[RLE] Smoothed: {rle_smoothed:.4f}, Normalized: {rle_norm:.4f}")
                
                # Make decision
                state, action = controller.control_decision(rle_norm)
                
                print(f"[State] {state.upper()} - Action: {action}")
                
                # Apply action
                if action != "continue":
                    controller.apply_action(action)
                else:
                    print("→ Normal operation")
            else:
                print("Waiting for monitoring data...")
            
            time.sleep(check_interval)
            
    except KeyboardInterrupt:
        print("\n\nStopping feed-forward controller...")

def main():
    import os
    
    parser = argparse.ArgumentParser(description="Feed-forward RLE controller")
    parser.add_argument("--csv", default="lab/sessions/recent/rle_*.csv", help="CSV file to monitor")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds")
    parser.add_argument("--warning", type=float, default=0.5, help="Warning threshold (default: 0.5)")
    parser.add_argument("--critical", type=float, default=0.3, help="Critical threshold (default: 0.3)")
    
    args = parser.parse_args()
    
    monitor_and_control(args.csv, args.interval)

if __name__ == "__main__":
    main()

