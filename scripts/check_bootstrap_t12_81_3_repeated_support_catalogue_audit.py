#!/usr/bin/env python3
"""Check the bootstrap/T12 81:3 repeated-support catalogue audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.bootstrap_t12_81_3_repeated_support_catalogue_audit import (  # noqa: E402
    DEFAULT_ARTIFACT,
    assert_expected_payload,
    build_t12_81_3_repeated_support_catalogue_audit_payload,
    load_artifact,
)


SUMMARY_KEYS = (
    "schema",
    "status",
    "trust",
    "claim_scope",
    "interpretation_warnings",
    "source_chain_closure_csp",
    "summary",
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
    print("bootstrap / T12 81:3 repeated-support catalogue audit")
    print(f"repeated-support candidates: {summary['repeated_support_candidate_count']}")
    print(f"supply-extension candidates: {summary['supply_extension_candidate_count']}")
    print(
        "initially compatible supply catalogues: "
        f"{summary['supply_extension_initially_compatible_count']}"
    )
    print(f"supply-extension survivors: {summary['supply_extension_survivor_count']}")
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
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print JSON payload")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON summary",
    )
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned values")
    args = parser.parse_args()

    generated = build_t12_81_3_repeated_support_catalogue_audit_payload()
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

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_summary(payload)
        if args.check:
            print("OK: stored bootstrap/T12 81:3 repeated-support artifact matches")
        if args.assert_expected:
            print("OK: bootstrap/T12 81:3 repeated-support expectations verified")
    return 0


def summary_json_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return the compact reviewer-facing JSON view."""

    return {key: payload[key] for key in SUMMARY_KEYS}


if __name__ == "__main__":
    raise SystemExit(main())
