#!/usr/bin/env python3
"""Generate or check n=9 row-Ptolemy order-sensitivity diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.incidence_filters import (  # noqa: E402
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.path_display import display_path  # noqa: E402
from scripts.check_n9_row_ptolemy_product_cancellations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_ROW_PTOLEMY_ARTIFACT,
    load_artifact,
    validate_payload as validate_row_ptolemy_payload,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_order_sensitivity.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_order_sensitivity.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Derived n=9 row-Ptolemy order-sensitivity diagnostic for three "
    "representative hit assignments; not a proof of n=9, not a counterexample, "
    "not an all-order obstruction, not an orderless abstract-incidence "
    "obstruction, and not a global status update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_order_sensitivity.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_order_sensitivity.py "
        "--assert-expected --write"
    ),
}
SOURCE_ARTIFACT = {
    "path": "data/certificates/n9_row_ptolemy_product_cancellations.json",
    "schema": "erdos97.n9_row_ptolemy_product_cancellations.v2",
    "status": "EXPLORATORY_LEDGER_ONLY",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "examined_order_count",
    "interpretation",
    "n",
    "normalization",
    "order_generation_rule",
    "provenance",
    "representative_count",
    "rows",
    "schema",
    "source_artifacts",
    "source_fixed_order",
    "status",
    "trust",
    "witness_size",
    "zero_challenge_order_count",
}
EXPECTED_REPRESENTATIVES = [
    {
        "family_id": "F02",
        "assignment_index": 1,
        "natural_certificate_count": 6,
        "challenge_order": [0, 1, 2, 6, 5, 7, 4, 8, 3],
    },
    {
        "family_id": "F09",
        "assignment_index": 13,
        "natural_certificate_count": 12,
        "challenge_order": [0, 1, 5, 6, 7, 2, 3, 4, 8],
    },
    {
        "family_id": "F13",
        "assignment_index": 22,
        "natural_certificate_count": 18,
        "challenge_order": [0, 1, 2, 6, 7, 8, 3, 4, 5],
    },
]


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _is_dihedral_order(order: Sequence[int], base: Sequence[int]) -> bool:
    """Return whether order is a rotation or reversal of base."""

    actual = tuple(order)
    reference = tuple(base)
    if len(actual) != len(reference):
        return False
    rotations = []
    for seq in (reference, tuple(reversed(reference))):
        rotations.extend(seq[index:] + seq[:index] for index in range(len(seq)))
    return actual in rotations


def _source_records_by_key(source: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    records = source.get("hit_records")
    if not isinstance(records, list):
        raise ValueError("source row-Ptolemy artifact must contain hit_records")
    rows: dict[tuple[str, int], dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        family_id = record.get("family_id")
        assignment_index = record.get("assignment_index")
        if isinstance(family_id, str) and isinstance(assignment_index, int):
            rows[(family_id, assignment_index)] = record
    return rows


def _certificate_histogram(certificates: Sequence[dict[str, object]]) -> dict[str, Any]:
    row_counts = Counter(int(certificate["row"]) for certificate in certificates)
    variant_counts = Counter(str(certificate["variant"]) for certificate in certificates)
    zero_counts = Counter(
        str(certificate.get("zero_product", {}).get("expression"))
        for certificate in certificates
        if isinstance(certificate.get("zero_product"), dict)
    )
    return {
        "certificate_count_by_row": _json_counter(row_counts),
        "variant_counts": _json_counter(variant_counts),
        "zero_product_expression_counts": _json_counter(zero_counts),
    }


def order_sensitivity_payload(source: dict[str, Any]) -> dict[str, Any]:
    """Return the representative order-sensitivity diagnostic payload."""

    source_errors = validate_row_ptolemy_payload(source, recompute=False)
    if source_errors:
        raise ValueError(f"source row-Ptolemy artifact invalid: {source_errors[0]}")
    records_by_key = _source_records_by_key(source)
    natural_order = list(source["cyclic_order"])

    rows = []
    for expected in EXPECTED_REPRESENTATIVES:
        key = (str(expected["family_id"]), int(expected["assignment_index"]))
        record = records_by_key.get(key)
        if record is None:
            raise ValueError(f"source row-Ptolemy artifact missing representative {key}")
        selected_rows = record.get("selected_rows")
        if not isinstance(selected_rows, list):
            raise ValueError(f"representative {key} selected_rows must be a list")

        natural_certificates = row_ptolemy_product_cancellation_certificates(
            selected_rows,
            natural_order,
        )
        challenge_order = list(expected["challenge_order"])
        challenge_certificates = row_ptolemy_product_cancellation_certificates(
            selected_rows,
            challenge_order,
        )
        rows.append(
            {
                "family_id": key[0],
                "assignment_index": key[1],
                "family_orbit_size": int(record["family_orbit_size"]),
                "selected_rows": selected_rows,
                "natural_order": natural_order,
                "stored_certificate_count": int(record["certificate_count"]),
                "natural_certificate_count": len(natural_certificates),
                "natural_certificate_histogram": _certificate_histogram(
                    natural_certificates,
                ),
                "challenge_order": challenge_order,
                "challenge_order_is_dihedral_of_natural_order": _is_dihedral_order(
                    challenge_order,
                    natural_order,
                ),
                "challenge_certificate_count": len(challenge_certificates),
                "certificate_count_drop": len(natural_certificates)
                - len(challenge_certificates),
            }
        )

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": source["n"],
        "witness_size": source["witness_size"],
        "source_fixed_order": {
            "cyclic_order": natural_order,
            "hit_assignment_count": source["hit_summary"]["hit_assignment_count"],
            "hit_certificate_count": source["hit_summary"]["hit_certificate_count"],
            "hit_family_ids": [
                row["family_id"] for row in source["hit_summary"]["hit_family_counts"]
            ],
        },
        "order_generation_rule": (
            "One deterministic non-dihedral challenge order is recorded for one "
            "representative assignment from each row-Ptolemy hit family. These "
            "challenge orders are guardrails, not an exhaustive cyclic-order search."
        ),
        "normalization": {
            "natural_order_source": "source_fixed_order.cyclic_order",
            "challenge_orders_are_full_supplied_cyclic_orders": True,
            "dihedral_comparison_base": "natural_order",
        },
        "representative_count": len(rows),
        "examined_order_count": 2 * len(rows),
        "zero_challenge_order_count": sum(
            1 for row in rows if row["challenge_certificate_count"] == 0
        ),
        "rows": rows,
        "interpretation": [
            "The natural-order counts replay the existing row-Ptolemy product-cancellation artifact for one representative of each hit family.",
            "Each challenge order is non-dihedral relative to the natural order and has zero row-Ptolemy product-cancellation certificates for the same selected rows.",
            "This demonstrates order sensitivity for the sampled representatives only; it is not an exhaustive all-order statement.",
            "The selected-distance quotient alone is not an orderless abstract-incidence obstruction.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": [dict(SOURCE_ARTIFACT)],
        "provenance": PROVENANCE,
    }
    assert_expected_counts(payload)
    return payload


def assert_expected_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected values for the order-sensitivity diagnostic."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["n"] != 9 or payload["witness_size"] != 4:
        raise AssertionError("unexpected n/witness size")
    if payload["representative_count"] != 3:
        raise AssertionError("unexpected representative count")
    if payload["examined_order_count"] != 6:
        raise AssertionError("unexpected examined order count")
    if payload["zero_challenge_order_count"] != 3:
        raise AssertionError("unexpected zero-challenge count")

    source = payload["source_fixed_order"]
    if source["hit_assignment_count"] != 26:
        raise AssertionError("unexpected source hit-assignment count")
    if source["hit_certificate_count"] != 216:
        raise AssertionError("unexpected source hit-certificate count")
    if source["hit_family_ids"] != ["F02", "F09", "F13"]:
        raise AssertionError("unexpected source hit-family ids")

    rows = payload["rows"]
    if not isinstance(rows, list):
        raise AssertionError("rows must be a list")
    if len(rows) != len(EXPECTED_REPRESENTATIVES):
        raise AssertionError("unexpected row count")
    for row, expected in zip(rows, EXPECTED_REPRESENTATIVES):
        if row["family_id"] != expected["family_id"]:
            raise AssertionError("unexpected representative family")
        if row["assignment_index"] != expected["assignment_index"]:
            raise AssertionError("unexpected representative assignment")
        if row["natural_certificate_count"] != expected["natural_certificate_count"]:
            raise AssertionError("unexpected natural certificate count")
        if row["stored_certificate_count"] != row["natural_certificate_count"]:
            raise AssertionError("stored and natural certificate counts differ")
        if row["challenge_order"] != expected["challenge_order"]:
            raise AssertionError("unexpected challenge order")
        if row["challenge_order_is_dihedral_of_natural_order"] is not False:
            raise AssertionError("challenge order should be non-dihedral")
        if row["challenge_certificate_count"] != 0:
            raise AssertionError("unexpected challenge certificate count")
        if row["certificate_count_drop"] != row["natural_certificate_count"]:
            raise AssertionError("unexpected certificate-count drop")


def validate_payload(
    payload: Any,
    *,
    source: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded order-sensitivity artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "representative_count": 3,
        "examined_order_count": 6,
        "zero_challenge_order_count": 3,
        "source_artifacts": [SOURCE_ARTIFACT],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    else:
        required = (
            "This demonstrates order sensitivity for the sampled representatives only; it is not an exhaustive all-order statement.",
            "The selected-distance quotient alone is not an orderless abstract-incidence obstruction.",
            "No proof of the n=9 case is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    try:
        assert_expected_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected counts failed: {exc}")

    if recompute:
        if source is None:
            try:
                source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load source row-Ptolemy artifact: {exc}")
                source = None
        if isinstance(source, dict):
            try:
                expected_payload = order_sensitivity_payload(source)
            except (AssertionError, TypeError, ValueError) as exc:
                errors.append(f"recomputed order-sensitivity diagnostic failed: {exc}")
            else:
                expect_equal(errors, "order-sensitivity diagnostic", payload, expected_payload)
        else:
            errors.append("source row-Ptolemy artifact must be an object")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "representative_count": object_payload.get("representative_count"),
        "examined_order_count": object_payload.get("examined_order_count"),
        "zero_challenge_order_count": object_payload.get("zero_challenge_order_count"),
        "families": [
            row.get("family_id")
            for row in object_payload.get("rows", [])
            if isinstance(row, dict)
        ],
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_ROW_PTOLEMY_ARTIFACT)
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated diagnostic")
    parser.add_argument("--check", action="store_true", help="validate an existing diagnostic")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    out = args.out if args.out.is_absolute() else ROOT / args.out

    try:
        source = load_artifact(source_path)
    except (OSError, json.JSONDecodeError) as exc:
        source = {}
        source_errors = [str(exc)]
    else:
        source_errors = validate_row_ptolemy_payload(source, recompute=False)

    if args.write:
        if source_errors:
            for error in source_errors:
                print(f"source artifact invalid: {error}", file=sys.stderr)
            return 1
        payload = order_sensitivity_payload(source)
        if args.assert_expected:
            assert_expected_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source=source,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    if source_errors:
        errors.extend(f"source artifact invalid: {error}" for error in source_errors)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy order-sensitivity diagnostic")
        print(f"artifact: {summary['artifact']}")
        print(f"representatives: {summary['representative_count']}")
        print(f"examined orders: {summary['examined_order_count']}")
        print(f"zero challenge orders: {summary['zero_challenge_order_count']}")
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy order-sensitivity checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
