#!/usr/bin/env python3
"""Check the rich-support counting bound for Erdos Problem #97.

This standalone checker verifies a simple proof-facing counting lemma:
for any choice of one same-radius support R_i at each center of a strict convex
n-gon, sum_i binom(|R_i|, 2) <= n(n - 1).  The reason is that a fixed witness
pair {a,b} can occur in at most two supports, since all centers using both
witnesses lie on the perpendicular bisector of ab, and a line contains at most
two vertices of a strictly convex polygon.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from typing import Any

SCHEMA = "erdos97.rich_support_counting_bound.v1"
TRUST = "LEMMA"


def pair_budget(n: int) -> int:
    """Maximum total center-witness-pair incidences allowed by pair-sharing."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return n * (n - 1)


def all_centers_min_n(k: int) -> int:
    """Smallest n not ruled out when every center has support size at least k."""

    if k < 0:
        raise ValueError("k must be nonnegative")
    return comb(k, 2) + 1


def max_total_support_size(n: int, min_size: int = 4) -> tuple[int, list[int]]:
    """Maximize sum |R_i| under sum binom(|R_i|,2) <= n(n-1).

    This is only a necessary counting relaxation.  It ignores all cyclic-order,
    row-intersection, and vertex-circle constraints.
    """

    if n <= 0:
        raise ValueError("n must be positive")
    if min_size < 0 or min_size >= n:
        raise ValueError("min_size must satisfy 0 <= min_size < n")

    budget = pair_budget(n)
    if n * comb(min_size, 2) > budget:
        raise ValueError(
            f"no counting-feasible family with {n} supports of size at least {min_size}"
        )
    # dp[cost] = (total_support_size, sorted support-size multiset)
    dp: dict[int, tuple[int, list[int]]] = {0: (0, [])}
    for _ in range(n):
        next_dp: dict[int, tuple[int, list[int]]] = {}
        for used, (total, sizes) in dp.items():
            for size in range(min_size, n):
                new_used = used + comb(size, 2)
                if new_used > budget:
                    continue
                candidate = (total + size, sorted([*sizes, size]))
                if new_used not in next_dp or candidate[0] > next_dp[new_used][0]:
                    next_dp[new_used] = candidate
        dp = next_dp
    used, (total, sizes) = max(dp.items(), key=lambda item: (item[1][0], -item[0]))
    # Include the exact used budget in a harmless way by returning the witness sizes.
    _ = used
    return total, sizes


def max_non_exact_four_centers(n: int) -> int:
    """Maximum number of centers with support size at least 5 in a 4-bad relaxation."""

    baseline = n * comb(4, 2)
    extra_budget = pair_budget(n) - baseline
    if extra_budget < 0:
        return -1
    # Raising one center from size 4 to size 5 costs 4 pair incidences, and
    # this is the cheapest way to make a center non-exact-four.
    return min(n, extra_budget // (comb(5, 2) - comb(4, 2)))


def row_summary(n: int) -> dict[str, Any]:
    """Return the counting-bound row for one n."""

    if n <= 4:
        # The Erdos #97 selected-witness problem starts at n >= 5; keep this
        # helper focused on the bad-polygon range where min_size=4 is feasible.
        raise ValueError("n must be at least 5")
    baseline_cost = n * comb(4, 2)
    budget = pair_budget(n)
    four_bad_ruled_out = baseline_cost > budget
    if four_bad_ruled_out:
        return {
            "n": n,
            "pair_budget": budget,
            "four_bad_ruled_out_by_pair_counting": True,
            "max_total_support_size_given_E_ge_4": None,
            "max_surplus_over_exact_four": None,
            "one_extremal_support_size_multiset": None,
            "all_centers_size_at_least_5_ruled_out_by_counting": True,
            "max_centers_with_E_at_least_5_by_counting": 0,
            "min_centers_with_E_equal_4_by_counting": None,
        }

    total, sizes = max_total_support_size(n, min_size=4)
    max_non_exact = max_non_exact_four_centers(n)
    return {
        "n": n,
        "pair_budget": budget,
        "four_bad_ruled_out_by_pair_counting": False,
        "max_total_support_size_given_E_ge_4": total,
        "max_surplus_over_exact_four": total - 4 * n,
        "one_extremal_support_size_multiset": sizes,
        "all_centers_size_at_least_5_ruled_out_by_counting": n < all_centers_min_n(5),
        "max_centers_with_E_at_least_5_by_counting": max_non_exact,
        "min_centers_with_E_equal_4_by_counting": max(0, n - max_non_exact),
    }


def build_summary(min_n: int = 5, max_n: int = 11) -> dict[str, Any]:
    """Build a stable JSON summary for the lemma and small-n consequences."""

    return {
        "schema": SCHEMA,
        "status": "PROVED_COUNTING_LEMMA",
        "trust": TRUST,
        "claim_scope": (
            "Proof-facing rich-support pair-counting lemma only. It records "
            "necessary support-size consequences and does not prove n=9, "
            "n=10, or Erdos Problem #97."
        ),
        "lemma": (
            "For same-radius supports R_i in a strict convex n-gon, "
            "sum_i binom(|R_i|, 2) <= n(n - 1)."
        ),
        "all_centers_min_support_thresholds": {
            str(k): all_centers_min_n(k) for k in range(4, 8)
        },
        "rows": [row_summary(n) for n in range(min_n, max_n + 1)],
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Check the small consequences used by the proposed repo note."""

    thresholds = summary["all_centers_min_support_thresholds"]
    if thresholds["5"] != 11:
        raise AssertionError("all-centers size-five threshold should be n >= 11")

    rows = {row["n"]: row for row in summary["rows"]}
    expected = {
        7: (28, 0, 0, 7),
        8: (34, 2, 2, 6),
        9: (40, 4, 4, 5),
        10: (47, 7, 7, 3),
        11: (55, 11, 11, 0),
    }
    for n, (total, surplus, max_non_exact, min_exact) in expected.items():
        row = rows[n]
        got = (
            row["max_total_support_size_given_E_ge_4"],
            row["max_surplus_over_exact_four"],
            row["max_centers_with_E_at_least_5_by_counting"],
            row["min_centers_with_E_equal_4_by_counting"],
        )
        want = (total, surplus, max_non_exact, min_exact)
        if got != want:
            raise AssertionError(f"n={n}: got {got}, expected {want}")

    for n in (5, 6):
        if not rows[n]["four_bad_ruled_out_by_pair_counting"]:
            raise AssertionError(f"n={n}: expected pair-counting to rule out four-bad supports")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=11)
    parser.add_argument("--check", action="store_true", help="assert expected small-n consequences")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    summary = build_summary(args.min_n, args.max_n)
    if args.check:
        if (args.min_n, args.max_n) != (5, 11):
            raise SystemExit("--check is only defined for the default n range")
        check_expected(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"schema: {summary['schema']}")
        print("all centers with size >=5 requires n >=", all_centers_min_n(5))
        for row in summary["rows"]:
            if row["four_bad_ruled_out_by_pair_counting"]:
                print(f"n={row['n']}: four-bad supports ruled out by pair-counting")
            else:
                print(
                    f"n={row['n']}: max total={row['max_total_support_size_given_E_ge_4']}, "
                    f"max surplus={row['max_surplus_over_exact_four']}, "
                    f"min exact-four centers={row['min_centers_with_E_equal_4_by_counting']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
