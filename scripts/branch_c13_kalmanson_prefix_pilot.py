#!/usr/bin/env python3
"""Bounded C13 prefix-branch Kalmanson pilot.

This is a small brancher for the C13 all-order program. It fixes label 0 as
the cyclic-order anchor, branches on two-sided boundary prefixes, prunes the
reflection duplicate as soon as the boundary decides it, and then runs a small
deterministic budget of fixed-order Kalmanson/Farkas certificate searches.

The output is not an exhaustive cyclic-order search.
"""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence

from check_kalmanson_certificate import check_certificate_dict
from find_kalmanson_certificate import find_certificate

PATTERN_NAME = "C13_sidon_1_2_4_10"
N = 13
OFFSETS = [1, 2, 4, 10]
DEFAULT_BOUNDARY_PAIRS = 2
DEFAULT_MAX_LP_CALLS = 12
MAX_BOUNDARY_PAIRS = 3


@dataclass(frozen=True)
class BranchCounts:
    raw_boundary_state_count: int
    canonical_boundary_state_count: int
    reflection_pruned_boundary_state_count: int
    extensions_considered_count: int
    prefix_pruned_extension_count: int


@dataclass(frozen=True)
class BoundaryState:
    left: tuple[int, ...]
    right: tuple[int, ...]
    remaining: tuple[int, ...]

    def canonical_completion(self) -> tuple[int, ...]:
        return (0,) + self.left + self.remaining + tuple(reversed(self.right))


def reflection_prefix_compare(left: Sequence[int], right: Sequence[int]) -> int:
    """Compare a boundary prefix with its reflected boundary prefix."""

    for a, b in zip(left, right):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


def generate_boundary_states(boundary_pairs: int) -> tuple[list[BoundaryState], BranchCounts]:
    if boundary_pairs < 1:
        raise ValueError("boundary_pairs must be positive")
    if boundary_pairs > MAX_BOUNDARY_PAIRS:
        raise ValueError(f"boundary_pairs is capped at {MAX_BOUNDARY_PAIRS} for this pilot")
    if 2 * boundary_pairs > N - 1:
        raise ValueError("boundary_pairs uses more labels than available")

    labels = tuple(range(1, N))
    states: list[BoundaryState] = []
    extensions_considered = 0
    prefix_pruned = 0

    def dfs(left: tuple[int, ...], right: tuple[int, ...], remaining: tuple[int, ...]) -> None:
        nonlocal extensions_considered, prefix_pruned
        if len(left) == boundary_pairs:
            states.append(BoundaryState(left=left, right=right, remaining=remaining))
            return

        for left_label in remaining:
            after_left = tuple(label for label in remaining if label != left_label)
            for right_label in after_left:
                extensions_considered += 1
                new_left = left + (left_label,)
                new_right = right + (right_label,)
                if reflection_prefix_compare(new_left, new_right) > 0:
                    prefix_pruned += 1
                    continue
                new_remaining = tuple(label for label in after_left if label != right_label)
                dfs(new_left, new_right, new_remaining)

    dfs((), (), labels)
    raw_boundary_state_count = math.perm(N - 1, 2 * boundary_pairs)
    canonical_boundary_state_count = raw_boundary_state_count // 2
    counts = BranchCounts(
        raw_boundary_state_count=raw_boundary_state_count,
        canonical_boundary_state_count=canonical_boundary_state_count,
        reflection_pruned_boundary_state_count=(
            raw_boundary_state_count - canonical_boundary_state_count
        ),
        extensions_considered_count=extensions_considered,
        prefix_pruned_extension_count=prefix_pruned,
    )
    if len(states) != canonical_boundary_state_count:
        raise AssertionError("canonical boundary count mismatch")
    return states, counts


def summarize_certificate(cert: Mapping[str, object]) -> dict[str, object]:
    result = check_certificate_dict(cert)
    return {
        "status": result.status,
        "positive_inequalities": result.positive_inequalities,
        "distance_classes_after_selected_equalities": (
            result.distance_classes_after_selected_equalities
        ),
        "weight_sum": result.weight_sum,
        "max_weight": result.max_weight,
        "zero_sum_verified": result.zero_sum_verified,
        "claim_strength": result.claim_strength,
    }


def run_pilot(
    *,
    boundary_pairs: int,
    max_lp_calls: int,
    include_certificates: bool,
    tol: float,
) -> dict[str, object]:
    if max_lp_calls < 0:
        raise ValueError("max_lp_calls must be nonnegative")
    states, counts = generate_boundary_states(boundary_pairs)
    sampled_states = states[:max_lp_calls]
    cases: list[dict[str, object]] = []

    for idx, state in enumerate(sampled_states):
        order = state.canonical_completion()
        cert = find_certificate(PATTERN_NAME, N, OFFSETS, order, tol)
        case: dict[str, object] = {
            "label": f"prefix_branch_{idx:04d}",
            "boundary_left": list(state.left),
            "boundary_right_reflection_side": list(state.right),
            "middle_completion_strategy": "ascending remaining labels",
            "canonical_completion_order": list(order),
            "status": (
                "EXACT_KALMANSON_CERTIFICATE_FOUND"
                if cert is not None
                else "NO_EXACT_KALMANSON_CERTIFICATE_FOUND"
            ),
        }
        if cert is not None:
            case["certificate_summary"] = summarize_certificate(cert)
            if include_certificates:
                case["certificate"] = cert
        cases.append(case)

    closed_count = sum(
        1 for case in cases if case["status"] == "EXACT_KALMANSON_CERTIFICATE_FOUND"
    )
    return {
        "type": "c13_kalmanson_prefix_branch_pilot_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is a bounded prefix-branch pilot, not an exhaustive all-order cyclic-order search.",
            "Reflection-pruned prefix counts are search accounting, not geometric obstructions.",
            "Every closed sampled completion was produced by an exact positive-integer Kalmanson/Farkas certificate checked by scripts/check_kalmanson_certificate.py.",
        ],
        "parameters": {
            "boundary_pairs": boundary_pairs,
            "max_lp_calls": max_lp_calls,
            "include_certificates": include_certificates,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
            "completion_strategy_for_sampled_states": "ascending remaining labels",
        },
        "branch_accounting": {
            "raw_boundary_state_count": counts.raw_boundary_state_count,
            "canonical_boundary_state_count": counts.canonical_boundary_state_count,
            "reflection_pruned_boundary_state_count": (
                counts.reflection_pruned_boundary_state_count
            ),
            "extensions_considered_count": counts.extensions_considered_count,
            "prefix_pruned_extension_count": counts.prefix_pruned_extension_count,
            "lp_call_count": len(cases),
            "closed_by_kalmanson_certificate_count": closed_count,
            "unclosed_lp_call_count": len(cases) - closed_count,
            "exhaustive_all_orders": False,
        },
        "cases": cases,
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "raw_boundary_state_count": 11880,
        "canonical_boundary_state_count": 5940,
        "reflection_pruned_boundary_state_count": 5940,
        "extensions_considered_count": 6072,
        "prefix_pruned_extension_count": 66,
        "lp_call_count": DEFAULT_MAX_LP_CALLS,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    if accounting["closed_by_kalmanson_certificate_count"] != DEFAULT_MAX_LP_CALLS:
        raise AssertionError("not all sampled prefix completions closed")
    if accounting["unclosed_lp_call_count"] != 0:
        raise AssertionError("sampled prefix completions have unclosed cases")
    if accounting["exhaustive_all_orders"] is not False:
        raise AssertionError("pilot must not claim exhaustive all-order coverage")

    cases = data["cases"]
    if not isinstance(cases, list):
        raise AssertionError("cases must be a list")
    if len(cases) != DEFAULT_MAX_LP_CALLS:
        raise AssertionError("unexpected sampled case count")
    for idx, case in enumerate(cases):
        if not isinstance(case, Mapping):
            raise AssertionError("case must be an object")
        if case["label"] != f"prefix_branch_{idx:04d}":
            raise AssertionError("case labels changed")
        if case["status"] != "EXACT_KALMANSON_CERTIFICATE_FOUND":
            raise AssertionError(f"{case['label']} did not close")
        summary = case["certificate_summary"]
        if not isinstance(summary, Mapping):
            raise AssertionError(f"{case['label']} missing certificate summary")
        if int(summary["positive_inequalities"]) <= 0:
            raise AssertionError(f"{case['label']} has empty certificate support")
        if summary["distance_classes_after_selected_equalities"] != 39:
            raise AssertionError(f"{case['label']} distance class count changed")
        if summary["zero_sum_verified"] is not True:
            raise AssertionError(f"{case['label']} certificate did not verify")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "boundary states: "
        f"{accounting['canonical_boundary_state_count']} canonical / "
        f"{accounting['raw_boundary_state_count']} raw"
    )
    print(
        "LP calls: "
        f"{accounting['lp_call_count']} closed="
        f"{accounting['closed_by_kalmanson_certificate_count']} unclosed="
        f"{accounting['unclosed_lp_call_count']}"
    )

    cases = data["cases"]
    if not isinstance(cases, list):
        raise TypeError("cases must be a list")
    headers = ["label", "left", "right", "status", "ineq", "max_weight"]
    rows = []
    for case in cases:
        if not isinstance(case, Mapping):
            raise TypeError("case must be an object")
        summary = case.get("certificate_summary", {})
        rows.append(
            [
                str(case["label"]),
                str(case["boundary_left"]),
                str(case["boundary_right_reflection_side"]),
                str(case["status"]),
                str(summary.get("positive_inequalities", "-")),
                str(summary.get("max_weight", "-")),
            ]
        )
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in rows:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundary-pairs", type=int, default=DEFAULT_BOUNDARY_PAIRS)
    parser.add_argument("--max-lp-calls", type=int, default=DEFAULT_MAX_LP_CALLS)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--include-certificates",
        action="store_true",
        help="include full certificate objects in the output",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = run_pilot(
        boundary_pairs=args.boundary_pairs,
        max_lp_calls=args.max_lp_calls,
        include_certificates=args.include_certificates,
        tol=args.tol,
    )
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: bounded C13 prefix branch pilot matched expected closures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
