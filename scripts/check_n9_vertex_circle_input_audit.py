#!/usr/bin/env python3
"""Input-data audit for the review-pending n=9 vertex-circle artifact."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_input_audit.v1"
STATUS = "REVIEW_PENDING_INPUT_DATA_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Input-data audit for the review-pending n=9 vertex-circle exhaustive "
    "artifact. It checks row0 coverage, explicit witness lists, masks, "
    "summary counts, and no-overclaiming scope from the stored JSON. It does "
    "not rerun the brancher, does not replay vertex-circle certificates, does "
    "not prove n=9, does not claim a counterexample, and does not update the "
    "official/global status."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_input_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_input_audit.py "
        "--check --assert-expected --json"
    ),
}
SUMMARY_JSON_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "source_artifact",
    "review_independence",
    "coverage_summary",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_vertex_circle_exhaustive.json"
N = 9
ROW_SIZE = 4
EXPECTED_TYPE = "n9_vertex_circle_exhaustive_v1"
EXPECTED_SOURCE_TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
EXPECTED_ROW0_CHOICES = 70
EXPECTED_MAIN_NODES = 16_752
EXPECTED_MAIN_FULL = 0
EXPECTED_MAIN_COUNTS = {
    "partial_self_edge": 11_271,
    "partial_strict_cycle": 11_011,
}
EXPECTED_CROSS_NODES = 100_817
EXPECTED_CROSS_FULL = 184
EXPECTED_CROSS_COUNTS = {
    "self_edge": 158,
    "strict_cycle": 26,
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expected_row0_records() -> list[dict[str, Any]]:
    """Return the independent lexicographic row0 selected-witness options."""

    records: list[dict[str, Any]] = []
    for index, witnesses in enumerate(combinations(range(1, N), ROW_SIZE)):
        witness_list = list(witnesses)
        records.append(
            {
                "row0_index": index,
                "row0_witnesses": witness_list,
                "row0_mask": sum(1 << witness for witness in witness_list),
            }
        )
    return records


def n9_vertex_circle_input_audit_payload(
    artifact: Mapping[str, Any],
    *,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict[str, Any]:
    """Return an input-data audit summary for the n=9 vertex-circle artifact."""

    errors: list[str] = []
    expected_rows = expected_row0_records()
    row0_audit = _audit_row0_options(artifact, expected_rows, errors)
    _audit_top_level(artifact, expected_rows, errors)
    count_audit = _audit_search_counts(artifact, expected_rows, errors)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": display_path(artifact_path, ROOT),
            "type": artifact.get("type"),
            "trust": artifact.get("trust"),
        },
        "review_independence": {
            "uses_exhaustive_brancher": False,
            "uses_vertex_circle_replay": False,
            "method": (
                "Recomputes row0 options directly as the 70 lexicographic "
                "4-subsets of labels 1..8, then checks the stored JSON "
                "witness lists, masks, and count arithmetic."
            ),
        },
        "coverage_summary": {
            "expected_row0_choices": len(expected_rows),
            "row0_choice_count_expected": artifact.get("row0_choice_count_expected"),
            "row0_witnesses_match_lexicographic_combinations": row0_audit[
                "row0_witnesses_match_lexicographic_combinations"
            ],
            "row0_masks_match_witnesses": row0_audit["row0_masks_match_witnesses"],
            "main_row0_choices": count_audit["main_row0_choices"],
            "cross_check_row0_choices": count_audit["cross_check_row0_choices"],
            "main_full_assignments": count_audit["main_full_assignments"],
            "cross_check_full_assignments": count_audit["cross_check_full_assignments"],
            "cross_check_status_total": count_audit["cross_check_status_total"],
        },
        "expected_counts": {
            "main_nodes": EXPECTED_MAIN_NODES,
            "main_full": EXPECTED_MAIN_FULL,
            "main_counts": dict(EXPECTED_MAIN_COUNTS),
            "cross_check_nodes": EXPECTED_CROSS_NODES,
            "cross_check_full": EXPECTED_CROSS_FULL,
            "cross_check_counts": dict(EXPECTED_CROSS_COUNTS),
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the checked-in n=9 exhaustive artifact is "
            "internally consistent as input data for the row0 coverage and "
            "summary counts. It is not a search rerun, vertex-circle proof "
            "replay, or n=9 proof."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_input_audit(payload: Mapping[str, Any]) -> None:
    """Assert the expected n=9 input-audit result."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not rerun the brancher",
        "does not replay vertex-circle certificates",
        "does not prove n=9",
        "does not claim a counterexample",
        "does not update the official/global status",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    review = payload.get("review_independence")
    if not isinstance(review, Mapping):
        raise AssertionError("review_independence must be an object")
    if review.get("uses_exhaustive_brancher") is not False:
        raise AssertionError("audit must not depend on the exhaustive brancher")
    if review.get("uses_vertex_circle_replay") is not False:
        raise AssertionError("audit must not replay vertex-circle certificates")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, Mapping):
        raise AssertionError("coverage_summary must be an object")
    expected = {
        "expected_row0_choices": EXPECTED_ROW0_CHOICES,
        "row0_choice_count_expected": EXPECTED_ROW0_CHOICES,
        "row0_witnesses_match_lexicographic_combinations": True,
        "row0_masks_match_witnesses": True,
        "main_row0_choices": EXPECTED_ROW0_CHOICES,
        "cross_check_row0_choices": EXPECTED_ROW0_CHOICES,
        "main_full_assignments": EXPECTED_MAIN_FULL,
        "cross_check_full_assignments": EXPECTED_CROSS_FULL,
        "cross_check_status_total": EXPECTED_CROSS_FULL,
    }
    for key, value in expected.items():
        if coverage.get(key) != value:
            raise AssertionError(
                f"coverage_summary[{key!r}] mismatch: expected {value!r}, "
                f"got {coverage.get(key)!r}"
            )


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view."""

    return {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}


def _audit_top_level(
    artifact: Mapping[str, Any],
    expected_rows: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> None:
    _check_equal(errors, "type", artifact.get("type"), EXPECTED_TYPE)
    _check_equal(errors, "trust", artifact.get("trust"), EXPECTED_SOURCE_TRUST)
    _check_equal(errors, "n", artifact.get("n"), N)
    _check_equal(errors, "row_size", artifact.get("row_size"), ROW_SIZE)
    _check_equal(errors, "cyclic_order", artifact.get("cyclic_order"), list(range(N)))
    _check_equal(
        errors,
        "row0_choice_count_expected",
        artifact.get("row0_choice_count_expected"),
        len(expected_rows),
    )
    _check_scope_text(artifact, errors)


def _audit_row0_options(
    artifact: Mapping[str, Any],
    expected_rows: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> dict[str, bool]:
    expected_witnesses = [row["row0_witnesses"] for row in expected_rows]
    expected_masks = [row["row0_mask"] for row in expected_rows]

    witnesses_ok = _check_equal(
        errors,
        "row0_witnesses",
        artifact.get("row0_witnesses"),
        expected_witnesses,
    )
    masks_ok = _check_equal(
        errors,
        "row0_masks",
        artifact.get("row0_masks"),
        expected_masks,
    )
    return {
        "row0_witnesses_match_lexicographic_combinations": witnesses_ok,
        "row0_masks_match_witnesses": masks_ok,
    }


def _audit_search_counts(
    artifact: Mapping[str, Any],
    expected_rows: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> dict[str, int]:
    main = _mapping_field(artifact, "main_search", errors)
    cross = _mapping_field(
        artifact,
        "cross_check_without_vertex_circle_pruning",
        errors,
    )
    expected_count = len(expected_rows)

    _check_equal(errors, "main vertex_circle_pruning", main.get("vertex_circle_pruning"), True)
    _check_equal(errors, "main row0_choices", main.get("row0_choices"), expected_count)
    _check_equal(errors, "main nodes_visited", main.get("nodes_visited"), EXPECTED_MAIN_NODES)
    _check_equal(errors, "main full_assignments", main.get("full_assignments"), EXPECTED_MAIN_FULL)
    _check_equal(errors, "main counts", main.get("counts"), EXPECTED_MAIN_COUNTS)

    _check_equal(errors, "cross vertex_circle_pruning", cross.get("vertex_circle_pruning"), False)
    _check_equal(errors, "cross row0_choices", cross.get("row0_choices"), expected_count)
    _check_equal(errors, "cross nodes_visited", cross.get("nodes_visited"), EXPECTED_CROSS_NODES)
    _check_equal(errors, "cross full_assignments", cross.get("full_assignments"), EXPECTED_CROSS_FULL)
    _check_equal(errors, "cross counts", cross.get("counts"), EXPECTED_CROSS_COUNTS)
    cross_counts = cross.get("counts")
    cross_status_total = (
        sum(int(value) for value in cross_counts.values())
        if isinstance(cross_counts, Mapping)
        else -1
    )
    _check_equal(
        errors,
        "cross status total",
        cross_status_total,
        int(cross.get("full_assignments", -1)),
    )

    return {
        "main_row0_choices": int(main.get("row0_choices", -1)),
        "cross_check_row0_choices": int(cross.get("row0_choices", -1)),
        "main_full_assignments": int(main.get("full_assignments", -1)),
        "cross_check_full_assignments": int(cross.get("full_assignments", -1)),
        "cross_check_status_total": cross_status_total,
    }


def _check_scope_text(artifact: Mapping[str, Any], errors: list[str]) -> None:
    text_parts = [str(artifact.get("scope", "")), str(artifact.get("conclusion", ""))]
    notes = artifact.get("notes")
    if isinstance(notes, list):
        text_parts.extend(str(note) for note in notes)
    text = "\n".join(text_parts)
    for required in (
        "No general proof of Erdos Problem #97 is claimed.",
        "No counterexample is claimed.",
        "Public theorem-style use requires independent review",
        "does not update the official/global falsifiable-open status",
    ):
        if required not in text:
            errors.append(f"source artifact scope/notes missing {required!r}")


def _mapping_field(
    artifact: Mapping[str, Any],
    key: str,
    errors: list[str],
) -> Mapping[str, Any]:
    value = artifact.get(key)
    if not isinstance(value, Mapping):
        errors.append(f"{key} must be an object")
        return {}
    return value


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> bool:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")
        return False
    return True


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"row0 choices: {coverage['row0_choice_count_expected']} / {coverage['expected_row0_choices']}",
        f"main full assignments: {coverage['main_full_assignments']}",
        f"cross-check full assignments: {coverage['cross_check_full_assignments']}",
        f"cross-check status total: {coverage['cross_check_status_total']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON summary",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    try:
        artifact = load_artifact(artifact_path)
        if not isinstance(artifact, Mapping):
            raise TypeError("n=9 vertex-circle artifact top level must be an object")
        payload = n9_vertex_circle_input_audit_payload(
            artifact,
            artifact_path=artifact_path,
        )
    except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
        payload = {
            "schema": SCHEMA,
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "validation_status": "failed",
            "validation_errors": [str(exc)],
            "provenance": dict(PROVENANCE),
        }

    if args.assert_expected:
        assert_expected_input_audit(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle input-data audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 vertex-circle input-data audit checks passed")
    else:
        print("FAILED: n=9 vertex-circle input-data audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
