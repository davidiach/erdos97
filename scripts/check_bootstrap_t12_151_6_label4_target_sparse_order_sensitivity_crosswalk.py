#!/usr/bin/env python3
"""Crosswalk the 151:6 natural-order blocker and alternate-order certificate.

This checker records the route decision forced by two exact local packets:

* the natural-order full-cone dual certificates prove the current 255-row
  Kalmanson/Altman family cannot certify the three target-sparse endpoint
  quotients in the natural order; and
* the alternate order [0,1,2,3,4,5,7,8,6] has exact Kalmanson zero-sum
  certificates for the same three quotients.

The conclusion is deliberately about a proof route, not about the problem:
the current row-family all-order route is not ready without a new ingredient
such as order forcing, a stronger strict-row family, or a geometric endpoint
exclusion.  This is not an n=9 proof, not a bridge proof, and not a
counterexample.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_order_"
    "sensitivity_crosswalk.v1"
)
STATUS = "EXACT_ORDER_SENSITIVITY_ROUTE_DECISION_CROSSWALK"
TRUST = "EXACT_ROUTE_PRUNING_CERTIFICATE"
TARGET_ROW_KEY = "151:6"
NATURAL_ORDER = list(range(9))
ALT_ORDER = [0, 1, 2, 3, 4, 5, 7, 8, 6]
NATURAL_DUAL_ARTIFACT = Path(
    "data/certificates/"
    "bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.json"
)
ALT_ORDER_ARTIFACT = Path(
    "data/certificates/"
    "bootstrap_t12_151_6_label4_target_sparse_alt_order_kalmanson.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.json"
)
NATURAL_DUAL_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_full_cone_"
    "dual_certificates.v1"
)
ALT_ORDER_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_alt_order_"
    "kalmanson.v1"
)
NATURAL_DUAL_STATUS = (
    "EXACT_DUAL_INFEASIBILITY_CERTIFICATES_FOR_CURRENT_FULL_CONE_SCREENS"
)
ALT_ORDER_STATUS = "EXACT_FIXED_ORDER_KALMANSON_CERTIFICATES_FOR_ALT_ORDER"
EXPECTED_ENDPOINT_ROWS = [[0, 1, 4, 6], [0, 2, 4, 6], [0, 4, 6, 7]]
EXPECTED_POTENTIAL_WEIGHT_SUMS = [250, 253, 243]
EXPECTED_ALT_CERTIFICATE_ROW_COUNTS = [10, 10, 9]
EXPECTED_ALT_CERTIFICATE_WEIGHT_SUMS = [10, 11, 10]

CLAIM_SCOPE = (
    "Exact route-decision crosswalk for the three source-151 row-6 label-4 "
    "target-sparse endpoint quotients. It combines the natural-order dual "
    "certificates, which prove the current 255-row Kalmanson/Altman family "
    "cannot produce either normalized screen in the natural order, with the "
    "alternate-order Kalmanson zero-sum certificates for fixed cyclic order "
    "[0,1,2,3,4,5,7,8,6]. This proves only order sensitivity of the current "
    "certificate route and blocks a no-new-ingredient current-row-family "
    "all-order certificate route. It does not prove an all-order obstruction, "
    "does not prove assignments 0 or 11 possible or impossible, does not prove "
    "support existence, does not prove center migration, does not prove row "
    "forcing, does not prove endpoint-8 forcing, does not prove pair [3,5] "
    "impossibility, does not prove n=9, does not prove the bootstrap bridge, "
    "does not prove Erdos #97, and is not a counterexample or global status "
    "update."
)

PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_target_sparse_"
        "order_sensitivity_crosswalk.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_target_sparse_"
        "order_sensitivity_crosswalk.py --write --assert-expected"
    ),
}


def build_payload(
    natural_dual: Mapping[str, Any] | None = None,
    alt_order: Mapping[str, Any] | None = None,
    *,
    natural_dual_path: Path = NATURAL_DUAL_ARTIFACT,
    alt_order_path: Path = ALT_ORDER_ARTIFACT,
) -> dict[str, Any]:
    """Return the deterministic order-sensitivity crosswalk payload."""

    if natural_dual is None:
        natural_dual = load_json(natural_dual_path)
    if alt_order is None:
        alt_order = load_json(alt_order_path)

    natural_summary = required_mapping(natural_dual.get("summary"), "natural summary")
    alt_summary = required_mapping(alt_order.get("summary"), "alternate-order summary")
    natural_rows = endpoint_rows_from_records(
        natural_dual.get("dual_certificate_records"),
        "natural dual records",
    )
    alt_rows = endpoint_rows_from_records(
        alt_order.get("certificate_records"),
        "alternate-order records",
    )
    if natural_rows != EXPECTED_ENDPOINT_ROWS or alt_rows != EXPECTED_ENDPOINT_ROWS:
        raise AssertionError("source endpoint rows changed")

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_miss_count": 3,
            "endpoint_rows": EXPECTED_ENDPOINT_ROWS,
            "natural_order": NATURAL_ORDER,
            "natural_order_current_row_family": natural_summary[
                "strict_row_family"
            ],
            "natural_order_current_row_family_size_each": natural_summary[
                "strict_row_count_each"
            ],
            "natural_order_zero_sum_screen_certified_infeasible": True,
            "natural_order_nonpositive_screen_certified_infeasible": True,
            "natural_order_minimum_strict_row_dot_each": natural_summary[
                "minimum_strict_row_dot_each"
            ],
            "natural_order_potential_weight_sum_each": natural_summary[
                "potential_weight_sum_each"
            ],
            "alternate_order": ALT_ORDER,
            "alternate_order_certificate_row_family": alt_summary[
                "certificate_row_family"
            ],
            "alternate_order_exact_zero_sum_certificates": True,
            "alternate_order_certificate_row_count_each": alt_summary[
                "certificate_row_count_each"
            ],
            "alternate_order_certificate_weight_sum_each": alt_summary[
                "certificate_weight_sum_each"
            ],
            "same_endpoint_rows_verified": natural_rows == alt_rows,
            "current_row_family_all_order_route_ready": False,
            "all_order_obstruction_proved": False,
            "target_sparse_obstruction_proved": False,
            "solves_n9": False,
            "solves_erdos97": False,
        },
        "route_decision": {
            "question": (
                "Can the current natural/alternate Kalmanson-Altman row-family "
                "evidence be promoted directly into an all-order certificate "
                "for the three target-sparse endpoint quotients?"
            ),
            "answer": (
                "no_not_without_new_rows_order_forcing_or_geometric_endpoint_"
                "exclusion"
            ),
            "exact_blocker": (
                "The natural-order dual certificates prove that the current "
                "255-row Kalmanson/Altman family cannot produce either a "
                "normalized zero-sum or coordinatewise-nonpositive certificate "
                "for these endpoint quotients in the natural order."
            ),
            "positive_signal": (
                "The alternate order [0,1,2,3,4,5,7,8,6] has exact "
                "Kalmanson zero-sum certificates for the same endpoint "
                "quotients, so the obstruction is strongly order-sensitive."
            ),
            "minimal_next_ingredients": [
                "prove useful cyclic-order structure from geometry",
                "add a stronger strict-row family with an exact source",
                "prove a geometric endpoint exclusion for the target-sparse lane",
                "prove center migration for the off-center [0,4,6] rows",
            ],
        },
        "source_artifacts": [
            {
                "path": natural_dual_path.as_posix(),
                "role": (
                    "natural-order exact dual infeasibility certificate for "
                    "the current row-family screens"
                ),
                "expected_schema": NATURAL_DUAL_SCHEMA,
                "expected_status": NATURAL_DUAL_STATUS,
            },
            {
                "path": alt_order_path.as_posix(),
                "role": (
                    "alternate-order exact Kalmanson zero-sum certificates "
                    "for the same endpoint quotients"
                ),
                "expected_schema": ALT_ORDER_SCHEMA,
                "expected_status": ALT_ORDER_STATUS,
            },
        ],
        "interpretation": [
            (
                "The natural-order artifact is an exact negative result about "
                "the current row-family certificate route, not a realization "
                "or counterexample."
            ),
            (
                "The alternate-order artifact is an exact positive certificate "
                "for one fixed cyclic order, not an all-order obstruction."
            ),
            (
                "Together they say the current evidence is order-sensitive: a "
                "future bridge step needs order forcing, a new strict-row "
                "source, or genuine endpoint/source geometry."
            ),
        ],
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    payload["payload_sha256"] = sha256_without_self_hash(payload)
    return payload


def validate_payload(
    payload: Mapping[str, Any],
    *,
    natural_dual_path: Path = NATURAL_DUAL_ARTIFACT,
    alt_order_path: Path = ALT_ORDER_ARTIFACT,
) -> list[str]:
    """Return validation errors for an order-sensitivity crosswalk payload."""

    errors: list[str] = []
    natural_dual = load_json(natural_dual_path)
    alt_order = load_json(alt_order_path)
    _validate_source_artifacts(natural_dual, alt_order, errors)
    generated = build_payload(
        natural_dual,
        alt_order,
        natural_dual_path=natural_dual_path,
        alt_order_path=alt_order_path,
    )
    if dict(payload) != generated:
        errors.append("stored payload differs from deterministic regeneration")
    if payload.get("payload_sha256") != sha256_without_self_hash(payload):
        errors.append("payload_sha256 mismatch")
    _validate_claim_scope(payload, errors)
    return errors


def _validate_source_artifacts(
    natural_dual: Mapping[str, Any],
    alt_order: Mapping[str, Any],
    errors: list[str],
) -> None:
    if natural_dual.get("schema") != NATURAL_DUAL_SCHEMA:
        errors.append("natural dual schema mismatch")
    if natural_dual.get("status") != NATURAL_DUAL_STATUS:
        errors.append("natural dual status mismatch")
    if alt_order.get("schema") != ALT_ORDER_SCHEMA:
        errors.append("alternate-order schema mismatch")
    if alt_order.get("status") != ALT_ORDER_STATUS:
        errors.append("alternate-order status mismatch")

    natural_summary = required_mapping(natural_dual.get("summary"), "natural summary")
    alt_summary = required_mapping(alt_order.get("summary"), "alternate summary")
    expected_natural = {
        "miss_count": 3,
        "strict_row_count_each": [255],
        "distance_class_count_each": [28],
        "minimum_strict_row_dot_each": [1, 1, 1],
        "potential_weight_sum_each": EXPECTED_POTENTIAL_WEIGHT_SUMS,
        "solves_n9": False,
        "solves_erdos97": False,
    }
    expected_alt = {
        "source_miss_count": 3,
        "certificate_count": 3,
        "fixed_cyclic_order": ALT_ORDER,
        "available_fixed_order_strict_row_count_each": [255],
        "certificate_row_count_each": EXPECTED_ALT_CERTIFICATE_ROW_COUNTS,
        "certificate_weight_sum_each": EXPECTED_ALT_CERTIFICATE_WEIGHT_SUMS,
        "all_exact_zero_sum_verified": True,
        "all_order_obstruction_proved": False,
        "solves_n9": False,
        "solves_erdos97": False,
    }
    for key, expected in expected_natural.items():
        if natural_summary.get(key) != expected:
            errors.append(f"natural summary {key} mismatch")
    for key, expected in expected_alt.items():
        if alt_summary.get(key) != expected:
            errors.append(f"alternate summary {key} mismatch")

    natural_rows = endpoint_rows_from_records(
        natural_dual.get("dual_certificate_records"),
        "natural dual records",
    )
    alt_rows = endpoint_rows_from_records(
        alt_order.get("certificate_records"),
        "alternate-order records",
    )
    if natural_rows != EXPECTED_ENDPOINT_ROWS:
        errors.append("natural endpoint rows changed")
    if alt_rows != EXPECTED_ENDPOINT_ROWS:
        errors.append("alternate endpoint rows changed")
    if natural_rows != alt_rows:
        errors.append("source artifact endpoint rows disagree")


def _validate_claim_scope(payload: Mapping[str, Any], errors: list[str]) -> None:
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
        return
    for phrase in (
        "route-decision crosswalk",
        "order sensitivity",
        "blocks a no-new-ingredient current-row-family all-order certificate route",
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


def endpoint_rows_from_records(raw: object, label: str) -> list[list[int]]:
    if not isinstance(raw, list):
        raise AssertionError(f"{label} must be a list")
    rows: list[list[int]] = []
    for record in raw:
        if not isinstance(record, Mapping):
            raise AssertionError(f"{label} entry must be an object")
        rows.append([int(item) for item in record["endpoint_row_witnesses"]])
    return rows


def required_mapping(raw: object, label: str) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise AssertionError(f"{label} must be an object")
    return raw


def load_json(path: Path) -> Mapping[str, Any]:
    resolved = resolve_repo_path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    if Path.cwd().name == "scripts":
        return Path.cwd().parent / path
    return Path.cwd() / path


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


def compact_summary(payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "source_miss_count": summary.get("source_miss_count"),
        "endpoint_rows": summary.get("endpoint_rows"),
        "natural_order_current_row_family_size_each": summary.get(
            "natural_order_current_row_family_size_each"
        ),
        "natural_order_potential_weight_sum_each": summary.get(
            "natural_order_potential_weight_sum_each"
        ),
        "alternate_order": summary.get("alternate_order"),
        "alternate_order_certificate_row_count_each": summary.get(
            "alternate_order_certificate_row_count_each"
        ),
        "current_row_family_all_order_route_ready": summary.get(
            "current_row_family_all_order_route_ready"
        ),
        "all_order_obstruction_proved": summary.get("all_order_obstruction_proved"),
        "solves_n9": summary.get("solves_n9"),
        "solves_erdos97": summary.get("solves_erdos97"),
        "validation_errors": list(errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--natural-dual", type=Path, default=NATURAL_DUAL_ARTIFACT)
    parser.add_argument("--alt-order", type=Path, default=ALT_ORDER_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write deterministic JSON artifact")
    parser.add_argument("--check", action="store_true", help="compare stored artifact to regeneration")
    parser.add_argument("--assert-expected", action="store_true", help="accepted for checker parity")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    args = parser.parse_args()

    generated = build_payload(
        natural_dual_path=args.natural_dual,
        alt_order_path=args.alt_order,
    )
    artifact = resolve_repo_path(args.artifact)
    payload: Mapping[str, Any] = generated
    if args.write:
        write_json(generated, artifact)
    if args.check:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    errors = validate_payload(
        payload,
        natural_dual_path=args.natural_dual,
        alt_order_path=args.alt_order,
    )
    summary = compact_summary(payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 target-sparse order-sensitivity crosswalk")
        print(f"endpoint rows: {summary['endpoint_rows']}")
        print(
            "natural row-family sizes: "
            f"{summary['natural_order_current_row_family_size_each']}"
        )
        print(
            "alternate-order certificate row counts: "
            f"{summary['alternate_order_certificate_row_count_each']}"
        )
        print(
            "current all-order route ready: "
            f"{summary['current_row_family_all_order_route_ready']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: order-sensitivity route decision verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
