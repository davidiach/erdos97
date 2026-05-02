#!/usr/bin/env python3
"""Find fixed-selection stuck sets for selected-witness systems."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.search import built_in_patterns  # noqa: E402
from erdos97.stuck_sets import (  # noqa: E402
    find_minimal_stuck_sets,
    forward_ear_order,
    greedy_peeling_run,
    pattern_filter_snapshot,
    result_to_json,
)


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def matrix_to_rows(matrix: Sequence[Sequence[int]]) -> list[list[int]]:
    return [
        [int(label) for label, value in enumerate(row) if int(value)]
        for row in matrix
    ]


def load_n8_survivors(path: Path) -> list[tuple[str, list[list[int]]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    out: list[tuple[str, list[list[int]]]] = []
    for entry in data:
        out.append((f"n8_class_{entry['id']}", matrix_to_rows(entry["rows"])))
    return out


def default_max_size(n: int, requested: int | None) -> int:
    if requested is not None:
        return requested
    return n if n <= 20 else 12


def analyze_one(
    name: str,
    rows: list[list[int]],
    order: list[int] | None,
    requested_min_size: int | None,
    requested_max_size: int | None,
    max_examples: int,
    radius_node_limit: int,
    fragile_cover_max_size: int | None,
) -> dict[str, object]:
    max_size = default_max_size(len(rows), requested_max_size)
    stuck = find_minimal_stuck_sets(
        rows,
        min_size=requested_min_size,
        max_size=max_size,
        max_examples=max_examples,
    )
    forward = forward_ear_order(rows)
    greedy = greedy_peeling_run(rows)
    filters = pattern_filter_snapshot(
        rows,
        order=order,
        radius_node_limit=radius_node_limit,
        fragile_cover_max_size=fragile_cover_max_size,
        fragile_cover_max_examples=max_examples,
    )
    return result_to_json(name, rows, stuck, forward, greedy_result=greedy, filters=filters)


def assert_expectations(rows: list[dict[str, object]], assert_stuck: bool, assert_no_stuck: bool) -> None:
    for row in rows:
        status = row["key_peeling_status"]
        if assert_stuck and status != "STUCK_SET_FOUND":
            raise AssertionError(f"{row['pattern']}: expected a stuck set, got {status}")
        if assert_no_stuck and status != "NO_STUCK_SETS":
            raise AssertionError(f"{row['pattern']}: expected no stuck sets, got {status}")


def fragile_cover_label(fragile_stats: dict[str, object]) -> str:
    """Return a compact cover label without overstating truncated searches."""

    if fragile_stats["status"] == "SKIPPED_LARGE_N":
        return "SKIP"
    if fragile_stats["cover_exists"]:
        min_size = fragile_stats["min_cover_size"]
        return f"YES({min_size})" if min_size is not None else "YES"
    if fragile_stats.get("search_complete"):
        return "NO"
    searched = fragile_stats.get("searched_up_to_size")
    if searched is not None:
        return f"NONE<={searched}"
    return "UNKNOWN"


def print_summary(rows: list[dict[str, object]]) -> None:
    print(
        "pattern  n  forward-ear  greedy-terminal  key-peeling  radius  "
        "fragile-cover  searched  min-size  examples"
    )
    for row in rows:
        forward = "YES" if row["forward_ear_order"]["exists"] else "NO"
        greedy = row["greedy_reverse_peeling"]
        terminal_size = "-" if greedy is None else str(len(greedy["terminal_vertices"]))
        filters = row["filters"]
        radius = filters["radius_propagation"]["status"]
        fragile_stats = filters["fragile_cover"]["cover_stats"]
        fragile = fragile_cover_label(fragile_stats)
        search = row["stuck_search"]
        min_size = search["minimal_size"]
        min_text = "-" if min_size is None else str(min_size)
        print(
            f"{row['pattern']}  {row['n']}  {forward:<11}  "
            f"{terminal_size:<15}  "
            f"{row['key_peeling_status']:<24}  "
            f"{radius:<24}  "
            f"{fragile:<13}  "
            f"{search['searched_up_to_size']}  {min_text:<8}  "
            f"{len(search['examples'])}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--pattern", help="built-in pattern name")
    target.add_argument("--all-built-ins", action="store_true", help="analyze all built-in patterns")
    target.add_argument(
        "--n8-survivors",
        type=Path,
        help="analyze rows from an n=8 survivor JSON file",
    )
    parser.add_argument(
        "--order",
        type=parse_order,
        help="comma-separated cyclic order for order-sensitive filters",
    )
    parser.add_argument(
        "--min-set-size",
        type=int,
        help="smallest subset size to search; defaults to 4",
    )
    parser.add_argument(
        "--max-set-size",
        type=int,
        help="largest subset size to search; defaults to n for n<=20, else 12",
    )
    parser.add_argument("--max-examples", type=int, default=8, help="stored examples at minimal size")
    parser.add_argument(
        "--radius-node-limit",
        type=int,
        default=100_000,
        help="backtracking node limit for the radius propagation filter",
    )
    parser.add_argument(
        "--fragile-cover-max-size",
        type=int,
        help="maximum fragile-center subset size to enumerate for cover stats",
    )
    parser.add_argument("--json", action="store_true", help="print JSON instead of a compact summary")
    parser.add_argument("--write-certificate", type=Path, help="write JSON result to this path")
    parser.add_argument("--assert-stuck", action="store_true", help="assert every target has a stuck set")
    parser.add_argument(
        "--assert-no-stuck",
        action="store_true",
        help="assert every target has a complete no-stuck certificate",
    )
    args = parser.parse_args()

    patterns = built_in_patterns()
    targets: list[tuple[str, list[list[int]]]]
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        pat = patterns[args.pattern]
        targets = [(pat.name, pat.S)]
    elif args.all_built_ins:
        targets = [(pat.name, pat.S) for pat in patterns.values()]
    else:
        if not args.n8_survivors.exists():
            raise SystemExit(f"n8 survivor file does not exist: {args.n8_survivors}")
        targets = load_n8_survivors(args.n8_survivors)

    rows = [
        analyze_one(
            name,
            selected_rows,
            order=args.order,
            requested_min_size=args.min_set_size,
            requested_max_size=args.max_set_size,
            max_examples=args.max_examples,
            radius_node_limit=args.radius_node_limit,
            fragile_cover_max_size=args.fragile_cover_max_size,
        )
        for name, selected_rows in targets
    ]

    assert_expectations(rows, args.assert_stuck, args.assert_no_stuck)

    payload: dict[str, object] | list[dict[str, object]]
    payload = rows[0] if len(rows) == 1 else rows

    if args.write_certificate:
        args.write_certificate.parent.mkdir(parents=True, exist_ok=True)
        args.write_certificate.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(rows)
        if args.assert_stuck or args.assert_no_stuck:
            print("OK: stuck-set expectation verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
