#!/usr/bin/env python3
"""Replay the exact counting ledger for the two-deletion profile lemma.

The proof-facing statement is in ``docs/minimal-two-deletion-profile.md``.
This script checks only finite-set incidence and integer arithmetic. It does
not prove cardinality-minimality, Euclidean realizability, or Erdos Problem
#97.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import json
from math import ceil, comb
from typing import Mapping


SCHEMA = "erdos97.minimal_two_deletion_profile.v1"
STATUS = "LEMMA_COUNTING_REPLAY"
TRUST = "EXACT_COMBINATORIAL_REPLAY"
MIN_N = 9


def profile_capacity(n: int, profile: str) -> int:
    """Return the exact number of deletion pairs certified by one center."""

    if n < MIN_N:
        raise ValueError(f"the reviewer ledger is recorded only for n >= {MIN_N}")
    if profile == "T4":
        return comb(n - 1, 2) - comb(n - 5, 2)
    if profile == "T5":
        return comb(5, 2)
    if profile == "T44":
        return 4 * 4
    raise ValueError(f"unknown profile: {profile}")


def direct_profile_capacity(n: int, profile: str) -> int:
    """Enumerate deletion pairs for canonical disjoint rich classes."""

    if n < MIN_N:
        raise ValueError(f"the reviewer ledger is recorded only for n >= {MIN_N}")
    labels = set(range(1, n))  # center 0 is not a deletion seed for this count
    if profile == "T4":
        classes = (set(range(1, 5)),)
        needed = (1,)
    elif profile == "T5":
        classes = (set(range(1, 6)),)
        needed = (2,)
    elif profile == "T44":
        classes = (set(range(1, 5)), set(range(5, 9)))
        needed = (1, 1)
    else:
        raise ValueError(f"unknown profile: {profile}")
    return sum(
        all(len(set(pair) & rich_class) >= demand for rich_class, demand in zip(classes, needed, strict=True))
        for pair in combinations(sorted(labels), 2)
    )


def singleton_t4_lower_bound(n: int) -> int:
    """Minimum number of four-classes needed merely to cover n vertices."""

    if n < MIN_N:
        raise ValueError(f"the reviewer ledger is recorded only for n >= {MIN_N}")
    return ceil(n / 4)


def pair_average_t4_lower_bound(n: int) -> int:
    """T4 count demanded by the coarse pair-capacity average alone."""

    capacity = profile_capacity(n, "T4")
    return ceil(comb(n, 2) / capacity)


def pair_coverage_rhs(n: int, t4: int, t5: int, t44: int) -> int:
    """Right side of the deletion-pair double-counting inequality."""

    if min(t4, t5, t44) < 0:
        raise ValueError("profile counts must be nonnegative")
    return (
        profile_capacity(n, "T4") * t4
        + profile_capacity(n, "T5") * t5
        + profile_capacity(n, "T44") * t44
    )


def exclusive_pair_matching_capacity(t5: int, t44: int) -> int:
    """Maximum exclusive-pair charges allowed by vertex disjointness."""

    if min(t5, t44) < 0:
        raise ValueError("profile counts must be nonnegative")
    return 2 * t5 + 4 * t44


def exclusive_pair_t4_center_floor(exclusive_pairs: int) -> int:
    """T4 endpoint centers forced by disjoint exclusive mutual pairs."""

    if exclusive_pairs < 0:
        raise ValueError("the exclusive-pair count must be nonnegative")
    return 2 * exclusive_pairs


def direct_richer_matching_capacity(profile: str) -> int:
    """Enumerate the largest vertex-disjoint pair family for T5 or T44."""

    if profile == "T5":
        candidates = tuple(combinations(range(5), 2))
    elif profile == "T44":
        candidates = tuple((left, right) for left in range(4) for right in range(4, 8))
    else:
        raise ValueError("matching capacity is recorded only for T5 and T44")

    def search(index: int, used: frozenset[int]) -> int:
        if index == len(candidates):
            return 0
        best = search(index + 1, used)
        left, right = candidates[index]
        if left not in used and right not in used:
            best = max(
                best,
                1 + search(index + 1, used | {left, right}),
            )
        return best

    return search(0, frozenset())


def t4_covering_centers(
    vertex: int,
    t4_classes: Mapping[int, frozenset[int]],
) -> frozenset[int]:
    """Return Gamma(vertex) for a supplied abstract T4 family."""

    return frozenset(
        center for center, rich_class in t4_classes.items() if vertex in rich_class
    )


def t4_pair_certifiers(
    left: int,
    right: int,
    t4_classes: Mapping[int, frozenset[int]],
) -> frozenset[int]:
    """Return T4 centers outside the pair whose class meets the pair."""

    pair = {left, right}
    return frozenset(
        center
        for center, rich_class in t4_classes.items()
        if center not in pair and bool(pair & rich_class)
    )


def is_exclusive_mutual_pair(
    left: int,
    right: int,
    t4_classes: Mapping[int, frozenset[int]],
) -> bool:
    """Whether Gamma(left)={right} and Gamma(right)={left}."""

    return t4_covering_centers(left, t4_classes) == {right} and t4_covering_centers(
        right, t4_classes
    ) == {left}


def bound_row(n: int) -> dict[str, int | bool]:
    """Return one deterministic arithmetic row."""

    singleton_floor = singleton_t4_lower_bound(n)
    pair_floor = pair_average_t4_lower_bound(n)
    return {
        "n": n,
        "deletion_pairs": comb(n, 2),
        "T4_capacity": profile_capacity(n, "T4"),
        "T5_capacity": profile_capacity(n, "T5"),
        "T44_capacity": profile_capacity(n, "T44"),
        "singleton_T4_floor": singleton_floor,
        "pair_average_T4_floor": pair_floor,
        "pair_average_forces_richer_profile": pair_floor > singleton_floor,
    }


def build_summary() -> dict[str, object]:
    """Build the reviewer-facing exact summary."""

    fixture = {
        0: frozenset({1, 2, 3, 4}),
        1: frozenset({0, 2, 3, 5}),
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Exact finite-set and integer-arithmetic replay for the minimal "
            "two-deletion rich-profile lemma; not a minimality proof, not a "
            "Euclidean realization search, not a proof or counterexample for "
            "Erdos Problem #97."
        ),
        "profiles": {
            "T4": "one size-four rich class hit by at least one deletion seed",
            "T5": "one size-five rich class containing both deletion seeds",
            "T44": "two disjoint size-four rich classes hit one seed each",
        },
        "rows": [bound_row(n) for n in range(MIN_N, 65)],
        "exclusive_mutual_fixture": {
            "pair": [0, 1],
            "gamma_0": sorted(t4_covering_centers(0, fixture)),
            "gamma_1": sorted(t4_covering_centers(1, fixture)),
            "exclusive_mutual": is_exclusive_mutual_pair(0, 1, fixture),
            "T4_pair_certifiers": sorted(t4_pair_certifiers(0, 1, fixture)),
        },
        "exclusive_pair_capacity": "e <= 2*T5 + 4*T44",
        "exclusive_endpoint_center_floor": "T4 >= 2*e",
        "exclusive_total_center_capacity": "2*e + T5 + T44 <= n",
        "direct_richer_matching_capacities": {
            "T5": direct_richer_matching_capacity("T5"),
            "T44": direct_richer_matching_capacity("T44"),
        },
    }


def check_expected(summary: dict[str, object]) -> None:
    """Check formulae, direct enumeration, and the mutual-pair fixture."""

    for n in range(MIN_N, 65):
        for profile in ("T4", "T5", "T44"):
            formula = profile_capacity(n, profile)
            direct = direct_profile_capacity(n, profile)
            if formula != direct:
                raise AssertionError(
                    f"n={n}, profile={profile}: formula {formula} != direct {direct}"
                )
        if pair_average_t4_lower_bound(n) > singleton_t4_lower_bound(n):
            raise AssertionError(f"n={n}: pair averaging unexpectedly strengthens T4")
        if pair_coverage_rhs(n, singleton_t4_lower_bound(n), 0, 0) < comb(n, 2):
            raise AssertionError(f"n={n}: singleton T4 floor misses pair average")

    fixture = summary["exclusive_mutual_fixture"]
    if not isinstance(fixture, dict):
        raise AssertionError("missing exclusive-mutual fixture")
    if fixture != {
        "pair": [0, 1],
        "gamma_0": [1],
        "gamma_1": [0],
        "exclusive_mutual": True,
        "T4_pair_certifiers": [],
    }:
        raise AssertionError(f"unexpected exclusive-mutual fixture: {fixture}")
    if direct_richer_matching_capacity("T5") != 2:
        raise AssertionError("unexpected T5 matching capacity")
    if direct_richer_matching_capacity("T44") != 4:
        raise AssertionError("unexpected T44 matching capacity")
    for exclusive_pairs in range(33):
        if exclusive_pair_t4_center_floor(exclusive_pairs) != 2 * exclusive_pairs:
            raise AssertionError("unexpected exclusive-pair T4 endpoint floor")


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
        print(
            "minimal two-deletion profile ledger: "
            f"n={MIN_N}..64; capacities T4={profile_capacity(MIN_N, 'T4')}, "
            f"T5={profile_capacity(MIN_N, 'T5')}, "
            f"T44={profile_capacity(MIN_N, 'T44')}"
        )


if __name__ == "__main__":
    main()
