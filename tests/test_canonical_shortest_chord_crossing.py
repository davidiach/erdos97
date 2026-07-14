from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from scripts.check_canonical_shortest_chord_crossing import (
    CLAIM_SCOPE,
    STATUS,
    TRUST,
    build_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_payload_is_exact_local_noncrossing_negative_control() -> None:
    payload = build_payload()

    assert validate_payload(payload) == []
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["strict_convexity"]["all_positive"]
    assert payload["exact_bad_centers"] == [0, 1]
    assert payload["center_max_distance_multiplicities"] == [
        4, 4, 1, 1, 1, 1, 1, 1, 1, 1
    ]
    assert payload["all_other_centers_good"]
    assert payload["erdos97_counterexample"] is False
    assert payload["selected_chords"] == [[2, 4], [3, 5]]
    assert payload["selected_chords_cross"]


def test_exactly_two_rich_centers_and_unique_shortest_chords() -> None:
    payload = build_payload()

    assert [record["center"] for record in payload["bad_centers"]] == [0, 1]
    assert [record["witnesses"] for record in payload["bad_centers"]] == [
        [2, 4, 6, 8],
        [3, 5, 7, 9],
    ]
    assert all(
        record["distance_class_multiplicities"] == [4, 1, 1, 1, 1, 1]
        for record in payload["bad_centers"]
    )
    assert all(
        record["all_other_chords_strictly_longer"]
        for record in payload["bad_centers"]
    )


def test_cli_replays_stored_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_canonical_shortest_chord_crossing.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["status"] == STATUS
    assert payload["selected_chords_cross"]
