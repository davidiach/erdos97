#!/usr/bin/env python3
"""Replay n=9 branch option predicates against a direct implementation."""

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

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402

SCHEMA = "erdos97.n9_vertex_circle_branch_options.v1"
STATUS = "REVIEW_PENDING_BRANCH_OPTION_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Fixed-center-order branch-option audit for the review-pending n=9 "
    "vertex-circle checker. It walks the no-vertex-circle fixed-order search "
    "states and compares the helper valid-options predicate with a direct "
    "row-shape, row-pair crossing, witness-pair capacity, and "
    "selected-indegree capacity implementation plus independently recomputed "
    "count arrays. It does not prove dynamic-MRO branch coverage, "
    "strict-edge geometry, selected-distance quotient soundness, n=9, a "
    "counterexample, or any official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_branch_options.py",
    "command": (
        "python scripts/check_n9_vertex_circle_branch_options.py "
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
    "validation_status",
    "validation_errors",
    "interpretation",
    "provenance",
)
BRANCH_OPTION_SUMMARY_KEYS = (
    "row_order_rule",
    "vertex_circle_pruning",
    "nodes_visited",
    "full_assignments",
    "status_counts",
    "option_contexts",
    "helper_option_total",
    "empty_option_contexts",
    "option_mismatches",
    "count_array_mismatches",
)

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_SELECTED_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)
ORDER = tuple(range(N))

PAIRS = [(left, right) for left in range(N) for right in range(left + 1, N)]
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
BITS = {mask: tuple(index for index in range(N) if (mask >> index) & 1) for mask in range(1 << N)}
ROW_PAIR_INDICES = {
    mask: [PAIR_INDEX[(left, right)] for left, right in combinations(BITS[mask], 2)]
    for options in n9.OPTIONS
    for mask in options
}

EXPECTED_NODES_VISITED = 520_782
EXPECTED_FULL_ASSIGNMENTS = 184
EXPECTED_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_OPTION_CONTEXTS = 520_598
EXPECTED_HELPER_OPTION_TOTAL = 520_712
EXPECTED_EMPTY_OPTION_CONTEXTS = 297_936


def branch_option_payload() -> dict[str, Any]:
    """Return the fixed-order branch-option audit payload."""

    errors: list[str] = []
    summary = _fixed_order_no_vertex_circle_replay()
    _check_equal(errors, "nodes visited", summary["nodes_visited"], EXPECTED_NODES_VISITED)
    _check_equal(errors, "full assignments", summary["full_assignments"], EXPECTED_FULL_ASSIGNMENTS)
    _check_equal(errors, "status counts", summary["status_counts"], EXPECTED_STATUS_COUNTS)
    _check_equal(errors, "option contexts", summary["option_contexts"], EXPECTED_OPTION_CONTEXTS)
    _check_equal(
        errors,
        "helper option total",
        summary["helper_option_total"],
        EXPECTED_HELPER_OPTION_TOTAL,
    )
    _check_equal(
        errors,
        "empty option contexts",
        summary["empty_option_contexts"],
        EXPECTED_EMPTY_OPTION_CONTEXTS,
    )
    _check_equal(errors, "option mismatches", summary["option_mismatches"], 0)
    _check_equal(errors, "count-array mismatches", summary["count_array_mismatches"], 0)

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "max_selected_indegree": MAX_SELECTED_INDEGREE,
        "branch_option_audit": summary,
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says the helper valid-options predicate agrees "
            "with the direct implementation on every no-vertex-circle "
            "fixed-order search state reached by this replay, and the "
            "maintained count arrays agree with independently recomputed "
            "counts. This is a branch-option implementation audit only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_branch_option_payload(payload: Mapping[str, Any]) -> None:
    """Assert the expected fixed-order branch-option audit result."""

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
        "does not prove dynamic-MRO branch coverage",
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
    summary = payload.get("branch_option_audit")
    if not isinstance(summary, Mapping):
        raise AssertionError("branch_option_audit missing")
    expected = {
        "row_order_rule": "fixed_center_order",
        "vertex_circle_pruning": False,
        "nodes_visited": EXPECTED_NODES_VISITED,
        "full_assignments": EXPECTED_FULL_ASSIGNMENTS,
        "status_counts": EXPECTED_STATUS_COUNTS,
        "option_contexts": EXPECTED_OPTION_CONTEXTS,
        "helper_option_total": EXPECTED_HELPER_OPTION_TOTAL,
        "empty_option_contexts": EXPECTED_EMPTY_OPTION_CONTEXTS,
        "option_mismatches": 0,
        "count_array_mismatches": 0,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} mismatch: {summary.get(key)!r} != {value!r}")


def _fixed_order_no_vertex_circle_replay() -> dict[str, Any]:
    nodes_visited = 0
    full_assignments = 0
    status_counts: Counter[str] = Counter()
    option_contexts = 0
    helper_option_total = 0
    empty_option_contexts = 0
    option_mismatches = 0
    count_array_mismatches = 0
    example_mismatches: list[dict[str, Any]] = []

    def search(
        assignment: n9.Assignment,
        selected_indegrees: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes_visited
        nonlocal full_assignments
        nonlocal option_contexts
        nonlocal helper_option_total
        nonlocal empty_option_contexts
        nonlocal option_mismatches
        nonlocal count_array_mismatches

        nodes_visited += 1
        recomputed_indegrees, recomputed_pair_counts = direct_counts(assignment)
        if (
            recomputed_indegrees != selected_indegrees
            or recomputed_pair_counts != witness_pair_counts
        ):
            count_array_mismatches += 1
            _record_example(
                example_mismatches,
                assignment,
                "maintained counts differ from direct recomputation",
            )

        if len(assignment) == N:
            full_assignments += 1
            status_counts[n9.vertex_circle_status(assignment)] += 1
            return

        center = next(candidate for candidate in ORDER if candidate not in assignment)
        helper_options = n9.valid_options_for_center(
            center,
            assignment,
            selected_indegrees,
            witness_pair_counts,
        )
        direct_options = direct_valid_options(
            center,
            assignment,
            recomputed_indegrees,
            recomputed_pair_counts,
        )
        option_contexts += 1
        helper_option_total += len(helper_options)
        if not helper_options:
            empty_option_contexts += 1
        if helper_options != direct_options:
            option_mismatches += 1
            _record_example(
                example_mismatches,
                assignment,
                "helper options differ from direct options",
                center=center,
                helper_options=helper_options,
                direct_options=direct_options,
            )

        for row_mask in helper_options:
            assignment[center] = row_mask
            for target in BITS[row_mask]:
                selected_indegrees[target] += 1
            for pair_index in ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            search(assignment, selected_indegrees, witness_pair_counts)

            for pair_index in ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in BITS[row_mask]:
                selected_indegrees[target] -= 1
            del assignment[center]

    for row0 in n9.OPTIONS[0]:
        assignment = {0: row0}
        selected_indegrees, witness_pair_counts = direct_counts(assignment)
        search(assignment, selected_indegrees, witness_pair_counts)

    return {
        "row_order_rule": "fixed_center_order",
        "vertex_circle_pruning": False,
        "nodes_visited": nodes_visited,
        "full_assignments": full_assignments,
        "status_counts": dict(sorted(status_counts.items())),
        "option_contexts": option_contexts,
        "helper_option_total": helper_option_total,
        "empty_option_contexts": empty_option_contexts,
        "option_mismatches": option_mismatches,
        "count_array_mismatches": count_array_mismatches,
        "example_mismatches": example_mismatches,
    }


def direct_counts(assignment: Mapping[int, int]) -> tuple[list[int], list[int]]:
    """Recompute selected indegrees and witness-pair counts from scratch."""

    selected_indegrees = [0] * N
    witness_pair_counts = [0] * len(PAIRS)
    for row_mask in assignment.values():
        for target in BITS[row_mask]:
            selected_indegrees[target] += 1
        for pair_index in ROW_PAIR_INDICES[row_mask]:
            witness_pair_counts[pair_index] += 1
    return selected_indegrees, witness_pair_counts


def direct_valid_options(
    center: int,
    assignment: Mapping[int, int],
    selected_indegrees: Sequence[int],
    witness_pair_counts: Sequence[int],
) -> list[int]:
    """Return directly recomputed valid row masks for one center."""

    out: list[int] = []
    assigned_rows = tuple(assignment.items())
    for row_mask in n9.OPTIONS[center]:
        if not _direct_row_pair_compatible(center, row_mask, assigned_rows):
            continue
        if any(selected_indegrees[target] >= MAX_SELECTED_INDEGREE for target in BITS[row_mask]):
            continue
        if any(witness_pair_counts[pair_index] >= PAIR_CAP for pair_index in ROW_PAIR_INDICES[row_mask]):
            continue
        out.append(row_mask)
    return out


def _direct_row_pair_compatible(
    center: int,
    row_mask: int,
    assigned_rows: Sequence[tuple[int, int]],
) -> bool:
    for other_center, other_mask in assigned_rows:
        common_mask = row_mask & other_mask
        common_size = common_mask.bit_count()
        if common_size > PAIR_CAP:
            return False
        if common_size == PAIR_CAP:
            witness_a, witness_b = BITS[common_mask]
            if not chords_cross((center, other_center), (witness_a, witness_b)):
                return False
    return True


def pair(left: int, right: int) -> tuple[int, int]:
    """Return a normalized unordered pair."""

    if left == right:
        raise ValueError("loop pair")
    return (left, right) if left < right else (right, left)


def in_open_arc(left: int, right: int, item: int) -> bool:
    """Return whether item lies strictly on the cyclic arc left -> right."""

    return ((item - left) % N) < ((right - left) % N) and item != left and item != right


def chords_cross(first: tuple[int, int], second: tuple[int, int]) -> bool:
    """Return whether two disjoint chords cross in the natural cyclic order."""

    left, right = first
    a, b = second
    if len({left, right, a, b}) < 4:
        return False
    return in_open_arc(left, right, a) != in_open_arc(left, right, b)


def _record_example(
    examples: list[dict[str, Any]],
    assignment: Mapping[int, int],
    message: str,
    **extra: Any,
) -> None:
    if len(examples) >= 5:
        return
    examples.append(
        {
            "message": message,
            "assigned_centers": sorted(int(center) for center in assignment),
            **extra,
        }
    )


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audit = payload.get("branch_option_audit")
    if isinstance(audit, Mapping):
        summary["branch_option_audit_summary"] = {
            key: audit[key] for key in BRANCH_OPTION_SUMMARY_KEYS if key in audit
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    summary = payload["branch_option_audit"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"nodes visited: {summary['nodes_visited']}",
        f"option contexts: {summary['option_contexts']}",
        f"option mismatches: {summary['option_mismatches']}",
        f"count-array mismatches: {summary['count_array_mismatches']}",
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
        help="emit compact reviewer-facing JSON summary",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = branch_option_payload()

    if args.assert_expected:
        assert_expected_branch_option_payload(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle branch-option audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 branch-option audit checks passed")
    else:
        print("FAILED: n=9 branch-option audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
