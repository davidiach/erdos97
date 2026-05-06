#!/usr/bin/env python3
"""Focused numerical search on cyclic survivors that pass exact filters
including the natural-order vertex-circle filter.
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))

import numpy as np
from scipy.optimize import minimize

from erdos97.search import (
    polygon_from_x, init_x, pairwise_distances, pairwise_sqdist,
    convexity_margins, independent_diagnostics,
)
from erdos97.incidence_filters import filter_summary
from erdos97.vertex_circle_order_filter import vertex_circle_order_obstruction


def cyclic_pattern(n, offsets):
    return [sorted({(i + o) % n for o in offsets}) for i in range(n)]


def run_one(S, n, mode='polar', restarts=20, seed=42, margin=1e-4,
            max_iter=300, time_budget=4.0, prescreen_loss=8.0):
    rng = np.random.default_rng(seed)
    def loss_fn(x):
        P = polygon_from_x(x, n, mode)
        D2 = pairwise_sqdist(P)
        terms = []
        for i, Si in enumerate(S):
            vals = np.array([D2[i, j] for j in Si])
            terms.append(vals - vals.mean())
        r = np.concatenate(terms)
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
        {'type':'ineq', 'fun':conv_c},
        {'type':'ineq', 'fun':edge_c},
        {'type':'ineq', 'fun':pair_c},
    ]
    best = None
    t0 = time.time()
    # prescreen: short iters
    for r in range(restarts):
        if time.time() - t0 > time_budget * 0.5: break
        x0 = init_x(n, rng, mode, jitter=0.45 if r else 0.10)
        try:
            res = minimize(loss_fn, x0, method='SLSQP', constraints=constraints,
                          options={'maxiter': 60, 'ftol':1e-9})
        except Exception:
            continue
        if not np.all(np.isfinite(res.x)): continue
        if conv_c(res.x).min() < -1e-9 or edge_c(res.x).min() < -1e-9 or pair_c(res.x).min() < -1e-9:
            continue
        if best is None or res.fun < best[0]:
            best = (float(res.fun), np.asarray(res.x).copy())
    if best is None or best[0] > prescreen_loss:
        return best
    # refine
    while time.time() - t0 < time_budget:
        try:
            res = minimize(loss_fn, best[1], method='SLSQP', constraints=constraints,
                          options={'maxiter': max_iter, 'ftol':1e-13})
        except Exception:
            break
        if not np.all(np.isfinite(res.x)): break
        if conv_c(res.x).min() < -1e-9 or edge_c(res.x).min() < -1e-9 or pair_c(res.x).min() < -1e-9:
            break
        improved = res.fun < best[0] - 1e-12
        best = (float(res.fun), np.asarray(res.x).copy())
        if not improved:
            break
    return best


def main():
    survivors = {
        12: [(1, 4, 8, 11), (3, 4, 6, 8), (4, 6, 8, 9)],
        13: [(1, 3, 8, 10), (3, 5, 10, 12)],
        14: [(1, 2, 7, 12), (2, 7, 12, 13), (4, 5, 7, 10), (4, 6, 7, 9), (4, 7, 9, 10), (5, 7, 8, 10)],
    }
    results = []
    for n, combos in survivors.items():
        for combo in combos:
            S = cyclic_pattern(n, combo)
            t0 = time.time()
            best = run_one(S, n, restarts=15, seed=42 + n + sum(combo),
                           margin=1e-4, time_budget=3.0)
            elapsed = time.time() - t0
            if best is None:
                print(f'n={n} {combo}: NO FEASIBLE  ({elapsed:.1f}s)', flush=True)
                continue
            loss, x_best = best
            P = polygon_from_x(x_best, n, 'polar')
            diag = independent_diagnostics(P, S)
            res_dict = {
                'n': n, 'combo': list(combo),
                'family': 'cyclic',
                'loss': loss,
                'eq_rms': diag['eq_rms'],
                'max_spread': diag['max_spread'],
                'max_rel_spread': diag['max_rel_spread'],
                'convexity_margin': diag['convexity_margin'],
                'min_edge_length': diag['min_edge_length'],
                'min_pair_distance': diag['min_pair_distance'],
                'coordinates': [[float(a),float(b)] for a,b in P],
                'S': S,
            }
            results.append(res_dict)
            print(f'n={n} offsets={combo}: loss={loss:.3e} eq_rms={diag["eq_rms"]:.3e} '
                  f'max_spread={diag["max_spread"]:.3e} conv={diag["convexity_margin"]:.3e} '
                  f'min_edge={diag["min_edge_length"]:.3e}  ({elapsed:.1f}s)', flush=True)

    out = REPO_ROOT / 'data' / 'runs' / '2026-05-06' / 'cyclic_survivors_n12_n14.json'
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, 'w') as f:
        json.dump(results, f, indent=2)
    print(f'wrote {out}', flush=True)


if __name__ == '__main__':
    main()
