#!/usr/bin/env python3
"""Mine bounded fixed-selection stuck motifs with SMT plus exact filters."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.stuck_motif_search import (  # noqa: E402
    MotifSearchConfig,
    mine_stuck_motif,
    search_result_to_json,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, required=True, help="number of vertices")
    parser.add_argument("--stuck-size", type=int, required=True, help="forced stuck subset size")
    parser.add_argument("--max-models", type=int, default=100, help="maximum SMT models to inspect")
    parser.add_argument("--solver-seed", type=int, default=0, help="Z3 random seed")
    parser.add_argument(
        "--radius-node-limit",
        type=int,
        default=100_000,
        help="node limit for radius propagation filter",
    )
    parser.add_argument(
        "--fragile-cover-max-size",
        type=int,
        help="maximum fragile-cover subset size to enumerate",
    )
    parser.add_argument("--allow-uncovered", action="store_true", help="do not require all labels to appear in selected rows")
    parser.add_argument("--allow-adjacent-two-overlap", action="store_true", help="do not reject adjacent source rows with two overlaps")
    parser.add_argument("--allow-crossing-violations", action="store_true", help="do not reject two-overlap crossing violations")
    parser.add_argument("--allow-odd-cycle", action="store_true", help="do not reject odd forced-perpendicularity cycles")
    parser.add_argument("--allow-radius-obstruction", action="store_true", help="do not reject radius-cycle obstructions")
    parser.add_argument("--allow-no-fragile-cover", action="store_true", help="do not require incidence-level fragile cover")
    parser.add_argument(
        "--require-no-forward-ear-order",
        action="store_true",
        help="reject models that admit a forward ear order from some three-vertex seed",
    )
    parser.add_argument("--json", action="store_true", help="print full JSON")
    parser.add_argument("--write-certificate", type=Path, help="write JSON result to this path")
    parser.add_argument("--assert-found", action="store_true", help="assert a motif is found")
    args = parser.parse_args()

    config = MotifSearchConfig(
        n=args.n,
        stuck_size=args.stuck_size,
        max_models=args.max_models,
        solver_seed=args.solver_seed,
        radius_node_limit=args.radius_node_limit,
        require_all_rows_cover=not args.allow_uncovered,
        require_adjacent_overlap=not args.allow_adjacent_two_overlap,
        require_crossing=not args.allow_crossing_violations,
        require_no_odd_cycle=not args.allow_odd_cycle,
        require_radius_pass=not args.allow_radius_obstruction,
        require_fragile_cover=not args.allow_no_fragile_cover,
        require_no_forward_ear_order=args.require_no_forward_ear_order,
        fragile_cover_max_size=args.fragile_cover_max_size,
    )
    result = mine_stuck_motif(config)
    payload = search_result_to_json(result)

    if args.assert_found and result.status != "FOUND":
        raise AssertionError(f"expected FOUND, got {result.status}")

    if args.write_certificate:
        args.write_certificate.parent.mkdir(parents=True, exist_ok=True)
        args.write_certificate.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n  stuck-size  status  models-checked  rejection-counts")
        print(
            f"{args.n}  {args.stuck_size}  {result.status}  "
            f"{result.models_checked}  {result.rejection_counts}"
        )
        if result.status == "FOUND" and result.motif is not None:
            motif = result.motif
            search = motif["stuck_search"]
            print(
                "motif:",
                motif["pattern"],
                "minimal stuck size",
                search["minimal_size"],
                "forward-ear",
                motif["forward_ear_order"]["exists"],
                "radius",
                motif["filters"]["radius_propagation"]["status"],
                "fingerprint",
                motif["fingerprint"]["cyclic_dihedral_sha256"][:12],
            )
        if args.assert_found:
            print("OK: stuck motif found")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
