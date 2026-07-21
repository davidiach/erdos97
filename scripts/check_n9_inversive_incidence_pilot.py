#!/usr/bin/env python3
"""Run the n=9 inversive point-line incidence pilot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.inversive_incidence import (
    assert_expected_counts,
    n9_inversive_incidence_summary,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_inversive_incidence_pilot.json"


def load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--check", action="store_true", help="check an existing artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument("--artifact", default=str(DEFAULT_OUT), help="path used by --check")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    if args.check:
        payload = load_json(Path(args.artifact))
        current = n9_inversive_incidence_summary()
        if payload != current:
            raise AssertionError("n=9 inversive incidence pilot artifact is not current")
        assert_expected_counts(payload)
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True))
        else:
            print("OK: n=9 inversive incidence pilot artifact verified")
        return 0

    payload = n9_inversive_incidence_summary()
    if args.assert_expected:
        assert_expected_counts(payload)

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        source = payload["source_frontier"]
        summary = payload["summary"]
        histograms = payload["histograms"]
        print("n=9 inversive point-line incidence pilot")
        print(f"source assignments: {source['assignment_count']}")
        print(f"total inversion pivots: {summary['total_pivots']}")
        print(f"total line seeds: {summary['total_line_seeds']}")
        print(f"compressed pivots: {summary['compressed_pivots']}")
        print(f"max closed line size: {summary['max_closed_line_size']}")
        print(
            "pivot max-line histogram: "
            f"{histograms['pivot_max_closed_line_size']}"
        )
        if args.assert_expected:
            print("OK: expected n=9 inversion-incidence counts verified")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
