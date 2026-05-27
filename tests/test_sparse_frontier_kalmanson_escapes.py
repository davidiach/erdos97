from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.check_sparse_frontier_kalmanson_escapes import (
    CLAIM_SCOPE,
    SCHEMA,
    STATUS,
    assert_expected,
    diagnostic_payload,
)


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def payload() -> dict[str, object]:
    return diagnostic_payload()


def test_sparse_frontier_kalmanson_escape_counts(payload: dict[str, object]) -> None:
    assert_expected(payload)
    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"

    by_case = {
        case["case"]: case for case in payload["cases"] if isinstance(case, dict)
    }
    c25 = by_case["C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor"]
    assert c25["distance_class_count"] == 225
    assert c25["full_kalmanson_rows_seen"] == 25_300
    assert c25["inverse_pair_conflicts"] == 0
    assert c25["stored_direct_rows_seen"] == 25_025
    assert c25["stored_row_count_matches_full_replay"] is False

    c29 = by_case["C29_sidon_1_3_7_15:z3_kalmanson_survivor"]
    assert c29["distance_class_count"] == 319
    assert c29["full_kalmanson_rows_seen"] == 47_502
    assert c29["inverse_pair_conflicts"] == 0
    assert c29["stored_direct_rows_seen"] == 47_259
    assert c29["stored_row_count_matches_full_replay"] is False


def test_sparse_frontier_kalmanson_escape_scope(payload: dict[str, object]) -> None:
    claim_scope = str(payload["claim_scope"])
    assert "fixed cyclic orders" in claim_scope
    assert "not an all-order obstruction" in claim_scope
    assert "not a geometric realizability result" in claim_scope
    assert "not a counterexample" in claim_scope
    assert "not a proof of Erdos Problem #97" in claim_scope
    assert "cannot retire these sparse-frontier orders" in str(payload["interpretation"])


def test_sparse_frontier_kalmanson_escape_rejects_drift(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["cases"][0]["inverse_pair_conflicts"] = 1

    with pytest.raises(AssertionError, match="inverse_pair_conflicts changed"):
        assert_expected(bad)


def test_sparse_frontier_kalmanson_escape_rejects_appended_claim_scope_overclaim(
    payload: dict[str, object],
) -> None:
    bad = copy.deepcopy(payload)
    bad["claim_scope"] = f"{CLAIM_SCOPE} This proves Erdos Problem #97."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        assert_expected(bad)


def test_sparse_frontier_kalmanson_escape_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_sparse_frontier_kalmanson_escapes.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert [case["inverse_pair_conflicts"] for case in payload["cases"]] == [0, 0]
