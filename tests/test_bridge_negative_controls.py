from __future__ import annotations

from scripts.check_bridge_negative_controls import all_certificates, assert_expected


def test_bridge_negative_controls_replay_expected_statuses() -> None:
    payload = all_certificates()

    assert_expected(payload)


def test_false_output8_table_has_forward_ear_order() -> None:
    payload = all_certificates()
    certificates = payload["certificates"]
    assert isinstance(certificates, dict)
    correction = certificates["false_output8_correction"]
    assert isinstance(correction, dict)

    ear = correction["forward_ear_order"]
    assert ear["exists"]
    assert ear["seed"] == [0, 7, 10]


def test_block6_certificate_checks_exact_bisection() -> None:
    payload = all_certificates()
    certificates = payload["certificates"]
    assert isinstance(certificates, dict)
    block6 = certificates["block6_geometric_atom"]
    assert isinstance(block6, dict)

    assert block6["source_witness_bisection_ok"]
    assert block6["source_witness_midpoints"]["source"] == ["1/2", "0"]
    assert block6["source_witness_midpoints"]["witness"] == ["1/2", "0"]
