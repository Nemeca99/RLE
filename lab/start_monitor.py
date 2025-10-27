#!/usr/bin/env python3
"""Start RLE monitor daemon"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from monitoring.hardware_monitor import monitor, parse_args
import argparse

if __name__ == "__main__":
    args = parse_args()
    monitor(args)
