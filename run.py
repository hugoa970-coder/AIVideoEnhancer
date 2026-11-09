#!/usr/bin/env python3
"""Main Entry Point for AI Video Enhancer (Patent US 2026/0341309 A1).
"""

import sys
import io

# Ensure UTF-8 output across Windows command prompts
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.cli import run_cli

if __name__ == "__main__":
    run_cli()
