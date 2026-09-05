"""Exact rational Q(sqrt(3)) controls for the C3 geometry and angle encoding."""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from functools import cmp_to_key
from itertools import combinations
import json
from pathlib import Path
from c3_eight_check import Geometry, require

def rotate(p):
    return (-(p[0] + 3 * p[1]) / 2, (p[0] - p[1]) / 2)

def norm(p):
    return p[0] * p[0] + 3 * p[1] * p[1]

def squared(p, q):
    return norm((p[0] - q[0], p[1] - q[1]))

def cross(p, q):
    return p[0] * q[1] - p[1] * q[0]

def det(a, b, c):
    return cross((b[0] - a[0], b[1] - a[1]), (c[0] - a[0], c[1] - a[1]))

def divide(z, w):
    d = norm(w)
    require(d > 0, 'nonzero divisor required')
    return ((z[0] * w[0] + 3 * z[1] * w[1]) / d, (z[1] * w[0] - z[0] * w[1]) / d)

def canonical(seeds):
    """Choose maximum norm as label zero, order sector representatives, and check strict convexity."""
    anchor = max(seeds, key=norm)
    reps = []
    for seed in seeds:
        z = divide(seed, anchor)
        for _ in range(3):
            if z[1] >= 0 and z[0] + z[1] > 0:
                reps.append(z)
                break
            z = rotate(z)
        else:
            raise ValueError('sector representative missing')
    reps.sort(key=cmp_to_key(lambda x, y: -1 if cross(x, y) > 0 else 1 if cross(x, y) < 0 else 0))
    require(reps[0] == (1, 0), 'maximum norm anchor is not first')
    m = len(reps)
    points = reps + [rotate(z) for z in reps] + [rotate(rotate(z)) for z in reps]
    require(len(set(points)) == 3 * m, 'coincident points')
    for i in range(3 * m):
        for j in range(3 * m):
            if j not in (i, (i + 1) % (3 * m)):
                require(det(points[i], points[(i + 1) % (3 * m)], points[j]) > 0, 'nonconvex control')
    rows = []
    for i in range(m):
        r = []
        for j in range(m):
            if i == j:
                continue
            gains = [g for g in range(3) if squared(points[i], points[j + g * m]) == 3 * norm(points[i])]
            require(len(gains) <= 1, 'multiple witnesses from same orbit')
            if gains:
                r.extend((j, gains[0]))
        rows.append(r)
    return (reps, points, rows)

def fixture_data():
    return {'irrational_three_cycle': [(Q(1), Q(0)), (Q(-26503, 21854), Q(8991, 21854)), (Q(-44665, 37058), Q(10753, 37058))], 'two_suppliers_one_center': [(Q(1), Q(0)), (Q(-5, 7), Q(1, 7)), (Q(-5, 7), Q(-1, 7))]}

def four_orbit_order_control():
    """Check the exact four-orbit strict Pythagorean consequence without float angles."""
    reps, _, _ = canonical(fixture_data()['irrational_three_cycle'])
    a, b, c = reps
    w = rotate(a)
    epsilon = Q(1, 1000)
    edge = (w[0] - c[0], w[1] - c[1])
    d = ((c[0] + w[0]) / 2 + 3 * epsilon * edge[1], (c[1] + w[1]) / 2 - epsilon * edge[0])
    reps = [a, b, c, d]
    points = reps + [rotate(z) for z in reps] + [rotate(rotate(z)) for z in reps]
    require(all((det(points[i], points[(i + 1) % 12], points[j]) > 0 for i in range(12) for j in range(12) if j not in (i, (i + 1) % 12))), 'four-orbit order control is not strictly convex')
    require(squared(c, a) == 3 * norm(c), 'four-orbit control arrow failed')
    margin = squared(b, rotate(d)) - squared(b, rotate(c)) - squared(c, d)
    require(margin > 0, 'strict Pythagorean comparison failed')
    return {'vertices': 12, 'exact_convexity': True, 'arrow_C_to_A': True, 'strict_squared_distance_margin': str(margin)}

def audit_controls(path=None):
    """Validate genuine geometric fixtures and their rational angle-relaxation witnesses."""
    vectors = json.loads((Path(path) if path else Path(__file__).with_name('positive_angle_vectors.json')).read_text())
    summaries = {}
    for name, seeds in fixture_data().items():
        reps, points, rows = canonical(seeds)
        geo = Geometry(rows, full=False)
        distribution = Counter((max(Counter((squared(p, q) for j, q in enumerate(points) if j != i)).values()) for i, p in enumerate(points)))
        expected = {3: 9} if name == 'irrational_three_cycle' else {4: 3, 2: 6}
        require(distribution == expected, 'wrong exact control multiplicities')
        for p, pairs in enumerate(geo.right):
            for u, v in pairs:
                a, b, c = (points[p], points[u], points[v])
                require((b[0] - a[0]) * (c[0] - a[0]) + 3 * (b[1] - a[1]) * (c[1] - a[1]) == 0, 'right angle identity')
        from c3_eight_angles import model
        A, E, _, _ = model(rows)
        x = [Q(v) for v in vectors[name]]
        require(len(x) == len(geo.variables), 'positive-vector dimension')
        require(all((sum((int(c) * v for c, v in zip(row, x))) > 0 for row in A)), 'positive vector violates a strict row')
        require(all((sum((int(c) * v for c, v in zip(row, x))) == 0 for row in E)), 'positive vector violates equality')
        n = len(points)
        for center, witnesses in enumerate(geo.selected):
            for p, b in combinations(sorted(witnesses), 2):
                for p, b in ((p, b), (b, p)):
                    lo, hi = sorted(((center - p) % n, (b - p) % n))
                    for u, v in geo.right[p]:
                        a, c = sorted(((u - p) % n, (v - p) % n))
                        require(not lo <= a < c <= hi, 'false obtuse-base rejection of actual geometry')
        summaries[name] = {'rows': rows, 'vertices': len(points), 'maximum_multiplicity_distribution': dict(sorted(distribution.items())), 'exact_convexity': True, 'exact_right_angles': True, 'rational_angle_relaxation_feasible': True}
    summaries['four_orbit_order_inequality'] = four_orbit_order_control()
    return summaries
if __name__ == '__main__':
    print(json.dumps(audit_controls(), indent=2))
