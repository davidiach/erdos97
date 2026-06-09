#!/usr/bin/env python3
"""Dynamic-witness (free-pattern) search CLI for Erdos Problem #97.

This drives ``erdos97.dynamic_witness_search``: every center re-selects its
best witness 4-set at every evaluation, so one continuous run probes all
selected-witness patterns reachable by the configuration family, instead of
one registered catalog pattern at a time.

Outputs are NUMERICAL_EVIDENCE / HEURISTIC diagnostics only.  No output of
this script is a proof, and no output of this script is a counterexample;
the repo exactification standards gate any claim upgrade.

Examples:

  python scripts/search_dynamic_witness.py --m 6 --t 3 --restarts 40 --json
  python scripts/search_dynamic_witness.py --sweep --restarts 16 \
      --seed 20260609 --out data/runs/dynamic_witness_sweep_2026-06-09
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.dynamic_witness_search import GuardConfig, search_cell  # noqa: E402

DEFAULT_SWEEP: list[tuple[int, int]] = (
    [(m, 2) for m in range(5, 19)]
    + [(m, 3) for m in range(4, 13)]
    + [(m, 4) for m in range(3, 10)]
    + [(m, 5) for m in range(3, 8)]
    + [(m, 6) for m in range(3, 7)]
    + [(m, 7) for m in (3, 4, 5)]
    + [(m, 8) for m in (3, 4)]
    + [(3, 9), (3, 10)]
    + [(1, n) for n in (10, 11, 12, 13, 14)]
)

CONTROL_CELLS: list[tuple[int, int]] = [(12, 2), (6, 4)]


def run_cells(
    cells: list[tuple[int, int]],
    restarts: int,
    asym_restarts: int,
    seed: int,
    max_cycles: int,
    require_convexity: bool,
) -> list[dict[str, object]]:
    guards = GuardConfig(require_convexity=require_convexity)
    records: list[dict[str, object]] = []
    for index, (m, t) in enumerate(cells):
        cell_restarts = asym_restarts if m == 1 else restarts
        record = search_cell(
            m,
            t,
            restarts=cell_restarts,
            seed=seed + 1000 * index,
            guards=guards,
            max_cycles=max_cycles,
        )
        records.append(record)
        best_convex = record["best_convex"]
        best = record["best"]
        convex_text = (
            f"{best_convex['max_relative_spread']:.3e}"
            f" (margin {best_convex['convexity']['min_cross_normalized']:.1e})"
            if best_convex is not None
            else "none"
        )
        print(
            f"m={m} t={t} n={record['n']} "
            f"convex={record['convex_restarts']}/{record['restarts']} "
            f"best_convex_rel_spread={convex_text} "
            f"best_any={best['max_relative_spread']:.3e}",
            flush=True,
        )
    return records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--m", type=int, help="cyclic symmetry order (1 = asymmetric)")
    parser.add_argument("--t", type=int, help="number of orbits")
    parser.add_argument("--sweep", action="store_true", help="run the default grid")
    parser.add_argument("--restarts", type=int, default=16)
    parser.add_argument("--asym-restarts", type=int, default=8)
    parser.add_argument("--max-cycles", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260609)
    parser.add_argument(
        "--no-convexity-control",
        action="store_true",
        help="drop the convexity guard (negative-control mode only)",
    )
    parser.add_argument(
        "--with-controls",
        action="store_true",
        help="also run the built-in nonconvex control cells",
    )
    parser.add_argument("--out", type=Path, help="directory for the JSON artifact")
    parser.add_argument("--json", action="store_true", help="print full JSON")
    args = parser.parse_args()

    if args.sweep:
        cells = list(DEFAULT_SWEEP)
    elif args.m is not None and args.t is not None:
        cells = [(args.m, args.t)]
    else:
        parser.error("pass --sweep or both --m and --t")

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    records = run_cells(
        cells,
        restarts=args.restarts,
        asym_restarts=args.asym_restarts,
        seed=args.seed,
        max_cycles=args.max_cycles,
        require_convexity=not args.no_convexity_control,
    )
    control_records: list[dict[str, object]] = []
    if args.with_controls:
        print("-- nonconvex control cells (convexity guard off) --", flush=True)
        control_records = run_cells(
            CONTROL_CELLS,
            restarts=args.restarts,
            asym_restarts=args.asym_restarts,
            seed=args.seed + 999_999,
            max_cycles=args.max_cycles,
            require_convexity=False,
        )

    convex_best = [
        record for record in records if record["best_convex"] is not None
    ]
    min_rel = min(
        (record["best_convex"]["max_relative_spread"] for record in convex_best),
        default=None,
    )
    payload = {
        "tool": "scripts/search_dynamic_witness.py",
        "mode": "dynamic_witness_free_pattern",
        "trust": "NUMERICAL_EVIDENCE",
        "interpretation": (
            "search diagnostics only; not a proof and not a counterexample; "
            "candidate status requires the repo exactification standards"
        ),
        "started_utc": started,
        "seed": args.seed,
        "restarts": args.restarts,
        "asym_restarts": args.asym_restarts,
        "max_cycles": args.max_cycles,
        "convexity_guard": not args.no_convexity_control,
        "cells": records,
        "nonconvex_controls": control_records,
        "best_strictly_convex_relative_spread": min_rel,
    }
    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        out_path = args.out / "summary.json"
        out_path.write_text(json.dumps(payload, indent=1, sort_keys=True) + "\n")
        print(f"wrote {out_path}")
    if args.json:
        print(json.dumps(payload, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
