#!/usr/bin/env python3
"""Run the Barany--Roldan-Pensado boundary-to-vertex diagnostic."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.brp_boundary_probe import (  # noqa: E402
    ROOT_TOL,
    assert_expected_counts,
    build_payload,
)
from erdos97.path_display import display_path  # noqa: E402


DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "brp_boundary_vertexization_probe.json"


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} does not contain a JSON object")
    return payload


def _assert_payload_current(
    stored: object,
    current: object,
    *,
    tol: float,
    path: str = "$",
) -> None:
    if isinstance(stored, float) or isinstance(current, float):
        if not isinstance(stored, (int, float)) or not isinstance(current, (int, float)):
            raise AssertionError(f"{path}: numeric type mismatch")
        if not math.isclose(float(stored), float(current), rel_tol=tol, abs_tol=tol):
            raise AssertionError(f"{path}: expected {current!r}, got {stored!r}")
        return

    if isinstance(stored, dict) and isinstance(current, dict):
        stored_keys = set(stored)
        current_keys = set(current)
        if stored_keys != current_keys:
            missing = sorted(current_keys - stored_keys)
            extra = sorted(stored_keys - current_keys)
            raise AssertionError(f"{path}: key mismatch; missing={missing}, extra={extra}")
        for key in sorted(stored):
            _assert_payload_current(
                stored[key],
                current[key],
                tol=tol,
                path=f"{path}.{key}",
            )
        return

    if isinstance(stored, list) and isinstance(current, list):
        if len(stored) != len(current):
            raise AssertionError(f"{path}: expected length {len(current)}, got {len(stored)}")
        for index, (stored_item, current_item) in enumerate(zip(stored, current, strict=True)):
            _assert_payload_current(
                stored_item,
                current_item,
                tol=tol,
                path=f"{path}[{index}]",
            )
        return

    if stored != current:
        raise AssertionError(f"{path}: expected {current!r}, got {stored!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--write", action="store_true", help="write the JSON payload")
    mode_group.add_argument("--check", action="store_true", help="check an existing JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--tol", type=float, default=ROOT_TOL)
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    args = parser.parse_args()

    artifact = Path(args.artifact)
    if args.check:
        payload = _load_json(artifact)
        current = build_payload(tol=args.tol)
        _assert_payload_current(payload, current, tol=args.tol)
    else:
        payload = build_payload(tol=args.tol)

    if args.assert_expected:
        assert_expected_counts(payload)

    if args.write:
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        convexity = payload["convexity"]
        synthetic = payload["synthetic_a5_scan"]
        preflight = payload["lemma31_preflight"]
        a5_scan = payload["lemma31_a5_constraint_scan"]
        angle_abc = preflight["angle_ABC"]
        bprime_budget = preflight["bprime_neighbourhood_budget"]
        filter_counts = a5_scan["filter_counts"]
        witnesses = a5_scan["sampled_witnesses"]
        print("BRP boundary-to-vertex diagnostic")
        print(f"seed vertices: {summary['seed_vertex_count']}")
        print(f"strictly convex seed order: {convexity['strictly_convex_in_seed_order']}")
        print(f"distinct centered vertex radii: {summary['distinct_centered_vertex_radii']}")
        print(f"max seed-vertex hits: {summary['max_vertex_hits_on_seed']}")
        print(f"max seed-boundary hits: {summary['max_boundary_hits_on_seed_edges']}")
        print(
            "circles with >=4 boundary hits: "
            f"{summary['circles_with_at_least_four_boundary_hits']}"
        )
        print(
            "circles with >=4 seed vertices: "
            f"{summary['circles_with_at_least_four_seed_vertices']}"
        )
        print(
            "synthetic A5 convex candidates: "
            f"{synthetic['strictly_convex_candidate_count']} / {synthetic['candidate_count']}"
        )
        print(f"synthetic A5 best vertex hits: {synthetic['best_max_vertex_hits']}")
        print(f"Lemma 3.1 role angle ABC degrees: {angle_abc['degrees']}")
        print(
            "Lemma 3.1 default Bprime valid: "
            f"{bprime_budget['C_outside_default_S_Bprime']}"
        )
        print(
            "Lemma 3.1 sampled A5 witnesses: "
            f"{len(witnesses)} / {a5_scan['parameterization']['sample_count']}"
        )
        print(
            "Lemma 3.1 final convex sampled witnesses: "
            f"{filter_counts['plus_rotated_15gon_strictly_convex']}"
        )
        if witnesses:
            witness = witnesses[0]
            print(
                "Lemma 3.1 first sampled A5: "
                f"t={witness['t']}, h={witness['normal_offset']}"
            )
        if args.assert_expected:
            print("OK: expected BRP boundary diagnostic counts verified")
        if args.write:
            print(f"wrote {display_path(artifact, ROOT)}")
        if args.check:
            print(f"OK: {display_path(artifact, ROOT)} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
