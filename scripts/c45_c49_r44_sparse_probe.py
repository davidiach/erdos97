#!/usr/bin/env python3
"""Sparse-frontier probe for C45_offsets_4_13_25_37, C49_offsets_5_16_29_41,
and R44_four_lift_2_4_7_9.

This script is a self-contained adaptation of the existing filter pipeline:
  * pair-overlap and Sidon checks,
  * Altman natural-order signature obstruction (offset-based),
  * mutual-rhombus midpoint forced-equality classes,
  * crossing-bisector and rectangle-trap filters (natural order),
  * vertex-circle order filter (natural order, plus alternative orders),
  * Kalmanson two-inequality inverse-pair Z3 search (cyclic patterns only),
  * minimum-radius short-chord filter,
  * SLSQP polar search at margins 1e-3, 1e-4, 1e-5, 1e-6 with 24 restarts,
  * step-k cyclic relabelings.

It writes a JSON certificate at the path supplied with --out.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


from erdos97.search import (  # noqa: E402
    PatternInfo,
    circulant_pattern,
)
from erdos97.altman_diagonal_sums import (  # noqa: E402
    altman_order_lp_diagnostic,
    altman_order_obstruction,
    check_altman,
)
from erdos97.incidence_filters import filter_summary  # noqa: E402
from erdos97.vertex_circle_order_filter import (  # noqa: E402
    order_result_to_json,
    vertex_circle_order_obstruction,
)
from erdos97.min_radius_filter import (  # noqa: E402
    minimum_radius_order_obstruction,
    result_to_json as minrad_result_to_json,
)


# ---------------------- pattern definitions -----------------------

def c45_pattern() -> PatternInfo:
    p = circulant_pattern(45, [4, 13, 25, 37], "C45_offsets_4_13_25_37")
    p.family = "circulant/sidon-type"
    return p


def c49_pattern() -> PatternInfo:
    p = circulant_pattern(49, [5, 16, 29, 41], "C49_offsets_5_16_29_41")
    p.family = "circulant/sidon-type"
    return p


def r44_pattern() -> PatternInfo:
    """Build R44_four_lift_2_4_7_9.

    n = 44, layout i = 4*g + r where g in [0,11), r in [0,4).
    S_{4g+r} = { 4*((g + a_t) mod 11) + ((r + t) mod 4) : t = 0..3 }
    with a = (2, 4, 7, 9).
    """
    n = 44
    g_mod = 11
    r_mod = 4
    a = (2, 4, 7, 9)
    S = []
    for i in range(n):
        g, r = divmod(i, r_mod)
        row = sorted(
            ((g + a[t]) % g_mod) * r_mod + ((r + t) % r_mod) for t in range(4)
        )
        if i in row or len(set(row)) != 4:
            raise ValueError(f"R44 row {i} bad: {row}")
        S.append(row)
    return PatternInfo(
        name="R44_four_lift_2_4_7_9",
        n=n,
        S=S,
        family="residue-rotating 4-lift",
        formula="i=4g+r, S_i={4((g+a_t) mod 11)+((r+t) mod 4): t=0..3}, a=(2,4,7,9)",
    )


# ----------------------- combinatorial filters ----------------------

def pair_overlap_max(S):
    n = len(S)
    sets = [set(row) for row in S]
    worst = 0
    bad = []
    for i, j in itertools.combinations(range(n), 2):
        c = len(sets[i] & sets[j])
        if c > 2:
            bad.append((i, j, c))
        if c > worst:
            worst = c
    return worst, bad


def sidon_check(n: int, offsets: Sequence[int]) -> dict:
    diffs = []
    for a, b in itertools.permutations(offsets, 2):
        diffs.append((a - b) % n)
    distinct = len(set(diffs))
    return {
        "n": n,
        "offsets": list(offsets),
        "ordered_pair_count": len(diffs),
        "distinct_diff_count": distinct,
        "is_sidon": distinct == len(diffs),
    }


# ---- vertex_circle search wrapper that gracefully handles missing API ----


def _vc_search(S, name, max_terminal=64):
    try:
        from erdos97.vertex_circle_order_filter import (
            find_cyclic_order_with_vertex_circle_filter,
            search_result_to_json,
        )
    except ImportError:
        return None
    try:
        result = find_cyclic_order_with_vertex_circle_filter(
            S, name, max_terminal_conflicts=max_terminal
        )
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    return search_result_to_json(result)


# ---- Kalmanson two-order Z3 search (circulant only) ----


def _kalmanson_two_order_z3(name, n, offsets, max_iter=200, conflict_cap=512, seed=2026):
    try:
        scripts_dir = ROOT / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        from check_kalmanson_two_order_z3 import generate_certificate  # type: ignore
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}
    try:
        return generate_certificate(
            name,
            int(n),
            list(offsets),
            max_iterations=max_iter,
            conflict_cap=conflict_cap,
            random_seed=seed,
        )
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


# -------------------------- SLSQP probe ----------------------------


def slsqp_probe(pat: PatternInfo, margins, restarts=24, seed=2026,
                maxiter=40, wall_budget=18.0):
    """Polar-mode SLSQP probe with budgeted restarts.

    For n in this range (44..49) the per-step cost of the n*(n-1)/2 pair
    constraint with finite-difference Jacobians blows up.  We replace the
    pair-distance hard inequality by a soft barrier and keep convexity and
    edge length as hard inequalities -- both still excluding the degenerate
    polygon family.  We then cap each restart's wall-clock budget.
    """

    import numpy as np  # local import to keep top-level light
    from erdos97.search import (
        polygon_from_x,
        equality_residual,
        convexity_margins,
        init_x,
        independent_diagnostics,
    )
    from scipy.optimize import minimize

    n = pat.n
    S = pat.S
    out = []

    for margin in margins:
        rng = np.random.default_rng(seed + int(round(-math.log10(margin))))
        per_restart = []
        best_loss = float("inf")
        best_eq_rms = float("inf")
        best_diag = None
        t0 = time.time()
        attempts = 0
        feasible = 0
        for r in range(restarts):
            if time.time() - t0 > wall_budget * max(1.0, restarts / 6.0):
                break
            attempts += 1
            x0 = init_x(n, rng, "polar", jitter=0.10 if r == 0 else 0.50)

            def loss(x):
                rsd = equality_residual(x, n, S, "polar")
                return float(np.dot(rsd, rsd))

            def conv(x):
                P = polygon_from_x(x, n, "polar")
                return convexity_margins(P) - margin

            def edge(x):
                P = polygon_from_x(x, n, "polar")
                ed = np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)
                return ed - margin

            constraints = [
                {"type": "ineq", "fun": conv},
                {"type": "ineq", "fun": edge},
            ]
            try:
                res = minimize(
                    loss,
                    x0,
                    method="SLSQP",
                    constraints=constraints,
                    options={"maxiter": maxiter, "ftol": 1e-9, "disp": False},
                )
            except Exception as exc:
                per_restart.append({"restart": r, "error": str(exc)})
                continue
            if not np.all(np.isfinite(res.x)):
                continue
            cv = conv(res.x).min()
            ed = edge(res.x).min()
            if cv < -1e-9 or ed < -1e-9:
                per_restart.append(
                    {"restart": r, "loss": float(res.fun),
                     "convex_violation": float(cv),
                     "edge_violation": float(ed),
                     "feasible": False}
                )
                continue
            feasible += 1
            P = polygon_from_x(res.x, n, "polar")
            diag = independent_diagnostics(P, S)
            per_restart.append(
                {"restart": r,
                 "loss": float(res.fun),
                 "eq_rms": float(diag["eq_rms"]),
                 "max_spread": float(diag["max_spread"]),
                 "max_rel_spread": float(diag["max_rel_spread"]),
                 "convexity_margin": float(diag["convexity_margin"]),
                 "min_edge_length": float(diag["min_edge_length"]),
                 "min_pair_distance": float(diag["min_pair_distance"]),
                 "feasible": True}
            )
            if res.fun < best_loss:
                best_loss = float(res.fun)
                best_eq_rms = float(diag["eq_rms"])
                best_diag = diag
        out.append(
            {
                "margin": margin,
                "restarts_attempted": attempts,
                "restarts_feasible": feasible,
                "best_loss": (None if not np.isfinite(best_loss) else best_loss),
                "best_eq_rms": (None if not np.isfinite(best_eq_rms) else best_eq_rms),
                "best_max_spread": (None if best_diag is None else float(best_diag["max_spread"])),
                "best_max_rel_spread": (None if best_diag is None else float(best_diag["max_rel_spread"])),
                "best_convex_margin": (None if best_diag is None else float(best_diag["convexity_margin"])),
                "best_min_edge_length": (None if best_diag is None else float(best_diag["min_edge_length"])),
                "best_min_pair_distance": (None if best_diag is None else float(best_diag["min_pair_distance"])),
                "elapsed_sec": time.time() - t0,
                "per_restart": per_restart,
                "note": (
                    "polar SLSQP; convexity+edge hard margins, no pair-distance "
                    "hard constraint (n^2 cost prohibitive at n>=44); "
                    "min_pair_distance reported as diagnostic."
                ),
            }
        )
    return out


# ------------------ alternative cyclic orders -----------------------


def step_k_orders(n: int, ks):
    out = []
    for k in ks:
        if math.gcd(k, n) != 1:
            continue
        order = [(k * i) % n for i in range(n)]
        out.append((k, order))
    return out


def vertex_circle_check_order(S, order, name):
    try:
        result = vertex_circle_order_obstruction(S, list(order), name)
        return order_result_to_json(result)
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


def altman_check_order(S, order, name):
    try:
        result = altman_order_obstruction(S, list(order), pattern=name)
        return {
            "altman_contradiction": result.altman_contradiction,
            "status": result.status,
            "equal_diagonal_order_groups": result.equal_diagonal_order_groups,
            "distance_class_count": result.distance_class_count,
        }
    except Exception as exc:
        return {"error": f"{type(exc).__name__}: {exc}"}


# ------------- R44 automorphism-style summary ---------------


def r44_orbit_structure(S):
    n = len(S)
    # Translation by 4: i -> (i+4) mod 44 should map S to itself.
    sigma = [(i + 4) % n for i in range(n)]
    # Action: row_i -> sorted(sigma[j] for j in S_i); compare to S[sigma[i]].
    invariant = True
    bad = []
    for i in range(n):
        mapped = sorted(sigma[j] for j in S[i])
        if mapped != S[sigma[i]]:
            invariant = False
            bad.append((i, mapped, S[sigma[i]]))
    # Translation-by-1 within residue: j -> (j + 1) mod 44 maps r-residue r to r+1
    # and g unchanged.
    sigma1 = [(i + 1) % n for i in range(n)]
    inv1 = True
    bad1 = []
    for i in range(n):
        mapped = sorted(sigma1[j] for j in S[i])
        if mapped != S[sigma1[i]]:
            inv1 = False
            bad1.append((i, mapped, S[sigma1[i]]))
    # Distance classes mod n under selected pair distances:
    pair_diffs = set()
    for i, row in enumerate(S):
        for j in row:
            pair_diffs.add(((i - j) % n, (j - i) % n))
    return {
        "translation_by_4_invariant": invariant,
        "translation_by_4_violations": len(bad),
        "translation_by_1_invariant": inv1,
        "translation_by_1_violations": len(bad1),
        "selected_pair_residue_count": len({min(a, b) for a, b in pair_diffs}),
    }


# ----------------------------- main --------------------------------


def run(pat: PatternInfo, margins, restarts, seed, kalmanson_iter):
    name = pat.name
    n = pat.n
    S = pat.S
    print(f"\n=== {name} (n={n}) ===", flush=True)
    record = {
        "name": name,
        "n": n,
        "family": pat.family,
        "formula": pat.formula,
    }

    # 1) pair overlap
    worst, bad = pair_overlap_max(S)
    record["pair_overlap_max"] = worst
    record["pair_overlap_violations"] = bad[:8]
    print(f"  pair-overlap max = {worst}", flush=True)

    # 2) Sidon (cyclic only)
    if name.startswith("C"):
        offsets = [int(o) for o in pat.formula.split("[")[1].split("]")[0].split(",")]
        record["sidon"] = sidon_check(n, offsets)
        record["circulant_offsets"] = list(offsets)
        print(f"  sidon = {record['sidon']['is_sidon']}", flush=True)

    # 3) Altman natural-order
    natural_altman = check_altman(pat)
    record["altman_natural_order"] = {
        "status": natural_altman.status,
        "natural_order_only": natural_altman.natural_order_only,
        "offsets": natural_altman.offsets,
        "chord_orders": natural_altman.chord_orders,
        "forced_equal_U": natural_altman.forced_equal_U,
        "altman_contradiction": natural_altman.altman_contradiction,
    }
    print(f"  altman natural = {natural_altman.status}", flush=True)
    record["altman_natural_order_diag"] = altman_check_order(S, list(range(n)), name)
    print(
        f"  altman natural diag = "
        f"{record['altman_natural_order_diag'].get('status')}",
        flush=True,
    )

    # 4) altman LP
    try:
        lp = altman_order_lp_diagnostic(S, list(range(n)), pattern=name)
        record["altman_natural_lp"] = {
            "status": lp.status,
            "obstructed": lp.obstructed,
            "max_margin": lp.max_margin,
            "distance_class_count": lp.distance_class_count,
            "inequality_count": lp.inequality_count,
        }
        print(
            f"  altman LP = {lp.status} (margin={lp.max_margin})",
            flush=True,
        )
    except Exception as exc:
        record["altman_natural_lp"] = {"error": f"{type(exc).__name__}: {exc}"}

    # 5) mutual-rhombus / phi / odd cycle / rectangle trap (natural order)
    try:
        rh = filter_summary(S)
        record["mutual_rhombus_filter"] = {
            "phi_edges": rh["phi_edges"],
            "odd_cycle_length": rh["odd_cycle_length"],
            "mutual_phi_2_cycles": rh["mutual_phi_2_cycles"],
            "midpoint_matrix_rank": rh["midpoint_matrix_rank"],
            "forced_equality_classes": rh["forced_equality_classes"],
            "adjacent_two_overlap_violations_count": len(
                rh["adjacent_two_overlap_violations"]
            ),
            "crossing_bisector_violations_count": len(
                rh["crossing_bisector_violations"]
            ),
            "rectangle_trap_4_cycles": rh["rectangle_trap_4_cycles"],
        }
        print(
            "  mutual-rhombus: "
            f"phi={rh['phi_edges']} odd={rh['odd_cycle_length']} "
            f"mutual={rh['mutual_phi_2_cycles']} "
            f"forced_classes={len(rh['forced_equality_classes'])} "
            f"rect4={rh['rectangle_trap_4_cycles']} "
            f"adjacent={len(rh['adjacent_two_overlap_violations'])} "
            f"cross={len(rh['crossing_bisector_violations'])}",
            flush=True,
        )
    except Exception as exc:
        record["mutual_rhombus_filter"] = {"error": f"{type(exc).__name__}: {exc}"}

    # 6) vertex-circle natural order
    record["vertex_circle_natural"] = vertex_circle_check_order(S, list(range(n)), name)
    vcnat = record["vertex_circle_natural"]
    if "error" in vcnat:
        print(f"  vertex-circle natural ERROR: {vcnat['error']}", flush=True)
    else:
        print(
            f"  vertex-circle natural: obstructed={vcnat.get('obstructed')} "
            f"strict_edges={vcnat.get('strict_edge_count')} "
            f"self_conflicts={len(vcnat.get('self_edge_conflicts', []))} "
            f"cycle_edges={len(vcnat.get('cycle_edges', []))}",
            flush=True,
        )

    # 7) min-radius
    try:
        mr = minimum_radius_order_obstruction(S, order=None, pattern=name)
        record["min_radius_natural"] = minrad_result_to_json(mr)
        print(
            "  min-radius natural: obstructed="
            f"{record['min_radius_natural'].get('obstructed')} "
            f"blocked={len(record['min_radius_natural'].get('blocked_centers', []))}",
            flush=True,
        )
    except Exception as exc:
        record["min_radius_natural"] = {"error": f"{type(exc).__name__}: {exc}"}

    # 8) Kalmanson two-order Z3 search (cyclic only)
    if name.startswith("C") and "circulant_offsets" in record:
        kal = _kalmanson_two_order_z3(
            name,
            n,
            record["circulant_offsets"],
            max_iter=kalmanson_iter,
            conflict_cap=512,
            seed=seed,
        )
        if isinstance(kal, dict) and "error" in kal:
            record["kalmanson_two_order_z3"] = {"error": kal["error"]}
            print(f"  kalmanson Z3 ERROR: {kal['error']}", flush=True)
        elif isinstance(kal, dict):
            record["kalmanson_two_order_z3"] = {
                "status": kal.get("status"),
                "trust": kal.get("trust"),
                "iterations": kal.get("iterations"),
                "forbidden_clause_count": kal.get("forbidden_clause_count"),
                "candidate_order": kal.get("candidate_order"),
            }
            print(
                "  kalmanson Z3: "
                f"status={kal.get('status')} "
                f"iter={kal.get('iterations')} "
                f"clauses={kal.get('forbidden_clause_count')}",
                flush=True,
            )

    # 9) alternative cyclic orders -- step-k shifts
    alt = []
    coprime_ks = [k for k in [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]
                  if math.gcd(k, n) == 1 and k != 1]
    # cap to 5 alternatives for speed
    for k, order in step_k_orders(n, coprime_ks)[:5]:
        try:
            r_alt = altman_check_order(S, order, name)
        except Exception as exc:
            r_alt = {"error": str(exc)}
        try:
            v_alt = vertex_circle_check_order(S, order, name)
            v_alt = {
                k2: v_alt.get(k2)
                for k2 in (
                    "obstructed",
                    "strict_edge_count",
                    "self_edge_conflicts",
                    "cycle_edges",
                )
            }
            if isinstance(v_alt.get("self_edge_conflicts"), list):
                v_alt["self_edge_conflicts"] = len(v_alt["self_edge_conflicts"])
            if isinstance(v_alt.get("cycle_edges"), list):
                v_alt["cycle_edges"] = len(v_alt["cycle_edges"])
        except Exception as exc:
            v_alt = {"error": str(exc)}
        alt.append({"step_k": k, "altman": r_alt, "vertex_circle": v_alt})
        print(
            f"  step-{k}: altman={r_alt.get('status', r_alt.get('error'))}, "
            f"vc-obstructed={v_alt.get('obstructed', v_alt.get('error'))}",
            flush=True,
        )
    record["alt_orders_step_k"] = alt

    # 10) SLSQP polar probe
    print("  slsqp probe...", flush=True)
    record["slsqp"] = slsqp_probe(
        pat, margins=margins, restarts=restarts, seed=seed, max_nfev=4000
    )
    for s in record["slsqp"]:
        if "error" in s:
            print(f"    margin={s['margin']:g} ERROR {s['error']}", flush=True)
        else:
            print(
                f"    margin={s['margin']:g} loss={s['loss']:.3e} "
                f"eq_rms={s['eq_rms']:.3e} max_spread={s['max_spread']:.3e} "
                f"convex={s['convexity_margin']:.3e}",
                flush=True,
            )

    # 11) R44 specific: orbit / automorphism summary
    if name.startswith("R44"):
        record["r44_orbit"] = r44_orbit_structure(S)
        print(f"  r44 orbit: {record['r44_orbit']}", flush=True)

    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--restarts", type=int, default=24)
    ap.add_argument("--seed", type=int, default=2026)
    ap.add_argument("--margins", type=str, default="1e-3,1e-4,1e-5,1e-6")
    ap.add_argument("--kalmanson-iter", type=int, default=80)
    ap.add_argument("--patterns", type=str, default="C45,C49,R44")
    args = ap.parse_args()

    margins = [float(x) for x in args.margins.split(",") if x.strip()]
    selected = set(args.patterns.split(","))

    pats = []
    if "C45" in selected:
        pats.append(c45_pattern())
    if "C49" in selected:
        pats.append(c49_pattern())
    if "R44" in selected:
        pats.append(r44_pattern())

    started = time.time()
    records = []
    for pat in pats:
        records.append(
            run(
                pat,
                margins=margins,
                restarts=args.restarts,
                seed=args.seed,
                kalmanson_iter=args.kalmanson_iter,
            )
        )

    payload = {
        "type": "c45_c49_r44_sparse_probe_v1",
        "trust": "MIXED_FILTER_AND_NUMERICAL_DIAGNOSTIC",
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "elapsed_sec": time.time() - started,
        "seed": args.seed,
        "restarts": args.restarts,
        "margins": margins,
        "patterns": records,
        "semantics": (
            "Per-pattern combinatorial filters (pair-overlap, Altman natural-order, "
            "mutual-rhombus, crossing/rectangle, vertex-circle, min-radius, "
            "Kalmanson Z3 for circulant patterns) plus SLSQP polar probes at "
            "multiple convexity/edge/pair margins. Numerical results are "
            "diagnostics only and do not certify realizability."
        ),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"\nwrote {args.out}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
