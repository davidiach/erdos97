#!/usr/bin/env python3
"""Run the review-pending exhaustive n=9 vertex-circle finite-case checker."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_exhaustive import (  # noqa: E402
    assert_expected_counts,
    exhaustive_search,
    summary_payload,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_vertex_circle_exhaustive.json"


def print_result(label: str, result: dict[str, object], elapsed: float | None = None) -> None:
    """Print a compact human-readable result block."""
    print(label)
    print(f"row0 choices: {result['row0_choices']}")
    print(f"nodes visited: {result['nodes_visited']}")
    print(f"full assignments: {result['full_assignments']}")
    print(f"counts: {result['counts']}")
    if elapsed is not None:
        print(f"elapsed_seconds: {elapsed:.6f}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--cross-check-only",
        action="store_true",
        help="run only the slower no-vertex-circle-pruning cross-check",
    )
    parser.add_argument(
        "--main-only",
        action="store_true",
        help="run only the vertex-circle-pruned search",
    )
    args = parser.parse_args()

    if args.cross_check_only and args.main_only:
        parser.error("--cross-check-only and --main-only are mutually exclusive")

    if args.cross_check_only:
        start = perf_counter()
        result = exhaustive_search(use_vertex_circle=False).to_json()
        elapsed = perf_counter() - start
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print_result("n=9 cross-check without vertex-circle pruning", result, elapsed)
        return 0

    if args.main_only:
        start = perf_counter()
        result = exhaustive_search(use_vertex_circle=True).to_json()
        elapsed = perf_counter() - start
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print_result("n=9 exhaustive selected-witness search", result, elapsed)
        return 0

    start = perf_counter()
    payload = summary_payload()
    elapsed = perf_counter() - start
    if args.assert_expected:
        assert_expected_counts(payload)

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("review-pending exhaustive n=9 vertex-circle finite-case checker")
        print_result("main search", payload["main_search"])
        print_result(
            "cross-check without vertex-circle pruning",
            payload["cross_check_without_vertex_circle_pruning"],
        )
        print(f"total_elapsed_seconds: {elapsed:.6f}")
        if args.assert_expected:
            print("OK: n=9 vertex-circle exhaustive counts verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
