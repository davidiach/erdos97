#!/usr/bin/env python3
"""Replay the all-rich-class pair budgets and profile-excess ledger.

The proof-facing statement is ``docs/all-rich-class-pair-budget.md``. This
script checks only integer arithmetic and a finite necessary-inequality
optimization; it is not an incidence realization search, a Euclidean
realization search, or a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from math import ceil


SCHEMA = "erdos97.all_rich_class_pair_budget.v1"
STATUS = "LEMMA_COUNTING_REPLAY"
TRUST = "EXACT_COMBINATORIAL_REPLAY"
MIN_N = 8


def global_pair_capacity(n: int) -> int:
    """Capacity of all unordered witness pairs in a strict convex n-gon."""

    if n < MIN_N:
        raise ValueError(f"the 4-bad ledger is recorded only for n >= {MIN_N}")
    hull_edges = n
    nonedges = n * (n - 1) // 2 - n
    return hull_edges + 2 * nonedges


def localized_pair_capacity(n: int) -> int:
    """Capacity of all witness pairs containing one fixed label."""

    if n < MIN_N:
        raise ValueError(f"the 4-bad ledger is recorded only for n >= {MIN_N}")
    return 2 + 2 * (n - 3)


def baseline_mass(n: int) -> int:
    """Six pair occurrences per bad center."""

    if n < MIN_N:
        raise ValueError(f"the 4-bad ledger is recorded only for n >= {MIN_N}")
    return 6 * n


def excess_budget(n: int) -> int:
    """Pair mass remaining beyond one size-four class per center."""

    return global_pair_capacity(n) - baseline_mass(n)


def complete_profile_mass(sizes: tuple[int, ...]) -> int:
    """All-class pair mass of one complete rich profile."""

    if not sizes or any(size < 4 for size in sizes):
        raise ValueError("a bad-center rich profile has one or more sizes >= 4")
    return sum(size * (size - 1) // 2 for size in sizes)


def complete_profile_excess(sizes: tuple[int, ...]) -> int:
    """Excess above the universal six-pair bad-center baseline."""

    return complete_profile_mass(sizes) - 6


@dataclass(frozen=True)
class ExclusiveOptimization:
    n: int
    excess_budget: int
    maximum_exclusive_pairs: int
    minimum_t4_centers: int
    t5_centers: int
    t44_centers: int
    singleton_t4_floor: int
    localized_forces_all_t4: bool


def max_rich_classes_per_witness(n: int) -> int:
    """Maximum rich-class incidences at one witness from the local budget."""

    return localized_pair_capacity(n) // 3


def localized_forces_all_t4(n: int) -> bool:
    """Whether local incidence capacity meets the 4-bad minimum exactly."""

    return n * max_rich_classes_per_witness(n) == 4 * n


def localized_profile_excess_budget(n: int) -> int:
    """Rich-class incidence left beyond one size-four class per center."""

    return n * (max_rich_classes_per_witness(n) - 4)


def endpoint_nonendpoint_incidence_capacity(n: int, exclusive: int) -> int:
    """Capacity for the six nonendpoint incidences per exclusive pair."""

    if not 0 <= 2 * exclusive <= n:
        raise ValueError("exclusive pairs must be vertex-disjoint")
    return (n - 2 * exclusive) * max_rich_classes_per_witness(n)


def endpoint_nonendpoint_pair_capacity(n: int, exclusive: int) -> int:
    """Edge-sensitive pair capacity inside the nonendpoint set."""

    if not 0 <= 2 * exclusive <= n:
        raise ValueError("exclusive pairs must be vertex-disjoint")
    nonendpoints = n - 2 * exclusive
    forced_internal_edges = max(0, n - 4 * exclusive)
    return nonendpoints * (nonendpoints - 1) - forced_internal_edges


def endpoint_pair_quadratic_bound(n: int) -> int:
    """Clean e bound after dropping the favorable hull-edge correction."""

    localized_pair_capacity(n)  # validate n
    return max(
        exclusive
        for exclusive in range(n // 2 + 1)
        if 6 * exclusive
        <= (n - 2 * exclusive) * (n - 2 * exclusive - 1)
    )


def exclusive_pair_inequality_bound(n: int) -> int:
    """Largest e allowed by the proved aggregate exclusive-pair inequalities."""

    if localized_forces_all_t4(n):
        return 0
    allowed = [
        exclusive
        for exclusive in range(n // 2 + 1)
        if 9 * exclusive <= 4 * n
        and 6 * exclusive
        <= endpoint_nonendpoint_incidence_capacity(n, exclusive)
        and 6 * exclusive <= endpoint_nonendpoint_pair_capacity(n, exclusive)
    ]
    return max(allowed, default=0)


def maximum_exclusive_pairs(n: int) -> ExclusiveOptimization:
    """Optimize e under the excess, charge, and endpoint-center bounds."""

    budget = excess_budget(n)
    local_profile_budget = localized_profile_excess_budget(n)
    t4_floor = ceil(n / 4)
    all_t4 = localized_forces_all_t4(n)
    best: tuple[int, int, int, int] | None = None
    for exclusive in range(n // 2 + 1):
        for t5 in range(n + 1):
            for t44 in range(n - t5 + 1):
                if all_t4 and (exclusive or t5 or t44):
                    continue
                t4 = n if all_t4 else max(t4_floor, 2 * exclusive)
                if t4 + t5 + t44 > n:
                    continue
                if 4 * t5 + 6 * t44 > budget:
                    continue
                if t5 + 4 * t44 > local_profile_budget:
                    continue
                if exclusive > 2 * t5 + 4 * t44:
                    continue
                if 6 * exclusive > endpoint_nonendpoint_incidence_capacity(
                    n, exclusive
                ):
                    continue
                if 6 * exclusive > endpoint_nonendpoint_pair_capacity(n, exclusive):
                    continue
                if best is None or exclusive > best[0]:
                    best = (exclusive, t4, t5, t44)
    if best is None:
        raise AssertionError("T4-only profile counts must always be feasible")
    return ExclusiveOptimization(
        n=n,
        excess_budget=budget,
        maximum_exclusive_pairs=best[0],
        minimum_t4_centers=best[1],
        t5_centers=best[2],
        t44_centers=best[3],
        singleton_t4_floor=t4_floor,
        localized_forces_all_t4=all_t4,
    )


def build_summary() -> dict[str, object]:
    """Build the deterministic reviewer-facing summary."""

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Exact arithmetic replay for global/local pair capacities over all "
            "rich classes and their minimal two-deletion profile excess; not "
            "a Euclidean proof checker, not a proof or counterexample for "
            "Erdos Problem #97."
        ),
        "optimization_scope": (
            "The reported exclusive-pair maximum is only the maximum allowed "
            "by the listed aggregate necessary inequalities; it is not an "
            "attainable incidence system or Euclidean realization claim."
        ),
        "profile_masses": {
            "T4": complete_profile_mass((4,)),
            "T5": complete_profile_mass((5,)),
            "T44": complete_profile_mass((4, 4)),
        },
        "profile_excesses": {
            "T4": complete_profile_excess((4,)),
            "T5": complete_profile_excess((5,)),
            "T44": complete_profile_excess((4, 4)),
        },
        "rows": [
            {
                **asdict(maximum_exclusive_pairs(n)),
                "global_pair_capacity": global_pair_capacity(n),
                "localized_pair_capacity": localized_pair_capacity(n),
                "max_rich_classes_per_witness": max_rich_classes_per_witness(n),
                "localized_profile_excess_budget": localized_profile_excess_budget(
                    n
                ),
                "baseline_mass": baseline_mass(n),
                "unrestricted_matching_floor": n // 2,
                "simple_exclusive_center_bound": 4 * n // 9,
                "endpoint_pair_quadratic_bound": endpoint_pair_quadratic_bound(n),
                "exclusive_pair_inequality_bound": exclusive_pair_inequality_bound(
                    n
                ),
            }
            for n in range(MIN_N, 65)
        ],
    }


def check_expected(summary: dict[str, object]) -> None:
    """Check identities and the exact small-n optimization boundary."""

    if summary["profile_masses"] != {"T4": 6, "T5": 10, "T44": 12}:
        raise AssertionError("unexpected profile masses")
    if summary["profile_excesses"] != {"T4": 0, "T5": 4, "T44": 6}:
        raise AssertionError("unexpected profile excesses")

    rows = summary["rows"]
    if not isinstance(rows, list):
        raise AssertionError("missing rows")
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("malformed row")
        n = int(row["n"])
        if int(row["global_pair_capacity"]) != n * (n - 2):
            raise AssertionError(f"n={n}: global capacity mismatch")
        if int(row["localized_pair_capacity"]) != 2 * n - 4:
            raise AssertionError(f"n={n}: localized capacity mismatch")
        expected_maximum = exclusive_pair_inequality_bound(n)
        if int(row["maximum_exclusive_pairs"]) != expected_maximum:
            raise AssertionError(f"n={n}: unexpected exclusive-pair maximum")
        if bool(row["localized_forces_all_t4"]) != (n in (8, 9)):
            raise AssertionError(f"n={n}: unexpected localized-integrality flag")
        if n >= 10:
            clean_bound = min(4 * n // 9, endpoint_pair_quadratic_bound(n))
            if expected_maximum != clean_bound:
                raise AssertionError(f"n={n}: clean bound mismatch")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="assert stable formulae")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    summary = build_summary()
    if args.check:
        check_expected(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        first = maximum_exclusive_pairs(MIN_N)
        print(
            "all-rich-class pair ledger: "
            f"n={MIN_N} excess={first.excess_budget}, "
            f"max exclusive pairs={first.maximum_exclusive_pairs}"
        )


if __name__ == "__main__":
    main()
