#!/usr/bin/env python3
"""Generate the n=9 D=3 escape-frontier representative packet."""

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

from erdos97.n9_base_apex_d3_escape_frontier_packet import (  # noqa: E402
    assert_expected_packet_counts,
    d3_escape_frontier_packet_report,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_OUT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_base_apex_d3_escape_frontier_packet.json"
)


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def load_json(path: Path) -> object:
    """Load JSON from a path."""

    return json.loads(path.read_text(encoding="utf-8"))


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
    payload = d3_escape_frontier_packet_report()
    if args.assert_expected:
        assert_expected_packet_counts(payload)

    if args.check_artifact is not None:
        artifact = (
            args.check_artifact
            if args.check_artifact.is_absolute()
            else ROOT / args.check_artifact
        )
        checked = load_json(artifact)
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
        print("OK: n=9 D=3 escape-frontier packet artifact is current")
    elif args.out is not None:
        print(f"wrote {display_path(out, ROOT)}")
    else:
        print("n=9 base-apex D=3 escape-frontier representative packet")
        print(
            "representatives: "
            f"profiles={payload['profile_multiset_count']}, "
            f"escapes={payload['escape_class_count']}, "
            f"rows={payload['representative_count']}"
        )
        print(
            "counts: "
            f"labelled profiles={payload['labelled_profile_sequence_count']}, "
            f"labelled escapes={payload['labelled_escape_placement_count']}, "
            f"common-dihedral classes="
            f"{payload['common_dihedral_pair_class_count']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
