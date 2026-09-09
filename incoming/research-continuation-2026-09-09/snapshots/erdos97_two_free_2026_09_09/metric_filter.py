"""Exact zero/inverse strict-Kalmanson obstructions for partial witness rows.

Only quadruples with four different insertion ranks are used. No ordering of
vertices within a tied cell is assumed. Rows may be absent at old vertices.
"""
from __future__ import annotations
from itertools import combinations


def chord(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError('Self chord')
    return (min(a, b), max(a, b))


def obstruction(rows: dict[int, list[int]], ranks: dict[int, int], old_count: int = 9):
    """Return a checkable cancellation, or None (not a feasibility claim)."""
    parent = {}

    def root(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def join(x, y):
        x, y = root(x), root(y)
        if x != y:
            parent[max(x, y)] = min(x, y)

    labels = set(range(old_count))
    for source, witnesses in rows.items():
        if len(witnesses) != 4 or len(set(witnesses)) != 4 or source in witnesses:
            raise ValueError('Invalid selected row')
        labels.add(source)
        labels.update(witnesses)
        for witness in witnesses[1:]:
            join(chord(source, witnesses[0]), chord(source, witness))
    ordered = sorted(labels, key=lambda i: (ranks[i], i))
    seen = {}
    for quad in combinations(ordered, 4):
        if len({ranks[i] for i in quad}) < 4:
            continue
        a, b, c, d = quad
        for kind, sides in enumerate((((a, b), (c, d)), ((a, d), (b, c)))):
            coefficients = {}
            for edge, sign in ((chord(a, c), 1), (chord(b, d), 1),
                               (chord(*sides[0]), -1), (chord(*sides[1]), -1)):
                key = root(edge)
                coefficients[key] = coefficients.get(key, 0) + sign
            vector = tuple(sorted((k, v) for k, v in coefficients.items() if v))
            item = {'quad': list(quad), 'kind': kind}
            if not vector:
                return {'type': 'zero', 'inequalities': [item]}
            opposite = tuple((key, -value) for key, value in vector)
            if opposite in seen:
                return {'type': 'inverse', 'inequalities': [seen[opposite], item]}
            seen.setdefault(vector, item)
    return None
