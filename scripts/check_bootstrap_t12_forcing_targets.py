#!/usr/bin/env python3
"""Check the bootstrap/T12 forcing-target diagnostic artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.bootstrap_t12_forcing_targets import (
    DEFAULT_ARTIFACT,
    assert_expected_payload,
    build_t12_forcing_targets_payload,
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
    print("bootstrap / T12 forcing targets")
    print(f"targets: {summary['target_count']}")
    print(f"source record ids: {summary['source_record_ids']}")
    print(f"classification assignment ids: {summary['classification_assignment_ids']}")
    print(f"templates: {summary['template_counts']}")
    print(f"row gaps: {summary['row_gap_centers_by_source_id']}")
    print(f"private-pair hits: {summary['private_pair_hit_counts_by_source_id']}")
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
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned target counts")
    args = parser.parse_args()

    generated = build_t12_forcing_targets_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated T12 targets")
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
            print("OK: stored bootstrap/T12 forcing-target artifact matches regenerated payload")
        if args.assert_expected:
            print("OK: bootstrap/T12 forcing-target expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
