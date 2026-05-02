#!/usr/bin/env python3
"""Analyze sparse witness-pair sources for selected-witness patterns."""

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
from erdos97.sparse_frontier import (  # noqa: E402
    sample_empty_gap_orders,
    sample_radius_propagation_orders,
    search_adversarial_orders,
    sparse_frontier_summary,
)

FRONTIER_PATTERNS = (
    "C19_skew",
    "C13_sidon_1_2_4_10",
    "C25_sidon_2_5_9_14",
    "C29_sidon_1_3_7_15",
)


def parse_order(raw: str) -> list[int]:
    try:
        return [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid comma-separated order: {raw}") from exc


def print_summary(rows: list[dict[str, object]]) -> None:
    print(
        "pattern  n  all-pair-sources  consecutive-sources  "
        "uncovered-consecutive-rows  order-free-blocked  "
        "order-free-empty-gap  empty-radius-choice"
    )
    for row in rows:
        n = int(row["n"])
        uncovered = len(row["rows_with_uncovered_consecutive_pair"])
        blocked = len(row["order_free_blocked_rows"])
        empty_gap = len(row["order_free_empty_gap_rows"])
        print(
            f"{row['pattern']}  {n}  "
            f"{row['all_pair_source_count_histogram']}  "
            f"{row['consecutive_pair_source_count_histogram']}  "
            f"{uncovered}/{n}  {blocked}  "
            f"{empty_gap}/{n}  "
            f"{row['trivial_empty_radius_choice_exists']}"
        )


def print_sample_summary(rows: list[dict[str, object]]) -> None:
    has_radius = bool(rows and "radius_status_histogram" in rows[0])
    if has_radius:
        print(
            "pattern  n  orders  empty-choice  min-uncovered-rows  "
            "row-count-histogram  radius-status  no-empty-radius-status  "
            "natural-empty-choice  natural-radius-status"
        )
    else:
        print(
            "pattern  n  orders  empty-choice  min-uncovered-rows  "
            "row-count-histogram  natural-empty-choice"
        )
    for row in rows:
        natural = row["natural_order"]
        natural_empty = (
            natural["trivial_empty_radius_choice_exists"]
            if isinstance(natural, dict)
            else None
        )
        if has_radius:
            natural_radius = (
                natural["radius_propagation"]["status"]
                if isinstance(natural, dict)
                else None
            )
            print(
                f"{row['pattern']}  {row['n']}  {row['orders_checked']}  "
                f"{row['empty_choice_orders']}  "
                f"{row['min_rows_with_uncovered_consecutive_pair']}  "
                f"{row['rows_with_uncovered_consecutive_histogram']}  "
                f"{row['radius_status_histogram']}  "
                f"{row['no_empty_choice_radius_status_histogram']}  "
                f"{natural_empty}  {natural_radius}"
            )
        else:
            print(
                f"{row['pattern']}  {row['n']}  {row['orders_checked']}  "
                f"{row['empty_choice_orders']}  "
                f"{row['min_rows_with_uncovered_consecutive_pair']}  "
                f"{row['rows_with_uncovered_consecutive_histogram']}  "
                f"{natural_empty}"
            )


def print_adversarial_summary(rows: list[dict[str, object]]) -> None:
    print(
        "pattern  n  evaluated  min-uncovered-rows  "
        "row-count-histogram  radius-status  best-radius-status  "
        "best-edges  optimized-min-edges  best-explored"
    )
    for row in rows:
        examples = row["best_examples"]
        best = examples[0] if isinstance(examples, list) and examples else None
        radius = (
            best["radius_propagation"]
            if isinstance(best, dict)
            else {"status": None, "acyclic_edge_count": None, "explored_nodes": None}
        )
        optimized = (
            best["radius_choice_minimization"]
            if isinstance(best, dict) and "radius_choice_minimization" in best
            else {"edge_count": None}
        )
        print(
            f"{row['pattern']}  {row['n']}  {row['orders_evaluated']}  "
            f"{row['min_rows_with_uncovered_consecutive_pair']}  "
            f"{row['rows_with_uncovered_consecutive_histogram']}  "
            f"{row['radius_status_histogram']}  "
            f"{radius['status']}  {radius['acyclic_edge_count']}  "
            f"{optimized['edge_count']}  "
            f"{radius['explored_nodes']}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--pattern", help="built-in pattern name")
    target.add_argument(
        "--frontier",
        action="store_true",
        help="analyze C19 plus the Sidon frontier patterns",
    )
    target.add_argument(
        "--all-built-ins",
        action="store_true",
        help="analyze every built-in pattern",
    )
    parser.add_argument(
        "--order",
        type=parse_order,
        help="comma-separated cyclic order; defaults to natural order",
    )
    parser.add_argument(
        "--max-row-examples",
        type=int,
        default=4,
        help="number of row examples to include in JSON",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-empty-choice", action="store_true")
    parser.add_argument(
        "--sample-orders",
        type=int,
        help="sample this many random cyclic orders in addition to natural order",
    )
    parser.add_argument(
        "--adversarial-orders",
        type=int,
        help="sample this many random starts and hill-climb adversarial cyclic orders",
    )
    parser.add_argument("--sample-seed", type=int, default=0)
    parser.add_argument(
        "--sample-radius-propagation",
        action="store_true",
        help="with --sample-orders, run the full radius-propagation filter per order",
    )
    parser.add_argument(
        "--radius-node-limit",
        type=int,
        default=100_000,
        help="node limit for the sampled radius-propagation filter",
    )
    parser.add_argument("--adversarial-restarts", type=int, default=8)
    parser.add_argument("--adversarial-steps", type=int, default=200)
    args = parser.parse_args()

    patterns = built_in_patterns()
    if args.pattern:
        if args.pattern not in patterns:
            raise SystemExit(f"unknown pattern {args.pattern}; known: {', '.join(patterns)}")
        names = [args.pattern]
    elif args.frontier:
        names = list(FRONTIER_PATTERNS)
    else:
        names = list(patterns)

    if args.sample_orders is not None and args.order is not None:
        raise SystemExit("--sample-orders cannot be combined with --order")
    if args.adversarial_orders is not None and args.order is not None:
        raise SystemExit("--adversarial-orders cannot be combined with --order")
    if args.sample_orders is not None and args.adversarial_orders is not None:
        raise SystemExit("--sample-orders cannot be combined with --adversarial-orders")
    if args.sample_radius_propagation and args.sample_orders is None:
        raise SystemExit("--sample-radius-propagation requires --sample-orders")

    if args.sample_orders is None:
        if args.adversarial_orders is None:
            rows = [
                sparse_frontier_summary(
                    name,
                    patterns[name].S,
                    order=args.order,
                    max_row_examples=args.max_row_examples,
                )
                for name in names
            ]
        else:
            rows = [
                search_adversarial_orders(
                    name,
                    patterns[name].S,
                    random_samples=args.adversarial_orders,
                    seed=args.sample_seed,
                    include_natural=True,
                    restarts=args.adversarial_restarts,
                    local_steps=args.adversarial_steps,
                    max_examples=args.max_row_examples,
                    node_limit=args.radius_node_limit,
                )
                for name in names
            ]
    elif args.sample_radius_propagation:
        rows = [
            sample_radius_propagation_orders(
                name,
                patterns[name].S,
                random_samples=args.sample_orders,
                seed=args.sample_seed,
                include_natural=True,
                max_examples=args.max_row_examples,
                node_limit=args.radius_node_limit,
            )
            for name in names
        ]
    else:
        rows = [
            sample_empty_gap_orders(
                name,
                patterns[name].S,
                random_samples=args.sample_orders,
                seed=args.sample_seed,
                include_natural=True,
                max_examples=args.max_row_examples,
            )
            for name in names
        ]

    if args.assert_empty_choice:
        for row in rows:
            if args.sample_orders is None:
                ok = row["trivial_empty_radius_choice_exists"]
            else:
                ok = row["empty_choice_orders"] == row["orders_checked"]
            if not ok:
                raise AssertionError(f"{row['pattern']}: expected empty radius choice")

    payload: dict[str, object] | list[dict[str, object]]
    payload = rows[0] if len(rows) == 1 else rows
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        if args.adversarial_orders is not None:
            print_adversarial_summary(rows)
        elif args.sample_orders is None:
            print_summary(rows)
        else:
            print_sample_summary(rows)
        if args.assert_empty_choice:
            print("OK: empty radius choice verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
