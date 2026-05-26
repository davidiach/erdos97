#!/usr/bin/env python3
"""Replay n=9 vertex-circle row-level incidence filter audits."""

from __future__ import annotations

import argparse
import itertools
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

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_incidence_filters.v1"
STATUS = "REVIEW_PENDING_INCIDENCE_FILTER_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Row-level incidence filter audit for the review-pending n=9 "
    "vertex-circle checker. It checks the two-overlap crossing table, "
    "witness-pair cap table, and selected-indegree cap predicate. It does "
    "not replay the brancher, strict-edge geometry, selected-distance "
    "quotient, n=9, a counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_incidence_filters.py",
    "command": (
        "python scripts/check_n9_vertex_circle_incidence_filters.py "
        "--check --assert-expected --json"
    ),
}

EXPECTED_TWO_OVERLAP = {
    "chord_cross_equivalence_mismatches": 0,
    "compatibility_errors": 0,
    "row_pair_candidate_overlap_histogram": {0: 7_560, 1: 57_960, 2: 83_160, 3: 26_460, 4: 1_260},
    "two_overlap_crossing_accepted": 27_720,
    "two_overlap_noncrossing_rejected": 55_440,
}
EXPECTED_WITNESS_PAIR_CAP = {
    "unique_row_masks": 126,
    "row_pair_index_mismatches": 0,
    "rows_with_non_six_pair_indices": 0,
    "local_cap_profiles_tested": 91_854,
    "local_cap_predicate_mismatches": 0,
    "increment_decrement_roundtrip_errors": 0,
    "witness_pair_frequency_histogram": {21: 36},
}
EXPECTED_SELECTED_INDEGREE = {
    "max_indegree_formula": 5,
    "checker_max_indegree": 5,
    "unique_row_masks": 126,
    "row_mask_shape_errors": 0,
    "local_column_profiles_tested": 163_296,
    "local_column_predicate_mismatches": 0,
    "increment_decrement_roundtrip_errors": 0,
    "label_frequency_histogram": {56: 9},
}


def incidence_filter_payload() -> dict[str, Any]:
    """Return replay audits for n=9 row-level incidence filters."""

    errors: list[str] = []
    two_overlap = two_overlap_crossing_audit()
    witness_pair = witness_pair_cap_audit()
    selected_indegree = selected_indegree_cap_audit()

    _check_section(errors, "two_overlap_crossing", two_overlap, EXPECTED_TWO_OVERLAP)
    _check_section(errors, "witness_pair_cap", witness_pair, EXPECTED_WITNESS_PAIR_CAP)
    _check_section(
        errors,
        "selected_indegree_cap",
        selected_indegree,
        EXPECTED_SELECTED_INDEGREE,
    )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "pair_cap": n9.PAIR_CAP,
        "max_indegree": n9.MAX_INDEGREE,
        "two_overlap_crossing": two_overlap,
        "witness_pair_cap": witness_pair,
        "selected_indegree_cap": selected_indegree,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the n=9 checker's row-level incidence "
            "filter tables match direct finite predicates for two-overlap "
            "crossing, witness-pair capacity, and selected-indegree capacity. "
            "It does not audit the brancher or vertex-circle pruning."
        ),
        "provenance": dict(PROVENANCE),
    }


def two_overlap_crossing_audit() -> dict[str, Any]:
    """Replay the row-pair crossing compatibility table."""

    chord_mismatches = 0
    for first in n9.PAIRS:
        for second in n9.PAIRS:
            if n9.chords_cross(first, second) != _direct_chords_cross(first, second):
                chord_mismatches += 1

    compatibility_errors = 0
    overlap_histogram: Counter[int] = Counter()
    crossing_accepted = 0
    noncrossing_rejected = 0
    for i in range(n9.N):
        for j in range(i + 1, n9.N):
            source = n9.pair(i, j)
            for mask_i in n9.OPTIONS[i]:
                row_i = set(n9.MASK_BITS[mask_i])
                for mask_j in n9.OPTIONS[j]:
                    common = row_i & set(n9.MASK_BITS[mask_j])
                    common_count = len(common)
                    overlap_histogram[common_count] += 1
                    direct_ok = common_count <= n9.PAIR_CAP
                    if common_count == n9.PAIR_CAP:
                        target = n9.pair(*tuple(common))
                        direct_ok = _direct_chords_cross(source, target)
                        if direct_ok:
                            crossing_accepted += 1
                        else:
                            noncrossing_rejected += 1
                    if n9.rows_compatible(i, mask_i, j, mask_j) != direct_ok:
                        compatibility_errors += 1

    return {
        "chord_cross_equivalence_mismatches": chord_mismatches,
        "compatibility_errors": compatibility_errors,
        "row_pair_candidate_overlap_histogram": dict(sorted(overlap_histogram.items())),
        "two_overlap_crossing_accepted": crossing_accepted,
        "two_overlap_noncrossing_rejected": noncrossing_rejected,
    }


def witness_pair_cap_audit() -> dict[str, Any]:
    """Replay witness-pair index and partial cap predicates."""

    unique_masks = _unique_row_masks()
    row_pair_index_mismatches = 0
    rows_with_non_six_pair_indices = 0
    local_profiles_tested = 0
    local_predicate_mismatches = 0
    roundtrip_errors = 0
    pair_frequencies: Counter[int] = Counter()

    for row_mask in unique_masks:
        direct_indices = _direct_row_pair_indices(row_mask)
        checker_indices = n9.ROW_PAIR_INDICES[row_mask]
        if direct_indices != checker_indices:
            row_pair_index_mismatches += 1
        if len(checker_indices) != 6:
            rows_with_non_six_pair_indices += 1
        pair_frequencies.update(checker_indices)
        for profile in itertools.product(range(n9.PAIR_CAP + 1), repeat=6):
            local_profiles_tested += 1
            direct_reject = any(count >= n9.PAIR_CAP for count in profile)
            checker_reject = any(count >= n9.PAIR_CAP for count in profile)
            if direct_reject != checker_reject:
                local_predicate_mismatches += 1
        counts = [0] * len(n9.PAIRS)
        for pair_idx in checker_indices:
            counts[pair_idx] += 1
        for pair_idx in checker_indices:
            counts[pair_idx] -= 1
        if any(count != 0 for count in counts):
            roundtrip_errors += 1

    frequency_histogram = Counter(pair_frequencies.values())
    return {
        "unique_row_masks": len(unique_masks),
        "row_pair_index_mismatches": row_pair_index_mismatches,
        "rows_with_non_six_pair_indices": rows_with_non_six_pair_indices,
        "local_cap_profiles_tested": local_profiles_tested,
        "local_cap_predicate_mismatches": local_predicate_mismatches,
        "increment_decrement_roundtrip_errors": roundtrip_errors,
        "witness_pair_frequency_histogram": dict(sorted(frequency_histogram.items())),
    }


def selected_indegree_cap_audit() -> dict[str, Any]:
    """Replay selected-indegree formula and partial cap predicates."""

    unique_masks = _unique_row_masks()
    formula = (n9.PAIR_CAP * (n9.N - 1)) // (n9.ROW_SIZE - 1)
    row_mask_shape_errors = 0
    local_profiles_tested = 0
    local_predicate_mismatches = 0
    roundtrip_errors = 0
    label_frequencies: Counter[int] = Counter()

    for row_mask in unique_masks:
        witnesses = n9.MASK_BITS[row_mask]
        if len(witnesses) != n9.ROW_SIZE:
            row_mask_shape_errors += 1
        label_frequencies.update(witnesses)
        for profile in itertools.product(range(n9.MAX_INDEGREE + 1), repeat=n9.ROW_SIZE):
            local_profiles_tested += 1
            direct_reject = any(count >= formula for count in profile)
            checker_reject = any(count >= n9.MAX_INDEGREE for count in profile)
            if direct_reject != checker_reject:
                local_predicate_mismatches += 1
        counts = [0] * n9.N
        for witness in witnesses:
            counts[witness] += 1
        for witness in witnesses:
            counts[witness] -= 1
        if any(count != 0 for count in counts):
            roundtrip_errors += 1

    frequency_histogram = Counter(label_frequencies.values())
    return {
        "max_indegree_formula": formula,
        "checker_max_indegree": n9.MAX_INDEGREE,
        "unique_row_masks": len(unique_masks),
        "row_mask_shape_errors": row_mask_shape_errors,
        "local_column_profiles_tested": local_profiles_tested,
        "local_column_predicate_mismatches": local_predicate_mismatches,
        "increment_decrement_roundtrip_errors": roundtrip_errors,
        "label_frequency_histogram": dict(sorted(frequency_histogram.items())),
    }


def assert_expected_incidence_filters(payload: Mapping[str, Any]) -> None:
    """Assert the expected incidence-filter audit result."""

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
        "does not replay the brancher",
        "strict-edge geometry",
        "selected-distance quotient",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    _assert_section("two_overlap_crossing", payload, EXPECTED_TWO_OVERLAP)
    _assert_section("witness_pair_cap", payload, EXPECTED_WITNESS_PAIR_CAP)
    _assert_section("selected_indegree_cap", payload, EXPECTED_SELECTED_INDEGREE)


def _direct_row_pair_indices(row_mask: int) -> list[int]:
    return [
        n9.PAIR_INDEX[n9.pair(a, b)]
        for a, b in combinations(n9.MASK_BITS[row_mask], 2)
    ]


def _direct_chords_cross(first: tuple[int, int], second: tuple[int, int]) -> bool:
    a, b = first
    c, d = second
    if len({a, b, c, d}) < 4:
        return False
    return _in_open_arc(a, b, c) != _in_open_arc(a, b, d)


def _in_open_arc(a: int, b: int, x: int) -> bool:
    return ((x - a) % n9.N) < ((b - a) % n9.N) and x != a and x != b


def _unique_row_masks() -> list[int]:
    return sorted({row_mask for options in n9.OPTIONS for row_mask in options})


def _check_section(
    errors: list[str],
    name: str,
    section: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    for key, value in expected.items():
        if section.get(key) != value:
            errors.append(f"{name} {key} mismatch: {section.get(key)!r} != {value!r}")


def _assert_section(
    name: str,
    payload: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    section = payload.get(name)
    if not isinstance(section, Mapping):
        raise AssertionError(f"{name} section missing")
    errors: list[str] = []
    _check_section(errors, name, section, expected)
    if errors:
        raise AssertionError("; ".join(errors))


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        "compatibility errors: "
        f"{payload['two_overlap_crossing']['compatibility_errors']}",
        "witness-pair cap predicate mismatches: "
        f"{payload['witness_pair_cap']['local_cap_predicate_mismatches']}",
        "selected-indegree predicate mismatches: "
        f"{payload['selected_indegree_cap']['local_column_predicate_mismatches']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="emit JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = incidence_filter_payload()

    if args.assert_expected:
        assert_expected_incidence_filters(payload)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle incidence filter audits")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 incidence filter audit checks passed")
    else:
        print("FAILED: n=9 incidence filter audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
