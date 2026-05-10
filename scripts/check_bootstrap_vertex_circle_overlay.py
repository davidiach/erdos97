#!/usr/bin/env python3
"""Check the bootstrap-core / vertex-circle overlay artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.bootstrap_vertex_circle_overlay import (  # noqa: E402
    assert_expected_payload,
    build_overlay_payload,
)


DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "bootstrap_vertex_circle_overlay.json"


def load_artifact(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("bootstrap/vertex-circle overlay artifact must be a JSON object")
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
    print("bootstrap / vertex-circle overlay")
    print(f"targets: {summary['target_count']}")
    print(f"source assignment indices: {summary['source_assignment_indices']}")
    print(f"classification assignment ids: {summary['classification_assignment_ids']}")
    print(f"templates: {summary['template_counts']}")
    print(f"cycle lengths: {summary['cycle_length_counts']}")
    print(f"capacity margins: {summary['capacity_margins_by_source_id']}")
    print(f"conclusion: {summary['overlay_conclusion']}")


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
    parser.add_argument("--assert-expected", action="store_true", help="assert pinned overlay counts")
    args = parser.parse_args()

    generated = build_overlay_payload()
    payload = generated
    artifact = args.artifact
    if not artifact.is_absolute():
        artifact = ROOT / artifact

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{artifact} is stale relative to regenerated overlay")
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
            print("OK: stored bootstrap/vertex-circle overlay matches regenerated payload")
        if args.assert_expected:
            print("OK: bootstrap/vertex-circle overlay expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
