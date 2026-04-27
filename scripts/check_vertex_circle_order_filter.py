#!/usr/bin/env python3
"""Check the vertex-circle cyclic-order filter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.search import built_in_patterns  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    find_cyclic_order_with_vertex_circle_filter,
    order_result_to_json,
    search_result_to_json,
    vertex_circle_order_obstruction,
)


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def assert_obstructed(row: dict[str, object]) -> None:
    if row["type"] == "vertex_circle_order_result":
        if not row["obstructed"]:
            raise AssertionError(f"{row['pattern']}: expected vertex-circle obstruction")
        return
    if row["sat"]:
        raise AssertionError(f"{row['pattern']}: expected UNSAT, got {row['order']}")


def assert_sat(row: dict[str, object]) -> None:
    if row["type"] == "vertex_circle_order_result":
        if row["obstructed"]:
            raise AssertionError(f"{row['pattern']}: expected unobstructed order")
        return
    if not row["sat"]:
        raise AssertionError(f"{row['pattern']}: expected SAT")


def print_summary(row: dict[str, object]) -> None:
    if row["type"] == "vertex_circle_order_result":
        result = "OBSTRUCTED" if row["obstructed"] else "PASS"
        print(
            "pattern  n  result      rows  strict edges  self edges  cycle"
        )
        print(
            f"{row['pattern']}  {row['n']}  {result:<10}  "
            f"{row['row_count_completed']}  {row['strict_edge_count']}  "
            f"{len(row['self_edge_conflicts'])}  {row['cycle']}"
        )
        return

    result = "SAT" if row["sat"] else "UNSAT"
    print(
        "pattern  n  constraints  result  nodes  max depth  crossing prunes  vertex prunes  order"
    )
    print(
        f"{row['pattern']}  {row['n']}  {row['crossing_constraint_count']}  "
        f"{result}  {row['nodes_visited']}  {row['max_depth']}  "
        f"{row['crossing_prunes']}  {row['vertex_circle_prunes']}  "
        f"{row['order'] if row['order'] is not None else '-'}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pattern", required=True, help="built-in pattern name")
    parser.add_argument("--order", type=parse_order, help="comma-separated cyclic order")
    parser.add_argument("--search", action="store_true", help="run crossing + vertex-circle search")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a summary")
    parser.add_argument("--assert-obstructed", action="store_true", help="assert obstruction/UNSAT")
    parser.add_argument("--assert-sat", action="store_true", help="assert unobstructed/SAT")
    parser.add_argument("--write-certificate", help="write JSON result to this path")
    parser.add_argument(
        "--max-terminal-conflicts",
        type=int,
        default=128,
        help="maximum UNSAT terminal conflicts to retain; use --full-conflicts for no cap",
    )
    parser.add_argument(
        "--full-conflicts",
        action="store_true",
        help="retain every terminal conflict in UNSAT output",
    )
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern not in patterns:
        raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
    pattern = patterns[args.pattern]

    if args.search:
        max_conflicts = None if args.full_conflicts else args.max_terminal_conflicts
        result = find_cyclic_order_with_vertex_circle_filter(
            pattern.S,
            pattern.name,
            max_terminal_conflicts=max_conflicts,
        )
        row = search_result_to_json(result)
    else:
        if args.order is None:
            raise SystemExit("--order is required unless --search is passed")
        result = vertex_circle_order_obstruction(pattern.S, args.order, pattern.name)
        row = order_result_to_json(result)

    if args.assert_obstructed:
        assert_obstructed(row)
    if args.assert_sat:
        assert_sat(row)

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
        if args.assert_obstructed or args.assert_sat:
            print("OK: vertex-circle expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
