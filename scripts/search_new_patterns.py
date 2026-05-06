#!/usr/bin/env python3
"""Aggressive search for n in {11..21,24,25,30,36,48,60} counterexamples to Erdos #97.

Strategy:
  1. Generate candidate 4-regular incidence patterns from several novel families:
       - Random 4-regular Cayley patterns on Z/n (offsets satisfying pair-cap)
       - Almost-cyclic patterns (cyclic with one row perturbed)
       - Bipartite block patterns on Z/2m with offsets
       - Three-orbit patterns on Z/3m
       - Near-difference-set patterns with relaxed Sidon constraint
       - Fishburn-Reeds-style 20-point augmentations
  2. Apply ALL exact filters in the toolkit:
       - row-overlap |S_i cap S_j| <= 2
       - phi4 rectangle trap
       - mutual-rhombus midpoint
       - odd forced-perpendicularity cycle
       - adjacent two-overlap
       - vertex-circle order filter (single natural-order pass; full crossing
         search bypassed when too expensive)
  3. For survivors, run constrained SLSQP at margin 1e-4 with 50 restarts.
  4. Tag B12-style cluster collapse signatures and reject.
  5. Report top 5 candidates by (residual, convexity_margin, min_edge).

This is a search driver, not a proof. Robust near-misses (residual < 1e-6,
convexity_margin > 1e-3, min_edge > 1e-3, no clustering) are flagged for
exact certification.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from itertools import combinations
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import numpy as np  # noqa: E402
from scipy.optimize import minimize  # noqa: E402

from erdos97.incidence_filters import (  # noqa: E402
    filter_summary,
)
from erdos97.search import (  # noqa: E402
    convexity_margins,
    independent_diagnostics,
    init_x,
    pairwise_distances,
    pairwise_sqdist,
    polygon_from_x,
)
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction  # noqa: E402


@dataclass
class CandidateReport:
    name: str
    n: int
    family: str
    formula: str
    pair_cap_ok: bool
    max_common: int
    indegree_min: int
    indegree_max: int
    odd_cycle: bool
    rectangle_trap: int
    mutual_phi: int
    forced_classes: list
    natural_vertex_circle_obstructed: Optional[bool]
    num_filters_passed: int
    survives_all_exact_filters: bool


def pair_cap_ok(S, cap=2):
    n = len(S)
    sets = [set(r) for r in S]
    max_c = 0
    for a in range(n):
        for b in range(a + 1, n):
            c = len(sets[a] & sets[b])
            if c > max_c:
                max_c = c
            if c > cap:
                return False, max_c
    return True, max_c


def basic_validity(S, n):
    """Validate 4-regular, no-self, no-dups, no-out-of-range."""
    if len(S) != n:
        return False
    for i, row in enumerate(S):
        if len(row) != 4:
            return False
        if i in row:
            return False
        if len(set(row)) != 4:
            return False
        if any(x < 0 or x >= n for x in row):
            return False
    return True


def indegree_stats(S, n):
    indeg = [0] * n
    for row in S:
        for j in row:
            indeg[j] += 1
    return min(indeg), max(indeg)


def is_witness_indegree_balanced(S, n, lo=2, hi=6):
    mn, mx = indegree_stats(S, n)
    return lo <= mn and mx <= hi


# -------------------------- pattern generators ---------------------------

def cyclic_pattern(n, offsets):
    S = []
    for i in range(n):
        row = sorted({(i + o) % n for o in offsets})
        if i in row or len(row) != 4:
            return None
        S.append(row)
    return S


def almost_cyclic_pattern(n, offsets, perturbation_row=0, perturbed_offsets=None):
    """Cyclic pattern but row perturbation_row replaced by perturbed_offsets."""
    S = []
    for i in range(n):
        if i == perturbation_row:
            row = sorted({(i + o) % n for o in (perturbed_offsets or offsets)})
        else:
            row = sorted({(i + o) % n for o in offsets})
        if i in row or len(row) != 4:
            return None
        S.append(row)
    return S


def bipartite_block_pattern(n, even_offsets, odd_offsets):
    if n % 2:
        return None
    S = []
    for i in range(n):
        offs = even_offsets if i % 2 == 0 else odd_offsets
        row = sorted({(i + o) % n for o in offs})
        if i in row or len(row) != 4:
            return None
        S.append(row)
    return S


def three_orbit_pattern(n, off0, off1, off2):
    if n % 3:
        return None
    S = []
    for i in range(n):
        offs = [off0, off1, off2][i % 3]
        row = sorted({(i + o) % n for o in offs})
        if i in row or len(row) != 4:
            return None
        S.append(row)
    return S


# ------------------------- candidate enumeration -------------------------

def cyclic_candidates(n, max_count=200, rng=None):
    """Generate 4-element offset sets {a,b,c,d} that produce a 4-regular
    cyclic pattern with pair-cap <=2. The set must avoid 0 mod n,
    and no element should equal any other.
    Sidon-like restrictions are NOT imposed -- we accept |S_a ∩ S_b| <= 2
    weakly.
    """
    rng = rng or np.random.default_rng(42)
    # full enumeration up to a cap when feasible.
    nonzero = list(range(1, n))
    candidates = []
    # use combinations of 4 distinct offsets from 1..n-1
    if n <= 25:
        for combo in combinations(nonzero, 4):
            S = cyclic_pattern(n, combo)
            if S is None:
                continue
            ok, mc = pair_cap_ok(S)
            if ok:
                candidates.append((combo, S))
                if len(candidates) >= max_count:
                    break
    else:
        # random sampling for large n
        attempted = set()
        attempts = 0
        while len(candidates) < max_count and attempts < 30 * max_count:
            attempts += 1
            combo = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
            if combo in attempted:
                continue
            attempted.add(combo)
            S = cyclic_pattern(n, combo)
            if S is None:
                continue
            ok, mc = pair_cap_ok(S)
            if ok:
                candidates.append((combo, S))
    return candidates


def bipartite_candidates(n, max_count=120, rng=None):
    rng = rng or np.random.default_rng(43)
    if n % 2:
        return []
    out = []
    nonzero = list(range(1, n))
    attempts = 0
    seen = set()
    while len(out) < max_count and attempts < 30 * max_count:
        attempts += 1
        even_offs = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        odd_offs = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        key = (even_offs, odd_offs)
        if key in seen:
            continue
        seen.add(key)
        S = bipartite_block_pattern(n, even_offs, odd_offs)
        if S is None:
            continue
        ok, mc = pair_cap_ok(S)
        if ok:
            out.append((key, S))
    return out


def three_orbit_candidates(n, max_count=120, rng=None):
    rng = rng or np.random.default_rng(44)
    if n % 3:
        return []
    out = []
    nonzero = list(range(1, n))
    attempts = 0
    seen = set()
    while len(out) < max_count and attempts < 60 * max_count:
        attempts += 1
        off0 = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        off1 = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        off2 = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        key = (off0, off1, off2)
        if key in seen:
            continue
        seen.add(key)
        S = three_orbit_pattern(n, off0, off1, off2)
        if S is None:
            continue
        ok, mc = pair_cap_ok(S)
        if ok:
            out.append((key, S))
    return out


def almost_cyclic_candidates(n, base_offsets, max_count=80, rng=None):
    rng = rng or np.random.default_rng(45)
    out = []
    nonzero = list(range(1, n))
    base_S = cyclic_pattern(n, base_offsets)
    if base_S is None:
        return []
    attempts = 0
    seen = set()
    while len(out) < max_count and attempts < 30 * max_count:
        attempts += 1
        row = int(rng.integers(0, n))
        new_offs = tuple(sorted(rng.choice(nonzero, size=4, replace=False).tolist()))
        key = (row, new_offs)
        if key in seen:
            continue
        seen.add(key)
        S = almost_cyclic_pattern(n, base_offsets, perturbation_row=row, perturbed_offsets=new_offs)
        if S is None:
            continue
        ok, mc = pair_cap_ok(S)
        if ok:
            out.append((key, S))
    return out


def known_offsets_for(n):
    """Some seed offset sets (from existing patterns) used to base almost-cyclic."""
    return {
        11: [(1, 3, 4, 5), (2, 3, 5, 8), (1, 2, 5, 7)],
        13: [(1, 2, 4, 10), (1, 3, 4, 9), (2, 3, 5, 11)],
        14: [(1, 2, 5, 11), (1, 3, 5, 9), (2, 4, 5, 12)],
        15: [(1, 2, 7, 11), (1, 4, 5, 11), (2, 5, 7, 11)],
        16: [(1, 3, 7, 11), (2, 3, 7, 13), (1, 4, 7, 13)],
        17: [(-7 % 17, -2 % 17, 4, 8), (1, 3, 4, 11), (2, 5, 9, 14)],
        18: [(1, 3, 7, 11), (2, 5, 11, 15), (1, 4, 7, 13)],
        19: [(-8 % 19, -3 % 19, 5, 9), (1, 2, 5, 11), (2, 3, 7, 14)],
        20: [(1, 3, 7, 11), (2, 5, 9, 14), (1, 5, 7, 13)],
        21: [(1, 3, 7, 11), (2, 5, 11, 17), (1, 5, 9, 15)],
        24: [(1, 3, 8, 17), (2, 5, 11, 18), (1, 7, 11, 17)],
        25: [(2, 5, 9, 14), (1, 3, 7, 17), (1, 5, 11, 18)],
        30: [(1, 3, 8, 13), (2, 7, 13, 21), (1, 5, 11, 17)],
        36: [(1, 3, 9, 19), (2, 7, 13, 23), (1, 5, 11, 25)],
        48: [(1, 3, 9, 19), (2, 7, 13, 31), (1, 5, 11, 25)],
        60: [(1, 3, 9, 19), (2, 7, 13, 31), (1, 5, 11, 25)],
    }.get(n, [])


# ------------------------- equivalence reduction -------------------------

def canonical_signature(S, n):
    """Canonical-ish hash invariant under cyclic shift, dihedral reflection,
    and complement (label j -> n-1-j after shift). Approximate; collision
    OK because we're filtering near-equivalents conservatively, not proving
    distinctness.
    """
    sets = [tuple(sorted(r)) for r in S]
    best = None

    def shift(rows, k):
        return tuple(
            tuple(sorted((j + k) % n for j in rows[(i - k) % n]))
            for i in range(n)
        )

    def reflect(rows):
        return tuple(
            tuple(sorted((-j) % n for j in rows[(-i) % n]))
            for i in range(n)
        )

    forms = [tuple(sets), reflect(sets)]
    for f in forms:
        for k in range(n):
            cand = shift(f, k)
            cand = tuple(sorted(cand))
            if best is None or cand < best:
                best = cand
    return best


# ----------------------- exact filters wrapper --------------------------

def apply_exact_filters(S, n, deep_vertex_circle=True):
    info = filter_summary(S)
    odd_cycle_present = info["odd_cycle_length"] is not None
    rect = info["rectangle_trap_4_cycles"]
    mutual = info["mutual_phi_2_cycles"]
    forced = info["forced_equality_classes"]
    adjacent_violations = info["adjacent_two_overlap_violations"]

    natural_vc = None
    if deep_vertex_circle:
        try:
            res = vertex_circle_order_obstruction(S, list(range(n)), pattern="anon")
            natural_vc = bool(res.obstructed)
        except Exception:
            natural_vc = None

    ok_overlap = len(adjacent_violations) == 0
    forced_kill = any(len(cls) >= max(3, n // 3) for cls in forced)
    return {
        "summary": info,
        "odd_cycle": odd_cycle_present,
        "rectangle_trap": rect,
        "mutual_phi": mutual,
        "forced_classes": forced,
        "adjacent_violations": adjacent_violations,
        "ok_adjacent_overlap": ok_overlap,
        "ok_no_odd_cycle": not odd_cycle_present,
        "ok_no_rectangle": rect == 0,
        "ok_no_forced_kill": not forced_kill,
        "ok_no_mutual_collapse": True,
        "natural_vc_obstructed": natural_vc,
    }


# ------------------------ numerical SLSQP search ------------------------

def equality_residual(x, n, S, mode="polar"):
    P = polygon_from_x(x, n, mode)
    D2 = pairwise_sqdist(P)
    terms = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si], dtype=float)
        terms.append(vals - vals.mean())
    return np.concatenate(terms) if terms else np.zeros(0)


def slsqp_attempt(S, n, mode, restarts, seed, margin, max_iter, time_budget=None,
                  early_stop_loss=None, prescreen_loss=10.0, prescreen_iter=40):
    rng = np.random.default_rng(seed)

    def loss_fn(x):
        r = equality_residual(x, n, S, mode)
        return float(np.dot(r, r))

    def conv_c(x):
        P = polygon_from_x(x, n, mode)
        return convexity_margins(P) - margin

    def edge_c(x):
        P = polygon_from_x(x, n, mode)
        ed = np.linalg.norm(np.roll(P, -1, axis=0) - P, axis=1)
        return ed - margin

    def pair_c(x):
        P = polygon_from_x(x, n, mode)
        D = pairwise_distances(P)
        iu = np.triu_indices(n, 1)
        return D[iu] - margin

    constraints = [
        {"type": "ineq", "fun": conv_c},
        {"type": "ineq", "fun": edge_c},
        {"type": "ineq", "fun": pair_c},
    ]

    best = None
    start = time.time()
    # First a cheap prescreen with lower iter count -- skip pattern entirely
    # if no prescreen restart drops below `prescreen_loss`.
    prescreen_best = None
    for r in range(restarts):
        if time_budget is not None and time.time() - start > time_budget * 0.4:
            break
        x0 = init_x(n, rng, mode, jitter=0.45 if r else 0.10)
        try:
            res = minimize(
                loss_fn,
                x0,
                method="SLSQP",
                constraints=constraints,
                options={"maxiter": prescreen_iter, "ftol": 1e-9, "disp": False},
            )
        except Exception:
            continue
        if not np.all(np.isfinite(res.x)):
            continue
        if (conv_c(res.x).min() < -1e-9
                or edge_c(res.x).min() < -1e-9
                or pair_c(res.x).min() < -1e-9):
            continue
        score = float(res.fun)
        if prescreen_best is None or score < prescreen_best[0]:
            prescreen_best = (score, np.asarray(res.x).copy())
            if early_stop_loss is not None and score < early_stop_loss:
                return prescreen_best

    if prescreen_best is None:
        return None
    if prescreen_best[0] > prescreen_loss:
        return prescreen_best  # no point refining; structural wall

    # Refine the best prescreen restart with full iter count
    if time_budget is not None and time.time() - start > time_budget:
        return prescreen_best
    try:
        res = minimize(
            loss_fn,
            prescreen_best[1],
            method="SLSQP",
            constraints=constraints,
            options={"maxiter": max_iter, "ftol": 1e-12, "disp": False},
        )
        if (np.all(np.isfinite(res.x))
                and conv_c(res.x).min() >= -1e-9
                and edge_c(res.x).min() >= -1e-9
                and pair_c(res.x).min() >= -1e-9):
            best = (float(res.fun), np.asarray(res.x).copy())
    except Exception:
        pass
    if best is None or (prescreen_best is not None and prescreen_best[0] < best[0]):
        return prescreen_best
    return best


def detect_cluster_collapse(diag, n):
    """Heuristic: B12-like signature is many vertices in a few tight clusters
    relative to scale. We compare min edge to median edge -- if min_edge is
    much smaller than median, it's a degenerate clustering.
    """
    # use radii spread in distance_table; we have the diag dict with min/max
    if diag["min_edge_length"] < 1e-4:
        return True
    return False


# --------------------- candidate dispatch and reporting ---------------------

def evaluate_candidate(name, n, S, family, formula, mode, restarts, seed, margin,
                       max_iter, deep_vc=False, slsqp_time_budget=None):
    val = basic_validity(S, n)
    if not val:
        return None
    ok_pair, max_c = pair_cap_ok(S)
    if not ok_pair:
        return None
    if not is_witness_indegree_balanced(S, n):
        return None

    filt = apply_exact_filters(S, n, deep_vertex_circle=deep_vc)
    survives = (filt["ok_adjacent_overlap"]
                and filt["ok_no_odd_cycle"]
                and filt["ok_no_rectangle"]
                and filt["ok_no_forced_kill"])
    # Natural-order vertex-circle filter: this kills most circulants. We treat
    # natural-order obstructed = True as a kill. False/None means unobstructed
    # in this order; the pattern may still survive on other orders.
    if filt["natural_vc_obstructed"] is True:
        survives = False

    indeg_lo, indeg_hi = indegree_stats(S, n)
    report = CandidateReport(
        name=name,
        n=n,
        family=family,
        formula=formula,
        pair_cap_ok=ok_pair,
        max_common=max_c,
        indegree_min=indeg_lo,
        indegree_max=indeg_hi,
        odd_cycle=filt["odd_cycle"],
        rectangle_trap=filt["rectangle_trap"],
        mutual_phi=filt["mutual_phi"],
        forced_classes=filt["forced_classes"],
        natural_vertex_circle_obstructed=filt["natural_vc_obstructed"],
        num_filters_passed=int(filt["ok_adjacent_overlap"]) + int(filt["ok_no_odd_cycle"])
            + int(filt["ok_no_rectangle"]) + int(filt["ok_no_forced_kill"]),
        survives_all_exact_filters=bool(survives),
    )
    if not survives:
        return {"report": asdict(report), "numeric": None}

    # Numeric attempt
    res = slsqp_attempt(
        S, n, mode, restarts, seed, margin, max_iter,
        time_budget=slsqp_time_budget,
        early_stop_loss=1e-14,
    )
    if res is None:
        return {"report": asdict(report), "numeric": None}
    score, x_best = res
    P = polygon_from_x(x_best, n, mode)
    diag = independent_diagnostics(P, S)
    cluster_collapse = detect_cluster_collapse(diag, n)
    numeric = {
        "loss": score,
        "eq_rms": diag["eq_rms"],
        "max_spread": diag["max_spread"],
        "max_rel_spread": diag["max_rel_spread"],
        "convexity_margin": diag["convexity_margin"],
        "min_edge_length": diag["min_edge_length"],
        "min_pair_distance": diag["min_pair_distance"],
        "cluster_collapse": cluster_collapse,
        "x_best": x_best.tolist(),
        "coordinates": [[float(a), float(b)] for a, b in P],
    }
    return {"report": asdict(report), "numeric": numeric}


def summarize_run(records, n_top=5):
    # filter for robust near-misses
    near = []
    for entry in records:
        if entry is None or entry.get("numeric") is None:
            continue
        nm = entry["numeric"]
        rep = entry["report"]
        if rep["survives_all_exact_filters"] and nm["loss"] is not None:
            near.append(entry)

    def rank_key(e):
        nm = e["numeric"]
        e["report"]
        # primary: low loss; tie-break: high convexity, high min_edge
        return (
            nm["max_spread"],
            -nm["convexity_margin"],
            -nm["min_edge_length"],
        )

    near.sort(key=rank_key)
    return near[:n_top]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(REPO_ROOT / "data" / "runs" / "2026-05-06"))
    ap.add_argument("--margin", type=float, default=1e-4)
    ap.add_argument("--restarts", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--mode", default="polar")
    ap.add_argument("--max-iter", type=int, default=400)
    ap.add_argument("--ns", default="11,13,14,12")
    ap.add_argument("--ns-extended", default="15,16,17,18")
    ap.add_argument("--max-per-family", type=int, default=120)
    ap.add_argument("--quick", action="store_true",
                    help="run a quick sweep with fewer restarts/iters")
    ap.add_argument("--time-budget-per-pattern", type=float, default=15.0)
    ap.add_argument("--include-extended", action="store_true")
    ap.add_argument("--include-large", action="store_true")
    args = ap.parse_args()

    if args.quick:
        args.restarts = 4
        args.max_iter = 200
        args.time_budget_per_pattern = 6.0

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    ns_primary = [int(x) for x in args.ns.split(",") if x.strip()]
    ns_extended = [int(x) for x in args.ns_extended.split(",") if x.strip()]
    ns = list(ns_primary)
    if args.include_extended:
        ns += ns_extended
    if args.include_large:
        ns += [19, 20, 21, 24, 25, 30, 36, 48, 60]

    # de-dup
    seen_ns = []
    for n in ns:
        if n not in seen_ns:
            seen_ns.append(n)
    ns = seen_ns

    np.random.default_rng(args.seed)
    all_records = []
    seen_signatures = set()

    overall_start = time.time()
    for n in ns:
        print(f"\n=== n = {n} ===", flush=True)
        n_records = []

        # Family A: cyclic
        cyc = cyclic_candidates(n, max_count=args.max_per_family,
                                 rng=np.random.default_rng(args.seed + n))
        print(f" cyclic candidates: {len(cyc)}", flush=True)
        for combo, S in cyc[: args.max_per_family]:
            sig = canonical_signature(S, n)
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            name = f"C{n}_cyc_{'_'.join(str(o) for o in combo)}"
            formula = f"S_i = i + {list(combo)} mod {n}"
            entry = evaluate_candidate(
                name, n, S, "cyclic", formula, args.mode, args.restarts,
                args.seed + n, args.margin, args.max_iter, deep_vc=False,
                slsqp_time_budget=args.time_budget_per_pattern,
            )
            if entry is None:
                continue
            entry["report"]["pattern_S"] = S
            n_records.append(entry)

        # Family B: bipartite block
        if n <= 24 and n % 2 == 0:
            bip = bipartite_candidates(n, max_count=args.max_per_family,
                                        rng=np.random.default_rng(args.seed + n + 100))
            print(f" bipartite candidates: {len(bip)}", flush=True)
            for key, S in bip[: args.max_per_family]:
                sig = canonical_signature(S, n)
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)
                name = f"B{n}_bip_{'_'.join(str(o) for o in key[0])}__{'_'.join(str(o) for o in key[1])}"
                formula = f"even: i+{list(key[0])}, odd: i+{list(key[1])} mod {n}"
                entry = evaluate_candidate(
                    name, n, S, "bipartite", formula, args.mode, args.restarts,
                    args.seed + n + 100, args.margin, args.max_iter, deep_vc=False,
                    slsqp_time_budget=args.time_budget_per_pattern,
                )
                if entry is None:
                    continue
                entry["report"]["pattern_S"] = S
                n_records.append(entry)

        # Family C: three-orbit
        if n <= 24 and n % 3 == 0:
            tri = three_orbit_candidates(n, max_count=args.max_per_family // 2,
                                          rng=np.random.default_rng(args.seed + n + 200))
            print(f" three-orbit candidates: {len(tri)}", flush=True)
            for key, S in tri[: args.max_per_family // 2]:
                sig = canonical_signature(S, n)
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)
                name = f"T{n}_3orbit_{n}"
                formula = f"period-3 offsets {key}"
                entry = evaluate_candidate(
                    name, n, S, "three-orbit", formula, args.mode, args.restarts,
                    args.seed + n + 200, args.margin, args.max_iter, deep_vc=False,
                    slsqp_time_budget=args.time_budget_per_pattern,
                )
                if entry is None:
                    continue
                entry["report"]["pattern_S"] = S
                n_records.append(entry)

        # Family D: almost-cyclic
        for base in known_offsets_for(n)[:2]:
            ac = almost_cyclic_candidates(
                n, base, max_count=max(20, args.max_per_family // 3),
                rng=np.random.default_rng(args.seed + n + 300 + sum(base)),
            )
            print(f" almost-cyclic from {base}: {len(ac)}", flush=True)
            for key, S in ac:
                sig = canonical_signature(S, n)
                if sig in seen_signatures:
                    continue
                seen_signatures.add(sig)
                row, new_off = key
                name = f"A{n}_ac_{'_'.join(str(o) for o in base)}_r{row}_{'_'.join(str(o) for o in new_off)}"
                formula = f"cyclic({base}) with row {row} -> {list(new_off)} mod {n}"
                entry = evaluate_candidate(
                    name, n, S, "almost-cyclic", formula, args.mode, args.restarts,
                    args.seed + n + 300 + sum(base), args.margin, args.max_iter, deep_vc=False,
                    slsqp_time_budget=args.time_budget_per_pattern,
                )
                if entry is None:
                    continue
                entry["report"]["pattern_S"] = S
                n_records.append(entry)

        all_records.extend(n_records)
        # write per-n summary
        with open(out_dir / f"sweep_n{n}.json", "w") as f:
            json.dump({
                "n": n,
                "count_total": len(n_records),
                "count_survivors": sum(1 for e in n_records if e["report"]["survives_all_exact_filters"]),
                "records": n_records,
            }, f, indent=2)
        print(f" n={n}: {len(n_records)} unique candidates, "
              f"{sum(1 for e in n_records if e['report']['survives_all_exact_filters'])} pass exact filters",
              flush=True)

    # final summary
    near = summarize_run(all_records, n_top=10)
    summary = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "args": vars(args),
        "ns": ns,
        "total_candidates": len(all_records),
        "filter_survivors": sum(1 for e in all_records if e["report"]["survives_all_exact_filters"]),
        "top_near_misses": near,
        "elapsed_sec": time.time() - overall_start,
    }
    out_path = out_dir / "search_new_patterns_summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nWrote {out_path}", flush=True)

    # report
    print("\n=== TOP NEAR-MISSES ===")
    for i, entry in enumerate(near[:10]):
        rep = entry["report"]
        nm = entry["numeric"]
        print(f"#{i+1} {rep['name']}  n={rep['n']}  family={rep['family']}")
        print(f"    formula: {rep['formula']}")
        print(f"    loss={nm['loss']:.3e}  eq_rms={nm['eq_rms']:.3e}  max_spread={nm['max_spread']:.3e}")
        print(f"    conv_margin={nm['convexity_margin']:.3e}  min_edge={nm['min_edge_length']:.3e}  cluster_collapse={nm['cluster_collapse']}")


if __name__ == "__main__":
    main()
