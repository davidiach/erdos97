"""A2 lane: strict-convexity moment/SOS probe on n=8 class 14 (the convexity-only
survivor) -- the n=8 analogue of the repo P24 metric-only negative control.

Goal
----
Class 14 is the unique post-cyclic n=8 survivor whose metric equality system
(perpendicular-bisector + equal-distance, gauge p0=(0,0), p1=(1,0)) has genuine
real solutions: a finite set of 4 points, each a square/diamond on 4 labels with
the other 4 labels strictly interior. So its incompatibility with a strictly
convex polygon comes ONLY from convexity. This mirrors P24: metric conditions
hold, convexity fails.

We test, for a FIXED compatible cyclic order ``order``:

  * EQUALITY-ONLY moment relaxation: expect FEASIBLE (variety nonempty).
  * EQUALITY + edge-side convexity localizers: expect INFEASIBLE.

The convexity encoding is the plan-recommended "all other vertices strictly on
one side of every directed edge":  for each edge (order[i], order[i+1]) and each
non-edge vertex j,  sign * orient(p_a, p_b, p_j) >= 0  (closed cone; the 4
variety points already violate it strictly, so closed suffices to exclude them).
We run both orientation signs (CCW and CW); a strictly convex polygon in this
cyclic order would satisfy one of them.

A numeric INFEASIBLE here is NUMERICAL_EVIDENCE that the convexity-augmented
system is empty for that order. The exact statement (no compatible order realises
any branch as strictly convex) is established separately and exactly in
``a2_class14_convexity_exact`` below by evaluating the edge-side polynomials at
the 4 exact variety points.

This file claims NO general proof and NO counterexample.
"""
from __future__ import annotations

import json
import sys

import sympy as sp

sys.path.insert(0, "scripts/exploration")
import a2_sos_infeasibility as A  # noqa: E402

DATA = "certificates/n8_exact_analysis.json"
GAUGE_VARS = [f"{c}{k}" for k in range(2, 8) for c in ("x", "y")]


def _syms():
    return {name: sp.Symbol(name) for name in GAUGE_VARS}


def _points(syms):
    P = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    for k in range(2, 8):
        P[k] = (syms[f"x{k}"], syms[f"y{k}"])
    return P


def orient(A_, B_, C_):
    return (B_[0] - A_[0]) * (C_[1] - A_[1]) - (B_[1] - A_[1]) * (C_[0] - A_[0])


def load_class14():
    with open(DATA) as fh:
        d = json.load(fh)
    syms = _syms()
    gens = [syms[name] for name in GAUGE_VARS]
    s = d["systems_for_remaining_after_cyclic"]["14"]
    eqs = []
    for pe in s["phi_edges_with_perpendicular_bisector_equations"]:
        eqs.append(sp.sympify(pe["dot_equation"], locals=syms))
        eqs.append(sp.sympify(pe["bisector_midpoint_equation"], locals=syms))
    for ed in s["full_equal_distance_equations"]:
        eqs.append(sp.sympify(ed["equation"], locals=syms))
    return gens, [sp.expand(e) for e in eqs], s, d


def edge_side_inequalities(syms, order, sign):
    """sign * orient(p_a,p_b,p_j) for every edge (a,b) and non-edge vertex j."""
    P = _points(syms)
    ineqs = []
    m = len(order)
    for i in range(m):
        a, b = order[i], order[(i + 1) % m]
        for j in order:
            if j == a or j == b:
                continue
            ineqs.append(sp.expand(sign * orient(P[a], P[b], P[j])))
    return ineqs


def consecutive_turn_inequalities(syms, order, sign):
    """Smaller convexity proxy: sign * orient of consecutive triples only."""
    P = _points(syms)
    ineqs = []
    m = len(order)
    for i in range(m):
        a, b, c = order[i], order[(i + 1) % m], order[(i + 2) % m]
        ineqs.append(sp.expand(sign * orient(P[a], P[b], P[c])))
    return ineqs


# --------------------------------------------------------------------------- #
# EXACT layer: evaluate edge-side polynomials at the 4 exact variety points    #
# --------------------------------------------------------------------------- #
def class14_convexity_exact():
    """Exactly verify: no compatible cyclic order (CCW or CW) makes any of the 4
    exact equality-variety branches strictly convex under the full edge-side test.

    Returns dict with per-branch results. Pure sympy, exact; no floating point.
    """
    _, _, s, d = load_class14()
    orders = s["compatible_cyclic_orders"]
    branches = d["contradictions"]["class_14"]["solution_branches"]

    def point_map(b):
        P = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
        for k in range(2, 8):
            P[k] = (sp.sympify(b[f"x{k}"]), sp.sympify(b[f"y{k}"]))
        return P

    def strictly_convex(P, order, sign):
        m = len(order)
        for i in range(m):
            a, b = order[i], order[(i + 1) % m]
            for j in order:
                if j == a or j == b:
                    continue
                v = sp.simplify(sign * orient(P[a], P[b], P[j]))
                if not (v > 0):  # need strictly positive
                    return False
        return True

    per_branch = []
    all_excluded = True
    for bi, b in enumerate(branches):
        P = point_map(b)
        realizable = any(
            strictly_convex(P, o, sgn) for o in orders for sgn in (1, -1)
        )
        per_branch.append({"branch": bi, "strictly_convex_in_some_order": realizable})
        if realizable:
            all_excluded = False
    return {
        "num_branches": len(branches),
        "num_compatible_orders": len(orders),
        "per_branch": per_branch,
        "no_branch_strictly_convex": all_excluded,
        "trust_label": "EXACT_OBSTRUCTION" if all_excluded else "NO_OBSTRUCTION",
    }


# --------------------------------------------------------------------------- #
# NUMERIC moment-relaxation probe                                              #
# --------------------------------------------------------------------------- #
def moment_probe(order, sign, d=2, conv="edge", solver="CLARABEL"):
    """Run two moment relaxations for class 14 under one order:
    equality-only and equality+convexity. Return their statuses.
    """
    gens, eqs, _, _ = load_class14()
    syms = {str(g): g for g in gens}
    if conv == "edge":
        ineqs = edge_side_inequalities(syms, order, sign)
    else:
        ineqs = consecutive_turn_inequalities(syms, order, sign)

    eq_only = A.PolySystem(name="n8_class14_eq", gens=gens, equalities=eqs)
    eq_conv = A.PolySystem(
        name="n8_class14_eq_conv", gens=gens, equalities=eqs, inequalities=ineqs
    )
    r_eq = A.solve_primal(eq_only, d, solver=solver)
    r_conv = A.solve_primal(eq_conv, d, solver=solver)
    return {
        "order": order,
        "sign": sign,
        "moment_order_d": d,
        "convexity_encoding": conv,
        "num_inequalities": len(ineqs),
        "equality_only_status": r_eq["status"],
        "equality_plus_convexity_status": r_conv["status"],
        "moment_matrix_size": r_conv["moment_matrix_size"],
    }


if __name__ == "__main__":
    print("=== EXACT class-14 convexity obstruction (4 variety points) ===")
    exact = class14_convexity_exact()
    print(json.dumps(exact, indent=2))
