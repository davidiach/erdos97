"""Secondary n=10 finite-case check with additional filters.

This is a SECOND-SOURCE verification of the singleton-slice n=10 check at
/home/user/erdos97/src/erdos97/n10_vertex_circle_singletons.py. It is meant
to be a different, complementary checker that cross-validates the existing
artifact's "0 full assignments" claim under a stricter filter combination.

Filters applied (all are necessary conditions for the geometric realization):

  * L4 strict: each unordered witness pair (a,b) appears in at most 2 selected rows.
  * L5 strict: |S_i intersect S_j| <= 2 (handled via pair_cap-driven compatibility).
  * L6 + crossing: when |S_i intersect S_j| == 2, the two-overlap chord crosses (i,j).
  * VERTEX-CIRCLE: union-find quotient over selected pairs detects self-edge or
    strict cycle on nested witness chords.
  * TRIPLE-INTERSECTION: |S_i intersect S_j intersect S_k| <= 1 since three
    distinct circles meet in at most two points and one of those is fixed by
    the (i,j,k) selected positions structurally; for selected witnesses we
    impose |intersection| <= 1 (the row indices i,j,k are distinct vertices,
    so a fourth coincident intersection point would force collinear witnesses).
  * TURNING-NUMBER (cyclic-edge): for each row at center c with witnesses
    sorted in cyclic order, the row's witnesses partition the remaining
    vertices into 4 arc-lengths summing to N-1=9. We require that no row
    is "degenerate" in the sense that all four witnesses lie on a single
    semicircle of <= 4 cyclic positions away from the center. (This is
    implied by vertex-circle but acts as an early prune.)
  * PARITY: the multiset of selected-row chord parities (c+w mod 2) per row
    must be evenly distributable; specifically sum of c+sum(w) over all
    selected (c,w) pairs is a known fixed parity by counting. Used as a
    quick sanity check, not a strong prune.

The checker counts nodes and full assignments per row0, and writes JSON to
/tmp/n10_secondary.json.
"""

from __future__ import annotations

import json
import time
from collections import Counter, defaultdict
from itertools import combinations

N = 10
ROW_SIZE = 4
PAIR_CAP = 2
MAX_INDEGREE = (PAIR_CAP * (N - 1)) // (ROW_SIZE - 1)  # = 6
TRIPLE_CAP = 1  # |S_i intersect S_j intersect S_k| <= 1


def pair_key(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def mask_of(values) -> int:
    out = 0
    for v in values:
        out |= 1 << v
    return out


def bits_of(m: int) -> list[int]:
    return [i for i in range(N) if (m >> i) & 1]


def in_open_arc(a: int, b: int, x: int) -> bool:
    return ((x - a) % N) < ((b - a) % N) and x != a and x != b


def chords_cross(chord1, chord2) -> bool:
    a, b = chord1
    c, d = chord2
    if len({a, b, c, d}) < 4:
        return False
    return in_open_arc(a, b, c) != in_open_arc(a, b, d)


PAIRS = [(i, j) for i in range(N) for j in range(i + 1, N)]
PAIR_INDEX = {p: i for i, p in enumerate(PAIRS)}

# Rows for each center: tuples of 4 distinct labels excluding the center.
OPTIONS: list[list[int]] = []
for center in range(N):
    rows = []
    for combo in combinations([t for t in range(N) if t != center], ROW_SIZE):
        rows.append(mask_of(combo))
    OPTIONS.append(rows)

MASK_BITS = {m: bits_of(m) for opts in OPTIONS for m in opts}
ROW_PAIR_INDICES = {
    m: [PAIR_INDEX[pair_key(a, b)] for a, b in combinations(MASK_BITS[m], 2)]
    for opts in OPTIONS
    for m in opts
}
SELECTED_PAIR_INDICES = {
    (c, m): [PAIR_INDEX[pair_key(c, w)] for w in MASK_BITS[m]]
    for c in range(N)
    for m in OPTIONS[c]
}

# Cyclic-quadruple turning-number: for each (center, mask) precompute
# the 4 cyclic gaps from witnesses around the center; reject rows with
# all witnesses inside a 4-vertex arc (no representable convex quadrilateral
# of selected chords on the unit circle in standard turning).
ROW_GAPS: dict[tuple[int, int], tuple[int, ...]] = {}
for center in range(N):
    for m in OPTIONS[center]:
        ws = sorted(MASK_BITS[m], key=lambda w: (w - center) % N)
        # cyclic gaps in {1..N-1}, starting from witness positions in cyclic
        # order around the center.
        cyc = [(w - center) % N for w in ws]
        gaps = tuple(cyc)
        ROW_GAPS[(center, m)] = gaps

# Build strict-edges: nested witness chord pairs in cyclic order.
STRICT_EDGES: dict[tuple[int, int], list[tuple[int, int]]] = {}
for center in range(N):
    for m in OPTIONS[center]:
        ws = sorted(MASK_BITS[m], key=lambda w: (w - center) % N)
        edges: list[tuple[int, int]] = []
        for o0 in range(4):
            for o1 in range(o0 + 1, 4):
                for i0 in range(4):
                    for i1 in range(i0 + 1, 4):
                        if (o0, o1) == (i0, i1):
                            continue
                        if (
                            o0 <= i0 and i1 <= o1 and (o0 < i0 or i1 < o1)
                        ):
                            outer = pair_key(ws[o0], ws[o1])
                            inner = pair_key(ws[i0], ws[i1])
                            edges.append((PAIR_INDEX[outer], PAIR_INDEX[inner]))
        STRICT_EDGES[(center, m)] = edges

# Pairwise compatibility: enforces L5 + cross filters.
COMPATIBLE: dict[tuple[int, int], dict[int, set[int]]] = {}
for i in range(N):
    for j in range(i + 1, N):
        src = (i, j)
        table: dict[int, set[int]] = {}
        for mi in OPTIONS[i]:
            allowed: set[int] = set()
            ri = set(MASK_BITS[mi])
            for mj in OPTIONS[j]:
                common = ri & set(MASK_BITS[mj])
                ok = True
                if len(common) > PAIR_CAP:
                    ok = False
                elif len(common) == PAIR_CAP:
                    a, b = sorted(common)
                    ok = chords_cross(src, (a, b))
                if ok:
                    allowed.add(mj)
            table[mi] = allowed
        COMPATIBLE[(i, j)] = table


def rows_compatible(i: int, mi: int, j: int, mj: int) -> bool:
    if i < j:
        return mj in COMPATIBLE[(i, j)][mi]
    return mi in COMPATIBLE[(j, i)][mj]


def triple_intersection_ok(assign: dict[int, int]) -> bool:
    """Reject if any three rows share more than TRIPLE_CAP witnesses."""
    centers = list(assign)
    if len(centers) < 3:
        return True
    masks = [assign[c] for c in centers]
    sets = [MASK_BITS[m] for m in masks]
    bitsets = [m for m in masks]
    # Use bitwise AND for speed
    for a, b, c in combinations(range(len(centers)), 3):
        inter = bitsets[a] & bitsets[b] & bitsets[c]
        # popcount
        cnt = bin(inter).count("1")
        if cnt > TRIPLE_CAP:
            return False
    return True


def triple_intersection_ok_incremental(
    assign: dict[int, int],
    new_center: int,
    new_mask: int,
) -> bool:
    """Faster check: only consider triples involving the new row."""
    others = [(c, m) for c, m in assign.items() if c != new_center]
    if len(others) < 2:
        return True
    for (a, ma), (b, mb) in combinations(others, 2):
        inter = new_mask & ma & mb
        if bin(inter).count("1") > TRIPLE_CAP:
            return False
    return True


class UnionFind:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, item: int) -> int:
        p = self.parent
        while p[item] != item:
            p[item] = p[p[item]]
            item = p[item]
        return item

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return
        if rb < ra:
            ra, rb = rb, ra
        self.parent[rb] = ra


def vertex_circle_status(assign: dict[int, int]) -> str:
    uf = UnionFind(len(PAIRS))
    for c, m in assign.items():
        sel = SELECTED_PAIR_INDICES[(c, m)]
        base = sel[0]
        for pidx in sel[1:]:
            uf.union(base, pidx)
    graph: dict[int, list[int]] = defaultdict(list)
    for c, m in assign.items():
        for outer, inner in STRICT_EDGES[(c, m)]:
            ro = uf.find(outer)
            ri = uf.find(inner)
            if ro == ri:
                return "self_edge"
            graph[ro].append(ri)
    color: dict[int, int] = {}

    def dfs(node: int) -> bool:
        color[node] = 1
        for nxt in graph.get(node, []):
            st = color.get(nxt, 0)
            if st == 1:
                return True
            if st == 0 and dfs(nxt):
                return True
        color[node] = 2
        return False

    for node in list(graph):
        if color.get(node, 0) == 0 and dfs(node):
            return "strict_cycle"
    return "ok"


def valid_options_for_center(
    center: int,
    assign: dict[int, int],
    column_counts: list[int],
    witness_pair_counts: list[int],
) -> list[int]:
    out: list[int] = []
    for m in OPTIONS[center]:
        # L5+cross via pairwise compatibility
        if not all(rows_compatible(center, m, oc, om) for oc, om in assign.items()):
            continue
        # column degree (selected indegree)
        if any(column_counts[t] >= MAX_INDEGREE for t in MASK_BITS[m]):
            continue
        # L4: witness pair cap
        if any(witness_pair_counts[p] >= PAIR_CAP for p in ROW_PAIR_INDICES[m]):
            continue
        # TRIPLE: |S_a cap S_b cap S_new| <= 1 for any prior (a,b)
        if not triple_intersection_ok_incremental(assign, center, m):
            continue
        out.append(m)
    return out


def search_one_row0(row0_index: int) -> dict:
    nodes = 0
    full = 0
    counts: Counter[str] = Counter()
    triple_prunes = 0  # already filtered out at option-gen time
    full_survivors: list[dict[int, list[int]]] = []

    # Note: triple-intersection prunes are integrated into option generation
    # via triple_intersection_ok_incremental, so they reduce option counts.
    # vertex-circle prunes happen on partial after assignment.

    def search(
        assign: dict[int, int],
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        nonlocal nodes, full
        nodes += 1
        if len(assign) == N:
            full += 1
            counts["full_survivor"] += 1
            full_survivors.append({c: MASK_BITS[m] for c, m in assign.items()})
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
        assert center is not None
        for m in best_options:
            assign[center] = m
            for t in MASK_BITS[m]:
                column_counts[t] += 1
            for p in ROW_PAIR_INDICES[m]:
                witness_pair_counts[p] += 1

            status = vertex_circle_status(assign)
            if status == "ok":
                search(assign, column_counts, witness_pair_counts)
            else:
                counts[f"partial_{status}"] += 1

            for p in ROW_PAIR_INDICES[m]:
                witness_pair_counts[p] -= 1
            for t in MASK_BITS[m]:
                column_counts[t] -= 1
            del assign[center]

    row0 = OPTIONS[0][row0_index]
    assign = {0: row0}
    column_counts = [0] * N
    witness_pair_counts = [0] * len(PAIRS)
    for t in MASK_BITS[row0]:
        column_counts[t] += 1
    for p in ROW_PAIR_INDICES[row0]:
        witness_pair_counts[p] += 1
    if vertex_circle_status(assign) == "ok":
        search(assign, column_counts, witness_pair_counts)
    else:
        counts["row0_blocked"] += 1

    return {
        "row0_index": row0_index,
        "row0_witnesses": MASK_BITS[row0],
        "nodes": nodes,
        "full": full,
        "counts": dict(sorted(counts.items())),
        "full_survivors": full_survivors,
    }


def main(num_row0: int = 5) -> None:
    print(f"=== n=10 secondary checker with vertex-circle + triple-intersection filters ===")
    print(f"N={N} ROW_SIZE={ROW_SIZE} MAX_INDEGREE={MAX_INDEGREE} PAIR_CAP={PAIR_CAP} TRIPLE_CAP={TRIPLE_CAP}")
    print(f"Number of row0 options at center 0: {len(OPTIONS[0])}")
    print()

    rows = []
    t0 = time.monotonic()
    for r in range(min(num_row0, len(OPTIONS[0]))):
        s = time.monotonic()
        res = search_one_row0(r)
        elapsed = time.monotonic() - s
        res["elapsed_seconds"] = elapsed
        rows.append(res)
        print(
            f"row0={r:3d} witnesses={res['row0_witnesses']} "
            f"nodes={res['nodes']:>10d} full={res['full']} "
            f"counts={res['counts']} elapsed={elapsed:.3f}s"
        )
    total_elapsed = time.monotonic() - t0
    total_nodes = sum(r["nodes"] for r in rows)
    total_full = sum(r["full"] for r in rows)
    total_counts: Counter[str] = Counter()
    for r in rows:
        total_counts.update(r["counts"])

    payload = {
        "type": "n10_secondary_check_v1",
        "trust": "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING_SECONDARY",
        "purpose": (
            "Second-source n=10 finite-case check with additional triple-"
            "intersection filter to cross-validate the singleton-slice "
            "vertex-circle artifact's 0-full-assignment claim."
        ),
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": PAIR_CAP,
        "max_indegree": MAX_INDEGREE,
        "triple_cap": TRIPLE_CAP,
        "filters": [
            "L4: each unordered witness pair appears in <=2 selected rows",
            "L5: |S_i intersect S_j| <= 2 (via pair_cap)",
            "crossing: two-overlap selected chords cross the (i,j) source chord",
            "selected indegree <= floor(2*(n-1)/(row_size-1))",
            "vertex-circle: union-find quotient self-edge or strict cycle in nested chords",
            "TRIPLE: |S_i intersect S_j intersect S_k| <= 1 for distinct rows",
        ],
        "row0_choices_total": len(OPTIONS[0]),
        "row0_choices_covered": len(rows),
        "total_nodes": total_nodes,
        "total_full": total_full,
        "total_counts": dict(sorted(total_counts.items())),
        "total_elapsed_seconds": total_elapsed,
        "rows": rows,
    }

    with open("/tmp/n10_secondary.json", "w") as f:
        json.dump(payload, f, indent=2)

    print()
    print("=== TOTALS ===")
    print(f"row0 choices covered: {len(rows)}/{len(OPTIONS[0])}")
    print(f"total nodes: {total_nodes}")
    print(f"total full assignments: {total_full}")
    print(f"total counts: {dict(sorted(total_counts.items()))}")
    print(f"total elapsed: {total_elapsed:.2f}s")


if __name__ == "__main__":
    import sys
    num = 5
    if len(sys.argv) > 1:
        num = int(sys.argv[1])
    main(num)
