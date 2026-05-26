from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97 import n9_vertex_circle_exhaustive as n9
from scripts.check_n9_vertex_circle_strict_edge_geometry import (
    CLAIM_SCOPE,
    EXPECTED_SELECTED_ROWS,
    EXPECTED_SPAN_HISTOGRAM,
    EXPECTED_STRICT_EDGES_PER_ROW,
    EXPECTED_TOTAL_STRICT_EDGES,
    assert_expected_strict_edge_geometry,
    direct_strict_edges,
    strict_edge_geometry_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_direct_strict_edges_match_checker_for_sample_rows() -> None:
    samples = [
        (0, n9.OPTIONS[0][0]),
        (0, n9.OPTIONS[0][-1]),
        (4, n9.OPTIONS[4][17]),
        (8, n9.OPTIONS[8][42]),
    ]

    for center, row_mask in samples:
        assert direct_strict_edges(center, row_mask) == n9.STRICT_EDGES[(center, row_mask)]
        assert len(direct_strict_edges(center, row_mask)) == 9


def test_strict_edge_geometry_expected_counts_and_scope() -> None:
    payload = strict_edge_geometry_payload()

    assert_expected_strict_edge_geometry(payload)
    assert payload["validation_status"] == "passed"
    assert payload["selected_rows_checked"] == EXPECTED_SELECTED_ROWS
    assert payload["strict_edges_per_row"] == EXPECTED_STRICT_EDGES_PER_ROW
    assert payload["interval_span_histogram"] == EXPECTED_SPAN_HISTOGRAM
    assert payload["total_strict_edges"] == EXPECTED_TOTAL_STRICT_EDGES
    assert "does not prove row coverage" in payload["claim_scope"]
    assert "selected-distance quotient soundness" in payload["claim_scope"]
    assert "counterexample" in payload["claim_scope"]


def test_strict_edge_geometry_rejects_appended_claim_scope_overclaim() -> None:
    payload = strict_edge_geometry_payload()
    payload["claim_scope"] = f"{CLAIM_SCOPE} This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected_strict_edge_geometry(payload)


def test_strict_edge_geometry_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_vertex_circle_strict_edge_geometry.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    parsed = json.loads(result.stdout)
    assert parsed["validation_status"] == "passed"
    assert parsed["selected_rows_checked"] == 630
    assert parsed["strict_edges_per_row"] == {"9": 630}
