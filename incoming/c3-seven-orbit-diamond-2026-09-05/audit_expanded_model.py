#!/usr/bin/env python3
"""Cross-check folded models using all 66 chord variables and explicit rotations.

This independently reconstructs the finite encodings. It is not an independent
proof of their geometric soundness or a second external mathematical review.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations
import json

from core import AngleModel, MetricModel, all_cases, decode_case, require


class ExpandedEncoding:
    def __init__(self, m: int = 4):
        self.m, self.n = m, 3 * m
        self.pairs = list(combinations(range(self.n), 2))
        self.pair_id = {p: i for i, p in enumerate(self.pairs)}
        self.dimension = len(self.pairs) + 1
        self.rotation = []
        graph = [[] for _ in self.pairs]
        for i, (a, b) in enumerate(self.pairs):
            wraps = int(a + m >= self.n) + int(b + m >= self.n)
            target = self.index((a + m) % self.n, (b + m) % self.n)
            change = 2 - 3 * wraps  # Change of three times the chord direction, in pi units.
            self.rotation.append((i, target))
            graph[i].append((target, change))
            graph[target].append((i, -change))
        self.component = [-1] * len(self.pairs)
        self.offset = [0] * len(self.pairs)
        count = 0
        for first in range(len(self.pairs)):
            if self.component[first] >= 0:
                continue
            self.component[first] = count
            queue = deque([first])
            while queue:
                a = queue.popleft()
                for b, change in graph[a]:
                    if self.component[b] < 0:
                        self.component[b] = count
                        self.offset[b] = self.offset[a] + change
                        queue.append(b)
                    else:
                        require(self.component[b] == count and self.offset[b] == self.offset[a] + change,
                                'inconsistent rotation cycle')
            count += 1
        self.classes = count

    def index(self, a, b):
        return self.pair_id[min(a, b), max(a, b)]

    def row(self, terms=(), pi=0):
        result = [0] * self.dimension
        for a, b, coefficient in terms:
            result[self.index(a, b)] += coefficient
        result[-1] = pi
        return result

    def project_angles(self, row):
        result = [0] * (self.classes + 1)
        result[-1] = row[-1]
        for i, coefficient in enumerate(row[:-1]):
            result[self.component[i]] += coefficient
            result[-1] += self.offset[i] * coefficient
        return tuple(result)

    def lengths(self, arrows):
        # Whole-class relabeling instead of the folded model's disjoint set.
        labels = list(range(len(self.pairs)))
        def merge(a, b):
            low, high = sorted((labels[a], labels[b]))
            for k, value in enumerate(labels):
                if value == high:
                    labels[k] = low
        for a, b in self.rotation:
            merge(a, b)
        for source, target, gain in arrows:
            for layer in range(3):
                a = source + self.m * layer
                b = target + self.m * ((layer + gain) % 3)
                mate = source + self.m * ((layer + 1) % 3)
                merge(self.index(a, b), self.index(a, mate))
        distinct = sorted(set(labels))
        return [distinct.index(i) for i in labels]

    def angles(self, arrows, greater):
        labels = self.lengths(arrows)
        own = [labels[self.index(i, i + self.m)] for i in range(self.m)]
        larger = {(own[a], own[b]) for a, b in greater}
        A = {self.project_angles(self.row(pi=1))}
        E = {self.project_angles(self.row([(0, 1, 1)]))}
        for a, b, c in combinations(range(self.n), 3):
            angles = [self.row([(a, c, 1), (a, b, -1)]),
                      self.row([(a, b, 1), (b, c, -1)], pi=3),
                      self.row([(b, c, 1), (a, c, -1)])]
            opposite = [labels[self.index(b, c)], labels[self.index(a, c)], labels[self.index(a, b)]]
            A.update(self.project_angles(row) for row in angles)
            for i, j in combinations(range(3), 2):
                difference = [x - y for x, y in zip(angles[i], angles[j])]
                projected = self.project_angles(difference)
                if opposite[i] == opposite[j] and any(projected):
                    E.add(projected)
                if (opposite[i], opposite[j]) in larger:
                    A.add(projected)
                if (opposite[j], opposite[i]) in larger:
                    A.add(tuple(-v for v in projected))
        return sorted(A), sorted(E)

    def metric(self, arrows, greater):
        labels = self.lengths(arrows)
        dimension = max(labels) + 1
        def project(row):
            require(row[-1] == 0, 'unexpected metric constant')
            result = [0] * dimension
            for i, coefficient in enumerate(row[:-1]):
                result[labels[i]] += coefficient
            return tuple(result)
        A = set()
        for a, b, c, d in combinations(range(self.n), 4):
            for negatives in [[(a, b, -1), (c, d, -1)], [(a, d, -1), (b, c, -1)]]:
                A.add(project(self.row([(a, c, 1), (b, d, 1), *negatives])))
        for a, b, c in combinations(range(self.n), 3):
            edges = [(a, b), (a, c), (b, c)]
            for negative in range(3):
                A.add(project(self.row([(u, v, -1 if i == negative else 1)
                                        for i, (u, v) in enumerate(edges)])))
        for a, b in self.pairs:
            A.add(project(self.row([(a, b, 1)])))
        for a, b in greater:
            A.add(project(self.row([(a, a + self.m, 1), (b, b + self.m, -1)])))
        return sorted(A), []


def audit():
    expanded = ExpandedEncoding()
    angle, metric = AngleModel(), MetricModel()
    for case in all_cases():
        arrows, greater = decode_case(case)
        require(expanded.angles(arrows, greater) == angle.build(arrows, greater),
                f'angle model disagreement: {case}')
        require(expanded.metric(arrows, greater) == metric.build(arrows, greater),
                f'metric model disagreement: {case}')
    return {'status': 'passed', 'cases_compared': len(all_cases()),
            'expanded_chords': len(expanded.pairs), 'folded_chord_classes': expanded.classes,
            'angle_and_metric_disagreements': 0,
            'scope': 'two finite encodings agree; geometric soundness remains a written review obligation'}


if __name__ == '__main__':
    print(json.dumps(audit(), sort_keys=True))
