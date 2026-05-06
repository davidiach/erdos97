#!/usr/bin/env python3
"""Benchmark stronger incidence filters at n=9 and n=11.

This script measures:

1. n=9 with the existing vertex-circle filter alone vs. with each new filter
   (F1 triple uniqueness, F2 forced-perpendicularity 2-coloring, F3 mutual-
   rhombus rational closure) to verify they preserve the n=9 kill.

2. n=11 row0=0 partial run with a fixed node budget, comparing baseline
   (vertex-circle only) against the same baseline plus each new filter and
   the combined filter pack.

The output JSON is written to ``data/certificates/stronger_filters_test.json``.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.stronger_filters import StrongerVertexSearch  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "stronger_filters_test.json"


def run_n9_kill_check(
    node_limit: int | None = None,
    no_vc_node_limit: int | None = 60_000,
) -> list[dict[str, object]]:
    """Run n=9 with all filter combinations to confirm 0 full assignments.

    The ``F1_F2_F3_only`` mode (without vertex-circle pruning) is given a
    smaller ``no_vc_node_limit`` because each node is more expensive when only
    the new filters fire.
    """
    out: list[dict[str, object]] = []
    sv = StrongerVertexSearch(9)
    combos = [
        (
            "baseline_vc",
            dict(use_vertex_circle=True, use_triple_unique=False, use_perp_2color=False, use_parallel_endpoint=False, use_mutual_rhombus=False),
            node_limit,
        ),
        (
            "vc_F1",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=False, use_parallel_endpoint=False, use_mutual_rhombus=False),
            node_limit,
        ),
        (
            "vc_F1_F2",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=False, use_mutual_rhombus=False),
            node_limit,
        ),
        (
            "vc_F1_F2_F4",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=True, use_mutual_rhombus=False),
            node_limit,
        ),
        (
            "vc_F1_F2_F3_F4",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=True, use_mutual_rhombus=True),
            node_limit,
        ),
        (
            "F1_F2_F3_F4_only",
            dict(use_vertex_circle=False, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=True, use_mutual_rhombus=True),
            no_vc_node_limit,
        ),
    ]
    for label, kwargs, limit in combos:
        t0 = perf_counter()
        res = sv.exhaustive_search(node_limit=limit, **kwargs)
        elapsed = perf_counter() - t0
        out.append(
            {
                "label": label,
                "kwargs": kwargs,
                "node_limit": limit,
                "nodes": res.nodes_visited,
                "full": res.full_assignments,
                "aborted": res.aborted,
                "counts": dict(sorted(res.counts.items())),
                "elapsed_seconds": round(elapsed, 3),
            }
        )
        print(
            f"n=9 {label}: nodes={res.nodes_visited} full={res.full_assignments} "
            f"counts={dict(sorted(res.counts.items()))} elapsed={elapsed:.2f}s",
            flush=True,
        )
    return out


def run_n11_row0_slice(
    node_limit: int = 20_000, time_budget: float | None = None
) -> list[dict[str, object]]:
    """Run n=11 row0=0 slice for each filter combo with a node budget.

    All variants run with the same node_limit. Comparable metrics are:
    * total partial-prune events (sum of counts) per node;
    * elapsed wall time per node (per-node cost);
    * which filter classes actually fired.
    """
    out: list[dict[str, object]] = []
    sv = StrongerVertexSearch(11)
    combos = [
        (
            "baseline_vc",
            dict(use_vertex_circle=True, use_triple_unique=False, use_perp_2color=False, use_parallel_endpoint=False, use_mutual_rhombus=False),
        ),
        (
            "vc_F1",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=False, use_parallel_endpoint=False, use_mutual_rhombus=False),
        ),
        (
            "vc_F1_F2",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=False, use_mutual_rhombus=False),
        ),
        (
            "vc_F1_F2_F4",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=True, use_mutual_rhombus=False),
        ),
        (
            "vc_F1_F2_F3_F4",
            dict(use_vertex_circle=True, use_triple_unique=True, use_perp_2color=True, use_parallel_endpoint=True, use_mutual_rhombus=True),
        ),
    ]
    for label, kwargs in combos:
        t0 = perf_counter()
        res = sv.exhaustive_search(
            row0_start=0, row0_end=1, node_limit=node_limit, **kwargs
        )
        elapsed = perf_counter() - t0
        prunes = sum(v for k, v in res.counts.items() if k.startswith("partial_") or k.startswith("row0_"))
        out.append(
            {
                "label": label,
                "kwargs": kwargs,
                "node_limit": node_limit,
                "nodes": res.nodes_visited,
                "full": res.full_assignments,
                "aborted": res.aborted,
                "counts": dict(sorted(res.counts.items())),
                "partial_prune_events": prunes,
                "elapsed_seconds": round(elapsed, 3),
                "nodes_per_sec": (
                    round(res.nodes_visited / elapsed, 1) if elapsed > 0 else None
                ),
            }
        )
        print(
            f"n=11 row0=0 {label}: nodes={res.nodes_visited} full={res.full_assignments} "
            f"prunes={prunes} elapsed={elapsed:.2f}s "
            f"nps={out[-1]['nodes_per_sec']}",
            flush=True,
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", default=str(DEFAULT_OUT))
    parser.add_argument("--n11-node-limit", type=int, default=5_000)
    parser.add_argument("--n9-no-vc-node-limit", type=int, default=20_000)
    parser.add_argument(
        "--skip-n11", action="store_true", help="skip the n=11 row0=0 slice"
    )
    parser.add_argument(
        "--skip-n9", action="store_true", help="skip the n=9 kill check"
    )
    args = parser.parse_args()

    payload: dict[str, object] = {
        "type": "stronger_filters_test_v1",
        "trust": "DEVELOPMENT_BENCHMARK_NOT_AN_ARTIFACT",
        "notes": [
            "Benchmarks new partial-assignment incidence filters versus baseline.",
            "Baseline is vertex-circle pruning only.",
            "F1 = triple uniqueness; F2 = forced-perp 2-coloring; F3 = mutual-rhombus rational closure.",
            "n=9 kill check confirms each combo still yields 0 full assignments.",
            "n=11 row0=0 slice shows node count under a fixed node budget.",
            "Public claim status of Erdos #97 is unchanged.",
        ],
    }

    if not args.skip_n9:
        print("=== n=9 kill check ===", flush=True)
        payload["n9_kill_check"] = run_n9_kill_check(
            no_vc_node_limit=args.n9_no_vc_node_limit
        )

    if not args.skip_n11:
        print("=== n=11 row0=0 slice ===", flush=True)
        payload["n11_row0_slice"] = run_n11_row0_slice(node_limit=args.n11_node_limit)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
