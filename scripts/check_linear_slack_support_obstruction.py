#!/usr/bin/env python3
"""Check the linear rich-support slack obstruction bookkeeping.

The review-pending proof note ``docs/linear-slack-support-obstruction.md``
claims that, for same-radius supports on a strictly convex n-gon with n >= 8,
the unused edge-sensitive pair capacity ``d`` satisfies

    d >= ceil((n - 4) / 2) = floor((n - 3) / 2).

This checker verifies the discrete cyclic bookkeeping and independently
enumerates the minimum gap-2/gap-3 deficit needed to escape the resulting turn
clauses for n = 8,...,12. It does not verify the Euclidean lemmas used by the
proof note and is not a realization search or a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from itertools import combinations
import json


SCHEMA = "erdos97.linear_slack_support_obstruction.v1"
STATUS = "REVIEW_PENDING_LINEAR_SLACK_OBSTRUCTION"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
MIN_N = 8
FINITE_CROSSCHECK_MAX_N = 12


def raw_pair_budget(n: int) -> int:
    """Return the edge-sensitive witness-pair capacity n(n-2)."""

    if n < 0:
        raise ValueError("n must be nonnegative")
    return n * (n - 2)


def linear_slack_lower_bound(n: int) -> int:
    """Return ceil((n-4)/2), claimed for n >= 8."""

    if n < MIN_N:
        raise ValueError("the linear slack bound is claimed only for n >= 8")
    return (n - 3) // 2


def linear_pair_budget(n: int) -> int:
    """Return n(n-2) minus the claimed linear slack lower bound."""

    return raw_pair_budget(n) - linear_slack_lower_bound(n)


def clean_gap3_indices(
    n: int,
    unsaturated_gap2: frozenset[int],
    unsaturated_gap3: frozenset[int],
) -> tuple[int, ...]:
    """Indices whose local gap-2/gap-3 data force a two-turn clause.

    Gap-3 index i is clean precisely when its own diagonal is saturated and
    the gap-2 diagonals indexed i and i+1 are both saturated. Those two
    gap-2 equalities make side lengths s_i, s_(i+1), s_(i+2) equal locally;
    no global equilateral side chain is assumed.
    """

    if n < MIN_N:
        raise ValueError("short-diagonal bookkeeping requires n >= 8")
    bad2 = {index % n for index in unsaturated_gap2}
    bad3 = {index % n for index in unsaturated_gap3}
    return tuple(
        index
        for index in range(n)
        if index not in bad3
        and index not in bad2
        and (index + 1) % n not in bad2
    )


def forced_turn_edges(
    n: int,
    unsaturated_gap2: frozenset[int],
    unsaturated_gap3: frozenset[int],
) -> tuple[tuple[int, int], ...]:
    """Return the turn-cycle edges hit by a forced 2*pi/3 turn."""

    return tuple(
        ((index + 1) % n, (index + 2) % n)
        for index in clean_gap3_indices(n, unsaturated_gap2, unsaturated_gap3)
    )


def minimum_turn_cover_size(n: int, edges: tuple[tuple[int, int], ...]) -> int:
    """Return the exact minimum vertex cover for a small turn-edge set."""

    for size in range(n + 1):
        for chosen_tuple in combinations(range(n), size):
            chosen = set(chosen_tuple)
            if all(left in chosen or right in chosen for left, right in edges):
                return size
    raise AssertionError("the full turn set must cover every edge")


def forces_turn_contradiction(
    n: int,
    unsaturated_gap2: frozenset[int],
    unsaturated_gap3: frozenset[int],
) -> bool:
    """Whether the clauses force at least three 2*pi/3 exterior turns."""

    edges = forced_turn_edges(n, unsaturated_gap2, unsaturated_gap3)
    return minimum_turn_cover_size(n, edges) >= 3


@dataclass(frozen=True)
class EscapeRecord:
    n: int
    minimum_unit_deficit: int
    unsaturated_gap2: tuple[int, ...]
    unsaturated_gap3: tuple[int, ...]
    clean_clause_count: int
    minimum_forced_turns: int


def minimum_unit_deficit_to_escape(n: int) -> EscapeRecord:
    """Enumerate the first gap-2/gap-3 unit-deficit placement that escapes.

    A short diagonal with a larger shortfall consumes more total slack without
    removing any additional clause, so unit deficits are the extremal case for
    finding the minimum total slack.
    """

    if not MIN_N <= n <= FINITE_CROSSCHECK_MAX_N:
        raise ValueError("the exhaustive cross-check is limited to 8 <= n <= 12")
    tagged = tuple((gap, index) for gap in (2, 3) for index in range(n))
    for deficit in range(2 * n + 1):
        for removed in combinations(tagged, deficit):
            bad2 = frozenset(index for gap, index in removed if gap == 2)
            bad3 = frozenset(index for gap, index in removed if gap == 3)
            edges = forced_turn_edges(n, bad2, bad3)
            cover = minimum_turn_cover_size(n, edges)
            if cover < 3:
                return EscapeRecord(
                    n=n,
                    minimum_unit_deficit=deficit,
                    unsaturated_gap2=tuple(sorted(bad2)),
                    unsaturated_gap3=tuple(sorted(bad3)),
                    clean_clause_count=len(edges),
                    minimum_forced_turns=cover,
                )
    raise AssertionError("removing every short diagonal must escape the clauses")


def bound_row(n: int) -> dict[str, int]:
    """Return one exact arithmetic row for the claimed bound."""

    slack = linear_slack_lower_bound(n)
    return {
        "n": n,
        "raw_pair_budget": raw_pair_budget(n),
        "linear_slack_lower_bound": slack,
        "linear_pair_budget": linear_pair_budget(n),
        "twice_slack": 2 * slack,
        "n_minus_4": n - 4,
    }


def build_summary() -> dict[str, object]:
    """Build the deterministic reviewer-facing JSON summary."""

    escape_records = [
        asdict(minimum_unit_deficit_to_escape(n))
        for n in range(MIN_N, FINITE_CROSSCHECK_MAX_N + 1)
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Review-pending general-n strengthening of the edge-sensitive "
            "rich-support pair budget: pair-capacity slack d is at least "
            "ceil((n-4)/2) for n >= 8. Discrete bookkeeping checks only; "
            "not a realization search, not a finite-case proof beyond the "
            "stated counting lemma, not a proof of Erdos Problem #97, and "
            "not a counterexample."
        ),
        "lemma_draft": (
            "For same-radius supports R_i in a strictly convex n-gon with "
            "n >= 8, sum_i binom(|R_i|,2) <= "
            "n(n-2)-ceil((n-4)/2)."
        ),
        "proof_accounting": {
            "B": "indices of unsaturated gap-2 diagonals",
            "G": "indices of unsaturated gap-3 diagonals",
            "clean_clause_lower_bound": "h >= n - (2|B| + |G|)",
            "turn_budget": (
                "at most two exterior turns can equal 2*pi/3, so they hit "
                "at most four distinct turn-cycle edges"
            ),
            "slack_chain": (
                "n-4 <= 2|B|+|G| <= 2(|B|+|G|) <= 2d"
            ),
        },
        "bound_rows": [bound_row(n) for n in range(8, 33)],
        "finite_escape_crosscheck": escape_records,
    }


def check_expected(summary: dict[str, object]) -> None:
    """Assert the formula and independent finite escape cross-check."""

    rows = summary["bound_rows"]
    assert isinstance(rows, list)
    for row in rows:
        assert isinstance(row, dict)
        n = int(row["n"])
        slack = int(row["linear_slack_lower_bound"])
        if 2 * slack < n - 4:
            raise AssertionError(f"n={n}: lower bound misses n-4")
        if slack > 0 and 2 * (slack - 1) >= n - 4:
            raise AssertionError(f"n={n}: lower bound is not the ceiling")
        if int(row["linear_pair_budget"]) != raw_pair_budget(n) - slack:
            raise AssertionError(f"n={n}: pair-budget arithmetic mismatch")

    records = summary["finite_escape_crosscheck"]
    assert isinstance(records, list)
    expected = {8: 2, 9: 3, 10: 3, 11: 4, 12: 4}
    got = {
        int(record["n"]): int(record["minimum_unit_deficit"])
        for record in records
        if isinstance(record, dict)
    }
    if got != expected:
        raise AssertionError(f"finite escape minima {got} != {expected}")
    for n, deficit in got.items():
        if deficit != linear_slack_lower_bound(n):
            raise AssertionError(f"n={n}: finite minimum disagrees with formula")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="assert expected rows")
    parser.add_argument("--json", action="store_true", help="emit full JSON")
    args = parser.parse_args()

    summary = build_summary()
    if args.check:
        check_expected(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"schema: {SCHEMA}")
        print(f"trust: {TRUST}")
        print("linear slack bound: ceil((n-4)/2) for n >= 8")
        print(
            "finite escape minima: "
            + ", ".join(
                f"n={row['n']} -> {row['minimum_unit_deficit']}"
                for row in summary["finite_escape_crosscheck"]
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
