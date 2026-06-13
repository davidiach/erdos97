#!/usr/bin/env python3
"""Check one-completion plus two-repair rows for target-sparse cases."""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97 import (  # noqa: E402
    bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle as full_packet,
)
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
from scripts.check_bootstrap_t12_151_6_label4_center8_target_sparse_two_row_repairs import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_TWO_ROW_REPAIRS,
    GATE_STATUS as SOURCE_TWO_ROW_REPAIR_GATE_STATUS,
    REPAIR_STATUS as SOURCE_TWO_ROW_REPAIR_STATUS,
    SCHEMA as SOURCE_TWO_ROW_REPAIR_SCHEMA,
    STATUS as SOURCE_TWO_ROW_REPAIR_PACKET_STATUS,
    _all_selected_rows_by_center,
    _private_lane_survivors,
    assert_expected_target_sparse_two_row_repairs,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_TARGET_SPARSE_THREE_ROW_REPAIRS_"
    "DIAGNOSTIC_ONLY"
)
GATE_STATUS = "NOT_READY_TARGET_SPARSE_THREE_ROW_REPAIRS_FAIL_BASIC_FILTERS"
REPAIR_STATUS = "TARGET_SPARSE_ONE_COMPLETION_TWO_REPAIRS_ALL_BASIC_FILTER_BLOCKED"
CLAIM_SCOPE = (
    "Proof-mining repair-depth preflight for the source-151 row-6 label-4 "
    "center-8 target-sparse residual cases. It starts from the 12 one-row "
    "target completions for assignments 0 and 11, then allows two additional "
    "non-completion rows to be replaced by any other selected 4-set for those "
    "centers. All 1599696 one-completion plus two-repair candidates fail "
    "basic filters before vertex-circle replay. This does not prove "
    "assignments 0 and 11 are impossible under genuine geometry, does not "
    "prove center migration, does not prove support existence, does not "
    "prove row forcing, does not prove endpoint-8 forcing, does not prove "
    "that pair [3,5] is impossible, does not prove n=9, does not prove the "
    "bootstrap bridge, is not a counterexample, and is not a global status "
    "update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_target_sparse_three_row_repairs.json"
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
EXPECTED_REPAIR_CENTER_PAIR_COUNTS = {
    "0,1": 57132,
    "0,2": 38088,
    "0,3": 47610,
    "0,4": 57132,
    "0,5": 57132,
    "0,6": 57132,
    "0,7": 28566,
    "0,8": 57132,
    "1,2": 38088,
    "1,3": 47610,
    "1,4": 57132,
    "1,5": 57132,
    "1,6": 57132,
    "1,7": 28566,
    "1,8": 57132,
    "2,3": 28566,
    "2,4": 38088,
    "2,5": 38088,
    "2,6": 38088,
    "2,7": 9522,
    "2,8": 38088,
    "3,4": 47610,
    "3,5": 47610,
    "3,6": 47610,
    "3,7": 19044,
    "3,8": 47610,
    "4,5": 57132,
    "4,6": 57132,
    "4,7": 28566,
    "4,8": 57132,
    "5,6": 57132,
    "5,7": 28566,
    "5,8": 57132,
    "6,7": 28566,
    "6,8": 57132,
    "7,8": 28566,
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_completion_gate_status": SOURCE_COMPLETION_GATE_STATUS,
    "source_completion_status": SOURCE_COMPLETION_STATUS,
    "source_two_row_repair_gate_status": SOURCE_TWO_ROW_REPAIR_GATE_STATUS,
    "source_two_row_repair_status": SOURCE_TWO_ROW_REPAIR_STATUS,
    "target_sparse_assignment_indices": [0, 11],
    "source_completion_attempt_count": 12,
    "repair_centers_per_completion": 8,
    "repair_center_pairs_per_completion": 28,
    "candidate_rows_per_repair_center": 69,
    "candidate_row_pairs_per_repair_center_pair": 4761,
    "repair_candidate_count": 1599696,
    "repair_basic_filter_surviving_candidate_count": 0,
    "vertex_circle_checked_repair_candidate_count": 0,
    "repair_records_with_basic_filter_survivor_count": 0,
    "assignment_repair_candidate_counts": {"0": 266616, "11": 1333080},
    "repair_center_pair_counts": EXPECTED_REPAIR_CENTER_PAIR_COUNTS,
    "completion_row_repair_candidate_counts": {
        "0,1,4,6": 533232,
        "0,2,4,6": 133308,
        "0,3,4,6": 133308,
        "0,4,5,6": 133308,
        "0,4,6,7": 133308,
        "0,4,6,8": 533232,
    },
    "missing_target_repair_candidate_counts": {
        "0": 266616,
        "4": 799848,
        "6": 533232,
    },
    "endpoint_exact_row_allowed_repair_candidate_count": 1066464,
    "endpoint_exact_row_disallowed_repair_candidate_count": 533232,
    "failure_attempt_reason_counts": {
        "crossing": 1599696,
        "selected_indegree_cap": 774974,
        "witness_pair_cap": 1597494,
    },
    "failure_detail_counts": {
        "crossing": 13360634,
        "selected_indegree_cap": 873180,
        "witness_pair_cap": 6535699,
    },
    "one_completion_two_repairs_survives_basic_filters": False,
    "current_evidence_forces_target_sparse_obstruction": False,
    "gate_status": GATE_STATUS,
    "repair_status": REPAIR_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_target_sparse_three_row_repairs_payload(
    full_neighborhood: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    source_two_row_repairs: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    source_completions_path: Path = DEFAULT_SOURCE_COMPLETIONS,
    source_two_row_repairs_path: Path = DEFAULT_SOURCE_TWO_ROW_REPAIRS,
) -> dict[str, Any]:
    """Return the deterministic target-sparse depth-two repair payload."""

    errors: list[str] = []
    full_packet.assert_expected_payload(full_neighborhood)
    assert_expected_target_sparse_completions(source_completions)
    assert_expected_target_sparse_two_row_repairs(source_two_row_repairs)
    _validate_sources(full_neighborhood, source_completions, source_two_row_repairs, errors)
    summary, repair_records = _repair_records(full_neighborhood, source_completions)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "After completing one target-pair row to [0,4,6], can two "
                "additional arbitrary selected-row replacements repair the "
                "target-sparse assignment through the basic filters?"
            ),
            "answer": "no_all_one_completion_two_repair_candidates_fail_basic_filters",
            "gate_status": GATE_STATUS,
            "repair_status": REPAIR_STATUS,
            "one_completion_two_repairs_survives_basic_filters": False,
            "current_evidence_forces_target_sparse_obstruction": False,
            "blocking_reason": (
                "Every one-completion plus two-repair candidate still has a "
                "crossing violation; almost all keep witness-pair caps, and "
                "many add selected-indegree cap violations."
            ),
            "required_next_lemma": (
                "Use genuine support geometry to rule out assignments 0 and "
                "11, prove a center-migration mechanism, or find a stronger "
                "mechanism beyond one completion plus two arbitrary repairs."
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
            _source_summary(
                source_two_row_repairs_path,
                "source 151:6 target-sparse one-completion plus one-repair packet",
                source_two_row_repairs,
            ),
        ],
        "interpretation": [
            (
                "The target-sparse cases do not have a one-completion plus "
                "two-repair escape inside the selected-row basic filters."
            ),
            (
                "All 1599696 candidates fail before vertex-circle replay, so "
                "this is still a basic-filter preflight rather than an exact "
                "quotient obstruction."
            ),
            (
                "The result does not rule out genuine support geometry, "
                "center migration, or a different target source."
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
    assert_expected_target_sparse_three_row_repairs(payload)
    return payload


def assert_expected_target_sparse_three_row_repairs(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned target-sparse depth-two repair packet."""

    errors = validate_payload(payload)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(payload: Mapping[str, Any]) -> list[str]:
    """Return validation errors for a target-sparse depth-two repair payload."""

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
            "All 1599696 one-completion plus two-repair candidates fail",
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
    elif not any("support geometry" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the support geometry caveat")
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
        repair_records.append(
            _completion_repair_record(
                source_completion_index,
                completion,
                selected_rows,
                all_rows,
            )
        )

    summary = _summary(repair_records, source_completions)
    return summary, repair_records


def _completion_repair_record(
    source_completion_index: int,
    completion: Mapping[str, Any],
    selected_rows: Mapping[int, Sequence[int]],
    all_rows: Mapping[int, Sequence[tuple[int, ...]]],
) -> dict[str, Any]:
    completion_row_center = int(completion["row_center"])
    repair_center_pair_counts: Counter[str] = Counter()
    failure_attempt_reason_counts: Counter[str] = Counter()
    failure_detail_counts: Counter[str] = Counter()
    vertex_circle_status_counts: Counter[str] = Counter()
    basic_filter_survivor_count = 0
    vertex_circle_checked_count = 0

    repair_centers = [
        center for center in sorted(selected_rows) if center != completion_row_center
    ]
    for first_center, second_center in combinations(repair_centers, 2):
        first_original = tuple(selected_rows[first_center])
        second_original = tuple(selected_rows[second_center])
        for first_row in all_rows[first_center]:
            if first_row == first_original:
                continue
            for second_row in all_rows[second_center]:
                if second_row == second_original:
                    continue
                candidate = dict(selected_rows)
                candidate[first_center] = first_row
                candidate[second_center] = second_row
                violations = _basic_filter_violations(candidate)
                repair_center_pair_counts[f"{first_center},{second_center}"] += 1
                for reason in sorted(
                    {str(violation["type"]) for violation in violations}
                ):
                    failure_attempt_reason_counts[reason] += 1
                for violation in violations:
                    failure_detail_counts[str(violation["type"])] += 1
                if violations:
                    continue
                basic_filter_survivor_count += 1
                vertex_circle_checked_count += 1
                status = vertex_circle_status(
                    {
                        center: full_packet._row_mask(row)
                        for center, row in candidate.items()
                    }
                )
                vertex_circle_status_counts[str(status["status"])] += 1

    candidate_count = sum(repair_center_pair_counts.values())
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
        "repair_center_pair_counts": _json_counter(repair_center_pair_counts),
        "basic_filter_surviving_candidate_count": int(basic_filter_survivor_count),
        "vertex_circle_checked_candidate_count": int(vertex_circle_checked_count),
        "vertex_circle_status_counts": _json_counter(vertex_circle_status_counts),
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
    repair_center_pair_counts: Counter[str] = Counter()

    for record in repair_records:
        failure_attempt_reason_counts.update(record["failure_attempt_reason_counts"])
        failure_detail_counts.update(record["failure_detail_counts"])
        repair_center_pair_counts.update(record["repair_center_pair_counts"])

    candidate_count = sum(
        int(record["repair_candidate_count"]) for record in repair_records
    )
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
        "source_two_row_repair_gate_status": SOURCE_TWO_ROW_REPAIR_GATE_STATUS,
        "source_two_row_repair_status": SOURCE_TWO_ROW_REPAIR_STATUS,
        "target_sparse_assignment_indices": source_summary[
            "target_sparse_assignment_indices"
        ],
        "source_completion_attempt_count": len(repair_records),
        "repair_centers_per_completion": 8,
        "repair_center_pairs_per_completion": 28,
        "candidate_rows_per_repair_center": 69,
        "candidate_row_pairs_per_repair_center_pair": 69 * 69,
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
            Counter(
                str(record["assignment_index"])
                for record in repair_records
                for _ in range(int(record["repair_candidate_count"]))
            )
        ),
        "repair_center_pair_counts": _json_counter(repair_center_pair_counts),
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
        "one_completion_two_repairs_survives_basic_filters": bool(
            basic_filter_survivor_count
        ),
        "current_evidence_forces_target_sparse_obstruction": False,
        "gate_status": GATE_STATUS,
        "repair_status": REPAIR_STATUS,
    }


def _validate_sources(
    full_neighborhood: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    source_two_row_repairs: Mapping[str, Any],
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
    if source_two_row_repairs.get("schema") != SOURCE_TWO_ROW_REPAIR_SCHEMA:
        errors.append("source two-row repair schema mismatch")
    if source_two_row_repairs.get("status") != SOURCE_TWO_ROW_REPAIR_PACKET_STATUS:
        errors.append("source two-row repair status mismatch")
    if source_two_row_repairs.get("trust") != TRUST:
        errors.append("source two-row repair trust mismatch")
    two_row_summary = _mapping(
        source_two_row_repairs.get("summary"), "source two-row repair summary", errors
    )
    if two_row_summary.get("gate_status") != SOURCE_TWO_ROW_REPAIR_GATE_STATUS:
        errors.append("source two-row repair gate status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_all_one_completion_two_repair_candidates_fail_basic_filters",
        "gate_status": GATE_STATUS,
        "repair_status": REPAIR_STATUS,
        "one_completion_two_repairs_survives_basic_filters": False,
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
        if record.get("repair_candidate_count") != 133308:
            errors.append(f"repair_records[{index}] must contain 133308 candidates")
        if record.get("basic_filter_surviving_candidate_count") != 0:
            errors.append(f"repair_records[{index}] must fail basic filters")
        if record.get("vertex_circle_checked_candidate_count") != 0:
            errors.append(f"repair_records[{index}] must not need vertex replay")
        if record.get("vertex_circle_status_counts") != {}:
            errors.append(f"repair_records[{index}] must not record vertex statuses")
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
        "repair_status": summary.get("repair_status"),
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
    parser.add_argument(
        "--source-two-row-repairs",
        type=Path,
        default=DEFAULT_SOURCE_TWO_ROW_REPAIRS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_completions = _resolve(args.source_completions)
    source_two_row_repairs = _resolve(args.source_two_row_repairs)
    generated = build_target_sparse_three_row_repairs_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_completions),
        load_artifact(source_two_row_repairs),
        full_neighborhood_path=source_full_neighborhood,
        source_completions_path=source_completions,
        source_two_row_repairs_path=source_two_row_repairs,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(payload)
    if args.assert_expected:
        assert_expected_target_sparse_three_row_repairs(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 target-sparse three-row repairs")
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
            print("OK: target-sparse three-row repairs verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
