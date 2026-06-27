#!/usr/bin/env python3
"""Check support alignment for off-center center-8 migration targets."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_residual_target_rows import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS as SOURCE_RESIDUAL_GATE_STATUS,
    RESIDUAL_STATUS as SOURCE_RESIDUAL_STATUS,
    SCHEMA as SOURCE_RESIDUAL_SCHEMA,
    STATUS as SOURCE_RESIDUAL_STATUS_TEXT,
    assert_expected_center8_residual_target_rows,
)
from scripts.check_bootstrap_t12_151_6_label4_support_hypothesis_ledger import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SUPPORT_LEDGER,
    LEDGER_STATUS as SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY,
    SCHEMA as SOURCE_SUPPORT_LEDGER_SCHEMA,
    STATUS as SOURCE_SUPPORT_LEDGER_STATUS,
    assert_expected_support_hypothesis_ledger,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_MIGRATION_SUPPORT_CROSSWALK_DIAGNOSTIC_ONLY"
)
MIGRATION_STATUS = "NOT_READY_SUPPORT_BACKING_DOES_NOT_MIGRATE_OFF_CENTER_ROWS"
CLAIM_SCOPE = (
    "Proof-mining center-migration support crosswalk for the source-151 row-6 "
    "label-4 residual split. It joins the residual off-center [0,4,6] "
    "target rows to the centered support-hypothesis ledger and records that "
    "three of five off-center rows have some same-center support backing, "
    "including exactly one row using the row-5 [4,6] cascade support, while "
    "no current support requirement is centered at 8 and no same-center "
    "support backing supplies center-8 migration. This does not prove center "
    "migration, does not prove support existence, does not prove row forcing, "
    "does not prove endpoint-8 forcing, does not prove assignments 0 and 11 "
    "impossible, does not prove that pair [3,5] is impossible, does not "
    "prove n=9, does not prove the bootstrap bridge, is not a counterexample, "
    "and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.json"
)

CASCADE_ROW5_REQUIREMENT_KEY = "row5:[4,5]=[5,6]"
CASCADE_ROW6_REQUIREMENT_KEY = "row6:[5,6]=[0,6]"
ENDPOINT_PAIRS = [[0, 4], [0, 6], [4, 6]]

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "interpretation",
    "off_center_alignment_records",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "target_sparse_gap_records",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "source_residual_gate_status": SOURCE_RESIDUAL_GATE_STATUS,
    "source_residual_status": SOURCE_RESIDUAL_STATUS,
    "source_support_ledger_status": SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY,
    "residual_assignment_count": 6,
    "residual_assignment_indices": [0, 5, 7, 9, 10, 11],
    "off_center_target_row_occurrence_count": 5,
    "off_center_target_assignment_indices": [5, 7, 9, 10],
    "target_sparse_assignment_indices": [0, 11],
    "support_requirement_centers": [5, 6, 7],
    "support_requirement_center8_count": 0,
    "off_center_row_centers": [2, 5, 7],
    "off_center_rows_at_unsupported_center_count": 2,
    "off_center_assignments_at_unsupported_center_indices": [9],
    "off_center_rows_with_same_center_support_count": 3,
    "off_center_assignments_with_same_center_support_indices": [5, 7, 10],
    "same_center_support_requirement_match_count": 5,
    "same_center_support_match_count_by_row_center": {"5": 3, "7": 2},
    "same_center_support_endpoint_triple_pair_count": 2,
    "same_center_support_endpoint_triple_pairs": [[0, 4], [4, 6]],
    "endpoint_triple_pairs_missing_from_same_center_support": [[0, 6]],
    "off_center_rows_with_cascade_row5_support_count": 1,
    "cascade_row5_support_assignment_indices": [5],
    "off_center_rows_with_row6_cascade_support_count": 0,
    "cascade_row6_support_assignment_indices": [],
    "support_backing_supplies_center8_target": False,
    "current_evidence_proves_center_migration": False,
    "current_evidence_obstructs_target_sparse_assignments": False,
    "migration_status": MIGRATION_STATUS,
}


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a JSON artifact."""

    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{display_path(path, ROOT)} must contain a JSON object")
    return payload


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_center8_migration_support_crosswalk_payload(
    residual_target_rows: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    *,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> dict[str, Any]:
    """Return the deterministic center-8 migration support crosswalk."""

    errors: list[str] = []
    assert_expected_center8_residual_target_rows(residual_target_rows)
    assert_expected_support_hypothesis_ledger(support_ledger)
    _validate_sources(residual_target_rows, support_ledger, errors)
    summary, off_center_records, target_sparse_records = _alignment_records(
        residual_target_rows,
        support_ledger,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Does the current support ledger turn the off-center "
                "[0,4,6] residual rows into center-8 target supply?"
            ),
            "answer": "no_same_center_support_backing_is_not_center8_migration",
            "migration_status": MIGRATION_STATUS,
            "support_backing_supplies_center8_target": False,
            "current_evidence_proves_center_migration": False,
            "current_evidence_obstructs_target_sparse_assignments": False,
            "blocking_reason": (
                "The matched support requirements are centered at 5 or 7, "
                "and two off-center target rows are centered at 2 with no "
                "same-center support requirement. The support ledger still "
                "has no center-8 requirement."
            ),
            "required_next_lemma": (
                "Prove a genuine center-migration theorem from same-center "
                "support-backed off-center rows to a center-8 rich class, "
                "or separately obstruct target-sparse assignments 0 and 11."
            ),
        },
        "off_center_alignment_records": off_center_records,
        "target_sparse_gap_records": target_sparse_records,
        "source_artifacts": [
            _source_summary(
                residual_target_rows_path,
                "source 151:6 center-8 residual target rows",
                residual_target_rows,
            ),
            _source_summary(
                support_ledger_path,
                "source 151:6 label-4 support-hypothesis ledger",
                support_ledger,
            ),
        ],
        "interpretation": [
            (
                "The support ledger backs three of the five off-center "
                "target rows at their own centers, but never at center 8."
            ),
            (
                "Only assignment 5 has an off-center target row containing "
                "the row-5 [4,6] cascade support; the row-6 [0,5] cascade "
                "support is not an off-center target row."
            ),
            (
                "Assignment 9 supplies the target triple only at unsupported "
                "center 2, while assignments 0 and 11 remain target-sparse."
            ),
            (
                "This packet narrows the migration lemma target; it does not "
                "prove the migration lemma or any obstruction."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_migration_support_crosswalk(payload)
    return payload


def assert_expected_center8_migration_support_crosswalk(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned center-8 migration support crosswalk."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> list[str]:
    """Return validation errors for a center-8 migration support crosswalk."""

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
            "does not prove center migration",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove endpoint-8 forcing",
            "does not prove assignments 0 and 11 impossible",
            "does not prove that pair [3,5] is impossible",
            "does not prove n=9",
            "does not prove the bootstrap bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    decision = _mapping(payload.get("decision"), "decision", errors)
    _validate_decision(decision, errors)

    off_center_records = payload.get("off_center_alignment_records")
    if not isinstance(off_center_records, list):
        errors.append("off_center_alignment_records must be a list")
    else:
        _validate_off_center_records(off_center_records, errors)
    target_sparse_records = payload.get("target_sparse_gap_records")
    if not isinstance(target_sparse_records, list):
        errors.append("target_sparse_gap_records must be a list")
    else:
        _validate_target_sparse_records(target_sparse_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove the migration lemma" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the migration nonclaim")

    if recompute and not errors:
        generated = build_center8_migration_support_crosswalk_payload(
            load_artifact(residual_target_rows_path),
            load_artifact(support_ledger_path),
            residual_target_rows_path=residual_target_rows_path,
            support_ledger_path=support_ledger_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packets")
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
        "conditional_center8_triple": summary.get("conditional_center8_triple"),
        "off_center_target_row_occurrence_count": summary.get(
            "off_center_target_row_occurrence_count"
        ),
        "off_center_rows_with_same_center_support_count": summary.get(
            "off_center_rows_with_same_center_support_count"
        ),
        "off_center_rows_with_cascade_row5_support_count": summary.get(
            "off_center_rows_with_cascade_row5_support_count"
        ),
        "support_requirement_center8_count": summary.get(
            "support_requirement_center8_count"
        ),
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "migration_status": summary.get("migration_status"),
        "validation_errors": list(errors),
    }


def _alignment_records(
    residual_target_rows: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    residual_summary = _required_mapping(
        residual_target_rows.get("summary"), "residual target-row summary"
    )
    support_summary = _required_mapping(
        support_ledger.get("summary"), "support ledger summary"
    )
    requirements = _support_requirements_by_center(support_ledger)
    center8_requirements = requirements.get(ENDPOINT_CENTER, [])

    off_center_records: list[dict[str, Any]] = []
    same_center_match_count_by_center: Counter[str] = Counter()
    endpoint_pair_matches: set[tuple[int, int]] = set()
    same_center_support_assignments: set[int] = set()
    unsupported_assignments: set[int] = set()
    cascade_row5_assignments: set[int] = set()
    cascade_row6_assignments: set[int] = set()

    for raw_record in _required_list(
        residual_target_rows.get("off_center_target_row_records"),
        "off-center target-row records",
    ):
        record = _required_mapping(raw_record, "off-center target-row record")
        assignment_index = int(record["assignment_index"])
        row_center = int(record["row_center"])
        row_witnesses = _int_list(record["row_witnesses"])
        row_set = set(row_witnesses)
        same_center_matches = [
            requirement
            for requirement in requirements.get(row_center, [])
            if set(_int_list(requirement["witness_pair"])) <= row_set
        ]
        endpoint_matches = [
            _int_list(requirement["witness_pair"])
            for requirement in same_center_matches
            if sorted(_int_list(requirement["witness_pair"])) in ENDPOINT_PAIRS
        ]
        has_cascade_row5 = any(
            requirement["requirement_key"] == CASCADE_ROW5_REQUIREMENT_KEY
            for requirement in same_center_matches
        )
        has_cascade_row6 = any(
            requirement["requirement_key"] == CASCADE_ROW6_REQUIREMENT_KEY
            for requirement in same_center_matches
        )
        if same_center_matches:
            same_center_support_assignments.add(assignment_index)
        else:
            unsupported_assignments.add(assignment_index)
        if has_cascade_row5:
            cascade_row5_assignments.add(assignment_index)
        if has_cascade_row6:
            cascade_row6_assignments.add(assignment_index)
        if same_center_matches:
            same_center_match_count_by_center[str(row_center)] += len(
                same_center_matches
            )
        endpoint_pair_matches.update(tuple(pair) for pair in endpoint_matches)
        off_center_records.append(
            {
                "assignment_index": assignment_index,
                "core_index": int(record["core_index"]),
                "row_center": row_center,
                "row_witnesses": row_witnesses,
                "auxiliary_center_pair": str(record["auxiliary_center_pair"]),
                "label8_visible": bool(record["label8_visible"]),
                "row_center_equals_endpoint_center": row_center == ENDPOINT_CENTER,
                "same_center_support_requirement_count": len(same_center_matches),
                "same_center_support_requirement_keys": [
                    str(requirement["requirement_key"])
                    for requirement in same_center_matches
                ],
                "same_center_support_witness_pairs": [
                    _int_list(requirement["witness_pair"])
                    for requirement in same_center_matches
                ],
                "same_center_endpoint_triple_pair_supports": endpoint_matches,
                "has_same_center_support": bool(same_center_matches),
                "has_cascade_row5_support": has_cascade_row5,
                "has_row6_cascade_support": has_cascade_row6,
                "same_center_support_supplies_center8_target": False,
                "migration_obligation": (
                    "A same-center support-backed off-center row still "
                    "requires a genuine theorem moving support to center 8."
                    if same_center_matches
                    else "No current support requirement is centered at this row center."
                ),
            }
        )

    target_sparse_records = [
        {
            "assignment_index": int(record["assignment_index"]),
            "target_pair_row_count": int(record["target_pair_row_count"]),
            "target_pair_overlaps": _unique_pairs(
                pair_row["target_overlap"] for pair_row in record["target_pair_rows"]
            ),
            "max_target_overlap": int(record["max_target_overlap"]),
            "same_center_support_alignment_available": False,
            "requires_separate_obstruction": True,
        }
        for record in _required_list(
            residual_target_rows.get("target_sparse_assignment_records"),
            "target-sparse records",
        )
        if isinstance(record, Mapping)
    ]
    off_center_records = sorted(
        off_center_records,
        key=lambda record: (
            int(record["assignment_index"]),
            int(record["core_index"]),
            int(record["row_center"]),
        ),
    )
    target_sparse_records = sorted(
        target_sparse_records, key=lambda record: int(record["assignment_index"])
    )
    same_center_endpoint_pairs = [list(pair) for pair in sorted(endpoint_pair_matches)]
    missing_endpoint_pairs = [
        pair for pair in ENDPOINT_PAIRS if pair not in same_center_endpoint_pairs
    ]
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": ENDPOINT_CENTER,
        "conditional_center8_triple": ENDPOINT_TRIPLE,
        "source_residual_gate_status": residual_summary["gate_status"],
        "source_residual_status": residual_summary["residual_status"],
        "source_support_ledger_status": support_summary["ledger_status"],
        "residual_assignment_count": int(
            residual_summary["residual_assignment_count"]
        ),
        "residual_assignment_indices": list(
            residual_summary["residual_assignment_indices"]
        ),
        "off_center_target_row_occurrence_count": len(off_center_records),
        "off_center_target_assignment_indices": sorted(
            {
                int(record["assignment_index"])
                for record in off_center_records
            }
        ),
        "target_sparse_assignment_indices": [
            int(record["assignment_index"]) for record in target_sparse_records
        ],
        "support_requirement_centers": sorted(int(center) for center in requirements),
        "support_requirement_center8_count": len(center8_requirements),
        "off_center_row_centers": sorted(
            {int(record["row_center"]) for record in off_center_records}
        ),
        "off_center_rows_at_unsupported_center_count": sum(
            1
            for record in off_center_records
            if not record["has_same_center_support"]
        ),
        "off_center_assignments_at_unsupported_center_indices": sorted(
            unsupported_assignments
        ),
        "off_center_rows_with_same_center_support_count": sum(
            1
            for record in off_center_records
            if record["has_same_center_support"]
        ),
        "off_center_assignments_with_same_center_support_indices": sorted(
            same_center_support_assignments
        ),
        "same_center_support_requirement_match_count": sum(
            int(record["same_center_support_requirement_count"])
            for record in off_center_records
        ),
        "same_center_support_match_count_by_row_center": _json_counter(
            same_center_match_count_by_center
        ),
        "same_center_support_endpoint_triple_pair_count": len(
            same_center_endpoint_pairs
        ),
        "same_center_support_endpoint_triple_pairs": same_center_endpoint_pairs,
        "endpoint_triple_pairs_missing_from_same_center_support": missing_endpoint_pairs,
        "off_center_rows_with_cascade_row5_support_count": sum(
            1 for record in off_center_records if record["has_cascade_row5_support"]
        ),
        "cascade_row5_support_assignment_indices": sorted(cascade_row5_assignments),
        "off_center_rows_with_row6_cascade_support_count": sum(
            1 for record in off_center_records if record["has_row6_cascade_support"]
        ),
        "cascade_row6_support_assignment_indices": sorted(cascade_row6_assignments),
        "support_backing_supplies_center8_target": False,
        "current_evidence_proves_center_migration": False,
        "current_evidence_obstructs_target_sparse_assignments": False,
        "migration_status": MIGRATION_STATUS,
    }
    return summary, off_center_records, target_sparse_records


def _validate_sources(
    residual_target_rows: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = (
        (
            "residual target rows",
            residual_target_rows,
            SOURCE_RESIDUAL_SCHEMA,
            SOURCE_RESIDUAL_STATUS_TEXT,
        ),
        (
            "support ledger",
            support_ledger,
            SOURCE_SUPPORT_LEDGER_SCHEMA,
            SOURCE_SUPPORT_LEDGER_STATUS,
        ),
    )
    for label, payload, schema, status in expected:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")
    residual_summary = _mapping(
        residual_target_rows.get("summary"), "residual target-row summary", errors
    )
    if residual_summary.get("gate_status") != SOURCE_RESIDUAL_GATE_STATUS:
        errors.append("residual target-row gate status mismatch")
    support_summary = _mapping(
        support_ledger.get("summary"), "support ledger summary", errors
    )
    if support_summary.get("ledger_status") != SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY:
        errors.append("support ledger status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_same_center_support_backing_is_not_center8_migration",
        "migration_status": MIGRATION_STATUS,
        "support_backing_supplies_center8_target": False,
        "current_evidence_proves_center_migration": False,
        "current_evidence_obstructs_target_sparse_assignments": False,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "center-migration theorem" not in required_next:
        errors.append("decision.required_next_lemma must name center migration")


def _validate_off_center_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["off_center_target_row_occurrence_count"]:
        errors.append("off_center_alignment_records length mismatch")
        return
    same_center_count = 0
    cascade_row5_count = 0
    cascade_row6_count = 0
    unsupported_indices: set[int] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"off_center_alignment_records[{index}] must be an object")
            continue
        if record.get("row_center_equals_endpoint_center") is not False:
            errors.append("off-center records must not be centered at 8")
        if record.get("same_center_support_supplies_center8_target") is not False:
            errors.append("same-center support must not be promoted to center-8 supply")
        if record.get("has_same_center_support"):
            same_center_count += 1
        else:
            unsupported_indices.add(int(record.get("assignment_index", -1)))
        if record.get("has_cascade_row5_support"):
            cascade_row5_count += 1
        if record.get("has_row6_cascade_support"):
            cascade_row6_count += 1
    if same_center_count != EXPECTED_SUMMARY["off_center_rows_with_same_center_support_count"]:
        errors.append("same-center support-backed off-center row count mismatch")
    if cascade_row5_count != EXPECTED_SUMMARY["off_center_rows_with_cascade_row5_support_count"]:
        errors.append("cascade row-5 off-center support count mismatch")
    if cascade_row6_count != 0:
        errors.append("row-6 cascade support should not be an off-center target row")
    if sorted(unsupported_indices) != [9]:
        errors.append("unsupported off-center assignment indices mismatch")


def _validate_target_sparse_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    indices: list[int] = []
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("target_sparse_gap_records entries must be objects")
            continue
        indices.append(int(record.get("assignment_index", -1)))
        if record.get("same_center_support_alignment_available") is not False:
            errors.append("target-sparse rows must not claim support alignment")
        if record.get("requires_separate_obstruction") is not True:
            errors.append("target-sparse rows must preserve separate-obstruction flag")
    if indices != [0, 11]:
        errors.append(f"target-sparse assignment indices mismatch: {indices!r}")


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
        "gate_status": summary.get("gate_status"),
        "residual_status": summary.get("residual_status"),
        "ledger_status": summary.get("ledger_status"),
    }


def _support_requirements_by_center(
    support_ledger: Mapping[str, Any],
) -> dict[int, list[Mapping[str, Any]]]:
    raw_records = support_ledger.get("support_requirement_records")
    if not isinstance(raw_records, list):
        raise AssertionError("support_requirement_records must be a list")
    result: dict[int, list[Mapping[str, Any]]] = {}
    for record in raw_records:
        requirement = _required_mapping(record, "support requirement")
        center = int(requirement["center"])
        result.setdefault(center, []).append(requirement)
    for records in result.values():
        records.sort(key=lambda item: str(item["requirement_key"]))
    return result


def _unique_pairs(pairs: Sequence[object]) -> list[list[int]]:
    unique = {tuple(sorted(int(item) for item in pair)) for pair in pairs}
    return [list(pair) for pair in sorted(unique)]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _int_list(values: object) -> list[int]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise AssertionError("expected a sequence of integers")
    return [int(value) for value in values]


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _required_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"{name} must be an object")
    return value


def _required_list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError(f"{name} must be a list")
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-residual-target-rows",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
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
    source_residual_target_rows = _resolve(args.source_residual_target_rows)
    source_support_ledger = _resolve(args.source_support_ledger)
    generated = build_center8_migration_support_crosswalk_payload(
        load_artifact(source_residual_target_rows),
        load_artifact(source_support_ledger),
        residual_target_rows_path=source_residual_target_rows,
        support_ledger_path=source_support_ledger,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        residual_target_rows_path=source_residual_target_rows,
        support_ledger_path=source_support_ledger,
    )
    if args.assert_expected:
        assert_expected_center8_migration_support_crosswalk(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 migration support crosswalk")
        print(f"target row: {summary['target_row_key']}")
        print(f"center-8 target: {summary['conditional_center8_triple']}")
        print(
            "off-center target rows: "
            f"{summary['off_center_target_row_occurrence_count']}"
        )
        print(
            "same-center support-backed rows: "
            f"{summary['off_center_rows_with_same_center_support_count']}"
        )
        print(
            "center-8 support requirements: "
            f"{summary['support_requirement_center8_count']}"
        )
        print(f"migration status: {summary['migration_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 migration support crosswalk verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
