from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n9_kalmanson_three_row_core_compression.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_n9_kalmanson_three_row_core_compression",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def stored_payload():
    checker = load_checker()
    return checker, checker.load_json(checker.DEFAULT_ARTIFACT)


@pytest.mark.artifact
def test_n9_kalmanson_three_row_core_compression_expected_payload(stored_payload):
    checker, result = stored_payload

    checker.assert_expected_payload(result)
    compression = result["core_compression"]
    assert compression["best_kalmanson_minimal_core_size_histogram"] == {"3": 184}
    assert compression["best_kalmanson_distinct_dihedral_core_signatures16"] == 56
    assert result["terminal_assignments_after_filters"] == 184
    assert result["unkilled_terminal_assignments"] == 0


@pytest.mark.artifact
def test_n9_kalmanson_three_row_core_records_are_three_row(stored_payload):
    _, result = stored_payload

    assert all(
        record["best_kalmanson_minimal_core"]["row_count"] == 3
        for record in result["records"]
    )
    assert {
        record["best_kalmanson_self_edge"]["kind"] for record in result["records"]
    } == {"K1", "K2"}


@pytest.mark.artifact
def test_n9_kalmanson_three_row_core_rejects_claim_scope_append(stored_payload):
    checker, result = stored_payload
    edited = dict(result)
    edited["claim_scope"] = checker.CLAIM_SCOPE + " n=9 is proved."

    with pytest.raises(AssertionError, match="claim_scope"):
        checker.assert_expected_payload(edited)
