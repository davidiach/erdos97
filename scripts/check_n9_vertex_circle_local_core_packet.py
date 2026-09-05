#!/usr/bin/env python3
"""Generate or check the compact n=9 vertex-circle local-core packet."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from erdos97.json_io import write_json
from erdos97.n9_vertex_circle_obstruction_shapes import (
    local_core_packet_summary, assert_expected_local_core_packet_counts,
)
from erdos97.path_display import display_path
# Re-export the historical script API while reusable validation lives in src/.
from erdos97.finite_cases.n9.local_core_packet import (  # noqa: F401
    ROOT, DEFAULT_ARTIFACT, EXPECTED_TOP_LEVEL_KEYS, load_artifact,
    expect_equal, validate_payload, summary_payload,
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated packet")
    parser.add_argument("--check", action="store_true", help="validate an existing packet")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    out = args.out if args.out.is_absolute() else ROOT / args.out

    if args.write:
        payload = local_core_packet_summary()
        if args.assert_expected:
            assert_expected_local_core_packet_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload, recompute=args.check or args.assert_expected)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 vertex-circle compact local-core packet")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"orbit-size sum: {summary['orbit_size_sum']}")
        print(f"core size counts: {summary['core_size_counts']}")
        if args.check or args.assert_expected:
            print("OK: compact local-core packet checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
