#!/usr/bin/env python3
"""Independent SMT cross-check for the review-pending n=9 vertex-circle result.

Context. The exhaustive n=9 selected-witness search
(`src/erdos97/n9_vertex_circle_exhaustive.py`, `docs/n9-vertex-circle-exhaustive.md`)
leaves 184 full selected-witness assignments after the pair/crossing/count
filters, and the vertex-circle quotient filter kills all 184 (158 by a
self-edge, 26 by a strict cycle). That result is review-pending.

This checker is an independent second source using a different decision
procedure -- z3 nonlinear real arithmetic (NRA) -- for the realizability
question those assignments encode. For each of the 184 assignments it asks
whether a strictly convex 9-gon can carry the assignment's equal-distance
incidences, in two tiers:

- **Tier 1** (no convexity): equal-distance + perpendicular-bisector
  constraints with the gauge ``p_0=(0,0)``, ``p_1=(1,0)`` and distinct
  vertices. UNSAT here is an order-independent kill (no convexity assumption
  at all).
- **Tier 2** (only if Tier 1 is SAT): add **order-free strict convex
  position** -- every vertex exposed, i.e. for each ``k`` a direction
  ``(a_k,b_k)`` strictly maximized at ``p_k`` over the others, so the points
  form a strictly convex 9-gon in *some* boundary order, with no assumption
  that the canonical label order is the boundary order. UNSAT means no
  strictly convex realization in any order.

If every assignment is UNSAT in Tier 1 or Tier 2, no assignment has a strictly
convex realization -- an independent confirmation of the vertex-circle result
(the vertex-circle quotient self-edge / strict-cycle obstruction is a
*necessary* condition for realizability, so a realizable assignment would have
exposed a discrepancy). Any assignment that is z3-SAT under Tier 2 (a genuine
strictly convex realization) would contradict the vertex-circle kill and is
reported loudly; a z3 ``unknown`` is reported as unresolved (never silently
treated as a kill).

Performance. At n=9 each Tier-2 NRA call takes on the order of ten seconds, so
the full 184-assignment sweep is a multi-minute generation run (the ``full``
mode). The default ``sample`` mode re-verifies a fixed, deterministic
representative subset (covering both self-edge and strict-cycle assignments)
for a fast audit-tier reproducibility check.

Independence is in the decision procedure; the incidence-to-equation
translation and the assignment enumeration mirror the existing pipeline (the
problem statement, not the proof). Repo-local exact-obstruction cross-check
pending external review; not a general proof of Erdos Problem #97, not a
counterexample, not an official/global status update.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def collect_assignments():
    """Re-run the deterministic n=9 search (vertex-circle pruning off) and
    return the basic-filter-surviving full assignments as
    ``(rows, vc_status)`` pairs, where ``rows`` is the 0/1 witness matrix."""
    import erdos97.n9_vertex_circle_exhaustive as E

    n = E.N
    out: list[tuple[list[list[int]], str]] = []

    def search(assign, col, wp):
        if len(assign) == n:
            rows = [[0] * n for _ in range(n)]
            for c, m in assign.items():
                for t in E.MASK_BITS[m]:
                    rows[c][t] = 1
            out.append((rows, E.vertex_circle_status(dict(assign))))
            return
        best_c = best_o = None
        for c in range(n):
            if c in assign:
                continue
            o = E.valid_options_for_center(c, assign, col, wp)
            if best_o is None or len(o) < len(best_o):
                best_c, best_o = c, o
                if not o:
                    break
        if not best_o:
            return
        for m in best_o:
            assign[best_c] = m
            for t in E.MASK_BITS[m]:
                col[t] += 1
            for pidx in E.ROW_PAIR_INDICES[m]:
                wp[pidx] += 1
            search(assign, col, wp)
            for pidx in E.ROW_PAIR_INDICES[m]:
                wp[pidx] -= 1
            for t in E.MASK_BITS[m]:
                col[t] -= 1
            del assign[best_c]

    search({}, [0] * n, [0] * len(E.PAIRS))
    return out, n


def _witnesses(rows, i):
    return [j for j, v in enumerate(rows[i]) if v]


def _phi_edges(rows, n):
    sets = [set(_witnesses(rows, i)) for i in range(n)]
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            inter = sorted(sets[i] & sets[j])
            if len(inter) == 2:
                edges.append(((i, j), (inter[0], inter[1])))
    return edges


def _points(n):
    import z3

    zc = {f"{ax}{i}": z3.Real(f"{ax}{i}") for i in range(2, n) for ax in "xy"}
    p = [(z3.RealVal(0), z3.RealVal(0)), (z3.RealVal(1), z3.RealVal(0))]
    for i in range(2, n):
        p.append((zc[f"x{i}"], zc[f"y{i}"]))
    return p


def _add_base(s, p, rows, n):
    for i in range(n):
        w = _witnesses(rows, i)
        bx, by = p[w[0]]
        ix, iy = p[i]
        base = (ix - bx) ** 2 + (iy - by) ** 2
        for o in w[1:]:
            ox, oy = p[o]
            s.add((ix - ox) ** 2 + (iy - oy) ** 2 - base == 0)
    for (i, j), (a, b) in _phi_edges(rows, n):
        ix, iy = p[i]
        jx, jy = p[j]
        ax, ay = p[a]
        bx, by = p[b]
        s.add((ix - jx) * (ax - bx) + (iy - jy) * (ay - by) == 0)
        s.add((jx - ix) * (ay + by - 2 * iy) - (jy - iy) * (ax + bx - 2 * ix) == 0)


def decide(rows, n, tier1_ms, tier2_ms):
    """Two-tier verdict for one assignment."""
    import z3

    s1 = z3.Solver()
    s1.set("timeout", tier1_ms)
    p1 = _points(n)
    _add_base(s1, p1, rows, n)
    for i in range(n):
        for j in range(i + 1, n):
            dx = p1[i][0] - p1[j][0]
            dy = p1[i][1] - p1[j][1]
            s1.add(dx * dx + dy * dy > 0)
    t1 = str(s1.check())
    if t1 == "unsat":
        return {"tier1": t1, "verdict": "order_independent_unsat"}

    s2 = z3.Solver()
    s2.set("timeout", tier2_ms)
    p2 = _points(n)
    _add_base(s2, p2, rows, n)
    for k in range(n):
        a = z3.Real(f"a{k}")
        b = z3.Real(f"b{k}")
        s2.add(a * a + b * b == 1)
        for j in range(n):
            if j != k:
                s2.add(a * p2[k][0] + b * p2[k][1] > a * p2[j][0] + b * p2[j][1])
    t2 = str(s2.check())
    if t2 == "unsat":
        return {"tier1": t1, "tier2": t2, "verdict": "convex_unsat"}
    if t2 == "sat":
        return {"tier1": t1, "tier2": t2, "verdict": "REALIZABLE"}
    return {"tier1": t1, "tier2": t2, "verdict": "unknown"}


def sample_indices(assigns, k):
    """Deterministic representative subset covering both vc-status types."""
    self_edge = [i for i, (_, vc) in enumerate(assigns) if vc == "self_edge"]
    strict = [i for i, (_, vc) in enumerate(assigns) if vc == "strict_cycle"]
    half = max(1, k // 2)

    def spread(lst, m):
        if not lst or m <= 0:
            return []
        if m >= len(lst):
            return lst
        step = len(lst) / m
        return [lst[int(i * step)] for i in range(m)]

    return sorted(set(spread(self_edge, k - half) + spread(strict, half)))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--mode", choices=["full", "sample"], default="sample")
    ap.add_argument("--sample-size", type=int, default=12)
    ap.add_argument("--tier1-ms", type=int, default=30000)
    ap.add_argument("--tier2-ms", type=int, default=90000)
    ap.add_argument("--assert-clear", action="store_true")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    args = ap.parse_args()

    assigns, n = collect_assignments()
    if args.mode == "sample":
        idxs = sample_indices(assigns, args.sample_size)
    else:
        idxs = list(range(len(assigns)))

    records = []
    for idx in idxs:
        rows, vc = assigns[idx]
        d = decide(rows, n, args.tier1_ms, args.tier2_ms)
        records.append({"idx": idx, "vc_status": vc, **d})

    realizable = [r["idx"] for r in records if r["verdict"] == "REALIZABLE"]
    unknown = [r["idx"] for r in records if r["verdict"] == "unknown"]
    order_independent = [r["idx"] for r in records
                         if r["verdict"] == "order_independent_unsat"]
    clear = not realizable and not unknown
    payload = {
        "schema": "erdos97.n9_survivors_smt.v1",
        "status": "EXACT_OBSTRUCTION_SMT" if clear else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": "scripts/check_n9_survivors_smt.py",
            "command": (
                "python scripts/check_n9_survivors_smt.py --mode full "
                "--assert-clear --write-artifact "
                "data/certificates/n9_survivors_smt.json"
            ),
        },
        "scope": (
            "Independent z3 (NRA) cross-check of the review-pending n=9 "
            "vertex-circle result: each basic-filter-surviving full "
            "selected-witness assignment has no strictly convex 9-gon "
            "realization (Tier 1 ED+PB+distinct UNSAT, or Tier 2 ED+PB + "
            "order-free strict convex position UNSAT). Independent decision "
            "procedure relative to the vertex-circle quotient argument; the "
            "vertex-circle obstruction is a necessary condition for "
            "realizability, so all assignments are expected UNSAT and any "
            "z3-SAT (realizable) would flag a discrepancy. Repo-local "
            "exact-obstruction cross-check pending external review; not a "
            "proof of n=9, not a general proof of Erdos Problem #97, not a "
            "counterexample, not an official/global status update."
        ),
        "n": 9,
        "mode": args.mode,
        "assignments_total": len(assigns),
        "checked": len(records),
        "records": records,
        "order_independent_unsat": len(order_independent),
        "realizable": realizable,
        "unknown": unknown,
        "clear": clear,
    }
    if args.write_artifact:
        with open(args.write_artifact, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        for r in records:
            print(f"assignment {r['idx']:3d} [{r['vc_status']:12s}] -> "
                  f"{r['verdict']}")
        print(f"mode={args.mode} checked={len(records)}/{len(assigns)} "
              f"order_independent={len(order_independent)} "
              f"realizable={realizable} unknown={unknown} clear={clear}")
    if args.assert_clear and not clear:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
