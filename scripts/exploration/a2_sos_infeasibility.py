"""A2 lane: Sum-of-Squares / moment (Lasserre) infeasibility certificates for
Erdos Problem #97 polynomial systems.

Trust labels in this lane:
  - On KNOWN-infeasible n=8 survivor systems: validation of the pipeline.
    A positive infeasibility detection is NUMERICAL_EVIDENCE unless the dual
    SOS certificate is rationalised and exactly verified, in which case it is
    an EXACT_OBSTRUCTION (for that fixed incidence class only).
  - On an n=9 frontier incidence assignment: NUMERICAL_EVIDENCE / FAILED_ROUTE.

This file contains NO proof of the general problem and claims NO counterexample.

Method (moment / Lasserre relaxation, primal infeasibility detection)
---------------------------------------------------------------------
Given equality constraints g_k(x) = 0 (k=1..m) in variables x in R^N we build the
order-d moment relaxation:

  find a pseudo-moment vector y indexed by monomials of degree <= 2d with
      y_0 = 1
      M_d(y) >= 0                      (moment matrix PSD)
      L_y(g_k * x^alpha) = 0           for all alpha with deg <= 2d - deg g_k

If this SDP is INFEASIBLE then the real variety {g_k = 0} is empty: the system has
no real solution. (Any real solution x* would yield the genuine moment vector
y_alpha = (x*)^alpha which satisfies all constraints, so feasibility is necessary
for solvability.) Detecting SDP infeasibility numerically is NUMERICAL_EVIDENCE.

Dual / Positivstellensatz view (the actual certificate)
-------------------------------------------------------
Primal infeasibility is dual to existence of an SOS refutation

      sum_k lambda_k(x) * g_k(x) + sigma(x) + 1 = 0,    sigma SOS, deg <= 2d.

We solve this dual feasibility SDP directly (it is the certificate we want), then
attempt to round lambda_k, sigma to exact rationals and verify the polynomial
identity exactly with sympy. An exactly verified identity is a rigorous
infeasibility certificate for that fixed system.

We use only sympy (exact), numpy and cvxpy+SCS/CLARABEL (numeric SDP).
"""
from __future__ import annotations

import itertools
import json
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Sequence

import sympy as sp


# --------------------------------------------------------------------------- #
# Monomial / polynomial bookkeeping (exponent-tuple representation over QQ)    #
# --------------------------------------------------------------------------- #
Exp = tuple  # exponent tuple, one entry per variable


def poly_from_sympy(expr: sp.Expr, gens: Sequence[sp.Symbol]) -> dict[Exp, Fraction]:
    """Convert a sympy polynomial to {exponent_tuple: Fraction}."""
    p = sp.Poly(sp.expand(expr), *gens)
    out: dict[Exp, Fraction] = {}
    for monom, coeff in p.terms():
        out[tuple(monom)] = Fraction(int(sp.numer(coeff)), int(sp.denom(coeff)))
    return out


def poly_mul_monomial(p: dict[Exp, Fraction], m: Exp) -> dict[Exp, Fraction]:
    return {tuple(a + b for a, b in zip(e, m)): c for e, c in p.items()}


def monomials_up_to(n_vars: int, deg: int) -> list[Exp]:
    """All exponent tuples in n_vars variables of total degree <= deg, graded order."""
    mons: list[Exp] = []
    for d in range(deg + 1):
        # compositions of d into n_vars parts
        for combo in itertools.combinations_with_replacement(range(n_vars), d):
            e = [0] * n_vars
            for i in combo:
                e[i] += 1
            mons.append(tuple(e))
    # dedupe preserving order
    seen = set()
    out = []
    for m in mons:
        if m not in seen:
            seen.add(m)
            out.append(m)
    return out


# --------------------------------------------------------------------------- #
# Problem container                                                           #
# --------------------------------------------------------------------------- #
@dataclass
class PolySystem:
    name: str
    gens: list[sp.Symbol]
    equalities: list[sp.Expr]  # g_k = 0
    inequalities: list[sp.Expr] = field(default_factory=list)  # h_j >= 0 (optional)

    @property
    def n_vars(self) -> int:
        return len(self.gens)


# --------------------------------------------------------------------------- #
# Moment relaxation (PRIMAL infeasibility detection)                          #
# --------------------------------------------------------------------------- #
def build_moment_relaxation(sysm: PolySystem, d: int):
    """Return cvxpy Problem testing primal moment feasibility at order d.

    We seek a moment vector y (variable) with:
      y[0]=1, M_d(y) PSD, L_y(g_k * x^a)=0 for all a with deg<=2d-deg g_k,
      and (if inequalities present) localizing matrices PSD.

    If the problem is infeasible => no real solution to the equality system.
    """
    import cvxpy as cp

    N = sysm.n_vars
    half_basis = monomials_up_to(N, d)  # rows/cols of moment matrix
    s = len(half_basis)
    # full monomial index up to degree 2d (all that appear)
    idx: dict[Exp, int] = {}

    def midx(e: Exp) -> int:
        if e not in idx:
            idx[e] = len(idx)
        return idx[e]

    # ensure the constant comes first
    midx(tuple([0] * N))
    # moment matrix entry (i,j) maps to monomial alpha_i+alpha_j
    M_entry = [[None] * s for _ in range(s)]
    for i in range(s):
        for j in range(s):
            e = tuple(a + b for a, b in zip(half_basis[i], half_basis[j]))
            M_entry[i][j] = midx(e)

    # equality localizing constraints (degree-2d truncation)
    eq_rows: list[dict[int, Fraction]] = []
    for g in sysm.equalities:
        pg = poly_from_sympy(g, sysm.gens)
        dg = max((sum(e) for e in pg), default=0)
        mult_mons = monomials_up_to(N, 2 * d - dg) if 2 * d - dg >= 0 else []
        for a in mult_mons:
            row: dict[int, Fraction] = {}
            for e, c in poly_mul_monomial(pg, a).items():
                row[midx(e)] = row.get(midx(e), Fraction(0)) + c
            eq_rows.append(row)

    n_moments = len(idx)
    y = cp.Variable(n_moments)
    constraints = [y[0] == 1]
    # moment matrix
    Msym = cp.bmat([[y[M_entry[i][j]] for j in range(s)] for i in range(s)])
    constraints.append(Msym >> 0)
    # equality rows
    for row in eq_rows:
        constraints.append(
            cp.sum([float(c) * y[k] for k, c in row.items()]) == 0
        )
    # localizing matrices for inequalities h_j >= 0
    for h in sysm.inequalities:
        ph = poly_from_sympy(h, sysm.gens)
        dh = max((sum(e) for e in ph), default=0)
        dloc = d - (dh + 1) // 2
        if dloc < 0:
            continue
        loc_basis = monomials_up_to(N, dloc)
        sl = len(loc_basis)
        Lentry = [[None] * sl for _ in range(sl)]
        for i in range(sl):
            for j in range(sl):
                acc: dict[int, Fraction] = {}
                base = tuple(a + b for a, b in zip(loc_basis[i], loc_basis[j]))
                for e, c in poly_mul_monomial(ph, base).items():
                    acc[midx(e)] = acc.get(midx(e), Fraction(0)) + c
                Lentry[i][j] = acc
        Lsym = cp.bmat(
            [
                [cp.sum([float(c) * y[k] for k, c in Lentry[i][j].items()]) for j in range(sl)]
                for i in range(sl)
            ]
        )
        constraints.append(Lsym >> 0)

    prob = cp.Problem(cp.Minimize(0), constraints)
    return prob, dict(n_moments=n_moments, moment_matrix_size=s, n_eq_rows=len(eq_rows))


def solve_primal(sysm: PolySystem, d: int, solver: str = "CLARABEL", verbose=False):
    import cvxpy as cp

    prob, info = build_moment_relaxation(sysm, d)
    try:
        prob.solve(solver=solver, verbose=verbose)
    except cp.error.SolverError as exc:  # pragma: no cover - solver dependent
        return dict(status=f"SOLVER_ERROR:{exc}", **info)
    return dict(status=prob.status, value=prob.value, **info)


# --------------------------------------------------------------------------- #
# DUAL SOS refutation: sum lambda_k g_k + sigma + 1 = 0, sigma SOS            #
# --------------------------------------------------------------------------- #
def build_sos_refutation(sysm: PolySystem, d: int):
    """cvxpy problem for the Positivstellensatz infeasibility certificate.

    Variables:
      - Gram matrix Q >= 0 of size len(basis_d), giving sigma = z^T Q z (SOS),
        z = monomials up to degree d.
      - For each equality g_k, free coefficients of lambda_k (deg <= 2d-deg g_k).
    Identity enforced coefficient-by-coefficient up to degree 2d:
      sum_k lambda_k g_k + sigma + 1 == 0.
    Feasibility (Q>=0 + linear identity) => certificate of infeasibility.
    Returns the cvxpy problem plus a callback to read out exact-ready data.
    """
    import cvxpy as cp

    N = sysm.n_vars
    basis = monomials_up_to(N, d)
    sb = len(basis)
    Q = cp.Variable((sb, sb), symmetric=True)

    # accumulate identity polynomial as dict[exp] -> cvxpy expression
    poly_terms: dict[Exp, list] = {}

    def add_term(e: Exp, val):
        poly_terms.setdefault(e, []).append(val)

    # sigma = sum_{i,j} Q[i,j] * z_i z_j
    for i in range(sb):
        for j in range(sb):
            e = tuple(a + b for a, b in zip(basis[i], basis[j]))
            add_term(e, Q[i, j])

    # lambda_k * g_k
    lambda_vars = []
    for g in sysm.equalities:
        pg = poly_from_sympy(g, sysm.gens)
        dg = max((sum(e) for e in pg), default=0)
        lam_mons = monomials_up_to(N, max(0, 2 * d - dg))
        lvec = cp.Variable(len(lam_mons))
        lambda_vars.append((lvec, lam_mons))
        for t_i, a in enumerate(lam_mons):
            for e, c in poly_mul_monomial(pg, a).items():
                add_term(e, float(c) * lvec[t_i])

    # constant +1
    add_term(tuple([0] * N), 1.0)

    constraints = [Q >> 0]
    for e, terms in poly_terms.items():
        constraints.append(cp.sum(terms) == 0)

    prob = cp.Problem(cp.Minimize(0), constraints)
    meta = dict(basis=basis, Q=Q, lambda_vars=lambda_vars, sos_basis_size=sb)
    return prob, meta


def solve_sos(sysm: PolySystem, d: int, solver: str = "CLARABEL", verbose=False):
    import cvxpy as cp

    prob, meta = build_sos_refutation(sysm, d)
    try:
        prob.solve(solver=solver, verbose=verbose)
    except cp.error.SolverError as exc:  # pragma: no cover
        return dict(status=f"SOLVER_ERROR:{exc}"), meta
    res = dict(status=prob.status, value=prob.value, sos_basis_size=meta["sos_basis_size"])
    return res, meta


# --------------------------------------------------------------------------- #
# helpers                                                                      #
# --------------------------------------------------------------------------- #
def parse_n8_class(class_key: str, data_path: str = "certificates/n8_exact_analysis.json"):
    """Build PolySystem for an n=8 survivor class from the exact-analysis JSON.

    Variables: x2,y2,...,x7,y7 (gauge p0=(0,0), p1=(1,0)).
    Equalities: all PB dot+bisector equations and all full equal-distance equations.
    """
    with open(data_path) as fh:
        d = json.load(fh)
    sysd = d["systems_for_remaining_after_cyclic"][class_key]
    syms = {}
    for k in range(2, 8):
        syms[f"x{k}"] = sp.Symbol(f"x{k}")
        syms[f"y{k}"] = sp.Symbol(f"y{k}")
    gens = [syms[f"{c}{k}"] for k in range(2, 8) for c in ("x", "y")]
    local = dict(syms)
    eqs = []
    for pe in sysd["phi_edges_with_perpendicular_bisector_equations"]:
        eqs.append(sp.sympify(pe["dot_equation"], locals=local))
        eqs.append(sp.sympify(pe["bisector_midpoint_equation"], locals=local))
    for ed in sysd["full_equal_distance_equations"]:
        eqs.append(sp.sympify(ed["equation"], locals=local))
    return PolySystem(name=f"n8_class{sysd['class_id']}", gens=gens, equalities=eqs)


if __name__ == "__main__":  # pragma: no cover - manual driver
    import sys

    which = sys.argv[1] if len(sys.argv) > 1 else "5"
    d = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    sysm = parse_n8_class(which)
    print(f"system {sysm.name}: {sysm.n_vars} vars, {len(sysm.equalities)} equalities")
    pr = solve_primal(sysm, d)
    print("PRIMAL moment relaxation:", pr)
    sr, _ = solve_sos(sysm, d)
    print("DUAL SOS refutation:", sr)
