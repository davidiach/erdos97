"""High-risk n=9 frontier packet diagnostics.

This module extracts the mutual-edge-triangle slice of the 184 n=9
pre-vertex-circle selected-witness assignments.  The slice is useful because
the simple mutual-edge obstruction has no trigger on it, yet the assignments
are still killed by the existing vertex-circle quotient replay.

The payload is proof-mining bookkeeping only.  It does not prove the n=9 case,
does not independently review the exhaustive checker, and does not claim a
counterexample.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.adaptive_blockers import first_blocker
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    EXPECTED_PRE_VERTEX_CIRCLE_NODES,
    _rows_from_assignment,
    canonical_dihedral_rows,
    pre_vertex_circle_assignments,
)
from erdos97.radius_blocker_packets import (
    PacketConfig,
    analyze_radius_blocker_packet,
    exact_four_rich_classes_from_rows,
)
from erdos97.stuck_sets import forward_ear_order

SCHEMA = "erdos97.n9_high_risk_frontier_packet.v1"
STATUS = "REVIEW_PENDING_HIGH_RISK_FRONTIER_DIAGNOSTIC"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "High-risk mutual-edge-triangle slice of the 184 n=9 pre-vertex-circle "
    "selected-witness assignments, replayed through fixed-row radius-blocker "
    "and vertex-circle diagnostics; not a proof of n=9, not a counterexample, "
    "not an independent review of the exhaustive checker, and not a global "
    "status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_high_risk_frontier_packet.py",
    "command": (
        "python scripts/check_n9_high_risk_frontier_packet.py "
        "--write --assert-expected"
    ),
}

EXPECTED_SELECTED_ASSIGNMENT_COUNT = 62
EXPECTED_SELECTED_FAMILY_COUNTS = {
    "F03": 18,
    "F06": 18,
    "F07": 6,
    "F10": 18,
    "F16": 2,
}
EXPECTED_SELECTED_STATUS_COUNTS = {"self_edge": 54, "strict_cycle": 8}
EXPECTED_FAMILY_STATUS_COUNTS = {"self_edge": 3, "strict_cycle": 2}
EXPECTED_TRIANGLE_COUNT_DISTRIBUTION = {"1": 18, "2": 36, "3": 8}
EXPECTED_NON_EAR_INDICES = [81, 151]
EXPECTED_REPRESENTATIVE_REPLAY_STATUS_COUNTS = {
    "self_edge": 3,
    "strict_cycle": 2,
}

Rows = list[list[int]]
CanonicalRows = tuple[tuple[int, ...], ...]


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _json_pairs(pairs: Sequence[tuple[int, int]]) -> list[list[int]]:
    return [[int(left), int(right)] for left, right in pairs]


def _json_triples(triples: Sequence[tuple[int, int, int]]) -> list[list[int]]:
    return [[int(first), int(second), int(third)] for first, second, third in triples]


def family_labels(
    rows_by_assignment: Sequence[Sequence[Sequence[int]]],
) -> tuple[dict[CanonicalRows, str], dict[str, int]]:
    """Return stable dihedral family labels for a frontier assignment list."""

    family_counts: Counter[CanonicalRows] = Counter(
        canonical_dihedral_rows(rows) for rows in rows_by_assignment
    )
    labels: dict[CanonicalRows, str] = {}
    orbit_sizes: dict[str, int] = {}
    for index, (canonical, count) in enumerate(sorted(family_counts.items()), start=1):
        family_id = f"F{index:02d}"
        labels[canonical] = family_id
        orbit_sizes[family_id] = int(count)
    return labels, orbit_sizes


def mutual_edges(rows: Sequence[Sequence[int]]) -> list[tuple[int, int]]:
    """Return undirected mutual selected-witness edges."""

    row_sets = [set(row) for row in rows]
    edges = []
    for left, right in combinations(range(len(rows)), 2):
        if right in row_sets[left] and left in row_sets[right]:
            edges.append((left, right))
    return edges


def mutual_edge_triangles(
    edges: Sequence[tuple[int, int]],
    n: int = n9.N,
) -> list[tuple[int, int, int]]:
    """Return triangles in the mutual-edge graph."""

    edge_set = set(edges)
    triangles = []
    for first, second, third in combinations(range(n), 3):
        if (
            (first, second) in edge_set
            and (first, third) in edge_set
            and (second, third) in edge_set
        ):
            triangles.append((first, second, third))
    return triangles


def simple_mutual_edge_obstruction_triggers(
    rows: Sequence[Sequence[int]],
) -> list[dict[str, object]]:
    """Return occurrences of the simple mutual-edge obstruction trigger.

    For a mutual edge ``i <-> j`` with shared witnesses ``a,b``, the trigger is
    present when one shared witness row selects the other shared witness and an
    endpoint.  This is the small obstruction discussed in the external n=8
    notes; the n=9 high-risk slice intentionally has no such triggers.
    """

    row_sets = [set(row) for row in rows]
    triggers: list[dict[str, object]] = []
    for left, right in combinations(range(len(rows)), 2):
        if right not in row_sets[left] or left not in row_sets[right]:
            continue
        shared = sorted(row_sets[left] & row_sets[right])
        if len(shared) < 2:
            continue
        for witness in shared:
            witness_row = row_sets[witness]
            if left not in witness_row and right not in witness_row:
                continue
            for other_shared in shared:
                if other_shared == witness or other_shared not in witness_row:
                    continue
                triggers.append(
                    {
                        "mutual_edge": [left, right],
                        "shared_witnesses": shared,
                        "trigger_row": witness,
                        "other_shared_witness": other_shared,
                        "endpoint_witnesses": [
                            endpoint
                            for endpoint in (left, right)
                            if endpoint in witness_row
                        ],
                    }
                )
    return triggers


def fixed_row_radius_blocker_replay(
    *,
    name: str,
    rows: Sequence[Sequence[int]],
    blocker: Sequence[int],
) -> dict[str, object]:
    """Return the compact fixed-row radius-blocker replay summary."""

    result = analyze_radius_blocker_packet(
        name,
        exact_four_rich_classes_from_rows(rows),
        blocker,
        list(n9.ORDER),
        PacketConfig(max_nodes=1_000, max_survivor_examples=0),
    )
    return {
        "radius_blocker_ok": result.radius_blocker_ok,
        "row_option_counts": list(result.row_option_counts),
        "raw_selection_upper_bound": int(result.raw_selection_upper_bound),
        "nodes_visited": int(result.nodes_visited),
        "incidence_survivors": int(result.incidence_survivors),
        "aborted": result.aborted,
        "vertex_circle_status_counts": dict(result.vertex_circle_status_counts),
        "all_incidence_survivors_obstructed": (
            result.all_incidence_survivors_obstructed
        ),
        "rejection_counts": dict(result.rejection_counts),
    }


def _compact_ear_json(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    ear = forward_ear_order(rows)
    return {
        "exists": ear.exists,
        "seed": ear.seed,
        "order": ear.order,
        "largest_closure_size": ear.largest_closure_size,
        "largest_closure_seed": ear.largest_closure_seed,
    }


def _assignment_record(
    *,
    zero_based_index: int,
    rows: Rows,
    family_id: str,
    family_orbit_size: int,
) -> dict[str, object] | None:
    edges = mutual_edges(rows)
    triangles = mutual_edge_triangles(edges)
    triggers = simple_mutual_edge_obstruction_triggers(rows)
    if not triangles or triggers:
        return None

    status = n9.vertex_circle_status(
        {center: n9.mask(row) for center, row in enumerate(rows)}
    )
    blocker = first_blocker(exact_four_rich_classes_from_rows(rows), max_size=4)
    if blocker is None:
        raise AssertionError(f"A{zero_based_index + 1:03d}: expected size-4 blocker")
    replay = fixed_row_radius_blocker_replay(
        name=f"n9-high-risk-A{zero_based_index + 1:03d}",
        rows=rows,
        blocker=blocker,
    )
    if replay["vertex_circle_status_counts"] != {status: 1}:
        raise AssertionError(
            f"A{zero_based_index + 1:03d}: replay status mismatch"
        )
    return {
        "assignment_id": f"A{zero_based_index + 1:03d}",
        "zero_based_index": int(zero_based_index),
        "family_id": family_id,
        "family_orbit_size": int(family_orbit_size),
        "selected_rows": [[int(label) for label in row] for row in rows],
        "vertex_circle_status": status,
        "kill_reason": f"vertex_circle_{status}",
        "ear_order": _compact_ear_json(rows),
        "mutual_edge_count": len(edges),
        "mutual_edges": _json_pairs(edges),
        "mutual_edge_triangle_count": len(triangles),
        "mutual_edge_triangles": _json_triples(triangles),
        "simple_obstruction_a_trigger_count": len(triggers),
        "simple_obstruction_a_triggers": triggers,
        "first_radius_blocker": [int(label) for label in blocker],
        "radius_blocker_replay": replay,
    }


def build_payload() -> dict[str, object]:
    """Return the checked high-risk n=9 frontier packet."""

    assignments, nodes = pre_vertex_circle_assignments()
    rows_by_assignment = [_rows_from_assignment(assign) for assign in assignments]
    label_by_family, family_orbit_sizes = family_labels(rows_by_assignment)

    selected_records = []
    for index, rows in enumerate(rows_by_assignment):
        canonical = canonical_dihedral_rows(rows)
        family_id = label_by_family[canonical]
        record = _assignment_record(
            zero_based_index=index,
            rows=rows,
            family_id=family_id,
            family_orbit_size=family_orbit_sizes[family_id],
        )
        if record is not None:
            selected_records.append(record)

    family_counts = Counter(str(record["family_id"]) for record in selected_records)
    status_counts = Counter(
        str(record["vertex_circle_status"]) for record in selected_records
    )
    family_status: dict[str, str] = {}
    representative_by_family: dict[str, dict[str, object]] = {}
    for record in selected_records:
        family_id = str(record["family_id"])
        status = str(record["vertex_circle_status"])
        previous_status = family_status.setdefault(family_id, status)
        if previous_status != status:
            raise AssertionError(f"family {family_id} has mixed vertex-circle status")
        representative_by_family.setdefault(family_id, record)

    representative_status_counts = Counter(
        str(record["vertex_circle_status"])
        for record in representative_by_family.values()
    )
    triangle_count_distribution = Counter(
        int(record["mutual_edge_triangle_count"]) for record in selected_records
    )
    non_ear_indices = [
        int(record["zero_based_index"])
        for record in selected_records
        if not bool(record["ear_order"]["exists"])
    ]
    family_rows = []
    for family_id in sorted(representative_by_family):
        representative = representative_by_family[family_id]
        family_rows.append(
            {
                "family_id": family_id,
                "assignment_count": int(family_counts[family_id]),
                "source_orbit_size": int(representative["family_orbit_size"]),
                "vertex_circle_status": str(representative["vertex_circle_status"]),
                "representative_assignment_id": representative["assignment_id"],
                "representative_zero_based_index": int(
                    representative["zero_based_index"]
                ),
                "representative_selected_rows": representative["selected_rows"],
                "representative_mutual_edge_triangles": representative[
                    "mutual_edge_triangles"
                ],
                "representative_first_radius_blocker": representative[
                    "first_radius_blocker"
                ],
                "representative_radius_blocker_replay": representative[
                    "radius_blocker_replay"
                ],
                "ear_orderable_assignments": sum(
                    1
                    for record in selected_records
                    if record["family_id"] == family_id
                    and bool(record["ear_order"]["exists"])
                ),
                "non_ear_assignments": sum(
                    1
                    for record in selected_records
                    if record["family_id"] == family_id
                    and not bool(record["ear_order"]["exists"])
                ),
            }
        )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_frontier": {
            "assignment_count": len(assignments),
            "nodes_visited": int(nodes),
            "source": "src/erdos97/n9_vertex_circle_exhaustive.py",
        },
        "selection_rule": {
            "name": "mutual_edge_triangle_without_simple_obstruction_a_trigger",
            "description": (
                "Select pre-vertex-circle assignments whose mutual-edge graph "
                "contains at least one triangle and whose rows contain no "
                "simple mutual-edge obstruction-A trigger."
            ),
        },
        "summary": {
            "selected_assignment_count": len(selected_records),
            "selected_family_count": len(family_counts),
            "selected_family_counts": dict(sorted(family_counts.items())),
            "selected_status_counts": dict(sorted(status_counts.items())),
            "selected_family_status_counts": dict(
                sorted(
                    Counter(family_status.values()).items(),
                )
            ),
            "mutual_edge_triangle_count_distribution": _json_counter(
                triangle_count_distribution
            ),
            "all_selected_have_no_simple_obstruction_a_trigger": all(
                int(record["simple_obstruction_a_trigger_count"]) == 0
                for record in selected_records
            ),
            "all_selected_have_size4_radius_blocker": all(
                len(record["first_radius_blocker"]) == 4
                for record in selected_records
            ),
            "all_selected_radius_blocker_replays_obstructed": all(
                bool(record["radius_blocker_replay"]["all_incidence_survivors_obstructed"])
                for record in selected_records
            ),
            "representative_replay_status_counts": dict(
                sorted(representative_status_counts.items())
            ),
            "non_ear_zero_based_indices": non_ear_indices,
            "non_ear_assignment_count": len(non_ear_indices),
            "post_vertex_circle_survivor_count": sum(
                1
                for record in selected_records
                if record["radius_blocker_replay"]["vertex_circle_status_counts"].get(
                    "ok", 0
                )
            ),
        },
        "families": family_rows,
        "assignments": selected_records,
        "interpretation": [
            "This packet isolates the mutual-edge-triangle part of the n=9 frontier, where the simple mutual-edge obstruction has no trigger.",
            "Every selected assignment is still killed by the fixed-order vertex-circle quotient replay after the fixed-row radius-blocker packet check.",
            "The two non-ear assignments are the existing bridge-frontier n=9 proof-mining targets.",
            "The packet is diagnostic and review-pending; it is not an independent proof of the n=9 case.",
            "No proof of Erdos Problem #97 and no counterexample are claimed.",
        ],
        "provenance": {
            **PROVENANCE,
            "sources": [
                "src/erdos97/n9_vertex_circle_exhaustive.py",
                "src/erdos97/n9_vertex_circle_obstruction_shapes.py",
                "src/erdos97/radius_blocker_packets.py",
                "src/erdos97/vertex_circle_quotient_replay.py",
                "src/erdos97/stuck_sets.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline counts for the high-risk packet."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"unexpected trust: {payload.get('trust')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError("unexpected claim scope")
    source = payload.get("source_frontier")
    if not isinstance(source, Mapping):
        raise AssertionError("missing source_frontier")
    if source.get("assignment_count") != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError("unexpected source assignment count")
    if source.get("nodes_visited") != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError("unexpected source node count")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("missing summary")
    expected = {
        "selected_assignment_count": EXPECTED_SELECTED_ASSIGNMENT_COUNT,
        "selected_family_count": len(EXPECTED_SELECTED_FAMILY_COUNTS),
        "selected_family_counts": EXPECTED_SELECTED_FAMILY_COUNTS,
        "selected_status_counts": EXPECTED_SELECTED_STATUS_COUNTS,
        "selected_family_status_counts": EXPECTED_FAMILY_STATUS_COUNTS,
        "mutual_edge_triangle_count_distribution": EXPECTED_TRIANGLE_COUNT_DISTRIBUTION,
        "all_selected_have_no_simple_obstruction_a_trigger": True,
        "all_selected_have_size4_radius_blocker": True,
        "all_selected_radius_blocker_replays_obstructed": True,
        "representative_replay_status_counts": EXPECTED_REPRESENTATIVE_REPLAY_STATUS_COUNTS,
        "non_ear_zero_based_indices": EXPECTED_NON_EAR_INDICES,
        "non_ear_assignment_count": len(EXPECTED_NON_EAR_INDICES),
        "post_vertex_circle_survivor_count": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(
                f"summary[{key!r}] is {summary.get(key)!r}, expected {value!r}"
            )
    families = payload.get("families")
    if not isinstance(families, list) or len(families) != len(EXPECTED_SELECTED_FAMILY_COUNTS):
        raise AssertionError("unexpected family rows")
    assignments = payload.get("assignments")
    if not isinstance(assignments, list) or len(assignments) != EXPECTED_SELECTED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected assignment rows")
    if "No proof of Erdos Problem #97" not in " ".join(
        str(item) for item in payload.get("interpretation", [])
    ):
        raise AssertionError("missing no-proof interpretation warning")
