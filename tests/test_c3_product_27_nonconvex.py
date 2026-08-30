from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from scripts.check_c3_product_27_nonconvex import build_payload, validate_payload


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "c3_product_27_nonconvex.json"


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    return build_payload()


def test_c3_product_27_exact_summary(payload: dict[str, Any]) -> None:
    summary = payload["summary"]

    assert validate_payload(payload) == []
    assert payload["validation_status"] == "passed"
    assert summary["factor_point_counts"] == [9, 9]
    assert summary["factor_hull_vertex_counts"] == [9, 9]
    assert summary["cycle_monodromies"] == ["omega", "omega"]
    assert summary["product_point_count"] == 27
    assert summary["distinct_product_point_count"] == 27
    assert summary["product_named_equality_count"] == 108
    assert summary["product_hull_vertex_count"] == 18
    assert summary["product_interior_point_count"] == 9


def test_c3_product_27_pins_the_nonconvex_orbits(payload: dict[str, Any]) -> None:
    summary = payload["summary"]

    assert summary["product_interior_labels"] == [
        [0, 0, 0],
        [0, 0, 1],
        [0, 0, 2],
        [0, 2, 0],
        [0, 2, 1],
        [0, 2, 2],
        [2, 0, 0],
        [2, 0, 1],
        [2, 0, 2],
    ]


def test_c3_product_27_stored_artifact_is_current(payload: dict[str, Any]) -> None:
    stored = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert stored == payload


def test_c3_product_27_keeps_nonclaim_scope(payload: dict[str, Any]) -> None:
    assert payload["status"] == "EXACT_NONCONVEX_NEGATIVE_CONTROL"
    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert "not a counterexample" in payload["claim_scope"]
    assert "does not classify" in payload["claim_scope"]
