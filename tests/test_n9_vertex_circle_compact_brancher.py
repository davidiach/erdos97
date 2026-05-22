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
