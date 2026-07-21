#!/usr/bin/env python3
"""Check the bootstrap/T12 151 singleton full-neighborhood packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.bootstrap_t12_151_singleton_full_neighborhood_vertex_circle import (
    DEFAULT_ARTIFACT,
    assert_expected_payload,
    build_t12_151_singleton_full_neighborhood_vertex_circle_payload,
    load_artifact,
)

ROOT = Path(__file__).resolve().parents[1]

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
    print("bootstrap / T12 151 singleton full-neighborhood vertex-circle packet")
    print(f"target row keys: {', '.join(summary['target_row_keys'])}")
    print(
        "basic-filter complete assignments: "
        f"{summary['basic_filter_complete_assignment_count']}"
    )
    print(
        "non-original target-row basic survivors: "
        f"{summary['basic_filter_non_original_target_assignment_count']}"
    )
    print(
        "vertex-circle survivors: "
        f"{summary['vertex_circle_surviving_assignment_count']}"
    )
    print(f"scan status: {summary['scan_status']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact",
        type=Path,
        default=DEFAULT_ARTIFACT,
        help="artifact path to check or write",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare artifact to regenerated payload",
    )
    parser.add_argument("--write", action="store_true", help="write regenerated payload")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned values")
    args = parser.parse_args()

    generated = build_t12_151_singleton_full_neighborhood_vertex_circle_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated packet")
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
            print("OK: stored bootstrap/T12 151 full-neighborhood artifact matches")
        if args.assert_expected:
            print("OK: bootstrap/T12 151 full-neighborhood expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
