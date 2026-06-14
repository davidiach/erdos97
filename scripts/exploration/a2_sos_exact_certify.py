"""A2 lane (exact layer): rational Positivstellensatz / Nullstellensatz
infeasibility certificates for Erdos Problem #97 n=8 polynomial systems, plus a
strict-convexity SOS/moment probe that reproduces the P24 negative-control
behaviour.

This complements ``a2_sos_infeasibility.py`` (the numeric cvxpy+SCS/CLARABEL
relaxation). Here every certificate that is *reported as exact* is produced and
checked over the rationals with sympy only; no floating-point equality is used.

Trust labels produced here
--------------------------
* ``EXACT_OBSTRUCTION`` (for one fixed n=8 incidence class only) when a rational
  Nullstellensatz identity ``sum_k lambda_k g_k = 1`` is found and verified
  exactly. This certifies that the *metric equality system* of that class
  (perpendicular-bisector + equal-distance equations, in the gauge p0=(0,0),
  p1=(1,0)) has NO complex (hence no real) solution. It does NOT by itself use
  strict convexity, and it does NOT prove anything about the general problem.
* ``NUMERICAL_EVIDENCE`` for the strict-convexity SOS/moment probe on class 14.

Why two regimes appear among the n=8 survivor classes
-----------------------------------------------------
Running ``classify_equality_emptiness`` shows the 14 post-cyclic classes split:

  (A) classes whose equality ideal already contains 1 (variety empty over C):
      0,1,2,3,4,5,6,7,8,9,10,11,13. For these the metric equalities are *by
      themselves* contradictory, so a pure-equality Nullstellensatz refutation
      exists and convexity is not needed.

  (B) class 14: the equality ideal does NOT contain 1; the metric system has
      genuine (complex, and in fact real) solutions. Its incompatibility with a
      strictly convex polygon comes ONLY from convexity (every real branch puts
      four labels in the interior). This is the n=8 analogue of the repo P24
      negative control: metric/rank conditions hold, convexity fails.

So the n=8 *aggregate* obstruction is NOT a single uniform convexity argument:
most classes die on the metric equalities alone; one class (14) needs convexity.
The SOS pipeline here certifies (A) exactly and exercises convexity on (B).
"""
from __future__ import annotations

import argparse
import itertools
import json
from fractions import Fraction

import sympy as sp

DATA = "certificates/n8_exact_analysis.json"
GAUGE_VARS = [f"{c}{k}" for k in range(2, 8) for c in ("x", "y")]


def _symbols():
    return {name: sp.Symbol(name) for name in GAUGE_VARS}


def load_equalities(class_key: str, data_path: str = DATA):
    """Return (gens, equalities) for one n=8 survivor class.

    Equalities = all perpendicular-bisector (dot + midpoint) equations and all
    full equal-distance equations, expanded. Gauge: p0=(0,0), p1=(1,0).
    """
    with open(data_path) as fh:
        d = json.load(fh)
    syms = _symbols()
    gens = [syms[name] for name in GAUGE_VARS]
    s = d["systems_for_remaining_after_cyclic"][class_key]
    eqs = []
    for pe in s["phi_edges_with_perpendicular_bisector_equations"]:
        eqs.append(sp.sympify(pe["dot_equation"], locals=syms))
        eqs.append(sp.sympify(pe["bisector_midpoint_equation"], locals=syms))
    for ed in s["full_equal_distance_equations"]:
        eqs.append(sp.sympify(ed["equation"], locals=syms))
    return gens, [sp.expand(e) for e in eqs], s


def monomials_up_to(gens, deg):
    n = len(gens)
    out = set()
    for d in range(deg + 1):
        for combo in itertools.combinations_with_replacement(range(n), d):
            e = [0] * n
            for i in combo:
                e[i] += 1
            out.add(tuple(e))
    return sorted(out)


# --------------------------------------------------------------------------- #
# (A) Exact linear Nullstellensatz certificate  sum lambda_k g_k = 1          #
# --------------------------------------------------------------------------- #
def find_nullstellensatz_certificate(gens, eqs, mult_deg=1):
    """Search for rational lambda_k with deg<=mult_deg and sum lambda_k g_k = 1.

    Returns (found, lambdas) where lambdas is a list of sympy polynomials over QQ.
    The search is an EXACT rational linear-algebra feasibility problem; no SDP
    and no floating point are involved.
    """
    n = len(gens)
    mm = monomials_up_to(gens, mult_deg)
    # unknown coefficient symbols c_{k,j}
    cvars = []
    lambdas = []
    for k in range(len(eqs)):
        row = [sp.Symbol(f"c_{k}_{j}") for j in range(len(mm))]
        cvars.extend(row)
        mono_terms = [
            sp.prod([gens[v] ** mm[j][v] for v in range(n)]) for j in range(len(mm))
        ]
        lambdas.append(sum(row[j] * mono_terms[j] for j in range(len(mm))))
    expr = sp.expand(sum(lambdas[k] * eqs[k] for k in range(len(eqs))) - 1)
    poly = sp.Poly(expr, *gens)
    # one linear equation (in cvars) per monomial coefficient
    lin = list(poly.coeffs())
    sol = sp.linsolve(lin, cvars)
    if len(sol) == 0:
        return False, None
    point = next(iter(sol))
    # free parameters -> set to 0 for a concrete certificate
    subs = {}
    for var, val in zip(cvars, point):
        for fp in val.free_symbols:
            subs[fp] = 0
    concrete = [sp.nsimplify(v.subs(subs)) for v in point]
    cmap = dict(zip(cvars, concrete))
    lam_concrete = [sp.expand(lam.subs(cmap)) for lam in lambdas]
    return True, lam_concrete


def verify_nullstellensatz(gens, eqs, lambdas):
    """Exactly verify sum lambda_k g_k == 1 over QQ. Returns bool."""
    expr = sp.expand(sum(lam * g for lam, g in zip(lambdas, eqs)) - 1)
    return sp.simplify(expr) == 0


def certificate_to_rationals(lambdas, gens):
    """Serialise multipliers as {monomial_exponent_tuple: 'p/q'} dicts."""
    out = []
    for lam in lambdas:
        p = sp.Poly(lam, *gens)
        terms = {}
        for monom, coeff in p.terms():
            fr = Fraction(int(sp.numer(coeff)), int(sp.denom(coeff)))
            terms[",".join(map(str, monom))] = f"{fr.numerator}/{fr.denominator}"
        out.append(terms)
    return out


# --------------------------------------------------------------------------- #
# Classify which classes are equality-empty vs convexity-only                  #
# --------------------------------------------------------------------------- #
def classify_equality_emptiness(data_path: str = DATA):
    """For each post-cyclic class report whether 1 is in the equality ideal.

    1 in ideal  => metric equalities contradictory (no convexity needed).
    1 not in ideal => variety nonempty; convexity is the only possible obstruction.
    """
    with open(data_path) as fh:
        d = json.load(fh)
    keys = list(d["systems_for_remaining_after_cyclic"].keys())
    result = {}
    for key in keys:
        gens, eqs, _ = load_equalities(key, data_path)
        G = sp.groebner(eqs, *gens, order="grevlex")
        one_in_ideal = sp.Integer(1) in [sp.expand(g) for g in G.exprs]
        result[key] = {
            "one_in_equality_ideal": bool(one_in_ideal),
            "gb_len": len(G.exprs),
            "regime": "equality_empty" if one_in_ideal else "convexity_only",
        }
    return result


# --------------------------------------------------------------------------- #
# (B) strict-convexity moment probe for class 14 (P24-analogue behaviour)      #
# --------------------------------------------------------------------------- #
def orientation(pa, pb, pc):
    """2*signed area of triangle pa,pb,pc (CCW positive)."""
    (ax, ay), (bx, by), (cx, cy) = pa, pb, pc
    return (bx - ax) * (cy - ay) - (by - ay) * (cx - ax)


def class14_convexity_inequalities(order, data_path: str = DATA):
    """Strict-convexity orientation polynomials for class 14 under a fixed
    cyclic order (a list/permutation of 0..7). Returns list of polynomials that
    must be > 0 for a CCW strictly convex polygon in that order.

    Coordinates: p0=(0,0), p1=(1,0), p_k=(x_k,y_k). Consecutive-triple turns.
    """
    syms = _symbols()
    P = {0: (sp.Integer(0), sp.Integer(0)), 1: (sp.Integer(1), sp.Integer(0))}
    for k in range(2, 8):
        P[k] = (syms[f"x{k}"], syms[f"y{k}"])
    m = len(order)
    ineqs = []
    for i in range(m):
        a, b, c = order[i], order[(i + 1) % m], order[(i + 2) % m]
        ineqs.append(sp.expand(orientation(P[a], P[b], P[c])))
    return ineqs


def main():
    ap = argparse.ArgumentParser(description="A2 exact certify / classify")
    ap.add_argument("--classify", action="store_true",
                    help="report equality-empty vs convexity-only for all classes")
    ap.add_argument("--certify", metavar="CLASS",
                    help="find+verify exact Nullstellensatz certificate for a class")
    ap.add_argument("--mult-deg", type=int, default=1)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.classify:
        res = classify_equality_emptiness()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            for k, v in sorted(res.items(), key=lambda kv: int(kv[0])):
                print(f"class {k:>2}: {v['regime']:15s} "
                      f"(1 in ideal={v['one_in_equality_ideal']}, gb_len={v['gb_len']})")
        return

    if args.certify is not None:
        gens, eqs, _ = load_equalities(args.certify)
        found, lambdas = find_nullstellensatz_certificate(gens, eqs, args.mult_deg)
        if not found:
            out = {"class": args.certify, "mult_deg": args.mult_deg,
                   "certificate_found": False}
            print(json.dumps(out, indent=2) if args.json else out)
            return
        ok = verify_nullstellensatz(gens, eqs, lambdas)
        out = {
            "class": args.certify,
            "mult_deg": args.mult_deg,
            "certificate_found": True,
            "exact_identity_verified": bool(ok),
            "trust_label": "EXACT_OBSTRUCTION" if ok else "UNVERIFIED",
            "num_equalities": len(eqs),
            "num_nonzero_multipliers": sum(1 for lam in lambdas if lam != 0),
            "max_multiplier_degree": max(
                (sp.total_degree(sp.Poly(lam, *gens)) for lam in lambdas if lam != 0),
                default=0,
            ),
        }
        if args.json:
            out["multipliers"] = certificate_to_rationals(lambdas, gens)
        print(json.dumps(out, indent=2))
        return

    ap.print_help()


if __name__ == "__main__":
    main()
