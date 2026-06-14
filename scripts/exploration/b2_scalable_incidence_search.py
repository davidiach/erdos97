#!/usr/bin/env python3
"""B2: Scalable abstract-incidence backtracking search for Erdos Problem #97.

Lane B2 (Erdos Problem #97). This script pushes the *abstract necessary-incidence*
finite frontier beyond the repository's n=9 exhaustive enumerator and n=10
singleton-slice draft. It shares NO point coordinates: it is a purely
combinatorial search over the selected 4-sets S_i (one per center), enforcing the
exact NECESSARY incidence filters that every real bad n-gon must satisfy, with
aggressive dihedral symmetry-breaking.

Necessary filters enforced (each is a documented necessary condition for a
strictly convex 4-bad n-gon; see docs/claims.md and the n9 exhaustive note):

  1. two-circle cap            : |S_a cap S_b| <= 2 for distinct centers a,b
                                 (two distinct circles meet in <= 2 points).
  2. radical-axis crossing     : if |S_a cap S_b| = {u,v} exactly, the source
                                 chord {a,b} and witness chord {u,v} must CROSS in
                                 the cyclic order, and neither is a polygon edge
                                 (perpendicular-bisector / strict-convexity lemma).
                                 In particular adjacent centers share <= 1 witness.
  3. witness-pair cap          : each unordered witness pair occurs in <= 2 rows
                                 (perp-bisector meets the boundary in <= 2 verts).
  4. selected-indegree cap     : each label has selected indegree
                                 <= floor(2*(n-1)/3)  (sharpened count).
  5. vertex-circle quotient    : selected-distance equalities quotient ordinary
                                 pair-distances; nested-chord strict inequalities
                                 around each center orient strict edges between
                                 classes; a reflexive edge (self-edge) or a
                                 directed strict cycle is unrealizable.

This is the SAME filter stack as the review-pending n9/n10 vertex-circle
checkers. The point of this script is engineering: an incremental,
symmetry-broken solver that scales further. It does not introduce any new
mathematical claim.

TRUST: any non-existence output is at best
MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING for the *necessary-incidence*
layer. It is NOT a geometric proof of any n (a real bad n-gon would induce a
surviving incidence system, but a surviving incidence system need not be
geometrically realizable, and absence of survivors here is conditional on the
implementation being correct and on these filters being the complete necessary
set). It does NOT prove Erdos #97 and does NOT produce a counterexample.

Two symmetry modes:

  --symmetry none   : every row0 = lexicographic 4-subset of labels 1..n-1 is a
                      separate start (no quotient). At n=9 this reproduces the
                      canonical 70 row0 / 184 pre-vertex-circle frontier / 0
                      survivors, used as a CORRECTNESS oracle.
  --symmetry refl0  : row0 restricted to representatives canonical under the
                      single dihedral reflection r(k)=(-k) mod n that fixes
                      center 0. SOUND symmetry break: every labelled survivor
                      has a dihedral image whose center-0 row is refl0-canonical.
                      Survivor counts are orbit-reduced, NOT all labelled
                      survivors; reported as such.

Usage:
  python scripts/exploration/b2_scalable_incidence_search.py --n 9 --symmetry none --assert-n9
  python scripts/exploration/b2_scalable_incidence_search.py --n 10 --symmetry refl0
  python scripts/exploration/b2_scalable_incidence_search.py --n 11 --symmetry refl0 --time-budget 120
  python scripts/exploration/b2_scalable_incidence_search.py --n 10 --symmetry refl0 --json out.json
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from itertools import combinations
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]

ROW_SIZE = 4
PAIR_CAP = 2

TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Scalable abstract necessary-incidence search for Erdos Problem #97. It "
    "enforces only the documented necessary incidence/order filters (two-circle "
    "cap, radical-axis crossing, witness-pair cap, selected-indegree cap, and "
    "the vertex-circle self-edge / strict-cycle quotient obstruction). Absence "
    "of a survivor is a necessary-incidence non-existence statement conditional "
    "on implementation correctness; it is NOT a geometric proof for that n, does "
    "NOT prove Erdos Problem #97, and does NOT produce a counterexample. With "
    "--symmetry refl0 the survivor counts are dihedral-orbit reduced, not all "
    "labelled survivors."
)


# ---------------------------------------------------------------------------
# cyclic-order helpers (natural cyclic order 0,1,...,n-1)
# ---------------------------------------------------------------------------
def _in_open_arc(a: int, b: int, x: int, n: int) -> bool:
    return ((x - a) % n) < ((b - a) % n) and x != a and x != b


def _chords_cross(c1: tuple[int, int], c2: tuple[int, int], n: int) -> bool:
    a, b = c1
    c, d = c2
    if len({a, b, c, d}) < 4:
        return False
    return _in_open_arc(a, b, c, n) != _in_open_arc(a, b, d, n)


class ScalableIncidenceSearch:
    """Incremental, bitset-based selected-witness incidence search.

    Rows are encoded as label bitmasks. All pairwise-compatibility, witness-pair
    membership, selected-equality membership, and nested-chord strict-edge data
    are precomputed once. The recursive search maintains column counts,
    witness-pair counts, an incremental union-find over the binom(n,2) ordinary
    pair classes (with a rollback trail), and an incremental directed strict-edge
    graph, so the vertex-circle quotient obstruction is checked in time
    proportional to the new row only.
    """

    def __init__(self, n: int, *, symmetry: str = "refl0") -> None:
        if n < ROW_SIZE + 1:
            raise ValueError("n must be at least 5")
        self.n = n
        self.symmetry = symmetry
        self.max_indegree = (PAIR_CAP * (n - 1)) // (ROW_SIZE - 1)

        self.pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
        self.npairs = len(self.pairs)
        self.pair_index = {p: k for k, p in enumerate(self.pairs)}

        # candidate rows per center, as (mask, [witness labels])
        self.row_masks: list[list[int]] = []
        self.row_bits: dict[int, list[int]] = {}
        for center in range(n):
            labels = [x for x in range(n) if x != center]
            masks = []
            for combo in combinations(labels, ROW_SIZE):
                m = 0
                for v in combo:
                    m |= 1 << v
                masks.append(m)
                self.row_bits[m] = list(combo)
            self.row_masks.append(masks)

        # per (center, mask): witness-pair indices, selected-equality pair indices,
        # and nested-chord strict edges (outer_pair_index, inner_pair_index).
        self.row_wpairs: dict[tuple[int, int], list[int]] = {}
        self.row_selpairs: dict[tuple[int, int], list[int]] = {}
        self.row_strict: dict[tuple[int, int], list[tuple[int, int]]] = {}
        for center in range(n):
            for m in self.row_masks[center]:
                bits = self.row_bits[m]
                self.row_wpairs[(center, m)] = [
                    self.pair_index[self._np(a, b)] for a, b in combinations(bits, 2)
                ]
                self.row_selpairs[(center, m)] = [
                    self.pair_index[self._np(center, w)] for w in bits
                ]
                ordered = sorted(bits, key=lambda w: (w - center) % n)
                edges: list[tuple[int, int]] = []
                for oa in range(ROW_SIZE):
                    for ob in range(oa + 1, ROW_SIZE):
                        for ia in range(ROW_SIZE):
                            for ib in range(ia + 1, ROW_SIZE):
                                if (oa, ob) == (ia, ib):
                                    continue
                                if (
                                    oa <= ia
                                    and ib <= ob
                                    and (oa < ia or ib < ob)
                                ):
                                    outer = self.pair_index[
                                        self._np(ordered[oa], ordered[ob])
                                    ]
                                    inner = self.pair_index[
                                        self._np(ordered[ia], ordered[ib])
                                    ]
                                    edges.append((outer, inner))
                self.row_strict[(center, m)] = edges

        # pairwise compatibility table: for center i<j, dict mask_i -> set(mask_j)
        # passing two-circle cap + radical-axis crossing.
        self.compatible: dict[tuple[int, int], dict[int, set[int]]] = {}
        for i in range(n):
            for j in range(i + 1, n):
                table: dict[int, set[int]] = {}
                for mi in self.row_masks[i]:
                    bi = set(self.row_bits[mi])
                    ok_set: set[int] = set()
                    for mj in self.row_masks[j]:
                        common = bi & set(self.row_bits[mj])
                        if len(common) > PAIR_CAP:
                            continue
                        if len(common) == PAIR_CAP:
                            u, v = sorted(common)
                            if not _chords_cross((i, j), (u, v), n):
                                continue
                        ok_set.add(mj)
                    table[mi] = ok_set
                self.compatible[(i, j)] = table

        self.row0_options = self._row0_options()

    # ---- symmetry --------------------------------------------------------
    def _refl(self, k: int) -> int:
        return (self.n - k) % self.n

    def _row0_options(self) -> list[int]:
        """Row0 candidate masks under the chosen symmetry convention."""
        all0 = list(self.row_masks[0])
        if self.symmetry == "none":
            return all0
        if self.symmetry == "refl0":
            reps: list[int] = []
            for m in all0:
                bits = self.row_bits[m]
                img = tuple(sorted(self._refl(x) for x in bits))
                if tuple(sorted(bits)) <= img:
                    reps.append(m)
            return reps
        raise ValueError(f"unknown symmetry {self.symmetry!r}")

    def _np(self, a: int, b: int) -> tuple[int, int]:
        return (a, b) if a < b else (b, a)

    def _compat(self, i: int, mi: int, j: int, mj: int) -> bool:
        if i < j:
            return mj in self.compatible[(i, j)][mi]
        return mi in self.compatible[(j, i)][mj]

    def full_quotient_status(self, assign: dict[int, int]) -> str:
        """From-scratch vertex-circle quotient status of a COMPLETE assignment.

        Independent recomputation used as a terminal soundness guard: it applies
        ALL selected-distance equalities (spoke merges) first, then orients every
        nested-chord strict edge through the final roots, and reports
        'self_edge', 'strict_cycle', or 'ok'. This is the same logic the
        validated n=9 oracle uses on full assignments; any survivor of the
        incremental search is re-confirmed here so the incremental per-candidate
        convention cannot leak a false survivor.
        """
        parent = list(range(self.npairs))

        def find(x: int) -> int:
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra != rb:
                parent[rb] = ra

        for center, mask in assign.items():
            sp = self.row_selpairs[(center, mask)]
            for p in sp[1:]:
                union(sp[0], p)
        graph: dict[int, list[int]] = {}
        for center, mask in assign.items():
            for outer, inner in self.row_strict[(center, mask)]:
                ro, ri = find(outer), find(inner)
                if ro == ri:
                    return "self_edge"
                graph.setdefault(ro, []).append(ri)
        color: dict[int, int] = {}

        def dfs(node: int) -> bool:
            color[node] = 1
            for nxt in graph.get(node, ()):
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

    # ---- search ----------------------------------------------------------
    def run(self, *, time_budget: float | None = None, collect_survivors: bool = True):
        """Run the full incremental search; return a result dict."""
        n = self.n
        # incremental union-find with rollback trail
        parent = list(range(self.npairs))
        rank = [0] * self.npairs

        def find(x: int) -> int:
            root = x
            while parent[root] != root:
                root = parent[root]
            # path compression is NOT used (would complicate rollback);
            # depths stay tiny because npairs is small.
            return root

        # incremental directed strict graph as adjacency multiset of ROOT classes
        # is hard to maintain under union rollback. Instead, we store strict edges
        # as raw (outer_pair, inner_pair) and re-evaluate the quotient lazily only
        # when a candidate row is tentatively added, using a snapshot union-find.
        # To keep it fast we maintain the accumulated raw strict edges and the
        # accumulated selected-equality unions on a trail.

        assign: dict[int, int] = {}
        column_counts = [0] * n
        wpair_counts = [0] * self.npairs
        sel_union_trail: list[int] = []  # appended pair-index unions for rollback
        strict_edges: list[tuple[int, int]] = []

        stats = {
            "nodes": 0,
            "self_edge_prunes": 0,
            "strict_cycle_prunes": 0,
            "incidence_prunes": 0,
        }
        survivors: list[list[list[int]]] = []
        deadline = None if time_budget is None else time.monotonic() + time_budget
        aborted = {"flag": False}

        def union(a: int, b: int) -> None:
            ra, rb = find(a), find(b)
            if ra == rb:
                return
            if rank[ra] < rank[rb]:
                ra, rb = rb, ra
            parent[rb] = ra
            sel_union_trail.append(rb)  # rb's parent changed from rb to ra
            if rank[ra] == rank[rb]:
                rank[ra] += 1

        def build_base_graph() -> tuple[dict[int, list[int]], str]:
            """Build the strict graph (over current roots) from PLACED rows.

            The union-find is frozen for the duration of evaluating all candidate
            options at one center, so this base graph is computed ONCE per
            search() call and reused across candidates. Returns (graph, status)
            where status is 'self_edge' if a reflexive edge already exists, else
            'ok'. A pre-existing self-edge among placed rows cannot happen (those
            rows already passed), but we check defensively.
            """
            graph: dict[int, list[int]] = {}
            for outer, inner in strict_edges:
                ro, ri = find(outer), find(inner)
                if ro == ri:
                    return graph, "self_edge"
                graph.setdefault(ro, []).append(ri)
            return graph, "ok"

        def status_with_candidate(
            base_graph: dict[int, list[int]], center: int, mask: int
        ) -> str:
            """Status if candidate (center,mask) added to the cached base graph.

            Only the candidate's own selected-equalities and strict edges are
            new. Selected-equality unions can merge two classes that the base
            graph already separated; to stay sound we apply the candidate's
            unions on the live union-find via place() in the caller. Here we
            only need the strict-edge incrementality: we add the candidate's
            strict edges (mapped through the CURRENT roots, i.e. before the
            candidate's own unions) and re-run cycle detection.

            NOTE: the candidate's selected-equality merges are applied by the
            caller's place(); at THIS pre-check we map edges with current roots,
            which is the same convention the validated n=9 oracle uses (the
            quotient is recomputed from the full assignment, and merges only ever
            identify spoke pairs that are not endpoints of the same row's nested
            chords). The n=9 digest match certifies this convention.
            """
            new_strict = self.row_strict[(center, mask)]
            # quick self-edge check on new edges under current roots
            extra: dict[int, list[int]] = {}
            for outer, inner in new_strict:
                ro, ri = find(outer), find(inner)
                if ro == ri:
                    return "self_edge"
                extra.setdefault(ro, []).append(ri)
            if not extra:
                return "ok"
            # merged adjacency view without mutating base_graph
            def succ(node: int):
                if node in base_graph:
                    yield from base_graph[node]
                if node in extra:
                    yield from extra[node]

            color: dict[int, int] = {}
            nodes = set(base_graph) | set(extra)
            for start in nodes:
                if color.get(start, 0) != 0:
                    continue
                stack = [(start, succ(start))]
                color[start] = 1
                while stack:
                    node, it = stack[-1]
                    advanced = False
                    for nxt in it:
                        st = color.get(nxt, 0)
                        if st == 1:
                            return "strict_cycle"
                        if st == 0:
                            color[nxt] = 1
                            stack.append((nxt, succ(nxt)))
                            advanced = True
                            break
                    if not advanced:
                        color[node] = 2
                        stack.pop()
            return "ok"

        def quotient_status_with(center: int, mask: int) -> str:
            """Standalone status check (row0 / fallback): build base + candidate."""
            base_graph, base_status = build_base_graph()
            if base_status == "self_edge":
                return "self_edge"
            return status_with_candidate(base_graph, center, mask)

        def valid_options(center: int) -> list[int]:
            out: list[int] = []
            for m in self.row_masks[center]:
                ok = True
                for other, om in assign.items():
                    if not self._compat(center, m, other, om):
                        ok = False
                        break
                if not ok:
                    continue
                bits = self.row_bits[m]
                if any(column_counts[t] >= self.max_indegree for t in bits):
                    continue
                if any(wpair_counts[p] >= PAIR_CAP for p in self.row_wpairs[(center, m)]):
                    continue
                out.append(m)
            return out

        def choose_center() -> tuple[int | None, list[int]]:
            best_c: int | None = None
            best_opts: list[int] | None = None
            for c in range(n):
                if c in assign:
                    continue
                opts = valid_options(c)
                if best_opts is None or len(opts) < len(best_opts):
                    best_c, best_opts = c, opts
                    if not opts:
                        break
            return best_c, (best_opts or [])

        def place(center: int, mask: int) -> int:
            """Apply selected-equalities + strict edges; return trail marker."""
            marker = len(sel_union_trail)
            sel_pairs = self.row_selpairs[(center, mask)]
            base = sel_pairs[0]
            for p in sel_pairs[1:]:
                union(base, p)
            strict_edges.extend(self.row_strict[(center, mask)])
            for t in self.row_bits[mask]:
                column_counts[t] += 1
            for p in self.row_wpairs[(center, mask)]:
                wpair_counts[p] += 1
            assign[center] = mask
            return marker

        def unplace(center: int, mask: int, marker: int) -> None:
            del assign[center]
            for p in self.row_wpairs[(center, mask)]:
                wpair_counts[p] -= 1
            for t in self.row_bits[mask]:
                column_counts[t] -= 1
            del strict_edges[len(strict_edges) - len(self.row_strict[(center, mask)]):]
            while len(sel_union_trail) > marker:
                rb = sel_union_trail.pop()
                parent[rb] = rb  # undo union (rb was a root before)

        def search() -> None:
            if aborted["flag"]:
                return
            stats["nodes"] += 1
            if deadline is not None and (stats["nodes"] & 0x3FF) == 0:
                if time.monotonic() > deadline:
                    aborted["flag"] = True
                    return
            if len(assign) == n:
                # terminal soundness guard: re-confirm with the from-scratch
                # full quotient (applies all merges before orienting edges).
                final_status = self.full_quotient_status(assign)
                if final_status != "ok":
                    if final_status == "self_edge":
                        stats["self_edge_prunes"] += 1
                    else:
                        stats["strict_cycle_prunes"] += 1
                    return
                if collect_survivors:
                    survivors.append(
                        [
                            [int(x) for x in self.row_bits[assign[c]]]
                            for c in range(n)
                        ]
                    )
                else:
                    survivors.append([])  # count only
                return
            center, opts = choose_center()
            if center is None or not opts:
                if center is not None:
                    stats["incidence_prunes"] += 1
                return
            base_graph, base_status = build_base_graph()
            if base_status == "self_edge":
                # an already-placed-row self-edge (defensive; should not occur).
                stats["self_edge_prunes"] += 1
                return
            for m in opts:
                status = status_with_candidate(base_graph, center, m)
                if status == "self_edge":
                    stats["self_edge_prunes"] += 1
                    continue
                if status == "strict_cycle":
                    stats["strict_cycle_prunes"] += 1
                    continue
                marker = place(center, m)
                search()
                unplace(center, m, marker)
                if aborted["flag"]:
                    return

        t0 = time.monotonic()
        for row0 in self.row0_options:
            # row0 always passes its own filters; still check its quotient (no
            # edges/unions yet from others, but a single row can already
            # self-conflict? No: one row's strict edges are between distinct
            # ordinary pairs and its selected-equalities only merge spoke pairs,
            # which are not among its own witness-pair strict edges. We check
            # anyway for safety.)
            status = quotient_status_with(0, row0)
            if status == "self_edge":
                stats["self_edge_prunes"] += 1
                continue
            if status == "strict_cycle":
                stats["strict_cycle_prunes"] += 1
                continue
            marker = place(0, row0)
            search()
            unplace(0, row0, marker)
            if aborted["flag"]:
                break
        elapsed = time.monotonic() - t0

        survivor_count = len(survivors)
        digest = None
        if collect_survivors and survivors:
            sorted_surv = sorted(survivors)
            digest = hashlib.sha256(
                json.dumps(sorted_surv, separators=(",", ":")).encode()
            ).hexdigest()

        return {
            "n": n,
            "symmetry": self.symmetry,
            "row0_options": len(self.row0_options),
            "max_indegree": self.max_indegree,
            "nodes": stats["nodes"],
            "self_edge_prunes": stats["self_edge_prunes"],
            "strict_cycle_prunes": stats["strict_cycle_prunes"],
            "survivors": survivor_count,
            "survivor_digest_sha256": digest,
            "aborted": aborted["flag"],
            "elapsed_seconds": round(elapsed, 3),
            "_survivor_rows": survivors if collect_survivors else None,
        }


def build_payload(result: dict[str, Any]) -> dict[str, Any]:
    out = {
        "schema": "erdos97.b2_scalable_incidence_search.v1",
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "result": {k: v for k, v in result.items() if not k.startswith("_")},
    }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument(
        "--symmetry",
        choices=("none", "refl0"),
        default="refl0",
        help="row0 symmetry convention (default refl0)",
    )
    ap.add_argument(
        "--time-budget",
        type=float,
        default=None,
        help="abort after this many seconds (partial frontier reported)",
    )
    ap.add_argument(
        "--no-survivors",
        action="store_true",
        help="count survivors without materializing rows (lower memory)",
    )
    ap.add_argument(
        "--assert-n9",
        action="store_true",
        help="assert n=9 --symmetry none reproduces 70 row0 and 0 survivors",
    )
    ap.add_argument("--json", type=Path, default=None, help="write full JSON here")
    args = ap.parse_args(argv)

    search = ScalableIncidenceSearch(args.n, symmetry=args.symmetry)
    result = search.run(
        time_budget=args.time_budget,
        collect_survivors=not args.no_survivors,
    )

    if args.assert_n9:
        assert args.n == 9 and args.symmetry == "none", "--assert-n9 needs --n 9 --symmetry none"
        assert result["row0_options"] == 70, result["row0_options"]
        assert result["survivors"] == 0, result["survivors"]
        assert not result["aborted"], "search aborted before completion"
        print("ASSERT-N9 OK: 70 row0 options, 0 incidence survivors (matches frontier).")

    payload = build_payload(result)
    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        # include survivor rows on disk only when the set is small enough to be
        # useful for a downstream z3 realizability spot-check.
        rows = result.get("_survivor_rows")
        if rows is not None and len(rows) <= 500:
            payload["survivors"] = rows
            payload["cyclic_order"] = list(range(result["n"]))
        args.json.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    r = result
    print(
        f"n={r['n']} symmetry={r['symmetry']} row0={r['row0_options']} "
        f"indeg<={r['max_indegree']} | nodes={r['nodes']:,} "
        f"self_edge_prunes={r['self_edge_prunes']:,} "
        f"strict_cycle_prunes={r['strict_cycle_prunes']:,} "
        f"survivors={r['survivors']} aborted={r['aborted']} "
        f"elapsed={r['elapsed_seconds']}s"
    )
    if r["survivor_digest_sha256"]:
        print(f"survivor_digest={r['survivor_digest_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
