"""Exact checks for the half-step two-orbit radius-propagation ansatz.

This module verifies a narrow obstruction, not the general Erdos #97 problem.
The ansatz has two concentric regular ``m``-gons with half-step offset:

``A_j = R exp(2ijh)``, ``B_j = S exp((2j+1)ih)``, with ``m=4t`` and
``h=pi/m``.

The selected four-neighbor pattern matches same-orbit quarter-turn chords to
cross-orbit chords one half-step away. The distance equations force
``S/R = sqrt(1+sin(h)^2) - sin(h)``, while convexity of the alternating
polygon would require ``S/R > cos(h)``. The forced ratio is strictly smaller
than ``cos(h)``, so this symmetric ansatz is exactly concave.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Sequence

from erdos97.incidence_filters import chords_cross_in_order, normalize_chord


def _sympy():
    try:
        import sympy as sp  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dev dependency
        raise RuntimeError("SymPy is required for two-orbit exact checks") from exc
    return sp


@dataclass(frozen=True)
class TwoOrbitSummary:
    """Formula summary for one half-step two-orbit ansatz."""

    t: int
    m: int
    n: int
    h: object
    ratio: object
    distance_equation: object
    a_distance_gap: object
    b_distance_gap: object
    turn_at_b: object
    turn_at_a: object
    cos_minus_ratio: object
    sec_minus_ratio: object
    lower_convexity_certificate: object
    forced_concave: bool


@dataclass(frozen=True)
class TwoOrbitLinearizedEscapeSummary:
    """Numerical first-order deformation diagnostic for the two-orbit ansatz."""

    t: int
    m: int
    n: int
    status: str
    trust_label: str
    equality_equation_count: int
    equality_rank: int
    kernel_dimension: int
    concave_turn_count: int
    derivative_floor: float
    min_concave_turn_derivative: float | None
    max_abs_equality_jacobian_residual: float | None
    l1_norm: float | None
    direction: list[list[float]] | None


@dataclass(frozen=True)
class AlternatingTwoRadiusGapCertificate:
    """One adjacent paired-distance gap certificate for the alternating family."""

    k: int
    parity: str
    endpoint: str
    gap_at_endpoint: object
    positive: bool


@dataclass(frozen=True)
class AlternatingTwoRadiusFamilySummary:
    """Exact monotonicity summary for the alternating two-radius regular family."""

    m: int
    n: int
    h: object
    convexity_lower: object
    convexity_upper: object
    gap_certificates: list[AlternatingTwoRadiusGapCertificate]
    all_gap_certificates_positive: bool
    status: str


@dataclass(frozen=True)
class CyclicCrossingSearchSummary:
    """Finite cyclic-order crossing search summary for one fixed pattern."""

    pattern: str
    n: int
    constraint_count: int
    normalized_order_count: int
    survivor: tuple[int, ...] | None
    status: str


def _check_t(t: int) -> None:
    if not isinstance(t, int) or t < 1:
        raise ValueError("t must be a positive integer")


def _check_m(m: int) -> None:
    if not isinstance(m, int) or m < 4:
        raise ValueError("m must be an integer >= 4")


def forced_ratio(t: int):
    """Return the forced ratio ``S/R`` for ``m=4t``."""
    _check_t(t)
    sp = _sympy()
    h = sp.pi / (4 * t)
    s = sp.sin(h)
    return sp.simplify(sp.sqrt(1 + s * s) - s)


def two_orbit_summary(t: int) -> TwoOrbitSummary:
    """Return exact symbolic identities and turn signs for one ``t``."""
    _check_t(t)
    sp = _sympy()
    m = 4 * t
    n = 2 * m
    h = sp.pi / m
    s = sp.sin(h)
    c = sp.cos(h)
    ratio = forced_ratio(t)

    distance_equation = sp.simplify(ratio * ratio + 2 * ratio * s - 1)
    a_distance_gap = sp.simplify(1 + ratio * ratio + 2 * ratio * s - 2)
    b_distance_gap = sp.simplify(1 + ratio * ratio - 2 * ratio * s - 2 * ratio * ratio)

    turn_at_b = sp.factor(2 * s * (ratio - c))
    turn_at_a = sp.factor(2 * ratio * s * (1 - ratio * c))

    cos_minus_ratio = sp.simplify(c - ratio)
    sec_minus_ratio = sp.simplify(1 / c - ratio)
    lower_convexity_certificate = sp.simplify((s + c) ** 2 - (1 + s * s))

    return TwoOrbitSummary(
        t=t,
        m=m,
        n=n,
        h=h,
        ratio=ratio,
        distance_equation=distance_equation,
        a_distance_gap=a_distance_gap,
        b_distance_gap=b_distance_gap,
        turn_at_b=turn_at_b,
        turn_at_a=turn_at_a,
        cos_minus_ratio=cos_minus_ratio,
        sec_minus_ratio=sec_minus_ratio,
        lower_convexity_certificate=lower_convexity_certificate,
        forced_concave=_is_positive(cos_minus_ratio) and _is_positive(-turn_at_b),
    )


def two_orbit_points(t: int):
    """Return exact alternating points ``A_0,B_0,A_1,B_1,...`` with ``R=1``."""
    _check_t(t)
    sp = _sympy()
    m = 4 * t
    h = sp.pi / m
    ratio = forced_ratio(t)
    points = []
    for j in range(m):
        a_theta = 2 * j * h
        b_theta = (2 * j + 1) * h
        points.append((sp.cos(a_theta), sp.sin(a_theta)))
        points.append((sp.simplify(ratio * sp.cos(b_theta)), sp.simplify(ratio * sp.sin(b_theta))))
    return points


def two_orbit_cohorts(t: int) -> list[list[int]]:
    """Return selected cohorts for the two-orbit pattern.

    Labels are the alternating point labels returned by ``two_orbit_points``:
    ``2*j`` is ``A_j`` and ``2*j+1`` is ``B_j``.
    """
    _check_t(t)
    m = 4 * t
    cohorts: list[list[int]] = [[] for _ in range(2 * m)]
    for j in range(m):
        cohorts[2 * j] = [
            2 * ((j + t) % m),
            2 * ((j - t) % m),
            2 * ((j + t) % m) + 1,
            2 * ((j - t - 1) % m) + 1,
        ]
        cohorts[2 * j + 1] = [
            2 * ((j + t) % m) + 1,
            2 * ((j - t) % m) + 1,
            2 * ((j + t) % m),
            2 * ((j - t + 1) % m),
        ]
    return cohorts


def selected_distance_residuals(t: int) -> list[list[object]]:
    """Return exact selected squared-distance residuals for all rows.

    Each row contains the differences between every selected squared distance
    and the first selected squared distance in that row.
    """
    sp = _sympy()
    points = two_orbit_points(t)
    cohorts = two_orbit_cohorts(t)
    residuals = []
    for center, row in enumerate(cohorts):
        values = [_squared_distance(points[center], points[target]) for target in row]
        residuals.append([sp.simplify(value - values[0]) for value in values[1:]])
    return residuals


def alternating_turns(t: int) -> list[object]:
    """Return exact signed consecutive turns in alternating cyclic order."""
    sp = _sympy()
    points = two_orbit_points(t)
    turns = []
    n = len(points)
    for idx in range(n):
        p = points[idx]
        q = points[(idx + 1) % n]
        r = points[(idx + 2) % n]
        turns.append(sp.factor(_det(_sub(q, p), _sub(r, q))))
    return turns


def linearized_escape_summary(
    t: int,
    derivative_floor: float = 1.0,
    include_direction: bool = False,
) -> TwoOrbitLinearizedEscapeSummary:
    """Search for a first-order escape from the concave two-orbit ansatz.

    The linearized system keeps the selected squared-distance equalities fixed
    to first order and asks for every currently concave alternating turn to
    increase at rate at least ``derivative_floor``. This is a numerical LP
    diagnostic around the exact ansatz, not an exact proof certificate.
    """

    _check_t(t)
    if derivative_floor <= 0:
        raise ValueError("derivative_floor must be positive")

    np, linprog = _numeric_lp()
    points = _numeric_points(t)
    cohorts = two_orbit_cohorts(t)
    n = len(points)
    equality_jacobian = _selected_equality_jacobian(points, cohorts)
    turn_jacobian, base_turns = _turn_jacobian(points)
    concave_rows = [
        idx
        for idx, value in enumerate(base_turns)
        if float(value) < -1e-12
    ]
    concave_jacobian = turn_jacobian[concave_rows, :]

    equality_rank = int(np.linalg.matrix_rank(equality_jacobian, tol=1e-9))
    kernel_dimension = int(2 * n - equality_rank)
    if not concave_rows:
        return TwoOrbitLinearizedEscapeSummary(
            t=t,
            m=4 * t,
            n=n,
            status="NO_CONCAVE_TURNS",
            trust_label="NUMERICAL_LINEARIZED_DIAGNOSTIC",
            equality_equation_count=int(equality_jacobian.shape[0]),
            equality_rank=equality_rank,
            kernel_dimension=kernel_dimension,
            concave_turn_count=0,
            derivative_floor=float(derivative_floor),
            min_concave_turn_derivative=None,
            max_abs_equality_jacobian_residual=None,
            l1_norm=None,
            direction=None,
        )

    dim = 2 * n
    # Minimize ||v||_1 subject to Jv=0 and every concave turn derivative >= floor.
    c = np.concatenate([np.zeros(dim), np.ones(dim)])
    inequalities = []
    rhs = []

    inequalities.append(np.hstack([-concave_jacobian, np.zeros((len(concave_rows), dim))]))
    rhs.extend([-float(derivative_floor)] * len(concave_rows))

    identity = np.eye(dim)
    inequalities.append(np.hstack([identity, -identity]))
    rhs.extend([0.0] * dim)
    inequalities.append(np.hstack([-identity, -identity]))
    rhs.extend([0.0] * dim)

    bounds = [(None, None)] * dim + [(0.0, None)] * dim
    result = linprog(
        c=c,
        A_ub=np.vstack(inequalities),
        b_ub=np.array(rhs, dtype=float),
        A_eq=np.hstack([equality_jacobian, np.zeros((equality_jacobian.shape[0], dim))]),
        b_eq=np.zeros(equality_jacobian.shape[0]),
        bounds=bounds,
        method="highs",
    )
    if not result.success:
        return TwoOrbitLinearizedEscapeSummary(
            t=t,
            m=4 * t,
            n=n,
            status="NO_LINEARIZED_ESCAPE_FOUND",
            trust_label="NUMERICAL_LINEARIZED_DIAGNOSTIC",
            equality_equation_count=int(equality_jacobian.shape[0]),
            equality_rank=equality_rank,
            kernel_dimension=kernel_dimension,
            concave_turn_count=len(concave_rows),
            derivative_floor=float(derivative_floor),
            min_concave_turn_derivative=None,
            max_abs_equality_jacobian_residual=None,
            l1_norm=None,
            direction=None,
        )

    direction_vector = result.x[:dim]
    equality_residual = equality_jacobian @ direction_vector
    turn_derivatives = concave_jacobian @ direction_vector
    direction = direction_vector.reshape((n, 2))
    return TwoOrbitLinearizedEscapeSummary(
        t=t,
        m=4 * t,
        n=n,
        status="LINEARIZED_ESCAPE_FOUND",
        trust_label="NUMERICAL_LINEARIZED_DIAGNOSTIC",
        equality_equation_count=int(equality_jacobian.shape[0]),
        equality_rank=equality_rank,
        kernel_dimension=kernel_dimension,
        concave_turn_count=len(concave_rows),
        derivative_floor=float(derivative_floor),
        min_concave_turn_derivative=float(np.min(turn_derivatives)),
        max_abs_equality_jacobian_residual=float(np.max(np.abs(equality_residual))),
        l1_norm=float(np.sum(np.abs(direction_vector))),
        direction=(
            [[float(x), float(y)] for x, y in direction]
            if include_direction
            else None
        ),
    )


def alternating_two_radius_family_summary(
    m: int,
) -> AlternatingTwoRadiusFamilySummary:
    """Return exact endpoint certificates for the alternating two-radius family.

    The family has vertices on equally spaced rays with radii alternating
    between ``1`` and ``b``. In the strict-convexity interval
    ``cos(pi/m) < b < sec(pi/m)``, the paired distances from each vertex are
    strictly ordered, so no paired-offset collision can create four equal
    distances.
    """

    _check_m(m)
    sp = _sympy()
    h = sp.pi / m
    s = sp.sin(h)
    c = sp.cos(h)
    certificates: list[AlternatingTwoRadiusGapCertificate] = []
    for k in range(1, m - 1):
        if k % 2 == 0:
            gap = sp.simplify(s * (2 * sp.sin((k + 1) * h) - s))
            certificates.append(
                AlternatingTwoRadiusGapCertificate(
                    k=k,
                    parity="even",
                    endpoint="b=cos(pi/m)",
                    gap_at_endpoint=gap,
                    positive=_is_positive(gap),
                )
            )
        else:
            gap = sp.simplify(
                s * (2 * c * sp.sin((k + 1) * h) - s) / (c * c)
            )
            certificates.append(
                AlternatingTwoRadiusGapCertificate(
                    k=k,
                    parity="odd",
                    endpoint="b=sec(pi/m)",
                    gap_at_endpoint=gap,
                    positive=_is_positive(gap),
                )
            )
    all_positive = all(item.positive for item in certificates)
    return AlternatingTwoRadiusFamilySummary(
        m=m,
        n=2 * m,
        h=h,
        convexity_lower=c,
        convexity_upper=sp.simplify(1 / c),
        gap_certificates=certificates,
        all_gap_certificates_positive=all_positive,
        status=(
            "exact_family_obstruction_not_general_proof"
            if all_positive
            else "certificate_check_failed"
        ),
    )


ALTERNATING_DECAGON_PATTERN: list[list[int]] = [
    [2, 3, 7, 8],
    [0, 2, 5, 7],
    [0, 4, 5, 9],
    [2, 4, 7, 9],
    [1, 2, 6, 7],
    [1, 4, 6, 9],
    [3, 4, 8, 9],
    [1, 3, 6, 8],
    [0, 1, 5, 6],
    [0, 3, 5, 8],
]


def two_overlap_crossing_constraints(
    pattern: Sequence[Sequence[int]],
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    """Return source/witness chord crossings forced by two-row overlaps."""

    witness_sets = [set(row) for row in pattern]
    constraints: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for i, j in combinations(range(len(pattern)), 2):
        common = sorted(witness_sets[i] & witness_sets[j])
        if len(common) == 2:
            constraints.append(
                (
                    normalize_chord(i, j),
                    normalize_chord(common[0], common[1]),
                )
            )
        elif len(common) > 2:
            raise ValueError(f"rows {i} and {j} share more than two witnesses")
    return constraints


def alternating_decagon_crossing_search() -> CyclicCrossingSearchSummary:
    """Exhaustively check cyclic orders for the concave alternating decagon pattern."""

    n = len(ALTERNATING_DECAGON_PATTERN)
    constraints = two_overlap_crossing_constraints(ALTERNATING_DECAGON_PATTERN)
    count = 0
    survivor: tuple[int, ...] | None = None
    for perm in permutations(range(1, n)):
        order = (0,) + perm
        if order[1] > order[-1]:
            continue
        count += 1
        if all(
            chords_cross_in_order(source, target, order)
            for source, target in constraints
        ):
            survivor = order
            break
    return CyclicCrossingSearchSummary(
        pattern="alternating_concave_decagon",
        n=n,
        constraint_count=len(constraints),
        normalized_order_count=count,
        survivor=survivor,
        status=(
            "NO_CYCLIC_ORDER"
            if survivor is None
            else "CYCLIC_ORDER_SURVIVOR_FOUND"
        ),
    )


def summary_to_json(summary: TwoOrbitSummary) -> dict[str, object]:
    """Return a JSON-friendly exact summary."""
    return {
        "type": "two_orbit_radius_propagation",
        "status": "exact_ansatz_obstruction_not_general_proof",
        "t": summary.t,
        "m": summary.m,
        "n": summary.n,
        "h": str(summary.h),
        "ratio": str(summary.ratio),
        "distance_equation": str(summary.distance_equation),
        "a_distance_gap": str(summary.a_distance_gap),
        "b_distance_gap": str(summary.b_distance_gap),
        "turn_at_b": str(summary.turn_at_b),
        "turn_at_a": str(summary.turn_at_a),
        "cos_minus_ratio": str(summary.cos_minus_ratio),
        "sec_minus_ratio": str(summary.sec_minus_ratio),
        "lower_convexity_certificate": str(summary.lower_convexity_certificate),
        "forced_concave": summary.forced_concave,
        "interpretation": (
            "The equality equations force S/R below cos(h), while strict "
            "convexity of the alternating polygon requires S/R > cos(h)."
        ),
    }


def alternating_two_radius_family_to_json(
    summary: AlternatingTwoRadiusFamilySummary,
) -> dict[str, object]:
    """Return a JSON-friendly alternating-family summary."""

    return {
        "type": "alternating_two_radius_regular_family",
        "status": summary.status,
        "m": summary.m,
        "n": summary.n,
        "h": str(summary.h),
        "convexity_interval": {
            "lower": str(summary.convexity_lower),
            "upper": str(summary.convexity_upper),
        },
        "gap_certificates": [
            {
                "k": item.k,
                "parity": item.parity,
                "endpoint": item.endpoint,
                "gap_at_endpoint": str(item.gap_at_endpoint),
                "positive": item.positive,
            }
            for item in summary.gap_certificates
        ],
        "all_gap_certificates_positive": summary.all_gap_certificates_positive,
        "interpretation": (
            "Inside the strict-convexity interval, adjacent paired-distance "
            "gaps are positive, so paired offsets are strictly ordered. The "
            "family cannot give four equal-distance witnesses at a vertex."
        ),
    }


def cyclic_crossing_search_to_json(
    summary: CyclicCrossingSearchSummary,
) -> dict[str, object]:
    """Return a JSON-friendly cyclic crossing search summary."""

    return {
        "type": "fixed_pattern_cyclic_crossing_search",
        "pattern": summary.pattern,
        "status": summary.status,
        "n": summary.n,
        "constraint_count": summary.constraint_count,
        "normalized_order_count": summary.normalized_order_count,
        "survivor": None if summary.survivor is None else list(summary.survivor),
        "interpretation": (
            "This is a fixed selected-witness pattern obstruction only; it is "
            "not an n=10 completeness theorem and not a counterexample."
        ),
    }


def linearized_escape_to_json(
    summary: TwoOrbitLinearizedEscapeSummary,
) -> dict[str, object]:
    """Return a JSON-friendly linearized escape diagnostic."""

    return {
        "type": "two_orbit_linearized_escape",
        "status": summary.status,
        "trust_label": summary.trust_label,
        "t": summary.t,
        "m": summary.m,
        "n": summary.n,
        "equality_equation_count": summary.equality_equation_count,
        "equality_rank": summary.equality_rank,
        "kernel_dimension": summary.kernel_dimension,
        "concave_turn_count": summary.concave_turn_count,
        "derivative_floor": summary.derivative_floor,
        "min_concave_turn_derivative": summary.min_concave_turn_derivative,
        "max_abs_equality_jacobian_residual": (
            summary.max_abs_equality_jacobian_residual
        ),
        "l1_norm": summary.l1_norm,
        "direction": summary.direction,
        "interpretation": (
            "A LINEARIZED_ESCAPE_FOUND result means the equality Jacobian has "
            "a first-order tangent direction that increases every concave "
            "alternating turn. This rules out the hoped-for first-order "
            "Farkas obstruction for this ansatz, but it is not a counterexample."
        ),
    }


def _squared_distance(p: Sequence[object], q: Sequence[object]):
    sp = _sympy()
    return sp.simplify((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


def _numeric_lp():
    try:
        import numpy as np  # type: ignore
        from scipy.optimize import linprog  # type: ignore
    except ImportError as exc:  # pragma: no cover - depends on dev deps
        raise RuntimeError(
            "NumPy and SciPy are required for linearized escape diagnostics"
        ) from exc
    return np, linprog


def _numeric_points(t: int):
    sp = _sympy()
    np, _ = _numeric_lp()
    return np.array(
        [
            [float(sp.N(x, 80)), float(sp.N(y, 80))]
            for x, y in two_orbit_points(t)
        ],
        dtype=float,
    )


def _selected_equality_jacobian(points, cohorts: Sequence[Sequence[int]]):
    np, _ = _numeric_lp()
    n = len(points)
    rows = []
    for center, row in enumerate(cohorts):
        base = row[0]
        for target in row[1:]:
            gradient = np.zeros(2 * n)
            target_delta = points[center] - points[target]
            base_delta = points[center] - points[base]
            gradient[2 * center : 2 * center + 2] += 2 * (
                target_delta - base_delta
            )
            gradient[2 * target : 2 * target + 2] += -2 * target_delta
            gradient[2 * base : 2 * base + 2] += 2 * base_delta
            rows.append(gradient)
    return np.vstack(rows)


def _turn_jacobian(points):
    np, _ = _numeric_lp()
    n = len(points)
    rows = []
    values = []
    for idx in range(n):
        p = points[idx]
        q = points[(idx + 1) % n]
        r = points[(idx + 2) % n]
        e = q - p
        f = r - q
        values.append(_det2(e, f))

        gradient = np.zeros(2 * n)
        p_grad = np.array([-f[1], f[0]])
        r_grad = np.array([-e[1], e[0]])
        q_grad = -(p_grad + r_grad)
        gradient[2 * idx : 2 * idx + 2] = p_grad
        q_idx = (idx + 1) % n
        r_idx = (idx + 2) % n
        gradient[2 * q_idx : 2 * q_idx + 2] = q_grad
        gradient[2 * r_idx : 2 * r_idx + 2] = r_grad
        rows.append(gradient)
    return np.vstack(rows), np.array(values, dtype=float)


def _det2(u: Sequence[float], v: Sequence[float]) -> float:
    return float(u[0] * v[1] - u[1] * v[0])


def _sub(p: Sequence[object], q: Sequence[object]) -> tuple[object, object]:
    return (p[0] - q[0], p[1] - q[1])


def _det(u: Sequence[object], v: Sequence[object]):
    return u[0] * v[1] - u[1] * v[0]


def _is_positive(value: object) -> bool:
    sp = _sympy()
    simplified = sp.simplify(value)
    if simplified.is_positive is True:
        return True
    if simplified.is_positive is False:
        return False
    return bool(sp.N(simplified, 80) > 0)
