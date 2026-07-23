"""Free-Cartesian realization search for one fixed ordered witness pattern.

The boundary order is ``0, ..., n-1``.  Translation, rotation, and scale are
removed by fixing ``p_0=(0,0)`` and ``p_1=(1,0)``.  Equality and guard
Jacobians are analytic; results remain numerical until separately exactified.
"""

from __future__ import annotations

import dataclasses
import math
from collections.abc import Iterator, Sequence

import numpy as np
from scipy.optimize import least_squares


Array = np.ndarray
Pattern = Sequence[Sequence[int]]


@dataclasses.dataclass(frozen=True)
class CartesianConfig:
    pair_floor: float = 2.0e-3
    side_floor: float = 2.0e-6
    weight_pair: float = 25.0
    weight_side: float = 40.0
    candidate_tolerance: float = 1.0e-10


def unpack_points(vector: Array, n: int) -> Array:
    """Reconstruct points in the fixed similarity gauge."""

    vector = np.asarray(vector, dtype=float)
    if vector.shape != (2 * n - 4,):
        raise ValueError(f"expected vector shape {(2 * n - 4,)}, got {vector.shape}")
    points = np.empty((n, 2), dtype=float)
    points[0] = (0.0, 0.0)
    points[1] = (1.0, 0.0)
    points[2:] = vector.reshape(n - 2, 2)
    return points


def pack_points(points: Array) -> Array:
    """Normalize a point array to the fixed gauge and pack its free entries."""

    points = np.asarray(points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 3:
        raise ValueError("points must have shape (n, 2) with n >= 3")
    shifted = points - points[0]
    edge = shifted[1]
    scale = float(np.linalg.norm(edge))
    if not np.isfinite(scale) or scale <= 1.0e-15:
        raise ValueError("the first boundary edge is degenerate")
    cosine = edge[0] / scale
    sine = edge[1] / scale
    rotation = np.asarray([[cosine, sine], [-sine, cosine]])
    normalized = shifted @ rotation.T / scale
    return normalized[2:].reshape(-1)


def regular_start(n: int) -> Array:
    angles = 2.0 * math.pi * np.arange(n) / float(n)
    points = np.column_stack((np.cos(angles), np.sin(angles)))
    return pack_points(points)


def convex_starts(n: int, restarts: int, seed: int) -> Iterator[Array]:
    """Yield deterministic strictly convex starts in the fixed gauge."""

    if restarts <= 0:
        raise ValueError("restarts must be positive")
    yield regular_start(n)
    rng = np.random.default_rng(seed)
    for _ in range(restarts - 1):
        gaps = 0.35 + rng.gamma(shape=2.0, scale=1.0, size=n)
        angles = 2.0 * math.pi * np.cumsum(np.r_[0.0, gaps[:-1]]) / np.sum(gaps)
        points = np.column_stack((np.cos(angles), np.sin(angles)))
        stretch = math.exp(float(rng.normal(0.0, 0.35)))
        squeeze = math.exp(float(rng.normal(0.0, 0.35)))
        shear = float(rng.normal(0.0, 0.25))
        affine = np.asarray([[stretch, shear], [0.0, squeeze]])
        yield pack_points(points @ affine.T)


def _free_jacobian(full_gradient: Array) -> Array:
    return np.asarray(full_gradient[2:], dtype=float).reshape(-1)


def _add_squared_distance_gradient(
    gradient: Array, points: Array, left: int, right: int, coefficient: float
) -> None:
    delta = 2.0 * coefficient * (points[left] - points[right])
    gradient[left] += delta
    gradient[right] -= delta


def equality_residual_jacobian(points: Array, pattern: Pattern) -> tuple[Array, Array]:
    """Return three independent squared-distance differences per center."""

    points = np.asarray(points, dtype=float)
    n = len(points)
    if len(pattern) != n:
        raise ValueError(f"expected {n} witness rows, got {len(pattern)}")
    residuals: list[float] = []
    jacobian: list[Array] = []
    for center, row in enumerate(pattern):
        if len(row) != 4 or center in row or len(set(row)) != 4:
            raise ValueError(f"invalid four-witness row at center {center}: {row}")
        base = int(row[0])
        base_delta = points[center] - points[base]
        base_sq = float(np.dot(base_delta, base_delta))
        for witness_raw in row[1:]:
            witness = int(witness_raw)
            delta = points[center] - points[witness]
            residuals.append(float(np.dot(delta, delta)) - base_sq)
            gradient = np.zeros_like(points)
            _add_squared_distance_gradient(gradient, points, center, witness, 1.0)
            _add_squared_distance_gradient(gradient, points, center, base, -1.0)
            jacobian.append(_free_jacobian(gradient))
    return np.asarray(residuals), np.asarray(jacobian)


def guard_residual_jacobian(
    points: Array, config: CartesianConfig
) -> tuple[Array, Array]:
    """Return active pair-separation and strict-convexity hinge guards."""

    points = np.asarray(points, dtype=float)
    n = len(points)
    residuals: list[float] = []
    jacobian: list[Array] = []
    pair_floor_sq = config.pair_floor**2
    for left in range(n):
        for right in range(left + 1, n):
            delta = points[left] - points[right]
            distance_sq = float(np.dot(delta, delta))
            gradient = np.zeros_like(points)
            if distance_sq < pair_floor_sq:
                residual = config.weight_pair * (pair_floor_sq - distance_sq)
                _add_squared_distance_gradient(
                    gradient, points, left, right, -config.weight_pair
                )
            else:
                residual = 0.0
            residuals.append(residual)
            jacobian.append(_free_jacobian(gradient))

    for left in range(n):
        right = (left + 1) % n
        a = points[left]
        b = points[right]
        for vertex in range(n):
            if vertex in (left, right):
                continue
            p = points[vertex]
            side = float((b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0]))
            gradient = np.zeros_like(points)
            if side < config.side_floor:
                residual = config.weight_side * (config.side_floor - side)
                gradient[left] += config.weight_side * np.asarray(
                    [p[1] - b[1], b[0] - p[0]]
                )
                gradient[right] += config.weight_side * np.asarray(
                    [a[1] - p[1], p[0] - a[0]]
                )
                gradient[vertex] += config.weight_side * np.asarray(
                    [b[1] - a[1], a[0] - b[0]]
                )
            else:
                residual = 0.0
            residuals.append(residual)
            jacobian.append(_free_jacobian(gradient))

    width = 2 * n - 4
    if not residuals:
        return np.empty(0), np.empty((0, width))
    return np.asarray(residuals), np.asarray(jacobian)


def residual_jacobian(
    vector: Array, pattern: Pattern, config: CartesianConfig
) -> tuple[Array, Array]:
    points = unpack_points(vector, len(pattern))
    equality_residuals, equality_jacobian = equality_residual_jacobian(points, pattern)
    guard_residuals, guard_jacobian = guard_residual_jacobian(points, config)
    return (
        np.concatenate((equality_residuals, guard_residuals)),
        np.vstack((equality_jacobian, guard_jacobian)),
    )


def diagnostics(points: Array, pattern: Pattern, config: CartesianConfig) -> dict[str, object]:
    points = np.asarray(points, dtype=float)
    n = len(points)
    delta = points[:, None, :] - points[None, :, :]
    squared = np.einsum("ijk,ijk->ij", delta, delta)
    spreads = []
    relative_spreads = []
    for center, row in enumerate(pattern):
        values = squared[center, np.asarray(row, dtype=int)]
        spread = float(np.max(values) - np.min(values))
        spreads.append(spread)
        relative_spreads.append(spread / max(float(np.mean(values)), np.finfo(float).tiny))

    pair_values = squared[np.triu_indices(n, 1)]
    sides = []
    for left in range(n):
        right = (left + 1) % n
        edge = points[right] - points[left]
        for vertex in range(n):
            if vertex in (left, right):
                continue
            offset = points[vertex] - points[left]
            sides.append(float(edge[0] * offset[1] - edge[1] * offset[0]))
    equality_residuals, _ = equality_residual_jacobian(points, pattern)
    maximum_relative = max(relative_spreads)
    minimum_pair = math.sqrt(max(0.0, float(np.min(pair_values))))
    minimum_side = float(np.min(sides))
    return {
        "eq_rms": float(np.sqrt(np.mean(equality_residuals**2))),
        "max_squared_distance_spread": max(spreads),
        "max_relative_spread": maximum_relative,
        "min_pair_distance": minimum_pair,
        "min_side_margin": minimum_side,
        "strictly_convex": minimum_side > 0.0,
        "candidate": bool(
            maximum_relative <= config.candidate_tolerance
            and minimum_pair >= config.pair_floor
            and minimum_side >= config.side_floor
        ),
    }


def _report_key(report: dict[str, object], config: CartesianConfig) -> tuple[float, ...]:
    pair_deficit = max(0.0, config.pair_floor - float(report["min_pair_distance"]))
    side_deficit = max(0.0, config.side_floor - float(report["min_side_margin"]))
    return (
        0.0 if bool(report["candidate"]) else 1.0,
        pair_deficit / config.pair_floor,
        side_deficit / config.side_floor,
        float(report["max_relative_spread"]),
    )


def search_fixed_order(
    pattern: Pattern,
    *,
    restarts: int,
    max_nfev: int,
    seed: int,
    config: CartesianConfig | None = None,
) -> dict[str, object]:
    """Run guarded least squares for one natural-boundary-order pattern."""

    if max_nfev <= 0:
        raise ValueError("max_nfev must be positive")
    if config is None:
        config = CartesianConfig()
    best: dict[str, object] | None = None
    for restart, start in enumerate(convex_starts(len(pattern), restarts, seed)):
        result = least_squares(
            lambda vector: residual_jacobian(vector, pattern, config)[0],
            start,
            jac=lambda vector: residual_jacobian(vector, pattern, config)[1],
            method="trf",
            max_nfev=max_nfev,
            x_scale="jac",
        )
        points = unpack_points(result.x, len(pattern))
        report = diagnostics(points, pattern, config)
        report.update(
            {
                "restart": restart,
                "optimizer_success": bool(result.success),
                "optimizer_status": int(result.status),
                "optimizer_message": str(result.message),
                "nfev": int(result.nfev),
                "cost": float(result.cost),
                "coordinates": points.tolist(),
            }
        )
        if best is None or _report_key(report, config) < _report_key(best, config):
            best = report
        if bool(report["candidate"]):
            break
    assert best is not None
    return best
