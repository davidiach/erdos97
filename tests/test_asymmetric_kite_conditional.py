from __future__ import annotations

from scripts.check_asymmetric_kite_conditional import build_summary


def test_asymmetric_kite_identity_and_sign_guardrails() -> None:
    summary = build_summary()

    assert summary["status"] == "CONDITIONAL_REVIEW_PENDING"
    assert summary["all_identities_verified"] is True
    assert summary["identity_checks"] == {
        "LT_X1": True,
        "LT_X2": True,
        "LT_X3": True,
        "LT_X4": True,
    }
    assert summary["sign_sweep_has_no_violations"] is True
    assert summary["sign_sweep"]["sampled_formula_evaluations"] > 0
    assert "global Erdos #97 problem remain open" in summary["claim_scope"]
