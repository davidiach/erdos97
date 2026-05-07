"""Build a compact n=9 self-edge template packet for reviewer navigation.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_self_edge_path_join import (
    compact_core_rows,
    validate_equality_path,
)
from erdos97.vertex_circle_quotient_replay import pair


SCHEMA = "erdos97.n9_vertex_circle_self_edge_template_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Template-level packet for the 9 self-edge local-core templates covering "
    "158 n=9 self-edge frontier assignments; not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_self_edge_template_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_self_edge_template_packet.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SOURCE_ASSIGNMENT_COUNT = 184
EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT = 158
EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT = 26
EXPECTED_SELF_EDGE_FAMILY_COUNT = 13
EXPECTED_SELF_EDGE_TEMPLATE_COUNT = 9
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
EXPECTED_TEMPLATE_FAMILY_COUNTS = {
    "T01": 1,
    "T02": 4,
    "T03": 2,
    "T04": 1,
    "T05": 1,
    "T06": 1,
    "T07": 1,
    "T08": 1,
    "T09": 1,
}
EXPECTED_TEMPLATE_PATH_LENGTH_COUNTS = {
    "T01": {"3": 6},
    "T02": {"3": 40},
    "T03": {"3": 20},
    "T04": {"3": 2},
    "T05": {"3": 18},
    "T06": {"4": 18},
    "T07": {"4": 18},
    "T08": {"5": 18},
    "T09": {"6": 18},
}
EXPECTED_PATH_LENGTH_COUNTS = {"3": 86, "4": 36, "5": 18, "6": 18}
EXPECTED_SHARED_ENDPOINT_COUNTS = {"1": 158}
EXPECTED_ASSIGNMENT_CORE_SIZE_COUNTS = {"3": 46, "4": 40, "5": 36, "6": 36}
EXPECTED_TEMPLATE_CORE_SIZE_COUNTS = {
    "3": 2,
    "4": 3,
    "5": 2,
    "6": 2,
}
EXPECTED_TEMPLATE_STRICT_EDGE_COUNT_COUNTS = {
    "27": 2,
    "36": 3,
    "45": 2,
    "54": 2,
}
EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION = {"1": 7, "2": 1, "4": 1}


def _self_edge_certificates(
    local_core_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    certificates = local_core_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core payload must contain certificates")
    return {
        str(certificate["family_id"]): certificate
        for certificate in certificates
        if isinstance(certificate, dict) and certificate.get("status") == "self_edge"
    }


def _self_edge_template_rows(
    template_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    templates = template_payload.get("templates")
    if not isinstance(templates, list):
        raise ValueError("template payload must contain templates")
    return {
        str(template["template_id"]): template
        for template in templates
        if isinstance(template, dict) and template.get("status") == "self_edge"
    }


def _path_join_family_rows(path_join_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = path_join_payload.get("families")
    if not isinstance(families, list):
        raise ValueError("self-edge path join must contain families")
    return {str(family["family_id"]): family for family in families}


def _path_join_records_by_template(
    path_join_payload: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    records = path_join_payload.get("records")
    if not isinstance(records, list):
        raise ValueError("self-edge path join must contain records")
    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("self-edge path-join records must be objects")
        by_template[str(record["template_id"])].append(record)
    return {template_id: rows for template_id, rows in sorted(by_template.items())}


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _selected_path_shape(record: dict[str, Any]) -> str:
    edge = record["strict_inequality"]
    return (
        f"{int(edge['outer_span'])}:{int(edge['inner_span'])}:"
        f"{int(record['shared_endpoint_count'])}:path={int(record['path_length'])}"
    )


def _family_record(
    certificate: dict[str, Any],
    family_row: dict[str, Any],
) -> dict[str, Any]:
    if str(certificate["family_id"]) != str(family_row["family_id"]):
        raise AssertionError("family row does not match certificate")
    if family_row["status"] != "self_edge":
        raise AssertionError("family row must be self_edge")
    rows = compact_core_rows(certificate)
    equality = certificate["distance_equality"]
    validate_equality_path(rows, equality)
    edge = certificate["strict_inequality"]
    if pair(*equality["start_pair"]) != pair(*edge["outer_pair"]):
        raise AssertionError("self-edge equality must start at outer pair")
    if pair(*equality["end_pair"]) != pair(*edge["inner_pair"]):
        raise AssertionError("self-edge equality must end at inner pair")

    expected = {
        "core_size": int(certificate["core_size"]),
        "orbit_size": int(certificate["orbit_size"]),
        "path_length": len(equality["path"]),
        "status": "self_edge",
    }
    for key, value in expected.items():
        if family_row.get(key) != value:
            raise AssertionError(f"{family_row['family_id']} {key} mismatch")
    return {
        "family_id": str(certificate["family_id"]),
        "template_id": str(family_row["template_id"]),
        "status": "self_edge",
        "assignment_count": int(family_row["assignment_count"]),
        "orbit_size": int(certificate["orbit_size"]),
        "core_size": int(certificate["core_size"]),
        "path_length": len(equality["path"]),
        "core_selected_rows": rows,
        "strict_inequality": edge,
        "distance_equality": equality,
        "contradiction": {
            "kind": "self_edge",
            "outer_pair": edge["outer_pair"],
            "inner_pair": edge["inner_pair"],
            "statement": (
                "strict inequality outer_pair > inner_pair while "
                "selected-distance equalities identify the two pairs"
            ),
        },
    }


def _template_record(
    template_id: str,
    template_row: dict[str, Any],
    records: Sequence[dict[str, Any]],
    family_rows: dict[str, dict[str, Any]],
    certificates: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    template_families = [str(family_id) for family_id in template_row["families"]]
    path_join_families = sorted({str(record["family_id"]) for record in records})
    if path_join_families != sorted(template_families):
        raise AssertionError(f"{template_id} family coverage mismatch")

    family_records = []
    for family_id in sorted(template_families):
        family_row = family_rows.get(family_id)
        certificate = certificates.get(family_id)
        if family_row is None or certificate is None:
            raise AssertionError(f"{template_id} missing family {family_id}")
        family_records.append(_family_record(certificate, family_row))

    assignment_count = len(records)
    path_length_counts: Counter[int] = Counter(int(record["path_length"]) for record in records)
    shared_endpoint_counts: Counter[int] = Counter(
        int(record["shared_endpoint_count"]) for record in records
    )
    selected_path_shapes: Counter[str] = Counter(_selected_path_shape(record) for record in records)
    expected_assignment_count = sum(
        int(family_rows[family_id]["assignment_count"]) for family_id in template_families
    )
    if assignment_count != expected_assignment_count:
        raise AssertionError(f"{template_id} assignment coverage mismatch")
    if int(template_row["family_count"]) != len(template_families):
        raise AssertionError(f"{template_id} family_count mismatch")
    if int(template_row["orbit_size_sum"]) != assignment_count:
        raise AssertionError(f"{template_id} orbit_size_sum mismatch")
    assignment_ids = sorted(str(record["assignment_id"]) for record in records)

    return {
        "template_id": template_id,
        "template_key": str(template_row["template_key"]),
        "status": "self_edge",
        "core_size": int(template_row["core_size"]),
        "strict_edge_count": int(template_row["strict_edge_count"]),
        "family_count": len(template_families),
        "assignment_count": assignment_count,
        "orbit_size_sum": int(template_row["orbit_size_sum"]),
        "assignment_ids": assignment_ids,
        "families": sorted(template_families),
        "path_length_counts": _json_counter(path_length_counts),
        "shared_endpoint_counts": _json_counter(shared_endpoint_counts),
        "selected_path_shape_counts": _json_counter(selected_path_shapes),
        "self_edge_shape_counts": template_row["self_edge_shape_counts"],
        "family_records": family_records,
    }


def self_edge_template_packet_source_artifacts(
    local_core_payload: dict[str, Any],
    path_join_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the template packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_local_cores.json",
            "role": "canonical self-edge family local-core certificates",
            "type": local_core_payload.get("type"),
            "trust": local_core_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_path_join.json",
            "role": "assignment-level transformed self-edge equality paths",
            "schema": path_join_payload.get("schema"),
            "status": path_join_payload.get("status"),
            "trust": path_join_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_core_templates.json",
            "role": "self-edge template ids and shape summaries",
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
    ]


def self_edge_template_packet_payload(
    local_core_payload: dict[str, Any],
    path_join_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return the compact self-edge template packet."""

    certificates = _self_edge_certificates(local_core_payload)
    template_rows = _self_edge_template_rows(template_payload)
    family_rows = _path_join_family_rows(path_join_payload)
    records_by_template = _path_join_records_by_template(path_join_payload)

    template_records = []
    core_sizes: Counter[int] = Counter()
    strict_edge_counts: Counter[int] = Counter()
    family_count_distribution: Counter[int] = Counter()
    for template_id in sorted(template_rows):
        template_row = template_rows[template_id]
        records = records_by_template.get(template_id, [])
        record = _template_record(
            template_id,
            template_row,
            records,
            family_rows,
            certificates,
        )
        core_sizes[int(record["core_size"])] += 1
        strict_edge_counts[int(record["strict_edge_count"])] += 1
        family_count_distribution[int(record["family_count"])] += 1
        template_records.append(record)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_assignment_count": int(path_join_payload["source_assignment_count"]),
        "self_edge_assignment_count": int(path_join_payload["self_edge_assignment_count"]),
        "strict_cycle_assignment_count": int(path_join_payload["strict_cycle_assignment_count"]),
        "self_edge_family_count": int(path_join_payload["self_edge_family_count"]),
        "self_edge_template_count": len(template_records),
        "template_assignment_counts": {
            str(record["template_id"]): int(record["assignment_count"])
            for record in template_records
        },
        "template_family_counts": {
            str(record["template_id"]): int(record["family_count"])
            for record in template_records
        },
        "template_path_length_counts": {
            str(record["template_id"]): record["path_length_counts"]
            for record in template_records
        },
        "path_length_counts": path_join_payload["path_length_counts"],
        "shared_endpoint_counts": path_join_payload["shared_endpoint_counts"],
        "assignment_core_size_counts": path_join_payload["core_size_assignment_counts"],
        "template_core_size_counts": _json_counter(core_sizes),
        "template_strict_edge_count_counts": _json_counter(strict_edge_counts),
        "template_family_count_distribution": _json_counter(family_count_distribution),
        "templates": template_records,
        "interpretation": [
            "Each template record groups self-edge family certificates with the same replay-derived template id.",
            "Family records keep canonical local-core rows, one strict inequality, and the equality path identifying its outer and inner pairs.",
            "Selected path-shape counts summarize the assignment-level representative paths chosen by the self-edge path join.",
            "Template self-edge shape counts come from the core-template artifact and may include additional self-edge conflict shapes.",
            "These records are reviewer-navigation and lemma-mining diagnostics, not theorem names.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": self_edge_template_packet_source_artifacts(
            local_core_payload,
            path_join_payload,
            template_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_self_edge_template_packet_counts(payload)
    return payload


def assert_expected_self_edge_template_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the self-edge template packet."""

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
    if payload["source_assignment_count"] != EXPECTED_SOURCE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected source assignment count")
    if payload["self_edge_assignment_count"] != EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected self-edge assignment count")
    if payload["strict_cycle_assignment_count"] != EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected strict-cycle assignment count")
    if payload["self_edge_family_count"] != EXPECTED_SELF_EDGE_FAMILY_COUNT:
        raise AssertionError("unexpected self-edge family count")
    if payload["self_edge_template_count"] != EXPECTED_SELF_EDGE_TEMPLATE_COUNT:
        raise AssertionError("unexpected self-edge template count")
    if payload["template_assignment_counts"] != EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected template assignment counts")
    if payload["template_family_counts"] != EXPECTED_TEMPLATE_FAMILY_COUNTS:
        raise AssertionError("unexpected template family counts")
    if payload["template_path_length_counts"] != EXPECTED_TEMPLATE_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected template path-length counts")
    if payload["path_length_counts"] != EXPECTED_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected path-length counts")
    if payload["shared_endpoint_counts"] != EXPECTED_SHARED_ENDPOINT_COUNTS:
        raise AssertionError("unexpected shared-endpoint counts")
    if payload["assignment_core_size_counts"] != EXPECTED_ASSIGNMENT_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected assignment core-size counts")
    if payload["template_core_size_counts"] != EXPECTED_TEMPLATE_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected template core-size counts")
    if (
        payload["template_strict_edge_count_counts"]
        != EXPECTED_TEMPLATE_STRICT_EDGE_COUNT_COUNTS
    ):
        raise AssertionError("unexpected template strict-edge-count counts")
    if (
        payload["template_family_count_distribution"]
        != EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION
    ):
        raise AssertionError("unexpected template family-count distribution")
    if len(payload["templates"]) != EXPECTED_SELF_EDGE_TEMPLATE_COUNT:
        raise AssertionError("unexpected template record count")
