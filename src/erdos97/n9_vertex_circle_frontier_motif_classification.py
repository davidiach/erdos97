"""Classify every n=9 vertex-circle frontier assignment by motif family.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_obstruction_shapes import (
    EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES,
    EXPECTED_DIHEDRAL_STATUS_FAMILY_COUNTS,
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    EXPECTED_PRE_VERTEX_CIRCLE_NODES,
    EXPECTED_STATUS_COUNTS,
    canonical_dihedral_rows_with_map,
    pre_vertex_circle_assignments,
)
from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_vertex_circle_quotient,
)


SCHEMA = "erdos97.n9_vertex_circle_frontier_motif_classification.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Classification of the 184 n=9 pre-vertex-circle selected-witness "
    "assignments by dihedral motif family and replay-derived local-core "
    "template; not a proof of n=9, not a counterexample, not an independent "
    "review of the exhaustive checker, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_frontier_motif_classification.py",
    "command": (
        "python scripts/check_n9_vertex_circle_frontier_motif_classification.py "
        "--assert-expected --write"
    ),
}
EXPECTED_TEMPLATE_COUNT = 12
EXPECTED_TEMPLATE_STATUS_COUNTS = {"self_edge": 9, "strict_cycle": 3}
EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION = {"1": 10, "2": 1, "4": 1}

Rows = list[list[int]]
CanonicalRows = tuple[tuple[int, ...], ...]


def compact_rows(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return row records as ``[center, witness1, ..., witness4]`` lists."""

    return [
        [int(center), *[int(witness) for witness in row]]
        for center, row in enumerate(rows)
    ]


def compact_to_indexed_rows(rows: Sequence[Sequence[int]]) -> Rows:
    """Return compact row records as an indexed row list."""

    indexed: list[list[int] | None] = [None] * n9.N
    for raw in rows:
        if len(raw) != n9.ROW_SIZE + 1:
            raise ValueError(f"compact row must have 5 entries, got {raw!r}")
        center = int(raw[0])
        if center < 0 or center >= n9.N:
            raise ValueError(f"row center out of range: {center}")
        if indexed[center] is not None:
            raise ValueError(f"duplicate row center: {center}")
        witnesses = sorted(int(witness) for witness in raw[1:])
        indexed[center] = witnesses
    if any(row is None for row in indexed):
        raise ValueError("compact rows must contain every n=9 row center")
    return [list(row) for row in indexed if row is not None]


def invert_label_map(label_map: Sequence[int]) -> list[int]:
    """Return the inverse of a label map."""

    inverse = [0] * len(label_map)
    for source, target in enumerate(label_map):
        inverse[int(target)] = int(source)
    return inverse


def transform_compact_rows(
    rows: Sequence[Sequence[int]],
    label_map: Sequence[int],
) -> list[list[int]]:
    """Apply a label map to compact row records."""

    transformed = []
    for raw in rows:
        if len(raw) != n9.ROW_SIZE + 1:
            raise ValueError(f"compact row must have 5 entries, got {raw!r}")
        center = int(raw[0])
        witnesses = sorted(int(label_map[int(witness)]) for witness in raw[1:])
        transformed.append([int(label_map[center]), *witnesses])
    return sorted(transformed, key=lambda row: row[0])


def replay_status(rows: Sequence[Sequence[int]]) -> str:
    """Replay compact rows through the small quotient verifier."""

    result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parse_selected_rows(rows),
    )
    return result.status


def _rows_from_assignment(assign: dict[int, int]) -> Rows:
    return [list(n9.MASK_BITS[assign[center]]) for center in range(n9.N)]


def _family_rows(motif_payload: dict[str, Any]) -> list[dict[str, Any]]:
    families = motif_payload.get("dihedral_incidence_families", {}).get("families")
    if not isinstance(families, list):
        raise ValueError("motif payload must contain dihedral incidence families")
    return families


def _family_by_canonical(motif_payload: dict[str, Any]) -> dict[CanonicalRows, dict[str, Any]]:
    rows: dict[CanonicalRows, dict[str, Any]] = {}
    for family in _family_rows(motif_payload):
        if not isinstance(family, dict):
            raise ValueError("family row must be an object")
        canonical = tuple(tuple(row) for row in family["representative_selected_rows"])
        rows[canonical] = family
    return rows


def _packet_by_family(packet_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    certificates = packet_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("packet payload must contain certificates")
    return {str(certificate["family_id"]): certificate for certificate in certificates}


def _template_family_rows(template_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = template_payload.get("families")
    if not isinstance(families, list):
        raise ValueError("template payload must contain family rows")
    return {str(family["family_id"]): family for family in families}


def classification_source_artifacts(
    motif_payload: dict[str, Any],
    packet_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the classification."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_motif_families.json",
            "role": "dihedral family ids and canonical representative rows",
            "type": motif_payload.get("type"),
            "trust": motif_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_local_core_packet.json",
            "role": "compact replay rows for each family representative",
            "schema": packet_payload.get("schema"),
            "status": packet_payload.get("status"),
            "trust": packet_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_core_templates.json",
            "role": "replay-derived template labels for family representatives",
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
    ]


def frontier_motif_classification_payload(
    motif_payload: dict[str, Any],
    packet_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return a diagnostic classification for all 184 frontier assignments."""

    assignments, nodes = pre_vertex_circle_assignments()
    family_by_canonical = _family_by_canonical(motif_payload)
    packet_by_family = _packet_by_family(packet_payload)
    template_by_family = _template_family_rows(template_payload)

    assignment_rows = []
    status_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    core_size_counts: Counter[int] = Counter()

    for index, assign in enumerate(assignments, start=1):
        rows = _rows_from_assignment(assign)
        canonical_rows, label_map = canonical_dihedral_rows_with_map(rows)
        family = family_by_canonical[canonical_rows]
        family_id = str(family["family_id"])
        packet = packet_by_family[family_id]
        template = template_by_family[family_id]
        inverse_map = invert_label_map(label_map)
        selected_rows = compact_rows(rows)
        core_rows = transform_compact_rows(packet["compact_selected_rows"], inverse_map)
        status = str(family["status"])
        core_size = int(packet["core_size"])
        template_id = str(template["template_id"])

        full_status = replay_status(selected_rows)
        core_status = replay_status(core_rows)
        if full_status != status:
            raise AssertionError(
                f"assignment A{index:03d} full replay status {full_status!r} "
                f"does not match family status {status!r}"
            )
        if core_status != status:
            raise AssertionError(
                f"assignment A{index:03d} core replay status {core_status!r} "
                f"does not match family status {status!r}"
            )

        status_counts[status] += 1
        family_counts[family_id] += 1
        template_counts[template_id] += 1
        core_size_counts[core_size] += 1
        assignment_rows.append(
            {
                "assignment_id": f"A{index:03d}",
                "family_id": family_id,
                "template_id": template_id,
                "status": status,
                "core_size": core_size,
                "to_canonical_label_map": [int(label) for label in label_map],
                "selected_rows": selected_rows,
                "core_selected_rows": core_rows,
            }
        )

    families = []
    for family in sorted(_family_rows(motif_payload), key=lambda row: str(row["family_id"])):
        family_id = str(family["family_id"])
        template = template_by_family[family_id]
        packet = packet_by_family[family_id]
        families.append(
            {
                "family_id": family_id,
                "status": str(family["status"]),
                "orbit_size": int(family["orbit_size"]),
                "assignment_count": int(family_counts[family_id]),
                "template_id": str(template["template_id"]),
                "core_size": int(packet["core_size"]),
            }
        )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "pre_vertex_circle_search": {
            "nodes_visited": int(nodes),
            "full_assignments": len(assignments),
        },
        "assignment_count": len(assignment_rows),
        "family_count": len(families),
        "orbit_size_sum": sum(int(family["orbit_size"]) for family in families),
        "template_count": int(template_payload["template_count"]),
        "status_counts": {
            status: int(status_counts[status]) for status in sorted(status_counts)
        },
        "family_status_counts": motif_payload["dihedral_incidence_families"][
            "status_family_counts"
        ],
        "family_orbit_size_counts": motif_payload["dihedral_incidence_families"][
            "orbit_size_counts"
        ],
        "template_status_counts": template_payload["status_template_counts"],
        "template_assignment_counts": {
            template_id: int(template_counts[template_id])
            for template_id in sorted(template_counts)
        },
        "core_size_assignment_counts": {
            str(size): int(core_size_counts[size]) for size in sorted(core_size_counts)
        },
        "families": families,
        "assignments": assignment_rows,
        "interpretation": [
            "Each assignment row stores one labelled n=9 pre-vertex-circle selected-witness assignment.",
            "The family and template ids are diagnostic labels inherited from the checked n=9 motif-family and local-core artifacts.",
            "The stored compact core rows are transformed back into the assignment labels and replay to the recorded obstruction status.",
            "Template ids are review aids for lemma mining, not theorem names.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": classification_source_artifacts(
            motif_payload,
            packet_payload,
            template_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_classification_counts(payload)
    return payload


def assert_expected_classification_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the classification artifact."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != n9.N:
        raise AssertionError(f"unexpected n: {payload['n']}")
    if payload["row_size"] != n9.ROW_SIZE:
        raise AssertionError(f"unexpected row size: {payload['row_size']}")
    if payload["cyclic_order"] != list(n9.ORDER):
        raise AssertionError("unexpected cyclic order")
    search = payload["pre_vertex_circle_search"]
    if search["nodes_visited"] != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected nodes: {search['nodes_visited']}")
    if search["full_assignments"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected assignments: {search['full_assignments']}")
    if payload["assignment_count"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected assignment count: {payload['assignment_count']}")
    if payload["family_count"] != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["orbit_size_sum"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected orbit-size sum: {payload['orbit_size_sum']}")
    if payload["template_count"] != EXPECTED_TEMPLATE_COUNT:
        raise AssertionError(f"unexpected template count: {payload['template_count']}")
    if payload["status_counts"] != EXPECTED_STATUS_COUNTS:
        raise AssertionError(f"unexpected status counts: {payload['status_counts']}")
    if payload["family_status_counts"] != EXPECTED_DIHEDRAL_STATUS_FAMILY_COUNTS:
        raise AssertionError("unexpected family status counts")
    if payload["template_status_counts"] != EXPECTED_TEMPLATE_STATUS_COUNTS:
        raise AssertionError("unexpected template status counts")
    if len(payload["families"]) != EXPECTED_DIHEDRAL_INCIDENCE_FAMILIES:
        raise AssertionError("unexpected family rows")
    if len(payload["assignments"]) != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError("unexpected assignment rows")
    family_counts = {
        str(family["family_id"]): int(family["assignment_count"])
        for family in payload["families"]
    }
    orbit_sizes = {
        str(family["family_id"]): int(family["orbit_size"])
        for family in payload["families"]
    }
    if family_counts != orbit_sizes:
        raise AssertionError("family assignment counts do not match orbit sizes")
