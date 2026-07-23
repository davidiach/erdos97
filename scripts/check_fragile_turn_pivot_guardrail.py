#!/usr/bin/env python3
"""Generate or check the exact fragile/turn/pivot bridge guardrail."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.fragile_turn_pivot_guardrail import (
    assert_expected_payload,
    guardrail_payload,
    validate_payload,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "fragile_turn_pivot_guardrail.json"
)


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact reviewer-facing payload."""

    compact = dict(payload)
    compact.pop("selected_rows", None)
    fragile = compact.get("fragile_hypergraph")
    if isinstance(fragile, dict):
        compact["fragile_hypergraph"] = {
            key: fragile[key]
            for key in (
                "n",
                "fragile_centers",
                "ok",
                "cover_ok",
                "self_exclusion_ok",
                "uniformity_ok",
                "pairwise_intersection_ok",
                "crossing_ok",
                "essential_cover_ok",
                "witness_map_ok",
            )
        }
    matching = compact.get("essential_matching")
    if isinstance(matching, dict):
        compact["essential_matching"] = {
            key: value for key, value in matching.items() if key != "halos"
        }
    return compact


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    print("exact fragile/turn/pivot bridge guardrail")
    print(f"n: {payload['n']}")
    print(f"offsets: {payload['circulant_offsets']}")
    print(f"fragile hypergraph: {payload['fragile_hypergraph']['ok']}")
    print(
        "good-deletion seeds: "
        f"{payload['good_deletion']['nonempty_proper_seed_count']}"
    )
    print(f"matching cycles: {payload['essential_matching']['cycles']}")
    print(
        "weak turns strictly feasible: "
        f"{payload['weak_turn_replay']['all_weak_terms_strictly_satisfied']}"
    )
    print(f"vertex-circle status: {payload['vertex_circle_replay']['status']}")
    print(
        "Kalmanson inverse zero sum: "
        f"{payload['kalmanson_inverse']['zero_sum_verified']}"
    )
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print JSON without full rows and halo records",
    )
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--check", action="store_true", help="check a stored artifact")
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
    payload = _load_object(artifact_path) if args.check else guardrail_payload()
    errors = validate_payload(payload) if args.check else []
    if errors:
        raise SystemExit("; ".join(errors[:5]))
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
            print("OK: fragile/turn/pivot bridge guardrail matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
