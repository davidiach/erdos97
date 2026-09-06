#!/usr/bin/env python3
"""Exact finite checks for the one-closer-point obstruction for Erdos #97.

All coordinates and radii SQUARED are integers or rational numbers. No float
is accepted as geometric input. This program checks instances and recorded
controls; the arbitrary-size result is proved separately in proofs.md.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from typing import Iterable, Sequence

Point = tuple[F, F]
Edge = tuple[int, int]


class VerificationError(ValueError):
    """The supplied data do not meet a claimed hypothesis or conclusion."""


def require(ok: bool, message: str) -> None:
    if not ok:
        raise VerificationError(message)


def rational(value: int | str | F) -> F:
    if isinstance(value, bool) or isinstance(value, float):
        raise VerificationError("Boolean and floating-point geometric inputs are rejected")
    if not isinstance(value, (int, str, F)):
        raise VerificationError("Expected an integer, rational string, or Fraction")
    try:
        return F(value)
    except (ValueError, ZeroDivisionError) as exc:
        raise VerificationError("Invalid rational input") from exc


def point(value: Sequence[int | str | F]) -> Point:
    require(len(value) == 2, "A point must have two coordinates")
    return rational(value[0]), rational(value[1])


def squared(a: Point, b: Point) -> F:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def orient(a: Point, b: Point, c: Point) -> F:
    return ((b[0] - a[0]) * (c[1] - a[1])
            - (b[1] - a[1]) * (c[0] - a[0]))


def hull_indices(points: Sequence[Point]) -> tuple[int, ...]:
    """Exact monotone hull, omitting collinear boundary points."""
    require(len(set(points)) == len(points), "Duplicate points")
    order = sorted(range(len(points)), key=points.__getitem__)
    if len(order) <= 2:
        return tuple(order)
    def half(indices: Iterable[int]) -> list[int]:
        ans: list[int] = []
        for i in indices:
            while len(ans) >= 2 and orient(points[ans[-2]], points[ans[-1]], points[i]) <= 0:
                ans.pop()
            ans.append(i)
        return ans
    return tuple(half(order)[:-1] + half(reversed(order))[:-1])


def crosses(points: Sequence[Point], e: Edge, f: Edge) -> bool:
    if len(set(e + f)) != 4:
        return False
    a, b = (points[i] for i in e)
    c, d = (points[i] for i in f)
    return orient(a, b, c) * orient(a, b, d) < 0 and orient(c, d, a) * orient(c, d, b) < 0


@dataclass(frozen=True)
class Geometry:
    points: tuple[Point, ...]
    order: tuple[int, ...]
    d2: tuple[tuple[F, ...], ...]
    support_count: int
    support_minimum: F | None
    vertical_scale_squared: F = F(1)

    @classmethod
    def build(cls, values: Sequence[Sequence[int | str | F]],
              vertical_scale_squared: int | str | F = F(1)) -> 'Geometry':
        # Physical points are (x, sqrt(scale)*y). Orientation signs are unchanged;
        # squared Euclidean distances are dx^2 + scale*dy^2. This also permits
        # exact equilateral controls using scale=3 without floating point.
        scale = rational(vertical_scale_squared)
        require(scale > 0, "Vertical scale squared must be positive")
        pts = tuple(point(v) for v in values)
        require(bool(pts), "A nonempty set is required")
        order = hull_indices(pts)
        require(len(order) == len(pts), "Points are not strictly convexly independent")
        signs: list[F] = []
        if len(pts) >= 3:
            for i, a in enumerate(order):
                b = order[(i + 1) % len(order)]
                signs.extend(orient(pts[a], pts[b], pts[j])
                             for j in range(len(pts)) if j not in (a, b))
            require(all(v > 0 for v in signs), "A supporting-line determinant is not positive")
        d2 = tuple(tuple((a[0]-b[0])**2 + scale*(a[1]-b[1])**2 for b in pts) for a in pts)
        return cls(pts, order, d2, len(signs), min(signs) if signs else None, scale)

    def closer_counts(self, radii_squared: Sequence[int | str | F]) -> tuple[int, ...]:
        rho = tuple(map(rational, radii_squared))
        require(len(rho) == len(self.points), "Wrong radius-vector length")
        require(all(v > 0 for v in rho), "Radii squared must be strictly positive")
        return tuple(sum(i != j and d < rho[i] for j, d in enumerate(row))
                     for i, row in enumerate(self.d2))

    def witnesses(self, i: int, radius_squared: F) -> tuple[int, ...]:
        return tuple(j for j, d in enumerate(self.d2[i]) if j != i and d == radius_squared)

    def maximum_multiplicities(self) -> tuple[int, ...]:
        ans = []
        for i, row in enumerate(self.d2):
            counts: dict[F, int] = {}
            for j, d in enumerate(row):
                if j != i:
                    counts[d] = counts.get(d, 0) + 1
            ans.append(max(counts.values(), default=0))
        return tuple(ans)

    def second_neighbor_options(self, i: int) -> tuple[F, ...]:
        distances = sorted(d for j, d in enumerate(self.d2[i]) if j != i)
        if not distances:
            return (F(1),)
        cutoff = distances[min(1, len(distances) - 1)]
        return tuple(sorted({d for d in distances if d <= cutoff}))


def threshold_graph_certificate(geo: Geometry, vertices: Sequence[int], r2: F) -> dict:
    """Check the matching-short-edge/noncrossing lemma at one common scale."""
    vertices = tuple(vertices)
    require(r2 > 0, "Threshold squared must be positive")
    require(len(set(vertices)) == len(vertices), "Repeated graph vertex")
    require(all(0 <= i < len(geo.points) for i in vertices), "Graph vertex out of range")
    red = [e for e in combinations(vertices, 2) if geo.d2[e[0]][e[1]] < r2]
    blue = [e for e in combinations(vertices, 2) if geo.d2[e[0]][e[1]] == r2]
    degree = {i: 0 for i in vertices}
    for a, b in red:
        degree[a] += 1
        degree[b] += 1
    require(all(v <= 1 for v in degree.values()), "Short edges are not a matching")
    edges = red + blue
    for e, f in combinations(edges, 2):
        require(not crosses(geo.points, e, f), "Threshold edges cross")
    red_set = {frozenset(e) for e in red}
    edge_set = {frozenset(e) for e in edges}
    triangles = []
    red_triangles = []
    for t in combinations(vertices, 3):
        pairs = [frozenset(e) for e in combinations(t, 2)]
        if all(e in edge_set for e in pairs):
            triangles.append(t)
            bases = [e for e in pairs if e in red_set]
            require(len(bases) <= 1, "A triangle has two short edges")
            if bases:
                apex = next(i for i in t if i not in bases[0])
                red_triangles.append((t, tuple(sorted(bases[0])), apex))
    m = len(vertices)
    require(len(edges) <= max(0, 2 * m - 3), "Outerplanar edge bound failed")
    require(len(triangles) <= max(0, m - 2), "Outerplanar triangular-face bound failed")
    return {'vertices': list(vertices), 'short_edges': [list(e) for e in red],
            'unit_edges': [list(e) for e in blue],
            'triangles': [list(t) for t in triangles],
            'short_base_triangles': [dict(vertices=list(t), base=list(e), apex=a)
                                     for t, e, a in red_triangles],
            'face_budget': max(0, m - 2)}


def minimum_layer_certificate(geo: Geometry, radii_squared: Sequence[int | str | F]) -> dict:
    """Exact certificate for the minimum-layer deficiency theorem.

    Distances strictly BELOW each assigned radius are counted. Equal-distance
    points do not consume the one-closer allowance.
    """
    rho = tuple(map(rational, radii_squared))
    counts = geo.closer_counts(rho)
    require(max(counts, default=0) <= 1, "One-closer-point hypothesis fails")
    r2 = min(rho)
    layer = tuple(i for i, v in enumerate(rho) if v == r2)
    graph = threshold_graph_certificate(geo, layer, r2)
    layer_set = set(layer)
    assignments = []
    for p in layer:
        witnesses = geo.witnesses(p, r2)
        if len(witnesses) < 4:
            continue
        pair = next((e for e in combinations(witnesses, 2)
                     if geo.d2[e[0]][e[1]] < r2), None)
        require(pair is not None, "Four hull witnesses have no strictly short pair")
        a, b = pair
        require(a in layer_set and b in layer_set, "Minimum-radius transfer failed")
        triangle = tuple(sorted((p, a, b)))
        require(list(triangle) in graph['triangles'], "Assigned triangle is absent")
        assignments.append({'center': p, 'witnesses': list(witnesses),
                            'short_pair': [a, b], 'triangle': list(triangle)})
    selected_triangles = {tuple(t['triangle']) for t in assignments}
    require(len(selected_triangles) == len(assignments), "Different centers reused one triangle")
    require(len(assignments) <= graph['face_budget'], "Minimum-layer richness bound failed")
    rich = {t['center'] for t in assignments}
    return {'point_count': len(geo.points), 'radii_squared': list(map(str, rho)),
            'closer_counts': list(counts), 'minimum_radius_squared': str(r2),
            'minimum_layer': list(layer), 'rich_centers_in_minimum_layer': sorted(rich),
            'nonrich_centers_in_minimum_layer': [i for i in layer if i not in rich],
            'assignments': assignments, 'graph': graph}
