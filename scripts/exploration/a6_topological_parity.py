#!/usr/bin/env python3
"""A6: Topological / degree / parity obstruction for Erdos Problem #97.

EXPLORATION script. It does NOT prove Erdos Problem #97, does NOT claim a
counterexample, and does NOT certify Euclidean realizability. All combinatorics
here are exact (integer / set arithmetic). The only geometric ingredient is
lemma L6 (radical-axis perpendicularity), which is already proved in the repo.

GOAL
----
Isolate a concrete *parity / first-Z2-cohomology* invariant that generalizes the
canonical n=7 perpendicularity-cycle argument, and run it on the frontier
objects:

  * n=7 Fano dihedral classes (input: data/incidence/n7_fano_dihedral_representatives.json),
  * n=8 15 survivor incidence classes (input: data/incidence/n8_reconstructed_15_survivors.json),
  * n=9 184 frontier selected-witness systems
    (input: data/certificates/n9_vertex_circle_frontier_motif_classification.json).

THE INVARIANT (perpendicularity-graph bipartiteness / Z2 slope-consistency)
---------------------------------------------------------------------------
Lemma L6: if centers i,j share exactly two selected witnesses W_i cap W_j={a,b},
then the chord p_i p_j is perpendicular to the chord p_a p_b (both centers lie
on the perpendicular bisector of segment ab).

Form the *perpendicularity graph* G_perp on the set of unordered vertex-chords:
put an (undirected) edge between chord {i,j} and chord {a,b} whenever
W_i cap W_j = {a,b}. Every edge of G_perp asserts "these two chords are
perpendicular".

Assign to every chord e its slope class theta(e) in RP^1 (an angle mod pi,
i.e. an element of R/(pi Z)). Perpendicularity is the FIXED-POINT-FREE involution
theta -> theta + pi/2 on RP^1. So along any path in G_perp the slope alternates
by +pi/2 each step. Around a CLOSED WALK of odd length, the slope would have to
return to itself after an odd number of +pi/2 turns, i.e. theta = theta + pi/2
in R/(pi Z) -- impossible for a nonzero chord (and strict convexity forbids zero
chords, since all vertices are distinct: lemma L2).

Hence a NECESSARY condition for Euclidean realizability is:

    G_perp has no odd cycle  <=>  G_perp is bipartite.

This is exactly a *Z2 1-cocycle / 2-coloring* obstruction: assign each chord a
color in Z2 = {horizontal-ish class, vertical-ish class}; each perp edge demands
opposite colors; bipartiteness is solvability of this Z2 system. The "invariant"
that must vanish is the sum of the edge-cochain (all-ones in Z2) over a cycle
basis: it must be 0 in H^1(G_perp; Z2). Equivalently, NO cycle of G_perp may be
odd.

This is the n-independent generalization of the n=7 argument. At n=7 the map
phi(e)=W_i cap W_j is a permutation of all 21 chords, so G_perp is a disjoint
union of the functional-graph cycles of phi, and "21 objects" forces an odd
cycle. For n>=8 phi need not be a permutation, so G_perp is a more general
graph; the bipartiteness test is the right invariant and is checked directly.

STRICT CONVEXITY USAGE (mandatory per problem constraints)
----------------------------------------------------------
1. L6 itself: the perpendicular bisector of ab meets a strictly convex polygon in
   at most 2 vertices, and BOTH centers i,j lie on it; this is what pins
   {i,j} perp {a,b}. (Non-convex configs can violate the "at most 2 on a line"
   premise that makes the chord map well behaved.)
2. Zero-chord exclusion uses L2 (no two vertices coincide), which is strict
   convexity. Without it theta(e) is undefined and the involution argument fails.
3. The PARALLEL refinement (below) uses L3 cyclic=angular order indirectly:
   two distinct chords that are forced PARALLEL and share a vertex would create
   three collinear vertices, impossible by L2.

We also include a strictly-stronger RP^1 / parallel-class refinement that the
plain bipartiteness test misses:

  * Build the same graph but track BOTH relations: perp edges (slope flips) and
    *parallel* edges (slope equal). Parallel edges arise when bipartite color
    classes within one connected component force two chords into the same slope
    class. Two parallel chords sharing an endpoint => 3 collinear vertices
    (forbidden). This is the "same-color forced-parallel chord class sharing an
    endpoint" filter already named in the n=8 enumerator; we re-derive it as the
    *coloring* layer sitting on top of the parity layer, to measure whether the
    pure parity layer adds anything beyond what the n=8 pipeline already uses.

OUTPUT
------
For each frontier family, report:
  - number of systems whose G_perp is NON-bipartite (killed by pure parity),
  - number additionally killed by the parallel-endpoint refinement,
  - number surviving BOTH (i.e. parity underdetermines them).
Plus the n=7 sanity check that all classes are non-bipartite.
"""

from __future__ import annotations

import json
import sys
from collections import deque
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


# ---------------------------------------------------------------------------
# Core combinatorics: build the perpendicularity graph from selected rows.
# ---------------------------------------------------------------------------

def rows_to_witnesses(selected_rows):
    """Convert [center, w1, w2, w3, w4]-style rows to a dict center -> frozenset.

    Accepts either the n9 frontier shape (first entry is the center) or a plain
    list-of-witness-sets indexed by center (n7/n8 reconstruction shapes), which
    we detect and route via `adjacency_to_witnesses` separately.
    """
    W = {}
    for row in selected_rows:
        center = row[0]
        witnesses = frozenset(row[1:])
        W[center] = witnesses
    return W


def adjacency_to_witnesses(rows):
    """n8 survivor shape: 0/1 adjacency matrix rows -> dict center->frozenset."""
    W = {}
    for i, row in enumerate(rows):
        W[i] = frozenset(j for j, v in enumerate(row) if v == 1 and j != i)
    return W


def perpendicularity_edges(W):
    """List of (center_chord, common_witness_chord) for every 2-overlap pair.

    Each is an unordered chord as a sorted tuple. The pair asserts L6
    perpendicularity between the two chords.
    """
    centers = sorted(W)
    edges = []
    for i, j in combinations(centers, 2):
        common = W[i] & W[j]
        if len(common) == 2:
            ij = tuple(sorted((i, j)))
            ab = tuple(sorted(common))
            edges.append((ij, ab))
    return edges


def build_perp_graph(edges):
    """Undirected graph on chords; edges are perpendicularity constraints.

    Returns adjacency dict chord -> set(chord). Self-loops (a chord forced
    perpendicular to itself, i.e. {i,j} == {a,b}) are recorded specially: that
    is already an immediate contradiction (a chord cannot be perpendicular to
    itself). In a valid selected system this should not occur because the
    common-witness chord is disjoint from {i,j} when i,j are not witnesses of
    each other; we still guard for it.
    """
    adj = {}
    self_perp = []
    for u, v in edges:
        if u == v:
            self_perp.append(u)
            continue
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    return adj, self_perp


def two_color(adj):
    """Try to 2-color the perpendicularity graph.

    Returns (is_bipartite, coloring, odd_cycle_witness).
    coloring maps chord -> 0/1 (color/slope-class). On failure, returns one odd
    closed walk as a list of chords (witness of non-bipartiteness).
    """
    color = {}
    for start in adj:
        if start in color:
            continue
        color[start] = 0
        parent = {start: None}
        dq = deque([start])
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if w not in color:
                    color[w] = color[u] ^ 1
                    parent[w] = u
                    dq.append(w)
                elif color[w] == color[u]:
                    # odd cycle found: reconstruct
                    cyc = _odd_cycle(parent, u, w)
                    return False, color, cyc
    return True, color, None


def _odd_cycle(parent, u, w):
    """Reconstruct an odd cycle from a same-color edge (u,w) in a BFS tree."""
    pu = [u]
    x = u
    while parent.get(x) is not None:
        x = parent[x]
        pu.append(x)
    pw = [w]
    y = w
    while parent.get(y) is not None:
        y = parent[y]
        pw.append(y)
    set_pu = {node: idx for idx, node in enumerate(pu)}
    lca = None
    for node in pw:
        if node in set_pu:
            lca = node
            break
    cyc = []
    for node in pu:
        cyc.append(node)
        if node == lca:
            break
    tail = []
    for node in pw:
        if node == lca:
            break
        tail.append(node)
    cyc.extend(reversed(tail))
    return cyc


def parallel_endpoint_violation(adj, color):
    """Refinement: within a bipartite component, equal-color chords are PARALLEL.

    Two parallel chords sharing a vertex => 3 collinear polygon vertices (L2
    violation under strict convexity). Return a witness (chord_u, chord_v,
    shared_vertex) if found, else None. Only meaningful when `adj` is bipartite.
    """
    # group chords by (component_root color). Two chords in the same connected
    # component with the same color are forced parallel.
    comp_id = {}
    cid = 0
    for start in adj:
        if start in comp_id:
            continue
        # BFS to label component
        dq = deque([start])
        comp_id[start] = cid
        while dq:
            u = dq.popleft()
            for w in adj[u]:
                if w not in comp_id:
                    comp_id[w] = cid
                    dq.append(w)
        cid += 1
    # bucket chords by (component, color)
    buckets = {}
    for chord in adj:
        key = (comp_id[chord], color[chord])
        buckets.setdefault(key, []).append(chord)
    for key, chords in buckets.items():
        for u, v in combinations(chords, 2):
            shared = set(u) & set(v)
            if shared:
                return (u, v, sorted(shared))
    return None


def analyze_system(W):
    """Full parity analysis of one selected-witness system given W dict."""
    edges = perpendicularity_edges(W)
    adj, self_perp = build_perp_graph(edges)
    result = {
        "num_two_overlap_pairs": len(edges),
        "num_perp_chords": len(adj),
        "self_perp": bool(self_perp),
    }
    if self_perp:
        result["bipartite"] = False
        result["killed_by_parity"] = True
        result["odd_cycle_len"] = 1
        result["parallel_endpoint_violation"] = None
        return result
    is_bip, color, cyc = two_color(adj)
    result["bipartite"] = is_bip
    result["killed_by_parity"] = not is_bip
    result["odd_cycle_len"] = (len(cyc) if cyc else None)
    if is_bip:
        pv = parallel_endpoint_violation(adj, color)
        result["parallel_endpoint_violation"] = pv
    else:
        result["parallel_endpoint_violation"] = None
    return result


# ---------------------------------------------------------------------------
# Frontier loaders
# ---------------------------------------------------------------------------

def analyze_n7():
    path = ROOT / "data" / "incidence" / "n7_fano_dihedral_representatives.json"
    data = json.loads(path.read_text())
    reps = data["representatives"]
    out = []
    for rep in reps:
        Wrows = rep["witnesses_W"]  # list of 4-witness rows indexed by center
        W = {i: frozenset(row) for i, row in enumerate(Wrows)}
        out.append(analyze_system(W))
    return out


def analyze_n8():
    path = ROOT / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    data = json.loads(path.read_text())
    out = []
    for entry in data:
        W = adjacency_to_witnesses(entry["rows"])
        out.append(analyze_system(W))
    return out


def analyze_n9():
    path = (
        ROOT / "data" / "certificates"
        / "n9_vertex_circle_frontier_motif_classification.json"
    )
    data = json.loads(path.read_text())
    out = []
    for a in data["assignments"]:
        W = rows_to_witnesses(a["selected_rows"])
        res = analyze_system(W)
        res["assignment_id"] = a["assignment_id"]
        res["status"] = a["status"]
        out.append(res)
    return out


def summarize(name, results):
    n = len(results)
    killed_parity = sum(1 for r in results if r["killed_by_parity"])
    bip = sum(1 for r in results if r.get("bipartite"))
    parallel_kill = sum(
        1 for r in results
        if r.get("bipartite") and r.get("parallel_endpoint_violation") is not None
    )
    survive_both = sum(
        1 for r in results
        if r.get("bipartite") and r.get("parallel_endpoint_violation") is None
    )
    overlaps = [r["num_two_overlap_pairs"] for r in results]
    perpchords = [r["num_perp_chords"] for r in results]
    summary = {
        "family": name,
        "systems": n,
        "killed_by_pure_parity_nonbipartite": killed_parity,
        "bipartite": bip,
        "additionally_killed_by_parallel_endpoint": parallel_kill,
        "survive_parity_and_parallel": survive_both,
        "two_overlap_pairs_min_max": [min(overlaps), max(overlaps)] if overlaps else None,
        "perp_chords_min_max": [min(perpchords), max(perpchords)] if perpchords else None,
    }
    return summary


def main():
    families = []
    n7 = analyze_n7()
    families.append(summarize("n7_fano_dihedral_classes", n7))
    n8 = analyze_n8()
    families.append(summarize("n8_15_survivor_classes", n8))
    n9 = analyze_n9()
    families.append(summarize("n9_184_frontier", n9))

    report = {
        "invariant": "perpendicularity-graph bipartiteness (Z2 slope-consistency / H^1(G_perp;Z2))",
        "strict_convexity_used": [
            "L6 radical-axis perpendicularity (needs perp bisector meets strict polygon in <=2 vertices)",
            "L2 no two vertices coincide => chords nonzero => slope defined",
            "parallel-endpoint refinement uses L2 (no 3 collinear)",
        ],
        "families": families,
    }
    print(json.dumps(report, indent=2))

    # n9 per-status breakdown of survivors, to see where parity fails to cut.
    by_status = {}
    for r in n9:
        st = r["status"]
        d = by_status.setdefault(st, {"total": 0, "killed_parity": 0, "killed_parallel": 0, "survive": 0})
        d["total"] += 1
        if r["killed_by_parity"]:
            d["killed_parity"] += 1
        elif r.get("parallel_endpoint_violation") is not None:
            d["killed_parallel"] += 1
        else:
            d["survive"] += 1
    print("\n# n9 breakdown by vertex-circle status (for cross-check):", file=sys.stderr)
    print(json.dumps(by_status, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
