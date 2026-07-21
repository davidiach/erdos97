#!/usr/bin/env python3
"""Check bridge negative-control certificates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from erdos97.bridge_negative_controls import (
    block6_geometric_atom_certificate,
    c13_sidon_negative_control,
    false_output8_correction_certificate,
    output7_two_block_negative_control,
)

def all_certificates() -> dict[str, object]:
    return {
        "type": "bridge_negative_controls_v1",
        "status": "NEGATIVE_CONTROLS_AND_TRIAGE",
        "certificates": {
            "c13_sidon_linear": c13_sidon_negative_control(),
            "block6_geometric_atom": block6_geometric_atom_certificate(),
            "two_block_no_forward_ear": output7_two_block_negative_control(),
            "false_output8_correction": false_output8_correction_certificate(),
        },
        "interpretation": (
            "These are bridge guardrails and triage checks only. They do not "
            "claim a general proof, a counterexample, or a new finite-case "
            "status."
        ),
    }


def assert_expected(payload: dict[str, object]) -> None:
    certificates = payload["certificates"]
    if not isinstance(certificates, dict):
        raise AssertionError("certificates must be a dict")

    c13 = certificates["c13_sidon_linear"]
    if not isinstance(c13, dict):
        raise AssertionError("C13 certificate must be a dict")
    if c13["max_row_intersection"] != 1:
        raise AssertionError("C13 should be linear")
    if c13["phi_edges"] != 0:
        raise AssertionError("C13 should have no phi edges")
    if c13["forward_ear_order"]["exists"]:
        raise AssertionError("C13 should have no forward ear order")
    if not c13["fragile_cover_all_rows"]["ok"]:
        raise AssertionError("C13 all-row fragile cover should pass")

    block6 = certificates["block6_geometric_atom"]
    if not isinstance(block6, dict):
        raise AssertionError("block6 certificate must be a dict")
    if not block6["strict_convex_clockwise"]:
        raise AssertionError("block6 should be strictly convex")
    if not block6["row_equalities_ok"]:
        raise AssertionError("block6 fragile row equalities should hold")
    if not block6["unique_size4_rows_at_fragile_centers"]:
        raise AssertionError("block6 fragile rows should be unique at centers")
    if not block6["source_witness_chords_cross"]:
        raise AssertionError("block6 source/witness chords should cross")
    if not block6["source_witness_bisection_ok"]:
        raise AssertionError("block6 source/witness chords should bisect perpendicularly")

    two_block = certificates["two_block_no_forward_ear"]
    if not isinstance(two_block, dict):
        raise AssertionError("two-block certificate must be a dict")
    if two_block["forward_ear_order"]["exists"]:
        raise AssertionError("output7 two-block control should have no forward ear")
    if two_block["crossing_bisector_violations"]:
        raise AssertionError("output7 two-block control should pass crossing checks")

    correction = certificates["false_output8_correction"]
    if not isinstance(correction, dict):
        raise AssertionError("correction certificate must be a dict")
    if not correction["forward_ear_order"]["exists"]:
        raise AssertionError("outputs 8/10 correction should exhibit an ear order")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--write-certificate", help="write JSON to this path")
    args = parser.parse_args()

    payload = all_certificates()
    if args.assert_expected:
        assert_expected(payload)

    if args.write_certificate:
        path = Path(args.write_certificate)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        certificates = payload["certificates"]
        assert isinstance(certificates, dict)
        print("certificate  n  key status")
        for name, certificate in certificates.items():
            assert isinstance(certificate, dict)
            if name == "block6_geometric_atom":
                status = "strict-convex fragile atom"
            elif name == "false_output8_correction":
                status = (
                    "ear order found"
                    if certificate["forward_ear_order"]["exists"]
                    else "unexpected no ear"
                )
            else:
                status = (
                    "no forward ear"
                    if not certificate["forward_ear_order"]["exists"]
                    else "ear order found"
                )
            print(f"{name}  {certificate['n']}  {status}")
        if args.assert_expected:
            print("OK: bridge negative-control expectations verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
