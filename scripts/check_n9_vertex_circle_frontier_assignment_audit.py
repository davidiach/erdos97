#!/usr/bin/env python3
"""Audit stored n=9 frontier selected-witness assignments."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)

SCHEMA = "erdos97.n9_vertex_circle_frontier_assignment_audit.v1"
STATUS = "REVIEW_PENDING_FRONTIER_ASSIGNMENT_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Stored-frontier assignment audit for the review-pending n=9 "
    "vertex-circle checker. It checks row shape, row-center coverage, "
    "pairwise row-intersection caps, two-overlap crossing, witness-pair "
    "capacity, and selected-indegree capacity on the stored 184 frontier "
    "assignments. It does not prove frontier coverage, brancher soundness, "
    "strict-edge geometry, selected-distance quotient soundness, n=9, a "
    "counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_frontier_assignment_audit.py",
    "command": (
        "python scripts/check_n9_vertex_circle_frontier_assignment_audit.py "
        "--check --assert-expected --json"
    ),
}
SUMMARY_JSON_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "n",
    "row_size",
    "pair_cap",
    "max_selected_indegree",
    "source_artifact",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
FRONTIER_ASSIGNMENT_SUMMARY_KEYS = (
    "assignment_count",
    "row_count_total",
    "status_counts",
    "row_shape_errors",
    "center_coverage_errors",
    "intersection_cap_violations",
    "two_overlap_crossing_violations",
    "witness_pair_cap_violations",
    "selected_indegree_cap_violations",
    "center_pair_intersection_histogram",
    "two_overlap_crossing_count",
    "witness_pair_frequency_histogram",
    "selected_indegree_value_histogram",
    "assignment_witness_pair_profiles",
)

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_SELECTED_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)

EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_ROW_COUNT_TOTAL = 1_656
EXPECTED_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM = {0: 72, 1: 3_168, 2: 3_384}
EXPECTED_TWO_OVERLAP_CROSSING_COUNT = 3_384
EXPECTED_WITNESS_PAIR_FREQUENCY_HISTOGRAM = {0: 72, 1: 3_168, 2: 3_384}
EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM = {4: 1_656}
EXPECTED_ASSIGNMENT_WITNESS_PAIR_PROFILES = {
    "1:18|2:18": 148,
    "0:2|1:14|2:20": 36,
}


Pair = tuple[int, int]
CompactRows = dict[int, tuple[int, ...]]


def load_json(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def frontier_assignment_audit_payload(
    *,
    frontier_path: Path = DEFAULT_FRONTIER_CLASSIFICATION,
) -> dict[str, Any]:
    """Return a direct audit of stored n=9 frontier assignments."""

    frontier = load_json(frontier_path)
    errors: list[str] = []
    summary = _audit_frontier_assignments(frontier, errors)
    _check_equal(errors, "assignment count", summary["assignment_count"], EXPECTED_ASSIGNMENT_COUNT)
    _check_equal(errors, "row count total", summary["row_count_total"], EXPECTED_ROW_COUNT_TOTAL)
    _check_equal(errors, "status counts", summary["status_counts"], EXPECTED_STATUS_COUNTS)
    _check_equal(
        errors,
        "center-pair intersection histogram",
        summary["center_pair_intersection_histogram"],
        EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
    )
    _check_equal(
        errors,
        "two-overlap crossing count",
        summary["two_overlap_crossing_count"],
        EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
    )
    _check_equal(
        errors,
        "witness-pair frequency histogram",
        summary["witness_pair_frequency_histogram"],
        EXPECTED_WITNESS_PAIR_FREQUENCY_HISTOGRAM,
    )
    _check_equal(
        errors,
        "selected-indegree value histogram",
        summary["selected_indegree_value_histogram"],
        EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
    )
    _check_equal(
        errors,
        "assignment witness-pair profiles",
        summary["assignment_witness_pair_profiles"],
        EXPECTED_ASSIGNMENT_WITNESS_PAIR_PROFILES,
    )
    for key in (
        "row_shape_errors",
        "center_coverage_errors",
        "intersection_cap_violations",
        "two_overlap_crossing_violations",
        "witness_pair_cap_violations",
        "selected_indegree_cap_violations",
    ):
        _check_equal(errors, key, summary[key], 0)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "max_selected_indegree": MAX_SELECTED_INDEGREE,
        "frontier_assignment_audit": summary,
        "source_artifact": _source_metadata(frontier_path, frontier),
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the stored 184 n=9 pre-vertex-circle "
            "frontier assignments satisfy the direct row-shape, crossing, "
            "witness-pair capacity, and selected-indegree capacity predicates "
            "checked here. This is a stored-frontier diagnostic only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_frontier_assignment_audit(payload: Mapping[str, Any]) -> None:
    """Assert the expected stored-frontier assignment audit result."""

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
        "does not prove frontier coverage",
        "brancher soundness",
        "strict-edge geometry",
        "selected-distance quotient soundness",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    summary = payload.get("frontier_assignment_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("frontier_assignment_audit missing")
    expected = {
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "row_count_total": EXPECTED_ROW_COUNT_TOTAL,
        "status_counts": EXPECTED_STATUS_COUNTS,
        "center_pair_intersection_histogram": EXPECTED_CENTER_PAIR_INTERSECTION_HISTOGRAM,
        "two_overlap_crossing_count": EXPECTED_TWO_OVERLAP_CROSSING_COUNT,
        "witness_pair_frequency_histogram": EXPECTED_WITNESS_PAIR_FREQUENCY_HISTOGRAM,
        "selected_indegree_value_histogram": EXPECTED_SELECTED_INDEGREE_VALUE_HISTOGRAM,
        "assignment_witness_pair_profiles": EXPECTED_ASSIGNMENT_WITNESS_PAIR_PROFILES,
        "row_shape_errors": 0,
        "center_coverage_errors": 0,
        "intersection_cap_violations": 0,
        "two_overlap_crossing_violations": 0,
        "witness_pair_cap_violations": 0,
        "selected_indegree_cap_violations": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _audit_frontier_assignments(
    frontier: Mapping[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    assignments = frontier.get("assignments")
    if not isinstance(assignments, list):
        raise ValueError("frontier classification artifact must contain assignments")

    row_count_total = 0
    row_shape_errors = 0
    center_coverage_errors = 0
    intersection_cap_violations = 0
    two_overlap_crossing_violations = 0
    witness_pair_cap_violations = 0
    selected_indegree_cap_violations = 0
    two_overlap_crossing_count = 0
    status_counts: Counter[str] = Counter()
    center_pair_intersection_histogram: Counter[int] = Counter()
    witness_pair_frequency_histogram: Counter[int] = Counter()
    selected_indegree_value_histogram: Counter[int] = Counter()
    assignment_witness_pair_profiles: Counter[str] = Counter()
    example_errors: list[dict[str, Any]] = []

    for index, assignment in enumerate(assignments, start=1):
        if not isinstance(assignment, Mapping):
            row_shape_errors += 1
            _record_example(example_errors, f"A{index:03d}", "assignment row is not an object")
            continue
        assignment_id = str(assignment.get("assignment_id", f"A{index:03d}"))
        status_counts[str(assignment.get("status"))] += 1
        rows, row_errors = _compact_rows(assignment)
        row_count_total += len(rows)
        if row_errors:
            row_shape_errors += len(row_errors)
            for error in row_errors:
                _record_example(example_errors, assignment_id, error)
            continue
        if set(rows) != set(range(N)):
            center_coverage_errors += 1
            _record_example(example_errors, assignment_id, "centers are not exactly 0..8")

        for center_i, center_j in combinations(range(N), 2):
            common = set(rows[center_i]) & set(rows[center_j])
            center_pair_intersection_histogram[len(common)] += 1
            if len(common) > PAIR_CAP:
                intersection_cap_violations += 1
                _record_example(
                    example_errors,
                    assignment_id,
                    f"rows {center_i},{center_j} share {len(common)} witnesses",
                )
            elif len(common) == PAIR_CAP:
                source = pair(center_i, center_j)
                target = pair(*tuple(common))
                if chords_cross(source, target):
                    two_overlap_crossing_count += 1
                else:
                    two_overlap_crossing_violations += 1
                    _record_example(
                        example_errors,
                        assignment_id,
                        f"rows {center_i},{center_j} share noncrossing pair {target}",
                    )

        witness_pair_counts: Counter[Pair] = Counter()
        selected_indegrees: Counter[int] = Counter()
        for center, witnesses in rows.items():
            for witness in witnesses:
                selected_indegrees[witness] += 1
            for left, right in combinations(witnesses, 2):
                witness_pair_counts[pair(left, right)] += 1

        pair_frequency_profile = Counter()
        for witness_pair in all_pairs():
            frequency = witness_pair_counts[witness_pair]
            witness_pair_frequency_histogram[frequency] += 1
            pair_frequency_profile[frequency] += 1
            if frequency > PAIR_CAP:
                witness_pair_cap_violations += 1
                _record_example(
                    example_errors,
                    assignment_id,
                    f"witness pair {witness_pair} has frequency {frequency}",
                )
        assignment_witness_pair_profiles[_profile_key(pair_frequency_profile)] += 1

        for label in range(N):
            indegree = selected_indegrees[label]
            selected_indegree_value_histogram[indegree] += 1
            if indegree > MAX_SELECTED_INDEGREE:
                selected_indegree_cap_violations += 1
                _record_example(
                    example_errors,
                    assignment_id,
                    f"label {label} has selected indegree {indegree}",
                )

    if row_shape_errors:
        errors.append(f"row shape errors: {row_shape_errors}")
    if center_coverage_errors:
        errors.append(f"center coverage errors: {center_coverage_errors}")
    if intersection_cap_violations:
        errors.append(f"intersection cap violations: {intersection_cap_violations}")
    if two_overlap_crossing_violations:
        errors.append(f"two-overlap crossing violations: {two_overlap_crossing_violations}")
    if witness_pair_cap_violations:
        errors.append(f"witness-pair cap violations: {witness_pair_cap_violations}")
    if selected_indegree_cap_violations:
        errors.append(f"selected-indegree cap violations: {selected_indegree_cap_violations}")

    return {
        "assignment_count": len(assignments),
        "row_count_total": row_count_total,
        "status_counts": dict(sorted(status_counts.items())),
        "row_shape_errors": row_shape_errors,
        "center_coverage_errors": center_coverage_errors,
        "intersection_cap_violations": intersection_cap_violations,
        "two_overlap_crossing_violations": two_overlap_crossing_violations,
        "witness_pair_cap_violations": witness_pair_cap_violations,
        "selected_indegree_cap_violations": selected_indegree_cap_violations,
        "center_pair_intersection_histogram": dict(sorted(center_pair_intersection_histogram.items())),
        "two_overlap_crossing_count": two_overlap_crossing_count,
        "witness_pair_frequency_histogram": dict(sorted(witness_pair_frequency_histogram.items())),
        "selected_indegree_value_histogram": dict(sorted(selected_indegree_value_histogram.items())),
        "assignment_witness_pair_profiles": dict(sorted(assignment_witness_pair_profiles.items())),
        "example_errors": example_errors,
    }


def _compact_rows(assignment: Mapping[str, Any]) -> tuple[CompactRows, list[str]]:
    raw_rows = assignment.get("selected_rows")
    rows: CompactRows = {}
    errors: list[str] = []
    if not isinstance(raw_rows, list):
        return rows, ["selected_rows is not a list"]
    for index, raw_row in enumerate(raw_rows):
        if (
            not isinstance(raw_row, list)
            or len(raw_row) != ROW_SIZE + 1
            or not all(isinstance(value, int) for value in raw_row)
        ):
            errors.append(f"selected row {index} is not [center,w1,w2,w3,w4]")
            continue
        center = int(raw_row[0])
        witnesses = tuple(int(value) for value in raw_row[1:])
        if not 0 <= center < N:
            errors.append(f"selected row {index} has invalid center {center}")
            continue
        if center in rows:
            errors.append(f"duplicate selected row for center {center}")
        if len(set(witnesses)) != ROW_SIZE:
            errors.append(f"center {center} has duplicate witnesses")
        if any(not 0 <= witness < N for witness in witnesses):
            errors.append(f"center {center} has out-of-range witnesses")
        if center in witnesses:
            errors.append(f"center {center} selects itself")
        if tuple(sorted(witnesses)) != witnesses:
            errors.append(f"center {center} witnesses are not sorted")
        rows[center] = witnesses
    return rows, errors


def pair(left: int, right: int) -> Pair:
    """Return a normalized unordered pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def all_pairs() -> list[Pair]:
    """Return all unordered vertex pairs."""

    return [(left, right) for left in range(N) for right in range(left + 1, N)]


def in_open_arc(left: int, right: int, item: int) -> bool:
    """Return whether item lies strictly on the cyclic arc left -> right."""

    return ((item - left) % N) < ((right - left) % N) and item != left and item != right


def chords_cross(first: Pair, second: Pair) -> bool:
    """Return whether two disjoint chords cross in the natural cyclic order."""

    left, right = first
    a, b = second
    if len({left, right, a, b}) < 4:
        return False
    return in_open_arc(left, right, a) != in_open_arc(left, right, b)


def _profile_key(profile: Mapping[int, int]) -> str:
    return "|".join(f"{frequency}:{profile[frequency]}" for frequency in sorted(profile))


def _source_metadata(path: Path, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": str(path.relative_to(ROOT)).replace("\\", "/"),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _record_example(
    examples: list[dict[str, Any]],
    assignment_id: str,
    message: str,
) -> None:
    if len(examples) < 10:
        examples.append({"assignment_id": assignment_id, "message": message})


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without example errors."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audit = payload.get("frontier_assignment_audit")
    if isinstance(audit, Mapping):
        summary["frontier_assignment_audit_summary"] = {
            key: audit[key] for key in FRONTIER_ASSIGNMENT_SUMMARY_KEYS if key in audit
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["frontier_assignment_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"assignments checked: {summary['assignment_count']}",
        f"row count total: {summary['row_count_total']}",
        f"two-overlap crossing violations: {summary['two_overlap_crossing_violations']}",
        f"witness-pair cap violations: {summary['witness_pair_cap_violations']}",
        f"selected-indegree cap violations: {summary['selected_indegree_cap_violations']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--frontier-classification",
        type=Path,
        default=DEFAULT_FRONTIER_CLASSIFICATION,
    )
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without example errors",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    frontier_path = (
        args.frontier_classification
        if args.frontier_classification.is_absolute()
        else ROOT / args.frontier_classification
    )
    payload = frontier_assignment_audit_payload(frontier_path=frontier_path)

    if args.assert_expected:
        assert_expected_frontier_assignment_audit(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle frontier assignment audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 frontier assignment audit checks passed")
    else:
        print("FAILED: n=9 frontier assignment audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
