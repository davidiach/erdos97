#!/usr/bin/env python3
"""Check that legacy open GitHub issues are covered by scoped artifacts.

This is issue-triage bookkeeping only. It does not change the mathematical
status of Erdos Problem #97 and does not claim a counterexample.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.interval_verify import verify_interval_json  # noqa: E402

SCHEMA = "erdos97.open_issue_resolution_crosswalk.v1"
STATUS = "ISSUE_ACCEPTANCE_CROSSWALK_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Repository issue-resolution crosswalk for GitHub issues #5, #81, #82, "
    "and #83. It verifies that each issue's acceptance criteria are represented "
    "by existing scoped artifacts or checkers. It is not a proof of Erdos "
    "Problem #97, not a counterexample, and not a global status update."
)
EXPECTED_ISSUES = (5, 81, 82, 83)
PROVENANCE = {
    "generator": "scripts/check_open_issue_resolution_crosswalk.py",
    "command": "python scripts/check_open_issue_resolution_crosswalk.py --assert-expected --json",
}


def display_path(path: Path) -> str:
    """Return a stable repository-relative display path."""

    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def repo_path(raw_path: str) -> Path:
    """Return an absolute path under the repository root."""

    path = Path(raw_path)
    return path if path.is_absolute() else ROOT / path


def load_json(raw_path: str) -> Any:
    """Load a JSON file from a repository-relative path."""

    return json.loads(repo_path(raw_path).read_text(encoding="utf-8"))


def dotted_get(payload: Any, dotted_key: str) -> Any:
    """Read a dotted key path from nested JSON objects."""

    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, Mapping) or part not in current:
            raise KeyError(dotted_key)
        current = current[part]
    return current


def optional_dotted_get(payload: Any, dotted_key: str) -> Any:
    """Read a dotted key path, returning None when it is missing."""

    try:
        return dotted_get(payload, dotted_key)
    except KeyError:
        return None


def expect_equal(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    """Append a compact validation error when values differ."""

    if actual != expected:
        errors.append(f"{label} expected {expected!r}, got {actual!r}")


def expect_dotted_equal(
    errors: list[str],
    label: str,
    payload: Any,
    dotted_key: str,
    expected: Any,
) -> None:
    """Append a validation error when a dotted JSON value is missing or changed."""

    try:
        actual = dotted_get(payload, dotted_key)
    except KeyError:
        errors.append(f"{label} missing {dotted_key!r}")
        return
    expect_equal(errors, label, actual, expected)


def check_required_paths(paths: Sequence[str]) -> list[str]:
    """Return missing-path errors for repository-relative paths."""

    errors = []
    for raw_path in paths:
        if not repo_path(raw_path).exists():
            errors.append(f"missing required path: {raw_path}")
    return errors


def issue_row(
    *,
    number: int,
    title: str,
    acceptance_status: str,
    safe_closure_recommendation: bool,
    required_paths: Sequence[str],
    evidence: Mapping[str, Any],
    validation_errors: Sequence[str],
    claim_boundary: str,
) -> dict[str, Any]:
    """Return one issue crosswalk row."""

    all_errors = [*check_required_paths(required_paths), *validation_errors]
    return {
        "issue_number": number,
        "issue_url": f"https://github.com/davidiach/erdos97/issues/{number}",
        "title": title,
        "acceptance_status": acceptance_status,
        "safe_closure_recommendation": safe_closure_recommendation,
        "ok": not all_errors,
        "required_paths": list(required_paths),
        "evidence": dict(evidence),
        "claim_boundary": claim_boundary,
        "validation_errors": all_errors,
    }


def interval_issue_row() -> dict[str, Any]:
    """Return the #5 interval-verifier issue row."""

    required = (
        "src/erdos97/interval_verify.py",
        "scripts/interval_verify_candidate.py",
        "tests/test_interval_verify.py",
        "data/runs/best_B12_slsqp_m1e-6.json",
    )
    result = verify_interval_json(ROOT / "data" / "runs" / "best_B12_slsqp_m1e-6.json")
    errors: list[str] = []
    expect_equal(errors, "#5 ok", result.get("ok"), False)
    expect_equal(errors, "#5 failure_mode", result.get("failure_mode"), "floating_near_miss")
    expect_equal(errors, "#5 convexity_certified", result.get("convexity_certified"), True)
    expect_equal(
        errors,
        "#5 distance_equalities_certified",
        result.get("distance_equalities_certified"),
        False,
    )
    expect_equal(
        errors,
        "#5 claim_strength",
        result.get("claim_strength"),
        "NUMERICAL_EVIDENCE_OR_NEAR_MISS_NOT_A_COUNTEREXAMPLE",
    )
    return issue_row(
        number=5,
        title="Add interval-arithmetic verifier for convexity and distance equations",
        acceptance_status="satisfied_by_interval_checker_and_negative_b12_guard",
        safe_closure_recommendation=True,
        required_paths=required,
        evidence={
            "b12_failure_mode": result.get("failure_mode"),
            "convexity_certified": result.get("convexity_certified"),
            "distance_equalities_certified": result.get("distance_equalities_certified"),
            "claim_strength": result.get("claim_strength"),
            "definite_nonzero_residuals": dotted_get(
                result,
                "residual_bounds.definite_nonzero_residuals",
            ),
        },
        validation_errors=errors,
        claim_boundary=(
            "The verifier rejects the saved B12 floating near-miss as a "
            "counterexample. It is not a proof, and it does not certify exact "
            "equality from floating residuals."
        ),
    )


def c13_issue_row() -> dict[str, Any]:
    """Return the #81 C13 cyclic-order CSP issue row."""

    required = (
        "scripts/check_kalmanson_two_order_search.py",
        "data/certificates/c13_sidon_all_orders_kalmanson_two_search.json",
        "docs/kalmanson-two-order-search.md",
        "docs/c13-kalmanson-order-pilot.md",
        "tests/test_kalmanson_two_order_search.py",
    )
    artifact = load_json("data/certificates/c13_sidon_all_orders_kalmanson_two_search.json")
    expected = {
        "type": "kalmanson_two_inverse_pair_order_search_v1",
        "status": "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
        "trust": "EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
        "pattern.name": "C13_sidon_1_2_4_10",
        "pattern.n": 13,
        "nodes_visited": 1_496_677,
        "branches_pruned_by_completed_two_certificate": 6_192_576,
        "survivor_order": None,
    }
    errors: list[str] = []
    for key, value in expected.items():
        expect_dotted_equal(errors, f"#81 {key}", artifact, key, value)
    return issue_row(
        number=81,
        title="Pilot Kalmanson cyclic-order CSP on C13",
        acceptance_status="satisfied_by_all_order_c13_fixed_pattern_artifact",
        safe_closure_recommendation=True,
        required_paths=required,
        evidence={
            "status": artifact.get("status"),
            "trust": artifact.get("trust"),
            "nodes_visited": artifact.get("nodes_visited"),
            "branches_pruned_by_completed_two_certificate": artifact.get(
                "branches_pruned_by_completed_two_certificate"
            ),
            "survivor_order": artifact.get("survivor_order"),
        },
        validation_errors=errors,
        claim_boundary=(
            "The obstruction is all-order only for the fixed abstract "
            "C13_sidon_1_2_4_10 selected-witness pattern and does not transfer "
            "to C19 or to Erdos Problem #97. It is not a proof of the global "
            "problem."
        ),
    )


def n9_low_excess_issue_row() -> dict[str, Any]:
    """Return the #82 n=9 low-excess ledger issue row."""

    required = (
        "scripts/check_n9_base_apex_low_excess_ledgers.py",
        "scripts/check_n9_base_apex_low_excess_escape_crosswalk.py",
        "scripts/check_n9_base_apex_d3_artifact_join.py",
        "data/certificates/n9_base_apex_low_excess_ledgers.json",
        "data/certificates/n9_base_apex_low_excess_escape_crosswalk.json",
        "data/certificates/n9_base_apex_d3_escape_slice.json",
        "data/certificates/n9_base_apex_d3_escape_frontier_packet.json",
        "data/certificates/n9_base_apex_d3_p19_incidence_capacity_pilot.json",
        "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json",
        "docs/n9-base-apex-frontier.md",
    )
    ledgers = load_json("data/certificates/n9_base_apex_low_excess_ledgers.json")
    crosswalk = load_json("data/certificates/n9_base_apex_low_excess_escape_crosswalk.json")
    d3_slice = load_json("data/certificates/n9_base_apex_d3_escape_slice.json")
    d3_packet = load_json("data/certificates/n9_base_apex_d3_escape_frontier_packet.json")
    incidence_packet = load_json("data/certificates/n9_base_apex_d3_incidence_capacity_packet.json")
    expected = {
        "ledgers.schema": (
            ledgers,
            "erdos97.n9_base_apex_low_excess_ledgers.v1",
        ),
        "ledgers.status": (ledgers, "EXPLORATORY_LEDGER_ONLY"),
        "ledgers.trust": (ledgers, TRUST),
        "ledgers.strict_unresolved_profile_ledger_count": (ledgers, 30),
        "ledgers.strict_turn_cover_summary.forced_by_turn_cover_count": (ledgers, 65),
        "ledgers.strict_turn_cover_summary.unresolved_by_turn_cover_count": (ledgers, 30),
        "ledgers.strict_turn_cover_summary.minimum_capacity_deficit_to_escape": (ledgers, 3),
        "crosswalk.schema": (
            crosswalk,
            "erdos97.n9_base_apex_low_excess_escape_crosswalk.v1",
        ),
        "crosswalk.matrix_summary.profile_ledger_count": (crosswalk, 30),
        "crosswalk.matrix_summary.escape_class_count": (crosswalk, 8),
        "crosswalk.matrix_summary.total_common_dihedral_pair_class_count": (
            crosswalk,
            30_184,
        ),
        "d3_slice.profile_slice.labelled_profile_sequence_count": (d3_slice, 3_003),
        "d3_slice.escape_slice.labelled_escape_placement_count": (d3_slice, 108),
        "d3_slice.coupled_slice.common_dihedral_pair_class_count": (d3_slice, 18_088),
        "d3_packet.representative_count": (d3_packet, 88),
        "incidence_packet.incidence_state": (incidence_packet, "UNKNOWN"),
        "incidence_packet.representative_count": (incidence_packet, 88),
    }
    errors: list[str] = []
    for label, (payload, expected_value) in expected.items():
        dotted_key = label.split(".", 1)[1]
        expect_dotted_equal(errors, f"#82 {label}", payload, dotted_key, expected_value)
    return issue_row(
        number=82,
        title="Attack n=9 base-apex low-excess ledgers",
        acceptance_status="satisfied_as_bookkeeping_attack_with_remaining_unknowns_explicit",
        safe_closure_recommendation=True,
        required_paths=required,
        evidence={
            "strict_unresolved_profile_ledger_count": ledgers.get(
                "strict_unresolved_profile_ledger_count"
            ),
            "strict_unresolved_count_by_total_profile_excess": ledgers.get(
                "strict_unresolved_count_by_total_profile_excess"
            ),
            "low_excess_crosswalk_common_dihedral_pair_class_count": optional_dotted_get(
                crosswalk,
                "matrix_summary.total_common_dihedral_pair_class_count",
            ),
            "d3_common_dihedral_pair_class_count": optional_dotted_get(
                d3_slice,
                "coupled_slice.common_dihedral_pair_class_count",
            ),
            "d3_packet_representative_count": d3_packet.get("representative_count"),
            "incidence_state": incidence_packet.get("incidence_state"),
        },
        validation_errors=errors,
        claim_boundary=(
            "The low-excess ledgers and D=3 packets enumerate remaining "
            "bookkeeping targets and leave realizability/incidence states "
            "UNKNOWN; they are not a proof of n=9."
        ),
    )


def c19_issue_row() -> dict[str, Any]:
    """Return the #83 C19 certificate-decomposition issue row."""

    required = (
        "scripts/analyze_kalmanson_certificates.py",
        "scripts/analyze_kalmanson_inverse_pair_templates.py",
        "scripts/check_kalmanson_two_order_z3.py",
        "reports/kalmanson_certificate_diagnostics.json",
        "reports/c19_kalmanson_compact_vs_legacy.json",
        "reports/c19_kalmanson_z3_clause_diagnostics.json",
        "data/certificates/round2/c19_kalmanson_known_order_unsat.json",
        "data/certificates/round2/c19_kalmanson_known_order_two_unsat.json",
        "data/certificates/c19_skew_all_orders_kalmanson_z3.json",
        "docs/kalmanson-certificate-diagnostics.md",
        "docs/kalmanson-two-order-search.md",
    )
    diagnostics = load_json("reports/kalmanson_certificate_diagnostics.json")
    comparison = load_json("reports/c19_kalmanson_compact_vs_legacy.json")
    z3 = load_json("data/certificates/c19_skew_all_orders_kalmanson_z3.json")
    z3_diagnostic = load_json("reports/c19_kalmanson_z3_clause_diagnostics.json")
    by_pattern = {
        str(row["pattern"]): row
        for row in diagnostics.get("certificates", [])
        if isinstance(row, Mapping)
    }
    c19_diagnostic = by_pattern.get("C19_skew", {})
    errors: list[str] = []
    if not c19_diagnostic:
        errors.append("#83 diagnostics missing C19_skew row")
    expected = {
        "diagnostics.type": (diagnostics, "kalmanson_certificate_diagnostics_v1"),
        "diagnostics.trust": (diagnostics, "EXACT_CERTIFICATE_DIAGNOSTIC"),
        "c19_diagnostic.positive_inequalities": (c19_diagnostic, 94),
        "c19_diagnostic.distance_classes_after_selected_equalities": (
            c19_diagnostic,
            114,
        ),
        "c19_diagnostic.max_abs_weighted_sum_coefficient": (
            c19_diagnostic,
            0,
        ),
        "comparison.type": (comparison, "c19_kalmanson_compact_vs_legacy_diagnostic_v1"),
        "comparison.status": (comparison, "FIXED_ORDER_CERTIFICATE_COMPARISON_ONLY"),
        "comparison.comparison.legacy_inequality_count": (comparison, 94),
        "comparison.comparison.compact_inequality_count": (comparison, 2),
        "comparison.comparison.support_signature_overlap_count": (comparison, 0),
        "z3.status": (z3, "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION"),
        "z3.trust": (z3, "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN"),
        "z3.solver_result": (z3, "unsat"),
        "z3.forbidden_clause_count": (z3, 7_981),
        "z3_diagnostic.status": (z3_diagnostic, "ALL_ORDER_C19_Z3_CLAUSE_DIAGNOSTIC_ONLY"),
        "z3_diagnostic.template_summary.clause_count": (z3_diagnostic, 7_981),
        "z3_diagnostic.clause_validation_summary.solver_replay_result": (
            z3_diagnostic,
            "unsat",
        ),
    }
    for label, (payload, expected_value) in expected.items():
        dotted_key = label.split(".", 1)[1]
        expect_dotted_equal(errors, f"#83 {label}", payload, dotted_key, expected_value)
    return issue_row(
        number=83,
        title="Decompose C19 Kalmanson certificate and plan abstract-order search",
        acceptance_status="satisfied_by_fixed_order_decomposition_and_all_order_guardrails",
        safe_closure_recommendation=True,
        required_paths=required,
        evidence={
            "legacy_inequality_count": optional_dotted_get(
                comparison,
                "comparison.legacy_inequality_count",
            ),
            "compact_inequality_count": optional_dotted_get(
                comparison,
                "comparison.compact_inequality_count",
            ),
            "support_signature_overlap_count": optional_dotted_get(
                comparison,
                "comparison.support_signature_overlap_count",
            ),
            "all_order_c19_z3_solver_result": z3.get("solver_result"),
            "all_order_c19_z3_forbidden_clause_count": z3.get(
                "forbidden_clause_count"
            ),
            "z3_clause_diagnostic_status": z3_diagnostic.get("status"),
        },
        validation_errors=errors,
        claim_boundary=(
            "The compact-vs-legacy decomposition is fixed-order support "
            "diagnostic work. The all-order C19 statement is separate and "
            "limited to one fixed abstract selected-witness pattern; it is not "
            "a proof of Erdos Problem #97."
        ),
    )


def crosswalk_payload() -> dict[str, Any]:
    """Return the deterministic issue-resolution crosswalk payload."""

    issues = [
        interval_issue_row(),
        c13_issue_row(),
        n9_low_excess_issue_row(),
        c19_issue_row(),
    ]
    validation_errors = [
        f"issue #{issue['issue_number']}: {error}"
        for issue in issues
        for error in issue["validation_errors"]
    ]
    recommended = [
        int(issue["issue_number"])
        for issue in issues
        if issue["ok"] and issue["safe_closure_recommendation"]
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "issue_count": len(issues),
        "issue_numbers": [int(issue["issue_number"]) for issue in issues],
        "safe_closure_recommendation_issue_numbers": recommended,
        "issues": issues,
        "validation_errors": validation_errors,
        "ok": not validation_errors and recommended == list(EXPECTED_ISSUES),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Issue closure is recommended only for the scoped engineering/research acceptance criteria listed here.",
            "The official/global status remains open unless manually rechecked and updated from the official source.",
        ],
        "provenance": dict(PROVENANCE),
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    """Assert the pinned crosswalk values."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "issue_count": 4,
        "issue_numbers": list(EXPECTED_ISSUES),
        "safe_closure_recommendation_issue_numbers": list(EXPECTED_ISSUES),
        "validation_errors": [],
        "ok": True,
        "provenance": PROVENANCE,
    }
    for key, expected in expected_top.items():
        expect_equal_or_raise(key, payload.get(key), expected)
    issues = payload.get("issues")
    if not isinstance(issues, list) or len(issues) != len(EXPECTED_ISSUES):
        raise AssertionError("issues must be the expected four-row list")
    by_number = {
        int(issue["issue_number"]): issue
        for issue in issues
        if isinstance(issue, Mapping)
    }
    if tuple(sorted(by_number)) != EXPECTED_ISSUES:
        raise AssertionError(f"issue rows changed: {sorted(by_number)}")
    for number in EXPECTED_ISSUES:
        issue = by_number[number]
        expect_equal_or_raise(f"issue #{number} ok", issue.get("ok"), True)
        expect_equal_or_raise(
            f"issue #{number} safe_closure_recommendation",
            issue.get("safe_closure_recommendation"),
            True,
        )
        claim_boundary = str(issue.get("claim_boundary", ""))
        for phrase in ("not", "proof"):
            if phrase not in claim_boundary.lower():
                raise AssertionError(
                    f"issue #{number} claim boundary is not conservative enough"
                )


def expect_equal_or_raise(label: str, actual: Any, expected: Any) -> None:
    """Raise an AssertionError for mismatched values."""

    if actual != expected:
        raise AssertionError(f"{label} expected {expected!r}, got {actual!r}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    payload = crosswalk_payload()
    if args.assert_expected:
        assert_expected(payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Open issue resolution crosswalk")
        for issue in payload["issues"]:
            status = "OK" if issue["ok"] else "FAILED"
            print(f"#{issue['issue_number']}: {status} - {issue['acceptance_status']}")
        if args.assert_expected:
            print("OK: issue resolution crosswalk matches expected scoped artifacts")
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
