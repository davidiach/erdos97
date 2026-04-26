#!/usr/bin/env python3
"""Emit the exact n=7 Fano-incidence enumeration artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n7_fano import enumeration_data, enumeration_summary  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="optional JSON output path for the full artifact")
    parser.add_argument("--summary", action="store_true", help="print only the compact summary")
    parser.add_argument(
        "--check-data",
        type=Path,
        help="compare a checked-in JSON artifact against freshly generated data",
    )
    args = parser.parse_args()

    data = enumeration_data()

    if args.check_data:
        checked_in = json.loads(args.check_data.read_text(encoding="utf-8"))
        if checked_in != data:
            raise SystemExit(f"checked-in artifact is stale or mismatched: {args.check_data}")
        print(f"OK: {args.check_data} matches the generated n=7 Fano enumeration")

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
        return 0

    payload = enumeration_summary() if args.summary else data
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
