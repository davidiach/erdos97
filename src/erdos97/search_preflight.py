"""Exact necessary-condition preflight in the supplied boundary order.

Passing these inexpensive predicates is NOT a realization certificate. No
symmetry, reciprocal-witness, local-side-cap, or minimum-radius restriction is
imposed. Ordinary distances (not squared distances) index Kalmanson rows.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations
from math import gcd
from numbers import Integral
from typing import Sequence


def validate_rows(n: int, rows: Sequence[Sequence[int]]) -> None:
    """Validate structure separately from mathematical obstructions."""
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 5:
        raise ValueError("a k=4 pattern needs an integer n >= 5")
    if len(rows) != n:
        raise ValueError(f"expected {n} witness rows, got {len(rows)}")
    for i, row in enumerate(rows):
        if len(row) != 4 or any(
            isinstance(j, bool) or not isinstance(j, Integral) for j in row
        ):
            raise ValueError(f"row {i} must contain four integer labels")
        if len(set(row)) != 4 or i in row or any(j < 0 or j >= n for j in row):
            raise ValueError(f"row {i} must contain four distinct other labels in range")


def chords_cross(n: int, a: int, b: int, c: int, d: int) -> bool:
    if len({a, b, c, d}) != 4:
        return False
    return (0 < (c - a) % n < (b - a) % n) != (
        0 < (d - a) % n < (b - a) % n
    )


def preflight(n: int, rows: Sequence[Sequence[int]]) -> dict[str, object]:
    """Recompute obstructions; never infer them from a pattern name or status."""
    validate_rows(n, rows)
    rows = [set(map(int, row)) for row in rows]
    checked: list[str] = []

    def result(reason: str | None = None, **evidence: object) -> dict[str, object]:
        return {
            "status": "obstructed" if reason else "not_obstructed_by_preflight",
            "scope": "selected rows in supplied cyclic order only",
            "checks_run": checked.copy(),
            "reason": reason,
            "evidence": evidence,
            "realization_certified": False,
        }

    checked.append("two_circle_and_crossing_bisector")
    for a, b in combinations(range(n), 2):
        common = sorted(rows[a] & rows[b])
        if len(common) > 2:
            return result("two_circle_cap", centers=[a, b], witnesses=common)
        if len(common) == 2 and not chords_cross(n, a, b, *common):
            return result("crossing_bisector", centers=[a, b], witnesses=common)

    checked.append("base_pair_capacity")
    pair_users: dict[tuple[int, int], list[int]] = {}
    for i, row in enumerate(rows):
        for a, b in combinations(sorted(row), 2):
            users = pair_users.setdefault((a, b), [])
            users.append(i)
            # A boundary side has one possible apex; a diagonal has two.
            cap = 1 if (b - a) in (1, n - 1) else 2
            if len(users) > cap:
                return result("base_pair_capacity", pair=[a, b], centers=users, cap=cap)

    checked.append("strict_kalmanson_zero_and_inverse")
    pairs = list(combinations(range(n), 2))
    ids = {pair: index for index, pair in enumerate(pairs)}
    parent = list(range(len(pairs)))

    def root(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def edge(a: int, b: int) -> int:
        return ids[min(a, b), max(a, b)]

    for i, row in enumerate(rows):
        spokes = [edge(i, j) for j in sorted(row)]
        for spoke in spokes[1:]:
            a, b = root(spokes[0]), root(spoke)
            parent[max(a, b)] = min(a, b)
    classes = [root(i) for i in range(len(pairs))]
    seen: dict[tuple[tuple[int, int], ...], list[list[int]]] = {}
    for a, b, c, d in combinations(range(n), 4):
        for negatives in (((a, b), (c, d)), ((a, d), (b, c))):
            edges = ((a, c), (b, d), *negatives)
            coeffs: Counter[int] = Counter()
            for pair, sign in zip(edges, (1, 1, -1, -1)):
                coeffs[classes[edge(*pair)]] += sign
            terms = sorted((p, value) for p, value in coeffs.items() if value)
            encoded = [list(pair) for pair in edges]
            if not terms:
                return result("kalmanson_zero", positive_then_negative_edges=encoded)
            divisor = 0
            for _, value in terms:
                divisor = gcd(divisor, abs(value))
            key = tuple((p, value // divisor) for p, value in terms)
            inverse = tuple((p, -value) for p, value in key)
            if inverse in seen:
                return result(
                    "kalmanson_inverse",
                    positive_then_negative_edges=[seen[inverse], encoded],
                )
            seen[key] = encoded
    return result()
