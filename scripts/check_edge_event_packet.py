#!/usr/bin/env python3
"""Extract an exact edge-event / Gram packet from coordinate JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.edge_event_packet import edge_event_report

def _parse_selected_rows(raw: object) -> dict[int, list[int]]:
    if raw is None:
        return {}
    if isinstance(raw, dict):
        return {int(center): [int(v) for v in row] for center, row in raw.items()}
    if isinstance(raw, list):
        return {
            int(item["center"]): [int(v) for v in item["witnesses"]]
            for item in raw
        }
    raise ValueError("selected_rows must be a dict or a list of row records")


def print_summary(report: dict[str, object]) -> None:
    checks = report["identity_checks"]
    print("edge-event / Gram packet")
    print(f"n: {report['n']}")
    print(f"row-difference identity: {checks['row_difference_identity_verified']}")
    print(f"Gram closure: {checks['gram_closure_verified']}")
    print(f"column line-cut checks: {checks['column_line_cut_checks_verified']}")
    print(f"selected interval packets: {checks['selected_interval_packets_verified']}")
    print(f"interval packet count: {len(report['selected_interval_packets'])}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        help=(
            "JSON file with coordinates or vertices, and optional selected_rows. "
            "Coordinates may be ints or rational strings."
        ),
    )
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--write-certificate", help="write JSON report to this path")
    parser.add_argument(
        "--assert-verified",
        action="store_true",
        help="assert all reported identity checks are true",
    )
    args = parser.parse_args()

    payload = json.loads(Path(args.input).read_text(encoding="utf-8-sig"))
    coordinates = payload.get("coordinates", payload.get("vertices"))
    if coordinates is None:
        raise SystemExit("input JSON must contain coordinates or vertices")
    selected_rows = _parse_selected_rows(payload.get("selected_rows"))
    report = edge_event_report(coordinates, selected_rows)

    if args.assert_verified:
        checks = report["identity_checks"]
        failed = [name for name, value in checks.items() if value is not True]
        if failed:
            raise AssertionError(f"expected all identity checks true; failed={failed}")

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_summary(report)
        if args.assert_verified:
            print("OK: edge-event packet verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
