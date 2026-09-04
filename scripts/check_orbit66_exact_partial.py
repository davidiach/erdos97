#!/usr/bin/env python3
"""Exact checker for a 66-point PARTIAL construction for Erdos Problem #97.

The checked set is strictly convex. Exactly 60 of its 66 vertices have four
other vertices at one common distance; the other six have maximum distance
multiplicity two or three. It is therefore not a counterexample.

Only Python's standard library is used. The construction is defined by rational
seeds and nested radical circle intersections. Dyadic interval arithmetic is
used only to certify strict inequalities and to separate unequal distances;
the selected equalities follow symbolically from the defining identities.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any

# Support both ``python scripts/check_...py`` and package-style test imports.
if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.orbit66_exact_partial_data import (  # noqa: E402
    CLAIM_SCOPE,
    EXPECTED_AT_LEAST_FOUR,
    EXPECTED_AT_MOST_THREE,
    EXPECTED_CONVEXITY_TESTS,
    EXPECTED_DISTINCT_PAIRS,
    EXPECTED_DISTRIBUTION,
    EXPECTED_ORBIT_COUNT,
    EXPECTED_POINT_COUNT,
    HISTORY,
    SCHEMA,
    STATUS,
    TRUST,
)
from scripts.orbit66_exact_partial_verify import build_payload  # noqa: E402


def validate_payload(payload: dict[str, Any]) -> list[str]:
    """Check pinned claim scope and expected summary values."""

    errors = list(payload.get("errors", []))
    if payload.get("schema") != SCHEMA:
        errors.append("schema mismatch")
    if payload.get("status") != STATUS:
        errors.append("status mismatch")
    if payload.get("trust") != TRUST:
        errors.append("trust mismatch")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        errors.append("claim scope mismatch")
    if payload.get("validation_status") != "passed":
        errors.append("validation did not pass")

    summary = payload.get("summary", {})
    expected = {
        "point_count": EXPECTED_POINT_COUNT,
        "orbit_count": EXPECTED_ORBIT_COUNT,
        "vertices_with_maximum_multiplicity_at_least_four": (
            EXPECTED_AT_LEAST_FOUR
        ),
        "vertices_with_maximum_multiplicity_at_most_three": EXPECTED_AT_MOST_THREE,
        "exact_maximum_multiplicity_distribution": EXPECTED_DISTRIBUTION,
        "strict_hull_edge_point_determinants_certified": EXPECTED_CONVEXITY_TESTS,
        "distinct_pairs_certified": EXPECTED_DISTINCT_PAIRS,
        "intersection_radicand_count": len(HISTORY),
        "all_intersection_radicands_strictly_positive": True,
        "exceptional_orbits": [3, 7],
        "exceptional_vertices": [3, 7, 25, 29, 47, 51],
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append(
                f"summary mismatch for {key}: "
                f"{summary.get(key)!r} != {expected_value!r}"
            )
    return errors


def compact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": payload["schema"],
        "status": payload["status"],
        "trust": payload["trust"],
        "claim_scope": payload["claim_scope"],
        "validation_status": payload["validation_status"],
        "errors": payload["errors"],
        "summary": payload["summary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bits", type=int, default=256)
    parser.add_argument(
        "--output",
        type=Path,
        help="optional path for the complete regenerated JSON payload",
    )
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--json", action="store_true", help="print the complete JSON payload"
    )
    output_group.add_argument(
        "--summary-json", action="store_true", help="print compact JSON"
    )
    parser.add_argument(
        "--assert-expected",
        action="store_true",
        help="fail unless every exact check and pinned summary value passes",
    )
    args = parser.parse_args()

    try:
        payload = build_payload(bits=args.bits)
    except ValueError as exc:
        parser.error(str(exc))
    errors = validate_payload(payload)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    elif args.summary_json:
        print(json.dumps(compact_payload(payload), indent=2, sort_keys=True))
    else:
        summary = payload["summary"]
        print(f"validation: {payload['validation_status']}")
        print(f"points: {summary.get('point_count')}")
        print(
            "vertices with maximum multiplicity >= 4: "
            f"{summary.get('vertices_with_maximum_multiplicity_at_least_four')}"
        )
        print(
            "vertices with maximum multiplicity <= 3: "
            f"{summary.get('vertices_with_maximum_multiplicity_at_most_three')}"
        )
        print(
            "distribution: "
            f"{summary.get('exact_maximum_multiplicity_distribution')}"
        )
        print("counterexample: no")

    if errors:
        for error in errors:
            print(error)
        return 1
    if args.assert_expected and payload["validation_status"] != "passed":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
