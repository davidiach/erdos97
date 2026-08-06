#!/usr/bin/env python3
"""Generate or check the large-halo endpoint-reuse negative control."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_cycle_halo_endpoint_reuse import (
    assert_expected_payload,
    halo_endpoint_reuse_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "fragile_cycle_halo_endpoint_reuse.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def _section_summary(section: dict[str, Any]) -> dict[str, Any]:
    return {
        key: section[key]
        for key in (
            "halo_count",
            "placement_count",
            "essential_cover_count",
            "exclusive_trigger_cover_count",
            "pair_free_cover_count",
            "exclusive_pair_identity_histogram",
            "retained_vertex_circle_ok_count",
            "endpoint_reuse_survivor_count",
            "preferred_center_survivor_count",
            "alternate_center_survivor_count",
            "no_survivor_count",
            "chosen_center_histogram",
            "chosen_endpoint_count_histogram",
            "placement_trace_sha256",
        )
    }


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing result."""

    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "candidate_contract": payload["candidate_contract"],
        "four_halos": _section_summary(payload["four_halos"]),
        "five_halos": _section_summary(payload["five_halos"]),
        "summary": payload["summary"],
        "limitations": payload["limitations"],
        "conclusion": payload["conclusion"],
        "provenance": payload["provenance"],
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true", help="print full JSON")
    output.add_argument(
        "--summary-json", action="store_true", help="print compact JSON"
    )
    parser.add_argument("--write", action="store_true", help="write JSON artifact")
    parser.add_argument("--check", action="store_true", help="check stored artifact")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact_path = _resolve(args.artifact)
    out_path = _resolve(args.out)
    if args.write and args.check and artifact_path != out_path:
        raise SystemExit("--write --check requires --artifact and --out to match")
    start = perf_counter()
    generated = halo_endpoint_reuse_payload()
    if args.check:
        stored = _load_object(artifact_path)
        assert_expected_payload(stored)
        if stored != generated:
            raise SystemExit("stored payload differs from complete regeneration")
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
        print("exact fragile-cycle halo endpoint-reuse negative control")
        print(
            "four-halo endpoint-reuse survivors: "
            f"{payload['four_halos']['endpoint_reuse_survivor_count']}"
        )
        print(
            "five-halo endpoint-reuse survivors: "
            f"{payload['five_halos']['endpoint_reuse_survivor_count']}"
        )
        print(
            "alternate-center witnesses: "
            f"{payload['summary']['alternate_center_survivor_count']}"
        )
        print(f"elapsed_seconds: {elapsed:.6f}")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
