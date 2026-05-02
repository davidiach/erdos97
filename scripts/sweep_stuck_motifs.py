#!/usr/bin/env python3
"""Sweep bounded stuck-motif mining over n and stuck-size ranges."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.stuck_motif_sweep import SweepConfig, sweep_stuck_motifs  # noqa: E402


def parse_csv_ints(raw: str) -> list[int]:
    try:
        values = [int(item.strip()) for item in raw.split(",") if item.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"invalid integer list: {raw}") from exc
    if not values:
        raise argparse.ArgumentTypeError("list must not be empty")
    return values


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    n_group = parser.add_mutually_exclusive_group(required=True)
    n_group.add_argument("--n", type=parse_csv_ints, help="comma-separated n values")
    n_group.add_argument("--n-range", nargs=2, type=int, metavar=("MIN", "MAX"), help="inclusive n range")
    parser.add_argument("--stuck-sizes", type=parse_csv_ints, default=[4], help="comma-separated stuck sizes")
    parser.add_argument("--max-models", type=int, default=100)
    parser.add_argument("--solver-seed", type=int, default=0)
    parser.add_argument(
        "--variable-prefix",
        default="sweep",
        help="base prefix; n, stuck size, and seed are appended for each item",
    )
    parser.add_argument("--require-no-forward-ear-order", action="store_true")
    parser.add_argument("--fragile-cover-max-size", type=int)
    parser.add_argument("--radius-node-limit", type=int, default=100_000)
    parser.add_argument("--run-geometry", action="store_true")
    parser.add_argument("--geometry-optimizer", choices=["trf", "slsqp"], default="trf")
    parser.add_argument("--geometry-mode", choices=["polar", "direct", "support"], default="polar")
    parser.add_argument("--geometry-restarts", type=int, default=3)
    parser.add_argument("--geometry-max-nfev", type=int, default=300)
    parser.add_argument("--geometry-margin", type=float, default=1e-3)
    parser.add_argument("--geometry-seed", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-artifact", type=Path)
    args = parser.parse_args()

    if args.n is not None:
        n_values = args.n
    else:
        start, end = args.n_range
        if end < start:
            raise SystemExit("--n-range MAX must be >= MIN")
        n_values = list(range(start, end + 1))

    payload = sweep_stuck_motifs(
        SweepConfig(
            n_values=n_values,
            stuck_sizes=args.stuck_sizes,
            max_models=args.max_models,
            solver_seed=args.solver_seed,
            variable_prefix=args.variable_prefix,
            require_no_forward_ear_order=args.require_no_forward_ear_order,
            radius_node_limit=args.radius_node_limit,
            fragile_cover_max_size=args.fragile_cover_max_size,
            run_geometry=args.run_geometry,
            geometry_optimizer=args.geometry_optimizer,
            geometry_mode=args.geometry_mode,
            geometry_restarts=args.geometry_restarts,
            geometry_max_nfev=args.geometry_max_nfev,
            geometry_margin=args.geometry_margin,
            geometry_seed=args.geometry_seed,
        )
    )

    if args.write_artifact:
        args.write_artifact.parent.mkdir(parents=True, exist_ok=True)
        args.write_artifact.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n  stuck-size  status  models  forward-ear  radius  fingerprint  geometry-eq-rms")
        for item in payload["items"]:
            geometry = item["geometry"]
            eq_rms = "-"
            if isinstance(geometry, dict) and geometry.get("status") == "RAN":
                eq_rms = f"{geometry['eq_rms']:.6g}"
            motif = item["motif"]
            fingerprint = "-"
            if isinstance(motif, dict):
                fingerprint = motif["fingerprint"]["cyclic_dihedral_sha256"][:12]
            print(
                f"{item['n']}  {item['stuck_size']}  {item['status']}  "
                f"{item['models_checked']}  {item['motif_forward_ear_order']}  "
                f"{item['radius_status']}  {fingerprint}  {eq_rms}"
            )
        print("summary:", payload["summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
