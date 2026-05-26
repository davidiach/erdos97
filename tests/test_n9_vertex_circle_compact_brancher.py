from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n9_vertex_circle_compact_brancher.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_n9_vertex_circle_compact_brancher",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.artifact
def test_compact_n9_brancher_expected_payload():
    checker = load_checker()
    payload = checker.compact_brancher_payload()
    checker.assert_expected_payload(payload)


@pytest.mark.artifact
def test_compact_n9_brancher_rejects_top_level_claim_scope_append():
    checker = load_checker()
    payload = checker.compact_brancher_payload()
    payload["claim_scope"] = checker.CLAIM_SCOPE + " This proves n=9."

    with pytest.raises(AssertionError, match="claim_scope mismatch"):
        checker.assert_expected_payload(payload)
