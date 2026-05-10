#!/usr/bin/env python3
"""Check the two-block fragile-cover vertex-circle extension audit."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_hypergraph import _selected_pair_ok, block6_family  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    StrictInequality,
    UnionFind,
    _all_pairs,
    _find_strict_cycle,
    angular_witness_order,
    pair,
    vertex_circle_order_obstruction,
)


N = 12
ROW_SIZE = 4
ORDER = list(range(N))
PAIR_CAP = 2
INDEGREE_CAP = (2 * (N - 1)) // (ROW_SIZE - 1)
EXPECTED_PRUNED = {
    "result": "closed",
    "nodes": 1752,
    "zero_option_prunes": 37,
    "vc_prunes": {"self_edge": 645, "strict_cycle": 768},
    "solutions": 0,
}
EXPECTED_TERMINAL = {
    "full_extensions": 105978,
    "nodes": 320898,
    "zero_option_prunes": 79547,
    "vertex_circle_status_counts": {"self_edge": 105690, "strict_cycle": 288},
    "strict_edge_count_histogram": {"108": 105978},
}

Rows = dict[int, tuple[int, ...]]


def _fixed_rows() -> Rows:
    """Return the two-block block-6 fragile rows."""

    n, rows = block6_family(2)
    if n != N:
        raise AssertionError(f"unexpected block6 size: {n}")
    return {int(center): tuple(int(v) for v in row) for center, row in rows.items()}


def _options() -> dict[int, list[tuple[int, ...]]]:
    return {
        center: [
            tuple(row)
            for row in combinations(
                [label for label in range(N) if label != center],
                ROW_SIZE,
            )
        ]
        for center in range(N)
    }


def _paircross_ok(
    center: int,
    row: Sequence[int],
    assigned: Mapping[int, Sequence[int]],
) -> bool:
    return all(
        _selected_pair_ok(center, row, other, other_row, ORDER)
        for other, other_row in assigned.items()
    )


def _pair_cap_ok(row: Sequence[int], pair_counts: Counter[tuple[int, int]]) -> bool:
    return all(
        pair_counts[tuple(sorted(raw_pair))] < PAIR_CAP
        for raw_pair in combinations(row, 2)
    )


def _indegree_ok(row: Sequence[int], indegrees: Counter[int]) -> bool:
    return all(indegrees[label] < INDEGREE_CAP for label in row)


def _add_row(
    assigned: Rows,
    pair_counts: Counter[tuple[int, int]],
    indegrees: Counter[int],
    center: int,
    row: tuple[int, ...],
) -> None:
    assigned[center] = row
    pair_counts.update(tuple(sorted(raw_pair)) for raw_pair in combinations(row, 2))
    indegrees.update(row)


def _remove_row(
    assigned: Rows,
    pair_counts: Counter[tuple[int, int]],
    indegrees: Counter[int],
    center: int,
    row: tuple[int, ...],
) -> None:
    for raw_pair in combinations(row, 2):
        pair_counts[tuple(sorted(raw_pair))] -= 1
    for label in row:
        indegrees[label] -= 1
    del assigned[center]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _partial_vertex_circle_status(assigned: Mapping[int, Sequence[int]]) -> tuple[str, int]:
    """Return the partial quotient-obstruction status for assigned rows."""

    uf = UnionFind(_all_pairs(N))
    for center, row in assigned.items():
        base = pair(center, row[0])
        for witness in row[1:]:
            uf.union(base, pair(center, witness))

    edges: list[StrictInequality] = []
    for center, row in assigned.items():
        witnesses = angular_witness_order(ORDER, center, row)
        for outer_start in range(ROW_SIZE):
            for outer_end in range(outer_start + 1, ROW_SIZE):
                for inner_start in range(ROW_SIZE):
                    for inner_end in range(inner_start + 1, ROW_SIZE):
                        if (outer_start, outer_end) == (inner_start, inner_end):
                            continue
                        contains = (
                            outer_start <= inner_start
                            and inner_end <= outer_end
                            and (
                                outer_start < inner_start
                                or inner_end < outer_end
                            )
                        )
                        if not contains:
                            continue
                        outer_pair = pair(witnesses[outer_start], witnesses[outer_end])
                        inner_pair = pair(witnesses[inner_start], witnesses[inner_end])
                        edges.append(
                            StrictInequality(
                                row=center,
                                witness_order=list(witnesses),
                                outer_interval=[outer_start, outer_end],
                                inner_interval=[inner_start, inner_end],
                                outer_pair=outer_pair,
                                inner_pair=inner_pair,
                                outer_class=uf.find(outer_pair),
                                inner_class=uf.find(inner_pair),
                            )
                        )

    self_edges = [edge for edge in edges if edge.outer_class == edge.inner_class]
    if self_edges:
        return "self_edge", len(edges)
    if _find_strict_cycle(edges):
        return "strict_cycle", len(edges)
    return "ok", len(edges)


def _initial_state() -> tuple[Rows, Counter[tuple[int, int]], Counter[int]]:
    assigned: Rows = {}
    pair_counts: Counter[tuple[int, int]] = Counter()
    indegrees: Counter[int] = Counter()
    for center, row in _fixed_rows().items():
        if not _paircross_ok(center, row, assigned):
            raise AssertionError("fixed rows fail pair/crossing check")
        if not _pair_cap_ok(row, pair_counts):
            raise AssertionError("fixed rows fail pair cap")
        if not _indegree_ok(row, indegrees):
            raise AssertionError("fixed rows fail indegree cap")
        _add_row(assigned, pair_counts, indegrees, center, row)
    return assigned, pair_counts, indegrees


def _valid_options(
    center: int,
    options: Mapping[int, Sequence[tuple[int, ...]]],
    assigned: Mapping[int, Sequence[int]],
    pair_counts: Counter[tuple[int, int]],
    indegrees: Counter[int],
) -> list[tuple[int, ...]]:
    return [
        row
        for row in options[center]
        if _paircross_ok(center, row, assigned)
        and _pair_cap_ok(row, pair_counts)
        and _indegree_ok(row, indegrees)
    ]


def pruned_search_payload(*, max_nodes: int = 2_000_000) -> dict[str, Any]:
    """Search for a vertex-circle-clean extension using monotone pruning."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    initial_status, _edge_count = _partial_vertex_circle_status(assigned)
    nodes = 0
    zero_option_prunes = 0
    vc_prunes: Counter[str] = Counter()
    solutions = 0

    def search() -> str | None:
        nonlocal nodes, zero_option_prunes, solutions
        if nodes >= max_nodes:
            return "limit"
        if len(assigned) == N:
            status, _edge_count = _partial_vertex_circle_status(assigned)
            if status == "ok":
                solutions += 1
                return "found"
            vc_prunes[status] += 1
            return None

        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in range(N):
            if center in assigned:
                continue
            viable = _valid_options(
                center,
                options,
                assigned,
                pair_counts,
                indegrees,
            )
            if best_options is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        if best_center is None or not best_options:
            zero_option_prunes += 1
            return None

        for row in best_options:
            nodes += 1
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            status, _edge_count = _partial_vertex_circle_status(assigned)
            if status == "ok":
                result = search()
                if result in {"limit", "found"}:
                    return result
            else:
                vc_prunes[status] += 1
            _remove_row(assigned, pair_counts, indegrees, best_center, row)
        return None

    raw_result = search()
    return {
        "result": "closed" if raw_result is None else raw_result,
        "initial_vc": initial_status,
        "nodes": nodes,
        "max_nodes": max_nodes,
        "zero_option_prunes": zero_option_prunes,
        "vc_prunes": _json_counter(vc_prunes),
        "solutions": solutions,
    }


def terminal_classification_payload() -> dict[str, Any]:
    """Classify every terminal full extension without vertex-circle pruning."""

    assigned, pair_counts, indegrees = _initial_state()
    options = _options()
    nodes = 0
    zero_option_prunes = 0
    full_extensions = 0
    status_counts: Counter[str] = Counter()
    strict_edge_counts: Counter[int] = Counter()

    def search() -> None:
        nonlocal nodes, zero_option_prunes, full_extensions
        if len(assigned) == N:
            full_extensions += 1
            result = vertex_circle_order_obstruction(
                [assigned[center] for center in range(N)],
                ORDER,
                "block6x2_fragile_extension",
            )
            status = (
                "self_edge"
                if result.self_edge_conflicts
                else "strict_cycle"
                if result.cycle_edges
                else "ok"
            )
            status_counts[status] += 1
            strict_edge_counts[result.strict_edge_count] += 1
            return

        best_center: int | None = None
        best_options: list[tuple[int, ...]] | None = None
        for center in range(N):
            if center in assigned:
                continue
            viable = _valid_options(
                center,
                options,
                assigned,
                pair_counts,
                indegrees,
            )
            if best_options is None or len(viable) < len(best_options):
                best_center = center
                best_options = viable
            if not viable:
                break
        if best_center is None or not best_options:
            zero_option_prunes += 1
            return

        for row in best_options:
            nodes += 1
            _add_row(assigned, pair_counts, indegrees, best_center, row)
            search()
            _remove_row(assigned, pair_counts, indegrees, best_center, row)

    search()
    return {
        "full_extensions": full_extensions,
        "nodes": nodes,
        "zero_option_prunes": zero_option_prunes,
        "vertex_circle_status_counts": _json_counter(status_counts),
        "strict_edge_count_histogram": _json_counter(strict_edge_counts),
    }


def audit_payload(*, include_terminal: bool, max_nodes: int = 2_000_000) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "schema": "erdos97.block6_fragile_vertex_circle_extension_audit.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "claim_scope": (
            "Two-block block-6 fragile-cover extension audit in the natural "
            "cyclic order; not a proof of Erdos Problem #97 and not a counterexample."
        ),
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": ORDER,
        "fixed_rows": {str(center): list(row) for center, row in _fixed_rows().items()},
        "pair_cap": PAIR_CAP,
        "selected_indegree_cap": INDEGREE_CAP,
        "pruned_search": pruned_search_payload(max_nodes=max_nodes),
    }
    if include_terminal:
        payload["terminal_classification"] = terminal_classification_payload()
    return payload


def assert_expected(payload: Mapping[str, Any], *, include_terminal: bool) -> None:
    if payload["status"] != "REVIEW_PENDING_DIAGNOSTIC_ONLY":
        raise AssertionError("unexpected status")
    if "not a proof" not in payload["claim_scope"]:
        raise AssertionError("claim scope lost no-proof note")
    pruned = dict(payload["pruned_search"])
    pruned_subset = {key: pruned[key] for key in EXPECTED_PRUNED}
    if pruned_subset != EXPECTED_PRUNED:
        raise AssertionError(f"unexpected pruned search counts: {pruned_subset!r}")
    if include_terminal:
        terminal = dict(payload["terminal_classification"])
        terminal_subset = {key: terminal[key] for key in EXPECTED_TERMINAL}
        if terminal_subset != EXPECTED_TERMINAL:
            raise AssertionError(
                f"unexpected terminal classification counts: {terminal_subset!r}"
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print full JSON payload")
    parser.add_argument(
        "--terminal",
        action="store_true",
        help="also classify every terminal extension without vertex-circle pruning",
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert the current expected audit counts",
    )
    parser.add_argument("--max-nodes", type=int, default=2_000_000)
    args = parser.parse_args()

    payload = audit_payload(include_terminal=args.terminal, max_nodes=args.max_nodes)
    if args.assert_expected:
        assert_expected(payload, include_terminal=args.terminal)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        pruned = payload["pruned_search"]
        print("block6 fragile vertex-circle extension audit")
        print(f"n: {payload['n']}")
        print(f"fixed centers: {sorted(int(k) for k in payload['fixed_rows'])}")
        print(
            "pruned search: "
            f"result={pruned['result']} nodes={pruned['nodes']} "
            f"zero_option_prunes={pruned['zero_option_prunes']} "
            f"vc_prunes={pruned['vc_prunes']} solutions={pruned['solutions']}"
        )
        terminal = payload.get("terminal_classification")
        if terminal is not None:
            print(
                "terminal classification: "
                f"full_extensions={terminal['full_extensions']} "
                f"status_counts={terminal['vertex_circle_status_counts']}"
            )
        if args.assert_expected:
            print("OK: block6 fragile vertex-circle audit matched expected counts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
