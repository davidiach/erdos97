"""Join n=9 self-edge assignments to transformed equality paths.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_frontier_motif_classification import (
    invert_label_map,
    transform_compact_rows,
)
from erdos97.n9_vertex_circle_obstruction_shapes import EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS
from erdos97.vertex_circle_quotient_replay import (
    Pair,
    StrictInequality,
    pair,
    parse_selected_rows,
    replay_vertex_circle_quotient,
)


SCHEMA = "erdos97.n9_vertex_circle_self_edge_path_join.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Assignment-level join of the 158 n=9 self-edge frontier assignments to "
    "transformed family representative equality paths; not a proof of n=9, "
    "not a counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_self_edge_path_join.py",
    "command": (
        "python scripts/check_n9_vertex_circle_self_edge_path_join.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SELF_EDGE_ASSIGNMENTS = 158
EXPECTED_STRICT_CYCLE_ASSIGNMENTS = 26
EXPECTED_SELF_EDGE_FAMILIES = 13
EXPECTED_SELF_EDGE_TEMPLATES = 9
EXPECTED_PATH_LENGTH_COUNTS = {"3": 86, "4": 36, "5": 18, "6": 18}
EXPECTED_CORE_SIZE_COUNTS = {"3": 46, "4": 40, "5": 36, "6": 36}
EXPECTED_SHARED_ENDPOINT_COUNTS = {"1": 158}
EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS = {
    "T01": 6,
    "T02": 40,
    "T03": 20,
    "T04": 2,
    "T05": 18,
    "T06": 18,
    "T07": 18,
    "T08": 18,
    "T09": 18,
}
EXPECTED_FAMILY_ASSIGNMENT_COUNTS = {
    "F01": 18,
    "F02": 18,
    "F03": 18,
    "F04": 18,
    "F05": 18,
    "F06": 18,
    "F08": 2,
    "F09": 6,
    "F10": 18,
    "F11": 18,
    "F13": 2,
    "F14": 2,
    "F15": 2,
}


def transform_pair(raw_pair: Sequence[int], label_map: Sequence[int]) -> list[int]:
    """Apply a label map to one unordered pair."""

    if len(raw_pair) != 2:
        raise ValueError(f"expected pair, got {raw_pair!r}")
    return [int(value) for value in pair(label_map[int(raw_pair[0])], label_map[int(raw_pair[1])])]


def validate_label_map(label_map: Sequence[int], *, n: int = n9.N) -> None:
    """Validate that a label map is a permutation of ``range(n)``."""

    if len(label_map) != n:
        raise ValueError(f"label map must have {n} entries")
    if sorted(int(label) for label in label_map) != list(range(n)):
        raise ValueError(f"label map must be a permutation of 0..{n - 1}")


def _edge_to_json(edge: StrictInequality) -> dict[str, Any]:
    return {
        "row": int(edge.row),
        "witness_order": [int(label) for label in edge.witness_order],
        "outer_interval": [int(value) for value in edge.outer_interval],
        "inner_interval": [int(value) for value in edge.inner_interval],
        "outer_pair": [int(value) for value in edge.outer_pair],
        "inner_pair": [int(value) for value in edge.inner_pair],
        "outer_class": [int(value) for value in edge.outer_class],
        "inner_class": [int(value) for value in edge.inner_class],
        "outer_span": int(edge.outer_interval[1] - edge.outer_interval[0]),
        "inner_span": int(edge.inner_interval[1] - edge.inner_interval[0]),
    }


def transform_equality_path(
    equality: dict[str, Any],
    label_map: Sequence[int],
) -> dict[str, Any]:
    """Transform a representative equality path into assignment labels."""

    return {
        "start_pair": transform_pair(equality["start_pair"], label_map),
        "end_pair": transform_pair(equality["end_pair"], label_map),
        "path": [
            {
                "row": int(label_map[int(step["row"])]),
                "next_pair": transform_pair(step["next_pair"], label_map),
            }
            for step in equality["path"]
        ],
    }


def _selected_pairs_by_row(rows: Sequence[Sequence[int]]) -> dict[int, set[Pair]]:
    parsed = parse_selected_rows(rows)
    return {
        row.center: {pair(row.center, witness) for witness in row.witnesses}
        for row in parsed
    }


def compact_core_rows(certificate: dict[str, Any]) -> list[list[int]]:
    """Return detailed local-core rows as compact ``[row, witnesses...]`` rows."""

    compact = []
    for raw in certificate["core_selected_rows"]:
        row = int(raw["row"])
        witnesses = sorted(int(witness) for witness in raw["witnesses"])
        compact.append([row, *witnesses])
    return sorted(compact, key=lambda item: item[0])


def validate_equality_path(rows: Sequence[Sequence[int]], equality: dict[str, Any]) -> None:
    """Validate that an equality path follows selected-distance row equalities."""

    selected_pairs = _selected_pairs_by_row(rows)
    current = pair(*equality["start_pair"])
    end_pair = pair(*equality["end_pair"])
    for step in equality["path"]:
        row = int(step["row"])
        if row not in selected_pairs:
            raise ValueError(f"equality path row {row} is not selected")
        next_pair = pair(*step["next_pair"])
        if current not in selected_pairs[row] or next_pair not in selected_pairs[row]:
            raise ValueError(f"row {row} does not equate {current} and {next_pair}")
        current = next_pair
    if current != end_pair:
        raise ValueError(f"equality path ends at {current}, expected {end_pair}")


def _self_edge_certificates(local_core_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    certificates = local_core_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core payload must contain certificates")
    return {
        str(certificate["family_id"]): certificate
        for certificate in certificates
        if certificate.get("status") == "self_edge"
    }


def _find_transformed_self_edge(
    rows: Sequence[Sequence[int]],
    expected_row: int,
    outer_pair: Sequence[int],
    inner_pair: Sequence[int],
) -> StrictInequality:
    result = replay_vertex_circle_quotient(
        n9.N,
        list(n9.ORDER),
        parse_selected_rows(rows),
    )
    expected_outer = pair(*outer_pair)
    expected_inner = pair(*inner_pair)
    for edge in result.self_edge_conflicts:
        if (
            edge.row == expected_row
            and edge.outer_pair == expected_outer
            and edge.inner_pair == expected_inner
        ):
            return edge
    raise AssertionError(
        f"transformed self-edge conflict not found: {expected_outer} > {expected_inner}"
    )


def self_edge_path_join_record(
    assignment: dict[str, Any],
    certificate: dict[str, Any],
) -> dict[str, Any]:
    """Return one transformed self-edge path record for a labelled assignment."""

    family_id = str(assignment["family_id"])
    validate_label_map(assignment["to_canonical_label_map"])
    inverse_map = invert_label_map(assignment["to_canonical_label_map"])
    expected_core_rows = transform_compact_rows(
        compact_core_rows(certificate),
        inverse_map,
    )
    if assignment["core_selected_rows"] != expected_core_rows:
        raise AssertionError(
            f"{assignment['assignment_id']} core rows do not match transformed family core"
        )
    transformed_equality = transform_equality_path(
        certificate["distance_equality"],
        inverse_map,
    )
    transformed_edge_row = int(inverse_map[int(certificate["strict_inequality"]["row"])])
    edge = _find_transformed_self_edge(
        assignment["core_selected_rows"],
        transformed_edge_row,
        transformed_equality["start_pair"],
        transformed_equality["end_pair"],
    )
    validate_equality_path(assignment["core_selected_rows"], transformed_equality)

    path_length = len(transformed_equality["path"])
    shared_endpoints = len(
        set(transformed_equality["start_pair"]) & set(transformed_equality["end_pair"])
    )
    core_size = int(assignment["core_size"])
    return {
        "assignment_id": str(assignment["assignment_id"]),
        "family_id": family_id,
        "template_id": str(assignment["template_id"]),
        "core_size": core_size,
        "path_length": path_length,
        "shared_endpoint_count": shared_endpoints,
        "to_canonical_label_map": [
            int(label) for label in assignment["to_canonical_label_map"]
        ],
        "core_selected_rows": assignment["core_selected_rows"],
        "strict_inequality": _edge_to_json(edge),
        "distance_equality": transformed_equality,
        "contradiction": {
            "kind": "self_edge",
            "statement": "strict inequality outer_pair > inner_pair while selected-distance equalities identify the two pairs",
            "outer_pair": transformed_equality["start_pair"],
            "inner_pair": transformed_equality["end_pair"],
        },
    }


def self_edge_path_join_source_artifacts(
    local_core_payload: dict[str, Any],
    classification_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the path join."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_local_cores.json",
            "role": "family representative self-edge strict inequalities and equality paths",
            "type": local_core_payload.get("type"),
            "trust": local_core_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
            "role": "assignment-to-family label maps and transformed core rows",
            "schema": classification_payload.get("schema"),
            "status": classification_payload.get("status"),
            "trust": classification_payload.get("trust"),
        },
    ]


def self_edge_path_join_payload(
    local_core_payload: dict[str, Any],
    classification_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return transformed self-edge path records for all self-edge assignments."""

    certificates = _self_edge_certificates(local_core_payload)
    records = []
    family_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    path_lengths: Counter[int] = Counter()
    core_sizes: Counter[int] = Counter()
    shared_endpoint_counts: Counter[int] = Counter()
    family_rows: dict[str, dict[str, Any]] = {}

    for assignment in classification_payload["assignments"]:
        if assignment["status"] != "self_edge":
            continue
        family_id = str(assignment["family_id"])
        certificate = certificates[family_id]
        record = self_edge_path_join_record(assignment, certificate)
        path_length = int(record["path_length"])
        shared_endpoints = int(record["shared_endpoint_count"])
        core_size = int(record["core_size"])
        family_counts[family_id] += 1
        template_counts[str(assignment["template_id"])] += 1
        path_lengths[path_length] += 1
        core_sizes[core_size] += 1
        shared_endpoint_counts[shared_endpoints] += 1
        family_rows[family_id] = {
            "assignment_count": int(family_counts[family_id]),
            "core_size": core_size,
            "family_id": family_id,
            "orbit_size": int(certificate["orbit_size"]),
            "path_length": path_length,
            "status": "self_edge",
            "template_id": str(assignment["template_id"]),
        }
        records.append(record)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_assignment_count": int(classification_payload["assignment_count"]),
        "self_edge_assignment_count": len(records),
        "strict_cycle_assignment_count": int(
            classification_payload["status_counts"]["strict_cycle"]
        ),
        "self_edge_family_count": len(family_counts),
        "self_edge_template_count": len(template_counts),
        "path_length_counts": {
            str(length): int(path_lengths[length]) for length in sorted(path_lengths)
        },
        "shared_endpoint_counts": {
            str(count): int(shared_endpoint_counts[count])
            for count in sorted(shared_endpoint_counts)
        },
        "core_size_assignment_counts": {
            str(size): int(core_sizes[size]) for size in sorted(core_sizes)
        },
        "family_assignment_counts": {
            family_id: int(family_counts[family_id]) for family_id in sorted(family_counts)
        },
        "template_assignment_counts": {
            template_id: int(template_counts[template_id])
            for template_id in sorted(template_counts)
        },
        "families": [family_rows[family_id] for family_id in sorted(family_rows)],
        "records": records,
        "interpretation": [
            "Each record transforms a self-edge family representative equality path into one labelled n=9 frontier assignment.",
            "The transformed strict inequality is replayed from the assignment's compact core rows.",
            "These records are compact replay aids and lemma-mining diagnostics, not theorem names.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": self_edge_path_join_source_artifacts(
            local_core_payload,
            classification_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_self_edge_path_join_counts(payload)
    return payload


def assert_expected_self_edge_path_join_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the transformed self-edge path join."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != n9.N or payload["row_size"] != n9.ROW_SIZE:
        raise AssertionError("unexpected n or row size")
    if payload["cyclic_order"] != list(n9.ORDER):
        raise AssertionError("unexpected cyclic order")
    if payload["source_assignment_count"] != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError("unexpected source assignment count")
    if payload["self_edge_assignment_count"] != EXPECTED_SELF_EDGE_ASSIGNMENTS:
        raise AssertionError("unexpected self-edge assignment count")
    if payload["strict_cycle_assignment_count"] != EXPECTED_STRICT_CYCLE_ASSIGNMENTS:
        raise AssertionError("unexpected strict-cycle assignment count")
    if payload["self_edge_family_count"] != EXPECTED_SELF_EDGE_FAMILIES:
        raise AssertionError("unexpected self-edge family count")
    if payload["self_edge_template_count"] != EXPECTED_SELF_EDGE_TEMPLATES:
        raise AssertionError("unexpected self-edge template count")
    if payload["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected path length counts")
    if payload["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("unexpected shared-endpoint counts")
    if payload["core_size_assignment_counts"] != EXPECTED_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected core-size counts")
    if payload["family_assignment_counts"] != EXPECTED_FAMILY_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected family assignment counts")
    if payload["template_assignment_counts"] != EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected template assignment counts")
    if len(payload["families"]) != EXPECTED_SELF_EDGE_FAMILIES:
        raise AssertionError("unexpected family row count")
    if len(payload["records"]) != EXPECTED_SELF_EDGE_ASSIGNMENTS:
        raise AssertionError("unexpected record count")
    family_counts = {
        str(family["family_id"]): int(family["assignment_count"])
        for family in payload["families"]
    }
    if family_counts != EXPECTED_FAMILY_ASSIGNMENT_COUNTS:
        raise AssertionError("family rows do not match assignment counts")
