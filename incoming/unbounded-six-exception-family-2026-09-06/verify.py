"""Exact algebra and finite-instance checks for the unbounded partial family.

Equalities are inherited from the proved recurrence/rotation identities.
Only strict inequalities are established by interval arithmetic.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cmp_to_key
from itertools import combinations
import json
from pathlib import Path

from algebra import check_algebra, require
from intervals import Interval as I


def rot(p):
    return (-(p[0] + 3 * p[1]) / 2, (p[0] - p[1]) / 2)


def norm(p):
    return p[0].square() + 3 * p[1].square()


def sub(a, b):
    return a[0] - b[0], a[1] - b[1]


def cross(a, b):
    return a[0] * b[1] - a[1] * b[0]


def squared(a, b):
    return norm(sub(a, b))


def orientation(a, b, c):
    return cross(sub(b, a), sub(c, a))


def build(chain_orbits: int, bits: int):
    if not isinstance(chain_orbits, int) or isinstance(chain_orbits, bool) or chain_orbits < 1:
        raise ValueError('chain_orbits must be a positive integer')
    if not isinstance(bits, int) or isinstance(bits, bool) or bits < 64:
        raise ValueError('bits must be an integer of at least 64')
    t = I.exact(Q(1, 10), bits)
    ts = []
    reps = [(I.exact(1, bits), I.exact(0, bits))]
    for j in range(chain_orbits):
        require(t.lo > 0, 'parameter positivity not certified; increase precision')
        ts.append(t)
        d = 1 + 3 * t.square()
        z = (-I.exact(Q(1, 2), bits) + 3 * t / d, (1 - 3 * t.square()) / (2 * d))
        if j % 2:
            z = (z[0], -z[1])
        reps.append(z)
        if j + 1 < chain_orbits:
            b = 1 - 2 * t + 3 * t.square()
            disc = (1 - t) * (1 - 3 * t) * (1 + 3 * t.square())
            require(disc.lo > 0, 'positive discriminant not certified')
            new = 2 * t.square() / (b + disc.sqrt())
            require(new.lo > 0 and new.hi < t.lo,
                    'strict parameter decrease not certified; increase precision')
            t = new
    return reps, ts


class DSU:
    def __init__(self, n):
        self.p = list(range(n))

    def root(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        self.p[self.root(b)] = self.root(a)


def finite_check(chain_orbits=5, bits=2048):
    reps, ts = build(chain_orbits, bits)
    m = len(reps)
    points = []
    labels = []
    for i, z in enumerate(reps):
        for k in range(3):
            points.append(z)
            labels.append((i, k))
            z = rot(z)
    n = len(points)

    def half(z):
        x, y = z
        if y.lo > 0:
            return 0
        if y.hi < 0:
            return 1
        if y.lo == y.hi == 0:
            if x.lo > 0:
                return 0
            if x.hi < 0:
                return 1
        raise ArithmeticError('angular half-plane undecided; increase precision')

    def compare(i, j):
        a, b = points[i], points[j]
        ha, hb = half(a), half(b)
        if ha != hb:
            return -1 if ha < hb else 1
        c = cross(a, b)
        if c.lo > 0:
            return -1
        if c.hi < 0:
            return 1
        if i == j:
            return 0
        raise ArithmeticError('angular order undecided; increase precision')

    order = sorted(range(n), key=cmp_to_key(compare))
    supports = []
    for k, u in enumerate(order):
        v = order[(k + 1) % n]
        for w in order:
            if w in (u, v):
                continue
            det = orientation(points[u], points[v], points[w])
            require(det.lo > 0, f'convexity not certified at {labels[u], labels[v], labels[w]}')
            supports.append(det.lo)
    pairs = list(combinations(range(n), 2))
    ix = {p: i for i, p in enumerate(pairs)}
    ds = DSU(len(pairs))

    def edge(a, b):
        return ix[tuple(sorted((a, b)))]

    def shifted(i, k):
        return 3 * (i // 3) + (i % 3 + k) % 3

    for a, b in pairs:
        for k in (1, 2):
            ds.union(edge(a, b), edge(shifted(a, k), shifted(b, k)))
    for i in range(1, m):
        for k in range(3):
            source = 3 * i + k
            own = edge(source, 3 * i + (k + 1) % 3)
            ds.union(own, edge(source, k))
            if i >= 2:
                ds.union(own, edge(source, 3 * (i - 1) + k))
    distances = [squared(points[a], points[b]) for a, b in pairs]
    require(all(d.lo > 0 for d in distances), 'point distinctness not certified')
    rows = []
    separations = []
    for a in range(n):
        groups = defaultdict(list)
        enclosures = {}
        for b in range(n):
            if a == b:
                continue
            e = edge(a, b)
            cl = ds.root(e)
            groups[cl].append(b)
            if cl in enclosures:
                enclosures[cl] = enclosures[cl].intersect(distances[e])
            else:
                enclosures[cl] = distances[e]
        for c, d in combinations(groups, 2):
            v, w = enclosures[c], enclosures[d]
            sep = max(v.lo - w.hi, w.lo - v.hi)
            require(sep > 0,
                    f'unproved separation at {labels[a]}: {groups[c]}, {groups[d]};'
                    ' increase precision or audit extra identities')
            separations.append(sep)
        mult = max(map(len, groups.values()))
        if a // 3 == 0:
            require(mult == 2, 'unexpected anchor multiplicity')
        elif a // 3 == 1:
            require(mult == 3, 'unexpected initial-orbit multiplicity')
        else:
            require(mult >= 4, 'a constructed rich vertex lost its witnesses')
        rows.append({'vertex': list(labels[a]), 'maximum_multiplicity': mult,
          'rich_classes': [[list(labels[v]) for v in g] for g in groups.values() if len(g) >= 4]})
    dist = dict(sorted(Counter(r['maximum_multiplicity'] for r in rows).items()))
    require(sum(v for k, v in dist.items() if k <= 3) == 6, 'wrong number of good vertices')
    bounds = {'support_determinant_div_sqrt3': min(supports),
       'distinct_squared_distance': min(d.lo for d in distances),
       'separation_of_unequal_squared_distances': min(separations)}
    return {'status': 'EXACT_FINITE_INSTANCE_VERIFIED_NOT_A_COUNTEREXAMPLE',
      'chain_orbits': chain_orbits, 'total_orbits': m, 'point_count': n, 'bits': bits,
      'good_vertices': 6, 'rich_vertices': n - 6, 'maximum_multiplicity_distribution': dist,
      'support_checks': len(supports), 'distinct_pairs': len(pairs),
      'distance_class_separations': len(separations),
      'cyclic_order': [list(labels[v]) for v in order],
      'positive_dyadic_lower_bounds': {k: {'numerator_hex': hex(v), 'denominator_power_of_two': bits}
                                       for k, v in bounds.items()},
      'rows': rows}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--chain-orbits', type=int, default=5)
    parser.add_argument('--bits', type=int, default=2048)
    parser.add_argument('--algebra-only', action='store_true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    try:
        result = {'algebra': check_algebra()}
        if not args.algebra_only:
            result['finite'] = finite_check(args.chain_orbits, args.bits)
    except (ArithmeticError, AssertionError, ValueError) as exc:
        parser.exit(2, f'verification failed: {exc}\n')
    text = json.dumps(result, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
