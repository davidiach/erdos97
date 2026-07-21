#!/usr/bin/env python3
"""Replay the n=9 vertex-circle strict-edge geometry rule."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from typing import Any, Mapping, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.vertex_circle_quotient_replay import (
    SelectedRow,
    pair,
    replay_vertex_circle_quotient,
)

SCHEMA = "erdos97.n9_vertex_circle_strict_edge_geometry.v1"
STATUS = "REVIEW_PENDING_GEOMETRY_RULE_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Strict-edge geometry rule audit for the review-pending n=9 "
    "vertex-circle checker. It independently enumerates proper interval "
    "containments for every candidate selected row and compares them to the "
    "checker strict-edge table. It does not prove row coverage, brancher "
    "coverage, selected-distance quotient soundness, n=9, a counterexample, "
    "or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_strict_edge_geometry.py",
    "command": (
        "python scripts/check_n9_vertex_circle_strict_edge_geometry.py "
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
    "selected_rows_checked",
    "strict_edge_mismatches",
    "quotient_replay_strict_edge_mismatches",
    "strict_edges_per_row",
    "interval_span_histogram",
    "total_strict_edges",
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)

EXPECTED_SELECTED_ROWS = 630
EXPECTED_STRICT_EDGES_PER_ROW = {9: 630}
EXPECTED_SPAN_HISTOGRAM = {
    "2->1": 2_520,
    "3->1": 1_890,
    "3->2": 1_260,
}
EXPECTED_TOTAL_STRICT_EDGES = 5_670


def direct_strict_edges(center: int, row_mask: int) -> list[tuple[int, int]]:
    """Return direct proper-interval strict edges for one selected row."""

    witnesses = sorted(n9.MASK_BITS[row_mask], key=lambda witness: (witness - center) % n9.N)
    edges: list[tuple[int, int]] = []
    for outer_start in range(n9.ROW_SIZE):
        for outer_end in range(outer_start + 1, n9.ROW_SIZE):
            for inner_start in range(n9.ROW_SIZE):
                for inner_end in range(inner_start + 1, n9.ROW_SIZE):
                    if (outer_start, outer_end) == (inner_start, inner_end):
                        continue
                    if not _properly_contains(
                        outer_start,
                        outer_end,
                        inner_start,
                        inner_end,
                    ):
                        continue
                    outer = pair(witnesses[outer_start], witnesses[outer_end])
                    inner = pair(witnesses[inner_start], witnesses[inner_end])
                    edges.append((n9.PAIR_INDEX[outer], n9.PAIR_INDEX[inner]))
    return edges


def strict_edge_geometry_payload() -> dict[str, Any]:
    """Return a replay audit for the n=9 strict-edge geometry table."""

    errors: list[str] = []
    selected_rows_checked = 0
    mismatch_count = 0
    strict_edges_per_row: Counter[int] = Counter()
    span_histogram: Counter[str] = Counter()
    quotient_replay_strict_edge_mismatches = 0
    example_mismatches: list[dict[str, Any]] = []

    for center in range(n9.N):
        for row_mask in n9.OPTIONS[center]:
            selected_rows_checked += 1
            direct = direct_strict_edges(center, row_mask)
            checker = n9.STRICT_EDGES[(center, row_mask)]
            if direct != checker:
                mismatch_count += 1
                if len(example_mismatches) < 5:
                    example_mismatches.append(
                        {
                            "center": center,
                            "witnesses": n9.MASK_BITS[row_mask],
                            "direct": direct,
                            "checker": checker,
                        }
                    )
            strict_edges_per_row[len(direct)] += 1
            _add_span_histogram(center, row_mask, span_histogram)

            replay_result = replay_vertex_circle_quotient(
                n9.N,
                n9.ORDER,
                [
                    SelectedRow(
                        center=center,
                        witnesses=tuple(n9.MASK_BITS[row_mask]),
                    )
                ],
            )
            if replay_result.strict_edge_count != len(direct):
                quotient_replay_strict_edge_mismatches += 1

    total_strict_edges = sum(length * count for length, count in strict_edges_per_row.items())
    _check_equal(errors, "selected rows checked", selected_rows_checked, EXPECTED_SELECTED_ROWS)
    _check_equal(errors, "strict edge mismatches", mismatch_count, 0)
    _check_equal(
        errors,
        "quotient replay strict-edge mismatches",
        quotient_replay_strict_edge_mismatches,
        0,
    )
    _check_equal(
        errors,
        "strict edges per row",
        dict(sorted(strict_edges_per_row.items())),
        EXPECTED_STRICT_EDGES_PER_ROW,
    )
    _check_equal(
        errors,
        "span histogram",
        dict(sorted(span_histogram.items())),
        EXPECTED_SPAN_HISTOGRAM,
    )
    _check_equal(errors, "total strict edges", total_strict_edges, EXPECTED_TOTAL_STRICT_EDGES)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": n9.N,
        "row_size": n9.ROW_SIZE,
        "selected_rows_checked": selected_rows_checked,
        "strict_edge_mismatches": mismatch_count,
        "quotient_replay_strict_edge_mismatches": quotient_replay_strict_edge_mismatches,
        "strict_edges_per_row": dict(sorted(strict_edges_per_row.items())),
        "interval_span_histogram": dict(sorted(span_histogram.items())),
        "total_strict_edges": total_strict_edges,
        "example_mismatches": example_mismatches,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the n=9 checker strict-edge table matches a "
            "direct proper-interval-containment enumeration for every "
            "candidate row, and the quotient replay implementation records "
            "the same strict-edge count per one-row payload. It does not "
            "audit later quotient or exhaustive-search soundness."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_strict_edge_geometry(payload: Mapping[str, Any]) -> None:
    """Assert the expected strict-edge geometry audit result."""

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
        "does not prove row coverage",
        "brancher coverage",
        "selected-distance quotient soundness",
        "n=9",
        "counterexample",
        "official/global status update",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")
    if payload.get("validation_status") != "passed":
        raise AssertionError(f"validation errors: {payload.get('validation_errors')!r}")
    expected = {
        "selected_rows_checked": EXPECTED_SELECTED_ROWS,
        "strict_edge_mismatches": 0,
        "quotient_replay_strict_edge_mismatches": 0,
        "strict_edges_per_row": EXPECTED_STRICT_EDGES_PER_ROW,
        "interval_span_histogram": EXPECTED_SPAN_HISTOGRAM,
        "total_strict_edges": EXPECTED_TOTAL_STRICT_EDGES,
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            raise AssertionError(f"{key} mismatch: expected {value!r}, got {payload.get(key)!r}")


def _properly_contains(
    outer_start: int,
    outer_end: int,
    inner_start: int,
    inner_end: int,
) -> bool:
    return (
        outer_start <= inner_start
        and inner_end <= outer_end
        and (outer_start < inner_start or inner_end < outer_end)
    )


def _add_span_histogram(center: int, row_mask: int, histogram: Counter[str]) -> None:
    witnesses = sorted(n9.MASK_BITS[row_mask], key=lambda witness: (witness - center) % n9.N)
    for outer_start in range(n9.ROW_SIZE):
        for outer_end in range(outer_start + 1, n9.ROW_SIZE):
            for inner_start in range(n9.ROW_SIZE):
                for inner_end in range(inner_start + 1, n9.ROW_SIZE):
                    if (outer_start, outer_end) == (inner_start, inner_end):
                        continue
                    if _properly_contains(outer_start, outer_end, inner_start, inner_end):
                        outer_span = outer_end - outer_start
                        inner_span = inner_end - inner_start
                        outer = pair(witnesses[outer_start], witnesses[outer_end])
                        inner = pair(witnesses[inner_start], witnesses[inner_end])
                        if outer == inner:
                            raise AssertionError("proper interval produced equal pairs")
                        histogram[f"{outer_span}->{inner_span}"] += 1


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> bool:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")
        return False
    return True


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without mismatch examples."""

    return {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"selected rows checked: {payload['selected_rows_checked']}",
        f"strict-edge mismatches: {payload['strict_edge_mismatches']}",
        f"total strict edges: {payload['total_strict_edges']}",
    ]


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate the audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="emit JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without mismatch examples",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = strict_edge_geometry_payload()

    if args.assert_expected:
        assert_expected_strict_edge_geometry(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle strict-edge geometry audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 strict-edge geometry audit checks passed")
    else:
        print("FAILED: n=9 strict-edge geometry audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
