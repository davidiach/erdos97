#!/usr/bin/env python3
"""Check the n=12 tight all-five-rich determinant obstruction.

This standalone checker verifies a small exact obstruction at the first
size-five equality wall of the edge-sensitive rich-support count. The current
support-saturation lemma already rules out this wall; this checker records an
independent determinant obstruction for the same n=12 all-five-rich subcase.

If a strict convex 12-gon had a same-radius support of size at least five at
every center, choose five witnesses at each center.  The existing pair-sharing
count is then tight:

    12 * binom(5, 2) = 12 * (12 - 2).

Tightness forces every hull-edge witness pair to occur in exactly one chosen
support and every non-edge witness pair to occur in exactly two chosen supports.
The 12 by 12 center/witness incidence matrix A would therefore satisfy
A^T A = G, where G has diagonal 5, adjacent off-diagonal entries 1, and all
other off-diagonal entries 2.  But det(G) = 2,592,000 = 720^2 * 5 is not a
square, contradicting det(A^T A) = det(A)^2 for an integer matrix A.
"""

from __future__ import annotations

import argparse
import json
from math import comb, isqrt
from typing import Any

SCHEMA = "erdos97.n12_rich_support_determinant.v1"
STATUS = "PROVED_N12_ALL_FIVE_RICH_DETERMINANT_OBSTRUCTION"
TRUST = "LEMMA"


def cycle_adjacent(a: int, b: int, n: int) -> bool:
    """Return whether vertices a and b are adjacent in cyclic order C_n."""

    if not 0 <= a < n or not 0 <= b < n:
        raise ValueError("vertices must lie in range(n)")
    return (a - b) % n in {1, n - 1}


def pair_capacity(a: int, b: int, n: int) -> int:
    """Capacity of a witness pair in the rich-support counting lemma."""

    if a == b:
        raise ValueError("pair endpoints must be distinct")
    return 1 if cycle_adjacent(a, b, n) else 2


def tight_size_five_gram(n: int = 12) -> list[list[int]]:
    """Return the forced column Gram matrix for the tight all-five n=12 case."""

    if n != 12:
        raise ValueError("this checker is intentionally scoped to n=12")
    gram = [[0 for _ in range(n)] for _ in range(n)]
    for a in range(n):
        for b in range(n):
            if a == b:
                gram[a][b] = 5
            else:
                gram[a][b] = pair_capacity(a, b, n)
    return gram


def bareiss_det(matrix: list[list[int]]) -> int:
    """Compute an exact integer determinant with the Bareiss algorithm."""

    n = len(matrix)
    if any(len(row) != n for row in matrix):
        raise ValueError("matrix must be square")
    a = [row[:] for row in matrix]
    sign = 1
    prev = 1
    for k in range(n - 1):
        pivot = a[k][k]
        if pivot == 0:
            swap = next((r for r in range(k + 1, n) if a[r][k] != 0), None)
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign *= -1
            pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * pivot - a[i][k] * a[k][j]) // prev
        prev = pivot
        for i in range(k + 1, n):
            a[i][k] = 0
        for j in range(k + 1, n):
            a[k][j] = 0
    return sign * a[n - 1][n - 1]


def factorint(value: int) -> dict[int, int]:
    """Return the prime factorization of a positive integer."""

    if value <= 0:
        raise ValueError("value must be positive")
    remaining = value
    factors: dict[int, int] = {}
    p = 2
    while p * p <= remaining:
        while remaining % p == 0:
            factors[p] = factors.get(p, 0) + 1
            remaining //= p
        p += 1 if p == 2 else 2
    if remaining > 1:
        factors[remaining] = factors.get(remaining, 0) + 1
    return factors


def is_square(value: int) -> bool:
    """Return whether value is a perfect square."""

    if value < 0:
        return False
    root = isqrt(value)
    return root * root == value


def column_sum_for_tight_all_five(column: int, n: int = 12) -> int:
    """Derive the forced column sum from saturated pair capacities."""

    incident_pair_capacity = sum(
        pair_capacity(column, other, n) for other in range(n) if other != column
    )
    support_size_minus_one = 4
    if incident_pair_capacity % support_size_minus_one != 0:
        raise AssertionError("unexpected nonintegral forced column sum")
    return incident_pair_capacity // support_size_minus_one


def build_summary() -> dict[str, Any]:
    """Build a stable machine-readable summary of the obstruction."""

    n = 12
    support_size = 5
    total_support_pair_count = n * comb(support_size, 2)
    pair_capacity_budget = n + 2 * (comb(n, 2) - n)
    gram = tight_size_five_gram(n)
    determinant = bareiss_det(gram)
    root = isqrt(determinant)
    factors = factorint(determinant)
    forced_column_sums = [column_sum_for_tight_all_five(column, n) for column in range(n)]
    first_row = gram[0]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Exact support-level obstruction for the n=12 all-centers-size-at-least-five "
            "rich-support subcase. This independently checks the same all-five-rich "
            "dodecagon equality wall closed by support saturation; it does not prove "
            "n=12, does not handle mixed exact-four/size-five catalogues, and does not "
            "prove Erdos Problem #97."
        ),
        "n": n,
        "support_size_chosen_at_each_center": support_size,
        "total_support_pair_count": total_support_pair_count,
        "edge_sensitive_pair_capacity_budget": pair_capacity_budget,
        "counting_bound_is_tight": total_support_pair_count == pair_capacity_budget,
        "forced_column_sums": forced_column_sums,
        "forced_column_gram_first_row": first_row,
        "forced_column_gram_description": {
            "diagonal": 5,
            "hull_edge_off_diagonal": 1,
            "nonedge_off_diagonal": 2,
        },
        "determinant": determinant,
        "determinant_factorization": {str(prime): exponent for prime, exponent in factors.items()},
        "floor_square_root": root,
        "is_square": is_square(determinant),
        "contradiction": not is_square(determinant),
        "consequence": (
            "A hypothetical 4-bad convex 12-gon cannot have E(v) >= 5 at every vertex; "
            "there must be at least one exact-four center. This consequence is redundant "
            "with the support-saturation obstruction but follows here by determinant "
            "parity alone."
        ),
    }


def check_expected(summary: dict[str, Any]) -> None:
    """Assert the exact arithmetic used by the proof note."""

    expected = {
        "schema": SCHEMA,
        "status": STATUS,
        "n": 12,
        "support_size_chosen_at_each_center": 5,
        "total_support_pair_count": 120,
        "edge_sensitive_pair_capacity_budget": 120,
        "counting_bound_is_tight": True,
        "forced_column_sums": [5] * 12,
        "forced_column_gram_first_row": [5, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
        "determinant": 2_592_000,
        "determinant_factorization": {"2": 8, "3": 4, "5": 3},
        "floor_square_root": 1609,
        "is_square": False,
        "contradiction": True,
    }
    for key, want in expected.items():
        got = summary[key]
        if got != want:
            raise AssertionError(f"{key}: got {got!r}, expected {want!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="assert expected exact arithmetic")
    parser.add_argument("--json", action="store_true", help="emit JSON summary")
    args = parser.parse_args()

    summary = build_summary()
    if args.check:
        check_expected(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"schema: {summary['schema']}")
        print(f"counting-bound equality: {summary['total_support_pair_count']} = {summary['edge_sensitive_pair_capacity_budget']}")
        print(f"determinant: {summary['determinant']}")
        print(f"factorization: {summary['determinant_factorization']}")
        print(f"perfect square: {summary['is_square']}")
        print(summary["consequence"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
