#!/usr/bin/env python3
"""Generate or check the selected-baseline D=3 landing/template join."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

from erdos97.json_io import write_json
from erdos97.n9_selected_baseline_d3_escape_class_crosswalk import (
    assert_expected_crosswalk_counts,
)
from erdos97.n9_selected_baseline_d3_vertex_circle_template_join import (
    CLAIM_SCOPE,
    EXPECTED_ESCAPE_LANDING_COUNTS,
    EXPECTED_ESCAPING_LANDING_COUNT,
    EXPECTED_FAMILY_LANDING_COUNTS,
    EXPECTED_STATUS_LANDING_COUNTS,
    EXPECTED_TEMPLATE_LANDING_COUNTS,
    INTERPRETATION,
    PROVENANCE,
    SCHEMA,
    SOURCE_ARTIFACTS,
    STATUS,
    TRUST,
    assert_expected_template_join_counts,
    selected_baseline_d3_vertex_circle_template_join_payload,
)
from erdos97.n9_vertex_circle_frontier_motif_classification import (
    assert_expected_classification_counts,
)
from erdos97.n9_vertex_circle_template_lemma_catalog import (
    assert_expected_template_lemma_catalog_counts,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_selected_baseline_d3_vertex_circle_template_join.json"
)
DEFAULT_CROSSWALK = (
    ROOT
    / "data"
    / "certificates"
    / "n9_selected_baseline_d3_escape_class_crosswalk.json"
)
DEFAULT_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_TEMPLATE_CATALOG = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_template_lemma_catalog.json"
)
MAX_COMPARISON_ERRORS = 20
EXPECTED_TOP_LEVEL_KEYS = {
    "base_apex_slack",
    "capacity_deficit_budget",
    "claim_scope",
    "contradiction_threshold",
    "escape_class_count",
    "escape_class_landing_counts",
    "escaping_assignment_slot_choice_landing_count",
    "family_escape_class_landing_counts",
    "forced_budget3_slot_choice_count",
    "interpretation",
    "landing_records",
    "n",
    "provenance",
    "schema",
    "selected_baseline_class_count",
    "selected_baseline_class_landing_counts",
    "source_artifacts",
    "source_assignment_count",
    "status",
    "status_escape_class_landing_counts",
    "template_escape_class_landing_matrix",
    "template_escape_class_landing_rows",
    "total_budget3_slot_choice_count",
    "trust",
    "vertex_circle_family_count",
    "vertex_circle_family_landing_counts",
    "vertex_circle_status_landing_counts",
    "vertex_circle_template_count",
    "vertex_circle_template_landing_counts",
    "vertex_circle_template_summaries",
    "witness_size",
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def strict_int(value: Any) -> bool:
    """Return true only for JSON integers, excluding bool."""

    return type(value) is int


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


def _json_int_list(value: Any) -> list[int] | None:
    """Return a list of strict JSON ints, or None for malformed payloads."""

    if not isinstance(value, list) or not all(strict_int(item) for item in value):
        return None
    return [int(item) for item in value]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def load_source_payloads(
    *,
    crosswalk_path: Path = DEFAULT_CROSSWALK,
    classification_path: Path = DEFAULT_CLASSIFICATION,
    template_catalog_path: Path = DEFAULT_TEMPLATE_CATALOG,
) -> dict[str, Any]:
    """Load the source artifacts used by this join."""

    return {
        "crosswalk": load_artifact(_resolve(crosswalk_path)),
        "classification": load_artifact(_resolve(classification_path)),
        "template_catalog": load_artifact(_resolve(template_catalog_path)),
    }


def _validate_sources(source_payloads: dict[str, Any], errors: list[str]) -> None:
    crosswalk = source_payloads.get("crosswalk")
    classification = source_payloads.get("classification")
    template_catalog = source_payloads.get("template_catalog")
    if not isinstance(crosswalk, dict):
        errors.append("source selected-baseline D=3 crosswalk must be an object")
    else:
        try:
            assert_expected_crosswalk_counts(crosswalk)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source selected-baseline D=3 crosswalk invalid: {exc}")
    if not isinstance(classification, dict):
        errors.append("source frontier motif classification must be an object")
    else:
        try:
            assert_expected_classification_counts(classification)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source frontier motif classification invalid: {exc}")
    if not isinstance(template_catalog, dict):
        errors.append("source vertex-circle template catalog must be an object")
    else:
        try:
            assert_expected_template_lemma_catalog_counts(template_catalog)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            errors.append(f"source vertex-circle template catalog invalid: {exc}")


def _expected_payload(
    source_payloads: dict[str, Any],
    errors: list[str],
) -> dict[str, Any] | None:
    try:
        return selected_baseline_d3_vertex_circle_template_join_payload(
            source_payloads["classification"],
            source_payloads["template_catalog"],
        )
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"source-bound landing/template join failed: {exc}")
        return None


def _validate_crosswalk_alignment(
    payload: dict[str, Any],
    crosswalk: dict[str, Any],
    errors: list[str],
) -> None:
    summary = crosswalk.get("crosswalk_summary")
    if not isinstance(summary, dict):
        errors.append("source crosswalk missing crosswalk_summary")
        return
    expected_escape_counts = summary.get("escaping_landing_count_by_escape_class")
    expected_selected_counts = summary.get(
        "escaping_landing_count_by_selected_baseline_class"
    )
    expect_equal(
        errors,
        "total_budget3_slot_choice_count",
        payload.get("total_budget3_slot_choice_count"),
        crosswalk.get("total_budget3_slot_choice_count"),
    )
    expect_equal(
        errors,
        "forced_budget3_slot_choice_count",
        payload.get("forced_budget3_slot_choice_count"),
        crosswalk.get("forced_budget3_slot_choice_count"),
    )
    expect_equal(
        errors,
        "escaping_assignment_slot_choice_landing_count",
        payload.get("escaping_assignment_slot_choice_landing_count"),
        crosswalk.get("escaping_budget3_slot_choice_count"),
    )
    expect_equal(
        errors,
        "escape_class_landing_counts",
        payload.get("escape_class_landing_counts"),
        expected_escape_counts,
    )
    expect_equal(
        errors,
        "selected_baseline_class_landing_counts",
        payload.get("selected_baseline_class_landing_counts"),
        expected_selected_counts,
    )


def _validate_landing_records(payload: dict[str, Any], errors: list[str]) -> None:
    records = payload.get("landing_records")
    if not isinstance(records, list):
        errors.append("landing_records must be a list")
        return
    status_counts: dict[str, int] = {}
    template_counts: dict[str, int] = {key: 0 for key in EXPECTED_TEMPLATE_LANDING_COUNTS}
    family_counts: dict[str, int] = {key: 0 for key in EXPECTED_FAMILY_LANDING_COUNTS}
    escape_counts: dict[str, int] = {key: 0 for key in EXPECTED_ESCAPE_LANDING_COUNTS}
    seen_landing_ids: set[str] = set()
    previous_key: tuple[str, int] | None = None
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            errors.append(f"landing record {index} must be an object")
            continue
        landing_id = record.get("landing_id")
        expected_landing_id = f"L{index:04d}"
        if landing_id != expected_landing_id:
            errors.append(
                f"landing id mismatch at row {index}: "
                f"expected {expected_landing_id}, got {landing_id!r}"
            )
        if isinstance(landing_id, str):
            if landing_id in seen_landing_ids:
                errors.append(f"duplicate landing id {landing_id}")
            seen_landing_ids.add(landing_id)
        assignment_id = record.get("assignment_id")
        choice_index = record.get("budget3_slot_choice_index")
        if not isinstance(assignment_id, str) or not strict_int(choice_index):
            errors.append(f"{landing_id or index} must have assignment id and int choice")
            continue
        key = (assignment_id, int(choice_index))
        if previous_key is not None and key <= previous_key:
            errors.append("landing records must be sorted by assignment and choice")
        previous_key = key
        indices = record.get("budget3_slot_choice_indices")
        slots = record.get("budget3_slot_choice_slots")
        if not isinstance(indices, list) or len(indices) != 3:
            errors.append(f"{landing_id or index} slot indices must be a 3-list")
        elif any(not strict_int(item) for item in indices):
            errors.append(f"{landing_id or index} slot indices must be JSON ints")
        if not isinstance(slots, list) or len(slots) != 3:
            errors.append(f"{landing_id or index} slot payloads must be a 3-list")
        placement = record.get("relevant_escape_placement")
        if not isinstance(placement, dict):
            errors.append(f"{landing_id or index} missing relevant escape placement")
        else:
            spoiled2 = _json_int_list(placement.get("spoiled_length2"))
            spoiled3 = _json_int_list(placement.get("spoiled_length3"))
            if spoiled2 is None or spoiled3 is None:
                errors.append(
                    f"{landing_id or index} relevant placement lists must be JSON ints"
                )
            elif len(spoiled2) + len(spoiled3) != 3:
                errors.append(f"{landing_id or index} relevant placement is not D=3")
        status = str(record.get("vertex_circle_status"))
        template_id = str(record.get("vertex_circle_template_id"))
        family_id = str(record.get("vertex_circle_family_id"))
        escape_id = str(record.get("escape_class_id"))
        status_counts[status] = status_counts.get(status, 0) + 1
        if template_id in template_counts:
            template_counts[template_id] += 1
        else:
            errors.append(f"{landing_id or index} has unexpected template {template_id}")
        if family_id in family_counts:
            family_counts[family_id] += 1
        else:
            errors.append(f"{landing_id or index} has unexpected family {family_id}")
        if escape_id in escape_counts:
            escape_counts[escape_id] += 1
        else:
            errors.append(f"{landing_id or index} has unexpected escape class {escape_id}")

    expect_equal(
        errors,
        "vertex_circle_status_landing_counts",
        payload.get("vertex_circle_status_landing_counts"),
        dict(sorted(status_counts.items())),
    )
    expect_equal(
        errors,
        "vertex_circle_template_landing_counts",
        payload.get("vertex_circle_template_landing_counts"),
        template_counts,
    )
    expect_equal(
        errors,
        "vertex_circle_family_landing_counts",
        payload.get("vertex_circle_family_landing_counts"),
        family_counts,
    )
    expect_equal(
        errors,
        "escape_class_landing_counts",
        payload.get("escape_class_landing_counts"),
        escape_counts,
    )


def validate_payload(
    payload: Any,
    *,
    source_payloads: dict[str, Any] | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for the landing/template join artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    if source_payloads is None:
        try:
            source_payloads = load_source_payloads()
        except (OSError, json.JSONDecodeError) as exc:
            return [f"could not load source artifacts: {exc}"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "base_apex_slack": 9,
        "capacity_deficit_budget": 3,
        "contradiction_threshold": 3,
        "source_assignment_count": 184,
        "total_budget3_slot_choice_count": 15456,
        "forced_budget3_slot_choice_count": 13710,
        "escaping_assignment_slot_choice_landing_count": (
            EXPECTED_ESCAPING_LANDING_COUNT
        ),
        "selected_baseline_class_count": 13,
        "escape_class_count": 8,
        "vertex_circle_template_count": 12,
        "vertex_circle_family_count": 16,
        "vertex_circle_status_landing_counts": EXPECTED_STATUS_LANDING_COUNTS,
        "vertex_circle_template_landing_counts": EXPECTED_TEMPLATE_LANDING_COUNTS,
        "vertex_circle_family_landing_counts": EXPECTED_FAMILY_LANDING_COUNTS,
        "escape_class_landing_counts": EXPECTED_ESCAPE_LANDING_COUNTS,
        "interpretation": INTERPRETATION,
        "source_artifacts": SOURCE_ARTIFACTS,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        compare_json(errors, key, payload.get(key), expected)

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

    _validate_sources(source_payloads, errors)
    if not errors:
        _validate_crosswalk_alignment(payload, source_payloads["crosswalk"], errors)
    _validate_landing_records(payload, errors)

    try:
        assert_expected_template_join_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected landing/template join counts failed: {exc}")

    if recompute and not errors:
        expected_payload = _expected_payload(source_payloads, errors)
        if expected_payload is not None:
            comparison_errors: list[str] = []
            compare_json(
                comparison_errors,
                "landing/template join payload",
                payload,
                expected_payload,
            )
            errors.extend(comparison_errors)
            if len(comparison_errors) >= MAX_COMPARISON_ERRORS:
                errors.append("additional payload mismatches omitted")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "source_assignment_count": object_payload.get("source_assignment_count"),
        "escaping_assignment_slot_choice_landing_count": object_payload.get(
            "escaping_assignment_slot_choice_landing_count"
        ),
        "vertex_circle_status_landing_counts": object_payload.get(
            "vertex_circle_status_landing_counts"
        ),
        "vertex_circle_template_landing_counts": object_payload.get(
            "vertex_circle_template_landing_counts"
        ),
        "escape_class_landing_counts": object_payload.get("escape_class_landing_counts"),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated artifact")
    parser.add_argument("--check", action="store_true", help="validate an existing artifact")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--crosswalk", type=Path, default=DEFAULT_CROSSWALK)
    parser.add_argument("--classification", type=Path, default=DEFAULT_CLASSIFICATION)
    parser.add_argument("--template-catalog", type=Path, default=DEFAULT_TEMPLATE_CATALOG)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    out = _resolve(args.out)
    artifact = _resolve(args.artifact) if args.artifact is not None else DEFAULT_ARTIFACT
    if args.write and args.check:
        if args.artifact is not None and artifact != out:
            print(
                "--write --check requires matching --artifact/--out or omitted --artifact",
                file=sys.stderr,
            )
            return 2
        artifact = out

    try:
        sources = load_source_payloads(
            crosswalk_path=args.crosswalk,
            classification_path=args.classification,
            template_catalog_path=args.template_catalog,
        )
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAILED: could not load source artifacts: {exc}", file=sys.stderr)
        return 1

    if args.write:
        payload = selected_baseline_d3_vertex_circle_template_join_payload(
            sources["classification"],
            sources["template_catalog"],
        )
        errors = validate_payload(payload, source_payloads=sources, recompute=False)
        if args.assert_expected and not errors:
            try:
                assert_expected_template_join_counts(payload)
            except (AssertionError, KeyError, TypeError, ValueError) as exc:
                errors.append(f"expected landing/template join counts failed: {exc}")
        if errors:
            print(f"FAILED: generated payload for {display_path(out, ROOT)}", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source_payloads=sources,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 selected-baseline D=3 landing/template join")
        print(f"artifact: {summary['artifact']}")
        print(f"landings: {summary['escaping_assignment_slot_choice_landing_count']}")
        print(f"status counts: {summary['vertex_circle_status_landing_counts']}")
        print(f"template counts: {summary['vertex_circle_template_landing_counts']}")
        if args.check or args.assert_expected:
            print("OK: selected-baseline D=3 landing/template join checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
