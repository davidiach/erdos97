#!/usr/bin/env python3
"""Validate the n=9 selected-baseline D=3 escape-class crosswalk artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_selected_baseline_d3_escape_class_crosswalk import (  # noqa: E402
    selected_baseline_d3_escape_class_crosswalk_report,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_selected_baseline_d3_escape_class_crosswalk.json"
)
MAX_COMPARISON_ERRORS = 20
EXPECTED_SCHEMA = "erdos97.n9_selected_baseline_d3_escape_class_crosswalk.v1"
EXPECTED_STATUS = "EXPLORATORY_LEDGER_ONLY"
EXPECTED_TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 selected-baseline D=3 escape-class crosswalk bookkeeping; "
    "not a proof of n=9, not a counterexample, not an incidence-completeness "
    "result, not a geometric realizability test, and not a global status update."
)
EXPECTED_SOURCE_ARTIFACTS = {
    "pre_vertex_circle_assignments": "data/certificates/n9_vertex_circle_exhaustive.json",
    "selected_baseline_overlay": (
        "data/certificates/n9_selected_baseline_escape_budget_overlay.json"
    ),
    "d3_escape_slice": "data/certificates/n9_base_apex_d3_escape_slice.json",
    "low_excess_escape_crosswalk": (
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json"
    ),
}
EXPECTED_INTERPRETATION = [
    "Rows join selected-baseline relevant-deficit classes Bxx to strict r=3 escape classes Xyy.",
    "Budget-3 choices are three selected-baseline empty capacity slots per pre-vertex-circle assignment.",
    "The 1746 escaping assignment/slot-choice landings are not geometric realizability counts.",
    "The 1746 landings are not comparable to the 18088 common-dihedral profile/escape classes.",
    "Selected-baseline empty slots can later be filled by unselected equal-distance triples or profile excess.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py",
    "command": (
        "python scripts/analyze_n9_selected_baseline_d3_escape_class_crosswalk.py "
        "--assert-expected --out "
        "data/certificates/n9_selected_baseline_d3_escape_class_crosswalk.json"
    ),
}
EXPECTED_TOP_LEVEL_KEYS = {
    "assignment_count",
    "base_apex_slack",
    "capacity_deficit_budget",
    "claim_scope",
    "contradiction_threshold",
    "crosswalk_matrix",
    "crosswalk_rows",
    "crosswalk_summary",
    "escape_class_count",
    "escape_classes",
    "escaping_budget3_slot_choice_count",
    "escaping_relevant_count_distribution",
    "every_escaping_placement_relevant_count",
    "forced_budget3_slot_choice_count",
    "forced_relevant_count_distribution",
    "interpretation",
    "n",
    "provenance",
    "relevant_count_distribution",
    "schema",
    "selected_baseline_class_count",
    "selected_baseline_classes",
    "source_artifacts",
    "status",
    "total_budget3_slot_choice_count",
    "trust",
    "witness_size",
}


def strict_int(value: Any) -> bool:
    """Return true only for JSON integers, excluding bool."""

    return type(value) is int


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def append_comparison_error(errors: list[str], message: str) -> None:
    """Append a bounded recursive-comparison error."""

    if len(errors) < MAX_COMPARISON_ERRORS:
        errors.append(message)


def compare_json(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    """Compare JSON data with strict integer/bool typing and list ordering."""

    if len(errors) >= MAX_COMPARISON_ERRORS:
        return
    if strict_int(expected):
        if not strict_int(actual):
            append_comparison_error(
                errors,
                f"{label} must be int {expected!r}; got {actual!r} ({type(actual).__name__})",
            )
        elif actual != expected:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected {expected!r}, got {actual!r}",
            )
        return
    if type(expected) is bool:
        if type(actual) is not bool:
            append_comparison_error(
                errors,
                f"{label} must be bool {expected!r}; got {actual!r} ({type(actual).__name__})",
            )
        elif actual != expected:
            append_comparison_error(
                errors,
                f"{label} mismatch: expected {expected!r}, got {actual!r}",
            )
        return
    if isinstance(expected, list):
        if not isinstance(actual, list):
            append_comparison_error(errors, f"{label} must be a list")
            return
        if len(actual) != len(expected):
            append_comparison_error(
                errors,
                f"{label} length mismatch: expected {len(expected)}, got {len(actual)}",
            )
            return
        for index, (actual_item, expected_item) in enumerate(zip(actual, expected)):
            compare_json(errors, f"{label}[{index}]", actual_item, expected_item)
        return
    if isinstance(expected, dict):
        if not isinstance(actual, dict):
            append_comparison_error(errors, f"{label} must be an object")
            return
        if set(actual) != set(expected):
            append_comparison_error(
                errors,
                "keys mismatch at "
                f"{label}: expected {sorted(expected)!r}, got {sorted(actual)!r}",
            )
            return
        for key in expected:
            compare_json(errors, f"{label}.{key}", actual[key], expected[key])
        return
    if actual != expected:
        append_comparison_error(
            errors,
            f"{label} mismatch: expected {expected!r}, got {actual!r}",
        )


def validate_shape(payload: dict[str, Any]) -> list[str]:
    """Return lightweight shape and arithmetic validation errors."""

    errors: list[str] = []
    selected_rows = payload.get("selected_baseline_classes")
    escape_rows = payload.get("escape_classes")
    crosswalk_rows = payload.get("crosswalk_rows")
    matrix = payload.get("crosswalk_matrix")
    summary = payload.get("crosswalk_summary")

    if not isinstance(selected_rows, list):
        errors.append("selected_baseline_classes must be a list")
    else:
        expected_ids = [f"B{index:02d}" for index in range(len(selected_rows))]
        actual_ids = [
            row.get("selected_baseline_class_id")
            if isinstance(row, dict)
            else None
            for row in selected_rows
        ]
        if actual_ids != expected_ids:
            errors.append("selected_baseline_class ids are out of order")
        assignment_total = 0
        for index, row in enumerate(selected_rows):
            if not isinstance(row, dict):
                errors.append(f"selected_baseline_classes[{index}] must be an object")
                continue
            count = row.get("assignment_count")
            if not strict_int(count):
                errors.append(
                    f"selected_baseline_classes[{index}].assignment_count must be int"
                )
            else:
                assignment_total += int(count)
        if assignment_total != payload.get("assignment_count"):
            errors.append("selected-baseline assignment counts do not sum")

    if not isinstance(escape_rows, list):
        errors.append("escape_classes must be a list")
    else:
        expected_ids = [f"X{index:02d}" for index in range(len(escape_rows))]
        actual_ids = [
            row.get("escape_class_id") if isinstance(row, dict) else None
            for row in escape_rows
        ]
        if actual_ids != expected_ids:
            errors.append("escape class ids are out of order")

    if not isinstance(crosswalk_rows, list):
        errors.append("crosswalk_rows must be a list")
    else:
        row_total = 0
        previous_key: tuple[str, str] | None = None
        for index, row in enumerate(crosswalk_rows):
            if not isinstance(row, dict):
                errors.append(f"crosswalk_rows[{index}] must be an object")
                continue
            selected_id = row.get("selected_baseline_class_id")
            escape_id = row.get("escape_class_id")
            count = row.get("escaping_assignment_slot_choice_landing_count")
            if not isinstance(selected_id, str) or not isinstance(escape_id, str):
                errors.append(f"crosswalk_rows[{index}] must have string ids")
                continue
            key = (selected_id, escape_id)
            if previous_key is not None and key <= previous_key:
                errors.append("crosswalk_rows must be sorted and unique")
            previous_key = key
            if not strict_int(count) or int(count) <= 0:
                errors.append(f"crosswalk_rows[{index}] must have positive int count")
            else:
                row_total += int(count)
        if row_total != payload.get("escaping_budget3_slot_choice_count"):
            errors.append("crosswalk row counts do not sum to escaping landings")

    if not isinstance(matrix, dict):
        errors.append("crosswalk_matrix must be an object")
    else:
        matrix_rows = matrix.get("rows")
        if not isinstance(matrix_rows, list):
            errors.append("crosswalk_matrix.rows must be a list")
        elif isinstance(selected_rows, list) and len(matrix_rows) != len(selected_rows):
            errors.append("crosswalk matrix row count must match selected classes")

    if not isinstance(summary, dict):
        errors.append("crosswalk_summary must be an object")
    else:
        expect_equal(
            errors,
            "crosswalk_summary.not_comparable_reference",
            summary.get("not_comparable_reference_common_dihedral_profile_escape_class_count"),
            18088,
        )
    return errors


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded crosswalk artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(top_level_keys)!r}"
        )

    for key, expected in {
        "schema": EXPECTED_SCHEMA,
        "status": EXPECTED_STATUS,
        "trust": EXPECTED_TRUST,
        "claim_scope": EXPECTED_CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "base_apex_slack": 9,
        "capacity_deficit_budget": 3,
        "contradiction_threshold": 3,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
        "interpretation": EXPECTED_INTERPRETATION,
        "provenance": EXPECTED_PROVENANCE,
    }.items():
        expect_equal(errors, key, payload.get(key), expected)

    claim_scope = payload.get("claim_scope")
    if isinstance(claim_scope, str):
        lowered = claim_scope.lower()
        for phrase in (
            "not a proof",
            "not a counterexample",
            "not an incidence-completeness result",
            "not a geometric realizability test",
            "not a global status update",
        ):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")
    else:
        errors.append("claim_scope must be a string")

    if payload.get("every_escaping_placement_relevant_count") is not True:
        errors.append("every escaping placement must have relevant count 3")

    errors.extend(validate_shape(payload))

    try:
        expected_payload = selected_baseline_d3_escape_class_crosswalk_report()
    except (AssertionError, ValueError) as exc:
        errors.append(f"recomputed crosswalk failed: {exc}")
    else:
        comparison_errors: list[str] = []
        compare_json(comparison_errors, "crosswalk payload", payload, expected_payload)
        errors.extend(comparison_errors)
        if len(comparison_errors) >= MAX_COMPARISON_ERRORS:
            errors.append("additional payload mismatches omitted")
    return errors


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    summary = object_payload.get("crosswalk_summary", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "assignment_count": object_payload.get("assignment_count"),
        "selected_baseline_class_count": object_payload.get(
            "selected_baseline_class_count"
        ),
        "escape_class_count": object_payload.get("escape_class_count"),
        "total_budget3_slot_choice_count": object_payload.get(
            "total_budget3_slot_choice_count"
        ),
        "forced_budget3_slot_choice_count": object_payload.get(
            "forced_budget3_slot_choice_count"
        ),
        "escaping_budget3_slot_choice_count": object_payload.get(
            "escaping_budget3_slot_choice_count"
        ),
        "nonzero_crosswalk_cell_count": (
            summary.get("nonzero_crosswalk_cell_count")
            if isinstance(summary, dict)
            else None
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 selected-baseline D=3 escape-class crosswalk artifact")
        print(f"artifact: {summary['artifact']}")
        print(
            "budget-3 choices: "
            f"total={summary['total_budget3_slot_choice_count']}, "
            f"forced={summary['forced_budget3_slot_choice_count']}, "
            f"escaping={summary['escaping_budget3_slot_choice_count']}"
        )
        print(f"nonzero cells: {summary['nonzero_crosswalk_cell_count']}")
        if args.check:
            print("OK: selected-baseline D=3 crosswalk checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
