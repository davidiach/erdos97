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
