#!/usr/bin/env python3
"""
run_joint_session.py - Packaged Thermal-Optimization Coupling Analysis

Single-call script for reproducible thermal-optimization coupling experiments.
Input: model, duration, output folder. Everything else automatic.

Usage:
    python run_joint_session.py --model distilgpt2 --duration 120 --output results/
    python run_joint_session.py --model luna --duration 300 --output thermal_analysis/
    python run_joint_session.py --help
"""

import argparse
import subprocess
import time
import json
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
import os
from version_tracking import add_version_to_metadata, create_version_sidecar

class JointSessionRunner:
    """Manages synchronized RLE monitoring and AI training sessions"""
    
    def __init__(self, model_name, duration, output_dir, ambient_temp=21.0):
        self.model_name = model_name
        self.duration = duration
        self.output_dir = Path(output_dir)
        self.ambient_temp = ambient_temp
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Session metadata
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.session_start = time.time()
        
        print(f"🚀 Joint Session Runner Initialized")
        print(f"   Model: {self.model_name}")
        print(f"   Duration: {self.duration}s")
        print(f"   Output: {self.output_dir}")
        print(f"   Session ID: {self.session_id}")
    
    def setup_training_script(self):
        """Setup the training script with proper parameters"""
        
        # Determine training script path based on model
        if self.model_name.lower() == "distilgpt2":
            training_script = "L:/models/luna_trained_final/extended_training_with_sync.py"
        elif self.model_name.lower() == "luna":
            training_script = "L:/models/luna_trained_final/extended_training_with_sync.py"
        else:
            # Default to distilgpt2 for unknown models
            training_script = "L:/models/luna_trained_final/extended_training_with_sync.py"
        
        if not Path(training_script).exists():
            raise FileNotFoundError(f"Training script not found: {training_script}")
        
        return training_script
    
    def start_rle_monitoring(self):
        """Start RLE monitoring with synchronized parameters"""
        
        print(f"\n📊 Starting RLE monitoring...")
        
        rle_cmd = [
            "..\\venv\\Scripts\\python.exe",
            "monitoring\\hardware_monitor_v2.py",
            "--mode", "both",
            "--sample-hz", "1",
            "--duration", str(self.duration),
            "--realtime",
            "--model-name", f"{self.model_name} Joint Session",
            "--training-mode", f"Synchronized {self.model_name} training",
            "--ambient-temp", str(self.ambient_temp),
            "--notes", f"Joint session {self.session_id} - {self.model_name}"
        ]
        
        print(f"   Command: {' '.join(rle_cmd)}")
        
        # Start RLE monitoring process
        self.rle_process = subprocess.Popen(rle_cmd, cwd=".")
        
        # Wait for RLE to initialize
        time.sleep(2)
        
        print(f"   ✅ RLE monitoring started (PID: {self.rle_process.pid})")
        return self.rle_process
    
    def start_training(self):
        """Start AI training with synchronized logging"""
        
        print(f"\n🤖 Starting {self.model_name} training...")
        
        training_script = self.setup_training_script()
        
        train_cmd = [
            "..\\venv\\Scripts\\python.exe",
            training_script
        ]
        
        print(f"   Command: {' '.join(train_cmd)}")
        print(f"   Working directory: {Path(training_script).parent}")
        
        # Start training process
        self.train_process = subprocess.run(
            train_cmd, 
            cwd=Path(training_script).parent,
            capture_output=True,
            text=True
        )
        
        print(f"   ✅ Training completed (exit code: {self.train_process.returncode})")
        return self.train_process
    
    def wait_for_completion(self):
        """Wait for RLE monitoring to complete"""
        
        print(f"\n⏳ Waiting for RLE monitoring to complete...")
        
        # Wait for RLE process to finish
        self.rle_process.wait()
        
        print(f"   ✅ RLE monitoring completed (exit code: {self.rle_process.returncode})")
    
    def collect_results(self):
        """Collect and organize session results"""
        
        print(f"\n📁 Collecting session results...")
        
        # Find latest RLE CSV
        csv_files = sorted(Path("sessions/recent").glob("rle_enhanced_*.csv"), 
                          key=lambda p: p.stat().st_mtime, reverse=True)
        
        if not csv_files:
            raise FileNotFoundError("No RLE CSV files found!")
        
        rle_file = csv_files[0]
        print(f"   RLE data: {rle_file}")
        
        # Find training log
        train_log = Path("L:/models/luna_trained_final/grad_norm_sync_log.json")
        if not train_log.exists():
            raise FileNotFoundError("No training log file found!")
        
        print(f"   Training log: {train_log}")
        
        # Copy files to output directory
        import shutil
        
        output_rle = self.output_dir / f"rle_data_{self.session_id}.csv"
        output_train = self.output_dir / f"training_log_{self.session_id}.json"
        
        shutil.copy2(rle_file, output_rle)
        shutil.copy2(train_log, output_train)
        
        print(f"   ✅ Results copied to output directory")
        
        return {
            'rle_file': output_rle,
            'train_file': output_train,
            'session_id': self.session_id,
            'duration': self.duration,
            'model': self.model_name
        }
    
    def analyze_correlation(self, results):
        """Perform correlation analysis on the collected data"""
        
        print(f"\n🔬 Performing correlation analysis...")
        
        # Load RLE data
        rle_df = pd.read_csv(results['rle_file'])
        rle_df['timestamp'] = pd.to_datetime(rle_df['timestamp'])
        
        # Load training data
        with open(results['train_file'], 'r') as f:
            train_logs = json.load(f)
        
        train_df = pd.DataFrame(train_logs)
        train_df['timestamp'] = pd.to_datetime(train_df['timestamp_shared'], unit='s')
        
        # Convert to elapsed time since session start
        session_start = pd.Timestamp.fromtimestamp(self.session_start)
        rle_df['elapsed_time'] = (rle_df['timestamp'] - session_start).dt.total_seconds()
        train_df['elapsed_time'] = (train_df['timestamp'] - session_start).dt.total_seconds()
        
        # Align data using elapsed time
        merged_data = pd.merge_asof(
            train_df.sort_values('elapsed_time'),
            rle_df[rle_df['device'] == 'gpu'].sort_values('elapsed_time'),
            on='elapsed_time',
            direction='nearest',
            tolerance=2.0
        )
        
        if len(merged_data) == 0:
            print(f"   ❌ No aligned data found!")
            return None
        
        # Calculate correlations
        correlations = {
            'gpu_grad_rle': merged_data['grad_norm'].corr(merged_data['rle_smoothed']),
            'gpu_temp_grad': merged_data['temp_c'].corr(merged_data['grad_norm']),
            'gpu_loss_rle': merged_data['loss'].corr(merged_data['rle_smoothed'])
        }
        
        # Lag analysis
        lag_correlations = []
        for lag in range(-3, 4):
            if lag < 0:
                corr = merged_data['grad_norm'].shift(lag).corr(merged_data['rle_smoothed'])
            elif lag > 0:
                corr = merged_data['grad_norm'].corr(merged_data['rle_smoothed'].shift(lag))
            else:
                corr = merged_data['grad_norm'].corr(merged_data['rle_smoothed'])
            lag_correlations.append((lag, corr))
        
        peak_lag, peak_corr = max(lag_correlations, key=lambda x: abs(x[1]))
        
        analysis_results = {
            'session_id': self.session_id,
            'model': self.model_name,
            'duration': self.duration,
            'aligned_samples': len(merged_data),
            'correlations': correlations,
            'peak_lag': peak_lag,
            'peak_correlation': peak_corr,
            'causal_order': peak_lag < 0,
            'session_start': self.session_start,
            'ambient_temp': self.ambient_temp
        }
        
        # Add version tracking
        analysis_results = add_version_to_metadata(analysis_results)
        
        # Save analysis results
        analysis_file = self.output_dir / f"analysis_{self.session_id}.json"
        with open(analysis_file, 'w') as f:
            json.dump(analysis_results, f, indent=2)
        
        # Create version sidecar
        create_version_sidecar(self.session_id, self.output_dir)
        
        print(f"   ✅ Analysis completed and saved")
        print(f"   ✅ Version tracking embedded")
        
        return analysis_results
    
    def generate_report(self, analysis_results):
        """Generate a comprehensive session report"""
        
        print(f"\n📋 Generating session report...")
        
        if not analysis_results:
            print(f"   ❌ No analysis results to report")
            return
        
        # Create report
        report = f"""
THERMAL-OPTIMIZATION COUPLING ANALYSIS REPORT
============================================

Session Information:
  Session ID: {analysis_results['session_id']}
  Model: {analysis_results['model']}
  Duration: {analysis_results['duration']}s
  Ambient Temperature: {analysis_results['ambient_temp']}°C
  Aligned Samples: {analysis_results['aligned_samples']}

Correlation Analysis:
  GPU grad_norm ↔ RLE: {analysis_results['correlations']['gpu_grad_rle']:.3f}
  GPU temp ↔ grad_norm: {analysis_results['correlations']['gpu_temp_grad']:.3f}
  GPU loss ↔ RLE: {analysis_results['correlations']['gpu_loss_rle']:.3f}

Causal Analysis:
  Peak Correlation: {analysis_results['peak_correlation']:.3f} at lag {analysis_results['peak_lag']}s
  Causal Order: {'grad_norm → RLE' if analysis_results['causal_order'] else 'RLE → grad_norm'}

Interpretation:
  {'✅ Strong thermal-optimization coupling detected' if abs(analysis_results['correlations']['gpu_grad_rle']) > 0.3 else '⚠️  Weak thermal-optimization coupling'}
  {'✅ Consistent causal ordering' if analysis_results['causal_order'] else '⚠️  Reverse or simultaneous causality'}
  {'✅ Sufficient data for analysis' if analysis_results['aligned_samples'] > 50 else '⚠️  Limited data samples'}

Files Generated:
  - rle_data_{analysis_results['session_id']}.csv
  - training_log_{analysis_results['session_id']}.json
  - analysis_{analysis_results['session_id']}.json
  - report_{analysis_results['session_id']}.txt

Next Steps:
  - Run multiple sessions for reproducibility analysis
  - Vary model parameters to test coupling sensitivity
  - Use results for thermal-aware AI system design
"""
        
        # Save report
        report_file = self.output_dir / f"report_{self.session_id}.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"   ✅ Report generated: {report_file}")
        
        # Print summary
        print(f"\n" + "="*60)
        print(f"SESSION COMPLETE - {analysis_results['session_id']}")
        print(f"="*60)
        print(f"Model: {analysis_results['model']}")
        print(f"Duration: {analysis_results['duration']}s")
        print(f"Samples: {analysis_results['aligned_samples']}")
        print(f"Peak Correlation: {analysis_results['peak_correlation']:.3f} at lag {analysis_results['peak_lag']}s")
        print(f"Causal Order: {'grad_norm → RLE' if analysis_results['causal_order'] else 'RLE → grad_norm'}")
        print(f"Output Directory: {self.output_dir}")
        print(f"="*60)
    
    def run_session(self):
        """Run the complete joint session"""
        
        try:
            # Start RLE monitoring
            self.start_rle_monitoring()
            
            # Start training
            self.start_training()
            
            # Wait for completion
            self.wait_for_completion()
            
            # Collect results
            results = self.collect_results()
            
            # Analyze correlation
            analysis_results = self.analyze_correlation(results)
            
            # Generate report
            self.generate_report(analysis_results)
            
            return analysis_results
            
        except Exception as e:
            print(f"❌ Session failed: {e}")
            return None

def main():
    """Main entry point for the joint session runner"""
    
    parser = argparse.ArgumentParser(
        description="Run synchronized RLE monitoring and AI training session",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_joint_session.py --model distilgpt2 --duration 120 --output results/
  python run_joint_session.py --model luna --duration 300 --output thermal_analysis/
  python run_joint_session.py --model distilgpt2 --duration 60 --output quick_test/ --ambient-temp 22.5
        """
    )
    
    parser.add_argument('--model', required=True, 
                       help='Model name (distilgpt2, luna, etc.)')
    parser.add_argument('--duration', type=int, required=True,
                       help='Session duration in seconds')
    parser.add_argument('--output', required=True,
                       help='Output directory for results')
    parser.add_argument('--ambient-temp', type=float, default=21.0,
                       help='Ambient temperature in Celsius (default: 21.0)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.duration < 30:
        print("❌ Duration must be at least 30 seconds")
        sys.exit(1)
    
    if args.duration > 1800:
        print("❌ Duration must be less than 30 minutes")
        sys.exit(1)
    
    # Create and run session
    runner = JointSessionRunner(
        model_name=args.model,
        duration=args.duration,
        output_dir=args.output,
        ambient_temp=args.ambient_temp
    )
    
    results = runner.run_session()
    
    if results:
        print(f"\n🎉 Joint session completed successfully!")
        print(f"   Results saved to: {args.output}")
        sys.exit(0)
    else:
        print(f"\n❌ Joint session failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
