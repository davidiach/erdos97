#!/usr/bin/env python3
"""Check the bootstrap/T12 closure-exposed row packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.bootstrap_t12_closure_exposed import (  # noqa: E402
    DEFAULT_ARTIFACT,
    assert_expected_payload,
    build_t12_closure_exposed_payload,
    load_artifact,
)


def write_artifact(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def print_summary(payload: dict[str, object]) -> None:
    summary = payload["summary"]
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    print("bootstrap / T12 closure-exposed rows")
    print(f"records: {summary['closure_exposed_row_record_count']}")
    print(f"row centers: {summary['row_centers_by_source_id']}")
    print(f"exposure modes: {summary['exposure_mode_counts']}")
    print(f"full-row contained: {summary['full_row_contained_rows_by_source_id']}")
    print(f"core-witness only: {summary['core_witness_only_rows_by_source_id']}")
    print(f"target status: {summary['forcing_target_status']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="artifact path to check or write",
    )
    parser.add_argument("--check", action="store_true", help="compare artifact to regenerated payload")
    parser.add_argument("--write", action="store_true", help="write regenerated payload")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned closure-exposed counts")
    args = parser.parse_args()

    generated = build_t12_closure_exposed_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated closure-exposed packet")
        payload = stored

    if args.assert_expected:
        assert_expected_payload(payload)

    if args.write:
        write_artifact(artifact, generated)

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.check:
            print("OK: stored bootstrap/T12 closure-exposed artifact matches regenerated payload")
        if args.assert_expected:
            print("OK: bootstrap/T12 closure-exposed expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
