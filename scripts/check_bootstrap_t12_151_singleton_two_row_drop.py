#!/usr/bin/env python3
"""Check the bootstrap/T12 source-151 singleton two-row-drop audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.bootstrap_t12_151_singleton_two_row_drop import (  # noqa: E402
    DEFAULT_ARTIFACT,
    DEFAULT_SOURCE_ARTIFACT,
    assert_expected_payload,
    build_t12_151_singleton_two_row_drop_payload,
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
    print("bootstrap / T12 source-151 singleton two-row-drop audit")
    print(f"target rows: {summary['target_row_keys']}")
    print(f"two-row-drop candidates: {summary['two_row_drop_candidate_count']}")
    print(f"two-row-drop survivors: {summary['two_row_drop_surviving_candidate_count']}")
    print(
        "non-original survivors: "
        f"{summary['two_row_drop_non_original_survivor_count']}"
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
        "--source-artifact",
        type=Path,
        default=DEFAULT_SOURCE_ARTIFACT,
        help="source singleton-support audit packet",
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

    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact
    source_artifact = args.source_artifact
    if not source_artifact.is_absolute():
        source_artifact = ROOT / source_artifact

    generated = build_t12_151_singleton_two_row_drop_payload(source_artifact)
    payload = generated

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
            print("OK: stored source-151 singleton two-row artifact matches")
        if args.assert_expected:
            print("OK: source-151 singleton two-row expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
