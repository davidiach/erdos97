#!/usr/bin/env python3
"""Check one-completion plus one-repair rows for target-sparse cases."""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97 import (  # noqa: E402
    bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle as full_packet,
)
from erdos97.json_io import write_json  # noqa: E402
from erdos97.n9_vertex_circle_exhaustive import vertex_circle_status  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_center8_target_sparse_completions import (  # noqa: E402
    COMPLETION_STATUS as SOURCE_COMPLETION_STATUS,
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_COMPLETIONS,
    DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    GATE_STATUS as SOURCE_COMPLETION_GATE_STATUS,
    SCHEMA as SOURCE_COMPLETION_SCHEMA,
    STATUS as SOURCE_COMPLETION_PACKET_STATUS,
    _basic_filter_violations,
    assert_expected_target_sparse_completions,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_TARGET_SPARSE_TWO_ROW_REPAIRS_"
    "DIAGNOSTIC_ONLY"
)
GATE_STATUS = "NOT_READY_TARGET_SPARSE_TWO_ROW_REPAIRS_FAIL_BASIC_FILTERS"
REPAIR_STATUS = "TARGET_SPARSE_ONE_COMPLETION_ONE_REPAIR_ALL_BASIC_FILTER_BLOCKED"
CLAIM_SCOPE = (
    "Proof-mining repair-extension preflight for the source-151 row-6 label-4 "
    "center-8 target-sparse residual cases. It starts from the 12 one-row "
    "target completions for assignments 0 and 11, then allows one additional "
    "non-completion row to be replaced by any other selected 4-set for that "
    "center. All 6624 one-completion plus one-repair candidates fail basic "
    "filters before vertex-circle replay. This does not prove assignments 0 "
    "and 11 are impossible under genuine geometry, does not prove center "
    "migration, does not prove support existence, does not prove row forcing, "
    "does not prove endpoint-8 forcing, does not prove that pair [3,5] is "
    "impossible, does not prove n=9, does not prove the bootstrap bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "interpretation",
    "provenance",
    "repair_records",
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
    "source_completion_gate_status": SOURCE_COMPLETION_GATE_STATUS,
    "source_completion_status": SOURCE_COMPLETION_STATUS,
    "target_sparse_assignment_indices": [0, 11],
    "source_completion_attempt_count": 12,
    "repair_centers_per_completion": 8,
    "candidate_rows_per_repair_center": 69,
    "repair_candidate_count": 6624,
    "repair_basic_filter_surviving_candidate_count": 0,
    "vertex_circle_checked_repair_candidate_count": 0,
    "repair_records_with_basic_filter_survivor_count": 0,
    "assignment_repair_candidate_counts": {"0": 1104, "11": 5520},
    "repair_center_counts": {
        "0": 828,
        "1": 828,
        "2": 552,
        "3": 690,
        "4": 828,
        "5": 828,
        "6": 828,
        "7": 414,
        "8": 828,
    },
    "completion_row_repair_candidate_counts": {
        "0,1,4,6": 2208,
        "0,2,4,6": 552,
        "0,3,4,6": 552,
        "0,4,5,6": 552,
        "0,4,6,7": 552,
        "0,4,6,8": 2208,
    },
    "missing_target_repair_candidate_counts": {"0": 1104, "4": 3312, "6": 2208},
    "endpoint_exact_row_allowed_repair_candidate_count": 4416,
    "endpoint_exact_row_disallowed_repair_candidate_count": 2208,
    "failure_attempt_reason_counts": {
        "crossing": 6624,
        "selected_indegree_cap": 1260,
        "witness_pair_cap": 6582,
    },
    "failure_detail_counts": {
        "crossing": 36962,
        "selected_indegree_cap": 1260,
        "witness_pair_cap": 19141,
    },
    "one_completion_one_repair_survives_basic_filters": False,
    "current_evidence_forces_target_sparse_obstruction": False,
    "gate_status": GATE_STATUS,
    "repair_status": REPAIR_STATUS,
}


def build_target_sparse_two_row_repairs_payload(
    full_neighborhood: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    source_completions_path: Path = DEFAULT_SOURCE_COMPLETIONS,
) -> dict[str, Any]:
    """Return the deterministic target-sparse repair-extension payload."""

    errors: list[str] = []
    full_packet.assert_expected_payload(full_neighborhood)
    assert_expected_target_sparse_completions(source_completions)
    _validate_sources(full_neighborhood, source_completions, errors)
    summary, repair_records = _repair_records(full_neighborhood, source_completions)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "After completing one target-pair row to [0,4,6], can one "
                "additional arbitrary selected-row replacement repair the "
                "target-sparse assignment through the basic filters?"
            ),
            "answer": "no_all_one_completion_one_repair_candidates_fail_basic_filters",
            "gate_status": GATE_STATUS,
            "repair_status": REPAIR_STATUS,
            "one_completion_one_repair_survives_basic_filters": False,
            "current_evidence_forces_target_sparse_obstruction": False,
            "blocking_reason": (
                "Every one-completion plus one-repair candidate still has a "
                "crossing violation; most also keep witness-pair caps, and "
                "some add selected-indegree cap violations."
            ),
            "required_next_lemma": (
                "Use genuine support geometry to rule out assignments 0 and "
                "11, prove a center-migration mechanism, or find a stronger "
                "multi-row mechanism beyond one completion plus one repair."
            ),
        },
        "repair_records": repair_records,
        "source_artifacts": [
            _source_summary(
                full_neighborhood_path,
                "source 151:6 outside-pair full-neighborhood packet",
                full_neighborhood,
            ),
            _source_summary(
                source_completions_path,
                "source 151:6 center-8 target-sparse one-row completions",
                source_completions,
            ),
        ],
        "interpretation": [
            (
                "The target-sparse cases do not have a one-completion plus "
                "one-repair escape inside the selected-row basic filters."
            ),
            (
                "All 6624 repair-extension candidates fail before "
                "vertex-circle replay, so this is still a basic-filter "
                "preflight rather than an exact quotient obstruction."
            ),
            (
                "The result does not rule out genuine support geometry, "
                "center migration, or a stronger multi-row mechanism."
            ),
            (
                "This is diagnostic bookkeeping only; it is not row forcing, "
                "support existence, pair impossibility, n=9, or a bridge "
                "proof."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_target_sparse_two_row_repairs(payload)
    return payload


def assert_expected_target_sparse_two_row_repairs(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned target-sparse two-row repair packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    source_completions_path: Path = DEFAULT_SOURCE_COMPLETIONS,
) -> list[str]:
    """Return validation errors for a target-sparse repair payload."""

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
            "assignments 0 and 11",
            "All 6624 one-completion plus one-repair candidates fail",
            "does not prove assignments 0 and 11 are impossible",
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
    records = payload.get("repair_records")
    if not isinstance(records, list):
        errors.append("repair_records must be a list")
    else:
        _validate_repair_records(records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("stronger multi-row" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the stronger multi-row caveat")

    if recompute and not errors:
        generated = build_target_sparse_two_row_repairs_payload(
            load_artifact(full_neighborhood_path),
            load_artifact(source_completions_path),
            full_neighborhood_path=full_neighborhood_path,
            source_completions_path=source_completions_path,
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
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "source_completion_attempt_count": summary.get(
            "source_completion_attempt_count"
        ),
        "repair_candidate_count": summary.get("repair_candidate_count"),
        "repair_basic_filter_surviving_candidate_count": summary.get(
            "repair_basic_filter_surviving_candidate_count"
        ),
        "failure_attempt_reason_counts": summary.get(
            "failure_attempt_reason_counts"
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _repair_records(
    full_neighborhood: Mapping[str, Any],
    source_completions: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    private_survivors = _private_lane_survivors(full_neighborhood)
    source_records = _required_list(
        source_completions.get("completion_records"),
        "source completion records",
    )
    all_rows = _all_selected_rows_by_center()

    repair_records: list[dict[str, Any]] = []
    for source_completion_index, raw_completion in enumerate(source_records):
        completion = _required_mapping(raw_completion, "source completion")
        assignment_index = int(completion["assignment_index"])
        selected_rows = {
            int(center): tuple(_int_list(row))
            for center, row in _required_mapping(
                private_survivors[assignment_index].get("selected_rows"),
                "source selected rows",
            ).items()
        }
        completion_row_center = int(completion["row_center"])
        selected_rows[completion_row_center] = tuple(
            _int_list(completion["completion_row_witnesses"])
        )
        repair_record = _completion_repair_record(
            source_completion_index,
            completion,
            selected_rows,
            all_rows,
        )
        repair_records.append(repair_record)

    summary = _summary(repair_records, source_completions)
    return summary, repair_records


def _completion_repair_record(
    source_completion_index: int,
    completion: Mapping[str, Any],
    selected_rows: Mapping[int, Sequence[int]],
    all_rows: Mapping[int, Sequence[tuple[int, ...]]],
) -> dict[str, Any]:
    completion_row_center = int(completion["row_center"])
    failure_attempt_reason_counts: Counter[str] = Counter()
    failure_detail_counts: Counter[str] = Counter()
    repair_center_counts: Counter[str] = Counter()
    basic_filter_survivor_count = 0
    vertex_circle_checked_count = 0

    for repair_center in sorted(selected_rows):
        if repair_center == completion_row_center:
            continue
        original_row = tuple(selected_rows[repair_center])
        for repair_row in all_rows[repair_center]:
            if repair_row == original_row:
                continue
            candidate = dict(selected_rows)
            candidate[repair_center] = repair_row
            violations = _basic_filter_violations(candidate)
            repair_center_counts[str(repair_center)] += 1
            for reason in sorted({str(violation["type"]) for violation in violations}):
                failure_attempt_reason_counts[reason] += 1
            for violation in violations:
                failure_detail_counts[str(violation["type"])] += 1
            if violations:
                continue
            basic_filter_survivor_count += 1
            vertex_circle_checked_count += 1
            vertex_circle_status(
                {
                    center: full_packet._row_mask(row)
                    for center, row in candidate.items()
                }
            )

    candidate_count = sum(repair_center_counts.values())
    return {
        "source_completion_index": source_completion_index,
        "assignment_index": int(completion["assignment_index"]),
        "source_pair_row_index": int(completion["source_pair_row_index"]),
        "source_core_index": int(completion["source_core_index"]),
        "completion_row_center": completion_row_center,
        "completion_row_witnesses": _int_list(
            completion["completion_row_witnesses"]
        ),
        "completion_row_key": str(completion["completion_row_key"]),
        "completion_missing_target_label": int(completion["missing_target_label"]),
        "completion_replaced_label": int(completion["replaced_label"]),
        "completion_endpoint_exact_row_allowed": bool(
            completion["completion_endpoint_exact_row_allowed"]
        ),
        "repair_candidate_count": int(candidate_count),
        "repair_center_counts": _json_counter(repair_center_counts),
        "basic_filter_surviving_candidate_count": int(basic_filter_survivor_count),
        "vertex_circle_checked_candidate_count": int(vertex_circle_checked_count),
        "failure_attempt_reason_counts": _json_counter(
            failure_attempt_reason_counts
        ),
        "failure_detail_counts": _json_counter(failure_detail_counts),
        "all_repair_candidates_fail_basic_filters": basic_filter_survivor_count == 0,
    }


def _summary(
    repair_records: Sequence[Mapping[str, Any]],
    source_completions: Mapping[str, Any],
) -> dict[str, Any]:
    source_summary = _required_mapping(
        source_completions.get("summary"), "source completion summary"
    )
    failure_attempt_reason_counts: Counter[str] = Counter()
    failure_detail_counts: Counter[str] = Counter()
    repair_center_counts: Counter[str] = Counter()

    for record in repair_records:
        failure_attempt_reason_counts.update(record["failure_attempt_reason_counts"])
        failure_detail_counts.update(record["failure_detail_counts"])
        repair_center_counts.update(record["repair_center_counts"])

    candidate_count = sum(int(record["repair_candidate_count"]) for record in repair_records)
    basic_filter_survivor_count = sum(
        int(record["basic_filter_surviving_candidate_count"])
        for record in repair_records
    )
    vertex_circle_checked_count = sum(
        int(record["vertex_circle_checked_candidate_count"])
        for record in repair_records
    )
    return {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_completion_gate_status": source_summary["gate_status"],
        "source_completion_status": source_summary["completion_status"],
        "target_sparse_assignment_indices": source_summary[
            "target_sparse_assignment_indices"
        ],
        "source_completion_attempt_count": len(repair_records),
        "repair_centers_per_completion": 8,
        "candidate_rows_per_repair_center": 69,
        "repair_candidate_count": int(candidate_count),
        "repair_basic_filter_surviving_candidate_count": int(
            basic_filter_survivor_count
        ),
        "vertex_circle_checked_repair_candidate_count": int(
            vertex_circle_checked_count
        ),
        "repair_records_with_basic_filter_survivor_count": sum(
            1
            for record in repair_records
            if record["basic_filter_surviving_candidate_count"]
        ),
        "assignment_repair_candidate_counts": _json_counter(
            Counter(str(record["assignment_index"]) for record in repair_records for _ in range(int(record["repair_candidate_count"])))
        ),
        "repair_center_counts": _json_counter(repair_center_counts),
        "completion_row_repair_candidate_counts": _json_counter(
            Counter(
                str(record["completion_row_key"])
                for record in repair_records
                for _ in range(int(record["repair_candidate_count"]))
            )
        ),
        "missing_target_repair_candidate_counts": _json_counter(
            Counter(
                str(record["completion_missing_target_label"])
                for record in repair_records
                for _ in range(int(record["repair_candidate_count"]))
            )
        ),
        "endpoint_exact_row_allowed_repair_candidate_count": sum(
            int(record["repair_candidate_count"])
            for record in repair_records
            if record["completion_endpoint_exact_row_allowed"]
        ),
        "endpoint_exact_row_disallowed_repair_candidate_count": sum(
            int(record["repair_candidate_count"])
            for record in repair_records
            if not record["completion_endpoint_exact_row_allowed"]
        ),
        "failure_attempt_reason_counts": _json_counter(
            failure_attempt_reason_counts
        ),
        "failure_detail_counts": _json_counter(failure_detail_counts),
        "one_completion_one_repair_survives_basic_filters": bool(
            basic_filter_survivor_count
        ),
        "current_evidence_forces_target_sparse_obstruction": False,
        "gate_status": GATE_STATUS,
        "repair_status": REPAIR_STATUS,
    }


def _validate_sources(
    full_neighborhood: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    errors: list[str],
) -> None:
    if full_neighborhood.get("schema") != full_packet.SCHEMA:
        errors.append("full-neighborhood source schema mismatch")
    if full_neighborhood.get("status") != full_packet.STATUS:
        errors.append("full-neighborhood source status mismatch")
    if full_neighborhood.get("trust") != TRUST:
        errors.append("full-neighborhood source trust mismatch")
    if source_completions.get("schema") != SOURCE_COMPLETION_SCHEMA:
        errors.append("source completion schema mismatch")
    if source_completions.get("status") != SOURCE_COMPLETION_PACKET_STATUS:
        errors.append("source completion status mismatch")
    if source_completions.get("trust") != TRUST:
        errors.append("source completion trust mismatch")
    completion_summary = _mapping(
        source_completions.get("summary"), "source completion summary", errors
    )
    if completion_summary.get("gate_status") != SOURCE_COMPLETION_GATE_STATUS:
        errors.append("source completion gate status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_all_one_completion_one_repair_candidates_fail_basic_filters",
        "gate_status": GATE_STATUS,
        "repair_status": REPAIR_STATUS,
        "one_completion_one_repair_survives_basic_filters": False,
        "current_evidence_forces_target_sparse_obstruction": False,
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


def _validate_repair_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 12:
        errors.append("repair_records must contain twelve records")
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"repair_records[{index}] must be an object")
            continue
        if record.get("source_completion_index") != index:
            errors.append(f"repair_records[{index}] source index mismatch")
        if record.get("assignment_index") not in (0, 11):
            errors.append(f"repair_records[{index}] assignment index mismatch")
        if record.get("repair_candidate_count") != 552:
            errors.append(f"repair_records[{index}] must contain 552 candidates")
        if record.get("basic_filter_surviving_candidate_count") != 0:
            errors.append(f"repair_records[{index}] must fail basic filters")
        if record.get("vertex_circle_checked_candidate_count") != 0:
            errors.append(f"repair_records[{index}] must not need vertex replay")
        reasons = set(
            _required_mapping(
                record.get("failure_attempt_reason_counts"),
                "failure attempt reasons",
            )
        )
        if "crossing" not in reasons:
            errors.append(f"repair_records[{index}] must include crossing failures")


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
        "scan_status": summary.get("scan_status"),
        "gate_status": summary.get("gate_status"),
        "completion_status": summary.get("completion_status"),
    }


def _private_lane_survivors(full_neighborhood: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    per_target = _required_list(
        full_neighborhood.get("per_target_center_class"),
        "full-neighborhood per-target records",
    )
    matches = [
        record
        for record in per_target
        if isinstance(record, Mapping)
        and record.get("target_center_class") == PRIVATE_TARGET_CLASS
    ]
    if len(matches) != 1:
        raise AssertionError("expected one private target-center class record")
    survivors = _required_list(matches[0].get("basic_filter_survivors"), "survivors")
    if len(survivors) != 12:
        raise AssertionError("expected twelve private-lane survivors")
    return [_required_mapping(survivor, "private survivor") for survivor in survivors]


def _all_selected_rows_by_center() -> dict[int, list[tuple[int, ...]]]:
    return {
        center: [
            tuple(int(item) for item in row)
            for row in combinations(
                [witness for witness in range(9) if witness != center],
                4,
            )
        ]
        for center in range(9)
    }


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
        "--source-full-neighborhood",
        type=Path,
        default=DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    )
    parser.add_argument(
        "--source-completions",
        type=Path,
        default=DEFAULT_SOURCE_COMPLETIONS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_completions = _resolve(args.source_completions)
    generated = build_target_sparse_two_row_repairs_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_completions),
        full_neighborhood_path=source_full_neighborhood,
        source_completions_path=source_completions,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        full_neighborhood_path=source_full_neighborhood,
        source_completions_path=source_completions,
    )
    if args.assert_expected:
        assert_expected_target_sparse_two_row_repairs(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 target-sparse two-row repairs")
        print(f"target row: {summary['target_row_key']}")
        print(
            "target-sparse assignments: "
            f"{summary['target_sparse_assignment_indices']}"
        )
        print(
            "source completions: "
            f"{summary['source_completion_attempt_count']}"
        )
        print(f"repair candidates: {summary['repair_candidate_count']}")
        print(
            "basic-filter survivors: "
            f"{summary['repair_basic_filter_surviving_candidate_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: target-sparse two-row repairs verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
