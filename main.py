#!/usr/bin/env python3
"""Entrypoint script for Leahe CBT Mood Tracker."""

import sys
from pathlib import Path

# Ensure src/ is in sys.path
src_dir = Path(__file__).resolve().parent / "src"
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from leahe.cli import main

if __name__ == "__main__":
    main()
