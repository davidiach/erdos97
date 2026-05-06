#!/usr/bin/env python3
"""Validate or import the review-pending n=10 singleton-slice artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n10_vertex_circle_singletons import (  # noqa: E402
    artifact_payload,
    assert_expected_payload,
    assert_generic_spot_check,
    load_artifact,
    rows_from_archive_jsonl,
)
from erdos97.path_display import display_path  # noqa: E402

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n10_vertex_circle_singleton_slices.json"


def print_summary(payload: dict[str, object]) -> None:
    print("review-pending n=10 vertex-circle singleton-slice artifact")
    print(f"row0 choices covered: {payload['row0_choices_covered']}")
    print(f"total nodes: {payload['total_nodes']}")
    print(f"total full assignments: {payload['total_full']}")
    print(f"aborted any: {payload['aborted_any']}")
    print(f"counts: {payload['counts']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    parser.add_argument(
        "--import-jsonl",
        help="archive n10_rows.jsonl path to convert into the repo artifact",
    )
    parser.add_argument("--write", action="store_true", help="write imported artifact")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--spot-check-generic",
        action="store_true",
        help="rerun row0 singleton 0 with the repo-native generic checker",
    )
    parser.add_argument(
        "--spot-check-row0",
        action="append",
        type=int,
        default=[],
        metavar="INDEX",
        help="rerun this row0 singleton index with the repo-native generic checker",
    )
    args = parser.parse_args()

    artifact_path = Path(args.artifact)
    if args.import_jsonl:
        payload = artifact_payload(rows_from_archive_jsonl(Path(args.import_jsonl)))
        if args.write:
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
                newline="\n",
            )
    else:
        payload = load_artifact(artifact_path)

    if args.assert_expected:
        assert_expected_payload(payload)
    spot_check_indices = list(args.spot_check_row0)
    if args.spot_check_generic:
        spot_check_indices.insert(0, 0)
    for row0_index in dict.fromkeys(spot_check_indices):
        assert_generic_spot_check(payload, row0_index=row0_index)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.assert_expected:
            print("OK: n=10 singleton artifact expected counts verified")
        if args.spot_check_generic:
            print("OK: row0 singleton 0 matches the repo-native generic checker")
        for row0_index in dict.fromkeys(args.spot_check_row0):
            print(f"OK: row0 singleton {row0_index} matches the repo-native generic checker")
        if args.write:
            print(f"wrote {display_path(artifact_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
