#!/usr/bin/env python3
"""Exact fixed-order Kalmanson certificates for the 151:6 target-sparse misses.

This checker records a narrow order-sensitivity diagnostic for the three
source-151 row-6 label-4 endpoint quotients left by the target-sparse
support-cone lane.  The natural cyclic order is already route-pruned by exact
dual certificates for the current 255-row family; this overlay shows that one
fixed alternate cyclic order has tiny exact Kalmanson zero-sum certificates.

Important scope: the fixed order is part of the input.  This is not an
all-order obstruction, not a proof that assignments 0 or 11 are impossible,
not a proof of n=9, not a proof of Erdos #97, and not a counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates import (  # noqa: E402
    DEFAULT_ARTIFACT as NATURAL_DUAL_ARTIFACT,
    EXPECTED_MISSES,
    SOURCE_MISS_ARTIFACT,
    SOURCE_MISS_SCHEMA,
    SOURCE_MISS_STATUS,
    STATUS as NATURAL_DUAL_STATUS,
    TRUST as NATURAL_DUAL_TRUST,
    centered_classes_for_miss,
    distance_quotient,
    kalmanson_row,
    strict_rows,
)


SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_alt_order_"
    "kalmanson.v1"
)
STATUS = "EXACT_FIXED_ORDER_KALMANSON_CERTIFICATES_FOR_ALT_ORDER"
TRUST = "EXACT_ROUTE_PRUNING_CERTIFICATE"
TARGET_ROW_KEY = "151:6"
N = 9
ALT_ORDER = (0, 1, 2, 3, 4, 5, 7, 8, 6)
AVAILABLE_STRICT_ROW_FAMILY = (
    "kalmanson_all_quads_plus_altman_gaps_fixed_alternate_order"
)
CERTIFICATE_ROW_FAMILY = "kalmanson_rows_only_subsequence_of_fixed_alternate_order"
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.json"
)

CertificateRow = tuple[int, str, tuple[int, int, int, int]]

CERTIFICATE_ROWS_BY_ENDPOINT: Mapping[str, tuple[CertificateRow, ...]] = {
    "0,1,4,6": (
        (1, "K2_diag_gt_other", (0, 1, 5, 7)),
        (1, "K2_diag_gt_other", (0, 1, 7, 8)),
        (1, "K1_diag_gt_sides", (0, 5, 8, 6)),
        (1, "K2_diag_gt_other", (1, 3, 5, 7)),
        (1, "K2_diag_gt_other", (1, 4, 7, 8)),
        (1, "K2_diag_gt_other", (2, 3, 7, 8)),
        (1, "K2_diag_gt_other", (2, 4, 5, 7)),
        (1, "K1_diag_gt_sides", (2, 5, 7, 6)),
        (1, "K1_diag_gt_sides", (2, 7, 8, 6)),
        (1, "K2_diag_gt_other", (3, 4, 5, 8)),
    ),
    "0,2,4,6": (
        (1, "K2_diag_gt_other", (0, 2, 7, 8)),
        (1, "K2_diag_gt_other", (0, 3, 5, 7)),
        (1, "K1_diag_gt_sides", (0, 5, 8, 6)),
        (1, "K2_diag_gt_other", (1, 2, 5, 7)),
        (1, "K2_diag_gt_other", (1, 4, 7, 8)),
        (1, "K1_diag_gt_sides", (1, 5, 7, 6)),
        (1, "K1_diag_gt_sides", (1, 7, 8, 6)),
        (1, "K2_diag_gt_other", (2, 3, 5, 8)),
        (2, "K2_diag_gt_other", (3, 4, 5, 7)),
        (1, "K2_diag_gt_other", (3, 4, 7, 8)),
    ),
    "0,4,6,7": (
        (1, "K2_diag_gt_other", (0, 1, 5, 8)),
        (1, "K2_diag_gt_other", (0, 2, 7, 8)),
        (1, "K1_diag_gt_sides", (0, 5, 7, 6)),
        (2, "K1_diag_gt_sides", (0, 7, 8, 6)),
        (1, "K2_diag_gt_other", (1, 3, 7, 8)),
        (1, "K2_diag_gt_other", (1, 4, 5, 7)),
        (1, "K2_diag_gt_other", (2, 4, 7, 8)),
        (1, "K2_diag_gt_other", (3, 4, 5, 8)),
        (1, "K1_diag_gt_sides", (3, 5, 7, 6)),
    ),
}

CLAIM_SCOPE = (
    "Exact fixed-order Kalmanson zero-sum certificates for the three "
    "source-151 row-6 label-4 assignment-0 endpoint quotients left by the "
    "target-sparse full-cone miss packet. The checker fixes the alternate "
    "cyclic order [0,1,2,3,4,5,7,8,6] and verifies exact positive integer "
    "combinations of Kalmanson rows whose reduced selected-distance vectors "
    "sum to zero. This certifies obstruction only for that encoded local "
    "quotient and that one fixed cyclic order. It does not prove an all-order "
    "obstruction, does not prove the natural-order row family sufficient, does "
    "not prove assignments 0 or 11 possible or impossible, does not prove "
    "support existence, does not prove center migration, does not prove row "
    "forcing, does not prove endpoint-8 forcing, does not prove pair [3,5] "
    "impossibility, does not prove n=9, does not prove the bootstrap bridge, "
    "does not prove Erdos #97, and is not a counterexample or global status "
    "update."
)

PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_target_sparse_"
        "alt_order_kalmanson.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_target_sparse_"
        "alt_order_kalmanson.py --write --assert-expected"
    ),
}


def build_payload() -> dict[str, Any]:
    """Return the deterministic alternate-order Kalmanson certificate payload."""

    records = [verify_one_miss(miss) for miss in EXPECTED_MISSES]
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "fixed_cyclic_order": list(ALT_ORDER),
            "source_miss_count": len(records),
            "certificate_count": len(records),
            "assignment_indices": sorted(
                {int(record["assignment_index"]) for record in records}
            ),
            "endpoint_rows": [
                record["endpoint_row_witnesses"] for record in records
            ],
            "available_strict_row_family": AVAILABLE_STRICT_ROW_FAMILY,
            "available_fixed_order_strict_row_count_each": sorted(
                {
                    int(record["available_fixed_order_strict_row_count"])
                    for record in records
                }
            ),
            "certificate_row_family": CERTIFICATE_ROW_FAMILY,
            "certificate_row_count_each": [
                int(record["certificate_row_count"]) for record in records
            ],
            "certificate_weight_sum_each": [
                int(record["certificate_weight_sum"]) for record in records
            ],
            "distance_class_count_each": sorted(
                {int(record["distance_class_count"]) for record in records}
            ),
            "all_certificate_rows_in_fixed_order": all(
                bool(record["all_certificate_rows_in_fixed_order"])
                for record in records
            ),
            "all_exact_zero_sum_verified": all(
                bool(record["exact_zero_sum_check"]["zero_sum_verified"])
                for record in records
            ),
            "current_evidence_forces_target_sparse_obstruction": False,
            "all_order_obstruction_proved": False,
            "solves_n9": False,
            "solves_erdos97": False,
        },
        "proof_lemma": {
            "statement": (
                "For one fixed cyclic order, every listed Kalmanson row is a "
                "strict necessary inequality. If positive integer weights "
                "combine their reduced quotient vectors to the zero vector, "
                "then no point configuration realizing that quotient in that "
                "fixed cyclic order can exist."
            ),
            "proof": [
                (
                    "Each listed row is generated from a four-label subsequence "
                    "of the fixed cyclic order."
                ),
                (
                    "The selected-distance quotient applies only exact equality "
                    "identifications, so a zero reduced vector means the weighted "
                    "sum is the identically zero distance expression on the "
                    "quotient."
                ),
                (
                    "All weights are positive integers and every component row "
                    "is strict in the fixed cyclic order, so the same weighted "
                    "sum would have to be strictly positive."
                ),
                (
                    "The checker verifies the reduced vector sum by exact "
                    "integer arithmetic."
                ),
            ],
        },
        "source_artifacts": [
            {
                "path": SOURCE_MISS_ARTIFACT,
                "role": "source full-cone miss identities",
                "expected_schema": SOURCE_MISS_SCHEMA,
                "expected_status": SOURCE_MISS_STATUS,
            },
            {
                "path": str(NATURAL_DUAL_ARTIFACT).replace("\\", "/"),
                "role": (
                    "natural-order exact dual route-pruning comparison for "
                    "the same three endpoint quotients"
                ),
                "expected_status": NATURAL_DUAL_STATUS,
                "expected_trust": NATURAL_DUAL_TRUST,
            },
        ],
        "interpretation": [
            (
                "The natural-order full-cone lane is exactly route-pruned by "
                "separating potentials; this artifact shows the same quotient "
                "misses are obstructed outright in one alternate fixed order."
            ),
            (
                "The certificate is deliberately not an all-order certificate: "
                "cyclic orders other than [0,1,2,3,4,5,7,8,6] are unchecked here."
            ),
            (
                "The useful bridge signal is order sensitivity. Any future "
                "geometric bridge must either force useful order structure or "
                "replace this fixed-order obstruction by an all-order exact "
                "certificate."
            ),
        ],
        "certificate_records": records,
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    payload["payload_sha256"] = sha256_without_self_hash(payload)
    return payload


def verify_one_miss(miss: Mapping[str, Any]) -> dict[str, Any]:
    """Replay the fixed-order zero-sum certificate for one endpoint miss."""

    endpoint_key = str(miss["endpoint_row_key"])
    centered_classes = centered_classes_for_miss(miss)
    quotient = distance_quotient(N, centered_classes)
    available_rows = strict_rows(quotient, ALT_ORDER)
    certificate_rows = CERTIFICATE_ROWS_BY_ENDPOINT[endpoint_key]
    combined = [0] * quotient.class_count
    row_records: list[dict[str, Any]] = []

    if quotient.class_count != 28:
        raise AssertionError(
            f"{endpoint_key}: expected 28 quotient classes, got "
            f"{quotient.class_count}"
        )
    if len(available_rows) != 255:
        raise AssertionError(
            f"{endpoint_key}: expected 255 fixed-order rows, got "
            f"{len(available_rows)}"
        )

    for weight, kind, quad in certificate_rows:
        if weight <= 0:
            raise AssertionError(f"{endpoint_key}: nonpositive certificate weight")
        if not quad_in_fixed_order(quad):
            raise AssertionError(
                f"{endpoint_key}: certificate quad is not in fixed order: {quad}"
            )
        row = kalmanson_row(quotient, kind, quad)
        combined = [
            int(left) + int(weight) * int(right)
            for left, right in zip(combined, row.vector, strict=True)
        ]
        row_records.append(
            {
                "weight": int(weight),
                "source": row.source,
                "kind": kind,
                "quad": list(quad),
                "terms": [
                    {"pair": [int(a), int(b)], "coefficient": int(coefficient)}
                    for (a, b), coefficient in row.terms
                ],
                "reduced_vector": [int(value) for value in row.vector],
            }
        )

    zero_sum_verified = all(value == 0 for value in combined)
    if not zero_sum_verified:
        raise AssertionError(
            f"{endpoint_key}: certificate rows do not sum to zero: {combined!r}"
        )

    return {
        **{
            key: miss[key]
            for key in (
                "assignment_index",
                "source_pair_row_index",
                "source_core_index",
                "row_center",
                "row_witnesses",
                "endpoint_center",
                "endpoint_row_witnesses",
                "endpoint_row_key",
            )
        },
        "centered_classes": [
            {"center": int(center), "witnesses": [int(x) for x in witnesses]}
            for center, witnesses in centered_classes
        ],
        "distance_class_count": quotient.class_count,
        "fixed_cyclic_order": list(ALT_ORDER),
        "available_strict_row_family": AVAILABLE_STRICT_ROW_FAMILY,
        "available_fixed_order_strict_row_count": len(available_rows),
        "certificate_row_family": CERTIFICATE_ROW_FAMILY,
        "certificate_row_count": len(row_records),
        "certificate_weight_sum": sum(
            int(weight) for weight, _kind, _quad in certificate_rows
        ),
        "all_certificate_rows_in_fixed_order": all(
            quad_in_fixed_order(quad) for _weight, _kind, quad in certificate_rows
        ),
        "certificate_rows": row_records,
        "exact_zero_sum_check": {
            "coordinate_system": "selected-distance quotient class order",
            "combined_reduced_vector": [int(value) for value in combined],
            "zero_sum_verified": zero_sum_verified,
            "all_weights_positive": all(
                int(weight) > 0 for weight, _kind, _quad in certificate_rows
            ),
            "integer_arithmetic_only": True,
        },
        "claim_strength": (
            "Exact Kalmanson zero-sum obstruction for this encoded local "
            "quotient and this one fixed alternate cyclic order only."
        ),
    }


def quad_in_fixed_order(quad: Sequence[int]) -> bool:
    """Return whether ``quad`` is a four-label subsequence of ``ALT_ORDER``."""

    if len(quad) != 4 or len(set(quad)) != 4:
        return False
    positions = {label: index for index, label in enumerate(ALT_ORDER)}
    try:
        quad_positions = [positions[int(label)] for label in quad]
    except KeyError:
        return False
    return quad_positions == sorted(quad_positions)


def validate_payload(
    payload: Mapping[str, Any],
    *,
    source_misses_path: Path = Path(SOURCE_MISS_ARTIFACT),
    natural_dual_path: Path = NATURAL_DUAL_ARTIFACT,
) -> list[str]:
    """Return validation errors for an alternate-order certificate payload."""

    errors: list[str] = []
    generated = build_payload()
    if dict(payload) != generated:
        errors.append("stored payload differs from deterministic regeneration")
    if payload.get("payload_sha256") != sha256_without_self_hash(payload):
        errors.append("payload_sha256 mismatch")
    _validate_claim_scope(payload, errors)
    _validate_source_misses(source_misses_path, errors)
    _validate_natural_dual(natural_dual_path, errors)
    return errors


def _validate_claim_scope(payload: Mapping[str, Any], errors: list[str]) -> None:
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
        return
    for phrase in (
        "one fixed cyclic order",
        "does not prove an all-order obstruction",
        "does not prove assignments 0 or 11 possible or impossible",
        "does not prove support existence",
        "does not prove center migration",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove n=9",
        "does not prove the bootstrap bridge",
        "is not a counterexample",
        "global status update",
    ):
        if phrase not in claim_scope:
            errors.append(f"claim_scope must contain {phrase!r}")


def _validate_source_misses(source_misses_path: Path, errors: list[str]) -> None:
    path = resolve_repo_path(source_misses_path)
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"source miss artifact could not be read: {exc}")
        return
    if source.get("schema") != SOURCE_MISS_SCHEMA:
        errors.append("source miss artifact schema mismatch")
    if source.get("status") != SOURCE_MISS_STATUS:
        errors.append("source miss artifact status mismatch")
    raw_records = source.get("full_cone_probe_records")
    if not isinstance(raw_records, list):
        errors.append("source miss artifact records must be a list")
        return
    source_identities = [_miss_identity(record) for record in raw_records]
    if source_identities != list(EXPECTED_MISSES):
        errors.append("source miss artifact identities changed")


def _validate_natural_dual(natural_dual_path: Path, errors: list[str]) -> None:
    path = resolve_repo_path(natural_dual_path)
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"natural dual artifact could not be read: {exc}")
        return
    if source.get("status") != NATURAL_DUAL_STATUS:
        errors.append("natural dual artifact status mismatch")
    if source.get("trust") != NATURAL_DUAL_TRUST:
        errors.append("natural dual artifact trust mismatch")
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        errors.append("natural dual artifact summary must be an object")
        return
    expected_summary = {
        "miss_count": 3,
        "strict_row_count_each": [255],
        "distance_class_count_each": [28],
        "minimum_strict_row_dot_each": [1, 1, 1],
        "potential_weight_sum_each": [250, 253, 243],
        "solves_n9": False,
        "solves_erdos97": False,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            errors.append(
                f"natural dual summary {key} mismatch: "
                f"expected {expected!r}, got {summary.get(key)!r}"
            )


def _miss_identity(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "assignment_index": int(record["assignment_index"]),
        "source_pair_row_index": int(record["source_pair_row_index"]),
        "source_core_index": int(record["source_core_index"]),
        "row_center": int(record["row_center"]),
        "row_witnesses": [int(item) for item in record["row_witnesses"]],
        "endpoint_center": int(record["endpoint_center"]),
        "endpoint_row_witnesses": [
            int(item) for item in record["endpoint_row_witnesses"]
        ],
        "endpoint_row_key": str(record["endpoint_row_key"]),
    }


def sha256_without_self_hash(payload: Mapping[str, Any]) -> str:
    stripped = dict(payload)
    stripped.pop("payload_sha256", None)
    blob = json.dumps(stripped, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )
    return hashlib.sha256(blob).hexdigest()


def write_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    if Path.cwd().name == "scripts":
        return Path.cwd().parent / path
    return Path.cwd() / path


def compact_summary(payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "fixed_cyclic_order": summary.get("fixed_cyclic_order"),
        "source_miss_count": summary.get("source_miss_count"),
        "certificate_count": summary.get("certificate_count"),
        "endpoint_rows": summary.get("endpoint_rows"),
        "available_fixed_order_strict_row_count_each": summary.get(
            "available_fixed_order_strict_row_count_each"
        ),
        "certificate_row_count_each": summary.get("certificate_row_count_each"),
        "certificate_weight_sum_each": summary.get("certificate_weight_sum_each"),
        "all_exact_zero_sum_verified": summary.get("all_exact_zero_sum_verified"),
        "all_order_obstruction_proved": summary.get("all_order_obstruction_proved"),
        "solves_n9": summary.get("solves_n9"),
        "solves_erdos97": summary.get("solves_erdos97"),
        "validation_errors": list(errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source-misses", type=Path, default=Path(SOURCE_MISS_ARTIFACT))
    parser.add_argument("--natural-dual", type=Path, default=NATURAL_DUAL_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write deterministic JSON artifact")
    parser.add_argument("--check", action="store_true", help="compare stored artifact to regeneration")
    parser.add_argument("--assert-expected", action="store_true", help="accepted for checker parity")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    args = parser.parse_args()

    generated = build_payload()
    artifact = resolve_repo_path(args.artifact)
    payload: Mapping[str, Any] = generated
    if args.write:
        write_json(generated, artifact)
    if args.check:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    errors = validate_payload(
        payload,
        source_misses_path=args.source_misses,
        natural_dual_path=args.natural_dual,
    )
    summary = compact_summary(payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 target-sparse alternate-order Kalmanson")
        print(f"fixed cyclic order: {summary['fixed_cyclic_order']}")
        print(f"certificates: {summary['certificate_count']}")
        print(f"endpoint rows: {summary['endpoint_rows']}")
        print(f"certificate row counts: {summary['certificate_row_count_each']}")
        print(f"certificate weight sums: {summary['certificate_weight_sum_each']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: exact fixed-order Kalmanson certificates verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
