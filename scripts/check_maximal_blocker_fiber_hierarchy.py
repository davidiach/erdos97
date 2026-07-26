#!/usr/bin/env python3
"""Replay the maximal blocker-fiber hierarchy arithmetic.

The proof-facing statement is ``docs/maximal-blocker-fiber-hierarchy.md``.
This script checks the finite fiber-profile optimization and pair-capacity
arithmetic only.  It does not construct blocker assignments, certify Euclidean
realizability, or prove Erdős Problem #97.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json


SCHEMA = "erdos97.maximal_blocker_fiber_hierarchy.v1"
STATUS = "LEMMA_PROFILE_REPLAY"
TRUST = "EXACT_COMBINATORIAL_REPLAY"


@dataclass(frozen=True)
class HighFiberProfile:
    zero_fibers: int
    two_fibers: int
    three_fibers: int
    four_fibers: int
    high_centers: int
    high_sources: int
    maximum_singleton_fibers: int
    cardinality_upper_bound: int


def admissible_high_profiles(zero_fibers: int) -> list[tuple[int, int, int]]:
    """Enumerate ``(n2,n3,n4)`` with excess ``z`` and a saturated 4-fiber."""

    if zero_fibers < 3:
        return []
    profiles: list[tuple[int, int, int]] = []
    for n4 in range(1, zero_fibers // 3 + 1):
        remaining_after_four = zero_fibers - 3 * n4
        for n3 in range(remaining_after_four // 2 + 1):
            n2 = remaining_after_four - 2 * n3
            profiles.append((n2, n3, n4))
    return profiles


def profile_data(zero_fibers: int, profile: tuple[int, int, int]) -> HighFiberProfile:
    """Return the singleton/cardinality upper bounds from H-pair capacity."""

    n2, n3, n4 = profile
    if min(n2, n3, n4) < 0:
        raise ValueError("fiber counts must be nonnegative")
    if n4 < 1 or n2 + 2 * n3 + 3 * n4 != zero_fibers:
        raise ValueError("profile does not have the requested fiber excess")
    high_centers = n2 + n3 + n4
    high_sources = 2 * n2 + 3 * n3 + 4 * n4
    remaining_pair_capacity = high_sources * (high_sources - 1) - 6 * high_centers
    if remaining_pair_capacity < 0:
        raise ValueError("profile already exceeds H-pair capacity")
    maximum_singletons = remaining_pair_capacity // 3
    return HighFiberProfile(
        zero_fibers=zero_fibers,
        two_fibers=n2,
        three_fibers=n3,
        four_fibers=n4,
        high_centers=high_centers,
        high_sources=high_sources,
        maximum_singleton_fibers=maximum_singletons,
        cardinality_upper_bound=high_sources + maximum_singletons,
    )


def maximizing_profile(zero_fibers: int) -> HighFiberProfile:
    """Profile with the largest cardinality upper bound from pair capacity."""

    profiles = admissible_high_profiles(zero_fibers)
    if not profiles:
        raise ValueError("a saturated four-fiber requires at least three omissions")
    return max(
        (profile_data(zero_fibers, profile) for profile in profiles),
        key=lambda item: (
            item.cardinality_upper_bound,
            item.high_sources,
            item.two_fibers,
        ),
    )


def closed_form_cardinality_upper_bound(zero_fibers: int) -> int:
    """The floor of ``(4z^2-10z+12)/3`` from the proof note."""

    if zero_fibers < 3:
        raise ValueError("zero_fibers must be at least three")
    return (4 * zero_fibers * zero_fibers - 10 * zero_fibers + 12) // 3


def minimum_zero_fibers(cardinality: int) -> int:
    """Smallest ``z`` not ruled out by the exact profile/pair ledger."""

    if cardinality < 1:
        raise ValueError("cardinality must be positive")
    z = 3
    while closed_form_cardinality_upper_bound(z) < cardinality:
        z += 1
    return z


def build_summary() -> dict[str, object]:
    """Build a deterministic reviewer-facing summary."""

    rows = []
    for z in range(3, 17):
        best = maximizing_profile(z)
        rows.append(
            {
                **asdict(best),
                "closed_form_cardinality_upper_bound": (
                    closed_form_cardinality_upper_bound(z)
                ),
                "all_high_profiles": [
                    asdict(profile_data(z, profile))
                    for profile in admissible_high_profiles(z)
                ],
            }
        )
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Exact arithmetic replay of the maximizing blocker-fiber profile and "
            "H-pair capacity; not an assignment existence proof, Euclidean "
            "realizability checker, proof, or counterexample for Erdős Problem #97."
        ),
        "rows": rows,
        "cardinality_thresholds": {
            str(n): minimum_zero_fibers(n) for n in (6, 7, 9, 12, 13, 15, 21, 33)
        },
    }


def check_expected(summary: dict[str, object]) -> None:
    """Check the algebra and the first exact profile thresholds."""

    rows = summary.get("rows")
    if not isinstance(rows, list):
        raise AssertionError("missing profile rows")
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("malformed profile row")
        z = int(row["zero_fibers"])
        if int(row["cardinality_upper_bound"]) != (
            closed_form_cardinality_upper_bound(z)
        ):
            raise AssertionError(f"z={z}: closed form does not match enumeration")
        n2 = int(row["two_fibers"])
        n3 = int(row["three_fibers"])
        n4 = int(row["four_fibers"])
        if n2 + 2 * n3 + 3 * n4 != z or n4 < 1:
            raise AssertionError(f"z={z}: invalid maximizing profile")
        h = int(row["high_sources"])
        m = int(row["high_centers"])
        ell = int(row["maximum_singleton_fibers"])
        if 6 * m + 3 * ell > h * (h - 1):
            raise AssertionError(f"z={z}: pair capacity exceeded")
        all_profiles = row.get("all_high_profiles")
        if not isinstance(all_profiles, list) or not all_profiles:
            raise AssertionError(f"z={z}: missing high-fiber profiles")
        if any(
            int(candidate["cardinality_upper_bound"])
            > int(row["cardinality_upper_bound"])
            for candidate in all_profiles
        ):
            raise AssertionError(f"z={z}: selected profile is not maximizing")

    expected_first = {
        3: (0, 0, 1, 4, 6),
        4: (1, 0, 1, 6, 12),
        5: (2, 0, 1, 8, 20),
        6: (3, 0, 1, 10, 32),
    }
    by_z = {int(row["zero_fibers"]): row for row in rows}
    for z, (n2, n3, n4, h, nmax) in expected_first.items():
        row = by_z[z]
        actual = (
            int(row["two_fibers"]),
            int(row["three_fibers"]),
            int(row["four_fibers"]),
            int(row["high_sources"]),
            int(row["cardinality_upper_bound"]),
        )
        if actual != (n2, n3, n4, h, nmax):
            raise AssertionError(f"z={z}: unexpected maximizing profile {actual}")

    expected_thresholds = {
        "6": 3,
        "7": 4,
        "9": 4,
        "12": 4,
        "13": 5,
        "15": 5,
        "21": 6,
        "33": 7,
    }
    if summary.get("cardinality_thresholds") != expected_thresholds:
        raise AssertionError("unexpected zero-fiber thresholds")


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
        row = maximizing_profile(5)
        print(
            "maximal blocker-fiber ledger: "
            f"z=5 profile=(n2={row.two_fibers}, n3={row.three_fibers}, "
            f"n4={row.four_fibers}), n upper bound={row.cardinality_upper_bound}"
        )


if __name__ == "__main__":
    main()
