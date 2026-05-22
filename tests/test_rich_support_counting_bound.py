from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_rich_support_counting_bound import (  # noqa: E402
    all_centers_min_n,
    build_summary,
    check_expected,
    max_non_exact_four_centers,
    row_summary,
)


def test_rich_support_counting_expected_summary() -> None:
    summary = build_summary()

    check_expected(summary)
    rows = {row["n"]: row for row in summary["rows"]}
    assert summary["trust"] == "LEMMA"
    assert summary["all_centers_min_support_thresholds"]["5"] == 12
    assert rows[9]["max_centers_with_E_at_least_5_by_counting"] == 2
    assert rows[9]["min_centers_with_E_equal_4_by_counting"] == 7
    assert rows[10]["max_centers_with_E_at_least_5_by_counting"] == 5
    assert rows[10]["min_centers_with_E_equal_4_by_counting"] == 5
    assert rows[11]["max_centers_with_E_at_least_5_by_counting"] == 8
    assert rows[11]["min_centers_with_E_equal_4_by_counting"] == 3


def test_rich_support_counting_threshold_helpers() -> None:
    assert all_centers_min_n(4) == 8
    assert all_centers_min_n(5) == 12
    assert all_centers_min_n(6) == 17
    assert max_non_exact_four_centers(9) == 2
    assert max_non_exact_four_centers(10) == 5


def test_rich_support_counting_rows() -> None:
    row9 = row_summary(9)
    row10 = row_summary(10)

    assert row9["pair_budget"] == 63
    assert row9["max_total_support_size_given_E_ge_4"] == 38
    assert row10["pair_budget"] == 80
    assert row10["max_total_support_size_given_E_ge_4"] == 45


def test_rich_support_counting_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_rich_support_counting_bound.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == "erdos97.rich_support_counting_bound.v1"
    assert payload["status"] == "PROVED_COUNTING_LEMMA"
    assert payload["rows"][4]["n"] == 9
