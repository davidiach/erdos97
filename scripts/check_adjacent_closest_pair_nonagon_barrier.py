#!/usr/bin/env python3
"""Check the adjacent closest-pair nonagon barrier.

This is a finite combinatorial audit for one structural subcase. It does not
prove n=9, does not prove Erdos Problem #97, and does not produce a
counterexample.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from itertools import combinations
from typing import Any, Sequence

SCHEMA = "erdos97.adjacent_closest_pair_nonagon_barrier.v1"
STATUS = "LEMMA_COMBINATORIAL_AUDIT_ONLY"
TRUST = "LEMMA"
N = 9
ROW_SIZE = 4
ORDER = tuple(range(N))
ADJACENT_CLOSEST_PAIR = (0, 1)
BOUNDARY_CENTERS = (0, 1, 2, 8)
CLAIM_SCOPE = (
    "Finite combinatorial audit of the adjacent closest-pair n=9 boundary. "
    "It enumerates selected witness rows at centers 0, 1, 2, and 8 under the "
    "closest-pair endpoint exclusions, two-circle row-pair cap, and "
    "two-overlap crossing-bisector rule. It checks only the conditional "
    "subcase where a globally closest pair is a polygon side; it does not "
    "prove n=9, does not prove Erdos Problem #97, does not claim a "
    "counterexample, and does not update the official/global status."
)

EXPECTED_SUMMARY = {
    "n": 9,
    "row_size": 4,
    "adjacent_closest_pair": [0, 1],
    "endpoint_pair_count": 140,
    "endpoint_pair_union_saturation_count": 140,
    "endpoint_pair_intersection_histogram": {"1": 140},
    "v2_candidate_count": 900,
    "v2_forced_closest_pair_endpoint_count": 900,
    "v2_option_count_distribution": {"6": 120, "9": 20},
    "v8_candidate_count": 900,
    "v8_forced_closest_pair_endpoint_count": 900,
    "v8_option_count_distribution": {"6": 120, "9": 20},
    "partial_frontier_count_before_final_pair": 5760,
    "final_pair_rejection_counts": {
        "row_pair_cap": 3120,
        "two_overlap_crossing": 2640,
    },
    "final_pair_overlap_histogram": {"2": 2640, "3": 2520, "4": 600},
    "complete_assignment_count": 0,
}

Row = tuple[int, ...]
Pair = tuple[int, int]


def normalize_pair(left: int, right: int) -> Pair:
    """Return an unordered non-loop pair."""

    if left == right:
        raise ValueError(f"loop pair is not allowed: {left}")
    return (left, right) if left < right else (right, left)


def chords_cross_in_natural_order(left: Pair, right: Pair) -> bool:
    """Return whether two disjoint chords cross in cyclic order 0,...,8."""

    if set(left) & set(right):
        return False
    a, b = sorted(left)
    c, d = sorted(right)
    return (a < c < b < d) or (c < a < d < b)


def row_pair_rejection(
    left_center: int,
    left_row: Sequence[int],
    right_center: int,
    right_row: Sequence[int],
) -> str | None:
    """Return the exact row-pair reason rejecting two selected rows."""

    overlap = sorted(set(left_row) & set(right_row))
    if len(overlap) > 2:
        return "row_pair_cap"
    if len(overlap) == 2:
        source = normalize_pair(left_center, right_center)
        witness = normalize_pair(overlap[0], overlap[1])
        if not chords_cross_in_natural_order(source, witness):
            return "two_overlap_crossing"
    return None


def row_pair_is_compatible(
    left_center: int,
    left_row: Sequence[int],
    right_center: int,
    right_row: Sequence[int],
) -> bool:
    """Return whether the row pair passes the cap and crossing filters."""

    return row_pair_rejection(left_center, left_row, right_center, right_row) is None


def row_options(center: int, *, n: int = N, row_size: int = ROW_SIZE) -> tuple[Row, ...]:
    """Return all selected witness rows of size ``row_size`` for ``center``."""

    if center < 0 or center >= n:
        raise ValueError(f"center out of range: {center}")
    return tuple(
        tuple(row)
        for row in combinations((label for label in range(n) if label != center), row_size)
    )


def endpoint_pair_is_compatible(row0: Row, row1: Row) -> bool:
    """Check the closest-pair endpoint exclusions and row-pair filter."""

    return (
        1 not in row0
        and 0 not in row1
        and row_pair_is_compatible(0, row0, 1, row1)
    )


def compatible_boundary_rows(center: int, row0: Row, row1: Row) -> list[Row]:
    """Return rows at ``center`` compatible with the two closest-pair endpoints."""

    return [
        row
        for row in row_options(center)
        if row_pair_is_compatible(0, row0, center, row)
        and row_pair_is_compatible(1, row1, center, row)
    ]


def _counter_json(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter, key=str)}


def _row_json(row: Sequence[int]) -> list[int]:
    return [int(label) for label in row]


def build_payload() -> dict[str, Any]:
    """Build the finite audit payload."""

    rows0 = row_options(0)
    rows1 = row_options(1)
    endpoint_pairs: list[tuple[Row, Row]] = []
    endpoint_pair_intersections: Counter[int] = Counter()
    endpoint_pair_union_saturation_count = 0
    v2_count_distribution: Counter[int] = Counter()
    v8_count_distribution: Counter[int] = Counter()
    final_pair_rejections: Counter[str] = Counter()
    final_pair_overlap_histogram: Counter[int] = Counter()
    v2_candidate_count = 0
    v2_forced_closest_pair_endpoint_count = 0
    v8_candidate_count = 0
    v8_forced_closest_pair_endpoint_count = 0
    partial_frontier_count = 0
    complete_assignment_count = 0
    first_partial_record: dict[str, Any] | None = None
    first_final_rejection_examples: dict[str, dict[str, Any]] = {}

    other_endpoint_labels = set(range(2, N))
    closest_pair_endpoints = set(ADJACENT_CLOSEST_PAIR)

    for row0 in rows0:
        for row1 in rows1:
            if not endpoint_pair_is_compatible(row0, row1):
                continue
            endpoint_pairs.append((row0, row1))
            endpoint_intersection = len(set(row0) & set(row1))
            endpoint_pair_intersections[endpoint_intersection] += 1
            if set(row0) | set(row1) == other_endpoint_labels:
                endpoint_pair_union_saturation_count += 1

            v2_options = compatible_boundary_rows(2, row0, row1)
            v8_options = compatible_boundary_rows(8, row0, row1)
            v2_count_distribution[len(v2_options)] += 1
            v8_count_distribution[len(v8_options)] += 1

            for row2 in v2_options:
                v2_candidate_count += 1
                if closest_pair_endpoints <= set(row2):
                    v2_forced_closest_pair_endpoint_count += 1
            for row8 in v8_options:
                v8_candidate_count += 1
                if closest_pair_endpoints <= set(row8):
                    v8_forced_closest_pair_endpoint_count += 1

            for row2 in v2_options:
                for row8 in v8_options:
                    partial_frontier_count += 1
                    rejection = row_pair_rejection(2, row2, 8, row8)
                    overlap = sorted(set(row2) & set(row8))
                    final_pair_overlap_histogram[len(overlap)] += 1
                    if first_partial_record is None:
                        first_partial_record = {
                            "S0": _row_json(row0),
                            "S1": _row_json(row1),
                            "S2": _row_json(row2),
                            "S8": _row_json(row8),
                            "S2_cap_S8": _row_json(overlap),
                        }
                    if rejection is None:
                        complete_assignment_count += 1
                    else:
                        final_pair_rejections[rejection] += 1
                        first_final_rejection_examples.setdefault(
                            rejection,
                            {
                                "S0": _row_json(row0),
                                "S1": _row_json(row1),
                                "S2": _row_json(row2),
                                "S8": _row_json(row8),
                                "S2_cap_S8": _row_json(overlap),
                                "rejection": rejection,
                            },
                        )

    summary = {
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(ORDER),
        "adjacent_closest_pair": list(ADJACENT_CLOSEST_PAIR),
        "boundary_centers": list(BOUNDARY_CENTERS),
        "endpoint_pair_count": len(endpoint_pairs),
        "endpoint_pair_union_saturation_count": endpoint_pair_union_saturation_count,
        "endpoint_pair_intersection_histogram": _counter_json(
            endpoint_pair_intersections
        ),
        "v2_candidate_count": v2_candidate_count,
        "v2_forced_closest_pair_endpoint_count": (
            v2_forced_closest_pair_endpoint_count
        ),
        "v2_option_count_distribution": _counter_json(v2_count_distribution),
        "v8_candidate_count": v8_candidate_count,
        "v8_forced_closest_pair_endpoint_count": (
            v8_forced_closest_pair_endpoint_count
        ),
        "v8_option_count_distribution": _counter_json(v8_count_distribution),
        "partial_frontier_count_before_final_pair": partial_frontier_count,
        "final_pair_rejection_counts": _counter_json(final_pair_rejections),
        "final_pair_overlap_histogram": _counter_json(final_pair_overlap_histogram),
        "complete_assignment_count": complete_assignment_count,
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "first_partial_record": first_partial_record,
        "first_final_rejection_examples": first_final_rejection_examples,
        "interpretation": (
            "Every compatible endpoint pair saturates the seven non-endpoint "
            "labels; every compatible row at v2 and v8 contains both closest "
            "pair endpoints 0 and 1; the final row pair S2,S8 is always "
            "rejected by either the row-pair cap or the two-overlap crossing "
            "rule. Thus the adjacent closest-pair n=9 boundary has no "
            "selected-witness realization under these necessary conditions."
        ),
    }


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for the computed audit payload."""

    errors: list[str] = []
    if payload.get("schema") != SCHEMA:
        errors.append(f"schema is {payload.get('schema')!r}, expected {SCHEMA!r}")
    if payload.get("status") != STATUS:
        errors.append(f"status is {payload.get('status')!r}, expected {STATUS!r}")
    if payload.get("trust") != TRUST:
        errors.append(f"trust is {payload.get('trust')!r}, expected {TRUST!r}")
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        for phrase in (
            "does not prove n=9",
            "does not prove Erdos Problem #97",
            "does not claim a counterexample",
            "does not update the official/global status",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must include {phrase!r}")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary must be a mapping")
        return errors
    for key, expected in EXPECTED_SUMMARY.items():
        observed = summary.get(key)
        if observed != expected:
            errors.append(f"summary.{key} is {observed!r}, expected {expected!r}")
    if summary.get("complete_assignment_count") != 0:
        errors.append("complete_assignment_count must be 0")
    return errors


def summary_payload(payload: dict[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    """Return compact JSON for docs and CI output."""

    summary = payload.get("summary", {})
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "n": summary.get("n"),
        "adjacent_closest_pair": summary.get("adjacent_closest_pair"),
        "endpoint_pair_count": summary.get("endpoint_pair_count"),
        "endpoint_pair_union_saturation_count": summary.get(
            "endpoint_pair_union_saturation_count"
        ),
        "v2_forced_closest_pair_endpoint_count": summary.get(
            "v2_forced_closest_pair_endpoint_count"
        ),
        "v8_forced_closest_pair_endpoint_count": summary.get(
            "v8_forced_closest_pair_endpoint_count"
        ),
        "partial_frontier_count_before_final_pair": summary.get(
            "partial_frontier_count_before_final_pair"
        ),
        "final_pair_rejection_counts": summary.get("final_pair_rejection_counts"),
        "complete_assignment_count": summary.get("complete_assignment_count"),
        "validation_status": "passed" if not errors else "failed",
        "validation_error_count": len(errors),
        "first_validation_errors": list(errors[:5]),
    }


def render_markdown(payload: dict[str, Any], errors: Sequence[str]) -> str:
    """Render a small reviewer-facing note."""

    summary = payload.get("summary", {})
    status = "passed" if not errors else "failed"
    lines = [
        "# Adjacent Closest-Pair Nonagon Barrier Check",
        "",
        f"Status: `{payload.get('status')}`.",
        "",
        str(payload.get("claim_scope", "")).strip(),
        "",
        "## Result",
        "",
        f"- Validation status: `{status}`",
        f"- Endpoint row pairs: `{summary.get('endpoint_pair_count')}`",
        "- Partial boundary assignments before the final row-pair check: "
        f"`{summary.get('partial_frontier_count_before_final_pair')}`",
        f"- Complete assignments: `{summary.get('complete_assignment_count')}`",
        "",
        "## Boundary",
        "",
        "This checks only the adjacent closest-pair nonagon subcase. A "
        "hypothetical nonagon whose globally closest pairs are all diagonals "
        "is outside this checker.",
        "",
    ]
    return "\n".join(lines)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail on validation errors")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact JSON",
    )
    output_group.add_argument("--markdown", action="store_true", help="print Markdown")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_payload()
    errors = validate_payload(payload)

    if args.markdown:
        print(render_markdown(payload, errors))
    elif args.summary_json:
        print(json.dumps(summary_payload(payload, errors), indent=2, sort_keys=True))
    elif args.json:
        full_payload = dict(payload)
        full_payload["validation_status"] = "passed" if not errors else "failed"
        full_payload["validation_errors"] = errors
        print(json.dumps(full_payload, indent=2, sort_keys=True))
    else:
        print("adjacent closest-pair nonagon barrier")
        print(f"validation_status: {'passed' if not errors else 'failed'}")

    if args.check and errors:
        for error in errors:
            print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
