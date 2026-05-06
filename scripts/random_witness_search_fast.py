#!/usr/bin/env python3
"""Fast variant of random_witness_search with streaming progress.

Streams per-pattern progress, lower restarts, lower max_nfev so the run
finishes within a reasonable wall clock. If a near-miss appears
(eq_rms < 1e-3 with positive convexity margin), we re-run that pattern
with the higher-precision settings of the parent script.

Outputs to data/certificates/2026-05-06/random_witness_search.json.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.search import (  # noqa: E402
    PatternInfo,
    incidence_obstruction_stats,
    search_pattern,
)
from random_witness_search import generate_random_witness  # noqa: E402


def evaluate_pattern_fast(
    name: str,
    n: int,
    S: List[List[int]],
    restarts: int,
    seed: int,
    max_nfev: int,
    margin: float = 1e-4,
    optimizer: str = "trf",
) -> Dict:
    pat = PatternInfo(
        name=name,
        n=n,
        S=S,
        family="random_4regular_noncirculant",
        formula="random",
        notes="random 4-regular witness with pair_cap<=2 and adj_cap<=1",
        trust="EXACTIFICATION",
        lifecycle="exploratory",
    )
    t0 = time.time()
    try:
        result = search_pattern(
            pat,
            mode="polar",
            restarts=restarts,
            seed=seed,
            max_nfev=max_nfev,
            optimizer=optimizer,
            margin=margin,
            verbose=False,
        )
        elapsed = time.time() - t0
        return {
            "ok": True,
            "loss": float(result.loss),
            "eq_rms": float(result.eq_rms),
            "max_spread": float(result.max_spread),
            "max_rel_spread": float(result.max_rel_spread),
            "convexity_margin": float(result.convexity_margin),
            "min_edge_length": float(result.min_edge_length),
            "min_pair_distance": float(result.min_pair_distance),
            "elapsed_sec": elapsed,
            "coordinates": result.coordinates,
        }
    except Exception as exc:
        return {
            "ok": False,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_sec": time.time() - t0,
        }


def run_for_n(
    n: int,
    num_patterns: int,
    restarts: int,
    max_nfev: int,
    seed_base: int,
    margin: float = 1e-4,
    refine_threshold: float = 1e-3,
    refine_restarts: int = 20,
    refine_max_nfev: int = 4000,
    timeout_sec: float = 600.0,
    cancel_on_excellent: bool = True,
) -> Dict:
    rng = np.random.default_rng(seed_base)
    summary: Dict = {
        "n": n,
        "num_requested": num_patterns,
        "num_generated": 0,
        "num_evaluated": 0,
        "num_failed": 0,
        "best_eq_rms": float("inf"),
        "best_max_spread": float("inf"),
        "best_pattern": None,
        "best_coords": None,
        "filter_failure_count": 0,
        "patterns": [],
    }
    near_misses: List[Dict] = []
    t_start = time.time()
    for p_idx in range(num_patterns):
        if time.time() - t_start > timeout_sec:
            print(f"[n={n}] timeout reached at p_idx={p_idx}", flush=True)
            break
        S = generate_random_witness(n, rng, max_attempts=2000)
        if S is None:
            summary["filter_failure_count"] += 1
            continue
        summary["num_generated"] += 1
        stats = incidence_obstruction_stats(S)
        if stats["max_common_selected_neighbors"] > 2:
            summary["filter_failure_count"] += 1
            continue
        name = f"R_n{n}_p{p_idx}"
        seed = seed_base + 7919 * (p_idx + 1)
        ev = evaluate_pattern_fast(name, n, S, restarts=restarts, seed=seed,
                                   max_nfev=max_nfev, margin=margin,
                                   optimizer="trf")
        summary["num_evaluated"] += 1
        if not ev.get("ok", False):
            summary["num_failed"] += 1
            summary["patterns"].append({
                "idx": p_idx, "S": S, "seed": seed,
                "eq_rms": None, "loss": None, "convexity_margin": None,
                "min_pair_distance": None, "error": ev.get("error"),
            })
            print(f"[n={n}] p={p_idx} FAILED: {ev.get('error', '')[:80]}", flush=True)
            continue
        eq_rms = ev["eq_rms"]
        loss = ev["loss"]
        conv = ev["convexity_margin"]
        mpd = ev["min_pair_distance"]
        max_spread = ev["max_spread"]
        max_rel = ev["max_rel_spread"]
        rec = {
            "idx": p_idx, "S": S, "seed": seed,
            "eq_rms": eq_rms, "loss": loss,
            "max_spread": max_spread, "max_rel_spread": max_rel,
            "convexity_margin": conv,
            "min_edge_length": ev["min_edge_length"],
            "min_pair_distance": mpd,
            "elapsed_sec": ev["elapsed_sec"],
        }
        summary["patterns"].append(rec)
        # Print compact progress line
        print(f"[n={n}] p={p_idx:3d} eq_rms={eq_rms:.3e} conv={conv:.2e} "
              f"mpd={mpd:.2e} t={ev['elapsed_sec']:.1f}s", flush=True)
        # If near-miss, refine
        if eq_rms < refine_threshold and conv > margin:
            print(f"[n={n}] p={p_idx} REFINING (near-miss)", flush=True)
            ev_refine = evaluate_pattern_fast(
                name + "_refine", n, S,
                restarts=refine_restarts,
                seed=seed + 1,
                max_nfev=refine_max_nfev,
                margin=margin,
                optimizer="slsqp",
            )
            if ev_refine.get("ok") and ev_refine["eq_rms"] < eq_rms:
                eq_rms = ev_refine["eq_rms"]
                loss = ev_refine["loss"]
                conv = ev_refine["convexity_margin"]
                mpd = ev_refine["min_pair_distance"]
                max_spread = ev_refine["max_spread"]
                max_rel = ev_refine["max_rel_spread"]
                ev = ev_refine
                rec.update({
                    "eq_rms": eq_rms, "loss": loss,
                    "max_spread": max_spread, "max_rel_spread": max_rel,
                    "convexity_margin": conv,
                    "min_edge_length": ev["min_edge_length"],
                    "min_pair_distance": mpd,
                    "elapsed_sec": ev["elapsed_sec"],
                    "refined": True,
                })
                print(f"[n={n}] p={p_idx} REFINED eq_rms={eq_rms:.3e} "
                      f"conv={conv:.2e}", flush=True)
        if eq_rms < summary["best_eq_rms"]:
            summary["best_eq_rms"] = eq_rms
            summary["best_max_spread"] = max_spread
            summary["best_pattern"] = {
                "idx": p_idx, "S": S, "seed": seed,
                "eq_rms": eq_rms, "loss": loss,
                "convexity_margin": conv,
                "min_edge_length": ev["min_edge_length"],
                "min_pair_distance": mpd,
                "max_spread": max_spread,
                "max_rel_spread": max_rel,
            }
            summary["best_coords"] = ev.get("coordinates")
        if eq_rms < refine_threshold and conv > margin:
            near_misses.append(dict(rec))
        if cancel_on_excellent and eq_rms < 1e-6 and conv > margin and mpd > margin:
            summary["promoted"] = True
            print(f"[n={n}] PROMOTED p={p_idx}", flush=True)
            break
    summary["near_misses"] = near_misses
    summary["wall_clock_sec"] = time.time() - t_start
    if not math.isfinite(summary["best_eq_rms"]):
        summary["best_eq_rms"] = None
        summary["best_max_spread"] = None
    return summary


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-values", default="14,16,18,20,22,25")
    ap.add_argument("--num-patterns", type=int, default=50)
    ap.add_argument("--restarts", type=int, default=4)
    ap.add_argument("--max-nfev", type=int, default=600)
    ap.add_argument("--timeout-per-n", type=float, default=420.0,
                    help="seconds before moving to next n")
    ap.add_argument("--seed", type=int, default=20260506)
    ap.add_argument("--margin", type=float, default=1e-4)
    ap.add_argument("--out", default="")
    args = ap.parse_args()

    n_values = [int(v) for v in args.n_values.split(",") if v.strip()]
    out_path = Path(args.out) if args.out else (
        ROOT / "data" / "certificates" / "2026-05-06" / "random_witness_search.json"
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    record: Dict = {
        "type": "erdos97_random_witness_search_v0",
        "trust": "EXACTIFICATION",
        "lifecycle": "exploratory",
        "status": "numerical_only_not_a_proof",
        "started_at_utc": started_at,
        "n_values": n_values,
        "num_patterns_per_n": args.num_patterns,
        "restarts_per_pattern": args.restarts,
        "max_nfev": args.max_nfev,
        "timeout_per_n_sec": args.timeout_per_n,
        "margin": args.margin,
        "seed_base": args.seed,
        "results": {},
        "notes": (
            "Random non-circulant 4-regular witness graphs satisfying "
            "|S_i cap S_j| <= 2 for all i != j and "
            "|S_i cap S_j| <= 1 for cyclic-adjacent (i, j). "
            "Each pattern run via SLSQP polar with strict-convexity margin enforced. "
            "Near-miss patterns (eq_rms < 1e-3 and convex > margin) are auto-refined "
            "with higher restarts and max_nfev. "
            "Numerical near-misses are NOT counterexamples; "
            "exact algebraic data required for any candidate counterexample."
        ),
    }
    overall_promoted = False
    for n in n_values:
        print(f"\n=== n={n} ===", flush=True)
        summary = run_for_n(
            n,
            args.num_patterns,
            args.restarts,
            args.max_nfev,
            seed_base=args.seed + 1000003 * n,
            margin=args.margin,
            timeout_sec=args.timeout_per_n,
        )
        record["results"][str(n)] = summary
        if summary.get("promoted"):
            overall_promoted = True
        print(f"n={n}: gen={summary['num_generated']} "
              f"eval={summary['num_evaluated']} "
              f"fail={summary['num_failed']} "
              f"best_eq_rms={summary['best_eq_rms']} "
              f"near={len(summary.get('near_misses', []))} "
              f"wall={summary['wall_clock_sec']:.1f}s", flush=True)
        # write incremental
        with open(out_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(record, f, indent=2)
            f.write("\n")
    record["promoted_candidate_counterexample"] = overall_promoted
    record["finished_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"\nWrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
