#!/usr/bin/env python3
"""Crosswalk the n=9 three-row compression to one generic hinge lemma.

This checker reads the stored review-pending core-compression artifact.  It
does not regenerate the n=9 selected-witness frontier.  Its mathematical
payload is the arbitrary-n local Kalmanson equilateral-hinge recognizer; the
stored records are used only for a deterministic proof-mining crosswalk.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

from erdos97.kalmanson_equilateral_hinge import (
    HingeInstance,
    find_core_hinge_instances,
    find_hinge_instances,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_SOURCE = (
    ROOT / "data" / "certificates" / "n9_kalmanson_three_row_core_compression.json"
)
DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "kalmanson_equilateral_hinge_crosswalk.json"
)

SCHEMA = "erdos97.kalmanson_equilateral_hinge_crosswalk.v1"
STATUS = "REVIEW_PENDING_KALMANSON_EQUILATERAL_HINGE_CROSSWALK"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Arbitrary-n local strict-Kalmanson equilateral-hinge lemma and a "
    "deterministic crosswalk against the stored review-pending n=9 three-row "
    "compression; the source frontier is not regenerated and no result status "
    "is promoted."
)
SOURCE_SCHEMA = "erdos97.n9_kalmanson_three_row_core_compression.v1"
SOURCE_SHA256 = "a5387ef8575ace0cd16d55a0a29bbc45f72ca88caa7233be4c80041924fd703a"
SOURCE_COMPRESSED_SHA256 = (
    "55edb73475517dcc4e8413cdb84082957bc8426d2d67bd25cc28502ef3c124c0"
)
EXPECTED_RECORDS = 184
EXPECTED_KIND_COUNTS = {"K1": 95, "K2": 89}
EXPECTED_SOURCE_SIGNATURES = 56
EXPECTED_TEMPLATE_ORBITS = 1
EXPECTED_CORE_MATCH_HISTOGRAM = {"1": 184}
EXPECTED_FULL_HINGE_HISTOGRAM = {
    "2": 36,
    "3": 6,
    "5": 18,
    "6": 54,
    "8": 54,
    "9": 16,
}
EXPECTED_TOTAL_FULL_HINGES = 1_080
EXPECTED_CROSSWALK_SHA256 = (
    "41390dbac0177ace8615e393fe4826dd5a7d325ccdc46370e07d315caa2f2a8d"
)

PROVENANCE = {
    "generator": "scripts/check_kalmanson_equilateral_hinge_crosswalk.py",
    "command": (
        "python scripts/check_kalmanson_equilateral_hinge_crosswalk.py "
        "--write --assert-expected"
    ),
    "source_artifact": (
        "data/certificates/n9_kalmanson_three_row_core_compression.json"
    ),
}

NOT_CLAIMED = [
    "general proof of Erdos Problem #97",
    "counterexample to Erdos Problem #97",
    "n=9 is proved",
    "n=9 external review complete",
    "source frontier independently regenerated",
    "official/global status update",
]


def canonical_json(value: object) -> bytes:
    """Return a stable compact JSON encoding."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load one JSON object."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write a stable human-readable JSON artifact."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def _integer_list(value: object, name: str) -> list[int]:
    if not isinstance(value, list) or any(
        isinstance(item, bool) or not isinstance(item, int) for item in value
    ):
        raise ValueError(f"{name} must be a list of integer labels")
    return value


def _template_signature(hinge: HingeInstance) -> str:
    """Forget labels while retaining the oriented membership template."""
    slots = {hinge.a: "A", hinge.b: "B", hinge.c: "C", hinge.d: "D"}
    value = {
        "centers": [slots[center] for center in hinge.centers],
        "required_pairs": [
            [slots[left], slots[right]] for left, right in hinge.required_pairs
        ],
    }
    return hashlib.sha256(canonical_json(value)).hexdigest()[:16]


def _source_record_data(record: dict[str, Any]) -> tuple[list[list[int]], list[int], list[int], str, str]:
    rows_value = record.get("rows")
    if not isinstance(rows_value, list):
        raise ValueError("record.rows must be a list")
    rows = [
        _integer_list(row, f"record.rows[{index}]")
        for index, row in enumerate(rows_value)
    ]

    edge = record.get("best_kalmanson_self_edge")
    core = record.get("best_kalmanson_minimal_core")
    if not isinstance(edge, dict) or not isinstance(core, dict):
        raise ValueError("record must contain best edge and best core objects")
    quadruple = _integer_list(edge.get("quadrilateral"), "best quadrilateral")
    centers = _integer_list(core.get("row_indices"), "best core centers")
    kind = edge.get("kind")
    signature = record.get("best_kalmanson_dihedral_core_signature16")
    if kind not in {"K1", "K2"}:
        raise ValueError(f"unexpected best Kalmanson kind: {kind!r}")
    if not isinstance(signature, str):
        raise ValueError("best core signature must be a string")
    return rows, quadruple, centers, kind, signature


def build_payload(source_path: Path = DEFAULT_SOURCE) -> dict[str, Any]:
    """Build the exact crosswalk payload from the pinned source artifact."""
    source_digest = sha256_file(source_path)
    if source_digest != SOURCE_SHA256:
        raise AssertionError(
            f"source sha256: expected {SOURCE_SHA256}, got {source_digest}"
        )
    source = load_json(source_path)
    if source.get("schema") != SOURCE_SCHEMA:
        raise AssertionError(
            f"source schema: expected {SOURCE_SCHEMA!r}, got {source.get('schema')!r}"
        )
    if source.get("compressed_certificate_sha256") != SOURCE_COMPRESSED_SHA256:
        raise AssertionError("source compressed-certificate digest is not pinned value")

    cyclic_order = _integer_list(source.get("cyclic_order"), "source.cyclic_order")
    records_value = source.get("records")
    if not isinstance(records_value, list):
        raise ValueError("source.records must be a list")

    kind_counts: Counter[str] = Counter()
    source_signatures: set[str] = set()
    template_signatures: set[str] = set()
    core_match_counts: Counter[int] = Counter()
    full_hinge_counts: Counter[int] = Counter()
    crosswalk_records: list[dict[str, Any]] = []

    for position, value in enumerate(records_value):
        if not isinstance(value, dict):
            raise ValueError(f"source.records[{position}] must be an object")
        assignment_index = value.get("assignment_index")
        if isinstance(assignment_index, bool) or not isinstance(assignment_index, int):
            raise ValueError("assignment_index must be an integer")
        rows, quadruple, core_centers, kind, source_signature = _source_record_data(value)
        core_hits = find_core_hinge_instances(rows, quadruple, core_centers)
        full_hits = find_hinge_instances(rows, cyclic_order)
        core_match_counts[len(core_hits)] += 1
        full_hinge_counts[len(full_hits)] += 1
        kind_counts[kind] += 1
        source_signatures.add(source_signature)

        for hit in core_hits:
            template_signatures.add(_template_signature(hit))
        if len(core_hits) != 1:
            explanation = [hit.as_dict() for hit in core_hits]
            raise AssertionError(
                f"assignment {assignment_index} has {len(core_hits)} core hinges: "
                f"{explanation}"
            )
        hit = core_hits[0]
        if hit.inequality_kind != kind:
            raise AssertionError(
                f"assignment {assignment_index}: hinge kind {hit.inequality_kind} "
                f"does not match stored best kind {kind}"
            )

        crosswalk_records.append(
            {
                "assignment_index": assignment_index,
                "source_best_kalmanson_kind": kind,
                "source_best_dihedral_core_signature16": source_signature,
                "unique_hinge_orientation": [hit.a, hit.b, hit.c, hit.d],
                "full_assignment_hinge_count": len(full_hits),
            }
        )

    crosswalk_records.sort(key=lambda record: record["assignment_index"])
    crosswalk_digest = hashlib.sha256(
        canonical_json({"records": crosswalk_records})
    ).hexdigest()
    summary = {
        "source_record_count": len(records_value),
        "covered_source_records": sum(
            count for matches, count in core_match_counts.items() if matches > 0
        ),
        "unmatched_source_records": core_match_counts.get(0, 0),
        "ambiguous_source_records": sum(
            count for matches, count in core_match_counts.items() if matches > 1
        ),
        "core_hinge_match_count_histogram": {
            str(key): count for key, count in sorted(core_match_counts.items())
        },
        "source_best_kalmanson_kind_counts": dict(sorted(kind_counts.items())),
        "source_distinct_dihedral_core_signatures16": len(source_signatures),
        "generic_pair_membership_template_orbits": len(template_signatures),
        "generic_template_signatures16": sorted(template_signatures),
        "full_assignment_hinge_count_histogram": {
            str(key): count for key, count in sorted(full_hinge_counts.items())
        },
        "total_full_assignment_hinge_instances": sum(
            size * count for size, count in full_hinge_counts.items()
        ),
    }
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "lemma": {
            "name": "Kalmanson equilateral hinge",
            "scope": "any four cyclically ordered vertices in any strictly convex polygon",
            "oriented_vertices": ["A", "B", "C", "D"],
            "required_centers": ["A", "B", "D"],
            "required_pairs": [["B", "C"], ["A", "C"], ["A", "B"]],
            "strict_inequality": "D_AD + D_BC < D_AC + D_BD",
            "contradiction": "the three spoke equalities make both sides equal",
        },
        "source_artifact": {
            "path": str(source_path.relative_to(ROOT)),
            "sha256": source_digest,
            "schema": source.get("schema"),
            "status": source.get("status"),
            "trust": source.get("trust"),
            "compressed_certificate_sha256": source.get(
                "compressed_certificate_sha256"
            ),
            "frontier_regenerated_by_this_checker": False,
        },
        "summary": summary,
        "crosswalk_sha256": crosswalk_digest,
        "records": crosswalk_records,
        "interpretation_warnings": [
            "The local hinge lemma is arbitrary-n, but this crosswalk only audits the stored n=9 compression records.",
            "The source frontier remains review-pending and is not independently regenerated here.",
            "No theorem forces an equilateral hinge in every hypothetical counterexample yet.",
        ],
        "not_claimed": list(NOT_CLAIMED),
        "provenance": dict(PROVENANCE),
    }


def summary_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the artifact without record-level details."""
    return {key: value for key, value in payload.items() if key != "records"}


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert all pinned crosswalk counts and trust-boundary fields."""
    errors: list[str] = []
    expected_scalars = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "crosswalk_sha256": EXPECTED_CROSSWALK_SHA256,
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            errors.append(f"{key}: expected {expected!r}, got {payload.get(key)!r}")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        errors.append("summary must be an object")
        summary = {}
    expected_summary = {
        "source_record_count": EXPECTED_RECORDS,
        "covered_source_records": EXPECTED_RECORDS,
        "unmatched_source_records": 0,
        "ambiguous_source_records": 0,
        "core_hinge_match_count_histogram": EXPECTED_CORE_MATCH_HISTOGRAM,
        "source_best_kalmanson_kind_counts": EXPECTED_KIND_COUNTS,
        "source_distinct_dihedral_core_signatures16": EXPECTED_SOURCE_SIGNATURES,
        "generic_pair_membership_template_orbits": EXPECTED_TEMPLATE_ORBITS,
        "full_assignment_hinge_count_histogram": EXPECTED_FULL_HINGE_HISTOGRAM,
        "total_full_assignment_hinge_instances": EXPECTED_TOTAL_FULL_HINGES,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key}: expected {expected!r}, got {summary.get(key)!r}"
            )

    source = payload.get("source_artifact")
    if not isinstance(source, dict):
        errors.append("source_artifact must be an object")
        source = {}
    if source.get("sha256") != SOURCE_SHA256:
        errors.append("source_artifact.sha256 does not match pinned input")
    if source.get("frontier_regenerated_by_this_checker") is not False:
        errors.append("frontier_regenerated_by_this_checker must remain false")
    records = payload.get("records")
    if not isinstance(records, list) or len(records) != EXPECTED_RECORDS:
        errors.append(f"records must contain exactly {EXPECTED_RECORDS} entries")
    if payload.get("not_claimed") != NOT_CLAIMED:
        errors.append("not_claimed boundary changed")
    if errors:
        raise AssertionError("\n".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    output = parser.add_mutually_exclusive_group()
    output.add_argument("--json", action="store_true")
    output.add_argument("--summary-json", action="store_true")
    args = parser.parse_args()

    payload = build_payload(args.source)
    if args.assert_expected:
        assert_expected_payload(payload)
    if args.check:
        stored = load_json(args.artifact)
        if stored != payload:
            raise AssertionError(f"{args.artifact} does not match regenerated payload")
    if args.write:
        write_json(args.artifact, payload)

    if args.summary_json:
        print(json.dumps(summary_payload(payload), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print("Kalmanson equilateral-hinge crosswalk")
        print(f"source records: {summary['source_record_count']}")
        print(f"covered records: {summary['covered_source_records']}")
        print(
            "source signatures -> generic template orbits: "
            f"{summary['source_distinct_dihedral_core_signatures16']} -> "
            f"{summary['generic_pair_membership_template_orbits']}"
        )
        print(
            "total full-assignment hinges: "
            f"{summary['total_full_assignment_hinge_instances']}"
        )
        print(f"crosswalk sha256: {payload['crosswalk_sha256']}")
        if args.write:
            print(f"wrote {args.artifact}")
        if args.assert_expected:
            print("OK: expected crosswalk invariants verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
