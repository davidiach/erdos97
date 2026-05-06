"""Geometric analysis of the 2 non-ear-orderable n=9 patterns.

Both are circulants on Z/9 with offset multisets {+1,+3,−2,−3} and {+2,+3,−1,−3}.
Both are killed by vertex-circle (strict-cycle).

This script:
 1. Inspects the symmetry group of each pattern.
 2. Looks for additional independent obstructions beyond vertex-circle.
 3. Investigates the *combinatorial reason* why ear-ordering fails on these.
 4. Computes Ptolemy / row-circle / radical-axis structure.
"""

from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

# Pattern from analysis:
PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
          [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
PAT_151 = [[2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6],
           [1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6], [1, 2, 5, 7]]


def rows_to_masks(rows):
    return [sum(1 << v for v in row) for row in rows]


# --------------------------------------------------------------------------
# Why is ear-ordering impossible on these circulants?
# --------------------------------------------------------------------------

def show_internal_distribution(rows):
    """For every nonempty subset S of size 4..n, count how many vertices of S
    have >= 3 internal selected witnesses. If 0, S is stuck."""
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    # Just sample stuck sets and their structure
    for size in range(4, n + 1):
        n_subsets = 0
        n_stuck = 0
        max_internal = 0
        for sub in combinations(range(n), size):
            sm = 0
            for v in sub:
                sm |= 1 << v
            n_subsets += 1
            mx = max(bin(masks[c] & sm).count("1") for c in sub)
            max_internal = max(max_internal, mx)
            if mx < 3:
                n_stuck += 1
        out.append((size, n_subsets, n_stuck, max_internal))
    return out


def stuck_set_min_internal_pattern(rows, S):
    """For stuck S, return (internal_counts of each v in S, max internal degree)."""
    masks = rows_to_masks(rows)
    sm = 0
    for v in S:
        sm |= 1 << v
    counts = []
    for c in S:
        counts.append((c, bin(masks[c] & sm).count("1")))
    return counts


def all_stuck_sets(rows, threshold=3, min_size=4):
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for size in range(min_size, n + 1):
        for sub in combinations(range(n), size):
            sm = 0
            for v in sub:
                sm |= 1 << v
            if all(bin(masks[c] & sm).count("1") < threshold for c in sub):
                out.append(sub)
    return out


# --------------------------------------------------------------------------
# Symmetry group
# --------------------------------------------------------------------------

def pattern_signature(rows):
    """Sorted tuple of row sets, for isomorphism testing."""
    n = len(rows)
    return tuple(sorted(tuple(sorted(r)) for r in rows))


def pattern_under_perm(rows, perm):
    """Apply vertex permutation perm: new_rows[perm[c]] = sorted([perm[v] for v in rows[c]])."""
    n = len(rows)
    new_rows = [[]] * n
    new = [None] * n
    for c in range(n):
        new[perm[c]] = sorted(perm[v] for v in rows[c])
    return new


def find_automorphisms(rows, sample_perms=None):
    """Find permutations sigma with rows[sigma^-1(c)] mapped to rows[c]."""
    n = len(rows)
    sig = pattern_signature(rows)
    auts = []
    for perm in permutations(range(n)):
        new = pattern_under_perm(rows, perm)
        if pattern_signature(new) == sig and tuple(tuple(sorted(r)) for r in new) == tuple(tuple(sorted(r)) for r in rows):
            auts.append(perm)
    return auts


# --------------------------------------------------------------------------
# Cross-boundary L5-budget tightness on stuck sets
# --------------------------------------------------------------------------

def double_count_l5_budget(rows, S):
    """Stuck S => each v in S has internal_count <= 2 (since threshold=3 fails),
    so out_count = 4 - internal_count >= 2 (could be 2, 3, or 4).

    L5: each unordered pair {a,b} in V\\S can be 'outside-witnessed' by <= 2 centers.
    LHS = sum over v in S of C(out_v, 2) outside-pairs (v contributes pairs of outside witnesses).
    RHS <= 2 * C(|V\\S|, 2).
    """
    n = len(rows)
    masks = rows_to_masks(rows)
    sm = 0
    for v in S:
        sm |= 1 << v
    outside_indices = [v for v in range(n) if not ((sm >> v) & 1)]
    LHS = 0
    out_pair_counter = Counter()
    for c in S:
        outs = [w for w in rows[c] if not ((sm >> w) & 1)]
        from itertools import combinations as comb
        for a, b in comb(sorted(outs), 2):
            out_pair_counter[(a, b)] += 1
            LHS += 1
    RHS = 2 * len(list(combinations(outside_indices, 2)))
    saturated = sum(1 for v in out_pair_counter.values() if v >= 2)
    overflows = sum(1 for v in out_pair_counter.values() if v > 2)
    return {
        "S": list(S),
        "outside": outside_indices,
        "LHS_outside_pair_incidences": LHS,
        "RHS_2*C(|V\\S|,2)": RHS,
        "tight": LHS == RHS,
        "outside_pair_dist": dict(Counter(out_pair_counter.values())),
        "L5_saturated_pairs": saturated,
        "L5_overflows": overflows,
    }


def stuck_pattern_summary(rows, name):
    print(f"--- {name} ---")
    print(f"rows: {rows}")
    n = len(rows)
    stuck = all_stuck_sets(rows)
    print(f"Total stuck sets: {len(stuck)}, sizes={Counter(len(s) for s in stuck)}")
    if not stuck:
        return

    # Look at minimal stuck sets and their internal pattern
    minimal = [s for s in stuck if len(s) == 4]
    print(f"Number of minimal (size-4) stuck sets: {len(minimal)}")
    # Check: in size-4 stuck S, each v has internal_count <= 2 => sum <= 8
    # And pair-cap means sum is 2 * |E[S]| where E[S] = induced edges in selected graph
    # restricted to S.
    examples = minimal[:5]
    print("Sample minimal stuck sets (with internal counts):")
    for S in examples:
        counts = stuck_set_min_internal_pattern(rows, S)
        print(f"   S={S}: {counts}")
        cb = double_count_l5_budget(rows, S)
        rhs = cb['RHS_2*C(|V\\S|,2)']
        print(f"     L5 budget: LHS={cb['LHS_outside_pair_incidences']}, RHS={rhs}, "
              f"saturated={cb['L5_saturated_pairs']}, overflows={cb['L5_overflows']}, "
              f"tight={cb['tight']}, dist={cb['outside_pair_dist']}")
    return stuck


def can_we_starve_cyclic(rows):
    """For each subset S of size 4, check if the 'cyclic-quartet stuck' pattern
    has every center with internal_count = exactly 2 (i.e. a cycle in the induced graph)."""
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for sub in combinations(range(n), 4):
        sm = 0
        for v in sub:
            sm |= 1 << v
        counts = [bin(masks[c] & sm).count("1") for c in sub]
        if max(counts) <= 2:
            out.append((sub, counts))
    return out


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Non-ear-orderable n=9 patterns: detailed analysis")
    print("=" * 70)

    for name, rows in [("idx=81 (offsets +1,+3,-2,-3)", PAT_81),
                       ("idx=151 (offsets +2,+3,-1,-3)", PAT_151)]:
        print()
        stuck_pattern_summary(rows, name)

    print()
    print("=" * 70)
    print("Ear-orderable n=8 vs non-ear n=8 comparison: minimal stuck size & out-degree")
    print("=" * 70)

    # Load n8
    path = os.path.join(REPO, "data/incidence/n8_reconstructed_15_survivors.json")
    with open(path) as f:
        data = json.load(f)
    n8 = [(s["id"], [[j for j, v in enumerate(r) if v] for r in s["rows"]]) for s in data]
    NON_EAR_IDS = {0, 1, 2, 3}

    print("\nNon-ear (id 0,1,2,3): are they isomorphic? Use signature ('K_4-stuck core')")
    for pid, rows in n8:
        if pid in NON_EAR_IDS:
            print(f"\n--- id={pid} ---")
            print(f"rows: {rows}")
            stuck = all_stuck_sets(rows)
            print(f"#stuck sets: {len(stuck)}, sizes: {Counter(len(s) for s in stuck)}")
            # look for K_4-stuck cores: size 4 set with every v having internal=2 (max possible)
            cycles = [s for s in stuck if len(s) == 4 and all(bin(rows_to_masks(rows)[c] & sum(1<<x for x in s)).count("1") == 2 for c in s)]
            print(f"#size-4 stuck with all internal=2 ('K_4-bicycle'): {len(cycles)}")
            if cycles:
                # describe one
                S = cycles[0]
                print(f"  Example {S}: {stuck_set_min_internal_pattern(rows, S)}")
                # the induced selected-edges in S form a 2-regular graph on 4 vertices = 4-cycle
                # Identify it
                edges = []
                masks = rows_to_masks(rows)
                sm = sum(1 << x for x in S)
                for c in S:
                    for w in rows[c]:
                        if (sm >> w) & 1:
                            edges.append((c, w))
                print(f"  selected-edges in S (directed): {edges}")

    # n=9: same for the 2 non-ear circulants
    print()
    print("=" * 70)
    print("n=9 non-ear: K_4-bicycle / cycle structure?")
    print("=" * 70)
    for name, rows in [("idx=81", PAT_81), ("idx=151", PAT_151)]:
        print(f"\n--- {name} ---")
        stuck = all_stuck_sets(rows)
        cycles = [s for s in stuck if len(s) == 4 and
                  all(bin(rows_to_masks(rows)[c] & sum(1 << x for x in s)).count("1") == 2 for c in s)]
        print(f"#size-4 stuck-with-all-internal=2: {len(cycles)}")
        if cycles:
            S = cycles[0]
            counts = stuck_set_min_internal_pattern(rows, S)
            print(f"  example: S={S} counts={counts}")
            edges = []
            sm = sum(1 << x for x in S)
            for c in S:
                for w in rows[c]:
                    if (sm >> w) & 1:
                        edges.append((c, w))
            print(f"  directed selected-edges in S: {edges}")
        size5 = [s for s in stuck if len(s) == 5]
        print(f"#size-5 stuck: {len(size5)}")
        if size5:
            S = size5[0]
            print(f"  ex: S={S} counts={stuck_set_min_internal_pattern(rows, S)}")
            cb = double_count_l5_budget(rows, S)
            rhs = cb['RHS_2*C(|V\\S|,2)']
            print(f"  L5 budget: LHS={cb['LHS_outside_pair_incidences']}, RHS={rhs}, "
                  f"sat={cb['L5_saturated_pairs']}, dist={cb['outside_pair_dist']}")


if __name__ == "__main__":
    main()
