#!/usr/bin/env python3
"""Generate or check the fragile critical-radius midpoint diagnostic."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from erdos97.bridge_negative_controls import output7_two_block_rows
from erdos97.fragile_benchmarks import block6_two_block_survivor_extension_3_rows
from erdos97.fragile_radius_midpoint import (
    radius_midpoint_branch_certificate,
    two_overlap_relations,
    verify_radius_midpoint_identity,
)
from erdos97.json_io import load_json, write_json
from erdos97.path_display import display_path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "fragile_radius_midpoint.json"
SCHEMA = "erdos97.fragile_radius_midpoint.v1"
STATUS = "EXACT_LOCAL_RADIUS_MIDPOINT_TRICHOTOMY_DIAGNOSTIC"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
EXPECTED_CATALOG_SHA256 = (
    "3d64b404cce68cb1028421ee5a2a5c08aaf6956324e543642f46cdf894c9585e"
)


def _row_mapping(rows: Sequence[Sequence[int]]) -> dict[int, tuple[int, ...]]:
    return {center: tuple(int(label) for label in row) for center, row in enumerate(rows)}


def _benchmark_record(
    name: str,
    n: int,
    rows: Mapping[int, Sequence[int]],
    atom_equal_pairs: Sequence[Sequence[int]],
) -> dict[str, object]:
    relations = two_overlap_relations(rows)
    all_pairs = [relation.centers for relation in relations]
    return {
        "name": name,
        "n": n,
        "selected_rows": {
            str(center): list(map(int, row)) for center, row in sorted(rows.items())
        },
        "two_overlap_relation_count": len(relations),
        "two_overlap_relations": [relation.as_dict() for relation in relations],
        "all_equal_branch": radius_midpoint_branch_certificate(
            n, relations, all_pairs
        ),
        "all_strict_escape_branch": radius_midpoint_branch_certificate(n, relations, []),
        "atom_equal_mixed_escape_branch": radius_midpoint_branch_certificate(
            n, relations, atom_equal_pairs
        ),
    }


def build_payload() -> dict[str, object]:
    block6_rows = {0: (1, 2, 3, 4), 3: (0, 2, 4, 5)}
    benchmarks = [
        _benchmark_record("block6_geometric_atom", 6, block6_rows, [(0, 3)]),
        _benchmark_record(
            "two_block_full_extension_no_forward_ear",
            12,
            _row_mapping(output7_two_block_rows()),
            [(0, 3), (6, 9)],
        ),
        _benchmark_record(
            "block6_two_block_survivor_extension_3",
            12,
            _row_mapping(block6_two_block_survivor_extension_3_rows()),
            [(0, 3), (6, 9)],
        ),
    ]
    theorem_replay = verify_radius_midpoint_identity()
    catalog_material = {"theorem_replay": theorem_replay, "benchmarks": benchmarks}
    digest = sha256(
        json.dumps(catalog_material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": (
            "Exact local trichotomy for selected row pairs sharing two witnesses, "
            "plus bounded branch diagnostics on one block-6 atom and two fixed "
            "twelve-row controls. It neither forces a radius branch nor proves "
            "Euclidean realizability, catalog entry, n=9 or n=10, Erdos Problem "
            "#97, a counterexample, or an official/global status update."
        ),
        "theorem_replay": theorem_replay,
        "benchmarks": benchmarks,
        "catalog_sha256": digest,
        "summary": {
            "benchmarks_checked": len(benchmarks),
            "two_overlap_relation_counts": {
                record["name"]: record["two_overlap_relation_count"]
                for record in benchmarks
            },
            "all_equal_collision_obstructions": sum(
                bool(record["all_equal_branch"]["coordinate_collision_obstruction"])
                for record in benchmarks
            ),
            "atom_equal_mixed_escape_branches": sum(
                bool(record["atom_equal_mixed_escape_branch"]["survives_local_diagnostic"])
                for record in benchmarks
            ),
            "all_benchmarks_have_a_surviving_branch": all(
                bool(record["atom_equal_mixed_escape_branch"]["survives_local_diagnostic"])
                for record in benchmarks
            ),
        },
        "conclusion": (
            "The equal-radius branch is an exact rhombus/midpoint branch. Making "
            "all two-overlap radii equal collapses all twelve point labels in "
            "both full-row controls, but the two genuine block-6 atom equalities "
            "can coexist with an acyclic strict ordering on every other relation. "
            "Thus this lemma prunes a real metric branch but does not yet force "
            "entry into the three-halo hinge/splice endgame."
        ),
        "limitations": [
            "The diagnostic does not decide which equality or strict branch geometry selects.",
            "A surviving branch is only algebraic/order consistency, not a Euclidean realization.",
            "The two twelve-row benchmarks are fixed selected-row systems and fixed labels.",
            "No general proof, counterexample, or official/global status update is claimed.",
        ],
        "provenance": {
            "generator": "scripts/check_fragile_radius_midpoint.py",
            "command": (
                "python scripts/check_fragile_radius_midpoint.py "
                "--write --assert-expected --summary-json"
            ),
        },
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["catalog_sha256"] == EXPECTED_CATALOG_SHA256
    assert payload["theorem_replay"]["polynomial_identity_verified"] is True
    assert payload["theorem_replay"]["normalized_factorization_verified"] is True
    benchmarks = payload["benchmarks"]
    assert [record["two_overlap_relation_count"] for record in benchmarks] == [1, 18, 18]
    assert [record["all_equal_branch"]["midpoint_matrix_rank"] for record in benchmarks] == [1, 11, 11]
    assert benchmarks[0]["all_equal_branch"]["forced_point_equal_classes"] == []
    assert benchmarks[0]["all_equal_branch"]["survives_local_diagnostic"] is True
    for record in benchmarks[1:]:
        assert record["all_equal_branch"]["forced_point_equal_classes"] == [list(range(12))]
        assert record["all_equal_branch"]["survives_local_diagnostic"] is False
        mixed = record["atom_equal_mixed_escape_branch"]
        assert mixed["equal_relation_count"] == 2
        assert mixed["strict_relation_count"] == 16
        assert mixed["midpoint_matrix_rank"] == 2
        assert mixed["forced_point_equal_classes"] == []
        assert mixed["radius_equality_closed"] is True
        assert mixed["strict_radius_acyclic"] is True
        assert mixed["survives_local_diagnostic"] is True
    assert payload["summary"] == {
        "benchmarks_checked": 3,
        "two_overlap_relation_counts": {
            "block6_geometric_atom": 1,
            "two_block_full_extension_no_forward_ear": 18,
            "block6_two_block_survivor_extension_3": 18,
        },
        "all_equal_collision_obstructions": 2,
        "atom_equal_mixed_escape_branches": 3,
        "all_benchmarks_have_a_surviving_branch": True,
    }


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def _load_object(path: Path) -> dict[str, Any]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"expected object payload in {display_path(path, ROOT)}")
    return payload


def summary_json_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    return {
        key: payload[key]
        for key in (
            "schema",
            "status",
            "trust",
            "claim_scope",
            "theorem_replay",
            "catalog_sha256",
            "summary",
            "conclusion",
            "limitations",
            "provenance",
        )
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument("--summary-json", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
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
    generated = build_payload()
    if args.check:
        stored = _load_object(artifact_path)
        if stored != generated:
            raise SystemExit("stored payload differs from regenerated radius-midpoint diagnostic")
        payload = stored
    else:
        payload = generated
    if args.assert_expected:
        assert_expected(payload)
    if args.write:
        write_json(payload, out_path)
    if args.summary_json:
        print(json.dumps(summary_json_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("fragile critical-radius midpoint diagnostic")
        print(f"benchmarks: {payload['summary']['benchmarks_checked']}")
        print(
            "all-equal collision obstructions: "
            f"{payload['summary']['all_equal_collision_obstructions']}"
        )
        print(
            "atom-equal mixed escapes: "
            f"{payload['summary']['atom_equal_mixed_escape_branches']}"
        )
        if args.assert_expected:
            print("OK: radius-midpoint expectations verified")
        if args.check:
            print(f"checked {display_path(artifact_path, ROOT)}")
        if args.write:
            print(f"wrote {display_path(out_path, ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
