#!/usr/bin/env python3
"""Run the bounded n=9 selected-witness incidence frontier scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_incidence_frontier import run_bounded_scan  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_incidence_frontier_bounded.json"


def assert_expected(payload: dict[str, object]) -> None:
    if payload["type"] != "n9_incidence_frontier_bounded_scan_v1":
        raise AssertionError("unexpected payload type")
    seeded = payload["seeded_cases"]
    if not isinstance(seeded, list) or len(seeded) != 1:
        raise AssertionError("missing seeded n=9 rectangle-trap case")
    classification = seeded[0]["classification"]
    if not isinstance(classification, dict):
        raise AssertionError("seeded case classification should be a mapping")
    if classification["status"] != "phi4_rectangle_trap":
        raise AssertionError("registered n=9 seed should be killed by phi4 rectangle trap")
    if classification["rectangle_trap_4_cycles"] != 1:
        raise AssertionError("registered n=9 seed should have one phi4 trap")


def print_summary(payload: dict[str, object]) -> None:
    print("bounded n=9 incidence/CSP frontier scan")
    print(f"nodes visited: {payload['nodes_visited']}")
    print(f"row options considered: {payload['row_options_considered']}")
    print(f"full patterns checked: {payload['full_patterns_checked']}")
    print(f"truncated: {payload['truncated']}")
    print(f"partial rejections: {payload['partial_rejection_counts']}")
    print(f"full classifications: {payload['full_classification_counts']}")
    print(f"accepted frontier count: {payload['accepted_frontier_count']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="write JSON payload here")
    parser.add_argument("--write", action="store_true", help="write --out")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--max-nodes", type=int, default=250_000)
    parser.add_argument("--max-full-patterns", type=int, default=250)
    parser.add_argument("--max-examples", type=int, default=3)
    args = parser.parse_args()

    payload = run_bounded_scan(
        max_nodes=args.max_nodes,
        max_full_patterns=args.max_full_patterns,
        max_examples=args.max_examples,
    )
    if args.assert_expected:
        assert_expected(payload)

    if args.write:
        path = Path(args.out)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.assert_expected:
            print("OK: bounded n=9 frontier expectations verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
