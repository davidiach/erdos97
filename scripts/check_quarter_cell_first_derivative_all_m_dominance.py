#!/usr/bin/env python3
"""All-m dominance closure of the nine first-derivative quarter-cell cells.

Context: the three-orbit quarter-cell signed-band split
(`docs/quarter-cell-signed-band-preflight.md`) reduces the remaining
``m = 0 mod 4`` quarter cells to twelve signed band cells; the named missing
lemma per cell is that a fixed killer turn ``F`` is negative throughout the
strict cell. The three mixed-derivative cells are closed for all ``m >= 8``
by `scripts/check_quarter_cell_mixed_cells_all_m_smt.py`. This checker
closes the remaining NINE first-derivative cells for all ``m >= 8`` at once,
upgrading them from the finite ``m = 8, 12, 16`` interval certificate
(`docs/quarter-cell-derivative-certificate.md`).

Method (dominance): with ``T = 2h``, ``h = pi/m``, band variables
``0 < d, e < delta`` (``sin(delta) = omega = sin(h)^2/(2 cos h)``), each
cell's required derivative component ``F_c`` (``F_d`` or ``F_e``) satisfies:

1. **Exact corner identity** (sympy, m-uniform): ``F_c(T, 0, 0) = -A`` for
   the eight cells requiring ``F_c < 0`` and ``+A`` for ``HH_y-_z-``
   (requiring ``F_c > 0``), where ``A = sin T + cos T - 1``. Moreover
   ``A = 2 sh (ch - sh)`` exactly (``sh = sin h``, ``ch = cos h``), which is
   positive and of order ``sh`` for ``h in (0, pi/8]``.
2. **Certified Lipschitz bound** (interval arithmetic, outward-rounded
   mpmath ``iv`` at 80-bit precision): over the fixed box
   ``T in [0, pi/4]``, ``d, e in [0, 2/25]``, which contains every band
   square (step 3),

       sup |dF_c/dd| + sup |dF_c/de|  <=  M = 4.

   By the mean value theorem along the two-leg path ``(0,0) -> (d,0) ->
   (d,e)``, ``|F_c(T,d,e) - F_c(T,0,0)| <= d*sup|dF_c/dd| +
   e*sup|dF_c/de| <= delta * M``.
3. **Band bounds** (z3 + exact rationals): on the domain
   ``ch^2 + sh^2 = 1``, ``sh > 0``, ``ch > 0``, ``2ch^2 - 1 >= 2 sh ch``
   (i.e. ``T <= pi/4``, i.e. ``m >= 8``): ``ch > sh`` (so ``A > 0``),
   ``omega <= 397/5000`` (so, using ``arcsin(x) <= x / sqrt(1 - x^2)``,
   ``delta <= delta_bar := omega/sqrt(1-omega^2) <= 2/25``: the band square
   sits inside the interval box), and the **dominance combination**

       M^2 * sh^2  <  4 (ch - sh)^2 (4 ch^2 - sh^4),

   which is exactly ``(M * delta_bar)^2 < A^2 (cleared)``, hence
   ``M * delta >= |F_c - corner|`` can never reach ``A = |corner|``.
4. **Conclusion** (elementary, in the note): ``F_c`` has the corner's
   strict sign on the whole closed band square for every ``T in (0,
   pi/4]``. Combined with each cell's exact vanishing-boundary identity
   (``F(0,e) = 0``, ``F(d,0) = 0``, or diagonal ``F(d,d) = 0``, verified
   symbolically here) and one-variable integration along the cell's stored
   proof rule, the killer turn is strictly negative throughout each strict
   cell -- for every ``m >= 8``.

Controls: the z3 domain is SAT (non-empty); the dominance combination with
``M = 6`` is SAT (the inequality fails past ``M ~ 5.2``, so the margin is
real but bounded); a deterministic finite-difference lattice ties every
symbolic derivative component to the raw geometric turns of the preflight;
and the certified interval bounds are recorded per cell (largest enclosure sum is about ``3.27`` against a numeric
sum-of-separate-sups of about ``3.03``, so ``M = 4`` absorbs the interval
dependency inflation while staying well inside the ``M ~ 5.2`` dominance
ceiling).

Trust: ``EXACT_OBSTRUCTION`` for the nine named signed cells, all
``m >= 8``, with three disclosed trust roots: sympy symbolic algebra
(identities and derivative expressions, numerically cross-checked), mpmath
outward-rounded interval arithmetic (the Lipschitz bound), and z3
nonlinear real arithmetic (the band/dominance inequalities). Conditional on
the review-pending A-row reduction and boundary-band confinement prose.
Together with the mixed-cells artifact this closes all twelve signed band
cells for every ``m >= 8``; it is still not a closure of non-quarter
three-orbit branches, ``n = 9``, or Erdos Problem #97, not a
counterexample, and not an official/global status update.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from fractions import Fraction

M_LIPSCHITZ = 4
BOX_DE_MAX = Fraction(2, 25)  # 0.08
OMEGA_BOUND = Fraction(397, 5000)  # 0.0794

FIRST_DERIVATIVE_CELLS = (
    {"cell": "LL_y+_z+", "beta_form": "d", "gamma_form": "e", "y_sign": 1,
     "z_sign": 1, "killer_turn": 1, "component": "d", "required_sign": "<",
     "vanishing_boundary": "d0", "corner_sign": -1},
    {"cell": "LL_y+_z-", "beta_form": "d", "gamma_form": "e", "y_sign": 1,
     "z_sign": -1, "killer_turn": 1, "component": "d", "required_sign": "<",
     "vanishing_boundary": "d0", "corner_sign": -1},
    {"cell": "LL_y-_z-", "beta_form": "d", "gamma_form": "e", "y_sign": -1,
     "z_sign": -1, "killer_turn": 3, "component": "e", "required_sign": "<",
     "vanishing_boundary": "diag", "corner_sign": -1},
    {"cell": "LH_y+_z-", "beta_form": "d", "gamma_form": "Te", "y_sign": 1,
     "z_sign": -1, "killer_turn": 3, "component": "e", "required_sign": "<",
     "vanishing_boundary": "e0", "corner_sign": -1},
    {"cell": "LH_y-_z+", "beta_form": "d", "gamma_form": "Te", "y_sign": -1,
     "z_sign": 1, "killer_turn": 2, "component": "d", "required_sign": "<",
     "vanishing_boundary": "d0", "corner_sign": -1},
    {"cell": "LH_y-_z-", "beta_form": "d", "gamma_form": "Te", "y_sign": -1,
     "z_sign": -1, "killer_turn": 2, "component": "d", "required_sign": "<",
     "vanishing_boundary": "d0", "corner_sign": -1},
    {"cell": "HH_y+_z+", "beta_form": "Td", "gamma_form": "Te", "y_sign": 1,
     "z_sign": 1, "killer_turn": 1, "component": "e", "required_sign": "<",
     "vanishing_boundary": "e0", "corner_sign": -1},
    {"cell": "HH_y-_z+", "beta_form": "Td", "gamma_form": "Te", "y_sign": -1,
     "z_sign": 1, "killer_turn": 1, "component": "e", "required_sign": "<",
     "vanishing_boundary": "e0", "corner_sign": -1},
    {"cell": "HH_y-_z-", "beta_form": "Td", "gamma_form": "Te", "y_sign": -1,
     "z_sign": -1, "killer_turn": 2, "component": "e", "required_sign": ">",
     "vanishing_boundary": "diag", "corner_sign": 1},
)

# vanishing_boundary semantics (proof rules of the stored interval
# certificate): "d0" -> F(0, e) == 0, integrate F_d over [0, d];
# "e0" -> F(d, 0) == 0, integrate F_e over [0, e];
# "diag" -> F(d, d) == 0, integrate F_e from the diagonal (forward for
# LL_y-_z- where the cone is d < e, backward for HH_y-_z- where e < d).

EXPECTED_Z3_DECISIONS = {
    "domain_nonempty": "sat",
    "ch_gt_sh": "unsat",
    "omega_bound": "unsat",
    "dominance_combination_m4": "unsat",
    "dominance_combination_m6_control": "sat",
}


# ---------------------------------------------------------------------------
# Symbolic layer
# ---------------------------------------------------------------------------


def _sympy():
    import sympy as sp

    d, e, T = sp.symbols("d e T", positive=True)
    return sp, d, e, T


def killer_turn_expr(sp, d, e, T, cell):
    ys, zs = cell["y_sign"], cell["z_sign"]
    y = ys * sp.sin(d) + sp.sqrt(1 + sp.sin(d) ** 2)
    z = zs * sp.sin(e) + sp.sqrt(1 + sp.sin(e) ** 2)
    beta = d if cell["beta_form"] == "d" else T - d
    gamma = e if cell["gamma_form"] == "e" else T - e
    tau1 = y * sp.sin(beta) - y * z * sp.sin(T + beta - gamma) + z * sp.sin(T - gamma)
    tau2 = y * sp.sin(beta) - z * sp.sin(gamma) + y * z * sp.sin(gamma - beta)
    tau3 = z * sp.sin(T - gamma) - y * sp.sin(T - beta) + y * z * sp.sin(gamma - beta)
    return [tau1, tau2, tau3][cell["killer_turn"] - 1]


def symbolic_identities_hold(cell) -> dict:
    """Exact corner identity F_c(T,0,0) == corner_sign * A and the cell's
    vanishing-boundary identity, both as symbolic identities."""

    sp, d, e, T = _sympy()
    F = killer_turn_expr(sp, d, e, T, cell)
    comp = d if cell["component"] == "d" else e
    corner = sp.simplify(sp.diff(F, comp).subs({d: 0, e: 0}))
    a_expr = sp.sin(T) + sp.cos(T) - 1
    corner_ok = sp.simplify(corner - cell["corner_sign"] * a_expr) == 0
    if cell["vanishing_boundary"] == "d0":
        boundary_ok = sp.simplify(F.subs(d, 0)) == 0
    elif cell["vanishing_boundary"] == "e0":
        boundary_ok = sp.simplify(F.subs(e, 0)) == 0
    else:  # diagonal
        boundary_ok = sp.simplify(F.subs(e, d)) == 0
    return {"corner_identity": bool(corner_ok), "boundary_identity": bool(boundary_ok)}


def a_factorization_holds() -> bool:
    """A = sin T + cos T - 1 equals 2 sin(h) (cos h - sin h) at T = 2h."""

    sp, d, e, T = _sympy()
    h = sp.Symbol("h", positive=True)
    lhs = sp.sin(2 * h) + sp.cos(2 * h) - 1
    rhs = 2 * sp.sin(h) * (sp.cos(h) - sp.sin(h))
    return sp.simplify(sp.expand_trig(lhs) - sp.expand(rhs)) == 0


# ---------------------------------------------------------------------------
# Interval layer (certified Lipschitz bound)
# ---------------------------------------------------------------------------


def certified_lipschitz_bound(cell, *, n_t: int = 24, n_de: int = 4) -> dict:
    """Outward-rounded interval bound for sup |dF_c/dd| + sup |dF_c/de| over
    the box T in [0, pi/4], d, e in [0, 2/25], which contains every band
    square for h in (0, pi/8] (see the omega_bound z3 claim)."""

    import sympy as sp
    from mpmath import iv

    iv.prec = 80
    _, d, e, T = _sympy()
    F = killer_turn_expr(sp, d, e, T, cell)
    comp = d if cell["component"] == "d" else e
    fc = sp.diff(F, comp)
    d1 = sp.expand_trig(sp.diff(fc, d))
    d2 = sp.expand_trig(sp.diff(fc, e))
    mods = [{"sin": iv.sin, "cos": iv.cos, "sqrt": iv.sqrt}]
    f1 = sp.lambdify((T, d, e), d1, modules=mods)
    f2 = sp.lambdify((T, d, e), d2, modules=mods)
    # cover [0, pi/4] outward: float of the interval upper bound, nudged up
    t_upper = float((iv.pi / 4).b) * (1 + 4e-16)
    de_upper = float(BOX_DE_MAX)
    sups = []
    for f in (f1, f2):
        hi = 0.0
        for i in range(n_t):
            ti = iv.mpf([t_upper * i / n_t, t_upper * (i + 1) / n_t])
            for j in range(n_de):
                dj = iv.mpf([de_upper * j / n_de, de_upper * (j + 1) / n_de])
                for k in range(n_de):
                    ek = iv.mpf([de_upper * k / n_de, de_upper * (k + 1) / n_de])
                    cand = float(abs(f(ti, dj, ek)).b)
                    if not math.isfinite(cand):
                        raise RuntimeError(
                            f"non-finite interval enclosure for {cell['cell']}"
                        )
                    hi = max(hi, cand)
        sups.append(hi)
    # float() of an interval endpoint rounds to nearest (error <= 2^-52
    # relative); the explicit 1e-12 safety factor dominates that rounding,
    # and the true margin to M = 4 is about 18 percent.
    total = (sups[0] + sups[1]) * (1 + 1e-12)
    certified = total <= M_LIPSCHITZ
    return {
        "sup_abs_dd_upper": sups[0],
        "sup_abs_de_upper": sups[1],
        "sum_upper": total,
        "subdivision": [n_t, n_de, n_de],
        "certified_le_m": certified,
    }


# ---------------------------------------------------------------------------
# z3 layer (band and dominance inequalities; shared across all nine cells)
# ---------------------------------------------------------------------------


def decide_band_and_dominance(*, timeout_ms: int) -> dict:
    import z3

    results = {}

    def run(name, extra):
        ch, sh = z3.Reals("ch sh")
        s = z3.Solver()
        s.set("timeout", timeout_ms)
        s.add(ch * ch + sh * sh == 1, sh > 0, ch > 0)
        s.add(2 * ch * ch - 1 >= 2 * sh * ch)  # T <= pi/4, i.e. m >= 8
        for c in extra(ch, sh):
            s.add(c)
        results[name] = str(s.check())

    run("domain_nonempty", lambda ch, sh: [])
    run("ch_gt_sh", lambda ch, sh: [ch <= sh])  # negation of ch > sh
    omega = z3.Q(OMEGA_BOUND.numerator, OMEGA_BOUND.denominator)
    run("omega_bound", lambda ch, sh: [sh * sh > 2 * ch * omega])
    run(
        "dominance_combination_m4",
        lambda ch, sh: [
            M_LIPSCHITZ * M_LIPSCHITZ * sh * sh
            >= 4 * (ch - sh) * (ch - sh) * (4 * ch * ch - sh ** 4)
        ],
    )
    run(
        "dominance_combination_m6_control",
        lambda ch, sh: [
            36 * sh * sh >= 4 * (ch - sh) * (ch - sh) * (4 * ch * ch - sh ** 4)
        ],
    )
    return results


def band_inside_box_exact() -> bool:
    """delta_bar = omega/sqrt(1-omega^2) <= 2/25 for omega <= 397/5000,
    in exact rational arithmetic (squared form)."""

    w = OMEGA_BOUND
    return w * w <= BOX_DE_MAX * BOX_DE_MAX * (1 - w * w)


def dominance_chain_exact() -> bool:
    """The cleared combination inequality implies M * delta_bar < A:
    M^2 sh^2 < 4 (ch-sh)^2 (4 ch^2 - sh^4) is exactly
    (M * omega / sqrt(1 - omega^2))^2 < A^2 after clearing the positive
    factor 4 ch^2 / sh^2, with omega = sh^2/(2 ch) and A = 2 sh (ch - sh).
    Verified here as an unconditional symbolic identity in (ch, sh)."""

    import sympy as sp

    ch, sh = sp.symbols("ch sh", positive=True)
    omega = sh * sh / (2 * ch)
    a_sq = (2 * sh * (ch - sh)) ** 2
    lhs = M_LIPSCHITZ * M_LIPSCHITZ * omega * omega
    rhs = a_sq * (1 - omega * omega)
    cleared_lhs = M_LIPSCHITZ * M_LIPSCHITZ * sh * sh
    cleared_rhs = 4 * (ch - sh) ** 2 * (4 * ch * ch - sh ** 4)
    scale = 4 * ch * ch / (sh * sh)
    identity = sp.simplify((rhs - lhs) * scale - (cleared_rhs - cleared_lhs))
    return identity == 0


# ---------------------------------------------------------------------------
# Deterministic numeric spot checks
# ---------------------------------------------------------------------------


def _raw_turn(cell, T, dd, ee):
    ys, zs = cell["y_sign"], cell["z_sign"]
    beta = dd if cell["beta_form"] == "d" else T - dd
    gamma = ee if cell["gamma_form"] == "e" else T - ee
    y = math.exp(math.asinh(ys * math.sin(dd)))
    z = math.exp(math.asinh(zs * math.sin(ee)))

    def point(radius, angle):
        return (radius * math.cos(angle), radius * math.sin(angle))

    def cross(u, v, w):
        return (v[0] - u[0]) * (w[1] - v[1]) - (v[1] - u[1]) * (w[0] - v[0])

    a0 = point(1.0, 0.0)
    a1 = point(1.0, T)
    b0 = point(y, beta)
    c0 = point(z, gamma)
    c_minus_1 = point(z, gamma - T)
    turns = (
        cross(c_minus_1, a0, b0),
        cross(a0, b0, c0),
        cross(b0, c0, a1),
    )
    return turns[cell["killer_turn"] - 1]


def finite_difference_agreement(cell, grid: int = 5) -> dict:
    """The symbolic derivative component matches central finite differences
    of the raw geometric turn on a deterministic lattice."""

    import sympy as sp

    _, d, e, T = _sympy()
    F = killer_turn_expr(sp, d, e, T, cell)
    comp_sym = d if cell["component"] == "d" else e
    fc = sp.lambdify((T, d, e), sp.diff(F, comp_sym), "math")
    checked = 0
    max_rel_err = 0.0
    for i in range(1, grid + 1):
        T_val = (math.pi / 4) * i / grid
        h = T_val / 2
        omega = math.sin(h) ** 2 / (2 * math.cos(h))
        delta = math.asin(omega)
        for j in range(grid + 1):
            for k in range(grid + 1):
                dd = delta * j / grid
                ee = delta * k / grid
                eps = 1e-7
                if cell["component"] == "d":
                    fd = (
                        _raw_turn(cell, T_val, dd + eps, ee)
                        - _raw_turn(cell, T_val, dd - eps, ee)
                    ) / (2 * eps)
                else:
                    fd = (
                        _raw_turn(cell, T_val, dd, ee + eps)
                        - _raw_turn(cell, T_val, dd, ee - eps)
                    ) / (2 * eps)
                sv = fc(T_val, dd, ee)
                checked += 1
                scale = max(abs(fd), abs(sv), 1e-9)
                max_rel_err = max(max_rel_err, abs(fd - sv) / scale)
    return {
        "grid": grid,
        "points_checked": checked,
        "max_rel_err": round(max_rel_err, 12),
        "ok": max_rel_err < 1e-5,
    }


def embedding_spot_check(max_m: int = 120) -> dict:
    """Quarter-cell instances (m = 0 mod 4, m >= 8) satisfy the shared z3
    domain and have band radius below the interval box bound."""

    checked = 0
    ok = True
    for m in range(8, max_m + 1, 4):
        h = math.pi / m
        ch, sh = math.cos(h), math.sin(h)
        omega = sh * sh / (2 * ch)
        delta = math.asin(omega)
        conds = (
            2 * ch * ch - 1 >= 2 * sh * ch - 1e-15,
            ch > sh,
            omega <= float(OMEGA_BOUND) + 1e-15,
            delta <= float(BOX_DE_MAX),
        )
        ok = ok and all(conds)
        checked += 1
    return {"max_m": max_m, "instances_checked": checked, "ok": ok}


# ---------------------------------------------------------------------------
# Payload / CLI
# ---------------------------------------------------------------------------


def compare_artifact_replay(payload, artifact_path: str) -> list[str]:
    """Compare the freshly generated deterministic payload with a stored artifact."""

    with open(artifact_path, encoding="utf-8") as fh:
        stored = json.load(fh)
    if payload == stored:
        return []
    errors: list[str] = []
    for key in sorted(set(payload) | set(stored)):
        if payload.get(key) != stored.get(key):
            errors.append(f"{key}: replay differs from stored artifact")
    return errors


def build_payload(args) -> dict:
    z3_decisions = decide_band_and_dominance(timeout_ms=args.timeout_ms)
    a_fact = a_factorization_holds()
    band_box = band_inside_box_exact()
    chain = dominance_chain_exact()
    cells_out = []
    all_ok = True
    for cell in FIRST_DERIVATIVE_CELLS:
        idents = symbolic_identities_hold(cell)
        lip = certified_lipschitz_bound(cell, n_t=args.interval_t_slices,
                                        n_de=args.interval_de_slices)
        agreement = finite_difference_agreement(cell)
        cell_ok = (
            idents["corner_identity"]
            and idents["boundary_identity"]
            and lip["certified_le_m"]
            and agreement["ok"]
        )
        all_ok = all_ok and cell_ok
        cells_out.append(
            {
                "cell": cell["cell"],
                "component": cell["component"],
                "required_sign": cell["required_sign"],
                "corner_sign": cell["corner_sign"],
                "vanishing_boundary": cell["vanishing_boundary"],
                "killer_turn": cell["killer_turn"],
                "y_sign": cell["y_sign"],
                "z_sign": cell["z_sign"],
                "symbolic_identities": idents,
                "lipschitz": {
                    "sum_upper": round(lip["sum_upper"], 9),
                    "sup_abs_dd_upper": round(lip["sup_abs_dd_upper"], 9),
                    "sup_abs_de_upper": round(lip["sup_abs_de_upper"], 9),
                    "subdivision": lip["subdivision"],
                    "certified_le_m": lip["certified_le_m"],
                },
                "finite_difference_agreement": {
                    "grid": agreement["grid"],
                    "points_checked": agreement["points_checked"],
                    "ok": agreement["ok"],
                },
                "certified": cell_ok,
            }
        )
    embedding = embedding_spot_check(args.max_m)
    clear = (
        all_ok
        and z3_decisions == EXPECTED_Z3_DECISIONS
        and a_fact
        and band_box
        and chain
        and embedding["ok"]
    )
    return {
        "schema": "erdos97.quarter_cell_first_derivative_all_m_dominance.v1",
        "status": "EXACT_FIRST_DERIVATIVE_CELLS_ALL_M_DOMINANCE"
        if clear
        else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": (
                "scripts/check_quarter_cell_first_derivative_all_m_dominance.py"
            ),
            "command": (
                "python scripts/"
                "check_quarter_cell_first_derivative_all_m_dominance.py "
                "--assert-clear --write-artifact "
                "data/certificates/"
                "quarter_cell_first_derivative_all_m_dominance.json"
            ),
        },
        "scope": (
            "All-m dominance closure of the nine first-derivative "
            "three-orbit quarter-cell signed band cells for every m >= 8 at "
            "once: exact sympy corner identities F_c(T,0,0) = +/-(sin T + "
            "cos T - 1) and vanishing-boundary identities, an "
            "outward-rounded interval Lipschitz bound "
            "sup|dF_c/dd| + sup|dF_c/de| <= 4 over a box containing every "
            "band square, and z3-verified band/dominance inequalities "
            "showing 4 * delta_bar < A on the whole m >= 8 range, so each "
            "derivative component keeps its corner sign throughout the band "
            "square and one-variable integration closes each strict cell. "
            "Supersedes the finite m = 8, 12, 16 interval certificate for "
            "these nine cells (retained as an independent finite-m "
            "cross-check); together with "
            "quarter_cell_mixed_cells_all_m_smt this closes all twelve "
            "signed band cells for every m >= 8. Conditional on the "
            "review-pending A-row reduction and boundary-band confinement "
            "prose. Not a closure of non-quarter three-orbit branches, "
            "n = 9, or Erdos Problem #97, not a counterexample, and not an "
            "official/global status update."
        ),
        "m_lipschitz": M_LIPSCHITZ,
        "box_de_max": str(BOX_DE_MAX),
        "omega_bound": str(OMEGA_BOUND),
        "z3_decisions": z3_decisions,
        "expected_z3_decisions": dict(EXPECTED_Z3_DECISIONS),
        "exact_checks": {
            "a_factorization_2sh_ch_minus_sh": a_fact,
            "band_inside_box_rational": band_box,
            "dominance_clearing_identity_symbolic": chain,
        },
        "cells": cells_out,
        "embedding_spot_check": embedding,
        "clear": clear,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout-ms", type=int, default=120000)
    ap.add_argument("--max-m", type=int, default=120)
    ap.add_argument("--interval-t-slices", type=int, default=24)
    ap.add_argument("--interval-de-slices", type=int, default=4)
    ap.add_argument(
        "--assert-clear",
        action="store_true",
        help="exit nonzero unless every cell certifies and all shared "
        "z3/exact/embedding checks pass",
    )
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-artifact", type=str, default="")
    ap.add_argument(
        "--check-artifact",
        type=str,
        default="",
        help="compare deterministic replay fields against a stored artifact",
    )
    args = ap.parse_args()
    if args.max_m < 8:
        ap.error("--max-m must be at least 8 (the smallest quarter-cell m)")
    if args.interval_t_slices < 8 or args.interval_de_slices < 2:
        ap.error("interval subdivision too coarse to be meaningful")

    payload = build_payload(args)

    if args.check_artifact:
        errors = compare_artifact_replay(payload, args.check_artifact)
        if errors:
            print("artifact replay mismatch:", file=sys.stderr)
            for err in errors:
                print(f"- {err}", file=sys.stderr)
            return 1
    if args.write_artifact:
        if not payload["clear"]:
            print(
                "refusing to write a non-clear payload (an identity, "
                "interval bound, z3 decision, or agreement check failed); "
                "the target artifact is left untouched",
                file=sys.stderr,
            )
            return 1
        with open(args.write_artifact, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        print(f"z3: {payload['z3_decisions']}")
        print(f"exact: {payload['exact_checks']}")
        for cell in payload["cells"]:
            print(
                f"{cell['cell']}: identities="
                f"{cell['symbolic_identities']} "
                f"lipschitz_sum<= {cell['lipschitz']['sum_upper']:.4f} "
                f"fd_ok={cell['finite_difference_agreement']['ok']} "
                f"certified={cell['certified']}"
            )
        print(f"clear={payload['clear']}")
    if args.assert_clear and not payload["clear"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
