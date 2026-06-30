#!/usr/bin/env python3
"""Check the next-lemma obligations for the bootstrap/T12 151:6 lane.

This checker joins the latest route-decision packets for the source-151 row-6
label-4 private-lane target:

* endpoint-8 forcing is still blocked by the private-halo pair [3,5];
* off-center [0,4,6] rows still do not migrate to center 8 from current
  support evidence; and
* the target-sparse certificate route is order-sensitive, so the current row
  family is not an all-order route.

The payload is a bridge-work contract, not a proof.  It records which lemma
obligations remain useful and which tempting shortcuts are already ruled out.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "erdos97.bootstrap_t12_151_6_label4_next_lemma_obligations.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_NEXT_LEMMA_OBLIGATIONS_CONTRACT"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
TARGET_ROW_KEY = "151:6"
TARGET_CENTER = 6
PRIVATE_SUPPORT_PAIR = [3, 5]
CONDITIONAL_CENTER8_TARGET = [0, 4, 6]

ENDPOINT_PREFLIGHT_ARTIFACT = Path(
    "data/certificates/bootstrap_t12_151_6_endpoint8_forcing_preflight.json"
)
MIGRATION_SUPPORT_ARTIFACT = Path(
    "data/certificates/"
    "bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.json"
)
ORDER_SENSITIVITY_ARTIFACT = Path(
    "data/certificates/"
    "bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_crosswalk.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_next_lemma_obligations.json"
)

ENDPOINT_PREFLIGHT_SCHEMA = "erdos97.bootstrap_t12_151_6_endpoint8_forcing_preflight.v1"
ENDPOINT_PREFLIGHT_STATUS = (
    "BOOTSTRAP_T12_151_6_ENDPOINT8_FORCING_PREFLIGHT_DIAGNOSTIC_ONLY"
)
MIGRATION_SUPPORT_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_center8_migration_support_crosswalk.v1"
)
MIGRATION_SUPPORT_STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_MIGRATION_SUPPORT_CROSSWALK_"
    "DIAGNOSTIC_ONLY"
)
ORDER_SENSITIVITY_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_order_sensitivity_"
    "crosswalk.v1"
)
ORDER_SENSITIVITY_STATUS = "EXACT_ORDER_SENSITIVITY_ROUTE_DECISION_CROSSWALK"

ENDPOINT_GATE = "NOT_READY_PRIVATE_HALO_ONLY_ESCAPE_SURVIVES_BASIC_FILTERS"
MIGRATION_GATE = "NOT_READY_SUPPORT_BACKING_DOES_NOT_MIGRATE_OFF_CENTER_ROWS"
ORDER_ROUTE_ANSWER = (
    "no_not_without_new_rows_order_forcing_or_geometric_endpoint_exclusion"
)
TARGET_SPARSE_ENDPOINT_ROWS = [[0, 1, 4, 6], [0, 2, 4, 6], [0, 4, 6, 7]]

PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_next_lemma_obligations.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_next_lemma_obligations.py "
        "--write --assert-expected"
    ),
}

CLAIM_SCOPE = (
    "Bridge-obligation contract for the source-151 row-6 label-4 private-lane "
    "target. It joins the endpoint-8 forcing preflight, the center-8 "
    "migration support crosswalk, and the target-sparse order-sensitivity "
    "crosswalk to record the remaining useful lemma obligations: exclude the "
    "private-halo pair [3,5] or force endpoint 8, prove genuine center-8 "
    "migration or an independent center-8 [0,4,6] source, and add order "
    "forcing, stronger exact strict rows, or endpoint/source geometry for the "
    "target-sparse lane. It does not prove support existence, does not prove "
    "center migration, does not prove row forcing, does not prove endpoint-8 "
    "forcing, does not prove pair [3,5] impossible, does not prove assignments "
    "0 or 11 possible or impossible, does not prove an all-order obstruction, "
    "does not prove n=9, does not prove the bootstrap bridge, does not prove "
    "Erdos #97, is not a counterexample, and is not a global status update."
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "dead_end_guards",
    "interpretation",
    "obligations",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
}


def build_payload(
    endpoint_preflight: Mapping[str, Any] | None = None,
    migration_support: Mapping[str, Any] | None = None,
    order_sensitivity: Mapping[str, Any] | None = None,
    *,
    endpoint_preflight_path: Path = ENDPOINT_PREFLIGHT_ARTIFACT,
    migration_support_path: Path = MIGRATION_SUPPORT_ARTIFACT,
    order_sensitivity_path: Path = ORDER_SENSITIVITY_ARTIFACT,
) -> dict[str, Any]:
    """Return the deterministic next-lemma obligations payload."""

    if endpoint_preflight is None:
        endpoint_preflight = load_json(endpoint_preflight_path)
    if migration_support is None:
        migration_support = load_json(migration_support_path)
    if order_sensitivity is None:
        order_sensitivity = load_json(order_sensitivity_path)

    source_errors = validate_sources(
        endpoint_preflight,
        migration_support,
        order_sensitivity,
    )
    if source_errors:
        raise AssertionError("; ".join(source_errors))

    endpoint_summary = required_mapping(endpoint_preflight.get("summary"), "endpoint summary")
    migration_summary = required_mapping(migration_support.get("summary"), "migration summary")
    order_summary = required_mapping(order_sensitivity.get("summary"), "order summary")

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target": CONDITIONAL_CENTER8_TARGET,
        "open_obligation_count": 3,
        "open_obligation_ids": [
            "private_halo_endpoint8_exclusion",
            "center8_migration_or_source",
            "target_sparse_order_or_geometry",
        ],
        "blocked_shortcut_count": 8,
        "endpoint8_forced_by_current_evidence": endpoint_summary[
            "endpoint8_forced_by_current_evidence"
        ],
        "private_halo_only_basic_survivor_count": endpoint_summary[
            "private_halo_only_basic_survivor_count"
        ],
        "private_halo_escape_status": endpoint_summary["private_halo_escape_status"],
        "migration_status": migration_summary["migration_status"],
        "support_requirement_center8_count": migration_summary[
            "support_requirement_center8_count"
        ],
        "off_center_target_row_occurrence_count": migration_summary[
            "off_center_target_row_occurrence_count"
        ],
        "off_center_rows_with_same_center_support_count": migration_summary[
            "off_center_rows_with_same_center_support_count"
        ],
        "off_center_rows_at_unsupported_center_count": migration_summary[
            "off_center_rows_at_unsupported_center_count"
        ],
        "target_sparse_assignment_indices": migration_summary[
            "target_sparse_assignment_indices"
        ],
        "target_sparse_endpoint_rows": order_summary["endpoint_rows"],
        "natural_order_current_row_family_size_each": order_summary[
            "natural_order_current_row_family_size_each"
        ],
        "natural_order_potential_weight_sum_each": order_summary[
            "natural_order_potential_weight_sum_each"
        ],
        "alternate_order": order_summary["alternate_order"],
        "alternate_order_certificate_row_count_each": order_summary[
            "alternate_order_certificate_row_count_each"
        ],
        "current_row_family_all_order_route_ready": order_summary[
            "current_row_family_all_order_route_ready"
        ],
        "all_order_obstruction_proved": order_summary[
            "all_order_obstruction_proved"
        ],
        "solves_n9": False,
        "solves_erdos97": False,
    }
    obligations = [
        {
            "obligation_id": "private_halo_endpoint8_exclusion",
            "status": "open",
            "bridge_question": (
                "Under genuine minimal/rich-class hypotheses, must the "
                "source-151 row-6 outside-pair support include endpoint 8?"
            ),
            "current_blocker": (
                "The private-halo-only support pair [3,5] has 12 "
                "basic-filter selected-row survivors before vertex-circle "
                "replay."
            ),
            "useful_success_criterion": (
                "Either force one of [3,8] or [5,8], or prove that [3,5] "
                "cannot occur as a genuine support pair."
            ),
            "not_satisfied_by": [
                "the conditional connector contract alone",
                "basic incidence/crossing filters",
                "vertex-circle replay of selected-row neighborhoods",
            ],
            "source_gate": endpoint_summary["gate_status"],
        },
        {
            "obligation_id": "center8_migration_or_source",
            "status": "open",
            "bridge_question": (
                "Can off-center [0,4,6] rows, or a separate source, force a "
                "center-8 rich class containing [0,4,6]?"
            ),
            "current_blocker": (
                "Current support requirements are centered at 5, 6, and 7; "
                "none is centered at 8, and same-center support backing does "
                "not move the row to center 8."
            ),
            "useful_success_criterion": (
                "Prove a center-migration theorem, or supply an independent "
                "geometric source for the center-8 [0,4,6] rich class."
            ),
            "not_satisfied_by": [
                "same-center support backing at centers 5 or 7",
                "unsupported off-center rows at center 2",
                "arbitrary label-8 visibility",
                "the existing source-151 row-8 singleton packet",
            ],
            "source_gate": migration_summary["migration_status"],
        },
        {
            "obligation_id": "target_sparse_order_or_geometry",
            "status": "open",
            "bridge_question": (
                "Can the target-sparse assignments 0 and 11 be obstructed by "
                "order forcing, stronger exact strict rows, or endpoint/source "
                "geometry?"
            ),
            "current_blocker": (
                "The natural-order 255-row Kalmanson/Altman family is exactly "
                "route-pruned for the three endpoint quotients, while one "
                "alternate order is exactly obstructed."
            ),
            "useful_success_criterion": (
                "Prove useful cyclic-order structure, add a stronger strict "
                "row family with a geometric source, or prove a genuine "
                "endpoint/source exclusion for the target-sparse lane."
            ),
            "not_satisfied_by": [
                "another normalized solver screen over the same 255 rows",
                "the fixed alternate-order certificates alone",
                "the natural-order dual certificates alone",
                "one-completion plus two arbitrary selected-row repairs",
            ],
            "source_gate": ORDER_ROUTE_ANSWER,
        },
    ]
    dead_end_guards = [
        "Do not claim endpoint-8 support is forced from the current preflight.",
        "Do not treat vertex-circle replay of selected-row survivors as support existence.",
        "Do not treat same-center support backing as center-8 migration.",
        "Do not reuse the existing source-151 row-8 singleton packet as a source for [0,4,6].",
        "Do not treat label-8 visibility as a target-compatible center-8 core.",
        "Do not claim the natural-order dual certificates make the quotients realizable.",
        "Do not claim the alternate-order certificates prove all-order obstruction.",
        "Do not run another solver-only cone screen over the same 255-row family as bridge progress.",
    ]
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "obligations": obligations,
        "dead_end_guards": dead_end_guards,
        "source_artifacts": [
            source_record(
                endpoint_preflight_path,
                "endpoint-8 forcing preflight",
                endpoint_preflight,
            ),
            source_record(
                migration_support_path,
                "center-8 migration support crosswalk",
                migration_support,
            ),
            source_record(
                order_sensitivity_path,
                "target-sparse order-sensitivity crosswalk",
                order_sensitivity,
            ),
        ],
        "interpretation": [
            (
                "The source packets already rule out several tempting local "
                "shortcuts, so useful work must add a genuine bridge lemma or "
                "a new exact geometric source."
            ),
            (
                "The three open obligations are complementary: private-halo "
                "endpoint forcing, center-8 migration/source, and target-sparse "
                "order or geometry."
            ),
            (
                "This ledger is task-selection infrastructure only; it does "
                "not promote the 151:6 lane, n=9, or the global problem."
            ),
        ],
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    assert_expected_payload(payload)
    return payload


def validate_sources(
    endpoint_preflight: Mapping[str, Any],
    migration_support: Mapping[str, Any],
    order_sensitivity: Mapping[str, Any],
) -> list[str]:
    """Return source-packet validation errors."""

    errors: list[str] = []
    expected_meta = [
        (
            endpoint_preflight,
            ENDPOINT_PREFLIGHT_SCHEMA,
            ENDPOINT_PREFLIGHT_STATUS,
            TRUST,
            "endpoint preflight",
        ),
        (
            migration_support,
            MIGRATION_SUPPORT_SCHEMA,
            MIGRATION_SUPPORT_STATUS,
            TRUST,
            "migration support",
        ),
        (
            order_sensitivity,
            ORDER_SENSITIVITY_SCHEMA,
            ORDER_SENSITIVITY_STATUS,
            "EXACT_ROUTE_PRUNING_CERTIFICATE",
            "order sensitivity",
        ),
    ]
    for payload, schema, status, trust, label in expected_meta:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != trust:
            errors.append(f"{label} trust mismatch")
        if payload.get("validation_status") != "passed":
            errors.append(f"{label} validation status mismatch")
        if payload.get("validation_errors") != []:
            errors.append(f"{label} validation errors are not empty")

    endpoint_summary = required_mapping(endpoint_preflight.get("summary"), "endpoint summary")
    migration_summary = required_mapping(migration_support.get("summary"), "migration summary")
    order_summary = required_mapping(order_sensitivity.get("summary"), "order summary")
    expected_endpoint = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "gate_status": ENDPOINT_GATE,
        "endpoint8_forced_by_current_evidence": False,
        "endpoint8_forcing_blocked_by_private_halo_escape": True,
        "blocking_escape_support_pairs": [PRIVATE_SUPPORT_PAIR],
        "private_halo_only_basic_survivor_count": 12,
        "private_halo_only_vertex_circle_survivor_count": 0,
        "all_selected_row_diagnostic_survivors_vertex_circle_obstructed": True,
    }
    expected_migration = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": 8,
        "conditional_center8_triple": CONDITIONAL_CENTER8_TARGET,
        "migration_status": MIGRATION_GATE,
        "support_requirement_center8_count": 0,
        "off_center_target_row_occurrence_count": 5,
        "off_center_rows_with_same_center_support_count": 3,
        "off_center_rows_at_unsupported_center_count": 2,
        "target_sparse_assignment_indices": [0, 11],
        "support_backing_supplies_center8_target": False,
        "current_evidence_proves_center_migration": False,
        "current_evidence_obstructs_target_sparse_assignments": False,
    }
    expected_order = {
        "target_row_key": TARGET_ROW_KEY,
        "source_miss_count": 3,
        "endpoint_rows": TARGET_SPARSE_ENDPOINT_ROWS,
        "natural_order_current_row_family_size_each": [255],
        "natural_order_potential_weight_sum_each": [250, 253, 243],
        "alternate_order": [0, 1, 2, 3, 4, 5, 7, 8, 6],
        "alternate_order_certificate_row_count_each": [10, 10, 9],
        "current_row_family_all_order_route_ready": False,
        "all_order_obstruction_proved": False,
        "target_sparse_obstruction_proved": False,
        "solves_n9": False,
        "solves_erdos97": False,
    }
    for key, expected in expected_endpoint.items():
        if endpoint_summary.get(key) != expected:
            errors.append(f"endpoint summary {key} mismatch")
    for key, expected in expected_migration.items():
        if migration_summary.get(key) != expected:
            errors.append(f"migration summary {key} mismatch")
    for key, expected in expected_order.items():
        if order_summary.get(key) != expected:
            errors.append(f"order summary {key} mismatch")

    route_decision = required_mapping(
        order_sensitivity.get("route_decision"), "order route decision"
    )
    if route_decision.get("answer") != ORDER_ROUTE_ANSWER:
        errors.append("order route decision answer mismatch")
    return errors


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert the pinned next-lemma obligations payload."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    endpoint_preflight_path: Path = ENDPOINT_PREFLIGHT_ARTIFACT,
    migration_support_path: Path = MIGRATION_SUPPORT_ARTIFACT,
    order_sensitivity_path: Path = ORDER_SENSITIVITY_ARTIFACT,
) -> list[str]:
    """Return validation errors for a next-lemma obligations payload."""

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
        return errors
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "validation_status": "passed",
        "validation_errors": [],
        "provenance": PROVENANCE,
    }
    for key, expected in expected_meta.items():
        if payload.get(key) != expected:
            errors.append(
                f"{key} mismatch: expected {expected!r}, got {payload.get(key)!r}"
            )
    validate_claim_scope(payload.get("claim_scope"), errors)
    validate_summary(payload.get("summary"), errors)
    validate_obligations(payload.get("obligations"), errors)
    validate_dead_end_guards(payload.get("dead_end_guards"), errors)
    validate_source_artifact_records(payload.get("source_artifacts"), errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("task-selection infrastructure only" in str(item) for item in interpretation):
        errors.append("interpretation must preserve task-selection scope")
    if recompute and not errors:
        generated = build_payload(
            endpoint_preflight_path=endpoint_preflight_path,
            migration_support_path=migration_support_path,
            order_sensitivity_path=order_sensitivity_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packets")
    return errors


def validate_claim_scope(raw: object, errors: list[str]) -> None:
    if not isinstance(raw, str):
        errors.append("claim_scope must be a string")
        return
    for phrase in (
        "Bridge-obligation contract",
        "exclude the private-halo pair [3,5] or force endpoint 8",
        "does not prove support existence",
        "does not prove center migration",
        "does not prove row forcing",
        "does not prove endpoint-8 forcing",
        "does not prove pair [3,5] impossible",
        "does not prove assignments 0 or 11 possible or impossible",
        "does not prove an all-order obstruction",
        "does not prove n=9",
        "does not prove the bootstrap bridge",
        "does not prove Erdos #97",
        "is not a counterexample",
        "not a global status update",
    ):
        if phrase not in raw:
            errors.append(f"claim_scope must contain {phrase!r}")


def validate_summary(raw: object, errors: list[str]) -> None:
    summary = mapping_or_error(raw, "summary", errors)
    expected = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target": CONDITIONAL_CENTER8_TARGET,
        "open_obligation_count": 3,
        "open_obligation_ids": [
            "private_halo_endpoint8_exclusion",
            "center8_migration_or_source",
            "target_sparse_order_or_geometry",
        ],
        "blocked_shortcut_count": 8,
        "endpoint8_forced_by_current_evidence": False,
        "private_halo_only_basic_survivor_count": 12,
        "private_halo_escape_status": "PRIVATE_HALO_ONLY_PAIR_3_5_REMAINS_OPEN",
        "migration_status": MIGRATION_GATE,
        "support_requirement_center8_count": 0,
        "off_center_target_row_occurrence_count": 5,
        "off_center_rows_with_same_center_support_count": 3,
        "off_center_rows_at_unsupported_center_count": 2,
        "target_sparse_assignment_indices": [0, 11],
        "target_sparse_endpoint_rows": TARGET_SPARSE_ENDPOINT_ROWS,
        "natural_order_current_row_family_size_each": [255],
        "natural_order_potential_weight_sum_each": [250, 253, 243],
        "alternate_order": [0, 1, 2, 3, 4, 5, 7, 8, 6],
        "alternate_order_certificate_row_count_each": [10, 10, 9],
        "current_row_family_all_order_route_ready": False,
        "all_order_obstruction_proved": False,
        "solves_n9": False,
        "solves_erdos97": False,
    }
    for key, expected_value in expected.items():
        if summary.get(key) != expected_value:
            errors.append(f"summary {key} mismatch")


def validate_obligations(raw: object, errors: list[str]) -> None:
    obligations = list_or_error(raw, "obligations", errors)
    expected_ids = [
        "private_halo_endpoint8_exclusion",
        "center8_migration_or_source",
        "target_sparse_order_or_geometry",
    ]
    observed_ids: list[str] = []
    for item in obligations:
        record = mapping_or_error(item, "obligation record", errors)
        obligation_id = str(record.get("obligation_id"))
        observed_ids.append(obligation_id)
        if record.get("status") != "open":
            errors.append(f"obligation {obligation_id} must remain open")
        not_satisfied = record.get("not_satisfied_by")
        if not isinstance(not_satisfied, list) or not not_satisfied:
            errors.append(f"obligation {obligation_id} needs not_satisfied_by guards")
        if "useful_success_criterion" not in record:
            errors.append(f"obligation {obligation_id} missing useful_success_criterion")
    if observed_ids != expected_ids:
        errors.append(f"obligation ids mismatch: {observed_ids!r}")


def validate_dead_end_guards(raw: object, errors: list[str]) -> None:
    guards = list_or_error(raw, "dead_end_guards", errors)
    if len(guards) != 8:
        errors.append("dead_end_guards must contain eight guards")
    required_phrases = (
        "endpoint-8 support is forced",
        "support existence",
        "center-8 migration",
        "source-151 row-8 singleton",
        "label-8 visibility",
        "realizable",
        "all-order obstruction",
        "same 255-row family",
    )
    guard_text = "\n".join(str(item) for item in guards)
    for phrase in required_phrases:
        if phrase not in guard_text:
            errors.append(f"dead_end_guards must mention {phrase!r}")


def validate_source_artifact_records(raw: object, errors: list[str]) -> None:
    records = list_or_error(raw, "source_artifacts", errors)
    expected_paths = [
        ENDPOINT_PREFLIGHT_ARTIFACT.as_posix(),
        MIGRATION_SUPPORT_ARTIFACT.as_posix(),
        ORDER_SENSITIVITY_ARTIFACT.as_posix(),
    ]
    observed_paths = [record.get("path") for record in records if isinstance(record, Mapping)]
    if observed_paths != expected_paths:
        errors.append(f"source artifact paths mismatch: {observed_paths!r}")


def source_record(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": path.as_posix(),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "validation_status": payload.get("validation_status"),
    }


def compact_summary(payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "open_obligation_count": summary.get("open_obligation_count"),
        "open_obligation_ids": summary.get("open_obligation_ids"),
        "private_halo_only_basic_survivor_count": summary.get(
            "private_halo_only_basic_survivor_count"
        ),
        "support_requirement_center8_count": summary.get(
            "support_requirement_center8_count"
        ),
        "target_sparse_endpoint_rows": summary.get("target_sparse_endpoint_rows"),
        "current_row_family_all_order_route_ready": summary.get(
            "current_row_family_all_order_route_ready"
        ),
        "all_order_obstruction_proved": summary.get("all_order_obstruction_proved"),
        "solves_n9": summary.get("solves_n9"),
        "solves_erdos97": summary.get("solves_erdos97"),
        "validation_errors": list(errors),
    }


def load_json(path: Path) -> Mapping[str, Any]:
    resolved = resolve_repo_path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    if Path.cwd().name == "scripts":
        return Path.cwd().parent / path
    return Path.cwd() / path


def write_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def required_mapping(raw: object, label: str) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        raise AssertionError(f"{label} must be an object")
    return raw


def mapping_or_error(raw: object, label: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(raw, Mapping):
        errors.append(f"{label} must be an object")
        return {}
    return raw


def list_or_error(raw: object, label: str, errors: list[str]) -> list[Any]:
    if not isinstance(raw, list):
        errors.append(f"{label} must be a list")
        return []
    return raw


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--endpoint-preflight", type=Path, default=ENDPOINT_PREFLIGHT_ARTIFACT)
    parser.add_argument("--migration-support", type=Path, default=MIGRATION_SUPPORT_ARTIFACT)
    parser.add_argument("--order-sensitivity", type=Path, default=ORDER_SENSITIVITY_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write deterministic JSON artifact")
    parser.add_argument("--check", action="store_true", help="compare stored artifact to regeneration")
    parser.add_argument("--assert-expected", action="store_true", help="accepted for checker parity")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    args = parser.parse_args()

    generated = build_payload(
        endpoint_preflight_path=args.endpoint_preflight,
        migration_support_path=args.migration_support,
        order_sensitivity_path=args.order_sensitivity,
    )
    artifact = resolve_repo_path(args.artifact)
    payload: Mapping[str, Any] = generated
    if args.write:
        write_json(generated, artifact)
    if args.check:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    errors = validate_payload(
        payload,
        endpoint_preflight_path=args.endpoint_preflight,
        migration_support_path=args.migration_support,
        order_sensitivity_path=args.order_sensitivity,
    )
    summary = compact_summary(payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 next lemma obligations")
        print(f"open obligations: {summary['open_obligation_ids']}")
        print(
            "current all-order route ready: "
            f"{summary['current_row_family_all_order_route_ready']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: next-lemma obligation contract verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
