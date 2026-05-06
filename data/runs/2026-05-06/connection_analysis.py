"""Connect the K_4-bicycle stuck cores to the strict-cycle vertex-circle obstruction.

For each K_4-bicycle stuck core S in idx=81 / idx=151:
- look at the 4 selected rows (one per v in S)
- check which UF classes their selected chords belong to.

Hypothesis: the K_4-bicycle stuck core gives rise to the 3-cycle in UF classes.
"""

from __future__ import annotations

import os
import sys
from collections import defaultdict
from itertools import combinations

REPO = "/home/user/erdos97"
sys.path.insert(0, os.path.join(REPO, "src"))

from erdos97.n9_vertex_circle_exhaustive import (
    N, PAIRS, PAIR_INDEX, MASK_BITS, SELECTED_PAIR_INDICES, STRICT_EDGES,
    UnionFind, OPTIONS, ROW_PAIR_INDICES, mask, vertex_circle_status,
)

PAT_81 = [[1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6],
          [1, 2, 5, 7], [2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6]]
PAT_151 = [[2, 3, 6, 8], [0, 3, 4, 7], [1, 4, 5, 8], [0, 2, 5, 6],
           [1, 3, 6, 7], [2, 4, 7, 8], [0, 3, 5, 8], [0, 1, 4, 6], [1, 2, 5, 7]]


def rows_to_mask_assignment(rows):
    return {c: mask(rows[c]) for c in range(N)}


def class_per_pair(rows):
    assign = rows_to_mask_assignment(rows)
    uf = UnionFind(len(PAIRS))
    for center, m in assign.items():
        sp = SELECTED_PAIR_INDICES[(center, m)]
        for pidx in sp[1:]:
            uf.union(sp[0], pidx)
    return [uf.find(pidx) for pidx in range(len(PAIRS))]


def diff_class(rows, n=9):
    """For circulants: classify each unordered pair by |i-j| mod n."""
    out = {}
    for a, b in PAIRS:
        d = (b - a) % n
        d = min(d, n - d)
        out[(a, b)] = d
    return out


def main():
    print("=" * 70)
    print("Mapping K_4-bicycle stuck cores to UF chord-classes")
    print("=" * 70)

    for name, rows in [("idx=81 offsets {+1,+3,-2,-3}", PAT_81),
                       ("idx=151 offsets {+2,+3,-1,-3}", PAT_151)]:
        print(f"\n--- {name} ---")
        cls = class_per_pair(rows)
        # Count UF classes
        cls_set = set(cls)
        print(f"# UF classes: {len(cls_set)}")
        # Difference signatures of pairs in each UF class
        diffs = diff_class(rows)
        cls_to_diffs = defaultdict(list)
        for pidx, p in enumerate(PAIRS):
            cls_to_diffs[cls[pidx]].append(diffs[p])
        # Identify the big classes
        big = sorted([(len(set(ds)), root) for root, ds in cls_to_diffs.items()], reverse=True)
        big_classes = sorted(cls_to_diffs.keys(), key=lambda r: -len(cls_to_diffs[r]))[:3]
        print(f"3 large UF classes (each size 9):")
        for root in big_classes:
            from collections import Counter
            ds = cls_to_diffs[root]
            print(f"  root={root}: size={len(ds)}, diff-multiset={dict(Counter(ds))}")

    print()
    print("=" * 70)
    print("K_4-bicycle stuck cores: which 6 chord-pairs are in the core's induced subgraph?")
    print("=" * 70)
    for name, rows in [("idx=81", PAT_81), ("idx=151", PAT_151)]:
        print(f"\n--- {name} ---")
        cls = class_per_pair(rows)
        diffs = diff_class(rows)
        # Find K_4-bicycle stuck cores
        masks = [mask(r) for r in rows]
        cores = []
        for sub in combinations(range(N), 4):
            sm = sum(1 << v for v in sub)
            if all(bin(masks[c] & sm).count("1") == 2 for c in sub):
                cores.append(sub)
        print(f"# cores: {len(cores)}")
        # Show 3 examples and their inner chord classes
        for S in cores[:3]:
            print(f"  S={S}:")
            inner_pairs = [(min(a, b), max(a, b)) for a, b in combinations(S, 2)]
            for p in inner_pairs:
                pidx = PAIR_INDEX[p]
                print(f"    pair {p} (diff={diffs[p]}) -> UF root {cls[pidx]}")

    print()
    print("=" * 70)
    print("UF roots vs cyclic offset")
    print("=" * 70)
    # Map each unordered pair (a, b) to its forward offset (b-a) mod 9 and its class root.
    # Hypothesis: classes correspond to multiplicative cosets of <3> in Z/9 acting on offsets.
    for name, rows in [("idx=81", PAT_81), ("idx=151", PAT_151)]:
        print(f"\n--- {name} ---")
        cls = class_per_pair(rows)
        offsets = {}
        for pidx, p in enumerate(PAIRS):
            d = (p[1] - p[0]) % N
            d_signed = min(d, N - d)
            offsets.setdefault(cls[pidx], set()).add(d_signed)
        for root in sorted(offsets):
            print(f"  UF root {root}: offsets {sorted(offsets[root])}")


if __name__ == "__main__":
    main()
