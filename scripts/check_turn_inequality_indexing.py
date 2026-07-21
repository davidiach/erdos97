#!/usr/bin/env python3
"""Check the n=9 turn-inequality indexing convention."""

from __future__ import annotations

import argparse
import json

from erdos97.turn_inequality_indexing import (
    assert_expected_payload,
    audit_turn_inequality_indexing,
    summary_payload,
)

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON",
    )
    parser.add_argument("--check", action="store_true", help="validate generated audit data")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = audit_turn_inequality_indexing()
    if args.check and payload["validation_status"] != "passed":
        raise SystemExit("; ".join(str(error) for error in payload["validation_errors"][:5]))
    if args.assert_expected:
        assert_expected_payload(payload)

    if args.summary_json:
        print(json.dumps(summary_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("review-pending n=9 turn-inequality indexing audit")
        print(f"row offset subsets: {payload['row_offset_subset_count']}")
        print(f"row instances: {payload['row_instance_count']}")
        print(f"terms: {payload['observed_term_count']}")
        print(f"orientation counts: {payload['orientation_counts']}")
        print(f"support size histogram: {payload['support_size_histogram']}")
        print(f"mismatches: {payload['mismatch_count']}")
        print(f"validation_status: {payload['validation_status']}")
        if args.assert_expected:
            print("OK: turn-inequality indexing audit matches expected data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
