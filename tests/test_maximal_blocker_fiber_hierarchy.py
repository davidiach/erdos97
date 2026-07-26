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

from check_maximal_blocker_fiber_hierarchy import (  # noqa: E402
    SCHEMA,
    admissible_high_profiles,
    build_summary,
    check_expected,
    closed_form_maximum_cardinality,
    maximizing_profile,
    minimum_zero_fibers,
    profile_data,
)


def test_first_fiber_profiles_and_exact_maxima() -> None:
    assert admissible_high_profiles(2) == []
    assert admissible_high_profiles(3) == [(0, 0, 1)]
    assert set(admissible_high_profiles(5)) == {(2, 0, 1), (0, 1, 1)}

    expected = {
        3: (0, 0, 1, 4, 6),
        4: (1, 0, 1, 6, 12),
        5: (2, 0, 1, 8, 20),
        6: (3, 0, 1, 10, 32),
    }
    for z, target in expected.items():
        row = maximizing_profile(z)
        assert (
            row.two_fibers,
            row.three_fibers,
            row.four_fibers,
            row.high_sources,
            row.maximum_cardinality,
        ) == target
        assert row.maximum_cardinality == closed_form_maximum_cardinality(z)


def test_pair_capacity_is_replayed_exactly() -> None:
    for z in range(3, 20):
        for profile in admissible_high_profiles(z):
            row = profile_data(z, profile)
            assert 6 * row.high_centers + 3 * row.maximum_singleton_fibers <= (
                row.high_sources * (row.high_sources - 1)
            )
            assert row.maximum_cardinality == (
                row.high_sources + row.maximum_singleton_fibers
            )


def test_cardinality_thresholds() -> None:
    assert minimum_zero_fibers(6) == 3
    assert minimum_zero_fibers(7) == 4
    assert minimum_zero_fibers(9) == 4
    assert minimum_zero_fibers(12) == 4
    assert minimum_zero_fibers(13) == 5
    assert minimum_zero_fibers(15) == 5
    assert minimum_zero_fibers(21) == 6
    assert minimum_zero_fibers(33) == 7
    with pytest.raises(ValueError):
        minimum_zero_fibers(0)


def test_summary_and_cli() -> None:
    summary = build_summary()
    check_expected(summary)
    assert summary["schema"] == SCHEMA
    assert summary["cardinality_thresholds"]["15"] == 5

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_maximal_blocker_fiber_hierarchy.py",
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
    assert payload["rows"][0]["zero_fibers"] == 3
    assert payload["rows"][2]["maximum_cardinality"] == 20
    assert "not an assignment existence proof" in payload["claim_scope"]
