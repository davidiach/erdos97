#!/usr/bin/env python3
"""Check one-row completions for target-sparse center-8 residual cases."""

from __future__ import annotations

import argparse
from collections import Counter
import itertools
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
from erdos97.n9_vertex_circle_exhaustive import (  # noqa: E402
    MAX_INDEGREE,
    PAIR_CAP,
    MASK_BITS,
    rows_compatible,
    vertex_circle_status,
)
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    EXACT_FOUR_ENDPOINT_ROWS,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_residual_target_rows import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS as SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS,
    SCHEMA as SOURCE_RESIDUAL_TARGET_ROWS_SCHEMA,
    STATUS as SOURCE_RESIDUAL_TARGET_ROWS_STATUS,
    assert_expected_center8_residual_target_rows,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)
from scripts.check_bootstrap_t12_151_6_private_lane_strict_core_split import (  # noqa: E402
    load_artifact,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_target_sparse_completions.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_TARGET_SPARSE_COMPLETIONS_"
    "DIAGNOSTIC_ONLY"
)
GATE_STATUS = "NOT_READY_TARGET_SPARSE_ONE_ROW_COMPLETIONS_FAIL_BASIC_FILTERS"
COMPLETION_STATUS = "TARGET_SPARSE_ONE_ROW_COMPLETIONS_ALL_BASIC_FILTER_BLOCKED"
CLAIM_SCOPE = (
    "Proof-mining completion preflight for the source-151 row-6 label-4 "
    "center-8 target-sparse residual cases. It takes assignments 0 and 11 "
    "from the residual target-row packet, enumerates every one-row replacement "
    "that completes a target-pair row to contain [0,4,6], and checks the "
    "resulting complete selected-row assignments against the same basic "
    "incidence, witness-pair, crossing, and cap filters used by the "
    "full-neighborhood packet. All 12 one-row completions fail basic filters "
    "before vertex-circle replay. This does not prove support existence, does "
    "not prove row forcing, does not prove center migration, does not prove "
    "endpoint-8 forcing, does not prove that assignments 0 and 11 are "
    "impossible under genuine geometry, does not prove that pair [3,5] is "
    "impossible, does not prove n=9, does not prove the bootstrap bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_completions.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_center8_target_sparse_completions.py "
        "--write --assert-expected"
    ),
}

DEFAULT_SOURCE_FULL_NEIGHBORHOOD = full_packet.DEFAULT_ARTIFACT
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_target_sparse_completions.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "completion_records",
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
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
    "source_residual_gate_status": SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS,
    "target_sparse_assignment_indices": [0, 11],
    "target_sparse_pair_row_count": 6,
    "completion_attempt_count": 12,
    "generated_valid_completion_count": 12,
    "basic_filter_surviving_completion_count": 0,
    "vertex_circle_checked_completion_count": 0,
    "completion_assignment_counts": {"0": 2, "11": 10},
    "completion_row_center_counts": {"2": 4, "3": 2, "7": 6},
    "completion_missing_target_counts": {"0": 2, "4": 6, "6": 4},
    "completion_exact_row_counts": {
        "0,1,4,6": 4,
        "0,2,4,6": 1,
        "0,3,4,6": 1,
        "0,4,5,6": 1,
        "0,4,6,7": 1,
        "0,4,6,8": 4,
    },
    "endpoint_exact_row_allowed_completion_count": 8,
    "endpoint_exact_row_disallowed_completion_count": 4,
    "failure_attempt_reason_counts": {
        "crossing": 12,
        "witness_pair_cap": 12,
    },
    "failure_detail_counts": {
        "crossing": 29,
        "witness_pair_cap": 13,
    },
    "one_row_completions_survive_basic_filters": False,
    "current_evidence_forces_target_sparse_obstruction": False,
    "gate_status": GATE_STATUS,
    "completion_status": COMPLETION_STATUS,
}


def build_target_sparse_completions_payload(
    full_neighborhood: Mapping[str, Any],
    residual_target_rows: Mapping[str, Any],
    *,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
) -> dict[str, Any]:
    """Return the deterministic target-sparse one-row completion payload."""

    errors: list[str] = []
    full_packet.assert_expected_payload(full_neighborhood)
    assert_expected_center8_residual_target_rows(residual_target_rows)
    _validate_sources(full_neighborhood, residual_target_rows, errors)
    summary, completion_records = _completion_records(
        full_neighborhood, residual_target_rows
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Can either target-sparse residual assignment be repaired by "
                "one row replacement completing a target-pair row to [0,4,6]?"
            ),
            "answer": "no_all_one_row_completions_fail_basic_filters",
            "gate_status": GATE_STATUS,
            "completion_status": COMPLETION_STATUS,
            "one_row_completions_survive_basic_filters": False,
            "current_evidence_forces_target_sparse_obstruction": False,
            "blocking_reason": (
                "Every one-row completion violates witness-pair caps and "
                "crossing compatibility in the fixed target-sparse assignment."
            ),
            "required_next_lemma": (
                "Use genuine support geometry to rule out assignments 0 and "
                "11, or prove a stronger multi-row completion/center-migration "
                "mechanism beyond these one-row completions."
            ),
        },
        "completion_records": completion_records,
        "source_artifacts": [
            _source_summary(
                full_neighborhood_path,
                "source 151:6 outside-pair full-neighborhood packet",
                full_neighborhood,
            ),
            _source_summary(
                residual_target_rows_path,
                "source 151:6 center-8 residual target rows",
                residual_target_rows,
            ),
        ],
        "interpretation": [
            (
                "Assignments 0 and 11 cannot be repaired by completing a "
                "single target-pair row inside the fixed selected-row "
                "assignment."
            ),
            (
                "All 12 one-row completions fail before vertex-circle replay, "
                "so this packet is a basic-filter preflight rather than an "
                "exact quotient obstruction."
            ),
            (
                "The result does not rule out genuine multi-row support "
                "geometry, center migration, or a different target source."
            ),
            (
                "This is still diagnostic bookkeeping only; it is not row "
                "forcing, support existence, pair impossibility, n=9, or a "
                "bridge proof."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_target_sparse_completions(payload)
    return payload


def assert_expected_target_sparse_completions(payload: Mapping[str, Any]) -> None:
    """Assert the pinned target-sparse completion packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    full_neighborhood_path: Path = DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
) -> list[str]:
    """Return validation errors for a target-sparse completion payload."""

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
            "All 12 one-row completions fail basic filters",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove center migration",
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
    records = payload.get("completion_records")
    if not isinstance(records, list):
        errors.append("completion_records must be a list")
    else:
        _validate_completion_records(records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("multi-row support geometry" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the multi-row caveat")

    if recompute and not errors:
        generated = build_target_sparse_completions_payload(
            load_artifact(full_neighborhood_path),
            load_artifact(residual_target_rows_path),
            full_neighborhood_path=full_neighborhood_path,
            residual_target_rows_path=residual_target_rows_path,
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
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "completion_attempt_count": summary.get("completion_attempt_count"),
        "basic_filter_surviving_completion_count": summary.get(
            "basic_filter_surviving_completion_count"
        ),
        "failure_attempt_reason_counts": summary.get(
            "failure_attempt_reason_counts"
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _completion_records(
    full_neighborhood: Mapping[str, Any],
    residual_target_rows: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    private_survivors = _private_lane_survivors(full_neighborhood)
    target_sparse_records = _required_list(
        residual_target_rows.get("target_sparse_assignment_records"),
        "target-sparse assignment records",
    )

    completion_records: list[dict[str, Any]] = []
    for raw_sparse in target_sparse_records:
        if not isinstance(raw_sparse, Mapping):
            raise AssertionError("target-sparse records must be objects")
        assignment_index = int(raw_sparse["assignment_index"])
        selected_rows = {
            int(center): tuple(_int_list(row))
            for center, row in _required_mapping(
                private_survivors[assignment_index].get("selected_rows"),
                "source selected rows",
            ).items()
        }
        pair_rows = _required_list(raw_sparse.get("target_pair_rows"), "pair rows")
        for pair_row_index, raw_pair_row in enumerate(pair_rows):
            if not isinstance(raw_pair_row, Mapping):
                raise AssertionError("target pair rows must be objects")
            row_center = int(raw_pair_row["row_center"])
            source_row = tuple(_int_list(raw_pair_row["row_witnesses"]))
            overlap = tuple(_int_list(raw_pair_row["target_overlap"]))
            missing = sorted(set(ENDPOINT_TRIPLE) - set(overlap))
            if len(missing) != 1:
                raise AssertionError("target-sparse pair row must miss one label")
            missing_label = missing[0]
            replaceable = [label for label in source_row if label not in ENDPOINT_TRIPLE]
            for replaced_label in replaceable:
                completion_row = tuple(
                    sorted((set(source_row) - {replaced_label}) | {missing_label})
                )
                assigned = dict(selected_rows)
                assigned[row_center] = completion_row
                violations = _basic_filter_violations(assigned)
                failure_reason_types = sorted({violation["type"] for violation in violations})
                basic_filter_ok = not violations
                vertex_status = (
                    vertex_circle_status(
                        {
                            center: full_packet._row_mask(row)
                            for center, row in assigned.items()
                        }
                    )
                    if basic_filter_ok
                    else None
                )
                completion_records.append(
                    {
                        "assignment_index": assignment_index,
                        "source_pair_row_index": pair_row_index,
                        "source_core_index": int(raw_pair_row["core_index"]),
                        "row_center": row_center,
                        "source_row_witnesses": list(source_row),
                        "source_target_overlap": list(overlap),
                        "missing_target_label": missing_label,
                        "replaced_label": int(replaced_label),
                        "completion_row_witnesses": list(completion_row),
                        "completion_row_key": _row_key(completion_row),
                        "completion_contains_center": row_center in completion_row,
                        "completion_valid_4set": (
                            len(completion_row) == 4
                            and row_center not in completion_row
                        ),
                        "completion_endpoint_exact_row_allowed": list(completion_row)
                        in EXACT_FOUR_ENDPOINT_ROWS,
                        "basic_filter_ok": basic_filter_ok,
                        "vertex_circle_status": vertex_status,
                        "failure_reason_types": failure_reason_types,
                        "failure_violations": violations,
                    }
                )

    summary = _summary(completion_records, residual_target_rows)
    return summary, completion_records


def _summary(
    completion_records: Sequence[Mapping[str, Any]],
    residual_target_rows: Mapping[str, Any],
) -> dict[str, Any]:
    residual_summary = _required_mapping(
        residual_target_rows.get("summary"), "residual target-row summary"
    )
    failure_attempt_reason_counts: Counter[str] = Counter()
    failure_detail_counts: Counter[str] = Counter()
    for record in completion_records:
        for reason in record["failure_reason_types"]:
            failure_attempt_reason_counts[str(reason)] += 1
        for violation in record["failure_violations"]:
            failure_detail_counts[str(violation["type"])] += 1

    basic_ok = [record for record in completion_records if record["basic_filter_ok"]]
    return {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": ENDPOINT_CENTER,
        "conditional_center8_triple": ENDPOINT_TRIPLE,
        "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
        "source_residual_gate_status": residual_summary["gate_status"],
        "target_sparse_assignment_indices": residual_summary[
            "target_sparse_assignment_indices"
        ],
        "target_sparse_pair_row_count": int(
            residual_summary["target_sparse_pair_row_occurrence_count"]
        ),
        "completion_attempt_count": len(completion_records),
        "generated_valid_completion_count": sum(
            1 for record in completion_records if record["completion_valid_4set"]
        ),
        "basic_filter_surviving_completion_count": len(basic_ok),
        "vertex_circle_checked_completion_count": sum(
            1 for record in completion_records if record["vertex_circle_status"]
        ),
        "completion_assignment_counts": _json_counter(
            Counter(str(record["assignment_index"]) for record in completion_records)
        ),
        "completion_row_center_counts": _json_counter(
            Counter(str(record["row_center"]) for record in completion_records)
        ),
        "completion_missing_target_counts": _json_counter(
            Counter(str(record["missing_target_label"]) for record in completion_records)
        ),
        "completion_exact_row_counts": _json_counter(
            Counter(str(record["completion_row_key"]) for record in completion_records)
        ),
        "endpoint_exact_row_allowed_completion_count": sum(
            1
            for record in completion_records
            if record["completion_endpoint_exact_row_allowed"]
        ),
        "endpoint_exact_row_disallowed_completion_count": sum(
            1
            for record in completion_records
            if not record["completion_endpoint_exact_row_allowed"]
        ),
        "failure_attempt_reason_counts": _json_counter(
            failure_attempt_reason_counts
        ),
        "failure_detail_counts": _json_counter(failure_detail_counts),
        "one_row_completions_survive_basic_filters": bool(basic_ok),
        "current_evidence_forces_target_sparse_obstruction": False,
        "gate_status": GATE_STATUS,
        "completion_status": COMPLETION_STATUS,
    }


def _basic_filter_violations(
    assigned_rows: Mapping[int, Sequence[int]],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    column_counts: Counter[int] = Counter()
    pair_counts: Counter[tuple[int, int]] = Counter()
    row_masks = {
        int(center): full_packet._row_mask(row)
        for center, row in assigned_rows.items()
    }

    for center, row in sorted(assigned_rows.items()):
        if int(center) in row:
            violations.append(
                {
                    "type": "center_in_row",
                    "center": int(center),
                    "row": list(row),
                }
            )
        for witness in row:
            column_counts[int(witness)] += 1
        for pair in itertools.combinations(sorted(int(item) for item in row), 2):
            pair_counts[pair] += 1

    for witness, count in sorted(column_counts.items()):
        if count > MAX_INDEGREE:
            violations.append(
                {
                    "type": "selected_indegree_cap",
                    "witness": int(witness),
                    "count": int(count),
                    "cap": MAX_INDEGREE,
                }
            )
    for pair, count in sorted(pair_counts.items()):
        if count > PAIR_CAP:
            violations.append(
                {
                    "type": "witness_pair_cap",
                    "pair": list(pair),
                    "count": int(count),
                    "cap": PAIR_CAP,
                }
            )

    centers = sorted(row_masks)
    for left_index, left_center in enumerate(centers):
        for right_center in centers[left_index + 1 :]:
            if rows_compatible(
                left_center,
                row_masks[left_center],
                right_center,
                row_masks[right_center],
            ):
                continue
            violations.append(
                {
                    "type": "crossing",
                    "left_center": int(left_center),
                    "left_row": _mask_to_row(row_masks[left_center]),
                    "right_center": int(right_center),
                    "right_row": _mask_to_row(row_masks[right_center]),
                }
            )
    return violations


def _validate_sources(
    full_neighborhood: Mapping[str, Any],
    residual_target_rows: Mapping[str, Any],
    errors: list[str],
) -> None:
    if full_neighborhood.get("schema") != full_packet.SCHEMA:
        errors.append("full-neighborhood source schema mismatch")
    if full_neighborhood.get("status") != full_packet.STATUS:
        errors.append("full-neighborhood source status mismatch")
    if full_neighborhood.get("trust") != TRUST:
        errors.append("full-neighborhood source trust mismatch")
    full_summary = _mapping(
        full_neighborhood.get("summary"), "full-neighborhood summary", errors
    )
    if full_summary.get("scan_status") != full_packet.SCAN_STATUS:
        errors.append("full-neighborhood source scan status mismatch")

    if residual_target_rows.get("schema") != SOURCE_RESIDUAL_TARGET_ROWS_SCHEMA:
        errors.append("residual target-row source schema mismatch")
    if residual_target_rows.get("status") != SOURCE_RESIDUAL_TARGET_ROWS_STATUS:
        errors.append("residual target-row source status mismatch")
    if residual_target_rows.get("trust") != TRUST:
        errors.append("residual target-row source trust mismatch")
    residual_summary = _mapping(
        residual_target_rows.get("summary"), "residual target-row summary", errors
    )
    if residual_summary.get("gate_status") != SOURCE_RESIDUAL_TARGET_ROWS_GATE_STATUS:
        errors.append("residual target-row source gate status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_all_one_row_completions_fail_basic_filters",
        "gate_status": GATE_STATUS,
        "completion_status": COMPLETION_STATUS,
        "one_row_completions_survive_basic_filters": False,
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


def _validate_completion_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 12:
        errors.append("completion_records must contain twelve records")
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"completion_records[{index}] must be an object")
            continue
        if record.get("assignment_index") not in (0, 11):
            errors.append(f"completion_records[{index}] assignment index mismatch")
        if record.get("basic_filter_ok") is not False:
            errors.append(f"completion_records[{index}] must fail basic filters")
        reasons = set(record.get("failure_reason_types", []))
        if reasons != {"crossing", "witness_pair_cap"}:
            errors.append(f"completion_records[{index}] reason mismatch: {reasons!r}")
        witnesses = record.get("completion_row_witnesses")
        if not isinstance(witnesses, list) or not _contains(ENDPOINT_TRIPLE, witnesses):
            errors.append(f"completion_records[{index}] completion witness mismatch")


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


def _mask_to_row(row_mask: int) -> list[int]:
    return [int(item) for item in MASK_BITS[row_mask]]


def _contains(needles: Sequence[int], haystack: Sequence[int]) -> bool:
    return set(int(needle) for needle in needles) <= set(int(item) for item in haystack)


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
        "--source-full-neighborhood",
        type=Path,
        default=DEFAULT_SOURCE_FULL_NEIGHBORHOOD,
    )
    parser.add_argument(
        "--source-residual-target-rows",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_full_neighborhood = _resolve(args.source_full_neighborhood)
    source_residual_target_rows = _resolve(args.source_residual_target_rows)
    generated = build_target_sparse_completions_payload(
        load_artifact(source_full_neighborhood),
        load_artifact(source_residual_target_rows),
        full_neighborhood_path=source_full_neighborhood,
        residual_target_rows_path=source_residual_target_rows,
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
        residual_target_rows_path=source_residual_target_rows,
    )
    if args.assert_expected:
        assert_expected_target_sparse_completions(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 target-sparse completions")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade target: {summary['conditional_center8_triple']}")
        print(
            "target-sparse assignments: "
            f"{summary['target_sparse_assignment_indices']}"
        )
        print(f"completion attempts: {summary['completion_attempt_count']}")
        print(
            "basic-filter survivors: "
            f"{summary['basic_filter_surviving_completion_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: target-sparse one-row completions verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
