#!/usr/bin/env python3
"""Compare n=9 vertex-circle local cores with P18 and C19 frontier patterns."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

from erdos97.n9_vertex_circle_frontier_comparison import (
    assert_expected_frontier_comparison,
    frontier_comparison_summary,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_OUT = ROOT / "data" / "certificates" / "n9_vertex_circle_frontier_comparison.json"
DEFAULT_ARTIFACT = DEFAULT_OUT
SUMMARY_JSON_KEYS = (
    "type",
    "trust",
    "scope",
    "notes",
    "n9_local_core_artifact",
    "interpretation",
)
EXACT_CORE_EMBEDDING_SUMMARY_KEYS = (
    "pattern",
    "order",
    "exact_core_embedding_hits",
    "checked_core_count",
    "cyclic_order_preserving_maps_tested",
)
PATTERN_VERTEX_CIRCLE_SUMMARY_KEYS = (
    "pattern",
    "order",
    "obstructed",
    "status",
    "core_size",
    "vertex_support_size",
    "cycle_length",
    "span_signature",
    "matching_n9_strict_cycle_span_bucket_count",
)


def load_json(path: Path) -> object:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def artifact_check_errors(payload: object, artifact: Path) -> list[str]:
    try:
        checked = load_json(artifact)
    except OSError as exc:
        return [f"could not load {display_path(artifact, ROOT)}: {exc}"]
    except json.JSONDecodeError as exc:
        return [f"could not parse {display_path(artifact, ROOT)} as JSON: {exc}"]

    if checked != payload:
        return [
            f"generated payload differs from {display_path(artifact, ROOT)}",
        ]
    return []


def _summarize_records(
    records: object,
    keys: tuple[str, ...],
) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        return []
    return [
        {key: record[key] for key in keys if key in record}
        for record in records
        if isinstance(record, Mapping)
    ]


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without detailed records."""

    summary = {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}
    summary["exact_core_embedding_summary"] = _summarize_records(
        payload.get("exact_core_embedding_results"),
        EXACT_CORE_EMBEDDING_SUMMARY_KEYS,
    )
    summary["pattern_vertex_circle_summary"] = _summarize_records(
        payload.get("pattern_vertex_circle_results"),
        PATTERN_VERTEX_CIRCLE_SUMMARY_KEYS,
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print stable JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON without detailed records",
    )
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", default=str(DEFAULT_OUT), help="path used by --write")
    parser.add_argument(
        "--check",
        action="store_true",
        help="compare generated payload with --artifact",
    )
    parser.add_argument(
        "--artifact",
        default=str(DEFAULT_ARTIFACT),
        help="artifact path used by --check",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    payload = frontier_comparison_summary()
    if args.assert_expected:
        assert_expected_frontier_comparison(payload)
    check_errors: list[str] = []
    if args.check:
        artifact = Path(args.artifact)
        if not artifact.is_absolute():
            artifact = ROOT / artifact
        check_errors = artifact_check_errors(payload, artifact)
    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("n=9 vertex-circle frontier comparison")
        for result in payload["exact_core_embedding_results"]:
            print(
                f"{result['pattern']} exact n=9 core embeddings: "
                f"{result['exact_core_embedding_hits']}"
            )
        for result in payload["pattern_vertex_circle_results"]:
            print(f"{result['pattern']} vertex-circle status: {result['status']}")
        if args.assert_expected:
            print("OK: frontier comparison counts verified")
        if args.check and not check_errors:
            print(f"OK: artifact is current at {display_path(artifact, ROOT)}")
        if args.write:
            print(f"wrote {display_path(args.out, ROOT)}")
    if check_errors:
        print("FAILED: n=9 vertex-circle frontier comparison check failed", file=sys.stderr)
        for error in check_errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
