"""Natural-order Altman diagonal-sum obstruction.

This module is exact finite bookkeeping around cyclic offsets. It never uses
coordinates or floating point.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from erdos97.search import PatternInfo


@dataclass(frozen=True)
class AltmanDiagonalSumResult:
    pattern: str
    n: int
    natural_order_only: bool
    offsets: list[int]
    chord_orders: list[int]
    forced_equal_U: list[int]
    altman_contradiction: bool
    status: str
    abstract_incidence_status: str


def chord_order(n: int, offset: int) -> int:
    """Return the cyclic chord order of an offset modulo n."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    t = offset % n
    return min(t, n - t)


def signed_offset(n: int, residue: int) -> int:
    """Return a canonical signed representative for a nonzero residue mod n."""
    residue %= n
    if residue == 0:
        raise ValueError("zero offset would select the center")
    if residue > n // 2:
        return residue - n
    return residue


def constant_cyclic_offsets(S: Sequence[Sequence[int]]) -> list[int] | None:
    """
    Return offsets if S_i is one constant cyclic-offset pattern, else None.

    The offsets are canonical signed representatives sorted increasingly. This
    deliberately declines period-2 and other nonconstant patterns.
    """
    n = len(S)
    if n == 0:
        return []
    offsets = sorted(signed_offset(n, target) for target in S[0])
    residues = {offset % n for offset in offsets}
    for i, row in enumerate(S):
        if set(row) != {(i + offset) % n for offset in residues}:
            return None
    return offsets


def check_altman(pattern: PatternInfo) -> AltmanDiagonalSumResult:
    """Check the natural-order diagonal-sum obstruction for one pattern."""
    offsets = constant_cyclic_offsets(pattern.S)
    if offsets is None:
        return AltmanDiagonalSumResult(
            pattern=pattern.name,
            n=pattern.n,
            natural_order_only=True,
            offsets=[],
            chord_orders=[],
            forced_equal_U=[],
            altman_contradiction=False,
            status="NOT_APPLIED_NONCONSTANT_OFFSETS",
            abstract_incidence_status="UNTOUCHED",
        )

    chord_orders = [chord_order(pattern.n, offset) for offset in offsets]
    forced_equal_U = sorted(set(chord_orders))
    contradiction = len(forced_equal_U) >= 2
    abstract_status = "LIVE" if pattern.name == "C19_skew" else "UNTOUCHED"
    return AltmanDiagonalSumResult(
        pattern=pattern.name,
        n=pattern.n,
        natural_order_only=True,
        offsets=offsets,
        chord_orders=chord_orders,
        forced_equal_U=forced_equal_U,
        altman_contradiction=contradiction,
        status=(
            "NATURAL_ORDER_EXACT_OBSTRUCTION"
            if contradiction
            else "NO_NATURAL_ORDER_ALTMAN_OBSTRUCTION"
        ),
        abstract_incidence_status=abstract_status,
    )
