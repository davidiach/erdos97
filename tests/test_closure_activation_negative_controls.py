from __future__ import annotations

from copy import deepcopy

from erdos97.closure_activation_negative_controls import (
    assert_full_row_anti_activation_expected,
    assert_rich_class_activation_controls_expected,
    assert_visibility_anti_activation_expected,
    assert_wrong_fourth_expected,
    certificate_summary,
    full_row_anti_activation_control_certificate,
    full_row_anti_activation_summary,
    rich_class_activation_controls_certificate,
    rich_class_activation_controls_summary,
    validate_full_row_anti_activation_certificate,
    validate_rich_class_activation_controls_certificate,
    validate_visibility_anti_activation_certificate,
    validate_wrong_fourth_certificate,
    visibility_anti_activation_control_certificate,
    visibility_anti_activation_summary,
    wrong_fourth_negative_control_certificate,
)


def test_wrong_fourth_negative_control_replays_expected_status() -> None:
    payload = wrong_fourth_negative_control_certificate()

    assert validate_wrong_fourth_certificate(payload) == []
    assert_wrong_fourth_expected(payload)

    summary = certificate_summary(payload)
    assert summary["ok"] is True
    assert summary["two_overlap_count"] == 18
    assert summary["closure"] == [0, 1, 4, 7]
    assert summary["exposed_row"] == [0, 1, 4, 9]
    assert summary["target_row_absent"] == [0, 1, 4, 6]


def test_wrong_fourth_negative_control_rejects_target_row_substitution() -> None:
    payload = wrong_fourth_negative_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["selected_rows"]
    assert isinstance(rows, dict)
    rows["7"] = [0, 1, 4, 6]
    target = tampered["activation_target"]
    assert isinstance(target, dict)
    target["wrong_fourth"] = 6

    errors = validate_wrong_fourth_certificate(tampered)

    assert any("target fourth is already present" in error for error in errors)
    assert any("exposed row equals the target row" in error for error in errors)


def test_wrong_fourth_negative_control_rejects_crossing_violation() -> None:
    payload = wrong_fourth_negative_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["selected_rows"]
    assert isinstance(rows, dict)
    rows["0"] = [1, 2, 3, 9]

    errors = validate_wrong_fourth_certificate(tampered)

    assert any("two-overlap crossing violation" in error for error in errors)


def test_full_row_anti_activation_control_replays_expected_status() -> None:
    payload = full_row_anti_activation_control_certificate()

    assert validate_full_row_anti_activation_certificate(payload) == []
    assert_full_row_anti_activation_expected(payload)

    summary = full_row_anti_activation_summary(payload)
    assert summary["ok"] is True
    assert summary["closure_result"] == [0, 1, 4, 7]
    assert summary["closure_steps"] == [
        {"added_center": 7, "row": [0, 1, 3, 4], "support": [0, 1, 4]}
    ]
    assert summary["anti_activation_row"] == {
        "center": 7,
        "contains_core_witnesses": [0, 1, 4],
        "excluded_target_witness": 6,
        "replacement_witness": 3,
        "row": [0, 1, 3, 4],
        "target_row": [0, 1, 4, 6],
        "target_row_active_at_center": False,
    }
    assert summary["checks"]["cover_ok"] is True
    assert summary["checks"]["adjacent_intersections_size_at_most_1"] is True


def test_full_row_anti_activation_control_rejects_target_fourth() -> None:
    payload = full_row_anti_activation_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["selected_rows"]
    assert isinstance(rows, dict)
    rows["7"] = [0, 1, 4, 6]

    errors = validate_full_row_anti_activation_certificate(tampered)

    assert any("closure steps mismatch" in error for error in errors)
    assert any("contains the excluded target witness" in error for error in errors)
    assert any("target row is unexpectedly active" in error for error in errors)


def test_full_row_anti_activation_control_rejects_adjacent_overlap() -> None:
    payload = full_row_anti_activation_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["selected_rows"]
    assert isinstance(rows, dict)
    rows["0"] = [0, 2, 4, 7]

    errors = validate_full_row_anti_activation_certificate(tampered)

    assert any("check summary mismatch" in error for error in errors)


def test_rich_class_activation_controls_replay_expected_statuses() -> None:
    payload = rich_class_activation_controls_certificate()

    assert validate_rich_class_activation_controls_certificate(payload) == []
    assert_rich_class_activation_controls_expected(payload)

    summary = rich_class_activation_controls_summary(payload)
    assert summary["ok"] is True
    controls = {control["name"]: control for control in summary["controls"]}
    nc1 = controls["NC1_three_core_trigger_unpinned_fourth"]
    assert nc1["closure"] == [0, 1, 4, 7]
    assert nc1["target_row_active_at_center"] is False
    nc2 = controls["NC2_full_label_visibility_without_center_class_membership"]
    assert nc2["closure"] == [0, 1, 3, 4, 6]
    assert nc2["target_witnesses_in_closure"] == [0, 1, 4, 6]
    assert nc2["pair_checks"] == [
        {
            "centers": [3, 6],
            "intersection": [1, 4],
            "cap_ok": True,
            "crossing_ok_when_two_overlap": True,
            "ok": True,
        }
    ]
    source151 = controls["CE-private-fourth-switch/source-151-row-7"]
    assert source151["closure"] == [0, 1, 4, 7]
    assert source151["target_row_active_at_center"] is False
    source81 = controls["CE-full-label-containment-switch/source-81-row-3"]
    assert source81["closure"] == [0, 1, 3, 4, 6]
    assert source81["target_witnesses_in_closure"] == [0, 1, 4, 6]
    assert source81["target_row_active_at_center"] is False


def test_rich_class_activation_controls_reject_active_target_row() -> None:
    payload = rich_class_activation_controls_certificate()
    tampered = deepcopy(payload)
    controls = tampered["controls"]
    assert isinstance(controls, list)
    controls[2]["rich_classes"]["7"] = [[0, 1, 4, 6]]

    errors = validate_rich_class_activation_controls_certificate(tampered)

    assert any("target_row_active_at_center" in error for error in errors)
    assert any("passes_intended_negative_control" in error for error in errors)


def test_rich_class_activation_controls_reject_crossing_loss() -> None:
    payload = rich_class_activation_controls_certificate()
    tampered = deepcopy(payload)
    controls = tampered["controls"]
    assert isinstance(controls, list)
    controls[3]["rich_classes"]["6"] = [[0, 1, 4, 5]]

    errors = validate_rich_class_activation_controls_certificate(tampered)

    assert any("pair_checks" in error for error in errors)
    assert any("passes_intended_negative_control" in error for error in errors)


def test_visibility_anti_activation_control_replays_expected_status() -> None:
    payload = visibility_anti_activation_control_certificate()

    assert validate_visibility_anti_activation_certificate(payload) == []
    assert_visibility_anti_activation_expected(payload)

    summary = visibility_anti_activation_summary(payload)
    assert summary["ok"] is True
    assert summary["final_closure"] == [0, 1, 3, 4, 7]
    assert summary["target_center_in_final_closure"] is True
    assert summary["target_witnesses_in_final_closure"] == [0, 1, 4]
    assert summary["target_row_present_at_center"] is False
    assert summary["target_triple_contained_in_target_center_row"] is False
    assert summary["target_center_activated_by_target_triple"] is False


def test_visibility_anti_activation_control_rejects_target_triple_row() -> None:
    payload = visibility_anti_activation_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["rich_rows"]
    assert isinstance(rows, list)
    rows[1]["witnesses"] = [0, 1, 4, 8]
    rows[1]["activating_triple"] = [0, 1, 4]
    tampered["expected_closure_steps"][2]["using_triple"] = [0, 1, 4]

    errors = validate_visibility_anti_activation_certificate(tampered)

    assert any("target triple is unexpectedly contained" in error for error in errors)
    assert any("target center was activated by the target triple" in error for error in errors)


def test_visibility_anti_activation_control_rejects_visibility_loss() -> None:
    payload = visibility_anti_activation_control_certificate()
    tampered = deepcopy(payload)
    rows = tampered["rich_rows"]
    assert isinstance(rows, list)
    rows[0]["witnesses"] = [1, 4, 5, 6]

    errors = validate_visibility_anti_activation_certificate(tampered)

    assert any("target center is not in final closure" in error for error in errors)
