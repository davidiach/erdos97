#!/usr/bin/env python3
"""Generate or check the alternate-vertex perimeter relaxation guardrail."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter
from typing import Any

from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path
from erdos97.perimeter_relaxation_guardrail import (
    assert_expected_payload,
    control_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "runs"
    / "2026-09-04"
    / "perimeter_relaxation_guardrail.json"
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
    rich = compact.get("rich_classes")
    if isinstance(rich, dict):
        compact["rich_classes"] = {
            key: value for key, value in rich.items() if key != "records"
        }
    obstruction = compact.get("unshifted_euclidean_obstruction")
    if isinstance(obstruction, dict):
        compact["unshifted_euclidean_obstruction"] = {
            key: value for key, value in obstruction.items() if key != "coefficients"
        }
    return compact


def _print_summary(payload: dict[str, Any], elapsed: float) -> None:
    print("alternate-vertex perimeter relaxation guardrail")
    print(f"n: {payload['n']}")
    print(
        "rich radii: "
        f"even={payload['rich_classes']['even_radius']}, "
        f"odd={payload['rich_classes']['odd_radius']}"
    )
    print(
        "strict triangle minimum slack: "
        f"{payload['strict_triangle_replay']['minimum_slack']}"
    )
    print(
        "strict Kalmanson minimum slack: "
        f"{payload['strict_kalmanson_replay']['minimum_slack']}"
    )
    print(
        "weak-turn minimum slack: "
        f"{payload['weak_turn_replay']['minimum_slack']}"
    )
    print(
        "unshifted negative-type violation: "
        f"{payload['unshifted_euclidean_obstruction']['squared_distance_energy']}"
    )
    print(
        "shifted Euclidean strict gap: "
        f"{payload['shifted_high_dimensional_euclidean_lift']['strict_conditional_negative_type_gap']}"
    )
    print(f"elapsed_seconds: {elapsed:.6f}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print full JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print JSON without full row and coefficient records",
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
    payload = _load_object(artifact_path) if args.check else control_payload()
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
            print("OK: perimeter relaxation guardrail matches expected data")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
