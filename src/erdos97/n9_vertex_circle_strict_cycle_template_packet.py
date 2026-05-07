"""Build a compact n=9 strict-cycle template packet for reviewer navigation.

This module is diagnostic. It does not prove Erdos Problem #97, does not
claim a counterexample, and does not promote the review-pending n=9 checker.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.n9_vertex_circle_obstruction_shapes import EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS
from erdos97.n9_vertex_circle_self_edge_path_join import (
    compact_core_rows,
    validate_equality_path,
)
from erdos97.vertex_circle_quotient_replay import pair


SCHEMA = "erdos97.n9_vertex_circle_strict_cycle_template_packet.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Template-level packet for the 3 strict-cycle local-core templates covering "
    "26 n=9 strict-cycle frontier assignments; not a proof of n=9, not a "
    "counterexample, not an independent review of the exhaustive checker, "
    "and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_strict_cycle_template_packet.py",
    "command": (
        "python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT = 158
EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT = 26
EXPECTED_STRICT_CYCLE_FAMILY_COUNT = 3
EXPECTED_STRICT_CYCLE_TEMPLATE_COUNT = 3
EXPECTED_LOCAL_CORE_CYCLE_STEP_COUNT = 60
EXPECTED_LOCAL_CORE_CYCLE_LENGTH_COUNTS = {"2": 18, "3": 8}
EXPECTED_FIRST_FULL_ASSIGNMENT_CYCLE_LENGTH_COUNTS = {"2": 22, "3": 4}
EXPECTED_CORE_SIZE_ASSIGNMENT_COUNTS = {"4": 24, "6": 2}
EXPECTED_STRICT_EDGE_COUNT_ASSIGNMENT_COUNTS = {"36": 24, "54": 2}
EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS = {"0": 6, "1": 28, "2": 26}
EXPECTED_SPAN_SIGNATURE_COUNTS = {
    "2:1,2:1": 18,
    "2:1,3:1,3:2": 6,
    "3:1,3:1,3:1": 2,
}
EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS = {"T10": 18, "T11": 6, "T12": 2}
EXPECTED_TEMPLATE_FAMILY_COUNTS = {"T10": 1, "T11": 1, "T12": 1}
EXPECTED_TEMPLATE_CYCLE_LENGTH_COUNTS = {
    "T10": {"2": 18},
    "T11": {"3": 6},
    "T12": {"3": 2},
}
EXPECTED_TEMPLATE_CONNECTOR_PATH_LENGTH_COUNTS = {
    "T10": {"1": 18, "2": 18},
    "T11": {"0": 6, "1": 6, "2": 6},
    "T12": {"1": 4, "2": 2},
}
EXPECTED_TEMPLATE_SPAN_SIGNATURE_COUNTS = {
    "T10": {"2:1,2:1": 18},
    "T11": {"2:1,3:1,3:2": 6},
    "T12": {"3:1,3:1,3:1": 2},
}
EXPECTED_TEMPLATE_CORE_SIZE_COUNTS = {"4": 2, "6": 1}
EXPECTED_TEMPLATE_STRICT_EDGE_COUNT_COUNTS = {"36": 2, "54": 1}
EXPECTED_TEMPLATE_CYCLE_LENGTH_DISTRIBUTION = {"2": 1, "3": 2}
EXPECTED_TEMPLATE_FAMILY_COUNT_DISTRIBUTION = {"1": 3}


def _strict_cycle_certificates(
    local_core_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    certificates = local_core_payload.get("certificates")
    if not isinstance(certificates, list):
        raise ValueError("local-core payload must contain certificates")
    return {
        str(certificate["family_id"]): certificate
        for certificate in certificates
        if isinstance(certificate, dict) and certificate.get("status") == "strict_cycle"
    }


def _strict_cycle_template_rows(
    template_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    templates = template_payload.get("templates")
    if not isinstance(templates, list):
        raise ValueError("template payload must contain templates")
    return {
        str(template["template_id"]): template
        for template in templates
        if isinstance(template, dict) and template.get("status") == "strict_cycle"
    }


def _strict_cycle_template_family_rows(
    template_payload: dict[str, Any],
) -> dict[str, dict[str, Any]]:
    families = template_payload.get("families")
    if not isinstance(families, list):
        raise ValueError("template payload must contain families")
    return {
        str(family["family_id"]): family
        for family in families
        if isinstance(family, dict) and family.get("status") == "strict_cycle"
    }


def _path_join_family_rows(path_join_payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    families = path_join_payload.get("families")
    if not isinstance(families, list):
        raise ValueError("strict-cycle path join must contain families")
    return {str(family["family_id"]): family for family in families}


def _path_join_records_by_template(
    path_join_payload: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    records = path_join_payload.get("records")
    if not isinstance(records, list):
        raise ValueError("strict-cycle path join must contain records")
    by_template: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not isinstance(record, dict):
            raise ValueError("strict-cycle path-join records must be objects")
        by_template[str(record["template_id"])].append(record)
    return {template_id: rows for template_id, rows in sorted(by_template.items())}


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _span_signature_from_cycle_span_counts(span_counts: Sequence[dict[str, Any]]) -> str:
    tokens = []
    for span_count in span_counts:
        count = int(span_count["count"])
        outer_span = int(span_count["outer_span"])
        inner_span = int(span_count["inner_span"])
        tokens.extend(f"{outer_span}:{inner_span}" for _ in range(count))
    return ",".join(sorted(tokens))


def _validate_cycle_steps(
    rows: Sequence[Sequence[int]],
    steps: Sequence[dict[str, Any]],
) -> None:
    for index, step in enumerate(steps):
        edge = step["strict_inequality"]
        equality = step["equality_to_next_outer_pair"]
        next_edge = steps[(index + 1) % len(steps)]["strict_inequality"]
        if pair(*equality["start_pair"]) != pair(*edge["inner_pair"]):
            raise AssertionError("cycle equality must start at current inner pair")
        if pair(*equality["end_pair"]) != pair(*next_edge["outer_pair"]):
            raise AssertionError("cycle equality must end at next outer pair")
        validate_equality_path(rows, equality)


def _family_record(
    certificate: dict[str, Any],
    family_row: dict[str, Any],
    template_family_row: dict[str, Any],
) -> dict[str, Any]:
    family_id = str(certificate["family_id"])
    if family_id != str(family_row["family_id"]):
        raise AssertionError("family row does not match certificate")
    if family_id != str(template_family_row["family_id"]):
        raise AssertionError("template family row does not match certificate")
    if family_row["status"] != "strict_cycle":
        raise AssertionError("family row must be strict_cycle")
    if template_family_row["status"] != "strict_cycle":
        raise AssertionError("template family row must be strict_cycle")

    rows = compact_core_rows(certificate)
    steps = certificate["cycle_steps"]
    _validate_cycle_steps(rows, steps)
    cycle_span_counts = template_family_row["obstruction_summary"]["cycle_span_counts"]
    span_signature = _span_signature_from_cycle_span_counts(cycle_span_counts)
    expected = {
        "template_id": str(template_family_row["template_id"]),
        "core_size": int(certificate["core_size"]),
        "orbit_size": int(certificate["orbit_size"]),
        "cycle_length": len(steps),
        "strict_edge_count": int(template_family_row["strict_edge_count"]),
        "span_signature": span_signature,
        "status": "strict_cycle",
    }
    for key, value in expected.items():
        if family_row.get(key) != value:
            raise AssertionError(f"{family_id} {key} mismatch")
    return {
        "family_id": family_id,
        "template_id": str(template_family_row["template_id"]),
        "status": "strict_cycle",
        "assignment_count": int(family_row["assignment_count"]),
        "orbit_size": int(certificate["orbit_size"]),
        "core_size": int(certificate["core_size"]),
        "cycle_length": len(steps),
        "strict_edge_count": int(template_family_row["strict_edge_count"]),
        "span_signature": span_signature,
        "core_selected_rows": rows,
        "cycle_steps": steps,
        "contradiction": {
            "kind": "strict_cycle",
            "statement": (
                "strict inequalities form a directed cycle after "
                "selected-distance quotienting"
            ),
            "cycle_length": len(steps),
        },
    }


def _template_record(
    template_id: str,
    template_row: dict[str, Any],
    records: Sequence[dict[str, Any]],
    family_rows: dict[str, dict[str, Any]],
    certificates: dict[str, dict[str, Any]],
    template_family_rows: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    template_families = [str(family_id) for family_id in template_row["families"]]
    path_join_families = sorted({str(record["family_id"]) for record in records})
    if path_join_families != sorted(template_families):
        raise AssertionError(f"{template_id} family coverage mismatch")

    family_records = []
    for family_id in sorted(template_families):
        family_row = family_rows.get(family_id)
        certificate = certificates.get(family_id)
        template_family_row = template_family_rows.get(family_id)
        if family_row is None or certificate is None or template_family_row is None:
            raise AssertionError(f"{template_id} missing family {family_id}")
        family_records.append(_family_record(certificate, family_row, template_family_row))

    assignment_count = len(records)
    cycle_length_counts: Counter[int] = Counter(
        int(record["cycle_length"]) for record in records
    )
    connector_path_lengths: Counter[int] = Counter()
    for record in records:
        connector_path_lengths.update(
            int(length) for length in record["connector_path_lengths"]
        )
    span_signatures: Counter[str] = Counter(str(record["span_signature"]) for record in records)
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
        "status": "strict_cycle",
        "core_size": int(template_row["core_size"]),
        "cycle_length": int(template_row["cycle_length"]),
        "strict_edge_count": int(template_row["strict_edge_count"]),
        "family_count": len(template_families),
        "assignment_count": assignment_count,
        "orbit_size_sum": int(template_row["orbit_size_sum"]),
        "assignment_ids": assignment_ids,
        "families": sorted(template_families),
        "cycle_length_counts": _json_counter(cycle_length_counts),
        "connector_path_length_counts": _json_counter(connector_path_lengths),
        "span_signature_counts": _json_counter(span_signatures),
        "cycle_span_counts": template_row["cycle_span_counts"],
        "family_records": family_records,
    }


def strict_cycle_template_packet_source_artifacts(
    local_core_payload: dict[str, Any],
    path_join_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> list[dict[str, Any]]:
    """Return embedded source-artifact metadata for the template packet."""

    return [
        {
            "path": "data/certificates/n9_vertex_circle_local_cores.json",
            "role": "canonical strict-cycle family local-core certificates",
            "type": local_core_payload.get("type"),
            "trust": local_core_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_strict_cycle_path_join.json",
            "role": "assignment-level transformed strict-cycle quotient cycles",
            "schema": path_join_payload.get("schema"),
            "status": path_join_payload.get("status"),
            "trust": path_join_payload.get("trust"),
        },
        {
            "path": "data/certificates/n9_vertex_circle_core_templates.json",
            "role": "strict-cycle template ids and cycle span summaries",
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
    ]


def strict_cycle_template_packet_payload(
    local_core_payload: dict[str, Any],
    path_join_payload: dict[str, Any],
    template_payload: dict[str, Any],
) -> dict[str, Any]:
    """Return the compact strict-cycle template packet."""

    certificates = _strict_cycle_certificates(local_core_payload)
    template_rows = _strict_cycle_template_rows(template_payload)
    family_rows = _path_join_family_rows(path_join_payload)
    template_family_rows = _strict_cycle_template_family_rows(template_payload)
    records_by_template = _path_join_records_by_template(path_join_payload)

    template_records = []
    core_sizes: Counter[int] = Counter()
    cycle_lengths: Counter[int] = Counter()
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
            template_family_rows,
        )
        core_sizes[int(record["core_size"])] += 1
        cycle_lengths[int(record["cycle_length"])] += 1
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
        "strict_cycle_assignment_count": int(
            path_join_payload["strict_cycle_assignment_count"]
        ),
        "strict_cycle_family_count": int(path_join_payload["strict_cycle_family_count"]),
        "strict_cycle_template_count": len(template_records),
        "local_core_cycle_step_count": int(path_join_payload["cycle_step_count"]),
        "local_core_cycle_length_counts": path_join_payload["cycle_length_counts"],
        "first_full_assignment_cycle_length_counts": path_join_payload[
            "first_full_assignment_cycle_length_counts"
        ],
        "core_size_assignment_counts": path_join_payload["core_size_assignment_counts"],
        "strict_edge_count_assignment_counts": path_join_payload[
            "strict_edge_count_assignment_counts"
        ],
        "connector_path_length_counts": path_join_payload["connector_path_length_counts"],
        "span_signature_counts": path_join_payload["span_signature_counts"],
        "template_assignment_counts": {
            str(record["template_id"]): int(record["assignment_count"])
            for record in template_records
        },
        "template_family_counts": {
            str(record["template_id"]): int(record["family_count"])
            for record in template_records
        },
        "template_cycle_length_counts": {
            str(record["template_id"]): record["cycle_length_counts"]
            for record in template_records
        },
        "template_connector_path_length_counts": {
            str(record["template_id"]): record["connector_path_length_counts"]
            for record in template_records
        },
        "template_span_signature_counts": {
            str(record["template_id"]): record["span_signature_counts"]
            for record in template_records
        },
        "template_core_size_counts": _json_counter(core_sizes),
        "template_cycle_length_distribution": _json_counter(cycle_lengths),
        "template_strict_edge_count_counts": _json_counter(strict_edge_counts),
        "template_family_count_distribution": _json_counter(family_count_distribution),
        "templates": template_records,
        "interpretation": [
            "Each template record groups strict-cycle family certificates with the same replay-derived template id.",
            "Family records keep canonical local-core rows, directed strict-cycle steps, and equality connectors.",
            "Connector path-length counts summarize the assignment-level transformed strict-cycle path join.",
            "Cycle-length counts here summarize transformed local-core certificates, not first full-assignment obstruction-shape cycles.",
            "These records are reviewer-navigation and lemma-mining diagnostics, not theorem names.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": strict_cycle_template_packet_source_artifacts(
            local_core_payload,
            path_join_payload,
            template_payload,
        ),
        "provenance": PROVENANCE,
    }
    assert_expected_strict_cycle_template_packet_counts(payload)
    return payload


def assert_expected_strict_cycle_template_packet_counts(payload: dict[str, Any]) -> None:
    """Assert stable headline counts for the strict-cycle template packet."""

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
    if payload["self_edge_assignment_count"] != EXPECTED_SELF_EDGE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected self-edge assignment count")
    if payload["strict_cycle_assignment_count"] != EXPECTED_STRICT_CYCLE_ASSIGNMENT_COUNT:
        raise AssertionError("unexpected strict-cycle assignment count")
    if payload["strict_cycle_family_count"] != EXPECTED_STRICT_CYCLE_FAMILY_COUNT:
        raise AssertionError("unexpected strict-cycle family count")
    if payload["strict_cycle_template_count"] != EXPECTED_STRICT_CYCLE_TEMPLATE_COUNT:
        raise AssertionError("unexpected strict-cycle template count")
    if payload["local_core_cycle_step_count"] != EXPECTED_LOCAL_CORE_CYCLE_STEP_COUNT:
        raise AssertionError("unexpected local-core cycle-step count")
    if (
        payload["local_core_cycle_length_counts"]
        != EXPECTED_LOCAL_CORE_CYCLE_LENGTH_COUNTS
    ):
        raise AssertionError("unexpected local-core cycle-length counts")
    if (
        payload["first_full_assignment_cycle_length_counts"]
        != EXPECTED_FIRST_FULL_ASSIGNMENT_CYCLE_LENGTH_COUNTS
    ):
        raise AssertionError("unexpected first full-assignment cycle-length counts")
    if payload["core_size_assignment_counts"] != EXPECTED_CORE_SIZE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected core-size assignment counts")
    if (
        payload["strict_edge_count_assignment_counts"]
        != EXPECTED_STRICT_EDGE_COUNT_ASSIGNMENT_COUNTS
    ):
        raise AssertionError("unexpected strict-edge-count assignment counts")
    if payload["connector_path_length_counts"] != EXPECTED_CONNECTOR_PATH_LENGTH_COUNTS:
        raise AssertionError("unexpected connector path-length counts")
    if payload["span_signature_counts"] != EXPECTED_SPAN_SIGNATURE_COUNTS:
        raise AssertionError("unexpected span-signature counts")
    if payload["template_assignment_counts"] != EXPECTED_TEMPLATE_ASSIGNMENT_COUNTS:
        raise AssertionError("unexpected template assignment counts")
    if payload["template_family_counts"] != EXPECTED_TEMPLATE_FAMILY_COUNTS:
        raise AssertionError("unexpected template family counts")
    if payload["template_cycle_length_counts"] != EXPECTED_TEMPLATE_CYCLE_LENGTH_COUNTS:
        raise AssertionError("unexpected template cycle-length counts")
    if (
        payload["template_connector_path_length_counts"]
        != EXPECTED_TEMPLATE_CONNECTOR_PATH_LENGTH_COUNTS
    ):
        raise AssertionError("unexpected template connector path-length counts")
    if payload["template_span_signature_counts"] != EXPECTED_TEMPLATE_SPAN_SIGNATURE_COUNTS:
        raise AssertionError("unexpected template span-signature counts")
    if payload["template_core_size_counts"] != EXPECTED_TEMPLATE_CORE_SIZE_COUNTS:
        raise AssertionError("unexpected template core-size counts")
    if (
        payload["template_cycle_length_distribution"]
        != EXPECTED_TEMPLATE_CYCLE_LENGTH_DISTRIBUTION
    ):
        raise AssertionError("unexpected template cycle-length distribution")
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
    if len(payload["templates"]) != EXPECTED_STRICT_CYCLE_TEMPLATE_COUNT:
        raise AssertionError("unexpected template record count")
