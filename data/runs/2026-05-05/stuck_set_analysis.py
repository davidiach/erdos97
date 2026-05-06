"""Stuck-set census analysis for n=8, 9, 10.

Combinatorial enumeration: pairs (G, S) where G is a 4-regular witness pattern
and S subset V is a stuck set (every v in S has |E_v cap (S\{v})| <= 2).
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections import Counter, defaultdict
from itertools import combinations
from typing import Any

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))


# --------------------------------------------------------------------------
# Stuck-set core
# --------------------------------------------------------------------------

def rows_to_masks(rows: list[list[int]]) -> list[int]:
    masks = []
    for row in rows:
        m = 0
        for v in row:
            m |= 1 << v
        masks.append(m)
    return masks


def mask_to_list(m: int, n: int) -> list[int]:
    return [i for i in range(n) if (m >> i) & 1]


def find_all_stuck_sets(rows: list[list[int]], threshold: int = 3,
                        min_size: int = 4, max_size: int | None = None,
                        cap: int = 200_000) -> list[tuple[int, ...]]:
    """Return all stuck subsets S with |S| >= min_size, |S| <= max_size."""
    n = len(rows)
    if max_size is None:
        max_size = n
    masks = rows_to_masks(rows)
    stuck = []
    for size in range(min_size, max_size + 1):
        for subset in combinations(range(n), size):
            sm = 0
            for v in subset:
                sm |= 1 << v
            ok = True
            for c in subset:
                if bin(masks[c] & sm).count("1") >= threshold:
                    ok = False
                    break
            if ok:
                stuck.append(subset)
                if len(stuck) >= cap:
                    return stuck
    return stuck


def stuck_set_descriptor(rows: list[list[int]], subset: tuple[int, ...]) -> dict[str, Any]:
    n = len(rows)
    masks = rows_to_masks(rows)
    sm = 0
    for v in subset:
        sm |= 1 << v
    rows_info = []
    for c in subset:
        inside = sorted([w for w in rows[c] if (sm >> w) & 1])
        outside = sorted([w for w in rows[c] if not ((sm >> w) & 1)])
        rows_info.append({
            "center": c,
            "inside": inside,
            "outside": outside,
            "n_inside": len(inside),
            "n_outside": len(outside),
        })
    # L5/L6 outside-pair multiplicity
    pair_to_centers: dict[tuple[int, int], list[int]] = defaultdict(list)
    for r in rows_info:
        outs = r["outside"]
        if len(outs) >= 2:
            for a, b in combinations(outs, 2):
                pair_to_centers[(a, b)].append(r["center"])
    l5_violations = []
    for pair, centers in pair_to_centers.items():
        if len(centers) > 2:
            l5_violations.append({"pair": list(pair), "centers": centers, "count": len(centers)})
    return {
        "size": len(subset),
        "S": list(subset),
        "rows": rows_info,
        "max_inside_count": max(r["n_inside"] for r in rows_info),
        "outside_pair_centers": {f"{a},{b}": centers for (a, b), centers in pair_to_centers.items()},
        "l5_outside_pair_violations": l5_violations,
    }


# --------------------------------------------------------------------------
# Pattern generation: n=9 (184), n=8 (15), n=10 (sample)
# --------------------------------------------------------------------------

def generate_n9_184() -> list[list[list[int]]]:
    """Reproduce the 184 n=9 cross-check assignments (no vertex-circle)."""
    from erdos97.n9_vertex_circle_exhaustive import (
        OPTIONS, MASK_BITS, ROW_PAIR_INDICES, valid_options_for_center, N,
    )
    PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
    patterns: list[list[list[int]]] = []

    def search(assign: dict[int, int], column_counts: list[int],
               witness_pair_counts: list[int]) -> None:
        if len(assign) == N:
            rows = [list(MASK_BITS[assign[c]]) for c in range(N)]
            patterns.append(rows)
            return
        best_center = None
        best_options = None
        for center in range(N):
            if center in assign:
                continue
            opts = valid_options_for_center(center, assign, column_counts,
                                            witness_pair_counts)
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return
        center = best_center
        for m in best_options:
            assign[center] = m
            for target in MASK_BITS[m]:
                column_counts[target] += 1
            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] += 1
            search(assign, column_counts, witness_pair_counts)
            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] -= 1
            for target in MASK_BITS[m]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in OPTIONS[0]:
        assign = {0: row0}
        column_counts = [0] * N
        witness_pair_counts = [0] * len(PAIRS)
        for target in MASK_BITS[row0]:
            column_counts[target] += 1
        for pidx in ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pidx] += 1
        search(assign, column_counts, witness_pair_counts)
    return patterns


def load_n8_15() -> list[list[list[int]]]:
    path = os.path.join(REPO, "data/incidence/n8_reconstructed_15_survivors.json")
    with open(path) as f:
        data = json.load(f)
    out = []
    for s in data:
        rows = [[j for j, v in enumerate(r) if v] for r in s["rows"]]
        out.append(rows)
    return out


def generate_n10_sample(max_patterns: int = 500) -> list[list[list[int]]]:
    """Generate n=10 4-regular witness patterns with pair/crossing/count
    filters via the n=9 exhaustive infrastructure adapted for n=10.
    Stop once max_patterns reached, sampling broadly.
    """
    # Build local infra for n=10
    from erdos97.incidence_filters import chords_cross_in_order

    N = 10
    ROW_SIZE = 4
    PAIR_CAP = 2
    MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)

    def mask(values):
        out = 0
        for v in values:
            out |= 1 << v
        return out

    def bits_of(m):
        return [i for i in range(N) if (m >> i) & 1]

    OPTIONS = []
    for center in range(N):
        OPTIONS.append([
            mask(combo)
            for combo in combinations([t for t in range(N) if t != center], ROW_SIZE)
        ])

    MASK_BITS = {m: bits_of(m) for opts in OPTIONS for m in opts}

    PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
    PAIR_INDEX = {p: idx for idx, p in enumerate(PAIRS)}

    def pair(a, b):
        return (a, b) if a < b else (b, a)

    ROW_PAIR_INDICES = {
        m: [PAIR_INDEX[pair(a, b)] for a, b in combinations(MASK_BITS[m], 2)]
        for opts in OPTIONS for m in opts
    }

    natural_order = list(range(N))

    def chords_cross(c1, c2):
        a, b = c1
        c, d = c2
        if len({a, b, c, d}) < 4:
            return False
        # use natural cyclic order
        return chords_cross_in_order(c1, c2, natural_order)

    # Compatibility table: two rows i, j compatible if intersection has size <= 2 and
    # if intersection is exactly 2 then chord {i,j} crosses chord between the two intersection
    # vertices.
    COMPATIBLE = {}
    for i in range(N):
        for j in range(i + 1, N):
            source = (i, j)
            table = {}
            for mi in OPTIONS[i]:
                allowed = set()
                row_i = set(MASK_BITS[mi])
                for mj in OPTIONS[j]:
                    common = row_i & set(MASK_BITS[mj])
                    ok = True
                    if len(common) > PAIR_CAP:
                        ok = False
                    elif len(common) == PAIR_CAP:
                        target = tuple(sorted(common))
                        ok = chords_cross(source, target)
                    if ok:
                        allowed.add(mj)
                table[mi] = allowed
            COMPATIBLE[(i, j)] = table

    def rows_compatible(i, mi, j, mj):
        if i < j:
            return mj in COMPATIBLE[(i, j)][mi]
        return mi in COMPATIBLE[(j, i)][mj]

    def valid_options_for_center(center, assign, column_counts, witness_pair_counts):
        out = []
        for m in OPTIONS[center]:
            ok = True
            for other, om in assign.items():
                if not rows_compatible(center, m, other, om):
                    ok = False
                    break
            if not ok:
                continue
            if any(column_counts[t] >= MAX_INDEGREE for t in MASK_BITS[m]):
                continue
            if any(witness_pair_counts[p] >= PAIR_CAP for p in ROW_PAIR_INDICES[m]):
                continue
            out.append(m)
        return out

    patterns: list[list[list[int]]] = []
    aborted = [False]

    def search(assign, column_counts, witness_pair_counts):
        if aborted[0]:
            return
        if len(assign) == N:
            rows = [list(MASK_BITS[assign[c]]) for c in range(N)]
            patterns.append(rows)
            if len(patterns) >= max_patterns:
                aborted[0] = True
            return
        best_center = None
        best_options = None
        for center in range(N):
            if center in assign:
                continue
            opts = valid_options_for_center(center, assign, column_counts,
                                            witness_pair_counts)
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return
        center = best_center
        for m in best_options:
            if aborted[0]:
                break
            assign[center] = m
            for target in MASK_BITS[m]:
                column_counts[target] += 1
            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] += 1
            search(assign, column_counts, witness_pair_counts)
            for pidx in ROW_PAIR_INDICES[m]:
                witness_pair_counts[pidx] -= 1
            for target in MASK_BITS[m]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in OPTIONS[0]:
        if aborted[0]:
            break
        assign = {0: row0}
        column_counts = [0] * N
        witness_pair_counts = [0] * len(PAIRS)
        for target in MASK_BITS[row0]:
            column_counts[target] += 1
        for pidx in ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pidx] += 1
        search(assign, column_counts, witness_pair_counts)

    return patterns


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def analyze_set(label: str, n: int, patterns: list[list[list[int]]],
                max_full: int | None = None) -> dict[str, Any]:
    """Return per-(pattern, S) census + aggregated stats for this n."""
    examples = []
    pattern_count = len(patterns)
    stats: dict[str, Any] = {
        "n": n,
        "label": label,
        "num_patterns": pattern_count,
        "patterns_with_stuck": 0,
        "patterns_without_stuck": 0,
        "stuck_size_histogram": Counter(),
        "min_stuck_size": None,
        "min_stuck_pattern_count": 0,
        "total_stuck_sets_summed": 0,
        "stuck_sets_with_l5_violation": 0,
        "max_inside_count_histogram": Counter(),
        "outside_pair_max_codegree_hist": Counter(),
    }
    seen_min_size = None

    for pi, rows in enumerate(patterns):
        s_sets = find_all_stuck_sets(rows, threshold=3, min_size=4, max_size=n - 1, cap=10_000)
        # Note: |S| = n is full set (always stuck if no peelable v in V) — included separately
        s_sets_full = find_all_stuck_sets(rows, threshold=3, min_size=n, max_size=n, cap=2)
        all_stuck = s_sets + s_sets_full
        if all_stuck:
            stats["patterns_with_stuck"] += 1
            min_size = min(len(s) for s in all_stuck)
            stats["stuck_size_histogram"][min_size] += 1
            if seen_min_size is None or min_size < seen_min_size:
                seen_min_size = min_size
        else:
            stats["patterns_without_stuck"] += 1

        for s in all_stuck:
            stats["total_stuck_sets_summed"] += 1
            stats["stuck_size_histogram"][len(s)] += 0  # ensure existence
            d = stuck_set_descriptor(rows, s)
            stats["max_inside_count_histogram"][d["max_inside_count"]] += 1
            cgs = [len(c) for c in d["outside_pair_centers"].values()] or [0]
            stats["outside_pair_max_codegree_hist"][max(cgs)] += 1
            if d["l5_outside_pair_violations"]:
                stats["stuck_sets_with_l5_violation"] += 1
            if max_full is None or len(examples) < max_full:
                examples.append({
                    "pattern_index": pi,
                    "rows": rows,
                    "stuck_set": d,
                })

    stats["min_stuck_size"] = seen_min_size
    if seen_min_size is not None:
        stats["min_stuck_pattern_count"] = sum(
            1 for ex in examples if ex["stuck_set"]["size"] == seen_min_size
        )
    # Stuck-size histogram counts patterns with at least one S of that minimum size as well as
    # the descriptor count; expose both views.
    return {
        "stats": {
            **stats,
            "stuck_size_histogram": dict(stats["stuck_size_histogram"]),
            "max_inside_count_histogram": dict(stats["max_inside_count_histogram"]),
            "outside_pair_max_codegree_hist": dict(stats["outside_pair_max_codegree_hist"]),
        },
        "examples": examples,
    }


def main():
    t0 = time.time()
    out: dict[str, Any] = {"semantics": (
        "Stuck-set census across n=8 (15 incidence-completeness survivors), "
        "n=9 (184 pre-vertex-circle assignments) and n=10 (sample of patterns "
        "passing pair/crossing/count filters). Threshold=3 (Key Peeling)."
    )}

    print("[n=8] loading 15 reconstructed survivors...")
    n8_pats = load_n8_15()
    print(f"  got {len(n8_pats)} patterns; analyzing stuck sets...")
    out["n8"] = analyze_set("n8_reconstructed_15", 8, n8_pats, max_full=200)
    print(f"  n=8 done in {time.time()-t0:.1f}s; "
          f"min stuck = {out['n8']['stats']['min_stuck_size']}, "
          f"summed stuck sets = {out['n8']['stats']['total_stuck_sets_summed']}")

    print("[n=9] regenerating 184 pre-vertex-circle assignments...")
    t1 = time.time()
    n9_pats = generate_n9_184()
    print(f"  got {len(n9_pats)} patterns ({time.time()-t1:.1f}s); analyzing...")
    out["n9"] = analyze_set("n9_pre_vertex_circle_184", 9, n9_pats, max_full=400)
    print(f"  n=9 done in {time.time()-t0:.1f}s; "
          f"min stuck = {out['n9']['stats']['min_stuck_size']}, "
          f"summed stuck sets = {out['n9']['stats']['total_stuck_sets_summed']}")

    print("[n=10] sampling patterns passing filters (target up to 200)...")
    t2 = time.time()
    n10_pats = generate_n10_sample(max_patterns=200)
    print(f"  got {len(n10_pats)} patterns ({time.time()-t2:.1f}s); analyzing...")
    out["n10"] = analyze_set("n10_sample_pre_vertex_circle", 10, n10_pats, max_full=300)
    print(f"  n=10 done in {time.time()-t0:.1f}s; "
          f"min stuck = {out['n10']['stats']['min_stuck_size']}, "
          f"summed stuck sets = {out['n10']['stats']['total_stuck_sets_summed']}")

    # --------------------------- aggregate findings ---------------------------
    # smallest stuck size across all n
    overall_min = None
    for k in ("n8", "n9", "n10"):
        ms = out[k]["stats"].get("min_stuck_size")
        if ms is None:
            continue
        if overall_min is None or ms < overall_min:
            overall_min = ms
    out["overall_min_stuck_size"] = overall_min

    # L5/L6/L4-cyclic ruling-out audit
    out["l5_l6_audit"] = {
        "comment": (
            "L5/L6 says any unordered pair {a,b} of vertices appears in at most "
            "two selected rows globally. Inside a stuck set S, the outside-pair "
            "multiplicity (number of stuck centers whose 'outside witnesses' "
            "include {a,b}) is bounded by the global L5 cap = 2. We report "
            "patterns whose outside-pair multiplicity already meets the cap "
            "without any global slack."
        ),
        "n8_outside_pair_max_codegree_hist": out["n8"]["stats"]["outside_pair_max_codegree_hist"],
        "n9_outside_pair_max_codegree_hist": out["n9"]["stats"]["outside_pair_max_codegree_hist"],
        "n10_outside_pair_max_codegree_hist": out["n10"]["stats"]["outside_pair_max_codegree_hist"],
        "n8_l5_violating_stuck_sets": out["n8"]["stats"]["stuck_sets_with_l5_violation"],
        "n9_l5_violating_stuck_sets": out["n9"]["stats"]["stuck_sets_with_l5_violation"],
        "n10_l5_violating_stuck_sets": out["n10"]["stats"]["stuck_sets_with_l5_violation"],
    }

    out["wall_seconds"] = round(time.time() - t0, 2)

    with open("/tmp/stuck_set_census.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
    print(f"\nWrote /tmp/stuck_set_census.json in {out['wall_seconds']}s")


if __name__ == "__main__":
    main()
