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

from check_minimal_two_deletion_profile import (  # noqa: E402
    SCHEMA,
    build_summary,
    check_expected,
    direct_richer_matching_capacity,
    direct_profile_capacity,
    exclusive_pair_matching_capacity,
    exclusive_pair_t4_center_floor,
    is_exclusive_mutual_pair,
    pair_average_t4_lower_bound,
    pair_coverage_rhs,
    profile_capacity,
    singleton_t4_lower_bound,
    t4_pair_certifiers,
)


def test_profile_capacities_match_direct_enumeration() -> None:
    for n in (9, 10, 17):
        assert profile_capacity(n, "T4") == 4 * n - 14
        assert profile_capacity(n, "T5") == 10
        assert profile_capacity(n, "T44") == 16
        for profile in ("T4", "T5", "T44"):
            assert profile_capacity(n, profile) == direct_profile_capacity(n, profile)

    with pytest.raises(ValueError):
        profile_capacity(8, "T4")
    with pytest.raises(ValueError):
        profile_capacity(9, "unknown")


def test_pair_average_does_not_force_a_richer_profile() -> None:
    for n in range(9, 65):
        singleton_floor = singleton_t4_lower_bound(n)
        assert pair_average_t4_lower_bound(n) <= singleton_floor
        assert pair_coverage_rhs(n, singleton_floor, 0, 0) >= n * (n - 1) // 2
    assert exclusive_pair_matching_capacity(3, 5) == 26
    assert direct_richer_matching_capacity("T5") == 2
    assert direct_richer_matching_capacity("T44") == 4
    assert exclusive_pair_t4_center_floor(7) == 14
    with pytest.raises(ValueError):
        exclusive_pair_matching_capacity(-1, 0)
    with pytest.raises(ValueError):
        exclusive_pair_t4_center_floor(-1)


def test_exclusive_mutual_pair_has_no_t4_certifier() -> None:
    classes = {
        0: frozenset({1, 2, 3, 4}),
        1: frozenset({0, 2, 3, 5}),
    }
    assert is_exclusive_mutual_pair(0, 1, classes)
    assert t4_pair_certifiers(0, 1, classes) == frozenset()

    classes[2] = frozenset({0, 3, 4, 5})
    assert not is_exclusive_mutual_pair(0, 1, classes)
    assert t4_pair_certifiers(0, 1, classes) == frozenset({2})


def test_summary_and_cli() -> None:
    summary = build_summary()
    check_expected(summary)
    assert summary["schema"] == SCHEMA
    assert summary["trust"] == "EXACT_COMBINATORIAL_REPLAY"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_minimal_two_deletion_profile.py",
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
    assert payload["exclusive_mutual_fixture"]["T4_pair_certifiers"] == []
    assert payload["exclusive_endpoint_center_floor"] == "T4 >= 2*e"
