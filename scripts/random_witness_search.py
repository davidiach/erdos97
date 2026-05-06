#!/usr/bin/env python3
"""Random non-circulant 4-regular witness search for Erdős #97.

Generates random 4-regular witness systems satisfying:
  * S_i a 4-subset of {0..n-1}\{i}
  * |S_i cap S_j| <= 2 for all i != j (pair-overlap cap)
  * |S_i cap S_j| <= 1 for cyclic-adjacent (i, j) (crossing-bisector lemma)

For each pattern: SLSQP optimization with strict-convexity margin 1e-4,
polar parameterization, multiple restarts. Tracks best (lowest residual).

Outputs to data/certificates/2026-05-06/random_witness_search.json.
"""
from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

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


def generate_random_witness(
    n: int,
    rng: np.random.Generator,
    max_attempts: int = 5000,
    adjacent_cap: int = 1,
    pair_cap: int = 2,
) -> Optional[List[List[int]]]:
    """Generate a random 4-regular witness system at n.

    Constraints:
        - row i is a 4-subset of {0..n-1}\{i}
        - |S_i cap S_j| <= pair_cap (default 2) for all i != j
        - |S_i cap S_j| <= adjacent_cap (default 1) for j == i+1 mod n

    Returns None if no valid system was constructed within max_attempts.
    """
    universe = list(range(n))
    for attempt in range(max_attempts):
        S: List[Optional[List[int]]] = [None] * n
        # Random index ordering
        order = list(range(n))
        rng.shuffle(order)
        ok = True
        for idx in order:
            # Random 4-subset of {0..n-1}\{idx} that respects caps with already-set rows
            candidates = [j for j in universe if j != idx]
            row_attempts = 0
            chosen = None
            while row_attempts < 200:
                row_attempts += 1
                # sample 4 distinct
                pick = sorted(rng.choice(candidates, size=4, replace=False).tolist())
                # Check pair cap with existing rows
                ok_caps = True
                for k in range(n):
                    if k == idx or S[k] is None:
                        continue
                    common = len(set(S[k]).intersection(pick))
                    if common > pair_cap:
                        ok_caps = False
                        break
                    if (k == (idx - 1) % n or k == (idx + 1) % n) and common > adjacent_cap:
                        ok_caps = False
                        break
                if ok_caps:
                    chosen = pick
                    break
            if chosen is None:
                ok = False
                break
            S[idx] = chosen
        if ok:
            return [list(map(int, row)) for row in S]  # type: ignore[arg-type]
    return None


def evaluate_pattern(
    name: str,
    n: int,
    S: List[List[int]],
    restarts: int,
    seed: int,
    margin: float = 1e-4,
) -> Dict:
    """Run SLSQP-based search on the given pattern, return summary."""
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
            max_nfev=4000,
            optimizer="slsqp",
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
    seed_base: int,
    margin: float = 1e-4,
    cancel_on_excellent: bool = True,
) -> Dict:
    """Generate and evaluate num_patterns random witness systems at n."""
    rng = np.random.default_rng(seed_base)
    summary: Dict = {
        "n": n,
        "num_requested": num_patterns,
        "num_generated": 0,
        "num_evaluated": 0,
        "best_eq_rms": float("inf"),
        "best_max_spread": float("inf"),
        "best_pattern": None,
        "best_coords": None,
        "filter_failure_count": 0,
        "patterns": [],  # short list with key residuals (no coords)
    }
    near_misses: List[Dict] = []
    for p_idx in range(num_patterns):
        S = generate_random_witness(n, rng, max_attempts=2000)
        if S is None:
            summary["filter_failure_count"] += 1
            continue
        summary["num_generated"] += 1
        # Sanity check stats
        stats = incidence_obstruction_stats(S)
        if stats["max_common_selected_neighbors"] > 2:
            summary["filter_failure_count"] += 1
            continue
        # Evaluate via SLSQP
        name = f"R_n{n}_p{p_idx}"
        seed = seed_base + 7919 * (p_idx + 1)
        ev = evaluate_pattern(name, n, S, restarts=restarts, seed=seed, margin=margin)
        summary["num_evaluated"] += 1
        if not ev.get("ok", False):
            summary["patterns"].append({
                "idx": p_idx,
                "S": S,
                "seed": seed,
                "eq_rms": None,
                "loss": None,
                "convexity_margin": None,
                "min_pair_distance": None,
                "error": ev.get("error"),
            })
            continue
        eq_rms = ev["eq_rms"]
        loss = ev["loss"]
        conv = ev["convexity_margin"]
        mpd = ev["min_pair_distance"]
        max_spread = ev["max_spread"]
        max_rel = ev["max_rel_spread"]
        rec = {
            "idx": p_idx,
            "S": S,
            "seed": seed,
            "eq_rms": eq_rms,
            "loss": loss,
            "max_spread": max_spread,
            "max_rel_spread": max_rel,
            "convexity_margin": conv,
            "min_edge_length": ev["min_edge_length"],
            "min_pair_distance": mpd,
            "elapsed_sec": ev["elapsed_sec"],
        }
        summary["patterns"].append(rec)
        if eq_rms < summary["best_eq_rms"]:
            summary["best_eq_rms"] = eq_rms
            summary["best_max_spread"] = max_spread
            summary["best_pattern"] = {
                "idx": p_idx,
                "S": S,
                "seed": seed,
                "eq_rms": eq_rms,
                "loss": loss,
                "convexity_margin": conv,
                "min_edge_length": ev["min_edge_length"],
                "min_pair_distance": mpd,
                "max_spread": max_spread,
                "max_rel_spread": max_rel,
            }
            summary["best_coords"] = ev.get("coordinates")
        # Promotable near-miss?
        if eq_rms < 1e-3 and conv > margin:
            near_misses.append(rec)
        if cancel_on_excellent and eq_rms < 1e-6 and conv > margin and mpd > margin:
            summary["promoted"] = True
            break
    summary["near_misses"] = near_misses
    if not math.isfinite(summary["best_eq_rms"]):
        summary["best_eq_rms"] = None
        summary["best_max_spread"] = None
    return summary


def main() -> None:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--n-values", default="14,16,18,20,22,25",
                    help="comma-separated n values")
    ap.add_argument("--num-patterns", type=int, default=50,
                    help="patterns per n (target)")
    ap.add_argument("--restarts", type=int, default=10,
                    help="restarts per pattern")
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
        "margin": args.margin,
        "seed_base": args.seed,
        "results": {},
        "notes": (
            "Random non-circulant 4-regular witness graphs satisfying "
            "|S_i cap S_j| <= 2 for all i != j and "
            "|S_i cap S_j| <= 1 for cyclic-adjacent (i, j). "
            "Each pattern run via SLSQP polar with strict-convexity margin enforced. "
            "Numerical near-misses are NOT counterexamples; exact algebraic data required."
        ),
    }

    overall_promoted = False
    for n in n_values:
        print(f"\n=== n={n} ===", flush=True)
        t0 = time.time()
        summary = run_for_n(
            n,
            args.num_patterns,
            args.restarts,
            seed_base=args.seed + 1000003 * n,
            margin=args.margin,
        )
        summary["wall_clock_sec"] = time.time() - t0
        record["results"][str(n)] = summary
        if summary.get("promoted"):
            overall_promoted = True
        print(f"n={n}: generated={summary['num_generated']} "
              f"evaluated={summary['num_evaluated']} "
              f"best_eq_rms={summary['best_eq_rms']} "
              f"near_misses={len(summary.get('near_misses', []))} "
              f"wall={summary['wall_clock_sec']:.1f}s",
              flush=True)

    record["promoted_candidate_counterexample"] = overall_promoted
    record["finished_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")

    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, indent=2)
        f.write("\n")
    print(f"\nWrote {out_path}", flush=True)


if __name__ == "__main__":
    main()
