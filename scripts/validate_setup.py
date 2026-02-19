#!/usr/bin/env python3
"""Validate BTT setup: Python version, core packages, required executables."""

from __future__ import annotations

import importlib
import shutil
import subprocess
import sys


def check_python_version() -> bool:
    v = sys.version_info
    print(f"Python version: {v.major}.{v.minor}.{v.micro}")
    if (v.major, v.minor) != (3, 11):
        print("  FAIL: Python 3.11 is required.")
        return False
    print("  OK")
    return True


def check_packages() -> bool:
    required = ["streamlit", "pydub", "yt_dlp", "demucs", "basic_pitch", "music21"]
    all_ok = True
    for pkg in required:
        try:
            mod = importlib.import_module(pkg)
            version = getattr(mod, "__version__", "installed (no version attr)")
            print(f"Package {pkg}: {version}  OK")
        except ImportError:
            print(f"Package {pkg}: NOT FOUND  FAIL")
            all_ok = False
    return all_ok


def check_executables() -> bool:
    tools = {
        "demucs": ["demucs", "--help"],
        "basic-pitch": ["basic-pitch", "--help"],
        "mscore": ["mscore", "--version"],
        "ffmpeg": ["ffmpeg", "-version"],
    }
    all_ok = True
    for name, cmd in tools.items():
        if shutil.which(cmd[0]) is None:
            print(f"Executable {name}: '{cmd[0]}' not found on PATH  FAIL")
            all_ok = False
            continue
        try:
            subprocess.run(cmd, capture_output=True, timeout=10)
            print(f"Executable {name}: OK")
        except Exception as exc:
            print(f"Executable {name}: error ({exc})  FAIL")
            all_ok = False
    return all_ok


def main() -> int:
    print("=== BTT Setup Validation ===\n")

    results = [
        ("Python version", check_python_version()),
        ("Packages", check_packages()),
        ("Executables", check_executables()),
    ]

    print("\n=== Summary ===")
    all_pass = True
    for label, ok in results:
        status = "PASS" if ok else "FAIL"
        print(f"  {label}: {status}")
        if not ok:
            all_pass = False

    if all_pass:
        print("\nAll checks passed.")
        return 0
    else:
        print("\nSome checks failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
