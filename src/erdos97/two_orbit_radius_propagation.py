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
from typing import Sequence


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


def _check_t(t: int) -> None:
    if not isinstance(t, int) or t < 1:
        raise ValueError("t must be a positive integer")


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


def _squared_distance(p: Sequence[object], q: Sequence[object]):
    sp = _sympy()
    return sp.simplify((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2)


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
