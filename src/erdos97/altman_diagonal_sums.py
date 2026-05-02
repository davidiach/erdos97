"""Natural-order Altman diagonal-sum obstruction.

This module is exact finite bookkeeping around cyclic offsets. It never uses
coordinates or floating point.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from erdos97.search import PatternInfo

Pair = tuple[int, int]


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


@dataclass(frozen=True)
class AltmanOrderResult:
    pattern: str
    n: int
    order: list[int]
    diagonal_orders: list[int]
    distance_class_count: int
    equal_diagonal_order_groups: list[list[int]]
    altman_contradiction: bool
    status: str


@dataclass(frozen=True)
class AltmanLPResult:
    pattern: str
    n: int
    order: list[int]
    trust_label: str
    status: str
    obstructed: bool | None
    distance_class_count: int
    inequality_count: int
    max_margin: float | None
    tolerance: float
    message: str


class UnionFind:
    """Small deterministic union-find over unordered vertex pairs."""

    def __init__(self, items: Sequence[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        if item not in self.parent:
            self.parent[item] = item
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, a: Pair, b: Pair) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


def chord_order(n: int, offset: int) -> int:
    """Return the cyclic chord order of an offset modulo n."""
    if n <= 0:
        raise ValueError(f"n must be positive, got {n}")
    t = offset % n
    return min(t, n - t)


def pair(u: int, v: int) -> Pair:
    """Return a normalized unordered pair. Reject loops."""

    if u == v:
        raise ValueError(f"loop pair is not allowed: ({u}, {v})")
    return (u, v) if u < v else (v, u)


def signed_offset(n: int, residue: int) -> int:
    """Return a canonical signed representative for a nonzero residue mod n.

    Callers pass target-center residues. A zero residue is rejected because it
    would select the center itself rather than a witness.
    """
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
        )

    chord_orders = [chord_order(pattern.n, offset) for offset in offsets]
    forced_equal_U = sorted(set(chord_orders))
    contradiction = len(forced_equal_U) >= 2
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
    )


def altman_order_obstruction(
    S: Sequence[Sequence[int]],
    order: Sequence[int] | None = None,
    pattern: str = "",
) -> AltmanOrderResult:
    """Check the Altman diagonal-sum signature obstruction for one order.

    Selected rows force equal distance classes. For a fixed cyclic order, each
    Altman diagonal sum ``U_k`` is then a formal sum of those classes. If two
    distinct ``U_k`` have the same formal signature, the selected equalities
    force them equal, contradicting Altman's strict chain.
    """

    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    _validate_order(order, n)

    uf = _distance_class_union_find(S)
    representatives = {uf.find(pair(u, v)) for u in range(n) for v in range(u + 1, n)}
    signatures = {
        diagonal_order: _diagonal_signature(uf, order, diagonal_order)
        for diagonal_order in range(1, n // 2 + 1)
    }
    grouped: dict[tuple[tuple[Pair, int], ...], list[int]] = {}
    for diagonal_order, signature in signatures.items():
        grouped.setdefault(signature, []).append(diagonal_order)
    equal_groups = sorted(
        sorted(group)
        for group in grouped.values()
        if len(group) >= 2
    )
    contradiction = bool(equal_groups)
    return AltmanOrderResult(
        pattern=pattern,
        n=n,
        order=order,
        diagonal_orders=list(range(1, n // 2 + 1)),
        distance_class_count=len(representatives),
        equal_diagonal_order_groups=equal_groups,
        altman_contradiction=contradiction,
        status=(
            "ORDER_EXACT_OBSTRUCTION"
            if contradiction
            else "NO_ORDER_ALTMAN_SIGNATURE_OBSTRUCTION"
        ),
    )


def altman_order_lp_diagnostic(
    S: Sequence[Sequence[int]],
    order: Sequence[int] | None = None,
    pattern: str = "",
    tolerance: float = 1e-9,
) -> AltmanLPResult:
    """Numerically test Altman's strict chain over distance classes.

    This maximizes ``gamma`` subject to ``sum(x)=1``, ``x >= 0``, and
    ``U_{k+1}(x)-U_k(x) >= gamma`` for every adjacent diagonal order.  A
    positive optimum means the selected-distance classes can pass this
    necessary Altman-chain relaxation.  A nonpositive optimum is a numerical
    obstruction for the supplied order.
    """

    if tolerance < 0:
        raise ValueError("tolerance must be nonnegative")
    np, linprog = _linear_programming()
    n = len(S)
    if order is None:
        order = list(range(n))
    order = list(order)
    _validate_order(order, n)
    class_reps, coefficient_rows = _diagonal_coefficient_rows(S, order)
    inequality_count = max(0, len(coefficient_rows) - 1)
    if inequality_count == 0:
        return AltmanLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_LINEAR_DIAGNOSTIC",
            status="NO_ALTMAN_INEQUALITIES",
            obstructed=False,
            distance_class_count=len(class_reps),
            inequality_count=0,
            max_margin=None,
            tolerance=float(tolerance),
            message="fewer than two diagonal orders",
        )

    class_count = len(class_reps)
    objective = np.zeros(class_count + 1)
    objective[-1] = -1.0
    constraints = []
    for left, right in zip(coefficient_rows, coefficient_rows[1:]):
        gap = right - left
        row = np.zeros(class_count + 1)
        row[:class_count] = -gap
        row[-1] = 1.0
        constraints.append(row)
    result = linprog(
        c=objective,
        A_ub=np.vstack(constraints),
        b_ub=np.zeros(inequality_count),
        A_eq=np.array([[*([1.0] * class_count), 0.0]]),
        b_eq=np.array([1.0]),
        bounds=[(0.0, None)] * class_count + [(None, None)],
        method="highs",
    )
    if not result.success:
        return AltmanLPResult(
            pattern=pattern,
            n=n,
            order=order,
            trust_label="NUMERICAL_LINEAR_DIAGNOSTIC",
            status="UNKNOWN_LP_FAILURE",
            obstructed=None,
            distance_class_count=class_count,
            inequality_count=inequality_count,
            max_margin=None,
            tolerance=float(tolerance),
            message=str(result.message),
        )

    max_margin = float(result.x[-1])
    obstructed = max_margin <= tolerance
    return AltmanLPResult(
        pattern=pattern,
        n=n,
        order=order,
        trust_label="NUMERICAL_LINEAR_DIAGNOSTIC",
        status=(
            "NUMERICAL_ALTMAN_LP_OBSTRUCTION"
            if obstructed
            else "PASS_ALTMAN_LP_RELAXATION"
        ),
        obstructed=obstructed,
        distance_class_count=class_count,
        inequality_count=inequality_count,
        max_margin=max_margin,
        tolerance=float(tolerance),
        message=str(result.message),
    )
def _validate_order(order: Sequence[int], n: int) -> None:
    seen = set(order)
    if len(order) != n or seen != set(range(n)):
        missing = sorted(set(range(n)) - seen)
        extra = sorted(seen - set(range(n)))
        raise ValueError(
            f"cyclic order is not a permutation; missing={missing}, extra={extra}"
        )


def _all_pairs(n: int) -> list[Pair]:
    return [(u, v) for u in range(n) for v in range(u + 1, n)]


def _distance_class_union_find(S: Sequence[Sequence[int]]) -> UnionFind:
    n = len(S)
    uf = UnionFind(_all_pairs(n))
    for center, row in enumerate(S):
        if len(row) != 4:
            raise ValueError(f"row {center} has length {len(row)}, expected 4")
        if len(set(row)) != 4:
            raise ValueError(f"row {center} has repeated witnesses: {list(row)}")
        if center in row:
            raise ValueError(f"row {center} contains its own center")
        for witness in row:
            if witness < 0 or witness >= n:
                raise ValueError(
                    f"row {center} contains out-of-range label {witness}"
                )
        base = pair(center, int(row[0]))
        for witness in row[1:]:
            uf.union(base, pair(center, int(witness)))
    return uf


def _diagonal_signature(
    uf: UnionFind,
    order: Sequence[int],
    diagonal_order: int,
) -> tuple[tuple[Pair, int], ...]:
    counts: dict[Pair, int] = {}
    n = len(order)
    for idx, source in enumerate(order):
        target = order[(idx + diagonal_order) % n]
        distance_class = uf.find(pair(source, target))
        counts[distance_class] = counts.get(distance_class, 0) + 1
    return tuple(sorted(counts.items()))


def _diagonal_coefficient_rows(
    S: Sequence[Sequence[int]],
    order: Sequence[int],
):
    np, _ = _linear_programming()
    uf = _distance_class_union_find(S)
    class_reps = sorted(
        {uf.find(pair(u, v)) for u in range(len(S)) for v in range(u + 1, len(S))}
    )
    class_index = {distance_class: idx for idx, distance_class in enumerate(class_reps)}
    rows = []
    for diagonal_order in range(1, len(S) // 2 + 1):
        row = np.zeros(len(class_reps))
        for idx, source in enumerate(order):
            target = order[(idx + diagonal_order) % len(order)]
            distance_class = uf.find(pair(source, target))
            row[class_index[distance_class]] += 1.0
        rows.append(row)
    return class_reps, rows


def _linear_programming():
    try:
        import numpy as np  # type: ignore
        from scipy.optimize import linprog  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on dev deps
        raise RuntimeError(
            "NumPy and SciPy are required for Altman LP diagnostics"
        ) from exc
    return np, linprog
