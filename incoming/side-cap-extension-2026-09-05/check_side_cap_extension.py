#!/usr/bin/env python3
"""Exact controls and algebra for the radius-window paper-proof candidate.

This does not formally verify the geometric two-star lemma or arbitrary-n
propagation. The finite row census is calibration, not the theorem's proof.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
Point = tuple[Q, Q]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def point(x: int | str | Q, y: int | str | Q) -> Point:
    return Q(x), Q(y)


def squared(a: Point, b: Point, y_weight: int = 1) -> Q:
    """Coordinates (x,sqrt(y_weight)*y); all arithmetic remains rational."""
    return (a[0] - b[0]) ** 2 + y_weight * (a[1] - b[1]) ** 2


def orientation(a: Point, b: Point, c: Point) -> Q:
    """Actual orientation is this value times positive sqrt(y_weight)."""
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def certify_polygon(points: list[Point], order: list[int], y_weight: int = 1) -> dict:
    n = len(points)
    require(n >= 3 and sorted(order) == list(range(n)), "invalid polygon order")
    require(y_weight > 0, "coordinate scaling must be positive")
    determinants = [orientation(points[order[i]], points[order[(i + 1) % n]], points[j])
                    for i in range(n) for j in range(n)
                    if j not in (order[i], order[(i + 1) % n])]
    require(min(determinants) > 0, "polygon is not strictly convex in supplied order")
    pairs = [squared(a, b, y_weight) for a, b in combinations(points, 2)]
    require(min(pairs) > 0, "coincident vertices")
    sides = [squared(points[order[i]], points[order[(i + 1) % n]], y_weight) for i in range(n)]
    caps = [Q(0)] * n
    for i, label in enumerate(order):
        caps[label] = min(sides[i - 1], sides[i])
    classes = [Counter(squared(p, q, y_weight) for j, q in enumerate(points) if i != j)
               for i, p in enumerate(points)]
    maximum = [max(row.values()) for row in classes]
    window = [max((count for distance, count in row.items() if distance <= caps[i]), default=0)
              for i, row in enumerate(classes)]
    return {
        "points_scaled": [[str(x), str(y)] for x, y in points],
        "y_scale_squared": y_weight,
        "counterclockwise_order": order,
        "orientation_checks": len(determinants),
        "minimum_scaled_orientation": str(min(determinants)),
        "distinct_pair_checks": len(pairs),
        "minimum_squared_separation": str(min(pairs)),
        "side_squared_lengths": [str(x) for x in sides],
        "local_caps_squared_by_label": [str(x) for x in caps],
        "maximum_multiplicity_by_label": maximum,
        "maximum_radius_window_multiplicity_by_label": window,
        "distance_classes": [{str(r): count for r, count in sorted(row.items())} for row in classes],
    }


def rotate_c3(p: Point) -> Point:
    x, y = p
    return -(x + 3 * y) / 2, (x - y) / 2


def seven_point_control() -> dict:
    points = [point(0, 0), point("5/13", "-12/13"), point("79/100", "-47/25"),
              point("4/5", "-3/5"), point("4/5", "3/5"),
              point("79/100", "47/25"), point("5/13", "12/13")]
    result = certify_polygon(points, list(range(7)))
    require(all(Q(x) >= 1 for x in result["side_squared_lengths"]), "side lower bound failed")
    witnesses = [i for i in range(1, 7) if squared(points[0], points[i]) == 1]
    require(witnesses == [1, 3, 4, 6], "four-witness identity failed")
    require(result["maximum_multiplicity_by_label"][0] == 4, "source multiplicity mismatch")
    require(result["maximum_radius_window_multiplicity_by_label"][0] == 4, "local control not sharp")
    result.update({"source": 0, "radius_squared": "1", "four_witnesses": witnesses,
                   "purpose": "The local upper bound four cannot be replaced by three.",
                   "is_erdos97_counterexample": False})
    require(any(m < 4 for m in result["maximum_multiplicity_by_label"]), "unexpected complete counterexample")
    return result


def five_point_control() -> dict:
    points = [point(0, 0), point("79/100", "-47/25"), point("4/5", "-3/5"),
              point("4/5", "3/5"), point("79/100", "47/25")]
    result = certify_polygon(points, list(range(5)))
    require(min(Q(x) for x in result["side_squared_lengths"]) == Q(36, 25), "subthreshold sides")
    witnesses = [i for i in range(1, 5) if squared(points[0], points[i]) == 1]
    require(witnesses == [2, 3], "subthreshold witnesses")
    result.update({"source": 0, "radius_squared": "1", "two_witnesses": witnesses,
                   "purpose": "The multiplicity bound two below the shortest boundary side is attained.",
                   "is_erdos97_counterexample": False})
    return result


def nine_point_control() -> dict:
    seeds = [point(1, 0), point("-5/7", "1/7"), point("-5/7", "-1/7")]
    points: list[Point] = []
    current = seeds[:]
    for _ in range(3):
        points.extend(current)
        current = [rotate_c3(p) for p in current]
    require(current == seeds, "C3 rotation is not order three")
    result = certify_polygon(points, [2, 6, 4, 5, 0, 7, 8, 3, 1], 3)
    distribution = Counter(result["maximum_multiplicity_by_label"])
    require(distribution == {2: 6, 4: 3}, "nine-point multiplicity distribution")
    witnesses = [i for i in range(1, 9) if squared(points[0], points[i], 3) == 3]
    require(witnesses == [1, 2, 3, 6], "source long-radius witnesses")
    require(Q(result["local_caps_squared_by_label"][0]) == Q(3, 7), "source cap mismatch")
    norms = [squared(point(0, 0), p, 3) for p in points]
    require([i for i, norm in enumerate(norms) if norm == max(norms)] == [0, 3, 6], "maximum-norm orbit")
    require(all(norms[i] == Q(4, 7) for i in [1, 2, 4, 5, 7, 8]), "supplier norms")
    require(all(m <= 3 for m in result["maximum_radius_window_multiplicity_by_label"]), "window control")
    result.update({"source": 0, "rich_radius_squared": "3", "rich_to_cap_squared_ratio": "7",
                   "four_witnesses": witnesses, "maximum_norm_orbit": [0, 3, 6],
                   "multiplicity_distribution": {str(k): v for k, v in sorted(distribution.items())},
                   "purpose": "Long-radius richness survives local goodness and a maximum-norm choice.",
                   "is_erdos97_counterexample": False})
    return result


def linear_sum(terms: Iterable[tuple[Q, dict[str, Q]]]) -> dict[str, Q]:
    result: dict[str, Q] = {}
    for coefficient, expression in terms:
        for variable, value in expression.items():
            result[variable] = result.get(variable, Q(0)) + coefficient * value
    return {key: value for key, value in result.items() if value}


def check_turn_identity() -> dict:
    expressions = [
        {"pi": Q(1), "theta": Q(-1), "alpha1": Q(-1), "beta3": Q(-1)},
        {"pi": Q(1, 2), "theta": Q(1, 2), "beta1": Q(-1), "alpha2": Q(-1)},
        {"pi": Q(1, 2), "theta": Q(1, 2), "beta2": Q(-1), "alpha3": Q(-1)},
        {"alpha1": Q(2), "beta1": Q(1), "pi": Q(-1)},
        {"alpha3": Q(1), "beta3": Q(2), "pi": Q(-1)},
    ]
    weights = [Q(2), Q(1), Q(1), Q(1), Q(1)]
    combined = linear_sum(zip(weights, expressions))
    target = {"pi": Q(1), "theta": Q(-1), "alpha2": Q(-1), "beta2": Q(-1)}
    require(combined == target, "turn coefficient identity")
    return {"positive_multipliers": [str(w) for w in weights],
            "combined_coefficients": {k: str(v) for k, v in sorted(combined.items())},
            "formal_geometry_proof": False}


def check_midpoint_terminal() -> dict:
    o, u, v = point(0, 0), point(1, 0), point("1/2", "1/2")
    w = (o[0] + u[0] - v[0], o[1] + u[1] - v[1])
    z = (o[0] + v[0] - u[0], o[1] + v[1] - u[1])
    for a, b in [(o, u), (o, v), (u, v), (o, w), (u, w), (o, z), (v, z)]:
        require(squared(a, b, 3) == 1, "equilateral terminal distance")
    require((w[0] + z[0], w[1] + z[1]) == (2 * o[0], 2 * o[1]), "midpoint equality")
    require(squared(w, z, 3) == 4, "terminal noncoincidence")
    # Separately check the affine identity in formal O,U,V coefficients.
    require(linear_sum([(Q(1), {"O": Q(1), "U": Q(1), "V": Q(-1)}),
                        (Q(1), {"O": Q(1), "U": Q(-1), "V": Q(1)}),
                        (Q(-2), {"O": Q(1)})]) == {}, "formal affine terminal")
    return {"seven_unit_distance_equalities": True, "W_plus_Z_equals_2O": True,
            "WZ_squared": "4", "O_strictly_between_W_and_Z": True}


def adjacent(n: int, a: int, b: int) -> bool:
    return (a - b) % n in (1, n - 1)


def calibrate_local_row_forcing(max_n: int = 32) -> dict:
    require(5 <= max_n <= 40, "calibration size must be in [5,40]")
    rows_tested = 0
    summaries = []
    for n in range(5, max_n + 1):
        survivors = []
        for row in combinations(range(1, n), 4):
            rows_tested += 1
            interior = [x for x in row if not adjacent(n, 0, x)]
            if all(adjacent(n, a, b) for a, b in combinations(interior, 2)):
                survivors.append(row)
        expected = sorted((1, j, j + 1, n - 1) for j in range(2, n - 2))
        require(sorted(survivors) == expected, f"local forcing mismatch at n={n}")
        summaries.append({"n": n, "admissible_rows": len(survivors)})
    return {"scope": "finite combinatorial calibration, not proof for arbitrary n",
            "fixed_center": 0, "rows_tested": rows_tested, "summaries": summaries,
            "mismatches": 0}


def build_report() -> dict:
    return {
        "schema": "erdos97.side_cap_extension.v1",
        "date": "2026-09-05",
        "status": "EXACT_CONTROLS_FOR_REVIEW_PENDING_RADIUS_WINDOW_THEOREM",
        "claim_scope": "No unrestricted Erdos97 proof or counterexample; no finite-bound promotion.",
        "geometric_dependency": "../radius-descent-n11-2026-09-05/proofs.md, Sections 1-2",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "note_sha256": hashlib.sha256((ROOT / "README.md").read_bytes()).hexdigest(),
        "turn_identity": check_turn_identity(),
        "midpoint_terminal": check_midpoint_terminal(),
        "local_row_calibration": calibrate_local_row_forcing(),
        "seven_point_control": seven_point_control(),
        "five_point_subthreshold_control": five_point_control(),
        "nine_point_control": nine_point_control(),
        "repository_wide_CI_run_by_this_checker": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()
    report = build_report()
    destination = ROOT / "side_cap_report.json"
    if args.write:
        destination.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    if args.check:
        require(json.loads(destination.read_text()) == report, "stored report mismatch; regenerate explicitly")
    print(json.dumps({"status": "passed", "mode": "write" if args.write else "check" if args.check else "compute",
                      "rows_calibrated": report["local_row_calibration"]["rows_tested"],
                      "seven_point_source_multiplicity": 4,
                      "nine_point_multiplicity_distribution": report["nine_point_control"]["multiplicity_distribution"],
                      "scope": report["claim_scope"]}, sort_keys=True))


if __name__ == "__main__":
    main()
