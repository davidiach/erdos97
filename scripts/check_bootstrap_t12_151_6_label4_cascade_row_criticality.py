#!/usr/bin/env python3
"""Check row-criticality of the 151:6 label-4 cascade cores."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402
from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    SelectedRow,
    replay_vertex_circle_quotient,
    result_to_json,
)

from scripts.check_bootstrap_t12_151_6_label4_support_hypothesis_ledger import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SUPPORT_LEDGER,
    LEDGER_STATUS as SOURCE_SUPPORT_LEDGER_STATUS,
    SCHEMA as SOURCE_SUPPORT_LEDGER_SCHEMA,
    STATUS as SOURCE_SUPPORT_LEDGER_STATUS_TEXT,
    assert_expected_support_hypothesis_ledger,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_label8_free_residual_targets import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGETS,
    SCHEMA as SOURCE_RESIDUAL_SCHEMA,
    STATUS as SOURCE_RESIDUAL_STATUS,
    TARGET_STATUS as SOURCE_RESIDUAL_TARGET_STATUS,
    assert_expected_label8_free_residual_targets,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _json_counter,
)


N = 9
CYCLIC_ORDER = tuple(range(N))
CASCADE_AUXILIARY_CENTER_PAIR = "5,8"
CASCADE_COMPONENT_KEY = "D[0,6]=D[4,5]=D[5,6]"
CASCADE_SUPPORT_CENTERS = [5, 6]
CASCADE_SUPPORT_WITNESS_PAIRS = [[4, 6], [0, 5]]
REQUIRED_CORE_CENTERS = [5, 6, 8]
PROPER_TRUNCATION_CENTERS = [
    [5],
    [6],
    [8],
    [5, 6],
    [5, 8],
    [6, 8],
]

SCHEMA = "erdos97.bootstrap_t12_151_6_label4_cascade_row_criticality.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_CASCADE_ROW_CRITICALITY_DIAGNOSTIC_ONLY"
CRITICALITY_STATUS = "CASCADE_CORES_ARE_THREE_ROW_CRITICAL_FOR_VERTEX_CIRCLE_REPLAY"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "label-4 cascade. It joins the support-hypothesis ledger to the "
    "label-8-free residual target signatures and checks that the three "
    "cascade signatures with auxiliary center pair 5,8 are vertex-circle "
    "strict-cycle obstructed only when all three local rows 5,6,8 are "
    "present. Every nonempty proper row truncation is quotient-clean. This "
    "does not prove support existence, does not prove row forcing, does not "
    "prove pair [3,5] impossible, does not prove endpoint-8 forcing, does "
    "not prove n=9, does not prove the bridge, is not a counterexample, and "
    "is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_cascade_row_criticality.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_cascade_row_criticality.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "cascade_signature_records",
    "claim_scope",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "cascade_component_key": CASCADE_COMPONENT_KEY,
    "cascade_auxiliary_center_pair": CASCADE_AUXILIARY_CENTER_PAIR,
    "cascade_required_support_centers": CASCADE_SUPPORT_CENTERS,
    "cascade_required_witness_pairs": CASCADE_SUPPORT_WITNESS_PAIRS,
    "required_core_centers": REQUIRED_CORE_CENTERS,
    "source_label8_free_distinct_exact_signature_count": 10,
    "source_label8_free_occurrence_count": 12,
    "source_support_need_record_count": 6,
    "source_unique_centered_support_requirement_count": 7,
    "source_support_ledger_status": SOURCE_SUPPORT_LEDGER_STATUS,
    "cascade_signature_indices": [7, 8, 9],
    "cascade_signature_count": 3,
    "cascade_occurrence_count": 4,
    "cascade_full_core_status_counts": {"strict_cycle": 3},
    "cascade_full_core_occurrence_status_counts": {"strict_cycle": 4},
    "cascade_full_core_cycle_length_signature_counts": {"2": 1, "3": 2},
    "cascade_full_core_cycle_length_occurrence_counts": {"2": 1, "3": 3},
    "cascade_full_core_strict_edge_count_signature_counts": {"27": 3},
    "proper_truncation_record_count": 18,
    "proper_truncation_occurrence_count": 24,
    "proper_truncation_status_counts": {"ok": 18},
    "proper_truncation_occurrence_status_counts": {"ok": 24},
    "row_subset_status_counts_by_size": {
        "1": {"ok": 9},
        "2": {"ok": 9},
        "3": {"strict_cycle": 3},
    },
    "row_subset_occurrence_status_counts_by_size": {
        "1": {"ok": 12},
        "2": {"ok": 12},
        "3": {"strict_cycle": 4},
    },
    "clean_deletion_signature_counts_by_deleted_center": {
        "5": 3,
        "6": 3,
        "8": 3,
    },
    "clean_deletion_occurrence_counts_by_deleted_center": {
        "5": 4,
        "6": 4,
        "8": 4,
    },
    "full_core_cycle_edge_row_pair_signature_counts": {"5,8": 3},
    "full_core_cycle_edge_row_pair_occurrence_counts": {"5,8": 4},
    "criticality_status": CRITICALITY_STATUS,
}


def build_cascade_row_criticality_payload(
    residual_targets: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    *,
    residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> dict[str, Any]:
    """Return the deterministic cascade row-criticality payload."""

    errors: list[str] = []
    assert_expected_label8_free_residual_targets(residual_targets)
    assert_expected_support_hypothesis_ledger(support_ledger)
    _validate_sources(residual_targets, support_ledger, errors)
    records, summary = _cascade_records(residual_targets, support_ledger)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "cascade_signature_records": records,
        "source_artifacts": [
            _source_summary(
                residual_targets_path,
                "source 151:6 label-8-free residual targets",
                residual_targets,
            ),
            _source_summary(
                support_ledger_path,
                "source 151:6 label-4 support-hypothesis ledger",
                support_ledger,
            ),
        ],
        "interpretation": [
            (
                "The row-6 cascade signatures are exactly the label-8-free "
                "residual signatures with auxiliary center pair 5,8."
            ),
            (
                "All three rows 5,6,8 are needed for the recorded "
                "vertex-circle strict cycles: deleting any one of them leaves "
                "a quotient-clean two-row truncation."
            ),
            (
                "Rows 5 and 6 supply the cascade equalities named by the "
                "support ledger, while row 8 supplies the additional strict "
                "endpoint row used by the residual cycle."
            ),
            (
                "This packet is a row-criticality target, not support "
                "existence, row forcing, endpoint-8 forcing, or a proof that "
                "[3,5] is impossible."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_cascade_row_criticality(payload)
    return payload


def assert_expected_cascade_row_criticality(payload: Mapping[str, Any]) -> None:
    """Assert the pinned cascade row-criticality packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    residual_targets_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGETS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> list[str]:
    """Return validation errors for a cascade row-criticality payload."""

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
        return errors

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            errors.append(
                f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}"
            )

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        for phrase in (
            "Every nonempty proper row truncation is quotient-clean",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove pair [3,5] impossible",
            "does not prove endpoint-8 forcing",
            "does not prove n=9",
            "does not prove the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    records = payload.get("cascade_signature_records")
    if not isinstance(records, list):
        errors.append("cascade_signature_records must be a list")
    else:
        _validate_cascade_records(records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("row 8 supplies the additional strict" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the row-8 strict-row target")

    if recompute and not errors:
        generated = build_cascade_row_criticality_payload(
            load_artifact(residual_targets_path),
            load_artifact(support_ledger_path),
            residual_targets_path=residual_targets_path,
            support_ledger_path=support_ledger_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source artifacts")
    return errors


def summary_payload(
    path: Path,
    payload: Mapping[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a compact CLI summary."""

    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "artifact": display_path(path, ROOT),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "cascade_signature_count": summary.get("cascade_signature_count"),
        "cascade_occurrence_count": summary.get("cascade_occurrence_count"),
        "required_core_centers": summary.get("required_core_centers"),
        "proper_truncation_status_counts": summary.get(
            "proper_truncation_status_counts"
        ),
        "criticality_status": summary.get("criticality_status"),
        "validation_errors": list(errors),
    }


def _cascade_records(
    residual_targets: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    support_summary = _mapping_or_empty(support_ledger.get("summary"))
    cascade_indices = _cascade_signature_indices(support_ledger)
    records: list[dict[str, Any]] = []
    full_status_counts: Counter[str] = Counter()
    full_occurrence_status_counts: Counter[str] = Counter()
    cycle_length_counts: Counter[int] = Counter()
    cycle_length_occurrence_counts: Counter[int] = Counter()
    strict_edge_count_counts: Counter[int] = Counter()
    proper_status_counts: Counter[str] = Counter()
    proper_occurrence_status_counts: Counter[str] = Counter()
    subset_status_by_size: dict[int, Counter[str]] = {}
    subset_occurrence_status_by_size: dict[int, Counter[str]] = {}
    deletion_counts: Counter[int] = Counter()
    deletion_occurrence_counts: Counter[int] = Counter()
    cycle_row_pair_counts: Counter[str] = Counter()
    cycle_row_pair_occurrence_counts: Counter[str] = Counter()
    total_proper_records = 0
    total_proper_occurrences = 0

    for record in residual_targets["residual_signature_records"]:
        if str(record["auxiliary_center_pair"]) != CASCADE_AUXILIARY_CENTER_PAIR:
            continue
        signature_index = int(record["signature_index"])
        if signature_index not in cascade_indices:
            continue
        rows = _rows_by_center(record)
        centers = tuple(REQUIRED_CORE_CENTERS)
        full = _replay(rows, centers)
        full_json = result_to_json(full)
        multiplicity = int(record["multiplicity"])
        full_status_counts[full.status] += 1
        full_occurrence_status_counts[full.status] += multiplicity
        cycle_length = len(full.cycle_edges)
        cycle_length_counts[cycle_length] += 1
        cycle_length_occurrence_counts[cycle_length] += multiplicity
        strict_edge_count_counts[full.strict_edge_count] += 1
        subset_status_by_size.setdefault(len(centers), Counter())[full.status] += 1
        subset_occurrence_status_by_size.setdefault(len(centers), Counter())[
            full.status
        ] += multiplicity
        cycle_row_pair = ",".join(str(row) for row in _cycle_edge_rows(full_json))
        cycle_row_pair_counts[cycle_row_pair] += 1
        cycle_row_pair_occurrence_counts[cycle_row_pair] += multiplicity

        truncations: list[dict[str, Any]] = []
        for subset in PROPER_TRUNCATION_CENTERS:
            subset_tuple = tuple(subset)
            replay = _replay(rows, subset_tuple)
            deleted = sorted(set(REQUIRED_CORE_CENTERS) - set(subset))
            truncation = {
                "centers": list(subset_tuple),
                "deleted_centers": deleted,
                "status": replay.status,
                "strict_edge_count": replay.strict_edge_count,
                "self_edge_count": len(replay.self_edge_conflicts),
                "cycle_edge_count": len(replay.cycle_edges),
                "obstructed": replay.obstructed,
            }
            truncations.append(truncation)
            proper_status_counts[replay.status] += 1
            proper_occurrence_status_counts[replay.status] += multiplicity
            subset_status_by_size.setdefault(len(subset_tuple), Counter())[
                replay.status
            ] += 1
            subset_occurrence_status_by_size.setdefault(len(subset_tuple), Counter())[
                replay.status
            ] += multiplicity
            total_proper_records += 1
            total_proper_occurrences += multiplicity
            if len(subset_tuple) == 2 and replay.status == "ok":
                deleted_center = deleted[0]
                deletion_counts[deleted_center] += 1
                deletion_occurrence_counts[deleted_center] += multiplicity

        records.append(
            {
                "signature_index": signature_index,
                "multiplicity": multiplicity,
                "auxiliary_center_pair": record["auxiliary_center_pair"],
                "rows": record["rows"],
                "target_row_intersections": record["target_row_intersections"],
                "full_core_centers": list(centers),
                "full_core_status": full.status,
                "full_core_strict_edge_count": full.strict_edge_count,
                "full_core_cycle_edge_count": cycle_length,
                "full_core_cycle_edge_rows": _cycle_edge_rows(full_json),
                "full_core_cycle_edges": full_json["cycle_edges"],
                "proper_truncation_records": truncations,
                "all_proper_truncations_clean": all(
                    truncation["status"] == "ok" for truncation in truncations
                ),
                "next_proof_obligation": (
                    "Force the full local row package {5,6,8}: rows 5 and 6 "
                    "supply the cascade equalities, while row 8 supplies the "
                    "additional strict endpoint row."
                ),
            }
        )

    records = sorted(records, key=lambda item: int(item["signature_index"]))
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "cascade_component_key": CASCADE_COMPONENT_KEY,
        "cascade_auxiliary_center_pair": CASCADE_AUXILIARY_CENTER_PAIR,
        "cascade_required_support_centers": support_summary.get(
            "cascade_required_support_centers"
        ),
        "cascade_required_witness_pairs": support_summary.get(
            "cascade_required_witness_pairs"
        ),
        "required_core_centers": REQUIRED_CORE_CENTERS,
        "source_label8_free_distinct_exact_signature_count": residual_targets[
            "summary"
        ]["label8_free_distinct_exact_signature_count"],
        "source_label8_free_occurrence_count": residual_targets["summary"][
            "label8_free_occurrence_count"
        ],
        "source_support_need_record_count": support_summary.get(
            "support_need_record_count"
        ),
        "source_unique_centered_support_requirement_count": support_summary.get(
            "unique_centered_support_requirement_count"
        ),
        "source_support_ledger_status": support_summary.get("ledger_status"),
        "cascade_signature_indices": [int(item) for item in sorted(cascade_indices)],
        "cascade_signature_count": len(records),
        "cascade_occurrence_count": sum(int(record["multiplicity"]) for record in records),
        "cascade_full_core_status_counts": _json_counter(full_status_counts),
        "cascade_full_core_occurrence_status_counts": _json_counter(
            full_occurrence_status_counts
        ),
        "cascade_full_core_cycle_length_signature_counts": _json_counter(
            cycle_length_counts
        ),
        "cascade_full_core_cycle_length_occurrence_counts": _json_counter(
            cycle_length_occurrence_counts
        ),
        "cascade_full_core_strict_edge_count_signature_counts": _json_counter(
            strict_edge_count_counts
        ),
        "proper_truncation_record_count": total_proper_records,
        "proper_truncation_occurrence_count": total_proper_occurrences,
        "proper_truncation_status_counts": _json_counter(proper_status_counts),
        "proper_truncation_occurrence_status_counts": _json_counter(
            proper_occurrence_status_counts
        ),
        "row_subset_status_counts_by_size": _nested_counter(subset_status_by_size),
        "row_subset_occurrence_status_counts_by_size": _nested_counter(
            subset_occurrence_status_by_size
        ),
        "clean_deletion_signature_counts_by_deleted_center": _json_counter(
            deletion_counts
        ),
        "clean_deletion_occurrence_counts_by_deleted_center": _json_counter(
            deletion_occurrence_counts
        ),
        "full_core_cycle_edge_row_pair_signature_counts": _json_counter(
            cycle_row_pair_counts
        ),
        "full_core_cycle_edge_row_pair_occurrence_counts": _json_counter(
            cycle_row_pair_occurrence_counts
        ),
        "criticality_status": CRITICALITY_STATUS,
    }
    return records, summary


def _cascade_signature_indices(support_ledger: Mapping[str, Any]) -> set[int]:
    for record in support_ledger["support_need_records"]:
        if record["component_key"] == CASCADE_COMPONENT_KEY:
            return {int(index) for index in record["signature_indices"]}
    raise AssertionError("cascade component missing from support ledger")


def _rows_by_center(record: Mapping[str, Any]) -> dict[int, tuple[int, ...]]:
    rows: dict[int, tuple[int, ...]] = {}
    for row in record["rows"]:
        center = int(row["center"])
        witnesses = tuple(int(item) for item in row["witnesses"])
        rows[center] = witnesses
    if sorted(rows) != REQUIRED_CORE_CENTERS:
        raise AssertionError(f"unexpected cascade core centers: {sorted(rows)!r}")
    if list(rows[TARGET_CENTER]) != PRIVATE_TARGET_CLASS:
        raise AssertionError("cascade target row does not match private target class")
    return rows


def _replay(
    rows: Mapping[int, tuple[int, ...]],
    centers: Sequence[int],
) -> Any:
    return replay_vertex_circle_quotient(
        N,
        CYCLIC_ORDER,
        [SelectedRow(center=center, witnesses=rows[center]) for center in centers],
    )


def _cycle_edge_rows(result_json: Mapping[str, Any]) -> list[int]:
    rows = {int(edge["row"]) for edge in result_json["cycle_edges"]}
    return sorted(rows)


def _nested_counter(counters: Mapping[int, Counter[str]]) -> dict[str, dict[str, int]]:
    return {
        str(key): _json_counter(counter)
        for key, counter in sorted(counters.items(), key=lambda item: item[0])
    }


def _validate_sources(
    residual_targets: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected_sources = (
        (
            "residual targets source",
            residual_targets,
            SOURCE_RESIDUAL_SCHEMA,
            SOURCE_RESIDUAL_STATUS,
        ),
        (
            "support ledger source",
            support_ledger,
            SOURCE_SUPPORT_LEDGER_SCHEMA,
            SOURCE_SUPPORT_LEDGER_STATUS_TEXT,
        ),
    )
    for name, payload, schema, status in expected_sources:
        if payload.get("schema") != schema:
            errors.append(f"{name} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{name} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{name} trust mismatch")
    residual_summary = _mapping(residual_targets.get("summary"), "residual summary", errors)
    support_summary = _mapping(support_ledger.get("summary"), "support summary", errors)
    expected_fields = {
        "residual target status": (
            residual_summary.get("target_status"),
            SOURCE_RESIDUAL_TARGET_STATUS,
        ),
        "support ledger status": (
            support_summary.get("ledger_status"),
            SOURCE_SUPPORT_LEDGER_STATUS,
        ),
        "support cascade component": (
            support_summary.get("cascade_component_key"),
            CASCADE_COMPONENT_KEY,
        ),
        "support cascade centers": (
            support_summary.get("cascade_required_support_centers"),
            CASCADE_SUPPORT_CENTERS,
        ),
        "support cascade witness pairs": (
            support_summary.get("cascade_required_witness_pairs"),
            CASCADE_SUPPORT_WITNESS_PAIRS,
        ),
    }
    for name, (actual, expected) in expected_fields.items():
        if actual != expected:
            errors.append(f"{name} mismatch: expected {expected!r}, got {actual!r}")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_cascade_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["cascade_signature_count"]:
        errors.append("cascade_signature_records length mismatch")
    seen: set[int] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"cascade_signature_records[{index}] must be an object")
            continue
        signature_index = record.get("signature_index")
        if not isinstance(signature_index, int):
            errors.append(f"cascade_signature_records[{index}] signature missing")
            continue
        if signature_index in seen:
            errors.append(f"cascade_signature_records[{index}] duplicate signature")
        seen.add(signature_index)
        if record.get("auxiliary_center_pair") != CASCADE_AUXILIARY_CENTER_PAIR:
            errors.append(f"cascade_signature_records[{index}] wrong auxiliary pair")
        if record.get("full_core_centers") != REQUIRED_CORE_CENTERS:
            errors.append(f"cascade_signature_records[{index}] full centers mismatch")
        if record.get("full_core_status") != "strict_cycle":
            errors.append(f"cascade_signature_records[{index}] full core not strict")
        if record.get("all_proper_truncations_clean") is not True:
            errors.append(f"cascade_signature_records[{index}] truncation not clean")
        if record.get("full_core_cycle_edge_rows") != [5, 8]:
            errors.append(f"cascade_signature_records[{index}] cycle rows mismatch")
        truncations = record.get("proper_truncation_records")
        if not isinstance(truncations, list):
            errors.append(f"cascade_signature_records[{index}] truncations missing")
            continue
        if [item.get("centers") for item in truncations] != PROPER_TRUNCATION_CENTERS:
            errors.append(f"cascade_signature_records[{index}] truncation order drift")
        for truncation in truncations:
            if not isinstance(truncation, Mapping):
                errors.append(f"cascade_signature_records[{index}] bad truncation")
                continue
            if truncation.get("status") != "ok":
                errors.append(f"cascade_signature_records[{index}] truncation obstructs")
            if truncation.get("obstructed") is not False:
                errors.append(f"cascade_signature_records[{index}] truncation flag drift")
    if seen != set(EXPECTED_SUMMARY["cascade_signature_indices"]):
        errors.append(
            "cascade signature set mismatch: "
            f"expected {EXPECTED_SUMMARY['cascade_signature_indices']!r}, "
            f"got {sorted(seen)!r}"
        )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "target_status": summary.get("target_status"),
        "ledger_status": summary.get("ledger_status"),
    }


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _mapping_or_empty(value: object) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-residual-targets",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGETS,
    )
    parser.add_argument(
        "--source-support-ledger",
        type=Path,
        default=DEFAULT_SOURCE_SUPPORT_LEDGER,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    residual_targets = _resolve(args.source_residual_targets)
    support_ledger = _resolve(args.source_support_ledger)

    generated = build_cascade_row_criticality_payload(
        load_artifact(residual_targets),
        load_artifact(support_ledger),
        residual_targets_path=residual_targets,
        support_ledger_path=support_ledger,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        residual_targets_path=residual_targets,
        support_ledger_path=support_ledger,
    )
    if args.assert_expected:
        assert_expected_cascade_row_criticality(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 cascade row-criticality")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade signatures: {summary['cascade_signature_count']}")
        print(f"cascade occurrences: {summary['cascade_occurrence_count']}")
        print(f"required centers: {summary['required_core_centers']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: cascade row-criticality packet verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
