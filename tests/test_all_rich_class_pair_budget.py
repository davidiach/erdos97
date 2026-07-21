from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_all_rich_class_pair_budget import (  # noqa: E402
    SCHEMA,
    baseline_mass,
    build_summary,
    check_expected,
    complete_profile_excess,
    complete_profile_mass,
    endpoint_nonendpoint_incidence_capacity,
    endpoint_nonendpoint_pair_capacity,
    endpoint_pair_quadratic_bound,
    exclusive_pair_inequality_bound,
    excess_budget,
    global_pair_capacity,
    localized_forces_all_t4,
    localized_pair_capacity,
    localized_profile_excess_budget,
    max_rich_classes_per_witness,
    maximum_exclusive_pairs,
)


def test_all_class_capacity_identities() -> None:
    for n in (8, 9, 10, 31):
        assert global_pair_capacity(n) == n * (n - 2)
        assert localized_pair_capacity(n) == 2 * n - 4
        assert baseline_mass(n) == 6 * n
        assert excess_budget(n) == n * (n - 8)
    with pytest.raises(ValueError):
        global_pair_capacity(7)


def test_complete_profile_mass_and_excess() -> None:
    assert complete_profile_mass((4,)) == 6
    assert complete_profile_mass((5,)) == 10
    assert complete_profile_mass((4, 4)) == 12
    assert complete_profile_excess((4,)) == 0
    assert complete_profile_excess((5,)) == 4
    assert complete_profile_excess((4, 4)) == 6
    assert complete_profile_excess((6,)) == 9
    with pytest.raises(ValueError):
        complete_profile_mass(())


def test_localized_integrality_forces_all_t4_at_nine() -> None:
    assert max_rich_classes_per_witness(8) == 4
    assert max_rich_classes_per_witness(9) == 4
    assert max_rich_classes_per_witness(10) == 5
    assert localized_forces_all_t4(8) is True
    assert localized_forces_all_t4(9) is True
    assert localized_forces_all_t4(10) is False
    assert localized_profile_excess_budget(9) == 0
    assert localized_profile_excess_budget(10) == 10


def test_exclusive_endpoint_incidence_and_pair_capacities() -> None:
    assert endpoint_nonendpoint_incidence_capacity(10, 2) == 30
    assert endpoint_nonendpoint_pair_capacity(10, 2) == 28
    assert endpoint_nonendpoint_pair_capacity(10, 3) == 12
    assert endpoint_pair_quadratic_bound(10) == 2
    assert endpoint_pair_quadratic_bound(20) == 6
    with pytest.raises(ValueError):
        endpoint_nonendpoint_pair_capacity(10, 6)


def test_combined_exclusive_pair_optimization_uses_full_endpoint_structure() -> None:
    assert maximum_exclusive_pairs(8).maximum_exclusive_pairs == 0
    assert maximum_exclusive_pairs(9).maximum_exclusive_pairs == 0
    expected_small = [0, 2, 3, 3, 3, 4, 4, 5, 5, 5, 6, 6]
    assert [exclusive_pair_inequality_bound(n) for n in range(9, 21)] == (
        expected_small
    )
    for n in range(8, 65):
        row = maximum_exclusive_pairs(n)
        assert row.maximum_exclusive_pairs == exclusive_pair_inequality_bound(n)
        assert row.minimum_t4_centers >= 2 * row.maximum_exclusive_pairs
        assert (
            row.minimum_t4_centers + row.t5_centers + row.t44_centers <= n
        )
        assert (
            row.t5_centers + 4 * row.t44_centers
            <= localized_profile_excess_budget(n)
        )


def test_summary_and_cli() -> None:
    summary = build_summary()
    check_expected(summary)
    assert summary["schema"] == SCHEMA
    assert summary["profile_excesses"] == {"T4": 0, "T5": 4, "T44": 6}

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_all_rich_class_pair_budget.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["schema"] == SCHEMA
    assert payload["rows"][1]["n"] == 9
    assert payload["rows"][1]["localized_forces_all_t4"] is True
    assert payload["rows"][1]["maximum_exclusive_pairs"] == 0
    assert payload["rows"][1]["minimum_t4_centers"] == 9
    assert "not an attainable incidence system" in payload["optimization_scope"]
