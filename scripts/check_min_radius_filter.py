#!/usr/bin/env python3
"""Check the minimum-radius short-chord filter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.min_radius_filter import (  # noqa: E402
    minimum_radius_order_obstruction,
    radius_propagation_order_obstruction,
    radius_result_to_json,
    result_to_json,
)
from erdos97.search import built_in_patterns  # noqa: E402


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def assert_obstructed(row: dict[str, object]) -> None:
    if row["obstructed"] is not True:
        raise AssertionError(f"{row['pattern']}: expected obstruction")


def assert_pass(row: dict[str, object]) -> None:
    if row["obstructed"] is not False:
        raise AssertionError(f"{row['pattern']}: expected pass")


def print_summary(row: dict[str, object]) -> None:
    if row["type"] == "radius_propagation_order_result":
        print(
            "pattern  n  result                         nodes  max depth  "
            "choice count  acyclic choice"
        )
        print(
            f"{row['pattern']}  {row['n']}  {row['status']}  "
            f"{row['nodes_visited']}  {row['max_depth']}  "
            f"{row['short_gap_choice_count']}  "
            f"{row['acyclic_choice'] is not None}"
        )
        return

    result = "OBSTRUCTED" if row["obstructed"] else "PASS"
    print(
        "pattern  n  result      blocked centers  possible minimum centers  "
        "order-free blocked  order-free empty-gap"
    )
    print(
        f"{row['pattern']}  {row['n']}  {result:<10}  "
        f"{len(row['blocked_centers'])}  "
        f"{len(row['possible_min_centers'])}  "
        f"{len(row['order_free_blocked_centers'])}  "
        f"{len(row['order_free_empty_gap_centers'])}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", required=True, help="built-in pattern name")
    parser.add_argument(
        "--order",
        type=parse_order,
        help="comma-separated cyclic order; defaults to natural label order",
    )
    parser.add_argument("--json", action="store_true", help="print JSON instead of a summary")
    parser.add_argument("--assert-obstructed", action="store_true", help="assert obstruction")
    parser.add_argument("--assert-pass", action="store_true", help="assert no obstruction")
    parser.add_argument(
        "--radius-propagation",
        action="store_true",
        help="run the stronger fixed-order radius-propagation cycle search",
    )
    parser.add_argument(
        "--max-nodes",
        type=int,
        help="optional node cap for the radius-propagation search",
    )
    parser.add_argument("--write-certificate", help="write JSON result to this path")
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern not in patterns:
        raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
    pattern = patterns[args.pattern]

    if args.radius_propagation:
        result = radius_propagation_order_obstruction(
            pattern.S,
            order=args.order,
            pattern=pattern.name,
            max_nodes=args.max_nodes,
        )
        row = radius_result_to_json(result)
    else:
        result = minimum_radius_order_obstruction(
            pattern.S,
            order=args.order,
            pattern=pattern.name,
        )
        row = result_to_json(result)

    if args.assert_obstructed:
        assert_obstructed(row)
    if args.assert_pass:
        assert_pass(row)

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(row, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(row, indent=2, sort_keys=True))
    else:
        print_summary(row)
        if args.assert_obstructed or args.assert_pass:
            print("OK: minimum-radius expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
