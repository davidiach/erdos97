"""Exact necessary-condition models for four concentric C3 orbits.

Every row in A is strict and every row in E is an equality.  The models
are necessary, never asserted sufficient, for the indicated convex geometry.
No floating-point arithmetic or third-party package is used in this file.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
from typing import Iterable

Row = tuple[int, ...]
Matrix = list[Row]
Case = tuple[int, int, int]  # cyclic topology, base-three gain code, mode


def require(test: bool, message: str) -> None:
    if not test:
        raise ValueError(message)


def subtract(a: Row, b: Row) -> Row:
    return tuple(x - y for x, y in zip(a, b))


def unique(rows: Iterable[Row], *, drop_zero: bool = False) -> Matrix:
    return sorted(set(row for row in rows if not drop_zero or any(row)))


class OrbitPairs:
    """The simultaneous-rotation classes of unordered vertex pairs."""

    def __init__(self, m: int = 4) -> None:
        require(m >= 2, "at least two orbits required")
        self.m, self.n = m, 3 * m
        self.pairs = list(combinations(range(self.n), 2))
        self.classes: dict[tuple[int, int, int], int] = {}
        self.pair_class: dict[tuple[int, int], int] = {}
        self.angle_offset: dict[tuple[int, int], int] = {}
        representatives: dict[tuple[int, int, int], tuple[int, int]] = {}
        for a, b in self.pairs:
            i, k = a % m, a // m
            j, l = b % m, b // m
            if i == j:
                key = (i, i, 0)
            elif i < j:
                key = (i, j, (l - k) % 3)
            else:
                key = (j, i, (k - l) % 3)
            if key not in self.classes:
                self.classes[key] = len(self.classes)
                representatives[key] = (a, b)
            self.pair_class[a, b] = self.classes[key]
            difference = a + b - sum(representatives[key])
            require(difference % m == 0, "invalid angular orbit offset")
            self.angle_offset[a, b] = difference // m
        self.count = len(self.classes)
        require(self.count == m + 3 * m * (m - 1) // 2, "pair class count")

    def pair(self, a: int, b: int) -> int:
        require(a != b, "self pair")
        return self.pair_class[tuple(sorted((a, b)))]

    def quotient(self, arrows: list[tuple[int, int, int]]) -> list[int]:
        parent = list(range(self.count))

        def root(a: int) -> int:
            while parent[a] != a:
                a = parent[a]
            return a

        for a, b, gain in arrows:
            require(0 <= a < self.m and 0 <= b < self.m and a != b, "invalid arrow")
            require(gain in (0, 1, 2), "invalid gain")
            x = root(self.classes[a, a, 0])
            y = root(self.pair(a, b + self.m * gain))
            parent[max(x, y)] = min(x, y)
        roots = [root(a) for a in range(self.count)]
        labels = {a: i for i, a in enumerate(sorted(set(roots)))}
        return [labels[a] for a in roots]


def decode_case(case: Case) -> tuple[list[tuple[int, int, int]], list[tuple[int, int]]]:
    topology, gain_code, mode = case
    require(topology in (0, 1) and 0 <= gain_code < 81 and mode in (0, 1, 2), "invalid case")
    sources = (0, 1) if topology == 0 else (0, 2)
    targets = tuple(i for i in range(4) if i not in sources)
    gains = [(gain_code // (3 ** (3 - i))) % 3 for i in range(4)]
    arrows = [(a, b, g) for (a, b), g in zip(product(sources, targets), gains)]
    # Each pair (a,b) asserts r_a > r_b, equivalently own-side length_a > length_b.
    if mode == 0:
        greater = [(b, a) for a in sources for b in targets]  # both sources below
    else:
        greater = [(sources[mode - 1], b) for b in targets]  # one source above both
    return arrows, greater


def all_cases() -> list[Case]:
    return list(product(range(2), range(81), range(3)))


class AngleModel:
    def __init__(self, m: int = 4) -> None:
        self.orbits = o = OrbitPairs(m)
        self.dimension = o.count + 1
        self.triangles: list[tuple[list[Row], list[tuple[int, int]]]] = []
        positive: Matrix = []

        def angle(plus: tuple[int, int], minus: tuple[int, int], constant: int = 0) -> Row:
            row = [0] * self.dimension
            row[o.pair(*plus)] += 1
            row[o.pair(*minus)] -= 1
            row[-1] = constant + o.angle_offset[plus] - o.angle_offset[minus]
            return tuple(row)

        for a, b, c in combinations(range(o.n), 3):
            # These are THREE times the triangle angles at a,b,c, respectively.
            angles = [angle((a, c), (a, b)), angle((a, b), (b, c), 3),
                      angle((b, c), (a, c))]
            opposite_edges = [(b, c), (a, c), (a, b)]
            self.triangles.append((angles, opposite_edges))
            positive.extend(angles)
        positive.append(tuple([0] * o.count + [1]))  # pi > 0
        self.positive = unique(positive)

    def build(self, arrows: list[tuple[int, int, int]], greater: list[tuple[int, int]]) -> tuple[Matrix, Matrix]:
        o = self.orbits
        classes = o.quotient(arrows)
        own = [classes[o.classes[i, i, 0]] for i in range(o.m)]
        ordered = {(own[a], own[b]) for a, b in greater}
        inequalities = list(self.positive)
        equations: Matrix = []
        for angles, edges in self.triangles:
            labels = [classes[o.pair(*e)] for e in edges]
            for i, j in combinations(range(3), 2):
                if labels[i] == labels[j]:
                    equations.append(subtract(angles[i], angles[j]))
                if (labels[i], labels[j]) in ordered:
                    inequalities.append(subtract(angles[i], angles[j]))
                if (labels[j], labels[i]) in ordered:
                    inequalities.append(subtract(angles[j], angles[i]))
        gauge = [0] * self.dimension
        gauge[o.pair(0, 1)] = 1
        gauge[-1] = o.angle_offset[0, 1]
        equations.append(tuple(gauge))
        return unique(inequalities), unique(equations, drop_zero=True)


class MetricModel:
    def __init__(self, m: int = 4) -> None:
        self.orbits = o = OrbitPairs(m)
        rows: Matrix = []

        def terms(items: list[tuple[int, int, int]]) -> Row:
            row = [0] * o.count
            for a, b, coefficient in items:
                row[o.pair(a, b)] += coefficient
            return tuple(row)

        for a, b, c, d in combinations(range(o.n), 4):
            rows.append(terms([(a, c, 1), (b, d, 1), (a, b, -1), (c, d, -1)]))
            rows.append(terms([(a, c, 1), (b, d, 1), (a, d, -1), (b, c, -1)]))
        for a, b, c in combinations(range(o.n), 3):
            for x, y, z in [(a, b, c), (b, c, a), (c, a, b)]:
                rows.append(terms([(x, y, 1), (y, z, 1), (x, z, -1)]))
        for i in range(o.count):
            row = [0] * o.count
            row[i] = 1
            rows.append(tuple(row))
        self.positive = unique(rows)

    def build(self, arrows: list[tuple[int, int, int]], greater: list[tuple[int, int]]) -> tuple[Matrix, Matrix]:
        o = self.orbits
        classes = o.quotient(arrows)
        dimension = max(classes) + 1
        inequalities: Matrix = []
        for row in self.positive:
            reduced = [0] * dimension
            for j, c in enumerate(row):
                reduced[classes[j]] += c
            inequalities.append(tuple(reduced))
        for a, b in greater:
            row = [0] * dimension
            row[classes[o.classes[a, a, 0]]] += 1
            row[classes[o.classes[b, b, 0]]] -= 1
            inequalities.append(tuple(row))
        return unique(inequalities), []


def verify_certificate(A: Matrix, E: Matrix, positive: list[list[int]], equality: list[list[int]]) -> None:
    require(bool(A), "empty strict system")
    require(bool(positive), "certificate has no strict positive term")
    residual = [0] * len(A[0])
    for collection, terms, strict in [(A, positive, True), (E, equality, False)]:
        used: set[int] = set()
        for term in terms:
            require(isinstance(term, list) and len(term) == 2, "bad certificate term")
            index, weight = term
            require(type(index) is int and type(weight) is int, "noninteger certificate")
            require(0 <= index < len(collection) and index not in used, "invalid/repeated row index")
            require(weight > 0 if strict else weight != 0, "invalid multiplier sign")
            used.add(index)
            for j, c in enumerate(collection[index]):
                residual[j] += weight * c
    require(not any(residual), "nonzero certificate residual")


def check_rational_feasible(A: Matrix, E: Matrix, vector: list[str]) -> None:
    require(len(vector) == len(A[0]), "feasible-vector dimension")
    point = [Fraction(x) for x in vector]
    require(all(sum(c * x for c, x in zip(row, point)) > 0 for row in A), "strict feasibility failed")
    require(all(sum(c * x for c, x in zip(row, point)) == 0 for row in E), "equality feasibility failed")
