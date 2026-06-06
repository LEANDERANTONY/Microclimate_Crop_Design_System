"""Thin runner: add ``src/`` to the path and invoke the end-to-end pipeline.

Usage:
    uv run python scripts/run_pipeline.py
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agroforestry.cli.run_pipeline import main  # noqa: E402

if __name__ == "__main__":
    main()
