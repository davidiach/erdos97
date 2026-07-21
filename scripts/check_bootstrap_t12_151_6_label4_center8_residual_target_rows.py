#!/usr/bin/env python3
"""Check residual target rows after the source-151 center-8 core route."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    EXACT_FOUR_ENDPOINT_ROWS,
    TARGET_STATUS as SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_core_route import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CENTER8_CORE_ROUTE,
    GATE_STATUS as SOURCE_CENTER8_CORE_ROUTE_GATE_STATUS,
    SCHEMA as SOURCE_CENTER8_CORE_ROUTE_SCHEMA,
    STATUS as SOURCE_CENTER8_CORE_ROUTE_STATUS,
    assert_expected_center8_core_route,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)
from scripts.check_bootstrap_t12_151_6_private_lane_strict_core_split import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    SCHEMA as SOURCE_STRICT_CORE_SPLIT_SCHEMA,
    SPLIT_STATUS as SOURCE_STRICT_CORE_SPLIT_STATUS_SUMMARY,
    STATUS as SOURCE_STRICT_CORE_SPLIT_STATUS,
    assert_expected_private_lane_strict_core_split,
    load_artifact,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_residual_target_rows.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_RESIDUAL_TARGET_ROWS_DIAGNOSTIC_ONLY"
GATE_STATUS = "NOT_READY_RESIDUAL_TARGET_ROWS_DO_NOT_FORCE_CENTER8"
RESIDUAL_STATUS = "RESIDUAL_SPLIT_OFF_CENTER_TARGET_ROWS_OR_TARGET_SPARSE"
CLAIM_SCOPE = (
    "Proof-mining residual target-row crosswalk for the source-151 row-6 "
    "private-lane label-4 cascade. It refines the six private-lane "
    "assignments that have no center-8 target-compatible local core. Four "
    "of the six residual assignments contain an off-center row with "
    "witnesses [0,4,6] in a strict core, while assignments 0 and 11 do not "
    "contain the full target triple in any strict-core row. This does not "
    "prove center migration, does not prove support existence, does not "
    "prove row forcing, does not prove endpoint-8 forcing, does not prove "
    "that pair [3,5] is impossible, does not prove n=9, does not prove the "
    "bootstrap bridge, is not a counterexample, and is not a global status "
    "update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_center8_residual_target_rows.py"
    ),
    "command": (
        "python "
        "scripts/check_bootstrap_t12_151_6_label4_center8_residual_target_rows.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_residual_target_rows.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_residual_records",
    "claim_scope",
    "decision",
    "interpretation",
    "off_center_target_row_records",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "target_sparse_assignment_records",
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
    "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
    "conditional_center8_target_status": SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    "source_center8_core_route_gate_status": SOURCE_CENTER8_CORE_ROUTE_GATE_STATUS,
    "source_private_lane_assignment_count": 12,
    "source_center8_target_assignment_count": 6,
    "residual_assignment_count": 6,
    "residual_assignment_indices": [0, 5, 7, 9, 10, 11],
    "residual_core_count": 19,
    "residual_label8_visible_core_count": 15,
    "residual_label8_free_core_count": 4,
    "residual_center8_core_count": 1,
    "residual_center8_target_core_count": 0,
    "residual_assignments_with_off_center_target_row": 4,
    "residual_assignments_with_off_center_target_row_indices": [5, 7, 9, 10],
    "residual_assignments_without_any_target_row": 2,
    "target_sparse_assignment_indices": [0, 11],
    "off_center_target_row_occurrence_count": 5,
    "off_center_target_core_count": 5,
    "off_center_target_label8_visible_core_count": 1,
    "off_center_target_label8_free_core_count": 4,
    "off_center_target_row_center_counts": {"2": 2, "5": 1, "7": 2},
    "off_center_target_exact_row_counts": {
        "0,1,4,6": 1,
        "0,2,4,6": 2,
        "0,3,4,6": 2,
    },
    "off_center_target_auxiliary_center_pair_counts": {
        "2,5": 1,
        "2,7": 2,
        "3,5": 1,
        "3,7": 1,
    },
    "target_sparse_max_target_overlap": 2,
    "target_sparse_pair_row_occurrence_count": 6,
    "target_sparse_pair_overlap_counts": {"0,4": 2, "0,6": 3, "4,6": 1},
    "current_evidence_forces_center8_target_core": False,
    "off_center_target_rows_supply_center8_target": False,
    "gate_status": GATE_STATUS,
    "residual_status": RESIDUAL_STATUS,
}


def build_center8_residual_target_rows_payload(
    strict_core_split: Mapping[str, Any],
    center8_core_route: Mapping[str, Any],
    *,
    strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    center8_core_route_path: Path = DEFAULT_SOURCE_CENTER8_CORE_ROUTE,
) -> dict[str, Any]:
    """Return the deterministic center-8 residual target-row payload."""

    errors: list[str] = []
    assert_expected_private_lane_strict_core_split(strict_core_split)
    assert_expected_center8_core_route(center8_core_route)
    _validate_sources(strict_core_split, center8_core_route, errors)
    (
        summary,
        assignment_records,
        off_center_records,
        target_sparse_records,
    ) = _residual_records(strict_core_split, center8_core_route)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Do all no-center-8-target residual assignments already "
                "contain [0,4,6] in some strict-core row?"
            ),
            "answer": "no_two_residual_assignments_are_target_sparse",
            "gate_status": GATE_STATUS,
            "residual_status": RESIDUAL_STATUS,
            "current_evidence_forces_center8_target_core": False,
            "off_center_target_rows_supply_center8_target": False,
            "center_migration_required_for_off_center_rows": True,
            "target_sparse_assignments_require_separate_obstruction": True,
            "blocking_reason": (
                "The residual rows containing [0,4,6] are centered at 2, 5, "
                "or 7, not at 8, and assignments 0 and 11 contain no full "
                "[0,4,6] row in any residual strict core."
            ),
            "required_next_lemma": (
                "Either migrate the off-center target rows to center 8 under "
                "genuine support geometry, or obstruct the target-sparse "
                "residual assignments 0 and 11."
            ),
        },
        "assignment_residual_records": assignment_records,
        "off_center_target_row_records": off_center_records,
        "target_sparse_assignment_records": target_sparse_records,
        "source_artifacts": [
            _source_summary(
                strict_core_split_path,
                "source 151:6 private-lane strict-core split",
                strict_core_split,
            ),
            _source_summary(
                center8_core_route_path,
                "source 151:6 center-8 core route",
                center8_core_route,
            ),
        ],
        "interpretation": [
            (
                "The six no-center-8-target assignments split into four "
                "off-center-target cases and two target-sparse cases."
            ),
            (
                "The off-center rows already contain [0,4,6], but their row "
                "centers are 2, 5, or 7; they are not center-8 supply."
            ),
            (
                "Assignments 0 and 11 still require a separate obstruction "
                "or a stronger source because no strict-core row contains "
                "the full target triple."
            ),
            (
                "This is a residual route map only; it does not prove center "
                "migration, support existence, row forcing, endpoint-8 "
                "forcing, or impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_residual_target_rows(payload)
    return payload


def assert_expected_center8_residual_target_rows(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned center-8 residual target-row packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    center8_core_route_path: Path = DEFAULT_SOURCE_CENTER8_CORE_ROUTE,
) -> list[str]:
    """Return validation errors for a center-8 residual target-row payload."""

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
            "off-center row with witnesses [0,4,6]",
            "assignments 0 and 11",
            "does not prove center migration",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove endpoint-8 forcing",
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

    assignment_records = payload.get("assignment_residual_records")
    if not isinstance(assignment_records, list):
        errors.append("assignment_residual_records must be a list")
    else:
        _validate_assignment_records(assignment_records, errors)
    off_center_records = payload.get("off_center_target_row_records")
    if not isinstance(off_center_records, list):
        errors.append("off_center_target_row_records must be a list")
    else:
        _validate_off_center_records(off_center_records, errors)
    target_sparse_records = payload.get("target_sparse_assignment_records")
    if not isinstance(target_sparse_records, list):
        errors.append("target_sparse_assignment_records must be a list")
    else:
        _validate_target_sparse_records(target_sparse_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("not center-8 supply" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the off-center warning")

    if recompute and not errors:
        generated = build_center8_residual_target_rows_payload(
            load_artifact(strict_core_split_path),
            load_artifact(center8_core_route_path),
            strict_core_split_path=strict_core_split_path,
            center8_core_route_path=center8_core_route_path,
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
        "residual_assignment_count": summary.get("residual_assignment_count"),
        "residual_assignment_indices": summary.get("residual_assignment_indices"),
        "off_center_target_row_occurrence_count": summary.get(
            "off_center_target_row_occurrence_count"
        ),
        "residual_assignments_with_off_center_target_row": summary.get(
            "residual_assignments_with_off_center_target_row"
        ),
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _residual_records(
    strict_core_split: Mapping[str, Any],
    center8_core_route: Mapping[str, Any],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    split_summary = _required_mapping(
        strict_core_split.get("summary"), "strict-core split summary"
    )
    route_summary = _required_mapping(
        center8_core_route.get("summary"), "center-8 core route summary"
    )

    route_assignments = _required_list(
        center8_core_route.get("assignment_route_records"),
        "center-8 route assignment records",
    )
    residual_indices = [
        int(record["assignment_index"])
        for record in route_assignments
        if isinstance(record, Mapping) and not record["has_center8_target_core"]
    ]
    residual_index_set = set(residual_indices)
    route_record_by_index = {
        int(record["assignment_index"]): record
        for record in route_assignments
        if isinstance(record, Mapping)
    }

    raw_assignments = _required_list(
        strict_core_split.get("assignment_records"),
        "strict-core split assignment records",
    )
    assignment_records: list[dict[str, Any]] = []
    off_center_records: list[dict[str, Any]] = []
    target_sparse_records: list[dict[str, Any]] = []

    for raw_assignment in raw_assignments:
        if not isinstance(raw_assignment, Mapping):
            raise AssertionError("assignment record must be an object")
        assignment_index = int(raw_assignment["assignment_index"])
        if assignment_index not in residual_index_set:
            continue
        route_record = _required_mapping(
            route_record_by_index[assignment_index],
            f"route record {assignment_index}",
        )
        cores = _required_list(raw_assignment.get("cores"), "assignment cores")
        assignment_off_center_rows: list[dict[str, Any]] = []
        target_pair_rows: list[dict[str, Any]] = []
        center8_rows: list[list[int]] = []
        max_target_overlap = 0

        for core_index, raw_core in enumerate(cores):
            if not isinstance(raw_core, Mapping):
                raise AssertionError("core record must be an object")
            label8_visible = bool(raw_core["label8_visible"])
            rows = _required_list(raw_core.get("rows"), "core rows")
            for raw_row in rows:
                if not isinstance(raw_row, Mapping):
                    raise AssertionError("core row must be an object")
                row_center = int(raw_row["center"])
                witnesses = _int_list(raw_row["witnesses"])
                overlap = sorted(set(ENDPOINT_TRIPLE).intersection(witnesses))
                max_target_overlap = max(max_target_overlap, len(overlap))
                if row_center == ENDPOINT_CENTER:
                    center8_rows.append(witnesses)
                if len(overlap) >= 2:
                    target_pair_rows.append(
                        {
                            "core_index": core_index,
                            "row_center": row_center,
                            "row_witnesses": witnesses,
                            "target_overlap": overlap,
                        }
                    )
                if not _contains(ENDPOINT_TRIPLE, witnesses):
                    continue
                record = {
                    "assignment_index": assignment_index,
                    "core_index": core_index,
                    "row_center": row_center,
                    "row_witnesses": witnesses,
                    "target_overlap": overlap,
                    "row_center_equals_endpoint_center": row_center
                    == ENDPOINT_CENTER,
                    "exact_endpoint_row_allowed": list(witnesses)
                    in EXACT_FOUR_ENDPOINT_ROWS,
                    "auxiliary_center_pair": str(raw_core["auxiliary_center_pair"]),
                    "label8_visible": label8_visible,
                    "core_centers": _int_list(raw_core["centers"]),
                    "cycle_edge_count": int(raw_core["cycle_edge_count"]),
                    "strict_edge_count": int(raw_core["strict_edge_count"]),
                }
                off_center_records.append(record)
                assignment_off_center_rows.append(record)

        target_pair_rows = sorted(
            target_pair_rows,
            key=lambda item: (
                int(item["core_index"]),
                int(item["row_center"]),
                item["row_witnesses"],
            ),
        )
        assignment_record = {
            "assignment_index": assignment_index,
            "residual_class": (
                "off_center_target_row_available"
                if assignment_off_center_rows
                else "target_sparse"
            ),
            "core_count": int(raw_assignment["row6_three_row_strict_core_count"]),
            "label8_visible_core_count": int(raw_assignment["label8_visible_core_count"]),
            "label8_free_core_count": int(raw_assignment["label8_free_core_count"]),
            "center8_core_count": int(route_record["center8_core_count"]),
            "center8_target_core_count": int(route_record["center8_target_core_count"]),
            "off_center_target_row_count": len(assignment_off_center_rows),
            "off_center_target_core_indices": sorted(
                {int(record["core_index"]) for record in assignment_off_center_rows}
            ),
            "off_center_target_rows": [
                {
                    "core_index": int(record["core_index"]),
                    "row_center": int(record["row_center"]),
                    "row_witnesses": list(record["row_witnesses"]),
                    "label8_visible": bool(record["label8_visible"]),
                }
                for record in assignment_off_center_rows
            ],
            "target_pair_row_count": len(target_pair_rows),
            "target_pair_rows": target_pair_rows,
            "center8_rows": sorted(_unique_rows(center8_rows)),
            "max_target_overlap": max_target_overlap,
        }
        assignment_records.append(assignment_record)
        if not assignment_off_center_rows:
            target_sparse_records.append(assignment_record)

    off_center_records = sorted(
        off_center_records,
        key=lambda record: (
            int(record["assignment_index"]),
            int(record["core_index"]),
            int(record["row_center"]),
            record["row_witnesses"],
        ),
    )
    assignment_records = sorted(
        assignment_records, key=lambda record: int(record["assignment_index"])
    )
    target_sparse_records = sorted(
        target_sparse_records, key=lambda record: int(record["assignment_index"])
    )

    off_center_core_keys = {
        (int(record["assignment_index"]), int(record["core_index"]))
        for record in off_center_records
    }
    target_sparse_pair_overlap_counter: Counter[str] = Counter(
        _row_key(pair_row["target_overlap"])
        for record in target_sparse_records
        for pair_row in record["target_pair_rows"]
        if len(pair_row["target_overlap"]) == 2
    )
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": ENDPOINT_CENTER,
        "conditional_center8_triple": ENDPOINT_TRIPLE,
        "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
        "conditional_center8_target_status": SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
        "source_center8_core_route_gate_status": route_summary["gate_status"],
        "source_private_lane_assignment_count": int(
            split_summary["source_private_lane_survivor_count"]
        ),
        "source_center8_target_assignment_count": int(
            route_summary["assignments_with_center8_target_core"]
        ),
        "residual_assignment_count": len(assignment_records),
        "residual_assignment_indices": residual_indices,
        "residual_core_count": sum(
            int(record["core_count"]) for record in assignment_records
        ),
        "residual_label8_visible_core_count": sum(
            int(record["label8_visible_core_count"]) for record in assignment_records
        ),
        "residual_label8_free_core_count": sum(
            int(record["label8_free_core_count"]) for record in assignment_records
        ),
        "residual_center8_core_count": sum(
            int(record["center8_core_count"]) for record in assignment_records
        ),
        "residual_center8_target_core_count": sum(
            int(record["center8_target_core_count"]) for record in assignment_records
        ),
        "residual_assignments_with_off_center_target_row": sum(
            1
            for record in assignment_records
            if record["off_center_target_row_count"] > 0
        ),
        "residual_assignments_with_off_center_target_row_indices": [
            int(record["assignment_index"])
            for record in assignment_records
            if record["off_center_target_row_count"] > 0
        ],
        "residual_assignments_without_any_target_row": len(target_sparse_records),
        "target_sparse_assignment_indices": [
            int(record["assignment_index"]) for record in target_sparse_records
        ],
        "off_center_target_row_occurrence_count": len(off_center_records),
        "off_center_target_core_count": len(off_center_core_keys),
        "off_center_target_label8_visible_core_count": sum(
            1 for record in off_center_records if record["label8_visible"]
        ),
        "off_center_target_label8_free_core_count": sum(
            1 for record in off_center_records if not record["label8_visible"]
        ),
        "off_center_target_row_center_counts": _json_counter(
            Counter(str(record["row_center"]) for record in off_center_records)
        ),
        "off_center_target_exact_row_counts": _row_counts(
            record["row_witnesses"] for record in off_center_records
        ),
        "off_center_target_auxiliary_center_pair_counts": _json_counter(
            Counter(
                str(record["auxiliary_center_pair"]) for record in off_center_records
            )
        ),
        "target_sparse_max_target_overlap": max(
            int(record["max_target_overlap"]) for record in target_sparse_records
        ),
        "target_sparse_pair_row_occurrence_count": sum(
            int(record["target_pair_row_count"]) for record in target_sparse_records
        ),
        "target_sparse_pair_overlap_counts": _json_counter(
            target_sparse_pair_overlap_counter
        ),
        "current_evidence_forces_center8_target_core": False,
        "off_center_target_rows_supply_center8_target": False,
        "gate_status": GATE_STATUS,
        "residual_status": RESIDUAL_STATUS,
    }
    return summary, assignment_records, off_center_records, target_sparse_records


def _validate_sources(
    strict_core_split: Mapping[str, Any],
    center8_core_route: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = [
        (
            "strict-core split",
            strict_core_split,
            SOURCE_STRICT_CORE_SPLIT_SCHEMA,
            SOURCE_STRICT_CORE_SPLIT_STATUS,
        ),
        (
            "center-8 core route",
            center8_core_route,
            SOURCE_CENTER8_CORE_ROUTE_SCHEMA,
            SOURCE_CENTER8_CORE_ROUTE_STATUS,
        ),
    ]
    for label, payload, schema, status in expected:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")

    split_summary = _mapping(
        strict_core_split.get("summary"), "strict-core split summary", errors
    )
    if split_summary.get("split_status") != SOURCE_STRICT_CORE_SPLIT_STATUS_SUMMARY:
        errors.append("strict-core split status mismatch")
    route_summary = _mapping(
        center8_core_route.get("summary"), "center-8 core route summary", errors
    )
    if route_summary.get("gate_status") != SOURCE_CENTER8_CORE_ROUTE_GATE_STATUS:
        errors.append("center-8 core route gate status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_two_residual_assignments_are_target_sparse",
        "gate_status": GATE_STATUS,
        "residual_status": RESIDUAL_STATUS,
        "current_evidence_forces_center8_target_core": False,
        "off_center_target_rows_supply_center8_target": False,
        "center_migration_required_for_off_center_rows": True,
        "target_sparse_assignments_require_separate_obstruction": True,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "assignments 0 and 11" not in required_next:
        errors.append("decision.required_next_lemma must name assignments 0 and 11")


def _validate_assignment_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 6:
        errors.append("assignment_residual_records must contain six records")
        return
    expected_indices = [0, 5, 7, 9, 10, 11]
    indices: list[int] = []
    off_center_count = 0
    target_sparse_count = 0
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("assignment_residual_records entries must be objects")
            continue
        indices.append(int(record.get("assignment_index", -1)))
        if record.get("center8_target_core_count") != 0:
            errors.append("residual assignments must have no center-8 target core")
        if record.get("off_center_target_row_count", 0) > 0:
            off_center_count += 1
        if record.get("residual_class") == "target_sparse":
            target_sparse_count += 1
    if indices != expected_indices:
        errors.append(f"residual assignment indices mismatch: {indices!r}")
    if off_center_count != 4:
        errors.append("expected four residual assignments with off-center target rows")
    if target_sparse_count != 2:
        errors.append("expected two target-sparse residual assignments")


def _validate_off_center_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 5:
        errors.append("off_center_target_row_records must contain five records")
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"off_center_target_row_records[{index}] must be an object")
            continue
        if record.get("row_center") == ENDPOINT_CENTER:
            errors.append("off-center target rows must not be centered at 8")
        witnesses = record.get("row_witnesses")
        if not isinstance(witnesses, list) or not _contains(ENDPOINT_TRIPLE, witnesses):
            errors.append(f"off_center_target_row_records[{index}] witness mismatch")
        if record.get("row_center_equals_endpoint_center") is not False:
            errors.append("off-center target rows must preserve the center warning")


def _validate_target_sparse_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    indices: list[int] = []
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("target_sparse_assignment_records entries must be objects")
            continue
        indices.append(int(record.get("assignment_index", -1)))
        if record.get("off_center_target_row_count") != 0:
            errors.append("target-sparse records must have no full target row")
        if record.get("max_target_overlap") != 2:
            errors.append("target-sparse records should still have pair overlaps")
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
        "split_status": summary.get("split_status"),
        "gate_status": summary.get("gate_status"),
    }


def _contains(needles: Sequence[int], haystack: Sequence[int]) -> bool:
    return set(int(needle) for needle in needles) <= set(int(item) for item in haystack)


def _unique_rows(rows: Iterable[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in sorted({tuple(row) for row in rows})]


def _row_counts(rows: Iterable[Sequence[int]]) -> dict[str, int]:
    counts: Counter[tuple[int, ...]] = Counter(tuple(row) for row in rows)
    return {_row_key(row): int(counts[row]) for row in sorted(counts)}


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


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
        "--source-strict-core-split",
        type=Path,
        default=DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    )
    parser.add_argument(
        "--source-center8-core-route",
        type=Path,
        default=DEFAULT_SOURCE_CENTER8_CORE_ROUTE,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_strict_core_split = _resolve(args.source_strict_core_split)
    source_center8_core_route = _resolve(args.source_center8_core_route)
    generated = build_center8_residual_target_rows_payload(
        load_artifact(source_strict_core_split),
        load_artifact(source_center8_core_route),
        strict_core_split_path=source_strict_core_split,
        center8_core_route_path=source_center8_core_route,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        strict_core_split_path=source_strict_core_split,
        center8_core_route_path=source_center8_core_route,
    )
    if args.assert_expected:
        assert_expected_center8_residual_target_rows(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 residual target rows")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade target: {summary['conditional_center8_triple']}")
        print(f"residual assignments: {summary['residual_assignment_count']}")
        print(
            "off-center target rows: "
            f"{summary['off_center_target_row_occurrence_count']}"
        )
        print(
            "target-sparse assignments: "
            f"{summary['target_sparse_assignment_indices']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 residual target rows verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
