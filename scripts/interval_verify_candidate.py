#!/usr/bin/env python3
"""Conservatively interval-check a saved Erdos #97 numerical candidate."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from erdos97.interval_verify import verify_interval_json


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_path")
    parser.add_argument("--eq-bound", type=float, default=1e-8)
    parser.add_argument("--coord-abs-radius", type=float, default=1e-12)
    parser.add_argument("--coord-rel-radius", type=float, default=1e-12)
    parser.add_argument("--check", action="store_true", help="exit nonzero unless the candidate is certified")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    result = verify_interval_json(
        args.json_path,
        eq_bound=args.eq_bound,
        coord_abs_radius=args.coord_abs_radius,
        coord_rel_radius=args.coord_rel_radius,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    if args.check and not result["ok"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
