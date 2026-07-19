from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_kalmanson_equilateral_hinge_crosswalk.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "check_kalmanson_equilateral_hinge_crosswalk",
        SCRIPT,
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def generated_payload():
    checker = load_checker()
    return checker, checker.build_payload()


@pytest.mark.artifact
def test_crosswalk_matches_all_stored_best_cores(generated_payload) -> None:
    checker, payload = generated_payload

    checker.assert_expected_payload(payload)
    summary = payload["summary"]
    assert summary["covered_source_records"] == 184
    assert summary["core_hinge_match_count_histogram"] == {"1": 184}
    assert summary["source_best_kalmanson_kind_counts"] == {"K1": 95, "K2": 89}


@pytest.mark.artifact
def test_crosswalk_collapses_signatures_to_one_template(generated_payload) -> None:
    _, payload = generated_payload
    summary = payload["summary"]

    assert summary["source_distinct_dihedral_core_signatures16"] == 56
    assert summary["generic_pair_membership_template_orbits"] == 1
    assert len(summary["generic_template_signatures16"]) == 1


@pytest.mark.artifact
def test_crosswalk_full_assignment_histogram(generated_payload) -> None:
    _, payload = generated_payload
    summary = payload["summary"]

    assert summary["full_assignment_hinge_count_histogram"] == {
        "2": 36,
        "3": 6,
        "5": 18,
        "6": 54,
        "8": 54,
        "9": 16,
    }
    assert summary["total_full_assignment_hinge_instances"] == 1_080


@pytest.mark.artifact
def test_crosswalk_rejects_status_promotion(generated_payload) -> None:
    checker, payload = generated_payload
    edited = dict(payload)
    edited["claim_scope"] = checker.CLAIM_SCOPE + " n=9 is proved."

    with pytest.raises(AssertionError, match="claim_scope"):
        checker.assert_expected_payload(edited)
