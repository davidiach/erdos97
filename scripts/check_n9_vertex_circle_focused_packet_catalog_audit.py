#!/usr/bin/env python3
"""Audit focused n=9 local-lemma packets against the template catalog JSON."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.json_io import load_json
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_TEMPLATE_CATALOG = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_template_lemma_catalog.json"
)
DEFAULT_LOCAL_LEMMAS = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_local_lemmas.json"
)
DEFAULT_TEMPLATE_PACKET_PATHS = {
    "self_edge": ROOT / "data" / "certificates" / "n9_vertex_circle_self_edge_template_packet.json",
    "strict_cycle": (
        ROOT / "data" / "certificates" / "n9_vertex_circle_strict_cycle_template_packet.json"
    ),
}
DEFAULT_PACKET_PATHS = {
    "T01": ROOT / "data" / "certificates" / "n9_vertex_circle_t01_self_edge_lemma_packet.json",
    "T02": ROOT / "data" / "certificates" / "n9_vertex_circle_t02_self_edge_lemma_packet.json",
    "T03": ROOT / "data" / "certificates" / "n9_vertex_circle_t03_self_edge_lemma_packet.json",
    "T04": ROOT / "data" / "certificates" / "n9_vertex_circle_t04_self_edge_lemma_packet.json",
    "T05": ROOT / "data" / "certificates" / "n9_vertex_circle_t05_self_edge_lemma_packet.json",
    "T06": ROOT / "data" / "certificates" / "n9_vertex_circle_t06_self_edge_lemma_packet.json",
    "T07": ROOT / "data" / "certificates" / "n9_vertex_circle_t07_self_edge_lemma_packet.json",
    "T08": ROOT / "data" / "certificates" / "n9_vertex_circle_t08_self_edge_lemma_packet.json",
    "T09": ROOT / "data" / "certificates" / "n9_vertex_circle_t09_self_edge_lemma_packet.json",
    "T10": ROOT / "data" / "certificates" / "n9_vertex_circle_t10_strict_cycle_lemma_packet.json",
    "T11": ROOT / "data" / "certificates" / "n9_vertex_circle_t11_strict_cycle_lemma_packet.json",
    "T12": ROOT / "data" / "certificates" / "n9_vertex_circle_t12_strict_cycle_lemma_packet.json",
}

SCHEMA = "erdos97.n9_vertex_circle_focused_packet_catalog_audit.v1"
STATUS = "REVIEW_PENDING_FOCUSED_PACKET_CATALOG_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "JSON-only cross-artifact audit for the review-pending n=9 vertex-circle "
    "focused local-lemma packets. It checks that T01..T12 packet coverage, "
    "source catalog records, and aggregate focused-note crosschecks agree with "
    "the template lemma catalog, source template packets, and local-lemma scan. "
    "It does not prove packet soundness, local-lemma completeness, frontier "
    "coverage, n=9, a counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_focused_packet_catalog_audit.py "
        "--check --assert-expected --json"
    ),
}
SUMMARY_JSON_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "n",
    "row_size",
    "focused_packet_catalog_audit",
    "source_artifacts",
    "packet_artifacts",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
SUMMARY_AUDIT_OMIT_KEYS = {"packet_records"}

EXPECTED_TEMPLATE_IDS = [f"T{index:02d}" for index in range(1, 13)]
EXPECTED_STATUS_COUNTS = {"self_edge": 9, "strict_cycle": 3}
EXPECTED_STATUS_ASSIGNMENT_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_FAMILY_COUNT = 16
EXPECTED_ASSIGNMENT_COUNT = 184
ALLOWED_SOURCE_TEMPLATE_OMISSIONS = {
    template_id: {"family_records"} for template_id in EXPECTED_TEMPLATE_IDS
}
ALLOWED_SOURCE_TEMPLATE_OMISSIONS["T01"].update(
    {"orbit_size_sum", "shared_endpoint_counts"}
)
EXPECTED_ALLOWED_SOURCE_TEMPLATE_OMISSION_COUNT = sum(
    len(fields) for fields in ALLOWED_SOURCE_TEMPLATE_OMISSIONS.values()
)


def focused_packet_catalog_audit_payload(
    *,
    template_catalog_path: Path = DEFAULT_TEMPLATE_CATALOG,
    local_lemmas_path: Path = DEFAULT_LOCAL_LEMMAS,
    template_packet_paths: Mapping[str, Path] | None = None,
    packet_paths: Mapping[str, Path] | None = None,
) -> dict[str, Any]:
    """Return a JSON-only focused-packet/catalog cross-audit payload."""

    resolved_packets = {
        template_id: _resolve(path)
        for template_id, path in (packet_paths or DEFAULT_PACKET_PATHS).items()
    }
    catalog_path = _resolve(template_catalog_path)
    local_path = _resolve(local_lemmas_path)
    resolved_template_packets = {
        kind: _resolve(path)
        for kind, path in (template_packet_paths or DEFAULT_TEMPLATE_PACKET_PATHS).items()
    }
    catalog = load_json(catalog_path)
    local_lemmas = load_json(local_path)
    template_packets = {
        kind: load_json(path) for kind, path in resolved_template_packets.items()
    }
    packets = {
        template_id: load_json(path) for template_id, path in resolved_packets.items()
    }
    errors: list[str] = []
    summary = _audit(
        catalog,
        local_lemmas,
        template_packets,
        packets,
        resolved_packets,
        errors,
    )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "row_size": 4,
        "focused_packet_catalog_audit": summary,
        "source_artifacts": [
            {
                "path": display_path(catalog_path, ROOT),
                "role": "template lemma-candidate catalog",
                "schema": catalog.get("schema") if isinstance(catalog, Mapping) else None,
                "status": catalog.get("status") if isinstance(catalog, Mapping) else None,
                "trust": catalog.get("trust") if isinstance(catalog, Mapping) else None,
            },
            {
                "path": display_path(local_path, ROOT),
                "role": "aggregate local-lemma scan",
                "schema": local_lemmas.get("schema") if isinstance(local_lemmas, Mapping) else None,
                "status": local_lemmas.get("status") if isinstance(local_lemmas, Mapping) else None,
                "trust": local_lemmas.get("trust") if isinstance(local_lemmas, Mapping) else None,
            },
            *[
                {
                    "path": display_path(path, ROOT),
                    "role": f"{kind.replace('_', '-')} template packet",
                    "schema": template_packets.get(kind, {}).get("schema")
                    if isinstance(template_packets.get(kind), Mapping)
                    else None,
                    "status": template_packets.get(kind, {}).get("status")
                    if isinstance(template_packets.get(kind), Mapping)
                    else None,
                    "trust": template_packets.get(kind, {}).get("trust")
                    if isinstance(template_packets.get(kind), Mapping)
                    else None,
                }
                for kind, path in sorted(resolved_template_packets.items())
            ],
        ],
        "packet_artifacts": [
            {
                "template_id": template_id,
                "path": display_path(path, ROOT),
                "schema": packets.get(template_id, {}).get("schema")
                if isinstance(packets.get(template_id), Mapping)
                else None,
                "status": packets.get(template_id, {}).get("status")
                if isinstance(packets.get(template_id), Mapping)
                else None,
                "trust": packets.get(template_id, {}).get("trust")
                if isinstance(packets.get(template_id), Mapping)
                else None,
            }
            for template_id, path in sorted(resolved_packets.items())
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the stored focused packets, template catalog, "
            "source template packets, and aggregate local-lemma focused-note "
            "crosschecks agree on the T01..T12 coverage ledger. This is "
            "packet/catalog bookkeeping only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_focused_packet_catalog_audit(payload: Mapping[str, Any]) -> None:
    """Assert stable counts for the focused packet/catalog audit."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not prove packet soundness",
        "local-lemma completeness",
        "frontier coverage",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    summary = payload.get("focused_packet_catalog_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("focused_packet_catalog_audit missing")
    expected = {
        "packet_count": 12,
        "catalog_template_count": 12,
        "focused_crosscheck_count": 12,
        "covered_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "covered_family_count": EXPECTED_FAMILY_COUNT,
        "template_ids": EXPECTED_TEMPLATE_IDS,
        "status_counts": EXPECTED_STATUS_COUNTS,
        "status_assignment_counts": EXPECTED_STATUS_ASSIGNMENT_COUNTS,
        "missing_packet_template_count": 0,
        "extra_packet_template_count": 0,
        "source_catalog_mismatch_count": 0,
        "catalog_coverage_mismatch_count": 0,
        "focused_crosscheck_mismatch_count": 0,
        "source_template_packet_count": 12,
        "duplicate_assignment_id_count": 0,
        "duplicate_family_id_count": 0,
        "source_template_mismatch_count": 0,
        "source_template_field_mismatch_count": 0,
        "source_template_extra_field_count": 0,
        "source_template_unexpected_missing_field_count": 0,
        "source_template_allowed_omitted_field_count": (
            EXPECTED_ALLOWED_SOURCE_TEMPLATE_OMISSION_COUNT
        ),
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit(
    catalog: Any,
    local_lemmas: Any,
    template_packets: Mapping[str, Any],
    packets: Mapping[str, Any],
    packet_paths: Mapping[str, Path],
    errors: list[str],
) -> dict[str, Any]:
    catalog_records = _catalog_records(catalog, errors)
    focused_records = _focused_records(local_lemmas, errors)
    source_template_records = _source_template_records(template_packets, errors)
    packet_records: list[dict[str, Any]] = []
    source_catalog_mismatch_count = 0
    catalog_coverage_mismatch_count = 0
    focused_crosscheck_mismatch_count = 0
    source_template_mismatch_count = 0
    source_template_field_mismatch_count = 0
    source_template_extra_field_count = 0
    source_template_unexpected_missing_field_count = 0
    source_template_allowed_omitted_field_count = 0
    assignment_ids: list[str] = []
    family_ids: list[str] = []
    status_counts: Counter[str] = Counter()
    status_assignment_counts: Counter[str] = Counter()
    missing_template_ids = sorted(set(EXPECTED_TEMPLATE_IDS) - set(packets))
    extra_template_ids = sorted(set(packets) - set(EXPECTED_TEMPLATE_IDS))
    if missing_template_ids:
        errors.append(f"missing packet template ids: {missing_template_ids!r}")
    if extra_template_ids:
        errors.append(f"extra packet template ids: {extra_template_ids!r}")

    for template_id in EXPECTED_TEMPLATE_IDS:
        packet = packets.get(template_id)
        if not isinstance(packet, Mapping):
            errors.append(f"{template_id}: packet must be an object")
            continue
        record = _packet_record(template_id, packet, packet_paths.get(template_id), errors)
        packet_records.append(record)
        assignment_ids.extend(record["assignment_ids"])
        family_ids.extend(record["family_ids"])
        status_counts[record["status"]] += 1
        status_assignment_counts[record["status"]] += record["assignment_count"]

        catalog_record = catalog_records.get(template_id)
        if catalog_record is None:
            errors.append(f"{template_id}: missing template catalog record")
            catalog_coverage_mismatch_count += 1
        else:
            if packet.get("source_catalog_record") != catalog_record:
                source_catalog_mismatch_count += 1
                errors.append(f"{template_id}: source_catalog_record mismatch")
            if not _coverage_matches(record, catalog_record):
                catalog_coverage_mismatch_count += 1
                errors.append(f"{template_id}: packet coverage does not match catalog")
            source_template = packet.get("source_template_record")
            template_comparison = _source_template_comparison(
                template_id,
                source_template,
                source_template_records.get(template_id),
            )
            record["source_template_stored_field_count"] = template_comparison[
                "stored_field_count"
            ]
            record["source_template_allowed_omitted_fields"] = template_comparison[
                "allowed_omitted_fields"
            ]
            source_template_field_mismatch_count += len(
                template_comparison["field_mismatches"]
            )
            source_template_extra_field_count += len(template_comparison["extra_fields"])
            source_template_unexpected_missing_field_count += len(
                template_comparison["unexpected_missing_fields"]
            )
            source_template_allowed_omitted_field_count += len(
                template_comparison["allowed_omitted_fields"]
            )
            if not template_comparison["matches"]:
                source_template_mismatch_count += 1
                errors.extend(template_comparison["errors"])

        focused = focused_records.get(template_id)
        if focused is None:
            focused_crosscheck_mismatch_count += 1
            errors.append(f"{template_id}: missing aggregate focused crosscheck")
        elif not _focused_matches(record, focused):
            focused_crosscheck_mismatch_count += 1
            errors.append(f"{template_id}: aggregate focused crosscheck mismatch")

    duplicate_assignment_id_count = len(assignment_ids) - len(set(assignment_ids))
    duplicate_family_id_count = len(family_ids) - len(set(family_ids))
    if duplicate_assignment_id_count:
        errors.append(f"duplicate assignment ids across packets: {duplicate_assignment_id_count}")
    if duplicate_family_id_count:
        errors.append(f"duplicate family ids across packets: {duplicate_family_id_count}")

    return {
        "packet_count": len(packet_records),
        "catalog_template_count": len(catalog_records),
        "focused_crosscheck_count": len(focused_records),
        "source_template_packet_count": len(source_template_records),
        "covered_assignment_count": len(assignment_ids),
        "covered_family_count": len(set(family_ids)),
        "template_ids": [record["template_id"] for record in packet_records],
        "status_counts": dict(sorted(status_counts.items())),
        "status_assignment_counts": dict(sorted(status_assignment_counts.items())),
        "missing_packet_template_count": len(missing_template_ids),
        "extra_packet_template_count": len(extra_template_ids),
        "source_catalog_mismatch_count": source_catalog_mismatch_count,
        "source_template_mismatch_count": source_template_mismatch_count,
        "source_template_field_mismatch_count": source_template_field_mismatch_count,
        "source_template_extra_field_count": source_template_extra_field_count,
        "source_template_unexpected_missing_field_count": (
            source_template_unexpected_missing_field_count
        ),
        "source_template_allowed_omitted_field_count": (
            source_template_allowed_omitted_field_count
        ),
        "catalog_coverage_mismatch_count": catalog_coverage_mismatch_count,
        "focused_crosscheck_mismatch_count": focused_crosscheck_mismatch_count,
        "duplicate_assignment_id_count": duplicate_assignment_id_count,
        "duplicate_family_id_count": duplicate_family_id_count,
        "packet_records": packet_records,
    }


def _catalog_records(catalog: Any, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(catalog, Mapping):
        errors.append("template catalog must be an object")
        return {}
    templates = catalog.get("templates")
    if not isinstance(templates, list):
        errors.append("template catalog templates must be a list")
        return {}
    records: dict[str, Mapping[str, Any]] = {}
    for item in templates:
        if not isinstance(item, Mapping):
            errors.append("template catalog records must be objects")
            continue
        template_id = str(item.get("template_id"))
        if template_id in records:
            errors.append(f"duplicate catalog template id: {template_id}")
        records[template_id] = item
    return records


def _focused_records(local_lemmas: Any, errors: list[str]) -> dict[str, Mapping[str, Any]]:
    if not isinstance(local_lemmas, Mapping):
        errors.append("local-lemma scan must be an object")
        return {}
    focused = local_lemmas.get("focused_note_crosscheck")
    if not isinstance(focused, list):
        errors.append("local-lemma focused_note_crosscheck must be a list")
        return {}
    records: dict[str, Mapping[str, Any]] = {}
    for item in focused:
        if not isinstance(item, Mapping):
            errors.append("focused crosscheck records must be objects")
            continue
        template_id = str(item.get("template_id"))
        if template_id in records:
            errors.append(f"duplicate focused template id: {template_id}")
        records[template_id] = item
    return records


def _source_template_records(
    template_packets: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Mapping[str, Any]]:
    records: dict[str, Mapping[str, Any]] = {}
    for kind, payload in sorted(template_packets.items()):
        if not isinstance(payload, Mapping):
            errors.append(f"{kind}: template packet must be an object")
            continue
        templates = payload.get("templates")
        if not isinstance(templates, list):
            errors.append(f"{kind}: template packet templates must be a list")
            continue
        for item in templates:
            if not isinstance(item, Mapping):
                errors.append(f"{kind}: template packet records must be objects")
                continue
            template_id = str(item.get("template_id"))
            if template_id in records:
                errors.append(f"duplicate source template id: {template_id}")
            records[template_id] = item
    return records


def _packet_record(
    expected_template_id: str,
    packet: Mapping[str, Any],
    path: Path | None,
    errors: list[str],
) -> dict[str, Any]:
    template_id = str(packet.get("template_id"))
    if template_id != expected_template_id:
        errors.append(f"{expected_template_id}: packet template_id is {template_id!r}")
    source_catalog = packet.get("source_catalog_record")
    status = "unknown"
    if isinstance(source_catalog, Mapping):
        status = str(source_catalog.get("status"))
    families = _string_list(packet.get("family_ids"))
    if not families:
        family_id = packet.get("family_id")
        if isinstance(family_id, str):
            families = [family_id]
    assignment_ids = _string_list(packet.get("assignment_ids"))
    assignment_count = int(packet.get("assignment_count", -1))
    if assignment_count != len(assignment_ids):
        errors.append(f"{expected_template_id}: assignment_count does not match assignment_ids")
    family_count = int(packet.get("family_count", -1))
    if family_count != len(families):
        errors.append(f"{expected_template_id}: family_count does not match family ids")
    family_assignment_counts = _int_map(packet.get("family_assignment_counts"))
    if not family_assignment_counts and len(families) == 1:
        family_assignment_counts = {families[0]: assignment_count}
    family_orbit_sizes = _int_map(packet.get("family_orbit_sizes"))
    if not family_orbit_sizes and len(families) == 1:
        family_orbit_sizes = {families[0]: int(packet.get("orbit_size", -1))}
    orbit_size_sum = int(packet.get("orbit_size_sum", packet.get("orbit_size", -1)))
    if sum(family_assignment_counts.values()) != assignment_count:
        errors.append(f"{expected_template_id}: family assignment counts do not sum")
    if sum(family_orbit_sizes.values()) != orbit_size_sum:
        errors.append(f"{expected_template_id}: family orbit sizes do not sum")
    return {
        "template_id": expected_template_id,
        "path": display_path(path, ROOT) if path is not None else None,
        "status": status,
        "family_ids": families,
        "family_count": len(families),
        "assignment_ids": assignment_ids,
        "assignment_count": assignment_count,
        "family_assignment_counts": dict(sorted(family_assignment_counts.items())),
        "family_orbit_sizes": dict(sorted(family_orbit_sizes.items())),
        "orbit_size_sum": orbit_size_sum,
        "core_size": int(packet.get("core_size", -1)),
    }


def _source_template_comparison(
    template_id: str,
    source_template: Any,
    source_record: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not isinstance(source_template, Mapping):
        return {
            "matches": False,
            "errors": [f"{template_id}: source_template_record must be an object"],
            "stored_field_count": 0,
            "field_mismatches": [],
            "extra_fields": [],
            "unexpected_missing_fields": [],
            "allowed_omitted_fields": [],
        }
    if source_record is None:
        return {
            "matches": False,
            "errors": [f"{template_id}: missing source template packet record"],
            "stored_field_count": len(source_template),
            "field_mismatches": [],
            "extra_fields": sorted(set(source_template)),
            "unexpected_missing_fields": [],
            "allowed_omitted_fields": [],
        }

    expected_keys = set(source_record)
    stored_keys = set(source_template)
    allowed_omitted = ALLOWED_SOURCE_TEMPLATE_OMISSIONS.get(template_id, set())
    missing = expected_keys - stored_keys
    unexpected_missing = sorted(missing - allowed_omitted)
    allowed_missing = sorted(missing & allowed_omitted)
    extra_fields = sorted(stored_keys - expected_keys)
    field_mismatches = sorted(
        key for key in stored_keys & expected_keys if source_template[key] != source_record[key]
    )
    errors = []
    if field_mismatches:
        errors.append(
            f"{template_id}: source_template_record stored field mismatch: "
            f"{field_mismatches!r}"
        )
    if extra_fields:
        errors.append(
            f"{template_id}: source_template_record extra fields: {extra_fields!r}"
        )
    if unexpected_missing:
        errors.append(
            f"{template_id}: source_template_record unexpected missing fields: "
            f"{unexpected_missing!r}"
        )
    return {
        "matches": not errors,
        "errors": errors,
        "stored_field_count": len(source_template),
        "field_mismatches": field_mismatches,
        "extra_fields": extra_fields,
        "unexpected_missing_fields": unexpected_missing,
        "allowed_omitted_fields": allowed_missing,
    }


def _coverage_matches(record: Mapping[str, Any], catalog_record: Mapping[str, Any]) -> bool:
    coverage = catalog_record.get("coverage")
    if not isinstance(coverage, Mapping):
        return False
    return (
        coverage.get("assignment_count") == record["assignment_count"]
        and coverage.get("assignment_ids") == record["assignment_ids"]
        and coverage.get("families") == record["family_ids"]
        and coverage.get("family_count") == record["family_count"]
        and coverage.get("orbit_size_sum") == record["orbit_size_sum"]
        and catalog_record.get("status") == record["status"]
    )


def _focused_matches(record: Mapping[str, Any], focused: Mapping[str, Any]) -> bool:
    family_rows = focused.get("families_checked")
    if not isinstance(family_rows, list):
        return False
    family_assignment_counts = {
        str(item.get("family_id")): int(item.get("assignment_count", -1))
        for item in family_rows
        if isinstance(item, Mapping)
    }
    family_orbit_sizes = {
        str(item.get("family_id")): int(item.get("orbit_size", -1))
        for item in family_rows
        if isinstance(item, Mapping)
    }
    return (
        focused.get("check_status") == "checked"
        and focused.get("source_kind") == "focused_packet"
        and focused.get("packet_key") == record["template_id"]
        and focused.get("template_id") == record["template_id"]
        and focused.get("packet_path") == record["path"]
        and focused.get("family_ids") == record["family_ids"]
        and focused.get("covered_assignment_count") == record["assignment_count"]
        and family_assignment_counts == record["family_assignment_counts"]
        and family_orbit_sizes == record["family_orbit_sizes"]
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _int_map(value: Any) -> dict[str, int]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): int(item) for key, item in value.items()}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["focused_packet_catalog_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"packets checked: {summary['packet_count']}",
        f"assignments covered: {summary['covered_assignment_count']}",
        f"families covered: {summary['covered_family_count']}",
        f"status counts: {summary['status_counts']}",
        f"focused mismatches: {summary['focused_crosscheck_mismatch_count']}",
    ]


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audit = summary.get("focused_packet_catalog_audit")
    if isinstance(audit, Mapping):
        summary["focused_packet_catalog_audit"] = {
            key: value
            for key, value in audit.items()
            if key not in SUMMARY_AUDIT_OMIT_KEYS
        }
    return summary


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--template-catalog", type=Path, default=DEFAULT_TEMPLATE_CATALOG)
    parser.add_argument("--local-lemmas", type=Path, default=DEFAULT_LOCAL_LEMMAS)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON summary",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        payload = focused_packet_catalog_audit_payload(
            template_catalog_path=args.template_catalog,
            local_lemmas_path=args.local_lemmas,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_focused_packet_catalog_audit(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 focused packet/catalog audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: focused packet/catalog audit checks passed")
    else:
        print("FAILED: n=9 focused packet/catalog audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
