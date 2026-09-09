"""Exact coarse graph for one cap vertex without two-old support.

This is a necessary-condition relaxation, NOT a realization search or an
infeasibility certificate. The free vertex's outgoing equal-radius equations
and old-vertex richness are deliberately omitted. All nine cases survive.
"""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from core import Q, ORDER, base9, build_slots, graph_data, add, sub, mul, cross, turn, dot, norm, dist  # noqa: E402


def line_intersection(a, b, c, d):
    u, v = sub(b, a), sub(d, c)
    determinant = cross(u, v)
    if determinant == 0:
        raise ValueError('parallel cap sides; this input is not supported')
    return add(a, mul(u, cross(sub(c, a), v)/determinant))


def minimum_distance_to_triangle(x, triangle):
    assert turn(*triangle) > 0
    if all(turn(triangle[k], triangle[(k+1) % 3], x) >= 0 for k in range(3)):
        return Q(0)
    values = []
    for k in range(3):
        a, b = triangle[k], triangle[(k+1) % 3]
        v = sub(b, a)
        parameter = dot(sub(x, a), v)/norm(v)
        parameter = max(Q(0), min(Q(1), parameter))
        values.append(dist(x, add(a, mul(v, parameter))))
    return min(values)


def source_to_triangle_range(P, source, triangle):
    """Affine in source parameter; target extrema are nearest point/vertices."""
    values = []
    for parameter in (source.lower, source.upper):
        x = source.point(parameter)
        radius_squared = dist(x, P[source.pair[0]])
        values.extend(dist(x, y)-radius_squared for y in triangle)
        values.append(minimum_distance_to_triangle(x, triangle)-radius_squared)
    return min(values), max(values)


def run():
    P = base9()
    slots = build_slots(P, ORDER)
    edges, _, _ = graph_data(P, slots)
    results = []
    for cell in range(9):
        a, b = P[ORDER[cell]], P[ORDER[(cell+1) % 9]]
        c = line_intersection(P[ORDER[cell-1]], a, b, P[ORDER[(cell+2) % 9]])
        triangle = [a, c, b]
        assert turn(*triangle) > 0
        for k in range(9):
            value = turn(P[ORDER[k]], P[ORDER[(k+1) % 9]], c)
            assert value < 0 if k == cell else value >= 0
        possible = []
        for i, source in enumerate(slots):
            lower, upper = source_to_triangle_range(P, source, triangle)
            if lower <= 0 <= upper:
                possible.append(i)
        # One free vertex (label 42) is allowed all regular vertices as outgoing
        # witnesses, without enforcing their common radius. This is an explicit
        # relaxation, so survival is not evidence of geometric feasibility.
        extended_edges = edges + [(i,42) for i in possible] + [(42,i) for i in range(42)]
        active = set(range(43))
        layers = []
        while True:
            removed = sorted(i for i in active if sum(a == i and b in active for a,b in extended_edges) < (3 if i == 42 else 2))
            if not removed:
                break
            layers.append(removed)
            active.difference_update(removed)
        assert 42 in active
        assert len(active) == (16 if cell in (2,5,8) else 13)
        results.append({'free_cell': cell, 'insertion_edge': [ORDER[cell],ORDER[(cell+1) % 9]],
                        'closed_triangle': [[v.json() for v in p] for p in triangle],
                        'possible_regular_to_free': possible, 'core': sorted(active),
                        'peeling_layers': layers, 'geometric_realization_certified': False})
    return {'status': 'coarse exact necessary-condition relaxation; all nine cases survive',
            'old_seed_fixed': True, 'free_vertex_count': 1,
            'free_vertex_requires_at_least_three_new_witnesses': True,
            'omitted': ['common radius at free vertex','simultaneous equality realization',
                        'circle-sharing constraints','mutual convexity of cap points','old-vertex richness'],
            'cases': results}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    args = parser.parse_args()
    report = run()
    payload = json.dumps(report,indent=2,sort_keys=True)+'\n'
    path = Path(__file__).with_suffix('.json')
    if args.write:
        path.write_text(payload)
    else:
        assert path.read_text() == payload, 'coarse relaxation report differs'
    print(report['status'])
    print('Core sizes including the free vertex:',[len(c['core']) for c in report['cases']])


if __name__ == '__main__':
    main()
