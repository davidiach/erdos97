#!/usr/bin/env python3
"""Check the edge-sensitive rich-support counting bound for Erdos Problem #97.

This standalone checker verifies a proof-facing counting lemma: for any choice
of one same-radius support R_i at each center of a strict convex n-gon,

    sum_i binom(|R_i|, 2) <= n(n - 2).

The coarse reason is that a fixed witness pair {a,b} can occur in at most two
supports, since all centers using both witnesses lie on the perpendicular
bisector of ab.  The edge-sensitive improvement is that if {a,b} is a hull
edge, its perpendicular bisector already meets the polygon boundary at the
midpoint of that edge, so it can contain at most one further boundary vertex
and hence at most one center.  There are n hull-edge witness pairs and
binom(n,2)-n non-edge witness pairs.
"""

from __future__ import annotations

import argparse
import json
from itertools import combinations
from math import comb
from typing import Any

SCHEMA = "erdos97.rich_support_counting_bound.v3"
TRUST = "LEMMA"


def coarse_pair_budget(n: int) -> int:
    """Pair-sharing budget when every witness pair has capacity two."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return n * (n - 1)


def edge_sensitive_pair_budget(n: int) -> int:
    """Pair-sharing budget with hull-edge witness pairs counted at capacity one."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return 0
    # n hull edges have capacity 1; the remaining binom(n,2)-n pairs have
    # capacity 2.
    return max(0, n + 2 * (comb(n, 2) - n))


def pair_budget(n: int) -> int:
    """Maximum total center-witness-pair incidences allowed by pair-sharing."""

    return edge_sensitive_pair_budget(n)


def all_centers_min_n(k: int) -> int:
    """Smallest n not ruled out by pair counting alone for support size k."""

    if k < 0:
        raise ValueError("k must be nonnegative")
    return comb(k, 2) + 2


def support_profile_pair_cost(profile: list[int] | tuple[int, ...]) -> int:
    """Return sum binom(size, 2) for a support-size profile."""

    if any(size < 0 for size in profile):
        raise ValueError("support sizes must be nonnegative")
    return sum(comb(size, 2) for size in profile)


def counting_feasible_support_profiles(
    n: int,
    min_size: int = 4,
) -> list[tuple[int, ...]]:
    """Enumerate sorted support-size profiles allowed by the pair budget.

    The output is a pure counting relaxation: it records only profiles
    ``s_0 <= ... <= s_{n-1}`` with ``min_size <= s_i < n`` and
    ``sum_i binom(s_i, 2) <= n(n-2)``. It does not check row-intersection,
    cyclic-order, or vertex-circle constraints.
    """

    if n <= 0:
        raise ValueError("n must be positive")
    if min_size < 0 or min_size >= n:
        raise ValueError("min_size must satisfy 0 <= min_size < n")

    budget = pair_budget(n)
    profiles: list[tuple[int, ...]] = []

    def visit(start_size: int, remaining: int, used: int, profile: list[int]) -> None:
        if remaining == 0:
            profiles.append(tuple(profile))
            return
        for size in range(start_size, n):
            new_used = used + comb(size, 2)
            # Profiles are nondecreasing, so every remaining size is at least this size.
            min_completion = new_used + (remaining - 1) * comb(size, 2)
            if min_completion > budget:
                break
            visit(size, remaining - 1, new_used, [*profile, size])

    visit(min_size, n, 0, [])
    return profiles


def max_total_support_size(n: int, min_size: int = 4) -> tuple[int, list[int]]:
    """Maximize sum |R_i| under sum binom(|R_i|,2) <= n(n-2).

    This is only a necessary counting relaxation.  It ignores all cyclic-order,
    row-intersection, and vertex-circle constraints beyond the hull-edge
    witness-pair capacity used in the counting lemma.
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


def _n9_vertex_deficiency_floor(rich_increment: int) -> int:
    """Minimum possible pair-capacity deficiency for one nonagon label."""

    if rich_increment < 0:
        raise ValueError("rich_increment must be nonnegative")
    if rich_increment > 14:
        raise ValueError("rich_increment exceeds the nonagon label-pair capacity")
    return (14 - rich_increment) % 3


def _min_n9_vertex_deficiency_from_profile(profile: tuple[int, ...]) -> int:
    """Relaxedly minimize total nonagon vertex deficiency for one size profile."""

    if len(profile) != 9:
        raise ValueError("n=9 profile must have exactly nine support sizes")
    if any(size < 4 or size >= 9 for size in profile):
        raise ValueError("n=9 support sizes must satisfy 4 <= size < 9")

    states: set[tuple[int, ...]] = {tuple([0] * 9)}
    for size in profile:
        increment = size - 4
        if increment == 0:
            continue
        next_states: set[tuple[int, ...]] = set()
        for state in states:
            for witnesses in combinations(range(9), size):
                updated = list(state)
                for vertex in witnesses:
                    updated[vertex] += increment
                next_states.add(tuple(sorted(updated)))
        states = next_states

    return min(
        sum(_n9_vertex_deficiency_floor(increment) for increment in state)
        for state in states
    )


def n9_profile_deficiency_refinement() -> dict[str, Any]:
    """Return the nonagon profile refinement beyond the raw pair budget."""

    profiles = counting_feasible_support_profiles(9, min_size=4)
    rows: list[dict[str, Any]] = []
    for profile in profiles:
        pair_cost_value = support_profile_pair_cost(profile)
        pair_slack = pair_budget(9) - pair_cost_value
        required_vertex_deficiency = 2 * pair_slack
        min_vertex_deficiency = _min_n9_vertex_deficiency_from_profile(profile)
        excluded = min_vertex_deficiency > required_vertex_deficiency
        rows.append(
            {
                "profile": list(profile),
                "pair_cost": pair_cost_value,
                "pair_slack": pair_slack,
                "required_total_vertex_deficiency": required_vertex_deficiency,
                "minimum_total_vertex_deficiency_from_weighting": min_vertex_deficiency,
                "status": (
                    "EXCLUDED_BY_VERTEX_DEFICIENCY"
                    if excluded
                    else "NOT_EXCLUDED_BY_THIS_REFINEMENT"
                ),
            }
        )

    remaining = [
        row["profile"] for row in rows if row["status"] == "NOT_EXCLUDED_BY_THIS_REFINEMENT"
    ]
    return {
        "claim": (
            "In a hypothetical 4-bad nonagon, every maximum same-radius support "
            "has size exactly 4; the raw size-five and size-six profiles are "
            "excluded by pair-slack/vertex-deficiency counting."
        ),
        "pair_capacity_degree_per_label": 14,
        "raw_counting_feasible_profile_count": len(rows),
        "profiles": rows,
        "remaining_profiles_after_refinement": remaining,
        "consequence": (
            "The only remaining support-size profile is [4]*9. Therefore a "
            "4-bad nonagon, if it exists, is an exact-four selected-witness "
            "object at every center; applying the same weighted-degree cap then "
            "forces every witness label to have selected indegree 4."
        ),
    }


def row_summary(n: int) -> dict[str, Any]:
    """Return the counting-bound row for one n."""

    if n <= 4:
        # The Erdos #97 selected-witness problem starts at n >= 5; keep this
        # helper focused on the bad-polygon range where min_size=4 is feasible.
        raise ValueError("n must be at least 5")
    baseline_cost = n * comb(4, 2)
    budget = pair_budget(n)
    four_bad_ruled_out = baseline_cost > budget
    row: dict[str, Any] = {
        "n": n,
        "coarse_pair_budget": coarse_pair_budget(n),
        "edge_sensitive_pair_budget": budget,
    }
    if four_bad_ruled_out:
        row.update(
            {
                "four_bad_ruled_out_by_edge_sensitive_pair_counting": True,
                "max_total_support_size_given_E_ge_4": None,
                "max_surplus_over_exact_four": None,
                "one_extremal_support_size_multiset": None,
                "all_centers_size_at_least_5_ruled_out_by_counting": True,
                "max_centers_with_E_at_least_5_by_counting": 0,
                "min_centers_with_E_equal_4_by_counting": None,
            }
        )
        return row

    total, sizes = max_total_support_size(n, min_size=4)
    max_non_exact = max_non_exact_four_centers(n)
    row.update(
        {
            "four_bad_ruled_out_by_edge_sensitive_pair_counting": False,
            "max_total_support_size_given_E_ge_4": total,
            "max_surplus_over_exact_four": total - 4 * n,
            "one_extremal_support_size_multiset": sizes,
            "all_centers_size_at_least_5_ruled_out_by_counting": n < all_centers_min_n(5),
            "max_centers_with_E_at_least_5_by_counting": max_non_exact,
            "min_centers_with_E_equal_4_by_counting": max(0, n - max_non_exact),
        }
    )
    if n == 9:
        row.update(
            {
                "n9_max_support_size_after_vertex_deficiency_refinement": 4,
                "n9_all_centers_exact_four_after_vertex_deficiency_refinement": True,
                "n9_selected_indegree_for_exact_four_profile": 4,
            }
        )
    return row


def build_summary(min_n: int = 5, max_n: int = 12) -> dict[str, Any]:
    """Build a stable JSON summary for the lemma and small-n consequences."""

    return {
        "schema": SCHEMA,
        "status": "PROVED_COUNTING_LEMMA",
        "trust": TRUST,
        "claim_scope": (
            "Proof-facing edge-sensitive rich-support pair-counting lemma only. "
            "It records necessary support-size consequences and the n=9 "
            "vertex-deficiency profile refinement; it does not prove n=9, n=10, "
            "n=11, or Erdos Problem #97."
        ),
        "lemma": (
            "For same-radius supports R_i in a strict convex n-gon, "
            "sum_i binom(|R_i|, 2) <= n(n - 2)."
        ),
        "capacity_accounting": {
            "hull_edge_pairs": "n pairs, capacity 1 each",
            "nonedge_pairs": "binom(n, 2) - n pairs, capacity 2 each",
            "total_capacity": "n + 2*(binom(n,2)-n) = n(n-2)",
            "coarse_capacity_for_comparison": "n(n-1)",
        },
        "all_centers_min_support_thresholds": {
            str(k): all_centers_min_n(k) for k in range(4, 8)
        },
        "n9_profile_deficiency_refinement": n9_profile_deficiency_refinement(),
        "rows": [row_summary(n) for n in range(min_n, max_n + 1)],
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Check the small consequences used by the proposed repo note."""

    thresholds = summary["all_centers_min_support_thresholds"]
    expected_thresholds = {"4": 8, "5": 12, "6": 17, "7": 23}
    if thresholds != expected_thresholds:
        raise AssertionError(f"got thresholds {thresholds}, expected {expected_thresholds}")

    rows = {row["n"]: row for row in summary["rows"]}
    expected = {
        8: (32, 0, 0, 8),
        9: (38, 2, 2, 7),
        10: (45, 5, 5, 5),
        11: (52, 8, 8, 3),
        12: (60, 12, 12, 0),
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

    for n in (5, 6, 7):
        if not rows[n]["four_bad_ruled_out_by_edge_sensitive_pair_counting"]:
            raise AssertionError(
                f"n={n}: expected edge-sensitive pair-counting to rule out four-bad supports"
            )

    refinement = summary["n9_profile_deficiency_refinement"]
    remaining = refinement["remaining_profiles_after_refinement"]
    if remaining != [[4, 4, 4, 4, 4, 4, 4, 4, 4]]:
        raise AssertionError(f"unexpected n=9 refined profiles: {remaining}")
    statuses = {tuple(row["profile"]): row["status"] for row in refinement["profiles"]}
    expected_statuses = {
        (4, 4, 4, 4, 4, 4, 4, 4, 4): "NOT_EXCLUDED_BY_THIS_REFINEMENT",
        (4, 4, 4, 4, 4, 4, 4, 4, 5): "EXCLUDED_BY_VERTEX_DEFICIENCY",
        (4, 4, 4, 4, 4, 4, 4, 5, 5): "EXCLUDED_BY_VERTEX_DEFICIENCY",
        (4, 4, 4, 4, 4, 4, 4, 4, 6): "EXCLUDED_BY_VERTEX_DEFICIENCY",
    }
    if statuses != expected_statuses:
        raise AssertionError(f"unexpected n=9 profile statuses: {statuses}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=5)
    parser.add_argument("--max-n", type=int, default=12)
    parser.add_argument("--check", action="store_true", help="assert expected small-n consequences")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    summary = build_summary(args.min_n, args.max_n)
    if args.check:
        if (args.min_n, args.max_n) != (5, 12):
            raise SystemExit("--check is only defined for the default n range")
        check_expected(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"schema: {summary['schema']}")
        print(
            "pair-counting alone: all centers with size >=5 requires n >=",
            all_centers_min_n(5),
        )
        n9_refinement = summary["n9_profile_deficiency_refinement"]
        print(
            "n=9 refined support-size profiles:",
            n9_refinement["remaining_profiles_after_refinement"],
        )
        for row in summary["rows"]:
            if row["four_bad_ruled_out_by_edge_sensitive_pair_counting"]:
                print(f"n={row['n']}: four-bad supports ruled out by edge-sensitive pair-counting")
            else:
                print(
                    f"n={row['n']}: max total={row['max_total_support_size_given_E_ge_4']}, "
                    f"max surplus={row['max_surplus_over_exact_four']}, "
                    f"min exact-four centers={row['min_centers_with_E_equal_4_by_counting']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
