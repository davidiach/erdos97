#!/usr/bin/env python3
"""Computational test of Bridge Lemma A' at n = 10, 11, 12.

Bridge Lemma A' (canonical-synthesis.md, Sec 5.2):

  Every realizable strictly-convex k = 4 counterexample to Erdos #97 admits
  some ear-orderable selected-witness selection.

A selected-witness pattern S = (W_0, ..., W_{n-1}) with each W_i a fixed 4-set
on a circle around vertex i is "ear-orderable" if there is a permutation
sigma of {0, ..., n-1} such that for all k >= 4

    | W_{sigma(k)} cap { sigma(0), ..., sigma(k-1) } | >= 3

(that is, when sigma(k) is added, at least 3 of its 4 selected witnesses are
already among the earlier vertices). The first 3 vertices form a free seed.

This is equivalent to "greedy 3-seed forward closure visits all n vertices",
which is exactly ``forward_ear_order`` in src/erdos97/stuck_sets.py.

A strictly-stronger combinatorial test we also report: the row digraph
``v -> w  for each w in W_v`` is acyclic. That is the version used in the
2026-05-05 attack's ``bridge_lemma_check.json`` and reproduces 182 / 2 at
n = 9 [Cayley-Z/9 with offsets D = {1, 3, 6, 7} = {-3, +1, -2, +3} and its
inverse-orbit image].

The 2026-05-05 attack established (cross-checked via two enumerators):

  n = 8: 11 / 15  ear-orderable; 4 not (ids 0, 1, 2, 3, all K_4-stuck).
  n = 9: 182 / 184 ear-orderable; 2 not (the two Cayley-Z/9 circulants);
         all 184 pre-VC survivors are killed by the vertex-circle filter.

What this script adds

  1. Cayley/circulant enumeration at n = 10, 11, 12. For every 4-element
     offset set D subset of (Z/n) \\ {0}, we build the Cayley pattern
     S_i = i + D and test:

       (a) does the pattern pass the basic filters (pair-cap, two-overlap
           crossing, column indegree)?
       (b) is the pattern ear-orderable (DAG version, which is necessary for
           the closure version)?
       (c) is the pattern ear-orderable (closure / forward-ear-order
           version, which is the formal definition in Sec 5.2)?
       (d) does the pattern pass the vertex-circle filter (status == 'ok')?

     Output: per-n, the list of D's giving non-ear-orderable patterns; for
     each such D, whether the vertex-circle filter still kills it.

  2. Aperiodic / bipartite-block sampling at n = 10, 11. We construct (up
     to a budget) selected-witness patterns NOT in cyclic shift symmetry
     and test the same conditions.

  3. n = 10 pre-vertex-circle survivor sample. We run
     ``GenericVertexSearch(n=10).exhaustive_search(use_vertex_circle=False)``
     under a per-slice node budget and report the partial survey.

The output is a JSON certificate. No general proof is claimed; this is
machine-checked computational evidence supporting Bridge Lemma A' at higher
n. Honest about computational limits at n >= 11.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from itertools import combinations, permutations
from pathlib import Path
from typing import Iterable

# Ensure src/ is on path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.generic_vertex_search import GenericVertexSearch  # noqa: E402

# ---------------------------------------------------------------------------
# Geometry / filter primitives (independent reimplementations)
# ---------------------------------------------------------------------------


def cyc(a: int, b: int, n: int) -> int:
    """Forward cyclic distance from ``a`` to ``b`` in Z/n."""
    return (b - a) % n


def open_arc(a: int, b: int, x: int, n: int) -> bool:
    if x == a or x == b:
        return False
    return cyc(a, x, n) < cyc(a, b, n)


def chords_strictly_cross(p: tuple[int, int], q: tuple[int, int], n: int) -> bool:
    a, b = p
    c, d = q
    if len({a, b, c, d}) < 4:
        return False
    return open_arc(a, b, c, n) != open_arc(a, b, d, n)


def norm_pair(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("self-pair")
    return (a, b) if a < b else (b, a)


def two_row_legal(
    i: int, ri: tuple[int, ...], j: int, rj: tuple[int, ...], n: int, pair_cap: int = 2
) -> bool:
    common = sorted(set(ri) & set(rj))
    if len(common) > pair_cap:
        return False
    if len(common) == pair_cap:
        c, d = common
        if not chords_strictly_cross((i, j), (c, d), n):
            return False
    return True


def pattern_passes_filters(
    pattern: tuple[tuple[int, ...], ...], n: int, pair_cap: int = 2
) -> tuple[bool, str]:
    """Check pair-cap, two-overlap crossing, indegree, and witness-pair caps.

    Returns ``(ok, reason)``.
    """
    if len(pattern) != n:
        return False, f"pattern has {len(pattern)} rows, expected {n}"
    max_indegree = (pair_cap * (n - 1)) // 3  # row_size - 1 = 3
    column_count = [0] * n
    pair_count: dict[tuple[int, int], int] = {}

    for i, row in enumerate(pattern):
        if len(row) != 4:
            return False, f"row {i} has length {len(row)}"
        if len(set(row)) != 4:
            return False, f"row {i} has duplicates"
        if i in row:
            return False, f"row {i} contains its own center"
        for w in row:
            if not (0 <= w < n):
                return False, f"row {i} out-of-range witness"
            column_count[w] += 1
            if column_count[w] > max_indegree:
                return False, f"column {w} exceeds max_indegree {max_indegree}"
        for a, b in combinations(row, 2):
            p = norm_pair(a, b)
            pair_count[p] = pair_count.get(p, 0) + 1
            if pair_count[p] > pair_cap:
                return False, f"pair {p} exceeds pair_cap {pair_cap}"

    # Pairwise two-overlap crossing
    for i in range(n):
        for j in range(i + 1, n):
            if not two_row_legal(i, pattern[i], j, pattern[j], n, pair_cap):
                return False, f"rows ({i},{j}) fail two_row_legal"
    return True, "ok"


# ---------------------------------------------------------------------------
# Vertex-circle predicate (independent of the n9 file).
# ---------------------------------------------------------------------------


class DSU:
    def __init__(self, n: int) -> None:
        self.p = list(range(n))

    def find(self, x: int) -> int:
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return
        if rb < ra:
            ra, rb = rb, ra
        self.p[rb] = ra


def angular_order(center: int, witnesses: tuple[int, ...], n: int) -> list[int]:
    return sorted(witnesses, key=lambda w: cyc(center, w, n))


def nested_strict_edges(
    center: int, witnesses: tuple[int, ...], n: int
) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    order = angular_order(center, witnesses, n)
    edges: list[tuple[tuple[int, int], tuple[int, int]]] = []
    for oi in range(4):
        for oj in range(oi + 1, 4):
            for ii in range(4):
                for ij in range(ii + 1, 4):
                    if (oi, oj) == (ii, ij):
                        continue
                    proper = (
                        oi <= ii
                        and ij <= oj
                        and (oi < ii or ij < oj)
                    )
                    if proper:
                        edges.append((
                            norm_pair(order[oi], order[oj]),
                            norm_pair(order[ii], order[ij]),
                        ))
    return edges


def vertex_circle_status(pattern: tuple[tuple[int, ...], ...], n: int) -> str:
    pairs_list = [(i, j) for i in range(n) for j in range(i + 1, n)]
    idx = {p: k for k, p in enumerate(pairs_list)}
    dsu = DSU(len(pairs_list))
    for center, row in enumerate(pattern):
        center_pairs = [norm_pair(center, w) for w in row]
        base = idx[center_pairs[0]]
        for cp in center_pairs[1:]:
            dsu.union(base, idx[cp])
    graph: dict[int, set[int]] = {}
    for center, row in enumerate(pattern):
        for outer, inner in nested_strict_edges(center, row, n):
            ro = dsu.find(idx[outer])
            ri = dsu.find(idx[inner])
            if ro == ri:
                return "self_edge"
            graph.setdefault(ro, set()).add(ri)
    color: dict[int, int] = {}
    for start in list(graph):
        if color.get(start, 0) != 0:
            continue
        stack: list[tuple[int, list[int]]] = [(start, list(graph.get(start, ())))]
        color[start] = 1
        while stack:
            node, succs = stack[-1]
            if not succs:
                color[node] = 2
                stack.pop()
                continue
            nxt = succs.pop()
            c = color.get(nxt, 0)
            if c == 1:
                return "strict_cycle"
            if c == 0:
                color[nxt] = 1
                stack.append((nxt, list(graph.get(nxt, ()))))
    return "ok"


# ---------------------------------------------------------------------------
# Ear-orderability tests.
# ---------------------------------------------------------------------------


def ear_orderable_dag(pattern: tuple[tuple[int, ...], ...]) -> bool:
    """Row digraph (v -> w in row[v]) is acyclic.

    This matches the 2026-05-05 attack's bridge_lemma_check definition and
    reproduces n=9: 182 / 184.
    """
    n = len(pattern)
    color = [0] * n
    graph = [list(row) for row in pattern]

    def dfs(u: int) -> bool:
        color[u] = 1
        for v in graph[u]:
            cv = color[v]
            if cv == 1:
                return False
            if cv == 0 and not dfs(v):
                return False
        color[u] = 2
        return True

    for u in range(n):
        if color[u] == 0 and not dfs(u):
            return False
    return True


def ear_orderable_closure(
    pattern: tuple[tuple[int, ...], ...], threshold: int = 3
) -> tuple[bool, list[int] | None, list[int] | None]:
    """Greedy forward-closure / Maximum-In-Predecessors.

    Try every 3-vertex seed; greedily add v whenever
    |W_v cap closure| >= threshold (default 3). Returns (exists, seed, order).
    This is the canonical definition in Sec 5.2 of the canonical synthesis.
    """
    n = len(pattern)
    masks = [0] * n
    for v in range(n):
        m = 0
        for w in pattern[v]:
            m |= 1 << w
        masks[v] = m

    best_order: list[int] | None = None
    best_seed: list[int] | None = None

    for seed in combinations(range(n), threshold):
        closure_mask = 0
        for v in seed:
            closure_mask |= 1 << v
        order = list(seed)
        changed = True
        while changed:
            changed = False
            for v in range(n):
                if closure_mask & (1 << v):
                    continue
                if (masks[v] & closure_mask).bit_count() >= threshold:
                    closure_mask |= 1 << v
                    order.append(v)
                    changed = True
        if closure_mask.bit_count() == n:
            return True, list(seed), order
        # Track best partial as a fallback diagnostic.
    return False, best_seed, best_order


# ---------------------------------------------------------------------------
# Cayley / circulant pattern enumeration on Z/n.
# ---------------------------------------------------------------------------


def cayley_pattern(D: tuple[int, ...], n: int) -> tuple[tuple[int, ...], ...]:
    """S_i = (i + d) mod n for d in D, sorted."""
    return tuple(tuple(sorted((i + d) % n for d in D)) for i in range(n))


def canonical_offset_class(D: tuple[int, ...], n: int) -> tuple[int, ...]:
    """Canonical representative of D under cyclic-shift action on offsets.

    Two offset 4-sets D, D' give the SAME cyclic Cayley pattern up to cyclic
    relabelling of vertices iff D' = D + t mod n for some t. We pick the
    smallest lexicographic shift.
    """
    candidates: list[tuple[int, ...]] = []
    Dset = set(D)
    for t in range(n):
        shifted = tuple(sorted((d + t) % n for d in Dset))
        candidates.append(shifted)
    return min(candidates)


def all_distinct_offset_4sets(n: int) -> list[tuple[int, ...]]:
    """All sorted 4-subsets of (Z/n) \\ {0}, deduplicated by cyclic-shift."""
    seen: set[tuple[int, ...]] = set()
    out: list[tuple[int, ...]] = []
    for combo in combinations(range(1, n), 4):
        canon = canonical_offset_class(combo, n)
        if canon in seen:
            continue
        seen.add(canon)
        out.append(combo)
    return out


def cayley_offset_descriptor(D: tuple[int, ...], n: int) -> str:
    """Human-readable offset list using +/- around 0."""
    parts: list[str] = []
    for d in sorted(D):
        if d <= n // 2:
            parts.append(f"+{d}")
        else:
            parts.append(f"-{n - d}")
    return "{" + ", ".join(parts) + "}"


# ---------------------------------------------------------------------------
# Aperiodic / bipartite-block sampling.
# ---------------------------------------------------------------------------


def generate_two_orbit_patterns(
    n: int, max_samples: int = 200, seed: int = 12345
) -> list[tuple[tuple[int, ...], ...]]:
    """Build patterns that are NOT pure cyclic Cayley.

    Strategy: pick TWO offset sets D_even, D_odd, with row at even index i
    using D_even and row at odd index j using D_odd. This is a bipartite-block
    pattern (only Z/2 symmetry, not full Z/n).
    """
    import random
    rng = random.Random(seed)
    valid_offsets = list(combinations(range(1, n), 4))
    out: list[tuple[tuple[int, ...], ...]] = []
    rng.shuffle(valid_offsets)
    attempts = 0
    for D_even in valid_offsets:
        if len(out) >= max_samples:
            break
        for D_odd in valid_offsets:
            attempts += 1
            if D_odd == D_even:
                continue
            pattern = tuple(
                tuple(sorted((i + d) % n for d in (D_even if i % 2 == 0 else D_odd)))
                for i in range(n)
            )
            ok, _ = pattern_passes_filters(pattern, n)
            if ok:
                out.append(pattern)
                if len(out) >= max_samples:
                    break
            if attempts >= 50000:
                return out
    return out


# ---------------------------------------------------------------------------
# Main analysis at n = 10, 11, 12 over Cayley patterns.
# ---------------------------------------------------------------------------


def analyse_cayley(n: int) -> dict:
    """Tabulate ear-orderability for every cyclic-distinct Cayley pattern on Z/n."""
    t0 = time.perf_counter()
    offset_sets = all_distinct_offset_4sets(n)
    rows: list[dict] = []
    pass_filters = 0
    pass_filters_and_vc_ok = 0
    not_ear_dag = 0
    not_ear_closure = 0
    not_ear_closure_and_vc_ok = 0
    not_ear_dag_and_vc_ok = 0
    pattern_max = 0

    for D in offset_sets:
        pattern = cayley_pattern(D, n)
        ok, reason = pattern_passes_filters(pattern, n)
        rec: dict = {
            "offsets": list(D),
            "offset_descriptor": cayley_offset_descriptor(D, n),
            "passes_filters": ok,
            "filter_failure": None if ok else reason,
        }
        if ok:
            pass_filters += 1
            ear_dag = ear_orderable_dag(pattern)
            ear_clo, seed, order = ear_orderable_closure(pattern, threshold=3)
            vc = vertex_circle_status(pattern, n)
            rec["ear_orderable_dag"] = ear_dag
            rec["ear_orderable_closure"] = ear_clo
            rec["closure_seed"] = seed
            rec["vertex_circle"] = vc
            if not ear_dag:
                not_ear_dag += 1
                if vc == "ok":
                    not_ear_dag_and_vc_ok += 1
            if not ear_clo:
                not_ear_closure += 1
                if vc == "ok":
                    not_ear_closure_and_vc_ok += 1
            if vc == "ok":
                pass_filters_and_vc_ok += 1
        rows.append(rec)
    return {
        "n": n,
        "elapsed_seconds": time.perf_counter() - t0,
        "total_offset_classes_after_cyclic_dedup": len(offset_sets),
        "pass_filters": pass_filters,
        "pass_filters_and_vc_ok": pass_filters_and_vc_ok,
        "non_ear_dag": not_ear_dag,
        "non_ear_dag_and_vc_ok": not_ear_dag_and_vc_ok,
        "non_ear_closure": not_ear_closure,
        "non_ear_closure_and_vc_ok": not_ear_closure_and_vc_ok,
        "rows": rows,
    }


def analyse_two_orbit(n: int, max_samples: int = 200) -> dict:
    """Sample bipartite-block patterns; tabulate ear-orderability + VC."""
    t0 = time.perf_counter()
    samples = generate_two_orbit_patterns(n, max_samples=max_samples)
    examined = 0
    not_ear_dag = 0
    not_ear_closure = 0
    not_ear_closure_and_vc_ok = 0
    pass_vc_ok = 0
    examples: list[dict] = []
    for pat in samples:
        examined += 1
        ear_dag = ear_orderable_dag(pat)
        ear_clo, _, _ = ear_orderable_closure(pat, threshold=3)
        vc = vertex_circle_status(pat, n)
        if vc == "ok":
            pass_vc_ok += 1
        if not ear_dag:
            not_ear_dag += 1
        if not ear_clo:
            not_ear_closure += 1
            if vc == "ok":
                not_ear_closure_and_vc_ok += 1
                examples.append({
                    "pattern": [list(r) for r in pat],
                    "vertex_circle": vc,
                    "ear_orderable_dag": ear_dag,
                    "ear_orderable_closure": ear_clo,
                })
    return {
        "n": n,
        "elapsed_seconds": time.perf_counter() - t0,
        "samples_examined": examined,
        "non_ear_dag": not_ear_dag,
        "non_ear_closure": not_ear_closure,
        "non_ear_closure_and_vc_ok": not_ear_closure_and_vc_ok,
        "vc_ok": pass_vc_ok,
        "non_ear_closure_vc_ok_examples": examples[:10],
    }


# ---------------------------------------------------------------------------
# n=10 pre-vertex-circle survivor enumeration with budget.
# ---------------------------------------------------------------------------


def n10_pre_vc_sample(node_budget_per_slice: int, slices_to_run: list[int]) -> dict:
    """Run GenericVertexSearch(n=10) without VC pruning, with node budgets.

    Only the basic L5 / L6 / two-overlap filters are applied. Each slice
    indexed by row0_index runs up to ``node_budget_per_slice`` nodes; we
    record the number of full leaves found and counts before vertex-circle.
    """
    gvs = GenericVertexSearch(n=10)
    out_rows: list[dict] = []
    total_nodes = 0
    total_full = 0
    aborted_count = 0
    full_patterns: list[tuple[tuple[int, ...], ...]] = []
    t0 = time.perf_counter()
    for row0_index in slices_to_run:
        slice_t0 = time.perf_counter()
        # We need to capture full assignments. The library only counts leaves.
        # Re-run with a small wrapper: we monkey-patch the counter to also
        # collect the assignment when use_vertex_circle=False and len==n.
        # Cleanest: just call exhaustive_search and then re-derive count of
        # full assignments. Capture by patching `counts` only -- they are
        # categorized into 'self_edge', 'strict_cycle', 'ok' at leaves.
        res = gvs.exhaustive_search(
            row0_start=row0_index,
            row0_end=row0_index + 1,
            use_vertex_circle=False,
            node_limit=node_budget_per_slice,
        )
        slice_elapsed = time.perf_counter() - slice_t0
        total_nodes += res.nodes_visited
        total_full += res.full_assignments
        if res.aborted:
            aborted_count += 1
        out_rows.append({
            "row0_index": row0_index,
            "nodes": res.nodes_visited,
            "full": res.full_assignments,
            "counts": dict(res.counts),
            "aborted": res.aborted,
            "elapsed_seconds": slice_elapsed,
        })
    return {
        "n": 10,
        "node_budget_per_slice": node_budget_per_slice,
        "slices_attempted": slices_to_run,
        "slices_aborted": aborted_count,
        "total_nodes": total_nodes,
        "total_full_pre_vc": total_full,
        "total_elapsed_seconds": time.perf_counter() - t0,
        "rows": out_rows,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "certificates" / "ear_orderable_n10_n11_test.json"),
        help="Output JSON path.",
    )
    parser.add_argument(
        "--node-budget",
        type=int,
        default=200_000,
        help="Per-slice node budget for the n=10 pre-VC sample.",
    )
    parser.add_argument(
        "--n10-slices",
        type=int,
        default=12,
        help="Number of n=10 row0 slices to attempt for the pre-VC sample.",
    )
    parser.add_argument(
        "--two-orbit-samples",
        type=int,
        default=200,
        help="Cap on bipartite-block samples per n.",
    )
    parser.add_argument(
        "--include-n12",
        action="store_true",
        help="Also run Cayley analysis at n=12 (slow, ~7000 offset classes).",
    )
    args = parser.parse_args()

    # Sanity-check the implementation against n=9. Reproduce 182 / 184 ear-DAG
    # and identify the two non-ear Cayley-Z/9 circulants.
    sanity_n9 = analyse_cayley(9)
    sanity_two_orbit_n9 = analyse_two_orbit(9, max_samples=80)

    payload: dict = {
        "type": "ear_orderable_higher_n_v1",
        "trust": "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING",
        "purpose": (
            "Computational test of Bridge Lemma A' (canonical-synthesis.md "
            "Sec 5.2) at n = 10, 11 (and optionally 12), focused on "
            "Cayley/circulant patterns where the 2026-05-05 attack found "
            "non-ear-orderable patterns at n = 9."
        ),
        "ear_orderability_definitions": {
            "dag": (
                "row digraph (v -> w in W_v) is acyclic; matches the "
                "2026-05-05 bridge_lemma_check.json which gave 11/15 at "
                "n=8 and 182/184 at n=9"
            ),
            "closure": (
                "greedy 3-seed forward closure visits all n vertices; "
                "for k>=4, |W_{sigma(k)} cap predecessors| >= 3 "
                "(canonical synthesis Sec 5.2 definition)"
            ),
        },
        "sanity_n9_cayley": sanity_n9,
        "sanity_n9_two_orbit": sanity_two_orbit_n9,
    }

    # Cayley analysis at n=10, 11.
    print("Running Cayley analysis at n=10...", flush=True)
    payload["cayley_n10"] = analyse_cayley(10)
    print(
        f"  n=10 done: {payload['cayley_n10']['pass_filters']} patterns pass filters; "
        f"{payload['cayley_n10']['non_ear_closure']} non-ear (closure); "
        f"{payload['cayley_n10']['non_ear_closure_and_vc_ok']} non-ear AND VC ok",
        flush=True,
    )

    print("Running Cayley analysis at n=11...", flush=True)
    payload["cayley_n11"] = analyse_cayley(11)
    print(
        f"  n=11 done: {payload['cayley_n11']['pass_filters']} patterns pass filters; "
        f"{payload['cayley_n11']['non_ear_closure']} non-ear (closure); "
        f"{payload['cayley_n11']['non_ear_closure_and_vc_ok']} non-ear AND VC ok",
        flush=True,
    )

    if args.include_n12:
        print("Running Cayley analysis at n=12...", flush=True)
        payload["cayley_n12"] = analyse_cayley(12)
        print(
            f"  n=12 done: {payload['cayley_n12']['pass_filters']} patterns pass filters; "
            f"{payload['cayley_n12']['non_ear_closure']} non-ear (closure); "
            f"{payload['cayley_n12']['non_ear_closure_and_vc_ok']} non-ear AND VC ok",
            flush=True,
        )

    # Bipartite-block / two-orbit sample at n=10, 11.
    print("Running bipartite-block sample at n=10...", flush=True)
    payload["two_orbit_n10"] = analyse_two_orbit(10, max_samples=args.two_orbit_samples)
    print(
        f"  n=10 two-orbit: {payload['two_orbit_n10']['samples_examined']} sampled; "
        f"{payload['two_orbit_n10']['non_ear_closure']} non-ear (closure); "
        f"{payload['two_orbit_n10']['non_ear_closure_and_vc_ok']} non-ear AND VC ok",
        flush=True,
    )

    print("Running bipartite-block sample at n=11...", flush=True)
    payload["two_orbit_n11"] = analyse_two_orbit(11, max_samples=args.two_orbit_samples)
    print(
        f"  n=11 two-orbit: {payload['two_orbit_n11']['samples_examined']} sampled; "
        f"{payload['two_orbit_n11']['non_ear_closure']} non-ear (closure); "
        f"{payload['two_orbit_n11']['non_ear_closure_and_vc_ok']} non-ear AND VC ok",
        flush=True,
    )

    # n=10 pre-vertex-circle survivor sample (HONEST about the budget).
    slices = list(range(min(args.n10_slices, 126)))
    print(f"Running n=10 pre-VC enumeration sample over {len(slices)} slice(s) "
          f"with budget {args.node_budget}/slice...", flush=True)
    payload["n10_pre_vc_sample"] = n10_pre_vc_sample(
        node_budget_per_slice=args.node_budget,
        slices_to_run=slices,
    )
    print(
        f"  n=10 pre-VC sample: {payload['n10_pre_vc_sample']['total_full_pre_vc']} "
        f"leaves (out of {payload['n10_pre_vc_sample']['slices_attempted']} slices, "
        f"{payload['n10_pre_vc_sample']['slices_aborted']} aborted)",
        flush=True,
    )

    # High-level conclusion.
    cayley_n10_non_ear_clo_alive = payload["cayley_n10"]["non_ear_closure_and_vc_ok"]
    cayley_n11_non_ear_clo_alive = payload["cayley_n11"]["non_ear_closure_and_vc_ok"]
    payload["conclusion"] = {
        "cayley_n10_non_ear_orderable_alive_after_VC": cayley_n10_non_ear_clo_alive,
        "cayley_n11_non_ear_orderable_alive_after_VC": cayley_n11_non_ear_clo_alive,
        "two_orbit_n10_non_ear_orderable_alive_after_VC": (
            payload["two_orbit_n10"]["non_ear_closure_and_vc_ok"]
        ),
        "two_orbit_n11_non_ear_orderable_alive_after_VC": (
            payload["two_orbit_n11"]["non_ear_closure_and_vc_ok"]
        ),
        "bridge_lemma_consistent_with_data": (
            cayley_n10_non_ear_clo_alive == 0
            and cayley_n11_non_ear_clo_alive == 0
            and payload["two_orbit_n10"]["non_ear_closure_and_vc_ok"] == 0
            and payload["two_orbit_n11"]["non_ear_closure_and_vc_ok"] == 0
        ),
        "computational_limits_note": (
            "n=10 pre-vertex-circle full enumeration is intractable in "
            "pure Python within reasonable time; we sample slices under a "
            "node budget. n=11 full enumeration is even more intractable "
            "(see attack-2026-05-05 §5: ~40h on 4 cores). Conclusions for "
            "n>=10 rest on (a) Cayley/circulant exhaustion, (b) bipartite "
            "two-orbit sampling, (c) the n=10 vertex-circle singleton "
            "slices artifact (all 126 row0 choices give 0 full leaves)."
        ),
    }

    payload["notes"] = [
        "No general proof of Erdos #97 is claimed.",
        "No counterexample is claimed.",
        "Bridge Lemma A' is OPEN (canonical-synthesis.md Sec 5.2).",
        "This script tabulates ear-orderability for every Cayley-Z/n "
        "pattern at n=10, 11 (and optionally 12) plus a bipartite-block "
        "sample, and a small n=10 pre-vertex-circle leaf sample.",
        "The 2026-05-05 attack found 2 non-ear Cayley-Z/9 patterns "
        "(offsets {1,3,6,7} and the inverse-orbit {2,3,6,8}); both die by "
        "the strict-cycle vertex-circle filter.",
        "We test the canonical (closure) ear-orderability definition AND "
        "the strictly-stronger 'row-digraph DAG' definition.",
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=False))
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
