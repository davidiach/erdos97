#!/usr/bin/env python3
"""Validate joins across n=9 base-apex D=3 bookkeeping artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_base_apex_d3_artifact_join import (  # noqa: E402
    DEFAULT_ARTIFACT_PATHS,
    EXPECTED_CLAIM_SCOPE,
    load_artifacts,
    resolve_artifact_paths,
    summary_payload,
    validate_artifact_stack,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--d3-escape-slice",
        type=Path,
        default=DEFAULT_ARTIFACT_PATHS["d3_escape_slice"],
        help="Path to n9_base_apex_d3_escape_slice.json.",
    )
    parser.add_argument(
        "--d3-packet",
        type=Path,
        default=DEFAULT_ARTIFACT_PATHS["d3_escape_frontier_packet"],
        help="Path to n9_base_apex_d3_escape_frontier_packet.json.",
    )
    parser.add_argument(
        "--crosswalk",
        type=Path,
        default=DEFAULT_ARTIFACT_PATHS["low_excess_escape_crosswalk"],
        help="Path to n9_base_apex_low_excess_escape_crosswalk.json.",
    )
    parser.add_argument(
        "--p19-pilot",
        type=Path,
        default=DEFAULT_ARTIFACT_PATHS["d3_p19_incidence_capacity_pilot"],
        help="Path to n9_base_apex_d3_p19_incidence_capacity_pilot.json.",
    )
    parser.add_argument(
        "--full-packet",
        type=Path,
        default=DEFAULT_ARTIFACT_PATHS["d3_incidence_capacity_packet"],
        help="Path to n9_base_apex_d3_incidence_capacity_packet.json.",
    )
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    paths = resolve_artifact_paths(
        ROOT,
        {
            "d3_escape_slice": args.d3_escape_slice,
            "d3_escape_frontier_packet": args.d3_packet,
            "low_excess_escape_crosswalk": args.crosswalk,
            "d3_p19_incidence_capacity_pilot": args.p19_pilot,
            "d3_incidence_capacity_packet": args.full_packet,
        },
    )
    artifacts, errors = load_artifacts(paths)
    if not errors:
        errors = validate_artifact_stack(artifacts)

    summary = summary_payload(ROOT, paths, artifacts, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print("FAILED: n=9 base-apex D=3 artifact joins", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 base-apex D=3 artifact join checker")
        print(f"scope: {EXPECTED_CLAIM_SCOPE}")
        print(
            "rows: "
            f"packet={summary['d3_packet_representative_count']}, "
            f"crosswalk={summary['d3_crosswalk_row_count']}, "
            f"full={summary['full_packet_row_count']}, "
            f"p19={summary['p19_pilot_row_count']}"
        )
        print(
            "D=3 common-dihedral classes: "
            f"{summary['d3_crosswalk_common_dihedral_pair_class_count']}"
        )
        if args.check:
            print("OK: cross-artifact D=3 bookkeeping joins passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
