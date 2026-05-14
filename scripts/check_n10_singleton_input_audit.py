#!/usr/bin/env python3
"""Input-data audit for the draft n=10 singleton-slice artifact."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.n10_singleton_input_audit.v1"
STATUS = "DRAFT_INPUT_DATA_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Input-data audit for the draft review-pending n=10 singleton-slice "
    "artifact. It checks row0 coverage, explicit witness lists, masks, "
    "singleton ranges, and aggregate arithmetic from the stored JSON. It does "
    "not rerun the search, does not replay terminal conflicts, does not prove "
    "n=10, does not claim a counterexample, and does not update the "
    "official/global status."
)
PROVENANCE = {
    "generator": "scripts/check_n10_singleton_input_audit.py",
    "command": (
        "python scripts/check_n10_singleton_input_audit.py "
        "--check --assert-expected --json"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"
)
N = 10
ROW_SIZE = 4
EXPECTED_TYPE = "n10_vertex_circle_singleton_slices_v1"
EXPECTED_SOURCE_TRUST = "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING"
EXPECTED_ROW0_CHOICES = 126
EXPECTED_TOTAL_NODES = 4_142_738
EXPECTED_TOTAL_FULL = 0
EXPECTED_COUNTS = {
    "partial_self_edge": 4_467_592,
    "partial_strict_cycle": 5_318_250,
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def n10_singleton_input_audit_payload(
    artifact: Mapping[str, Any],
    *,
    artifact_path: Path = DEFAULT_ARTIFACT,
) -> dict[str, Any]:
    """Return an input-data audit summary for the n=10 singleton artifact."""

    errors: list[str] = []
    expected_rows = expected_row0_records()
    row_audit = _audit_rows(artifact, expected_rows, errors)
    _audit_top_level(artifact, expected_rows, row_audit, errors)

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
            "uses_generic_vertex_search": False,
            "uses_search_rerun": False,
            "method": (
                "Recomputes the row0 singleton option list directly as the "
                "126 lexicographic 4-subsets of labels 1..9, then checks the "
                "stored JSON rows and aggregate arithmetic."
            ),
        },
        "coverage_summary": {
            "expected_row0_choices": len(expected_rows),
            "row_count": row_audit["row_count"],
            "row0_ranges_cover_singletons": row_audit["row0_ranges_cover_singletons"],
            "row0_witnesses_match_lexicographic_combinations": row_audit[
                "row0_witnesses_match_lexicographic_combinations"
            ],
            "row0_masks_match_witnesses": row_audit["row0_masks_match_witnesses"],
            "aborted_any": row_audit["aborted_any"],
            "total_nodes_from_rows": row_audit["total_nodes_from_rows"],
            "total_full_from_rows": row_audit["total_full_from_rows"],
            "counts_from_rows": row_audit["counts_from_rows"],
        },
        "expected_counts": {
            "total_nodes": EXPECTED_TOTAL_NODES,
            "total_full": EXPECTED_TOTAL_FULL,
            "counts": dict(EXPECTED_COUNTS),
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the checked-in n=10 singleton artifact is "
            "internally consistent as input data for all 126 row0 singleton "
            "slices. It is not a search rerun or an n=10 proof."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_input_audit(payload: Mapping[str, Any]) -> None:
    """Assert the expected n=10 singleton input-audit result."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    claim_scope = str(payload.get("claim_scope", ""))
    for required in (
        "does not rerun the search",
        "does not prove n=10",
        "does not claim a counterexample",
        "does not update the official/global status",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    review = payload.get("review_independence")
    if not isinstance(review, Mapping):
        raise AssertionError("review_independence must be an object")
    if review.get("uses_generic_vertex_search") is not False:
        raise AssertionError("audit must not depend on GenericVertexSearch")
    if review.get("uses_search_rerun") is not False:
        raise AssertionError("audit must not rerun the search")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")

    coverage = payload.get("coverage_summary")
    if not isinstance(coverage, Mapping):
        raise AssertionError("coverage_summary must be an object")
    expected = {
        "expected_row0_choices": EXPECTED_ROW0_CHOICES,
        "row_count": EXPECTED_ROW0_CHOICES,
        "row0_ranges_cover_singletons": True,
        "row0_witnesses_match_lexicographic_combinations": True,
        "row0_masks_match_witnesses": True,
        "aborted_any": False,
        "total_nodes_from_rows": EXPECTED_TOTAL_NODES,
        "total_full_from_rows": EXPECTED_TOTAL_FULL,
        "counts_from_rows": EXPECTED_COUNTS,
    }
    for key, value in expected.items():
        if coverage.get(key) != value:
            raise AssertionError(
                f"coverage_summary[{key!r}] mismatch: expected {value!r}, "
                f"got {coverage.get(key)!r}"
            )


def expected_row0_records() -> list[dict[str, Any]]:
    """Return the independent lexicographic row0 singleton records."""

    out: list[dict[str, Any]] = []
    for index, witnesses in enumerate(combinations(range(1, N), ROW_SIZE)):
        witness_list = list(witnesses)
        out.append(
            {
                "row0_index": index,
                "row0_range": [index, index + 1],
                "row0_witnesses": witness_list,
                "row0_mask": sum(1 << witness for witness in witness_list),
            }
        )
    return out


def _audit_top_level(
    artifact: Mapping[str, Any],
    expected_rows: Sequence[Mapping[str, Any]],
    row_audit: Mapping[str, Any],
    errors: list[str],
) -> None:
    _check_equal(errors, "type", artifact.get("type"), EXPECTED_TYPE)
    _check_equal(errors, "trust", artifact.get("trust"), EXPECTED_SOURCE_TRUST)
    _check_equal(errors, "n", artifact.get("n"), N)
    _check_equal(errors, "row_size", artifact.get("row_size"), ROW_SIZE)
    _check_equal(
        errors,
        "row0_choice_count_expected",
        artifact.get("row0_choice_count_expected"),
        len(expected_rows),
    )
    _check_equal(
        errors,
        "row0_choices_covered",
        artifact.get("row0_choices_covered"),
        len(expected_rows),
    )
    _check_equal(errors, "aborted_any", artifact.get("aborted_any"), False)
    _check_equal(errors, "total_nodes", artifact.get("total_nodes"), EXPECTED_TOTAL_NODES)
    _check_equal(errors, "total_full", artifact.get("total_full"), EXPECTED_TOTAL_FULL)
    _check_equal(errors, "counts", artifact.get("counts"), EXPECTED_COUNTS)
    _check_equal(
        errors,
        "top-level row0_ranges",
        artifact.get("row0_ranges"),
        [row["row0_range"] for row in expected_rows],
    )
    _check_equal(
        errors,
        "top-level row0_witnesses",
        artifact.get("row0_witnesses"),
        [row["row0_witnesses"] for row in expected_rows],
    )
    _check_equal(
        errors,
        "row-derived total_nodes",
        row_audit.get("total_nodes_from_rows"),
        EXPECTED_TOTAL_NODES,
    )
    _check_equal(
        errors,
        "row-derived total_full",
        row_audit.get("total_full_from_rows"),
        EXPECTED_TOTAL_FULL,
    )
    _check_equal(
        errors,
        "row-derived counts",
        row_audit.get("counts_from_rows"),
        EXPECTED_COUNTS,
    )
    _check_scope_text(artifact, errors)


def _audit_rows(
    artifact: Mapping[str, Any],
    expected_rows: Sequence[Mapping[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    rows = artifact.get("rows")
    if not isinstance(rows, list):
        errors.append("rows must be a list")
        rows = []

    total_nodes = 0
    total_full = 0
    counts: Counter[str] = Counter()
    ranges_ok = len(rows) == len(expected_rows)
    witnesses_ok = len(rows) == len(expected_rows)
    masks_ok = len(rows) == len(expected_rows)
    aborted_any = False

    if len(rows) != len(expected_rows):
        errors.append(f"rows length mismatch: {len(rows)} != {len(expected_rows)}")

    for index, expected in enumerate(expected_rows):
        if index >= len(rows):
            break
        row = rows[index]
        if not isinstance(row, Mapping):
            errors.append(f"row {index} must be an object")
            ranges_ok = witnesses_ok = masks_ok = False
            continue
        ranges_ok &= _row_field_equal(errors, index, row, "row0_index", index)
        ranges_ok &= _row_field_equal(
            errors, index, row, "row0_range", expected["row0_range"]
        )
        witnesses_ok &= _row_field_equal(
            errors, index, row, "row0_witnesses", expected["row0_witnesses"]
        )
        masks_ok &= _row_field_equal(errors, index, row, "row0_mask", expected["row0_mask"])

        aborted = row.get("aborted")
        if aborted is not False:
            errors.append(f"row {index} aborted mismatch: {aborted!r} != False")
            aborted_any = True
        full = _nonnegative_int(errors, f"row {index} full", row.get("full"))
        if full != 0:
            errors.append(f"row {index} full mismatch: {full!r} != 0")
        total_full += full
        total_nodes += _nonnegative_int(errors, f"row {index} nodes", row.get("nodes"))

        row_counts = row.get("counts")
        if not isinstance(row_counts, Mapping):
            errors.append(f"row {index} counts must be an object")
        else:
            for key, value in row_counts.items():
                counts[str(key)] += _nonnegative_int(
                    errors,
                    f"row {index} counts[{key!r}]",
                    value,
                )

        elapsed = row.get("elapsed_seconds")
        if elapsed is not None and not _is_nonnegative_number(elapsed):
            errors.append(f"row {index} elapsed_seconds must be nonnegative numeric metadata")

    elapsed_sum = artifact.get("elapsed_sum_seconds")
    if elapsed_sum is not None and not _is_nonnegative_number(elapsed_sum):
        errors.append("elapsed_sum_seconds must be nonnegative numeric metadata")

    return {
        "row_count": len(rows),
        "row0_ranges_cover_singletons": ranges_ok,
        "row0_witnesses_match_lexicographic_combinations": witnesses_ok,
        "row0_masks_match_witnesses": masks_ok,
        "aborted_any": aborted_any,
        "total_nodes_from_rows": total_nodes,
        "total_full_from_rows": total_full,
        "counts_from_rows": dict(sorted(counts.items())),
    }


def _check_scope_text(artifact: Mapping[str, Any], errors: list[str]) -> None:
    text_parts = [str(artifact.get("scope", ""))]
    notes = artifact.get("notes")
    if isinstance(notes, list):
        text_parts.extend(str(note) for note in notes)
    text = "\n".join(text_parts)
    for required in (
        "No general proof of Erdos Problem #97 is claimed.",
        "No counterexample is claimed.",
        "source-of-truth strongest local result remains n <= 8",
        "needs independent checker review",
    ):
        if required not in text:
            errors.append(f"source artifact scope/notes missing {required!r}")


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def _row_field_equal(
    errors: list[str],
    index: int,
    row: Mapping[str, Any],
    key: str,
    expected: Any,
) -> bool:
    actual = row.get(key)
    if actual != expected:
        errors.append(f"row {index} {key} mismatch: {actual!r} != {expected!r}")
        return False
    return True


def _nonnegative_int(errors: list[str], name: str, value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        errors.append(f"{name} must be a nonnegative integer")
        return 0
    return value


def _is_nonnegative_number(value: Any) -> bool:
    return not isinstance(value, bool) and isinstance(value, (int, float)) and value >= 0


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    coverage = payload["coverage_summary"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"row0 choices: {coverage['row_count']} / {coverage['expected_row0_choices']}",
        f"total nodes from rows: {coverage['total_nodes_from_rows']}",
        f"total full from rows: {coverage['total_full_from_rows']}",
        f"counts from rows: {coverage['counts_from_rows']}",
    ]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    try:
        artifact = load_artifact(artifact_path)
        if not isinstance(artifact, Mapping):
            raise TypeError("n=10 singleton artifact top level must be an object")
        payload = n10_singleton_input_audit_payload(
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

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=10 singleton input-data audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=10 singleton input-data audit checks passed")
    else:
        print("FAILED: n=10 singleton input-data audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
