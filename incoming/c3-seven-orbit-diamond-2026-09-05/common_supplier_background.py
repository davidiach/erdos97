#!/usr/bin/env python3
"""Replay exact local certificates, finite graph coverage, and geometric controls.

No solver is imported. The general Erdős problem and other-radius C3 rows
are outside the checked claim. Geometry-to-model soundness is documented in
README.md and remains subject to independent mathematical review.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path

from core import (AngleModel, MetricModel, all_cases, check_rational_feasible,
                  decode_case, require, verify_certificate)

ROOT = Path(__file__).resolve().parent
Point = tuple[Q, Q]  # Actual Cartesian coordinates are (x, sqrt(3)*y).


def rotate(p: Point) -> Point:
    x, y = p
    return -(x + 3 * y) / 2, (x - y) / 2


def norm2(p: Point) -> Q:
    return p[0] ** 2 + 3 * p[1] ** 2


def distance2(p: Point, q: Point) -> Q:
    return norm2((p[0] - q[0], p[1] - q[1]))


def cube(p: Point) -> Point:
    x, y = p
    return x ** 3 - 9 * x * y * y, 3 * x * x * y - 3 * y ** 3


def cross(a: Point, b: Point, c: Point) -> Q:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def geometric_control(representatives: list[Point], arrows: list[tuple[int, int, int]],
                      ranks: list[int], angle_vector: list[str]) -> dict:
    m = len(representatives)
    points = representatives + [rotate(p) for p in representatives] + [rotate(rotate(p)) for p in representatives]
    n = len(points)
    areas = [cross(points[i], points[(i + 1) % n], points[j]) for i in range(n)
             for j in range(n) if j not in (i, (i + 1) % n)]
    require(min(areas) > 0, "control is not strictly convex in natural order")
    separation = min(distance2(a, b) for a, b in combinations(points, 2))
    require(separation > 0, "coincident control vertices")
    for a, b, gain in arrows:
        require(distance2(points[a], points[b + gain * m]) == 3 * norm2(points[a]), "false control arrow")
        s, t = norm2(points[a]), norm2(points[b])
        require(distance2(cube(points[a]), cube(points[b])) == 9 * s * (s - t) ** 2,
                "control cubic-distance identity")
    norms = [norm2(p) for p in representatives]
    greater = [(a, b) for a, b in product(range(m), repeat=2) if ranks[a] > ranks[b]]
    require(all(norms[a] > norms[b] for a, b in greater), "wrong control radial ranking")
    A, E = AngleModel(m).build(arrows, greater)
    check_rational_feasible(A, E, angle_vector)
    profiles = [Counter(distance2(p, q) for j, q in enumerate(points) if j != i)
                for i, p in enumerate(points)]
    maxima = [max(row.values()) for row in profiles]
    require(any(x < 4 for x in maxima), "unexpected unrestricted counterexample")
    return {"representatives_scaled": [[str(x), str(y)] for x, y in representatives],
            "arrows": [list(a) for a in arrows], "squared_radii": [str(s) for s in norms],
            "radial_ranks_in_phase_order": ranks, "vertices": n,
            "supporting_edge_checks": len(areas), "minimum_scaled_orientation": str(min(areas)),
            "minimum_squared_separation": str(separation),
            "maximum_multiplicity_by_vertex": maxima,
            "all_distance_classes": [{str(r): count for r, count in sorted(row.items())} for row in profiles],
            "rational_feasible_angle_vector": angle_vector, "is_erdos97_counterexample": False}


def controls() -> dict:
    # B=1, A=omega^2*(-173+47*i*sqrt(3))/148,
    # D=(71+53*i*sqrt(3))/74, C=omega^2*(-19-i*sqrt(3))/14.
    reps = [(Q(1), Q(0)), (Q(157, 148), Q(63, 148)),
            (Q(71, 74), Q(53, 74)), (Q(4, 7), Q(5, 7))]
    arrows = [(1, 0, 2), (1, 2, 2), (3, 0, 2), (3, 2, 1)]
    vector = ['0', '1', '4', '7', '16', '17', '18', '30', '33', '34', '3', '21/2',
              '20', '21', '45/2', '34', '35', '19', '23', '25', '36', '26', '12']
    rectangle = geometric_control(reps, arrows, [0, 1, 3, 2], vector)
    require(Q(1) < max(norm2(reps[1]), norm2(reps[3])) < norm2(reps[2]), "interlacing control")

    seed1 = (Q(-26503, 21854), Q(8991, 21854))
    seed2 = (Q(-44665, 37058), Q(10753, 37058))
    reps3 = [(Q(1), Q(0)), rotate(rotate(seed1)), rotate(rotate(seed2))]
    arrows3 = [(0, 1, 2), (1, 2, 1), (2, 0, 2)]
    vector3 = ['0', '4', '17', '18', '19', '31', '34', '17', '22', '24', '35', '25', '12']
    cycle = geometric_control(reps3, arrows3, [0, 2, 1], vector3)
    require(cycle['maximum_multiplicity_by_vertex'] == [3] * 9, "seed-cycle multiplicity")
    irrational = []
    for a, b, g in arrows3:
        z = reps3[b]
        for _ in range(g):
            z = rotate(z)
        dot = reps3[a][0] * z[0] + 3 * reps3[a][1] * z[1]
        value = 4 * dot ** 2 / (norm2(reps3[a]) * norm2(z)) - 2
        require(value.denominator != 1, "irrational-angle certificate failed")
        irrational.append(str(value))
    cycle['two_cos_double_angle_rational_nonintegers'] = irrational
    return {"interlacing_common_supplier_rectangle": rectangle,
            "irrational_three_orbit_cycle_is_permitted": cycle}


def graph_well_formed(rows: list[int], degree: int = 2) -> bool:
    n = len(rows)
    return (all(type(mask) is int and 0 <= mask < 1 << n and not mask & (1 << i)
                and mask.bit_count() == degree for i, mask in enumerate(rows))
            and all(not (rows[i] & (1 << j) and rows[j] & (1 << i)) for i, j in combinations(range(n), 2)))


def shortcut_obstructions(rows: list[int]) -> list[dict]:
    """Independent explicit path traversal; labels are weak radial order."""
    n = len(rows)
    neighbors = [{j for j in range(n) if rows[i] & (1 << j) or rows[j] & (1 << i)} for i in range(n)]
    result = []
    for high in range(n):
        for low in range(high):
            if not rows[high] & (1 << low):
                continue
            paths = {low: [low]}
            for a in range(low, high):
                if a not in paths:
                    continue
                for b in sorted(neighbors[a]):
                    if a < b <= high and (a, b) != (low, high) and b not in paths:
                        paths[b] = paths[a] + [b]
            if high in paths:
                result.append({"downward_edge": [high, low], "increasing_path": paths[high]})
    return result


def copair_obstructions(rows: list[int]) -> list[dict]:
    result = []
    for a, b in combinations(range(len(rows)), 2):
        targets = [j for j in range(len(rows)) if (rows[a] & rows[b]) & (1 << j)]
        for c, d in combinations(targets, 2):
            if not c < b < d:
                result.append({"sources": [a, b], "targets": [c, d],
                               "reason": "both sources below targets" if b < c else "a source above both targets"})
    return result


def enumerate_radial_graphs(n: int) -> tuple[list[list[int]], dict]:
    require(3 <= n <= 7, "exhaustive calibration supported only for 3..7 orbits")
    options = [[sum(1 << j for j in choice) for choice in combinations([j for j in range(n) if j != i], 2)]
               for i in range(n)]
    rows = [0] * n
    incoming = [0] * n
    adjacency = [0] * n
    stats = Counter()
    survivors: list[list[int]] = []

    def has_shortcut() -> bool:
        reach = [0] * n
        for a in range(n - 1, -1, -1):
            for b in range(a + 1, n):
                if adjacency[a] & (1 << b):
                    if reach[b] & incoming[a]:
                        return True
                    reach[a] |= (1 << b) | reach[b]
        return False

    def visit(center: int) -> None:
        stats['nodes'] += 1
        if center == n:
            survivors.append(rows.copy())
            return
        for mask in options[center]:
            if mask & incoming[center]:
                continue
            rows[center] = mask
            targets = [j for j in range(n) if mask & (1 << j)]
            for j in targets:
                incoming[j] |= 1 << center
                adjacency[center] |= 1 << j
                adjacency[j] |= 1 << center
            if has_shortcut():
                stats['shortcut_prunes'] += 1
            else:
                visit(center + 1)
            for j in targets:
                incoming[j] &= ~(1 << center)
                adjacency[center] &= ~(1 << j)
                adjacency[j] &= ~(1 << center)
            rows[center] = 0
    visit(0)
    for rows in survivors:
        require(graph_well_formed(rows) and not shortcut_obstructions(rows), "independent terminal predicate mismatch")
    return survivors, dict(stats)


def full_product_crosscheck() -> dict:
    """A separate, unpruned 1,000,000-tuple enumeration for six orbits."""
    n = 6
    options = [list(combinations([j for j in range(n) if j != i], 2)) for i in range(n)]
    tested = 0
    reciprocal_free = 0
    survivors = []
    for choices in product(*options):
        tested += 1
        if any(i in choices[j] for i in range(n) for j in choices[i]):
            continue
        reciprocal_free += 1
        rows = [sum(1 << j for j in row) for row in choices]
        if not shortcut_obstructions(rows):
            survivors.append(rows)
    expected, _ = enumerate_radial_graphs(6)
    require(sorted(survivors) == sorted(expected) and tested == 1_000_000, "full-product completeness mismatch")
    return {"raw_row_tuples_tested": tested, "reciprocal_free_graphs": reciprocal_free,
            "no_shortcut_survivors": len(survivors), "copair_survivors": sum(not copair_obstructions(r) for r in survivors)}


def graph_report() -> dict:
    entries = []
    for n in range(3, 7):
        survivors, stats = enumerate_radial_graphs(n)
        require(len(survivors) == (4 if n == 6 else 0), "unexpected graph frontier")
        require(all(copair_obstructions(rows) for rows in survivors), "unobstructed small graph")
        entries.append({"orbits": n, "stats": stats, "no_shortcut_survivors": survivors,
                        "copair_obstructions": [copair_obstructions(r) for r in survivors],
                        "survivors_after_copair": 0})
    guardrail = [6, 80, 66, 65, 12, 10, 48]
    require(graph_well_formed(guardrail) and not shortcut_obstructions(guardrail)
            and not copair_obstructions(guardrail), "seven-orbit graph guardrail")
    return {"finite_coverage": entries,
            "seven_orbit_guardrail": {"rows": guardrail, "outdegree": 2,
                                      "satisfies_checked_graph_rules": True,
                                      "coordinates_or_realization_claimed": False}}


def check_artifact(artifact: dict) -> dict:
    require(artifact.get('schema') == 'erdos97.c3_common_supplier_certificates.v1', "certificate schema")
    records = artifact.get('records', [])
    require([tuple(record[:3]) for record in records] == all_cases(), "missing, repeated, or unordered case coverage")
    models = [AngleModel(), MetricModel()]
    counts = Counter()
    maximum_terms = maximum_weight = 0
    for record in records:
        require(len(record) == 6 and record[3] in (0, 1), "bad certificate record")
        case = tuple(record[:3])
        arrows, greater = decode_case(case)
        A, E = models[record[3]].build(arrows, greater)
        verify_certificate(A, E, record[4], record[5])
        counts['angle' if record[3] == 0 else 'metric'] += 1
        maximum_terms = max(maximum_terms, len(record[4]) + len(record[5]))
        maximum_weight = max(maximum_weight, *(abs(term[1]) for group in record[4:] for term in group))
    require(dict(counts) == {'angle': 480, 'metric': 6}, "certificate type census changed")
    return {"exact_cases": len(records), "certificate_types": dict(counts),
            "maximum_nonzero_terms": maximum_terms, "maximum_integer_multiplier": maximum_weight,
            "all_integer_residuals_zero": True}


def build_report() -> dict:
    artifact = json.loads((ROOT / 'certificates.json').read_text())
    report = {"schema": "erdos97.c3_common_supplier_report.v1", "date": "2026-09-05",
              "status": "EXACT_CERTIFICATES_AND_FINITE_REPLAY_FOR_REVIEW_PENDING_RESTRICTED_THEOREMS",
              "claim_scope": "Common-supplier radius interlacing; paired-supplier acyclicity; no all-own-side four-bad union of at most six C3 orbits. Not unrestricted Erdos97 or an all-radius n<=18 exclusion.",
              "local_certificate_replay": check_artifact(artifact),
              "graph_replay": graph_report(), "exact_controls": controls(),
              "source_hashes": {name: sha256((ROOT / name).read_bytes()).hexdigest()
                                for name in ['README.md', 'core.py', 'certificates.json', 'check_common_suppliers.py']},
              "external_mathematical_review_claimed": False, "repository_wide_CI_run": False}
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument('--write', action='store_true')
    mode.add_argument('--check', action='store_true')
    parser.add_argument('--full-product-crosscheck', action='store_true')
    args = parser.parse_args()
    report = build_report()
    path = ROOT / 'report.json'
    if args.write:
        path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    if args.check:
        require(json.loads(path.read_text()) == report, "stored report differs from regenerated report")
    summary = {"status": "passed", "exact_certificate_cases": 486,
               "six_orbit_no_shortcut_survivors": 4, "six_orbit_final_survivors": 0,
               "unrestricted_solution_claimed": False}
    if args.full_product_crosscheck:
        summary['independent_full_product'] = full_product_crosscheck()
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
