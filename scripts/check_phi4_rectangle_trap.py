#!/usr/bin/env python3
"""Check and optionally write the n=9 phi 4-cycle rectangle-trap certificate."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.incidence_filters import (  # noqa: E402
    adjacent_two_overlap_violations,
    crossing_bisector_violations,
    forced_equal_classes_from_matrix,
    mutual_midpoint_matrix,
    odd_forced_perpendicular_cycle,
    phi4_rectangle_trap_certificates,
    phi_directed_4_cycles,
)

PATTERN_NAME = "N9_phi4_rectangle_trap_selected_witness_pattern"
CERT_PATH = ROOT / "data" / "certificates" / "n9_phi4_rectangle_trap.json"

N9_RECTANGLE_TRAP_PATTERN = [
    [1, 2, 3, 8],
    [0, 2, 4, 7],
    [1, 3, 5, 7],
    [1, 4, 6, 8],
    [0, 2, 5, 6],
    [3, 4, 6, 7],
    [2, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 4, 5],
]


def build_payload() -> dict[str, object]:
    matrix = mutual_midpoint_matrix(N9_RECTANGLE_TRAP_PATTERN)
    order = list(range(len(N9_RECTANGLE_TRAP_PATTERN)))
    certs = phi4_rectangle_trap_certificates(N9_RECTANGLE_TRAP_PATTERN, order)
    return {
        "pattern_name": PATTERN_NAME,
        "trust_label": "EXACT_OBSTRUCTION",
        "scope": "fixed selected-witness pattern only",
        "global_claim": "No general proof and no counterexample are claimed.",
        "cyclic_order": order,
        "S": N9_RECTANGLE_TRAP_PATTERN,
        "older_filter_diagnostics": {
            "odd_forced_perpendicularity_cycle": odd_forced_perpendicular_cycle(
                N9_RECTANGLE_TRAP_PATTERN
            ),
            "mutual_midpoint_matrix_rank": int(matrix.rank()),
            "forced_equality_classes": forced_equal_classes_from_matrix(matrix, 9),
            "adjacent_two_overlap_violations": adjacent_two_overlap_violations(
                N9_RECTANGLE_TRAP_PATTERN, order
            ),
            "crossing_bisector_violations": crossing_bisector_violations(
                N9_RECTANGLE_TRAP_PATTERN, order
            ),
        },
        "phi_directed_4_cycles": [
            [list(chord) for chord in cycle]
            for cycle in phi_directed_4_cycles(N9_RECTANGLE_TRAP_PATTERN)
        ],
        "rectangle_trap_certificates": certs,
    }


def assert_expected(payload: dict[str, object]) -> None:
    diagnostics = payload["older_filter_diagnostics"]
    if not isinstance(diagnostics, dict):
        raise AssertionError("older_filter_diagnostics should be a mapping")
    if diagnostics["odd_forced_perpendicularity_cycle"] is not None:
        raise AssertionError("unexpected odd forced-perpendicularity cycle")
    if diagnostics["mutual_midpoint_matrix_rank"] != 0:
        raise AssertionError("unexpected mutual midpoint rank")
    if diagnostics["forced_equality_classes"]:
        raise AssertionError("unexpected forced equality classes")
    if diagnostics["adjacent_two_overlap_violations"]:
        raise AssertionError("unexpected adjacent two-overlap violations")
    if diagnostics["crossing_bisector_violations"]:
        raise AssertionError("unexpected crossing-bisector violations")

    certs = payload["rectangle_trap_certificates"]
    if not isinstance(certs, list) or len(certs) != 1:
        raise AssertionError(f"expected one rectangle-trap certificate, got {certs}")
    cert = certs[0]
    if not isinstance(cert, dict):
        raise AssertionError("certificate should be a mapping")
    if cert["phi_cycle"] != [[0, 6], [2, 8], [1, 5], [4, 7]]:
        raise AssertionError(f"unexpected phi cycle: {cert['phi_cycle']}")
    if cert["cyclic_subsequence"] != [0, 1, 2, 4, 5, 6, 7, 8]:
        raise AssertionError(f"unexpected cyclic subsequence: {cert['cyclic_subsequence']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print the full JSON payload")
    parser.add_argument("--write", action="store_true", help=f"write {CERT_PATH}")
    parser.add_argument("--assert-expected", action="store_true", help="assert the known result")
    args = parser.parse_args()

    payload = build_payload()
    if args.assert_expected:
        assert_expected(payload)

    if args.write:
        CERT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CERT_PATH.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        certs = payload["rectangle_trap_certificates"]
        print(f"{PATTERN_NAME}: {len(certs)} phi 4-cycle rectangle-trap certificate(s)")
        if args.assert_expected:
            print("OK: expected n=9 rectangle-trap obstruction verified")
        if args.write:
            print(f"wrote {CERT_PATH.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
