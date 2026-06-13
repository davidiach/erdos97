#!/usr/bin/env python3
"""Check the center-8 core route for the source-151 row-6 cascade."""

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
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    EXACT_FOUR_ENDPOINT_ROWS,
    SCHEMA as SOURCE_CASCADE_ENDPOINT8_SCHEMA,
    STATUS as SOURCE_CASCADE_ENDPOINT8_STATUS,
    TARGET_STATUS as SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    assert_expected_cascade_endpoint8_targets,
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


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_core_route.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_CORE_ROUTE_DIAGNOSTIC_ONLY"
GATE_STATUS = "NOT_READY_CENTER8_TARGET_COMPATIBLE_CORE_NOT_FORCED"
ROUTE_STATUS = "CENTER8_TARGET_COMPATIBLE_LOCAL_CORES_PINNED_NOT_FORCED"
CLAIM_SCOPE = (
    "Proof-mining route crosswalk for the source-151 row-6 private-lane "
    "label-4 cascade. It joins the private-lane strict-core split with the "
    "cascade endpoint-8 target packet to identify which row-6 local cores "
    "actually contain a center-8 row with witnesses [0,4,6]. It records that "
    "8 of 9 center-8 cores are target-compatible, but only 4 of the 32 "
    "label-8-visible cores are label-8-visible and target-compatible. Thus "
    "label-8 visibility alone is not enough to supply the center-8 cascade "
    "target. This does not prove support existence, does not prove row "
    "forcing, does not prove endpoint-8 forcing, does not prove that pair "
    "[3,5] is impossible, does not prove n=9, does not prove the bootstrap "
    "bridge, is not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_label4_center8_core_route.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_center8_core_route.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_core_route.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_route_records",
    "center8_core_records",
    "claim_scope",
    "decision",
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
    "source_private_lane_assignment_count": 12,
    "source_row6_three_row_strict_core_count": 44,
    "source_label8_visible_core_count": 32,
    "source_label8_free_core_count": 12,
    "source_center8_core_count": 9,
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
    "conditional_center8_target_status": SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    "center8_core_count": 9,
    "center8_target_compatible_core_count": 8,
    "center8_target_incompatible_core_count": 1,
    "label8_visible_center8_core_count": 5,
    "label8_free_center8_core_count": 4,
    "label8_visible_center8_target_core_count": 4,
    "label8_free_center8_target_core_count": 4,
    "label8_visible_non_center8_core_count": 27,
    "assignments_with_center8_core": 7,
    "assignments_with_center8_target_core": 6,
    "assignments_with_label8_visible_center8_target_core": 4,
    "assignments_with_label8_free_center8_target_core": 4,
    "assignments_with_label8_visible_core_but_no_center8_target_core": 6,
    "assignments_without_center8_target_core": 6,
    "center8_target_exact_row_counts": {
        "0,1,4,6": 4,
        "0,2,4,6": 2,
        "0,4,6,7": 2,
    },
    "label8_visible_center8_target_exact_row_counts": {
        "0,1,4,6": 2,
        "0,2,4,6": 1,
        "0,4,6,7": 1,
    },
    "covered_endpoint_exact_four_rows": [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ],
    "missing_endpoint_exact_four_rows": [
        [0, 3, 4, 6],
        [0, 4, 5, 6],
    ],
    "center8_target_core_auxiliary_center_pair_counts": {
        "0,8": 2,
        "5,8": 5,
        "7,8": 1,
    },
    "label8_visible_center8_target_core_auxiliary_center_pair_counts": {
        "0,8": 2,
        "5,8": 1,
        "7,8": 1,
    },
    "current_evidence_forces_center8_target_core": False,
    "label8_visibility_alone_supplies_center8_target": False,
    "gate_status": GATE_STATUS,
    "route_status": ROUTE_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_center8_core_route_payload(
    strict_core_split: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    *,
    strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> dict[str, Any]:
    """Return the deterministic center-8 core-route payload."""

    errors: list[str] = []
    assert_expected_private_lane_strict_core_split(strict_core_split)
    assert_expected_cascade_endpoint8_targets(cascade_endpoint8_targets)
    _validate_sources(strict_core_split, cascade_endpoint8_targets, errors)
    summary, assignment_records, center8_core_records = _route_records(
        strict_core_split,
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
                "Does forcing an arbitrary label-8-visible row-6 local core "
                "supply the center-8 cascade target [0,4,6]?"
            ),
            "answer": "do_not_treat_label8_visibility_alone_as_center8_target_supply",
            "gate_status": GATE_STATUS,
            "route_status": ROUTE_STATUS,
            "current_evidence_forces_center8_target_core": False,
            "label8_visibility_alone_supplies_center8_target": False,
            "conditional_obstruction_available_if_target_core_forced": True,
            "blocking_reason": (
                "Only 4 of the 32 label-8-visible local cores are both "
                "label-8-visible and center-8 target-compatible. Six of the "
                "12 private-lane assignments still have no center-8 core "
                "containing [0,4,6]."
            ),
            "required_next_lemma": (
                "Force one of the target-compatible center-8 local cores, or "
                "give a separate support-rich obstruction for the remaining "
                "private-lane assignments."
            ),
        },
        "assignment_route_records": assignment_records,
        "center8_core_records": center8_core_records,
        "source_artifacts": [
            _source_summary(
                strict_core_split_path,
                "source 151:6 private-lane strict-core split",
                strict_core_split,
            ),
            _source_summary(
                cascade_endpoint8_targets_path,
                "source 151:6 cascade endpoint-8 target packet",
                cascade_endpoint8_targets,
            ),
        ],
        "interpretation": [
            (
                "Target-compatible center-8 local cores are present in the "
                "private-lane split, but they are not universal across the "
                "12 private-lane assignments."
            ),
            (
                "Four label-8-visible cores already include a center-8 row "
                "containing [0,4,6], so forcing one of those exact local-core "
                "routes would supply the conditional center-8 endpoint target."
            ),
            (
                "Label-8 visibility alone remains too weak: most "
                "label-8-visible cores use label 8 only as an auxiliary-row "
                "witness and do not contain center 8 as a row."
            ),
            (
                "This is a route map only; it does not prove support "
                "existence, row forcing, endpoint-8 forcing, or impossibility "
                "of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_core_route(payload)
    return payload


def assert_expected_center8_core_route(payload: Mapping[str, Any]) -> None:
    """Assert the pinned center-8 core-route packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    strict_core_split_path: Path = DEFAULT_SOURCE_STRICT_CORE_SPLIT,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> list[str]:
    """Return validation errors for a center-8 core-route payload."""

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
            "center-8 row with witnesses [0,4,6]",
            "label-8 visibility alone is not enough",
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
    assignment_records = payload.get("assignment_route_records")
    if not isinstance(assignment_records, list):
        errors.append("assignment_route_records must be a list")
    else:
        _validate_assignment_records(assignment_records, errors)
    center8_core_records = payload.get("center8_core_records")
    if not isinstance(center8_core_records, list):
        errors.append("center8_core_records must be a list")
    else:
        _validate_center8_core_records(center8_core_records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("Label-8 visibility alone remains too weak" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the label-8 visibility warning")

    if recompute and not errors:
        generated = build_center8_core_route_payload(
            load_artifact(strict_core_split_path),
            load_artifact(cascade_endpoint8_targets_path),
            strict_core_split_path=strict_core_split_path,
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
        "center8_core_count": summary.get("center8_core_count"),
        "center8_target_compatible_core_count": summary.get(
            "center8_target_compatible_core_count"
        ),
        "label8_visible_center8_target_core_count": summary.get(
            "label8_visible_center8_target_core_count"
        ),
        "assignments_with_label8_visible_center8_target_core": summary.get(
            "assignments_with_label8_visible_center8_target_core"
        ),
        "assignments_without_center8_target_core": summary.get(
            "assignments_without_center8_target_core"
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _route_records(
    strict_core_split: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    split_summary = _required_mapping(
        strict_core_split.get("summary"), "strict-core split summary"
    )
    cascade_summary = _required_mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary"
    )
    assignment_records: list[dict[str, Any]] = []
    center8_core_records: list[dict[str, Any]] = []
    target_core_records: list[dict[str, Any]] = []

    raw_assignments = strict_core_split.get("assignment_records")
    if not isinstance(raw_assignments, list):
        raise AssertionError("strict-core split assignment_records must be a list")

    for raw_assignment in raw_assignments:
        if not isinstance(raw_assignment, Mapping):
            raise AssertionError("assignment record must be an object")
        assignment_index = int(raw_assignment["assignment_index"])
        cores = raw_assignment.get("cores")
        if not isinstance(cores, list):
            raise AssertionError("assignment cores must be a list")

        center8_indices: list[int] = []
        target_indices: list[int] = []
        visible_target_indices: list[int] = []
        free_target_indices: list[int] = []
        non_target_center8_rows: list[list[int]] = []
        target_rows: list[list[int]] = []

        for core_index, raw_core in enumerate(cores):
            if not isinstance(raw_core, Mapping):
                raise AssertionError("core record must be an object")
            center8_row = _row_for_center(raw_core, ENDPOINT_CENTER)
            if center8_row is None:
                continue
            center8_indices.append(core_index)
            row8_witnesses = _int_list(center8_row["witnesses"])
            target_compatible = _contains(ENDPOINT_TRIPLE, row8_witnesses)
            label8_visible = bool(raw_core["label8_visible"])
            record = {
                "assignment_index": assignment_index,
                "core_index": core_index,
                "centers": _int_list(raw_core["centers"]),
                "auxiliary_center_pair": str(raw_core["auxiliary_center_pair"]),
                "label8_visible": label8_visible,
                "center8_row_witnesses": row8_witnesses,
                "center8_target_compatible": target_compatible,
                "center8_target_overlap": sorted(
                    set(ENDPOINT_TRIPLE).intersection(row8_witnesses)
                ),
                "center8_extra_labels": [
                    label for label in row8_witnesses if label not in ENDPOINT_TRIPLE
                ],
                "cycle_edge_count": int(raw_core["cycle_edge_count"]),
                "strict_edge_count": int(raw_core["strict_edge_count"]),
                "core_rows": _core_rows(raw_core),
            }
            center8_core_records.append(record)
            if target_compatible:
                target_core_records.append(record)
                target_indices.append(core_index)
                target_rows.append(row8_witnesses)
                if label8_visible:
                    visible_target_indices.append(core_index)
                else:
                    free_target_indices.append(core_index)
            else:
                non_target_center8_rows.append(row8_witnesses)

        assignment_records.append(
            {
                "assignment_index": assignment_index,
                "label8_visible_core_count": int(raw_assignment["label8_visible_core_count"]),
                "label8_free_core_count": int(raw_assignment["label8_free_core_count"]),
                "center8_core_count": len(center8_indices),
                "center8_target_core_count": len(target_indices),
                "label8_visible_center8_target_core_count": len(visible_target_indices),
                "label8_free_center8_target_core_count": len(free_target_indices),
                "has_center8_target_core": bool(target_indices),
                "has_label8_visible_center8_target_core": bool(visible_target_indices),
                "has_label8_visible_core_but_no_center8_target_core": (
                    int(raw_assignment["label8_visible_core_count"]) > 0
                    and not target_indices
                ),
                "center8_core_indices": center8_indices,
                "center8_target_core_indices": target_indices,
                "label8_visible_center8_target_core_indices": visible_target_indices,
                "label8_free_center8_target_core_indices": free_target_indices,
                "center8_target_rows": sorted(_unique_rows(target_rows)),
                "non_target_center8_rows": sorted(_unique_rows(non_target_center8_rows)),
            }
        )

    exact_row_counts = _row_counts(
        record["center8_row_witnesses"] for record in target_core_records
    )
    visible_exact_row_counts = _row_counts(
        record["center8_row_witnesses"]
        for record in target_core_records
        if record["label8_visible"]
    )
    covered_rows = [list(row) for row in sorted(exact_row_counts)]
    missing_rows = [
        row for row in EXACT_FOUR_ENDPOINT_ROWS if tuple(row) not in exact_row_counts
    ]
    target_pair_counts = _json_counter(
        Counter(str(record["auxiliary_center_pair"]) for record in target_core_records)
    )
    visible_target_pair_counts = _json_counter(
        Counter(
            str(record["auxiliary_center_pair"])
            for record in target_core_records
            if record["label8_visible"]
        )
    )

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_private_lane_assignment_count": int(
            split_summary["source_private_lane_survivor_count"]
        ),
        "source_row6_three_row_strict_core_count": int(
            split_summary["row6_three_row_strict_core_count"]
        ),
        "source_label8_visible_core_count": int(
            split_summary["label8_visible_core_count"]
        ),
        "source_label8_free_core_count": int(split_summary["label8_free_core_count"]),
        "source_center8_core_count": int(split_summary["center8_core_count"]),
        "conditional_center8_target_center": int(cascade_summary["endpoint_center"]),
        "conditional_center8_triple": list(cascade_summary["endpoint_triple"]),
        "conditional_center8_exact_four_rows": list(
            cascade_summary["exact_four_endpoint_rows"]
        ),
        "conditional_center8_target_status": cascade_summary["target_status"],
        "center8_core_count": len(center8_core_records),
        "center8_target_compatible_core_count": len(target_core_records),
        "center8_target_incompatible_core_count": (
            len(center8_core_records) - len(target_core_records)
        ),
        "label8_visible_center8_core_count": sum(
            1 for record in center8_core_records if record["label8_visible"]
        ),
        "label8_free_center8_core_count": sum(
            1 for record in center8_core_records if not record["label8_visible"]
        ),
        "label8_visible_center8_target_core_count": sum(
            1 for record in target_core_records if record["label8_visible"]
        ),
        "label8_free_center8_target_core_count": sum(
            1 for record in target_core_records if not record["label8_visible"]
        ),
        "label8_visible_non_center8_core_count": (
            int(split_summary["label8_visible_core_count"])
            - sum(1 for record in center8_core_records if record["label8_visible"])
        ),
        "assignments_with_center8_core": sum(
            1 for record in assignment_records if record["center8_core_count"] > 0
        ),
        "assignments_with_center8_target_core": sum(
            1 for record in assignment_records if record["has_center8_target_core"]
        ),
        "assignments_with_label8_visible_center8_target_core": sum(
            1
            for record in assignment_records
            if record["has_label8_visible_center8_target_core"]
        ),
        "assignments_with_label8_free_center8_target_core": sum(
            1
            for record in assignment_records
            if record["label8_free_center8_target_core_count"] > 0
        ),
        "assignments_with_label8_visible_core_but_no_center8_target_core": sum(
            1
            for record in assignment_records
            if record["has_label8_visible_core_but_no_center8_target_core"]
        ),
        "assignments_without_center8_target_core": sum(
            1 for record in assignment_records if not record["has_center8_target_core"]
        ),
        "center8_target_exact_row_counts": _string_row_counts(exact_row_counts),
        "label8_visible_center8_target_exact_row_counts": _string_row_counts(
            visible_exact_row_counts
        ),
        "covered_endpoint_exact_four_rows": covered_rows,
        "missing_endpoint_exact_four_rows": missing_rows,
        "center8_target_core_auxiliary_center_pair_counts": target_pair_counts,
        "label8_visible_center8_target_core_auxiliary_center_pair_counts": (
            visible_target_pair_counts
        ),
        "current_evidence_forces_center8_target_core": False,
        "label8_visibility_alone_supplies_center8_target": False,
        "gate_status": GATE_STATUS,
        "route_status": ROUTE_STATUS,
    }
    return summary, assignment_records, center8_core_records


def _validate_sources(
    strict_core_split: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
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
            "cascade endpoint-8 target packet",
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

    split_summary = _mapping(
        strict_core_split.get("summary"), "strict-core split summary", errors
    )
    if split_summary.get("split_status") != SOURCE_STRICT_CORE_SPLIT_STATUS_SUMMARY:
        errors.append("strict-core split status mismatch")
    cascade_summary = _mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary", errors
    )
    if cascade_summary.get("target_status") != SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS:
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
        "answer": "do_not_treat_label8_visibility_alone_as_center8_target_supply",
        "gate_status": GATE_STATUS,
        "route_status": ROUTE_STATUS,
        "current_evidence_forces_center8_target_core": False,
        "label8_visibility_alone_supplies_center8_target": False,
        "conditional_obstruction_available_if_target_core_forced": True,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "target-compatible center-8" not in required_next:
        errors.append("decision.required_next_lemma must name the target-compatible core")


def _validate_assignment_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 12:
        errors.append("assignment_route_records must contain 12 records")
        return
    visible_target_assignments = 0
    target_assignments = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"assignment_route_records[{index}] must be an object")
            continue
        if record.get("assignment_index") != index:
            errors.append(f"assignment_route_records[{index}] index mismatch")
        if record.get("has_center8_target_core"):
            target_assignments += 1
        if record.get("has_label8_visible_center8_target_core"):
            visible_target_assignments += 1
    if target_assignments != 6:
        errors.append("expected six assignments with a center-8 target core")
    if visible_target_assignments != 4:
        errors.append("expected four assignments with a visible center-8 target core")


def _validate_center8_core_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 9:
        errors.append("center8_core_records must contain nine records")
        return
    target_count = 0
    visible_target_count = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"center8_core_records[{index}] must be an object")
            continue
        if record.get("center8_target_compatible"):
            target_count += 1
            witnesses = record.get("center8_row_witnesses")
            if not isinstance(witnesses, list) or not _contains(ENDPOINT_TRIPLE, witnesses):
                errors.append(f"center8_core_records[{index}] target witness mismatch")
            if record.get("label8_visible"):
                visible_target_count += 1
    if target_count != 8:
        errors.append("expected eight target-compatible center-8 cores")
    if visible_target_count != 4:
        errors.append("expected four visible target-compatible center-8 cores")


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
        "target_status": summary.get("target_status"),
    }


def _row_for_center(core: Mapping[str, Any], center: int) -> Mapping[str, Any] | None:
    rows = core.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("core rows must be a list")
    for row in rows:
        if not isinstance(row, Mapping):
            raise AssertionError("core row must be an object")
        if int(row["center"]) == center:
            return row
    return None


def _core_rows(core: Mapping[str, Any]) -> list[dict[str, Any]]:
    rows = core.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("core rows must be a list")
    return [
        {"center": int(row["center"]), "witnesses": _int_list(row["witnesses"])}
        for row in rows
        if isinstance(row, Mapping)
    ]


def _contains(needles: Sequence[int], haystack: Sequence[int]) -> bool:
    return set(int(needle) for needle in needles) <= set(int(item) for item in haystack)


def _unique_rows(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    return [list(row) for row in sorted({tuple(row) for row in rows})]


def _row_counts(rows: Sequence[Sequence[int]]) -> dict[tuple[int, ...], int]:
    counts: Counter[tuple[int, ...]] = Counter(tuple(row) for row in rows)
    return {row: int(counts[row]) for row in sorted(counts)}


def _string_row_counts(counts: Mapping[tuple[int, ...], int]) -> dict[str, int]:
    return {",".join(str(label) for label in row): int(count) for row, count in counts.items()}


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
    source_strict_core_split = _resolve(args.source_strict_core_split)
    source_cascade_endpoint8_targets = _resolve(args.source_cascade_endpoint8_targets)
    generated = build_center8_core_route_payload(
        load_artifact(source_strict_core_split),
        load_artifact(source_cascade_endpoint8_targets),
        strict_core_split_path=source_strict_core_split,
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
        strict_core_split_path=source_strict_core_split,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
    )
    if args.assert_expected:
        assert_expected_center8_core_route(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 core route")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade target: {summary['conditional_center8_triple']}")
        print(f"center-8 cores: {summary['center8_core_count']}")
        print(
            "target-compatible center-8 cores: "
            f"{summary['center8_target_compatible_core_count']}"
        )
        print(
            "visible target-compatible cores: "
            f"{summary['label8_visible_center8_target_core_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 core route verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
