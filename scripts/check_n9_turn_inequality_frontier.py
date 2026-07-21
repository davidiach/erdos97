#!/usr/bin/env python3
"""Generate or check the review-pending n=9 turn-inequality frontier replay."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from time import perf_counter

from erdos97.n9_turn_inequality_frontier import (
    assert_expected_payload,
    summary_payload,
    validate_payload,
)
from erdos97.path_display import display_path

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_turn_inequality_frontier.json"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_json(path: Path) -> dict[str, object]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def _print_summary(payload: dict[str, object], elapsed: float | None = None) -> None:
    source = payload["source_frontier"]
    turn_system = payload["turn_system"]
    z3_replay = payload["z3_replay"]
    farkas_replay = payload["farkas_replay"]
    benchmark = payload["benchmarks"][0]
    assert isinstance(source, dict)
    assert isinstance(turn_system, dict)
    assert isinstance(z3_replay, dict)
    assert isinstance(farkas_replay, dict)
    assert isinstance(benchmark, dict)

    print("review-pending n=9 turn-inequality frontier replay")
    print(f"assignments: {source['assignment_count']}")
    print(f"frontier_sha256: {source['assignment_sha256']}")
    print(f"turn inequality counts: {turn_system['inequality_count_histogram']}")
    print(f"z3 status counts: {z3_replay['status_counts']}")
    print(f"farkas certificate hash: {farkas_replay['certificate_sha256']}")
    print(f"farkas lambda counts: {farkas_replay['lambda_histogram']}")
    print(
        "benchmark: "
        f"index={benchmark['frontier_assignment_index_1based']}, "
        f"frontier={benchmark['natural_order_classify_status']}, "
        f"vertex_circle={benchmark['vertex_circle_status']}, "
        f"turn={benchmark['turn_z3_status']}"
    )
    if elapsed is not None:
        print(f"elapsed_seconds: {elapsed:.6f}")


def summary_json_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return a compact reviewer-facing JSON view without certificate rows."""

    turn_system = payload.get("turn_system")
    compact_turn_system: dict[str, object] = {}
    if isinstance(turn_system, dict):
        for key in (
            "normalized_variables",
            "sum_constraint",
            "nonnegativity",
            "weak_inequality_template",
            "strict_geometry_note",
            "inequality_count_histogram",
        ):
            if key in turn_system:
                compact_turn_system[key] = turn_system[key]

    compact: dict[str, object] = {}
    for key in (
        "schema",
        "status",
        "trust",
        "claim_scope",
        "n",
        "row_size",
        "cyclic_order",
        "source_frontier",
        "z3_replay",
        "farkas_replay",
        "benchmarks",
        "conclusion",
        "review_requirements",
        "provenance",
    ):
        if key in payload:
            compact[key] = payload[key]
    if compact_turn_system:
        compact["turn_system"] = compact_turn_system
    return compact


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true", help="print stable JSON")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="print compact reviewer-facing JSON without certificate rows",
    )
    parser.add_argument("--write", action="store_true", help="write stable JSON artifact")
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="validate an existing artifact")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = _resolve(args.artifact)
    out = _resolve(args.out)
    if args.write and args.check and artifact != out:
        raise SystemExit("--write --check requires --artifact and --out to match")

    start = perf_counter()
    payload = _load_json(artifact) if args.check else summary_payload()
    if args.assert_expected:
        assert_expected_payload(payload)
    else:
        errors = validate_payload(payload)
        if errors:
            raise SystemExit("; ".join(errors[:5]))
    elapsed = perf_counter() - start

    if args.write:
        _write_json(out, payload)

    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        _print_summary(payload, elapsed)
        if args.assert_expected:
            print("OK: n=9 turn-inequality frontier replay matches expected data")
        if args.check:
            print(f"checked {display_path(artifact, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
