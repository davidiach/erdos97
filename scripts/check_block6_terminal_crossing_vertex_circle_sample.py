#!/usr/bin/env python3
"""Sample crossing-order vertex-circle status for block-6 terminal extensions."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.incidence_filters import (  # noqa: E402
    Chord,
    chords_cross_in_order,
    phi_map,
)
from erdos97.sparse_frontier import normalize_cyclic_order  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    vertex_circle_order_obstruction,
)
from scripts.check_block6_fragile_vertex_circle_extension import (  # noqa: E402
    N,
    _add_row,
    _initial_state,
    _options,
    _remove_row,
    _valid_options,
)

Rows = list[list[int]]
Constraint = tuple[Chord, Chord]

DEFAULT_LIMIT = 100
EXPECTED_DEFAULT_SUMMARY = {
    "terminal_extensions_examined": 100,
    "total_crossing_orders": 440,
    "extensions_with_vc_clean_crossing_order": 0,
    "vertex_circle_order_status_counts": {"self_edge": 440},
    "max_crossing_order_count": 15,
    "crossing_search_node_min": 40,
    "crossing_search_node_max": 272,
    "order_count_histogram": {
        "2": 31,
        "3": 18,
        "4": 24,
        "5": 3,
        "6": 5,
        "8": 8,
        "9": 3,
        "10": 2,
        "11": 3,
        "12": 2,
        "15": 1,
    },
    "constraint_order_histogram": {
        "16,2": 1,
        "16,3": 3,
        "16,5": 1,
        "16,8": 1,
        "16,11": 1,
        "16,15": 1,
        "17,2": 3,
        "17,3": 3,
        "17,4": 3,
        "17,5": 2,
        "17,6": 1,
        "17,8": 4,
        "17,9": 1,
        "17,10": 1,
        "17,11": 2,
        "18,2": 11,
        "18,3": 1,
        "18,4": 10,
        "18,6": 1,
        "18,8": 2,
        "18,9": 1,
        "18,10": 1,
        "18,12": 1,
        "19,2": 12,
        "19,3": 4,
        "19,4": 9,
        "19,6": 2,
        "19,8": 1,
        "19,12": 1,
        "20,2": 3,
        "20,3": 5,
        "20,4": 2,
        "20,6": 1,
        "20,9": 1,
        "21,2": 1,
        "21,3": 2,
    },
}


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _json_pair_counter(counter: Counter[tuple[int, int]]) -> dict[str, int]:
    return {
        f"{left},{right}": int(counter[(left, right)])
        for left, right in sorted(counter)
    }


def terminal_extensions(limit: int) -> Iterator[Rows]:
    """Yield the first deterministic terminal full extensions."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    yielded = 0

    def search() -> Iterator[Rows]:
        nonlocal yielded
        if yielded >= limit:
            return
        if len(assigned) == N:
            yielded += 1
            yield [list(assigned[center]) for center in range(N)]
            return

        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in range(N):
            if center in assigned:
                continue
            viable = _valid_options(center, options, assigned, pair_counts, indegrees)
            if best_options is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        if best_center is None or not best_options:
            return

        for row in best_options:
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            yield from search()
            _remove_row(assigned, pair_counts, indegrees, best_center, row)
            if yielded >= limit:
                return

    yield from search()


def enumerate_crossing_orders(rows: Rows) -> tuple[list[list[int]], int, int]:
    """Enumerate normalized cyclic orders satisfying two-overlap crossings."""

    constraints: list[Constraint] = sorted(phi_map(rows).items())
    labels = set(range(len(rows)))
    constraint_label_sets = [
        set(source) | set(target) for source, target in constraints
    ]
    label_to_constraints: dict[int, list[int]] = {label: [] for label in labels}
    for idx, constraint_labels in enumerate(constraint_label_sets):
        for label in constraint_labels:
            label_to_constraints[label].append(idx)

    orders: set[tuple[int, ...]] = set()
    nodes_visited = 0

    def completed_failure(
        order: Sequence[int],
        placed: set[int],
        affected_labels: set[int] | None = None,
    ) -> bool:
        if affected_labels is None:
            candidate_idxs = range(len(constraints))
        else:
            idxs: set[int] = set()
            for label in affected_labels:
                idxs.update(label_to_constraints[label])
            candidate_idxs = sorted(idxs)
        for idx in candidate_idxs:
            if constraint_label_sets[idx] <= placed:
                source, target = constraints[idx]
                if not chords_cross_in_order(source, target, order):
                    return True
        return False

    def choose_label(placed: set[int]) -> int:
        def score(label: int) -> tuple[int, int, int, int, int]:
            touches = [
                len(constraint_label_sets[idx] & placed)
                for idx in label_to_constraints[label]
            ]
            return (
                sum(count == 3 for count in touches),
                sum(count == 2 for count in touches),
                sum(count == 1 for count in touches),
                len(label_to_constraints[label]),
                -label,
            )

        return max(labels - placed, key=score)

    def search(order: list[int], placed: set[int]) -> None:
        nonlocal nodes_visited
        nodes_visited += 1
        if len(placed) == len(rows):
            if not completed_failure(order, placed):
                orders.add(tuple(normalize_cyclic_order(order)))
            return

        label = choose_label(placed)
        for position in range(1, len(order) + 1):
            candidate_order = order[:position] + [label] + order[position:]
            candidate_placed = placed | {label}
            if not completed_failure(candidate_order, candidate_placed, {label}):
                search(candidate_order, candidate_placed)

    search([0], {0})
    return [list(order) for order in sorted(orders)], nodes_visited, len(constraints)


def _vertex_circle_status(rows: Rows, order: Sequence[int]) -> str:
    result = vertex_circle_order_obstruction(rows, list(order), "block6_sample")
    if result.self_edge_conflicts:
        return "self_edge"
    if result.cycle_edges:
        return "strict_cycle"
    return "ok"


def audit(limit: int = DEFAULT_LIMIT) -> dict[str, Any]:
    """Return the sampled crossing-order vertex-circle audit."""

    status_counts: Counter[str] = Counter()
    order_count_histogram: Counter[int] = Counter()
    constraint_order_histogram: Counter[tuple[int, int]] = Counter()
    crossing_node_counts: list[int] = []
    clean_extension_records: list[dict[str, object]] = []
    sample_records: list[dict[str, object]] = []

    for extension_index, rows in enumerate(terminal_extensions(limit), start=1):
        crossing_orders, nodes, constraint_count = enumerate_crossing_orders(rows)
        crossing_node_counts.append(nodes)
        order_count_histogram[len(crossing_orders)] += 1
        constraint_order_histogram[(constraint_count, len(crossing_orders))] += 1

        local_status_counts: Counter[str] = Counter()
        clean_orders: list[list[int]] = []
        for order in crossing_orders:
            status = _vertex_circle_status(rows, order)
            status_counts[status] += 1
            local_status_counts[status] += 1
            if status == "ok":
                clean_orders.append(order)

        if clean_orders:
            clean_extension_records.append(
                {
                    "extension_index": extension_index,
                    "clean_crossing_orders": clean_orders,
                    "rows": {str(center): row for center, row in enumerate(rows)},
                }
            )
        if len(sample_records) < 5:
            sample_records.append(
                {
                    "extension_index": extension_index,
                    "crossing_constraint_count": constraint_count,
                    "crossing_order_count": len(crossing_orders),
                    "crossing_search_nodes": nodes,
                    "vertex_circle_status_counts": _json_counter(local_status_counts),
                    "first_row1": rows[1],
                }
            )

    examined = sum(order_count_histogram.values())
    total_crossing_orders = sum(status_counts.values())
    summary = {
        "terminal_extensions_examined": examined,
        "total_crossing_orders": total_crossing_orders,
        "extensions_with_vc_clean_crossing_order": len(clean_extension_records),
        "vertex_circle_order_status_counts": _json_counter(status_counts),
        "max_crossing_order_count": max(order_count_histogram, default=0),
        "crossing_search_node_min": min(crossing_node_counts, default=0),
        "crossing_search_node_max": max(crossing_node_counts, default=0),
        "order_count_histogram": _json_counter(order_count_histogram),
        "constraint_order_histogram": _json_pair_counter(constraint_order_histogram),
    }
    return {
        "schema": "erdos97.block6_terminal_crossing_vertex_circle_sample.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Deterministic first-terminal-extension sample for the two-block "
            "block-6 fragile family. This is not an all-extension proof, not "
            "a proof of Erdos Problem #97, and not a counterexample."
        ),
        "terminal_extension_limit": limit,
        "summary": summary,
        "sample_records": sample_records,
        "first_clean_extension_record": (
            clean_extension_records[0] if clean_extension_records else None
        ),
        "interpretation": (
            "The default sample checks the first 100 deterministic terminal "
            "full extensions from the natural-order block-6 audit across all "
            "their two-overlap crossing-compatible cyclic orders. The default "
            "packet finds no vertex-circle-clean crossing order in that sample."
        ),
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    if payload["terminal_extension_limit"] != DEFAULT_LIMIT:
        raise AssertionError("expected default sample limit")
    if payload["summary"] != EXPECTED_DEFAULT_SUMMARY:
        raise AssertionError(f"unexpected summary: {payload['summary']!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the default expected sample counts",
    )
    args = parser.parse_args()

    payload = audit(limit=args.limit)
    if args.assert_expected:
        assert_expected(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print("block6 terminal crossing vertex-circle sample")
        print(f"terminal extensions: {summary['terminal_extensions_examined']}")
        print(f"crossing orders: {summary['total_crossing_orders']}")
        print(
            "vc-clean extensions: "
            f"{summary['extensions_with_vc_clean_crossing_order']}"
        )
        print(f"status counts: {summary['vertex_circle_order_status_counts']}")
        if args.assert_expected:
            print("OK: expected block6 crossing-VC sample counts verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
