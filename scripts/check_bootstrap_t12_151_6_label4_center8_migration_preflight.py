#!/usr/bin/env python3
"""Check the center-migration preflight for source-151 center-8 residual rows."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    EXACT_FOUR_ENDPOINT_ROWS,
    SCHEMA as SOURCE_CASCADE_ENDPOINT8_SCHEMA,
    STATUS as SOURCE_CASCADE_ENDPOINT8_STATUS,
    TARGET_STATUS as SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    assert_expected_cascade_endpoint8_targets,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_residual_target_rows import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS as SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS,
    SCHEMA as SOURCE_RESIDUAL_TARGET_ROWS_SCHEMA,
    STATUS as SOURCE_RESIDUAL_TARGET_ROWS_STATUS,
    assert_expected_center8_residual_target_rows,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    GATE_STATUS as SOURCE_CENTER8_PREFLIGHT_GATE_STATUS,
    SCHEMA as SOURCE_CENTER8_PREFLIGHT_SCHEMA,
    STATUS as SOURCE_CENTER8_PREFLIGHT_STATUS,
    assert_expected_center8_rich_triple_preflight,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_source_crosswalk import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK,
    GATE_STATUS as SOURCE_CENTER8_SOURCE_CROSSWALK_GATE_STATUS,
    SCHEMA as SOURCE_CENTER8_SOURCE_CROSSWALK_SCHEMA,
    SOURCE151_CENTER8_KEY,
    STATUS as SOURCE_CENTER8_SOURCE_CROSSWALK_STATUS,
    assert_expected_center8_source_crosswalk,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_migration_preflight.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_MIGRATION_PREFLIGHT_DIAGNOSTIC_ONLY"
GATE_STATUS = "NOT_READY_CENTER_MIGRATION_NOT_PROVED"
MIGRATION_STATUS = (
    "OFF_CENTER_TARGET_ROWS_REQUIRE_NEW_CENTER8_SOURCE_OR_MIGRATION_LEMMA"
)
CLAIM_SCOPE = (
    "Proof-mining center-migration preflight for the source-151 row-6 "
    "private-lane label-4 cascade. It joins the residual target-row split, "
    "the center-8 rich-triple preflight, the source-151 center-8 source "
    "crosswalk, and the cascade endpoint-8 target packet. It records that "
    "four residual assignments contain [0,4,6] only as off-center strict-core "
    "rows at centers 2, 5, or 7. Re-centering those exact rows at center 8 "
    "would land inside the conditional endpoint-8 target family, but current "
    "checked support evidence does not supply a center-8 rich class and the "
    "existing source-151 row-8 packet supplies no target pair from [0,4,6]. "
    "This does not prove center migration, does not prove support existence, "
    "does not prove row forcing, does not prove endpoint-8 forcing, does not "
    "prove that assignments 0 and 11 are impossible, does not prove that pair "
    "[3,5] is impossible, does not prove n=9, does not prove the bootstrap "
    "bridge, is not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_center8_migration_preflight.py"
    ),
    "command": (
        "python "
        "scripts/check_bootstrap_t12_151_6_label4_center8_migration_preflight.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_migration_preflight.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_migration_records",
    "claim_scope",
    "decision",
    "interpretation",
    "migration_candidate_records",
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
    "source_residual_gate_status": SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS,
    "source_center8_preflight_gate_status": SOURCE_CENTER8_PREFLIGHT_GATE_STATUS,
    "source_center8_source_crosswalk_gate_status": (
        SOURCE_CENTER8_SOURCE_CROSSWALK_GATE_STATUS
    ),
    "source151_named_center8_target_row_key": SOURCE151_CENTER8_KEY,
    "source151_named_center8_max_target_triple_overlap": 1,
    "source151_named_center8_candidate_rows_with_target_pair_count": 0,
    "source151_named_center8_candidate_rows_with_full_target_triple_count": 0,
    "source151_one_outside_activation_rows_with_full_target_triple_count": 0,
    "support_requirement_center8_count": 0,
    "support_requirements_with_label8_witness_count": 0,
    "center8_requirement_with_full_triple_count": 0,
    "residual_assignment_count": 6,
    "residual_assignment_indices": [0, 5, 7, 9, 10, 11],
    "off_center_residual_assignment_count": 4,
    "off_center_residual_assignment_indices": [5, 7, 9, 10],
    "target_sparse_assignment_count": 2,
    "target_sparse_assignment_indices": [0, 11],
    "migration_candidate_count": 5,
    "migration_candidate_distinct_exact_row_count": 3,
    "migration_candidate_source_centers": [2, 5, 7],
    "migration_candidate_source_center_counts": {"2": 2, "5": 1, "7": 2},
    "migration_candidate_exact_row_counts": {
        "0,1,4,6": 1,
        "0,2,4,6": 2,
        "0,3,4,6": 2,
    },
    "migration_candidate_center8_exact_rows": [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 3, 4, 6],
    ],
    "candidate_center8_exact_rows_covered_by_endpoint_target_count": 3,
    "endpoint_exact_rows_not_seen_off_center": [
        [0, 4, 5, 6],
        [0, 4, 6, 7],
    ],
    "conditional_obstruction_available_if_migration_proved": True,
    "current_support_ledger_forces_center8_rich_triple": False,
    "current_source151_center8_supplies_cascade_triple": False,
    "current_evidence_proves_center_migration": False,
    "off_center_rows_migrate_to_center8_under_current_evidence": False,
    "gate_status": GATE_STATUS,
    "migration_status": MIGRATION_STATUS,
}


def build_center8_migration_preflight_payload(
    residual_target_rows: Mapping[str, Any],
    center8_preflight: Mapping[str, Any],
    center8_source_crosswalk: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    *,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    center8_preflight_path: Path = DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    center8_source_crosswalk_path: Path = DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> dict[str, Any]:
    """Return the deterministic center-migration preflight payload."""

    errors: list[str] = []
    assert_expected_center8_residual_target_rows(residual_target_rows)
    assert_expected_center8_rich_triple_preflight(center8_preflight)
    assert_expected_center8_source_crosswalk(center8_source_crosswalk)
    assert_expected_cascade_endpoint8_targets(cascade_endpoint8_targets)
    _validate_sources(
        residual_target_rows,
        center8_preflight,
        center8_source_crosswalk,
        cascade_endpoint8_targets,
        errors,
    )
    (
        summary,
        migration_candidate_records,
        assignment_migration_records,
        target_sparse_assignment_records,
    ) = _migration_records(
        residual_target_rows,
        center8_preflight,
        center8_source_crosswalk,
        cascade_endpoint8_targets,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Do the off-center residual rows containing [0,4,6] already "
                "supply the center-8 endpoint target by a checked "
                "center-migration argument?"
            ),
            "answer": "no_center_migration_requires_a_new_lemma_or_source",
            "gate_status": GATE_STATUS,
            "migration_status": MIGRATION_STATUS,
            "conditional_obstruction_available_if_migration_proved": True,
            "current_support_ledger_forces_center8_rich_triple": False,
            "current_source151_center8_supplies_cascade_triple": False,
            "current_evidence_proves_center_migration": False,
            "off_center_rows_migrate_to_center8_under_current_evidence": False,
            "blocking_reason": (
                "The five [0,4,6] occurrences are centered at 2, 5, or 7. "
                "The support preflight has no center-8 support requirement, "
                "and the existing source-151 row-8 packet has no target pair "
                "from [0,4,6]."
            ),
            "required_next_lemma": (
                "Prove a genuine center-migration lemma from the off-center "
                "[0,4,6] rows to a center-8 rich class, add an independent "
                "center-8 source for [0,4,6], or leave this lane and obstruct "
                "the target-sparse assignments 0 and 11 by stronger geometry."
            ),
        },
        "migration_candidate_records": migration_candidate_records,
        "assignment_migration_records": assignment_migration_records,
        "target_sparse_assignment_records": target_sparse_assignment_records,
        "source_artifacts": [
            _source_summary(
                residual_target_rows_path,
                "source 151:6 center-8 residual target rows",
                residual_target_rows,
            ),
            _source_summary(
                center8_preflight_path,
                "source 151:6 center-8 rich-triple preflight",
                center8_preflight,
            ),
            _source_summary(
                center8_source_crosswalk_path,
                "source 151:6 center-8 source crosswalk",
                center8_source_crosswalk,
            ),
            _source_summary(
                cascade_endpoint8_targets_path,
                "source 151:6 cascade endpoint-8 targets",
                cascade_endpoint8_targets,
            ),
        ],
        "interpretation": [
            (
                "The off-center rows are real target-triple occurrences: each "
                "contains [0,4,6] and each corresponding center-8 exact row "
                "belongs to the conditional endpoint-target family."
            ),
            (
                "They are not center-8 supply under current evidence because "
                "their row centers are 2, 5, or 7."
            ),
            (
                "The existing source-151 row-8 singleton packet cannot be "
                "reused as the migration source: its checked candidates have "
                "no pair from [0,4,6]."
            ),
            (
                "This packet is a route preflight only; it does not prove "
                "center migration, support existence, row forcing, endpoint-8 "
                "forcing, or impossibility of the target-sparse assignments."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_migration_preflight(payload)
    return payload


def assert_expected_center8_migration_preflight(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned center-migration preflight packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    center8_preflight_path: Path = DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    center8_source_crosswalk_path: Path = DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> list[str]:
    """Return validation errors for a center-migration preflight payload."""

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
            "off-center strict-core rows at centers 2, 5, or 7",
            "does not prove center migration",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove endpoint-8 forcing",
            "does not prove that assignments 0 and 11 are impossible",
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
    migration_candidate_records = payload.get("migration_candidate_records")
    if not isinstance(migration_candidate_records, list):
        errors.append("migration_candidate_records must be a list")
    else:
        _validate_migration_candidate_records(migration_candidate_records, errors)
    assignment_records = payload.get("assignment_migration_records")
    if not isinstance(assignment_records, list):
        errors.append("assignment_migration_records must be a list")
    else:
        _validate_assignment_records(assignment_records, errors)
    target_sparse_records = payload.get("target_sparse_assignment_records")
    if not isinstance(target_sparse_records, list):
        errors.append("target_sparse_assignment_records must be a list")
    else:
        _validate_target_sparse_records(target_sparse_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("not center-8 supply" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the center-8 warning")

    if recompute and not errors:
        generated = build_center8_migration_preflight_payload(
            load_artifact(residual_target_rows_path),
            load_artifact(center8_preflight_path),
            load_artifact(center8_source_crosswalk_path),
            load_artifact(cascade_endpoint8_targets_path),
            residual_target_rows_path=residual_target_rows_path,
            center8_preflight_path=center8_preflight_path,
            center8_source_crosswalk_path=center8_source_crosswalk_path,
            cascade_endpoint8_targets_path=cascade_endpoint8_targets_path,
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
        "off_center_residual_assignment_indices": summary.get(
            "off_center_residual_assignment_indices"
        ),
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "migration_candidate_count": summary.get("migration_candidate_count"),
        "migration_candidate_source_centers": summary.get(
            "migration_candidate_source_centers"
        ),
        "current_evidence_proves_center_migration": summary.get(
            "current_evidence_proves_center_migration"
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _migration_records(
    residual_target_rows: Mapping[str, Any],
    center8_preflight: Mapping[str, Any],
    center8_source_crosswalk: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    residual_summary = _required_mapping(
        residual_target_rows.get("summary"), "residual target-row summary"
    )
    preflight_summary = _required_mapping(
        center8_preflight.get("summary"), "center-8 preflight summary"
    )
    source_summary = _required_mapping(
        center8_source_crosswalk.get("summary"), "center-8 source summary"
    )
    endpoint_summary = _required_mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary"
    )
    off_center_records = _required_list(
        residual_target_rows.get("off_center_target_row_records"),
        "off-center target-row records",
    )
    residual_assignment_records = _required_list(
        residual_target_rows.get("assignment_residual_records"),
        "residual assignment records",
    )
    target_sparse_records_raw = _required_list(
        residual_target_rows.get("target_sparse_assignment_records"),
        "target-sparse assignment records",
    )

    migration_candidate_records: list[dict[str, Any]] = []
    records_by_assignment: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for raw_record in off_center_records:
        if not isinstance(raw_record, Mapping):
            raise AssertionError("off-center target-row record must be an object")
        assignment_index = int(raw_record["assignment_index"])
        row_center = int(raw_record["row_center"])
        row_witnesses = _int_list(raw_record["row_witnesses"])
        candidate = {
            "assignment_index": assignment_index,
            "core_index": int(raw_record["core_index"]),
            "source_row_center": row_center,
            "source_row_witnesses": row_witnesses,
            "candidate_center8_row_center": ENDPOINT_CENTER,
            "candidate_center8_row_witnesses": row_witnesses,
            "target_triple": ENDPOINT_TRIPLE,
            "candidate_center8_exact_row_allowed": row_witnesses
            in EXACT_FOUR_ENDPOINT_ROWS,
            "candidate_center8_obstructed_if_forced": True,
            "current_support_ledger_has_center8_requirement": False,
            "current_source151_center8_supplies_this_row": False,
            "current_evidence_migrates_this_row": False,
            "source_row_label8_visible": bool(raw_record["label8_visible"]),
            "source_auxiliary_center_pair": str(raw_record["auxiliary_center_pair"]),
            "source_core_centers": _int_list(raw_record["core_centers"]),
            "migration_blockers": [
                "source row center is not 8",
                "support ledger has no center-8 requirement",
                "source-151 row-8 packet has no target pair from [0,4,6]",
            ],
        }
        migration_candidate_records.append(candidate)
        records_by_assignment[assignment_index].append(candidate)

    migration_candidate_records = sorted(
        migration_candidate_records,
        key=lambda record: (
            int(record["assignment_index"]),
            int(record["core_index"]),
            int(record["source_row_center"]),
            record["source_row_witnesses"],
        ),
    )

    assignment_by_index = {
        int(record["assignment_index"]): record
        for record in residual_assignment_records
        if isinstance(record, Mapping)
    }
    assignment_migration_records: list[dict[str, Any]] = []
    for assignment_index in sorted(records_by_assignment):
        residual_record = _required_mapping(
            assignment_by_index[assignment_index],
            f"residual assignment {assignment_index}",
        )
        candidates = records_by_assignment[assignment_index]
        candidate_rows = _unique_rows(
            record["candidate_center8_row_witnesses"] for record in candidates
        )
        assignment_migration_records.append(
            {
                "assignment_index": assignment_index,
                "residual_class": residual_record["residual_class"],
                "source_center8_core_count": int(
                    residual_record["center8_core_count"]
                ),
                "source_center8_target_core_count": int(
                    residual_record["center8_target_core_count"]
                ),
                "off_center_target_row_count": int(
                    residual_record["off_center_target_row_count"]
                ),
                "migration_candidate_exact_rows": candidate_rows,
                "migration_candidate_source_centers": sorted(
                    {int(record["source_row_center"]) for record in candidates}
                ),
                "current_evidence_migrates_assignment": False,
                "required_migration_target": {
                    "center": ENDPOINT_CENTER,
                    "witness_triple": ENDPOINT_TRIPLE,
                    "candidate_exact_rows": candidate_rows,
                },
            }
        )

    target_sparse_assignment_records = [
        {
            "assignment_index": int(record["assignment_index"]),
            "residual_class": record["residual_class"],
            "target_pair_row_count": int(record["target_pair_row_count"]),
            "max_target_overlap": int(record["max_target_overlap"]),
            "current_evidence_migrates_assignment": False,
            "reason_not_a_migration_candidate": (
                "no strict-core row contains the full target triple [0,4,6]"
            ),
        }
        for record in target_sparse_records_raw
        if isinstance(record, Mapping)
    ]

    candidate_rows = _unique_rows(
        record["candidate_center8_row_witnesses"]
        for record in migration_candidate_records
    )
    endpoint_rows_not_seen = [
        list(row)
        for row in EXACT_FOUR_ENDPOINT_ROWS
        if list(row) not in candidate_rows
    ]
    source_center_counter = Counter(
        str(record["source_row_center"]) for record in migration_candidate_records
    )
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": ENDPOINT_CENTER,
        "conditional_center8_triple": ENDPOINT_TRIPLE,
        "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
        "conditional_center8_target_status": endpoint_summary["target_status"],
        "source_residual_gate_status": residual_summary["gate_status"],
        "source_center8_preflight_gate_status": preflight_summary["gate_status"],
        "source_center8_source_crosswalk_gate_status": source_summary["gate_status"],
        "source151_named_center8_target_row_key": source_summary[
            "source151_named_center8_target_row_key"
        ],
        "source151_named_center8_max_target_triple_overlap": int(
            source_summary["source151_named_center8_max_target_triple_overlap"]
        ),
        "source151_named_center8_candidate_rows_with_target_pair_count": int(
            source_summary[
                "source151_named_center8_candidate_rows_with_target_pair_count"
            ]
        ),
        "source151_named_center8_candidate_rows_with_full_target_triple_count": int(
            source_summary[
                "source151_named_center8_candidate_rows_with_full_target_triple_count"
            ]
        ),
        "source151_one_outside_activation_rows_with_full_target_triple_count": int(
            source_summary[
                "source151_one_outside_activation_rows_with_full_target_triple_count"
            ]
        ),
        "support_requirement_center8_count": int(
            preflight_summary["support_requirement_center8_count"]
        ),
        "support_requirements_with_label8_witness_count": int(
            preflight_summary["support_requirements_with_label8_witness_count"]
        ),
        "center8_requirement_with_full_triple_count": int(
            preflight_summary["center8_requirement_with_full_triple_count"]
        ),
        "residual_assignment_count": int(
            residual_summary["residual_assignment_count"]
        ),
        "residual_assignment_indices": residual_summary["residual_assignment_indices"],
        "off_center_residual_assignment_count": len(assignment_migration_records),
        "off_center_residual_assignment_indices": [
            int(record["assignment_index"]) for record in assignment_migration_records
        ],
        "target_sparse_assignment_count": len(target_sparse_assignment_records),
        "target_sparse_assignment_indices": [
            int(record["assignment_index"])
            for record in target_sparse_assignment_records
        ],
        "migration_candidate_count": len(migration_candidate_records),
        "migration_candidate_distinct_exact_row_count": len(candidate_rows),
        "migration_candidate_source_centers": sorted(
            {int(record["source_row_center"]) for record in migration_candidate_records}
        ),
        "migration_candidate_source_center_counts": _json_counter(
            source_center_counter
        ),
        "migration_candidate_exact_row_counts": _row_counts(
            record["candidate_center8_row_witnesses"]
            for record in migration_candidate_records
        ),
        "migration_candidate_center8_exact_rows": candidate_rows,
        "candidate_center8_exact_rows_covered_by_endpoint_target_count": sum(
            1 for row in candidate_rows if row in EXACT_FOUR_ENDPOINT_ROWS
        ),
        "endpoint_exact_rows_not_seen_off_center": endpoint_rows_not_seen,
        "conditional_obstruction_available_if_migration_proved": True,
        "current_support_ledger_forces_center8_rich_triple": bool(
            preflight_summary["current_evidence_forces_center8_rich_triple"]
        ),
        "current_source151_center8_supplies_cascade_triple": bool(
            source_summary[
                "current_source151_named_center8_evidence_supplies_cascade_triple"
            ]
        ),
        "current_evidence_proves_center_migration": False,
        "off_center_rows_migrate_to_center8_under_current_evidence": False,
        "gate_status": GATE_STATUS,
        "migration_status": MIGRATION_STATUS,
    }
    return (
        summary,
        migration_candidate_records,
        assignment_migration_records,
        target_sparse_assignment_records,
    )


def _validate_sources(
    residual_target_rows: Mapping[str, Any],
    center8_preflight: Mapping[str, Any],
    center8_source_crosswalk: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = [
        (
            "residual target rows",
            residual_target_rows,
            SOURCE_RESIDUAL_TARGET_ROWS_SCHEMA,
            SOURCE_RESIDUAL_TARGET_ROWS_STATUS,
        ),
        (
            "center-8 rich-triple preflight",
            center8_preflight,
            SOURCE_CENTER8_PREFLIGHT_SCHEMA,
            SOURCE_CENTER8_PREFLIGHT_STATUS,
        ),
        (
            "center-8 source crosswalk",
            center8_source_crosswalk,
            SOURCE_CENTER8_SOURCE_CROSSWALK_SCHEMA,
            SOURCE_CENTER8_SOURCE_CROSSWALK_STATUS,
        ),
        (
            "cascade endpoint-8 targets",
            cascade_endpoint8_targets,
            SOURCE_CASCADE_ENDPOINT8_SCHEMA,
            SOURCE_CASCADE_ENDPOINT8_STATUS,
        ),
    ]
    for label, payload, schema, status in expected:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")

    residual_summary = _mapping(
        residual_target_rows.get("summary"), "residual summary", errors
    )
    if residual_summary.get("gate_status") != SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS:
        errors.append("residual target-row gate status mismatch")
    preflight_summary = _mapping(
        center8_preflight.get("summary"), "center-8 preflight summary", errors
    )
    if preflight_summary.get("gate_status") != SOURCE_CENTER8_PREFLIGHT_GATE_STATUS:
        errors.append("center-8 preflight gate status mismatch")
    source_summary = _mapping(
        center8_source_crosswalk.get("summary"), "center-8 source summary", errors
    )
    if source_summary.get("gate_status") != SOURCE_CENTER8_SOURCE_CROSSWALK_GATE_STATUS:
        errors.append("center-8 source crosswalk gate status mismatch")
    endpoint_summary = _mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary", errors
    )
    if endpoint_summary.get("target_status") != SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS:
        errors.append("cascade endpoint target status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_center_migration_requires_a_new_lemma_or_source",
        "gate_status": GATE_STATUS,
        "migration_status": MIGRATION_STATUS,
        "conditional_obstruction_available_if_migration_proved": True,
        "current_support_ledger_forces_center8_rich_triple": False,
        "current_source151_center8_supplies_cascade_triple": False,
        "current_evidence_proves_center_migration": False,
        "off_center_rows_migrate_to_center8_under_current_evidence": False,
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


def _validate_migration_candidate_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 5:
        errors.append("migration_candidate_records must contain five records")
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"migration_candidate_records[{index}] must be an object")
            continue
        if record.get("source_row_center") == ENDPOINT_CENTER:
            errors.append("migration candidates must start off-center")
        if record.get("candidate_center8_row_center") != ENDPOINT_CENTER:
            errors.append("migration candidate target center must be 8")
        candidate = record.get("candidate_center8_row_witnesses")
        if not isinstance(candidate, list) or not _contains(ENDPOINT_TRIPLE, candidate):
            errors.append("migration candidate must contain [0,4,6]")
        if candidate not in EXACT_FOUR_ENDPOINT_ROWS:
            errors.append("migration candidate must be an exact endpoint row")
        for key in (
            "candidate_center8_obstructed_if_forced",
            "candidate_center8_exact_row_allowed",
        ):
            if record.get(key) is not True:
                errors.append(f"migration candidate must set {key} true")
        for key in (
            "current_support_ledger_has_center8_requirement",
            "current_source151_center8_supplies_this_row",
            "current_evidence_migrates_this_row",
        ):
            if record.get(key) is not False:
                errors.append(f"migration candidate must set {key} false")


def _validate_assignment_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    indices: list[int] = []
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("assignment_migration_records entries must be objects")
            continue
        indices.append(int(record.get("assignment_index", -1)))
        if record.get("current_evidence_migrates_assignment") is not False:
            errors.append("assignment migration records must not overclaim migration")
        if record.get("source_center8_target_core_count") != 0:
            errors.append("assignment migration records must be residual cases")
    if indices != [5, 7, 9, 10]:
        errors.append(f"assignment migration indices mismatch: {indices!r}")


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
        if record.get("current_evidence_migrates_assignment") is not False:
            errors.append("target-sparse records must not overclaim migration")
        reason = record.get("reason_not_a_migration_candidate")
        if not isinstance(reason, str) or "[0,4,6]" not in reason:
            errors.append("target-sparse records must name the missing target triple")
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
        "target_status": summary.get("target_status"),
        "decision_status": summary.get("decision_status"),
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
        "--source-residual-target-rows",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    )
    parser.add_argument(
        "--source-center8-preflight",
        type=Path,
        default=DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    )
    parser.add_argument(
        "--source-center8-source-crosswalk",
        type=Path,
        default=DEFAULT_SOURCE_CENTER8_SOURCE_CROSSWALK,
    )
    parser.add_argument(
        "--source-cascade-endpoint8-targets",
        type=Path,
        default=DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_residual_target_rows = _resolve(args.source_residual_target_rows)
    source_center8_preflight = _resolve(args.source_center8_preflight)
    source_center8_source_crosswalk = _resolve(args.source_center8_source_crosswalk)
    source_cascade_endpoint8_targets = _resolve(args.source_cascade_endpoint8_targets)
    generated = build_center8_migration_preflight_payload(
        load_artifact(source_residual_target_rows),
        load_artifact(source_center8_preflight),
        load_artifact(source_center8_source_crosswalk),
        load_artifact(source_cascade_endpoint8_targets),
        residual_target_rows_path=source_residual_target_rows,
        center8_preflight_path=source_center8_preflight,
        center8_source_crosswalk_path=source_center8_source_crosswalk,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
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
        center8_preflight_path=source_center8_preflight,
        center8_source_crosswalk_path=source_center8_source_crosswalk,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
    )
    if args.assert_expected:
        assert_expected_center8_migration_preflight(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 migration preflight")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade target: {summary['conditional_center8_triple']}")
        print(
            "off-center residual assignments: "
            f"{summary['off_center_residual_assignment_indices']}"
        )
        print(
            "target-sparse assignments: "
            f"{summary['target_sparse_assignment_indices']}"
        )
        print(f"migration candidates: {summary['migration_candidate_count']}")
        print(f"source centers: {summary['migration_candidate_source_centers']}")
        print(
            "current evidence proves migration: "
            f"{summary['current_evidence_proves_center_migration']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 migration preflight verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
