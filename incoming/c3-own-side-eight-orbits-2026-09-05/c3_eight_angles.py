"""Necessary exact chord-angle relaxation of strictly convex C3 own-side systems.
A feasible vector is not a geometric realization. Pi is a homogeneous variable.
"""
from __future__ import annotations
from itertools import combinations

def primitive(row):
    """Remove the positive integer content without reversing a strict inequality."""
    from math import gcd
    vals = list(row)
    g = 0
    for v in vals:
        g = gcd(g, int(v))
    if not g:
        return tuple(vals)
    vals = [int(v) // g for v in vals]
    return tuple(vals)

def model(rows, right=True, ordered=True):
    """Build necessary integer angle constraints, their equality rows, and premise labels."""
    m = len(rows)
    n = 3 * m
    pairs = list(combinations(range(n), 2))
    representatives = {}

    def key(a, b):
        i, j = (a % m, b % m)
        p, q = (a // m, b // m)
        if i == j:
            return (i,)
        return (i, j, (q - p) % 3) if i < j else (j, i, (p - q) % 3)
    for a, b in pairs:
        representatives.setdefault(key(a, b), (a, b))
    ids = {k: i for i, k in enumerate(representatives)}
    k = len(ids)
    pi = k
    dim = k + 1
    cls = {}
    eta = {}
    for a, b in pairs:
        c = key(a, b)
        u, v = representatives[c]
        cls[a, b] = ids[c]
        eta[a, b] = (a + b - u - v) // m
        assert (a + b - u - v) % m == 0
    length = list(range(k))

    def own(i):
        return cls[i, i + m]
    for i, row in enumerate(rows):
        if len(row) % 2:
            raise ValueError('target/gain pairs required')
        for j, g in zip(row[::2], row[1::2]):
            a, b = sorted((i, g * m + j))
            c = cls[a, b]
            if length[c] != c and length[c] != own(i):
                raise ValueError('conflicting pair')
            length[c] = own(i)
    A = []
    E = []
    alabel = []
    elabel = []

    def angle(a, b, c):
        """Angles opposite BC, AC, AB in sorted triangle (a,b,c), times 3."""
        ab, ac, bc = ((a, b), (a, c), (b, c))
        result = []
        for coeff, const in [([(ac, 1), (ab, -1)], 0), ([(ab, 1), (bc, -1)], 3), ([(bc, 1), (ac, -1)], 0)]:
            v = [0] * dim
            v[pi] = const
            for p, s in coeff:
                v[cls[p]] += s
                v[pi] += s * eta[p]
            result.append(v)
        return result
    cache = {}
    for a, b, c in combinations(range(n), 3):
        angles = angle(a, b, c)
        cache[a, b, c] = angles
        for t, v in enumerate(angles):
            A.append(v)
            alabel.append(['angle_positive', a, b, c, t])
        oppos = [length[cls[b, c]], length[cls[a, c]], length[cls[a, b]]]
        for i, j in combinations(range(3), 2):
            if oppos[i] == oppos[j]:
                E.append([x - y for x, y in zip(angles[i], angles[j])])
                elabel.append(['equal_sides', a, b, c, i, j])
    v = [0] * dim
    v[pi] = 1
    A.append(v)
    alabel.append(['pi_positive'])
    if right:
        for i, row in enumerate(rows):
            for j, g in zip(row[::2], row[1::2]):
                c = (g + 1) % 3 * m + j
                d = (g + 2) % 3 * m + j
                tri = tuple(sorted((i, c, d)))
                at = tri.index(i)
                v = [2 * x for x in cache[tri][at]]
                v[pi] -= 3
                E.append(v)
                elabel.append(['right_angle', i, j, g])
    if ordered:
        less = set()
        for i, row in enumerate(rows):
            for j, g in zip(row[::2], row[1::2]):
                down = g == (1 if j > i else 2)
                less.add((own(j), own(i)) if down else (own(i), own(j)))
        for a, b, c in combinations(range(n), 3):
            angles = cache[a, b, c]
            opp = [length[cls[b, c]], length[cls[a, c]], length[cls[a, b]]]
            for i, j in combinations(range(3), 2):
                if (opp[i], opp[j]) in less:
                    A.append([y - x for x, y in zip(angles[i], angles[j])])
                    alabel.append(['angle_order', a, b, c, i, j])
                elif (opp[j], opp[i]) in less:
                    A.append([x - y for x, y in zip(angles[i], angles[j])])
                    alabel.append(['angle_order', a, b, c, j, i])

    def dedup(matrix, labels, eq):
        out = []
        names = []
        seen = set()
        for v, label in zip(matrix, labels):
            t = primitive(v)
            if eq:
                if not any(t):
                    continue
                if next((x for x in t if x)) < 0:
                    t = tuple((-x for x in t))
            if t in seen:
                continue
            seen.add(t)
            out.append(t)
            names.append(label)
        return (out, names)
    A, alabel = dedup(A, alabel, False)
    E, elabel = dedup(E, elabel, True)
    return (A, E, alabel, elabel)
