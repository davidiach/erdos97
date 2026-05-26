#!/usr/bin/env python3
"""Check the localized rich-support counting cap for Erdos Problem #97.

For any choice of same-radius supports R_i in a strict convex n-gon, the
localized pair-sharing cap says that each fixed witness label x satisfies

    sum_{i: x in R_i} (|R_i| - 1) <= 2n - 4.

The proof counts support pairs {x,y}.  The two hull-neighbor pairs incident to
x have capacity one, and the remaining n-3 pairs have capacity two.  This
standalone checker records small-n consequences, especially that a hypothetical
4-bad nonagon is forced into the all-exact-four, selected-indegree-four case by
counting alone.
"""

from __future__ import annotations

import argparse
import json
from math import comb
from typing import Any

SCHEMA = "erdos97.localized_rich_support_counting.v1"
TRUST = "LEMMA"


def edge_sensitive_pair_budget(n: int) -> int:
    """Global support-pair budget from hull-edge/nonedge pair capacities."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    if n == 0:
        return 0
    return max(0, n + 2 * (comb(n, 2) - n))


def localized_pair_budget_per_label(n: int) -> int:
    """Incident support-pair budget for one fixed witness label."""

    if n < 3:
        raise ValueError("n must be at least 3")
    return 2 + 2 * (n - 3)


def all_centers_min_support_threshold(k: int) -> int:
    """Smallest n not ruled out when every center has support size at least k."""

    if k < 0:
        raise ValueError("k must be nonnegative")
    return comb(k, 2) + 2


def max_non_exact_centers_by_global_pair_budget(n: int) -> int:
    """Maximum number of size-at-least-five centers allowed by global pair count."""

    baseline = n * comb(4, 2)
    budget = edge_sensitive_pair_budget(n)
    if baseline > budget:
        return -1
    extra_pair_budget = budget - baseline
    # The cheapest non-exact-four center has size five and costs 10-6 = 4
    # additional support-pair incidences.
    return min(n, extra_pair_budget // (comb(5, 2) - comb(4, 2)))


def max_non_exact_centers_by_local_occurrence_budget(n: int) -> int:
    """Maximum number of size-at-least-five centers allowed by local occurrence caps.

    For 4-bad supports, every occurrence x in R_i contributes at least three to
    the localized budget at x.  Hence each label occurs in at most
    floor((2n-4)/3) supports.  A non-exact-four support has at least one more
    occurrence than an exact-four support.
    """

    baseline = 4 * n
    per_label_occurrence_cap = localized_pair_budget_per_label(n) // 3
    total_occurrence_cap = n * per_label_occurrence_cap
    if baseline > total_occurrence_cap:
        return -1
    return min(n, total_occurrence_cap - baseline)


def row_summary(n: int) -> dict[str, Any]:
    """Return a stable JSON row for one n."""

    if n < 5:
        raise ValueError("n must be at least 5")

    baseline_pair_demand = n * comb(4, 2)
    global_pair_budget = edge_sensitive_pair_budget(n)
    four_bad_ruled_out = baseline_pair_demand > global_pair_budget
    localized_budget = localized_pair_budget_per_label(n)
    occurrence_cap_per_label = localized_budget // 3
    total_occurrence_cap = n * occurrence_cap_per_label

    row: dict[str, Any] = {
        "n": n,
        "global_edge_sensitive_pair_budget": global_pair_budget,
        "baseline_pair_demand_for_E_ge_4": baseline_pair_demand,
        "localized_pair_budget_per_label": localized_budget,
        "max_support_occurrences_per_label_if_E_ge_4": occurrence_cap_per_label,
        "total_support_occurrence_cap_if_E_ge_4": total_occurrence_cap,
        "four_bad_ruled_out_by_global_pair_counting": four_bad_ruled_out,
    }

    if four_bad_ruled_out:
        row.update(
            {
                "global_extra_pair_budget_over_exact_four": None,
                "local_extra_occurrence_budget_over_exact_four": None,
                "max_non_exact_four_centers_by_global_pair_budget": None,
                "max_non_exact_four_centers_by_local_occurrence_budget": None,
                "max_non_exact_four_centers_by_best_counting_bound": None,
                "min_exact_four_centers_by_best_counting_bound": None,
                "all_centers_forced_exact_four_by_localized_counting": None,
                "exact_four_selected_indegree_forced_regular_by_localized_counting": None,
            }
        )
        return row

    global_max = max_non_exact_centers_by_global_pair_budget(n)
    local_max = max_non_exact_centers_by_local_occurrence_budget(n)
    best_max = min(global_max, local_max)
    row.update(
        {
            "global_extra_pair_budget_over_exact_four": global_pair_budget - baseline_pair_demand,
            "local_extra_occurrence_budget_over_exact_four": total_occurrence_cap - 4 * n,
            "max_non_exact_four_centers_by_global_pair_budget": global_max,
            "max_non_exact_four_centers_by_local_occurrence_budget": local_max,
            "max_non_exact_four_centers_by_best_counting_bound": best_max,
            "min_exact_four_centers_by_best_counting_bound": n - best_max,
            "all_centers_forced_exact_four_by_localized_counting": local_max == 0,
            # If all supports have size exactly four, the same per-label cap
            # forces selected indegree <= floor((2n-4)/3).  Since the average
            # selected indegree is four, regularity follows exactly when this
            # cap is four.
            "exact_four_selected_indegree_forced_regular_by_localized_counting": (
                occurrence_cap_per_label == 4
            ),
        }
    )
    return row


def build_summary(min_n: int = 5, max_n: int = 12) -> dict[str, Any]:
    """Build the checker summary."""

    return {
        "schema": SCHEMA,
        "status": "PROVED_LOCALIZED_COUNTING_LEMMA",
        "trust": TRUST,
        "claim_scope": (
            "Necessary localized rich-support counting only.  The n=9 consequence "
            "forces hypothetical 4-bad nonagons into the all-exact-four, "
            "selected-indegree-four case, but does not prove n=9 or Erdos #97."
        ),
        "lemma": (
            "For every fixed witness label x, "
            "sum_{i: x in R_i} (|R_i|-1) <= 2n-4."
        ),
        "capacity_accounting_per_label": {
            "hull_neighbor_pairs_incident_to_x": "2 pairs, capacity 1 each",
            "non_neighbor_pairs_incident_to_x": "n-3 pairs, capacity 2 each",
            "total_capacity": "2 + 2*(n-3) = 2n-4",
        },
        "all_centers_min_support_thresholds": {
            str(k): all_centers_min_support_threshold(k) for k in range(4, 8)
        },
        "rows": [row_summary(n) for n in range(min_n, max_n + 1)],
        "n9_consequence": {
            "all_centers_exact_four": True,
            "selected_indegree_per_label": 4,
            "reason": (
                "For n=9, each label occurs in at most floor(14/3)=4 supports, "
                "so total support occurrences are at most 36; the 4-bad baseline "
                "already requires 36 occurrences."
            ),
        },
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Check the small-n consequences intended for the repository note."""

    thresholds = summary["all_centers_min_support_thresholds"]
    expected_thresholds = {"4": 8, "5": 12, "6": 17, "7": 23}
    if thresholds != expected_thresholds:
        raise AssertionError(f"got thresholds {thresholds}, expected {expected_thresholds}")

    rows = {row["n"]: row for row in summary["rows"]}
    for n in (5, 6, 7):
        if not rows[n]["four_bad_ruled_out_by_global_pair_counting"]:
            raise AssertionError(f"n={n}: expected four-bad supports to be ruled out")

    expected = {
        8: (0, 8, True, True),
        9: (0, 9, True, True),
        10: (5, 5, False, False),
        11: (8, 3, False, False),
        12: (12, 0, False, False),
    }
    for n, (max_non_exact, min_exact, forced_exact, forced_regular) in expected.items():
        row = rows[n]
        got = (
            row["max_non_exact_four_centers_by_best_counting_bound"],
            row["min_exact_four_centers_by_best_counting_bound"],
            row["all_centers_forced_exact_four_by_localized_counting"],
            row["exact_four_selected_indegree_forced_regular_by_localized_counting"],
        )
        want = (max_non_exact, min_exact, forced_exact, forced_regular)
        if got != want:
            raise AssertionError(f"n={n}: got {got}, expected {want}")

    n9 = rows[9]
    if n9["total_support_occurrence_cap_if_E_ge_4"] != 36:
        raise AssertionError("n=9 should have total support occurrence cap 36")
    if not summary["n9_consequence"]["all_centers_exact_four"]:
        raise AssertionError("n=9 consequence should force exact-four supports")


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
        for row in summary["rows"]:
            n = row["n"]
            if row["four_bad_ruled_out_by_global_pair_counting"]:
                print(f"n={n}: four-bad supports ruled out by global pair counting")
            else:
                print(
                    f"n={n}: min exact-four centers by best count = "
                    f"{row['min_exact_four_centers_by_best_counting_bound']}; "
                    f"localized exact-four forced = "
                    f"{row['all_centers_forced_exact_four_by_localized_counting']}"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
