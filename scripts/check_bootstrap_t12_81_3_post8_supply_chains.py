#!/usr/bin/env python3
"""Check the bootstrap/T12 81:3 post-center-8 supply-chain CSP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Mapping

from erdos97.bootstrap_t12_81_3_post8_supply_chains import (
    DEFAULT_ARTIFACT,
    assert_expected_payload,
    build_t12_81_3_post8_supply_chains_payload,
    load_artifact,
)

ROOT = Path(__file__).resolve().parents[1]

def write_artifact(path: Path, payload: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def print_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    if not isinstance(summary, Mapping):
        raise AssertionError("summary must be a mapping")
    print("bootstrap / T12 81:3 post-center-8 supply-chain CSP")
    print(
        "support-catalogue candidates: "
        f"{summary['total_support_catalogue_candidate_count']}"
    )
    print(
        "initially compatible catalogues: "
        f"{summary['total_initially_compatible_support_catalogue_count']}"
    )
    print(
        "selected search nodes: "
        f"{summary['total_selected_search_node_count']}"
    )
    print(
        "selected-row survivors: "
        f"{summary['total_selected_detected_solution_count']}"
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
    parser.add_argument(
        "--write",
        action="store_true",
        help="write regenerated payload",
    )
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="assert pinned values",
    )
    args = parser.parse_args()

    generated = build_t12_81_3_post8_supply_chains_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(
                f"{artifact} is stale relative to regenerated post8 packet"
            )
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
            print("OK: stored bootstrap/T12 81:3 post8 artifact matches")
        if args.assert_expected:
            print("OK: bootstrap/T12 81:3 post8 expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
