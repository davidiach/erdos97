#!/usr/bin/env python3
"""Run the Barany--Roldan-Pensado boundary-to-vertex diagnostic."""

from __future__ import annotations

import argparse
import json
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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    parser.add_argument("--write", action="store_true", help="write the JSON payload")
    parser.add_argument("--check", action="store_true", help="check an existing JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--tol", type=float, default=ROOT_TOL)
    parser.add_argument("--artifact", default=str(DEFAULT_ARTIFACT))
    args = parser.parse_args()

    artifact = Path(args.artifact)
    if args.check:
        payload = _load_json(artifact)
        current = build_payload(tol=args.tol)
        if payload != current:
            raise AssertionError("BRP boundary vertexization probe artifact is not current")
    else:
        payload = build_payload(tol=args.tol)

    if args.assert_expected:
        assert_expected_counts(payload)

    if args.write and not args.check:
        artifact.parent.mkdir(parents=True, exist_ok=True)
        artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        convexity = payload["convexity"]
        synthetic = payload["synthetic_a5_scan"]
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
        if args.assert_expected:
            print("OK: expected BRP boundary diagnostic counts verified")
        if args.write and not args.check:
            print(f"wrote {display_path(artifact, ROOT)}")
        if args.check:
            print(f"OK: {display_path(artifact, ROOT)} is current")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
