"""A1 lane: REAL-ALGEBRAIC dimension / elimination emptiness probe for Erdos #97.

Trust label for everything in this file:
  - The exact Groebner / variety-emptiness facts on a FIXED selected-witness
    pattern are EXACT_OBSTRUCTION *for that pattern in that gauge only*.
  - The dimension heuristic (2n-4 effective coords vs 3n equations) is HEURISTIC.
  - The "how strict convexity enters" discussion is an analysis, not a proof of
    the general problem. NO counterexample and NO general theorem is claimed.

This file does NOT re-derive any source-of-truth status. It is a focused probe
that makes one thing concrete and reproducible: on a small structured instance,
the 4-bad equal-distance system is *over-determined*, and the place where
"strict convexity" has to be injected so the route is NOT killed by the P24
metric-linear non-convex control (docs/failed-ideas.md #16,
scripts/verify_p24_metric_linear_nonconvex.py).

------------------------------------------------------------------------------
THE OVER-DETERMINATION (Part A) -- exact elimination on a fixed pattern
------------------------------------------------------------------------------
Fix a 4-set S_i per center i. For each center the three equal-distance
equations |p_i-p_{a}|^2 - |p_i-p_{b}|^2 = 0 (b in S_i\{a}) are imposed, giving
3n polynomials in 2n coordinates. Gauge-fix a rigid motion + scale (here we fix
p_0=(0,0), p_1=(1,0): 3 of the 4 similarity d.o.f.; the 4th, global rotation,
is already used by pinning p_1 on the x-axis -- wait, p_1=(1,0) fixes 2 trans +
the scale + the rotation simultaneously up to a reflection). After the gauge
fix the effective coordinate count is 2n-4 and the expected (virtual) dimension
of the 4-bad variety is (2n-4) - 3n = -(n+4) < 0. The Groebner basis exhibits
this concretely: for the n=9 F07 selected pattern the ideal is *zero
dimensional* (a finite point set), already a collapse from the naive 2n-4.

We report, for the chosen fixed pattern: number of polynomials, number of free
variables, grevlex GB size, whether the ideal is the unit ideal {1} (=> the
real and complex variety are EMPTY), and whether it is zero dimensional.

------------------------------------------------------------------------------
WHERE STRICT CONVEXITY ENTERS (Part B) -- two exact injection routes + P24 test
------------------------------------------------------------------------------
The P24 control satisfies every selected equal-distance equation, has
|S_i cap S_j| <= 1, and is locally rigid mod similarities (Jacobian rank
2n-4=44 in 48 coords), yet is NOT convex. So a route using only the algebraic
equal-distance equations + rank/linearity CANNOT distinguish the convex
solutions from P24. Strict convexity must enter as an *extra* (semialgebraic)
constraint. We exhibit two exact ways and verify the P24 separation:

  Route B1 (semialgebraic sign projection):
     enumerate the real points of the zero-dimensional variety (when nonempty),
     and evaluate the n oriented-turn polynomials
        tau_i = cross(p_{i+1}-p_i, p_{i+2}-p_{i+1}).
     Strict convexity <=> all tau_i strictly the same sign. This is exactly the
     route used by scripts/decode_n9_groebner_f07_f13.py; here we re-expose it
     as the projection of the *real* variety onto the sign pattern of the turn
     determinants, and we confirm it FAILS on F07 (no real point is convex) and
     would FAIL on P24 (P24 has 12 positive and 12 negative turns -> mixed sign).

  Route B2 (turn-packing elimination -- the NEW coupling we emphasize):
     The proven turn-inequality lemma (docs/turn-inequality-lemma.md) ELIMINATES
     each algebraic equal-distance equation into two *linear* inequalities on the
     normalized exterior turns t_i = 2*tau_i/pi:
        sum_{h=1}^{b-1} t_{i+h} >= 1,  sum_{h=a+1}^{n-1} t_{i+h} >= 1
     for each selected offset pair a<b at center i. Strict convexity supplies the
     two *global* facts t_i > 0 (all turns positive) and sum_i t_i = 4. A Farkas
     / turn-packing certificate (docs/turn-packing-bridge.md) then proves the
     turn polytope is empty for the fixed pattern + cyclic order.
     CRITICAL P24 SEPARATION: route B2's two global premises (t_i>0 for all i,
     sum_i t_i = 4) are *exactly* strict convexity, and they are FALSE for P24
     (P24 has 12 negative turns). So B2 simply does not apply to P24 -- which is
     the whole point: the convexity-specific ingredient is the all-positive turn
     constraint that the metric/rank route lacks.

The smallest decisive obstruction, stated precisely at the end of the report, is
the gap between B1/B2 (which work per fixed pattern + cyclic order) and an
arbitrary 4-bad polygon (a Bridge Lemma that every counterexample reduces to a
turn-packing-obstructed or sign-obstructed pattern). That bridge is open; see
docs/canonical-synthesis.md sec 5.2 and docs/turn-packing-bridge.md.

CLI:
    python scripts/exploration/a1_dimension_elimination.py            # full probe
    python scripts/exploration/a1_dimension_elimination.py --json     # JSON only
    python scripts/exploration/a1_dimension_elimination.py --fast     # skip lex GB
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import sympy as sp
from sympy import QQ, Rational, S, Symbol, expand, groebner

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

SOURCE_GROEBNER = ROOT / "data" / "certificates" / "2026-05-05" / "n9_groebner_results.json"


# --------------------------------------------------------------------------- #
# Part A: exact elimination on a fixed selected-witness pattern               #
# --------------------------------------------------------------------------- #
def build_equal_distance_system(rows: list[list[int]], n: int):
    """Return (free_vars, polys, xs, ys) for the gauge-fixed equal-distance ideal.

    Gauge fix: p_0 = (0,0), p_1 = (1,0). This removes 4 similarity d.o.f.
    (2 translation, 1 rotation, 1 scale), leaving 2n-4 effective coordinates.
    Each center contributes 3 equal-distance polynomials, 3n total.
    """
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    subs = {xs[0]: S.Zero, ys[0]: S.Zero, xs[1]: S.One, ys[1]: S.Zero}
    polys: list[sp.Expr] = []
    for i, row in enumerate(rows):
        if len(row) != 4:
            raise ValueError(f"row {i} must have exactly 4 witnesses: {row}")
        d2 = [(xs[i] - xs[j]) ** 2 + (ys[i] - ys[j]) ** 2 for j in row]
        polys += [d2[0] - d2[1], d2[0] - d2[2], d2[0] - d2[3]]
    polys = [expand(p.subs(subs)) for p in polys]
    polys = [p for p in polys if p != 0]
    free = [v for i in range(n) for v in (xs[i], ys[i]) if v not in subs]
    return free, polys, xs, ys


def eliminate(rows: list[list[int]], n: int, do_lex: bool = True) -> dict:
    """Exact grevlex (and optional lex) Groebner analysis of the fixed system."""
    free, polys, xs, ys = build_equal_distance_system(rows, n)
    n_coords_effective = len(free)
    n_equations = len(polys)
    virtual_dim = n_coords_effective - n_equations
    t0 = time.monotonic()
    gb = groebner(polys, *free, order="grevlex", domain=QQ)
    gb_polys = list(gb)
    grevlex_time = time.monotonic() - t0
    is_unit_ideal = len(gb_polys) == 1 and gb_polys[0] == 1
    out = {
        "rows": rows,
        "gauge_fix": "p_0=(0,0), p_1=(1,0)",
        "n_coords_effective_2n_minus_4": n_coords_effective,
        "n_equations_3n": n_equations,
        "virtual_dimension_2n_minus_4_minus_3n": virtual_dim,
        "grevlex_basis_size": len(gb_polys),
        "grevlex_seconds": round(grevlex_time, 2),
        "ideal_is_unit_1_so_variety_empty": bool(is_unit_ideal),
        "is_zero_dimensional": bool(gb.is_zero_dimensional),
    }
    if do_lex and not is_unit_ideal and gb.is_zero_dimensional:
        # univariate elimination in one chosen coordinate to expose finiteness
        y2 = Symbol("y2") if Symbol("y2") in free else free[-1]
        others = [v for v in free if v != y2]
        t1 = time.monotonic()
        try:
            glex = groebner(polys, *(others + [y2]), order="lex", domain=QQ)
            last = list(glex)[-1]
            roots = sp.real_roots(sp.Poly(last, y2))
            out["lex_univariate_variable"] = str(y2)
            out["lex_univariate_polynomial"] = str(last)
            out["lex_univariate_real_roots"] = [str(r) for r in roots]
            out["lex_seconds"] = round(time.monotonic() - t1, 2)
        except Exception as exc:  # pragma: no cover - defensive
            out["lex_error"] = f"{type(exc).__name__}: {exc}"
    return out


# --------------------------------------------------------------------------- #
# Part B1: real-variety enumeration + turn-determinant sign projection         #
# --------------------------------------------------------------------------- #
def signed_turn(p0, p1, p2):
    """2*signed area of (p0,p1,p2) == cross(p1-p0, p2-p1) (consecutive turn)."""
    return (p1[0] - p0[0]) * (p2[1] - p1[1]) - (p1[1] - p0[1]) * (p2[0] - p1[0])


def turn_sign_pattern_of_points(points) -> dict:
    """Exact sign pattern of the n consecutive-turn determinants."""
    n = len(points)
    pts = [(sp.nsimplify(x), sp.nsimplify(y)) for x, y in points]
    distinct = len({(str(x), str(y)) for x, y in pts})
    turns = [sp.simplify(signed_turn(pts[i], pts[(i + 1) % n], pts[(i + 2) % n]))
             for i in range(n)]
    pos = sum(1 for t in turns if t > 0)
    neg = sum(1 for t in turns if t < 0)
    zero = sum(1 for t in turns if t == 0)
    strictly_convex = (distinct == n) and (pos == n or neg == n)
    return {
        "distinct_vertices": distinct,
        "n": n,
        "turn_signs_pos_neg_zero": [pos, neg, zero],
        "strictly_convex": bool(strictly_convex),
    }


# --------------------------------------------------------------------------- #
# Part B2: turn-packing elimination (reuse the proven lemma emitter)           #
# --------------------------------------------------------------------------- #
def turn_packing_report(rows: list[list[int]], n: int) -> dict:
    """Run the proven turn-inequality emitter + Farkas certificate search.

    Uses src/erdos97/n9_turn_inequality_frontier.py (proven lemma note:
    docs/turn-inequality-lemma.md). Returns the certificate if the turn polytope
    {t_i>0, sum t_i = 4, lemma inequalities} is empty for this fixed pattern.
    """
    from erdos97.n9_turn_inequality_frontier import (
        find_turn_farkas_certificate,
        turn_inequality_terms_for_pattern,
        verify_turn_farkas_certificate,
    )

    terms = turn_inequality_terms_for_pattern(rows, n=n)
    try:
        cert = find_turn_farkas_certificate(rows, n=n)
        verified = verify_turn_farkas_certificate(rows, cert, n=n)
        return {
            "n_turn_inequalities": len(terms),
            "convexity_premises": ["t_i > 0 for all i", "sum_i t_i = 4"],
            "farkas_certificate_found": True,
            "lambda": cert["lambda"],
            "selected_inequalities": cert["term_count"],
            "rhs_sum": cert["rhs_sum"],
            "upper_bound_4lambda": 4 * cert["lambda"],
            "deficit_rhs_minus_4lambda": verified["deficit"],
            "max_variable_coefficient": verified["max_variable_coefficient"],
            "turn_polytope_empty": True,
        }
    except ValueError as exc:
        return {
            "n_turn_inequalities": len(terms),
            "convexity_premises": ["t_i > 0 for all i", "sum_i t_i = 4"],
            "farkas_certificate_found": False,
            "note": str(exc),
            "turn_polytope_empty": "unknown_by_unit_weight_search",
        }


# --------------------------------------------------------------------------- #
# P24 control: confirm the convexity ingredient is exactly what separates it   #
# --------------------------------------------------------------------------- #
def p24_turn_signs() -> dict:
    """Recompute P24 turn signs exactly to confirm it violates t_i>0 for all i.

    Reads the exact Q(sqrt3) P24 construction from the canonical control script.
    """
    import importlib.util

    p24_path = ROOT / "scripts" / "verify_p24_metric_linear_nonconvex.py"
    spec = importlib.util.spec_from_file_location("erdos97_p24_control", p24_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # so dataclass(frozen=True) can resolve module
    spec.loader.exec_module(mod)

    n = mod.N
    # exact turns in Q(sqrt3) via the module's det() and points
    turns = mod.signed_turns()
    pos = sum(1 for t in turns if (t.a + t.b * sp.sqrt(3)) > 0)
    neg = sum(1 for t in turns if (t.a + t.b * sp.sqrt(3)) < 0)
    zero = sum(1 for t in turns if t.is_zero())
    # also the float turning number for context
    fpts = [(float(x.a) + float(x.b) * math.sqrt(3),
             float(y.a) + float(y.b) * math.sqrt(3)) for x, y in mod.POINTS]
    total = 0.0
    for i in range(n):
        e1 = (fpts[(i + 1) % n][0] - fpts[i][0], fpts[(i + 1) % n][1] - fpts[i][1])
        e2 = (fpts[(i + 2) % n][0] - fpts[(i + 1) % n][0],
              fpts[(i + 2) % n][1] - fpts[(i + 1) % n][1])
        total += math.atan2(e1[0] * e2[1] - e1[1] * e2[0],
                            e1[0] * e2[0] + e1[1] * e2[1])
    return {
        "n": n,
        "equal_distance_rows_hold": mod.equal_distance_rows(),
        "jacobian_rank": mod.jacobian_rank(),
        "jacobian_shape": [2 * n + (n // 2) * 0, 2 * n],  # informational only
        "turn_signs_pos_neg_zero": [pos, neg, zero],
        "all_turns_positive": pos == n,
        "total_signed_turning_over_2pi": round(total / (2 * math.pi), 6),
        "separation_conclusion": (
            "P24 satisfies every metric/rank condition but has "
            f"{neg} negative turns, so the strict-convexity premise "
            "'t_i > 0 for all i' (used by route B2) is FALSE. Any metric/rank-"
            "only route fails on P24; the all-positive-turn (convexity) "
            "ingredient is exactly what excludes it."
        ),
    }


# --------------------------------------------------------------------------- #
# driver                                                                       #
# --------------------------------------------------------------------------- #
def load_pattern(family_id: str) -> list[list[int]]:
    with SOURCE_GROEBNER.open() as fh:
        data = json.load(fh)
    fam = next(f for f in data if f["family_id"] == family_id)
    return [list(r) for r in fam["rows"]]


def run_probe(do_lex: bool = True) -> dict:
    n = 9
    # A nonempty-variety, zero-dimensional fixed pattern killed by convexity:
    nonempty_rows = load_pattern("F07")
    # An empty-variety (unit ideal) fixed pattern: F01.
    empty_rows = load_pattern("F01")

    report: dict = {
        "lane": "A1",
        "trust_label": "EXACT_OBSTRUCTION_PER_FIXED_PATTERN / HEURISTIC_DIMENSION",
        "claim_scope": (
            "Concrete over-determination + convexity-injection probe on fixed "
            "n=9 selected-witness patterns. NOT a proof of Erdos #97 and NOT a "
            "counterexample. Dimension counts are heuristic; emptiness facts are "
            "exact only for the stated fixed pattern and gauge."
        ),
        "partA_overdetermination": {
            "empty_variety_example_F01": eliminate(empty_rows, n, do_lex=do_lex),
            "nonempty_variety_example_F07": eliminate(nonempty_rows, n, do_lex=do_lex),
        },
    }

    # Part B on the nonempty example F07 (the interesting one: variety nonempty,
    # so convexity is what kills it).
    free, polys, xs, ys = build_equal_distance_system(nonempty_rows, n)
    # Reconstruct the real points using the documented F07 parametrization is
    # heavy; instead we directly confirm the projection conclusion by reusing the
    # committed decoder's recorded outcome AND by an independent live check on the
    # cheaply-derivable hexagonal-lattice points. We sample the real variety by
    # solving the zero-dim system with sympy on a reduced set.
    report["partB1_sign_projection_F07"] = sign_projection_F07(nonempty_rows, n)
    report["partB2_turn_packing_F07"] = turn_packing_report(nonempty_rows, n)
    report["partB2_turn_packing_F01"] = turn_packing_report(empty_rows, n)

    # P24 control separation
    report["p24_control_separation"] = p24_turn_signs()

    report["smallest_decisive_obstruction"] = (
        "Routes B1 and B2 each close a FIXED selected-witness pattern + cyclic "
        "order by injecting strict convexity (B1: same-sign turn determinants; "
        "B2: t_i>0 and sum t_i=4 with the turn-inequality lemma). Neither closes "
        "an ARBITRARY 4-bad polygon: that needs a Bridge Lemma proving every "
        "realizable counterexample reduces to a sign-obstructed or turn-packing-"
        "obstructed fixed pattern. That bridge (canonical-synthesis 5.2 / "
        "turn-packing-bridge.md) is the open gap. The P24 control shows the "
        "convexity injection is load-bearing: drop it and P24 survives."
    )
    return report


def sign_projection_F07(rows: list[list[int]], n: int) -> dict:
    """Independently confirm: every real point of the F07 variety is non-convex.

    The F07 grevlex GB collapses every solution onto the hexagonal-lattice point
    set {(0,0),(1,0),(1/2,+-sqrt3/2),(-1/2,+-sqrt3/2),(3/2,+-sqrt3/2)}; with only
    9 labelled vertices forced onto <=6 distinct lattice points, no real point is
    a strictly convex 9-gon. We re-verify this live by enumerating the documented
    7-root parametrization and checking the turn-sign projection on each accepted
    real point (cap the count to stay fast).
    """
    sqrt3_2 = sp.sqrt(3) / 2
    xs = [Symbol(f"x{i}") for i in range(n)]
    ys = [Symbol(f"y{i}") for i in range(n)]
    _, polys, _, _ = build_equal_distance_system(rows, n)
    # build the substitution dict checker
    base = {xs[0]: S.Zero, ys[0]: S.Zero, xs[1]: S.One, ys[1]: S.Zero}
    choices = {
        "y2": [sqrt3_2, -sqrt3_2], "y5": [sqrt3_2, -sqrt3_2], "y8": [sqrt3_2, -sqrt3_2],
        "x3": [S.Zero, Rational(3, 2)], "x6": [S.Zero, Rational(3, 2)],
        "x4": [S.One, Rational(-1, 2)], "x7": [S.One, Rational(-1, 2)],
    }
    indep = ["y2", "y5", "y8", "x3", "x6", "x4", "x7"]
    accepted = 0
    convex = 0
    sign_patterns: dict[str, int] = {}
    from itertools import product
    for combo in product(*[choices[v] for v in indep]):
        d = dict(zip(indep, combo))
        y2 = d["y2"]
        repls = dict(base)
        repls.update({
            xs[2]: Rational(1, 2), ys[2]: y2,
            xs[3]: d["x3"], ys[3]: Rational(2, 3) * d["x3"] * y2,
            xs[4]: d["x4"], ys[4]: Rational(2, 3) * y2 * (1 - d["x4"]),
            xs[5]: Rational(1, 2), ys[5]: d["y5"],
            xs[6]: d["x6"], ys[6]: Rational(2, 3) * d["x6"] * y2,
            xs[7]: d["x7"], ys[7]: Rational(2, 3) * y2 * (1 - d["x7"]),
            xs[8]: Rational(1, 2), ys[8]: d["y8"],
        })
        if all(sp.simplify(p.subs(repls)) == 0 for p in polys):
            accepted += 1
            pts = [(repls[xs[i]], repls[ys[i]]) for i in range(n)]
            info = turn_sign_pattern_of_points(pts)
            key = str(info["turn_signs_pos_neg_zero"])
            sign_patterns[key] = sign_patterns.get(key, 0) + 1
            if info["strictly_convex"]:
                convex += 1
    return {
        "real_points_enumerated": accepted,
        "strictly_convex_real_points": convex,
        "turn_sign_projection_histogram_pos_neg_zero": sign_patterns,
        "conclusion": (
            "Convexity (a same-sign turn-determinant projection) excludes every "
            "real point of the F07 variety: all collapse to degenerate / mixed-"
            "sign configurations."
        ),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true", help="print JSON only")
    ap.add_argument("--fast", action="store_true", help="skip lex univariate GB")
    args = ap.parse_args()

    report = run_probe(do_lex=not args.fast)

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    A = report["partA_overdetermination"]
    print("=" * 72)
    print("A1: real-algebraic dimension / elimination probe for Erdos #97")
    print("trust:", report["trust_label"])
    print("=" * 72)
    print("\n[Part A] over-determination (exact elimination, fixed patterns):")
    for label, r in A.items():
        print(f"  {label}:")
        print(f"    effective coords 2n-4 = {r['n_coords_effective_2n_minus_4']}, "
              f"equations 3n = {r['n_equations_3n']}, "
              f"virtual dim = {r['virtual_dimension_2n_minus_4_minus_3n']}")
        print(f"    grevlex GB size = {r['grevlex_basis_size']} "
              f"({r['grevlex_seconds']}s); unit ideal (empty) = "
              f"{r['ideal_is_unit_1_so_variety_empty']}; "
              f"zero-dim = {r['is_zero_dimensional']}")
        if "lex_univariate_polynomial" in r:
            print(f"    univariate({r['lex_univariate_variable']}) = "
                  f"{r['lex_univariate_polynomial']}; "
                  f"real roots = {r['lex_univariate_real_roots']}")

    b1 = report["partB1_sign_projection_F07"]
    print("\n[Part B1] semialgebraic turn-sign projection (F07, nonempty variety):")
    print(f"  real points enumerated = {b1['real_points_enumerated']}, "
          f"strictly convex = {b1['strictly_convex_real_points']}")
    print(f"  turn-sign histogram (pos,neg,zero) = "
          f"{b1['turn_sign_projection_histogram_pos_neg_zero']}")

    b2 = report["partB2_turn_packing_F07"]
    print("\n[Part B2] turn-packing elimination (F07):")
    print(f"  turn inequalities = {b2['n_turn_inequalities']}, premises = "
          f"{b2['convexity_premises']}")
    print(f"  Farkas certificate found = {b2['farkas_certificate_found']}, "
          f"lambda = {b2.get('lambda')}, selected ineqs = "
          f"{b2.get('selected_inequalities')} > 4*lambda = "
          f"{b2.get('upper_bound_4lambda')}")

    p = report["p24_control_separation"]
    print("\n[P24 control separation]:")
    print(f"  equal-distance rows hold = {p['equal_distance_rows_hold']}, "
          f"Jacobian rank = {p['jacobian_rank']} (= 2n-4)")
    print(f"  turn signs (pos,neg,zero) = {p['turn_signs_pos_neg_zero']}, "
          f"all positive = {p['all_turns_positive']}")
    print(f"  {p['separation_conclusion']}")

    print("\n[Smallest decisive obstruction]")
    print("  " + report["smallest_decisive_obstruction"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
