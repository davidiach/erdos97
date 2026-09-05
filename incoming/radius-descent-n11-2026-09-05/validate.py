#!/usr/bin/env python3
"""Exact packet checks. This is not a regeneration of the n=11 search."""
from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction as Q
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COLUMNS = ["slice", "nodes", "trials", "pair_dead", "turn_prunes", "zero_prunes", "inverse_prunes"]
EXPECTED = [114344315, 114344105, 206595, 59064768, 7065757, 40525345]
SOURCE_SHA256 = "c54766f191a022fbc0f8f653266f9373ef02fe8f4de37fcd342848a06877ab48"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def det(matrix: list[list[Q]]) -> Q:
    a = [row[:] for row in matrix]
    result = Q(1)
    for col in range(len(a)):
        pivot = next((i for i in range(col, len(a)) if a[i][col]), None)
        if pivot is None:
            return Q(0)
        if pivot != col:
            a[pivot], a[col] = a[col], a[pivot]
            result = -result
        value = a[col][col]
        result *= value
        for row in range(col + 1, len(a)):
            scale = a[row][col] / value
            for j in range(col + 1, len(a)):
                a[row][j] -= scale * a[col][j]
            a[row][col] = Q(0)
    return result


def squared(p: tuple[Q, Q], q: tuple[Q, Q], y_weight: int = 1) -> Q:
    return (p[0] - q[0]) ** 2 + y_weight * (p[1] - q[1]) ** 2


def strict_convex(points: list[tuple[Q, Q]]) -> bool:
    n = len(points)
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        for j, c in enumerate(points):
            if j in (i, (i + 1) % n):
                continue
            cross = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
            if cross <= 0:
                return False
    return True


def check_turn_identity() -> dict:
    # Basis: pi, theta, alpha1, beta1, alpha2, beta2, alpha3, beta3.
    terms = [
        [1, -1, -1, 0, 0, 0, 0, -1],
        [Q(1, 2), Q(1, 2), 0, -1, -1, 0, 0, 0],
        [Q(1, 2), Q(1, 2), 0, 0, 0, -1, -1, 0],
        [-1, 0, 2, 1, 0, 0, 0, 0],
        [-1, 0, 0, 0, 0, 0, 1, 2],
    ]
    multipliers = [2, 1, 1, 1, 1]
    combined = [sum(Q(w) * term[j] for w, term in zip(multipliers, terms)) for j in range(8)]
    target = [1, -1, 0, 0, -1, -1, 0, 0]
    require(combined == target, "two-star turn identity failed")
    return {"multipliers": multipliers, "coefficient_residual": [0] * 8}


def check_geometry_controls() -> dict:
    kite = [(Q(0), Q(0)), (Q(5, 13), Q(-12, 13)), (Q(1), Q(0)), (Q(5, 13), Q(12, 13))]
    require(strict_convex(kite), "kite convexity")
    for center, radius2 in [(0, Q(1)), (2, Q(16, 13))]:
        for neighbor in [(center - 1) % 4, (center + 1) % 4]:
            require(squared(kite[center], kite[neighbor]) == radius2, "kite side")
    require(squared(kite[0], kite[2]) == 1, "kite short chord")

    square = [(Q(0), Q(0)), (Q(1), Q(0)), (Q(1), Q(1)), (Q(0), Q(1))]
    require(strict_convex(square), "square convexity")
    require(all(sum(squared(p, q) == 1 for q in square) == 2 for p in square), "square witnesses")

    # Actual coordinates are (x, sqrt(3)*y); orientation has positive sqrt(3) factor.
    hexagon = [(Q(1), Q(0)), (Q(1, 2), Q(1, 2)), (Q(-1, 2), Q(1, 2)),
               (Q(-1), Q(0)), (Q(-1, 2), Q(-1, 2)), (Q(1, 2), Q(-1, 2))]
    require(strict_convex(hexagon), "hexagon convexity")
    require(all(squared(hexagon[i], hexagon[(i + 1) % 6], 3) == 1 for i in range(6)), "hexagon sides")
    require(all(squared(hexagon[i], hexagon[j], 3) == 3 for i, j in itertools.combinations([0, 2, 4], 2)),
            "hexagon alternate distances")
    return {"unequal_radius_kite": True, "independence_required_square": True, "side_cap_required_hexagon": True}


def check_metric_control() -> dict:
    rows = [(3, 4), (0, 4), (0, 1), (1, 2), (2, 3)]
    radii = [100 + i for i in range(5)]
    distance = [[0] * 5 for _ in range(5)]
    for i, witnesses in enumerate(rows):
        for j in witnesses:
            require(distance[i][j] == 0, "duplicate directed pair")
            distance[i][j] = distance[j][i] = radii[i]
    require(all(distance[i][j] > 0 for i, j in itertools.combinations(range(5), 2)), "missing pair")
    for i, j, k in itertools.permutations(range(5), 3):
        require(distance[i][j] < distance[i][k] + distance[k][j], "triangle inequality")
    edges = [(i, j) for i, j in itertools.combinations(range(5), 2) if distance[i][j] <= min(radii[i], radii[j])]
    require(edges == [(0, 3), (0, 4), (1, 4)], "threshold graph")
    order = [3, 0, 4, 1, 2]
    position = {v: i for i, v in enumerate(order)}
    for e, f in itertools.combinations(edges, 2):
        a, b = sorted(position[v] for v in e)
        c, d = sorted(position[v] for v in f)
        require(not (a < c < b < d or c < a < d < b), "crossing in control")
    parent = list(range(5))
    def root(v: int) -> int:
        while parent[v] != v:
            v = parent[v]
        return v
    for a, b in edges:
        require(root(a) != root(b), "cycle in control")
        parent[root(a)] = root(b)
    gram = [[Q(distance[0][i] ** 2 + distance[0][j] ** 2 - distance[i][j] ** 2, 2)
             for j in range(1, 5)] for i in range(1, 5)]
    minors = [det([row[:k] for row in gram[:k]]) for k in range(1, 5)]
    expected = [Q(10201), Q(320464415, 4), Q(2227125383159, 4), Q(3647257216075788)]
    require(minors == expected and all(x > 0 for x in minors), "Gram minors")
    return {"forest_edges": edges, "positive_gram_minors": [str(x) for x in minors], "affine_dimension": 4,
            "planar_counterexample": False, "two_star_excludes_locally_bounded_extension_at": 0}


def validate() -> dict:
    payload = json.loads((ROOT / "results.json").read_text())
    require(payload["schema"] == "erdos97.radius_descent_n11.v1", "schema mismatch")
    sha = hashlib.sha256((ROOT / "exact_search.cpp").read_bytes()).hexdigest()
    require(sha == SOURCE_SHA256 == payload["source_sha256"], "search source hash mismatch")
    require(payload["columns"] == COLUMNS, "counter columns mismatch")
    table = payload["n11_slices"]
    require(len(table) == 210, "wrong number of slices")
    require([row[0] for row in table] == list(range(210)), "slice coverage or order mismatch")
    for row in table:
        require(len(row) == len(COLUMNS) and all(type(x) is int and x >= 0 for x in row), "invalid counters")
        require(row[1] == row[2] + 1, "slice node/trial identity")
    aggregate = [sum(row[j] for row in table) for j in range(1, len(COLUMNS))]
    require(aggregate == EXPECTED, "aggregate mismatch")
    require(payload["all_n11_runs_complete"] is True and payload["n11_survivors"] == 0, "run status mismatch")
    require(payload["aggregate"] == dict(zip(COLUMNS[1:], EXPECTED)), "stored aggregate mismatch")
    return {"scope": "stored-artifact consistency and exact controls, not exhaustive regeneration",
            "n11_slices": 210, "n11_nodes": aggregate[0], "source_sha256": sha,
            "turn_identity": check_turn_identity(), "geometry_controls": check_geometry_controls(),
            "forest_only_metric_control": check_metric_control()}


if __name__ == "__main__":
    print(json.dumps(validate(), indent=2))
