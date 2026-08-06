#!/usr/bin/env python3
"""Generate or check the exact three-halo hinge/splice motif crosswalk."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_cycle_three_halo_motif_crosswalk import (
    assert_expected_payload,
    motif_crosswalk_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_motif_crosswalk.json"
)
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_three_halo_kalmanson_endgame.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "source_artifact": payload["source_artifact"],
        "splice_template_replays": payload["splice_template_replays"],
        "motif_class_counts": payload["motif_class_counts"],
        "reciprocal_selected_center_pair_count_histogram": payload[
            "reciprocal_selected_center_pair_count_histogram"
        ],
        "motif_crosswalk_catalog_sha256": payload[
            "motif_crosswalk_catalog_sha256"
        ],
        "summary": payload["summary"],
        "limitations": payload["limitations"],
        "conclusion": payload["conclusion"],
        "provenance": payload["provenance"],
    }


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    summary = payload["summary"]
    print("exact fragile-cycle three-halo hinge/splice motif crosswalk")
    print(f"source states: {summary['source_states_checked']}")
    print(f"hinge states: {summary['equilateral_hinge_states']}")
    print(f"five-role splices: {summary['five_role_splice_states']}")
    print(f"six-role splices: {summary['six_role_splice_states']}")
    print(f"motif classes: {summary['distinct_local_motif_classes']}")
    print(f"catalog digest: {payload['motif_crosswalk_catalog_sha256']}")
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json", action="store_true", help="print compact packet JSON"
    )
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
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
    generated = motif_crosswalk_payload(source)
    if args.check:
        stored = _load_object(artifact_path)
        try:
            assert_expected_payload(stored)
        except (AssertionError, KeyError, TypeError, ValueError) as exc:
            raise SystemExit(str(exc)) from exc
        if stored != generated:
            raise SystemExit("stored payload differs from regenerated motif crosswalk")
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
            print("OK: hinge/splice motif crosswalk matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
