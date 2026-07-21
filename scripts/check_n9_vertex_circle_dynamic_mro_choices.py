#!/usr/bin/env python3
"""Audit dynamic MRO center choices in the n=9 vertex-circle checker."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from typing import Any, Mapping, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9

SCHEMA = "erdos97.n9_vertex_circle_dynamic_mro_choices.v1"
STATUS = "REVIEW_PENDING_DYNAMIC_MRO_CHOICE_AUDIT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Dynamic minimum-remaining-options choice audit for the review-pending "
    "n=9 vertex-circle checker. It replays the dynamic brancher with and "
    "without vertex-circle pruning, recomputes selected-indegree and "
    "witness-pair count arrays at each reached state, recomputes every "
    "unassigned center's valid options with a direct row-shape, crossing, "
    "witness-pair capacity, and selected-indegree predicate, and checks that "
    "the brancher chooses the first center with minimum remaining options. "
    "It does not prove the geometric filters, strict-edge geometry, "
    "selected-distance quotient soundness, n=9, a counterexample, or any "
    "official/global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_dynamic_mro_choices.py",
    "command": (
        "python scripts/check_n9_vertex_circle_dynamic_mro_choices.py "
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
DYNAMIC_MRO_SUMMARY_KEYS = (
    "row_order_rule",
    "vertex_circle_pruning",
    "row0_choices",
    "nodes_visited",
    "full_assignments",
    "counts",
    "choice_contexts",
    "center_option_contexts",
    "helper_option_total",
    "empty_choice_contexts",
    "child_prune_attempts",
    "chosen_center_mismatches",
    "chosen_option_mismatches",
    "helper_direct_option_mismatches",
    "count_array_mismatches",
)

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
MAX_SELECTED_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)

PAIRS = [(left, right) for left in range(N) for right in range(left + 1, N)]
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
BITS = {mask: tuple(index for index in range(N) if (mask >> index) & 1) for mask in range(1 << N)}
ROW_PAIR_INDICES = {
    mask: [PAIR_INDEX[(left, right)] for left, right in combinations(BITS[mask], 2)]
    for options in n9.OPTIONS
    for mask in options
}

EXPECTED_WITH_VERTEX = {
    "row_order_rule": "dynamic_minimum_remaining_options",
    "vertex_circle_pruning": True,
    "row0_choices": 70,
    "nodes_visited": 16_752,
    "full_assignments": 0,
    "counts": {"partial_self_edge": 11_271, "partial_strict_cycle": 11_011},
    "choice_contexts": 16_752,
    "center_option_contexts": 93_837,
    "helper_option_total": 751_918,
    "empty_choice_contexts": 5_686,
    "child_prune_attempts": 22_282,
    "assigned_depth_histogram": {1: 70, 2: 1_460, 3: 7_876, 4: 6_424, 5: 915, 6: 7},
    "minimum_option_count_histogram": {
        0: 5_686,
        1: 2_278,
        2: 2_837,
        3: 705,
        4: 3_122,
        5: 152,
        6: 1_112,
        7: 64,
        8: 408,
        9: 164,
        10: 1,
        11: 5,
        12: 39,
        14: 19,
        17: 145,
        35: 15,
    },
    "minimum_tie_count_histogram": {1: 10_164, 2: 4_637, 3: 1_388, 4: 448, 5: 97, 6: 18},
}
EXPECTED_WITHOUT_VERTEX = {
    "row_order_rule": "dynamic_minimum_remaining_options",
    "vertex_circle_pruning": False,
    "row0_choices": 70,
    "nodes_visited": 100_817,
    "full_assignments": 184,
    "counts": {"self_edge": 158, "strict_cycle": 26},
    "choice_contexts": 100_633,
    "center_option_contexts": 406_285,
    "helper_option_total": 1_596_469,
    "empty_choice_contexts": 54_122,
    "child_prune_attempts": 0,
    "assigned_depth_histogram": {
        1: 70,
        2: 1_460,
        3: 9_380,
        4: 25_333,
        5: 32_488,
        6: 20_955,
        7: 8_796,
        8: 2_151,
    },
    "minimum_option_count_histogram": {
        0: 54_122,
        1: 23_008,
        2: 11_011,
        3: 4_080,
        4: 5_387,
        5: 572,
        6: 1_266,
        7: 206,
        8: 574,
        9: 180,
        10: 4,
        11: 5,
        12: 39,
        14: 19,
        17: 145,
        35: 15,
    },
    "minimum_tie_count_histogram": {1: 55_678, 2: 31_138, 3: 11_740, 4: 1_925, 5: 134, 6: 18},
}


def dynamic_mro_choice_payload() -> dict[str, Any]:
    """Return the dynamic MRO choice audit payload."""

    errors: list[str] = []
    with_vertex = _dynamic_mro_replay(use_vertex_circle=True)
    without_vertex = _dynamic_mro_replay(use_vertex_circle=False)
    _audit_summary("with vertex-circle pruning", with_vertex, EXPECTED_WITH_VERTEX, errors)
    _audit_summary(
        "without vertex-circle pruning",
        without_vertex,
        EXPECTED_WITHOUT_VERTEX,
        errors,
    )

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "max_selected_indegree": MAX_SELECTED_INDEGREE,
        "dynamic_mro_audits": {
            "with_vertex_circle_pruning": with_vertex,
            "without_vertex_circle_pruning": without_vertex,
        },
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "interpretation": (
            "A passed audit says that on every reached dynamic-MRO state in "
            "both the vertex-circle-pruned and no-vertex-circle searches, the "
            "maintained count arrays agree with direct recomputation, helper "
            "options agree with direct options for every unassigned center, "
            "and the selected branch center is the first minimum-options "
            "center. This is a dynamic branch-choice implementation audit only."
        ),
        "provenance": dict(PROVENANCE),
    }


def assert_expected_dynamic_mro_choice_payload(payload: Mapping[str, Any]) -> None:
    """Assert the expected dynamic MRO choice audit result."""

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
        "does not prove the geometric filters",
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
    audits = payload.get("dynamic_mro_audits")
    if not isinstance(audits, Mapping):
        raise AssertionError("dynamic_mro_audits missing")
    for key, expected in (
        ("with_vertex_circle_pruning", EXPECTED_WITH_VERTEX),
        ("without_vertex_circle_pruning", EXPECTED_WITHOUT_VERTEX),
    ):
        summary = audits.get(key)
        if not isinstance(summary, Mapping):
            raise AssertionError(f"{key} summary missing")
        _assert_summary_matches(key, summary, expected)


def _dynamic_mro_replay(*, use_vertex_circle: bool) -> dict[str, Any]:
    nodes_visited = 0
    full_assignments = 0
    counts: Counter[str] = Counter()
    choice_contexts = 0
    center_option_contexts = 0
    helper_option_total = 0
    empty_choice_contexts = 0
    child_prune_attempts = 0
    assigned_depth_histogram: Counter[int] = Counter()
    minimum_option_count_histogram: Counter[int] = Counter()
    minimum_tie_count_histogram: Counter[int] = Counter()
    chosen_center_mismatches = 0
    chosen_option_mismatches = 0
    helper_direct_option_mismatches = 0
    count_array_mismatches = 0
    example_mismatches: list[dict[str, Any]] = []

    def search(
        assignment: n9.Assignment,
        selected_indegrees: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes_visited
        nonlocal full_assignments
        nonlocal choice_contexts
        nonlocal center_option_contexts
        nonlocal helper_option_total
        nonlocal empty_choice_contexts
        nonlocal child_prune_attempts
        nonlocal chosen_center_mismatches
        nonlocal chosen_option_mismatches
        nonlocal helper_direct_option_mismatches
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
            if use_vertex_circle:
                counts["full_survivor"] += 1
            else:
                counts[n9.vertex_circle_status(assignment)] += 1
            return

        choice_contexts += 1
        assigned_depth_histogram[len(assignment)] += 1
        helper_by_center: dict[int, list[int]] = {}
        direct_by_center: dict[int, list[int]] = {}
        for center in range(N):
            if center in assignment:
                continue
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
            helper_by_center[center] = helper_options
            direct_by_center[center] = direct_options
            center_option_contexts += 1
            helper_option_total += len(helper_options)
            if helper_options != direct_options:
                helper_direct_option_mismatches += 1
                _record_example(
                    example_mismatches,
                    assignment,
                    "helper options differ from direct options",
                    center=center,
                    helper_options=helper_options,
                    direct_options=direct_options,
                )

        helper_center, helper_options = _first_minimum_option_center(helper_by_center)
        direct_center, direct_options = _first_minimum_option_center(direct_by_center)
        minimum_option_count = len(direct_options)
        minimum_option_count_histogram[minimum_option_count] += 1
        minimum_tie_count_histogram[
            sum(1 for options in direct_by_center.values() if len(options) == minimum_option_count)
        ] += 1
        if helper_center != direct_center:
            chosen_center_mismatches += 1
            _record_example(
                example_mismatches,
                assignment,
                "dynamic MRO center differs from direct first-minimum center",
                helper_center=helper_center,
                direct_center=direct_center,
            )
        if helper_options != direct_options:
            chosen_option_mismatches += 1
            _record_example(
                example_mismatches,
                assignment,
                "dynamic MRO chosen options differ from direct chosen options",
                center=helper_center,
                helper_options=helper_options,
                direct_options=direct_options,
            )
        if not helper_options:
            empty_choice_contexts += 1
            return

        for row_mask in helper_options:
            assignment[helper_center] = row_mask
            for target in BITS[row_mask]:
                selected_indegrees[target] += 1
            for pair_index in ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            status = n9.vertex_circle_status(assignment) if use_vertex_circle else "ok"
            if status == "ok":
                search(assignment, selected_indegrees, witness_pair_counts)
            else:
                counts[f"partial_{status}"] += 1
                child_prune_attempts += 1

            for pair_index in ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in BITS[row_mask]:
                selected_indegrees[target] -= 1
            del assignment[helper_center]

    for row0 in n9.OPTIONS[0]:
        assignment = {0: row0}
        selected_indegrees, witness_pair_counts = direct_counts(assignment)
        if n9.vertex_circle_status(assignment) == "ok":
            search(assignment, selected_indegrees, witness_pair_counts)

    return {
        "row_order_rule": "dynamic_minimum_remaining_options",
        "vertex_circle_pruning": use_vertex_circle,
        "row0_choices": len(n9.OPTIONS[0]),
        "nodes_visited": nodes_visited,
        "full_assignments": full_assignments,
        "counts": dict(sorted(counts.items())),
        "choice_contexts": choice_contexts,
        "center_option_contexts": center_option_contexts,
        "helper_option_total": helper_option_total,
        "empty_choice_contexts": empty_choice_contexts,
        "child_prune_attempts": child_prune_attempts,
        "assigned_depth_histogram": dict(sorted(assigned_depth_histogram.items())),
        "minimum_option_count_histogram": dict(sorted(minimum_option_count_histogram.items())),
        "minimum_tie_count_histogram": dict(sorted(minimum_tie_count_histogram.items())),
        "chosen_center_mismatches": chosen_center_mismatches,
        "chosen_option_mismatches": chosen_option_mismatches,
        "helper_direct_option_mismatches": helper_direct_option_mismatches,
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


def _first_minimum_option_center(options_by_center: Mapping[int, list[int]]) -> tuple[int, list[int]]:
    return min(options_by_center.items(), key=lambda item: len(item[1]))


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


def _audit_summary(
    label: str,
    summary: Mapping[str, Any],
    expected: Mapping[str, Any],
    errors: list[str],
) -> None:
    for key, value in expected.items():
        _check_equal(errors, f"{label} {key}", summary.get(key), value)
    for key in (
        "chosen_center_mismatches",
        "chosen_option_mismatches",
        "helper_direct_option_mismatches",
        "count_array_mismatches",
    ):
        _check_equal(errors, f"{label} {key}", summary.get(key), 0)
    _check_equal(errors, f"{label} example_mismatches", summary.get("example_mismatches"), [])


def _assert_summary_matches(
    label: str,
    summary: Mapping[str, Any],
    expected: Mapping[str, Any],
) -> None:
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{label} {key} mismatch: {summary.get(key)!r} != {value!r}")
    for key in (
        "chosen_center_mismatches",
        "chosen_option_mismatches",
        "helper_direct_option_mismatches",
        "count_array_mismatches",
    ):
        if summary.get(key) != 0:
            raise AssertionError(f"{label} {key} nonzero: {summary.get(key)!r}")
    if summary.get("example_mismatches") != []:
        raise AssertionError(f"{label} example_mismatches nonempty")


def _check_equal(errors: list[str], name: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{name} mismatch: {actual!r} != {expected!r}")


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without histograms."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    audits = payload.get("dynamic_mro_audits")
    if isinstance(audits, Mapping):
        summary["dynamic_mro_audit_summaries"] = {
            audit_key: {
                key: audit[key]
                for key in DYNAMIC_MRO_SUMMARY_KEYS
                if isinstance(audit, Mapping) and key in audit
            }
            for audit_key, audit in audits.items()
        }
    return summary


def summary_lines(payload: Mapping[str, Any]) -> list[str]:
    audits = payload["dynamic_mro_audits"]
    with_vertex = audits["with_vertex_circle_pruning"]
    without_vertex = audits["without_vertex_circle_pruning"]
    return [
        f"schema: {payload['schema']}",
        f"status: {payload['status']}",
        f"validation: {payload['validation_status']}",
        f"with-vertex nodes: {with_vertex['nodes_visited']}",
        f"with-vertex choice contexts: {with_vertex['choice_contexts']}",
        f"without-vertex nodes: {without_vertex['nodes_visited']}",
        f"without-vertex choice contexts: {without_vertex['choice_contexts']}",
        f"chosen center mismatches: {with_vertex['chosen_center_mismatches'] + without_vertex['chosen_center_mismatches']}",
        f"helper/direct option mismatches: {with_vertex['helper_direct_option_mismatches'] + without_vertex['helper_direct_option_mismatches']}",
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
        help="emit compact reviewer-facing JSON without histograms",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = dynamic_mro_choice_payload()

    if args.assert_expected:
        assert_expected_dynamic_mro_choice_payload(payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif payload.get("validation_status") == "passed":
        print("n=9 vertex-circle dynamic MRO choice audit")
        for line in summary_lines(payload):
            print(line)
        print("OK: n=9 dynamic MRO choice audit checks passed")
    else:
        print("FAILED: n=9 dynamic MRO choice audit", file=sys.stderr)
        for error in payload.get("validation_errors", []):
            print(f"- {error}", file=sys.stderr)

    if args.check and payload.get("validation_status") != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
