#!/usr/bin/env python3
"""Exact all-m SMT closure of the three mixed-derivative quarter-cell cells.

Context (`docs/quarter-cell-signed-band-preflight.md` and
`docs/quarter-cell-derivative-certificate.md`): the remaining ``m = 0 mod 4``
three-orbit quarter cells reduce, via the A-row reduction and the
boundary-band confinement, to twelve signed band cells with ``T = 2*pi/m``,
band variables ``0 < d, e < delta_m`` (``sin(delta_m) = sin(h)^2/(2 cos h)``,
``h = T/2``), offsets ``beta, gamma`` in ``{d, T-d} x {e, T-e}``, and radii
``P(y) = ys*sin d``, ``P(z) = zs*sin e`` with ``P(r) = (r^2-1)/(2r)``. The
missing exact lemma per cell is that a fixed killer turn ``F`` is negative
throughout the strict cell; the stored interval certificate proves it for
``m = 8, 12, 16`` only, via per-cell derivative signs.

This checker closes the three *mixed-derivative* cells for ALL ``m >= 8`` at
once (in particular every quarter-cell ``m = 0 mod 4``, ``m >= 8``):

    LL_y-_z+  (beta=d,   gamma=e,   ys=-1, zs=+1, killer tau_2)
    LH_y+_z+  (beta=d,   gamma=T-e, ys=+1, zs=+1, killer tau_1)
    HH_y+_z-  (beta=T-d, gamma=T-e, ys=+1, zs=-1, killer tau_3)

by the stored certificate's own proof rule ``F(d,0) = F(0,e) = 0 and
F_de < 0``, upgraded to all ``m``:

1. Boundary identities (exact, m-uniform): sympy verifies symbolically that
   ``F(0, e) == 0`` and ``F(d, 0) == 0`` as identities in ``(e, T)`` and
   ``(d, T)``.
2. Mixed-derivative sign (exact, all m at once): the mixed derivative
   ``F_de`` is derived symbolically, the radius derivative uses
   ``dy/dd = ys*cos(d)*y / S_d`` with ``S_d = sqrt(1+sin^2 d) = y - ys*sin d
   > 0``, and clearing the positive denominator ``S_d^a S_e^b`` leaves a
   polynomial numerator ``N`` in ``(sin d, cos d, sin e, cos e, sin T,
   cos T, y, z)``. Every integer instance lands in the polynomial relaxation

       ch^2+sh^2=1, sh>0, ch>0, cT=2ch^2-1, sT=2 sh ch, cT>=sT   [T in (0,pi/4]]
       cd^2+sd^2=1, sd>=0, cd>0, 2 ch sd <= sh^2                 [d in [0,delta]]
       ce^2+se^2=1, se>=0, ce>0, 2 ch se <= sh^2                 [e in [0,delta]]
       y^2 - 2 ys sd y - 1 = 0, y > 0;  z^2 - 2 zs se z - 1 = 0, z > 0

   (cosine monotonicity turns ``m >= 8`` into ``cos T >= sin T`` and the
   closed band ``sin d <= sin(h)^2/(2 cos h)`` into ``2 ch sd <= sh^2``),
   and z3 nonlinear real arithmetic proves ``N >= 0`` UNSAT over it, so
   ``F_de < 0`` on the closed band square for every ``T in (0, pi/4]``.
3. Integration (elementary, in the note): ``F(d, e) = int_0^d int_0^e F_de``
   by the vanishing edges, so ``F < 0`` for all ``0 < d, e <= delta`` --
   in particular throughout each strict cell cone.

Controls per cell: the relaxation alone is SAT (non-empty domain) and
``N < 0`` is SAT (the domain sees the negative side), so the main UNSAT is
neither vacuous nor a mis-signed contradiction. A deterministic
finite-difference grid ties ``N`` back to the raw geometric turn defined by
the preflight's point coordinates.

Trust: ``EXACT_OBSTRUCTION`` (SMT + symbolic identities) for the three named
signed cells only, all ``m >= 8``. The remaining nine signed cells stay at
the finite ``m = 8, 12, 16`` interval grade: their first-derivative claims
degenerate only in the ``T -> 0`` limit but z3 NRA returns unknown on them
(120 s budget) in this same encoding -- the recorded next target is a
small-T dominance lemma, not another direct solver run. This artifact is
conditional on the quarter-cell A-row reduction and boundary-band
confinement (review-pending prose), does not close the quarter cells by
itself, and is not a proof of the three-orbit family or Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import math
import sys

MIXED_CELLS = (
    {
        "cell": "LL_y-_z+",
        "beta_form": "d",
        "gamma_form": "e",
        "y_sign": -1,
        "z_sign": 1,
        "killer_turn": 2,
    },
    {
        "cell": "LH_y+_z+",
        "beta_form": "d",
        "gamma_form": "Te",
        "y_sign": 1,
        "z_sign": 1,
        "killer_turn": 1,
    },
    {
        "cell": "HH_y+_z-",
        "beta_form": "Td",
        "gamma_form": "Te",
        "y_sign": 1,
        "z_sign": -1,
        "killer_turn": 3,
    },
)

EXPECTED_DECISIONS = {
    "mixed_derivative_nonnegative": "unsat",
    "domain_nonempty": "sat",
    "negative_side_reachable": "sat",
}


# ---------------------------------------------------------------------------
# Symbolic layer (sympy): killer turn, boundary identities, F_de numerator
# ---------------------------------------------------------------------------


def _symbols():
    import sympy as sp

    d, e, T = sp.symbols("d e T", positive=True)
    poly_syms = sp.symbols("Sd Cd Se Ce ST CT Yv Zv")
    return sp, d, e, T, poly_syms


def killer_turn_expr(sp, d, e, T, cell):
    """The cell's killer turn with radii substituted:
    y = ys*sin d + sqrt(1+sin^2 d) (the positive root of P(y) = ys*sin d)."""

    ys, zs = cell["y_sign"], cell["z_sign"]
    y = ys * sp.sin(d) + sp.sqrt(1 + sp.sin(d) ** 2)
    z = zs * sp.sin(e) + sp.sqrt(1 + sp.sin(e) ** 2)
    beta = d if cell["beta_form"] == "d" else T - d
    gamma = e if cell["gamma_form"] == "e" else T - e
    tau1 = y * sp.sin(beta) - y * z * sp.sin(T + beta - gamma) + z * sp.sin(T - gamma)
    tau2 = y * sp.sin(beta) - z * sp.sin(gamma) + y * z * sp.sin(gamma - beta)
    tau3 = z * sp.sin(T - gamma) - y * sp.sin(T - beta) + y * z * sp.sin(gamma - beta)
    return [tau1, tau2, tau3][cell["killer_turn"] - 1]


def boundary_identities_hold(cell) -> bool:
    """F(0, e) == 0 and F(d, 0) == 0 as exact symbolic identities."""

    sp, d, e, T, _ = _symbols()
    F = killer_turn_expr(sp, d, e, T, cell)
    return sp.simplify(F.subs(d, 0)) == 0 and sp.simplify(F.subs(e, 0)) == 0


def mixed_numerator(cell):
    """Return (sympy_poly_numerator, canonical_terms) for F_de.

    The numerator N satisfies F_de = N / (S_d^a * S_e^b) with
    S_d = sqrt(1+sin^2 d) > 0 and S_e = sqrt(1+sin^2 e) > 0, so
    sign(F_de) = sign(N). Canonical terms are the sorted
    (exponent-tuple, coefficient) list of N as a polynomial in
    (Sd, Cd, Se, Ce, ST, CT, Yv, Zv), stable across sympy versions.
    """

    sp, d, e, T, poly_syms = _symbols()
    Sd, Cd, Se, Ce, ST, CT, Yv, Zv = poly_syms
    ys, zs = cell["y_sign"], cell["z_sign"]
    Y = sp.Function("Y")(d)
    Z = sp.Function("Z")(e)
    beta = d if cell["beta_form"] == "d" else T - d
    gamma = e if cell["gamma_form"] == "e" else T - e
    tau1 = Y * sp.sin(beta) - Y * Z * sp.sin(T + beta - gamma) + Z * sp.sin(T - gamma)
    tau2 = Y * sp.sin(beta) - Z * sp.sin(gamma) + Y * Z * sp.sin(gamma - beta)
    tau3 = Z * sp.sin(T - gamma) - Y * sp.sin(T - beta) + Y * Z * sp.sin(gamma - beta)
    F = sp.expand_trig([tau1, tau2, tau3][cell["killer_turn"] - 1])
    D = sp.diff(sp.diff(F, d), e)
    SQd = Yv - ys * Sd  # = sqrt(1 + sin^2 d) for the positive root
    SQe = Zv - zs * Se
    D = D.subs(sp.Derivative(Y, d), ys * sp.cos(d) * Y / SQd)
    D = D.subs(sp.Derivative(Z, e), zs * sp.cos(e) * Z / SQe)
    D = D.subs({Y: Yv, Z: Zv})
    D = D.subs(
        {
            sp.sin(d): Sd,
            sp.cos(d): Cd,
            sp.sin(e): Se,
            sp.cos(e): Ce,
            sp.sin(T): ST,
            sp.cos(T): CT,
        }
    )
    D = sp.together(sp.expand(D))
    num, den = sp.fraction(D)
    # The denominator must be (const) * SQd^a * SQe^b; determine its overall
    # sign by rewriting in explicitly positive symbols.
    SQD, SQE = sp.symbols("SQD SQE", positive=True)
    den_pos = sp.expand(den).subs(Yv, SQD + ys * Sd).subs(Zv, SQE + zs * Se)
    den_pos = sp.factor(sp.expand(den_pos))
    const, factors = sp.factor_list(den_pos)
    for fac, _power in factors:
        if fac not in (SQD, SQE):
            raise RuntimeError(f"unexpected denominator factor {fac}")
    if not const.is_number or const == 0:
        raise RuntimeError(f"unexpected denominator constant {const}")
    if const < 0:
        num = -num
    num = sp.expand(num)
    poly = sp.Poly(num, Sd, Cd, Se, Ce, ST, CT, Yv, Zv)
    terms = sorted(
        (list(map(int, mono)), str(coef)) for mono, coef in poly.terms()
    )
    return num, [[mono, coef] for mono, coef in terms]


# ---------------------------------------------------------------------------
# SMT layer (z3): all-T decisions over the polynomial relaxation
# ---------------------------------------------------------------------------


def _sympy_to_z3(expr, env):
    import z3

    if expr.is_Symbol:
        return env[expr]
    if expr.is_Integer:
        return z3.IntVal(int(expr))
    if expr.is_Rational:
        return z3.Q(int(expr.p), int(expr.q))
    if expr.is_Add:
        result = _sympy_to_z3(expr.args[0], env)
        for arg in expr.args[1:]:
            result = result + _sympy_to_z3(arg, env)
        return result
    if expr.is_Mul:
        result = _sympy_to_z3(expr.args[0], env)
        for arg in expr.args[1:]:
            result = result * _sympy_to_z3(arg, env)
        return result
    if expr.is_Pow:
        base, exponent = expr.args
        if not (exponent.is_Integer and exponent > 0):
            raise ValueError(f"cannot convert power {expr}")
        result = _sympy_to_z3(base, env)
        out = result
        for _ in range(int(exponent) - 1):
            out = out * result
        return out
    raise ValueError(f"cannot convert {expr}")


def decide_cell(cell, numer, poly_syms, *, timeout_ms: int) -> dict:
    import z3

    Sd, Cd, Se, Ce, ST, CT, Yv, Zv = poly_syms
    ys, zs = cell["y_sign"], cell["z_sign"]
    results = {}
    for name, relation in (
        ("mixed_derivative_nonnegative", ">="),
        ("domain_nonempty", None),
        ("negative_side_reachable", "<"),
    ):
        ch, sh, cT, sT, cd, sd, ce, se, y, z = z3.Reals(
            "ch sh cT sT cd sd ce se y z"
        )
        env = {Sd: sd, Cd: cd, Se: se, Ce: ce, ST: sT, CT: cT, Yv: y, Zv: z}
        solver = z3.Solver()
        solver.set("timeout", timeout_ms)
        solver.add(ch * ch + sh * sh == 1, sh > 0, ch > 0)
        solver.add(cT == 2 * ch * ch - 1, sT == 2 * sh * ch, cT >= sT)
        solver.add(cd * cd + sd * sd == 1, sd >= 0, cd > 0, 2 * ch * sd <= sh * sh)
        solver.add(ce * ce + se * se == 1, se >= 0, ce > 0, 2 * ch * se <= sh * sh)
        solver.add(y * y - 2 * ys * sd * y - 1 == 0, y > 0)
        solver.add(z * z - 2 * zs * se * z - 1 == 0, z > 0)
        if relation is not None:
            n_expr = _sympy_to_z3(numer, env)
            solver.add(n_expr >= 0 if relation == ">=" else n_expr < 0)
        results[name] = str(solver.check())
    return results


# ---------------------------------------------------------------------------
# Deterministic numeric spot checks (redundant with the symbolic layer)
# ---------------------------------------------------------------------------


def _raw_turn(cell, T, dd, ee):
    """Raw geometric per-period turn from the preflight's point coordinates."""

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


def finite_difference_agreement(cell, numer, poly_syms, grid: int = 6) -> dict:
    """On a deterministic (T, d, e) lattice, the polynomial numerator has the
    same sign as (and a positive ratio to) the finite-difference mixed
    derivative of the raw geometric turn."""

    import sympy as sp

    ys, zs = cell["y_sign"], cell["z_sign"]
    n_func = sp.lambdify(poly_syms, numer, "math")
    checked = 0
    sign_mismatches = 0
    ratio_nonpositive = 0
    for i in range(1, grid + 1):
        T = (math.pi / 4) * i / grid
        h = T / 2
        omega = math.sin(h) ** 2 / (2 * math.cos(h))
        delta = math.asin(omega)
        for j in range(1, grid + 1):
            for k in range(1, grid + 1):
                dd = delta * j / (grid + 1)
                ee = delta * k / (grid + 1)
                eps = 1e-6 * delta
                fde = (
                    _raw_turn(cell, T, dd + eps, ee + eps)
                    - _raw_turn(cell, T, dd + eps, ee - eps)
                    - _raw_turn(cell, T, dd - eps, ee + eps)
                    + _raw_turn(cell, T, dd - eps, ee - eps)
                ) / (4 * eps * eps)
                y = math.exp(math.asinh(ys * math.sin(dd)))
                z = math.exp(math.asinh(zs * math.sin(ee)))
                n_val = n_func(
                    math.sin(dd),
                    math.cos(dd),
                    math.sin(ee),
                    math.cos(ee),
                    math.sin(T),
                    math.cos(T),
                    y,
                    z,
                )
                checked += 1
                if (n_val < 0) != (fde < 0):
                    sign_mismatches += 1
                if fde != 0 and n_val / fde <= 0:
                    ratio_nonpositive += 1
    return {
        "grid": grid,
        "points_checked": checked,
        "sign_mismatches": sign_mismatches,
        "ratio_nonpositive": ratio_nonpositive,
        "ok": sign_mismatches == 0 and ratio_nonpositive == 0,
    }


def embedding_spot_check(max_m: int = 120) -> dict:
    """Quarter-cell instances (m = 0 mod 4, m >= 8) land in the relaxation:
    T = 2*pi/m has cos T >= sin T > 0 and the band bound maps to
    2*cos(h)*sin(delta) <= sin(h)^2 with equality (delta is the band edge)."""

    checked = 0
    ok = True
    for m in range(8, max_m + 1, 4):
        T = 2 * math.pi / m
        h = T / 2
        ch, sh = math.cos(h), math.sin(h)
        cT, sT = math.cos(T), math.sin(T)
        omega = sh * sh / (2 * ch)
        delta = math.asin(omega)
        conds = (
            sT > 0,
            cT >= sT - 1e-15,
            abs(2 * ch * math.sin(delta) - sh * sh) < 1e-12,
            0 < omega < 1,
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
    _, _, _, _, poly_syms = _symbols()
    cells_out = []
    all_ok = True
    for cell in MIXED_CELLS:
        numer, terms = mixed_numerator(cell)
        identities = boundary_identities_hold(cell)
        decisions = decide_cell(cell, numer, poly_syms, timeout_ms=args.timeout_ms)
        agreement = finite_difference_agreement(cell, numer, poly_syms)
        cell_ok = (
            identities
            and decisions == EXPECTED_DECISIONS
            and agreement["ok"]
        )
        all_ok = all_ok and cell_ok
        cells_out.append(
            {
                "cell": cell["cell"],
                "beta_form": cell["beta_form"],
                "gamma_form": cell["gamma_form"],
                "y_sign": cell["y_sign"],
                "z_sign": cell["z_sign"],
                "killer_turn": cell["killer_turn"],
                "boundary_identities_exact": identities,
                "decisions": decisions,
                "numerator_term_count": len(terms),
                "numerator_terms": terms,
                "finite_difference_agreement": agreement,
                "certified": cell_ok,
            }
        )
    embedding = embedding_spot_check(args.max_m)
    clear = all_ok and embedding["ok"]
    return {
        "schema": "erdos97.quarter_cell_mixed_cells_all_m_smt.v1",
        "status": "EXACT_MIXED_CELLS_ALL_M_SMT" if clear else "INCOMPLETE",
        "trust": "EXACT_OBSTRUCTION",
        "provenance": {
            "generator": "scripts/check_quarter_cell_mixed_cells_all_m_smt.py",
            "command": (
                "python scripts/check_quarter_cell_mixed_cells_all_m_smt.py "
                "--assert-clear --write-artifact "
                "data/certificates/quarter_cell_mixed_cells_all_m_smt.json"
            ),
        },
        "scope": (
            "Exact all-m closure of the three mixed-derivative quarter-cell "
            "signed band cells LL_y-_z+, LH_y+_z+, HH_y+_z- for every "
            "m >= 8 at once (in particular every quarter-cell m = 0 mod 4, "
            "m >= 8): sympy verifies the boundary identities F(d,0) = "
            "F(0,e) = 0 exactly, and z3 nonlinear real arithmetic proves "
            "the cleared mixed-derivative numerator cannot be nonnegative "
            "over a polynomial relaxation containing every T in (0, pi/4] "
            "and the full closed band square, so F_de < 0 there and double "
            "integration gives F < 0 throughout each strict cell. This "
            "supersedes the finite m = 8, 12, 16 interval certificate for "
            "these three cells only; the other nine signed cells remain at "
            "finite-m interval grade with a recorded small-T dominance "
            "lemma as the named next target. Conditional on the "
            "quarter-cell A-row reduction and boundary-band confinement "
            "(review-pending prose). Not a closure of the quarter cells, "
            "the three-orbit family, or Erdos Problem #97, not a "
            "counterexample, and not an official/global status update."
        ),
        "expected_decisions": dict(EXPECTED_DECISIONS),
        "cells": cells_out,
        "embedding_spot_check": embedding,
        "route_notes": {
            "direct_sign_claim": (
                "z3 NRA returned unknown within 450-480 s budgets on the "
                "direct all-m killer-turn sign claim (circle-variable and "
                "tangent-half-angle encodings); a plausible cause is that "
                "F vanishes on the whole d,e -> 0 boundary, making the "
                "negation tangent to the feasible set along a curve"
            ),
            "first_derivative_cells": (
                "the nine first-derivative cells returned unknown at 120 s "
                "per cell in this same relaxation; their claims degenerate "
                "only as T -> 0, and the recorded next target is a small-T "
                "dominance lemma, not another direct solver run"
            ),
        },
        "clear": clear,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--timeout-ms", type=int, default=120000)
    ap.add_argument(
        "--max-m",
        type=int,
        default=120,
        help="embedding spot-check bound (redundant with the exact argument)",
    )
    ap.add_argument(
        "--assert-clear",
        action="store_true",
        help="exit nonzero unless every cell certifies (boundary identities, "
        "three z3 decisions, finite-difference agreement) and the embedding "
        "spot-check passes",
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
                "refusing to write a non-clear payload (an identity, z3 "
                "decision, or agreement check failed); the target artifact "
                "is left untouched",
                file=sys.stderr,
            )
            return 1
        with open(args.write_artifact, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh, indent=1, sort_keys=True)
            fh.write("\n")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    else:
        for cell in payload["cells"]:
            print(
                f"{cell['cell']}: identities={cell['boundary_identities_exact']} "
                f"decisions={cell['decisions']} "
                f"fd_agreement_ok={cell['finite_difference_agreement']['ok']} "
                f"certified={cell['certified']}"
            )
        print(
            f"embedding m<= {payload['embedding_spot_check']['max_m']}: "
            f"instances={payload['embedding_spot_check']['instances_checked']} "
            f"ok={payload['embedding_spot_check']['ok']}"
        )
        print(f"clear={payload['clear']}")
    if args.assert_clear and not payload["clear"]:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
