from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_n9_hinge_forcing.py"


def load_checker():
    spec = importlib.util.spec_from_file_location("check_n9_hinge_forcing", SCRIPT)
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
def test_hinge_forcing_expected_payload(generated_payload) -> None:
    checker, payload = generated_payload

    checker.assert_expected_payload(payload)
    complement = payload["hinge_free_complement"]
    assert complement["search_complete"] is True
    assert complement["satisfiable"] is False
    assert complement["stats"]["terminal_assignments"] == 0


@pytest.mark.artifact
def test_pair_capacity_and_balance_are_derived(generated_payload) -> None:
    _, payload = generated_payload

    implication = payload["finite_implication"]
    assert implication["explicit_indegree_exact_4_assumed"] is False
    assert implication["explicit_witness_pair_capacity_2_assumed"] is False
    crosscheck = payload["derived_consequences"]["finite_crosscheck"]
    derived = crosscheck["derived_filter_frontier"]
    explicit = crosscheck["explicit_filter_frontier"]
    assert derived["stats"]["terminal_assignments"] == 184
    assert explicit["stats"]["terminal_assignments"] == 184


@pytest.mark.artifact
def test_each_core_assumption_has_a_validated_drop_witness(
    generated_payload,
) -> None:
    checker, payload = generated_payload

    drops = payload["assumption_drop_witnesses"]
    assert set(drops) == {axiom.value for axiom in checker.THEOREM_ASSUMPTIONS}
    for entry in drops.values():
        assert len(entry["witness"]) == 9
        assert entry["diagnostics"]["hinge_instance_count"] == 0
        assert entry["kept_constraints_validated"] is True
        assert entry["restored_assumption_rejected"] is True


@pytest.mark.artifact
def test_hinge_forcing_rejects_claim_promotion(generated_payload) -> None:
    checker, payload = generated_payload
    edited = dict(payload)
    edited["claim_scope"] = checker.CLAIM_SCOPE + " n=9 is proved."

    with pytest.raises(AssertionError, match="claim_scope"):
        checker.assert_expected_payload(edited)
