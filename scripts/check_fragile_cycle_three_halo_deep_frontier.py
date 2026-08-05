#!/usr/bin/env python3
"""Generate or check the exact three-halo deep-frontier packet."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_cycle_three_halo_deep_frontier import (
    assert_expected_payload,
    deep_frontier_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_deep_frontier.json"
)
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_vertex_circle.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing deep-frontier summary."""

    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "source_artifact": payload["source_artifact"],
        "depth_status_profile": payload["depth_status_profile"],
        "deep_placements": payload["deep_placements"],
        "minimum_obstruction_core_status_counts": payload[
            "minimum_obstruction_core_status_counts"
        ],
        "incidence_rejection_totals": payload["incidence_rejection_totals"],
        "deep_frontier_catalog_sha256": payload[
            "deep_frontier_catalog_sha256"
        ],
        "summary": payload["summary"],
        "limitations": payload["limitations"],
        "conclusion": payload["conclusion"],
        "provenance": payload["provenance"],
    }


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    summary = payload["summary"]
    print("exact fragile-cycle three-halo deep frontier")
    print(f"clean eight-row states: {summary['clean_eight_row_state_count']}")
    print(f"deep placements: {summary['clean_eight_row_placement_count']}")
    print(f"incidence-dead states: {summary['incidence_dead_state_count']}")
    print(f"forced ninth-row states: {summary['forced_ninth_row_state_count']}")
    print(
        "forced obstruction width: "
        f"{summary['minimum_forced_obstruction_core_width']}"
    )
    print(f"catalog trace: {payload['deep_frontier_catalog_sha256']}")
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact packet JSON",
    )
    parser.add_argument(
        "--write", action="store_true", help="write stable JSON artifact"
    )
    parser.add_argument("--check", action="store_true", help="check stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")

    source = _load_object(_resolve(args.source))
    start = perf_counter()
    generated = deep_frontier_payload(source)
    if args.check:
        stored = _load_object(artifact_path)
        try:
            assert_expected_payload(stored)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        if stored != generated:
            raise SystemExit(
                "stored payload differs from regenerated three-halo deep frontier"
            )
        payload = stored
    else:
        payload = generated
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.write:
        write_json(payload, out_path)
    elapsed = perf_counter() - start

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_summary(payload, elapsed)
        if args.assert_expected:
            print("OK: three-halo deep frontier matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
