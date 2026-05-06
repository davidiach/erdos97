#!/usr/bin/env python3
"""Z3 enumeration of selected-witness incidence patterns for n=10, 11, 12.

Constraints (necessary):
  - x[i,i] = 0
  - sum_j x[i,j] = 4 for each i
  - For all i != j: |S_i cap S_j| <= 2 (column-pair cap)
  - For each cyclic-adjacent (i, i+1 mod n): |S_i cap S_j| <= 1
    (rejects adjacent two-overlap; this is a known incidence necessary
    condition for the natural cyclic order 0..n-1)
  - sum over i of x[i,j] >= 1 for each j (vertex must be hit somewhere)

Symmetry breaking:
  Fix row 0 to S_0 = {1, 2, 3, 4}; after enumeration we canonicalize under
  the dihedral group D_n acting on the cyclic order.

Filters applied to surviving patterns:
  - crossing-bisector violations along natural order;
  - odd forced-perpendicular cycle;
  - phi^4 rectangle trap;
  - mutual-rhombus / mutual-phi-pair count.

Realization attempt:
  - SLSQP minimization of "fourth-nearest hinge" residual.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

import z3

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.incidence_filters import (  # noqa: E402
    adjacent_two_overlap_violations,
    crossing_bisector_violations,
    mutual_phi_pairs,
    odd_forced_perpendicular_cycle,
    phi4_rectangle_trap_certificates,
    phi_map,
)


def encode_pattern_constraints(n: int, fix_row0: bool = True):
    s = z3.Solver()
    x = [[z3.Bool(f"x_{i}_{j}") for j in range(n)] for i in range(n)]

    for i in range(n):
        s.add(z3.Not(x[i][i]))
    for i in range(n):
        s.add(z3.PbEq([(x[i][j], 1) for j in range(n) if j != i], 4))
    for i in range(n):
        for j in range(i + 1, n):
            zs = []
            for k in range(n):
                if k == i or k == j:
                    continue
                z = z3.Bool(f"and_{i}_{j}_{k}")
                s.add(z == z3.And(x[i][k], x[j][k]))
                zs.append(z)
            cap = 1 if (j - i) % n in (1, n - 1) else 2
            s.add(z3.PbLe([(z, 1) for z in zs], cap))
    for j in range(n):
        s.add(z3.PbGe([(x[i][j], 1) for i in range(n) if i != j], 1))
    if fix_row0:
        for j in range(n):
            if j in (1, 2, 3, 4):
                s.add(x[0][j])
            else:
                s.add(z3.Not(x[0][j]))
    return s, x


def model_to_pattern(model, x, n):
    rows = []
    for i in range(n):
        row = tuple(j for j in range(n)
                    if z3.is_true(model.eval(x[i][j], model_completion=True)))
        rows.append(row)
    return tuple(rows)


def block_pattern(s, x, pattern):
    n = len(pattern)
    lits = []
    for i in range(n):
        rs = set(pattern[i])
        for j in range(n):
            if j == i:
                continue
            lits.append(z3.Not(x[i][j]) if j in rs else x[i][j])
    s.add(z3.Or(lits))


def cyclic_rotations(pattern):
    n = len(pattern)
    out = []
    for r in range(n):
        new_pattern = [None] * n
        for i in range(n):
            new_i = (i + r) % n
            new_pattern[new_i] = tuple(sorted(((j + r) % n) for j in pattern[i]))
        out.append(tuple(new_pattern))
    return out


def reflection(pattern):
    n = len(pattern)
    new_pattern = [None] * n
    for i in range(n):
        new_i = (-i) % n
        new_pattern[new_i] = tuple(sorted(((-j) % n) for j in pattern[i]))
    return tuple(new_pattern)


def canonical_form(pattern):
    cands = list(cyclic_rotations(pattern))
    cands.extend(cyclic_rotations(reflection(pattern)))
    return min(cands)


def enumerate_patterns(n, time_limit_s=600.0, max_patterns=200000):
    s, x = encode_pattern_constraints(n, fix_row0=True)
    canonical_seen = set()
    patterns = []
    raw_count = 0
    start = time.time()
    while True:
        if time.time() - start > time_limit_s:
            break
        if len(patterns) >= max_patterns:
            break
        if s.check() != z3.sat:
            break
        m = s.model()
        pat = model_to_pattern(m, x, n)
        raw_count += 1

        canon = canonical_form(pat)
        if canon not in canonical_seen:
            canonical_seen.add(canon)
            patterns.append(canon)

        # Block all dihedral images that still have row0=(1,2,3,4) for efficiency.
        for refl in (pat, reflection(pat)):
            for rot in cyclic_rotations(refl):
                if rot[0] == (1, 2, 3, 4):
                    block_pattern(s, x, rot)
        block_pattern(s, x, pat)

    elapsed = time.time() - start
    return {
        "n": n,
        "raw_models_seen": raw_count,
        "canonical_patterns": len(patterns),
        "patterns": patterns,
        "elapsed_seconds": elapsed,
        "complete": (time.time() - start) <= time_limit_s and len(patterns) < max_patterns,
    }


def apply_filters(pattern):
    n = len(pattern)
    S = [list(row) for row in pattern]
    order = list(range(n))

    odd_cycle = odd_forced_perpendicular_cycle(S)
    rect_traps = phi4_rectangle_trap_certificates(S, order)
    crossing_viol = crossing_bisector_violations(S, order)
    adj_viol = adjacent_two_overlap_violations(S, order)
    survives = (
        odd_cycle is None
        and len(rect_traps) == 0
        and len(crossing_viol) == 0
        and len(adj_viol) == 0
    )
    return {
        "odd_perp_cycle": [list(c) for c in odd_cycle] if odd_cycle else None,
        "rectangle_trap_count": len(rect_traps),
        "crossing_bisector_violation_count": len(crossing_viol),
        "adjacent_two_overlap_violation_count": len(adj_viol),
        "phi_map_size": len(phi_map(S)),
        "mutual_phi_pairs": len(mutual_phi_pairs(S)),
        "survives": survives,
    }


def realize_pattern(pattern, max_attempts=8, max_iter=400, seed=0):
    n = len(pattern)
    target = [set(row) for row in pattern]
    rng = np.random.default_rng(seed)

    def loss_fn(p):
        P = p.reshape(n, 2)
        loss = 0.0
        margin = 0.005
        for i in range(n):
            d = np.array([np.inf if j == i else float(np.linalg.norm(P[i] - P[j]))
                          for j in range(n)])
            din = np.array([d[j] for j in target[i]])
            dout = np.array([d[j] for j in range(n) if j != i and j not in target[i]])
            v = float(din.max() - dout.min() + margin)
            if v > 0:
                loss += v * v
        return loss

    best = None
    for attempt in range(max_attempts):
        theta = 2 * np.pi * np.arange(n) / n
        P0 = np.column_stack([np.cos(theta), np.sin(theta)])
        P0 = P0 + 0.15 * rng.standard_normal(P0.shape)
        try:
            res = minimize(loss_fn, P0.flatten(),
                           method="SLSQP",
                           options={"maxiter": max_iter, "ftol": 1e-12})
        except Exception:
            continue
        loss = float(res.fun)
        if best is None or loss < best[0]:
            best = (loss, res.x.reshape(n, 2).tolist(), bool(res.success))
        if loss < 1e-12:
            break
    if best is None:
        return {"realized": False, "best_loss": None, "points": None, "success": False}
    return {"realized": best[0] < 1e-8, "best_loss": best[0],
            "points": best[1], "success": best[2]}


def verify_realization(pattern, points):
    n = len(pattern)
    P = np.array(points)
    issues = []
    for i in range(n):
        d = np.array([np.inf if j == i else float(np.linalg.norm(P[i] - P[j]))
                      for j in range(n)])
        order = np.argsort(d)
        nearest4 = set(int(j) for j in order[:4])
        target = set(pattern[i])
        if nearest4 != target:
            issues.append({"i": i, "expected": sorted(target), "got": sorted(nearest4)})
    return {"verified": len(issues) == 0, "issues": issues}


def run(n, time_limit_s, max_patterns, slsqp_attempts):
    print(f"=== n={n} enumeration ===", flush=True)
    enum = enumerate_patterns(n, time_limit_s=time_limit_s, max_patterns=max_patterns)
    print(
        f"  raw={enum['raw_models_seen']} canonical={enum['canonical_patterns']} "
        f"elapsed={enum['elapsed_seconds']:.1f}s complete={enum['complete']}",
        flush=True,
    )
    survivors = []
    fs = {"total": len(enum["patterns"]), "survived": 0,
          "killed_odd_cycle": 0, "killed_rect_trap": 0,
          "killed_crossing": 0, "killed_adjacent": 0}
    detailed = []
    for idx, pat in enumerate(enum["patterns"]):
        res = apply_filters(pat)
        if res["odd_perp_cycle"] is not None:
            fs["killed_odd_cycle"] += 1
        if res["rectangle_trap_count"] > 0:
            fs["killed_rect_trap"] += 1
        if res["crossing_bisector_violation_count"] > 0:
            fs["killed_crossing"] += 1
        if res["adjacent_two_overlap_violation_count"] > 0:
            fs["killed_adjacent"] += 1
        if res["survives"]:
            fs["survived"] += 1
            survivors.append((idx, pat))
        detailed.append({
            "index": idx,
            "pattern": [list(r) for r in pat],
            "filters": res,
        })
    print(
        f"  filters: survived={fs['survived']} odd_cycle={fs['killed_odd_cycle']} "
        f"rect_trap={fs['killed_rect_trap']} crossing={fs['killed_crossing']} "
        f"adjacent={fs['killed_adjacent']}",
        flush=True,
    )

    realizations = []
    best_near_miss = None
    for idx, pat in survivors[:50]:
        rea = realize_pattern(pat, max_attempts=slsqp_attempts, seed=idx)
        ver = verify_realization(pat, rea["points"]) if rea["points"] else None
        rec = {
            "index": idx,
            "pattern": [list(r) for r in pat],
            "best_loss": rea["best_loss"],
            "verifier": ver,
        }
        realizations.append(rec)
        if rea["best_loss"] is not None:
            if best_near_miss is None or rea["best_loss"] < best_near_miss["best_loss"]:
                best_near_miss = {
                    "index": idx,
                    "pattern": [list(r) for r in pat],
                    "best_loss": rea["best_loss"],
                    "verifier_match": (ver["verified"] if ver else False),
                    "points": rea["points"],
                }

    return {
        "n": n,
        "enumeration": {
            "raw_models_seen": enum["raw_models_seen"],
            "canonical_patterns": enum["canonical_patterns"],
            "complete": enum["complete"],
            "elapsed_seconds": enum["elapsed_seconds"],
        },
        "filter_summary": fs,
        "patterns": detailed,
        "realizations": realizations,
        "best_near_miss": best_near_miss,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ns", type=int, nargs="+", default=[10, 11, 12])
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--max-patterns", type=int, default=200000)
    parser.add_argument("--slsqp-attempts", type=int, default=8)
    parser.add_argument("--out", type=Path,
                        default=ROOT / "data" / "certificates" / "2026-05-06"
                        / "sat_smt_n10_n11_n12.json")
    args = parser.parse_args()

    payload = {
        "schema_version": 1,
        "task": "Z3 enumeration of incidence patterns + filters + SLSQP realization",
        "ns": args.ns,
        "time_limit_per_n": args.time_limit,
        "max_patterns": args.max_patterns,
        "results": {},
    }
    for n in args.ns:
        payload["results"][str(n)] = run(
            n=n,
            time_limit_s=args.time_limit,
            max_patterns=args.max_patterns,
            slsqp_attempts=args.slsqp_attempts,
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2, default=list) + "\n",
                        encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
