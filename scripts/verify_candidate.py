#!/usr/bin/env python3
"""Verify a saved Erdős #97 numerical candidate JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from erdos97.search import verify_json


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("json_path")
    ap.add_argument("--tol", type=float, default=1e-8)
    ap.add_argument("--min-margin", type=float, default=1e-8)
    args = ap.parse_args()
    print(json.dumps(verify_json(args.json_path, tol=args.tol, min_margin=args.min_margin), indent=2))


if __name__ == "__main__":
    main()
