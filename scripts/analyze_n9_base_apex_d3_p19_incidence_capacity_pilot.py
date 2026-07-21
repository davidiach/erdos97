#!/usr/bin/env python3
"""Generate the n=9 D=3 P19 incidence-capacity pilot ledger."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Sequence

from erdos97.json_io import load_json, write_json
from erdos97.n9_base_apex_d3_p19_incidence_capacity_pilot import (
    assert_expected_pilot_counts,
    p19_incidence_capacity_pilot_report,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_base_apex_d3_p19_incidence_capacity_pilot.json"
)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print generated JSON")
    parser.add_argument("--out", type=Path, help="write generated JSON to this path")
    parser.add_argument(
        "--check-artifact",
        type=Path,
        help="compare generated JSON with an existing artifact",
    )
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    checked = None
    artifact = None
    if args.check_artifact is not None:
        artifact = (
            args.check_artifact
            if args.check_artifact.is_absolute()
            else ROOT / args.check_artifact
        )
        try:
            checked = load_json(artifact)
        except OSError as exc:
            print(
                "FAILED: could not load "
                f"{display_path(artifact, ROOT)}: {exc}",
                file=sys.stderr,
            )
            return 1
        except json.JSONDecodeError as exc:
            print(
                "FAILED: could not parse "
                f"{display_path(artifact, ROOT)} as JSON: {exc}",
                file=sys.stderr,
            )
            return 1

    payload = p19_incidence_capacity_pilot_report()
    if args.assert_expected:
        assert_expected_pilot_counts(payload)

    if checked is not None:
        if checked != payload:
            print(
                f"FAILED: generated payload differs from {display_path(artifact, ROOT)}",
                file=sys.stderr,
            )
            return 1

    if args.out is not None:
        out = args.out if args.out.is_absolute() else ROOT / args.out
        write_json(payload, out)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.check_artifact is not None:
        print("OK: n=9 D=3 P19 incidence-capacity pilot artifact is current")
    elif args.out is not None:
        print(f"wrote {display_path(out, ROOT)}")
    else:
        print("n=9 base-apex D=3 P19 incidence-capacity pilot ledger")
        print(
            "rows: "
            f"profile={payload['profile_ledger_id']}, "
            f"representatives={payload['representative_count']}, "
            f"common-dihedral classes="
            f"{payload['common_dihedral_pair_class_count']}"
        )
        print(
            "states: "
            f"realizability={payload['realizability_state']}, "
            f"incidence={payload['incidence_state']}, "
            f"scope={payload['state_scope']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
