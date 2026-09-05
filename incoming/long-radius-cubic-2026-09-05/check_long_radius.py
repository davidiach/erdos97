#!/usr/bin/env python3
"""Exact controls for review-pending long-radius theorems, not a proof of #97."""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
Point = tuple[Q, Q]  # Actual complex coordinate x + i*sqrt(3)*y.
Polynomial = dict[tuple[int, ...], Q]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def clean(p: Polynomial) -> Polynomial:
    return {key: value for key, value in p.items() if value}


def add(a: Polynomial, b: Polynomial) -> Polynomial:
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, Q(0)) + value
    return clean(result)


def scale(a: Polynomial, c: int | Q) -> Polynomial:
    return clean({key: c * value for key, value in a.items()})


def multiply(a: Polynomial, b: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for x, c in a.items():
        for y, d in b.items():
            require(len(x) == len(y), "polynomial dimension mismatch")
            key = tuple(v + w for v, w in zip(x, y))
            result[key] = result.get(key, Q(0)) + c * d
    return clean(result)


def power(a: Polynomial, k: int) -> Polynomial:
    require(k >= 1, "positive power required")
    result = a
    for _ in range(k - 1):
        result = multiply(result, a)
    return result


def algebra_checks() -> dict:
    # Laurent monomials in u.
    x = {(1,): Q(1), (-1,): Q(-2)}
    v = {(-2,): Q(1), (0,): Q(-1)}
    left = multiply({(-2,): Q(1)}, add({(0,): Q(4)}, scale(power(x, 2), -1)))
    right = add({(0,): Q(3)}, scale(power(v, 2), -4))
    require(left == right == {(0,): -1, (-2,): 8, (-4,): -4}, "unit norm identity")
    # Variables s,t,U, where U = Re(a^3*conj(b^3)).
    s, t, u = {(1, 0, 0): Q(1)}, {(0, 1, 0): Q(1)}, {(0, 0, 1): Q(1)}
    ts = add(t, scale(s, -2))
    lhs = add(add(power(ts, 3), scale(multiply(multiply(s, t), ts), -3)), scale(u, -2))
    rhs = add(add(add(power(s, 3), power(t, 3)), scale(u, -2)),
              scale(multiply(s, power(add(s, scale(t, -1)), 2)), -9))
    require(lhs == rhs, "cubic quotient identity")
    require(Q(3, 4) < 1, "conjugate bound is not strict")
    return {
        "unit_identity_residual": {},
        "unit_identity_laurent_coefficients": {str(k[0]): str(value) for k, value in sorted(left.items())},
        "conjugate_squared_bound": "3/4",
        "cubic_identity_residual": {},
        "cubic_identity_coefficients_s_t_U": {','.join(map(str, k)): str(value) for k, value in sorted(lhs.items())},
        "algebraic_integer_norm_argument_formalized": False,
    }


def rotate(p: Point) -> Point:
    x, y = p
    return -(x + 3 * y) / 2, (x - y) / 2


def cube(p: Point) -> Point:
    x, y = p
    return x**3 - 9*x*y*y, 3*x*x*y - 3*y**3


def norm_squared(p: Point) -> Q:
    return p[0]**2 + 3*p[1]**2


def distance_squared(p: Point, q: Point) -> Q:
    return norm_squared((p[0] - q[0], p[1] - q[1]))


def cross(a: Point, b: Point, c: Point) -> Q:
    # Actual signed area differs by the positive factor sqrt(3).
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def hull_order(points: list[Point]) -> list[int]:
    require(len(set(points)) == len(points), "duplicate points")
    indices = sorted(range(len(points)), key=lambda i: points[i])
    lower: list[int] = []
    upper: list[int] = []
    for i in indices:
        while len(lower) >= 2 and cross(points[lower[-2]], points[lower[-1]], points[i]) <= 0:
            lower.pop()
        lower.append(i)
    for i in reversed(indices):
        while len(upper) >= 2 and cross(points[upper[-2]], points[upper[-1]], points[i]) <= 0:
            upper.pop()
        upper.append(i)
    return lower[:-1] + upper[:-1]


def certify_convex(points: list[Point]) -> dict:
    require(len(points) >= 3, "at least three points required")
    order = hull_order(points)
    require(len(order) == len(points), "point set is not strictly convex")
    n = len(points)
    areas = [cross(points[order[i]], points[order[(i+1) % n]], points[j])
             for i in range(n) for j in range(n) if j not in (order[i], order[(i+1) % n])]
    require(min(areas) > 0, "supporting-edge check failed")
    origin_areas = [cross(points[order[i]], points[order[(i+1) % n]], (Q(0), Q(0))) for i in range(n)]
    return {
        "number_of_points": n,
        "points_scaled": [[str(x), str(y)] for x, y in points],
        "order": order,
        "supporting_edge_checks": len(areas),
        "minimum_scaled_area": str(min(areas)),
        "minimum_squared_separation": str(min(distance_squared(a, b) for a, b in combinations(points, 2))),
        "origin_strictly_inside_hull": min(origin_areas) > 0,
        "origin_outside_hull": min(origin_areas) < 0,
    }


def expand_orbits(representatives: list[Point]) -> list[Point]:
    points: list[Point] = []
    layer = representatives[:]
    for _ in range(3):
        points.extend(layer)
        layer = [rotate(z) for z in layer]
    require(layer == representatives, "rotation not order three")
    return points


def seed_cycle_control() -> dict:
    z = [(Q(1), Q(0)), (Q(-26503, 21854), Q(8991, 21854)),
         (Q(-44665, 37058), Q(10753, 37058))]
    points = expand_orbits(z)
    polygon = certify_convex(points)
    edges = [(0, 1, 1), (1, 2, 1), (2, 0, 0)]
    squares = [norm_squared(p) for p in z]
    certificates = []
    for i, j, k in edges:
        target = z[j]
        for _ in range(k):
            target = rotate(target)
        require(distance_squared(z[i], target) == 3*squares[i], "seed arrow equality")
        require(distance_squared(cube(z[i]), cube(z[j])) == 9*squares[i]*(squares[i]-squares[j])**2,
                "seed cubic edge identity")
        dot = z[i][0]*target[0] + 3*z[i][1]*target[1]
        twice_cosine_double_angle = 4*dot**2/(squares[i]*squares[j])-2
        require(twice_cosine_double_angle.denominator != 1, "irrational-angle certificate failed")
        certificates.append({"source": i, "target": j, "rotation": k,
                             "two_cos_two_theta": str(twice_cosine_double_angle),
                             "rational_noninteger": True})
    profiles = [Counter(distance_squared(p, q) for j, q in enumerate(points) if i != j)
                for i, p in enumerate(points)]
    maxima = [max(row.values()) for row in profiles]
    require(maxima == [3]*9, "seed multiplicity profile")
    quotient = certify_convex([cube(p) for p in z])
    require(polygon["origin_strictly_inside_hull"] and quotient["origin_outside_hull"], "origin-location control")
    return {"polygon": polygon, "cube_quotient": quotient,
            "squared_norms": [str(s) for s in squares], "selected_cycle": certificates,
            "all_distance_classes": [{str(d): c for d, c in sorted(row.items())} for row in profiles],
            "maximum_multiplicity": maxima, "is_erdos97_counterexample": False,
            "purpose": "Exact convex irrational-angle cycle; commensurability cannot be removed."}


def power_fixture(m: int = 7) -> dict:
    require(m >= 3, "at least three orbits required")
    z = []
    for j in range(m):
        t = Q(j, m)
        z.append((1-Q(3, 2)*t*t, 2*t-Q(3, 2)*t*t))
    original = certify_convex(expand_orbits(z))
    quotient = certify_convex([cube(p) for p in z])
    require(len(set(norm_squared(p) for p in z)) > 1, "fixture should have varying norms")
    for p in z:
        require(cube(rotate(p)) == cube(p), "cube not rotation invariant")
        require(norm_squared(cube(p)) == norm_squared(p)**3, "cube modulus identity")
    return {"original": original, "quotient": quotient, "varying_norms": True,
            "scope": "finite exact fixture, not the arbitrary-size geometric proof"}


def nonconverse_control() -> dict:
    z = [(Q(1), Q(0)), (Q(2), Q(0)), (Q(0), Q(1))]
    original = expand_orbits(z)
    quotient = certify_convex([cube(p) for p in z])
    outer = [z[1], rotate(z[1]), rotate(rotate(z[1]))]
    coefficients = [Q(2, 3), Q(1, 6), Q(1, 6)]
    combination = tuple(sum(c*p[j] for c, p in zip(coefficients, outer)) for j in range(2))
    require(combination == z[0] and all(c > 0 for c in coefficients), "interior convex combination")
    require(len(hull_order(original)) < len(original), "nonconverse control unexpectedly convex")
    return {"cube_quotient": quotient, "original_hull_vertices": len(hull_order(original)),
            "original_points": len(original), "strict_interior_coefficients": [str(c) for c in coefficients],
            "purpose": "Convexity of the cube quotient is not sufficient for convexity before cubing."}


def downward_shortcuts(rows: list[list[int]]) -> list[dict]:
    """Labels here are increasing STRICT radial ranks, not boundary ranks."""
    n = len(rows)
    require(all(len(row) == len(set(row)) and all(type(j) is int and 0 <= j < n and i != j for j in row)
                for i, row in enumerate(rows)), "invalid graph")
    require(all(i not in rows[j] for i, row in enumerate(rows) for j in row), "reciprocal edge")
    neighbors = [set() for _ in rows]
    for i, row in enumerate(rows):
        for j in row:
            neighbors[i].add(j)
            neighbors[j].add(i)
    found = []
    for high, row in enumerate(rows):
        for low in row:
            if low >= high:
                continue
            # Increasing paths excluding the direct low--high edge.
            paths = {low: [low]}
            for a in range(low, high):
                if a not in paths:
                    continue
                for b in sorted(neighbors[a]):
                    if not (a < b <= high) or (a == low and b == high):
                        continue
                    if b not in paths:
                        paths[b] = paths[a] + [b]
            if high in paths:
                found.append({"downward_edge": [high, low], "increasing_path": paths[high]})
    return found


def graph_checks() -> dict:
    control = [[4, 5], [4, 5], [0, 1], [0, 1], [2, 3], [2, 3]]
    require(not downward_shortcuts(control), "six-label control fails no-shortcut test")
    rejected = [[1], [2], [0]]
    obstruction = downward_shortcuts(rejected)
    require(obstruction == [{"downward_edge": [2, 0], "increasing_path": [0, 1, 2]}], "shortcut not detected")
    seed_radial_order = [[2], [0], [1]]
    require(not downward_shortcuts(seed_radial_order), "genuine cycle radial order wrongly rejected")
    return {"six_label_control": control, "outdegrees": [2]*6, "downward_shortcuts": [],
            "euclidean_realization_claimed": False,
            "rejected_control": {"rows": rejected, "obstructions": obstruction},
            "seed_cycle_in_increasing_radial_order": seed_radial_order}


def build_report() -> dict:
    return {"schema": "erdos97.long_radius_cubic.v1", "date": "2026-09-05",
            "status": "EXACT_CONTROLS_FOR_REVIEW_PENDING_THEOREMS",
            "claim_scope": "Commensurable own-side cycle obstruction and necessary quotient conditions; not a solution of Erdos97.",
            "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "note_sha256": hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest(),
            "algebra": algebra_checks(), "irrational_seed_cycle": seed_cycle_control(),
            "power_fixture": power_fixture(), "nonconverse": nonconverse_control(),
            "radial_path_controls": graph_checks(), "repository_wide_CI_run": False}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    path = ROOT / "report.json"
    if args.write:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.check:
        require(json.loads(path.read_text()) == report, "stored report mismatch")
    print(json.dumps({"status": "passed", "mode": "write" if args.write else "check" if args.check else "compute",
                      "seed_points": 9, "seed_maximum_multiplicity": 3, "irrational_edge_certificates": 3,
                      "power_fixture_points": 21, "cube_quotient_points": 7,
                      "six_label_two_out_graph_survives_path_rule": True,
                      "scope": report["claim_scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
