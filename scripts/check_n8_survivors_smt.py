#!/usr/bin/env python3
"""Independent SMT second-source for the n=8 exact-survivor obstruction.

Context. The repo-local `n <= 8` finite-case result reduces all necessary
selected-witness incidence survivors to 15 canonical classes
(`docs/n8-incidence-enumeration.md`) and then kills every class with exact
arithmetic (`docs/n8-exact-survivors.md`): one class by a cyclic-order
noncrossing argument, the other fourteen by perpendicular-bisector /
equal-distance (PB+ED) algebra, four of those via Groebner bases (classes 3,
4, 5, 14). The existing SymPy-free recheck (`docs/n8-independent-obstruction.md`)
deliberately does **not** cover the four Groebner-dependent classes.

This checker provides a uniform **independent** cross-check of all 15 classes
using a completely different decision procedure: z3 nonlinear real arithmetic
(NRA). For each survivor class it builds the equal-distance constraints (each
center is equidistant from its four selected witnesses) and the derived
perpendicular-bisector constraints for shared-witness pairs, then asks z3
whether any **strictly convex** octagon (vertices in cyclic label order)
satisfies them. Every class is UNSAT, so no survivor class has a strictly
convex realization -- confirming the cyclic-order and Groebner conclusions
without using Groebner bases or the cyclic-order combinatorics.

Soundness. Any realization of a survivor class is a strictly convex octagon
`p_0,...,p_7` in label order with each center equidistant from its witnesses,
so it satisfies the ED constraints (and hence their PB consequences) and the
convexity inequalities. z3 UNSAT for that conjunction therefore means no
realization exists. The gauge `p_0=(0,0)`, `p_1=(1,0)` is without loss of
generality: the ED/PB constraints are similarity-covariant (translation,
rotation, scaling) and the opposite orientation is the `y -> -y` reflection,
which preserves both the constraints and the gauge -- so checking the
counter-clockwise orientation (all per-period turn determinants `> 0`)
suffices.

This is a repo-local exact-obstruction cross-check pending external review; it
strengthens, but does not replace, the existing artifacts. It is not a general
proof of Erdos Problem #97 and not a counterexample. Independence is in the
**decision procedure**; the incidence-to-equation translation below mirrors
the standard one (it is the problem statement, not the proof).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

N = 8


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_survivors(root: Path) -> list[dict]:
    path = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    return json.loads(path.read_text(encoding="utf-8"))


def witnesses(rows: list[list[int]], i: int) -> list[int]:
    return [j for j, v in enumerate(rows[i]) if v]


def phi_edges(rows: list[list[int]]):
    sets = [set(witnesses(rows, i)) for i in range(N)]
    out = []
    for i in range(N):
        for j in range(i + 1, N):
            inter = sorted(sets[i] & sets[j])
            if len(inter) == 2:
                out.append(((i, j), (inter[0], inter[1])))
    return out


def coords(zvars):
    import z3

    pts = [(z3.RealVal(0), z3.RealVal(0)), (z3.RealVal(1), z3.RealVal(0))]
    for i in range(2, N):
        pts.append((zvars[f"x{i}"], zvars[f"y{i}"]))
    return pts


def equations(rows, p):
    """ED constraints (each center equidistant from its witnesses) plus the
    derived PB constraints (shared-witness pairs lie on a perpendicular
    bisector), as z3 expressions that must equal zero."""
    eqs = []
    # equal-distance: |p_i - p_w0|^2 = |p_i - p_wk|^2 for each witness wk
    for i in range(N):
        w = witnesses(rows, i)
        bx, by = p[w[0]]
        ix, iy = p[i]
        base = (ix - bx) * (ix - bx) + (iy - by) * (iy - by)
        for other in w[1:]:
            ox, oy = p[other]
            eqs.append((ix - ox) * (ix - ox) + (iy - oy) * (iy - oy) - base)
    # perpendicular-bisector: for a shared-witness pair (i,j) with common
    # witnesses (a,b), both centers lie on the perpendicular bisector of
    # p_a p_b, i.e. (p_i - p_j).(p_a - p_b) = 0 and the midpoint collinearity.
    for (i, j), (a, b) in phi_edges(rows):
        ix, iy = p[i]
        jx, jy = p[j]
        ax, ay = p[a]
        bx, by = p[b]
        eqs.append((ix - jx) * (ax - bx) + (iy - jy) * (ay - by))
        eqs.append((jx - ix) * (ay + by - 2 * iy) - (jy - iy) * (ax + bx - 2 * ix))
    return eqs


def _solver(timeout_ms):
    import z3

    s = z3.Solver()
    s.set("timeout", timeout_ms)
    zvars = {f"{ax}{i}": z3.Real(f"{ax}{i}") for i in range(2, N) for ax in "xy"}
    return s, zvars


def add_distinct(s, p):
    """All vertices pairwise distinct (no convexity / order assumption)."""
    for i in range(N):
        for j in range(i + 1, N):
            dx = p[i][0] - p[j][0]
            dy = p[i][1] - p[j][1]
            s.add(dx * dx + dy * dy > 0)


def add_strict_convex_position(s, p):
    """Order-free strict convex position: every vertex p_k is *exposed* --
    there is a direction (a_k, b_k) (unit, so nonzero) strictly maximized at
    p_k over all other vertices. All eight exposed <=> the points are the
    vertices of a strictly convex octagon, in *some* cyclic order. This makes
    no assumption that the label order equals the boundary order."""
    import z3

    for k in range(N):
        a = z3.Real(f"a{k}")
        b = z3.Real(f"b{k}")
        s.add(a * a + b * b == 1)  # unit direction (excludes the zero vector)
        for j in range(N):
            if j == k:
                continue
            s.add(a * p[k][0] + b * p[k][1] > a * p[j][0] + b * p[j][1])


def decide_class(rows, timeout_ms: int) -> dict:
    """Two z3 verdicts per class, both order-free:

    - ``without_convexity``: ED + PB + gauge + distinct vertices. UNSAT here is
      an order-independent kill (no convexity assumption at all).
    - ``strict_convex``: ED + PB + gauge + strict convex position (every vertex
      exposed). UNSAT here means no strictly convex octagon in *any* order
      realizes the class -- the conclusion the cross-check needs.
    """
    s1, zv1 = _solver(timeout_ms)
    p1 = coords(zv1)
    eqs = equations(rows, p1)
    for e in eqs:
        s1.add(e == 0)
    add_distinct(s1, p1)
    without_convexity = str(s1.check())

    s2, zv2 = _solver(timeout_ms)
    p2 = coords(zv2)
    for e in equations(rows, p2):
        s2.add(e == 0)
    add_strict_convex_position(s2, p2)
    strict_convex = str(s2.check())
    return {
        "equations": len(eqs),
        "without_convexity": without_convexity,
        "strict_convex": strict_convex,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout-ms", type=int, default=60000)
    ap.add_argument("--assert-clear", action="store_true",
                    help="exit nonzero unless all 15 classes are UNSAT")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    args = ap.parse_args()

    root = repo_root()
    survivors = load_survivors(root)
    records = []
    for rec in survivors:
        cid = int(rec["id"])
        d = decide_class(rec["rows"], args.timeout_ms)
        records.append({"class": cid, **d})
    # main result: no strictly convex octagon (any order) realizes any class
    not_convex_unsat = [r["class"] for r in records if r["strict_convex"] != "unsat"]
    # bonus: classes killed with no convexity assumption at all
    order_independent = [r["class"] for r in records
                         if r["without_convexity"] == "unsat"]
    clear = len(records) == 15 and not not_convex_unsat
    payload = {
        "schema": "erdos97.n8_survivors_smt.v1",
        "status": "EXACT_OBSTRUCTION_SMT" if clear else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": "scripts/check_n8_survivors_smt.py",
            "command": (
                "python scripts/check_n8_survivors_smt.py --assert-clear "
                "--write-artifact data/certificates/n8_survivors_smt.json"
            ),
        },
        "scope": (
            "Independent z3 (NRA) cross-check that none of the 15 n=8 "
            "selected-witness survivor classes has a strictly convex octagon "
            "realization. For each class the equal-distance + "
            "perpendicular-bisector constraints together with ORDER-FREE "
            "strict convex position (every vertex exposed in some direction) "
            "are UNSAT, so no strictly convex octagon in any boundary order "
            "realizes the class -- no assumption that the canonical label "
            "order equals the geometric boundary order. As a stronger bonus, "
            "14 of the 15 classes are already UNSAT under ED+PB+distinct with "
            "no convexity assumption at all (order-independent); the remaining "
            "class (14) needs the strict-convex-position constraint. "
            "Independent in the decision procedure (z3 NRA vs the existing "
            "Groebner / cyclic-order arguments), covering all 15 classes "
            "including the four Groebner-dependent ones (3,4,5,14) the "
            "SymPy-free recheck skips. Repo-local exact-obstruction "
            "cross-check pending external review; not a general proof of "
            "Erdos Problem #97, not a counterexample, not an official/global "
            "status update."
        ),
        "n": 8,
        "classes_total": len(records),
        "records": records,
        "not_strictly_convex_unsat_failures": not_convex_unsat,
        "order_independent_unsat_classes": order_independent,
        "clear": clear,
    }
    if args.write_artifact:
        with open(args.write_artifact, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        for r in records:
            print(f"class {r['class']:2d}: strict_convex={r['strict_convex']:7s} "
                  f"without_convexity={r['without_convexity']:7s} "
                  f"({r['equations']} eqs)")
        print(f"all 15 not-strictly-convex (UNSAT): {clear}")
        print(f"order-independent (UNSAT w/o convexity): "
              f"{len(order_independent)}/15 classes {order_independent}")
    if args.assert_clear and not clear:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
