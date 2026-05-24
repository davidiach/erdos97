#!/usr/bin/env python3
"""Verify a saved Erdős #97 numerical candidate JSON."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from erdos97.search import verify_json


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path")
    parser.add_argument("--tol", type=float, default=1e-8)
    parser.add_argument("--min-margin", type=float, default=1e-8)
    args = parser.parse_args()
    result = verify_json(args.json_path, tol=args.tol, min_margin=args.min_margin)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result.get("ok_at_tol") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
