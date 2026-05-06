"""
Independent re-implementation of n=9 vertex-circle exhaustive checker.

Audit goal: determine whether 0 full assignments survive the necessary
filters for any 4-bad strictly convex 9-gon in cyclic labels 0..8.

Filters re-derived from geometric necessary conditions:

  (F1) PAIR-CAP (L4 perpendicular-bisector vertex bound)
       For any unordered pair {a,b}, at most 2 vertices c can be
       equidistant from a and b (otherwise three points lie on the
       perpendicular bisector of ab, forcing 3 collinear vertices).
       Equivalently: each unordered witness pair {a,b} appears in at
       most 2 selected rows.

  (F2) TWO-CIRCLE-CAP (L5)
       |S_i intersect S_j| <= 2 for any two selected rows i != j.

  (F3) CROSSING (L6)
       If S_x intersect S_y = {a,b}, then in the cyclic order on
       {0,...,8} the chord (x,y) crosses chord (a,b). Both x,y are
       on the perpendicular bisector of ab.

  (F4) INDEGREE CAP
       Each vertex v can appear in at most floor(2*(n-1)/(k-1)) rows.
       For n=9, k=4: floor(16/3) = 5.

  (F5) VERTEX-CIRCLE STRICT-MONOTONICITY
       For each row i, the witnesses lie on a circle around p_i, in
       angular order matching their cyclic boundary order on P
       (stripping i from 0..8). Nested chords give strict monotone
       inequalities between selected distances modulo selected
       equalities. Self-edges and directed cycles are obstructions.

Search:
  Enumerate row 0's selected witnesses S_0 over the C(8,4)=70 4-subsets
  of {1,...,8}.  Branch row-by-row in increasing label order, applying
  the filters incrementally.  No symmetry quotient (only relabeling).

For independence we *do not* import erdos97.n9_vertex_circle_exhaustive
or scripts/check_n9_vertex_circle_exhaustive.py.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import multiprocessing
import os
import sys
import time
from functools import lru_cache
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

N = 9
ROW_SIZE = 4
INDEGREE_CAP = (2 * (N - 1)) // (ROW_SIZE - 1)  # 5
PAIR_CAP = 2  # each pair appears in at most 2 rows (filter F1)
TWO_CIRCLE_CAP = 2  # filter F2

# 4-subsets of an 8-element set, used for row 0
ROW0_CHOICES = list(itertools.combinations(range(1, N), ROW_SIZE))


# ---------------------------------------------------------------------------
# Cyclic-order primitives
# ---------------------------------------------------------------------------

def cyclic_position(v: int, center: int, n: int = N) -> int:
    """
    Position of vertex v in the angular order of the n-gon's boundary
    when we 'cut' at center.  We strip center from {0,...,n-1} and
    return the position of v in the resulting sequence.

    Order: traverse cyclic labels (center+1, center+2, ..., center-1) mod n.
    """
    if v == center:
        raise ValueError("center vertex has no angular position")
    return (v - center - 1) % n  # 0..n-2


def chord_separates(a: int, b: int, c: int, d: int, n: int = N) -> bool:
    """True iff the cyclic chord (a,b) separates c,d on the cyclic order
    0,...,n-1.  Equivalently, exactly one of {c,d} lies in the open
    cyclic arc from a to b (going forward) and the other lies in the
    open cyclic arc from b to a.

    Treats {a,b}, {c,d} as unordered chords.
    """
    if len({a, b, c, d}) != 4:
        return False
    # arc from a (exclusive) to b (exclusive), going forward
    forward_arc = []
    x = (a + 1) % n
    while x != b:
        forward_arc.append(x)
        x = (x + 1) % n
    in_forward = lambda z: z in forward_arc
    return in_forward(c) ^ in_forward(d)


def angular_order_around(center: int, vertices: Sequence[int], n: int = N) -> Tuple[int, ...]:
    """Sort the witness vertices in increasing angular order around
    the n-gon vertex `center`.  Equivalent to sorting by cyclic_position.
    """
    return tuple(sorted(vertices, key=lambda v: cyclic_position(v, center, n)))


# ---------------------------------------------------------------------------
# Union-Find for selected-distance equivalence classes
# ---------------------------------------------------------------------------

class UnionFind:
    __slots__ = ("parent",)

    def __init__(self, items):
        self.parent = {x: x for x in items}

    def find(self, x):
        # Path compression
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, x, y):
        rx, ry = self.find(x), self.find(y)
        if rx == ry:
            return False
        # Choose canonical: smaller root wins (deterministic)
        if rx < ry:
            self.parent[ry] = rx
        else:
            self.parent[rx] = ry
        return True

    def snapshot(self):
        # Return a frozen dict {pair: root}
        return tuple(sorted((k, self.find(k)) for k in self.parent))


def all_unordered_pairs(n: int = N):
    return [frozenset((a, b)) for a in range(n) for b in range(a + 1, n)]


# ---------------------------------------------------------------------------
# Vertex-circle nested-chord strict-inequality graph
# ---------------------------------------------------------------------------

def vertex_circle_strict_edges(rows: Dict[int, Tuple[int, ...]], n: int = N) -> List[Tuple[FrozenSet[int], FrozenSet[int]]]:
    """For each completed row i, sort its 4 witnesses in angular order
    around i.  For every pair of witness-witness chords (s,t) and (u,v)
    among the witnesses of that row, if the angular interval (s,t)
    *properly* contains the angular interval (u,v) (with witness
    indices in the row's own ordering), record a strict edge

         class({s,t}) > class({u,v}).

    A 'proper' containment uses *strict* containment of the open arcs
    among the row's 4 sorted witnesses.

    For 4 angularly-sorted witnesses w0 < w1 < w2 < w3 (in row position),
    the complete set of strict containments is:
       (w0,w3) properly contains (w0,w2)  =>  d(w0,w3) > d(w0,w2)
       (w0,w3) properly contains (w1,w3)  =>  d(w0,w3) > d(w1,w3)
       (w0,w3) properly contains (w1,w2)  =>  d(w0,w3) > d(w1,w2)
       (w0,w2) properly contains (w1,w2)  =>  d(w0,w2) > d(w1,w2)
       (w1,w3) properly contains (w1,w2)  =>  d(w1,w3) > d(w1,w2)
    There is NO containment (w0,w2) vs (w1,w3): those chords cross,
    not nest.
    """
    edges: List[Tuple[FrozenSet[int], FrozenSet[int]]] = []
    for i, witnesses in rows.items():
        if len(witnesses) != ROW_SIZE:
            continue
        ordered = angular_order_around(i, witnesses, n)
        # Generate all strict-containment pairs of witness-witness arcs.
        # Positions 0 < 1 < 2 < 3 in the angular order around center i.
        for o_lo in range(ROW_SIZE):
            for o_hi in range(o_lo + 1, ROW_SIZE):
                for i_lo in range(ROW_SIZE):
                    for i_hi in range(i_lo + 1, ROW_SIZE):
                        if (o_lo, o_hi) == (i_lo, i_hi):
                            continue
                        if o_lo <= i_lo and i_hi <= o_hi and (o_lo < i_lo or i_hi < o_hi):
                            outer = frozenset((ordered[o_lo], ordered[o_hi]))
                            inner = frozenset((ordered[i_lo], ordered[i_hi]))
                            edges.append((outer, inner))
    return edges


def vertex_circle_check(rows: Dict[int, Tuple[int, ...]], require_all_complete: bool = False) -> Tuple[bool, str]:
    """Build UF on selected pairs, then strict graph on classes.
    Returns (ok, reason).  ok=True means no contradiction yet found.
    """
    # 1) Build UF on selected pair classes
    uf = UnionFind(all_unordered_pairs(N))
    for i, witnesses in rows.items():
        if not witnesses:
            continue
        # All pairs {i, w} for w in witnesses are equal (they are
        # selected distances on row i's circle).
        anchor = frozenset((i, witnesses[0]))
        for w in witnesses[1:]:
            uf.union(anchor, frozenset((i, w)))

    # 2) Build strict edges from completed rows (including partials only
    #    when row is fully completed).
    edges = vertex_circle_strict_edges(rows, N)
    # Project to class roots
    class_edges = []
    for outer, inner in edges:
        ro = uf.find(outer)
        ri = uf.find(inner)
        if ro == ri:
            return False, "vertex_circle_self_edge"
        class_edges.append((ro, ri))

    # 3) Check for strict directed cycle (Tarjan/Kahn-style).
    if not class_edges:
        return True, "ok"
    adj: Dict[FrozenSet[int], List[FrozenSet[int]]] = {}
    nodes = set()
    for u, v in class_edges:
        adj.setdefault(u, []).append(v)
        nodes.add(u)
        nodes.add(v)
    indeg: Dict[FrozenSet[int], int] = {n_: 0 for n_ in nodes}
    for u, v in class_edges:
        indeg[v] += 1
    # Kahn's algorithm
    queue = [n_ for n_ in nodes if indeg[n_] == 0]
    visited = 0
    while queue:
        u = queue.pop()
        visited += 1
        for w in adj.get(u, []):
            indeg[w] -= 1
            if indeg[w] == 0:
                queue.append(w)
    if visited != len(nodes):
        return False, "vertex_circle_strict_cycle"
    return True, "ok"


# ---------------------------------------------------------------------------
# Pair / row filters
# ---------------------------------------------------------------------------

def pair_cap_violated(pair_to_rows: Dict[FrozenSet[int], List[int]]) -> bool:
    """F1: each unordered pair appears in at most PAIR_CAP rows."""
    for rows in pair_to_rows.values():
        if len(rows) > PAIR_CAP:
            return True
    return False


def two_circle_cap_violated(rows: Dict[int, Tuple[int, ...]]) -> Optional[Tuple[int, int, int]]:
    """F2: |S_i & S_j| <= 2 for any pair of complete rows i != j."""
    keys = sorted(rows)
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            i, j = keys[a], keys[b]
            wa, wb = rows[i], rows[j]
            if not wa or not wb:
                continue
            inter = set(wa) & set(wb)
            if len(inter) > TWO_CIRCLE_CAP:
                return (i, j, len(inter))
    return None


def crossing_violated(rows: Dict[int, Tuple[int, ...]]) -> bool:
    """F3: if rows i,j share exactly two witnesses {a,b}, then chord
    (i,j) must separate {a,b} on the cyclic order 0..8.

    Note: Both a and b are equidistant from i and from j, so i and j
    lie on the perpendicular bisector of segment ab. In a strictly
    convex polygon, this perpendicular bisector intersects the convex
    hull in a chord (or single point) which crosses ab.
    """
    keys = sorted(rows)
    for a in range(len(keys)):
        for b in range(a + 1, len(keys)):
            i, j = keys[a], keys[b]
            wa, wb = rows[i], rows[j]
            if not wa or not wb:
                continue
            inter = set(wa) & set(wb)
            if len(inter) == 2:
                p, q = sorted(inter)
                if not chord_separates(p, q, i, j, N):
                    return True
    return False


def indegree_violated(indegree: Dict[int, int]) -> bool:
    """F4: each vertex has indegree at most INDEGREE_CAP=5."""
    return any(c > INDEGREE_CAP for c in indegree.values())


# ---------------------------------------------------------------------------
# Backtracking search
# ---------------------------------------------------------------------------

def witness_candidates_for_row(
    i: int,
    rows: Dict[int, Tuple[int, ...]],
    pair_to_rows: Dict[FrozenSet[int], List[int]],
    indegree: Dict[int, int],
) -> List[Tuple[int, ...]]:
    """Generate candidate witness 4-subsets for row i, applying simple
    static filters.  Witnesses are drawn from {0,...,N-1} \\ {i} and
    further pruned by pair-cap and indegree-cap.
    """
    available = [v for v in range(N) if v != i]
    candidates = []
    for combo in itertools.combinations(available, ROW_SIZE):
        # Quick indegree increment check
        ok = True
        for w in combo:
            if indegree.get(w, 0) + 1 > INDEGREE_CAP:
                ok = False
                break
        if not ok:
            continue
        # Pair-cap (witness-witness pairs)
        for wa, wb in itertools.combinations(combo, 2):
            pair = frozenset((wa, wb))
            if len(pair_to_rows.get(pair, [])) >= PAIR_CAP:
                ok = False
                break
        if not ok:
            continue
        # F2 with already-completed rows: |S_i & S_j| <= 2
        bad = False
        for j, wj in rows.items():
            if not wj:
                continue
            if len(set(combo) & set(wj)) > TWO_CIRCLE_CAP:
                bad = True
                break
        if bad:
            continue
        # F3 crossing check w/ already-completed rows
        bad = False
        for j, wj in rows.items():
            if not wj:
                continue
            inter = set(combo) & set(wj)
            if len(inter) == 2:
                p, q = sorted(inter)
                if not chord_separates(p, q, i, j, N):
                    bad = True
                    break
        if bad:
            continue
        candidates.append(combo)
    return candidates


def search_one_row0(
    row0_witnesses: Tuple[int, ...],
    apply_vertex_circle_pruning: bool = True,
) -> Dict[str, int]:
    """Run the backtracking search for a fixed choice of row 0
    witnesses. Branch over rows 1, 2, ..., 8 in label order (no
    minimum-remaining-options heuristic, to avoid copying the existing
    implementation's branching).
    """
    rows: Dict[int, Tuple[int, ...]] = {0: tuple(row0_witnesses)}

    # Pair_to_rows tracks which rows include each unordered witness pair
    pair_to_rows: Dict[FrozenSet[int], List[int]] = {}
    for wa, wb in itertools.combinations(row0_witnesses, 2):
        pair_to_rows[frozenset((wa, wb))] = [0]

    # Indegree counts: for each vertex v, how many rows include v as a witness
    indegree: Dict[int, int] = {v: 0 for v in range(N)}
    for w in row0_witnesses:
        indegree[w] += 1

    counters = {
        "row0": 1,  # the row 0 itself counts as a node in the existing
                    # checker's accounting
        "nodes": 1,
        "full": 0,
        "partial_self_edge": 0,
        "partial_strict_cycle": 0,
        "leaf_self_edge": 0,
        "leaf_strict_cycle": 0,
        "pair_cap_prune": 0,
        "indegree_prune": 0,
    }

    # Validate row 0 itself for vertex-circle (a single completed row
    # cannot give a self-edge unless something pathological occurs;
    # check anyway for consistency).
    if apply_vertex_circle_pruning:
        ok, reason = vertex_circle_check(rows)
        if not ok:
            counters["partial_self_edge" if reason == "vertex_circle_self_edge"
                     else "partial_strict_cycle"] += 1
            return counters

    def recurse(next_row: int):
        if next_row > N - 1:
            # Full assignment.  Final vertex-circle check is implicit
            # in the partial check we already perform.
            counters["full"] += 1
            return

        cands = witness_candidates_for_row(next_row, rows, pair_to_rows, indegree)
        for combo in cands:
            counters["nodes"] += 1

            rows[next_row] = combo
            for w in combo:
                indegree[w] += 1
            for wa, wb in itertools.combinations(combo, 2):
                pair_to_rows.setdefault(frozenset((wa, wb)), []).append(next_row)
            # Add (next_row, w) pairs as well (these update UF in vertex_circle_check)
            # We don't need to track {next_row,w} in pair_to_rows since they
            # are 'source-target' selected edges, but the witness-witness
            # pairs are what F1/F3 watch.

            # Apply vertex-circle filter (uses *all* completed rows so far)
            ok = True
            if apply_vertex_circle_pruning:
                vc_ok, reason = vertex_circle_check(rows)
                if not vc_ok:
                    if reason == "vertex_circle_self_edge":
                        counters["partial_self_edge"] += 1
                    else:
                        counters["partial_strict_cycle"] += 1
                    ok = False

            if ok:
                recurse(next_row + 1)

            # backtrack
            del rows[next_row]
            for w in combo:
                indegree[w] -= 1
            for wa, wb in itertools.combinations(combo, 2):
                key = frozenset((wa, wb))
                pair_to_rows[key].pop()
                if not pair_to_rows[key]:
                    del pair_to_rows[key]

    recurse(1)
    return counters


def search_one_row0_no_vc(row0_witnesses: Tuple[int, ...]) -> Dict[str, int]:
    """Cross-check pass: same as search_one_row0 but without the
    vertex-circle filter (filter F5).  At full assignment, classify the
    failure mode (self_edge vs strict_cycle vs ok)."""
    rows: Dict[int, Tuple[int, ...]] = {0: tuple(row0_witnesses)}
    pair_to_rows: Dict[FrozenSet[int], List[int]] = {}
    for wa, wb in itertools.combinations(row0_witnesses, 2):
        pair_to_rows[frozenset((wa, wb))] = [0]
    indegree: Dict[int, int] = {v: 0 for v in range(N)}
    for w in row0_witnesses:
        indegree[w] += 1

    counters = {
        "nodes": 1,
        "full": 0,
        "self_edge": 0,
        "strict_cycle": 0,
        "vc_pass": 0,
    }

    def recurse(next_row: int):
        if next_row > N - 1:
            counters["full"] += 1
            ok, reason = vertex_circle_check(rows)
            if ok:
                counters["vc_pass"] += 1
            elif reason == "vertex_circle_self_edge":
                counters["self_edge"] += 1
            else:
                counters["strict_cycle"] += 1
            return
        cands = witness_candidates_for_row(next_row, rows, pair_to_rows, indegree)
        for combo in cands:
            counters["nodes"] += 1
            rows[next_row] = combo
            for w in combo:
                indegree[w] += 1
            for wa, wb in itertools.combinations(combo, 2):
                pair_to_rows.setdefault(frozenset((wa, wb)), []).append(next_row)
            recurse(next_row + 1)
            del rows[next_row]
            for w in combo:
                indegree[w] -= 1
            for wa, wb in itertools.combinations(combo, 2):
                key = frozenset((wa, wb))
                pair_to_rows[key].pop()
                if not pair_to_rows[key]:
                    del pair_to_rows[key]

    recurse(1)
    return counters


# ---------------------------------------------------------------------------
# Driver
# ---------------------------------------------------------------------------

def _run_with_vc(combo):
    return combo, search_one_row0(combo, apply_vertex_circle_pruning=True)


def _run_without_vc(combo):
    return combo, search_one_row0_no_vc(combo)


def run_main(parallel: bool = True) -> Dict:
    """Run the main vertex-circle pruning search across all 70 row0 choices."""
    aggregate = {
        "row0_choices": len(ROW0_CHOICES),
        "nodes_visited": 0,
        "full_assignments": 0,
        "partial_self_edge": 0,
        "partial_strict_cycle": 0,
    }
    per_row0 = {}
    if parallel:
        with multiprocessing.Pool(processes=min(os.cpu_count() or 1, 8)) as pool:
            for combo, counters in pool.imap_unordered(_run_with_vc, ROW0_CHOICES):
                per_row0[str(list(combo))] = counters
                aggregate["nodes_visited"] += counters["nodes"]
                aggregate["full_assignments"] += counters["full"]
                aggregate["partial_self_edge"] += counters["partial_self_edge"]
                aggregate["partial_strict_cycle"] += counters["partial_strict_cycle"]
    else:
        for combo in ROW0_CHOICES:
            counters = search_one_row0(combo, True)
            per_row0[str(list(combo))] = counters
            aggregate["nodes_visited"] += counters["nodes"]
            aggregate["full_assignments"] += counters["full"]
            aggregate["partial_self_edge"] += counters["partial_self_edge"]
            aggregate["partial_strict_cycle"] += counters["partial_strict_cycle"]
    return {"aggregate": aggregate, "per_row0": per_row0}


def run_no_vc(parallel: bool = True) -> Dict:
    """Cross-check pass without vertex-circle pruning."""
    aggregate = {
        "row0_choices": len(ROW0_CHOICES),
        "nodes_visited": 0,
        "full_assignments": 0,
        "self_edge": 0,
        "strict_cycle": 0,
        "vc_pass": 0,
    }
    if parallel:
        with multiprocessing.Pool(processes=min(os.cpu_count() or 1, 8)) as pool:
            for combo, counters in pool.imap_unordered(_run_without_vc, ROW0_CHOICES):
                aggregate["nodes_visited"] += counters["nodes"]
                aggregate["full_assignments"] += counters["full"]
                aggregate["self_edge"] += counters["self_edge"]
                aggregate["strict_cycle"] += counters["strict_cycle"]
                aggregate["vc_pass"] += counters["vc_pass"]
    else:
        for combo in ROW0_CHOICES:
            counters = search_one_row0_no_vc(combo)
            aggregate["nodes_visited"] += counters["nodes"]
            aggregate["full_assignments"] += counters["full"]
            aggregate["self_edge"] += counters["self_edge"]
            aggregate["strict_cycle"] += counters["strict_cycle"]
            aggregate["vc_pass"] += counters["vc_pass"]
    return {"aggregate": aggregate}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out",
                        default="/home/user/erdos97/data/certificates/2026-05-06/n9_independent_audit.json")
    parser.add_argument("--no-parallel", action="store_true")
    args = parser.parse_args()

    parallel = not args.no_parallel

    print(f"=== Independent n=9 vertex-circle audit ===", file=sys.stderr)
    print(f"row0 choices: {len(ROW0_CHOICES)}", file=sys.stderr)
    print(f"INDEGREE_CAP = {INDEGREE_CAP}", file=sys.stderr)
    print(f"PAIR_CAP = {PAIR_CAP}, TWO_CIRCLE_CAP = {TWO_CIRCLE_CAP}", file=sys.stderr)

    t0 = time.time()
    main_result = run_main(parallel=parallel)
    t_main = time.time() - t0
    print(f"\n[main pass with vertex-circle pruning] time={t_main:.1f}s", file=sys.stderr)
    print(json.dumps(main_result["aggregate"], indent=2), file=sys.stderr)

    t0 = time.time()
    nv_result = run_no_vc(parallel=parallel)
    t_nv = time.time() - t0
    print(f"\n[cross-check without vertex-circle] time={t_nv:.1f}s", file=sys.stderr)
    print(json.dumps(nv_result["aggregate"], indent=2), file=sys.stderr)

    # Compare against the expected/checked-in counts
    expected_main = {
        "row0_choices": 70,
        "nodes_visited": 16752,
        "full_assignments": 0,
        "partial_self_edge": 11271,
        "partial_strict_cycle": 11011,
    }
    expected_nv = {
        "row0_choices": 70,
        "nodes_visited": 100817,
        "full_assignments": 184,
        "self_edge": 158,
        "strict_cycle": 26,
    }

    main_match = main_result["aggregate"] == expected_main
    nv_match_modulo_pass = (
        nv_result["aggregate"]["row0_choices"] == expected_nv["row0_choices"]
        and nv_result["aggregate"]["nodes_visited"] == expected_nv["nodes_visited"]
        and nv_result["aggregate"]["full_assignments"] == expected_nv["full_assignments"]
        and nv_result["aggregate"]["self_edge"] == expected_nv["self_edge"]
        and nv_result["aggregate"]["strict_cycle"] == expected_nv["strict_cycle"]
    )

    verdict_lines = []
    if main_result["aggregate"]["full_assignments"] == 0:
        verdict_lines.append("AGREE: 0 full assignments survive in main pass")
    else:
        verdict_lines.append(f"DISAGREE: {main_result['aggregate']['full_assignments']} full assignments survive in main pass")

    if main_match:
        verdict_lines.append("EXACT-MATCH: main-pass counters identical to checked-in artifact")
    else:
        verdict_lines.append("DIFF: main-pass counters differ from checked-in artifact (see below)")

    if nv_match_modulo_pass:
        verdict_lines.append("EXACT-MATCH: cross-check-pass counters identical to checked-in artifact")
    else:
        verdict_lines.append("DIFF: cross-check-pass counters differ from checked-in artifact (see below)")

    output = {
        "type": "n9_independent_audit",
        "trust": "MACHINE_CHECKED_FINITE_CASE_INDEPENDENT_AUDIT",
        "n": N,
        "row_size": ROW_SIZE,
        "indegree_cap": INDEGREE_CAP,
        "filters_applied": [
            "F1 pair-cap (each unordered witness-witness pair in <= 2 rows)",
            "F2 two-circle-cap (|S_i & S_j| <= 2)",
            "F3 crossing (shared two-witnesses cross source chord)",
            "F4 indegree cap (each vertex appears in <= floor(2*(n-1)/(k-1)) rows)",
            "F5 vertex-circle nested-chord strict-monotonicity self-edge / strict-cycle",
        ],
        "main_pass": main_result["aggregate"],
        "cross_check_pass": nv_result["aggregate"],
        "expected_main_pass": expected_main,
        "expected_cross_check_pass": expected_nv,
        "main_pass_matches_expected": main_match,
        "cross_check_matches_expected": nv_match_modulo_pass,
        "verdict": verdict_lines,
        "elapsed_seconds": {"main": t_main, "cross_check": t_nv},
        "implementation_independence_notes": [
            "Re-derived UnionFind, vertex_circle_check, and witness candidates from the geometric necessary conditions only",
            "Did not import or re-execute erdos97.n9_vertex_circle_exhaustive or scripts/check_n9_vertex_circle_exhaustive",
            "Branches rows in increasing label order (label-order, not minimum-remaining-options)",
            "Strict-cycle detection by Kahn's algorithm; self-edge detection by checking ro==ri before adding edge",
        ],
    }
    print("\n=== verdict ===", file=sys.stderr)
    for line in verdict_lines:
        print("  " + line, file=sys.stderr)
    if args.write:
        with open(args.out, "w") as fh:
            json.dump(output, fh, indent=2, sort_keys=True)
        print(f"\nWrote {args.out}", file=sys.stderr)

    print(json.dumps({k: v for k, v in output.items()
                      if k not in ("expected_main_pass", "expected_cross_check_pass")},
                     indent=2, default=str)[:4000])
    return 0


if __name__ == "__main__":
    sys.exit(main())
