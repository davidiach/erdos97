"""Conservative interval checks for saved numerical candidates.

The floating path certifies residual bounds, not exact equalities. Exact
acceptance is reserved for rational-coordinate inputs under
``coordinates_exact``.
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from typing import Any, Sequence

import numpy as np

from erdos97.search import (
    Pattern,
    independent_diagnostics,
    normalize_points,
    polygon_area2,
    validate_candidate_shape,
)


@dataclass(frozen=True)
class Interval:
    lo: float
    hi: float

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError(f"empty interval [{self.lo}, {self.hi}]")

    def __add__(self, other: Interval) -> Interval:
        return Interval(down(self.lo + other.lo), up(self.hi + other.hi))

    def __sub__(self, other: Interval) -> Interval:
        return Interval(down(self.lo - other.hi), up(self.hi - other.lo))

    def __mul__(self, other: Interval) -> Interval:
        products = (
            self.lo * other.lo,
            self.lo * other.hi,
            self.hi * other.lo,
            self.hi * other.hi,
        )
        return Interval(down(min(products)), up(max(products)))

    def square(self) -> Interval:
        if self.lo <= 0.0 <= self.hi:
            return Interval(0.0, up(max(self.lo * self.lo, self.hi * self.hi)))
        values = (self.lo * self.lo, self.hi * self.hi)
        return Interval(down(min(values)), up(max(values)))

    def scaled(self, factor: float) -> Interval:
        if factor >= 0:
            return Interval(down(factor * self.lo), up(factor * self.hi))
        return Interval(down(factor * self.hi), up(factor * self.lo))

    def contains_zero(self) -> bool:
        return self.lo <= 0.0 <= self.hi

    def abs_upper(self) -> float:
        return max(abs(self.lo), abs(self.hi))

    def to_json(self) -> list[float]:
        return [float(self.lo), float(self.hi)]


def down(value: float) -> float:
    return math.nextafter(float(value), -math.inf)


def up(value: float) -> float:
    return math.nextafter(float(value), math.inf)


def load_candidate(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def parse_pattern(data: dict[str, Any]) -> Pattern:
    return [[int(j) for j in row] for row in data["S"]]


def parse_float_coordinates(data: dict[str, Any]) -> np.ndarray:
    coordinates = data.get("coordinates", data.get("coordinates_float"))
    if coordinates is None:
        raise KeyError("candidate JSON must contain coordinates or coordinates_float")
    return np.array(coordinates, dtype=float)


def parse_exact_coordinates(data: dict[str, Any]) -> list[list[Fraction]] | None:
    raw = data.get("coordinates_exact")
    if raw is None:
        return None
    if not isinstance(raw, list):
        raise ValueError("coordinates_exact must be a list")
    parsed: list[list[Fraction]] = []
    for row in raw:
        if not isinstance(row, list) or len(row) != 2:
            raise ValueError("coordinates_exact entries must be coordinate pairs")
        parsed.append([Fraction(str(row[0])), Fraction(str(row[1]))])
    return parsed


def exact_coordinates_to_float(points: list[list[Fraction]]) -> np.ndarray:
    return np.array([[float(x), float(y)] for x, y in points], dtype=float)


def coordinate_intervals(
    coordinates: np.ndarray,
    *,
    abs_radius: float,
    rel_radius: float,
) -> list[list[Interval]]:
    intervals: list[list[Interval]] = []
    for row in coordinates:
        interval_row: list[Interval] = []
        for value in row:
            radius = abs_radius + rel_radius * abs(float(value))
            interval_row.append(Interval(down(float(value) - radius), up(float(value) + radius)))
        intervals.append(interval_row)
    return intervals


def interval_sqdist(points: list[list[Interval]], i: int, j: int) -> Interval:
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return dx.square() + dy.square()


def interval_cross(
    points: list[list[Interval]],
    a: int,
    b: int,
    c: int,
) -> Interval:
    edge_x = points[b][0] - points[a][0]
    edge_y = points[b][1] - points[a][1]
    vertex_x = points[c][0] - points[a][0]
    vertex_y = points[c][1] - points[a][1]
    return (edge_x * vertex_y) - (edge_y * vertex_x)


def convexity_interval_bounds(points: list[list[Interval]], sign: float) -> dict[str, Any]:
    n = len(points)
    margins: list[Interval] = []
    for i in range(n):
        for j in range(n):
            if j == i or j == (i + 1) % n:
                continue
            margins.append(interval_cross(points, i, (i + 1) % n, j).scaled(sign))
    if not margins:
        return {"certified": False, "min_interval": [float("-inf"), float("-inf")]}
    min_lo = min(margin.lo for margin in margins)
    min_hi = min(margin.hi for margin in margins)
    return {
        "certified": min_lo > 0.0,
        "min_interval": [float(min_lo), float(min_hi)],
    }


def residual_intervals(points: list[list[Interval]], S: Pattern) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for i, row in enumerate(S):
        base = row[0]
        base_dist = interval_sqdist(points, i, base)
        for target in row[1:]:
            residual = interval_sqdist(points, i, target) - base_dist
            records.append(
                {
                    "center": i,
                    "base": base,
                    "target": target,
                    "interval": residual.to_json(),
                    "abs_upper": residual.abs_upper(),
                    "contains_zero": residual.contains_zero(),
                }
            )
    return records


def exact_sqdist(points: list[list[Fraction]], i: int, j: int) -> Fraction:
    dx = points[i][0] - points[j][0]
    dy = points[i][1] - points[j][1]
    return dx * dx + dy * dy


def exact_cross(points: list[list[Fraction]], a: int, b: int, c: int) -> Fraction:
    edge_x = points[b][0] - points[a][0]
    edge_y = points[b][1] - points[a][1]
    vertex_x = points[c][0] - points[a][0]
    vertex_y = points[c][1] - points[a][1]
    return edge_x * vertex_y - edge_y * vertex_x


def exact_verification(points: list[list[Fraction]], S: Pattern) -> dict[str, Any]:
    n = len(points)
    area2 = sum(
        points[i][0] * points[(i + 1) % n][1] - points[i][1] * points[(i + 1) % n][0]
        for i in range(n)
    )
    sign = Fraction(-1 if area2 < 0 else 1)
    margins = [
        sign * exact_cross(points, i, (i + 1) % n, j)
        for i in range(n)
        for j in range(n)
        if j != i and j != (i + 1) % n
    ]
    residuals = [
        exact_sqdist(points, i, target) - exact_sqdist(points, i, row[0])
        for i, row in enumerate(S)
        for target in row[1:]
    ]
    min_pair = min(
        exact_sqdist(points, i, j)
        for i in range(n)
        for j in range(i + 1, n)
    )
    convexity_certified = bool(margins) and min(margins) > 0
    distance_equalities_certified = all(residual == 0 for residual in residuals)
    accepted = convexity_certified and distance_equalities_certified and min_pair > 0
    return {
        "exact_mode": True,
        "convexity_certified": convexity_certified,
        "distance_equalities_certified": distance_equalities_certified,
        "min_exact_convexity_margin": str(min(margins)) if margins else None,
        "max_abs_exact_residual": str(max((abs(value) for value in residuals), default=Fraction(0))),
        "failure_mode": "exact_algebraic_candidate_accepted" if accepted else "exact_algebraic_rejected",
    }


def classify_float_result(
    *,
    validation_errors: Sequence[str],
    convexity_certified: bool,
    distance_equalities_certified: bool,
    definite_nonzero_residuals: int,
    claimed_success: bool,
) -> str:
    if validation_errors:
        return "malformed"
    if convexity_certified and distance_equalities_certified:
        return "interval_certified_candidate_at_tolerance"
    if convexity_certified and definite_nonzero_residuals:
        if claimed_success:
            return "floating_near_miss"
        return "interval_convexity_certified_equality_uncertified"
    if convexity_certified:
        return "interval_convexity_certified_equality_uncertified"
    return "uncertified"


def malformed_result(message: str) -> dict[str, Any]:
    """Return the standard malformed-input result shape."""

    return {
        "ok": False,
        "failure_mode": "malformed",
        "validation_errors": [message],
        "claim_strength": "MALFORMED_INPUT",
    }


def validate_interval_parameters(
    *,
    eq_bound: float,
    coord_abs_radius: float,
    coord_rel_radius: float,
) -> list[str]:
    """Return validation errors for interval verifier parameters."""

    errors = []
    for name, value in [
        ("eq_bound", eq_bound),
        ("coord_abs_radius", coord_abs_radius),
        ("coord_rel_radius", coord_rel_radius),
    ]:
        if not math.isfinite(value):
            errors.append(f"{name} must be finite, got {value!r}")
        elif value < 0.0:
            errors.append(f"{name} must be nonnegative, got {value!r}")
    return errors


def verify_interval_json(
    path: str | Path,
    *,
    eq_bound: float = 1e-8,
    coord_abs_radius: float = 1e-12,
    coord_rel_radius: float = 1e-12,
) -> dict[str, Any]:
    parameter_errors = validate_interval_parameters(
        eq_bound=eq_bound,
        coord_abs_radius=coord_abs_radius,
        coord_rel_radius=coord_rel_radius,
    )
    if parameter_errors:
        return malformed_result("; ".join(parameter_errors))

    data = load_candidate(path)
    try:
        S = parse_pattern(data)
        exact_coordinates = parse_exact_coordinates(data)
        raw_coordinates = (
            exact_coordinates_to_float(exact_coordinates)
            if exact_coordinates is not None
            else parse_float_coordinates(data)
        )
    except (KeyError, TypeError, ValueError) as exc:
        return malformed_result(str(exc))

    validation_errors = validate_candidate_shape(raw_coordinates, S)
    if validation_errors:
        return {
            "ok": False,
            "failure_mode": "malformed",
            "validation_errors": validation_errors,
            "claim_strength": "MALFORMED_INPUT",
        }

    if exact_coordinates is not None:
        exact = exact_verification(exact_coordinates, S)
        return {
            "ok": exact["failure_mode"] == "exact_algebraic_candidate_accepted",
            "validation_errors": [],
            "eq_bound": eq_bound,
            "does_not_claim": [
                "general proof of Erdos Problem #97",
                "counterexample without independent review",
            ],
            "claim_strength": (
                "EXACT_OR_ALGEBRAIC_CANDIDATE_ACCEPTED_PENDING_REVIEW"
                if exact["failure_mode"] == "exact_algebraic_candidate_accepted"
                else "EXACT_OR_ALGEBRAIC_INPUT_REJECTED"
            ),
            **exact,
        }

    coordinates = normalize_points(raw_coordinates)
    diagnostics = independent_diagnostics(coordinates, S)
    points = coordinate_intervals(
        coordinates,
        abs_radius=coord_abs_radius,
        rel_radius=coord_rel_radius,
    )
    sign = -1.0 if polygon_area2(coordinates) < 0 else 1.0
    convexity = convexity_interval_bounds(points, sign)
    residuals = residual_intervals(points, S)
    max_abs_residual_bound = max((record["abs_upper"] for record in residuals), default=0.0)
    definite_nonzero = sum(1 for record in residuals if not record["contains_zero"])
    distance_equalities_certified = bool(residuals) and max_abs_residual_bound <= eq_bound
    failure_mode = classify_float_result(
        validation_errors=[],
        convexity_certified=bool(convexity["certified"]),
        distance_equalities_certified=distance_equalities_certified,
        definite_nonzero_residuals=definite_nonzero,
        claimed_success=bool(data.get("success") is True),
    )
    ok = failure_mode == "interval_certified_candidate_at_tolerance"
    return {
        "ok": ok,
        "failure_mode": failure_mode,
        "validation_errors": [],
        "eq_bound": eq_bound,
        "coordinate_interval": {
            "abs_radius": coord_abs_radius,
            "rel_radius": coord_rel_radius,
            "normalization": "search.normalize_points applied before interval bounds",
        },
        "convexity_certified": bool(convexity["certified"]),
        "convexity_margin_interval": convexity["min_interval"],
        "distance_equalities_certified": distance_equalities_certified,
        "residual_bounds": {
            "max_abs_residual_bound": max_abs_residual_bound,
            "definite_nonzero_residuals": definite_nonzero,
            "residual_count": len(residuals),
        },
        "claim_strength": (
            "INTERVAL_BOUNDED_NUMERICAL_CANDIDATE"
            if ok
            else "NUMERICAL_EVIDENCE_OR_NEAR_MISS_NOT_A_COUNTEREXAMPLE"
        ),
        "does_not_claim": [
            "general proof of Erdos Problem #97",
            "counterexample to Erdos Problem #97",
            "exact equality from floating residuals alone",
        ],
        "float_diagnostics": {
            "max_spread": diagnostics["max_spread"],
            "max_rel_spread": diagnostics["max_rel_spread"],
            "convexity_margin": diagnostics["convexity_margin"],
            "min_pair_distance": diagnostics["min_pair_distance"],
        },
    }
