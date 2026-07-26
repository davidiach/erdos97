#!/usr/bin/env python3
"""Generate or check the review-pending n=9 fragile/turn/pivot crosswalk."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.json_io import load_json, write_json
from erdos97.n9_fragile_turn_pivot_crosswalk import (
    assert_expected_payload,
    crosswalk_payload,
    validate_payload,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "n9_fragile_turn_pivot_crosswalk.json"
)
DEFAULT_TURN_SOURCE = (
    ROOT / "data" / "certificates" / "n9_turn_inequality_frontier.json"
)
DEFAULT_MOTIF_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def _generate(turn_path: Path, motif_path: Path) -> dict[str, Any]:
    return crosswalk_payload(
        _load_object(turn_path),
        _load_object(motif_path),
        turn_source_file_sha256=_file_sha256(turn_path),
        motif_source_file_sha256=_file_sha256(motif_path),
    )


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a reviewer-facing summary without per-assignment records."""

    compact: dict[str, Any] = {}
    for key in (
        "schema",
        "status",
        "trust",
        "claim_scope",
        "n",
        "row_size",
        "cyclic_order",
        "source_artifacts",
        "regular_incidence",
        "witness_pivot_matching",
        "pivot_halo_turn_certificates",
        "inversion_row_pivot_covers",
        "three_pivot_exception",
        "limitations",
        "conclusion",
        "review_requirements",
        "provenance",
    ):
        value = payload.get(key)
        if isinstance(value, dict) and "records" in value:
            value = {
                field: field_value
                for field, field_value in value.items()
                if field != "records"
            }
        compact[key] = value
    return compact


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    matching = payload["witness_pivot_matching"]
    pivot_halo = payload["pivot_halo_turn_certificates"]
    inversion = payload["inversion_row_pivot_covers"]
    exception = payload["three_pivot_exception"]

    print("review-pending n=9 fragile/turn/pivot crosswalk")
    print(f"assignments: {payload['regular_incidence']['assignment_count']}")
    print(f"perfect matchings: {matching['perfect_matching_count']}")
    print(f"Hamiltonian matchings: {matching['hamiltonian_matching_count']}")
    print(f"pivot-to-halo lambda counts: {pivot_halo['lambda_histogram']}")
    print(f"inversion cover sizes: {inversion['minimum_cover_size_histogram']}")
    print(
        "three-pivot exception: "
        f"assignments={inversion['three_pivot_assignment_ids']}, "
        f"families={exception['family_ids']}, "
        f"two-pivot feasible={exception['two_pivot_binary_feasible_count']}, "
        f"vertex-circle={exception['vertex_circle_status_counts']}"
    )
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print JSON without per-assignment records",
    )
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--check", action="store_true", help="check a stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--turn-source", type=Path, default=DEFAULT_TURN_SOURCE)
    parser.add_argument("--motif-source", type=Path, default=DEFAULT_MOTIF_SOURCE)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    turn_path = _resolve(args.turn_source)
    motif_path = _resolve(args.motif_source)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")

    start = perf_counter()
    turn_payload = _load_object(turn_path)
    motif_payload = _load_object(motif_path)
    if args.check:
        payload = _load_object(artifact_path)
        errors = validate_payload(
            payload,
            turn_payload,
            motif_payload,
            turn_source_file_sha256=_file_sha256(turn_path),
            motif_source_file_sha256=_file_sha256(motif_path),
        )
        if errors:
            raise SystemExit("; ".join(errors[:5]))
    else:
        payload = crosswalk_payload(
            turn_payload,
            motif_payload,
            turn_source_file_sha256=_file_sha256(turn_path),
            motif_source_file_sha256=_file_sha256(motif_path),
        )

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
            print("OK: n=9 fragile/turn/pivot crosswalk matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
