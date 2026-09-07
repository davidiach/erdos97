"""Exact, finite, fixed-order replay of the nine-orbit rows quoted in conversation.
This checks selected necessary filters only. It neither enumerates all patterns
nor certifies a Euclidean realization. A containment obstruction is stronger
than the earlier filters and is reported separately.
"""

from __future__ import annotations
import argparse
from itertools import combinations
import json
from pathlib import Path

ROWS = [
    [1, 1, 2, 1],
    [3, 1, 4, 1],
    [4, 1, 7, 1],
    [2, 1, 5, 1],
    [6, 2, 8, 1],
    [0, 0, 7, 2],
    [0, 0, 3, 2],
    [6, 1, 8, 1],
    [1, 0, 5, 2],
]


def crosses(a: int, b: int, c: int, d: int) -> bool:
    if len({a, b, c, d}) != 4:
        return False
    a, b = sorted((a, b))
    return (a < c < b) != (a < d < b)


def transitive_closure(n: int, edges: set[tuple[int, int]]) -> list[set[int]]:
    reach = [set() for _ in range(n)]
    for a, b in edges:
        reach[a].add(b)
    for k in range(n):
        for i in range(n):
            if k in reach[i]:
                reach[i].update(reach[k])
    return reach


def verify(rows: list[list[int]]) -> dict:
    if not isinstance(rows, list) or len(rows) < 3:
        raise ValueError("At least three orbit rows required")
    m = len(rows)
    n = 3 * m
    for i, row in enumerate(rows):
        if (
            not isinstance(row, list)
            or len(row) != 4
            or any(type(x) is not int for x in row)
        ):
            raise ValueError("Each row must contain two integer target/gain pairs")
        if len(set(row[::2])) != 2:
            raise ValueError("Distinct supplier orbits required")
        for j, g in zip(row[::2], row[1::2]):
            if not 0 <= j < m or j == i or not 0 <= g < 3:
                raise ValueError("Target/gain outside its domain")
    reciprocal = [
        (i, j) for i, row in enumerate(rows) for j in row[::2] if i in rows[j][::2]
    ]
    selected = []
    right = []
    radial = {(i, 0) for i in range(1, m)}
    adjacency = [set() for _ in range(m)]
    for p in range(n):
        i = p % m
        k = p // m
        selected.append({i + ((k + 1) % 3) * m, i + ((k + 2) % 3) * m})
        right.append([])
        for j, g in zip(rows[i][::2], rows[i][1::2]):
            selected[p].add(j + ((k + g) % 3) * m)
            right[p].append((j + ((k + g + 1) % 3) * m, j + ((k + g + 2) % 3) * m))
            if k == 0:
                off = (g * m + j - i) % n
                radial.add((j, i) if m < off < 2 * m else (i, j))
                adjacency[i].add(j)
                adjacency[j].add(i)
    interlace_fail = [p for p in range(n) if not crosses(*right[p][0], *right[p][1])]
    circle_fail = []
    circle_pairs = 0
    for a, b in combinations(range(n), 2):
        common = sorted(selected[a] & selected[b])
        circle_pairs += 1
        if len(common) > 2 or (len(common) == 2 and not crosses(a, b, *common)):
            circle_fail.append([a, b, common])
    radial_reach = transitive_closure(m, radial)
    radial_cycles = [i for i in range(m) if i in radial_reach[i]]
    up = {(i, j) for i in range(m) for j in adjacency[i] if j in radial_reach[i]}
    up_reach = transitive_closure(m, up)
    shortcuts = []
    for i, row in enumerate(rows):
        for j in row[::2]:
            if any((j, k) in up and i in up_reach[k] for k in range(m)):
                shortcuts.append([i, j])
    pairs = list(combinations(range(n), 2))
    parent = {p: p for p in pairs}

    def find(p):
        p = tuple(sorted(p))
        while parent[p] != p:
            parent[p] = parent[parent[p]]
            p = parent[p]
        return p

    def join(p, q):
        a, b = find(p), find(q)
        if a != b:
            a, b = sorted((a, b))
            parent[b] = a

    for a, b in pairs:
        join((a, b), ((a + m) % n, (b + m) % n))
    for i, ws in enumerate(selected):
        spokes = [(i, j) for j in sorted(ws)]
        for a, b in zip(spokes, spokes[1:]):
            join(a, b)
    classes = sorted({find(p) for p in pairs})
    number = {c: i for i, c in enumerate(classes)}

    def cl(a, b):
        return number[find((a, b))]

    own = [cl(i, i + m) for i in range(m)]
    own_collision = len(set(own)) != m
    owners = {v: i for i, v in enumerate(own)}
    metric_edges = {(own[i], own[j]) for i in range(m) for j in radial_reach[i]}
    metric_zero = []
    metric_dominated = []
    ineq_count = 0
    for a, b, c, d in combinations(range(n), 4):
        for lo in ((cl(a, b), cl(c, d)), (cl(a, d), cl(b, c))):
            hi = (cl(a, c), cl(b, d))
            left = list(hi)
            low = list(lo)
            ineq_count += 1
            for x in hi:
                if x in low:
                    left.remove(x)
                    low.remove(x)
            if not left:
                metric_zero.append([a, b, c, d, list(hi), list(lo)])
            elif len(left) == 1:
                metric_edges.add((low[0], left[0]))
            elif all(x in owners for x in hi + lo):

                def le(x, y):
                    return x == y or owners[y] in radial_reach[owners[x]]

                if (le(hi[0], lo[0]) and le(hi[1], lo[1])) or (
                    le(hi[0], lo[1]) and le(hi[1], lo[0])
                ):
                    metric_dominated.append([a, b, c, d])
    metric_reach = transitive_closure(len(classes), metric_edges)
    metric_cycles = [i for i in range(len(classes)) if i in metric_reach[i]]
    containment = []
    for center, ws in enumerate(selected):
        for p in sorted(ws):
            for b in sorted(ws - {p}):
                low, high = sorted(((center - p) % n, (b - p) % n))
                for u, v in right[p]:
                    x, y = sorted(((u - p) % n, (v - p) % n))
                    if 0 < low <= x < y <= high < n:
                        containment.append([center, p, b, u, v])
    failures = {
        "reciprocal_arrows": reciprocal,
        "right_interlacing": interlace_fail,
        "circle_overlap_or_crossing": circle_fail,
        "radius_cycles": radial_cycles,
        "increasing_path_shortcuts": shortcuts,
        "own_length_collision": own_collision,
        "metric_zero_rows": metric_zero,
        "metric_radial_domination": metric_dominated,
        "metric_comparison_cycles": metric_cycles,
    }
    return {
        "schema": 1,
        "scope": "One nine-orbit fixed-order pattern; selected necessary filters only",
        "rows": rows,
        "orbit_count": m,
        "physical_vertex_count": n,
        "selected_orbit_arrows": 2 * m,
        "selected_directed_spokes": sum(map(len, selected)),
        "circle_pairs_checked": circle_pairs,
        "kalmanson_inequalities_checked": ineq_count,
        "length_quotient_classes": len(classes),
        "earlier_filter_failures": failures,
        "survives_earlier_filters": not any(failures.values()),
        "right_angle_containment_obstructions": containment,
        "euclidean_realization_claimed": False,
        "all_pattern_exhaustion_claimed": False,
        "full_chord_angle_feasibility_checked": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rows", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    rows = json.loads(args.rows.read_text()) if args.rows else ROWS
    result = verify(rows)
    if args.check and json.loads(args.check.read_text()) != result:
        raise SystemExit("Stored candidate report differs")
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text)


if __name__ == "__main__":
    main()
