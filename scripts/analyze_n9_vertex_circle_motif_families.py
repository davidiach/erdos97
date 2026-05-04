#!/usr/bin/env python3
"""Canonicalize motif families in the n=9 vertex-circle frontier."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    assert_expected_motif_family_counts,
    motif_family_summary,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_vertex_circle_motif_families.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = motif_family_summary()
    if args.assert_expected:
        assert_expected_motif_family_counts(payload)
    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        search = payload["pre_vertex_circle_search"]
        families = payload["dihedral_incidence_families"]
        shapes = payload["loose_obstruction_shapes"]
        print("n=9 vertex-circle motif-family diagnostic")
        print(f"pre-vertex-circle full assignments: {search['full_assignments']}")
        print(f"dihedral incidence families: {families['family_count']}")
        print(f"orbit size counts: {families['orbit_size_counts']}")
        print(f"family status counts: {families['status_family_counts']}")
        print(
            "loose self-edge shape families: "
            f"{shapes['self_edge_shape_family_count']}"
        )
        print(
            "strict-cycle span shape families: "
            f"{shapes['strict_cycle_span_family_count']}"
        )
        if args.assert_expected:
            print("OK: motif-family counts verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
