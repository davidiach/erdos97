#!/usr/bin/env python3
"""Exploratory n=12 vertex-circle row0 singleton-slice driver.

This is a partial finite-case probe at n=12. It is NOT a finite-case
artifact; the repo source-of-truth strongest local result remains
machine-checked n <= 8, with review-pending n=9 and n=10 finite-case
extensions. This script merely runs a handful of row0 singleton slices
of the same generic vertex-circle search at n=12, in order to gauge
whether the same filters that work for n <= 11 (per existing partial
n=11 timing data) might extend to n=12 within a feasible wallclock.
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fast_vertex_search import FastVertexSearch  # noqa: E402

N = 12
ROW_SIZE = 4


def run_slices_in_worker(
    args: tuple[list[int], int | None, float | None],
) -> list[dict[str, object]]:
    """Run a sequence of row0 singleton slices in a single worker.

    The engine's __init__ for n=12 takes ~50s (compatibility bitset build), so
    we amortize that cost by reusing one FastVertexSearch instance per worker
    for many slices.
    """
    row0_indices, node_limit, time_budget = args
    init_start = monotonic()
    search = FastVertexSearch(N, row_size=ROW_SIZE)
    init_elapsed = monotonic() - init_start

    out: list[dict[str, object]] = []
    for row0_index in row0_indices:
        start = monotonic()
        result = search.search_one_row0(
            row0_index,
            time_budget=time_budget,
            node_limit=node_limit,
        )
        elapsed = monotonic() - start
        out.append(
            {
                "row0_start": row0_index,
                "row0_end": row0_index + 1,
                "row0_mask": result.row0_mask,
                "nodes": result.nodes_visited,
                "full": result.full_assignments,
                "aborted": result.aborted,
                "counts": dict(sorted(result.counts.items())),
                "elapsed_seconds": elapsed,
                "node_limit": node_limit,
                "time_budget_seconds": time_budget,
                "init_amortized_seconds": init_elapsed,
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", type=int, default=0, help="first row0 index (inclusive)")
    parser.add_argument("--end", type=int, default=5, help="last row0 index (exclusive)")
    parser.add_argument(
        "--node-limit",
        type=int,
        default=None,
        help="abort each slice once node count reaches this (default: no cap)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="multiprocessing workers (default 4)",
    )
    parser.add_argument(
        "--time-budget-seconds",
        type=float,
        default=None,
        help="advisory hint stored in payload only; engine has no native timer",
    )
    parser.add_argument(
        "--out",
        default=str(
            ROOT / "data" / "certificates" / "2026-05-06" / "n12_partial.json"
        ),
        help="output JSON path",
    )
    args = parser.parse_args()

    if args.start < 0 or args.end <= args.start:
        raise SystemExit("invalid [start,end)")

    # Build singleton slices [i,i+1) for i in [start,end), then split across
    # workers in round-robin order so each worker amortizes one engine init
    # over multiple slices.
    indices = list(range(args.start, args.end))
    workers = max(1, args.workers)
    bins: list[list[int]] = [[] for _ in range(workers)]
    for k, idx in enumerate(indices):
        bins[k % workers].append(idx)
    payloads = [
        (bin_indices, args.node_limit, args.time_budget_seconds)
        for bin_indices in bins
        if bin_indices
    ]

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"n=12 partial: running row0 singletons [{args.start},{args.end}) "
        f"with {workers} worker(s); node_limit={args.node_limit}; "
        f"per-worker bins={[len(b) for b in bins if b]}"
    )

    start = monotonic()
    if workers <= 1:
        per_worker = [run_slices_in_worker(payload) for payload in payloads]
    else:
        with mp.get_context("fork").Pool(processes=workers) as pool:
            per_worker = pool.map(run_slices_in_worker, payloads)
    rows = [row for chunk in per_worker for row in chunk]
    rows.sort(key=lambda row: int(row["row0_start"]))
    elapsed = monotonic() - start

    total_nodes = sum(int(row["nodes"]) for row in rows)
    total_full = sum(int(row["full"]) for row in rows)
    aborted_any = any(bool(row["aborted"]) for row in rows)

    payload = {
        "type": "n12_vertex_circle_extension_probe_v0",
        "trust": "EXPLORATORY_TIMINGS_NOT_AN_ARTIFACT",
        "scope": (
            "Exploratory n=12 row0 singleton-slice probe of the same "
            "selected-witness vertex-circle search used at n=9, n=10, n=11. "
            "Does not update the repo-local n <= 8 result. Does not claim "
            "a finite-case artifact at n=12; only reports per-slice "
            "timings, node counts, and whether each completed slice "
            "returned 0 full assignments."
        ),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The repo source-of-truth strongest local result remains n <= 8.",
            "Review-pending n=9 and n=10 vertex-circle extensions remain unchanged.",
            "Partial n=11 timing data (2026-05-05) is the prior probe.",
            "n=12 here is partial; full coverage is not attempted.",
            (
                "n=12 row0 singletons admit MANY full survivors of the "
                "vertex-circle filter, in stark contrast with n<=10 where "
                "every slice returned full=0. Therefore the same "
                "selected-witness + vertex-circle filter that closes "
                "n<=10 is INSUFFICIENT at n=12; further geometric or "
                "metric filters (Ptolemy, Kalmanson, metric LP) would "
                "have to absorb these survivors before any n=12 "
                "finite-case kill could be claimed."
            ),
        ],
        "n": N,
        "row_size": ROW_SIZE,
        "pair_cap": 2,
        "max_indegree": (2 * (N - 1)) // (ROW_SIZE - 1),
        "engine": "erdos97.fast_vertex_search.FastVertexSearch",
        "row0_choice_count_total": 330,
        "row0_singleton_range_attempted": [args.start, args.end],
        "workers": args.workers,
        "node_limit": args.node_limit,
        "time_budget_seconds": args.time_budget_seconds,
        "wallclock_seconds": elapsed,
        "total_nodes": total_nodes,
        "total_full": total_full,
        "aborted_any": aborted_any,
        "rows": rows,
    }

    out_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(
        f"completed: wallclock={elapsed:.1f}s nodes={total_nodes} full={total_full} "
        f"aborted_any={aborted_any}; wrote {out_path}"
    )
    for row in rows:
        print(
            f"  row0={row['row0_start']}: nodes={row['nodes']:>10} full={row['full']} "
            f"aborted={row['aborted']} elapsed={row['elapsed_seconds']:.1f}s "
            f"counts={row['counts']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
