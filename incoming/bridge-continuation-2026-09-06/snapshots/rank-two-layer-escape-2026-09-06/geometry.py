"""Exact rational geometry for the rank-two layer-escape research packet.

Coordinates are (x, sqrt(vertical_scale_squared) * y), with rational x,y.
All comparisons use rational squared distances and determinant coefficients.
Finite checks do not constitute formal verification of the paper proofs.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction
from itertools import combinations
from typing import Any, Iterable

Q = Fraction
Point = tuple[Q, Q]
Edge = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rational(value: Any) -> Q:
    require(isinstance(value, (str, int, Q)) and not isinstance(value, bool),
            'Use exact rational strings, integers, or Fractions; floats are rejected.')
    return Q(value)


def edge(a: int, b: int) -> Edge:
    require(a != b, 'An edge needs distinct endpoints.')
    return (min(a, b), max(a, b))


def determinant(a: Point, b: Point, c: Point) -> Q:
    return ((b[0]-a[0])*(c[1]-a[1])
            - (b[1]-a[1])*(c[0]-a[0]))


def unit(t: Any) -> Point:
    t = rational(t)
    return ((1-t*t)/(1+t*t), 2*t/(1+t*t))


class Geometry:
    def __init__(self, points: Iterable[Iterable[Any]], vertical_scale_squared: Any = 1):
        self.points = [tuple(rational(x) for x in p) for p in points]
        require(bool(self.points), 'The point set must be nonempty.')
        require(all(len(p) == 2 for p in self.points), 'Points must have two coordinates.')
        require(len(set(self.points)) == len(self.points), 'Repeated point.')
        self.scale = rational(vertical_scale_squared)
        require(self.scale > 0, 'The vertical scale must be positive.')
        self.n = len(self.points)
        self.order = self._hull()
        require(len(self.order) == self.n, 'The points are not in strictly convex position.')
        self.pos = {v: j for j, v in enumerate(self.order)}
        self.d2 = [[self._distance2(i, j) for j in range(self.n)] for i in range(self.n)]
        self.support_count = 0
        self.minimum_support = None
        if self.n >= 3:
            margins = []
            for i, a in enumerate(self.order):
                b = self.order[(i+1) % self.n]
                for c in range(self.n):
                    if c not in (a, b):
                        value = determinant(self.points[a], self.points[b], self.points[c])
                        require(value > 0, 'A supporting-line inequality is not strict.')
                        margins.append(value)
            self.support_count = len(margins)
            self.minimum_support = min(margins)

    def _hull(self) -> list[int]:
        ids = sorted(range(self.n), key=lambda i: self.points[i])
        if self.n <= 2:
            return ids
        answer = []
        for seq in (ids, ids[::-1]):
            chain: list[int] = []
            for i in seq:
                while (len(chain) >= 2 and determinant(
                        self.points[chain[-2]], self.points[chain[-1]], self.points[i]) <= 0):
                    chain.pop()
                chain.append(i)
            answer.extend(chain[:-1])
        return answer

    def _distance2(self, i: int, j: int) -> Q:
        a, b = self.points[i], self.points[j]
        return (a[0]-b[0])**2 + self.scale*(a[1]-b[1])**2

    def crosses(self, e: Edge, f: Edge) -> bool:
        if len(set(e+f)) != 4:
            return False
        a, b = (self.pos[i] for i in e)
        c, d = (self.pos[i] for i in f)
        def inside(x: int) -> bool:
            return 0 < (x-a) % self.n < (b-a) % self.n
        return inside(c) != inside(d)

    def crossings(self, edges: Iterable[Edge]) -> list[list[list[int]]]:
        return [[list(e), list(f)] for e, f in combinations(sorted(set(edges)), 2)
                if self.crosses(e, f)]

    def blockers(self, e: Edge) -> list[int]:
        a, b = e
        # A point k is in the closed disk of diameter ab exactly when this holds.
        return [k for k in range(self.n) if k not in e
                and self.d2[a][k] + self.d2[k][b] <= self.d2[a][b]]

    def multiplicities(self) -> list[int]:
        return [max(Counter(self.d2[i][j] for j in range(self.n) if j != i).values(), default=0)
                for i in range(self.n)]

    def rows(self, radii2: Iterable[Any]) -> dict[str, Any]:
        r = [rational(x) for x in radii2]
        require(len(r) == self.n and all(x > 0 for x in r), 'Invalid squared radii.')
        closer = [[j for j in range(self.n) if j != i and self.d2[i][j] < r[i]]
                  for i in range(self.n)]
        witnesses = [[j for j in range(self.n) if j != i and self.d2[i][j] == r[i]]
                     for i in range(self.n)]
        return {'radii_squared': r, 'closer': closer, 'witnesses': witnesses}

    def crossing_diagonal_lemma(self) -> dict[str, int]:
        count = 0
        for quad in combinations(self.order, 4):
            found = []
            for k, v in enumerate(quad):
                a, b, opposite = quad[(k-1) % 4], quad[(k+1) % 4], quad[(k+2) % 4]
                if self.d2[v][a] < self.d2[v][opposite] and self.d2[v][b] < self.d2[v][opposite]:
                    found.append(v)
            require(bool(found), 'Crossing-diagonal endpoint lemma failed.')
            count += 1
        return {'quadrilaterals': count}

    def mutual_short(self, radii2: Iterable[Any]) -> dict[str, Any]:
        rows = self.rows(radii2)
        require(max(map(len, rows['closer']), default=0) <= 2, 'More than two closer vertices.')
        r = rows['radii_squared']
        edges = {e for e in combinations(range(self.n), 2) if self.d2[e[0]][e[1]] < min(r[e[0]], r[e[1]])}
        deg = Counter(v for e in edges for v in e)
        require(max(deg.values(), default=0) <= 2, 'Mutual short degree exceeds two.')
        crossings = self.crossings(edges)
        require(not crossings, 'Mutual short edges cross.')
        return {'edges': sorted(edges), 'degrees': [deg[i] for i in range(self.n)],
                'crossings': crossings}

    def components(self, edges: Iterable[Edge]) -> list[dict[str, Any]]:
        adj = {i: set() for i in range(self.n)}
        for a, b in edges:
            adj[a].add(b); adj[b].add(a)
        unseen = set(range(self.n)); components = []
        while unseen:
            root = min(unseen); todo = [root]; vertices = set()
            while todo:
                v = todo.pop()
                if v in vertices:
                    continue
                vertices.add(v); unseen.discard(v); todo.extend(adj[v]-vertices)
            s = sum(len(adj[v]) for v in vertices)//2
            if len(vertices) == 1:
                kind = 'isolated'
            elif s == len(vertices)-1 and all(len(adj[v]) <= 2 for v in vertices):
                kind = 'path'
            elif s == len(vertices) and all(len(adj[v]) == 2 for v in vertices):
                kind = 'cycle'
            else:
                raise ValueError('A short component is neither a path nor a cycle.')
            components.append({'vertices': sorted(vertices, key=self.pos.get), 'kind': kind})
        return components

    def triangulation(self, initial: set[Edge]) -> set[Edge]:
        require(not self.crossings(initial), 'Cannot extend a crossing graph.')
        if self.n <= 2:
            return set(combinations(range(self.n), 2))
        out = set(initial)
        for j, a in enumerate(self.order):
            out.add(edge(a, self.order[(j+1) % self.n]))
        for e in combinations(range(self.n), 2):
            if e not in out and not any(self.crosses(e, f) for f in out):
                out.add(e)
        require(len(out) == 2*self.n-3 and not self.crossings(out), 'Triangulation completion failed.')
        return out

    def threshold(self, radius_squared: Any) -> dict[str, Any]:
        r = rational(radius_squared)
        require(r > 0, 'The threshold must be positive.')
        short = {e for e in combinations(range(self.n), 2) if self.d2[e[0]][e[1]] < r}
        unit_edges = {e for e in combinations(range(self.n), 2) if self.d2[e[0]][e[1]] == r}
        degrees = Counter(v for e in short for v in e)
        require(max(degrees.values(), default=0) <= 2, 'Threshold short degree exceeds two.')
        require(not self.crossings(short), 'Short edges cross.')
        components = self.components(short)
        paths = sum(c['kind'] == 'path' for c in components)
        cycles = [c['vertices'] for c in components if c['kind'] == 'cycle']
        triangles = [c for c in cycles if len(c) == 3]
        long_cycles = [c for c in cycles if len(c) >= 4]
        triangle_vertices = {v for c in triangles for v in c}
        gab_short = {e for e in short if not self.blockers(e)}
        gab_unit = {e for e in unit_edges if not self.blockers(e)}
        gab = gab_short | gab_unit
        require(not self.crossings(gab), 'Strict Gabriel edges cross.')
        require(len(short-gab_short) <= len(triangles), 'Too many non-Gabriel short edges.')
        blocked = {}
        for e in sorted(unit_edges-gab_unit):
            blockers = self.blockers(e)
            require(bool(blockers), 'Missing blocker.')
            v = blockers[0]
            require(degrees[v] == 2 and v not in triangle_vertices, 'Invalid unit-edge blocker.')
            require({edge(v, e[0]), edge(v, e[1])} <= short, 'Blocker does not define two short edges.')
            require(v not in blocked, 'One blocker was assigned two different endpoint pairs.')
            blocked[v] = e
        capacity = {v for v in range(self.n) if degrees[v] == 2 and v not in triangle_vertices}
        unused = capacity-set(blocked)
        tri = self.triangulation(gab)
        added = tri-gab
        charges: list[dict[str, Any]] = []
        used_charges = set()
        for cyc in long_cycles:
            k = len(cyc)
            require(all(edge(cyc[j], cyc[(j+1) % k]) in gab_short for j in range(k)),
                    'A long short cycle has a non-Gabriel side.')
            ears = [j for j in range(k) if edge(cyc[(j-1) % k], cyc[(j+1) % k]) in tri]
            require(len(ears) >= 2, 'A triangulated cycle has fewer than two ears.')
            for j in ears[:2]:
                v = cyc[j]; base = edge(cyc[(j-1) % k], cyc[(j+1) % k])
                if v in blocked:
                    require(blocked[v] == base and base in added, 'Ear-edge charge failed.')
                    key = ('edge', base)
                    item = {'ear_vertex': v, 'charged_added_edge': base}
                else:
                    require(v in unused, 'Ear-vertex charge failed.')
                    key = ('vertex', v)
                    item = {'ear_vertex': v, 'charged_unused_blocker': v}
                require(key not in used_charges, 'A cycle charge was reused.')
                used_charges.add(key); charges.append(item)
        require(len(unused)+len(added) >= 2*len(long_cycles), 'Cycle deficit inequality failed.')
        bound = 0 if self.n == 1 else 2*self.n-3-paths-2*len(cycles)
        require(len(unit_edges) <= bound, 'The fixed-radius edge bound failed.')
        return {'point_count': self.n, 'radius_squared': r, 'short_edges': sorted(short),
                'unit_edges': sorted(unit_edges), 'short_degrees': [degrees[i] for i in range(self.n)],
                'short_components': components, 'nontrivial_short_paths': paths,
                'short_cycles': len(cycles), 'strict_gabriel_edges': sorted(gab),
                'non_gabriel_unit_blockers': [[list(e), v] for v, e in sorted(blocked.items())],
                'triangulation_added_edges': sorted(added), 'unused_blocker_vertices': sorted(unused),
                'cycle_ear_charges': charges, 'unit_edge_count': len(unit_edges),
                'unit_edge_bound': bound}

    def layer_escape(self, radii2: Iterable[Any]) -> dict[str, Any]:
        rows = self.rows(radii2)
        require(max(map(len, rows['closer']), default=0) <= 2, 'More than two closer vertices.')
        r = min(rows['radii_squared'])
        layer = [i for i in range(self.n) if rows['radii_squared'][i] == r]
        rich = [i for i in layer if len(rows['witnesses'][i]) >= 4]
        result: dict[str, Any] = {'minimum_radius_squared': r, 'minimum_layer': layer,
            'rich_minimum_vertices': rich, 'all_minimum_vertices_rich': rich == layer}
        if rich != layer:
            return result
        exports = [(i, j) for i in layer for j in rows['witnesses'][i] if j not in layer]
        targets = sorted({j for i, j in exports})
        require(len(targets) >= 4, 'Four-target escape failed.')
        require(all(r < rows['radii_squared'][j] < 4*r for j in targets), 'Strict factor-two band failed.')
        if len(layer) >= 2:
            sub = Geometry([self.points[i] for i in layer], self.scale)
            certificate = sub.threshold(r)
            lower = 6 + 2*certificate['nontrivial_short_paths'] + 4*certificate['short_cycles']
            require(len(exports) >= lower, 'The layer export count failed.')
            result['layer_threshold_certificate'] = certificate
        else:
            lower = 4
        result.update({'exported_incidences': exports, 'export_count': len(exports),
                       'export_lower_bound': lower, 'higher_radius_targets': targets,
                       'target_radii_squared': [rows['radii_squared'][j] for j in targets]})
        return result


def contains_disk(container_radius2: Any, contained_radius2: Any, centers_distance2: Any) -> bool:
    a, b, d = map(rational, (container_radius2, contained_radius2, centers_distance2))
    require(a > 0 and b > 0 and d >= 0, 'Invalid disk data.')
    z = a-b-d
    return z >= 0 and z*z >= 4*b*d


def jsonable(x: Any) -> Any:
    if isinstance(x, Q):
        return str(x)
    if isinstance(x, dict):
        return {str(k): jsonable(v) for k, v in x.items()}
    if isinstance(x, (tuple, list, set)):
        return [jsonable(v) for v in x]
    return x
