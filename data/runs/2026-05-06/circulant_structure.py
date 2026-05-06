"""Detailed structure of the n=9 non-ear circulants.

Findings: both have 9 size-4 stuck sets where every center has exactly 2
internal selected-witnesses (K_4-bicycle stuck cores). We want to:
 - Identify these cores combinatorially (cosets? difference set?)
 - Compute L5 saturation on these cores.
 - Find geometric obstructions specific to these cores.
"""

from __future__ import annotations

import os
import sys
from collections import Counter, defaultdict
from itertools import combinations, permutations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
          [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
PAT_151 = [[2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6],
           [1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6], [1, 2, 5, 7]]


def rows_to_masks(rows):
    return [sum(1 << v for v in row) for row in rows]


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


def k4_bicycle_stuck(rows):
    """size-4 stuck S where every v in S has internal_count == 2."""
    n = len(rows)
    masks = rows_to_masks(rows)
    out = []
    for sub in combinations(range(n), 4):
        sm = 0
        for v in sub:
            sm |= 1 << v
        counts = [bin(masks[c] & sm).count("1") for c in sub]
        if all(c == 2 for c in counts):
            out.append(sub)
    return out


def diff_signature(S, n):
    """Multiset of unsigned differences (mod n) within S, taken minimum of d and n-d."""
    diffs = []
    for a, b in combinations(S, 2):
        d = (b - a) % n
        d = min(d, n - d)
        diffs.append(d)
    return tuple(sorted(diffs))


def signed_diff_set(S, n):
    """For circulant analysis: list signed offsets c->w where (c,w) is a selected edge."""
    return None


def selected_in_S(rows, S):
    """Return all directed edges (c -> w) with c in S, w in S, w in rows[c]."""
    sm = sum(1 << v for v in S)
    edges = []
    for c in S:
        for w in rows[c]:
            if (sm >> w) & 1:
                edges.append((c, w))
    return edges


def selected_in_S_signed_offsets(rows, S, n):
    edges = selected_in_S(rows, S)
    return Counter((w - c) % n for c, w in edges)


def main():
    print("=" * 70)
    print("K_4-bicycle stuck cores for the 2 non-ear circulants")
    print("=" * 70)

    for name, rows in [("idx=81 offsets {+1,+3,-2,-3}", PAT_81),
                       ("idx=151 offsets {+2,+3,-1,-3}", PAT_151)]:
        print(f"\n--- {name} ---")
        n = len(rows)
        cores = k4_bicycle_stuck(rows)
        print(f"Number of K_4-bicycle stuck cores: {len(cores)}")
        # Group by difference signature
        sig_groups = defaultdict(list)
        for S in cores:
            sig = diff_signature(S, n)
            sig_groups[sig].append(S)
        print(f"Difference signatures (sorted multiset of |a-b| mod n):")
        for sig, group in sorted(sig_groups.items()):
            print(f"  diffs {sig}: {len(group)} examples: {group[:5]}")

        # signed offsets used
        for sig, group in sig_groups.items():
            print(f"  Detail of diffs {sig}:")
            for S in group[:3]:
                offs = selected_in_S_signed_offsets(rows, S, n)
                print(f"    S={S} edges-by-offset: {dict(offs)} (total directed = {sum(offs.values())})")

    print()
    print("=" * 70)
    print("Cyclic shift / dihedral structure of cores")
    print("=" * 70)
    for name, rows in [("idx=81", PAT_81)]:
        print(f"\n--- {name} ---")
        cores = k4_bicycle_stuck(rows)
        n = len(rows)
        # Are cores cyclic-shift orbits?
        canonical = []
        for S in cores:
            shifts = []
            for k in range(n):
                shifted = tuple(sorted((v + k) % n for v in S))
                shifts.append(shifted)
            canonical.append(min(shifts))
        canonical_classes = set(canonical)
        print(f"# distinct cyclic-shift classes among {len(cores)} cores: {len(canonical_classes)}")
        for cls in sorted(canonical_classes):
            count = canonical.count(cls)
            print(f"  representative={cls}, orbit size={count}")

    print()
    print("=" * 70)
    print("All stuck-set sizes 4 and 5")
    print("=" * 70)
    for name, rows in [("idx=81", PAT_81), ("idx=151", PAT_151)]:
        print(f"\n--- {name} ---")
        n = len(rows)
        stuck = all_stuck_sets(rows)
        size4 = [s for s in stuck if len(s) == 4]
        size5 = [s for s in stuck if len(s) == 5]
        # Distribute by max-internal-count
        size4_dist = Counter()
        for S in size4:
            masks = rows_to_masks(rows)
            sm = sum(1 << v for v in S)
            counts = sorted([bin(masks[c] & sm).count("1") for c in S])
            size4_dist[tuple(counts)] += 1
        print(f"size=4 stuck: {len(size4)}, internal-count profile distribution:")
        for cnts, freq in sorted(size4_dist.items()):
            print(f"  internal_counts={cnts}: {freq}")

        size5_dist = Counter()
        for S in size5:
            masks = rows_to_masks(rows)
            sm = sum(1 << v for v in S)
            counts = sorted([bin(masks[c] & sm).count("1") for c in S])
            size5_dist[tuple(counts)] += 1
        print(f"size=5 stuck: {len(size5)}, internal-count profile:")
        for cnts, freq in sorted(size5_dist.items()):
            print(f"  internal_counts={cnts}: {freq}")

    # Question: Why does ear-ordering fail?
    # Ear-orderability requires: at every step k>=4, the new vertex has >=3 already-placed witnesses.
    # Equivalently, reverse-peeling: at every step the remaining set has some vertex with >=3 internal witnesses.
    # If the full set V is stuck (every v has internal <= 2), can't even start to peel. But here |V|=9 and full set is NOT stuck (because each v has 4 internal witnesses).
    # So peeling can start. The failure is that peeling MUST eventually hit a stuck set.
    # Let's verify: forward search ear orderings.
    print()
    print("=" * 70)
    print("Why does ear-ordering fail? Test all reverse-peeling sequences")
    print("=" * 70)

    for name, rows in [("idx=81", PAT_81), ("idx=151", PAT_151)]:
        n = len(rows)
        masks = rows_to_masks(rows)
        full = (1 << n) - 1
        # BFS / DFS through (subset_mask, peelable_count)
        # Actually a key question: what is the smallest set the peeling must terminate at?
        # i.e., what is the smallest set reachable by removing peelable vertices that has no peelable vertex?
        smallest_terminal = None
        # search: from full, find all reachable subsets and identify those with no peelable vertex
        # but |reachable| can be 2^9 = 512, manageable
        memo = {}

        def rec(sm):
            if sm in memo:
                return memo[sm]
            if bin(sm).count("1") <= 3:
                memo[sm] = (bin(sm).count("1"), sm)
                return memo[sm]
            best_size = bin(sm).count("1")
            best_sm = sm
            stuck = True
            for c in range(n):
                if not ((sm >> c) & 1):
                    continue
                if bin(masks[c] & sm).count("1") >= 3:
                    stuck = False
                    s2 = sm & ~(1 << c)
                    sz, sub_sm = rec(s2)
                    if sz < best_size:
                        best_size = sz
                        best_sm = sub_sm
            if stuck:
                memo[sm] = (bin(sm).count("1"), sm)
            else:
                memo[sm] = (best_size, best_sm)
            return memo[sm]

        sz, sub_sm = rec(full)
        print(f"--- {name}: smallest terminal subset reachable by reverse-peeling = "
              f"{[i for i in range(n) if (sub_sm >> i) & 1]}, size={sz}")


if __name__ == "__main__":
    main()
