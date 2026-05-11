"""Order-resolved fixed-row escape audit for bootstrap/T12 row 81:3.

The preceding rich-triple packet shows that a genuine rich class at center
``3`` containing witnesses ``0`` and ``1`` supplies the T12/F16 connector
``[1,3]=[0,3]``.  This packet audits the narrower fixed singleton-row closure
order from seed ``[0,1,4]``: in that bookkeeping model, center ``3`` activates
before label ``6`` is available, and label ``6`` is added only after using
center ``3``.

This remains diagnostic bookkeeping.  It does not prove that the fixed row is
geometrically forced, and it does not rule out a genuine rich-class catalogue
that supplies label ``6`` before center ``3`` by additional rich classes.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.adaptive_blockers import singleton_rich_classes_from_pattern
from erdos97.bootstrap_cores import RichClasses, closure
from erdos97.bootstrap_t12_81_3_closure_target import (
    TARGET_CLASSIFICATION_ASSIGNMENT_ID,
)
from erdos97.bootstrap_t12_81_3_rich_triple_contract import (
    CONNECTOR_AVOIDING_ACTIVATION_TRIPLES,
    CONNECTOR_DISTANCE_PAIRS,
    CONNECTOR_FORCING_TRIPLES,
    CONNECTOR_PAIR,
    DEFAULT_ARTIFACT as RICH_TRIPLE_ARTIFACT,
    ESCAPE_STATUS as RICH_TRIPLE_ESCAPE_STATUS,
    RICH_CLASS_EXISTENCE_STATUS,
    SCHEMA as RICH_TRIPLE_SCHEMA,
    STATUS as RICH_TRIPLE_STATUS,
    TARGET_CLOSURE_LABELS,
    TARGET_DELETION_SEED,
    TARGET_EXPOSED_CORE_VERTEX,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    TARGET_SOURCE_RECORD_ID,
    TARGET_WITNESSES,
    TRUST as RICH_TRIPLE_TRUST,
    build_t12_81_3_rich_triple_contract_payload,
)
from erdos97.bootstrap_vertex_circle_overlay import (
    SCHEMA as OVERLAY_SCHEMA,
    STATUS as OVERLAY_STATUS,
    TRUST as OVERLAY_TRUST,
    build_overlay_payload,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_order_escape.v1"
STATUS = "BOOTSTRAP_T12_81_3_ORDER_ESCAPE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Fixed singleton-rich order diagnostic for source 81 row 3: in the fixed "
    "selected-row closure from seed [0,1,4], center 3 activates before label "
    "6 is available, and label 6 is then added using a trigger containing "
    "center 3. This refines the remaining connector-avoiding escape target, "
    "but does not prove genuine rich-class order, does not prove row forcing, "
    "does not prove n=9, does not prove the bridge, and does not claim a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bootstrap_t12_81_3_order_escape.json"
)

FIXED_SINGLETON_ORDER_STATUS = "FIXED_SINGLETON_ORDER_ESCAPE_NOT_REALIZED"
GENUINE_ESCAPE_STATUS = "GENUINE_RICH_CLASS_PRE_3_LABEL_6_SUPPLY_OPEN"
PRE_3_LABEL_6_SUPPLY_STATUS = "NO_FIXED_SINGLETON_SUPPLY_BEFORE_CENTER_3"
ORDER_ESCAPE_GAP = "FIXED_SINGLETON_ORDER_NOT_GENUINE_RICH_CLASS_ORDER"
EXPECTED_FIXED_SINGLETON_ORDER = [0, 1, 4, 3, 6]
EXPECTED_INITIAL_ENABLED_CENTERS = [3]
EXPECTED_CENTER_3_TRIGGER = [0, 1, 4]
EXPECTED_LABEL_6_TRIGGER = [0, 3, 4]
EXPECTED_LABEL_6_SUPPLY_CENTER = 6


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _contains_connector_pair(values: Iterable[int]) -> bool:
    value_set = {int(value) for value in values}
    return all(label in value_set for label in CONNECTOR_PAIR)


def _source_81_overlay_record() -> Mapping[str, Any]:
    payload = build_overlay_payload()
    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("overlay payload records must be a list")
    matches = [
        record
        for record in records
        if isinstance(record, Mapping)
        and int(record.get("source_record_id", -1)) == TARGET_SOURCE_RECORD_ID
    ]
    if len(matches) != 1:
        raise AssertionError("expected exactly one overlay record for source 81")
    record = matches[0]
    if record.get("classification_assignment_id") != TARGET_CLASSIFICATION_ASSIGNMENT_ID:
        raise AssertionError("source 81 overlay assignment id drifted")
    if record.get("selected_rows", [])[TARGET_ROW_CENTER] != TARGET_WITNESSES:
        raise AssertionError("source 81 target row drifted")
    return record


def _enabled_entries(
    rich_classes: RichClasses,
    closure_vertices: Iterable[int],
) -> list[dict[str, object]]:
    closure_set = {int(label) for label in closure_vertices}
    entries: list[dict[str, object]] = []
    for center, classes in enumerate(rich_classes):
        if center in closure_set:
            continue
        for class_index, row in enumerate(classes):
            row_list = _int_list(row)
            internal = sorted(set(row_list) & closure_set)
            if len(internal) < 3:
                continue
            trigger = internal[:3]
            entries.append(
                {
                    "enabled_center": center,
                    "rich_class_index": class_index,
                    "rich_class": row_list,
                    "trigger_witnesses": trigger,
                    "trigger_contains_connector_pair": _contains_connector_pair(
                        trigger
                    ),
                    "trigger_uses_label_6": 6 in trigger,
                }
            )
    return entries


def _step_entries(result_steps: Sequence[Any]) -> list[dict[str, object]]:
    entries: list[dict[str, object]] = []
    for step_index, step in enumerate(result_steps):
        trigger = _int_list(step.trigger_witnesses)
        closure_before = _int_list(step.closure_before)
        entries.append(
            {
                "step_index": step_index,
                "added_center": int(step.added_center),
                "rich_class_index": int(step.rich_class_index),
                "rich_class": _int_list(step.rich_class),
                "trigger_witnesses": trigger,
                "closure_before": closure_before,
                "target_center_step": int(step.added_center)
                == TARGET_ROW_CENTER,
                "label_6_supply_step": int(step.added_center)
                == EXPECTED_LABEL_6_SUPPLY_CENTER,
                "trigger_contains_connector_pair": _contains_connector_pair(
                    trigger
                ),
                "trigger_uses_label_6": 6 in trigger,
                "label_6_available_before_step": 6 in closure_before,
                "trigger_depends_on_center_3": TARGET_ROW_CENTER in trigger,
            }
        )
    return entries


def _step_index_for(entries: Sequence[Mapping[str, Any]], center: int) -> int | None:
    for entry in entries:
        if int(entry["added_center"]) == center:
            return int(entry["step_index"])
    return None


def _fixed_singleton_order_audit() -> dict[str, object]:
    record = _source_81_overlay_record()
    selected_rows = record["selected_rows"]
    if not isinstance(selected_rows, list):
        raise AssertionError("source selected rows must be a list")
    rich_classes = singleton_rich_classes_from_pattern(selected_rows)
    result = closure(TARGET_DELETION_SEED, rich_classes)
    steps = _step_entries(result.steps)
    center_3_step_index = _step_index_for(steps, TARGET_ROW_CENTER)
    label_6_step_index = _step_index_for(steps, EXPECTED_LABEL_6_SUPPLY_CENTER)
    if center_3_step_index is None:
        raise AssertionError("fixed singleton closure did not activate center 3")
    if label_6_step_index is None:
        raise AssertionError("fixed singleton closure did not activate label 6")
    center_3_step = steps[center_3_step_index]
    label_6_step = steps[label_6_step_index]
    initial_enabled = _enabled_entries(rich_classes, TARGET_DELETION_SEED)
    seed_plus_3_enabled = _enabled_entries(
        rich_classes,
        sorted(set(TARGET_DELETION_SEED) | {TARGET_ROW_CENTER}),
    )

    return {
        "source_record_id": TARGET_SOURCE_RECORD_ID,
        "classification_assignment_id": record["classification_assignment_id"],
        "target_row_key": TARGET_ROW_KEY,
        "selected_rows": selected_rows,
        "rich_class_model": "singleton_fixed_selected_rows",
        "seed": result.seed,
        "closure": result.closure,
        "order": result.order,
        "generates_all": result.generates_all,
        "post_seed_steps": steps,
        "initial_enabled_activations": initial_enabled,
        "enabled_after_seed_plus_center_3": seed_plus_3_enabled,
        "center_3_step_index": center_3_step_index,
        "label_6_step_index": label_6_step_index,
        "center_3_step": center_3_step,
        "label_6_supply_step": label_6_step,
        "label_6_before_center_3": label_6_step_index < center_3_step_index,
        "center_3_before_label_6": center_3_step_index < label_6_step_index,
        "center_3_trigger": center_3_step["trigger_witnesses"],
        "center_3_trigger_forces_connector": center_3_step[
            "trigger_contains_connector_pair"
        ],
        "label_6_supply_trigger": label_6_step["trigger_witnesses"],
        "label_6_supply_depends_on_center_3": label_6_step[
            "trigger_depends_on_center_3"
        ],
        "pre_3_label_6_supply_status": PRE_3_LABEL_6_SUPPLY_STATUS,
    }


def _rich_triple_source_summary() -> dict[str, object]:
    payload = build_t12_81_3_rich_triple_contract_payload()
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("rich-triple source summary must be a mapping")
    return {
        "source_artifact": RICH_TRIPLE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
        "source_schema": payload.get("schema"),
        "source_status": payload.get("status"),
        "source_trust": payload.get("trust"),
        "target_row_key": summary.get("target_row_key"),
        "target_row_center": summary.get("target_row_center"),
        "target_witnesses": summary.get("target_witnesses"),
        "deletion_seed": summary.get("deletion_seed"),
        "connector_pair": summary.get("connector_pair"),
        "connector_distance_pairs": summary.get("connector_distance_pairs"),
        "connector_forcing_triples": summary.get("connector_forcing_triples"),
        "connector_avoiding_activation_triples": summary.get(
            "connector_avoiding_activation_triples"
        ),
        "rich_class_existence_status": summary.get(
            "rich_class_existence_status"
        ),
        "escape_status": summary.get("escape_status"),
    }


def build_t12_81_3_order_escape_payload() -> dict[str, object]:
    """Return the deterministic order-resolved fixed-row escape packet."""

    order_audit = _fixed_singleton_order_audit()
    rich_triple_summary = _rich_triple_source_summary()
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet audits only the fixed singleton-rich closure order for source 81.",
            "It does not prove that the fixed selected row 81:3 is a genuine rich class.",
            "It does not rule out extra genuine rich classes that add label 6 before center 3.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [TARGET_SOURCE_RECORD_ID],
            "target_row_center": TARGET_ROW_CENTER,
            "target_witnesses": TARGET_WITNESSES,
            "deletion_seed": TARGET_DELETION_SEED,
            "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
            "closure_labels": TARGET_CLOSURE_LABELS,
            "connector_pair": CONNECTOR_PAIR,
            "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
            "connector_forcing_triples": CONNECTOR_FORCING_TRIPLES,
            "connector_avoiding_activation_triples": (
                CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
            ),
            "fixed_singleton_order": order_audit["order"],
            "fixed_singleton_closure": order_audit["closure"],
            "initial_enabled_centers": [
                entry["enabled_center"]
                for entry in order_audit["initial_enabled_activations"]
            ],
            "fixed_singleton_center_3_step_index": order_audit[
                "center_3_step_index"
            ],
            "fixed_singleton_label_6_step_index": order_audit[
                "label_6_step_index"
            ],
            "fixed_singleton_label_6_before_center_3": order_audit[
                "label_6_before_center_3"
            ],
            "fixed_singleton_center_3_before_label_6": order_audit[
                "center_3_before_label_6"
            ],
            "fixed_singleton_center_3_trigger": order_audit[
                "center_3_trigger"
            ],
            "fixed_singleton_center_3_trigger_forces_connector": order_audit[
                "center_3_trigger_forces_connector"
            ],
            "fixed_singleton_label_6_supply_trigger": order_audit[
                "label_6_supply_trigger"
            ],
            "fixed_singleton_label_6_supply_depends_on_center_3": order_audit[
                "label_6_supply_depends_on_center_3"
            ],
            "fixed_singleton_order_status": FIXED_SINGLETON_ORDER_STATUS,
            "pre_3_label_6_supply_status": PRE_3_LABEL_6_SUPPLY_STATUS,
            "genuine_escape_status": GENUINE_ESCAPE_STATUS,
            "order_escape_gap_type": ORDER_ESCAPE_GAP,
            "next_bridge_question": (
                "Can a genuine rich-class catalogue add label 6 before center "
                "3 without already forcing the connector, or can this "
                "pre-3 label-6 supply be ruled out under the minimal/rich-class "
                "hypotheses?"
            ),
        },
        "fixed_singleton_order_audit": order_audit,
        "order_resolved_escape_contract": {
            "status": GENUINE_ESCAPE_STATUS,
            "fixed_singleton_status": FIXED_SINGLETON_ORDER_STATUS,
            "required_for_connector_avoiding_activation": (
                "Label 6 must be available before center 3 activates, because "
                "the connector-avoiding triples from [0,1,4,6] are [0,4,6] "
                "and [1,4,6]."
            ),
            "fixed_singleton_result": (
                "The fixed singleton-rich closure does not realize that escape: "
                "center 3 is the only initial activation from [0,1,4], and "
                "label 6 is supplied only afterward by trigger [0,3,4]."
            ),
            "genuine_escape_certificate_needed": [
                "a genuine rich class at some non-3 center that adds label 6 before center 3",
                "or an exact proof that no such pre-3 label-6 supply exists",
                "plus guardrails showing that any proposed supply does not already force the T12 connector",
            ],
        },
        "source_rich_triple_contract": rich_triple_summary,
        "source_artifacts": [
            {
                "path": RICH_TRIPLE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
                "role": "source 81:3 connector-pair rich-triple contract",
                "schema": RICH_TRIPLE_SCHEMA,
                "status": RICH_TRIPLE_STATUS,
                "trust": RICH_TRIPLE_TRUST,
            },
            {
                "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
                "role": "source selected rows and deletion-closure audit for source 81",
                "schema": OVERLAY_SCHEMA,
                "status": OVERLAY_STATUS,
                "trust": OVERLAY_TRUST,
            },
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_order_escape.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_order_escape.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline values for the order-escape packet."""

    expected_top = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} mismatch: expected {expected!r}")

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [TARGET_SOURCE_RECORD_ID],
        "target_row_center": TARGET_ROW_CENTER,
        "target_witnesses": TARGET_WITNESSES,
        "deletion_seed": TARGET_DELETION_SEED,
        "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
        "closure_labels": TARGET_CLOSURE_LABELS,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "connector_forcing_triples": CONNECTOR_FORCING_TRIPLES,
        "connector_avoiding_activation_triples": (
            CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
        ),
        "fixed_singleton_order": EXPECTED_FIXED_SINGLETON_ORDER,
        "fixed_singleton_closure": TARGET_CLOSURE_LABELS,
        "initial_enabled_centers": EXPECTED_INITIAL_ENABLED_CENTERS,
        "fixed_singleton_center_3_step_index": 0,
        "fixed_singleton_label_6_step_index": 1,
        "fixed_singleton_label_6_before_center_3": False,
        "fixed_singleton_center_3_before_label_6": True,
        "fixed_singleton_center_3_trigger": EXPECTED_CENTER_3_TRIGGER,
        "fixed_singleton_center_3_trigger_forces_connector": True,
        "fixed_singleton_label_6_supply_trigger": EXPECTED_LABEL_6_TRIGGER,
        "fixed_singleton_label_6_supply_depends_on_center_3": True,
        "fixed_singleton_order_status": FIXED_SINGLETON_ORDER_STATUS,
        "pre_3_label_6_supply_status": PRE_3_LABEL_6_SUPPLY_STATUS,
        "genuine_escape_status": GENUINE_ESCAPE_STATUS,
        "order_escape_gap_type": ORDER_ESCAPE_GAP,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    warnings = payload.get("interpretation_warnings")
    if not isinstance(warnings, Sequence):
        raise AssertionError("interpretation_warnings must be a sequence")
    if not any("fixed selected row 81:3" in str(warning) for warning in warnings):
        raise AssertionError("warnings must preserve the row-forcing gap")
    if not any("extra genuine rich classes" in str(warning) for warning in warnings):
        raise AssertionError("warnings must preserve the genuine escape gap")

    audit = payload.get("fixed_singleton_order_audit")
    if not isinstance(audit, Mapping):
        raise AssertionError("fixed_singleton_order_audit must be a mapping")
    expected_audit = {
        "source_record_id": TARGET_SOURCE_RECORD_ID,
        "classification_assignment_id": TARGET_CLASSIFICATION_ASSIGNMENT_ID,
        "target_row_key": TARGET_ROW_KEY,
        "rich_class_model": "singleton_fixed_selected_rows",
        "seed": TARGET_DELETION_SEED,
        "closure": TARGET_CLOSURE_LABELS,
        "order": EXPECTED_FIXED_SINGLETON_ORDER,
        "generates_all": False,
        "center_3_step_index": 0,
        "label_6_step_index": 1,
        "label_6_before_center_3": False,
        "center_3_before_label_6": True,
        "center_3_trigger": EXPECTED_CENTER_3_TRIGGER,
        "center_3_trigger_forces_connector": True,
        "label_6_supply_trigger": EXPECTED_LABEL_6_TRIGGER,
        "label_6_supply_depends_on_center_3": True,
        "pre_3_label_6_supply_status": PRE_3_LABEL_6_SUPPLY_STATUS,
    }
    for key, expected in expected_audit.items():
        if audit.get(key) != expected:
            raise AssertionError(
                f"fixed_singleton_order_audit {key} is {audit.get(key)!r}, "
                f"expected {expected!r}"
            )

    initial_enabled = audit.get("initial_enabled_activations")
    if not isinstance(initial_enabled, Sequence) or len(initial_enabled) != 1:
        raise AssertionError("initial enabled activations must contain one entry")
    initial = initial_enabled[0]
    if not isinstance(initial, Mapping):
        raise AssertionError("initial enabled activation must be a mapping")
    if initial.get("enabled_center") != TARGET_ROW_CENTER:
        raise AssertionError("center 3 must be the only initial activation")
    if initial.get("trigger_witnesses") != EXPECTED_CENTER_3_TRIGGER:
        raise AssertionError("initial center 3 trigger drifted")
    if not initial.get("trigger_contains_connector_pair"):
        raise AssertionError("initial center 3 trigger must contain connector pair")

    steps = audit.get("post_seed_steps")
    if not isinstance(steps, Sequence) or len(steps) != 2:
        raise AssertionError("fixed singleton closure should have two post-seed steps")
    center_3_step = steps[0]
    label_6_step = steps[1]
    if not isinstance(center_3_step, Mapping) or not isinstance(label_6_step, Mapping):
        raise AssertionError("post-seed steps must be mappings")
    if center_3_step.get("added_center") != TARGET_ROW_CENTER:
        raise AssertionError("first post-seed step must add center 3")
    if center_3_step.get("trigger_witnesses") != EXPECTED_CENTER_3_TRIGGER:
        raise AssertionError("center 3 step trigger drifted")
    if center_3_step.get("label_6_available_before_step"):
        raise AssertionError("label 6 must not be available before center 3")
    if label_6_step.get("added_center") != EXPECTED_LABEL_6_SUPPLY_CENTER:
        raise AssertionError("second post-seed step must add label 6")
    if label_6_step.get("trigger_witnesses") != EXPECTED_LABEL_6_TRIGGER:
        raise AssertionError("label 6 supply trigger drifted")
    if not label_6_step.get("trigger_depends_on_center_3"):
        raise AssertionError("label 6 supply must depend on center 3")

    contract = payload.get("order_resolved_escape_contract")
    if not isinstance(contract, Mapping):
        raise AssertionError("order_resolved_escape_contract must be a mapping")
    if contract.get("status") != GENUINE_ESCAPE_STATUS:
        raise AssertionError("genuine escape contract status drifted")
    if contract.get("fixed_singleton_status") != FIXED_SINGLETON_ORDER_STATUS:
        raise AssertionError("fixed singleton status drifted")

    source = payload.get("source_rich_triple_contract")
    if not isinstance(source, Mapping):
        raise AssertionError("source_rich_triple_contract must be a mapping")
    expected_source = {
        "source_schema": RICH_TRIPLE_SCHEMA,
        "source_status": RICH_TRIPLE_STATUS,
        "source_trust": RICH_TRIPLE_TRUST,
        "target_row_key": TARGET_ROW_KEY,
        "target_row_center": TARGET_ROW_CENTER,
        "target_witnesses": TARGET_WITNESSES,
        "deletion_seed": TARGET_DELETION_SEED,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "connector_forcing_triples": CONNECTOR_FORCING_TRIPLES,
        "connector_avoiding_activation_triples": (
            CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
        ),
        "rich_class_existence_status": RICH_CLASS_EXISTENCE_STATUS,
        "escape_status": RICH_TRIPLE_ESCAPE_STATUS,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise AssertionError(
                f"source_rich_triple_contract {key} is {source.get(key)!r}, "
                f"expected {expected!r}"
            )

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_order_escape.py"
    ):
        raise AssertionError("provenance generator drifted")
