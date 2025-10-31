#!/usr/bin/env python3
"""
Auto-push latest RLE CSV to GitHub for Streamlit Cloud to read
Runs as a background daemon alongside the monitor
"""
import subprocess
import time
from pathlib import Path
import os

def find_latest_csv():
    """Find the latest CSV in sessions/recent/"""
    sessions_dir = Path(__file__).parent.parent / "sessions" / "recent"
    if not sessions_dir.exists():
        return None
    
    csv_files = list(sessions_dir.glob("rle_*.csv"))
    if not csv_files:
        return None
    
    return max(csv_files, key=lambda p: p.stat().st_mtime)

def push_to_github(csv_path, branch="live-data"):
    """Commit and push CSV to GitHub"""
    repo_root = Path(__file__).parent.parent.parent
    
    try:
        # Copy CSV to a predictable location
        target_path = repo_root / "lab" / "sessions" / "live" / "latest.csv"
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file
        import shutil
        shutil.copy2(csv_path, target_path)
        
        # Git operations
        os.chdir(repo_root)
        
        # Check if branch exists, create if not
        branch_check = subprocess.run(
            ["git", "branch", "--list", branch],
            capture_output=True,
            text=True
        )
        
        if branch not in branch_check.stdout:
            # Create branch
            subprocess.run(["git", "checkout", "-b", branch], capture_output=True, check=False)
        else:
            # Switch to branch
            subprocess.run(["git", "checkout", branch], capture_output=True, check=False)
        
        # Add file (use relative path)
        rel_path = str(target_path.relative_to(repo_root)).replace('\\', '/')
        subprocess.run(["git", "add", rel_path], check=False, capture_output=True)
        
        # Commit
        commit_msg = f"Update live RLE data {time.strftime('%Y%m%d_%H%M%S')}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg],
            check=False,
            capture_output=True
        )
        
        # Push
        result = subprocess.run(
            ["git", "push", "origin", branch, "--force"],
            check=False,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            return True
        else:
            print(f"Push failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"Push failed: {e}")
        return False

def main():
    """Watch and push latest CSV every 30 seconds"""
    last_csv = None
    last_mtime = 0
    
    print("[GitHub Sync] Started - pushing latest CSV every 30s to live-data branch")
    
    while True:
        latest = find_latest_csv()
        
        if latest and latest.stat().st_mtime > last_mtime:
            print(f"[GitHub Sync] New CSV detected: {latest.name}")
            
            if push_to_github(latest):
                print(f"[GitHub Sync] Successfully pushed {latest.name}")
                last_csv = latest
                last_mtime = latest.stat().st_mtime
                
                # Switch back to main branch
                repo_root = Path(__file__).parent.parent.parent
                os.chdir(repo_root)
                subprocess.run(["git", "checkout", "main"], capture_output=True, check=False)
            else:
                print(f"[GitHub Sync] Push failed for {latest.name}")
        
        time.sleep(30)  # Check every 30 seconds

if __name__ == "__main__":
    main()

