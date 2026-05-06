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
EXPECTED_LOCAL_CORE_SIZE_COUNTS = {3: 5, 4: 6, 5: 2, 6: 3}
EXPECTED_LOCAL_CORE_STATUS_SIZE_COUNTS = {
    "self_edge": {3: 5, 4: 4, 5: 2, 6: 2},
    "strict_cycle": {4: 2, 6: 1},
}
LOCAL_CORE_PACKET_SCHEMA = "erdos97.n9_vertex_circle_local_core_packet.v1"
LOCAL_CORE_PACKET_TRUST = "REVIEW_PENDING_DIAGNOSTIC"
LOCAL_CORE_PACKET_STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
LOCAL_CORE_PACKET_CLAIM_SCOPE = (
    "Compact replay packet for the 16 n=9 vertex-circle local-core motif "
    "representatives; not a proof of n=9, not a counterexample, not an "
    "independent review of the exhaustive checker, and not a global status update."
)
LOCAL_CORE_PACKET_PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_local_core_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_local_core_packet.py "
        "--assert-expected --write"
    ),
}


Assignment = dict[int, int]
Rows = list[list[int]]
CanonicalRows = tuple[tuple[int, ...], ...]


def _json_pair(item: Pair) -> list[int]:
    return [int(item[0]), int(item[1])]


def _pair_from_json(item: Sequence[int]) -> Pair:
    if len(item) != 2:
        raise AssertionError(f"expected pair, got {item}")
    return pair(int(item[0]), int(item[1]))


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _json_nested_counter(counter: Counter[tuple[str, int]]) -> dict[str, dict[str, int]]:
    nested: dict[str, Counter[int]] = defaultdict(Counter)
    for (status, size), count in counter.items():
        nested[status][size] = int(count)
    return {status: _json_counter(nested[status]) for status in sorted(nested)}


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


def canonical_dihedral_rows_with_map(
    rows: Sequence[Sequence[int]],
) -> tuple[CanonicalRows, tuple[int, ...]]:
    """Return the canonical dihedral row system and the label map that gives it.

    The map sends labels in ``rows`` to labels in the returned canonical
    representative. Ties are broken by the map so callers can store a stable
    provenance witness, even when a row system has nontrivial dihedral symmetry.
    """

    return min(
        (
            tuple(tuple(row) for row in _transform_rows(rows, label_map)),
            tuple(label_map),
        )
        for label_map in _dihedral_maps()
    )


def _rows_to_json(rows: Sequence[Sequence[int]]) -> Rows:
    return [[int(value) for value in row] for row in rows]


def _core_rows_to_json(
    rows: Sequence[Sequence[int]],
    centers: Sequence[int],
) -> list[dict[str, object]]:
    return [
        {"row": int(center), "witnesses": [int(witness) for witness in rows[center]]}
        for center in sorted(centers)
    ]


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


def _path_rows(path: Sequence[dict[str, object]]) -> set[int]:
    return {int(step["row"]) for step in path}


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


def _cycle_span_key(
    edges: Sequence[StrictInequality],
) -> tuple[int, tuple[tuple[int, int], ...]]:
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


def _self_edge_core_certificate(
    family_id: str,
    orbit_size: int,
    rows: Sequence[Sequence[int]],
    edge: StrictInequality,
) -> dict[str, object]:
    equality_path = _distance_equality_path(rows, edge.outer_pair, edge.inner_pair)
    core_rows = {edge.row} | _path_rows(equality_path)
    return {
        "family_id": family_id,
        "orbit_size": int(orbit_size),
        "status": "self_edge",
        "core_size": len(core_rows),
        "core_rows": [int(row) for row in sorted(core_rows)],
        "core_selected_rows": _core_rows_to_json(rows, sorted(core_rows)),
        "strict_inequality": _json_inequality(edge),
        "distance_equality": {
            "start_pair": _json_pair(edge.outer_pair),
            "end_pair": _json_pair(edge.inner_pair),
            "path": equality_path,
        },
    }


def _strict_cycle_core_certificate(
    family_id: str,
    orbit_size: int,
    rows: Sequence[Sequence[int]],
    edges: Sequence[StrictInequality],
) -> dict[str, object]:
    cycle_steps = []
    core_rows = {edge.row for edge in edges}
    for idx, edge in enumerate(edges):
        next_edge = edges[(idx + 1) % len(edges)]
        equality_path = _distance_equality_path(
            rows,
            edge.inner_pair,
            next_edge.outer_pair,
        )
        core_rows.update(_path_rows(equality_path))
        cycle_steps.append(
            {
                "strict_inequality": _json_inequality(edge),
                "equality_to_next_outer_pair": {
                    "start_pair": _json_pair(edge.inner_pair),
                    "end_pair": _json_pair(next_edge.outer_pair),
                    "path": equality_path,
                },
            }
        )
    return {
        "family_id": family_id,
        "orbit_size": int(orbit_size),
        "status": "strict_cycle",
        "core_size": len(core_rows),
        "core_rows": [int(row) for row in sorted(core_rows)],
        "core_selected_rows": _core_rows_to_json(rows, sorted(core_rows)),
        "cycle_length": len(edges),
        "cycle_steps": cycle_steps,
    }


def _local_core_certificate(
    family_id: str,
    orbit_size: int,
    rows: Sequence[Sequence[int]],
) -> dict[str, object]:
    result = vertex_circle_order_obstruction(rows, list(n9.ORDER), "n9")
    if result.self_edge_conflicts:
        return _self_edge_core_certificate(
            family_id,
            orbit_size,
            rows,
            result.self_edge_conflicts[0],
        )
    if result.cycle_edges:
        return _strict_cycle_core_certificate(
            family_id,
            orbit_size,
            rows,
            result.cycle_edges,
        )
    raise AssertionError("pre-vertex-circle survivor was not obstructed")


def _core_row_map(certificate: dict[str, object]) -> dict[int, list[int]]:
    rows: dict[int, list[int]] = {}
    for item in certificate["core_selected_rows"]:
        if not isinstance(item, dict):
            raise AssertionError("malformed core row")
        center = int(item["row"])
        witnesses = [int(witness) for witness in item["witnesses"]]
        if len(witnesses) != n9.ROW_SIZE:
            raise AssertionError(f"row {center} has {len(witnesses)} witnesses")
        if center in witnesses:
            raise AssertionError(f"row {center} selects itself")
        if center in rows:
            raise AssertionError(f"duplicate core row {center}")
        rows[center] = sorted(witnesses)
    return rows


def _selected_pairs_for_core_row(rows: dict[int, list[int]], center: int) -> set[Pair]:
    return {pair(center, witness) for witness in rows[center]}


def _validate_strict_inequality(
    rows: dict[int, list[int]],
    edge: dict[str, object],
) -> None:
    center = int(edge["row"])
    if center not in rows:
        raise AssertionError(f"strict row {center} missing from core")
    witness_order = [int(label) for label in edge["witness_order"]]
    expected_order = sorted(
        rows[center],
        key=lambda witness: (witness - center) % n9.N,
    )
    if witness_order != expected_order:
        raise AssertionError(f"bad witness order in row {center}")

    outer_interval = [int(idx) for idx in edge["outer_interval"]]
    inner_interval = [int(idx) for idx in edge["inner_interval"]]
    outer_start, outer_end = outer_interval
    inner_start, inner_end = inner_interval
    contains = (
        outer_start <= inner_start
        and inner_end <= outer_end
        and (outer_start < inner_start or inner_end < outer_end)
    )
    if not contains:
        raise AssertionError("strict inequality intervals are not nested")
    outer_pair = pair(witness_order[outer_start], witness_order[outer_end])
    inner_pair = pair(witness_order[inner_start], witness_order[inner_end])
    if outer_pair != _pair_from_json(edge["outer_pair"]):
        raise AssertionError("outer pair does not match interval endpoints")
    if inner_pair != _pair_from_json(edge["inner_pair"]):
        raise AssertionError("inner pair does not match interval endpoints")


def _validate_equality_path(
    rows: dict[int, list[int]],
    start_pair: Pair,
    end_pair: Pair,
    path: Sequence[dict[str, object]],
) -> None:
    current = start_pair
    for step in path:
        row = int(step["row"])
        if row not in rows:
            raise AssertionError(f"equality path row {row} missing from core")
        next_pair = _pair_from_json(step["next_pair"])
        selected_pairs = _selected_pairs_for_core_row(rows, row)
        if current not in selected_pairs or next_pair not in selected_pairs:
            raise AssertionError(
                f"row {row} does not equate {current} and {next_pair}"
            )
        current = next_pair
    if current != end_pair:
        raise AssertionError(f"equality path ends at {current}, expected {end_pair}")


def verify_local_core_certificate(certificate: dict[str, object]) -> None:
    """Verify a local self-edge or strict-cycle core certificate."""
    rows = _core_row_map(certificate)
    if sorted(rows) != [int(row) for row in certificate["core_rows"]]:
        raise AssertionError("core row list does not match core_selected_rows")
    if len(rows) != int(certificate["core_size"]):
        raise AssertionError("core_size does not match core_selected_rows")
    status = certificate["status"]
    if status == "self_edge":
        edge = certificate["strict_inequality"]
        if not isinstance(edge, dict):
            raise AssertionError("malformed strict inequality")
        _validate_strict_inequality(rows, edge)
        equality = certificate["distance_equality"]
        if not isinstance(equality, dict):
            raise AssertionError("malformed distance equality")
        start_pair = _pair_from_json(equality["start_pair"])
        end_pair = _pair_from_json(equality["end_pair"])
        if start_pair != _pair_from_json(edge["outer_pair"]):
            raise AssertionError("self-edge equality must start at outer pair")
        if end_pair != _pair_from_json(edge["inner_pair"]):
            raise AssertionError("self-edge equality must end at inner pair")
        _validate_equality_path(rows, start_pair, end_pair, equality["path"])
        return
    if status == "strict_cycle":
        cycle_steps = certificate["cycle_steps"]
        if len(cycle_steps) != int(certificate["cycle_length"]):
            raise AssertionError("cycle_length does not match cycle_steps")
        for step in cycle_steps:
            edge = step["strict_inequality"]
            equality = step["equality_to_next_outer_pair"]
            if not isinstance(edge, dict) or not isinstance(equality, dict):
                raise AssertionError("malformed cycle step")
            _validate_strict_inequality(rows, edge)
            start_pair = _pair_from_json(equality["start_pair"])
            end_pair = _pair_from_json(equality["end_pair"])
            if start_pair != _pair_from_json(edge["inner_pair"]):
                raise AssertionError("cycle equality must start at inner pair")
            _validate_equality_path(rows, start_pair, end_pair, equality["path"])
        edges = [step["strict_inequality"] for step in cycle_steps]
        for idx, edge in enumerate(edges):
            equality = cycle_steps[idx]["equality_to_next_outer_pair"]
            next_edge = edges[(idx + 1) % len(edges)]
            if _pair_from_json(equality["end_pair"]) != _pair_from_json(
                next_edge["outer_pair"]
            ):
                raise AssertionError("cycle equality does not reach next outer pair")
        return
    raise AssertionError(f"unknown local core status {status!r}")


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


def local_core_summary() -> dict[str, object]:
    """Return local row-core certificates for the 16 n=9 motif families."""
    motif_payload = motif_family_summary()
    certificates = []
    core_size_counts: Counter[int] = Counter()
    status_core_size_counts: Counter[tuple[str, int]] = Counter()
    for family in motif_payload["dihedral_incidence_families"]["families"]:
        if not isinstance(family, dict):
            raise AssertionError("malformed family row")
        certificate = _local_core_certificate(
            str(family["family_id"]),
            int(family["orbit_size"]),
            family["representative_selected_rows"],
        )
        verify_local_core_certificate(certificate)
        certificates.append(certificate)
        core_size = int(certificate["core_size"])
        status = str(certificate["status"])
        core_size_counts[core_size] += 1
        status_core_size_counts[(status, core_size)] += 1

    payload = {
        "type": "n9_vertex_circle_local_cores_v1",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "scope": "Local row-core certificates for the 16 dihedral n=9 vertex-circle motif families.",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The official/global status remains falsifiable/open.",
            "Each core verifies only a representative n=9 motif family under the recorded cyclic order.",
        ],
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "family_count": len(certificates),
        "core_size_counts": _json_counter(core_size_counts),
        "status_core_size_counts": _json_nested_counter(status_core_size_counts),
        "max_core_size": max(core_size_counts),
        "certificates": certificates,
        "interpretation": [
            "Every dihedral n=9 motif family has a local vertex-circle certificate using at most 6 selected rows.",
            "The self-edge cores are one strict chord-containment inequality plus a selected-distance equality path.",
            "The strict-cycle cores are directed cycles of strict inequalities, with selected-distance equality paths connecting each inner chord to the next outer chord.",
            "These are promising lemma candidates, but they still cover only the n=9 motif representatives.",
        ],
    }
    assert_expected_local_core_counts(payload)
    return payload


def local_core_packet_summary() -> dict[str, object]:
    """Return a compact replay packet for the 16 n=9 local-core certificates."""

    local_payload = local_core_summary()
    certificates = []
    for certificate in local_payload["certificates"]:
        if not isinstance(certificate, dict):
            raise AssertionError("malformed local-core certificate")
        compact_rows = []
        for row in certificate["core_selected_rows"]:
            if not isinstance(row, dict):
                raise AssertionError("malformed core row")
            compact_rows.append(
                [
                    int(row["row"]),
                    *[int(witness) for witness in row["witnesses"]],
                ]
            )
        certificates.append(
            {
                "family_id": str(certificate["family_id"]),
                "orbit_size": int(certificate["orbit_size"]),
                "status": str(certificate["status"]),
                "core_size": int(certificate["core_size"]),
                "compact_selected_rows": compact_rows,
            }
        )

    payload = {
        "schema": LOCAL_CORE_PACKET_SCHEMA,
        "status": LOCAL_CORE_PACKET_STATUS,
        "trust": LOCAL_CORE_PACKET_TRUST,
        "claim_scope": LOCAL_CORE_PACKET_CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "family_count": len(certificates),
        "orbit_size_sum": sum(int(cert["orbit_size"]) for cert in certificates),
        "core_size_counts": local_payload["core_size_counts"],
        "status_core_size_counts": local_payload["status_core_size_counts"],
        "max_core_size": local_payload["max_core_size"],
        "certificates": certificates,
        "interpretation": [
            "This packet stores only the selected rows needed to replay each local quotient obstruction.",
            "Each certificate covers one deterministic n=9 motif-family representative under the recorded cyclic order.",
            "The packet is a reviewer aid for the review-pending n=9 vertex-circle frontier, not a promotion of the n=9 finite-case status.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": [
            {
                "path": "data/certificates/n9_vertex_circle_local_cores.json",
                "role": "detailed source local-core certificate artifact",
            },
            {
                "path": "data/certificates/n9_vertex_circle_motif_families.json",
                "role": "deterministic family-id convention",
            },
        ],
        "provenance": LOCAL_CORE_PACKET_PROVENANCE,
    }
    assert_expected_local_core_packet_counts(payload)
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


def assert_expected_local_core_counts(payload: dict[str, object]) -> None:
    """Assert that local core diagnostics match the checked n=9 motifs."""
    if payload["family_count"] != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["core_size_counts"] != _json_counter(
        Counter(EXPECTED_LOCAL_CORE_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected local core size counts")
    expected_status_sizes = {
        status: _json_counter(Counter(counts))
        for status, counts in sorted(EXPECTED_LOCAL_CORE_STATUS_SIZE_COUNTS.items())
    }
    if payload["status_core_size_counts"] != expected_status_sizes:
        raise AssertionError("unexpected local core status/size counts")
    if payload["max_core_size"] != max(EXPECTED_LOCAL_CORE_SIZE_COUNTS):
        raise AssertionError(f"unexpected max core size: {payload['max_core_size']}")
    certificates = payload["certificates"]
    if len(certificates) != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError("unexpected local core certificate count")
    for certificate in certificates:
        if not isinstance(certificate, dict):
            raise AssertionError("malformed local core certificate")
        verify_local_core_certificate(certificate)


def assert_expected_local_core_packet_counts(payload: dict[str, object]) -> None:
    """Assert that the compact local-core packet matches the known n=9 motifs."""

    if payload["schema"] != LOCAL_CORE_PACKET_SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != LOCAL_CORE_PACKET_STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != LOCAL_CORE_PACKET_TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["family_count"] != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["orbit_size_sum"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected orbit-size sum: {payload['orbit_size_sum']}")
    if payload["core_size_counts"] != _json_counter(
        Counter(EXPECTED_LOCAL_CORE_SIZE_COUNTS)
    ):
        raise AssertionError("unexpected packet core size counts")
    expected_status_sizes = {
        status: _json_counter(Counter(counts))
        for status, counts in sorted(EXPECTED_LOCAL_CORE_STATUS_SIZE_COUNTS.items())
    }
    if payload["status_core_size_counts"] != expected_status_sizes:
        raise AssertionError("unexpected packet status/core size counts")
    certificates = payload["certificates"]
    if len(certificates) != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError("unexpected packet certificate count")
    expected_family_ids = [f"F{idx:02d}" for idx in range(1, 17)]
    actual_family_ids = [
        str(certificate["family_id"])
        for certificate in certificates
        if isinstance(certificate, dict)
    ]
    if actual_family_ids != expected_family_ids:
        raise AssertionError(f"unexpected packet family ids: {actual_family_ids}")
    for certificate in certificates:
        if not isinstance(certificate, dict):
            raise AssertionError("malformed packet certificate")
        compact_rows = certificate.get("compact_selected_rows")
        if not isinstance(compact_rows, list):
            raise AssertionError("packet certificate missing compact rows")
        if len(compact_rows) != int(certificate["core_size"]):
            raise AssertionError("compact row count does not match core_size")
        for row in compact_rows:
            if not isinstance(row, list) or len(row) != 5:
                raise AssertionError(f"malformed compact row: {row!r}")
