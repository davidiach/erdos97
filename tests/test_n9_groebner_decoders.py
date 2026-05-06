from __future__ import annotations

import json
from pathlib import Path

import sympy as sp

from scripts.decode_n9_groebner_f07_f13 import infer_constraint_set


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_groebner_real_root_decoders.json"
SOURCE = ROOT / "data" / "certificates" / "2026-05-05" / "n9_groebner_results.json"
TARGET_FAMILIES = {"F07", "F08", "F09", "F13"}


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def test_n9_groebner_decoder_artifact_headline_is_review_pending() -> None:
    payload = load_json(ARTIFACT)

    assert payload["schema_version"] == "n9_groebner_real_root_decoders/v1"
    assert set(payload["target_families"]) == TARGET_FAMILIES
    assert payload["headline"] == {
        "total_real_solutions_across_families": 80,
        "strictly_convex_solutions": 0,
    }
    assert payload["provenance"]["status"] == (
        "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
    )
    assert "not a proof of Erdos Problem #97" in payload["provenance"]["claim_scope"]
    assert "REVIEW_PENDING" in payload["honest_caveat"]


def test_n9_groebner_decoder_family_rows_match_source_artifact() -> None:
    payload = load_json(ARTIFACT)
    source_by_id = {
        family["family_id"]: family
        for family in load_json(SOURCE)
        if family["family_id"] in TARGET_FAMILIES
    }

    assert set(source_by_id) == TARGET_FAMILIES
    for family in payload["families"]:
        source = source_by_id[family["family_id"]]
        assert family["rows"] == source["rows"]
        assert family["orbit_size"] == source["orbit_size"]
        assert family["status"] == source["status"]


def test_n9_groebner_decoder_families_have_only_degenerate_real_points() -> None:
    payload = load_json(ARTIFACT)

    assert len(payload["families"]) == 4
    for family in payload["families"]:
        assert family["grevlex_basis_size"] == 62
        assert family["is_zero_dimensional"] is True
        assert family["univariate_elimination"]["polynomial"] == "y2**2 - 3/4"
        assert family["real_solutions_count"] == 20
        assert family["any_strictly_convex"] is False
        assert len(family["convexity_audit"]) == 20
        assert {
            entry["verdict"]
            for entry in family["convexity_audit"]
        } == {"degenerate_coincident_vertices"}


def test_decoder_constraint_inference_requires_dependent_binders() -> None:
    x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7, x8, y8 = sp.symbols(
        "x2 y2 x3 y3 x4 y4 x5 y5 x6 y6 x7 y7 x8 y8"
    )
    simple_generators = [
        x2 - sp.Rational(1, 2),
        x5 - sp.Rational(1, 2),
        x8 - sp.Rational(1, 2),
        y2**2 - sp.Rational(3, 4),
        y5**2 - sp.Rational(3, 4),
        y8**2 - sp.Rational(3, 4),
        x3**2 - sp.Rational(3, 2) * x3,
        x6**2 - sp.Rational(3, 2) * x6,
        x4**2 - x4 / 2 - sp.Rational(1, 2),
        x7**2 - x7 / 2 - sp.Rational(1, 2),
    ]

    _constraints, missing = infer_constraint_set(
        simple_generators,
        [x2, y2, x3, y3, x4, y4, x5, y5, x6, y6, x7, y7, x8, y8],
    )

    assert "x3*y2 - 3*y3/2" in missing
    assert "x4*y2 - y2 + 3*y4/2" in missing
    assert "x6*y2 - 3*y6/2" in missing
    assert "x7*y2 - y2 + 3*y7/2" in missing
