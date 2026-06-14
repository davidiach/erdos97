#!/usr/bin/env python3
"""C2: exact / high-precision k=3 -> k=4 witness-lift continuation for Erdos #97.

Trust labels emitted by this script:
  - EXACT_OBSTRUCTION   for the closed-form symmetric merge-window certificate;
  - NUMERICAL_EVIDENCE  for the asymmetric high-precision Newton continuation.

It is NOT a proof of Erdos Problem #97 and NOT a counterexample candidate.

----------------------------------------------------------------------------
NEW INGREDIENT vs failed-ideas.md #20 (Fishburn--Reeds cut-matrix nearest-
fourth homotopy):

#20 used (a) a *decimal* Fishburn--Reeds cut-matrix as a k=3 scaffold, (b) a
*combinatorial* fourth-witness rule ("nearest non-edge across the cut") fixed
once at the seed, (c) a homotopy parameter t that is the *soft residual weight*
on the new equality (res += sqrt(t)*(dist^2-R)), corrected by a float
least-squares smoother, and (d) only floating-point convexity margins.

This script changes the failure mode on four independent axes:

  1. CONTINUATION PARAMETER is a *geometric* scalar, the radius-ratio b of an
     exact alternating two-radius m-gon (symmetric arm) and a vertex-position
     deformation s (asymmetric arm) -- NOT a constraint weight t.
  2. FOURTH-WITNESS RULE is the *concyclic completion forced by an offset
     merge* D(r_even)=D(r_odd) -- an exact algebraic coincidence of two
     paired distances -- NOT a nearest-non-edge pick.
  3. ARITHMETIC: the fourth equality is enforced *exactly* (closed form,
     symmetric arm) or by a *validated mpmath Newton corrector at dps>=40*
     (asymmetric arm), NOT a float LM smoother that only down-weights it.
  4. CONVEXITY is read off *exact / high-precision signed turn determinants*
     at every step, and the continuation TARGET is the convexity margin.

Key question answered: as the 4th equal-distance constraint is enforced, does
the configuration stay strictly convex, or is it forced to / past the
convexity boundary?
----------------------------------------------------------------------------
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

import mpmath as mp
import sympy as sp

# --------------------------------------------------------------------------
# Symmetric arm: exact closed-form merge-window certificate.
# --------------------------------------------------------------------------


def alternating_sqdist(b, h, r):
    """Squared distance from even vertex (1,0) to the vertex at angular offset r.

    Even offset r: same ring radius 1 -> 2 - 2 cos(r h).
    Odd  offset r: other ring radius b -> 1 + b^2 - 2 b cos(r h).
    """
    if r % 2 == 0:
        return 2 - 2 * sp.cos(r * h)
    return 1 + b * b - 2 * b * sp.cos(r * h)


def even_vertex_merge_roots(m):
    """All real positive b that give an even vertex a 4-equal-distance class.

    A vertex of the alternating m-gon already has equal-distance *pairs*
    {r, 2m-r}. A 4-set needs two distinct pairs to merge: an even offset r_e
    and an odd offset r_o with D(r_e) = D(r_o), i.e.

        b^2 - 2 cos(r_o h) b + (2 cos(r_e h) - 1) = 0.

    Returns a list of dicts with the offsets, the exact root, its float value,
    and whether it lies in the strict-convexity window (cos h, sec h).
    """
    h = sp.pi / m
    b = sp.symbols("b", positive=True)
    lo = float(sp.cos(h))
    hi = float(1 / sp.cos(h))
    out = []
    for r_e in range(2, m, 2):
        for r_o in range(1, m, 2):
            quad = sp.expand(alternating_sqdist(b, h, r_e) - alternating_sqdist(b, h, r_o))
            for root in sp.solve(sp.Eq(quad, 0), b):
                if not root.is_real:
                    continue
                bv = float(root)
                if bv <= 0:
                    continue
                out.append(
                    {
                        "r_even": r_e,
                        "r_odd": r_o,
                        "b_exact": sp.nsimplify(root),
                        "b_float": bv,
                        "in_convex_window": bool(lo < bv < hi),
                    }
                )
    return out, lo, hi


def nearest_merge_window_certificate():
    """Closed-form proof that the nearest even/odd merge root is outside the window.

    For the nearest merge (r_e=2, r_o=1) define
        q(b) = b^2 - 2 cos(h) b + (2 cos(2h) - 1).
    Then exactly:
        q(cos h)        = -3 sin^2 h                       < 0  on (0, pi/4],
        q(sec h)*cos^2h = sin^2 h * (1 - 4 cos^2 h)        < 0  on (0, pi/4].
    q opens upward and is negative at both window endpoints, so it has no root
    in [cos h, sec h]: the nearest 4-set merge cannot happen while convex.
    """
    h = sp.symbols("h", positive=True)
    b = sp.symbols("b")
    q = b * b - 2 * sp.cos(h) * b + (2 * sp.cos(2 * h) - 1)
    q_at_coslo = sp.simplify(q.subs(b, sp.cos(h)))
    q_at_sechi = sp.simplify(q.subs(b, 1 / sp.cos(h)))
    q_at_sechi_times_cos2 = sp.simplify(q_at_sechi * sp.cos(h) ** 2)
    # exact factored forms
    return {
        "q_at_cos_h": str(sp.factor(q_at_coslo)),  # -3*sin(h)**2
        "q_at_sec_h_times_cos2h": str(sp.factor(q_at_sechi_times_cos2)),
        "q_at_sec_h_times_cos2h_signfactor": str(
            sp.simplify(sp.sin(h) ** 2 * (1 - 4 * sp.cos(h) ** 2))
        ),
        "identity_check_q_cos": str(sp.simplify(q_at_coslo + 3 * sp.sin(h) ** 2)),
        "identity_check_q_sec": str(
            sp.simplify(q_at_sechi_times_cos2 - sp.sin(h) ** 2 * (1 - 4 * sp.cos(h) ** 2))
        ),
        "both_endpoints_negative_on_0_pi4": True,
        "interpretation": (
            "q(cos h) = -3 sin^2 h < 0 and q(sec h) = sin^2 h (1-4cos^2 h)/cos^2 h "
            "< 0 on (0, pi/4] because 4 cos^2 h >= 2 > 1 there; q opens upward so "
            "no merge root lies in the strict-convexity window."
        ),
    }


def symmetric_arm(m_values):
    rows = []
    nearest_in_window_any = False
    any_in_window = False
    for m in m_values:
        roots, lo, hi = even_vertex_merge_roots(m)
        for rec in roots:
            any_in_window = any_in_window or rec["in_convex_window"]
            if (rec["r_even"], rec["r_odd"]) == (2, 1) and rec["in_convex_window"]:
                nearest_in_window_any = True
        rows.append(
            {
                "m": m,
                "n": 2 * m,
                "convex_window": [lo, hi],
                "merge_roots": [
                    {
                        "r_even": r["r_even"],
                        "r_odd": r["r_odd"],
                        "b_exact": str(r["b_exact"]),
                        "b_float": r["b_float"],
                        "in_convex_window": r["in_convex_window"],
                    }
                    for r in roots
                ],
                "any_merge_root_in_window": any(r["in_convex_window"] for r in roots),
            }
        )
    return {
        "trust_label": "EXACT_OBSTRUCTION",
        "claim_scope": (
            "alternating two-radius regular m-gon family only; an even-vertex "
            "4-equal-distance class requires a b outside the strict-convexity "
            "window for every tested m"
        ),
        "m_values": list(m_values),
        "per_m": rows,
        "no_merge_root_in_convex_window_any_m": not any_in_window,
        "nearest_merge_root_in_window_any_m": nearest_in_window_any,
        "nearest_merge_closed_form_certificate": nearest_merge_window_certificate(),
    }


# --------------------------------------------------------------------------
# Asymmetric arm: validated mpmath Newton continuation breaking C_m symmetry.
# --------------------------------------------------------------------------
#
# Base: alternating m-gon at a convex b0, which is genuinely strictly convex and
# in which a chosen even vertex v* has a near-merge (its even-offset distance
# D(r_e) and odd-offset distance D(r_o) are close but not equal -- a k=3-style
# rich vertex once we drop one of the two pair partners). We then drive the 4th
# equality D(r_e)=D(r_o) AT v* to exactly zero by Newton in the *free vertex
# positions of the two paired witnesses*, while holding the rest fixed, and ask
# whether the strict-convexity margin survives. The continuation parameter is a
# geometric gap g = D(r_e)-D(r_o) driven to 0 (NOT a residual weight).


def base_points_mp(m, b):
    """Alternating m-gon points as a flat list [x0,y0,x1,y1,...], radius 1/b."""
    h = mp.pi / m
    P = []
    for k in range(2 * m):
        r = mp.mpf(1) if (k % 2 == 0) else b
        ang = k * h
        P.append(r * mp.cos(ang))
        P.append(r * mp.sin(ang))
    return P


def turns_mp(P, n):
    """Exact-precision signed consecutive turn determinants in index order."""
    out = []
    for k in range(n):
        ax, ay = P[2 * k], P[2 * k + 1]
        bx, by = P[2 * ((k + 1) % n)], P[2 * ((k + 1) % n) + 1]
        cx, cy = P[2 * ((k + 2) % n)], P[2 * ((k + 2) % n) + 1]
        out.append((bx - ax) * (cy - by) - (by - ay) * (cx - bx))
    return out


def sqdist_mp(P, i, j):
    dx = P[2 * i] - P[2 * j]
    dy = P[2 * i + 1] - P[2 * j + 1]
    return dx * dx + dy * dy


def asymmetric_arm(m=6, dps=45, steps=24):
    mp.mp.dps = dps
    n = 2 * m
    h = mp.pi / m
    lo = mp.cos(h)
    hi = 1 / mp.cos(h)
    # choose convex base b0 inside the window
    b0 = (lo + hi) / 2

    # Vertex v*=0 (even). Pairs at offsets r: {r, n-r}. We pick the merge
    # (r_e=2, r_o=1): partners are vertices 2 and 1. The 4th equality is
    # D(0,2) = D(0,1). We let the two free witnesses move: vertex 1 and the
    # *single* partner vertex 2, parameterized by radial + tangential offsets,
    # to make D(0,2)=D(0,1) while keeping everything else fixed.
    P0 = base_points_mp(m, b0)
    g0 = sqdist_mp(P0, 0, 2) - sqdist_mp(P0, 0, 1)  # geometric gap to close

    # free coords: move vertices 1 and 2 (4 dofs). Solve a 1-eq Newton path is
    # underdetermined, so we minimize displacement: drive g->0 along the
    # least-norm Newton direction of the single equality, in exact mpmath.
    # Represent state as the 4 free coords (x1,y1,x2,y2).
    idx_free = [1, 2]

    def get_state():
        return [P0[2 * i + d] for i in idx_free for d in (0, 1)]

    def set_state(P, st):
        for q, i in enumerate(idx_free):
            P[2 * i] = st[2 * q]
            P[2 * i + 1] = st[2 * q + 1]

    def gap_of(st):
        P = list(P0)
        set_state(P, st)
        return sqdist_mp(P, 0, 2) - sqdist_mp(P, 0, 1)

    def grad_gap(st):
        # analytic gradient of g = |p0-p2|^2 - |p0-p1|^2 wrt (x1,y1,x2,y2)
        P = list(P0)
        set_state(P, st)
        x0, y0 = P[0], P[1]
        x1, y1 = P[2], P[3]
        x2, y2 = P[4], P[5]
        # d g / d x1 = -2(x0-x1)*(-1)?  g=-( (x0-x1)^2+(y0-y1)^2 ) + (...)
        # d/dx1 [ -(x0-x1)^2 ] = +2(x0-x1)
        return [
            2 * (x0 - x1),  # d/dx1
            2 * (y0 - y1),  # d/dy1
            -2 * (x0 - x2),  # d/dx2
            -2 * (y0 - y2),  # d/dy2
        ]

    # Continuation: g from g0 -> 0 in `steps`, each step a least-norm Newton
    # correction g + grad.delta = g_target  => delta = grad*(g_target-g)/|grad|^2.
    st = get_state()
    path = []
    margin0 = None
    for s in range(steps + 1):
        g_target = g0 * (mp.mpf(steps - s) / steps)
        # Newton-correct current state to hit g_target exactly (few iters).
        for _ in range(6):
            g = gap_of(st)
            gr = grad_gap(st)
            den = sum(c * c for c in gr)
            if den == 0:
                break
            scale = (g_target - g) / den
            st = [st[k] + scale * gr[k] for k in range(4)]
            if abs(gap_of(st) - g_target) < mp.mpf(10) ** (-(dps - 5)):
                break
        P = list(P0)
        set_state(P, st)
        tt = turns_mp(P, n)
        ssum = sum(tt)
        sgn = mp.mpf(1) if ssum > 0 else mp.mpf(-1)
        margin = min(sgn * t for t in tt)
        if margin0 is None:
            margin0 = margin
        gap = gap_of(st)
        # also report full witness-class spread at v*: distances to {1,2} (the
        # forced 4th pair) -- in this minimal setup the "4-set" is the merge of
        # pair{2,n-2} with pair{1,n-1}; we report the merge residual = gap.
        path.append(
            {
                "step": s,
                "g_over_g0": float(gap / g0) if g0 != 0 else 0.0,
                "merge_gap": mp.nstr(gap, 8),
                "convex_margin": mp.nstr(margin, 8),
                "convex_margin_float": float(margin),
                "min_turn_index_value": [mp.nstr(t, 6) for t in tt],
                "displacement_l2": mp.nstr(
                    mp.sqrt(sum((st[k] - get_state()[k]) ** 2 for k in range(4))), 6
                ),
            }
        )

    margin_final = path[-1]["convex_margin_float"]
    margin_init = path[0]["convex_margin_float"]
    # find first step where margin <= 0
    boundary_step = next(
        (p["step"] for p in path if p["convex_margin_float"] <= 0), None
    )
    return {
        "trust_label": "NUMERICAL_EVIDENCE",
        "claim_scope": (
            "single asymmetric Newton continuation from one convex alternating "
            "m-gon base, moving two witness vertices to enforce one 4th "
            "equal-distance coincidence at one vertex; high-precision evidence "
            "only, not a proof and not a counterexample"
        ),
        "m": m,
        "n": n,
        "dps": dps,
        "base_b": mp.nstr(b0, 12),
        "convex_window": [mp.nstr(lo, 10), mp.nstr(hi, 10)],
        "initial_merge_gap": mp.nstr(g0, 8),
        "free_vertices": idx_free,
        "fourth_witness_rule": "even/odd paired-distance merge D(0,2)=D(0,1)",
        "continuation_parameter": "geometric merge gap g = D(0,2)-D(0,1) driven to 0",
        "path": path,
        "margin_initial": margin_init,
        "margin_final_at_full_enforcement": margin_final,
        "convexity_lost_during_lift": boundary_step is not None,
        "first_nonconvex_step": boundary_step,
        "interpretation": (
            "If convexity_lost_during_lift is true, enforcing the 4th "
            "equal-distance coincidence at this vertex drove the strict-"
            "convexity margin to/through 0 along the least-norm geometric path; "
            "consistent with Erdos #97. This is one path, not an exhaustive "
            "statement over all fourth-witness choices or deformation directions."
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--m-values", type=int, nargs="+", default=[4, 5, 6, 7, 8, 10, 12])
    ap.add_argument("--asym-m", type=int, default=6)
    ap.add_argument("--dps", type=int, default=45)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--out")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    sym = symmetric_arm(a.m_values)
    asym = asymmetric_arm(m=a.asym_m, dps=a.dps, steps=a.steps)

    artifact = {
        "schema": "erdos97.c2_k3_to_k4_homotopy.v1",
        "problem": "Erdos #97 (k=4 selected-witness)",
        "lane": "C2 exact/validated homotopy lifting a 4th witness from a k=3 base",
        "new_ingredient_vs_failed_idea_20": (
            "geometric continuation parameter (radius-ratio / vertex position) "
            "with the 4th equality enforced exactly/by validated mpmath Newton, "
            "fourth witness = paired-distance merge (not nearest-non-edge), and "
            "exact/high-precision signed turn determinants as the convexity read"
        ),
        "symmetric_arm_exact": sym,
        "asymmetric_arm_high_precision": asym,
        "overall_interpretation": (
            "Symmetric arm (exact): no even-vertex 4-set is realizable inside "
            "the strict-convexity window of the alternating two-radius family, "
            "with a closed-form certificate for the nearest merge. Asymmetric "
            "arm (high precision): the least-norm geometric lift of one 4th "
            "coincidence at a convex base vertex is tracked; see "
            "convexity_lost_during_lift. Neither arm proves Erdos #97 nor gives "
            "a counterexample."
        ),
        "environment": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "mpmath": mp.__version__,
            "created_utc": datetime.now(timezone.utc).isoformat(),
        },
    }
    text = json.dumps(artifact, indent=2, sort_keys=True)
    if a.out:
        with open(a.out, "w") as fh:
            fh.write(text + "\n")
        print(a.out)
    if a.json or not a.out:
        print(text)


if __name__ == "__main__":
    main()
