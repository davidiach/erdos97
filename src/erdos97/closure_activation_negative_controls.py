"""Negative controls for closure-activation bridge claims.

These helpers are finite abstract incidence checks.  They do not certify
Euclidean realizability and they do not obstruct Erdos Problem #97.
"""

from __future__ import annotations

from itertools import combinations
from typing import Any, Sequence

from erdos97.incidence_filters import chords_cross_in_order, normalize_chord


Rows = list[list[int]]


def rich_class_activation_controls_certificate() -> dict[str, Any]:
    """Return the RS-2026-05-10-CE-A rich-class controls."""

    return {
        "schema": "erdos97.closure_activation_negative_controls.v1",
        "run_id": "RS-2026-05-10-CE-A",
        "date": "2026-05-10",
        "status": "NEGATIVE_CONTROL_ABSTRACT_RICH_CLASS_ONLY",
        "trust_label": "NEGATIVE_CONTROL",
        "claim_status": "abstract_rich_class_closure_stress_tests_only",
        "nonclaims": [
            "Not a polygon.",
            "Not a counterexample to Erdos Problem #97.",
            "Not a Euclidean realizability certificate.",
            "Only stress-tests closure-exposure-to-exact-row activation bridges.",
        ],
        "controls": [
            {
                "name": "NC1_three_core_trigger_unpinned_fourth",
                "vertices": list(range(9)),
                "cyclic_order": list(range(9)),
                "seed": [0, 1, 4],
                "target_center": 7,
                "target_row": [0, 1, 4, 6],
                "target_role": "strict_edge_pinned_fourth_needed",
                "required_core_witnesses": [0, 1, 4],
                "rich_classes": {"7": [[0, 1, 4, 5]]},
                "intended_exposure_mode": "CENTER_AND_CORE_WITNESSES_IN_CLOSURE",
                "role_lesson": (
                    "Closure from the three core witnesses activates some "
                    "rich row through the triple, but not the named fourth "
                    "witness 6."
                ),
                "closure": [0, 1, 4, 7],
                "target_center_in_closure": True,
                "required_core_witnesses_in_closure": [0, 1, 4],
                "target_witnesses_in_closure": [0, 1, 4],
                "target_row_active_at_center": False,
                "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
                "pair_checks": [],
                "passes_intended_negative_control": True,
            },
            {
                "name": "NC2_full_label_visibility_without_center_class_membership",
                "vertices": list(range(9)),
                "cyclic_order": list(range(9)),
                "seed": [0, 1, 4],
                "target_center": 3,
                "target_row": [0, 1, 4, 6],
                "target_role": "full_label_visibility_target",
                "required_core_witnesses": [0, 1, 4],
                "rich_classes": {
                    "3": [[0, 1, 4, 5]],
                    "6": [[1, 3, 4, 7]],
                },
                "intended_exposure_mode": (
                    "CENTER_AND_FULL_TARGET_LABELS_IN_CLOSURE_BUT_TARGET_ROW_INACTIVE"
                ),
                "role_lesson": (
                    "The target fourth label can enter closure for an "
                    "independent reason without belonging to the target "
                    "center's rich class."
                ),
                "closure": [0, 1, 3, 4, 6],
                "target_center_in_closure": True,
                "required_core_witnesses_in_closure": [0, 1, 4],
                "target_witnesses_in_closure": [0, 1, 4, 6],
                "target_row_active_at_center": False,
                "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
                "pair_checks": [
                    {
                        "centers": [3, 6],
                        "intersection": [1, 4],
                        "cap_ok": True,
                        "crossing_ok_when_two_overlap": True,
                        "ok": True,
                    }
                ],
                "passes_intended_negative_control": True,
            },
            {
                "name": "CE-private-fourth-switch/source-151-row-7",
                "vertices": list(range(9)),
                "cyclic_order": list(range(9)),
                "seed": [0, 1, 4],
                "target_center": 7,
                "target_row": [0, 1, 4, 6],
                "target_role": "strict_edge_pinned_fourth_needed",
                "required_core_witnesses": [0, 1, 4],
                "rich_classes": {"7": [[0, 1, 4, 8]]},
                "intended_exposure_mode": "CENTER_AND_CORE_WITNESSES_IN_CLOSURE",
                "role_lesson": (
                    "A different fourth witness activates the center through "
                    "the same core triple."
                ),
                "closure": [0, 1, 4, 7],
                "target_center_in_closure": True,
                "required_core_witnesses_in_closure": [0, 1, 4],
                "target_witnesses_in_closure": [0, 1, 4],
                "target_row_active_at_center": False,
                "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
                "pair_checks": [],
                "passes_intended_negative_control": True,
            },
            {
                "name": "CE-full-label-containment-switch/source-81-row-3",
                "vertices": list(range(9)),
                "cyclic_order": list(range(9)),
                "seed": [0, 1, 4],
                "target_center": 3,
                "target_row": [0, 1, 4, 6],
                "target_role": "full_label_visibility_target",
                "required_core_witnesses": [0, 1, 4],
                "rich_classes": {
                    "3": [[0, 1, 4, 8]],
                    "6": [[0, 3, 4, 5]],
                },
                "intended_exposure_mode": (
                    "CENTER_AND_FULL_TARGET_LABELS_IN_CLOSURE_BUT_TARGET_ROW_INACTIVE"
                ),
                "role_lesson": (
                    "Full target-label visibility remains weaker than "
                    "same-class membership at the target center."
                ),
                "closure": [0, 1, 3, 4, 6],
                "target_center_in_closure": True,
                "required_core_witnesses_in_closure": [0, 1, 4],
                "target_witnesses_in_closure": [0, 1, 4, 6],
                "target_row_active_at_center": False,
                "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
                "pair_checks": [
                    {
                        "centers": [3, 6],
                        "intersection": [0, 4],
                        "cap_ok": True,
                        "crossing_ok_when_two_overlap": True,
                        "ok": True,
                    }
                ],
                "passes_intended_negative_control": True,
            },
        ],
    }


def visibility_anti_activation_control_certificate() -> dict[str, Any]:
    """Return the RS-2026-05-10-A closure-visibility control."""

    return {
        "type": "closure_visibility_anti_activation_control_v1",
        "run_id": "RS-2026-05-10-A",
        "date": "2026-05-10",
        "title": "Closure-visibility anti-activation negative control",
        "trust_label": "NEGATIVE_CONTROL",
        "status": "EXACT_NEGATIVE_CONTROL",
        "claim_status": "abstract_incidence_closure_stress_test_only",
        "vertices": list(range(9)),
        "cyclic_order": list(range(9)),
        "seed_closure": [0, 1, 4],
        "target": {
            "source_row": "151:7-style closure-exposed target",
            "center": 7,
            "target_witnesses": [0, 1, 4],
            "private_outside_witness": 6,
            "target_row": [0, 1, 4, 6],
        },
        "rich_rows": [
            {
                "center": 3,
                "witnesses": [0, 1, 4, 6],
                "intended_activation_step": 1,
                "activating_triple": [0, 1, 4],
                "role": "helper row: adds center 3 from the seed closure",
            },
            {
                "center": 7,
                "witnesses": [0, 3, 4, 8],
                "intended_activation_step": 2,
                "activating_triple": [0, 3, 4],
                "role": (
                    "alternative row at target center; activates 7 through "
                    "a different triple"
                ),
            },
        ],
        "claimed_bridge_that_this_falsifies": (
            "If a deletion closure contains a target row center and three "
            "target witnesses, then the target center's active row contains "
            "those three target witnesses, or the specified target row is forced."
        ),
        "expected_closure_steps": [
            {"step": 0, "closure": [0, 1, 4]},
            {
                "step": 1,
                "activate_center": 3,
                "using_row_center": 3,
                "using_triple": [0, 1, 4],
                "closure": [0, 1, 3, 4],
            },
            {
                "step": 2,
                "activate_center": 7,
                "using_row_center": 7,
                "using_triple": [0, 3, 4],
                "closure": [0, 1, 3, 4, 7],
            },
        ],
        "expected_pairwise_checks": {
            "self_exclusion": True,
            "four_uniformity": True,
            "max_pairwise_row_intersection": 2,
            "two_overlap_crossing_pairs": [
                {"source_chord": [3, 7], "witness_chord": [0, 4]}
            ],
        },
        "expected_failure_of_target_activation": {
            "target_center_in_final_closure": True,
            "target_witnesses_in_final_closure": True,
            "target_row_present_at_center": False,
            "target_triple_contained_in_target_center_row": False,
            "target_center_activated_by_target_triple": False,
        },
        "source_provenance": {
            "prompt_pack": "01_master_reusable_prompt.md after 00_common_prelude.md",
            "source_run": (
                "User-supplied GPT-5.5 Pro run RS-2026-05-10-A, "
                "shared on 2026-05-11."
            ),
        },
        "nonclaims": [
            "This is not a polygon.",
            "This is not a counterexample to Erdos Problem #97.",
            "This is not a Euclidean realizability certificate.",
            "This does not refute activation lemmas that require provenance.",
            (
                "This does not refute activation lemmas with critical-row "
                "uniqueness or all-fourth obstruction hypotheses."
            ),
        ],
    }


def full_row_anti_activation_control_certificate() -> dict[str, Any]:
    """Return the full-row bootstrap/T12 anti-activation control."""

    return {
        "type": "bootstrap_t12_full_row_anti_activation_negative_control_v1",
        "run_id": "RS-2026-05-10-A",
        "date": "2026-05-10",
        "title": "Full selected-row closure-exposure anti-activation control",
        "trust_label": "NEGATIVE_CONTROL",
        "status": "EXACT_NEGATIVE_CONTROL",
        "claim_status": "abstract_full_selected_row_closure_stress_test_only",
        "n": 10,
        "cyclic_order": list(range(10)),
        "selected_rows": {
            "0": [1, 2, 5, 9],
            "1": [0, 2, 4, 7],
            "2": [1, 3, 5, 7],
            "3": [1, 4, 8, 9],
            "4": [0, 2, 5, 8],
            "5": [2, 6, 7, 9],
            "6": [4, 5, 7, 8],
            "7": [0, 1, 3, 4],
            "8": [0, 5, 6, 9],
            "9": [2, 3, 6, 8],
        },
        "closure_seed": [0, 1, 4],
        "expected_closure": [0, 1, 4, 7],
        "expected_closure_steps": [
            {
                "added_center": 7,
                "row": [0, 1, 3, 4],
                "support": [0, 1, 4],
            }
        ],
        "anti_activation_row": {
            "center": 7,
            "contains_core_witnesses": [0, 1, 4],
            "excluded_target_witness": 6,
            "replacement_witness": 3,
            "row": [0, 1, 3, 4],
            "target_row": [0, 1, 4, 6],
        },
        "expected_checks": {
            "uniformity_ok": True,
            "self_exclusion_ok": True,
            "cover_ok": True,
            "pairwise_intersection_and_crossing_ok": True,
            "adjacent_intersections_size_at_most_1": True,
        },
        "targeted_overstrong_bridge": (
            "Closure exposure of center 7 with witnesses 0,1,4 forces "
            "selected row 7->{0,1,4,6}."
        ),
        "source_provenance": {
            "prompt_pack": (
                "00_common_prelude.md + 01_master_reusable_prompt.md, "
                "with closure-activation/negative-control focus"
            ),
            "source_run": (
                "User-supplied GPT-5.5 Pro run RS-2026-05-10-A, "
                "shared on 2026-05-11."
            ),
        },
        "nonclaims": [
            "Not a Euclidean realization.",
            "Not a counterexample to Erdos Problem #97.",
            (
                "Not a proof that closure activation is false for genuine "
                "minimal counterexamples."
            ),
            (
                "Not checked as avoiding all vertex-circle, Kalmanson, "
                "row-Ptolemy, or algebraic obstruction templates."
            ),
        ],
    }


def wrong_fourth_negative_control_certificate() -> dict[str, Any]:
    """Return the RS-2026-05-10-A wrong-fourth negative control."""

    rows = {
        "0": [1, 2, 6, 9],
        "1": [0, 2, 4, 7],
        "2": [3, 4, 8, 9],
        "3": [1, 4, 5, 6],
        "4": [2, 5, 7, 9],
        "5": [0, 3, 6, 8],
        "6": [1, 3, 5, 7],
        "7": [0, 1, 4, 9],
        "8": [3, 6, 7, 9],
        "9": [0, 2, 5, 8],
    }
    return {
        "type": "closure_activation_wrong_fourth_negative_control_v1",
        "run_id": "RS-2026-05-10-A",
        "date": "2026-05-10",
        "title": "Wrong-fourth closure activation negative control",
        "trust_label": "NEGATIVE_CONTROL",
        "status": "EXACT_NEGATIVE_CONTROL",
        "claim_status": "abstract_incidence_closure_stress_test_only",
        "n": 10,
        "cyclic_order": list(range(10)),
        "selected_rows": rows,
        "activation_target": {
            "closure_seed": [0, 1, 4],
            "exposed_center": 7,
            "exposed_triple": [0, 1, 4],
            "wrong_fourth": 9,
            "target_fourth_not_forced": 6,
            "target_row_that_should_not_be_inferred": [0, 1, 4, 6],
            "expected_closure_from_seed": [0, 1, 4, 7],
        },
        "source_provenance": {
            "prompt_pack": (
                "00_common_prelude + 07_closure_activation_bridge + "
                "11_bridge_falsifier posture"
            ),
            "source_run": (
                "User-supplied GPT-5.5 Pro run RS-2026-05-10-A, "
                "shared on 2026-05-11."
            ),
        },
        "nonclaims": [
            "This is not a polygon.",
            "This is not a counterexample to Erdos Problem #97.",
            "This is not a Euclidean realizability certificate.",
            "This does not refute T12-style lemmas that assume exact selected rows.",
            (
                "This does not refute activation lemmas with extra criticality, "
                "uniqueness, radius-order, Ptolemy, or Kalmanson hypotheses."
            ),
        ],
    }


def rows_from_payload(payload: dict[str, Any]) -> Rows:
    """Return selected rows as a center-indexed list."""

    n = _expect_int(payload, "n")
    raw = payload.get("selected_rows", payload.get("rows"))
    if isinstance(raw, dict):
        rows: Rows = []
        for center in range(n):
            value = raw.get(str(center), raw.get(center))
            rows.append(_expect_int_list(value, f"selected_rows[{center}]"))
        return rows
    if isinstance(raw, list):
        if len(raw) != n:
            raise ValueError(f"selected_rows has length {len(raw)}, expected {n}")
        return [_expect_int_list(row, f"selected_rows[{idx}]") for idx, row in enumerate(raw)]
    raise ValueError("selected_rows must be a mapping or list")


def rich_triple_closure(seed: set[int], rows: Sequence[Sequence[int]]) -> set[int]:
    """Close a seed by adding centers with at least three visible witnesses."""

    closure = set(seed)
    changed = True
    while changed:
        changed = False
        for center, witnesses in enumerate(rows):
            if center in closure:
                continue
            if len(set(witnesses) & closure) >= 3:
                closure.add(center)
                changed = True
    return closure


def sparse_rich_triple_closure_steps(
    seed: set[int],
    rich_rows: Sequence[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Replay sparse rich-row closure and record each activation."""

    closure = set(seed)
    steps: list[dict[str, Any]] = [{"step": 0, "closure": sorted(closure)}]
    changed = True
    step = 0
    while changed:
        changed = False
        for row in rich_rows:
            center = _expect_int(row, "center")
            witnesses = set(_expect_int_list(row.get("witnesses"), "witnesses"))
            if center in closure:
                continue
            visible = sorted(witnesses & closure)
            if len(visible) < 3:
                continue
            step += 1
            triple = visible[:3]
            closure.add(center)
            steps.append(
                {
                    "step": step,
                    "activate_center": center,
                    "using_row_center": center,
                    "using_triple": triple,
                    "closure": sorted(closure),
                }
            )
            changed = True
    return steps


def rich_class_closure(
    seed: set[int],
    rich_classes: dict[int, list[set[int]]],
) -> set[int]:
    """Close a seed using abstract rich classes, sorted by center."""

    closure = set(seed)
    changed = True
    while changed:
        changed = False
        for center in sorted(rich_classes):
            if center in closure:
                continue
            if any(len(row & closure) >= 3 for row in rich_classes[center]):
                closure.add(center)
                changed = True
    return closure


def certificate_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact replay summary for a closure negative-control payload."""

    rows = rows_from_payload(payload)
    n = _expect_int(payload, "n")
    order = _expect_int_list(payload.get("cyclic_order"), "cyclic_order")
    target = _expect_mapping(payload.get("activation_target"), "activation_target")
    seed = set(_expect_int_list(target.get("closure_seed"), "closure_seed"))
    closure = rich_triple_closure(seed, rows)
    exposed_center = _expect_int(target, "exposed_center")
    target_row = sorted(
        _expect_int_list(
            target.get("target_row_that_should_not_be_inferred"),
            "target_row_that_should_not_be_inferred",
        )
    )

    row_pair_stats = _row_pair_stats(rows)
    witness_pair_violations = _witness_pair_cap_violations(rows)
    crossing_violations = _crossing_violations(rows, order)
    return {
        "ok": not validate_wrong_fourth_certificate(payload),
        "n": n,
        "two_overlap_count": row_pair_stats["two_overlap_count"],
        "closure": sorted(closure),
        "exposed_center": exposed_center,
        "exposed_row": sorted(rows[exposed_center]),
        "target_row_absent": target_row,
        "row_pair_cap_ok": not row_pair_stats["row_pair_cap_violations"],
        "witness_pair_cap_ok": not witness_pair_violations,
        "two_overlap_crossing_ok": not crossing_violations,
        "message": (
            "closure exposure holds, but the specific target fourth is not forced"
        ),
    }


def full_row_anti_activation_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact replay summary for the full-row anti-activation control."""

    data = _full_row_validation_data(payload)
    errors = _validate_full_row_from_data(data)
    return {
        "ok": not errors,
        "errors": errors,
        "closure_result": data["closure_result"],
        "closure_steps": data["closure_steps"],
        "anti_activation_row": data["anti_activation_row"],
        "checks": data["checks"],
        "covered_vertices": data["covered_vertices"],
        "indegrees": data["indegrees"],
        "two_overlap_count": data["two_overlap_count"],
        "adjacent_intersections": data["adjacent_intersections"],
        "nonclaims": payload.get("nonclaims", []),
    }


def rich_class_activation_controls_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact replay summary for aggregate rich-class controls."""

    errors = validate_rich_class_activation_controls_certificate(payload)
    controls = [
        _rich_class_control_summary(control)
        for control in _expect_controls(payload.get("controls"))
    ]
    return {
        "ok": not errors,
        "errors": errors,
        "control_count": len(controls),
        "controls": controls,
        "nonclaims": payload.get("nonclaims", []),
    }


def visibility_anti_activation_summary(payload: dict[str, Any]) -> dict[str, Any]:
    """Return a compact replay summary for the visibility control."""

    validation = _visibility_validation_data(payload)
    errors = _validate_visibility_from_data(validation)
    return {
        "ok": not errors,
        "errors": errors,
        "closure_steps": validation["closure_steps"],
        "final_closure": validation["final_closure"],
        "max_pairwise_row_intersection": validation["max_pairwise_row_intersection"],
        "two_overlap_crossings": validation["two_overlap_crossings"],
        "target_center_in_final_closure": validation["target_center_in_final_closure"],
        "target_witnesses_in_final_closure": validation[
            "target_witnesses_in_final_closure"
        ],
        "target_row_present_at_center": validation["target_row_present_at_center"],
        "target_triple_contained_in_target_center_row": validation[
            "target_triple_contained_in_target_center_row"
        ],
        "target_center_activated_by_target_triple": validation[
            "target_center_activated_by_target_triple"
        ],
        "nonclaim": (
            "abstract closure/incidence negative control only; "
            "no Euclidean realization checked"
        ),
    }


def validate_wrong_fourth_certificate(payload: dict[str, Any]) -> list[str]:
    """Return validation errors for the wrong-fourth negative control."""

    errors: list[str] = []
    if payload.get("type") != "closure_activation_wrong_fourth_negative_control_v1":
        errors.append("unexpected certificate type")

    try:
        n = _expect_int(payload, "n")
        rows = rows_from_payload(payload)
        order = _expect_int_list(payload.get("cyclic_order"), "cyclic_order")
    except ValueError as exc:
        return [str(exc)]

    if sorted(order) != list(range(n)):
        errors.append("cyclic_order must be a permutation of 0..n-1")

    for center, witnesses in enumerate(rows):
        witness_set = set(witnesses)
        if len(witnesses) != 4 or len(witness_set) != 4:
            errors.append(f"row {center} must contain four distinct witnesses")
        if center in witness_set:
            errors.append(f"row {center} violates self-exclusion")
        if any(witness < 0 or witness >= n for witness in witness_set):
            errors.append(f"row {center} contains a witness outside 0..n-1")

    row_pair_stats = _row_pair_stats(rows)
    for violation in row_pair_stats["row_pair_cap_violations"]:
        errors.append(
            "row-pair cap violation at centers "
            f"{violation['centers']}: {violation['intersection']}"
        )

    for violation in _witness_pair_cap_violations(rows):
        errors.append(
            "witness-pair cap violation for pair "
            f"{violation['pair']}: centers {violation['centers']}"
        )

    for violation in _crossing_violations(rows, order):
        errors.append(
            "two-overlap crossing violation for source "
            f"{violation['source_chord']} and witness {violation['witness_chord']}"
        )

    try:
        target = _expect_mapping(payload.get("activation_target"), "activation_target")
        seed = set(_expect_int_list(target.get("closure_seed"), "closure_seed"))
        expected_closure = set(
            _expect_int_list(
                target.get("expected_closure_from_seed"),
                "expected_closure_from_seed",
            )
        )
        exposed_center = _expect_int(target, "exposed_center")
        exposed_triple = set(
            _expect_int_list(target.get("exposed_triple"), "exposed_triple")
        )
        wrong_fourth = _expect_int(target, "wrong_fourth")
        target_fourth = _expect_int(target, "target_fourth_not_forced")
        target_row = set(
            _expect_int_list(
                target.get("target_row_that_should_not_be_inferred"),
                "target_row_that_should_not_be_inferred",
            )
        )
    except ValueError as exc:
        errors.append(str(exc))
        return errors

    if exposed_center < 0 or exposed_center >= n:
        errors.append("exposed_center is outside 0..n-1")
        return errors

    closure = rich_triple_closure(seed, rows)
    exposed_row = set(rows[exposed_center])
    if closure != expected_closure:
        errors.append(
            f"closure mismatch: got {sorted(closure)}, expected {sorted(expected_closure)}"
        )
    if exposed_center not in closure:
        errors.append("exposed center is not in the computed closure")
    if not exposed_triple <= closure:
        errors.append("exposed triple is not contained in the computed closure")
    if not exposed_triple <= seed:
        errors.append("exposed triple should already be visible in the seed")
    if len(exposed_row & seed) < 3:
        errors.append("exposed center is not activated by three seed witnesses")
    if wrong_fourth not in exposed_row:
        errors.append("wrong fourth is not present in the exposed row")
    if target_fourth in exposed_row:
        errors.append("target fourth is already present in the exposed row")
    if target_fourth in closure:
        errors.append("target fourth is not private to the computed closure")
    if exposed_row == target_row:
        errors.append("the exposed row equals the target row")
    if any(set(row) == target_row for row in rows):
        errors.append("the target row is present somewhere in the selected system")

    return errors


def validate_full_row_anti_activation_certificate(
    payload: dict[str, Any],
) -> list[str]:
    """Return validation errors for the full-row anti-activation control."""

    try:
        data = _full_row_validation_data(payload)
    except ValueError as exc:
        return [str(exc)]
    return _validate_full_row_from_data(data)


def validate_rich_class_activation_controls_certificate(
    payload: dict[str, Any],
) -> list[str]:
    """Return validation errors for the aggregate rich-class controls."""

    errors: list[str] = []
    if payload.get("schema") != "erdos97.closure_activation_negative_controls.v1":
        errors.append("unexpected aggregate certificate schema")
    if payload.get("status") != "NEGATIVE_CONTROL_ABSTRACT_RICH_CLASS_ONLY":
        errors.append("unexpected aggregate certificate status")
    try:
        controls = _expect_controls(payload.get("controls"))
    except ValueError as exc:
        return errors + [str(exc)]
    if not controls:
        errors.append("controls must not be empty")
    for index, control in enumerate(controls):
        errors.extend(
            f"controls[{index}] {error}"
            for error in _validate_rich_class_control(control)
        )
    return errors


def validate_visibility_anti_activation_certificate(
    payload: dict[str, Any],
) -> list[str]:
    """Return validation errors for the closure-visibility control."""

    try:
        data = _visibility_validation_data(payload)
    except ValueError as exc:
        return [str(exc)]
    return _validate_visibility_from_data(data)


def assert_wrong_fourth_expected(payload: dict[str, Any]) -> None:
    """Assert the stable RS-2026-05-10-A replay values."""

    errors = validate_wrong_fourth_certificate(payload)
    if errors:
        raise AssertionError("; ".join(errors))
    summary = certificate_summary(payload)
    expected = {
        "n": 10,
        "two_overlap_count": 18,
        "closure": [0, 1, 4, 7],
        "exposed_center": 7,
        "exposed_row": [0, 1, 4, 9],
        "target_row_absent": [0, 1, 4, 6],
        "row_pair_cap_ok": True,
        "witness_pair_cap_ok": True,
        "two_overlap_crossing_ok": True,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} is {summary.get(key)!r}, expected {value!r}")


def assert_full_row_anti_activation_expected(payload: dict[str, Any]) -> None:
    """Assert the stable full-row anti-activation replay values."""

    errors = validate_full_row_anti_activation_certificate(payload)
    if errors:
        raise AssertionError("; ".join(errors))
    summary = full_row_anti_activation_summary(payload)
    expected_checks = {
        "uniformity_ok": True,
        "self_exclusion_ok": True,
        "cover_ok": True,
        "pairwise_intersection_and_crossing_ok": True,
        "adjacent_intersections_size_at_most_1": True,
    }
    expected_row = {
        "center": 7,
        "contains_core_witnesses": [0, 1, 4],
        "excluded_target_witness": 6,
        "replacement_witness": 3,
        "row": [0, 1, 3, 4],
        "target_row": [0, 1, 4, 6],
        "target_row_active_at_center": False,
    }
    if summary["closure_result"] != [0, 1, 4, 7]:
        raise AssertionError(f"unexpected closure: {summary['closure_result']!r}")
    if summary["closure_steps"] != [
        {"added_center": 7, "row": [0, 1, 3, 4], "support": [0, 1, 4]}
    ]:
        raise AssertionError(f"unexpected closure steps: {summary['closure_steps']!r}")
    if summary["anti_activation_row"] != expected_row:
        raise AssertionError(f"unexpected anti-activation row: {summary['anti_activation_row']!r}")
    if summary["checks"] != expected_checks:
        raise AssertionError(f"unexpected checks: {summary['checks']!r}")
    if summary["covered_vertices"] != list(range(10)):
        raise AssertionError(f"unexpected cover: {summary['covered_vertices']!r}")


def assert_rich_class_activation_controls_expected(payload: dict[str, Any]) -> None:
    """Assert the stable RS-2026-05-10-CE-A replay values."""

    errors = validate_rich_class_activation_controls_certificate(payload)
    if errors:
        raise AssertionError("; ".join(errors))
    summary = rich_class_activation_controls_summary(payload)
    if summary["control_count"] != 4:
        raise AssertionError("expected exactly four rich-class controls")
    expected = {
        "NC1_three_core_trigger_unpinned_fourth": {
            "closure": [0, 1, 4, 7],
            "target_center_in_closure": True,
            "required_core_witnesses_in_closure": [0, 1, 4],
            "target_witnesses_in_closure": [0, 1, 4],
            "target_row_active_at_center": False,
            "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
            "passes_intended_negative_control": True,
        },
        "NC2_full_label_visibility_without_center_class_membership": {
            "closure": [0, 1, 3, 4, 6],
            "target_center_in_closure": True,
            "required_core_witnesses_in_closure": [0, 1, 4],
            "target_witnesses_in_closure": [0, 1, 4, 6],
            "target_row_active_at_center": False,
            "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
            "passes_intended_negative_control": True,
        },
        "CE-private-fourth-switch/source-151-row-7": {
            "closure": [0, 1, 4, 7],
            "target_center_in_closure": True,
            "required_core_witnesses_in_closure": [0, 1, 4],
            "target_witnesses_in_closure": [0, 1, 4],
            "target_row_active_at_center": False,
            "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
            "passes_intended_negative_control": True,
        },
        "CE-full-label-containment-switch/source-81-row-3": {
            "closure": [0, 1, 3, 4, 6],
            "target_center_in_closure": True,
            "required_core_witnesses_in_closure": [0, 1, 4],
            "target_witnesses_in_closure": [0, 1, 4, 6],
            "target_row_active_at_center": False,
            "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": True,
            "passes_intended_negative_control": True,
        },
    }
    controls = {control["name"]: control for control in summary["controls"]}
    if set(controls) != set(expected):
        raise AssertionError(f"unexpected control names: {sorted(controls)}")
    for name, expected_values in expected.items():
        for key, value in expected_values.items():
            actual = controls[name].get(key)
            if actual != value:
                raise AssertionError(
                    f"{name} {key} is {actual!r}, expected {value!r}"
                )


def assert_visibility_anti_activation_expected(payload: dict[str, Any]) -> None:
    """Assert the stable closure-visibility replay values."""

    errors = validate_visibility_anti_activation_certificate(payload)
    if errors:
        raise AssertionError("; ".join(errors))
    summary = visibility_anti_activation_summary(payload)
    expected = {
        "final_closure": [0, 1, 3, 4, 7],
        "max_pairwise_row_intersection": 2,
        "two_overlap_crossings": [
            {"source_chord": [3, 7], "witness_chord": [0, 4]}
        ],
        "target_center_in_final_closure": True,
        "target_witnesses_in_final_closure": [0, 1, 4],
        "target_row_present_at_center": False,
        "target_triple_contained_in_target_center_row": False,
        "target_center_activated_by_target_triple": False,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"{key} is {summary.get(key)!r}, expected {value!r}")


def _full_row_validation_data(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("type") != "bootstrap_t12_full_row_anti_activation_negative_control_v1":
        raise ValueError("unexpected full-row anti-activation certificate type")
    n = _expect_int(payload, "n")
    order = _expect_int_list(payload.get("cyclic_order"), "cyclic_order")
    rows = rows_from_payload(payload)
    seed = set(_expect_int_list(payload.get("closure_seed"), "closure_seed"))
    expected_closure = _expect_int_list(
        payload.get("expected_closure"),
        "expected_closure",
    )
    expected_steps = _expect_list_of_mappings(
        payload.get("expected_closure_steps"),
        "expected_closure_steps",
    )
    anti = _expect_mapping(payload.get("anti_activation_row"), "anti_activation_row")
    closure_result, closure_steps = _selected_row_closure_with_steps(seed, rows)
    row_pair_stats = _row_pair_stats(rows)
    crossing_violations = _crossing_violations(rows, order)
    cover = sorted({witness for row in rows for witness in row})
    adjacent = _adjacent_intersections(rows, order)
    anti_center = _expect_int(anti, "center")
    anti_row = sorted(rows[anti_center])
    core = _expect_int_list(
        anti.get("contains_core_witnesses"),
        "contains_core_witnesses",
    )
    excluded = _expect_int(anti, "excluded_target_witness")
    replacement = _expect_int(anti, "replacement_witness")
    target_row = _expect_int_list(anti.get("target_row"), "target_row")
    anti_summary = {
        "center": anti_center,
        "contains_core_witnesses": core,
        "excluded_target_witness": excluded,
        "replacement_witness": replacement,
        "row": anti_row,
        "target_row": target_row,
        "target_row_active_at_center": set(rows[anti_center]) == set(target_row),
    }
    checks = {
        "uniformity_ok": all(len(row) == 4 and len(set(row)) == 4 for row in rows),
        "self_exclusion_ok": all(center not in row for center, row in enumerate(rows)),
        "cover_ok": cover == list(range(n)),
        "pairwise_intersection_and_crossing_ok": (
            not row_pair_stats["row_pair_cap_violations"] and not crossing_violations
        ),
        "adjacent_intersections_size_at_most_1": all(
            len(item["intersection"]) <= 1 for item in adjacent
        ),
    }
    return {
        "n": n,
        "order": order,
        "rows": rows,
        "closure_result": closure_result,
        "expected_closure": expected_closure,
        "closure_steps": closure_steps,
        "expected_closure_steps": expected_steps,
        "anti_activation_row": anti_summary,
        "anti_activation_expected": anti,
        "checks": checks,
        "expected_checks": payload.get("expected_checks"),
        "covered_vertices": cover,
        "indegrees": _indegrees(rows, n),
        "two_overlap_count": row_pair_stats["two_overlap_count"],
        "adjacent_intersections": adjacent,
        "row_pair_cap_violations": row_pair_stats["row_pair_cap_violations"],
        "crossing_violations": crossing_violations,
    }


def _validate_full_row_from_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    n = data["n"]
    if sorted(data["order"]) != list(range(n)):
        errors.append("cyclic_order must be a permutation of 0..n-1")
    if data["closure_result"] != data["expected_closure"]:
        errors.append(
            f"closure mismatch: got {data['closure_result']}, "
            f"expected {data['expected_closure']}"
        )
    if data["closure_steps"] != data["expected_closure_steps"]:
        errors.append(
            f"closure steps mismatch: got {data['closure_steps']}, "
            f"expected {data['expected_closure_steps']}"
        )
    if data["checks"] != data["expected_checks"]:
        errors.append(f"check summary mismatch: got {data['checks']}")
    anti = data["anti_activation_row"]
    anti_expected = data["anti_activation_expected"]
    if anti["row"] != _expect_int_list(anti_expected.get("row"), "anti row"):
        errors.append("anti-activation row does not match the expected row")
    if not set(anti["contains_core_witnesses"]) <= set(anti["row"]):
        errors.append("anti-activation row does not contain all core witnesses")
    if anti["excluded_target_witness"] in anti["row"]:
        errors.append("anti-activation row contains the excluded target witness")
    if anti["replacement_witness"] not in anti["row"]:
        errors.append("anti-activation row does not contain the replacement witness")
    if anti["target_row_active_at_center"]:
        errors.append("target row is unexpectedly active at the exposed center")
    if data["row_pair_cap_violations"]:
        errors.append(f"row-pair cap violations: {data['row_pair_cap_violations']}")
    if data["crossing_violations"]:
        errors.append(f"crossing violations: {data['crossing_violations']}")
    return errors


def _selected_row_closure_with_steps(
    seed: set[int],
    rows: Sequence[Sequence[int]],
) -> tuple[list[int], list[dict[str, Any]]]:
    closure = set(seed)
    steps: list[dict[str, Any]] = []
    changed = True
    while changed:
        changed = False
        for center, row in enumerate(rows):
            if center in closure:
                continue
            support = sorted(set(row) & closure)
            if len(support) < 3:
                continue
            closure.add(center)
            steps.append(
                {
                    "added_center": center,
                    "row": sorted(row),
                    "support": support[:3],
                }
            )
            changed = True
    return sorted(closure), steps


def _adjacent_intersections(
    rows: Sequence[Sequence[int]],
    order: Sequence[int],
) -> list[dict[str, Any]]:
    return [
        {
            "centers": [order[idx], order[(idx + 1) % len(order)]],
            "intersection": sorted(
                set(rows[order[idx]]) & set(rows[order[(idx + 1) % len(order)]])
            ),
        }
        for idx in range(len(order))
    ]


def _indegrees(rows: Sequence[Sequence[int]], n: int) -> dict[str, int]:
    return {
        str(label): sum(1 for row in rows if label in row)
        for label in range(n)
    }


def _visibility_validation_data(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("type") != "closure_visibility_anti_activation_control_v1":
        raise ValueError("unexpected certificate type")

    vertices = _expect_int_list(payload.get("vertices"), "vertices")
    if sorted(vertices) != list(range(len(vertices))):
        raise ValueError("vertices must be 0..n-1")
    order = _expect_int_list(payload.get("cyclic_order"), "cyclic_order")
    rich_rows = _expect_rich_rows(payload.get("rich_rows"))
    target = _expect_mapping(payload.get("target"), "target")
    seed = set(_expect_int_list(payload.get("seed_closure"), "seed_closure"))
    target_center = _expect_int(target, "center")
    target_witnesses = set(
        _expect_int_list(target.get("target_witnesses"), "target_witnesses")
    )
    target_row = set(_expect_int_list(target.get("target_row"), "target_row"))

    row_errors = _sparse_row_errors(rich_rows, vertices)
    row_pair_stats = _sparse_row_pair_stats(rich_rows)
    witness_pair_violations = _sparse_witness_pair_cap_violations(rich_rows, vertices)
    crossing_violations, crossing_pairs = _sparse_crossing_checks(rich_rows, order)
    closure_steps = sparse_rich_triple_closure_steps(seed, rich_rows)
    final_closure = set(closure_steps[-1]["closure"])
    target_center_rows = [
        set(_expect_int_list(row.get("witnesses"), "witnesses"))
        for row in rich_rows
        if _expect_int(row, "center") == target_center
    ]
    target_row_present = any(row == target_row for row in target_center_rows)
    target_triple_present = any(target_witnesses <= row for row in target_center_rows)
    activation_steps = [
        step
        for step in closure_steps[1:]
        if step.get("activate_center") == target_center
    ]
    target_triple_sorted = sorted(target_witnesses)
    target_activation = any(
        step.get("using_triple") == target_triple_sorted for step in activation_steps
    )
    return {
        "vertices": vertices,
        "order": order,
        "rich_rows": rich_rows,
        "target_center": target_center,
        "target_witnesses": target_witnesses,
        "target_row": target_row,
        "row_errors": row_errors,
        "row_pair_cap_violations": row_pair_stats["row_pair_cap_violations"],
        "max_pairwise_row_intersection": row_pair_stats["max_row_intersection"],
        "witness_pair_cap_violations": witness_pair_violations,
        "crossing_violations": crossing_violations,
        "two_overlap_crossings": crossing_pairs,
        "closure_steps": closure_steps,
        "expected_closure_steps": payload.get("expected_closure_steps"),
        "final_closure": sorted(final_closure),
        "target_center_in_final_closure": target_center in final_closure,
        "target_witnesses_in_final_closure": (
            sorted(target_witnesses)
            if target_witnesses <= final_closure
            else sorted(target_witnesses & final_closure)
        ),
        "target_row_present_at_center": target_row_present,
        "target_triple_contained_in_target_center_row": target_triple_present,
        "target_center_activated_by_target_triple": target_activation,
    }


def _validate_rich_class_control(control: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        summary = _rich_class_control_summary(control)
    except ValueError as exc:
        return [str(exc)]
    for key in (
        "closure",
        "target_center_in_closure",
        "required_core_witnesses_in_closure",
        "target_witnesses_in_closure",
        "target_row_active_at_center",
        "pair_cap_and_two_overlap_crossing_ok_for_listed_rows",
        "pair_checks",
        "passes_intended_negative_control",
    ):
        if control.get(key) != summary[key]:
            errors.append(
                f"{control.get('name', '<unnamed>')} {key} is {control.get(key)!r}, "
                f"expected {summary[key]!r}"
            )
    if summary["row_errors"]:
        errors.extend(summary["row_errors"])
    if sorted(summary["cyclic_order"]) != summary["vertices"]:
        errors.append("cyclic_order must be a permutation of vertices")
    return errors


def _rich_class_control_summary(control: dict[str, Any]) -> dict[str, Any]:
    name = control.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError("control name must be a nonempty string")
    vertices = _expect_int_list(control.get("vertices"), "vertices")
    if sorted(vertices) != list(range(len(vertices))):
        raise ValueError(f"{name} vertices must be 0..n-1")
    order = _expect_int_list(control.get("cyclic_order"), "cyclic_order")
    seed = set(_expect_int_list(control.get("seed"), "seed"))
    target_center = _expect_int(control, "target_center")
    target_row = set(_expect_int_list(control.get("target_row"), "target_row"))
    required_core = set(
        _expect_int_list(
            control.get("required_core_witnesses"),
            "required_core_witnesses",
        )
    )
    rich_classes = _rich_classes_from_control(control.get("rich_classes"))
    closure = rich_class_closure(seed, rich_classes)
    row_errors = _rich_class_row_errors(rich_classes, vertices)
    pair_ok, pair_checks = _rich_class_pair_checks(rich_classes, order)
    target_classes = rich_classes.get(target_center, [])
    target_row_active = any(target_row <= row for row in target_classes)
    return {
        "name": name,
        "vertices": vertices,
        "cyclic_order": order,
        "closure": sorted(closure),
        "target_center_in_closure": target_center in closure,
        "required_core_witnesses_in_closure": sorted(required_core & closure),
        "target_witnesses_in_closure": sorted(target_row & closure),
        "target_row_active_at_center": target_row_active,
        "pair_cap_and_two_overlap_crossing_ok_for_listed_rows": pair_ok,
        "pair_checks": pair_checks,
        "passes_intended_negative_control": (
            target_center in closure
            and required_core <= closure
            and not target_row_active
            and pair_ok
            and not row_errors
        ),
        "row_errors": row_errors,
    }


def _validate_visibility_from_data(data: dict[str, Any]) -> list[str]:
    errors = list(data["row_errors"])
    if sorted(data["order"]) != data["vertices"]:
        errors.append("cyclic_order must be a permutation of vertices")
    for violation in data["row_pair_cap_violations"]:
        errors.append(
            "row-pair cap violation at centers "
            f"{violation['centers']}: {violation['intersection']}"
        )
    for violation in data["witness_pair_cap_violations"]:
        errors.append(
            "witness-pair cap violation for pair "
            f"{violation['pair']}: centers {violation['centers']}"
        )
    for violation in data["crossing_violations"]:
        errors.append(
            "two-overlap crossing violation for source "
            f"{violation['source_chord']} and witness {violation['witness_chord']}"
        )
    if data["closure_steps"] != data["expected_closure_steps"]:
        errors.append(
            "closure steps mismatch: got "
            f"{data['closure_steps']}, expected {data['expected_closure_steps']}"
        )
    if not data["target_center_in_final_closure"]:
        errors.append("target center is not in final closure")
    if data["target_witnesses_in_final_closure"] != sorted(data["target_witnesses"]):
        errors.append("target witnesses are not all in final closure")
    if data["target_row_present_at_center"]:
        errors.append("target row is unexpectedly present at the target center")
    if data["target_triple_contained_in_target_center_row"]:
        errors.append(
            "target triple is unexpectedly contained in a target-center row"
        )
    if data["target_center_activated_by_target_triple"]:
        errors.append("target center was activated by the target triple")
    return errors


def _rich_classes_from_control(value: object) -> dict[int, list[set[int]]]:
    if not isinstance(value, dict):
        raise ValueError("rich_classes must be a mapping")
    rich_classes: dict[int, list[set[int]]] = {}
    for raw_center, raw_classes in value.items():
        try:
            center = int(raw_center)
        except (TypeError, ValueError) as exc:
            raise ValueError("rich_classes keys must be integer-like centers") from exc
        if not isinstance(raw_classes, list):
            raise ValueError(f"rich_classes[{center}] must be a list")
        rich_classes[center] = [
            set(_expect_int_list(row, f"rich_classes[{center}] row"))
            for row in raw_classes
        ]
    return rich_classes


def _rich_class_row_errors(
    rich_classes: dict[int, list[set[int]]],
    vertices: Sequence[int],
) -> list[str]:
    errors: list[str] = []
    vertex_set = set(vertices)
    for center, rows in rich_classes.items():
        if center not in vertex_set:
            errors.append(f"row center {center} is outside the vertex set")
        for row in rows:
            if len(row) != 4:
                errors.append(f"row {center} must contain four distinct witnesses")
            if center in row:
                errors.append(f"row {center} violates self-exclusion")
            if not row <= vertex_set:
                errors.append(f"row {center} contains witnesses outside the vertex set")
    return errors


def _rich_class_pair_checks(
    rich_classes: dict[int, list[set[int]]],
    order: Sequence[int],
) -> tuple[bool, list[dict[str, Any]]]:
    rows = [
        (center, row)
        for center, classes in sorted(rich_classes.items())
        for row in classes
    ]
    checks: list[dict[str, Any]] = []
    ok = True
    for (left_center, left_row), (right_center, right_row) in combinations(rows, 2):
        intersection = sorted(left_row & right_row)
        cap_ok = len(intersection) <= 2
        crossing_ok: bool | None = None
        if len(intersection) == 2:
            crossing_ok = chords_cross_in_order(
                normalize_chord(left_center, right_center),
                normalize_chord(intersection[0], intersection[1]),
                order,
            )
        row_ok = cap_ok and crossing_ok is not False
        ok = ok and row_ok
        checks.append(
            {
                "centers": [left_center, right_center],
                "intersection": intersection,
                "cap_ok": cap_ok,
                "crossing_ok_when_two_overlap": crossing_ok,
                "ok": row_ok,
            }
        )
    return ok, checks


def _row_pair_stats(rows: Sequence[Sequence[int]]) -> dict[str, Any]:
    max_intersection = 0
    two_overlap_count = 0
    violations: list[dict[str, Any]] = []
    for left, right in combinations(range(len(rows)), 2):
        intersection = sorted(set(rows[left]) & set(rows[right]))
        max_intersection = max(max_intersection, len(intersection))
        if len(intersection) == 2:
            two_overlap_count += 1
        if len(intersection) > 2:
            violations.append(
                {
                    "centers": [left, right],
                    "intersection": intersection,
                    "intersection_size": len(intersection),
                }
            )
    return {
        "max_row_intersection": max_intersection,
        "two_overlap_count": two_overlap_count,
        "row_pair_cap_violations": violations,
    }


def _witness_pair_cap_violations(
    rows: Sequence[Sequence[int]],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for left, right in combinations(range(len(rows)), 2):
        centers = [
            center
            for center, row in enumerate(rows)
            if left in row and right in row
        ]
        if len(centers) > 2:
            violations.append(
                {"pair": [left, right], "centers": centers, "count": len(centers)}
            )
    return violations


def _sparse_row_errors(
    rich_rows: Sequence[dict[str, Any]],
    vertices: Sequence[int],
) -> list[str]:
    errors: list[str] = []
    vertex_set = set(vertices)
    for row in rich_rows:
        center = _expect_int(row, "center")
        witnesses = _expect_int_list(row.get("witnesses"), "witnesses")
        witness_set = set(witnesses)
        if center not in vertex_set:
            errors.append(f"row center {center} is outside the vertex set")
        if len(witnesses) != 4 or len(witness_set) != 4:
            errors.append(f"row {center} must contain four distinct witnesses")
        if center in witness_set:
            errors.append(f"row {center} violates self-exclusion")
        if not witness_set <= vertex_set:
            errors.append(f"row {center} contains witnesses outside the vertex set")
    return errors


def _sparse_row_pair_stats(
    rich_rows: Sequence[dict[str, Any]],
) -> dict[str, Any]:
    max_intersection = 0
    violations: list[dict[str, Any]] = []
    for left, right in combinations(rich_rows, 2):
        left_center = _expect_int(left, "center")
        right_center = _expect_int(right, "center")
        left_witnesses = set(_expect_int_list(left.get("witnesses"), "witnesses"))
        right_witnesses = set(_expect_int_list(right.get("witnesses"), "witnesses"))
        intersection = sorted(left_witnesses & right_witnesses)
        max_intersection = max(max_intersection, len(intersection))
        if len(intersection) > 2:
            violations.append(
                {
                    "centers": [left_center, right_center],
                    "intersection": intersection,
                    "intersection_size": len(intersection),
                }
            )
    return {
        "max_row_intersection": max_intersection,
        "row_pair_cap_violations": violations,
    }


def _sparse_witness_pair_cap_violations(
    rich_rows: Sequence[dict[str, Any]],
    vertices: Sequence[int],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for left, right in combinations(vertices, 2):
        centers = [
            _expect_int(row, "center")
            for row in rich_rows
            if left in _expect_int_list(row.get("witnesses"), "witnesses")
            and right in _expect_int_list(row.get("witnesses"), "witnesses")
        ]
        if len(centers) > 2:
            violations.append(
                {"pair": [left, right], "centers": centers, "count": len(centers)}
            )
    return violations


def _sparse_crossing_checks(
    rich_rows: Sequence[dict[str, Any]],
    order: Sequence[int],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    violations: list[dict[str, Any]] = []
    crossing_pairs: list[dict[str, Any]] = []
    for left, right in combinations(rich_rows, 2):
        source = normalize_chord(_expect_int(left, "center"), _expect_int(right, "center"))
        left_witnesses = set(_expect_int_list(left.get("witnesses"), "witnesses"))
        right_witnesses = set(_expect_int_list(right.get("witnesses"), "witnesses"))
        intersection = sorted(left_witnesses & right_witnesses)
        if len(intersection) != 2:
            continue
        witness = normalize_chord(intersection[0], intersection[1])
        record = {"source_chord": list(source), "witness_chord": list(witness)}
        if chords_cross_in_order(source, witness, order):
            crossing_pairs.append(record)
        else:
            violations.append(record)
    return violations, crossing_pairs


def _crossing_violations(
    rows: Sequence[Sequence[int]],
    order: Sequence[int],
) -> list[dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for left, right in combinations(range(len(rows)), 2):
        intersection = sorted(set(rows[left]) & set(rows[right]))
        if len(intersection) != 2:
            continue
        source = normalize_chord(left, right)
        witness = normalize_chord(intersection[0], intersection[1])
        if not chords_cross_in_order(source, witness, order):
            violations.append(
                {
                    "source_chord": list(source),
                    "witness_chord": list(witness),
                }
            )
    return violations


def _expect_rich_rows(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("rich_rows must be a list")
    rows: list[dict[str, Any]] = []
    for index, row in enumerate(value):
        if not isinstance(row, dict):
            raise ValueError(f"rich_rows[{index}] must be a mapping")
        rows.append(row)
    return rows


def _expect_controls(value: object) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError("controls must be a list")
    controls: list[dict[str, Any]] = []
    for index, control in enumerate(value):
        if not isinstance(control, dict):
            raise ValueError(f"controls[{index}] must be a mapping")
        controls.append(control)
    return controls


def _expect_list_of_mappings(value: object, name: str) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    out: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise ValueError(f"{name}[{index}] must be a mapping")
        out.append(item)
    return out


def _expect_mapping(value: object, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be a mapping")
    return value


def _expect_int(mapping: dict[str, Any], key: str) -> int:
    value = mapping.get(key)
    if not isinstance(value, int):
        raise ValueError(f"{key} must be an integer")
    return value


def _expect_int_list(value: object, name: str) -> list[int]:
    if not isinstance(value, list) or not all(isinstance(item, int) for item in value):
        raise ValueError(f"{name} must be a list of integers")
    return [int(item) for item in value]
