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

from check_near_saturation_support_obstruction import (  # noqa: E402
    DEFAULT_ARTIFACT,
    build_summary,
    check_artifact,
    check_expected,
    cycle_minus_edges_connected,
    enumerate_profiles,
    four_bad_q_bound,
    min_vertex_cover_cycle,
    min_vertex_cover_path_edges,
    raw_pair_budget,
    sharpened_pair_budget,
    short_diagonals_distinct,
    slack_one_case_row,
)


def test_near_saturation_expected_summary() -> None:
    summary = build_summary()

    check_expected(summary)
    assert summary["trust"] == "LEMMA_DRAFT_REVIEW_PENDING"
    rows = {row["n"]: row for row in summary["four_bad_profile_rows"]}
    assert rows[10]["sharpened_q_bound"] == 4
    assert rows[10]["min_exact_four_centers_sharpened"] == 6
    assert rows[11]["sharpened_q_bound"] == 7
    assert rows[11]["min_exact_four_centers_sharpened"] == 4


def test_near_saturation_budgets_and_cases() -> None:
    assert raw_pair_budget(10) == 80
    assert sharpened_pair_budget(10) == 78
    assert sharpened_pair_budget(8) == 46
    with pytest.raises(ValueError):
        sharpened_pair_budget(7)

    assert short_diagonals_distinct(8)
    assert short_diagonals_distinct(11)

    for n in (8, 9, 11, 16):
        row = slack_one_case_row(n)
        assert row["slack_le_1_contradiction_in_every_case"]
        for case in row["cases"].values():
            assert case["forced_turn_units_pi_over_3"] > 6


def test_near_saturation_cover_and_chain_helpers() -> None:
    assert min_vertex_cover_cycle(8) == 4
    assert min_vertex_cover_cycle(11) == 6
    assert min_vertex_cover_path_edges(7) == 4
    assert min_vertex_cover_path_edges(10) == 5

    assert cycle_minus_edges_connected(8, (3,))
    assert not cycle_minus_edges_connected(8, (0, 4))


def test_near_saturation_profile_enumeration() -> None:
    newly_excluded, surviving = enumerate_profiles(10)
    excluded_profiles = [tuple(entry["profile"]) for entry in newly_excluded]
    assert excluded_profiles == [
        (4, 4, 4, 4, 4, 4, 4, 4, 5, 7),
        (4, 4, 4, 4, 4, 5, 5, 5, 5, 5),
    ]
    assert max(sum(1 for s in profile if s >= 5) for profile in surviving) == 4
    assert four_bad_q_bound(10) == 4
    assert four_bad_q_bound(11) == 7
    assert four_bad_q_bound(12) == 11


def test_near_saturation_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_near_saturation_support_obstruction.py",
            "--check",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == "erdos97.near_saturation_support_obstruction.v1"
    assert payload["status"] == "REVIEW_PENDING_NEAR_SATURATION_OBSTRUCTION"
    assert payload["uniform_threshold_consistency"]["all_match"]
    failures = payload["slack_two_failure_records"]
    assert failures["turn_count_failure"]["turn_contradiction"] is False


@pytest.mark.artifact
def test_near_saturation_stored_artifact_matches() -> None:
    summary = build_summary()
    check_artifact(DEFAULT_ARTIFACT, summary)
