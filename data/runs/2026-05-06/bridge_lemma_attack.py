"""Bridge Lemma A' attack: stuck-set analysis and non-ear pattern characterization.

Goals:
 1. Reconstruct the n=9 patterns and isolate the 2 non-ear-orderable ones
    (idx 81, 151), which are circulant Cayley graphs on Z/9.
 2. Characterize the stuck-set structure of these patterns and of the 4
    non-ear n=8 patterns (ids 0,1,2,3).
 3. Hunt for new geometric obstructions targeting non-ear patterns:
    perp-bisector / radical axis / Ptolemy / convex-position constraints.

This script is purely combinatorial. Geometric statements are proved on
paper in the accompanying memo; this script only generates evidence.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def rows_to_masks(rows):
    return [sum(1 << v for v in row) for row in rows]


def is_stuck(rows, S, threshold=3):
    """Subset S is 'stuck' iff no v in S has >= threshold internal witnesses."""
    masks = rows_to_masks(rows)
    sm = 0
    for v in S:
        sm |= 1 << v
    for c in S:
        inside = bin(masks[c] & sm).count("1")
        if inside >= threshold:
            return False
    return True


def find_all_stuck_sets(rows, threshold=3, min_size=4):
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for size in range(min_size, n + 1):
        for sub in combinations(range(n), size):
            sm = 0
            for v in sub:
                sm |= 1 << v
            ok = True
            for c in sub:
                if bin(masks[c] & sm).count("1") >= threshold:
                    ok = False
                    break
            if ok:
                out.append(sub)
    return out


def ear_orderable(rows, threshold=3):
    """True iff some ordering (v_1,...,v_n) exists with |S_{v_k} cap {v_1..v_{k-1}}| >= threshold for k >= threshold+1."""
    n = len(rows)
    masks = rows_to_masks(rows)
    # Reverse: peelable order. Build by greedy reverse: at each step, find vertex
    # in remaining set with >= threshold internal selected witnesses.
    # We need to check existence by exhaustive backtracking over reverse-peel orders.

    def can_peel(sm):
        if bin(sm).count("1") <= threshold:
            return True
        for c in range(n):
            if not ((sm >> c) & 1):
                continue
            if bin(masks[c] & sm).count("1") >= threshold:
                # remove c
                if can_peel(sm & ~(1 << c)):
                    return True
        return False

    full = (1 << n) - 1
    return can_peel(full)


# --------------------------------------------------------------------------
# Pattern reconstruction: n=8 (15 survivors), n=9 (184 cross-check)
# --------------------------------------------------------------------------

def load_n8_15():
    path = os.path.join(REPO, "data/incidence/n8_reconstructed_15_survivors.json")
    with open(path) as f:
        data = json.load(f)
    out = []
    for s in data:
        rows = [[j for j, v in enumerate(r) if v] for r in s["rows"]]
        out.append((s["id"], rows))
    return out


def generate_n9_184():
    """Reproduce n=9 184 cross-check assignments (filters 1-4, no vertex-circle)."""
    from erdos97.n9_vertex_circle_exhaustive import (
        OPTIONS, MASK_BITS, ROW_PAIR_INDICES, valid_options_for_center, N,
    )
    PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
    patterns = []

    def search(assign, column_counts, witness_pair_counts):
        if len(assign) == N:
            rows = [list(MASK_BITS[assign[c]]) for c in range(N)]
            patterns.append(rows)
            return
        best_center = None
        best_options = None
        for center in range(N):
            if center in assign:
                continue
            opts = valid_options_for_center(center, assign, column_counts, witness_pair_counts)
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
            for t in MASK_BITS[m]:
                column_counts[t] += 1
            for p in ROW_PAIR_INDICES[m]:
                witness_pair_counts[p] += 1
            search(assign, column_counts, witness_pair_counts)
            for p in ROW_PAIR_INDICES[m]:
                witness_pair_counts[p] -= 1
            for t in MASK_BITS[m]:
                column_counts[t] -= 1
            del assign[center]

    for row0 in OPTIONS[0]:
        assign = {0: row0}
        column_counts = [0] * N
        witness_pair_counts = [0] * len(PAIRS)
        for t in MASK_BITS[row0]:
            column_counts[t] += 1
        for p in ROW_PAIR_INDICES[row0]:
            witness_pair_counts[p] += 1
        search(assign, column_counts, witness_pair_counts)
    return patterns


# --------------------------------------------------------------------------
# Circulant analysis
# --------------------------------------------------------------------------

def is_circulant(rows):
    """Check if pattern is Cayley/circulant on Z/n with a fixed offset multiset."""
    n = len(rows)
    offsets = sorted([(w - 0) % n for w in rows[0]])
    for c in range(n):
        these = sorted([(w - c) % n for w in rows[c]])
        if these != offsets:
            return False, None
    return True, offsets


def offset_signed(offsets, n):
    return [o if o <= n // 2 else o - n for o in offsets]


# --------------------------------------------------------------------------
# Cross-boundary double counting on stuck sets
# --------------------------------------------------------------------------

def cross_boundary_analysis(rows, S):
    """For stuck S: count out-edges (v -> w with w not in S, v in S).

    Each v in S has |E_v cap (V\\S)| = 4 - |E_v cap S|. Stuck means each v has
    >= 2 outside witnesses (since internal_count <= 2).

    Returns (out_edge_count, outside_pair_centers, l5_violations, l5_saturated_pairs).
    """
    n = len(rows)
    sm = 0
    for v in S:
        sm |= 1 << v
    outside = [v for v in range(n) if not ((sm >> v) & 1)]

    out_edge = 0
    outside_pair_centers = defaultdict(list)
    for c in S:
        outs = [w for w in rows[c] if not ((sm >> w) & 1)]
        out_edge += len(outs)
        if len(outs) >= 2:
            for a, b in combinations(sorted(outs), 2):
                outside_pair_centers[(a, b)].append(c)

    l5_viol = [(p, cs) for p, cs in outside_pair_centers.items() if len(cs) > 2]
    l5_sat = [(p, cs) for p, cs in outside_pair_centers.items() if len(cs) == 2]
    return {
        "n": n,
        "S": list(S),
        "size_S": len(S),
        "outside": outside,
        "size_outside": len(outside),
        "out_edge_count": out_edge,
        "min_out_per_v": min(4 - bin(rows_to_masks(rows)[c] & sm).count("1") for c in S),
        "outside_pair_centers": {f"{a},{b}": cs for (a, b), cs in outside_pair_centers.items()},
        "l5_violations": [(list(p), cs) for p, cs in l5_viol],
        "l5_saturated_pair_count": len(l5_sat),
        "double_count_LHS": out_edge,  # sum over v in S of out_v
        "double_count_RHS_unordered_pair_bound": 2 * len(list(combinations(outside, 2))),  # each unordered pair seen by <=2 centers
    }


def cyclic_order_internal_check(rows, S, order=None):
    """Check whether internal witnesses respect convex order: when v in S has 2 internal witnesses,
    those 2 witnesses lie on a chord that v sees as a diagonal in the cyclic order."""
    n = len(rows)
    if order is None:
        order = list(range(n))
    pos = {v: i for i, v in enumerate(order)}
    sm = 0
    for v in S:
        sm |= 1 << v
    constraints = []
    for c in S:
        inside = sorted([w for w in rows[c] if (sm >> w) & 1], key=lambda x: pos[x])
        outside = sorted([w for w in rows[c] if not ((sm >> w) & 1)], key=lambda x: pos[x])
        if len(inside) == 2:
            constraints.append({"center": c, "inside_pair": inside, "outside_pair": outside})
    return constraints


# --------------------------------------------------------------------------
# Main analysis
# --------------------------------------------------------------------------

def analyze_pattern(name, rows, threshold=3):
    n = len(rows)
    masks = rows_to_masks(rows)
    is_circ, offs = is_circulant(rows)
    stuck = find_all_stuck_sets(rows, threshold=threshold, min_size=4)
    ear = ear_orderable(rows, threshold=threshold)

    sample_S = stuck[0] if stuck else None
    cb = cross_boundary_analysis(rows, sample_S) if sample_S else None
    return {
        "name": name,
        "n": n,
        "rows": rows,
        "is_circulant": is_circ,
        "offsets_signed": offset_signed(offs, n) if is_circ else None,
        "ear_orderable": ear,
        "n_stuck_sets": len(stuck),
        "minimal_stuck_size": min(len(s) for s in stuck) if stuck else None,
        "minimal_stuck_count": sum(1 for s in stuck if len(s) == min(len(x) for x in stuck)) if stuck else 0,
        "stuck_size_dist": Counter(len(s) for s in stuck),
        "stuck_examples": [list(s) for s in stuck[:5]],
        "cross_boundary_first": cb,
    }


def main():
    out = {"n8": {}, "n9": {}, "summary": {}}

    print("=" * 70)
    print("n=8 analysis")
    print("=" * 70)
    n8 = load_n8_15()
    n8_results = []
    for pid, rows in n8:
        r = analyze_pattern(f"n8_id{pid}", rows)
        n8_results.append(r)
        is_ear = r["ear_orderable"]
        size = r["minimal_stuck_size"]
        cnt = r["minimal_stuck_count"]
        circ = r["is_circulant"]
        offs = r["offsets_signed"]
        print(f"  id={pid}: ear={is_ear}, min_stuck_size={size}, count={cnt}, circulant={circ}, offsets={offs}")

    out["n8"]["per_pattern"] = [
        {k: (dict(v) if isinstance(v, Counter) else v) for k, v in r.items()}
        for r in n8_results
    ]

    print()
    print("=" * 70)
    print("n=9 analysis (regenerating 184 cross-check patterns)")
    print("=" * 70)
    try:
        n9 = generate_n9_184()
        print(f"Generated {len(n9)} patterns")
    except Exception as e:
        print(f"Failed to regenerate: {e}")
        n9 = []

    n9_results = []
    non_ear_n9 = []
    for idx, rows in enumerate(n9):
        r = analyze_pattern(f"n9_idx{idx}", rows, threshold=3)
        n9_results.append(r)
        if not r["ear_orderable"]:
            non_ear_n9.append((idx, r))

    print(f"Total n=9 patterns: {len(n9_results)}; non-ear-orderable: {len(non_ear_n9)}")

    print()
    print("Non-ear-orderable patterns at n=9:")
    for idx, r in non_ear_n9:
        print(f"  idx={idx}, circulant={r['is_circulant']}, offsets={r['offsets_signed']}")
        print(f"    rows: {r['rows']}")
        print(f"    n_stuck_sets={r['n_stuck_sets']}, sizes={dict(r['stuck_size_dist'])}")
        print(f"    minimal_stuck examples: {r['stuck_examples']}")

    out["n9"]["non_ear"] = [{
        "idx": idx,
        "rows": r["rows"],
        "is_circulant": r["is_circulant"],
        "offsets_signed": r["offsets_signed"],
        "n_stuck_sets": r["n_stuck_sets"],
        "stuck_size_dist": dict(r["stuck_size_dist"]),
        "stuck_examples": r["stuck_examples"],
    } for idx, r in non_ear_n9]

    # Aggregate stats
    print()
    print("=" * 70)
    print("Aggregate: relation between ear-orderability and minimal stuck-set size")
    print("=" * 70)
    for tag, results in [("n=8", n8_results), ("n=9", n9_results)]:
        ear_min_stuck = Counter()
        for r in results:
            ear_min_stuck[(r["ear_orderable"], r["minimal_stuck_size"])] += 1
        print(f"{tag}: (ear_orderable, minimal_stuck_size) -> count")
        for k, v in sorted(ear_min_stuck.items()):
            print(f"    {k}: {v}")
        out["summary"][tag] = {f"ear={k[0]},min_stuck={k[1]}": v for k, v in ear_min_stuck.items()}

    # Save
    out_path = os.path.join(REPO, "data/runs/2026-05-06/bridge_lemma_attack_data.json")
    with open(out_path, "w") as f:
        # Strip overly large fields
        cleaned = {
            "n8": {"per_pattern": [{k: v for k, v in r.items() if k != "stuck_size_dist"} for r in out["n8"]["per_pattern"]]},
            "n9": out["n9"],
            "summary": out["summary"],
        }
        json.dump(cleaned, f, indent=2, default=lambda o: dict(o) if isinstance(o, Counter) else str(o))
    print(f"\nSaved data to {out_path}")


if __name__ == "__main__":
    main()
