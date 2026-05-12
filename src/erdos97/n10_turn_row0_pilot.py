"""Bounded n=10 turn-inequality pilot for the first row0 slice.

This module is exploratory and review-pending. It checks the row0-index-0
slice of the n=10 pair/crossing/count frontier against the candidate turn
inequalities. It does not prove n=10, does not produce a counterexample, and
does not change the repository source-of-truth status.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction
from functools import lru_cache
from hashlib import sha256
from typing import Sequence
import json

import z3

from erdos97.generic_vertex_search import GenericVertexSearch
from erdos97.n9_turn_inequality_frontier import (
    find_turn_farkas_certificate,
    turn_inequality_terms_for_pattern,
    turn_z3_status,
    verify_turn_farkas_certificate,
)
from erdos97.vertex_circle_order_filter import (
    Pair,
    StrictInequality,
    pair,
    vertex_circle_order_obstruction,
)

N = 10
ROW_SIZE = 4
PAIR_CAP = 2
ROW0_INDEX = 0
SCHEMA = "erdos97.n10_turn_row0_pilot.v1"
STATUS = "EXPLORATORY_ROW0_TURN_FRONTIER_PILOT"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_FULL_ASSIGNMENTS = 160
EXPECTED_TURN_FARKAS_UNSAT = 156
EXPECTED_TURN_SAT_VERTEX_SELF_EDGE = 4
EXPECTED_ASSIGNMENT_SHA256 = (
    "ec0fa48ec4db8a4a133bffbd86647ade7f33444a1ccb7eea098aae04df4d42b7"
)
EXPECTED_CERTIFICATE_SHA256 = (
    "c55eb78466233cc7c9c379ffd1d8d555304349e4bc4eaf588c79be5638ee4a55"
)


@lru_cache(maxsize=1)
def _searcher() -> GenericVertexSearch:
    return GenericVertexSearch(N, row_size=ROW_SIZE, pair_cap=PAIR_CAP)


def _mask_from_row(row: Sequence[int]) -> int:
    mask = 0
    for value in row:
        mask |= 1 << int(value)
    return mask


def normalize_pattern(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return sorted JSON-friendly rows."""
    return [sorted(int(value) for value in row) for row in rows]


def _stable_sha256(value: object) -> str:
    blob = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(blob.encode("utf-8")).hexdigest()


def enumerate_row0_full_assignments(row0_index: int = ROW0_INDEX) -> list[list[list[int]]]:
    """Enumerate raw full assignments in one n=10 row0 slice."""
    searcher = _searcher()
    row0 = searcher.options[0][row0_index]
    frontier: list[list[list[int]]] = []

    def search(
        assign: dict[int, int],
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        if len(assign) == N:
            frontier.append(
                [list(searcher.mask_bits[assign[center]]) for center in range(N)]
            )
            return
        best_center = None
        best_options = None
        for center in range(N):
            if center in assign:
                continue
            opts = searcher.valid_options_for_center(
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
        assert best_center is not None
        for mask in best_options:
            assign[best_center] = mask
            for target in searcher.mask_bits[mask]:
                column_counts[target] += 1
            for pair_index in searcher.row_pair_indices[mask]:
                witness_pair_counts[pair_index] += 1
            search(assign, column_counts, witness_pair_counts)
            for pair_index in searcher.row_pair_indices[mask]:
                witness_pair_counts[pair_index] -= 1
            for target in searcher.mask_bits[mask]:
                column_counts[target] -= 1
            del assign[best_center]

    assign = {0: row0}
    column_counts = [0] * N
    witness_pair_counts = [0] * len(searcher.pairs)
    for target in searcher.mask_bits[row0]:
        column_counts[target] += 1
    for pair_index in searcher.row_pair_indices[row0]:
        witness_pair_counts[pair_index] += 1
    search(assign, column_counts, witness_pair_counts)
    return [normalize_pattern(rows) for rows in frontier]


def _z3_turn_model(rows: Sequence[Sequence[int]]) -> list[str] | None:
    variables = [z3.Real(f"t_{idx}") for idx in range(N)]
    solver = z3.Solver()
    solver.add(z3.Sum(variables) == 4)
    for variable in variables:
        solver.add(variable >= 0)
    for term in turn_inequality_terms_for_pattern(rows, n=N):
        solver.add(z3.Sum([variables[idx] for idx in term["support"]]) >= 1)
    if str(solver.check()) != "sat":
        return None
    model = solver.model()
    return [str(model.evaluate(variable, model_completion=True)) for variable in variables]


def _verify_turn_model(rows: Sequence[Sequence[int]], model: Sequence[str]) -> None:
    values = [Fraction(value) for value in model]
    if len(values) != N:
        raise ValueError("turn model has wrong length")
    if any(value < 0 for value in values):
        raise ValueError("turn model has negative entry")
    if sum(values) != 4:
        raise ValueError("turn model does not sum to 4")
    for term in turn_inequality_terms_for_pattern(rows, n=N):
        lhs = sum(values[int(index)] for index in term["support"])
        if lhs < 1:
            raise ValueError(f"turn model violates term {term}")


def _vertex_circle_status(rows: Sequence[Sequence[int]]) -> str:
    searcher = _searcher()
    assign = {center: _mask_from_row(row) for center, row in enumerate(rows)}
    return searcher.vertex_circle_status(assign)


def _json_self_edge(edge: StrictInequality) -> dict[str, object]:
    return {
        "row": int(edge.row),
        "witness_order": [int(value) for value in edge.witness_order],
        "outer_interval": [int(value) for value in edge.outer_interval],
        "inner_interval": [int(value) for value in edge.inner_interval],
        "outer_pair": [int(value) for value in edge.outer_pair],
        "inner_pair": [int(value) for value in edge.inner_pair],
        "outer_class": [int(value) for value in edge.outer_class],
        "inner_class": [int(value) for value in edge.inner_class],
        "outer_span": int(edge.outer_interval[1] - edge.outer_interval[0]),
        "inner_span": int(edge.inner_interval[1] - edge.inner_interval[0]),
        "shared_endpoint_count": len(set(edge.outer_pair) & set(edge.inner_pair)),
    }


def _distance_equality_graph(
    rows: Sequence[Sequence[int]],
) -> dict[Pair, list[tuple[Pair, int]]]:
    graph: dict[Pair, list[tuple[Pair, int]]] = defaultdict(list)
    for center, row in enumerate(rows):
        selected_pairs = [pair(center, witness) for witness in row]
        for left_index, left_pair in enumerate(selected_pairs):
            for right_pair in selected_pairs[left_index + 1 :]:
                graph[left_pair].append((right_pair, center))
                graph[right_pair].append((left_pair, center))
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
                            "next_pair": [int(value) for value in next_pair],
                        }
                    ],
                )
            )
    raise ValueError(f"no equality path from {start} to {end}")


def first_self_edge_conflict(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    """Return the first vertex-circle self-edge conflict for rows."""
    result = vertex_circle_order_obstruction(
        rows,
        list(range(N)),
        pattern="n10_turn_row0_pilot",
    )
    if not result.self_edge_conflicts:
        raise ValueError("rows do not have a self-edge conflict")
    edge = result.self_edge_conflicts[0]
    out = _json_self_edge(edge)
    out["distance_equality_path"] = _distance_equality_path(
        rows,
        edge.outer_pair,
        edge.inner_pair,
    )
    return out


def _validate_full_assignment(rows: Sequence[Sequence[int]]) -> None:
    searcher = _searcher()
    normalized = normalize_pattern(rows)
    if len(normalized) != N:
        raise ValueError("wrong row count")
    if normalized[0] != list(searcher.mask_bits[searcher.options[0][ROW0_INDEX]]):
        raise ValueError("row0 does not match pilot slice")
    masks = [_mask_from_row(row) for row in normalized]
    for center, row in enumerate(normalized):
        if center in row or len(row) != ROW_SIZE:
            raise ValueError(f"invalid row {center}: {row}")
        if masks[center] not in searcher.options[center]:
            raise ValueError(f"unknown row option {center}: {row}")
    for left in range(N):
        for right in range(left + 1, N):
            if not searcher.rows_compatible(left, masks[left], right, masks[right]):
                raise ValueError(f"incompatible rows {left}, {right}")
    indegrees = [sum(1 for row in normalized if target in row) for target in range(N)]
    if any(value > searcher.max_indegree for value in indegrees):
        raise ValueError(f"indegree cap violation: {indegrees}")


def classify_assignment(
    rows: Sequence[Sequence[int]],
    assignment_index_1based: int,
) -> dict[str, object]:
    """Classify one row0-pilot assignment by turn and vertex-circle checks."""
    normalized = normalize_pattern(rows)
    _validate_full_assignment(normalized)
    try:
        certificate = find_turn_farkas_certificate(
            normalized,
            assignment_index_1based=assignment_index_1based,
            n=N,
        )
        verify_turn_farkas_certificate(normalized, certificate, n=N)
        return {
            "assignment_index_1based": assignment_index_1based,
            "rows": normalized,
            "turn_status": "farkas_unsat",
            "turn_certificate": certificate,
            "vertex_circle_status": _vertex_circle_status(normalized),
        }
    except ValueError:
        turn_status = turn_z3_status(normalized, n=N)
        record: dict[str, object] = {
            "assignment_index_1based": assignment_index_1based,
            "rows": normalized,
            "turn_status": turn_status,
            "vertex_circle_status": _vertex_circle_status(normalized),
        }
        if turn_status == "sat":
            model = _z3_turn_model(normalized)
            if model is None:
                raise ValueError("Z3 reported sat but no model was extracted")
            _verify_turn_model(normalized, model)
            record["turn_model"] = model
        return record


def summary_payload() -> dict[str, object]:
    """Generate the n=10 row0-index-0 turn pilot artifact."""
    assignments = enumerate_row0_full_assignments(ROW0_INDEX)
    records = [
        classify_assignment(rows, index)
        for index, rows in enumerate(assignments, start=1)
    ]
    status_counts = Counter(str(record["turn_status"]) for record in records)
    vertex_counts = Counter(str(record["vertex_circle_status"]) for record in records)
    certificates = [
        record["turn_certificate"]
        for record in records
        if record.get("turn_status") == "farkas_unsat"
    ]
    turn_sat_self_edges = [
        {
            "assignment_index_1based": record["assignment_index_1based"],
            "self_edge": first_self_edge_conflict(record["rows"]),
        }
        for record in records
        if record.get("turn_status") == "sat"
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Bounded n=10 row0-index-0 turn-frontier pilot; not a proof of n=10, "
            "not a counterexample, not a completeness result, and not a global "
            "status update."
        ),
        "n": N,
        "row_size": ROW_SIZE,
        "row0_index": ROW0_INDEX,
        "full_assignment_count": len(records),
        "assignment_sha256": _stable_sha256(
            [record["rows"] for record in records]
        ),
        "turn_status_counts": dict(sorted(status_counts.items())),
        "vertex_circle_status_counts": dict(sorted(vertex_counts.items())),
        "turn_farkas_certificate_count": len(certificates),
        "turn_farkas_certificate_sha256": _stable_sha256(certificates),
        "turn_sat_escape_count": len(turn_sat_self_edges),
        "turn_sat_escape_self_edges": turn_sat_self_edges,
        "interpretation": (
            "The candidate turn inequalities kill most, but not all, raw "
            "assignments in this bounded n=10 slice. The four weak-turn SAT "
            "escapes are all killed by the existing vertex-circle self-edge "
            "filter."
        ),
        "assignments": records,
        "provenance": {
            "generator": "scripts/check_n10_turn_row0_pilot.py",
            "command": "python scripts/check_n10_turn_row0_pilot.py --assert-expected --write",
        },
    }


def validate_payload(payload: dict[str, object]) -> list[str]:
    """Validate a stored n=10 row0 pilot payload."""
    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append("unexpected schema")
    records = payload.get("assignments")
    if not isinstance(records, list):
        return errors + ["missing assignments list"]
    for expected_index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"assignment {expected_index} is not an object")
            continue
        rows = record.get("rows")
        if not isinstance(rows, list):
            errors.append(f"assignment {expected_index} has no rows")
            continue
        try:
            normalized_rows = normalize_pattern(rows)
            _validate_full_assignment(normalized_rows)
            if rows != normalized_rows:
                raise ValueError("rows are not stored in normalized order")
            if record.get("assignment_index_1based") != expected_index:
                raise ValueError("assignment index mismatch")
            turn_status = record.get("turn_status")
            if turn_status == "farkas_unsat":
                certificate = record.get("turn_certificate")
                if not isinstance(certificate, dict):
                    raise ValueError("missing turn certificate")
                verify_turn_farkas_certificate(normalized_rows, certificate, n=N)
            elif turn_status == "sat":
                model = record.get("turn_model")
                if not isinstance(model, list):
                    raise ValueError("missing turn model")
                _verify_turn_model(normalized_rows, [str(value) for value in model])
            else:
                raise ValueError(f"unexpected turn status {turn_status!r}")
            vertex_status = _vertex_circle_status(normalized_rows)
            if record.get("vertex_circle_status") != vertex_status:
                raise ValueError("vertex-circle status mismatch")
        except ValueError as exc:
            errors.append(f"assignment {expected_index}: {exc}")

    status_counts = Counter(str(record.get("turn_status")) for record in records)
    vertex_counts = Counter(str(record.get("vertex_circle_status")) for record in records)
    certificates = [
        record["turn_certificate"]
        for record in records
        if isinstance(record, dict) and record.get("turn_status") == "farkas_unsat"
    ]
    turn_sat_self_edges = []
    for record in records:
        if not isinstance(record, dict) or record.get("turn_status") != "sat":
            continue
        rows = record.get("rows")
        if not isinstance(rows, list):
            continue
        try:
            turn_sat_self_edges.append(
                {
                    "assignment_index_1based": record.get(
                        "assignment_index_1based"
                    ),
                    "self_edge": first_self_edge_conflict(rows),
                }
            )
        except ValueError as exc:
            errors.append(
                "assignment "
                f"{record.get('assignment_index_1based')}: SAT escape self-edge "
                f"mismatch: {exc}"
            )
    expected_fields = {
        "full_assignment_count": len(records),
        "assignment_sha256": _stable_sha256([record.get("rows") for record in records]),
        "turn_status_counts": dict(sorted(status_counts.items())),
        "vertex_circle_status_counts": dict(sorted(vertex_counts.items())),
        "turn_farkas_certificate_count": len(certificates),
        "turn_farkas_certificate_sha256": _stable_sha256(certificates),
        "turn_sat_escape_count": len(turn_sat_self_edges),
        "turn_sat_escape_self_edges": turn_sat_self_edges,
    }
    for key, expected in expected_fields.items():
        if payload.get(key) != expected:
            errors.append(f"{key} mismatch: {payload.get(key)!r} != {expected!r}")
    return errors


def assert_expected_payload(payload: dict[str, object] | None = None) -> None:
    """Assert stable expected counts for the bounded pilot."""
    if payload is None:
        payload = summary_payload()
    errors = validate_payload(payload)
    if errors:
        raise AssertionError(errors[:5])
    expected = {
        "full_assignment_count": EXPECTED_FULL_ASSIGNMENTS,
        "assignment_sha256": EXPECTED_ASSIGNMENT_SHA256,
        "turn_status_counts": {
            "farkas_unsat": EXPECTED_TURN_FARKAS_UNSAT,
            "sat": EXPECTED_TURN_SAT_VERTEX_SELF_EDGE,
        },
        "vertex_circle_status_counts": {
            "self_edge": EXPECTED_FULL_ASSIGNMENTS,
        },
        "turn_farkas_certificate_count": EXPECTED_TURN_FARKAS_UNSAT,
        "turn_farkas_certificate_sha256": EXPECTED_CERTIFICATE_SHA256,
        "turn_sat_escape_count": EXPECTED_TURN_SAT_VERTEX_SELF_EDGE,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            raise AssertionError(
                f"unexpected {key}: {payload.get(key)!r} != {expected_value!r}"
            )
