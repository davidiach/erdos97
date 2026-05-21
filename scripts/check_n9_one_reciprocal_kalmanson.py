#!/usr/bin/env python3
"""Audit n=9 selected-row systems with exactly one reciprocal pair.

The audit fixes the cyclic order 0,1,...,8.  If a selected-witness system on
nine labels has exactly one reciprocal selected unordered pair, then the total
selected-edge count forces exactly one unordered pair to be unselected.  All
remaining unordered pairs are selected in exactly one direction.

For each such reciprocal/absent status, this checker searches all orientations
of the remaining pairs with selected outdegree 4 at every center.  It substitutes
selected-distance quotient variables into strict Kalmanson inequalities and
prunes whenever one-term cancellation creates a strict implication cycle.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from typing import Iterable

N = 9
TARGET_OUTDEGREE = 4
SCHEMA = "erdos97.n9_one_reciprocal_kalmanson.v1"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
EXPECTED_LABELLED_STATUS_PAIRS = 36 * 35
EXPECTED_DIHEDRAL_ORBITS = 76

Edge = tuple[int, int]
Rows = tuple[tuple[int, ...], ...]
Status = tuple[tuple[int, ...], tuple[int, ...]]


def edge(i: int, j: int) -> Edge:
    return (i, j) if i < j else (j, i)


def build_edges(n: int = N) -> tuple[Edge, ...]:
    return tuple((i, j) for i in range(n) for j in range(i + 1, n))


EDGES = build_edges()
EDGE_INDEX = {e: index for index, e in enumerate(EDGES)}


def edge_index(i: int, j: int) -> int:
    return EDGE_INDEX[edge(i, j)]


def build_kalmanson_inequalities(n: int = N) -> tuple[tuple[int, int, int, int], ...]:
    """Return strict Kalmanson rows as edge-index quadruples.

    A quadruple `(a, b, c, d)` denotes the strict inequality
    `D[a] + D[b] < D[c] + D[d]` for a strictly convex cyclic order.
    """

    inequalities: list[tuple[int, int, int, int]] = []
    for i, j, k, m in combinations(range(n), 4):
        inequalities.append(
            (
                edge_index(i, j),
                edge_index(k, m),
                edge_index(i, k),
                edge_index(j, m),
            )
        )
        inequalities.append(
            (
                edge_index(i, m),
                edge_index(j, k),
                edge_index(i, k),
                edge_index(j, m),
            )
        )
    return tuple(inequalities)


KALMANSON_INEQUALITIES = build_kalmanson_inequalities()


def build_edge_to_inequalities() -> tuple[tuple[int, ...], ...]:
    buckets: list[list[int]] = [[] for _ in EDGES]
    for index, inequality in enumerate(KALMANSON_INEQUALITIES):
        for edge_id in set(inequality):
            buckets[edge_id].append(index)
    return tuple(tuple(bucket) for bucket in buckets)


EDGE_TO_INEQUALITIES = build_edge_to_inequalities()


def dihedral_permutations(n: int = N) -> tuple[tuple[int, ...], ...]:
    rotations = [tuple((i + shift) % n for i in range(n)) for shift in range(n)]
    reflections = [tuple((shift - i) % n for i in range(n)) for shift in range(n)]
    return tuple(rotations + reflections)


DIHEDRAL_PERMUTATIONS = dihedral_permutations()


def transform_edge(edge_id: int, permutation: tuple[int, ...]) -> int:
    u, v = EDGES[edge_id]
    return EDGE_INDEX[edge(permutation[u], permutation[v])]


EDGE_PERMUTATION_MAPS = tuple(
    tuple(transform_edge(index, permutation) for index in range(len(EDGES)))
    for permutation in DIHEDRAL_PERMUTATIONS
)


def canonical_status(
    reciprocal_edges: Iterable[int],
    absent_edges: Iterable[int],
) -> Status:
    reciprocal = tuple(sorted(reciprocal_edges))
    absent = tuple(sorted(absent_edges))
    best: Status | None = None
    for edge_map in EDGE_PERMUTATION_MAPS:
        transformed = (
            tuple(sorted(edge_map[index] for index in reciprocal)),
            tuple(sorted(edge_map[index] for index in absent)),
        )
        if best is None or transformed < best:
            best = transformed
    assert best is not None
    return best


def one_reciprocal_status_orbits() -> dict[Status, int]:
    """Return dihedral orbits of ordered `(reciprocal edge, absent edge)` statuses."""

    orbits: dict[Status, int] = {}
    for reciprocal in range(len(EDGES)):
        for absent in range(len(EDGES)):
            if absent == reciprocal:
                continue
            representative = canonical_status((reciprocal,), (absent,))
            orbits[representative] = orbits.get(representative, 0) + 1
    return orbits


def add_strict_edge(
    reach: tuple[int, ...],
    source: int,
    target: int,
) -> tuple[int, ...] | None:
    """Add `source < target` to a transitive strict graph, or return None on cycle."""

    if source == target or ((reach[target] >> source) & 1):
        return None
    successor_mask = reach[target] | (1 << target)
    updated = list(reach)
    for predecessor, predecessor_reach in enumerate(reach):
        if predecessor == source or ((predecessor_reach >> source) & 1):
            updated[predecessor] |= successor_mask
    return tuple(updated)


def add_kalmanson_implications(
    reach: tuple[int, ...],
    classes: tuple[int, int, int, int],
) -> tuple[int, ...] | None:
    """Apply one-term cancellation implications from one strict Kalmanson row."""

    left_a, left_b, right_a, right_b = classes
    implications: list[tuple[int, int]] = []
    if left_a == right_a:
        implications.append((left_b, right_b))
    if left_a == right_b:
        implications.append((left_b, right_a))
    if left_b == right_a:
        implications.append((left_a, right_b))
    if left_b == right_b:
        implications.append((left_a, right_a))

    updated = reach
    for source, target in implications:
        updated = add_strict_edge(updated, source, target)
        if updated is None:
            return None
    return updated


def row_classes_for_status(
    reciprocal_edge: int,
    absent_edge: int,
) -> tuple[tuple[int, ...], int, int]:
    """Return row-radius classes, absent-edge class, and class count."""

    u, v = EDGES[reciprocal_edge]
    row_classes = [-1] * N
    class_count = 0
    for label in range(N):
        if row_classes[label] != -1:
            continue
        if label == u or label == v:
            row_classes[u] = class_count
            row_classes[v] = class_count
        else:
            row_classes[label] = class_count
        class_count += 1
    absent_class = class_count
    class_count += 1
    return tuple(row_classes), absent_class, class_count


def greedy_edge_order(
    reciprocal_edge: int,
    absent_edge: int,
    initial_known_counts: list[int],
) -> tuple[int, ...]:
    """Choose a deterministic order that completes Kalmanson rows early."""

    remaining = set(range(len(EDGES))) - {reciprocal_edge, absent_edge}
    known_counts = initial_known_counts[:]
    order: list[int] = []
    while remaining:
        chosen = max(
            remaining,
            key=lambda index: (
                sum(known_counts[row] for row in EDGE_TO_INEQUALITIES[index]),
                len(EDGE_TO_INEQUALITIES[index]),
                -index,
            ),
        )
        order.append(chosen)
        remaining.remove(chosen)
        for row in EDGE_TO_INEQUALITIES[chosen]:
            known_counts[row] += 1
    return tuple(order)


def rows_from_assignment(
    reciprocal_edge: int,
    tails: dict[int, int],
) -> Rows:
    rows: list[set[int]] = [set() for _ in range(N)]
    u, v = EDGES[reciprocal_edge]
    rows[u].add(v)
    rows[v].add(u)
    for edge_id, tail in tails.items():
        a, b = EDGES[edge_id]
        other = b if tail == a else a
        rows[tail].add(other)
    return tuple(tuple(sorted(row)) for row in rows)


def find_acyclic_orientation(
    reciprocal_edge: int,
    absent_edge: int,
) -> tuple[Rows | None, int]:
    """Search all degree-4 orientations for one status.

    Returns `(first_survivor, search_nodes)`.  A survivor is a complete
    orientation whose selected-distance quotient has no strict Kalmanson cycle
    detected by this one-term-cancellation filter.
    """

    row_classes, absent_class, class_count = row_classes_for_status(
        reciprocal_edge,
        absent_edge,
    )
    edge_classes: list[int | None] = [None] * len(EDGES)
    edge_classes[reciprocal_edge] = row_classes[EDGES[reciprocal_edge][0]]
    edge_classes[absent_edge] = absent_class

    known_counts = [0] * len(KALMANSON_INEQUALITIES)
    for edge_id, quotient_class in enumerate(edge_classes):
        if quotient_class is not None:
            for row in EDGE_TO_INEQUALITIES[edge_id]:
                known_counts[row] += 1

    reach = tuple(0 for _ in range(class_count))
    for row, known_count in enumerate(known_counts):
        if known_count == 4:
            classes = tuple(
                edge_classes[edge_id]
                for edge_id in KALMANSON_INEQUALITIES[row]
            )
            assert all(quotient_class is not None for quotient_class in classes)
            reach = add_kalmanson_implications(reach, classes)  # type: ignore[arg-type]
            if reach is None:
                return None, 0

    outdegree = [0] * N
    u, v = EDGES[reciprocal_edge]
    outdegree[u] += 1
    outdegree[v] += 1

    order = greedy_edge_order(reciprocal_edge, absent_edge, known_counts)
    remaining_incidence: list[list[int]] = [[0] * N for _ in range(len(order) + 1)]
    for position in range(len(order) - 1, -1, -1):
        remaining = remaining_incidence[position + 1].copy()
        a, b = EDGES[order[position]]
        remaining[a] += 1
        remaining[b] += 1
        remaining_incidence[position] = remaining

    tails: dict[int, int] = {}
    search_nodes = 0

    def feasible(next_position: int) -> bool:
        remaining = remaining_incidence[next_position]
        for label in range(N):
            if outdegree[label] > TARGET_OUTDEGREE:
                return False
            if outdegree[label] + remaining[label] < TARGET_OUTDEGREE:
                return False
        return True

    def recurse(position: int, current_reach: tuple[int, ...]) -> Rows | None:
        nonlocal search_nodes
        search_nodes += 1
        if position == len(order):
            return rows_from_assignment(reciprocal_edge, tails)

        edge_id = order[position]
        a, b = EDGES[edge_id]
        for tail in (a, b):
            tails[edge_id] = tail
            outdegree[tail] += 1
            if feasible(position + 1):
                edge_classes[edge_id] = row_classes[tail]
                changed_rows: list[int] = []
                updated_reach = current_reach
                ok = True
                for row in EDGE_TO_INEQUALITIES[edge_id]:
                    known_counts[row] += 1
                    changed_rows.append(row)
                    if known_counts[row] == 4:
                        classes = tuple(
                            edge_classes[index]
                            for index in KALMANSON_INEQUALITIES[row]
                        )
                        assert all(
                            quotient_class is not None
                            for quotient_class in classes
                        )
                        next_reach = add_kalmanson_implications(
                            updated_reach,
                            classes,  # type: ignore[arg-type]
                        )
                        if next_reach is None:
                            ok = False
                            break
                        updated_reach = next_reach
                if ok:
                    survivor = recurse(position + 1, updated_reach)
                    if survivor is not None:
                        return survivor
                for row in changed_rows:
                    known_counts[row] -= 1
                edge_classes[edge_id] = None
            outdegree[tail] -= 1
            del tails[edge_id]
        return None

    if not feasible(0):
        return None, search_nodes
    survivor = recurse(0, reach)
    return survivor, search_nodes


def edge_json(edge_id: int) -> list[int]:
    return list(EDGES[edge_id])


def audit_one_reciprocal(
    *,
    limit_representatives: int | None = None,
) -> dict[str, object]:
    statuses = one_reciprocal_status_orbits()
    total_statuses = sum(statuses.values())
    checked_representatives = 0
    total_search_nodes = 0
    max_search_nodes = -1
    max_status: Status | None = None
    first_survivor: dict[str, object] | None = None

    for status, multiplicity in sorted(statuses.items()):
        if (
            limit_representatives is not None
            and checked_representatives >= limit_representatives
        ):
            break
        reciprocal_edges, absent_edges = status
        assert len(reciprocal_edges) == 1
        assert len(absent_edges) == 1
        reciprocal = reciprocal_edges[0]
        absent = absent_edges[0]
        survivor, search_nodes = find_acyclic_orientation(reciprocal, absent)
        checked_representatives += 1
        total_search_nodes += search_nodes
        if search_nodes > max_search_nodes:
            max_search_nodes = search_nodes
            max_status = status
        if survivor is not None:
            first_survivor = {
                "reciprocal_edge": edge_json(reciprocal),
                "absent_edge": edge_json(absent),
                "orbit_multiplicity": multiplicity,
                "selected_rows": [list(row) for row in survivor],
            }
            break

    return {
        "schema": SCHEMA,
        "status": "EXACT_N9_ONE_RECIPROCAL_SUBCASE_AUDIT",
        "trust": TRUST,
        "claim_scope": (
            "Fixed cyclic order n=9 selected-witness systems with exactly one "
            "reciprocal selected unordered pair; the selected-edge count then "
            "forces exactly one absent unordered pair."
        ),
        "n": N,
        "target_outdegree": TARGET_OUTDEGREE,
        "unordered_pairs": len(EDGES),
        "kalmanson_inequalities": len(KALMANSON_INEQUALITIES),
        "reciprocal_pair_count": 1,
        "absent_pair_count": 1,
        "use_dihedral_reduction": True,
        "limit_representatives": limit_representatives,
        "labelled_status_pairs": total_statuses,
        "checked_representatives": checked_representatives,
        "dihedral_orbits": len(statuses),
        "total_search_nodes": total_search_nodes,
        "max_search_nodes": max_search_nodes,
        "max_search_status": None
        if max_status is None
        else {
            "reciprocal_edge": edge_json(max_status[0][0]),
            "absent_edge": edge_json(max_status[1][0]),
            "orbit_multiplicity": statuses[max_status],
        },
        "kalmanson_acyclic_survivors_found": 0 if first_survivor is None else 1,
        "first_survivor": first_survivor,
        "checked_all": (
            first_survivor is None
            and checked_representatives == len(statuses)
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--limit-representatives",
        type=int,
        default=None,
        help="Smoke-test only: stop after this many dihedral representatives.",
    )
    args = parser.parse_args()

    audit = audit_one_reciprocal(limit_representatives=args.limit_representatives)

    if args.assert_expected:
        if args.limit_representatives is not None:
            raise AssertionError(
                "--assert-expected requires the full audit "
                "without --limit-representatives"
            )
        if audit["schema"] != SCHEMA:
            raise AssertionError(f"unexpected schema: {audit['schema']}")
        if audit["trust"] != TRUST:
            raise AssertionError(f"unexpected trust: {audit['trust']}")
        if audit["labelled_status_pairs"] != EXPECTED_LABELLED_STATUS_PAIRS:
            raise AssertionError(
                f"expected {EXPECTED_LABELLED_STATUS_PAIRS} status pairs, "
                f"got {audit['labelled_status_pairs']}"
            )
        if audit["dihedral_orbits"] != EXPECTED_DIHEDRAL_ORBITS:
            raise AssertionError(
                f"expected {EXPECTED_DIHEDRAL_ORBITS} dihedral orbits, "
                f"got {audit['dihedral_orbits']}"
            )
        if audit["kalmanson_acyclic_survivors_found"] != 0:
            raise AssertionError("expected zero Kalmanson-acyclic survivors")
        if not audit["checked_all"]:
            raise AssertionError("expected all representatives to close")

    if args.json:
        print(json.dumps(audit, indent=2, sort_keys=True))
    else:
        print("n=9 one-reciprocal Kalmanson audit")
        print(f"labelled status pairs covered: {audit['labelled_status_pairs']}")
        if audit["dihedral_orbits"] is not None:
            print(f"dihedral representatives checked: {audit['dihedral_orbits']}")
        print(f"Kalmanson inequalities per order: {audit['kalmanson_inequalities']}")
        print(f"total search nodes: {audit['total_search_nodes']}")
        print(f"max search nodes for one representative: {audit['max_search_nodes']}")
        print(
            "Kalmanson-acyclic survivors found: "
            f"{audit['kalmanson_acyclic_survivors_found']}"
        )
        if args.assert_expected:
            print(
                "OK: all exactly-one-reciprocal n=9 statuses "
                "are Kalmanson-obstructed"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
