#!/usr/bin/env python3
"""Check the finite Bridge Lemma A' frontier diagnostic artifact.

This script regenerates the n=8/n=9 ear-orderability frontier and the exact
obstruction crosswalk for the non-ear proof-mining targets.  It is diagnostic
only: no general proof, bridge proof, or counterexample is claimed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import analyze_n8_exact_survivors as n8_exact  # noqa: E402
from erdos97.bridge_lemma_frontier import (  # noqa: E402
    CLAIM_SCOPE,
    GeometryConfig,
    assert_expected_payload,
    build_payload,
)


DEFAULT_OUT = ROOT / "data" / "certificates" / "bridge_lemma_frontier.json"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def n8_exact_obstruction_map(root: Path) -> dict[int, list[dict[str, object]]]:
    """Return exact obstruction labels for the reconstructed n=8 classes."""

    survivors = n8_exact.load_survivors(root)
    compatible_counts = n8_exact.check_cyclic_counts(survivors)
    y2_span = n8_exact.check_y2_span(survivors)
    class3_duplicate = n8_exact.check_class3_duplicate_certificate(survivors)
    class4_collinearity = n8_exact.check_class4_collinearity_certificate(survivors)
    class5_groebner = n8_exact.check_class5_groebner(survivors)
    class14 = n8_exact.check_class14_certificate(survivors)

    out: dict[int, list[dict[str, object]]] = {}
    for record in survivors:
        class_id = int(record["id"])
        obstructions: list[dict[str, object]] = []
        count = int(compatible_counts[class_id])
        if count == 0:
            obstructions.append(
                {
                    "method": "cyclic_order_noncrossing",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": "0 compatible cyclic orders",
                }
            )
        if y2_span.get(class_id):
            obstructions.append(
                {
                    "method": "pb_y2_span",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": "y_2 lies in the rational PB-polynomial span",
                }
            )
        if class_id == 3 and class3_duplicate:
            obstructions.append(
                {
                    "method": "class3_duplicate_vertex",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": "Groebner substitution chain forces duplicate vertices",
                }
            )
        if class_id == 4 and class4_collinearity:
            obstructions.append(
                {
                    "method": "class4_collinearity",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": "Groebner substitution chain forces collinearity",
                }
            )
        if class_id == 5 and class5_groebner:
            obstructions.append(
                {
                    "method": "class5_groebner_contradiction",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": "Groebner basis contains 1",
                }
            )
        if class_id == 14 and all(bool(value) for value in class14.values()):
            obstructions.append(
                {
                    "method": "class14_pb_ed_groebner_strict_interior",
                    "status": "EXACT_OBSTRUCTION",
                    "scope": "n=8 selected-witness survivor class",
                    "detail": (
                        "PB+ED Groebner branches exist only in configurations "
                        "failing strict convexity"
                    ),
                }
            )
        out[class_id] = obstructions
    return out


def build_payload_from_repo(
    root: Path = ROOT,
    geometry_config: GeometryConfig | None = None,
) -> dict[str, object]:
    survivors_path = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    survivors = load_json(survivors_path)
    if not isinstance(survivors, list):
        raise ValueError("n8 survivor artifact should be a JSON list")
    return build_payload(
        survivors,
        n8_exact_obstruction_map(root),
        geometry_config=geometry_config,
    )


def compare_artifact(payload: Mapping[str, object], path: Path) -> None:
    checked = load_json(path)
    if checked != payload:
        raise AssertionError(f"checked artifact is stale: {path.relative_to(ROOT)}")


def print_human_summary(payload: Mapping[str, object]) -> None:
    summary = payload["summary"]
    assert isinstance(summary, Mapping)
    print("Bridge Lemma A' frontier diagnostic")
    print(f"claim scope: {CLAIM_SCOPE}")
    print(
        "n=8: "
        f"{summary['n8_ear_orderable']} ear-orderable, "
        f"{summary['n8_non_ear_orderable']} non-ear "
        f"{summary['n8_non_ear_ids']}"
    )
    print(
        "n=9: "
        f"{summary['n9_ear_orderable']} ear-orderable, "
        f"{summary['n9_non_ear_orderable']} non-ear "
        f"{summary['n9_non_ear_indices']}"
    )
    print(f"n=9 vertex-circle statuses: {summary['n9_vertex_circle_status_counts']}")
    print(f"proof-mining targets: {summary['proof_mining_target_count']}")
    geometry = payload.get("geometry")
    if isinstance(geometry, Mapping) and geometry.get("status") == "RAN":
        print("geometry smoke probes:")
        records = geometry.get("records")
        if isinstance(records, list):
            for record in records:
                if not isinstance(record, Mapping):
                    continue
                if record.get("status") != "RAN":
                    print(f"  {record.get('target_id')}: {record.get('status')}")
                    continue
                print(
                    f"  {record.get('target_id')}: "
                    f"eq_rms={record.get('eq_rms')} "
                    f"max_spread={record.get('max_spread')} "
                    f"success={record.get('success')}"
                )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--write", action="store_true", help="write the checked artifact")
    parser.add_argument("--check", action="store_true", help="compare against the checked artifact")
    parser.add_argument("--assert-expected", action="store_true", help="assert stable frontier counts")
    parser.add_argument("--json", action="store_true", help="print the full JSON payload")
    parser.add_argument("--run-geometry", action="store_true", help="run optional numerical smoke probes")
    parser.add_argument("--geometry-mode", choices=["polar", "direct", "support"], default="polar")
    parser.add_argument("--geometry-optimizer", choices=["trf", "slsqp"], default="slsqp")
    parser.add_argument("--geometry-restarts", type=int, default=3)
    parser.add_argument("--geometry-seed", type=int, default=0)
    parser.add_argument("--geometry-max-nfev", type=int, default=1000)
    parser.add_argument("--geometry-margin", type=float, default=1e-3)
    args = parser.parse_args(argv)
    if args.check and args.run_geometry:
        parser.error("--check cannot be combined with --run-geometry")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    geometry = GeometryConfig(
        run=args.run_geometry,
        mode=args.geometry_mode,
        optimizer=args.geometry_optimizer,
        restarts=args.geometry_restarts,
        seed=args.geometry_seed,
        max_nfev=args.geometry_max_nfev,
        margin=args.geometry_margin,
    )
    payload = build_payload_from_repo(ROOT, geometry)

    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        compare_artifact(payload, args.out)
    if args.write:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print_human_summary(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
