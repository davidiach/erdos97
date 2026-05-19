#!/usr/bin/env python3
"""Audit no-reciprocal n=9 selected-row patterns by strict Kalmanson implications."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

N = 9
TARGET_OUTDEGREE = 4
EXPECTED_REGULAR_TOURNAMENTS = 3_230_080

Edge = tuple[int, int]
Rows = tuple[tuple[int, ...], ...]


def edge(i: int, j: int) -> Edge:
    return (i, j) if i < j else (j, i)


def build_edges(n: int = N) -> tuple[Edge, ...]:
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


EDGES = build_edges()
EDGE_INDEX = {e: index for index, e in enumerate(EDGES)}


def build_kalmanson_inequalities(n: int = N) -> tuple[tuple[int, int, int, int], ...]:
    inequalities: list[tuple[int, int, int, int]] = []
    for i, j, k, m in combinations(range(n), 4):
        inequalities.append(
            (
                EDGE_INDEX[edge(i, j)],
                EDGE_INDEX[edge(k, m)],
                EDGE_INDEX[edge(i, k)],
                EDGE_INDEX[edge(j, m)],
            )
        )
        inequalities.append(
            (
                EDGE_INDEX[edge(i, m)],
                EDGE_INDEX[edge(j, k)],
                EDGE_INDEX[edge(i, k)],
                EDGE_INDEX[edge(j, m)],
            )
        )
    return tuple(inequalities)


KALMANSON_INEQUALITIES = build_kalmanson_inequalities()


def build_remaining_incidence(n: int = N) -> tuple[tuple[int, ...], ...]:
    remaining: list[list[int]] = [[0] * n for _ in range(len(EDGES) + 1)]
    for index in range(len(EDGES) - 1, -1, -1):
        remaining[index][:] = remaining[index + 1][:]
        u, v = EDGES[index]
        remaining[index][u] += 1
        remaining[index][v] += 1
    return tuple(tuple(row) for row in remaining)


REMAINING_INCIDENCE = build_remaining_incidence()


def selected_rows_from_tails(tails: Iterable[int]) -> Rows:
    rows: list[list[int]] = [[] for _ in range(N)]
    for (u, v), tail in zip(EDGES, tails):
        if tail == u:
            rows[u].append(v)
        elif tail == v:
            rows[v].append(u)
        else:
            raise ValueError(f"tail {tail} is not incident to edge {(u, v)}")
    return tuple(tuple(row) for row in rows)


def tails_from_selected_rows(rows: Rows) -> tuple[int, ...]:
    if len(rows) != N:
        raise ValueError(f"expected {N} rows")
    row_sets = [set(row) for row in rows]
    tails: list[int] = []
    for u, v in EDGES:
        u_selects_v = v in row_sets[u]
        v_selects_u = u in row_sets[v]
        if u_selects_v == v_selects_u:
            raise ValueError(f"edge {(u, v)} is not selected in exactly one direction")
        tails.append(u if u_selects_v else v)
    return tuple(tails)


def add_implication(adj: list[int], source: int, target: int) -> None:
    adj[source] |= 1 << target


def strict_implication_graph(tails: tuple[int, ...]) -> tuple[int, ...]:
    """Return row-variable implications forced by one-term Kalmanson cancellation."""

    adj = [0] * N
    for left_a, left_b, right_a, right_b in KALMANSON_INEQUALITIES:
        la = tails[left_a]
        lb = tails[left_b]
        ra = tails[right_a]
        rb = tails[right_b]
        if la == ra:
            add_implication(adj, lb, rb)
        if la == rb:
            add_implication(adj, lb, ra)
        if lb == ra:
            add_implication(adj, la, rb)
        if lb == rb:
            add_implication(adj, la, ra)
    return tuple(adj)


def transitive_closure(adj: tuple[int, ...], *, include_self: bool = True) -> tuple[int, ...]:
    reach = [
        row | ((1 << index) if include_self else 0)
        for index, row in enumerate(adj)
    ]
    for k in range(N):
        bit = 1 << k
        kth = reach[k]
        for i in range(N):
            if reach[i] & bit:
                reach[i] |= kth
    return tuple(reach)


def is_strongly_connected(adj: tuple[int, ...]) -> bool:
    all_mask = (1 << N) - 1
    return all(row == all_mask for row in transitive_closure(adj))


def has_strict_cycle(adj: tuple[int, ...]) -> bool:
    closure = transitive_closure(adj, include_self=False)
    return any(closure[index] & (1 << index) for index in range(N))


@dataclass(frozen=True)
class RegularTournamentAudit:
    total_regular_tournaments: int
    strong_connectivity_failures: int
    acyclic_implication_failures: int
    first_strong_failure_rows: Rows | None
    first_acyclic_failure_rows: Rows | None
    checked_all: bool


def audit_regular_tournaments(limit: int | None = None) -> RegularTournamentAudit:
    tails = [-1] * len(EDGES)
    outdegree = [0] * N
    total = 0
    strong_failures = 0
    acyclic_failures = 0
    first_strong_failure: Rows | None = None
    first_acyclic_failure: Rows | None = None

    def feasible(next_index: int) -> bool:
        remaining = REMAINING_INCIDENCE[next_index]
        for vertex in range(N):
            degree = outdegree[vertex]
            if degree > TARGET_OUTDEGREE:
                return False
            if degree + remaining[vertex] < TARGET_OUTDEGREE:
                return False
        return True

    def recurse(index: int) -> None:
        nonlocal total, strong_failures, acyclic_failures
        nonlocal first_strong_failure, first_acyclic_failure

        if limit is not None and total >= limit:
            return
        if index == len(EDGES):
            total += 1
            frozen_tails = tuple(tails)
            adj = strict_implication_graph(frozen_tails)
            rows = None
            if not is_strongly_connected(adj):
                strong_failures += 1
                if first_strong_failure is None:
                    rows = selected_rows_from_tails(frozen_tails)
                    first_strong_failure = rows
            if not has_strict_cycle(adj):
                acyclic_failures += 1
                if first_acyclic_failure is None:
                    if rows is None:
                        rows = selected_rows_from_tails(frozen_tails)
                    first_acyclic_failure = rows
            return

        u, v = EDGES[index]

        tails[index] = u
        outdegree[u] += 1
        if feasible(index + 1):
            recurse(index + 1)
        outdegree[u] -= 1

        tails[index] = v
        outdegree[v] += 1
        if feasible(index + 1):
            recurse(index + 1)
        outdegree[v] -= 1

        tails[index] = -1

    recurse(0)
    return RegularTournamentAudit(
        total_regular_tournaments=total,
        strong_connectivity_failures=strong_failures,
        acyclic_implication_failures=acyclic_failures,
        first_strong_failure_rows=first_strong_failure,
        first_acyclic_failure_rows=first_acyclic_failure,
        checked_all=limit is None or total < limit,
    )


def rows_json(rows: Rows | None) -> list[list[int]] | None:
    if rows is None:
        return None
    return [list(row) for row in rows]


def audit_json(audit: RegularTournamentAudit) -> dict[str, object]:
    return {
        "status": "EXACT_N9_NO_RECIPROCAL_SUBCASE_AUDIT",
        "claim_scope": (
            "For n=9 selected-witness systems with no reciprocal selected pair, "
            "the selected graph is a labelled regular tournament. This audit "
            "checks those tournament patterns only under the fixed cyclic order."
        ),
        "n": N,
        "target_outdegree": TARGET_OUTDEGREE,
        "kalmanson_inequalities": len(KALMANSON_INEQUALITIES),
        "total_regular_tournaments": audit.total_regular_tournaments,
        "strong_connectivity_failures": audit.strong_connectivity_failures,
        "acyclic_implication_failures": audit.acyclic_implication_failures,
        "first_strong_failure_rows": rows_json(audit.first_strong_failure_rows),
        "first_acyclic_failure_rows": rows_json(audit.first_acyclic_failure_rows),
        "checked_all": audit.checked_all,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    audit = audit_regular_tournaments(limit=args.limit)
    if args.assert_expected:
        if args.limit is not None:
            raise AssertionError("--assert-expected requires a full audit without --limit")
        if audit.total_regular_tournaments != EXPECTED_REGULAR_TOURNAMENTS:
            raise AssertionError(
                f"expected {EXPECTED_REGULAR_TOURNAMENTS} regular tournaments, "
                f"got {audit.total_regular_tournaments}"
            )
        if audit.strong_connectivity_failures != 0:
            raise AssertionError("expected zero strong-connectivity failures")
        if audit.acyclic_implication_failures != 0:
            raise AssertionError("expected zero acyclic-implication failures")

    if args.json:
        print(json.dumps(audit_json(audit), indent=2, sort_keys=True))
    else:
        print("n=9 regular-tournament Kalmanson audit")
        print(f"regular tournaments checked: {audit.total_regular_tournaments}")
        print(f"Kalmanson inequalities per order: {len(KALMANSON_INEQUALITIES)}")
        print(f"strong-connectivity failures: {audit.strong_connectivity_failures}")
        print(f"acyclic-implication failures: {audit.acyclic_implication_failures}")
        if args.assert_expected:
            print("OK: all no-reciprocal n=9 regular tournaments are Kalmanson-obstructed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
