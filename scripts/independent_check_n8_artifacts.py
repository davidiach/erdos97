#!/usr/bin/env python3
"""Audit the checked-in n=8 finite-case artifacts as input data.

This script is a proof-hygiene entrypoint for independent review.  It does not
regenerate the full incidence enumeration and does not turn the repo-local
machine-checked result into a public theorem claim.  Instead it checks that the
checked-in survivor, completeness, compatible-order, and exact-analysis
artifacts agree with each other and with exact obstruction verifiers that do
not import the main ``erdos97.n8_incidence`` generator.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import analyze_n8_exact_survivors as exact
import independent_check_n8_incidence_json as incidence


EXPECTED_COMPLETENESS_COUNTS = {
    "balanced_cap_matrices_with_row0_fixed": 117072,
    "forced_perpendicular_survivors_with_row0_fixed": 4560,
    "canonical_survivor_class_count": 15,
    "existing_reconstructed_survivor_count": 15,
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def row_strings(rows: list[list[int]]) -> list[str]:
    return ["".join(str(value) for value in row) for row in rows]


def json_load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def survivor_canonical_keys(records: list[dict[str, Any]]) -> set[tuple[int, ...]]:
    keys: set[tuple[int, ...]] = set()
    for record in records:
        _rows, canonical, errors = incidence.validate_incidence_record(record)
        if errors:
            continue
        assert canonical is not None
        keys.add(canonical)
    return keys


def check_completeness_artifact(path: Path, survivor_path: Path) -> dict[str, Any]:
    data = json_load(path)
    survivors = json_load(survivor_path)
    errors: list[str] = []

    if not isinstance(data, dict):
        return {
            "path": str(path),
            "verified": False,
            "errors": ["top-level completeness artifact should be an object"],
        }
    if data.get("n") != incidence.N:
        errors.append(f"n is {data.get('n')!r}, expected {incidence.N}")
    if data.get("status") != "INCIDENCE_COMPLETENESS":
        errors.append(f"status is {data.get('status')!r}, expected INCIDENCE_COMPLETENESS")
    for key, expected in EXPECTED_COMPLETENESS_COUNTS.items():
        if data.get(key) != expected:
            errors.append(f"{key} is {data.get(key)!r}, expected {expected}")
    if data.get("matches_existing_reconstructed_survivors") is not True:
        errors.append("matches_existing_reconstructed_survivors is not true")

    symmetry_break = data.get("symmetry_break", {})
    if symmetry_break.get("row") != 0 or symmetry_break.get("witnesses") != [1, 2, 3, 4]:
        errors.append("symmetry_break should fix row 0 to witnesses [1, 2, 3, 4]")

    column_sum_derivation = data.get("column_sum_derivation", {})
    if column_sum_derivation.get("forced_indegrees") != [4] * incidence.N:
        errors.append("column_sum_derivation does not record all indegrees forced to 4")

    classes = data.get("canonical_survivor_classes")
    if not isinstance(classes, list):
        errors.append("canonical_survivor_classes should be a list")
        classes = []

    ids: list[int] = []
    completion_records: list[dict[str, Any]] = []
    for item in classes:
        if not isinstance(item, dict):
            errors.append("canonical_survivor_classes entries should be objects")
            continue
        class_id = item.get("canonical_id")
        rows = item.get("rows")
        if not isinstance(class_id, int):
            errors.append(f"canonical_id is {class_id!r}, expected integer")
            continue
        ids.append(class_id)
        if not isinstance(rows, list):
            errors.append(f"class {class_id}: rows should be a matrix")
            continue
        if item.get("row_strings") != row_strings(rows):
            errors.append(f"class {class_id}: row_strings do not match rows")
        record = {"id": class_id, "rows": rows}
        completion_records.append(record)
        _rows, _canonical, record_errors = incidence.validate_incidence_record(record)
        errors.extend(f"completeness {error}" for error in record_errors)

    if sorted(ids) != list(range(len(ids))):
        errors.append(f"canonical ids are {sorted(ids)}, expected contiguous 0..{len(ids) - 1}")

    survivor_keys = survivor_canonical_keys(survivors)
    completeness_keys = survivor_canonical_keys(completion_records)
    if survivor_keys != completeness_keys:
        errors.append("canonical classes differ between completeness and survivor artifacts")

    return {
        "path": str(path),
        "verified": not errors,
        "canonical_class_count": len(completeness_keys),
        "checked_conditions": [
            "schema and fixed n=8 status metadata",
            "recorded finite-enumeration counts match the checked artifact values",
            "row strings agree with matrices",
            "each stored class is independently incidence-valid and brute-force canonical",
            "canonical class set matches n8_reconstructed_15_survivors.json",
        ],
        "errors": errors,
        "status": (
            "artifact_alignment_check_not_independent_completeness_enumeration"
        ),
    }


def check_exact_obstruction_artifacts(
    survivor_path: Path,
    compatible_orders_path: Path,
    exact_analysis_path: Path,
) -> dict[str, Any]:
    survivors = json_load(survivor_path)
    counts = exact.check_cyclic_counts(survivors)
    killed = sorted(k for k, v in counts.items() if v == 0)
    y2_span = exact.check_y2_span(survivors)
    class14 = exact.check_class14_certificate(survivors)
    compatible_orders_check = {
        "path": str(compatible_orders_path),
        "verified": json_load(compatible_orders_path) == exact.compatible_orders_artifact(survivors),
    }
    exact_analysis_check = exact.check_exact_analysis_artifact(
        survivors,
        exact_analysis_path,
        counts,
    )

    certificates = {
        "cyclic_order_noncrossing_killed_ids": killed,
        "pb_y2_span_killed_ids": sorted(k for k, ok in y2_span.items() if ok),
        "class3_duplicate_vertex": exact.check_class3_duplicate_certificate(survivors),
        "class4_collinearity": exact.check_class4_collinearity_certificate(survivors),
        "class5_groebner_contradiction": exact.check_class5_groebner(survivors),
        "class14_pb_ed_groebner_basis": class14["groebner_basis_verified"],
        "class14_solution_branches": class14["branches_solve_pb_ed"],
        "class14_strict_interior": class14["all_branches_have_four_hull_vertices"],
    }
    all_killed = sorted(
        set(certificates["cyclic_order_noncrossing_killed_ids"])
        | set(certificates["pb_y2_span_killed_ids"])
        | ({3} if certificates["class3_duplicate_vertex"] else set())
        | ({4} if certificates["class4_collinearity"] else set())
        | ({5} if certificates["class5_groebner_contradiction"] else set())
        | ({14} if all(class14.values()) else set())
    )
    expected_ids = list(range(len(survivors)))
    errors: list[str] = []
    if counts != exact.EXPECTED_COMPATIBLE_COUNTS:
        errors.append("compatible cyclic-order counts do not match expected fingerprints")
    if set(certificates["pb_y2_span_killed_ids"]) != exact.Y2_SPAN_CLASS_IDS:
        errors.append("PB y2-span certificate ids do not match expected fingerprints")
    if all_killed != expected_ids:
        errors.append(f"exact certificates kill ids {all_killed}, expected {expected_ids}")
    if not compatible_orders_check["verified"]:
        errors.append("compatible-order artifact does not match regenerated exact data")
    if not exact_analysis_check["verified"]:
        errors.append("exact-analysis artifact does not match regenerated exact data")

    return {
        "verified": not errors,
        "cyclic_order_compatible_counts": counts,
        "certificates": certificates,
        "all_reconstructed_15_rejected": all_killed == expected_ids,
        "compatible_orders_artifact": compatible_orders_check,
        "exact_analysis_artifact": exact_analysis_check,
        "checked_conditions": [
            "cyclic-order noncrossing counts",
            "rational PB linear-span certificates",
            "class 3 duplicate-vertex certificate",
            "class 4 collinearity certificate",
            "class 5 Groebner contradiction",
            "class 14 PB+ED Groebner basis and strict-interior branches",
            "checked-in compatible-order and exact-analysis artifacts",
        ],
        "errors": errors,
        "status": "exact_obstruction_artifact_check_pending_external_review",
    }


def check_all(root: Path) -> dict[str, Any]:
    survivor_path = root / "data" / "incidence" / "n8_reconstructed_15_survivors.json"
    completeness_path = root / "data" / "incidence" / "n8_incidence_completeness.json"
    compatible_orders_path = root / "data" / "incidence" / "n8_compatible_orders.json"
    exact_analysis_path = root / "certificates" / "n8_exact_analysis.json"

    survivor_check = incidence.check_file(survivor_path)
    completeness_check = check_completeness_artifact(completeness_path, survivor_path)
    exact_check = check_exact_obstruction_artifacts(
        survivor_path,
        compatible_orders_path,
        exact_analysis_path,
    )
    verified = (
        bool(survivor_check["verified"])
        and bool(completeness_check["verified"])
        and bool(exact_check["verified"])
    )
    return {
        "verified": verified,
        "survivor_json": survivor_check,
        "completeness_artifact": completeness_check,
        "exact_obstruction_artifacts": exact_check,
        "overall_status": (
            "n8_artifacts_verified_repo_local_pending_external_review"
            if verified
            else "n8_artifact_audit_failed_or_uncertain"
        ),
        "claim_scope": (
            "Checks checked-in artifacts and exact obstruction certificates; "
            "does not claim a general proof of Erdos Problem #97 or a "
            "standalone public theorem."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--check", action="store_true", help="fail if any audit step fails")
    args = parser.parse_args()

    summary = check_all(repo_root())
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif summary["verified"]:
        print("verified n=8 checked-in artifacts and exact obstruction certificates")
    else:
        print("n=8 artifact audit failed or found uncertainty")
        for section in ["survivor_json", "completeness_artifact", "exact_obstruction_artifacts"]:
            for error in summary[section].get("errors", []):
                print(f"- {section}: {error}")

    if args.check and not summary["verified"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
