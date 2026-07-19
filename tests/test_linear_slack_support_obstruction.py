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

from check_linear_slack_support_obstruction import (  # noqa: E402
    SCHEMA,
    build_summary,
    check_expected,
    clean_gap3_indices,
    forced_turn_edges,
    linear_pair_budget,
    linear_slack_lower_bound,
    minimum_unit_deficit_to_escape,
)
from erdos97.n9_base_apex import (  # noqa: E402
    minimum_capacity_deficit_to_escape_turn_cover,
)


def test_linear_slack_formula_and_budget() -> None:
    expected = {8: 2, 9: 3, 10: 3, 11: 4, 12: 4, 13: 5}
    assert {n: linear_slack_lower_bound(n) for n in expected} == expected
    assert linear_pair_budget(8) == 46
    assert linear_pair_budget(9) == 60
    assert linear_pair_budget(12) == 116
    with pytest.raises(ValueError):
        linear_slack_lower_bound(7)


def test_clean_clause_indices_use_only_local_side_equalities() -> None:
    assert clean_gap3_indices(9, frozenset(), frozenset()) == tuple(range(9))

    # A gap-2 deficit at index 2 removes only clauses 1 and 2, because the
    # clean clause at i needs gap-2 indices i and i+1.
    assert clean_gap3_indices(9, frozenset({2}), frozenset()) == (
        0,
        3,
        4,
        5,
        6,
        7,
        8,
    )
    # A gap-3 deficit removes only its own clause.
    assert 5 not in clean_gap3_indices(9, frozenset(), frozenset({5}))
    assert forced_turn_edges(9, frozenset(), frozenset({5}))[0] == (1, 2)


def test_finite_escape_minima_match_formula_and_prior_independent_search() -> None:
    for n in range(8, 13):
        local = minimum_unit_deficit_to_escape(n)
        prior = minimum_capacity_deficit_to_escape_turn_cover(
            n,
            contradiction_threshold=3,
        )
        assert local.minimum_unit_deficit == linear_slack_lower_bound(n)
        assert prior.minimum_capacity_deficit == local.minimum_unit_deficit
        assert local.minimum_forced_turns < 3


def test_linear_slack_summary() -> None:
    summary = build_summary()
    check_expected(summary)
    assert summary["schema"] == SCHEMA
    assert summary["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert [
        row["minimum_unit_deficit"]
        for row in summary["finite_escape_crosscheck"]
    ] == [2, 3, 3, 4, 4]


def test_linear_slack_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_linear_slack_support_obstruction.py",
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
    assert payload["status"] == "REVIEW_PENDING_LINEAR_SLACK_OBSTRUCTION"
