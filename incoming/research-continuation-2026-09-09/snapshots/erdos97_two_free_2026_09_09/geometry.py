"""Exact necessary row models for two free vertices and 42 old-pair slots.

All coordinates lie in Q(sqrt(721)); (x,y) denotes Cartesian (x,sqrt(3)*y).
Closed domains deliberately include inadmissible boundary configurations.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import product

from prior import load
from row_search import Model

O = load("one_free")


@lru_cache(maxsize=1)
def context():
    points, slots, edges, ceiling = O.setup()
    triangles = tuple(O.insertion_triangle(points, k) for k in range(9))
    return points, slots, tuple(edges), ceiling, triangles


@lru_cache(maxsize=None)
def incoming(triangle):
    points, slots, _, _, _ = context()
    return tuple(O.allowed_incoming(points, slots, triangle))


@lru_cache(maxsize=None)
def outgoing(triangle, old):
    points, slots, _, _, _ = context()
    if old is None:
        return tuple(range(42))
    return tuple(
        i for i, slot in enumerate(slots)
        if O.possible(O.free_to_regular_range(points, old, slot, triangle))
    )


@lru_cache(maxsize=None)
def free_edge_possible(source, target, old):
    if old is None:
        return True
    points, _, _, _, _ = context()
    values = []
    for f in source:
        radius_squared = O.dist(f, points[old])
        values.extend(O.dist(f, g) - radius_squared for g in target)
        values.append(O.dist(f, O.closest_on_triangle(f, target)) - radius_squared)
    return min(values) <= 0 <= max(values)


@lru_cache(maxsize=None)
def triangle_distance_range(first, second):
    high = max(O.dist(x, y) for x in first for y in second)
    intersects = any(
        O.segment_meets_triangle(first[k], first[(k + 1) % 3], second)
        for k in range(3)
    ) or any(
        O.segment_meets_triangle(second[k], second[(k + 1) % 3], first)
        for k in range(3)
    )
    if intersects:
        return O.Q(0), high
    values = [O.dist(x, O.closest_on_triangle(x, second)) for x in first]
    values.extend(O.dist(x, O.closest_on_triangle(x, first)) for x in second)
    return min(values), high


@lru_cache(maxsize=None)
def slot_distance_range(slot_index, triangle):
    return O.distance_interval(context()[1][slot_index], triangle)


def degree_core(adjacency, need):
    active = set(range(len(adjacency)))
    while True:
        removed = {i for i in active if len(adjacency[i] & active) < need[i]}
        if not removed:
            return active
        active.difference_update(removed)


def radius_covers(intervals, need):
    """Maximal sets sharing a common closed squared-radius interval point.

    Any finite actual witness set has a common interval point at its actual
    radius. It is contained in a maximal set generated at an interval endpoint.
    """
    covers = set()
    endpoints = sorted({endpoint for bounds in intervals.values() for endpoint in bounds})
    for radius in endpoints:
        selected = frozenset(
            i for i, (lower, upper) in intervals.items() if lower <= radius <= upper
        )
        if len(selected) >= need:
            covers.add(selected)
    return sorted(
        (s for s in covers if not any(s < t for t in covers)),
        key=lambda s: tuple(sorted(s)),
    )


def models(first, second, cells, old_witnesses):
    points, slots, edges, _, _ = context()
    adjacency = [set() for _ in range(44)]
    for source, target in edges:
        adjacency[source].add(target)
    for source, triangle, old in (
        (42, first, old_witnesses[0]), (43, second, old_witnesses[1])
    ):
        for i in incoming(triangle):
            adjacency[i].add(source)
        adjacency[source].update(outgoing(triangle, old))
    if free_edge_possible(first, second, old_witnesses[0]):
        adjacency[42].add(43)
    if free_edge_possible(second, first, old_witnesses[1]):
        adjacency[43].add(42)
    need = [2] * 42 + [4 if old is None else 3 for old in old_witnesses]
    active = degree_core(adjacency, need)
    if not {42, 43} <= active:
        return []
    covers = []
    for source, triangle, other_triangle, old in (
        (42, first, second, old_witnesses[0]),
        (43, second, first, old_witnesses[1]),
    ):
        targets = adjacency[source] & active
        if old is None:
            intervals = {
                i: slot_distance_range(i, triangle) if i < 42 else
                   triangle_distance_range(triangle, other_triangle)
                for i in targets
            }
            covers.append(radius_covers(intervals, need[source]))
        else:
            covers.append([frozenset(targets)])
    ranks = {v: 2 * k for k, v in enumerate(O.B.ORDER)}
    ranks.update({9 + i: 2 * slot.cell + 1 for i, slot in enumerate(slots)})
    ranks.update({51: 2 * cells[0] + 1, 52: 2 * cells[1] + 1})
    result = []
    for selected_first, selected_second in product(*covers):
        restricted = [set(targets) for targets in adjacency]
        restricted[42] = set(selected_first)
        restricted[43] = set(selected_second)
        active = degree_core(restricted, need)
        if not {42, 43} <= active:
            continue
        old_support = {}
        for i in sorted(active):
            if i < 42:
                old_support[i] = slots[i].pair
            else:
                old = old_witnesses[i - 42]
                old_support[i] = () if old is None else (old,)
        result.append(Model(
            adjacency={i: tuple(sorted(restricted[i] & active)) for i in sorted(active)},
            old_support=old_support, ranks=ranks,
        ))
    return result


def split(triangle, edge):
    if type(edge) is not int or not 0 <= edge < 3:
        raise ValueError("Invalid subdivision edge")
    a, b, c = (triangle[(edge + j) % 3] for j in range(3))
    midpoint = O.mul(O.add(a, b), O.Q(1) / 2)
    children = ((a, midpoint, c), (midpoint, b, c))
    if not all(O.turn(*child) > 0 for child in children):
        raise ValueError("Degenerate subdivision")
    return children
