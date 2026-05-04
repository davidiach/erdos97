#!/usr/bin/env python3
"""Extract local row-core certificates for n=9 vertex-circle motif families."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_local_core_counts,
    local_core_summary,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_vertex_circle_local_cores.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = local_core_summary()
    if args.assert_expected:
        assert_expected_local_core_counts(payload)
    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n=9 vertex-circle local-core diagnostic")
        print(f"dihedral motif families: {payload['family_count']}")
        print(f"core size counts: {payload['core_size_counts']}")
        print(f"status/core size counts: {payload['status_core_size_counts']}")
        print(f"max core size: {payload['max_core_size']}")
        if args.assert_expected:
            print("OK: local core counts verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
