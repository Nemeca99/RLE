#!/usr/bin/env python3
"""
Version tracking utilities for RLE scientific instrument
Automatically embeds git hash and version info in metadata
"""

import subprocess
import json
import time
from datetime import datetime
from pathlib import Path

def get_git_hash():
    """Get current git commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Short hash
    except:
        pass
    return "unknown"

def get_git_status():
    """Get git status for reproducibility"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        if result.returncode == 0:
            return "clean" if not result.stdout.strip() else "dirty"
    except:
        pass
    return "unknown"

def get_python_version():
    """Get Python version info"""
    import sys
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

def get_instrument_version():
    """Get instrument version info"""
    return {
        "instrument_name": "RLE Thermal-Optimization Coupling Analysis",
        "version": "1.0.0",
        "git_hash": get_git_hash(),
        "git_status": get_git_status(),
        "python_version": get_python_version(),
        "timestamp": datetime.now().isoformat(),
        "reproducibility": "Scientific instrument with version tracking"
    }

def add_version_to_metadata(metadata_dict):
    """Add version info to metadata dictionary"""
    version_info = get_instrument_version()
    metadata_dict.update(version_info)
    return metadata_dict

def create_version_sidecar(session_id, output_dir):
    """Create version sidecar file for session"""
    version_info = get_instrument_version()
    version_info["session_id"] = session_id
    
    version_file = Path(output_dir) / f"version_{session_id}.json"
    with open(version_file, 'w') as f:
        json.dump(version_info, f, indent=2)
    
    return version_file

if __name__ == "__main__":
    # Test version tracking
    print("RLE Instrument Version Info:")
    print(json.dumps(get_instrument_version(), indent=2))
