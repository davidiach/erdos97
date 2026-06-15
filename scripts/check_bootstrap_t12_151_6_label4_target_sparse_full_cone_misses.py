#!/usr/bin/env python3
"""Check full-row-family cone screens for 151:6 support-cone misses."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

from scipy.optimize import linprog

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402
from erdos97.quotient_cone import StrictRow  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_support_cone import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SUPPORT_CONE,
    GATE_STATUS as SOURCE_GATE_STATUS,
    PROBE_STATUS as SOURCE_PROBE_STATUS,
    SCHEMA as SOURCE_SCHEMA,
    STATUS as SOURCE_STATUS,
    STRICT_ROW_FAMILY,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _distance_quotient,
    _int_list,
    _strict_rows,
    assert_expected_target_sparse_support_cone,
    load_artifact,
    write_json,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_FULL_CONE_MISSES_"
    "DIAGNOSTIC_ONLY"
)
GATE_STATUS = "NOT_READY_FULL_CONE_MISSES_REMAIN_OPEN"
PROBE_STATUS = "TARGET_SPARSE_FULL_CONE_LP_SCREEN_NO_CERTIFICATE_FOR_THREE_MISSES"
LP_SOLVER = "scipy.optimize.linprog(method=highs)"
LP_SCREEN_MODES = [
    "zero_sum_equalities_normalized",
    "nonpositive_inequalities_normalized",
]
EXPECTED_MISSES = [
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 1, 4, 6],
        "endpoint_row_key": "0,1,4,6",
    },
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 2, 4, 6],
        "endpoint_row_key": "0,2,4,6",
    },
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 4, 6, 7],
        "endpoint_row_key": "0,4,6,7",
    },
]
CLAIM_SCOPE = (
    "Proof-mining diagnostic for the three source-151 row-6 label-4 "
    "assignment-0 endpoint rows left uncovered by the bounded support-cone "
    "packet. It reuses the exact selected-distance quotient equalities from "
    "that packet and asks a stronger linear-programming screen over the full "
    "current natural-order Kalmanson/Altman strict-row family: whether any "
    "nonnegative normalized combination gives either an exact zero-sum row "
    "or a nonpositive row. HiGHS reports both screens infeasible for all "
    "three local quotients, but this artifact stores no exact dual "
    "infeasibility certificate. It is therefore a solver diagnostic only; it "
    "does not prove that no current-row-family certificate exists, does not "
    "prove assignments 0 and 11 are impossible, does not prove support "
    "existence, does not prove center migration, does not prove row forcing, "
    "does not prove endpoint-8 forcing, does not prove that pair [3,5] is "
    "impossible, does not prove n=9, does not prove the bootstrap bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "full_cone_probe_records",
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
    "source_support_cone_status": SOURCE_STATUS,
    "source_support_cone_gate_status": SOURCE_GATE_STATUS,
    "source_support_cone_probe_status": SOURCE_PROBE_STATUS,
    "strict_row_family": STRICT_ROW_FAMILY,
    "strict_row_count": 255,
    "lp_solver": LP_SOLVER,
    "lp_screen_modes": LP_SCREEN_MODES,
    "source_endpoint_augmented_probe_count": 30,
    "source_endpoint_augmented_bounded_certificate_count": 27,
    "source_endpoint_augmented_probe_without_certificate_count": 3,
    "full_cone_probe_count": 3,
    "zero_sum_equalities_feasible_count": 0,
    "nonpositive_inequalities_feasible_count": 0,
    "full_cone_solver_certificate_found_count": 0,
    "all_full_cone_lp_screens_report_infeasible": True,
    "all_misses_are_assignment0_source_pair0": True,
    "uncovered_endpoint_rows": [
        [0, 1, 4, 6],
        [0, 2, 4, 6],
        [0, 4, 6, 7],
    ],
    "exact_infeasibility_certificates_stored": False,
    "current_evidence_forces_target_sparse_obstruction": False,
    "gate_status": GATE_STATUS,
    "probe_status": PROBE_STATUS,
}


def build_target_sparse_full_cone_misses_payload(
    source_support_cone: Mapping[str, Any],
    *,
    source_support_cone_path: Path = DEFAULT_SOURCE_SUPPORT_CONE,
) -> dict[str, Any]:
    """Return the deterministic full-cone screen payload for the three misses."""

    errors: list[str] = []
    assert_expected_target_sparse_support_cone(source_support_cone)
    _validate_source(source_support_cone, errors)
    records = _full_cone_records(source_support_cone)
    summary = _summary(source_support_cone, records)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Do the three uncovered assignment-0 endpoint quotients admit "
                "a full nonnegative combination certificate from the current "
                "natural-order Kalmanson/Altman strict-row family?"
            ),
            "answer": (
                "no_solver_certificate_found_and_no_exact_infeasibility_"
                "certificate_stored"
            ),
            "gate_status": GATE_STATUS,
            "probe_status": PROBE_STATUS,
            "current_evidence_forces_target_sparse_obstruction": False,
            "exact_infeasibility_certificates_stored": False,
            "blocking_reason": (
                "Both normalized LP screens report infeasible for all three "
                "misses, but the artifact stores no exact dual certificate. "
                "The current row-family search is therefore pruned only as a "
                "diagnostic, not discharged as an exact nonexistence theorem."
            ),
            "required_next_lemma": (
                "Add exact infeasibility certificates for these LP screens, "
                "enlarge the strict-row family, prove a genuine endpoint-row "
                "source exclusion, or add a new support-geometry condition for "
                "the target-sparse assignments."
            ),
        },
        "full_cone_probe_records": records,
        "source_artifacts": [
            _source_summary(
                source_support_cone_path,
                "source 151:6 label-4 target-sparse support-cone packet",
                source_support_cone,
            )
        ],
        "interpretation": [
            (
                "The bounded support-cone packet left exactly three "
                "assignment-0 endpoint rows; this packet probes those same "
                "three local quotients with arbitrary nonnegative row weights "
                "over the current strict-row family."
            ),
            (
                "HiGHS reports infeasible for both the normalized zero-sum "
                "and normalized nonpositive LP screens on every miss."
            ),
            (
                "Because no exact dual infeasibility certificate is stored, "
                "the result is only a diagnostic route-pruning artifact, not "
                "an exact proof that no current-row-family certificate exists."
            ),
            (
                "The next exact task is to certify these infeasibility screens, "
                "add a stronger row family, or prove a geometric reason the "
                "three endpoint rows cannot occur."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_target_sparse_full_cone_misses(payload)
    return payload


def assert_expected_target_sparse_full_cone_misses(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned target-sparse full-cone miss packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_support_cone_path: Path = DEFAULT_SOURCE_SUPPORT_CONE,
) -> list[str]:
    """Return validation errors for a target-sparse full-cone miss payload."""

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
            "three source-151 row-6 label-4 assignment-0 endpoint rows",
            "HiGHS reports both screens infeasible",
            "stores no exact dual infeasibility certificate",
            "solver diagnostic only",
            "does not prove that no current-row-family certificate exists",
            "does not prove assignments 0 and 11 are impossible",
            "does not prove support existence",
            "does not prove center migration",
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
    _validate_records(payload, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("exact dual infeasibility certificate" in str(item) for item in interpretation):
        errors.append("interpretation must preserve exact-certificate caveat")

    if recompute and not errors:
        generated = build_target_sparse_full_cone_misses_payload(
            load_artifact(source_support_cone_path),
            source_support_cone_path=source_support_cone_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packet")
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
        "full_cone_probe_count": summary.get("full_cone_probe_count"),
        "zero_sum_equalities_feasible_count": summary.get(
            "zero_sum_equalities_feasible_count"
        ),
        "nonpositive_inequalities_feasible_count": summary.get(
            "nonpositive_inequalities_feasible_count"
        ),
        "exact_infeasibility_certificates_stored": summary.get(
            "exact_infeasibility_certificates_stored"
        ),
        "gate_status": summary.get("gate_status"),
        "probe_status": summary.get("probe_status"),
        "validation_errors": list(errors),
    }


def _full_cone_records(
    source_support_cone: Mapping[str, Any],
) -> list[dict[str, Any]]:
    endpoint_records = source_support_cone.get("endpoint_augmented_probe_records")
    if not isinstance(endpoint_records, list):
        raise AssertionError("source endpoint_augmented_probe_records must be a list")
    misses = [
        _required_mapping(record, "endpoint miss")
        for record in endpoint_records
        if isinstance(record, Mapping)
        and not bool(record.get("bounded_certificate_found"))
    ]
    pinned = [
        {
            "assignment_index": int(record["assignment_index"]),
            "source_pair_row_index": int(record["source_pair_row_index"]),
            "source_core_index": int(record["source_core_index"]),
            "row_center": int(record["row_center"]),
            "row_witnesses": _int_list(record["row_witnesses"]),
            "endpoint_center": int(record["endpoint_center"]),
            "endpoint_row_witnesses": _int_list(record["endpoint_row_witnesses"]),
            "endpoint_row_key": str(record["endpoint_row_key"]),
        }
        for record in sorted(
            misses,
            key=lambda item: (
                int(item["assignment_index"]),
                int(item["source_pair_row_index"]),
                _int_list(item["endpoint_row_witnesses"]),
            ),
        )
    ]
    if pinned != EXPECTED_MISSES:
        raise AssertionError("source support-cone misses changed")

    records: list[dict[str, Any]] = []
    for source_record in sorted(
        misses,
        key=lambda item: _int_list(item["endpoint_row_witnesses"]),
    ):
        centered_classes = _centered_classes(source_record)
        quotient = _distance_quotient(9, centered_classes)
        strict_rows = _strict_rows(quotient, list(range(9)))
        zero_sum_screen = _lp_screen(strict_rows, quotient.class_count, "zero_sum")
        nonpositive_screen = _lp_screen(
            strict_rows,
            quotient.class_count,
            "nonpositive",
        )
        records.append(
            {
                "assignment_index": int(source_record["assignment_index"]),
                "source_pair_row_index": int(source_record["source_pair_row_index"]),
                "source_core_index": int(source_record["source_core_index"]),
                "row_center": int(source_record["row_center"]),
                "row_witnesses": _int_list(source_record["row_witnesses"]),
                "endpoint_center": int(source_record["endpoint_center"]),
                "endpoint_row_witnesses": _int_list(
                    source_record["endpoint_row_witnesses"]
                ),
                "endpoint_row_key": str(source_record["endpoint_row_key"]),
                "centered_class_count": len(centered_classes),
                "centered_classes": [
                    {"center": int(center), "witnesses": _int_list(witnesses)}
                    for center, witnesses in centered_classes
                ],
                "distance_class_count": quotient.class_count,
                "strict_row_family": STRICT_ROW_FAMILY,
                "strict_row_count": len(strict_rows),
                "lp_solver": LP_SOLVER,
                "zero_sum_equalities_screen": zero_sum_screen,
                "nonpositive_inequalities_screen": nonpositive_screen,
                "full_cone_solver_certificate_found": (
                    bool(zero_sum_screen["feasible"])
                    or bool(nonpositive_screen["feasible"])
                ),
                "exact_infeasibility_certificate_stored": False,
                "claim_strength": (
                    "Solver-only full-row-family LP screen for this encoded "
                    "quotient input and fixed cyclic order; no exact "
                    "infeasibility certificate is stored."
                ),
            }
        )
    return records


def _summary(
    source_support_cone: Mapping[str, Any],
    records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    source_summary = _required_mapping(
        source_support_cone.get("summary"),
        "source support-cone summary",
    )
    return {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "source_support_cone_status": SOURCE_STATUS,
        "source_support_cone_gate_status": source_summary["gate_status"],
        "source_support_cone_probe_status": source_summary["probe_status"],
        "strict_row_family": STRICT_ROW_FAMILY,
        "strict_row_count": len(_strict_rows(_distance_quotient(9, []), list(range(9)))),
        "lp_solver": LP_SOLVER,
        "lp_screen_modes": LP_SCREEN_MODES,
        "source_endpoint_augmented_probe_count": source_summary[
            "endpoint_augmented_probe_count"
        ],
        "source_endpoint_augmented_bounded_certificate_count": source_summary[
            "endpoint_augmented_bounded_certificate_count"
        ],
        "source_endpoint_augmented_probe_without_certificate_count": source_summary[
            "endpoint_augmented_probe_without_certificate_count"
        ],
        "full_cone_probe_count": len(records),
        "zero_sum_equalities_feasible_count": sum(
            1
            for record in records
            if record["zero_sum_equalities_screen"]["feasible"]
        ),
        "nonpositive_inequalities_feasible_count": sum(
            1
            for record in records
            if record["nonpositive_inequalities_screen"]["feasible"]
        ),
        "full_cone_solver_certificate_found_count": sum(
            1 for record in records if record["full_cone_solver_certificate_found"]
        ),
        "all_full_cone_lp_screens_report_infeasible": all(
            record["zero_sum_equalities_screen"]["normalized_status"]
            == "infeasible_reported_by_highs"
            and record["nonpositive_inequalities_screen"]["normalized_status"]
            == "infeasible_reported_by_highs"
            for record in records
        ),
        "all_misses_are_assignment0_source_pair0": all(
            int(record["assignment_index"]) == 0
            and int(record["source_pair_row_index"]) == 0
            for record in records
        ),
        "uncovered_endpoint_rows": [
            _int_list(record["endpoint_row_witnesses"]) for record in records
        ],
        "exact_infeasibility_certificates_stored": False,
        "current_evidence_forces_target_sparse_obstruction": False,
        "gate_status": GATE_STATUS,
        "probe_status": PROBE_STATUS,
    }


def _lp_screen(
    strict_rows: Sequence[StrictRow],
    distance_class_count: int,
    mode: str,
) -> dict[str, Any]:
    variable_count = len(strict_rows)
    transposed = _transposed_vectors(strict_rows, distance_class_count)
    c = [0.0] * variable_count
    bounds = [(0.0, None)] * variable_count
    if mode == "zero_sum":
        a_eq = [list(row) for row in transposed]
        a_eq.append([1.0] * variable_count)
        b_eq = [0.0] * distance_class_count + [1.0]
        a_ub = None
        b_ub = None
        mode_name = "zero_sum_equalities_normalized"
    elif mode == "nonpositive":
        a_eq = [[1.0] * variable_count]
        b_eq = [1.0]
        a_ub = [list(row) for row in transposed]
        b_ub = [0.0] * distance_class_count
        mode_name = "nonpositive_inequalities_normalized"
    else:  # pragma: no cover - defensive against future callers.
        raise ValueError(f"unknown LP screen mode: {mode}")

    result = linprog(
        c,
        A_ub=a_ub,
        b_ub=b_ub,
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=bounds,
        method="highs",
    )
    payload: dict[str, Any] = {
        "mode": mode_name,
        "solver": LP_SOLVER,
        "normalization": "sum_weights_equals_1",
        "variable_count": variable_count,
        "distance_class_count": distance_class_count,
        "equality_constraint_count": len(a_eq),
        "inequality_constraint_count": 0 if a_ub is None else len(a_ub),
        "feasible": bool(result.success),
        "scipy_status_code": int(result.status),
        "normalized_status": _normalized_status(int(result.status), bool(result.success)),
        "exact_certificate_stored": False,
        "solver_result_is_not_exact_certificate": True,
    }
    if result.success:
        weights = [float(value) for value in result.x]
        combined = [
            sum(weight * row.vector[index] for weight, row in zip(weights, strict_rows))
            for index in range(distance_class_count)
        ]
        payload.update(
            {
                "positive_weight_count": sum(1 for weight in weights if weight > 1e-9),
                "min_combined_coefficient": min(combined),
                "max_combined_coefficient": max(combined),
            }
        )
    return payload


def _transposed_vectors(
    strict_rows: Sequence[StrictRow],
    distance_class_count: int,
) -> list[list[float]]:
    return [
        [float(row.vector[index]) for row in strict_rows]
        for index in range(distance_class_count)
    ]


def _normalized_status(status: int, success: bool) -> str:
    if success:
        return "feasible"
    if status == 2:
        return "infeasible_reported_by_highs"
    if status == 3:
        return "unbounded_reported_by_highs"
    return f"solver_status_{status}"


def _centered_classes(record: Mapping[str, Any]) -> list[tuple[int, list[int]]]:
    classes = record.get("centered_classes")
    if not isinstance(classes, list):
        raise AssertionError("source miss centered_classes must be a list")
    return [
        (
            int(_required_mapping(item, "centered class")["center"]),
            _int_list(_required_mapping(item, "centered class")["witnesses"]),
        )
        for item in classes
    ]


def _validate_source(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("schema") != SOURCE_SCHEMA:
        errors.append("source support-cone schema mismatch")
    if payload.get("status") != SOURCE_STATUS:
        errors.append("source support-cone status mismatch")
    if payload.get("trust") != TRUST:
        errors.append("source support-cone trust mismatch")
    summary = _mapping(payload.get("summary"), "source support-cone summary", errors)
    if summary.get("gate_status") != SOURCE_GATE_STATUS:
        errors.append("source support-cone gate status mismatch")
    if summary.get("probe_status") != SOURCE_PROBE_STATUS:
        errors.append("source support-cone probe status mismatch")
    if summary.get("endpoint_augmented_probe_without_certificate_count") != 3:
        errors.append("source support-cone endpoint miss count mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": (
            "no_solver_certificate_found_and_no_exact_infeasibility_"
            "certificate_stored"
        ),
        "gate_status": GATE_STATUS,
        "probe_status": PROBE_STATUS,
        "current_evidence_forces_target_sparse_obstruction": False,
        "exact_infeasibility_certificates_stored": False,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "exact infeasibility" not in required_next:
        errors.append("decision.required_next_lemma must name exact infeasibility")


def _validate_records(payload: Mapping[str, Any], errors: list[str]) -> None:
    records = payload.get("full_cone_probe_records")
    if not isinstance(records, list):
        errors.append("full_cone_probe_records must be a list")
        return
    if len(records) != EXPECTED_SUMMARY["full_cone_probe_count"]:
        errors.append("full_cone_probe_records length mismatch")
        return

    pinned = []
    for index, raw_record in enumerate(records):
        if not isinstance(raw_record, Mapping):
            errors.append(f"full_cone_probe_records[{index}] must be an object")
            continue
        record = raw_record
        pinned.append(
            {
                "assignment_index": record.get("assignment_index"),
                "source_pair_row_index": record.get("source_pair_row_index"),
                "source_core_index": record.get("source_core_index"),
                "row_center": record.get("row_center"),
                "row_witnesses": record.get("row_witnesses"),
                "endpoint_center": record.get("endpoint_center"),
                "endpoint_row_witnesses": record.get("endpoint_row_witnesses"),
                "endpoint_row_key": record.get("endpoint_row_key"),
            }
        )
        if record.get("centered_class_count") != 4:
            errors.append(f"full_cone_probe_records[{index}] centered class mismatch")
        if record.get("distance_class_count") != 28:
            errors.append(f"full_cone_probe_records[{index}] distance class mismatch")
        if record.get("strict_row_count") != EXPECTED_SUMMARY["strict_row_count"]:
            errors.append(f"full_cone_probe_records[{index}] strict row mismatch")
        for screen_key in (
            "zero_sum_equalities_screen",
            "nonpositive_inequalities_screen",
        ):
            screen = _mapping(record.get(screen_key), screen_key, errors)
            if screen.get("feasible") is not False:
                errors.append(f"{screen_key} must stay infeasible")
            if screen.get("normalized_status") != "infeasible_reported_by_highs":
                errors.append(f"{screen_key} status mismatch")
            if screen.get("exact_certificate_stored") is not False:
                errors.append(f"{screen_key} must not store an exact certificate")
        if record.get("full_cone_solver_certificate_found") is not False:
            errors.append("full-cone solver certificate flag must remain false")
        if record.get("exact_infeasibility_certificate_stored") is not False:
            errors.append("exact infeasibility certificate flag must remain false")

    if pinned != EXPECTED_MISSES:
        errors.append("full_cone_probe_records miss identities changed")


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
        "probe_status": summary.get("probe_status"),
    }


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
        "--source-support-cone",
        type=Path,
        default=DEFAULT_SOURCE_SUPPORT_CONE,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_support_cone = _resolve(args.source_support_cone)
    generated = build_target_sparse_full_cone_misses_payload(
        load_artifact(source_support_cone),
        source_support_cone_path=source_support_cone,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_support_cone_path=source_support_cone,
    )
    if args.assert_expected:
        assert_expected_target_sparse_full_cone_misses(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 target-sparse full-cone misses")
        print(f"target row: {summary['target_row_key']}")
        print(f"full-cone probes: {summary['full_cone_probe_count']}")
        print(
            "zero-sum feasible screens: "
            f"{summary['zero_sum_equalities_feasible_count']}"
        )
        print(
            "nonpositive feasible screens: "
            f"{summary['nonpositive_inequalities_feasible_count']}"
        )
        print(
            "exact infeasibility certificates stored: "
            f"{summary['exact_infeasibility_certificates_stored']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: target-sparse full-cone miss diagnostic verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
