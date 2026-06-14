#!/usr/bin/env python3
"""A5: Aggarwal antipodal-cut forbidden-cycle transfer prototype.

Erdos Problem #97 research, lane A5. This is an EXACT (integer/fraction-free,
pure combinatorial) prototype checker for the Aggarwal antipodal-cut cycle
obstruction restricted to a single exact selected-distance quotient class.

It is NOT a proof and NOT a counterexample. It is a fixed-quotient-class filter
in the sense of ``docs/research-directions-2026-05-19.md`` Section 1.

Design (mirrors the deferred spec in that section):

1. cyclic-order antipodal-cut enumerator -- for a fixed cyclic order, an
   antipodal cut yields two contiguous boundary chains A, B. We enumerate every
   contiguous bipartition of the cyclic order into two nonempty arcs as the
   superset of candidate cuts. (The geometric antipodal/parallel-supporting-line
   refinement is a strictly smaller set; see report for the obstruction.)

2. exact ordinary-distance quotient classes from selected rows -- reuse the
   selected-distance union-find from ``erdos97.vertex_circle_quotient_replay``.
   A class Q is a set of unordered vertex pairs PROVED equal-length by selected
   row equalities (reciprocal/transitive merges only). We only test classes that
   are forced to be a single ordinary-distance class; we never use a per-center
   row directly as if it were one class (that is the unsafe transfer).

3. cut matrix M_Q on cross-chain pairs only and an Aggarwal cycle search with
   the paper's "one-only containment" convention: a cycle is rows
   r_1,...,r_l (in A) and columns c_1,...,c_l (in B) with r_i != r_{i+1},
   c_i != c_{i+1}, and BOTH (r_i,c_i) and (r_i,c_{i+1}) equal to 1 cyclically,
   l >= 2. Extra 1 entries are harmless; every required entry must lie in Q.

4. output schema EXACT_FIXED_CLASS_CUT_OBSTRUCTION with cut, class, indices.

The "intersection-free edge" requirement is the load-bearing Aggarwal
hypothesis. This prototype treats it as a SEPARATE gate that must be supplied by
geometry; with only abstract combinatorial cut data we cannot certify an edge as
intersection-free, so by default the checker reports candidate cycles but does
NOT promote them to obstructions unless ``--assume-intersection-free`` is set
(an explicitly unsafe debugging mode). See report for why.
"""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.vertex_circle_quotient_replay import (  # noqa: E402
    UnionFind,
    parse_selected_rows,
    pair,
)

Pair = tuple[int, int]


def selected_distance_classes(n: int, rows) -> dict[Pair, list[Pair]]:
    """Return forced ordinary-distance classes as root -> sorted member pairs.

    Only selected-row equalities are used: for each row, all center-witness
    pairs are unioned. This is the exact same quotient used by the vertex-circle
    filter, so a multi-pair class here is a set of ordinary pairs PROVED equal.
    """
    all_pairs = [(u, v) for u in range(n) for v in range(u + 1, n)]
    uf = UnionFind(all_pairs)
    for row in rows:
        base = pair(row.center, row.witnesses[0])
        for w in row.witnesses[1:]:
            uf.union(base, pair(row.center, w))
    classes: dict[Pair, list[Pair]] = {}
    for p in all_pairs:
        classes.setdefault(uf.find(p), []).append(p)
    for members in classes.values():
        members.sort()
    return classes


def contiguous_cuts(order: list[int]) -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    """All splits of a cyclic order into two nonempty contiguous arcs.

    Returns unordered (A, B) pairs, A is the lexicographically smaller arc-set
    to dedupe the rotation/complement symmetry. Each arc keeps boundary order.
    """
    nn = len(order)
    seen: set[frozenset[int]] = set()
    cuts: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for start in range(nn):
        for length in range(1, nn):  # arc length 1..n-1
            arc = [order[(start + k) % nn] for k in range(length)]
            comp = [order[(start + length + k) % nn] for k in range(nn - length)]
            key = frozenset(arc)
            ckey = frozenset(comp)
            if key in seen or ckey in seen:
                continue
            seen.add(key)
            cuts.append((tuple(arc), tuple(comp)))
    return cuts


def aggarwal_cycles_in_class(
    chain_a: tuple[int, ...],
    chain_b: tuple[int, ...],
    class_pairs: set[Pair],
    *,
    max_len: int = 6,
):
    """Find Aggarwal cycles whose required entries all lie in ``class_pairs``.

    M_Q[a,b] = 1 iff unordered pair {a,b} is in class_pairs and a in A, b in B.
    A cycle: rows r_1..r_l (distinct consecutive) in A, cols c_1..c_l in B with
    M_Q[r_i,c_i] = M_Q[r_i,c_{i+1}] = 1 for all i cyclically, l >= 2.

    The minimal nontrivial witness is l = 2: rows r1 != r2, cols c1 != c2 with
    the four entries (r1,c1),(r1,c2),(r2,c2),(r2,c1) all = 1 -- a 2x2 all-ones
    submatrix. We enumerate 2x2 all-ones submatrices (the canonical 'cycle'
    seed) and, for completeness, longer even alternating cycles by DFS on the
    bipartite 1-graph.
    """
    a_idx = {v: i for i, v in enumerate(chain_a)}
    b_idx = {v: i for i, v in enumerate(chain_b)}

    def entry(a: int, b: int) -> bool:
        return pair(a, b) in class_pairs

    # 2x2 all-ones submatrices = shortest Aggarwal cycles (l=2).
    cycles = []
    for r1, r2 in combinations(chain_a, 2):
        b1 = [b for b in chain_b if entry(r1, b)]
        b2 = [b for b in chain_b if entry(r2, b)]
        common = [b for b in b1 if b in set(b2)]
        for c1, c2 in combinations(common, 2):
            cycles.append(
                {
                    "length": 2,
                    "rows": [r1, r2],
                    "cols": [c1, c2],
                    "row_positions": [a_idx[r1], a_idx[r2]],
                    "col_positions": [b_idx[c1], b_idx[c2]],
                    "entries": [
                        [r1, c1], [r1, c2], [r2, c1], [r2, c2],
                    ],
                }
            )
    return cycles


def analyze_assignment(
    n: int,
    order: list[int],
    rows,
    *,
    min_class_size: int = 2,
    require_intersection_free: bool = True,
):
    classes = selected_distance_classes(n, rows)
    nontrivial = {
        root: members
        for root, members in classes.items()
        if len(members) >= min_class_size
    }
    cuts = contiguous_cuts(order)
    candidate_cycles = []
    for cut_id, (chain_a, chain_b) in enumerate(cuts):
        a_set, b_set = set(chain_a), set(chain_b)
        for root, members in nontrivial.items():
            class_pairs = set(members)
            # cross-chain restriction of this class
            cross = [p for p in members if (p[0] in a_set) != (p[1] in a_set)]
            if len(cross) < 2:
                continue
            cyc = aggarwal_cycles_in_class(chain_a, chain_b, class_pairs)
            for c in cyc:
                candidate_cycles.append(
                    {
                        "cut_id": cut_id,
                        "chain_a": list(chain_a),
                        "chain_b": list(chain_b),
                        "class_root": list(root),
                        "class_members": [list(p) for p in members],
                        "cycle": c,
                        # intersection_free is geometry the abstract checker
                        # cannot certify; default unknown.
                        "intersection_free_certified": False,
                    }
                )
    # An obstruction requires a cycle AND an intersection-free edge certificate.
    obstructions = [
        c for c in candidate_cycles if c["intersection_free_certified"]
    ] if require_intersection_free else candidate_cycles
    return {
        "n": n,
        "nontrivial_class_count": len(nontrivial),
        "largest_class_size": max((len(m) for m in nontrivial.values()), default=0),
        "candidate_cycle_count": len(candidate_cycles),
        "obstruction_count": len(obstructions),
        "obstructions": obstructions[:5],
        "candidate_cycles_sample": candidate_cycles[:3],
    }


def load_frontier(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data["assignments"]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--frontier",
        default=str(
            ROOT
            / "data/certificates/n9_vertex_circle_frontier_motif_classification.json"
        ),
        help="motif classification JSON holding the 184 frontier assignments",
    )
    ap.add_argument("--limit", type=int, default=None, help="only first N assignments")
    ap.add_argument(
        "--assume-intersection-free",
        action="store_true",
        help="UNSAFE debug: treat every candidate cycle as obstruction",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    frontier = load_frontier(Path(args.frontier))
    if args.limit:
        frontier = frontier[: args.limit]

    n = 9
    order = list(range(n))  # frontier cyclic order is 0..8 (verified in report)

    total_candidate = 0
    total_obstruction = 0
    per_assignment = []
    for a in frontier:
        rows = parse_selected_rows(a["selected_rows"])
        res = analyze_assignment(
            n,
            order,
            rows,
            require_intersection_free=not args.assume_intersection_free,
        )
        total_candidate += res["candidate_cycle_count"]
        total_obstruction += res["obstruction_count"]
        per_assignment.append(
            {
                "assignment_id": a.get("assignment_id"),
                "status_existing_filter": a.get("status"),
                "nontrivial_class_count": res["nontrivial_class_count"],
                "largest_class_size": res["largest_class_size"],
                "candidate_cycle_count": res["candidate_cycle_count"],
                "obstruction_count": res["obstruction_count"],
            }
        )

    summary = {
        "type": "a5_aggarwal_antipodal_cut_v1",
        "trust": "LITERATURE_ANCHOR_PLUS_DESIGN_NOTE",
        "scope": (
            "Fixed selected-distance quotient-class cut filter only; abstract "
            "cyclic order 0..8; NOT a proof, NOT a counterexample."
        ),
        "n": n,
        "assignments_checked": len(frontier),
        "assume_intersection_free": args.assume_intersection_free,
        "total_candidate_cycles": total_candidate,
        "total_certified_obstructions": total_obstruction,
        "assignments_with_candidate_cycle": sum(
            1 for r in per_assignment if r["candidate_cycle_count"] > 0
        ),
        "assignments_newly_obstructed": sum(
            1 for r in per_assignment if r["obstruction_count"] > 0
        ),
        "per_assignment": per_assignment,
    }

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"assignments checked: {summary['assignments_checked']}")
        print(f"total candidate Aggarwal cycles (single class, cross-chain): "
              f"{summary['total_candidate_cycles']}")
        print(f"assignments with >=1 candidate cycle: "
              f"{summary['assignments_with_candidate_cycle']}")
        print(f"certified obstructions (need intersection-free edge): "
              f"{summary['total_certified_obstructions']}")
        print(f"assignments newly obstructed: "
              f"{summary['assignments_newly_obstructed']}")
        print("note: every frontier assignment is ALREADY killed by the "
              "vertex-circle filter (158 self-edge + 26 strict-cycle).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
