"""Bridge Lemma A' attack tests.

We test the central computational hypothesis: if a witness pattern is non-ear-orderable,
does it always have a chord-length collapse forcing a strict cycle (vertex-circle)?

Concretely: enumerate (combinatorially) all 4-regular witness patterns up to small n,
under the necessary filters (pair-cap, crossing, indegree, vertex-circle),
and check whether ear-orderable is a strict superset of vertex-circle-passable.

We also test specific obstruction conjectures:

H1: Every non-ear-orderable pattern at n in {7, 8, 9, 10} has vertex-circle obstruction.

H2: Every K_4-bicycle stuck core (4 vertices, each with 2 internal selected witnesses)
    forces a 3-cycle in some chord-length class quotient.

H3: For the Bridge Lemma A' to fail, you'd need a non-ear-orderable pattern that ALSO
    survives all filters (pair-cap, crossing, vertex-circle, perp-bisector). At n=7,8,9
    this is impossible by current data; we want to enumerate at n=10 to see.

If H1 + H2 hold up to higher n, that's strong evidence the Bridge Lemma A' is true.
"""

from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict
from itertools import combinations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

from erdos97.n9_vertex_circle_exhaustive import (
    N as _N9, OPTIONS as _OPTIONS_9, PAIRS as _PAIRS_9, MASK_BITS as _MB_9,
    SELECTED_PAIR_INDICES as _SPI_9, STRICT_EDGES as _SE_9, UnionFind, mask, vertex_circle_status,
)


def rows_to_masks(rows):
    return [sum(1 << v for v in row) for row in rows]


def is_ear_orderable(rows, threshold=3):
    n = len(rows)
    masks = rows_to_masks(rows)
    full = (1 << n) - 1
    memo = {}

    def can_peel(sm):
        if sm in memo:
            return memo[sm]
        sz = bin(sm).count("1")
        if sz <= threshold:
            memo[sm] = True
            return True
        for c in range(n):
            if not ((sm >> c) & 1):
                continue
            if bin(masks[c] & sm).count("1") >= threshold:
                if can_peel(sm & ~(1 << c)):
                    memo[sm] = True
                    return True
        memo[sm] = False
        return False

    return can_peel(full)


# --------------------------------------------------------------------------
# Hypothesis 1 verification at n=8 and n=9
# --------------------------------------------------------------------------

def verify_h1_n8():
    import json
    path = os.path.join(REPO, "data/incidence/n8_reconstructed_15_survivors.json")
    with open(path) as f:
        data = json.load(f)
    n8 = [(s["id"], [[j for j, v in enumerate(r) if v] for r in s["rows"]]) for s in data]

    # at n=8 we need a vertex-circle checker. The n9 module has N=9, so we replicate logic.
    print("n=8 H1 check (vertex-circle status of all 15):")
    for pid, rows in n8:
        vc = vertex_circle_status_n(rows, 8)
        ear = is_ear_orderable(rows)
        print(f"  id={pid}: ear={ear}, vertex_circle={vc}")


def vertex_circle_status_n(rows, n):
    """Replicate vertex_circle_status for arbitrary n."""
    PAIRS = [(i, j) for i in range(n) for j in range(i + 1, n)]
    PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

    def pair(a, b):
        return (a, b) if a < b else (b, a)

    uf = UnionFind(len(PAIRS))
    for c, row in enumerate(rows):
        sp = [PAIR_INDEX[pair(c, w)] for w in row]
        for pidx in sp[1:]:
            uf.union(sp[0], pidx)

    # build strict edges per row: for each row sorted by cyclic angle from center,
    # pairs (witnesses[i], witnesses[j]) with i<j strictly contain pairs (witnesses[k], witnesses[l]) with i<=k, l<=j, strict
    graph = defaultdict(set)
    self_edge = False
    for c, row in enumerate(rows):
        # natural cyclic order: order witnesses by (w - c) % n
        witnesses = sorted(row, key=lambda w: (w - c) % n)
        for outer_start in range(4):
            for outer_end in range(outer_start + 1, 4):
                for inner_start in range(4):
                    for inner_end in range(inner_start + 1, 4):
                        if (outer_start, outer_end) == (inner_start, inner_end):
                            continue
                        contains = (
                            outer_start <= inner_start
                            and inner_end <= outer_end
                            and (outer_start < inner_start or inner_end < outer_end)
                        )
                        if contains:
                            outer = pair(witnesses[outer_start], witnesses[outer_end])
                            inner = pair(witnesses[inner_start], witnesses[inner_end])
                            o = uf.find(PAIR_INDEX[outer])
                            i = uf.find(PAIR_INDEX[inner])
                            if o == i:
                                self_edge = True
                            graph[o].add(i)
    if self_edge:
        return "self_edge"

    # detect cycle
    color = {}

    def dfs(node):
        color[node] = 1
        for nxt in graph.get(node, []):
            if color.get(nxt, 0) == 1:
                return True
            if color.get(nxt, 0) == 0 and dfs(nxt):
                return True
        color[node] = 2
        return False

    for nd in list(graph):
        if color.get(nd, 0) == 0 and dfs(nd):
            return "strict_cycle"
    return "ok"


# --------------------------------------------------------------------------
# Hypothesis 2: K_4-bicycle stuck core => UF 3-cycle
# --------------------------------------------------------------------------

def has_k4_bicycle(rows):
    n = len(rows)
    masks = rows_to_masks(rows)
    for sub in combinations(range(n), 4):
        sm = sum(1 << v for v in sub)
        if all(bin(masks[c] & sm).count("1") == 2 for c in sub):
            return sub
    return None


# --------------------------------------------------------------------------
# Test: enumerate all 4-regular witness patterns at n=7 with pair-cap & crossing
# Filter for ear-orderable vs not, and check which are killable.
# --------------------------------------------------------------------------

def chords_cross(a, b, c, d, order):
    """Strict crossing in given cyclic order."""
    pos = {v: i for i, v in enumerate(order)}
    pa, pb, pc, pd = pos[a], pos[b], pos[c], pos[d]
    n = len(order)
    # rotate so pa = 0
    delta_b = (pb - pa) % n
    delta_c = (pc - pa) % n
    delta_d = (pd - pa) % n
    # c, d on different sides of chord (0, delta_b)?
    return (delta_c < delta_b) != (delta_d < delta_b) and pc != pa and pd != pa and pc != pb and pd != pb


def enumerate_n_patterns(n, max_count=2000):
    """Generate 4-out-regular witness patterns under filters (pair-cap, crossing)."""
    PAIRS = [(i, j) for i in range(n) for j in range(i + 1, n)]
    PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

    def pair_(a, b):
        return (a, b) if a < b else (b, a)

    natural = list(range(n))

    # Per-center options (4-subsets)
    OPTS = []
    for c in range(n):
        opts = []
        for combo in combinations([t for t in range(n) if t != c], 4):
            opts.append(set(combo))
        OPTS.append(opts)

    patterns = []

    def rows_compatible(c1, w1, c2, w2):
        common = w1 & w2
        if len(common) > 2:
            return False
        if len(common) == 2:
            ca, cb = sorted(common)
            return chords_cross(c1, c2, ca, cb, natural)
        return True

    def search(assign, column_counts, witness_pair_counts):
        if len(patterns) >= max_count:
            return
        if len(assign) == n:
            patterns.append([sorted(assign[c]) for c in range(n)])
            return
        # MRV
        best_c = None
        best_opts = None
        for c in range(n):
            if c in assign:
                continue
            opts = []
            for w in OPTS[c]:
                ok = True
                for c2, w2 in assign.items():
                    if not rows_compatible(c, w, c2, w2):
                        ok = False
                        break
                if not ok:
                    continue
                # column cap = floor(2*(n-1)/3) for row size 4
                indeg_cap = (2 * (n - 1)) // 3
                if any(column_counts[t] + 1 > indeg_cap for t in w):
                    continue
                # pair cap
                if any(witness_pair_counts[PAIR_INDEX[pair_(a, b)]] >= 2 for a, b in combinations(w, 2)):
                    continue
                opts.append(w)
            if best_opts is None or len(opts) < len(best_opts):
                best_c = c
                best_opts = opts
                if not opts:
                    return
        c = best_c
        for w in best_opts:
            assign[c] = w
            for t in w:
                column_counts[t] += 1
            for a, b in combinations(w, 2):
                witness_pair_counts[PAIR_INDEX[pair_(a, b)]] += 1
            search(assign, column_counts, witness_pair_counts)
            for a, b in combinations(w, 2):
                witness_pair_counts[PAIR_INDEX[pair_(a, b)]] -= 1
            for t in w:
                column_counts[t] -= 1
            del assign[c]

    search({}, [0] * n, [0] * len(PAIRS))
    return patterns


def main():
    print("=" * 70)
    print("Hypothesis 1: every non-ear pattern is killed by vertex-circle")
    print("=" * 70)
    verify_h1_n8()

    print()
    print("=" * 70)
    print("n=7 enumeration (4-regular under pair-cap & crossing)")
    print("=" * 70)
    pats = enumerate_n_patterns(7, max_count=10000)
    print(f"# patterns found: {len(pats)}")
    n_ear = sum(1 for p in pats if is_ear_orderable(p))
    n_nonear = len(pats) - n_ear
    print(f"  ear-orderable: {n_ear}, non-ear: {n_nonear}")
    if n_nonear:
        non_ear = [p for p in pats if not is_ear_orderable(p)]
        # check vertex-circle
        kills = Counter()
        for p in non_ear:
            kills[vertex_circle_status_n(p, 7)] += 1
        print(f"  Vertex-circle status of non-ear: {dict(kills)}")
        # Show one
        if non_ear:
            print(f"  Sample non-ear pattern at n=7: {non_ear[0]}")


if __name__ == "__main__":
    main()
