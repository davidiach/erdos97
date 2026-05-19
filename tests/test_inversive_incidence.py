from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.inversive_incidence import (
    InversionLineSeed,
    assert_expected_counts,
    close_lines_from_seeds,
    inversion_line_seeds,
    n9_inversive_incidence_summary,
    pivot_inversive_incidence,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_inversive_incidence_pilot.json"


def test_inversion_line_seeds_for_one_pivot() -> None:
    rows = [
        [1, 2, 3, 4],
        [0, 2, 5, 6],
        [0, 1, 5, 7],
        [0, 1, 2, 8],
    ]

    seeds = inversion_line_seeds(rows, pivot=0)

    assert [seed.center for seed in seeds] == [1, 2, 3]
    assert [seed.points for seed in seeds] == [(2, 5, 6), (1, 5, 7), (1, 2, 8)]


def test_line_closure_merges_after_enlargement() -> None:
    seeds = (
        InversionLineSeed(pivot=0, center=1, points=(1, 2, 3)),
        InversionLineSeed(pivot=0, center=2, points=(1, 2, 4)),
        InversionLineSeed(pivot=0, center=3, points=(3, 4, 5)),
    )

    assert close_lines_from_seeds(seeds) == ((1, 2, 3, 4, 5),)


def test_pivot_summary_tracks_repeated_pairs() -> None:
    rows = [
        [1, 2, 3, 4],
        [0, 2, 5, 6],
        [0, 2, 5, 7],
        [0, 1, 2, 8],
    ]

    summary = pivot_inversive_incidence(rows, pivot=0)

    assert summary.seed_count == 3
    assert summary.repeated_pair_count == 1
    assert summary.closed_lines == ((1, 2, 8), (2, 5, 6, 7))


def test_n9_inversive_incidence_artifact_counts() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert_expected_counts(payload)
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert payload["status"] == "INVERSION_INCIDENCE_HEURISTIC_DIAGNOSTIC_ONLY"
    assert payload["summary"]["compressed_pivots"] == 0
    assert payload["histograms"]["pivot_seed_count"] == {"4": 1656}
    assert payload["histograms"]["closed_line_size"] == {"3": 6624}


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_n9_inversive_incidence_artifact_is_current() -> None:
    checked_in = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert n9_inversive_incidence_summary() == checked_in
