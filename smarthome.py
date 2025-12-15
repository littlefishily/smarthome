#!/usr/bin/env python3
"""Launcher for running the project from the repository root.

Usage:
  python3 smarthome.py
  or
  python3 -m src.main
"""
import asyncio
import os
import sys

# Ensure repo root is on sys.path
ROOT = os.path.dirname(__file__)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.main import main


if __name__ == '__main__':
    asyncio.run(main())
