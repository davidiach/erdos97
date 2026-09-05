from __future__ import annotations

import json
import subprocess
import sys

import pytest

from erdos97.sparse_minimum_distance_forest import (
    CLAIM_SCOPE,
    arithmetic_payload,
    assert_expected_payload,
    export_arithmetic,
    fan_in_arithmetic,
    long_cycle_arithmetic,
    one_defect_cycle_arithmetic,
    triangle_turn_arithmetic,
)


def test_long_cycle_margin_is_exact_for_unbounded_formula() -> None:
    for length in (4, 5, 6, 17, 128, 10_000):
        case = long_cycle_arithmetic(length)
        assert case.cycle_tour_coefficient == length
        assert case.perimeter_lower_coefficient == 2 * (length - 2)
        assert case.margin == length - 4
        assert case.contradiction is True


def test_long_cycle_arithmetic_rejects_triangle_input() -> None:
    with pytest.raises(ValueError, match="cycle_length >= 4"):
        long_cycle_arithmetic(3)


def test_one_defect_return_threshold_is_six() -> None:
    for length in range(3, 6):
        case = one_defect_cycle_arithmetic(length)
        assert case.margin == length - 6
        assert case.contradiction is False
    for length in (6, 7, 20, 10_000):
        case = one_defect_cycle_arithmetic(length)
        assert case.perimeter_lower_coefficient == 2 * length - 6
        assert case.margin == length - 6
        assert case.contradiction is True
    with pytest.raises(ValueError, match="cycle_length >= 3"):
        one_defect_cycle_arithmetic(2)


def test_triangle_turn_budget_is_exact() -> None:
    triangle = triangle_turn_arithmetic()

    assert triangle["minimum_boundary_detour_multiple"] == 2
    assert triangle["normalized_turn_lower_per_arc"] == "1/3"
    assert triangle["normalized_internal_turn_lower_sum"] == "1"
    assert triangle["normalized_internal_turn_strict_upper_bound"] == "<1"
    assert triangle["contradiction"] is True


def test_common_target_fan_in_threshold_is_four() -> None:
    assert fan_in_arithmetic(3).contradiction is False
    assert fan_in_arithmetic(3).normalized_strict_lower_bound == ">1/2"
    assert fan_in_arithmetic(4).contradiction is True
    assert fan_in_arithmetic(4).normalized_strict_lower_bound == ">1"
    assert fan_in_arithmetic(100).contradiction is True
    with pytest.raises(ValueError, match="positive"):
        fan_in_arithmetic(0)


def test_forest_export_formula_and_target_rounding() -> None:
    threshold = export_arithmetic(10, 3)
    assert threshold.maximum_forest_edges == 7
    assert threshold.maximum_internal_incidences == 14
    assert threshold.minimum_external_incidences == 6
    assert threshold.minimum_distinct_external_targets == 2

    richer = export_arithmetic(10, 3, 4)
    assert richer.minimum_external_incidences == 26
    assert richer.minimum_distinct_external_targets == 9

    rounded = export_arithmetic(5, 2, 3)
    assert rounded.minimum_external_incidences == 9
    assert rounded.minimum_distinct_external_targets == 3

    with pytest.raises(ValueError, match="1..vertex_count"):
        export_arithmetic(4, 5)
    with pytest.raises(ValueError, match="at least 2"):
        export_arithmetic(4, 1, 1)


def test_payload_preserves_claim_scope_and_complete_range() -> None:
    payload = arithmetic_payload(256)

    assert_expected_payload(payload)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["checked_cycle_length_range"] == [4, 256]
    assert len(payload["long_cycle_cases"]) == 253
    assert payload["long_cycle_cases"][0]["margin"] == 0
    assert payload["long_cycle_cases"][-1]["margin"] == 252
    assert payload["checked_one_defect_cycle_range"] == [3, 256]
    assert len(payload["one_defect_cycle_cases"]) == 254
    assert payload["one_defect_first_forbidden_cycle_length"] == 6
    assert payload["all_checked_one_defect_cases_match_threshold"] is True
    assert payload["fan_in_cap"] == 3
    assert payload["all_checked_fan_in_cases_match_cap"] is True
    assert payload["all_checked_export_cases_nonnegative"] is True


def test_cli_summary_json_is_compact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_sparse_minimum_distance_forest.py",
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
    payload = json.loads(result.stdout)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["checked_cycle_length_range"] == [4, 512]
    assert payload["all_checked_long_cycles_close"] is True
    assert payload["one_defect_first_forbidden_cycle_length"] == 6
    assert payload["all_checked_one_defect_cases_match_threshold"] is True
    assert payload["triangle_case"]["contradiction"] is True
    assert payload["fan_in_cap"] == 3
    assert payload["export_identity"] == "d*n-2*(n-c)=(d-2)*n+2*c"
    assert "long_cycle_cases" not in payload
    assert "one_defect_cycle_cases" not in payload
    assert "fan_in_cases" not in payload
    assert "export_cases" not in payload
