#!/usr/bin/env python3
"""Validate the n=9 row-Ptolemy product-cancellation artifact."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.n9_row_ptolemy_product_cancellations import (  # noqa: E402
    CLAIM_SCOPE,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TRUST,
    row_ptolemy_product_cancellation_report,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_product_cancellations.json"
)
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "cyclic_order",
    "filter",
    "hit_records",
    "hit_summary",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "source_artifacts",
    "source_frontier",
    "status",
    "trust",
    "witness_size",
}


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _validate_claim_scope(errors: list[str], claim_scope: Any) -> None:
    expect_equal(errors, "claim_scope", claim_scope, CLAIM_SCOPE)
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
        return
    lowered = claim_scope.lower()
    for phrase in (
        "not a proof",
        "not a counterexample",
        "not a geometric realizability test",
        "not a global status update",
    ):
        if phrase not in lowered:
            errors.append(f"claim_scope must include {phrase!r}")


def _validate_interpretation(errors: list[str], interpretation: Any) -> None:
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
        return
    required = (
        "No proof of the n=9 case is claimed.",
        "The row order must be supplied or certified. This is not an orderless abstract-incidence obstruction.",
    )
    for phrase in required:
        if phrase not in interpretation:
            errors.append(f"interpretation must include {phrase!r}")


def validate_payload(payload: Any, *, recompute: bool = True) -> list[str]:
    """Return validation errors for a loaded cancellation artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, "
            f"got {sorted(top_level_keys)!r}"
        )

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "n": 9,
        "witness_size": 4,
        "cyclic_order": list(range(9)),
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    _validate_claim_scope(errors, payload.get("claim_scope"))
    _validate_interpretation(errors, payload.get("interpretation"))
    expect_equal(errors, "provenance", payload.get("provenance"), PROVENANCE)

    source = payload.get("source_frontier")
    if isinstance(source, dict):
        expect_equal(errors, "source assignment count", source.get("assignment_count"), 184)
        expect_equal(errors, "source nodes", source.get("nodes_visited"), 100817)
        expect_equal(errors, "source families", source.get("dihedral_family_count"), 16)
    else:
        errors.append("source_frontier must be an object")

    summary = payload.get("hit_summary")
    if isinstance(summary, dict):
        expect_equal(errors, "hit assignment count", summary.get("hit_assignment_count"), 26)
        expect_equal(errors, "hit certificate count", summary.get("hit_certificate_count"), 216)
        expect_equal(errors, "hit family count", summary.get("hit_family_count"), 3)
        expect_equal(
            errors,
            "hit status counts",
            summary.get("hit_assignment_vertex_circle_status_counts"),
            {"self_edge": 26},
        )
    else:
        errors.append("hit_summary must be an object")

    if recompute:
        try:
            expected_payload = row_ptolemy_product_cancellation_report()
        except (AssertionError, ValueError) as exc:
            errors.append(f"recomputed row-Ptolemy report failed: {exc}")
        else:
            expect_equal(
                errors,
                "row-Ptolemy product-cancellation payload",
                payload,
                expected_payload,
            )
    return errors


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    source = object_payload.get("source_frontier", {})
    hit_summary = object_payload.get("hit_summary", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "source_assignment_count": (
            source.get("assignment_count") if isinstance(source, dict) else None
        ),
        "hit_assignment_count": (
            hit_summary.get("hit_assignment_count")
            if isinstance(hit_summary, dict)
            else None
        ),
        "hit_certificate_count": (
            hit_summary.get("hit_certificate_count")
            if isinstance(hit_summary, dict)
            else None
        ),
        "hit_family_count": (
            hit_summary.get("hit_family_count") if isinstance(hit_summary, dict) else None
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy product-cancellation artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"source assignments: {summary['source_assignment_count']}")
        print(f"hit assignments: {summary['hit_assignment_count']}")
        print(f"hit certificates: {summary['hit_certificate_count']}")
        print(f"hit families: {summary['hit_family_count']}")
        if args.check:
            print("OK: row-Ptolemy product-cancellation checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
