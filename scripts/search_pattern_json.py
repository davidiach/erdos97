#!/usr/bin/env python3
"""Run the numerical geometry search on a selected-witness JSON pattern."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.pattern_io import load_pattern_json  # noqa: E402
from erdos97.search import (  # noqa: E402
    PatternInfo,
    result_to_json,
    search_pattern,
    write_certificate_template,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSON pattern or mined motif artifact")
    parser.add_argument("--name", help="override pattern name")
    parser.add_argument("--mode", choices=["polar", "direct", "support"], default="polar")
    parser.add_argument("--optimizer", choices=["trf", "slsqp"], default="slsqp")
    parser.add_argument("--restarts", type=int, default=20)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-nfev", type=int, default=3000)
    parser.add_argument("--margin", type=float, default=1e-3)
    parser.add_argument("--out", type=Path, help="write full numerical result JSON")
    parser.add_argument("--certificate", type=Path, help="write exactification certificate template")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    args = parser.parse_args()

    name, rows = load_pattern_json(args.input)
    if args.name:
        name = args.name
    pattern = PatternInfo(
        name=name,
        n=len(rows),
        S=rows,
        family="json",
        formula=str(args.input),
        notes="loaded from selected-witness JSON; numerical evidence only",
    )
    try:
        result = search_pattern(
            pattern,
            mode=args.mode,
            restarts=args.restarts,
            seed=args.seed,
            max_nfev=args.max_nfev,
            optimizer=args.optimizer,
            margin=args.margin,
        )
    except RuntimeError as exc:
        summary = {
            "pattern_name": name,
            "n": len(rows),
            "mode": f"{args.mode}_{args.optimizer}",
            "success": False,
            "message": str(exc),
            "interpretation": (
                "The numerical optimizer did not return a usable run. This is not "
                "an exact obstruction or a counterexample."
            ),
        }
        if args.json:
            print(json.dumps(summary, indent=2, sort_keys=True))
        else:
            print("pattern  n  mode  success  message")
            print(f"{name}  {len(rows)}  {args.mode}_{args.optimizer}  False  {exc}")
        return 2
    data = result_to_json(result)
    summary = {
        key: data[key]
        for key in [
            "pattern_name",
            "n",
            "mode",
            "loss",
            "eq_rms",
            "max_spread",
            "max_rel_spread",
            "convexity_margin",
            "min_edge_length",
            "min_pair_distance",
            "success",
            "elapsed_sec",
        ]
    }
    summary["interpretation"] = (
        "NUMERICAL_EVIDENCE only. A positive residual is not an exact obstruction; "
        "a low residual is not a counterexample without exact or interval certificates."
    )

    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(data, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.certificate:
        args.certificate.parent.mkdir(parents=True, exist_ok=True)
        write_certificate_template(str(args.certificate), result)

    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("pattern  n  mode  eq_rms  max_spread  convexity  min_edge  success")
        print(
            f"{summary['pattern_name']}  {summary['n']}  {summary['mode']}  "
            f"{summary['eq_rms']:.6g}  {summary['max_spread']:.6g}  "
            f"{summary['convexity_margin']:.6g}  "
            f"{summary['min_edge_length']:.6g}  {summary['success']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
