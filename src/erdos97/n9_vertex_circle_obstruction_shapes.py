"""Mine vertex-circle obstruction shapes for n=9 survivor assignments.

This module is diagnostic. It does not prove Erdos Problem #97 and does not
promote the review-pending n=9 finite-case checker to source-of-truth status.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from itertools import combinations
from typing import Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.vertex_circle_order_filter import (
    Pair,
    StrictInequality,
    pair,
    vertex_circle_order_obstruction,
)

EXPECTED_PRE_VERTEX_CIRCLE_NODES = 100_817
EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS = 184
EXPECTED_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_STRICT_CYCLE_LENGTH_COUNTS = {2: 22, 3: 4}
EXPECTED_SELF_EDGE_PATH_LENGTH_COUNTS = {3: 92, 4: 41, 5: 14, 6: 6, 7: 4, 8: 1}
EXPECTED_SELF_EDGE_SHARED_ENDPOINT_COUNTS = {0: 11, 1: 147}
EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES = 16
EXPECTED_DIHEDRAL_INCIDENCE_ORBIT_SIZE_COUNTS = {2: 5, 6: 2, 18: 9}
EXPECTED_DIHEDRAL_STATUS_FAMILY_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_SELF_EDGE_LOOSE_SHAPE_FAMILIES = 16
EXPECTED_STRICT_CYCLE_SPAN_SHAPE_FAMILIES = 8


Assignment = dict[int, int]
Rows = list[list[int]]
CanonicalRows = tuple[tuple[int, ...], ...]


def _json_pair(item: Pair) -> list[int]:
    return [int(item[0]), int(item[1])]


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _rows_from_assignment(assign: Assignment) -> list[list[int]]:
    return [list(n9.MASK_BITS[assign[center]]) for center in range(n9.N)]


def _dihedral_maps() -> list[tuple[int, ...]]:
    return [
        tuple((direction * label + shift) % n9.N for label in range(n9.N))
        for direction in (1, -1)
        for shift in range(n9.N)
    ]


def _transform_rows(rows: Sequence[Sequence[int]], label_map: Sequence[int]) -> Rows:
    transformed: list[list[int] | None] = [None] * n9.N
    for center, row in enumerate(rows):
        transformed[label_map[center]] = sorted(label_map[witness] for witness in row)
    if any(row is None for row in transformed):  # pragma: no cover - defensive
        raise AssertionError("dihedral map did not produce a complete row system")
    return [list(row) for row in transformed if row is not None]


def canonical_dihedral_rows(rows: Sequence[Sequence[int]]) -> CanonicalRows:
    """Return the canonical dihedral representative of a row system."""
    return min(
        tuple(tuple(row) for row in _transform_rows(rows, label_map))
        for label_map in _dihedral_maps()
    )


def _rows_to_json(rows: Sequence[Sequence[int]]) -> Rows:
    return [[int(value) for value in row] for row in rows]


def pre_vertex_circle_assignments() -> tuple[list[Assignment], int]:
    """Return full n=9 assignments before applying vertex-circle filtering."""
    assignments: list[Assignment] = []
    nodes = 0

    def search(
        assign: Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes
        nodes += 1
        if len(assign) == n9.N:
            assignments.append(dict(sorted(assign.items())))
            return

        best_center = None
        best_options = None
        for center in range(n9.N):
            if center in assign:
                continue
            opts = n9.valid_options_for_center(
                center,
                assign,
                column_counts,
                witness_pair_counts,
            )
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return

        center = best_center
        assert center is not None
        for row_mask in best_options:
            assign[center] = row_mask
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] += 1
            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            search(assign, column_counts, witness_pair_counts)

            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in n9.OPTIONS[0]:
        assign = {0: row0}
        column_counts = [0] * n9.N
        witness_pair_counts = [0] * len(n9.PAIRS)
        for target in n9.MASK_BITS[row0]:
            column_counts[target] += 1
        for pair_index in n9.ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pair_index] += 1
        if n9.vertex_circle_status(assign) == "ok":
            search(assign, column_counts, witness_pair_counts)

    return assignments, nodes


def _distance_equality_graph(
    rows: Sequence[Sequence[int]],
) -> dict[Pair, list[tuple[Pair, int]]]:
    graph: dict[Pair, list[tuple[Pair, int]]] = defaultdict(list)
    for center, row in enumerate(rows):
        selected_pairs = [pair(center, witness) for witness in row]
        for first, second in combinations(selected_pairs, 2):
            graph[first].append((second, center))
            graph[second].append((first, center))
    for item in graph:
        graph[item].sort()
    return graph


def _distance_equality_path(
    rows: Sequence[Sequence[int]],
    start: Pair,
    end: Pair,
) -> list[dict[str, object]]:
    graph = _distance_equality_graph(rows)
    queue: deque[tuple[Pair, list[dict[str, object]]]] = deque([(start, [])])
    seen = {start}
    while queue:
        current, path = queue.popleft()
        if current == end:
            return path
        for next_pair, row in graph.get(current, []):
            if next_pair in seen:
                continue
            seen.add(next_pair)
            queue.append(
                (
                    next_pair,
                    path
                    + [
                        {
                            "row": int(row),
                            "next_pair": _json_pair(next_pair),
                        }
                    ],
                )
            )
    raise AssertionError(f"distance classes are disconnected: {start} -> {end}")


def _json_inequality(edge: StrictInequality) -> dict[str, object]:
    return {
        "row": int(edge.row),
        "witness_order": [int(label) for label in edge.witness_order],
        "outer_interval": [int(idx) for idx in edge.outer_interval],
        "inner_interval": [int(idx) for idx in edge.inner_interval],
        "outer_pair": _json_pair(edge.outer_pair),
        "inner_pair": _json_pair(edge.inner_pair),
        "outer_class": _json_pair(edge.outer_class),
        "inner_class": _json_pair(edge.inner_class),
        "outer_span": int(edge.outer_interval[1] - edge.outer_interval[0]),
        "inner_span": int(edge.inner_interval[1] - edge.inner_interval[0]),
    }


def _self_edge_representative(
    rows: Sequence[Sequence[int]],
    edge: StrictInequality,
) -> dict[str, object]:
    return {
        "status": "self_edge",
        "conflict": _json_inequality(edge),
        "distance_equality_path": _distance_equality_path(
            rows,
            edge.outer_pair,
            edge.inner_pair,
        ),
    }


def _obstruction_representative(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    result = vertex_circle_order_obstruction(rows, list(n9.ORDER), "n9")
    if result.self_edge_conflicts:
        return _self_edge_representative(rows, result.self_edge_conflicts[0])
    if result.cycle_edges:
        return {
            "status": "strict_cycle",
            "cycle_edges": [_json_inequality(edge) for edge in result.cycle_edges],
        }
    raise AssertionError("pre-vertex-circle survivor was not obstructed")


def _status_for_rows(rows: Sequence[Sequence[int]]) -> str:
    result = vertex_circle_order_obstruction(rows, list(n9.ORDER), "n9")
    if result.self_edge_conflicts:
        return "self_edge"
    if result.cycle_edges:
        return "strict_cycle"
    raise AssertionError("pre-vertex-circle survivor was not obstructed")


def _loose_self_edge_key(
    edge: StrictInequality,
    equality_path_length: int,
) -> tuple[int, int, int, int]:
    return (
        len(set(edge.outer_pair) & set(edge.inner_pair)),
        equality_path_length,
        edge.outer_interval[1] - edge.outer_interval[0],
        edge.inner_interval[1] - edge.inner_interval[0],
    )


def _cycle_span_key(edges: Sequence[StrictInequality]) -> tuple[int, tuple[tuple[int, int], ...]]:
    return (
        len(edges),
        tuple(
            sorted(
                (
                    edge.outer_interval[1] - edge.outer_interval[0],
                    edge.inner_interval[1] - edge.inner_interval[0],
                )
                for edge in edges
            )
        ),
    )


def _json_loose_self_edge_shapes(
    counter: Counter[tuple[int, int, int, int]],
) -> list[dict[str, int]]:
    rows = []
    for key, count in counter.items():
        shared, path_length, outer_span, inner_span = key
        rows.append(
            {
                "count": int(count),
                "shared_endpoints": int(shared),
                "equality_path_length": int(path_length),
                "outer_span": int(outer_span),
                "inner_span": int(inner_span),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -row["count"],
            row["shared_endpoints"],
            row["equality_path_length"],
            row["outer_span"],
            row["inner_span"],
        ),
    )


def _json_cycle_span_shapes(
    counter: Counter[tuple[int, tuple[tuple[int, int], ...]]],
) -> list[dict[str, object]]:
    rows = []
    for (cycle_length, span_signature), count in counter.items():
        rows.append(
            {
                "count": int(count),
                "cycle_length": int(cycle_length),
                "span_signature": [
                    [int(outer_span), int(inner_span)]
                    for outer_span, inner_span in span_signature
                ],
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            -int(row["count"]),
            int(row["cycle_length"]),
            row["span_signature"],
        ),
    )


def obstruction_shape_summary() -> dict[str, object]:
    """Return a stable diagnostic summary of n=9 vertex-circle obstructions."""
    assignments, nodes = pre_vertex_circle_assignments()
    status_counts: Counter[str] = Counter()
    self_edge_rows: Counter[int] = Counter()
    self_edge_path_lengths: Counter[int] = Counter()
    self_edge_shared_endpoints: Counter[int] = Counter()
    strict_cycle_lengths: Counter[int] = Counter()
    strict_cycle_rows: Counter[int] = Counter()
    strict_cycle_span_signatures: Counter[str] = Counter()
    representatives: dict[str, object] = {}

    for assign in assignments:
        rows = _rows_from_assignment(assign)
        result = vertex_circle_order_obstruction(rows, list(n9.ORDER), "n9")
        if result.self_edge_conflicts:
            status_counts["self_edge"] += 1
            edge = result.self_edge_conflicts[0]
            equality_path = _distance_equality_path(
                rows,
                edge.outer_pair,
                edge.inner_pair,
            )
            self_edge_rows[edge.row] += 1
            self_edge_path_lengths[len(equality_path)] += 1
            shared = len(set(edge.outer_pair) & set(edge.inner_pair))
            self_edge_shared_endpoints[shared] += 1
            representatives.setdefault(
                "self_edge",
                {
                    "selected_rows": rows,
                    "conflict": _json_inequality(edge),
                    "distance_equality_path": equality_path,
                },
            )
            continue

        if not result.cycle_edges:
            raise AssertionError("pre-vertex-circle survivor was not obstructed")
        status_counts["strict_cycle"] += 1
        strict_cycle_lengths[len(result.cycle_edges)] += 1
        span_signature = tuple(
            sorted(
                (
                    edge.outer_interval[1] - edge.outer_interval[0],
                    edge.inner_interval[1] - edge.inner_interval[0],
                )
                for edge in result.cycle_edges
            )
        )
        strict_cycle_span_signatures[str(span_signature)] += 1
        for edge in result.cycle_edges:
            strict_cycle_rows[edge.row] += 1
        representatives.setdefault(
            "strict_cycle",
            {
                "selected_rows": rows,
                "cycle_edges": [_json_inequality(edge) for edge in result.cycle_edges],
            },
        )

    payload = {
        "type": "n9_vertex_circle_obstruction_shapes_v1",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "scope": "Diagnostic mining of the 184 complete n=9 selected-witness assignments that survive pair/crossing/count filters before vertex-circle obstruction.",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The official/global status remains falsifiable/open.",
            "This diagnostic identifies obstruction shapes; it is not a separate n=9 proof path.",
        ],
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "pre_vertex_circle_search": {
            "row0_choices": len(n9.OPTIONS[0]),
            "nodes_visited": int(nodes),
            "full_assignments": len(assignments),
        },
        "obstruction_status_counts": dict(sorted(status_counts.items())),
        "self_edge_summary": {
            "assignments": int(status_counts["self_edge"]),
            "first_conflict_row_counts": _json_counter(self_edge_rows),
            "equality_path_length_counts": _json_counter(self_edge_path_lengths),
            "shared_endpoint_counts": _json_counter(self_edge_shared_endpoints),
            "max_equality_path_length": max(self_edge_path_lengths),
        },
        "strict_cycle_summary": {
            "assignments": int(status_counts["strict_cycle"]),
            "cycle_length_counts": _json_counter(strict_cycle_lengths),
            "cycle_edge_row_participation_counts": _json_counter(strict_cycle_rows),
            "span_signature_counts": {
                key: int(strict_cycle_span_signatures[key])
                for key in sorted(strict_cycle_span_signatures)
            },
        },
        "representatives": representatives,
        "interpretation": [
            "All strict-cycle obstructions found here have length 2 or 3.",
            "All self-edge obstructions found here have distance-equality paths of length at most 8.",
            "This suggests a general proof target: force a self-edge or directed cycle in the quotient graph whose vertices are selected-distance classes and whose directed edges come from vertex-circle interval containment.",
            "The existing C19 caveat shows this quotient-graph obstruction alone is not yet a global solution route.",
        ],
    }
    assert_expected_counts(payload)
    return payload


def motif_family_summary() -> dict[str, object]:
    """Return dihedral and loose-shape families for n=9 obstructions."""
    assignments, nodes = pre_vertex_circle_assignments()
    families: dict[CanonicalRows, list[Rows]] = defaultdict(list)
    status_counts: Counter[str] = Counter()
    loose_self_shapes: Counter[tuple[int, int, int, int]] = Counter()
    cycle_span_shapes: Counter[tuple[int, tuple[tuple[int, int], ...]]] = Counter()

    for assign in assignments:
        rows = _rows_from_assignment(assign)
        families[canonical_dihedral_rows(rows)].append(rows)
        result = vertex_circle_order_obstruction(rows, list(n9.ORDER), "n9")
        if result.self_edge_conflicts:
            status_counts["self_edge"] += 1
            edge = result.self_edge_conflicts[0]
            equality_path = _distance_equality_path(
                rows,
                edge.outer_pair,
                edge.inner_pair,
            )
            loose_self_shapes[_loose_self_edge_key(edge, len(equality_path))] += 1
            continue
        if not result.cycle_edges:
            raise AssertionError("pre-vertex-circle survivor was not obstructed")
        status_counts["strict_cycle"] += 1
        cycle_span_shapes[_cycle_span_key(result.cycle_edges)] += 1

    orbit_size_counts: Counter[int] = Counter()
    family_status_counts: Counter[str] = Counter()
    family_rows = []
    for family_id, (canonical_rows, members) in enumerate(
        sorted(families.items()),
        start=1,
    ):
        orbit_size_counts[len(members)] += 1
        member_statuses = Counter(_status_for_rows(rows) for rows in members)
        if len(member_statuses) != 1:
            raise AssertionError(f"mixed obstruction status in family {family_id}")
        status = next(iter(member_statuses))
        family_status_counts[status] += 1
        representative_rows = [list(row) for row in canonical_rows]
        representative = _obstruction_representative(representative_rows)
        family_rows.append(
            {
                "family_id": f"F{family_id:02d}",
                "orbit_size": len(members),
                "status": status,
                "status_counts": dict(sorted(member_statuses.items())),
                "representative_selected_rows": _rows_to_json(representative_rows),
                "representative_obstruction": representative,
            }
        )

    payload = {
        "type": "n9_vertex_circle_motif_families_v1",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "scope": "Canonicalized diagnostic families for the 184 complete n=9 selected-witness assignments before vertex-circle obstruction.",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The official/global status remains falsifiable/open.",
            "Dihedral incidence families are selected-witness row-system orbits under rotations and reflections of the cyclic labels.",
            "Loose obstruction shapes intentionally discard labels; they are proof-search hints, not complete certificates.",
        ],
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "pre_vertex_circle_search": {
            "row0_choices": len(n9.OPTIONS[0]),
            "nodes_visited": int(nodes),
            "full_assignments": len(assignments),
        },
        "obstruction_status_counts": dict(sorted(status_counts.items())),
        "dihedral_incidence_families": {
            "family_count": len(families),
            "orbit_size_counts": _json_counter(orbit_size_counts),
            "status_family_counts": dict(sorted(family_status_counts.items())),
            "families": family_rows,
        },
        "loose_obstruction_shapes": {
            "self_edge_shape_family_count": len(loose_self_shapes),
            "self_edge_shape_buckets": _json_loose_self_edge_shapes(loose_self_shapes),
            "strict_cycle_span_family_count": len(cycle_span_shapes),
            "strict_cycle_span_buckets": _json_cycle_span_shapes(cycle_span_shapes),
        },
        "interpretation": [
            "The 184 labelled pre-vertex-circle assignments collapse to 16 full selected-witness row-system orbits under dihedral cyclic symmetry.",
            "Those 16 orbits split into 13 self-edge families and 3 strict-cycle families.",
            "Literal first-conflict paths are still too detailed to be theorem templates; the useful next compression is to classify the representative family obstructions by incidence motifs.",
            "This narrows the next proof-search task, but it does not prove a general vertex-circle lemma.",
        ],
    }
    assert_expected_motif_family_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, object]) -> None:
    """Assert that the diagnostic still matches the checked n=9 frontier."""
    search = payload["pre_vertex_circle_search"]
    if not isinstance(search, dict):
        raise AssertionError("missing pre-vertex-circle search block")
    if search["nodes_visited"] != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected nodes: {search['nodes_visited']}")
    if search["full_assignments"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected full assignments: {search['full_assignments']}")
    if payload["obstruction_status_counts"] != EXPECTED_STATUS_COUNTS:
        raise AssertionError(f"unexpected status counts: {payload['obstruction_status_counts']}")
    self_edge = payload["self_edge_summary"]
    strict_cycle = payload["strict_cycle_summary"]
    if not isinstance(self_edge, dict) or not isinstance(strict_cycle, dict):
        raise AssertionError("missing obstruction summary block")
    if self_edge["equality_path_length_counts"] != _json_counter(
        Counter(EXPECTED_SELF_EDGE_PATH_LENGTH_COUNTS)
    ):
        raise AssertionError("unexpected self-edge path length counts")
    if self_edge["shared_endpoint_counts"] != _json_counter(
        Counter(EXPECTED_SELF_EDGE_SHARED_ENDPOINT_COUNTS)
    ):
        raise AssertionError("unexpected self-edge shared endpoint counts")
    if strict_cycle["cycle_length_counts"] != _json_counter(
        Counter(EXPECTED_STRICT_CYCLE_LENGTH_COUNTS)
    ):
        raise AssertionError("unexpected strict-cycle length counts")


def assert_expected_motif_family_counts(payload: dict[str, object]) -> None:
    """Assert that motif-family diagnostics match the checked n=9 frontier."""
    search = payload["pre_vertex_circle_search"]
    if not isinstance(search, dict):
        raise AssertionError("missing pre-vertex-circle search block")
    if search["nodes_visited"] != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected nodes: {search['nodes_visited']}")
    if search["full_assignments"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected full assignments: {search['full_assignments']}")
    if payload["obstruction_status_counts"] != EXPECTED_STATUS_COUNTS:
        raise AssertionError(f"unexpected status counts: {payload['obstruction_status_counts']}")

    families = payload["dihedral_incidence_families"]
    shapes = payload["loose_obstruction_shapes"]
    if not isinstance(families, dict) or not isinstance(shapes, dict):
        raise AssertionError("missing family or shape block")
    if families["family_count"] != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError(f"unexpected family count: {families['family_count']}")
    if families["orbit_size_counts"] != _json_counter(
        Counter(EXPECTED_DIHEDRAL_INCIDENCE_ORBIT_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected orbit size counts")
    if families["status_family_counts"] != EXPECTED_DIHEDRAL_STATUS_FAMILY_COUNTS:
        raise AssertionError("unexpected family status counts")
    if shapes["self_edge_shape_family_count"] != EXPECTED_SELF_EDGE_LOOSE_SHAPE_FAMILIES:
        raise AssertionError("unexpected self-edge loose shape count")
    if (
        shapes["strict_cycle_span_family_count"]
        != EXPECTED_STRICT_CYCLE_SPAN_SHAPE_FAMILIES
    ):
        raise AssertionError("unexpected strict-cycle span shape count")
