#!/usr/bin/env python3
"""Screen the complex two-mode cyclic family for Erdos Problem #97.

The family is

    z_i = w**i + c*w**(k*i),  w = exp(2*pi*I/n),  c complex.

For fixed ``(n, k)`` and center zero, every squared distance has the form

    alpha_s + beta_s*R + ux_s*x + uy_s*y,

where ``x=Re(c)``, ``y=Im(c)``, and ``R=|c|^2``.  Requiring four selected
distances to agree therefore gives three linear equations in ``(R,x,y)``.
This script enumerates all such row-zero quadruples, intersects their affine
solutions with ``R=x^2+y^2``, and tests every resulting coefficient against
all rows and strict convexity.

This is a floating-point construction screen, not an exact certificate.  A
reported hit must be rebuilt in exact cyclotomic arithmetic before it can be
called a counterexample. Rank-deficient affine systems are handled: rank two
by line/paraboloid intersection at float precision, and rank one by
crossing its conic with every collision plane from the remaining rows.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class ScreenConfig:
    linear_tol: float = 2.0e-10
    surface_tol: float = 2.0e-9
    equality_tol: float = 2.0e-8
    dedup_digits: int = 9


def row_coefficients(n: int, k: int, center: int) -> np.ndarray:
    """Return rows ``[constant, R, x, y]`` for shifts 1 through n-1."""

    angles = 2.0 * math.pi * np.arange(n) / float(n)
    w1 = np.exp(1j * angles)
    wk = np.exp(1j * k * angles)
    rows = []
    for shift in range(1, n):
        target = (center + shift) % n
        a = w1[target] - w1[center]
        b = wk[target] - wk[center]
        gamma = b * np.conjugate(a)
        rows.append(
            [
                float(abs(a) ** 2),
                float(abs(b) ** 2),
                float(2.0 * gamma.real),
                float(-2.0 * gamma.imag),
            ]
        )
    return np.asarray(rows, dtype=float)


def _surface_error(solution: np.ndarray) -> float:
    radius_sq, real, imag = solution
    scale = max(1.0, abs(radius_sq), real * real + imag * imag)
    return abs(radius_sq - real * real - imag * imag) / scale


def _rank_two_candidates(
    matrix: np.ndarray, rhs: np.ndarray, cfg: ScreenConfig
) -> list[complex]:
    """Intersect a rank-two affine solution line with R=x^2+y^2."""

    u, singular, vh = np.linalg.svd(matrix)
    scale = max(1.0, float(singular[0]))
    rank = int(np.sum(singular > cfg.linear_tol * scale))
    if rank != 2:
        return []
    particular = np.linalg.lstsq(matrix, rhs, rcond=None)[0]
    if np.linalg.norm(matrix @ particular - rhs) > cfg.linear_tol * max(
        1.0, np.linalg.norm(rhs)
    ):
        return []
    direction = vh[-1]
    r0, x0, y0 = particular
    dr, dx, dy = direction
    # r0+t*dr = (x0+t*dx)^2 + (y0+t*dy)^2.
    qa = dx * dx + dy * dy
    qb = 2.0 * (x0 * dx + y0 * dy) - dr
    qc = x0 * x0 + y0 * y0 - r0
    roots: list[float] = []
    if abs(qa) <= cfg.linear_tol:
        if abs(qb) > cfg.linear_tol:
            roots.append(-qc / qb)
    else:
        discriminant = qb * qb - 4.0 * qa * qc
        tolerance = cfg.surface_tol * max(1.0, qb * qb, abs(4.0 * qa * qc))
        if discriminant >= -tolerance:
            discriminant = max(0.0, discriminant)
            square_root = math.sqrt(discriminant)
            roots.extend(
                ((-qb - square_root) / (2.0 * qa), (-qb + square_root) / (2.0 * qa))
            )
    out = []
    for value in roots:
        solution = particular + value * direction
        if _surface_error(solution) <= cfg.surface_tol:
            out.append(complex(float(solution[1]), float(solution[2])))
    return out


def _normalized_plane(row: np.ndarray, digits: int) -> tuple[float, ...] | None:
    """Canonicalize constant + (R,x,y) coefficients = 0."""

    coefficient_norm = float(np.linalg.norm(row[1:]))
    if coefficient_norm <= 1.0e-12:
        return None
    normalized = np.asarray(row, dtype=float) / coefficient_norm
    pivot = int(np.argmax(np.abs(normalized)))
    if normalized[pivot] < 0.0:
        normalized = -normalized
    return tuple(round(float(value), digits) for value in normalized)


def rank_one_intersection_candidates(
    n: int, k: int, cfg: ScreenConfig
) -> tuple[list[complex], dict[str, int]]:
    """Resolve rank-one row-zero conics using one collision from another row.

    A fourfold class in every other row contains at least one equal-distance
    pair. Intersecting that collision plane with the row-zero plane gives an
    affine line in (R,x,y) unless the two planes coincide; the line has at
    most two intersections with R=x^2+y^2.
    """

    coefficients = row_coefficients(n, k, 0)
    plane_map: dict[tuple[float, ...], np.ndarray] = {}
    rank_zero = 0
    inconsistent = 0
    for quadruple in combinations(range(n - 1), 4):
        rows = coefficients[list(quadruple)]
        differences = rows[1:] - rows[0]
        scale = max(1.0, float(np.max(np.abs(differences))))
        augmented_rank = int(
            np.linalg.matrix_rank(differences, tol=cfg.linear_tol * scale)
        )
        matrix_rank = int(
            np.linalg.matrix_rank(differences[:, 1:], tol=cfg.linear_tol * scale)
        )
        if augmented_rank == 0:
            rank_zero += 1
            continue
        if augmented_rank != 1:
            continue
        if matrix_rank == 0:
            inconsistent += 1
            continue
        row = differences[int(np.argmax(np.linalg.norm(differences, axis=1)))]
        key = _normalized_plane(row, cfg.dedup_digits)
        if key is not None:
            plane_map.setdefault(key, np.asarray(key, dtype=float))

    candidates: list[complex] = []
    coincident_plane_collisions = 0
    independent_collisions = 0
    for row_zero_plane in plane_map.values():
        for center in range(1, n):
            other = row_coefficients(n, k, center)
            for left, right in combinations(range(n - 1), 2):
                collision = other[right] - other[left]
                matrix = np.vstack((row_zero_plane[1:], collision[1:]))
                rhs = -np.asarray((row_zero_plane[0], collision[0]))
                scale = max(1.0, float(np.max(np.abs(matrix))))
                rank = int(np.linalg.matrix_rank(matrix, tol=cfg.linear_tol * scale))
                augmented = np.column_stack((matrix, rhs))
                augmented_rank = int(
                    np.linalg.matrix_rank(
                        augmented,
                        tol=cfg.linear_tol * max(1.0, float(np.max(np.abs(augmented)))),
                    )
                )
                if augmented_rank > rank:
                    continue
                if rank == 2:
                    independent_collisions += 1
                    candidates.extend(_rank_two_candidates(matrix, rhs, cfg))
                elif rank == 1:
                    coincident_plane_collisions += 1

    continuous_all_row_planes = 0
    continuous_plane_samples = 0
    for row_zero_plane in plane_map.values():
        plane_norm_sq = float(np.dot(row_zero_plane, row_zero_plane))
        forced_all_rows = True
        for center in range(n):
            groups: dict[tuple[float, ...], int] = {}
            for value_row in row_coefficients(n, k, center):
                residual = value_row - (
                    float(np.dot(value_row, row_zero_plane))
                    / plane_norm_sq
                    * row_zero_plane
                )
                key = tuple(round(float(value), 8) for value in residual)
                groups[key] = groups.get(key, 0) + 1
            if max(groups.values(), default=0) < 4:
                forced_all_rows = False
                break
        if not forced_all_rows:
            continue
        continuous_all_row_planes += 1
        constant, radial, real_term, imag_term = row_zero_plane
        if abs(radial) > cfg.linear_tol:
            center_value = complex(
                -real_term / (2.0 * radial),
                -imag_term / (2.0 * radial),
            )
            radius_sq = (real_term * real_term + imag_term * imag_term) / (
                4.0 * radial * radial
            ) - constant / radial
            if radius_sq >= -cfg.surface_tol:
                radius = math.sqrt(max(0.0, radius_sq))
                for angle in np.linspace(0.0, 2.0 * math.pi, 721)[:-1]:
                    candidates.append(center_value + radius * np.exp(1j * angle))
                    continuous_plane_samples += 1
        else:
            normal_sq = real_term * real_term + imag_term * imag_term
            if normal_sq > cfg.linear_tol:
                foot = -constant / normal_sq * complex(real_term, imag_term)
                direction = complex(-imag_term, real_term) / math.sqrt(normal_sq)
                for parameter in np.linspace(-20.0, 20.0, 801):
                    candidates.append(foot + parameter * direction)
                    continuous_plane_samples += 1

    unique: dict[tuple[float, float], complex] = {}
    for candidate in candidates:
        key = (
            round(candidate.real, cfg.dedup_digits),
            round(candidate.imag, cfg.dedup_digits),
        )
        unique.setdefault(key, candidate)
    return list(unique.values()), {
        "rank_zero_identity_quadruples": rank_zero,
        "rank_one_inconsistent_quadruples": inconsistent,
        "rank_one_unique_planes": len(plane_map),
        "rank_one_independent_collisions": independent_collisions,
        "rank_one_coincident_plane_collisions": coincident_plane_collisions,
        "rank_one_intersection_candidates": len(unique),
        "rank_one_continuous_all_row_planes": continuous_all_row_planes,
        "rank_one_continuous_plane_samples": continuous_plane_samples,
    }


def row_zero_candidates(
    n: int, k: int, cfg: ScreenConfig
) -> tuple[list[complex], dict[str, int]]:
    """Enumerate all isolated coefficients forced by a row-zero quadruple."""

    coefficients = row_coefficients(n, k, 0)
    quadruples = np.asarray(list(combinations(range(n - 1), 4)), dtype=int)
    base = coefficients[quadruples[:, 0]]
    differences = coefficients[quadruples[:, 1:]] - base[:, None, :]
    matrices = differences[:, :, 1:]
    rhs = -differences[:, :, 0]
    determinants = np.linalg.det(matrices)
    matrix_scale = np.maximum(1.0, np.max(np.abs(matrices), axis=(1, 2)))
    nonsingular = np.abs(determinants) > cfg.linear_tol * matrix_scale**3

    candidates: list[complex] = []
    if np.any(nonsingular):
        solutions = np.linalg.solve(matrices[nonsingular], rhs[nonsingular, :, None])[
            :, :, 0
        ]
        errors = np.asarray([_surface_error(solution) for solution in solutions])
        for solution in solutions[errors <= cfg.surface_tol]:
            candidates.append(complex(float(solution[1]), float(solution[2])))

    rank_two = 0
    rank_low = 0
    for matrix, right in zip(matrices[~nonsingular], rhs[~nonsingular], strict=True):
        rank = int(
            np.linalg.matrix_rank(
                matrix, tol=cfg.linear_tol * max(1.0, np.max(np.abs(matrix)))
            )
        )
        if rank == 2:
            rank_two += 1
            candidates.extend(_rank_two_candidates(matrix, right, cfg))
        else:
            rank_low += 1

    rank_one_candidates, rank_one_stats = rank_one_intersection_candidates(n, k, cfg)
    candidates.extend(rank_one_candidates)

    unique: dict[tuple[float, float], complex] = {}
    for candidate in candidates:
        if not (math.isfinite(candidate.real) and math.isfinite(candidate.imag)):
            continue
        key = (
            round(candidate.real, cfg.dedup_digits),
            round(candidate.imag, cfg.dedup_digits),
        )
        unique.setdefault(key, candidate)
    return list(unique.values()), {
        "quadruples": int(len(quadruples)),
        "nonsingular": int(np.sum(nonsingular)),
        "rank_two": rank_two,
        "rank_zero_or_one_quadruples": rank_low,
        **rank_one_stats,
        "candidate_coefficients": len(unique),
    }


def points(n: int, k: int, coefficient: complex) -> np.ndarray:
    indices = np.arange(n)
    first = np.exp(2j * math.pi * indices / float(n))
    second = np.exp(2j * math.pi * k * indices / float(n))
    values = first + coefficient * second
    return np.column_stack((values.real, values.imag))


def best_four(row: np.ndarray) -> tuple[float, tuple[int, ...]]:
    order = np.argsort(row, kind="stable")
    ordered = row[order]
    spreads = ordered[3:] - ordered[:-3]
    start = int(np.argmin(spreads))
    selected = tuple(sorted(int(value) for value in order[start : start + 4]))
    mean = float(np.mean(ordered[start : start + 4]))
    relative = float(spreads[start]) / max(mean, np.finfo(float).tiny)
    return relative, selected


def all_row_report(n: int, k: int, coefficient: complex) -> dict[str, object]:
    pts = points(n, k, coefficient)
    delta = pts[:, None, :] - pts[None, :, :]
    squared = np.einsum("ijk,ijk->ij", delta, delta)
    windows = []
    maximum = 0.0
    for center in range(n):
        keep = np.arange(n) != center
        relative, local = best_four(squared[center, keep])
        others = np.arange(n)[keep]
        selected = tuple(int(others[index]) for index in local)
        maximum = max(maximum, relative)
        windows.append(
            {"center": center, "witnesses": selected, "relative_spread": relative}
        )

    centroid = np.mean(pts, axis=0)
    angles = np.arctan2(pts[:, 1] - centroid[1], pts[:, 0] - centroid[0])
    order = np.argsort(angles, kind="stable")
    polygon = pts[order]
    edges = np.roll(polygon, -1, axis=0) - polygon
    turns = edges[:, 0] * np.roll(edges[:, 1], -1) - edges[:, 1] * np.roll(
        edges[:, 0], -1
    )
    diameter_sq = float(np.max(squared))
    pair_squared = squared + np.diag(np.full(n, np.inf))
    return {
        "coefficient": [coefficient.real, coefficient.imag],
        "max_relative_spread": maximum,
        "strictly_convex": bool(
            np.min(turns) > 0.0 and np.min(pair_squared) > 1.0e-16 * diameter_sq
        ),
        "min_turn_normalized": float(np.min(turns))
        / max(diameter_sq, np.finfo(float).tiny),
        "min_pair_normalized": math.sqrt(
            float(np.min(pair_squared)) / max(diameter_sq, np.finfo(float).tiny)
        ),
        "cyclic_order": [int(value) for value in order],
        "windows": windows,
    }


def screen_case(n: int, k: int, cfg: ScreenConfig) -> dict[str, object]:
    candidates, counts = row_zero_candidates(n, k, cfg)
    best: dict[str, object] | None = None
    best_convex: dict[str, object] | None = None
    best_invalid_exact_like: dict[str, object] | None = None
    invalid_exact_like_count = 0
    hits = []
    for coefficient in candidates:
        report = all_row_report(n, k, coefficient)
        if best is None or float(report["max_relative_spread"]) < float(
            best["max_relative_spread"]
        ):
            best = report
        if report["strictly_convex"]:
            if best_convex is None or float(report["max_relative_spread"]) < float(
                best_convex["max_relative_spread"]
            ):
                best_convex = report
        elif float(report["max_relative_spread"]) <= cfg.equality_tol:
            invalid_exact_like_count += 1
            if best_invalid_exact_like is None or float(
                report["max_relative_spread"]
            ) < float(best_invalid_exact_like["max_relative_spread"]):
                best_invalid_exact_like = report
        if (
            report["strictly_convex"]
            and float(report["max_relative_spread"]) <= cfg.equality_tol
        ):
            hits.append(report)
    return {
        "n": n,
        "k": k,
        **counts,
        "best": best,
        "best_convex": best_convex,
        "best_invalid_exact_like": best_invalid_exact_like,
        "invalid_exact_like_count": invalid_exact_like_count,
        "hits": hits,
    }


def iter_cases(min_n: int, max_n: int) -> Iterable[tuple[int, int]]:
    for n in range(min_n, max_n + 1):
        for k in range(2, n - 1):
            yield n, k


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=9)
    parser.add_argument("--max-n", type=int, default=30)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.min_n < 5 or args.max_n < args.min_n:
        parser.error("require 5 <= min-n <= max-n")

    cfg = ScreenConfig()
    started = time.monotonic()
    cases = []
    total_hits = 0
    low_rank_quadruples = 0
    invalid_exact_like_count = 0
    for n, k in iter_cases(args.min_n, args.max_n):
        case = screen_case(n, k, cfg)
        cases.append(case)
        total_hits += len(case["hits"])
        low_rank_quadruples += int(case["rank_zero_or_one_quadruples"])
        invalid_exact_like_count += int(case["invalid_exact_like_count"])
        best = case["best"]
        best_text = (
            "none" if best is None else f"{float(best['max_relative_spread']):.3e}"
        )
        print(
            f"n={n} k={k} candidates={case['candidate_coefficients']} "
            f"best={best_text} hits={len(case['hits'])} "
            f"invalid-exact={case['invalid_exact_like_count']} "
            f"rank<=1={case['rank_zero_or_one_quadruples']}",
            flush=True,
        )

    duplicate_mirage = all_row_report(12, 7, 1j * (2.0 + math.sqrt(3.0)))
    payload = {
        "tool": "scripts/exploration/search_complex_two_mode_cyclic.py",
        "trust": "NUMERICAL_EVIDENCE",
        "scope": "complex two-mode cyclic family; floating candidate enumeration",
        "interpretation": (
            "restricted-family numerical screen only; zero hits are not an exact "
            "obstruction and any hit requires exactification"
        ),
        "min_n": args.min_n,
        "max_n": args.max_n,
        "elapsed_sec": time.monotonic() - started,
        "total_cases": len(cases),
        "total_hits": total_hits,
        "rank_zero_or_one_quadruples": low_rank_quadruples,
        "invalid_exact_like_coefficients": invalid_exact_like_count,
        "n12_k7_duplicate_mirage": {
            "coefficient_exact": "I*(2+sqrt(3))",
            **duplicate_mirage,
        },
        "cases": cases,
    }
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=1, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"wrote {args.out}")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        print(
            f"summary: cases={len(cases)} hits={total_hits} "
            f"rank<=1 quadruples={low_rank_quadruples} elapsed={payload['elapsed_sec']:.1f}s"
        )
    return 0 if total_hits == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
