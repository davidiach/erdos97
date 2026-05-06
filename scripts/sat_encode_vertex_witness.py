#!/usr/bin/env python3
"""SAT/SMT encoding for the n vertex-witness incidence system.

Each center i in {0, ..., n-1} must select a 4-subset S_i of {0, ..., n-1}\\{i}.
We encode necessary combinatorial constraints (the same ones used by the pure-
Python `n9_vertex_circle_exhaustive` checker, parameterized by n) and ask a
SAT solver whether any assignment survives.

Constraints encoded:
  (R) Exactly one row choice per center.
  (P) Pair cap: |S_i cap S_j| <= 2; on overlap == 2 the source chord (i,j) and
      the witness chord (a,b) must cross in the cyclic order.
  (A) Adjacent rows (i, i+1 mod n) share at most one witness (special case of
      P, since on the polygon edge the witness chord cannot cross the edge).
  (T) Triple uniqueness: no three rows can share the same 3 witnesses.
  (W) Witness-pair indegree cap: each unordered witness pair (a, b) appears in
      at most 2 selected rows.
  (V) Vertex-circle: select-pair equivalence collapse + nested-chord directed
      edges, and the resulting directed graph on classes must have no
      self-loop and no directed cycle.

Solver options:
  --solver z3    (default, recommended for the V constraint)
  --solver pysat (handles R, P, A, T, W; V dropped to a self-loop pre-check
                  via row-internal nested chords inside one row).

For pysat the V constraint is approximated by intra-row checks: the strict
edges that lie within a single row already are caught by detecting impossible
self-edges at the *row* level (after merging the row's selected pairs).  The
multi-row vertex-circle cycle check is omitted in pysat mode.

n=9 is run as a sanity check (expected UNSAT under the z3 encoding).

Usage:
  python3 scripts/sat_encode_vertex_witness.py --n 9 --solver z3
  python3 scripts/sat_encode_vertex_witness.py --n 11 --solver z3 \
      --output data/certificates/sat_n11_witness.json --timeout-ms 600000
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

ROW_SIZE = 4
PAIR_CAP = 2


# ----------------------------------------------------------------------
# Combinatorial helpers parameterized by n.
# ----------------------------------------------------------------------


def in_open_arc(n: int, a: int, b: int, x: int) -> bool:
    return ((x - a) % n) < ((b - a) % n) and x != a and x != b


def chords_cross(n: int, chord1: tuple[int, int], chord2: tuple[int, int]) -> bool:
    a, b = chord1
    c, d = chord2
    if len({a, b, c, d}) < 4:
        return False
    return in_open_arc(n, a, b, c) != in_open_arc(n, a, b, d)


def normalized_pair(a: int, b: int) -> tuple[int, int]:
    if a == b:
        raise ValueError("loop pair")
    return (a, b) if a < b else (b, a)


@dataclass
class WitnessProblem:
    n: int

    def __post_init__(self) -> None:
        n = self.n
        self.pairs: list[tuple[int, int]] = [
            (i, j) for i in range(n) for j in range(i + 1, n)
        ]
        self.pair_index = {p: idx for idx, p in enumerate(self.pairs)}

        self.options: list[list[tuple[int, ...]]] = [
            [
                tuple(sorted(combo))
                for combo in combinations(
                    [t for t in range(n) if t != center],
                    ROW_SIZE,
                )
            ]
            for center in range(n)
        ]

        self.selected_pair_idx: dict[tuple[int, int], list[int]] = {}
        self.row_pair_idx: dict[tuple[int, int], list[int]] = {}
        self.strict_edges: dict[tuple[int, int], list[tuple[int, int]]] = {}

        for center in range(n):
            for k, witnesses in enumerate(self.options[center]):
                self.selected_pair_idx[(center, k)] = [
                    self.pair_index[normalized_pair(center, w)] for w in witnesses
                ]
                self.row_pair_idx[(center, k)] = [
                    self.pair_index[normalized_pair(a, b)]
                    for a, b in combinations(witnesses, 2)
                ]
                ordered = sorted(witnesses, key=lambda w: (w - center) % n)
                edges: list[tuple[int, int]] = []
                for outer_start in range(4):
                    for outer_end in range(outer_start + 1, 4):
                        for inner_start in range(4):
                            for inner_end in range(inner_start + 1, 4):
                                if (outer_start, outer_end) == (
                                    inner_start,
                                    inner_end,
                                ):
                                    continue
                                contains = (
                                    outer_start <= inner_start
                                    and inner_end <= outer_end
                                    and (
                                        outer_start < inner_start
                                        or inner_end < outer_end
                                    )
                                )
                                if contains:
                                    outer_p = normalized_pair(
                                        ordered[outer_start], ordered[outer_end]
                                    )
                                    inner_p = normalized_pair(
                                        ordered[inner_start], ordered[inner_end]
                                    )
                                    edges.append(
                                        (
                                            self.pair_index[outer_p],
                                            self.pair_index[inner_p],
                                        )
                                    )
                self.strict_edges[(center, k)] = edges

    def num_options(self) -> int:
        return sum(len(opts) for opts in self.options)


def witness_set(p: WitnessProblem, center: int, k: int) -> frozenset[int]:
    return frozenset(p.options[center][k])


def adjacent_compatible(
    p: WitnessProblem,
    i: int,
    j: int,
    ki: int,
    kj: int,
) -> bool:
    Si = witness_set(p, i, ki)
    Sj = witness_set(p, j, kj)
    common = Si & Sj
    if len(common) > 1:
        return False
    return True


def pair_compatible(p: WitnessProblem, i: int, j: int, ki: int, kj: int) -> bool:
    Si = witness_set(p, i, ki)
    Sj = witness_set(p, j, kj)
    common = Si & Sj
    if len(common) > PAIR_CAP:
        return False
    if len(common) == PAIR_CAP:
        a, b = sorted(common)
        if not chords_cross(p.n, (i, j), (a, b)):
            return False
    return True


# ----------------------------------------------------------------------
# Z3 encoder
# ----------------------------------------------------------------------


def encode_z3(p: WitnessProblem, *, timeout_ms: int | None = None):
    import z3

    s = z3.Solver()
    if timeout_ms is not None:
        s.set("timeout", int(timeout_ms))
    n = p.n
    num_pairs = len(p.pairs)

    # row_idx[i] in {0..len(options[i])-1}
    row_idx = [z3.Int(f"row_{i}") for i in range(n)]
    for i in range(n):
        s.add(row_idx[i] >= 0)
        s.add(row_idx[i] < len(p.options[i]))

    # x[(i, k)] Bool: row i picks option k.
    x: dict[tuple[int, int], object] = {}
    for i in range(n):
        opts_i = p.options[i]
        ks = []
        for k in range(len(opts_i)):
            v = z3.Bool(f"x_{i}_{k}")
            x[(i, k)] = v
            ks.append(v)
            s.add(v == (row_idx[i] == k))
        # exactly_one is implied by the row_idx encoding.

    # rank[pi] = integer rank assigned to pair index pi.  Pairs in the same
    # equivalence class must share the same rank; strict-edge outer < inner
    # in rank.  This precisely encodes the union-find collapse + acyclicity.
    rank = [z3.Int(f"rank_{pi}") for pi in range(num_pairs)]
    for pi in range(num_pairs):
        s.add(rank[pi] >= 0)
        s.add(rank[pi] < num_pairs)

    # (P) Pair compatibility.
    for i in range(n):
        for j in range(i + 1, n):
            for ki in range(len(p.options[i])):
                for kj in range(len(p.options[j])):
                    if not pair_compatible(p, i, j, ki, kj):
                        s.add(z3.Or(z3.Not(x[(i, ki)]), z3.Not(x[(j, kj)])))

    # (A) Adjacent rows share at most 1 (subsumed by P via cyclic-cross failure
    # on polygon edges, but we keep it explicit for redundancy).
    for i in range(n):
        j = (i + 1) % n
        a, b = (i, j) if i < j else (j, i)
        for ki in range(len(p.options[a])):
            for kj in range(len(p.options[b])):
                if not adjacent_compatible(p, a, b, ki, kj):
                    s.add(z3.Or(z3.Not(x[(a, ki)]), z3.Not(x[(b, kj)])))

    # (T) Triple uniqueness is *implied* by pair_cap = 2 (any three centers
    # sharing three witnesses would force two of them to share 3 witnesses,
    # violating P).  We omit it.

    # (W) Witness-pair indegree cap 2.  For each pair (a, b), at most 2 rows
    # cover it.  Use linear sum over Bool casts.
    for pair_idx, (a, b) in enumerate(p.pairs):
        covering: list[object] = []
        for c in range(n):
            if c == a or c == b:
                continue
            for k, witnesses in enumerate(p.options[c]):
                if a in witnesses and b in witnesses:
                    covering.append(z3.If(x[(c, k)], 1, 0))
        if len(covering) > PAIR_CAP:
            s.add(z3.Sum(covering) <= PAIR_CAP)

    # (V) Vertex-circle: rank collapse + acyclicity.
    # If row (i, k) is selected, all selected_pair_idx[i,k] must share the
    # same rank, and each strict_edge (outer, inner) must satisfy
    # rank[outer] < rank[inner].
    for (i, k), vid in x.items():
        sel = p.selected_pair_idx[(i, k)]
        if len(sel) >= 2:
            base = sel[0]
            for q in sel[1:]:
                s.add(z3.Implies(vid, rank[base] == rank[q]))
        for outer, inner in p.strict_edges[(i, k)]:
            s.add(z3.Implies(vid, rank[outer] < rank[inner]))

    return s, x, row_idx, rank


# ----------------------------------------------------------------------
# pysat encoder (fast but does not encode the multi-row V acyclicity).
# ----------------------------------------------------------------------


class CNFBuilder:
    def __init__(self) -> None:
        self.next_id = 1
        self.clauses: list[list[int]] = []

    def new_var(self) -> int:
        v = self.next_id
        self.next_id += 1
        return v

    def add_clause(self, clause: Iterable[int]) -> None:
        self.clauses.append(list(clause))

    def add_at_most_one(self, variables: Sequence[int]) -> None:
        for a, b in combinations(variables, 2):
            self.clauses.append([-a, -b])

    def add_exactly_one(self, variables: Sequence[int]) -> None:
        if not variables:
            raise ValueError("exactly_one of empty list is unsatisfiable")
        self.clauses.append(list(variables))
        self.add_at_most_one(variables)

    def add_at_most_k(self, variables: Sequence[int], k: int) -> None:
        """Sequential counter (Sinz 2005) at-most-k encoding.

        Introduces O(n*k) auxiliary variables and O(n*k) clauses, replacing
        the naive O(C(n, k+1)) pairwise approach.
        """
        n = len(variables)
        if k >= n:
            return
        if k == 0:
            for v in variables:
                self.clauses.append([-v])
            return
        if k == n - 1:
            # at most n-1 -> at least one negative; weak constraint, do nothing.
            # actually that's "not all true": just NAND. We add it anyway.
            self.clauses.append([-v for v in variables])
            return
        # s[i][j] = "at least j+1 of variables[0..i] are true"
        s = [[self.new_var() for _ in range(k)] for _ in range(n)]
        # base: var[0] -> s[0][0]
        self.clauses.append([-variables[0], s[0][0]])
        # s[0][j] for j > 0 must be false
        for j in range(1, k):
            self.clauses.append([-s[0][j]])
        for i in range(1, n):
            # var[i] -> s[i][0]
            self.clauses.append([-variables[i], s[i][0]])
            # s[i-1][0] -> s[i][0]
            self.clauses.append([-s[i - 1][0], s[i][0]])
            for j in range(1, k):
                # var[i] AND s[i-1][j-1] -> s[i][j]
                self.clauses.append([-variables[i], -s[i - 1][j - 1], s[i][j]])
                # s[i-1][j] -> s[i][j]
                self.clauses.append([-s[i - 1][j], s[i][j]])
            # forbid (k+1)-th: var[i] AND s[i-1][k-1] -> false
            self.clauses.append([-variables[i], -s[i - 1][k - 1]])


def encode_pysat(p: WitnessProblem) -> tuple[CNFBuilder, dict[tuple[int, int], int]]:
    """Encode R, P, A, T, W only.  V must be checked post-hoc."""
    cnf = CNFBuilder()
    n = p.n

    x: dict[tuple[int, int], int] = {}
    for i in range(n):
        ids = [cnf.new_var() for _ in p.options[i]]
        cnf.add_exactly_one(ids)
        for k, vid in enumerate(ids):
            x[(i, k)] = vid

    for i in range(n):
        for j in range(i + 1, n):
            for ki in range(len(p.options[i])):
                for kj in range(len(p.options[j])):
                    if not pair_compatible(p, i, j, ki, kj):
                        cnf.add_clause([-x[(i, ki)], -x[(j, kj)]])

    for i in range(n):
        j = (i + 1) % n
        a, b = (i, j) if i < j else (j, i)
        for ki in range(len(p.options[a])):
            for kj in range(len(p.options[b])):
                if not adjacent_compatible(p, a, b, ki, kj):
                    cnf.add_clause([-x[(a, ki)], -x[(b, kj)]])

    # Triple uniqueness is implied by pair_cap = 2 (P), so omitted.

    for pair_idx, (a, b) in enumerate(p.pairs):
        covering = []
        for c in range(n):
            if c == a or c == b:
                continue
            for k, witnesses in enumerate(p.options[c]):
                if a in witnesses and b in witnesses:
                    covering.append(x[(c, k)])
        if len(covering) > PAIR_CAP:
            cnf.add_at_most_k(covering, PAIR_CAP)

    return cnf, x


# ----------------------------------------------------------------------
# Driver
# ----------------------------------------------------------------------


def _build_uf_and_graph(p: WitnessProblem, rows: list[list[int]]):
    """Helper returning (row_choices, uf_parent, edges_with_source_row)."""
    from collections import defaultdict  # noqa: F401

    n = p.n
    row_choices: list[int] = []
    for i in range(n):
        target = tuple(sorted(rows[i])) if rows[i] else None
        if target is None:
            row_choices.append(-1)
            continue
        for k, opt in enumerate(p.options[i]):
            if opt == target:
                row_choices.append(k)
                break
        else:
            row_choices.append(-1)

    parent = list(range(len(p.pairs)))
    union_source: dict[tuple[int, int], int] = {}

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a: int, b: int, src_row: int) -> None:
        ra, rb = find(a), find(b)
        if ra == rb:
            return
        if rb < ra:
            ra, rb = rb, ra
        parent[rb] = ra
        union_source[(ra, rb)] = src_row

    for i, k in enumerate(row_choices):
        if k < 0:
            continue
        sel = p.selected_pair_idx[(i, k)]
        for q in sel[1:]:
            union(sel[0], q, i)

    edges: list[tuple[int, int, int]] = []  # (outer_idx, inner_idx, source_row)
    for i, k in enumerate(row_choices):
        if k < 0:
            continue
        for outer, inner in p.strict_edges[(i, k)]:
            edges.append((outer, inner, i))
    return row_choices, parent, edges, union_source


def vertex_circle_status_pattern(p: WitnessProblem, rows: list[list[int]]) -> str:
    """Return ok/self_edge/strict_cycle for a full pattern.

    Re-implementation of the n=9 checker for general n.
    """
    from collections import defaultdict

    row_choices, parent, edges, _ = _build_uf_and_graph(p, rows)
    if any(k < 0 for k in row_choices):
        return "missing_row"

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    graph: dict[int, list[int]] = defaultdict(list)
    for outer, inner, _src in edges:
        o = find(outer)
        n_inner = find(inner)
        if o == n_inner:
            return "self_edge"
        graph[o].append(n_inner)

    color: dict[int, int] = {}

    def dfs(node: int) -> bool:
        color[node] = 1
        for nxt in graph.get(node, []):
            if color.get(nxt, 0) == 1:
                return True
            if color.get(nxt, 0) == 0 and dfs(nxt):
                return True
        color[node] = 2
        return False

    for node in list(graph):
        if color.get(node, 0) == 0 and dfs(node):
            return "strict_cycle"
    return "ok"


def minimal_v_failure_rows(p: WitnessProblem, rows: list[list[int]]) -> tuple[str, list[int]]:
    """Return (status, sorted list of row indices that suffice to reproduce V failure).

    For self-edge: identifies the row giving the offending strict edge plus a
    chain of rows whose selected pairs cause the merge of outer~inner in
    union-find.

    For strict-cycle: identifies the rows giving the cycle's edges plus a
    chain whose unions merge each (outer, inner) endpoint to a class
    participating in the cycle.

    The result is a sound subset: removing those rows breaks the V failure
    (modulo the rest still being R/P/A/W-feasible), so blocking any subset
    extension with the same row choices on those indices preserves UNSAT.
    """
    from collections import defaultdict

    row_choices, parent_initial, edges, _ = _build_uf_and_graph(p, rows)
    if any(k < 0 for k in row_choices):
        return ("missing_row", list(range(len(rows))))

    # Re-do unions, but track per-pair which rows merged which.
    parent = list(range(len(p.pairs)))

    def find(x: int) -> int:
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    # Pair-of-pairs -> rows that merged them (the entire chain).
    # We store: for each pair index pi, the row that connected it to its
    # representative.  Then walking up through a sequence of unions, we can
    # collect the rows.
    edge_row: dict[int, int] = {}  # pair_idx -> row that connected pi to its current parent

    for i, k in enumerate(row_choices):
        sel = p.selected_pair_idx[(i, k)]
        base = sel[0]
        for q in sel[1:]:
            ra = find(base)
            rb = find(q)
            if ra == rb:
                continue
            # union; record the row.
            if rb < ra:
                ra, rb = rb, ra
            parent[rb] = ra
            edge_row[rb] = i
            # also the underlying connection: q's path to base.
            # Mark sel and q to connect via row i.

    def connecting_rows(a: int, b: int) -> set[int]:
        """Find a sequence of unions that connect a and b.

        Walk up parent chain from a and b until they meet at a common
        ancestor; collect each `edge_row[node]` along both paths.
        """
        path_a: list[int] = []
        cur = a
        while parent[cur] != cur:
            path_a.append(cur)
            cur = parent[cur]
        path_a.append(cur)
        a_anc = set(path_a)
        path_b: list[int] = []
        cur = b
        while parent[cur] != cur and cur not in a_anc:
            path_b.append(cur)
            cur = parent[cur]
        # cur is the common ancestor
        path_b.append(cur)
        common = cur
        idx = path_a.index(common)
        path_a = path_a[: idx + 1]
        rows_set: set[int] = set()
        # Each parent step in path_a (except last == common) had an edge_row entry.
        for node in path_a[:-1]:
            if node in edge_row:
                rows_set.add(edge_row[node])
        for node in path_b[:-1]:
            if node in edge_row:
                rows_set.add(edge_row[node])
        return rows_set

    # Detect first violation:
    graph: dict[int, list[tuple[int, int]]] = defaultdict(list)  # class -> [(class, source_row, outer_idx, inner_idx)]
    for outer, inner, src in edges:
        o = find(outer)
        ni = find(inner)
        if o == ni:
            blame_rows = {src}
            blame_rows |= connecting_rows(outer, inner)
            return ("self_edge", sorted(blame_rows))
        graph[o].append((ni, src, outer, inner))

    # Cycle detection on graph (DAG check).
    color: dict[int, int] = {}
    parent_in_dfs: dict[int, tuple[int, int, int, int]] = {}

    def dfs(node: int) -> tuple[int, int] | None:
        color[node] = 1
        for ni, src, outer, inner in graph.get(node, []):
            if color.get(ni, 0) == 1:
                # cycle: from ni back to node forms one direction.
                cycle_rows: set[int] = set()
                cycle_rows.add(src)
                cycle_rows |= connecting_rows(node, outer)
                cycle_rows |= connecting_rows(ni, inner)
                # walk back from node through parent_in_dfs until we hit ni.
                cur = node
                while cur != ni:
                    pn, ps, po, pi_ = parent_in_dfs[cur]
                    cycle_rows.add(ps)
                    cycle_rows |= connecting_rows(pn, po)
                    cycle_rows |= connecting_rows(cur, pi_)
                    cur = pn
                # convert to sorted list
                # Note we use the rows tuple as the result via scope hack:
                cycle_rows_holder.append(cycle_rows)
                return None
            if color.get(ni, 0) == 0:
                parent_in_dfs[ni] = (node, src, outer, inner)
                if dfs(ni) is None and cycle_rows_holder:
                    return None
        color[node] = 2
        return None

    cycle_rows_holder: list[set[int]] = []
    for node in list(graph):
        if color.get(node, 0) == 0:
            dfs(node)
            if cycle_rows_holder:
                return ("strict_cycle", sorted(cycle_rows_holder[0]))
    return ("ok", [])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--solver", choices=["z3", "pysat"], default="z3")
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--timeout-ms", type=int, default=None)
    parser.add_argument(
        "--all-models",
        action="store_true",
        help="Iteratively block found models and report total surviving incidence patterns (only useful for small n).",
    )
    parser.add_argument(
        "--max-models",
        type=int,
        default=1,
        help="Maximum number of models to enumerate.",
    )
    args = parser.parse_args()

    p = WitnessProblem(args.n)
    print(
        f"[encode] n={args.n} options/center={len(p.options[0])} "
        f"total_options={p.num_options()} solver={args.solver}"
    )

    payload: dict[str, object] = {
        "n": args.n,
        "encoding_version": "v2_vertex_witness",
        "solver": args.solver,
        "filters": [
            "exactly_one_row_per_center",
            "pair_intersection_cap_2_with_cyclic_cross",
            "adjacent_rows_share_at_most_one",
            "witness_pair_indegree_cap_2",
            "vertex_circle_rank_collapse_and_strict_edge_inequality",
        ]
        if args.solver == "z3"
        else [
            "exactly_one_row_per_center",
            "pair_intersection_cap_2_with_cyclic_cross",
            "adjacent_rows_share_at_most_one",
            "witness_pair_indegree_cap_2",
            "vertex_circle_v_check_via_cegar_no_good_loop",
        ],
        "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "UNSAT proves: under these necessary combinatorial filters, no n vertex-witness assignment exists.",
            "SAT returns an incidence pattern; geometric realizability is NOT implied by SAT.",
            "Independent reviewer audit required before any theorem-style claim.",
        ],
    }

    if args.solver == "z3":
        import z3

        s, x, row_idx, rank = encode_z3(p, timeout_ms=args.timeout_ms)
        models: list[list[list[int]]] = []
        start = time.perf_counter()
        result_str = "unknown"
        for attempt in range(args.max_models):
            res = s.check()
            if res == z3.sat:
                m = s.model()
                rows: list[list[int]] = []
                for i in range(args.n):
                    k = m.eval(row_idx[i]).as_long()
                    rows.append(list(p.options[i][k]))
                models.append(rows)
                # Independent verification of the V status:
                vc_status = vertex_circle_status_pattern(p, rows)
                if vc_status != "ok":
                    print(f"  [warn] model has vc_status={vc_status} (encoding bug?)")
                if attempt == 0:
                    result_str = "sat"
                # Block this assignment to find another one (for --all-models).
                if not args.all_models:
                    break
                block = []
                for i in range(args.n):
                    k = m.eval(row_idx[i]).as_long()
                    block.append(z3.Not(row_idx[i] == k))
                s.add(z3.Or(block))
            elif res == z3.unsat:
                if attempt == 0:
                    result_str = "unsat"
                break
            else:
                if attempt == 0:
                    result_str = "unknown"
                break
        elapsed = time.perf_counter() - start
        print(f"[z3] result={result_str} models_found={len(models)} elapsed={elapsed:.2f}s")
        payload["result"] = result_str
        payload["elapsed_seconds"] = round(elapsed, 3)
        payload["models_found"] = len(models)
        if models:
            payload["sample_pattern"] = models[0]
            payload["all_patterns"] = models if args.all_models else [models[0]]

    else:
        cnf, x = encode_pysat(p)
        print(
            f"[pysat] vars={cnf.next_id - 1} clauses={len(cnf.clauses)}"
        )
        from pysat.solvers import Cadical195

        solver = Cadical195()
        for clause in cnf.clauses:
            solver.add_clause(clause)
        start = time.perf_counter()

        # CEGAR loop: pysat finds an R/P/A/W-satisfying model; we check the V
        # constraint via the post-hoc `vertex_circle_status_pattern` function.
        # If V fails, block the exact full assignment (a no-good clause over
        # the 9 chosen x_{i,k} variables) and re-solve.  Repeat until either
        # UNSAT (proves no R/P/A/W/V model exists) or a V-OK model.
        survivors: list[list[list[int]]] = []
        rejected = 0
        rejection_status: dict[str, int] = {}
        timeout_s = (args.timeout_ms / 1000.0) if args.timeout_ms else None
        result_str = "unknown"
        last_pattern: list[list[int]] | None = None
        iteration = 0
        progress_every = 10
        last_log_t = start
        while True:
            iteration += 1
            elapsed_now = time.perf_counter() - start
            if timeout_s is not None and elapsed_now >= timeout_s:
                result_str = "timeout"
                break
            if iteration % progress_every == 0 or (time.perf_counter() - last_log_t) > 30:
                last_log_t = time.perf_counter()
                print(
                    f"[pysat-cegar] iter={iteration} elapsed={elapsed_now:.1f}s"
                    f" v_ok={len(survivors)} v_rejected={rejected}"
                    f" status={rejection_status}",
                    flush=True,
                )
            res = solver.solve()
            if res is False:
                result_str = "unsat" if not survivors else "sat"
                break
            if res is None:
                result_str = "unknown"
                break
            model = solver.get_model()
            truth = {abs(lit): (lit > 0) for lit in model}
            rows = []
            chosen_x_vars: list[int] = []
            for i in range(args.n):
                chosen = None
                for k in range(len(p.options[i])):
                    if truth.get(x[(i, k)]):
                        chosen = k
                        break
                rows.append(list(p.options[i][chosen]) if chosen is not None else [])
                if chosen is not None:
                    chosen_x_vars.append(x[(i, chosen)])
            last_pattern = rows
            # First: V check (vertex-circle status)
            vc_status, blame_rows = minimal_v_failure_rows(p, rows)
            extra_filter_status: str | None = None
            if vc_status == "ok":
                # Run additional combinatorial filters from incidence_filters.
                from erdos97.incidence_filters import (
                    crossing_bisector_violations,
                    odd_forced_perpendicular_cycle,
                    phi4_rectangle_trap_certificates,
                )

                cyc_viol = crossing_bisector_violations(rows, list(range(args.n)))
                odd_cyc = odd_forced_perpendicular_cycle(rows)
                rect = phi4_rectangle_trap_certificates(rows, list(range(args.n)))
                if cyc_viol:
                    extra_filter_status = "crossing_bisector"
                elif odd_cyc is not None:
                    extra_filter_status = "odd_perpendicular_cycle"
                elif rect:
                    extra_filter_status = "phi4_rectangle_trap"

            if vc_status == "ok" and extra_filter_status is None:
                survivors.append(rows)
                if not args.all_models:
                    result_str = "sat"
                    break
                solver.add_clause([-v for v in chosen_x_vars])
            else:
                rejected += 1
                full_status = vc_status if vc_status != "ok" else extra_filter_status
                rejection_status[full_status] = rejection_status.get(full_status, 0) + 1
                if vc_status != "ok" and blame_rows:
                    clause_vars: list[int] = []
                    for ridx in blame_rows:
                        for k in range(len(p.options[ridx])):
                            if truth.get(x[(ridx, k)]):
                                clause_vars.append(x[(ridx, k)])
                                break
                    solver.add_clause([-v for v in clause_vars])
                else:
                    # For extra filters we don't yet compute minimal blame,
                    # so block the full assignment.
                    solver.add_clause([-v for v in chosen_x_vars])
        elapsed = time.perf_counter() - start
        print(
            f"[pysat-cegar] result={result_str} v_ok={len(survivors)} v_rejected={rejected}"
            f" rejection_breakdown={rejection_status} elapsed={elapsed:.2f}s"
        )
        payload["result"] = result_str
        payload["v_ok_count"] = len(survivors)
        payload["v_rejected_count"] = rejected
        payload["v_rejection_breakdown"] = rejection_status
        payload["elapsed_seconds"] = round(elapsed, 3)
        if survivors:
            payload["sample_pattern"] = survivors[0]
            if args.all_models:
                payload["all_patterns"] = survivors
        elif last_pattern is not None and result_str in ("timeout", "unknown"):
            payload["last_v_failed_pattern"] = last_pattern
        solver.delete()

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        print(f"[encode] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
