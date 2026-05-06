#!/usr/bin/env python3
"""Generate or check n=9 row-Ptolemy per-family signature diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
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

from erdos97.path_display import display_path  # noqa: E402
from scripts.check_n9_row_ptolemy_product_cancellations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_ROW_PTOLEMY_ARTIFACT,
    load_artifact,
    validate_payload as validate_row_ptolemy_payload,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_family_signatures.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_family_signatures.v1"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Derived n=9 row-Ptolemy per-family certificate-signature diagnostic for "
    "the fixed natural cyclic order; not a proof of n=9, not a counterexample, "
    "not an orderless abstract-incidence obstruction, and not a global status "
    "update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_family_signatures.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_family_signatures.py "
        "--assert-expected --write"
    ),
}
EXPECTED_SOURCE_ARTIFACT = {
    "path": "data/certificates/n9_row_ptolemy_product_cancellations.json",
    "schema": "erdos97.n9_row_ptolemy_product_cancellations.v2",
    "status": "EXPLORATORY_LEDGER_ONLY",
    "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
}
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "cyclic_order",
    "family_count",
    "hit_assignment_count",
    "hit_certificate_count",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "signature_rows",
    "source_artifact",
    "status",
    "trust",
    "witness_size",
}
EXPECTED_SIGNATURE_ROWS = [
    {
        "family_id": "F02",
        "template_id": "T08",
        "template_status": "self_edge",
        "family_orbit_size": 18,
        "hit_assignment_count": 18,
        "hit_certificate_count": 108,
        "certificate_count_per_assignment": 6,
        "hit_row_count_per_assignment": 3,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"3": 18},
        "certificate_count_by_center": {str(center): 12 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 3,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 3,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 6},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 6},
        "signature_key": (
            "row_ptolemy_product|hit_rows=3|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
    },
    {
        "family_id": "F09",
        "template_id": "T01",
        "template_status": "self_edge",
        "family_orbit_size": 6,
        "hit_assignment_count": 6,
        "hit_certificate_count": 72,
        "certificate_count_per_assignment": 12,
        "hit_row_count_per_assignment": 6,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"6": 6},
        "certificate_count_by_center": {str(center): 8 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 6,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 6,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 12},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 12},
        "signature_key": (
            "row_ptolemy_product|hit_rows=6|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
    },
    {
        "family_id": "F13",
        "template_id": "T04",
        "template_status": "self_edge",
        "family_orbit_size": 2,
        "hit_assignment_count": 2,
        "hit_certificate_count": 36,
        "certificate_count_per_assignment": 18,
        "hit_row_count_per_assignment": 9,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"9": 2},
        "certificate_count_by_center": {str(center): 4 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 9,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 9,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 18},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 18},
        "signature_key": (
            "row_ptolemy_product|hit_rows=9|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
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


def _same_counter(
    errors: list[str],
    *,
    label: str,
    family_id: str,
    counters: Sequence[Counter[str] | Counter[int]],
) -> dict[str, int]:
    rows = [_json_counter(counter) for counter in counters]
    if not rows:
        errors.append(f"{label} has no rows for {family_id}")
        return {}
    first = rows[0]
    for index, row in enumerate(rows[1:], start=1):
        if row != first:
            errors.append(
                f"{label} is not stable for {family_id}: "
                f"record 0 has {first!r}, record {index} has {row!r}"
            )
    return first


def _signature_rows(
    source: dict[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    records_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in source.get("hit_records", []):
        if isinstance(record, dict) and isinstance(record.get("family_id"), str):
            records_by_family[str(record["family_id"])].append(record)

    crosswalk = source.get("template_crosswalk", {})
    crosswalk_rows = {}
    if isinstance(crosswalk, dict) and isinstance(crosswalk.get("hit_family_rows"), list):
        crosswalk_rows = {
            str(row["family_id"]): row
            for row in crosswalk["hit_family_rows"]
            if isinstance(row, dict) and "family_id" in row
        }

    rows = []
    for family_id in sorted(records_by_family):
        records = records_by_family[family_id]
        family_crosswalk = crosswalk_rows.get(family_id, {})
        certificate_count = sum(int(record["certificate_count"]) for record in records)
        certificate_counts = [int(record["certificate_count"]) for record in records]
        if len(set(certificate_counts)) != 1:
            errors.append(f"certificate count is not stable for {family_id}")

        row_count_counters = []
        variant_counters = []
        cancelled_counters = []
        zero_counters = []
        center_counter: Counter[int] = Counter()
        certificate_count_per_hit_row_values = set()
        for record in records:
            row_counter = Counter(
                int(certificate["row"])
                for certificate in record.get("certificates", [])
                if isinstance(certificate, dict)
            )
            row_count_counters.append(Counter({len(row_counter): 1}))
            variant_counters.append(
                Counter(
                    str(certificate.get("variant"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                )
            )
            cancelled_counters.append(
                Counter(
                    str(certificate.get("cancelled_product"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                )
            )
            zero_counters.append(
                Counter(
                    str(certificate.get("zero_product", {}).get("expression"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                    and isinstance(certificate.get("zero_product"), dict)
                )
            )
            center_counter.update(row_counter)
            certificate_count_per_hit_row_values.update(row_counter.values())

        row_count_distribution: Counter[int] = Counter()
        for counter in row_count_counters:
            row_count_distribution.update(counter)
        hit_row_count = next(iter(row_count_counters[0]))
        certs_per_hit_row = (
            next(iter(certificate_count_per_hit_row_values))
            if len(certificate_count_per_hit_row_values) == 1
            else None
        )
        if certs_per_hit_row is None:
            errors.append(f"certificate count per hit row is not stable for {family_id}")

        signature_key = (
            f"row_ptolemy_product|hit_rows={hit_row_count}|"
            f"certs_per_row={certs_per_hit_row}|cancelled=d01*d23|zero=d03*d12"
        )
        rows.append(
            {
                "family_id": family_id,
                "template_id": family_crosswalk.get("template_id"),
                "template_status": family_crosswalk.get("template_status"),
                "family_orbit_size": int(records[0]["family_orbit_size"]),
                "hit_assignment_count": len(records),
                "hit_certificate_count": certificate_count,
                "certificate_count_per_assignment": certificate_counts[0],
                "hit_row_count_per_assignment": int(hit_row_count),
                "certificate_count_per_hit_row": int(certs_per_hit_row or 0),
                "rows_with_certificates_per_assignment_counts": _json_counter(
                    row_count_distribution,
                ),
                "certificate_count_by_center": _json_counter(center_counter),
                "variant_counts_per_assignment": _same_counter(
                    errors,
                    label="variant_counts_per_assignment",
                    family_id=family_id,
                    counters=variant_counters,
                ),
                "cancelled_product_counts_per_assignment": _same_counter(
                    errors,
                    label="cancelled_product_counts_per_assignment",
                    family_id=family_id,
                    counters=cancelled_counters,
                ),
                "zero_product_expression_counts_per_assignment": _same_counter(
                    errors,
                    label="zero_product_expression_counts_per_assignment",
                    family_id=family_id,
                    counters=zero_counters,
                ),
                "signature_key": signature_key,
            }
        )
    return rows


def signature_payload(source: dict[str, Any]) -> dict[str, Any]:
    """Return a derived per-family signature diagnostic."""

    errors = validate_row_ptolemy_payload(source, recompute=False)
    if errors:
        raise ValueError(f"source row-Ptolemy artifact invalid: {errors[0]}")
    signature_errors: list[str] = []
    signature_rows = _signature_rows(source, signature_errors)
    if signature_errors:
        raise ValueError(f"signature derivation failed: {signature_errors[0]}")

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": source["n"],
        "witness_size": source["witness_size"],
        "cyclic_order": source["cyclic_order"],
        "family_count": len(signature_rows),
        "hit_assignment_count": sum(
            int(row["hit_assignment_count"]) for row in signature_rows
        ),
        "hit_certificate_count": sum(
            int(row["hit_certificate_count"]) for row in signature_rows
        ),
        "signature_rows": signature_rows,
        "interpretation": [
            "Rows summarize stable certificate histograms within each row-Ptolemy hit family.",
            "The signatures are prompts for local-lemma extraction, not local lemmas by themselves.",
            "Each underlying certificate remains fixed-pattern and fixed-row-order only.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifact": {
            "path": "data/certificates/n9_row_ptolemy_product_cancellations.json",
            "schema": source["schema"],
            "status": source["status"],
            "trust": source["trust"],
        },
        "provenance": PROVENANCE,
    }
    assert_expected_signature_counts(payload)
    return payload


def assert_expected_signature_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected values for the signature diagnostic."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["family_count"] != 3:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["hit_assignment_count"] != 26:
        raise AssertionError(
            f"unexpected hit assignment count: {payload['hit_assignment_count']}",
        )
    if payload["hit_certificate_count"] != 216:
        raise AssertionError(
            f"unexpected hit certificate count: {payload['hit_certificate_count']}",
        )
    if payload["signature_rows"] != EXPECTED_SIGNATURE_ROWS:
        raise AssertionError("unexpected signature rows")


def validate_payload(
    payload: Any,
    *,
    source: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded signature artifact."""

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
        "cyclic_order": list(range(9)),
        "family_count": 3,
        "hit_assignment_count": 26,
        "hit_certificate_count": 216,
        "signature_rows": EXPECTED_SIGNATURE_ROWS,
        "provenance": PROVENANCE,
        "source_artifact": EXPECTED_SOURCE_ARTIFACT,
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
            "The signatures are prompts for local-lemma extraction, not local lemmas by themselves.",
            "No proof of the n=9 case is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    try:
        assert_expected_signature_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected signature counts failed: {exc}")

    if recompute:
        if source is None:
            try:
                source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load source row-Ptolemy artifact: {exc}")
                source = None
        if isinstance(source, dict):
            try:
                expected_payload = signature_payload(source)
            except (TypeError, ValueError) as exc:
                errors.append(f"recomputed signature diagnostic failed: {exc}")
            else:
                expect_equal(errors, "signature diagnostic", payload, expected_payload)
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
        "family_count": object_payload.get("family_count"),
        "hit_assignment_count": object_payload.get("hit_assignment_count"),
        "hit_certificate_count": object_payload.get("hit_certificate_count"),
        "signature_keys": [
            row.get("signature_key")
            for row in object_payload.get("signature_rows", [])
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
        payload = signature_payload(source)
        if args.assert_expected:
            assert_expected_signature_counts(payload)
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
        print("n=9 row-Ptolemy family-signature diagnostic")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"hit assignments: {summary['hit_assignment_count']}")
        print(f"hit certificates: {summary['hit_certificate_count']}")
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy family-signature checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
