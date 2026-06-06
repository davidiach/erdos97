from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_kalmanson_selfedge import (
    EXPECTED_CERTIFICATE_SHA256,
    EXPECTED_KILLS,
    EXPECTED_NODES,
    EXPECTED_ROW_OPTIONS,
    EXPECTED_TERMINALS,
    EXPECTED_UNKILLED,
    N,
    assert_expected_summary,
    bitset,
    chords_cross,
    first_kalmanson_self_edge,
    row_options,
    row_pair_is_necessary,
    rows_from_payload,
    run,
    summary_payload,
    verify_certificate_payload,
)


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_kalmanson_selfedge.json"


def test_chords_cross_basic_cases() -> None:
    assert chords_cross(9, 0, 4, 1, 7)
    assert chords_cross(9, 4, 0, 1, 7)
    assert not chords_cross(9, 0, 4, 1, 3)
    assert not chords_cross(9, 0, 4, 4, 7)


def test_row_pair_filters_two_overlap_crossing() -> None:
    row_i = bitset([2, 4, 6, 8])
    crossing_row = bitset([0, 2, 4, 7])
    noncrossing_row = bitset([4, 5, 6, 7])
    adjacent_row = bitset([2, 4, 5, 7])

    assert row_pair_is_necessary(9, 0, row_i, 3, crossing_row)
    assert not row_pair_is_necessary(9, 0, row_i, 3, noncrossing_row)
    assert not row_pair_is_necessary(9, 0, row_i, 1, adjacent_row)


def test_row_count_is_literal_70_per_center() -> None:
    assert len(row_options(N, 0)) == EXPECTED_ROW_OPTIONS
    assert all(len(row_options(N, center)) == EXPECTED_ROW_OPTIONS for center in range(N))


def test_run_rejects_non_nine_payloads() -> None:
    with pytest.raises(ValueError, match="n=9"):
        run(8)


def test_first_stored_assignment_has_kalmanson_self_edge() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    first = payload["certificates"][0]
    rows = rows_from_payload(first["rows"])

    assert first_kalmanson_self_edge(N, rows) == first["self_edge"]
    assert first["self_edge"]["quadruple"] == [0, 1, 2, 7]
    assert first["self_edge"]["inequality"] == "K1"


def test_certificate_artifact_replays_without_brancher() -> None:
    payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    summary = verify_certificate_payload(payload)

    assert_expected_summary(summary)
    assert summary["verified_certificates"] == EXPECTED_KILLS
    assert summary_payload(payload)["row_options_per_center"] == EXPECTED_ROW_OPTIONS
    assert summary_payload(payload)["nodes_visited"] == EXPECTED_NODES
    assert summary_payload(payload)["terminal_assignments"] == EXPECTED_TERMINALS
    assert summary_payload(payload)["killed_by_kalmanson_self_edge"] == EXPECTED_KILLS
    assert summary_payload(payload)["unkilled"] == EXPECTED_UNKILLED
    assert summary_payload(payload)["certificate_sha256"] == EXPECTED_CERTIFICATE_SHA256


def test_certificate_verify_cli_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_kalmanson_selfedge.py",
            "--verify-certificate",
            "data/certificates/n9_kalmanson_selfedge.json",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    summary = json.loads(result.stdout)
    assert summary["mode"] == "verify_certificate"
    assert summary["verified_certificates"] == EXPECTED_KILLS
    assert summary["certificate_sha256"] == EXPECTED_CERTIFICATE_SHA256
    assert "certificates" not in summary
    assert "unkilled_assignments" not in summary


def test_certificate_verify_cli_rejects_json_and_summary_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_kalmanson_selfedge.py",
            "--verify-certificate",
            "data/certificates/n9_kalmanson_selfedge.json",
            "--json",
            "--summary-json",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 2
    assert "not allowed with argument --json" in result.stderr
