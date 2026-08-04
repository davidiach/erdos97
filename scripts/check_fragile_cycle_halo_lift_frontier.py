#!/usr/bin/env python3
"""Generate or check the exact fragile-cycle halo-lift frontier."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_cycle_halo_lift_frontier import (
    assert_expected_payload,
    halo_lift_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "fragile_cycle_halo_lift_frontier.json"
)
DEFAULT_FRONTIER = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
DEFAULT_DUALS = ROOT / "data" / "certificates" / "n9_vertex_circle_template_duals.json"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing frontier summary."""

    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "source_template": payload["source_template"],
        "zero_halos": {
            key: payload["zero_halos"][key]
            for key in (
                "raw_row_combination_count",
                "pair_and_crossing_compatible_count",
                "essential_cover_count",
            )
        },
        "one_halo": {
            key: payload["one_halo"][key]
            for key in (
                "placement_count",
                "raw_row_combination_count",
                "essential_cover_count",
                "extendable_partial_cover_count",
                "initially_dead_partial_cover_count",
            )
        },
        "two_halos": {
            key: payload["two_halos"][key]
            for key in (
                "placement_count",
                "raw_row_combination_count",
                "essential_cover_count",
                "extendable_partial_cover_count",
                "canonical_full_system_count",
                "assignment_ids",
                "template_id_counts",
                "frontier_status_counts",
                "all_positive_circuit_identities_zero",
            )
        },
        "summary": payload["summary"],
        "limitations": payload["limitations"],
        "conclusion": payload["conclusion"],
        "source_artifacts": payload["source_artifacts"],
        "provenance": payload["provenance"],
    }


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    print("exact fragile-cycle halo-lift frontier")
    print(
        "minimum halos for fragile cover: "
        f"{payload['summary']['minimum_added_halos_for_fragile_cover']}"
    )
    print(
        "minimum halos for full selected extension: "
        f"{payload['summary']['minimum_added_halos_for_full_selected_extension']}"
    )
    print(f"one-halo covers: {payload['one_halo']['essential_cover_count']}")
    print(f"two-halo covers: {payload['two_halos']['essential_cover_count']}")
    print(
        "two-halo extendable covers: "
        f"{payload['two_halos']['extendable_partial_cover_count']}"
    )
    print(f"n=9 assignments: {payload['two_halos']['assignment_ids']}")
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact frontier JSON",
    )
    parser.add_argument(
        "--write", action="store_true", help="write stable JSON artifact"
    )
    parser.add_argument("--check", action="store_true", help="check a stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--frontier", type=Path, default=DEFAULT_FRONTIER)
    parser.add_argument("--duals", type=Path, default=DEFAULT_DUALS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")

    frontier = _load_object(_resolve(args.frontier))
    duals = _load_object(_resolve(args.duals))
    start = perf_counter()
    generated = halo_lift_payload(frontier, duals)
    if args.check:
        stored = _load_object(artifact_path)
        try:
            assert_expected_payload(stored)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        if stored != generated:
            raise SystemExit(
                "stored payload differs from complete regenerated halo-lift frontier"
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
            print("OK: fragile-cycle halo-lift frontier matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
