#!/usr/bin/env python3
"""Check the support-saturation equality-wall obstruction.

This standalone checker records the arithmetic consequences of the lemma in
docs/support-saturation-obstruction.md.  It does not verify Euclidean
realizability, run a search, or prove Erdos Problem #97.

The proof-facing claim is:

    If every center of a strict convex n-gon has a same-radius support of size
    at least k >= 4, then n >= binom(k, 2) + 3.

Pair-counting alone gives binom(k,2)+2; the equality wall is ruled out by the
support-saturation/turn-cover argument.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from typing import Any

SCHEMA = "erdos97.support_saturation_obstruction.v1"
TRUST = "LEMMA"


def pair_counting_wall(k: int) -> int:
    """Smallest n not ruled out by pair-counting alone."""

    if k < 0:
        raise ValueError("k must be nonnegative")
    return comb(k, 2) + 2


def saturation_improved_wall(k: int) -> int:
    """Smallest n not ruled out after excluding the saturated equality wall."""

    if k < 0:
        raise ValueError("k must be nonnegative")
    if k < 4:
        raise ValueError("the saturation obstruction is used here only for k >= 4")
    return pair_counting_wall(k) + 1


def min_vertex_cover_size_cycle(n: int) -> int:
    """Minimum vertex-cover size of the n-cycle."""

    if n < 3:
        raise ValueError("cycle size must be at least 3")
    return (n + 1) // 2


def forced_turn_units_pi_over_3(n: int) -> int:
    """Lower bound on total forced turn in units of pi/3.

    Every forced exterior turn contributes 2*pi/3, and the forced turn set is a
    vertex cover of the n-cycle.
    """

    return 2 * min_vertex_cover_size_cycle(n)


def turn_cover_contradiction(n: int) -> bool:
    """Return whether the turn-cover lower bound exceeds total turn 2*pi."""

    # Total turn 2*pi is 6 units of pi/3.
    return forced_turn_units_pi_over_3(n) > 6


def threshold_row(k: int) -> dict[str, Any]:
    """Return a checked threshold row for support size k."""

    n0 = pair_counting_wall(k)
    return {
        "k": k,
        "pair_counting_wall_n": n0,
        "saturation_improved_min_n": saturation_improved_wall(k),
        "equality_wall_has_n_at_least_8": n0 >= 8,
        "cycle_vertex_cover_size_at_wall": min_vertex_cover_size_cycle(n0),
        "forced_turn_lower_bound_units_pi_over_3": forced_turn_units_pi_over_3(n0),
        "total_turn_units_pi_over_3": 6,
        "equality_wall_ruled_out_by_turn_cover": turn_cover_contradiction(n0),
    }


def build_summary(min_k: int = 4, max_k: int = 8) -> dict[str, Any]:
    """Build a stable JSON summary for the saturation obstruction."""

    if min_k < 4:
        raise ValueError("min_k must be at least 4")
    if max_k < min_k:
        raise ValueError("max_k must be at least min_k")
    return {
        "schema": SCHEMA,
        "status": "PROVED_EQUALITY_WALL_OBSTRUCTION",
        "trust": TRUST,
        "claim_scope": (
            "Equality-wall obstruction for the edge-sensitive rich-support "
            "count. It upgrades all-centers support-size thresholds by one at "
            "k >= 4, but does not prove n=9, n=10, n=11, or Erdos Problem #97."
        ),
        "lemma": (
            "If every center has a same-radius support of size at least k >= 4, "
            "then n >= binom(k,2)+3."
        ),
        "proof_accounting": {
            "pair_counting_wall": "n = binom(k,2)+2",
            "equality_forces": (
                "all supports have size exactly k and every hull-edge/nonedge "
                "witness-pair capacity is saturated"
            ),
            "length_2_diagonal_step": "short-side apex saturation forces all side lengths equal",
            "length_3_diagonal_step": (
                "short-side apex saturation forces exterior turns equal to 2*pi/3 "
                "to hit every adjacent pair"
            ),
            "turn_contradiction": "a cycle vertex cover of forced 2*pi/3 turns exceeds total turn 2*pi",
        },
        "threshold_rows": [threshold_row(k) for k in range(min_k, max_k + 1)],
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Check the default small threshold table."""

    rows = {row["k"]: row for row in summary["threshold_rows"]}
    expected = {
        4: (8, 9, 4, 8),
        5: (12, 13, 6, 12),
        6: (17, 18, 9, 18),
        7: (23, 24, 12, 24),
        8: (30, 31, 15, 30),
    }
    for k, (counting_wall, improved, cover_size, turn_units) in expected.items():
        row = rows[k]
        got = (
            row["pair_counting_wall_n"],
            row["saturation_improved_min_n"],
            row["cycle_vertex_cover_size_at_wall"],
            row["forced_turn_lower_bound_units_pi_over_3"],
        )
        want = (counting_wall, improved, cover_size, turn_units)
        if got != want:
            raise AssertionError(f"k={k}: got {got}, expected {want}")
        if not row["equality_wall_has_n_at_least_8"]:
            raise AssertionError(f"k={k}: equality wall should have n >= 8")
        if not row["equality_wall_ruled_out_by_turn_cover"]:
            raise AssertionError(f"k={k}: expected turn-cover contradiction")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-k", type=int, default=4)
    parser.add_argument("--max-k", type=int, default=8)
    parser.add_argument(
        "--check",
        action="store_true",
        help="assert expected default thresholds",
    )
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    summary = build_summary(args.min_k, args.max_k)
    if args.check:
        if (args.min_k, args.max_k) != (4, 8):
            raise SystemExit("--check is only defined for the default k range")
        check_expected(summary)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"schema: {summary['schema']}")
        for row in summary["threshold_rows"]:
            print(
                f"k={row['k']}: pair-counting wall n="
                f"{row['pair_counting_wall_n']} is saturated-obstructed; "
                f"improved minimum n={row['saturation_improved_min_n']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
