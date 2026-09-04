from __future__ import annotations

import json
import subprocess
import sys

import pytest

from erdos97.radius_level_advanced_arithmetic import (
    CLAIM_SCOPE,
    assert_expected_payload,
    component_cycle_arithmetic,
    linear_forest_angle_arithmetic,
    payload,
    triple_fanin_radius_arithmetic,
    weak_arc_cycle_arithmetic,
)


def test_weak_arc_threshold_is_g_at_least_h_plus_four() -> None:
    for length in range(3, 20):
        for weak in range(length + 1):
            case = weak_arc_cycle_arithmetic(length, weak)
            assert case.margin == length - weak - 4
            assert case.contradiction is (length >= weak + 4)

    with pytest.raises(ValueError, match="at least 3"):
        weak_arc_cycle_arithmetic(2, 0)
    with pytest.raises(ValueError, match="0..cycle_length"):
        weak_arc_cycle_arithmetic(5, 6)


def test_linear_forest_angle_and_degree_three_budgets() -> None:
    arithmetic = linear_forest_angle_arithmetic()

    assert arithmetic["two_neighbor_end_arc_total"] == "2/3"
    assert arithmetic["forced_angle_normalized_lower_bound"] == "1/6"
    assert arithmetic["forced_angle_radians"] == ">pi/3"
    assert arithmetic["degree_three_normalized_strict_lower_bound"] == ">7/6"
    assert arithmetic["degree_three_contradiction"] is True


def test_component_cycle_threshold_depends_only_on_total_path_length() -> None:
    for components in (2, 3, 10, 100):
        for path_length in range(9):
            case = component_cycle_arithmetic(components, path_length)
            assert case.lifted_cycle_length == 2 * components + path_length
            assert case.weak_arc_upper_bound == 2 * components
            assert case.worst_case_margin == path_length - 4
            assert case.contradiction is (path_length >= 4)


def test_triple_fanin_threshold_is_exact_in_q_sqrt_2() -> None:
    arithmetic = triple_fanin_radius_arithmetic()

    assert arithmetic["equivalent_asymmetric_condition"] == "x^2+y^2>1"
    assert arithmetic["positive_threshold"] == "sqrt(2)-1"
    assert arithmetic["threshold_quadratic_value"] == [0, 0]
    assert arithmetic["threshold_identity_verified"] is True
    assert arithmetic["descent_conclusion"] == "min(a,b)<(sqrt(2)-1)*R"


def test_payload_regenerates_exactly() -> None:
    candidate = payload(256)

    assert_expected_payload(candidate)
    assert candidate["claim_scope"] == CLAIM_SCOPE
    assert candidate["checked_cycle_length_range"] == [3, 256]
    assert candidate["all_weak_arc_cases_match_threshold"] is True
    assert candidate["all_component_cycle_cases_match_threshold"] is True


def test_cli_summary_is_compact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_radius_level_advanced_arithmetic.py",
            "--max-cycle-length",
            "512",
            "--assert-expected",
            "--summary-json",
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    candidate = json.loads(result.stdout)
    assert candidate["claim_scope"] == CLAIM_SCOPE
    assert candidate["checked_cycle_length_range"] == [3, 512]
    assert candidate["triple_fanin_radius_descent"][
        "threshold_identity_verified"
    ] is True
    assert "weak_arc_cases" not in candidate
    assert "component_cycle_cases" not in candidate
