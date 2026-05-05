#!/usr/bin/env python3
"""Check fragile-cover hypergraph constraints for the block-6 family."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.fragile_hypergraph import (  # noqa: E402
    block6_family,
    canonical_witness_map,
    check_fragile_hypergraph,
    check_to_json,
    full_extension_to_json,
    full_selected_extension,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blocks", type=int, default=2, help="number of six-vertex blocks")
    parser.add_argument("--json", action="store_true", help="print JSON instead of a summary")
    parser.add_argument("--assert-ok", action="store_true", help="assert the checks pass")
    parser.add_argument(
        "--check-full-extension",
        action="store_true",
        help="also search for a full selected-witness incidence extension",
    )
    parser.add_argument(
        "--assert-full-extension",
        action="store_true",
        help="assert the optional full-extension check passes",
    )
    parser.add_argument(
        "--max-extension-nodes",
        type=int,
        default=100_000,
        help="maximum backtracking nodes for --check-full-extension",
    )
    parser.add_argument("--write-certificate", help="write JSON result to this path")
    args = parser.parse_args()

    n, rows = block6_family(args.blocks)
    witness_map = canonical_witness_map(n, rows)
    result = check_fragile_hypergraph(n, rows, witness_map=witness_map)
    payload = {
        **check_to_json(result),
        "family": "block6",
        "blocks": args.blocks,
        "rows": {str(center): row for center, row in sorted(rows.items())},
        "witness_map": {str(vertex): center for vertex, center in sorted(witness_map.items())},
        "interpretation": (
            "abstract hypergraph only; passing this check is not a Euclidean "
            "realization or counterexample"
        ),
    }
    extension = None
    if args.check_full_extension or args.assert_full_extension:
        extension = full_selected_extension(
            n,
            rows,
            max_nodes=args.max_extension_nodes,
        )
        payload["full_selected_extension"] = full_extension_to_json(extension)

    if args.assert_ok and not result.ok:
        raise AssertionError("expected block6 fragile hypergraph checks to pass")
    if args.assert_full_extension and (extension is None or not extension.ok):
        raise AssertionError("expected a full selected-witness extension")

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        status = "PASS" if result.ok else "FAIL"
        print("family  blocks  n  fragile centers  result")
        print(f"block6  {args.blocks}  {n}  {len(rows)}  {status}")
        if extension is not None:
            extension_status = "PASS" if extension.ok else "FAIL"
            print(
                "full selected extension: "
                f"{extension_status} ({extension.nodes_visited} nodes)"
            )
            if extension.failure_reason:
                print(f"extension reason: {extension.failure_reason}")
        if args.assert_ok:
            print("OK: fragile hypergraph expectation verified")
        if args.assert_full_extension:
            print("OK: full selected-witness extension verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
