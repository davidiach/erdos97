#!/usr/bin/env python3
"""Independent exact checks for the seven-orbit right-angle packet.

This replays the stored final 138 cases and exact controls. It does NOT replace
full exhaustive regeneration by search.cpp/replay.py or external geometry review.
No floating-point operation is used here.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
import hashlib
from itertools import combinations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def decode(record: list) -> tuple:
    require(isinstance(record, list) and len(record) == 5, "five-field case required")
    index, masks, order, gains, rejecting = record
    require(type(index) is int and index >= 0, "invalid graph index")
    require(isinstance(masks, list) and 5 <= len(masks) <= 7, "unsupported orbit count")
    m = len(masks)
    require(all(type(v) is int and 0 <= v < 2**m and v.bit_count() == 2
                and not (v & (1 << i)) for i, v in enumerate(masks)), "invalid row mask")
    graph = [[j for j in range(m) if mask & (1 << j)] for mask in masks]
    require(all(i not in graph[j] for i, row in enumerate(graph) for j in row), "reciprocal graph")
    require(isinstance(order, list) and len(order) == m
            and all(type(v) is int for v in order) and set(order) == set(range(m))
            and order[0] == 0, "invalid normalized angular order")
    require(isinstance(gains, list) and len(gains) == 2*m
            and all(type(g) is int and 0 <= g < 3 for g in gains), "invalid rotation gains")
    pos = {v: i for i, v in enumerate(order)}
    for i, row in enumerate(graph):
        for k, j in enumerate(row):
            down = (1,) if pos[j] > pos[i] else (2,)
            up = (0, 2) if pos[j] > pos[i] else (0, 1)
            require(gains[2*i+k] in (down if j < i else up), "gain contradicts radial order")
    require(type(rejecting) is int and 0 <= rejecting < m, "invalid rejecting center")
    return graph, order, gains, rejecting


def expand(graph: list, order: list, gains: list) -> list:
    m = len(graph)
    pos = {v: i for i, v in enumerate(order)}
    rows = [[] for _ in range(3*m)]
    for i, targets in enumerate(graph):
        for p in range(3):
            rows[p*m+pos[i]] = [((p+1) % 3)*m+pos[i], ((p+2) % 3)*m+pos[i]] + [
                ((p+gains[2*i+k]) % 3)*m+pos[j] for k, j in enumerate(targets)]
    return rows


def crossing(a: int, b: int, c: int, d: int, n: int) -> bool:
    require(len({a, b, c, d}) == 4 and all(0 <= v < n for v in (a, b, c, d)),
            "four distinct chord endpoints required")
    # Circular traversal, rather than the C++ sorted-endpoint comparison.
    inside = set()
    v = (a+1) % n
    while v != b:
        inside.add(v)
        v = (v+1) % n
    return (c in inside) != (d in inside)


def right_certificate(record: list) -> dict:
    graph, order, gains, source = decode(record)
    m = len(graph)
    pos = {v: i for i, v in enumerate(order)}
    chords = []
    for k, j in enumerate(graph[source]):
        g = gains[2*source+k]
        chords.append([((g+1) % 3)*m+pos[j], ((g+2) % 3)*m+pos[j]])
    require(not crossing(*chords[0], *chords[1], 3*m), "opposite sides actually cross")
    return {"kind": "two_right_angles_noninterlacing", "source_orbit": source,
            "opposite_sides": chords}


def shortcut(graph: list) -> bool:
    # Exhaust increasing paths recursively, unlike either C++ closure routine.
    n = len(graph)
    for hi, row in enumerate(graph):
        for lo in row:
            if lo >= hi:
                continue
            def path(v: int, length: int) -> bool:
                if v == hi:
                    return length >= 2
                return any(path(w, length+1) for w in range(v+1, hi+1)
                           if w in graph[v] or v in graph[w])
            if path(lo, 0):
                return True
    return False


def distance_classes(rows: list) -> dict:
    # Explicit equality graph/components, not the C++ direct orbit-class assignment.
    pairs = list(combinations(range(len(rows)), 2))
    neighbors = defaultdict(set)
    for i, row in enumerate(rows):
        spokes = [tuple(sorted((i, j))) for j in row]
        for a, b in combinations(spokes, 2):
            neighbors[a].add(b)
            neighbors[b].add(a)
    classes = {}
    for pair in pairs:
        if pair in classes:
            continue
        representative = len(classes)
        stack = [pair]
        classes[pair] = representative
        while stack:
            for nxt in neighbors[stack.pop()]:
                if nxt not in classes:
                    classes[nxt] = representative
                    stack.append(nxt)
    return classes


def before_right_obstruction(record: list) -> str | None:
    graph, order, gains, _ = decode(record)
    if shortcut(graph):
        return "shortcut"
    rows = expand(graph, order, gains)
    m, n = len(graph), len(rows)
    for a, b in combinations(range(n), 2):
        common = sorted(set(rows[a]) & set(rows[b]))
        if len(common) > 2:
            return "two_circle"
        if len(common) == 2 and not crossing(a, b, *common, n):
            return "crossing_bisector"
    classes = distance_classes(rows)
    pos = {v: i for i, v in enumerate(order)}
    radial = [classes[pos[v], pos[v]+m] for v in range(m)]
    require(len(set(radial)) == m, "unexpected orbit radius identification")
    adjacent = defaultdict(set)
    for a, b in zip(radial, radial[1:]):
        adjacent[a].add(b)
    for a, b, c, d in combinations(range(n), 4):
        for negative in [((a, b), (c, d)), ((a, d), (b, c))]:
            coeff = Counter([classes[a, c], classes[b, d]])
            for edge in negative:
                coeff[classes[edge]] -= 1
            coeff = {k: v for k, v in coeff.items() if v}
            if not coeff:
                return "kalmanson_zero"
            if set(coeff) <= set(radial):
                values = [coeff.get(k, 0) for k in radial]
                if all(sum(values[i:]) <= 0 for i in range(1, m)):
                    return "radial_kalmanson"
            if len(coeff) == 2:
                positive = [k for k, v in coeff.items() if v > 0]
                negative_labels = [k for k, v in coeff.items() if v < 0]
                require(len(positive) == len(negative_labels) == 1, "unbalanced Kalmanson row")
                adjacent[negative_labels[0]].add(positive[0])
    # Topological deletion, not recursive DFS.
    vertices = set(adjacent) | {v for targets in adjacent.values() for v in targets}
    indegree = Counter(v for targets in adjacent.values() for v in targets)
    stack = [v for v in vertices if not indegree[v]]
    removed = 0
    while stack:
        u = stack.pop()
        removed += 1
        for v in adjacent.get(u, ()):
            indegree[v] -= 1
            if not indegree[v]:
                stack.append(v)
    return "kalmanson_cycle" if removed != len(vertices) else None


def polynomial_identity() -> bool:
    # Variables (x,y,u,v) stand for a=x+i sqrt(3)y, b=u+i sqrt(3)v.
    def mul(a, b):
        result = Counter()
        for i, x in enumerate(a):
            for j, y in enumerate(b):
                degree = [0]*4
                degree[i] += 1
                degree[j] += 1
                result[tuple(degree)] += x*y
        return result
    ax, ay = [Q(1), 0, 0, 0], [0, Q(1), 0, 0]
    bx, by = [0, 0, Q(1), 0], [0, 0, 0, Q(1)]
    cx, cy = [0, 0, Q(-1, 2), Q(-3, 2)], [0, 0, Q(1, 2), Q(-1, 2)]
    dx, dy = [0, 0, Q(-1, 2), Q(3, 2)], [0, 0, Q(-1, 2), Q(-1, 2)]
    def sub(a, b):
        return [x-y for x, y in zip(a, b)]
    terms = [(1, mul(sub(ax, bx), sub(ax, bx))), (3, mul(sub(ay, by), sub(ay, by))),
             (-3, mul(ax, ax)), (-9, mul(ay, ay)),
             (2, mul(sub(cx, ax), sub(dx, ax))), (6, mul(sub(cy, ay), sub(dy, ay)))]
    total = Counter()
    for weight, term in terms:
        for k, value in term.items():
            total[k] += weight*value
    require(not any(total.values()), "right-angle polynomial identity failed")
    return True


def controls() -> dict:
    def rotate(p):
        return (-(p[0]+3*p[1])/2, (p[0]-p[1])/2)

    def squared(a, b):
        return (a[0]-b[0])**2+3*(a[1]-b[1])**2

    def det(a, b, c):
        return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
    seeds = [(Q(1), Q(0)), (Q(-5, 7), Q(1, 7)), (Q(-5, 7), Q(-1, 7))]
    points = seeds + [rotate(p) for p in seeds] + [rotate(rotate(p)) for p in seeds]
    sorted_ids = sorted(range(9), key=points.__getitem__)
    def chain(ids):
        out = []
        for v in ids:
            while len(out) > 1 and det(points[out[-2]], points[out[-1]], points[v]) <= 0:
                out.pop()
            out.append(v)
        return out
    hull = chain(sorted_ids)[:-1]+chain(sorted_ids[::-1])[:-1]
    require(len(hull) == 9, "positive fixture lost strict hull vertices")
    require(all(det(points[hull[i]], points[hull[(i+1) % 9]], points[j]) > 0
                for i in range(9) for j in range(9) if j not in (hull[i], hull[(i+1) % 9])),
            "positive fixture supporting-edge failure")
    for j in (1, 2):
        require(squared(points[0], points[j]) == 3, "positive own-side arrow failed")
        u, v = points[j+3], points[j+6]
        dot = (u[0]-points[0][0])*(v[0]-points[0][0])+3*(u[1]-points[0][1])*(v[1]-points[0][1])
        require(dot == 0, "positive right angle failed")
    position = {v: i for i, v in enumerate(hull)}
    require(crossing(position[4], position[7], position[5], position[8], 9),
            "positive opposite sides should cross")
    multiplicities = Counter(max(Counter(squared(p, q) for j, q in enumerate(points) if j != i).values())
                             for i, p in enumerate(points))
    require(multiplicities == {4: 3, 2: 6}, "positive fixture multiplicity mismatch")
    # Without an extreme center the two 90-degree intervals can be disjoint.
    a, b, c, d = (1, 0), (0, 1), (-1, 0), (0, -1)
    require(a[0]*b[0]+a[1]*b[1] == c[0]*d[0]+c[1]*d[1] == 0, "interior control angles")
    require(not crossing(0, 1, 2, 3, 4), "interior-center control chords")
    return {"symbolic_identity": polynomial_identity(), "positive_nine_point_hull": hull,
            "positive_multiplicity_distribution": {str(k): v for k, v in multiplicities.items()},
            "two_right_angles_and_crossing": True, "extreme_center_hypothesis_control": True}


def audit_frontier(path: Path = ROOT / "frontier.json", full: bool = True) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    require(payload["schema"] == 1, "frontier schema mismatch")
    records = payload["records"]
    require(len(records) == 138, "frontier must have 138 ordered cases")
    require(len({digest(r[:4]) for r in records}) == len(records), "duplicate frontier case")
    certificates = []
    for record in records:
        if full:
            require(before_right_obstruction(record) is None, "stored case failed an earlier filter")
        certificates.append(right_certificate(record))
    return {"records": len(records), "certificates": len(certificates),
            "records_sha256": digest(records), "certificates_sha256": digest(certificates),
            "earlier_filters_replayed": full, "controls": controls()}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--skip-earlier-filters", action="store_true")
    args = parser.parse_args()
    result = audit_frontier(full=not args.skip_earlier_filters)
    if args.check:
        report = json.loads((ROOT / "report.json").read_text(encoding="utf-8"))
        for key in ("records_sha256", "certificates_sha256"):
            require(result[key] == report["frontier"][key], f"{key} mismatch")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
