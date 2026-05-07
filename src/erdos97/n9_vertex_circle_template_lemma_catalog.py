"""Build a derived n=9 vertex-circle template lemma-candidate catalog.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_self_edge_template_packet import (
    EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT,
    EXPECTED_SELF_EDGE_FAMILY_COUNT,
    EXPECTED_SELF_EDGE_TEMPLATE_COUNT,
    EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS as EXPECTED_SELF_EDGE_TEMPLATE_ASSIGNMENTS,
    EXPECTED_TEMPLATE_FAMILY_COUNTS as EXPECTED_SELF_EDGE_TEMPLATE_FAMILIES,
    SCHEMA as SELF_EDGE_PACKET_SCHEMA,
)
from erdos97.n9_vertex_circle_strict_cycle_template_packet import (
    EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT,
    EXPECTED_STRICT_CYCLE_FAMILY_COUNT,
    EXPECTED_STRICT_CYCLE_TEMPLATE_COUNT,
    EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS as EXPECTED_STRICT_CYCLE_TEMPLATE_ASSIGNMENTS,
    EXPECTED_TEMPLATE_FAMILY_COUNTS as EXPECTED_STRICT_CYCLE_TEMPLATE_FAMILIES,
    SCHEMA as STRICT_CYCLE_PACKET_SCHEMA,
)


SCHEMA = "erdos97.n9_vertex_circle_template_lemma_catalog.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Derived lemma-candidate catalog for the 12 n=9 vertex-circle local-core "
    "templates covering 184 frontier assignments; not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_template_lemma_catalog.py",
    "command": (
        "python scripts/check_n9_vertex_circle_template_lemma_catalog.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SOURCE_ASSIGNMENT_COUNT = 184
EXPECTED_TEMPLATE_COUNT = 12
EXPECTED_FAMILY_COUNT = 16
EXPECTED_COVERED_ASSIGNMENT_COUNT = 184
EXPECTED_TEMPLATE_STATUS_COUNTS = {"self_edge": 9, "strict_cycle": 3}
EXPECTED_FAMILY_STATUS_COUNTS = {"self_edge": 13, "strict_cycle": 3}
EXPECTED_STATUS_ASSIGNMENT_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS = {
    **EXPECTED_SELF_EDGE_TEMPLATE_ASSIGNMENTS,
    **EXPECTED_STRICT_CYCLE_TEMPLATE_ASSIGNMENTS,
}
EXPECTED_TEMPLATE_FAMILY_COUNTS = {
    **EXPECTED_SELF_EDGE_TEMPLATE_FAMILIES,
    **EXPECTED_STRICT_CYCLE_TEMPLATE_FAMILIES,
}
EXPECTED_TEMPLATE_CORE_SIZE_COUNTS = {"3": 2, "4": 5, "5": 2, "6": 3}
EXPECTED_FAMILY_CORE_SIZE_COUNTS = {"3": 5, "4": 6, "5": 2, "6": 3}
EXPECTED_TEMPLATE_IDS = tuple(f"T{index:02d}" for index in range(1, 13))


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _template_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = packet.get("templates")
    if not isinstance(rows, list):
        raise ValueError("template packet must contain templates")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("template packet rows must be objects")
    return rows


def _core_template_families(core_template_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = core_template_payload.get("families")
    if not isinstance(rows, list):
        raise ValueError("core-template artifact must contain families")
    if not all(isinstance(row, dict) for row in rows):
        raise ValueError("core-template family rows must be objects")
    return rows


def _family_summaries(template: dict[str, Any]) -> list[dict[str, Any]]:
    records = template.get("family_records")
    if not isinstance(records, list):
        raise ValueError(f"{template.get('template_id')} must contain family_records")
    summaries = []
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("family records must be objects")
        summary = {
            "family_id": str(record["family_id"]),
            "template_id": str(record["template_id"]),
            "status": str(record["status"]),
            "assignment_count": int(record["assignment_count"]),
            "orbit_size": int(record["orbit_size"]),
            "core_size": int(record["core_size"]),
        }
        if record["status"] == "self_edge":
            edge = record["strict_inequality"]
            equality = record["distance_equality"]
            summary.update(
                {
                    "path_length": int(record["path_length"]),
                    "outer_span": int(edge["outer_span"]),
                    "inner_span": int(edge["inner_span"]),
                    "outer_pair": edge["outer_pair"],
                    "inner_pair": edge["inner_pair"],
                    "equality_path_length": len(equality["path"]),
                    "contradiction_kind": "self_edge",
                }
            )
        elif record["status"] == "strict_cycle":
            summary.update(
                {
                    "cycle_length": int(record["cycle_length"]),
                    "strict_edge_count": int(record["strict_edge_count"]),
                    "span_signature": str(record["span_signature"]),
                    "cycle_step_count": len(record["cycle_steps"]),
                    "contradiction_kind": "strict_cycle",
                }
            )
        else:
            raise ValueError(f"unexpected family status: {record['status']!r}")
        summaries.append(summary)
    return summaries


def _self_edge_catalog_record(template: dict[str, Any]) -> dict[str, Any]:
    template_id = str(template["template_id"])
    return {
        "template_id": template_id,
        "status": "self_edge",
        "template_key": str(template["template_key"]),
        "coverage": {
            "assignment_count": int(template["assignment_count"]),
            "assignment_ids": list(template["assignment_ids"]),
            "family_count": int(template["family_count"]),
            "families": list(template["families"]),
            "orbit_size_sum": int(template["orbit_size_sum"]),
        },
        "hypothesis_shape": {
            "core_size": int(template["core_size"]),
            "strict_edge_count": int(template["strict_edge_count"]),
            "path_length_counts": template["path_length_counts"],
            "shared_endpoint_counts": template["shared_endpoint_counts"],
            "selected_path_shape_counts": template["selected_path_shape_counts"],
            "self_edge_shape_counts": template["self_edge_shape_counts"],
        },
        "conclusion_shape": {
            "kind": "self_edge",
            "strict_graph_obstruction": "reflexive strict edge after selected-distance quotienting",
            "certificate_fields": ["strict_inequality", "distance_equality"],
        },
        "family_summaries": _family_summaries(template),
    }


def _strict_cycle_catalog_record(template: dict[str, Any]) -> dict[str, Any]:
    template_id = str(template["template_id"])
    return {
        "template_id": template_id,
        "status": "strict_cycle",
        "template_key": str(template["template_key"]),
        "coverage": {
            "assignment_count": int(template["assignment_count"]),
            "assignment_ids": list(template["assignment_ids"]),
            "family_count": int(template["family_count"]),
            "families": list(template["families"]),
            "orbit_size_sum": int(template["orbit_size_sum"]),
        },
        "hypothesis_shape": {
            "core_size": int(template["core_size"]),
            "strict_edge_count": int(template["strict_edge_count"]),
            "cycle_length": int(template["cycle_length"]),
            "cycle_length_counts": template["cycle_length_counts"],
            "connector_path_length_counts": template["connector_path_length_counts"],
            "span_signature_counts": template["span_signature_counts"],
            "cycle_span_counts": template["cycle_span_counts"],
        },
        "conclusion_shape": {
            "kind": "strict_cycle",
            "strict_graph_obstruction": "directed strict cycle after selected-distance quotienting",
            "certificate_fields": ["cycle_steps", "equality_to_next_outer_pair"],
        },
        "family_summaries": _family_summaries(template),
    }


def _source_artifacts(
    self_edge_packet: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
    core_template_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "path": "data/certificates/n9_vertex_circle_self_edge_template_packet.json",
            "role": "self-edge template packet source for 9 catalog records",
            "schema": self_edge_packet.get("schema"),
            "status": self_edge_packet.get("status"),
            "trust": self_edge_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_strict_cycle_template_packet.json",
            "role": "strict-cycle template packet source for 3 catalog records",
            "schema": strict_cycle_packet.get("schema"),
            "status": strict_cycle_packet.get("status"),
            "trust": strict_cycle_packet.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_core_templates.json",
            "role": "family/template crosswalk and core-size distribution source",
            "schema": core_template_payload.get("schema"),
            "status": core_template_payload.get("status"),
            "trust": core_template_payload.get("trust"),
        },
    ]


def _assert_core_template_crosswalk(
    records: list[dict[str, Any]],
    core_template_payload: dict[str, Any],
) -> dict[str, int]:
    expected_by_family = {
        str(row["family_id"]): row for row in _core_template_families(core_template_payload)
    }
    actual_by_family = {}
    for record in records:
        for family in record["family_summaries"]:
            actual_by_family[str(family["family_id"])] = {
                "template_id": str(record["template_id"]),
                "status": str(record["status"]),
                "core_size": int(family["core_size"]),
                "assignment_count": int(family["assignment_count"]),
            }
    if set(actual_by_family) != set(expected_by_family):
        raise AssertionError("catalog family coverage does not match core-template artifact")
    core_sizes: Counter[int] = Counter()
    for family_id, expected in expected_by_family.items():
        actual = actual_by_family[family_id]
        for key in ("template_id", "status", "core_size"):
            if actual[key] != expected[key]:
                raise AssertionError(f"{family_id} {key} mismatch")
        if actual["assignment_count"] != int(expected["orbit_size"]):
            raise AssertionError(f"{family_id} orbit/assignment count mismatch")
        core_sizes[int(expected["core_size"])] += 1
    return _json_counter(core_sizes)


def template_lemma_catalog_payload(
    self_edge_packet: dict[str, Any],
    strict_cycle_packet: dict[str, Any],
    core_template_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return the derived n=9 template lemma-candidate catalog."""

    if self_edge_packet.get("schema") != SELF_EDGE_PACKET_SCHEMA:
        raise ValueError("unexpected self-edge template packet schema")
    if strict_cycle_packet.get("schema") != STRICT_CYCLE_PACKET_SCHEMA:
        raise ValueError("unexpected strict-cycle template packet schema")

    records = [
        _self_edge_catalog_record(template)
        for template in _template_rows(self_edge_packet)
    ] + [
        _strict_cycle_catalog_record(template)
        for template in _template_rows(strict_cycle_packet)
    ]
    records = sorted(records, key=lambda record: str(record["template_id"]))

    template_status_counts: Counter[str] = Counter(str(record["status"]) for record in records)
    status_assignment_counts: Counter[str] = Counter()
    template_core_sizes: Counter[int] = Counter()
    template_assignment_counts: dict[str, int] = {}
    template_family_counts: dict[str, int] = {}
    assignment_ids: list[str] = []
    family_count = 0
    for record in records:
        template_id = str(record["template_id"])
        coverage = record["coverage"]
        status = str(record["status"])
        assignment_count = int(coverage["assignment_count"])
        status_assignment_counts[status] += assignment_count
        template_core_sizes[int(record["hypothesis_shape"]["core_size"])] += 1
        template_assignment_counts[template_id] = assignment_count
        template_family_counts[template_id] = int(coverage["family_count"])
        assignment_ids.extend(str(item) for item in coverage["assignment_ids"])
        family_count += int(coverage["family_count"])

    if len(assignment_ids) != len(set(assignment_ids)):
        raise AssertionError("assignment ids overlap across catalog records")
    family_core_size_counts = _assert_core_template_crosswalk(records, core_template_payload)

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "cyclic_order": list(n9.ORDER),
        "source_assignment_count": int(self_edge_packet["source_assignment_count"]),
        "covered_assignment_count": len(assignment_ids),
        "self_edge_assignment_count": int(self_edge_packet["self_edge_assignment_count"]),
        "strict_cycle_assignment_count": int(
            strict_cycle_packet["strict_cycle_assignment_count"]
        ),
        "template_count": len(records),
        "self_edge_template_count": int(self_edge_packet["self_edge_template_count"]),
        "strict_cycle_template_count": int(
            strict_cycle_packet["strict_cycle_template_count"]
        ),
        "family_count": family_count,
        "self_edge_family_count": int(self_edge_packet["self_edge_family_count"]),
        "strict_cycle_family_count": int(strict_cycle_packet["strict_cycle_family_count"]),
        "template_status_counts": _json_counter(template_status_counts),
        "family_status_counts": {
            "self_edge": int(self_edge_packet["self_edge_family_count"]),
            "strict_cycle": int(strict_cycle_packet["strict_cycle_family_count"]),
        },
        "status_assignment_counts": _json_counter(status_assignment_counts),
        "template_assignment_counts": template_assignment_counts,
        "template_family_counts": template_family_counts,
        "template_core_size_counts": _json_counter(template_core_sizes),
        "family_core_size_counts": family_core_size_counts,
        "templates": records,
        "interpretation": [
            "Each catalog record is derived from a checked template packet and summarizes one local-core template as a lemma candidate.",
            "Self-edge records end in a reflexive strict inequality after selected-distance quotienting.",
            "Strict-cycle records end in a directed strict cycle after selected-distance quotienting.",
            "Template ids and catalog records are reviewer-navigation and lemma-mining diagnostics, not theorem names.",
            "The catalog is derived from review-pending n=9 diagnostics and is not an independent review of the exhaustive checker.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": _source_artifacts(
            self_edge_packet,
            strict_cycle_packet,
            core_template_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_template_lemma_catalog_counts(payload)
    return payload


def assert_expected_template_lemma_catalog_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the template lemma-candidate catalog."""

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
    if payload["covered_assignment_count"] != EXPECTED_COVERED_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected covered assignment count")
    if payload["self_edge_assignment_count"] != EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected self-edge assignment count")
    if payload["strict_cycle_assignment_count"] != EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected strict-cycle assignment count")
    if payload["template_count"] != EXPECTED_TEMPLATE_COUNT:
        raise AssertionError("unexpected template count")
    if payload["self_edge_template_count"] != EXPECTED_SELF_EDGE_TEMPLATE_COUNT:
        raise AssertionError("unexpected self-edge template count")
    if payload["strict_cycle_template_count"] != EXPECTED_STRICT_CYCLE_TEMPLATE_COUNT:
        raise AssertionError("unexpected strict-cycle template count")
    if payload["family_count"] != EXPECTED_FAMILY_COUNT:
        raise AssertionError("unexpected family count")
    if payload["self_edge_family_count"] != EXPECTED_SELF_EDGE_FAMILY_COUNT:
        raise AssertionError("unexpected self-edge family count")
    if payload["strict_cycle_family_count"] != EXPECTED_STRICT_CYCLE_FAMILY_COUNT:
        raise AssertionError("unexpected strict-cycle family count")
    if payload["template_status_counts"] != EXPECTED_TEMPLATE_STATUS_COUNTS:
        raise AssertionError("unexpected template status counts")
    if payload["family_status_counts"] != EXPECTED_FAMILY_STATUS_COUNTS:
        raise AssertionError("unexpected family status counts")
    if payload["status_assignment_counts"] != EXPECTED_STATUS_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected status assignment counts")
    if payload["template_assignment_counts"] != EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected template assignment counts")
    if payload["template_family_counts"] != EXPECTED_TEMPLATE_FAMILY_COUNTS:
        raise AssertionError("unexpected template family counts")
    if payload["template_core_size_counts"] != EXPECTED_TEMPLATE_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected template core-size counts")
    if payload["family_core_size_counts"] != EXPECTED_FAMILY_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected family core-size counts")
    template_ids = tuple(record["template_id"] for record in payload["templates"])
    if template_ids != EXPECTED_TEMPLATE_IDS:
        raise AssertionError(f"unexpected template ids: {template_ids!r}")
