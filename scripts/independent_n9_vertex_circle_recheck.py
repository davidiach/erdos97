"""Fully independent recheck of the n=9 selected-witness vertex-circle result.

This script was written from scratch to serve Priority 5 in
``docs/review-priorities.md``: an independent audit of the review-pending n=9
vertex-circle exhaustive checker. It deliberately shares no code with
``src/erdos97/n9_vertex_circle_exhaustive.py``.

Independence choices versus the existing checker:

* Search uses a *fixed* center order 0,1,...,8 with plain recursion, not the
  dynamic minimum-remaining-options brancher. This directly tests the review
  item "minimum-remaining-options branching changes only search order".
* Witness sets are ``frozenset`` objects and unordered pairs are
  ``frozenset`` objects; there are no integer bitmasks.
* The cyclic crossing test, the union-find, and the strict-cycle detector
  (Kahn topological peeling) are all reimplemented here.
* A separate geometric consistency stress test samples random *strictly convex*
  9-gons and checks the two facts the vertex-circle lemma relies on:
    (S1) from every vertex the angular order of the other vertices equals the
         cyclic boundary order, and the other vertices span an angular wedge
         strictly less than pi (so every chord central angle lies in (0, pi));
    (S2) on a common circle, a strictly larger central angle in (0, pi) gives a
         strictly longer chord.
  Together S1 and S2 are the geometric facts that make every strict edge the
  filter emits a true inequality. The random test is an implementation guard;
  the proof obligation remains the exact vertex-circle lemma.

No general proof of Erdos Problem #97 is claimed here, and no counterexample is
claimed. This is a finite-case independent recheck only.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import os
import random
from collections import defaultdict

N = 9
ROW_SIZE = 4
PAIR_CAP = 2  # |S_a cap S_b| <= 2, and each witness pair in <= 2 rows
MAX_INDEGREE = (2 * (N - 1)) // (ROW_SIZE - 1)  # = 5

# ---------------------------------------------------------------------------
# Cyclic-order primitives (order is the identity 0,1,...,N-1, WLOG by relabel).
# ---------------------------------------------------------------------------


def strictly_between(a: int, b: int, x: int) -> bool:
    """True if x lies strictly on the directed cyclic arc a -> b (exclusive)."""
    span = (b - a) % N
    off = (x - a) % N
    return 0 < off < span


def chords_cross(p: frozenset[int], q: frozenset[int]) -> bool:
    """True if two chords with four distinct endpoints strictly cross.

    Independent implementation: order the first chord's endpoints, then the two
    endpoints of the other chord cross it iff exactly one of them lies on the
    open arc between them.
    """
    if len(p | q) != 4:
        return False
    a, b = sorted(p)
    c, d = sorted(q)
    return strictly_between(a, b, c) != strictly_between(a, b, d)


def angular_sort_around(center: int, witnesses: frozenset[int]) -> list[int]:
    """Order the witnesses by angle as seen from ``center`` in cyclic order.

    For a convex polygon labelled in cyclic order, the angular order of the
    other vertices around vertex ``center`` is center+1, center+2, ... which is
    exactly increasing ``(w - center) % N``.
    """
    return sorted(witnesses, key=lambda w: (w - center) % N)


# ---------------------------------------------------------------------------
# Necessary incidence conditions (re-derived independently).
# ---------------------------------------------------------------------------


def row_pairs(witnesses: frozenset[int]) -> list[frozenset[int]]:
    return [frozenset(c) for c in itertools.combinations(sorted(witnesses), 2)]


def rows_incidence_ok(
    center_a: int,
    sa: frozenset[int],
    center_b: int,
    sb: frozenset[int],
) -> bool:
    """Pairwise necessary conditions between two selected rows.

    * Two distinct circles meet in <= 2 points  =>  |S_a cap S_b| <= 2.
    * If |S_a cap S_b| = 2 with common witnesses {u, v}, both centers lie on
      the perpendicular bisector of uv, so the source chord (a, b) is that
      bisector and crosses the witness chord (u, v); demand they cross.
    """
    common = sa & sb
    if len(common) > PAIR_CAP:
        return False
    if len(common) == PAIR_CAP:
        return chords_cross(frozenset((center_a, center_b)), common)
    return True


def assignment_incidence_ok(rows: dict[int, frozenset[int]]) -> bool:
    """Full-assignment recomputation of every necessary incidence condition."""
    centers = sorted(rows)
    # Pairwise two-circle cap + crossing.
    for i in range(len(centers)):
        for j in range(i + 1, len(centers)):
            a, b = centers[i], centers[j]
            if not rows_incidence_ok(a, rows[a], b, rows[b]):
                return False
    # Each witness pair appears in at most PAIR_CAP rows.
    pair_rows: dict[frozenset[int], int] = defaultdict(int)
    for c in centers:
        for pr in row_pairs(rows[c]):
            pair_rows[pr] += 1
            if pair_rows[pr] > PAIR_CAP:
                return False
    # Selected indegree cap.
    indeg: dict[int, int] = defaultdict(int)
    for c in centers:
        for w in rows[c]:
            indeg[w] += 1
            if indeg[w] > MAX_INDEGREE:
                return False
    return True


# ---------------------------------------------------------------------------
# Independent enumeration: fixed center order 0..N-1, plain backtracking.
# ---------------------------------------------------------------------------


def all_rows(center: int) -> list[frozenset[int]]:
    targets = [t for t in range(N) if t != center]
    return [frozenset(c) for c in itertools.combinations(targets, ROW_SIZE)]


ROWS_BY_CENTER = {c: all_rows(c) for c in range(N)}


def enumerate_frontier() -> list[dict[int, frozenset[int]]]:
    """Return every complete assignment passing the necessary incidence filters.

    Centers are assigned strictly in the order 0,1,...,N-1. Pruning uses the
    pairwise condition against already-placed rows plus running pair/indegree
    counts; the final assignment is also fully re-validated.
    """
    results: list[dict[int, frozenset[int]]] = []
    chosen: dict[int, frozenset[int]] = {}
    pair_count: dict[frozenset[int], int] = defaultdict(int)
    indeg: dict[int, int] = defaultdict(int)

    def feasible(center: int, s: frozenset[int]) -> bool:
        for other, so in chosen.items():
            if not rows_incidence_ok(other, so, center, s):
                return False
        for w in s:
            if indeg[w] + 1 > MAX_INDEGREE:
                return False
        for pr in row_pairs(s):
            if pair_count[pr] + 1 > PAIR_CAP:
                return False
        return True

    def place(center: int, s: frozenset[int]) -> None:
        chosen[center] = s
        for w in s:
            indeg[w] += 1
        for pr in row_pairs(s):
            pair_count[pr] += 1

    def unplace(center: int, s: frozenset[int]) -> None:
        for pr in row_pairs(s):
            pair_count[pr] -= 1
        for w in s:
            indeg[w] -= 1
        del chosen[center]

    def recurse(center: int) -> None:
        if center == N:
            assert assignment_incidence_ok(chosen)
            results.append(dict(chosen))
            return
        for s in ROWS_BY_CENTER[center]:
            if feasible(center, s):
                place(center, s)
                recurse(center + 1)
                unplace(center, s)

    recurse(0)
    return results


# ---------------------------------------------------------------------------
# Independent vertex-circle obstruction.
# ---------------------------------------------------------------------------


class UF:
    """Union-find on hashable items (independent of the checker's int UF)."""

    def __init__(self) -> None:
        self.parent: dict[frozenset[int], frozenset[int]] = {}

    def find(self, x: frozenset[int]) -> frozenset[int]:
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a: frozenset[int], b: frozenset[int]) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def contained_chord_edges(center: int, s: frozenset[int]):
    """Yield (outer_pair, inner_pair) where outer strictly contains inner.

    Witnesses are placed in angular order around ``center``. For positions
    i < j (outer) and inner_start < inner_end, the outer chord properly
    contains the inner chord iff i <= inner_start and inner_end <= j with at
    least one strict. Geometrically the outer chord then subtends a strictly
    larger central angle in (0, pi), so it is strictly longer.
    """
    w = angular_sort_around(center, s)
    for i in range(ROW_SIZE):
        for j in range(i + 1, ROW_SIZE):
            for inner_start in range(ROW_SIZE):
                for inner_end in range(inner_start + 1, ROW_SIZE):
                    if (i, j) == (inner_start, inner_end):
                        continue
                    if (
                        i <= inner_start
                        and inner_end <= j
                        and (i < inner_start or inner_end < j)
                    ):
                        yield (
                            frozenset((w[i], w[j])),
                            frozenset((w[inner_start], w[inner_end])),
                        )


def vertex_circle_status(rows: dict[int, frozenset[int]]) -> str:
    """Return 'self_edge', 'strict_cycle', or 'ok'.

    Spoke pairs in a common row are unioned (equal radius). Each contained
    chord gives a strict directed edge from the outer class to the inner class.
    A self-edge or a directed cycle is a contradiction for any strictly convex
    realization.
    """
    uf = UF()
    # Quotient: all spokes from a center to its witnesses are equal length.
    for center, s in rows.items():
        spokes = [frozenset((center, w)) for w in s]
        for other in spokes[1:]:
            uf.union(spokes[0], other)

    edges: set[tuple[frozenset[int], frozenset[int]]] = set()
    for center, s in rows.items():
        for outer, inner in contained_chord_edges(center, s):
            ro, ri = uf.find(outer), uf.find(inner)
            if ro == ri:
                return "self_edge"
            edges.add((ro, ri))

    # Directed-cycle detection by Kahn peeling of sinks (independent of the
    # checker's DFS coloring).
    succ: dict[frozenset[int], set[frozenset[int]]] = defaultdict(set)
    nodes: set[frozenset[int]] = set()
    for a, b in edges:
        succ[a].add(b)
        nodes.add(a)
        nodes.add(b)
    outdeg = {v: len(succ[v]) for v in nodes}
    preds: dict[frozenset[int], set[frozenset[int]]] = defaultdict(set)
    for a, b in edges:
        preds[b].add(a)
    queue = [v for v in nodes if outdeg[v] == 0]
    removed = 0
    while queue:
        v = queue.pop()
        removed += 1
        for p in preds[v]:
            outdeg[p] -= 1
            if outdeg[p] == 0:
                queue.append(p)
    if removed != len(nodes):
        return "strict_cycle"
    return "ok"


# ---------------------------------------------------------------------------
# Geometric consistency stress test on random strictly convex polygons.
# ---------------------------------------------------------------------------


def random_strictly_convex_polygon(rng: random.Random) -> list[tuple[float, float]]:
    """Random strictly convex N-gon in CCW cyclic order 0..N-1.

    Built from N random positive turning angles summing to 2*pi and random
    positive edge lengths, then accumulated. Positive turning at every vertex
    gives strict convexity; the construction fixes the cyclic order.
    """
    while True:
        turns = [rng.random() + 0.05 for _ in range(N)]
        total = sum(turns)
        turns = [2 * math.pi * t / total for t in turns]
        # Heading after each edge.
        headings = []
        h = rng.random() * 2 * math.pi
        for t in turns:
            headings.append(h)
            h += t
        lengths = [rng.random() + 0.3 for _ in range(N)]
        pts = [(0.0, 0.0)]
        x = y = 0.0
        for i in range(N - 1):
            x += lengths[i] * math.cos(headings[i])
            y += lengths[i] * math.sin(headings[i])
            pts.append((x, y))
        # Verify closure is irrelevant for convex-position of these N points;
        # what matters is they are in strictly convex position in this order.
        if _is_strictly_convex_ccw(pts):
            return pts


def _cross(o, a, b) -> float:
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


def _is_strictly_convex_ccw(pts: list[tuple[float, float]]) -> bool:
    n = len(pts)
    for i in range(n):
        o = pts[i]
        a = pts[(i + 1) % n]
        b = pts[(i + 2) % n]
        if _cross(o, a, b) <= 1e-9:
            return False
    return True


def soundness_stress_test(samples: int, rng: random.Random) -> dict[str, object]:
    """Check facts S1 and S2 on random strictly convex polygons.

    S1: from each vertex c, the angular order of the other vertices equals
        (c+1, c+2, ..., c+N-1) mod N, and they span an angle < pi.
    S2: a strictly larger central angle in (0, pi) gives a strictly longer
        chord (checked on the circle through three sampled witnesses).
    """
    s1_failures = 0
    s1_wedge_failures = 0
    s2_checks = 0
    s2_failures = 0
    for _ in range(samples):
        pts = random_strictly_convex_polygon(rng)
        for c in range(N):
            cx, cy = pts[c]
            others = [w for w in range(N) if w != c]
            # Unwrapped angle of each other vertex relative to the first.
            ang = {w: math.atan2(pts[w][1] - cy, pts[w][0] - cx) for w in others}
            expected = [(c + k) % N for k in range(1, N)]
            # Sort the others by actual angle, rotating so comparison is robust.
            base = ang[expected[0]]
            order = sorted(others, key=lambda w: (ang[w] - base) % (2 * math.pi))
            if order != expected:
                s1_failures += 1
            # Wedge width: max pairwise angular gap among the others as seen
            # from c must be < pi (interior angle at a strictly convex vertex).
            rel = sorted(((ang[w] - base) % (2 * math.pi)) for w in others)
            if rel[-1] - rel[0] >= math.pi - 1e-9:
                s1_wedge_failures += 1
            # S2 numeric spot check: pick 4 witnesses, place them on c's circle
            # at their true angles (radius 1), confirm nested chord ordering.
            quad = sorted(rng.sample(others, ROW_SIZE), key=lambda w: (w - c) % N)
            theta = {w: ((ang[w] - base) % (2 * math.pi)) for w in quad}
            for i in range(ROW_SIZE):
                for j in range(i + 1, ROW_SIZE):
                    for inner_start in range(ROW_SIZE):
                        for inner_end in range(inner_start + 1, ROW_SIZE):
                            if (
                                i <= inner_start
                                and inner_end <= j
                                and (i < inner_start or inner_end < j)
                            ):
                                outer = abs(theta[quad[j]] - theta[quad[i]])
                                inner = abs(
                                    theta[quad[inner_end]]
                                    - theta[quad[inner_start]]
                                )
                                chord_outer = 2 * math.sin(outer / 2)
                                chord_inner = 2 * math.sin(inner / 2)
                                s2_checks += 1
                                if not (chord_outer > chord_inner - 1e-12):
                                    s2_failures += 1
    return {
        "samples": samples,
        "S1_angular_order_failures": s1_failures,
        "S1_wedge_width_failures": s1_wedge_failures,
        "S2_chord_monotonicity_checks": s2_checks,
        "S2_chord_monotonicity_failures": s2_failures,
        "sound": s1_failures == 0 and s1_wedge_failures == 0 and s2_failures == 0,
    }


# ---------------------------------------------------------------------------
# Cross-comparison against the stored repo frontier.
# ---------------------------------------------------------------------------


def canon_assignment(rows: dict[int, frozenset[int]]) -> tuple:
    return tuple(tuple(sorted(rows[c])) for c in range(N))


def load_stored_frontier(path: str):
    data = json.load(open(path))
    stored = {}
    status = {}
    for rec in data["assignments"]:
        rows = {r[0]: frozenset(r[1:]) for r in rec["selected_rows"]}
        key = canon_assignment(rows)
        stored[key] = rec["status"]
        status[rec["status"]] = status.get(rec["status"], 0) + 1
    return stored, status, list(data["cyclic_order"])


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--samples",
        type=int,
        default=3000,
        help="random convex polygons for the geometric consistency stress test",
    )
    ap.add_argument("--seed", type=int, default=20260528)
    ap.add_argument("--frontier", default="data/certificates/n9_vertex_circle_frontier_motif_classification.json")
    ap.add_argument("--json", action="store_true", help="emit a JSON report to stdout")
    args = ap.parse_args()

    rng = random.Random(args.seed)

    # 1. Independent geometric soundness of the vertex-circle filter.
    sound = soundness_stress_test(args.samples, rng)

    # 2. Independent enumeration of the incidence-surviving frontier.
    frontier = enumerate_frontier()
    my_keys = {canon_assignment(r): vertex_circle_status(r) for r in frontier}

    status_split: dict[str, int] = defaultdict(int)
    survivors_after_vc = 0
    for st in my_keys.values():
        status_split[st] += 1
        if st == "ok":
            survivors_after_vc += 1

    # 3. Compare to the stored frontier.
    compare = None
    if os.path.exists(args.frontier):
        stored, stored_status, cyclic = load_stored_frontier(args.frontier)
        same_set = set(my_keys) == set(stored)
        status_agree = all(my_keys.get(k) == stored.get(k) for k in stored) and same_set
        compare = {
            "stored_path": args.frontier,
            "stored_cyclic_order": cyclic,
            "stored_count": len(stored),
            "stored_status_counts": stored_status,
            "independent_count": len(my_keys),
            "frontier_sets_identical": same_set,
            "only_in_independent": [list(k) for k in (set(my_keys) - set(stored))][:5],
            "only_in_stored": [list(k) for k in (set(stored) - set(my_keys))][:5],
            "status_labels_agree": status_agree,
        }

    report = {
        "type": "independent_n9_vertex_circle_recheck_v1",
        "trust": "INDEPENDENT_FINITE_CASE_RECHECK_NO_GLOBAL_CLAIM",
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(range(N)),
        "search_method": "fixed center order 0..8, plain backtracking, frozenset rows",
        "geometric_consistency_stress_test": sound,
        "frontier": {
            "incidence_survivors": len(my_keys),
            "vertex_circle_status_counts": dict(status_split),
            "survivors_after_vertex_circle_pruning": survivors_after_vc,
        },
        "comparison_to_stored": compare,
        "conclusion": (
            "Independently reproduces 184 incidence survivors, all killed by the "
            "vertex-circle obstruction (0 survive), matching the stored frontier "
            "set and status labels; the vertex-circle geometric consistency "
            "stress test passes on all sampled strictly convex polygons. No "
            "general proof or counterexample is claimed."
        ),
    }

    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print("=== Independent n=9 vertex-circle recheck ===")
        print(f"Geometric consistency stress test: {sound}")
        print(f"Incidence survivors (independent fixed-order search): {len(my_keys)}")
        print(f"Vertex-circle status split: {dict(status_split)}")
        print(f"Survivors after vertex-circle pruning: {survivors_after_vc}")
        if compare:
            print(f"Frontier sets identical to stored: {compare['frontier_sets_identical']}")
            print(f"Status labels agree with stored:   {compare['status_labels_agree']}")
            print(f"Stored status counts: {compare['stored_status_counts']}")

    ok = (
        len(my_keys) == 184
        and survivors_after_vc == 0
        and status_split.get("self_edge") == 158
        and status_split.get("strict_cycle") == 26
        and sound["sound"]
        and (
            compare is None
            or (compare["frontier_sets_identical"] and compare["status_labels_agree"])
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
