#!/usr/bin/env python3
"""Check the center-8 rich-triple forcing preflight for the 151:6 cascade."""

from __future__ import annotations

import argparse
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_endpoint8_forcing_preflight import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT,
    GATE_STATUS as SOURCE_ENDPOINT8_FORCING_GATE_STATUS,
    SCHEMA as SOURCE_ENDPOINT8_FORCING_SCHEMA,
    STATUS as SOURCE_ENDPOINT8_FORCING_STATUS,
    assert_expected_endpoint8_forcing_preflight,
)
from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    SCHEMA as SOURCE_CASCADE_ENDPOINT8_SCHEMA,
    STATUS as SOURCE_CASCADE_ENDPOINT8_STATUS,
    TARGET_STATUS as SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    assert_expected_cascade_endpoint8_targets,
)
from scripts.check_bootstrap_t12_151_6_label4_cascade_row_criticality import (  # noqa: E402
    CASCADE_COMPONENT_KEY,
    REQUIRED_CORE_CENTERS,
)
from scripts.check_bootstrap_t12_151_6_label4_support_hypothesis_ledger import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SUPPORT_LEDGER,
    LEDGER_STATUS as SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY,
    SCHEMA as SOURCE_SUPPORT_LEDGER_SCHEMA,
    STATUS as SOURCE_SUPPORT_LEDGER_STATUS,
    assert_expected_support_hypothesis_ledger,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_rich_triple_preflight.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_RICH_TRIPLE_PREFLIGHT_DIAGNOSTIC_ONLY"
)
GATE_STATUS = "NOT_READY_NO_CENTER8_RICH_TRIPLE_SOURCE"
DECISION_STATUS = "CENTER8_RICH_TRIPLE_NOT_FORCED_BY_CURRENT_SUPPORT_LEDGER"
CLAIM_SCOPE = (
    "Proof-mining preflight for the source-151 row-6 label-4 cascade. It "
    "joins the label-4 support-hypothesis ledger, the cascade endpoint-8 "
    "target packet, and the older endpoint-8 outside-pair forcing preflight "
    "to check whether current checked evidence already supplies the new "
    "center-8 rich-class target [0,4,6]. It records that the target is a "
    "conditional quotient obstruction but is not forced by the current "
    "support ledger: there is no centered support requirement at center 8, "
    "and no current support requirement contains the full center-8 triple. "
    "This does not prove support existence, does not prove row forcing, does "
    "not prove endpoint-8 forcing, does not prove that pair [3,5] is "
    "impossible, does not prove n=9, does not prove the bootstrap bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_rich_triple_preflight.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "endpoint8_distinction_records",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "support_requirement_audit",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "cascade_component_key": CASCADE_COMPONENT_KEY,
    "cascade_required_support_centers": [5, 6],
    "cascade_required_witness_pairs": [[4, 6], [0, 5]],
    "required_core_centers": REQUIRED_CORE_CENTERS,
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "conditional_target_status": SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    "conditional_rich_superset_signature_record_count": 93,
    "conditional_rich_superset_obstructed_count": 93,
    "support_ledger_status": SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY,
    "support_requirement_centers": [5, 6, 7],
    "support_requirement_center8_count": 0,
    "support_requirements_with_label8_witness_count": 0,
    "center8_requirement_with_full_triple_count": 0,
    "endpoint_triple_pair_requirements_any_center": [[0, 4], [4, 6]],
    "endpoint_triple_pair_requirements_at_center8": [],
    "endpoint_triple_pair_requirements_missing_any_center": [[0, 6]],
    "components_with_center8_auxiliary_center_count": 1,
    "center8_auxiliary_pair_is_not_center8_support_requirement": True,
    "outside_pair_endpoint8_preflight_target_center": 6,
    "outside_pair_endpoint8_support_pairs": [[3, 8], [5, 8]],
    "outside_pair_endpoint8_gate_status": SOURCE_ENDPOINT8_FORCING_GATE_STATUS,
    "current_evidence_forces_center8_rich_triple": False,
    "gate_status": GATE_STATUS,
    "decision_status": DECISION_STATUS,
}


def load_artifact(path: Path) -> dict[str, Any]:
    """Load a JSON artifact."""

    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise ValueError(f"{display_path(path, ROOT)} must contain a JSON object")
    return payload


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_center8_rich_triple_preflight_payload(
    support_ledger: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    endpoint8_forcing_preflight: Mapping[str, Any],
    *,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    endpoint8_forcing_preflight_path: Path = DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT,
) -> dict[str, Any]:
    """Return the deterministic center-8 rich-triple preflight payload."""

    errors: list[str] = []
    assert_expected_support_hypothesis_ledger(support_ledger)
    assert_expected_cascade_endpoint8_targets(cascade_endpoint8_targets)
    assert_expected_endpoint8_forcing_preflight(endpoint8_forcing_preflight)
    _validate_sources(support_ledger, cascade_endpoint8_targets, endpoint8_forcing_preflight, errors)

    summary, support_audit = _summary_and_support_audit(
        support_ledger,
        cascade_endpoint8_targets,
        endpoint8_forcing_preflight,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Can current checked support evidence accept the claim that "
                "the source-151 row-6 label-4 cascade forces a genuine "
                "center-8 rich class containing [0,4,6]?"
            ),
            "answer": "do_not_accept_center8_rich_triple_forcing_claim",
            "gate_status": GATE_STATUS,
            "decision_status": DECISION_STATUS,
            "current_evidence_forces_center8_rich_triple": False,
            "conditional_obstruction_available_if_hypothesis_supplied": True,
            "blocking_reason": (
                "The current label-4 support ledger has requirements at "
                "centers 5, 6, and 7 only; it has no centered support "
                "requirement at center 8 and no support requirement "
                "containing the full witness triple [0,4,6]."
            ),
            "required_next_lemma": (
                "Prove from genuine minimal/rich-class geometry that center "
                "8 has a rich class containing [0,4,6] alongside the row-5/"
                "row-6 cascade package, or find a different support-rich "
                "obstruction."
            ),
        },
        "support_requirement_audit": support_audit,
        "endpoint8_distinction_records": _endpoint8_distinction_records(
            endpoint8_forcing_preflight,
            cascade_endpoint8_targets,
        ),
        "interpretation": [
            (
                "The cascade endpoint-target packet proves a conditional "
                "local obstruction: every center-8 rich class containing "
                "[0,4,6] obstructs the stored row-5/row-6 cascade packages."
            ),
            (
                "The label-4 support ledger does not supply that center-8 "
                "rich class; its centered support requirements live at "
                "centers 5, 6, and 7."
            ),
            (
                "The phrase endpoint-8 appears in two different proof "
                "targets: an older center-6 outside-pair support target "
                "using witness 8, and the newer center-8 rich-triple target."
            ),
            (
                "Current checked evidence therefore identifies a sharp "
                "conditional target, not a forcing lemma."
            ),
        ],
        "source_artifacts": [
            _source_summary(
                support_ledger_path,
                "source 151:6 label-4 support-hypothesis ledger",
                support_ledger,
            ),
            _source_summary(
                cascade_endpoint8_targets_path,
                "source 151:6 label-4 cascade endpoint-8 targets",
                cascade_endpoint8_targets,
            ),
            _source_summary(
                endpoint8_forcing_preflight_path,
                "source 151:6 endpoint-8 outside-pair forcing preflight",
                endpoint8_forcing_preflight,
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_rich_triple_preflight(payload)
    return payload


def assert_expected_center8_rich_triple_preflight(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned center-8 rich-triple preflight packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    endpoint8_forcing_preflight_path: Path = DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT,
) -> list[str]:
    """Return validation errors for a center-8 rich-triple preflight payload."""

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

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        for phrase in (
            "current checked evidence already supplies the new center-8 rich-class target [0,4,6]",
            "not forced by the current support ledger",
            "no centered support requirement at center 8",
            "does not prove support existence",
            "does not prove row forcing",
            "does not prove endpoint-8 forcing",
            "does not prove that pair [3,5] is impossible",
            "does not prove n=9",
            "does not prove the bootstrap bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    decision = _mapping(payload.get("decision"), "decision", errors)
    _validate_decision(decision, errors)
    support_audit = payload.get("support_requirement_audit")
    if not isinstance(support_audit, list):
        errors.append("support_requirement_audit must be a list")
    else:
        _validate_support_audit(support_audit, errors)
    distinction = payload.get("endpoint8_distinction_records")
    if not isinstance(distinction, list):
        errors.append("endpoint8_distinction_records must be a list")
    else:
        _validate_endpoint8_distinction(distinction, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("not a forcing lemma" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the forcing nonclaim")

    if recompute and not errors:
        generated = build_center8_rich_triple_preflight_payload(
            load_artifact(support_ledger_path),
            load_artifact(cascade_endpoint8_targets_path),
            load_artifact(endpoint8_forcing_preflight_path),
            support_ledger_path=support_ledger_path,
            cascade_endpoint8_targets_path=cascade_endpoint8_targets_path,
            endpoint8_forcing_preflight_path=endpoint8_forcing_preflight_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source packets")
    return errors


def summary_payload(
    path: Path,
    payload: Mapping[str, Any],
    errors: Sequence[str],
) -> dict[str, Any]:
    """Return a compact CLI summary."""

    summary = payload.get("summary", {})
    if not isinstance(summary, Mapping):
        summary = {}
    decision = payload.get("decision", {})
    if not isinstance(decision, Mapping):
        decision = {}
    return {
        "artifact": display_path(path, ROOT),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "conditional_center8_target_center": summary.get(
            "conditional_center8_target_center"
        ),
        "conditional_center8_triple": summary.get("conditional_center8_triple"),
        "support_requirement_center8_count": summary.get(
            "support_requirement_center8_count"
        ),
        "center8_requirement_with_full_triple_count": summary.get(
            "center8_requirement_with_full_triple_count"
        ),
        "gate_status": summary.get("gate_status"),
        "decision_answer": decision.get("answer"),
        "validation_errors": list(errors),
    }


def _summary_and_support_audit(
    support_ledger: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    endpoint8_forcing_preflight: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    support_summary = _required_mapping(
        support_ledger.get("summary"), "support ledger summary"
    )
    endpoint_target_summary = _required_mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint target summary"
    )
    endpoint8_preflight_summary = _required_mapping(
        endpoint8_forcing_preflight.get("summary"), "endpoint-8 preflight summary"
    )
    requirements = _requirement_records(support_ledger)
    center8_requirements = [
        record for record in requirements if int(record["center"]) == ENDPOINT_CENTER
    ]
    requirements_with_label8 = [
        record for record in requirements if bool(record.get("label8_as_witness"))
    ]
    endpoint_pairs = [list(pair) for pair in combinations(ENDPOINT_TRIPLE, 2)]
    endpoint_pair_records = [
        record
        for record in requirements
        if sorted(record["witness_pair"]) in endpoint_pairs
    ]
    endpoint_pair_records_at_center8 = [
        record for record in endpoint_pair_records if int(record["center"]) == 8
    ]
    endpoint_pairs_any_center = _unique_pairs(
        record["witness_pair"] for record in endpoint_pair_records
    )
    endpoint_pairs_at_center8 = _unique_pairs(
        record["witness_pair"] for record in endpoint_pair_records_at_center8
    )
    missing_pairs_any_center = [
        pair for pair in endpoint_pairs if pair not in endpoint_pairs_any_center
    ]

    support_audit = [
        {
            "audit_question": (
                "Does the current label-4 support ledger contain any centered "
                "support requirement at center 8?"
            ),
            "answer": False,
            "matching_requirement_keys": [],
            "matching_requirement_count": len(center8_requirements),
        },
        {
            "audit_question": (
                "Does the current label-4 support ledger contain any support "
                "requirement whose center is 8 and whose witnesses include "
                "the full target triple [0,4,6]?"
            ),
            "answer": False,
            "matching_requirement_keys": [],
            "matching_requirement_count": 0,
        },
        {
            "audit_question": (
                "Which endpoint-triple witness pairs appear anywhere in the "
                "current support ledger?"
            ),
            "answer": "partial_pair_coverage_only",
            "covered_pairs_any_center": endpoint_pairs_any_center,
            "covered_pairs_at_center8": endpoint_pairs_at_center8,
            "missing_pairs_any_center": missing_pairs_any_center,
            "matching_requirement_keys": [
                str(record["requirement_key"]) for record in endpoint_pair_records
            ],
        },
        {
            "audit_question": (
                "Does the current label-4 support ledger use label 8 as a "
                "support witness?"
            ),
            "answer": False,
            "matching_requirement_keys": [
                str(record["requirement_key"]) for record in requirements_with_label8
            ],
            "matching_requirement_count": len(requirements_with_label8),
        },
    ]
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "cascade_component_key": CASCADE_COMPONENT_KEY,
        "cascade_required_support_centers": list(
            support_summary["cascade_required_support_centers"]
        ),
        "cascade_required_witness_pairs": list(
            support_summary["cascade_required_witness_pairs"]
        ),
        "required_core_centers": REQUIRED_CORE_CENTERS,
        "conditional_center8_target_center": int(
            endpoint_target_summary["endpoint_center"]
        ),
        "conditional_center8_triple": list(endpoint_target_summary["endpoint_triple"]),
        "conditional_target_status": endpoint_target_summary["target_status"],
        "conditional_rich_superset_signature_record_count": int(
            endpoint_target_summary["rich_superset_signature_record_count"]
        ),
        "conditional_rich_superset_obstructed_count": int(
            endpoint_target_summary["rich_superset_obstructed_count"]
        ),
        "support_ledger_status": support_summary["ledger_status"],
        "support_requirement_centers": sorted(
            int(center)
            for center in support_summary["unique_support_requirement_count_by_center"]
        ),
        "support_requirement_center8_count": len(center8_requirements),
        "support_requirements_with_label8_witness_count": len(requirements_with_label8),
        "center8_requirement_with_full_triple_count": 0,
        "endpoint_triple_pair_requirements_any_center": endpoint_pairs_any_center,
        "endpoint_triple_pair_requirements_at_center8": endpoint_pairs_at_center8,
        "endpoint_triple_pair_requirements_missing_any_center": missing_pairs_any_center,
        "components_with_center8_auxiliary_center_count": int(
            support_summary["components_with_center8_auxiliary_center_count"]
        ),
        "center8_auxiliary_pair_is_not_center8_support_requirement": (
            len(center8_requirements) == 0
        ),
        "outside_pair_endpoint8_preflight_target_center": int(
            endpoint8_preflight_summary["target_center"]
        ),
        "outside_pair_endpoint8_support_pairs": list(
            endpoint8_preflight_summary["endpoint8_support_pairs"]
        ),
        "outside_pair_endpoint8_gate_status": endpoint8_preflight_summary[
            "gate_status"
        ],
        "current_evidence_forces_center8_rich_triple": False,
        "gate_status": GATE_STATUS,
        "decision_status": DECISION_STATUS,
    }
    return summary, support_audit


def _endpoint8_distinction_records(
    endpoint8_forcing_preflight: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
) -> list[dict[str, Any]]:
    endpoint8_preflight_summary = _required_mapping(
        endpoint8_forcing_preflight.get("summary"), "endpoint-8 preflight summary"
    )
    endpoint_target_summary = _required_mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint target summary"
    )
    return [
        {
            "target_name": "endpoint-8 outside-pair support",
            "source_doc": "docs/bootstrap-t12-151-6-endpoint8-forcing-preflight.md",
            "row_center": endpoint8_preflight_summary["target_center"],
            "uses_label_8_as_witness": True,
            "support_pairs": endpoint8_preflight_summary["endpoint8_support_pairs"],
            "conditional_supply": "center-6 support with witnesses 0 and 8 supplies [0,6]=[8,6]",
            "gate_status": endpoint8_preflight_summary["gate_status"],
            "forced_by_current_evidence": endpoint8_preflight_summary[
                "endpoint8_forced_by_current_evidence"
            ],
        },
        {
            "target_name": "center-8 rich-triple row target",
            "source_doc": (
                "docs/bootstrap-t12-151-6-label4-cascade-endpoint8-targets.md"
            ),
            "row_center": endpoint_target_summary["endpoint_center"],
            "uses_label_8_as_center": True,
            "witness_triple": endpoint_target_summary["endpoint_triple"],
            "conditional_supply": (
                "center-8 rich class containing [0,4,6] obstructs the stored "
                "row-5/row-6 cascade packages"
            ),
            "target_status": endpoint_target_summary["target_status"],
            "forced_by_current_evidence": False,
        },
    ]


def _validate_sources(
    support_ledger: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    endpoint8_forcing_preflight: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = [
        (
            "support ledger",
            support_ledger,
            SOURCE_SUPPORT_LEDGER_SCHEMA,
            SOURCE_SUPPORT_LEDGER_STATUS,
        ),
        (
            "cascade endpoint target",
            cascade_endpoint8_targets,
            SOURCE_CASCADE_ENDPOINT8_SCHEMA,
            SOURCE_CASCADE_ENDPOINT8_STATUS,
        ),
        (
            "endpoint-8 forcing preflight",
            endpoint8_forcing_preflight,
            SOURCE_ENDPOINT8_FORCING_SCHEMA,
            SOURCE_ENDPOINT8_FORCING_STATUS,
        ),
    ]
    for label, payload, schema, status in expected:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")
    support_summary = _mapping(support_ledger.get("summary"), "support summary", errors)
    if support_summary.get("ledger_status") != SOURCE_SUPPORT_LEDGER_STATUS_SUMMARY:
        errors.append("support ledger status mismatch")
    endpoint_target_summary = _mapping(
        cascade_endpoint8_targets.get("summary"), "endpoint target summary", errors
    )
    if endpoint_target_summary.get("target_status") != SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS:
        errors.append("cascade endpoint target status mismatch")
    endpoint8_summary = _mapping(
        endpoint8_forcing_preflight.get("summary"),
        "endpoint-8 forcing summary",
        errors,
    )
    if endpoint8_summary.get("gate_status") != SOURCE_ENDPOINT8_FORCING_GATE_STATUS:
        errors.append("endpoint-8 forcing gate status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "do_not_accept_center8_rich_triple_forcing_claim",
        "gate_status": GATE_STATUS,
        "decision_status": DECISION_STATUS,
        "current_evidence_forces_center8_rich_triple": False,
        "conditional_obstruction_available_if_hypothesis_supplied": True,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    question = decision.get("decision_question")
    if not isinstance(question, str) or "center-8 rich class" not in question:
        errors.append("decision.decision_question must name the center-8 target")
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "[0,4,6]" not in required_next:
        errors.append("decision.required_next_lemma must name [0,4,6]")


def _validate_support_audit(
    support_audit: Sequence[object],
    errors: list[str],
) -> None:
    if len(support_audit) != 4:
        errors.append("support_requirement_audit must contain four records")
        return
    expected_answers = [False, False, "partial_pair_coverage_only", False]
    for index, expected_answer in enumerate(expected_answers):
        record = support_audit[index]
        if not isinstance(record, Mapping):
            errors.append(f"support_requirement_audit[{index}] must be an object")
            continue
        if record.get("answer") != expected_answer:
            errors.append(
                f"support_requirement_audit[{index}].answer mismatch: "
                f"expected {expected_answer!r}, got {record.get('answer')!r}"
            )
    pair_record = support_audit[2]
    if isinstance(pair_record, Mapping):
        if pair_record.get("covered_pairs_any_center") != [[0, 4], [4, 6]]:
            errors.append("support audit endpoint-pair coverage mismatch")
        if pair_record.get("covered_pairs_at_center8") != []:
            errors.append("support audit center-8 endpoint-pair coverage mismatch")
        if pair_record.get("missing_pairs_any_center") != [[0, 6]]:
            errors.append("support audit missing endpoint-pair mismatch")


def _validate_endpoint8_distinction(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 2:
        errors.append("endpoint8_distinction_records must contain two records")
        return
    names = [record.get("target_name") for record in records if isinstance(record, Mapping)]
    if names != ["endpoint-8 outside-pair support", "center-8 rich-triple row target"]:
        errors.append(f"endpoint8 distinction names mismatch: got {names!r}")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"endpoint8_distinction_records[{index}] must be an object")
            continue
        if record.get("forced_by_current_evidence") is not False:
            errors.append(
                f"endpoint8_distinction_records[{index}] must keep forcing open"
            )


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        summary = {}
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "target_status": summary.get("target_status"),
        "gate_status": summary.get("gate_status"),
        "ledger_status": summary.get("ledger_status"),
    }


def _requirement_records(payload: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    raw_records = payload.get("support_requirement_records")
    if not isinstance(raw_records, list):
        raise AssertionError("support_requirement_records must be a list")
    records: list[Mapping[str, Any]] = []
    for record in raw_records:
        if not isinstance(record, Mapping):
            raise AssertionError("support requirement record must be an object")
        records.append(record)
    return records


def _unique_pairs(pairs: Sequence[object]) -> list[list[int]]:
    unique = {tuple(sorted(int(item) for item in pair)) for pair in pairs}
    return [list(pair) for pair in sorted(unique)]


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _required_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"{name} must be an object")
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-support-ledger",
        type=Path,
        default=DEFAULT_SOURCE_SUPPORT_LEDGER,
    )
    parser.add_argument(
        "--source-cascade-endpoint8-targets",
        type=Path,
        default=DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    )
    parser.add_argument(
        "--source-endpoint8-forcing-preflight",
        type=Path,
        default=DEFAULT_SOURCE_ENDPOINT8_FORCING_PREFLIGHT,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_support_ledger = _resolve(args.source_support_ledger)
    source_cascade_endpoint8_targets = _resolve(args.source_cascade_endpoint8_targets)
    source_endpoint8_forcing_preflight = _resolve(
        args.source_endpoint8_forcing_preflight
    )

    generated = build_center8_rich_triple_preflight_payload(
        load_artifact(source_support_ledger),
        load_artifact(source_cascade_endpoint8_targets),
        load_artifact(source_endpoint8_forcing_preflight),
        support_ledger_path=source_support_ledger,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
        endpoint8_forcing_preflight_path=source_endpoint8_forcing_preflight,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        support_ledger_path=source_support_ledger,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
        endpoint8_forcing_preflight_path=source_endpoint8_forcing_preflight,
    )
    if args.assert_expected:
        assert_expected_center8_rich_triple_preflight(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 rich-triple preflight")
        print(f"target row: {summary['target_row_key']}")
        print(
            "center-8 target: "
            f"{summary['conditional_center8_triple']} at center "
            f"{summary['conditional_center8_target_center']}"
        )
        print(
            "center-8 support requirements: "
            f"{summary['support_requirement_center8_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 rich-triple preflight verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
