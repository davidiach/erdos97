#!/usr/bin/env python3
"""Dynamic construction search in a complex three-mode cyclic family.

The family is

    z_i = w**i + c*w**(k*i) + d*w**(ell*i),

where ``w = exp(2*pi*I/n)`` and ``c,d`` are complex.  Four real parameters
remain after fixing the leading coefficient.  At every alternating-search
cycle each center selects its minimum-spread four-distance window, then a
nonlinear least-squares step refines the four coefficients for those rows.

Every output is numerical construction evidence only.  A hit must be rebuilt
in exact cyclotomic arithmetic and supplied with exact equality, distinctness,
and strict-convexity certificates before it is a counterexample.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import math
import time
from concurrent.futures import ProcessPoolExecutor
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from scipy.optimize import least_squares


@dataclasses.dataclass(frozen=True)
class SearchConfig:
    pair_floor: float = 2.0e-3
    side_floor: float = 2.0e-6
    weight_equalities: float = 1.0
    weight_pair: float = 25.0
    weight_side: float = 40.0
    candidate_tolerance: float = 1.0e-10


def points(
    n: int, k: int, ell: int, coefficient_c: complex, coefficient_d: complex
) -> np.ndarray:
    indices = np.arange(n)
    angles = 2.0j * math.pi * indices / float(n)
    values = (
        np.exp(angles)
        + coefficient_c * np.exp(k * angles)
        + coefficient_d * np.exp(ell * angles)
    )
    return np.column_stack((values.real, values.imag))


def lifted_distance_rows(n: int, k: int, ell: int, center: int) -> np.ndarray:
    """Return exact-form float coefficients for all distances from ``center``.

    Columns multiply

      [1, |c|^2, |d|^2, Re(c), Im(c), Re(d), Im(d),
       Re(c*conj(d)), Im(c*conj(d))].
    """

    indices = np.arange(n)
    roots = np.exp(2.0j * math.pi * indices / float(n))
    rows = []
    for shift in range(1, n):
        target = (center + shift) % n
        a = roots[target] - roots[center]
        b = roots[(k * target) % n] - roots[(k * center) % n]
        e = roots[(ell * target) % n] - roots[(ell * center) % n]
        gamma_c = b * np.conjugate(a)
        gamma_d = e * np.conjugate(a)
        gamma_cross = b * np.conjugate(e)
        rows.append(
            [
                float(abs(a) ** 2),
                float(abs(b) ** 2),
                float(abs(e) ** 2),
                float(2.0 * gamma_c.real),
                float(-2.0 * gamma_c.imag),
                float(2.0 * gamma_d.real),
                float(-2.0 * gamma_d.imag),
                float(2.0 * gamma_cross.real),
                float(-2.0 * gamma_cross.imag),
            ]
        )
    return np.asarray(rows, dtype=float)


def lifted_variables(coefficient_c: complex, coefficient_d: complex) -> np.ndarray:
    cross = coefficient_c * np.conjugate(coefficient_d)
    return np.asarray(
        [
            1.0,
            abs(coefficient_c) ** 2,
            abs(coefficient_d) ** 2,
            coefficient_c.real,
            coefficient_c.imag,
            coefficient_d.real,
            coefficient_d.imag,
            cross.real,
            cross.imag,
        ]
    )


def squared_distances(point_array: np.ndarray) -> np.ndarray:
    delta = point_array[:, None, :] - point_array[None, :, :]
    return np.einsum("ijk,ijk->ij", delta, delta)


def best_window(row: np.ndarray) -> tuple[float, tuple[int, ...]]:
    order = np.argsort(row, kind="stable")
    ordered = row[order]
    spreads = ordered[3:] - ordered[:-3]
    start = int(np.argmin(spreads))
    selected_values = ordered[start : start + 4]
    relative = float(spreads[start]) / max(
        float(np.mean(selected_values)), np.finfo(float).tiny
    )
    return relative, tuple(int(value) for value in order[start : start + 4])


def assign_windows(point_array: np.ndarray) -> tuple[tuple[int, ...], ...]:
    distance_matrix = squared_distances(point_array)
    assignments = []
    for center in range(len(point_array)):
        others = np.arange(len(point_array))[np.arange(len(point_array)) != center]
        _relative, local = best_window(distance_matrix[center, others])
        assignments.append(tuple(int(others[index]) for index in local))
    return tuple(assignments)


def convexity_data(point_array: np.ndarray) -> dict[str, object]:
    n = len(point_array)
    centroid = np.mean(point_array, axis=0)
    angles = np.arctan2(
        point_array[:, 1] - centroid[1], point_array[:, 0] - centroid[0]
    )
    order = np.argsort(angles, kind="stable")
    polygon = point_array[order]
    edge = np.roll(polygon, -1, axis=0) - polygon
    all_sides = []
    for index in range(n):
        delta = polygon - polygon[index]
        side = edge[index, 0] * delta[:, 1] - edge[index, 1] * delta[:, 0]
        mask = np.ones(n, dtype=bool)
        mask[index] = False
        mask[(index + 1) % n] = False
        all_sides.extend(float(value) for value in side[mask])

    distance_matrix = squared_distances(point_array)
    diameter_sq = float(np.max(distance_matrix))
    off_diagonal = distance_matrix + np.diag(np.full(n, np.inf))
    scale = max(diameter_sq, np.finfo(float).tiny)
    side_normalized = np.asarray(all_sides) / scale
    pair_normalized = math.sqrt(float(np.min(off_diagonal)) / scale)
    return {
        "order": tuple(int(value) for value in order),
        "side_normalized": side_normalized,
        "min_side_normalized": float(np.min(side_normalized)),
        "min_pair_normalized": pair_normalized,
        "strictly_convex": bool(
            np.min(side_normalized) > 0.0 and pair_normalized > 1.0e-10
        ),
    }


def evaluate(
    n: int, k: int, ell: int, vector: np.ndarray, config: SearchConfig
) -> dict[str, object]:
    coefficient_c = complex(float(vector[0]), float(vector[1]))
    coefficient_d = complex(float(vector[2]), float(vector[3]))
    point_array = points(n, k, ell, coefficient_c, coefficient_d)
    distance_matrix = squared_distances(point_array)
    windows = []
    maximum = 0.0
    for center in range(n):
        others = np.arange(n)[np.arange(n) != center]
        relative, local = best_window(distance_matrix[center, others])
        witnesses = tuple(int(others[index]) for index in local)
        maximum = max(maximum, relative)
        windows.append(
            {
                "center": center,
                "witnesses": witnesses,
                "relative_spread": relative,
            }
        )
    convexity = convexity_data(point_array)
    return {
        "coefficient_c": [coefficient_c.real, coefficient_c.imag],
        "coefficient_d": [coefficient_d.real, coefficient_d.imag],
        "max_relative_spread": maximum,
        "strictly_convex": convexity["strictly_convex"],
        "min_side_normalized": convexity["min_side_normalized"],
        "min_pair_normalized": convexity["min_pair_normalized"],
        "cyclic_order": convexity["order"],
        "candidate": bool(
            convexity["strictly_convex"]
            and convexity["min_pair_normalized"] >= config.pair_floor
            and convexity["min_side_normalized"] >= config.side_floor
            and maximum <= config.candidate_tolerance
        ),
        "windows": windows,
    }


def report_key(
    report: dict[str, object], config: SearchConfig
) -> tuple[int, float, float, float]:
    pair_deficit = max(
        0.0,
        (config.pair_floor - float(report["min_pair_normalized"])) / config.pair_floor,
    )
    side_deficit = max(
        0.0,
        (config.side_floor - float(report["min_side_normalized"])) / config.side_floor,
    )
    return (
        0 if report["strictly_convex"] else 1,
        max(pair_deficit, side_deficit),
        float(report["max_relative_spread"]),
        -float(report["min_side_normalized"]),
    )


def residuals(
    vector: np.ndarray,
    n: int,
    k: int,
    ell: int,
    assignments: Sequence[Sequence[int]],
    config: SearchConfig,
) -> np.ndarray:
    coefficient_c = complex(float(vector[0]), float(vector[1]))
    coefficient_d = complex(float(vector[2]), float(vector[3]))
    point_array = points(n, k, ell, coefficient_c, coefficient_d)
    distance_matrix = squared_distances(point_array)
    parts = []
    for center, witnesses in enumerate(assignments):
        values = distance_matrix[center, list(witnesses)]
        mean = max(float(np.mean(values)), np.finfo(float).tiny)
        parts.extend(config.weight_equalities * (values - np.mean(values)) / mean)

    convexity = convexity_data(point_array)
    parts.extend(
        config.weight_side
        * np.maximum(0.0, config.side_floor - convexity["side_normalized"])
    )
    parts.append(
        config.weight_pair
        * max(0.0, config.pair_floor - convexity["min_pair_normalized"])
    )
    return np.asarray(parts, dtype=float)


def refine(
    n: int,
    k: int,
    ell: int,
    start: np.ndarray,
    config: SearchConfig,
    max_cycles: int,
) -> tuple[np.ndarray, dict[str, object]]:
    vector = np.asarray(start, dtype=float)
    best_vector = vector.copy()
    best_report = evaluate(n, k, ell, vector, config)
    previous: set[tuple[tuple[int, ...], ...]] = set()
    for _ in range(max_cycles):
        point_array = points(
            n,
            k,
            ell,
            complex(float(vector[0]), float(vector[1])),
            complex(float(vector[2]), float(vector[3])),
        )
        assignments = assign_windows(point_array)
        result = least_squares(
            residuals,
            vector,
            args=(n, k, ell, assignments, config),
            method="trf",
            max_nfev=500,
            xtol=1.0e-12,
            ftol=1.0e-12,
            gtol=1.0e-12,
        )
        vector = result.x
        report = evaluate(n, k, ell, vector, config)
        if report_key(report, config) < report_key(best_report, config):
            best_vector = vector.copy()
            best_report = report
        if assignments in previous:
            break
        previous.add(assignments)
    return best_vector, best_report


def starts(
    n: int,
    k: int,
    ell: int,
    restarts: int,
    seed: int,
) -> Iterable[np.ndarray]:
    rng = np.random.default_rng(seed + 1009 * k + 9176 * ell)
    emitted = 0
    if emitted < restarts:
        yield np.zeros(4)
        emitted += 1
    if k == 7 and n == 12 and emitted < restarts:
        for sign in (-1.0, 1.0):
            if emitted >= restarts:
                break
            yield np.asarray([0.0, sign * (2.0 + math.sqrt(3.0)), 1.0e-3, 0.0])
            emitted += 1
    random_restarts = restarts - emitted
    for slot in range(random_restarts):
        fraction = slot / max(1, random_restarts - 1)
        scale = 0.03 * (5.0 / 0.03) ** fraction
        yield rng.normal(0.0, scale, size=4)


def search_cell(
    n: int,
    k: int,
    ell: int,
    restarts: int,
    seed: int,
    max_cycles: int,
    config: SearchConfig,
) -> dict[str, object]:
    started = time.monotonic()
    best = None
    candidates = []
    for restart, start in enumerate(starts(n, k, ell, restarts, seed)):
        _vector, report = refine(n, k, ell, start, config, max_cycles)
        report = {"restart": restart, **report}
        if report["candidate"]:
            candidates.append(report)
        if best is None or report_key(report, config) < report_key(best, config):
            best = report
    assert best is not None
    return {
        "n": n,
        "k": k,
        "ell": ell,
        "restarts": restarts,
        "elapsed_sec": time.monotonic() - started,
        "best": best,
        "candidates": candidates,
    }


def mode_pairs(n: int) -> Iterable[tuple[int, int]]:
    return combinations(range(2, n), 2)


def run_search_task(task: tuple[int, int, int, int, int, int]) -> dict[str, object]:
    n, k, ell, restarts, seed, max_cycles = task
    return search_cell(
        n,
        k,
        ell,
        restarts=restarts,
        seed=seed,
        max_cycles=max_cycles,
        config=SearchConfig(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int)
    parser.add_argument("--k", type=int)
    parser.add_argument("--ell", type=int)
    parser.add_argument("--min-n", type=int, default=12)
    parser.add_argument("--max-n", type=int, default=18)
    parser.add_argument("--restarts", type=int, default=12)
    parser.add_argument("--max-cycles", type=int, default=8)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--seed", type=int, default=20260722)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.restarts < 1:
        parser.error("--restarts must be positive")
    if args.max_cycles < 1:
        parser.error("--max-cycles must be positive")
    if args.workers < 1:
        parser.error("--workers must be positive")

    if args.n is not None:
        if args.k is None or args.ell is None:
            parser.error("--n requires --k and --ell")
        if args.n < 5 or not (2 <= args.k < args.n) or not (2 <= args.ell < args.n):
            parser.error("require n >= 5 and 2 <= k,ell < n")
        if args.k == args.ell:
            parser.error("--k and --ell must be distinct")
        cells = [(args.n, min(args.k, args.ell), max(args.k, args.ell))]
    else:
        if args.min_n < 5 or args.max_n < args.min_n:
            parser.error("require 5 <= min-n <= max-n")
        cells = [
            (n, k, ell)
            for n in range(args.min_n, args.max_n + 1)
            for k, ell in mode_pairs(n)
        ]

    tasks = [
        (n, k, ell, args.restarts, args.seed + 100_000 * index, args.max_cycles)
        for index, (n, k, ell) in enumerate(cells)
    ]
    if args.workers == 1:
        records = [run_search_task(task) for task in tasks]
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            records = list(executor.map(run_search_task, tasks, chunksize=1))

    hit_count = 0
    for record in records:
        hit_count += len(record["candidates"])
        best = record["best"]
        n, k, ell = record["n"], record["k"], record["ell"]
        print(
            f"n={n} modes=({k},{ell}) "
            f"spread={float(best['max_relative_spread']):.3e} "
            f"side={float(best['min_side_normalized']):.3e} "
            f"pair={float(best['min_pair_normalized']):.3e} "
            f"hits={len(record['candidates'])}",
            flush=True,
        )

    payload = {
        "tool": "scripts/exploration/search_complex_three_mode_cyclic.py",
        "trust": "NUMERICAL_EVIDENCE",
        "interpretation": (
            "construction screen only; every hit requires exact cyclotomic "
            "equality, distinctness, and strict-convexity certificates"
        ),
        "seed": args.seed,
        "restarts": args.restarts,
        "max_cycles": args.max_cycles,
        "workers": args.workers,
        "cell_count": len(records),
        "hit_count": hit_count,
        "cells": records,
    }
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=1, sort_keys=True) + "\n", encoding="utf-8"
        )
        print(f"wrote {args.out}")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    return 0 if hit_count == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
