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

from check_localized_rich_support_counting import (  # noqa: E402
    build_summary,
    check_expected,
    localized_pair_budget_per_label,
    max_non_exact_centers_by_global_pair_budget,
    max_non_exact_centers_by_local_occurrence_budget,
)


def test_localized_counting_expected_summary() -> None:
    summary = build_summary()
    check_expected(summary)

    assert summary["schema"] == "erdos97.localized_rich_support_counting.v1"
    assert summary["trust"] == "LEMMA"
    assert "does not prove n=9" in summary["claim_scope"]
    assert summary["n9_consequence"] == {
        "all_centers_exact_four": True,
        "selected_indegree_per_label": 4,
        "reason": (
            "For n=9, each label occurs in at most floor(14/3)=4 supports, "
            "so total support occurrences are at most 36; the 4-bad baseline "
            "already requires 36 occurrences."
        ),
    }


def test_localized_counting_rows() -> None:
    rows = {row["n"]: row for row in build_summary()["rows"]}

    assert rows[8]["max_non_exact_four_centers_by_best_counting_bound"] == 0
    assert rows[8]["min_exact_four_centers_by_best_counting_bound"] == 8
    assert rows[8]["exact_four_selected_indegree_forced_regular_by_localized_counting"]

    assert rows[9]["max_non_exact_four_centers_by_best_counting_bound"] == 0
    assert rows[9]["min_exact_four_centers_by_best_counting_bound"] == 9
    assert rows[9]["total_support_occurrence_cap_if_E_ge_4"] == 36
    assert rows[9]["max_non_exact_four_centers_by_global_pair_budget"] == 2
    assert rows[9]["max_non_exact_four_centers_by_local_occurrence_budget"] == 0
    assert rows[9]["exact_four_selected_indegree_forced_regular_by_localized_counting"]

    assert rows[10]["max_non_exact_four_centers_by_best_counting_bound"] == 5
    assert rows[11]["max_non_exact_four_centers_by_best_counting_bound"] == 8


def test_localized_counting_helpers() -> None:
    assert localized_pair_budget_per_label(8) == 12
    assert localized_pair_budget_per_label(9) == 14
    assert max_non_exact_centers_by_global_pair_budget(9) == 2
    assert max_non_exact_centers_by_local_occurrence_budget(9) == 0

    with pytest.raises(ValueError, match="at least 3"):
        localized_pair_budget_per_label(2)


def test_localized_counting_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_localized_rich_support_counting.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    payload = json.loads(result.stdout)

    assert payload["schema"] == "erdos97.localized_rich_support_counting.v1"
    assert payload["n9_consequence"]["all_centers_exact_four"] is True
