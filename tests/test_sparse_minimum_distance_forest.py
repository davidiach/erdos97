from __future__ import annotations

import json
import subprocess
import sys

import pytest

from erdos97.sparse_minimum_distance_forest import (
    CLAIM_SCOPE,
    arithmetic_payload,
    assert_expected_payload,
    long_cycle_arithmetic,
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


def test_triangle_turn_budget_is_exact() -> None:
    triangle = triangle_turn_arithmetic()

    assert triangle["minimum_boundary_edges_per_arc"] == 2
    assert triangle["normalized_turn_lower_per_arc"] == "1/3"
    assert triangle["normalized_internal_turn_lower_sum"] == "1"
    assert triangle["normalized_internal_turn_strict_upper_bound"] == "<1"
    assert triangle["contradiction"] is True


def test_payload_preserves_claim_scope_and_complete_range() -> None:
    payload = arithmetic_payload(256)

    assert_expected_payload(payload)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["checked_cycle_length_range"] == [4, 256]
    assert len(payload["long_cycle_cases"]) == 253
    assert payload["long_cycle_cases"][0]["margin"] == 0
    assert payload["long_cycle_cases"][-1]["margin"] == 252


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
    assert payload["triangle_case"]["contradiction"] is True
    assert "long_cycle_cases" not in payload
