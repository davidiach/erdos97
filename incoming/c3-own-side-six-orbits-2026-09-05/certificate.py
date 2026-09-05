#!/usr/bin/env python3
"""Exact finite certificates for one six-C3-orbit graph, not Erdős #97.

The geometric reduction is proved in README.md. This standard-library module
regenerates every reduced case and verifies its explicit contradiction. It
neither solves arbitrary six-orbit systems nor treats an abstract survivor as
Euclidean. No floating-point operation is used.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations, product
import json
from pathlib import Path

ROWS = ((4, 5), (4, 5), (0, 1), (0, 1), (2, 3), (2, 3))
CANONICAL = ((0, 1, 2, 3, 4, 5), (0, 2, 3, 4, 5, 1))
EXPECTED = ({"crossing": 1712, "kalmanson_inverse": 208},
            {"crossing": 1600, "kalmanson_inverse": 320})
SCOPE = "Fixed six-orbit K2,2,2 directed cycle; all radii and phases; review pending."


def digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def automorphisms() -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(2 * ((v // 2 + shift) % 3) + ((v % 2) ^ flips[v // 2])
                       for v in range(6))
                 for shift in range(3) for flips in product(range(2), repeat=3))


def radius_audit() -> list[dict]:
    """Classify all total radius orders, allowing arbitrary within-pair tie breaks."""
    autos = automorphisms()
    for image in autos:
        if any({image[w] for w in ROWS[v]} != set(ROWS[image[v]]) for v in range(6)):
            raise ValueError("invalid graph automorphism")
    records = []
    for order in permutations(range(6)):
        rank = {v: i for i, v in enumerate(order)}
        bad = None
        for triangle in product((0, 1), (2, 3), (4, 5)):
            lo, mid, hi = sorted(triangle, key=rank.__getitem__)
            if lo in ROWS[hi]:
                bad = [lo, mid, hi]
                break
        if bad is not None:
            records.append({"order": order, "downward_triangle": bad})
        else:
            canonical, image = min((tuple(g[v] for v in order), g) for g in autos)
            if canonical not in CANONICAL:
                raise ValueError(f"uncovered radial order: {order}")
            records.append({"order": order, "canonical": canonical, "image": image})
    return records


def allowed_gains(source: int, target: int, rank: dict, pos: dict) -> tuple[int, ...]:
    """Angle restriction from cos(theta) = u/2 - 1/u; see README."""
    if rank[target] < rank[source]:
        return (1 if pos[target] > pos[source] else 2,)
    return (0, 2 if pos[target] > pos[source] else 1)


def cases(radial_order: tuple[int, ...], graph=ROWS):
    rank = {v: i for i, v in enumerate(radial_order)}
    for tail in permutations(range(1, 6)):
        order = (0,) + tail
        pos = {v: i for i, v in enumerate(order)}
        choices = [allowed_gains(v, w, rank, pos) for v in range(6) for w in graph[v]]
        for gains in product(*choices):
            yield order, gains


def expand(order: tuple[int, ...], gains: tuple[int, ...], graph=ROWS) -> list[list[int]]:
    if len(order) != 6 or set(order) != set(range(6)):
        raise ValueError("angle order must be a permutation of six labels")
    if len(gains) != 12 or any(type(g) is not int or g not in range(3) for g in gains):
        raise ValueError("twelve rotation gains in {0,1,2} required")
    pos = {v: i for i, v in enumerate(order)}
    rows = [[] for _ in range(18)]
    for v in range(6):
        for phase in range(3):
            row = [6 * ((phase + 1) % 3) + pos[v], 6 * ((phase + 2) % 3) + pos[v]]
            row += [6 * ((phase + gains[2 * v + k]) % 3) + pos[w]
                    for k, w in enumerate(graph[v])]
            rows[6 * phase + pos[v]] = sorted(row)
    return rows


def crosses(a: int, b: int, c: int, d: int, n: int) -> bool:
    return len({a, b, c, d}) == 4 and (
        (0 < (c - a) % n < (b - a) % n) != (0 < (d - a) % n < (b - a) % n))


def distance_classes(rows: list[list[int]], independent: bool = False) -> dict:
    pairs = list(combinations(range(len(rows)), 2))
    pair_id = {edge: i for i, edge in enumerate(pairs)}
    spokes = [[pair_id[tuple(sorted((i, j)))] for j in row] for i, row in enumerate(rows)]
    if independent:
        # Certificate replay uses graph components rather than the search DSU.
        adjacency = [set() for _ in pairs]
        for row in spokes:
            for a, b in combinations(row, 2):
                adjacency[a].add(b)
                adjacency[b].add(a)
        labels = [-1] * len(pairs)
        for start in range(len(pairs)):
            if labels[start] >= 0:
                continue
            stack = [start]
            labels[start] = start
            while stack:
                for nxt in adjacency[stack.pop()]:
                    if labels[nxt] < 0:
                        labels[nxt] = start
                        stack.append(nxt)
    else:
        labels = list(range(len(pairs)))

        def root(x: int) -> int:
            while x != labels[x]:
                labels[x] = labels[labels[x]]
                x = labels[x]
            return x

        for row in spokes:
            for other in row[1:]:
                a, b = root(row[0]), root(other)
                labels[max(a, b)] = min(a, b)
        labels = [root(i) for i in range(len(pairs))]
    return dict(zip(pairs, labels))


def inequality_coefficients(spec: list[int], classes: dict, n: int) -> tuple:
    if (len(spec) != 5 or any(type(v) is not int for v in spec)
            or not 0 <= spec[0] < spec[1] < spec[2] < spec[3] < n
            or spec[4] not in (0, 1)):
        raise ValueError("invalid strict Kalmanson inequality")
    a, b, c, d, side = spec
    positive = ((a, c), (b, d))
    negative = ((a, b), (c, d)) if side == 0 else ((a, d), (b, c))
    coefficients = Counter(classes[e] for e in positive)
    for edge in negative:
        coefficients[classes[edge]] -= 1
    return tuple(sorted((k, v) for k, v in coefficients.items() if v))


def find_certificate(rows: list[list[int]]) -> dict | None:
    n = len(rows)
    for a, b in combinations(range(n), 2):
        common = sorted(set(rows[a]) & set(rows[b]))
        if len(common) > 2:
            return {"kind": "two_circle", "centers": [a, b], "witnesses": common[:3]}
        if len(common) == 2 and not crosses(a, b, *common, n):
            return {"kind": "crossing", "centers": [a, b], "witnesses": common}
    classes = distance_classes(rows)
    seen = {}
    for quad in combinations(range(n), 4):
        for side in range(2):
            spec = list(quad) + [side]
            key = inequality_coefficients(spec, classes, n)
            if not key:
                return {"kind": "kalmanson_zero", "inequalities": [spec]}
            inverse = tuple((k, -v) for k, v in key)
            if inverse in seen:
                return {"kind": "kalmanson_inverse", "inequalities": [seen[inverse], spec]}
            seen[key] = spec
    return None


def verify_certificate(rows: list[list[int]], certificate: dict) -> None:
    n = len(rows)
    if any(not row or len(set(row)) != len(row)
           or any(type(j) is not int or not 0 <= j < n or i == j for j in row)
           for i, row in enumerate(rows)):
        raise ValueError("invalid selected rows")
    kind = certificate["kind"]
    if kind in ("crossing", "two_circle"):
        centers, witnesses = certificate["centers"], certificate["witnesses"]
        if (len(centers) != 2 or len(set(centers)) != 2
                or any(type(v) is not int or not 0 <= v < n for v in centers)):
            raise ValueError("invalid centers")
        a, b = centers
        count = 2 if kind == "crossing" else 3
        if (len(witnesses) != count or len(set(witnesses)) != count
                or any(type(v) is not int or not 0 <= v < n for v in witnesses)):
            raise ValueError("invalid common witnesses")
        if not set(witnesses) <= (set(rows[a]) & set(rows[b])):
            raise ValueError("witness equality not supplied")
        if kind == "crossing":
            # Different representation: chord endpoints separate a boundary list.
            lo, hi = sorted(centers)
            separated = [lo < v < hi for v in witnesses]
            if separated[0] != separated[1]:
                raise ValueError("claimed noncrossing chords actually cross")
        return
    expected = {"kalmanson_zero": 1, "kalmanson_inverse": 2}
    if kind not in expected or len(certificate["inequalities"]) != expected[kind]:
        raise ValueError("invalid obstruction type or support size")
    classes = distance_classes(rows, independent=True)
    total = Counter()
    for spec in certificate["inequalities"]:
        for label, value in inequality_coefficients(spec, classes, n):
            total[label] += value
    if any(total.values()):
        raise ValueError("strict inequalities do not cancel")


def positive_control() -> dict:
    """Exact convex three-orbit cycle: k=3 only, never a k=4 counterexample."""
    seeds = [(Q(1), Q(0)), (Q(-26503, 21854), Q(8991, 21854)),
             (Q(-44665, 37058), Q(10753, 37058))]

    def rotate(p):
        x, y = p
        return (-(x + 3 * y) / 2, (x - y) / 2)

    def distance(p, q):
        return (p[0] - q[0]) ** 2 + 3 * (p[1] - q[1]) ** 2

    def turn(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])

    points = seeds + [rotate(p) for p in seeds] + [rotate(rotate(p)) for p in seeds]
    indexed = sorted(range(9), key=points.__getitem__)
    chains = []
    for seq in (indexed, indexed[::-1]):
        chain = []
        for i in seq:
            while len(chain) >= 2 and turn(points[chain[-2]], points[chain[-1]], points[i]) <= 0:
                chain.pop()
            chain.append(i)
        chains.append(chain[:-1])
    order = chains[0] + chains[1]
    if len(set(order)) != 9:
        raise ValueError("positive control not strictly convex")
    pos = {v: i for i, v in enumerate(order)}
    rows = [[] for _ in range(9)]
    for v in range(3):
        for phase in range(3):
            i = 3 * phase + v
            targets = [3 * ((phase + 1) % 3) + v, 3 * ((phase + 2) % 3) + v,
                       3 * ((phase + (1 if v < 2 else 0)) % 3) + (v + 1) % 3]
            radius2 = 3 * distance(points[i], (Q(0), Q(0)))
            if any(distance(points[i], points[j]) != radius2 for j in targets):
                raise ValueError("positive-control selected equality failed")
            rows[pos[i]] = sorted(pos[j] for j in targets)
    multiplicities = [max(Counter(distance(p, q) for q in points if q != p).values()) for p in points]
    if multiplicities != [3] * 9 or find_certificate(rows) is not None:
        raise ValueError("valid k=3 control was rejected or misclassified")
    return {"points": 9, "maximum_multiplicities": multiplicities,
            "passes_exact_filters": True, "not_a_four_witness_counterexample": True}


def generate() -> tuple[dict, list[dict]]:
    radial = radius_audit()
    radius_counts = Counter(tuple(r["canonical"]) for r in radial if "canonical" in r)
    if radius_counts != Counter({c: 24 for c in CANONICAL}):
        raise ValueError("radial coverage mismatch")
    certificates, summaries = [], []
    for kind, radial_order in enumerate(CANONICAL):
        count = Counter()
        start = len(certificates)
        for index, (order, gains) in enumerate(cases(radial_order)):
            rows = expand(order, gains)
            certificate = find_certificate(rows)
            if certificate is None:
                raise ValueError(f"unobstructed case: {radial_order}, {order}, {gains}")
            verify_certificate(rows, certificate)
            count[certificate["kind"]] += 1
            certificates.append({"radial_type": kind, "case": index,
                                 "angle_order": order, "gains": gains,
                                 "certificate": certificate})
        if len(certificates) - start != 1920 or dict(count) != EXPECTED[kind]:
            raise ValueError("certificate census mismatch")
        summaries.append({"radial_order": list(radial_order), "cases": 1920,
                          "obstructions": dict(count)})
    report = {"schema": "erdos97.six_orbit_radial_obstruction.v1", "scope": SCOPE,
              "status": "EXACT_FINITE_CERTIFICATE_REVIEW_PENDING",
              "radial_orders": 720, "downward_triangle_obstructions": 672,
              "remaining_radial_orders": 48, "graph_automorphisms": 24,
              "radial_types": summaries, "total_phase_order_cases": len(certificates),
              "survivors": 0, "radial_audit_sha256": digest(radial),
              "certificates_sha256": digest(certificates), "positive_control": positive_control()}
    return report, certificates


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--write", action="store_true", help="regenerate report.json")
    actions.add_argument("--check", action="store_true", help="compare regenerated report.json")
    parser.add_argument("--certificates", type=Path, help="also export every explicit certificate")
    args = parser.parse_args()
    report, certificates = generate()
    encoded = json.dumps(report, sort_keys=True, indent=2) + "\n"
    stored = Path(__file__).with_name("report.json")
    if args.write:
        stored.write_text(encoded, encoding="utf-8")
    if args.check and stored.read_text(encoding="utf-8") != encoded:
        raise ValueError("stored report mismatch")
    if args.certificates:
        args.certificates.write_text(json.dumps(certificates, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
