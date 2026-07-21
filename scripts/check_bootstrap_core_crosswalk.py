#!/usr/bin/env python3
"""Check the bootstrap-core frontier crosswalk artifact."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.bootstrap_core_crosswalk import (
    assert_expected_payload,
    build_crosswalk_payload,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "bootstrap_core_crosswalk.json"


def load_artifact(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("bootstrap-core crosswalk artifact must be a JSON object")
    return payload


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
    base_apex = payload["base_apex_d3_reference"]
    if not isinstance(base_apex, dict):
        raise AssertionError("base-apex reference must be a mapping")
    print("bootstrap-core crosswalk")
    print(f"order cases: {summary['order_case_count']}")
    print(f"rank > 3 cases: {summary['rank_gt_3_order_cases']}")
    print(f"minimum-rank counts: {summary['minimum_rank_counts']}")
    print(
        "weighted-capacity survivors: "
        f"{summary['weighted_capacity_survivor_count']}; "
        "obstructions: "
        f"{summary['weighted_capacity_obstruction_count']}"
    )
    print(
        "base-apex D=3 reference rows: "
        f"{base_apex['representative_count']} "
        f"({base_apex['reason_not_audited']})"
    )


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
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned crosswalk counts")
    args = parser.parse_args()

    generated = build_crosswalk_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated crosswalk")
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
            print("OK: stored bootstrap-core crosswalk matches regenerated payload")
        if args.assert_expected:
            print("OK: bootstrap-core crosswalk expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
