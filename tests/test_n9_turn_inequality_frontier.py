from __future__ import annotations

from erdos97.n9_turn_inequality_frontier import (
    EXPECTED_TURN_INEQUALITY_COUNT,
    SIDE_CAP_BENCHMARK_PATTERN,
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
