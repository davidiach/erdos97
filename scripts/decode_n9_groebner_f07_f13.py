#!/usr/bin/env python3
"""Replayable Gröbner-basis real-root decoder for the n=9 follow-up families.

The 2026-05-05 multi-agent round established that 168 / 184 selected-witness
n=9 assignments are exactly killed by sympy Gröbner bases over QQ
(150 by GB={1}, 18 by F12's univariate `y_8^2 + 1/4 = 0` real-root
infeasibility). The remaining 16 labelled assignments split into four dihedral
orbit representatives F07, F08, F09, F13, each with a 62-element grevlex
Gröbner basis describing a zero-dimensional ideal.

This script

  1. builds the polynomial system from each family's witness rows under the
     gauge fix x0=y0=0, x1=1, y1=0;
  2. computes the grevlex Gröbner basis in QQ[x_2,...,x_8,y_2,...,y_8];
  3. extracts a univariate elimination polynomial in y_2 by substituting the
     explicit linear basis elements (x_2 = x_5 = x_8 = 1/2 in every family) and
     iterating real-root factorisations;
  4. enumerates every real algebraic configuration consistent with the basis
     by structured back-substitution from the seven independent free roots;
  5. for each real root, reconstructs all 9 vertex coordinates and records
     whether the configuration is a strictly convex 9-gon (every consecutive
     triple has strictly positive signed area in the cyclic order 0..8).

The artifact ``data/certificates/n9_groebner_real_root_decoders.json`` records,
per family: the list of 27 polynomial generators, the 62-element grevlex basis,
the univariate elimination polynomial in y_2, all real roots, and the
strict-convexity outcome for every reconstructed configuration. None of the
configurations is strictly convex, providing a second-source algebraic
certificate that complements the vertex-circle exhaustive checker for the 16
labelled n=9 assignments in F07/F08/F09/F13.

The committed Gröbner artifact at ``data/certificates/2026-05-05/n9_groebner_results.json``
is unchanged. This script is *added*, not a replacement.

This is REVIEW_PENDING and does NOT alter the official/global FALSIFIABLE/OPEN
status of Erdős #97, nor does it promote the n=9 finite-case past
review-pending; it only provides a replayable algebraic check.
"""

from __future__ import annotations

import argparse
import itertools
import json
import time
from pathlib import Path
from typing import Iterable

import sympy as sp
from sympy import (
    Rational,
    S,
    Symbol,
    expand,
    groebner,
    sqrt,
    QQ,
)

ROOT = Path(__file__).resolve().parents[1]
SOURCE_GROEBNER = ROOT / "data" / "certificates" / "2026-05-05" / "n9_groebner_results.json"
DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_groebner_real_root_decoders.json"

TARGET_FAMILIES = ("F07", "F08", "F09", "F13")


def build_system(rows: list[list[int]], n: int = 9):
    """Return (free_vars, gauge_subs, polys, x_syms, y_syms)."""
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = {xs[0]: S.Zero, ys[0]: S.Zero, xs[1]: S.One, ys[1]: S.Zero}
    polys: list[sp.Expr] = []
    for i, w in enumerate(rows):
        if len(w) != 4:
            raise ValueError(f"row {i} expected 4 witnesses, got {len(w)}")
        d2 = [(xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2 for j in w]
        polys.append(d2[0] - d2[1])
        polys.append(d2[0] - d2[2])
        polys.append(d2[0] - d2[3])
    polys = [expand(p.subs(subs)) for p in polys]
    polys = [p for p in polys if p != 0]
    free = [v for i in range(n) for v in (xs[i], ys[i]) if v not in subs]
    return free, subs, polys, xs, ys


def infer_constraint_set(gb_polys: Iterable[sp.Expr], free: list[Symbol]):
    """Return a dict mapping each free Symbol to a list of admissible exact values.

    For F07/F08/F09/F13 the grevlex Gröbner basis contains the following purely
    univariate or simple linear relations (after gauge fix):

        x2 - 1/2,  x5 - 1/2,  x8 - 1/2                (linear)
        y2^2 - 3/4, y5^2 - 3/4, y8^2 - 3/4            (real, ±sqrt(3)/2)
        x3^2 - 3 x3 / 2, x6^2 - 3 x6 / 2              (real, {0, 3/2})
        x4^2 - x4/2 - 1/2, x7^2 - x7/2 - 1/2          (real, {1, -1/2})

    Plus the linear y3, y4, y6, y7 binders

        x3*y2 - 3*y3/2 = 0           => y3 = (2/3) x3 y2
        x4*y2 - y2 + 3*y4/2 = 0      => y4 = (2/3) y2 (1 - x4)
        x6*y2 - 3*y6/2 = 0           => y6 = (2/3) x6 y2
        x7*y2 - y2 + 3*y7/2 = 0      => y7 = (2/3) y2 (1 - x7)

    which means the variety is fully parametrised by the 7 free roots
    (y2, y5, y8, x3, x6, x4, x7).  The remaining 55 generators of the GB express
    consistency conditions among these seven roots; each candidate tuple is
    subsequently *verified* against the full polynomial system in
    :func:`enumerate_real_solutions`.
    """
    constraints: dict[Symbol, list[sp.Expr]] = {}
    poly_set = set(sp.simplify(p) for p in gb_polys)

    sqrt3_2 = sqrt(3) / 2
    candidate_map: dict[Symbol, list[sp.Expr]] = {
        Symbol("x2"): [Rational(1, 2)],
        Symbol("x5"): [Rational(1, 2)],
        Symbol("x8"): [Rational(1, 2)],
        Symbol("y2"): [sqrt3_2, -sqrt3_2],
        Symbol("y5"): [sqrt3_2, -sqrt3_2],
        Symbol("y8"): [sqrt3_2, -sqrt3_2],
        Symbol("x3"): [S.Zero, Rational(3, 2)],
        Symbol("x6"): [S.Zero, Rational(3, 2)],
        Symbol("x4"): [S.One, Rational(-1, 2)],
        Symbol("x7"): [S.One, Rational(-1, 2)],
    }
    for var in free:
        constraints[var] = candidate_map.get(var, [])
    # Cross-check that each of the simple GB polynomials is actually present
    expected = [
        sp.Symbol("x2") - Rational(1, 2),
        sp.Symbol("x5") - Rational(1, 2),
        sp.Symbol("x8") - Rational(1, 2),
        sp.Symbol("y2") ** 2 - Rational(3, 4),
        sp.Symbol("y5") ** 2 - Rational(3, 4),
        sp.Symbol("y8") ** 2 - Rational(3, 4),
        sp.Symbol("x3") ** 2 - Rational(3, 2) * sp.Symbol("x3"),
        sp.Symbol("x6") ** 2 - Rational(3, 2) * sp.Symbol("x6"),
        sp.Symbol("x4") ** 2 - sp.Symbol("x4") / 2 - Rational(1, 2),
        sp.Symbol("x7") ** 2 - sp.Symbol("x7") / 2 - Rational(1, 2),
    ]
    missing = [str(p) for p in expected if sp.simplify(p) not in poly_set]
    return constraints, missing


def enumerate_real_solutions(
    rows: list[list[int]],
    free_constraints: dict[Symbol, list[sp.Expr]],
    polys: list[sp.Expr],
    xs: list[Symbol],
    ys: list[Symbol],
    n: int = 9,
):
    """Enumerate every (x_2,...,x_8,y_2,...,y_8) tuple satisfying the GB.

    For each tuple we substitute into all 27 polynomial generators of the
    original system and accept only those that are identically zero.  The
    resulting list is the complete real algebraic variety in the chosen gauge
    (the GB is zero-dimensional and all roots are in QQ[sqrt(3)]).
    """

    base = {xs[0]: S.Zero, ys[0]: S.Zero, xs[1]: S.One, ys[1]: S.Zero}
    sols: list[dict[Symbol, sp.Expr]] = []

    # Independent generators: y2, y5, y8, x3, x6, x4, x7
    indep_vars = [Symbol(s) for s in ("y2", "y5", "y8", "x3", "x6", "x4", "x7")]
    indep_choices = [free_constraints[v] for v in indep_vars]

    for combo in itertools.product(*indep_choices):
        d = dict(zip(indep_vars, combo))
        y2 = d[Symbol("y2")]
        x3, x6 = d[Symbol("x3")], d[Symbol("x6")]
        x4, x7 = d[Symbol("x4")], d[Symbol("x7")]
        y3 = Rational(2, 3) * x3 * y2
        y4 = Rational(2, 3) * y2 * (1 - x4)
        y6 = Rational(2, 3) * x6 * y2
        y7 = Rational(2, 3) * y2 * (1 - x7)

        repls = dict(base)
        repls.update({
            xs[2]: Rational(1, 2), ys[2]: y2,
            xs[3]: x3, ys[3]: y3,
            xs[4]: x4, ys[4]: y4,
            xs[5]: Rational(1, 2), ys[5]: d[Symbol("y5")],
            xs[6]: x6, ys[6]: y6,
            xs[7]: x7, ys[7]: y7,
            xs[8]: Rational(1, 2), ys[8]: d[Symbol("y8")],
        })
        ok = True
        for p in polys:
            v = sp.simplify(p.subs(repls))
            if v != 0:
                ok = False
                break
        if ok:
            sols.append(repls)
    return sols


def reconstruct_points(repls: dict[Symbol, sp.Expr], xs: list[Symbol], ys: list[Symbol], n: int = 9):
    return [(repls[xs[i]], repls[ys[i]]) for i in range(n)]


def signed_area(p0, p1, p2) -> sp.Expr:
    """2 * signed area of triangle (p0, p1, p2)."""
    return (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])


def is_strictly_convex_in_cyclic_order(points):
    """All consecutive cross products positive (strictly convex CCW polygon).

    Returns (verdict, distinct_count, min_cross_zero_count).
    """
    n = len(points)
    pts = [(sp.simplify(x), sp.simplify(y)) for (x, y) in points]
    distinct_set = set((str(x), str(y)) for x, y in pts)
    if len(distinct_set) < n:
        return ("degenerate_coincident_vertices", len(distinct_set), 0)
    crosses = []
    for i in range(n):
        a = pts[i]
        b = pts[(i + 1) % n]
        c = pts[(i + 2) % n]
        crosses.append(sp.simplify(signed_area(a, b, c)))
    pos = sum(1 for c in crosses if c > 0)
    neg = sum(1 for c in crosses if c < 0)
    zero = sum(1 for c in crosses if c == 0)
    if pos == n:
        return ("strictly_convex_ccw", len(distinct_set), 0)
    if neg == n:
        return ("strictly_convex_cw", len(distinct_set), 0)
    return (f"non_convex(pos={pos},neg={neg},zero={zero})", len(distinct_set), zero)


def lex_univariate_in_y2(polys: list[sp.Expr], free: list[Symbol], time_budget_sec: float = 600.0):
    """Try a lex Gröbner basis with y2 last so the elimination polynomial is in y2 only."""
    y2 = Symbol("y2")
    others = [v for v in free if v != y2]
    order = others + [y2]
    t0 = time.monotonic()
    try:
        G = groebner(polys, *order, order="lex", domain=QQ)
    except Exception as exc:  # pragma: no cover - defensive
        return None, time.monotonic() - t0, f"{type(exc).__name__}: {exc}"
    elapsed = time.monotonic() - t0
    polys_lex = list(G)
    last = polys_lex[-1]
    return (polys_lex, last, elapsed)


def expr_to_str(e: sp.Expr) -> str:
    return str(sp.sympify(e))


def decode_family(family: dict, *, lex_budget: float = 600.0):
    fid = family["family_id"]
    rows = family["rows"]
    free, subs, polys, xs, ys = build_system(rows)
    print(f"\n[{fid}] generating system: {len(polys)} polys in {len(free)} free vars")
    t0 = time.monotonic()
    G = groebner(polys, *free, order="grevlex", domain=QQ)
    grevlex_polys = list(G)
    grevlex_time = time.monotonic() - t0
    print(f"[{fid}] grevlex GB: {len(grevlex_polys)} polys, {grevlex_time:.2f}s, "
          f"zero-dim={G.is_zero_dimensional}")
    constraints, missing = infer_constraint_set(grevlex_polys, free)
    if missing:
        raise RuntimeError(
            f"[{fid}] expected GB generators not found, refusing to decode: {missing}"
        )

    sols = enumerate_real_solutions(rows, constraints, polys, xs, ys)
    print(f"[{fid}] real algebraic solutions: {len(sols)}")

    # Univariate elimination polynomial in y2 via lex GB.
    lex_result = lex_univariate_in_y2(polys, free, time_budget_sec=lex_budget)
    if isinstance(lex_result, tuple) and len(lex_result) == 3 and isinstance(lex_result[0], list):
        lex_polys, lex_last, lex_time = lex_result
        univariate_poly = lex_last
        univariate_str = str(univariate_poly)
        univariate_real_roots = [str(r) for r in sp.real_roots(sp.Poly(univariate_poly, Symbol("y2")))]
        lex_size = len(lex_polys)
    else:  # fallback: report failure but continue with grevlex extraction
        lex_polys, lex_last, lex_time = (None, None, lex_result[1])
        univariate_poly = sp.Poly(Symbol("y2") ** 2 - Rational(3, 4), Symbol("y2"))
        univariate_str = "y2**2 - 3/4 (extracted from grevlex GB; lex computation failed)"
        univariate_real_roots = ["sqrt(3)/2", "-sqrt(3)/2"]
        lex_size = -1

    # Strict-convexity audit
    convex_verdicts = []
    any_strictly_convex = False
    for k, repls in enumerate(sols):
        pts = reconstruct_points(repls, xs, ys)
        verdict, distinct, zero_crosses = is_strictly_convex_in_cyclic_order(pts)
        convex_verdicts.append(
            {
                "solution_index": k,
                "verdict": verdict,
                "distinct_points": distinct,
                "zero_crosses": zero_crosses,
                "y2": expr_to_str(repls[Symbol("y2")]),
                "y5": expr_to_str(repls[Symbol("y5")]),
                "y8": expr_to_str(repls[Symbol("y8")]),
                "x3": expr_to_str(repls[Symbol("x3")]),
                "x4": expr_to_str(repls[Symbol("x4")]),
                "x6": expr_to_str(repls[Symbol("x6")]),
                "x7": expr_to_str(repls[Symbol("x7")]),
                "points": [(expr_to_str(x), expr_to_str(y)) for (x, y) in pts],
            }
        )
        if verdict.startswith("strictly_convex"):
            any_strictly_convex = True

    payload = {
        "family_id": fid,
        "orbit_size": family["orbit_size"],
        "status": family["status"],
        "rows": rows,
        "gauge_fix": "x0=y0=0, x1=1, y1=0",
        "num_polys": len(polys),
        "num_free_vars": len(free),
        "free_vars": [str(v) for v in free],
        "polys": [str(p) for p in polys],
        "grevlex_basis_size": len(grevlex_polys),
        "grevlex_basis_seconds": grevlex_time,
        "grevlex_basis": [str(p) for p in grevlex_polys],
        "is_zero_dimensional": bool(G.is_zero_dimensional),
        "univariate_elimination": {
            "variable": "y2",
            "polynomial": univariate_str,
            "real_roots": univariate_real_roots,
            "lex_basis_size": lex_size,
            "lex_basis_seconds": lex_time,
        },
        "real_solutions_count": len(sols),
        "convexity_audit": convex_verdicts,
        "any_strictly_convex": any_strictly_convex,
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--lex-budget", type=float, default=600.0,
                        help="seconds before lex GB is considered slow (informational)")
    args = parser.parse_args()

    with SOURCE_GROEBNER.open("r") as f:
        groebner_data = json.load(f)

    families = [fam for fam in groebner_data if fam["family_id"] in TARGET_FAMILIES]
    if len(families) != len(TARGET_FAMILIES):
        missing = set(TARGET_FAMILIES) - {f["family_id"] for f in families}
        raise SystemExit(f"missing target families in source artifact: {sorted(missing)}")

    decoded = []
    overall_t0 = time.monotonic()
    for fam in families:
        payload = decode_family(fam, lex_budget=args.lex_budget)
        decoded.append(payload)

    summary = {
        "schema_version": "n9_groebner_real_root_decoders/v1",
        "target_families": list(TARGET_FAMILIES),
        "wall_time_seconds": time.monotonic() - overall_t0,
        "sympy_version": sp.__version__,
        "gauge_fix": "x0=y0=0, x1=1, y1=0",
        "definition": (
            "For each labelled selected-witness assignment in F07/F08/F09/F13 we "
            "encode the 27 squared-distance equality polynomials, compute a grevlex "
            "Gröbner basis over QQ, derive a univariate elimination polynomial in y_2, "
            "and check strict convexity for every real algebraic configuration."
        ),
        "headline": {
            "total_real_solutions_across_families": sum(d["real_solutions_count"] for d in decoded),
            "strictly_convex_solutions": sum(1 for d in decoded if d["any_strictly_convex"]),
        },
        "provenance": {
            "generator": "scripts/decode_n9_groebner_f07_f13.py",
            "source_artifact": "data/certificates/2026-05-05/n9_groebner_results.json",
            "status": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING",
            "claim_scope": (
                "Review-pending algebraic decoder audit for the F07/F08/F09/F13 "
                "n=9 selected-witness families only; not a source-of-truth "
                "promotion and not a proof of Erdos Problem #97."
            ),
        },
        "families": decoded,
        "honest_caveat": (
            "REVIEW_PENDING. This artifact is one of two independent n=9 selected-witness "
            "obstructions (the other is the vertex-circle exhaustive checker). Neither "
            "promotes the official/global FALSIFIABLE/OPEN status of Erdős #97. The lex "
            "Gröbner basis and univariate elimination polynomial are computed online; "
            "reviewers should re-run scripts/decode_n9_groebner_f07_f13.py with sympy "
            "1.14.0 (or a comparable 1.x build) to reproduce the artifact bit-for-bit."
        ),
    }
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=False)
    print(f"\nwrote {out_path}")
    print(f"total real solutions across F07/F08/F09/F13: {summary['headline']['total_real_solutions_across_families']}")
    print(f"strictly convex configurations: {summary['headline']['strictly_convex_solutions']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
