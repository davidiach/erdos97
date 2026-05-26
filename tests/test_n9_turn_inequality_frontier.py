from __future__ import annotations

from erdos97.n9_turn_inequality_frontier import (
    CLAIM_SCOPE,
    CONCLUSION,
    CYCLIC_ORDER,
    EXPECTED_TURN_INEQUALITY_COUNT,
    PROVENANCE,
    REVIEW_REQUIREMENTS,
    SIDE_CAP_BENCHMARK_PATTERN,
    STATUS,
    TRUST,
    find_turn_farkas_certificate,
    side_sensitive_pair_cap_violations,
    turn_inequality_terms_for_pattern,
    turn_z3_status,
    validate_payload,
    verify_turn_farkas_certificate,
    vertex_circle_status_for_pattern,
)


def test_side_cap_benchmark_has_expected_turn_system() -> None:
    terms = turn_inequality_terms_for_pattern(SIDE_CAP_BENCHMARK_PATTERN)

    assert len(terms) == EXPECTED_TURN_INEQUALITY_COUNT
    assert terms[0] == {
        "center": 0,
        "selected_offsets": [1, 2],
        "support": [1],
        "bound": 1,
        "orientation": "forward",
    }
    assert terms[1] == {
        "center": 0,
        "selected_offsets": [1, 2],
        "support": [2, 3, 4, 5, 6, 7, 8],
        "bound": 1,
        "orientation": "reverse",
    }


def test_side_cap_benchmark_replays_known_obstructions() -> None:
    assert side_sensitive_pair_cap_violations(SIDE_CAP_BENCHMARK_PATTERN) == []
    assert vertex_circle_status_for_pattern(SIDE_CAP_BENCHMARK_PATTERN) == "self_edge"
    assert turn_z3_status(SIDE_CAP_BENCHMARK_PATTERN) == "unsat"


def test_side_cap_benchmark_has_integer_farkas_certificate() -> None:
    certificate = find_turn_farkas_certificate(
        SIDE_CAP_BENCHMARK_PATTERN,
        assignment_index_1based=4,
    )
    summary = verify_turn_farkas_certificate(SIDE_CAP_BENCHMARK_PATTERN, certificate)

    assert certificate["assignment_index_1based"] == 4
    assert summary["deficit"] == 1
    assert summary["rhs_sum"] > 4 * summary["lambda"]
    assert summary["max_variable_coefficient"] <= summary["lambda"]


def test_payload_validation_rejects_malformed_check_payload() -> None:
    errors = validate_payload(
        {
            "schema": "erdos97.n9_turn_inequality_frontier.v1",
            "n": 9,
            "row_size": 4,
        }
    )

    assert "missing source_frontier object" in errors
    assert "missing farkas_certificates list" in errors


def test_payload_validation_guards_review_pending_claim_scope() -> None:
    errors = validate_payload(
        {
            "schema": "erdos97.n9_turn_inequality_frontier.v1",
            "status": "MACHINE_CHECKED_TURN_FRONTIER",
            "trust": "MACHINE_CHECKED_FINITE_CASE_ARTIFACT",
            "claim_scope": "Candidate n=9 proof.",
            "review_requirements": [],
            "provenance": {
                "generator": "scripts/check_n9_turn_inequality_frontier.py",
                "command": "python scripts/check_n9_turn_inequality_frontier.py",
            },
            "n": 9,
            "row_size": 4,
        }
    )

    assert "unexpected status: 'MACHINE_CHECKED_TURN_FRONTIER'" in errors
    assert "unexpected trust: 'MACHINE_CHECKED_FINITE_CASE_ARTIFACT'" in errors
    assert "claim_scope mismatch" in errors
    assert "review_requirements mismatch" in errors
    assert "provenance mismatch" in errors


def test_payload_validation_accepts_canonical_claim_scope_fields() -> None:
    assert CYCLIC_ORDER == tuple(range(9))

    errors = validate_payload(
        {
            "schema": "erdos97.n9_turn_inequality_frontier.v1",
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "cyclic_order": list(CYCLIC_ORDER),
            "conclusion": CONCLUSION,
            "review_requirements": list(REVIEW_REQUIREMENTS),
            "provenance": dict(PROVENANCE),
            "n": 9,
            "row_size": 4,
        }
    )

    assert not any(error.startswith("unexpected status:") for error in errors)
    assert not any(error.startswith("unexpected trust:") for error in errors)
    assert "claim_scope mismatch" not in errors
    assert "cyclic_order mismatch" not in errors
    assert "conclusion mismatch" not in errors
    assert "review_requirements mismatch" not in errors
    assert "provenance mismatch" not in errors
    assert "missing source_frontier object" in errors


def test_payload_validation_rejects_claim_scope_with_extra_overclaim() -> None:
    errors = validate_payload(
        {
            "schema": "erdos97.n9_turn_inequality_frontier.v1",
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE + " This establishes a counterexample.",
            "cyclic_order": list(CYCLIC_ORDER),
            "conclusion": CONCLUSION,
            "review_requirements": list(REVIEW_REQUIREMENTS),
            "provenance": dict(PROVENANCE),
            "n": 9,
            "row_size": 4,
        }
    )

    assert "claim_scope mismatch" in errors


def test_payload_validation_rejects_conclusion_and_order_drift() -> None:
    errors = validate_payload(
        {
            "schema": "erdos97.n9_turn_inequality_frontier.v1",
            "status": STATUS,
            "trust": TRUST,
            "claim_scope": CLAIM_SCOPE,
            "cyclic_order": list(reversed(CYCLIC_ORDER)),
            "conclusion": CONCLUSION + " This proves n=9.",
            "review_requirements": list(REVIEW_REQUIREMENTS),
            "provenance": dict(PROVENANCE),
            "n": 9,
            "row_size": 4,
        }
    )

    assert "cyclic_order mismatch" in errors
    assert "conclusion mismatch" in errors
