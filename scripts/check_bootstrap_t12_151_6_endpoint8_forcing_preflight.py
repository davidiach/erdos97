#!/usr/bin/env python3
"""Check the bootstrap/T12 151:6 endpoint-8 forcing preflight packet."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from erdos97.json_io import write_json  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_outside_pair_escape_partition import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_ESCAPE_PARTITION,
    load_artifact,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_endpoint8_forcing_preflight.v1"
STATUS = "BOOTSTRAP_T12_151_6_ENDPOINT8_FORCING_PREFLIGHT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
GATE_STATUS = "NOT_READY_PRIVATE_HALO_ONLY_ESCAPE_SURVIVES_BASIC_FILTERS"
PRIVATE_ESCAPE_STATUS = "PRIVATE_HALO_ONLY_PAIR_3_5_REMAINS_OPEN"
CLAIM_SCOPE = (
    "Proof-mining preflight for the source-151 row-6 endpoint-8 outside-pair "
    "forcing question. It checks the current connector contract and escape "
    "partition and records that endpoint-8 support is not forced by current "
    "evidence because the private-halo-only pair [3,5] remains a live "
    "connector-avoiding support lane under basic incidence/crossing filters. "
    "This does not prove endpoint-8 support existence, does not prove row "
    "forcing, does not prove pair [3,5] impossible, does not prove n=9, does "
    "not prove the bridge, is not a counterexample, and is not a global status "
    "update."
)
PROVENANCE = {
    "generator": "scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py",
    "command": (
        "python scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py "
        "--write --assert-expected"
    ),
}

DEFAULT_SOURCE_CONNECTOR_CONTRACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_connector_contract.json"
)
DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_endpoint8_forcing_preflight.json"
)

SOURCE_CONNECTOR_CONTRACT_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_outside_pair_connector_contract.v1"
)
SOURCE_CONNECTOR_CONTRACT_STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_CONNECTOR_CONTRACT_DIAGNOSTIC_ONLY"
)
SOURCE_ESCAPE_PARTITION_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_outside_pair_escape_partition.v1"
)
SOURCE_ESCAPE_PARTITION_STATUS = (
    "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_ESCAPE_PARTITION_DIAGNOSTIC_ONLY"
)
SOURCE_ESCAPE_PARTITION_SCAN_STATUS = (
    "PRIVATE_HALO_ONLY_AND_ENDPOINT8_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"
)

TARGET_ROW_KEY = "151:6"
TARGET_CENTER = 6
BOOTSTRAP_CORE_WITNESSES = [0]
CONNECTOR_PAIR = [0, 8]
CONNECTOR_DISTANCE_PAIRS = [[0, 6], [8, 6]]
OUTSIDE_SUPPORT_PAIRS = [[3, 5], [3, 8], [5, 8]]
ENDPOINT8_SUPPORT_PAIRS = [[3, 8], [5, 8]]
PRIVATE_HALO_ONLY_SUPPORT_PAIRS = [[3, 5]]
PRIVATE_HALO_PARTITION = "private_halo_only_connector_avoiding"
ENDPOINT8_PARTITION = "endpoint8_connector_available"
MIXED_PARTITION = "mixed_private_and_endpoint8"

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
}


def build_endpoint8_forcing_preflight_payload(
    connector_contract: Mapping[str, Any],
    escape_partition: Mapping[str, Any],
    *,
    connector_contract_path: Path = DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    escape_partition_path: Path = DEFAULT_SOURCE_ESCAPE_PARTITION,
) -> dict[str, Any]:
    """Return the deterministic endpoint-8 forcing preflight payload."""

    errors: list[str] = []
    _validate_connector_contract(connector_contract, errors)
    _validate_escape_partition(escape_partition, errors)
    _validate_source_alignment(connector_contract, escape_partition, errors)

    summary = _summary(connector_contract, escape_partition)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Can current checked evidence accept the lemma that any genuine "
                "151:6 outside-pair support must include endpoint 8?"
            ),
            "answer": "do_not_accept_endpoint8_forcing_claim",
            "gate_status": GATE_STATUS,
            "endpoint8_forced_by_current_evidence": False,
            "can_use_connector_if_endpoint8_support_hypothesis_supplied": True,
            "blocking_escape_status": PRIVATE_ESCAPE_STATUS,
            "blocking_escape_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
            "blocking_basic_survivor_count": summary[
                "private_halo_only_basic_survivor_count"
            ],
            "required_next_lemma": summary["next_required_lemma"],
        },
        "interpretation": [
            (
                "The connector contract is useful only conditionally: if a "
                "genuine center-6 rich class contains witnesses 0 and 8, then "
                "the equality connector [0,6]=[8,6] is available."
            ),
            (
                "The current outside-pair ledger still has the connector-"
                "avoiding support pair [3,5]."
            ),
            (
                "The escape partition shows that private-halo-only rows survive "
                "basic filters, so endpoint-8 forcing is not justified by "
                "incidence/crossing evidence alone."
            ),
            (
                "The vertex-circle replay kills all selected-row diagnostic "
                "survivors, but it is not a support-existence or row-forcing "
                "lemma."
            ),
        ],
        "source_artifacts": [
            _source_summary(
                connector_contract_path,
                "source 151:6 outside-pair connector contract",
                connector_contract,
            ),
            _source_summary(
                escape_partition_path,
                "source 151:6 outside-pair escape partition",
                escape_partition,
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_endpoint8_forcing_preflight(payload)
    return payload


def assert_expected_endpoint8_forcing_preflight(payload: Mapping[str, Any]) -> None:
    """Assert the pinned endpoint-8 forcing preflight packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    connector_contract_path: Path = DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    escape_partition_path: Path = DEFAULT_SOURCE_ESCAPE_PARTITION,
) -> list[str]:
    """Return validation errors for an endpoint-8 forcing preflight payload."""

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
            "does not prove endpoint-8 support existence",
            "does not prove row forcing",
            "does not prove pair [3,5] impossible",
            "does not prove n=9",
            "does not prove the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)
    decision = _mapping(payload.get("decision"), "decision", errors)
    _validate_decision(decision, summary, errors)
    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("not a support-existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_endpoint8_forcing_preflight_payload(
            load_artifact(connector_contract_path),
            load_artifact(escape_partition_path),
            connector_contract_path=connector_contract_path,
            escape_partition_path=escape_partition_path,
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
        "gate_status": summary.get("gate_status"),
        "endpoint8_forced_by_current_evidence": summary.get(
            "endpoint8_forced_by_current_evidence"
        ),
        "blocking_escape_support_pairs": summary.get("blocking_escape_support_pairs"),
        "private_halo_only_basic_survivor_count": summary.get(
            "private_halo_only_basic_survivor_count"
        ),
        "private_halo_only_vertex_circle_survivor_count": summary.get(
            "private_halo_only_vertex_circle_survivor_count"
        ),
        "endpoint8_connector_available_basic_survivor_count": summary.get(
            "endpoint8_connector_available_basic_survivor_count"
        ),
        "decision_answer": decision.get("answer"),
        "validation_errors": list(errors),
    }


def _summary(
    connector_contract: Mapping[str, Any],
    escape_partition: Mapping[str, Any],
) -> dict[str, Any]:
    connector_summary = _required_mapping(
        connector_contract.get("summary"), "source connector summary"
    )
    partition_summary = _required_mapping(
        escape_partition.get("summary"), "source escape-partition summary"
    )
    private_basic = int(partition_summary["connector_avoiding_basic_survivor_count"])
    private_vertex = int(
        partition_summary["connector_avoiding_vertex_circle_survivor_count"]
    )
    endpoint_basic = int(partition_summary["connector_available_basic_survivor_count"])
    endpoint_vertex = int(
        partition_summary["connector_available_vertex_circle_survivor_count"]
    )
    return {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [151],
        "target_center": TARGET_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "endpoint8_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "blocking_escape_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "connector_contract_escape_status": connector_summary["escape_status"],
        "connector_contract_support_existence_status": connector_summary[
            "rich_support_existence_status"
        ],
        "connector_conditional_available": (
            connector_summary["local_conditional_lemma_status"]
            == "EXACT_LOCAL_CONDITIONAL"
        ),
        "private_halo_only_target_row_count": int(
            partition_summary["connector_avoiding_target_row_count"]
        ),
        "private_halo_only_basic_survivor_count": private_basic,
        "private_halo_only_vertex_circle_survivor_count": private_vertex,
        "endpoint8_connector_available_target_row_count": int(
            partition_summary["connector_available_target_row_count"]
        ),
        "endpoint8_connector_available_basic_survivor_count": endpoint_basic,
        "endpoint8_connector_available_vertex_circle_survivor_count": endpoint_vertex,
        "all_selected_row_diagnostic_survivors_vertex_circle_obstructed": (
            int(partition_summary["vertex_circle_surviving_assignment_count"]) == 0
        ),
        "source_escape_partition_scan_status": partition_summary["scan_status"],
        "gate_status": GATE_STATUS,
        "endpoint8_forced_by_current_evidence": False,
        "endpoint8_forcing_blocked_by_private_halo_escape": private_basic > 0,
        "private_halo_escape_status": PRIVATE_ESCAPE_STATUS,
        "preflight_reasons": [
            "The endpoint-8 support pairs [3,8] and [5,8] would supply the connector conditionally.",
            "The connector-avoiding support pair [3,5] still exists in the outside-pair ledger.",
            "The private-halo-only lane has 12 complete assignments after basic filters.",
            "Vertex-circle replay kills those selected-row assignments but does not prove support existence or row forcing.",
        ],
        "next_required_lemma": (
            "Prove under genuine minimal/rich-class hypotheses that endpoint 8 "
            "is forced in the outside-pair support, or prove that the "
            "private-halo-only pair [3,5] cannot occur."
        ),
    }


def _validate_connector_contract(
    payload: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_CONNECTOR_CONTRACT_SCHEMA,
        "status": SOURCE_CONNECTOR_CONTRACT_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("connector contract", payload, expected, errors)
    summary = _mapping(payload.get("summary"), "connector contract summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [151],
        "target_row_center": TARGET_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "connector_forcing_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "connector_avoiding_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "local_conditional_lemma_status": "EXACT_LOCAL_CONDITIONAL",
        "rich_support_existence_status": "OPEN_TARGET_NOT_PROVED",
        "escape_status": "CONNECTOR_ESCAPE_REQUIRES_PRIVATE_HALO_ONLY_PAIR_3_5",
    }
    _expect_fields("connector contract summary", summary, expected_summary, errors)


def _validate_escape_partition(
    payload: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_ESCAPE_PARTITION_SCHEMA,
        "status": SOURCE_ESCAPE_PARTITION_STATUS,
        "trust": TRUST,
    }
    _validate_source_meta("escape partition", payload, expected, errors)
    summary = _mapping(payload.get("summary"), "escape partition summary", errors)
    if not summary:
        return
    expected_summary = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [151],
        "target_center": TARGET_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "connector_avoiding_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "connector_forcing_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "connector_avoiding_target_row_count": 4,
        "connector_available_target_row_count": 9,
        "connector_avoiding_basic_survivor_count": 12,
        "connector_available_basic_survivor_count": 16,
        "connector_avoiding_vertex_circle_survivor_count": 0,
        "connector_available_vertex_circle_survivor_count": 0,
        "vertex_circle_surviving_assignment_count": 0,
        "scan_status": SOURCE_ESCAPE_PARTITION_SCAN_STATUS,
    }
    _expect_fields("escape partition summary", summary, expected_summary, errors)


def _validate_source_alignment(
    connector_contract: Mapping[str, Any],
    escape_partition: Mapping[str, Any],
    errors: list[str],
) -> None:
    connector_summary = _mapping(
        connector_contract.get("summary"), "connector contract summary", errors
    )
    partition_summary = _mapping(
        escape_partition.get("summary"), "escape partition summary", errors
    )
    if not connector_summary or not partition_summary:
        return
    pairs = (
        ("target_row_key", "target_row_key"),
        ("source_record_ids", "source_record_ids"),
        ("target_row_center", "target_center"),
        ("bootstrap_core_witnesses", "bootstrap_core_witnesses"),
        ("outside_support_pairs", "outside_support_pairs"),
        ("connector_avoiding_support_pairs", "connector_avoiding_support_pairs"),
        ("connector_forcing_support_pairs", "connector_forcing_support_pairs"),
    )
    for left_key, right_key in pairs:
        if connector_summary.get(left_key) != partition_summary.get(right_key):
            errors.append(
                "source alignment mismatch: "
                f"connector.{left_key} != partition.{right_key}"
            )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    pinned = {
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [151],
        "target_center": TARGET_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "endpoint8_support_pairs": ENDPOINT8_SUPPORT_PAIRS,
        "blocking_escape_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "connector_contract_escape_status": (
            "CONNECTOR_ESCAPE_REQUIRES_PRIVATE_HALO_ONLY_PAIR_3_5"
        ),
        "connector_contract_support_existence_status": "OPEN_TARGET_NOT_PROVED",
        "connector_conditional_available": True,
        "private_halo_only_target_row_count": 4,
        "private_halo_only_basic_survivor_count": 12,
        "private_halo_only_vertex_circle_survivor_count": 0,
        "endpoint8_connector_available_target_row_count": 9,
        "endpoint8_connector_available_basic_survivor_count": 16,
        "endpoint8_connector_available_vertex_circle_survivor_count": 0,
        "all_selected_row_diagnostic_survivors_vertex_circle_obstructed": True,
        "source_escape_partition_scan_status": SOURCE_ESCAPE_PARTITION_SCAN_STATUS,
        "gate_status": GATE_STATUS,
        "endpoint8_forced_by_current_evidence": False,
        "endpoint8_forcing_blocked_by_private_halo_escape": True,
        "private_halo_escape_status": PRIVATE_ESCAPE_STATUS,
    }
    for key, expected in pinned.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )
    reasons = summary.get("preflight_reasons")
    if not isinstance(reasons, list) or len(reasons) != 4:
        errors.append("summary.preflight_reasons must contain four reasons")
    elif not any("[3,5]" in reason for reason in reasons):
        errors.append("summary.preflight_reasons must name [3,5]")
    next_required = summary.get("next_required_lemma")
    if not isinstance(next_required, str) or "[3,5]" not in next_required:
        errors.append("summary.next_required_lemma must name the [3,5] escape")


def _validate_decision(
    decision: Mapping[str, Any],
    summary: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "answer": "do_not_accept_endpoint8_forcing_claim",
        "gate_status": GATE_STATUS,
        "endpoint8_forced_by_current_evidence": False,
        "can_use_connector_if_endpoint8_support_hypothesis_supplied": True,
        "blocking_escape_status": PRIVATE_ESCAPE_STATUS,
        "blocking_escape_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "blocking_basic_survivor_count": summary.get(
            "private_halo_only_basic_survivor_count"
        ),
        "required_next_lemma": summary.get("next_required_lemma"),
    }
    _expect_fields("decision", decision, expected, errors)
    question = decision.get("decision_question")
    if not isinstance(question, str) or "endpoint 8" not in question:
        errors.append("decision.decision_question must name endpoint 8")


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
    }


def _validate_source_meta(
    label: str,
    source: Mapping[str, Any],
    expected: Mapping[str, str],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if source.get(key) != expected_value:
            errors.append(
                f"{label} {key} mismatch: expected {expected_value!r}, "
                f"got {source.get(key)!r}"
            )


def _expect_fields(
    label: str,
    mapping: Mapping[str, Any],
    expected: Mapping[str, object],
    errors: list[str],
) -> None:
    for key, expected_value in expected.items():
        if mapping.get(key) != expected_value:
            errors.append(
                f"{label}.{key} mismatch: expected {expected_value!r}, "
                f"got {mapping.get(key)!r}"
            )


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
        "--source-connector-contract",
        type=Path,
        default=DEFAULT_SOURCE_CONNECTOR_CONTRACT,
    )
    parser.add_argument(
        "--source-escape-partition",
        type=Path,
        default=DEFAULT_SOURCE_ESCAPE_PARTITION,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_connector_contract = _resolve(args.source_connector_contract)
    source_escape_partition = _resolve(args.source_escape_partition)

    generated = build_endpoint8_forcing_preflight_payload(
        load_artifact(source_connector_contract),
        load_artifact(source_escape_partition),
        connector_contract_path=source_connector_contract,
        escape_partition_path=source_escape_partition,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        connector_contract_path=source_connector_contract,
        escape_partition_path=source_escape_partition,
    )
    if args.assert_expected:
        assert_expected_endpoint8_forcing_preflight(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 endpoint-8 forcing preflight")
        print(f"target row: {summary['target_row_key']}")
        print(f"gate status: {summary['gate_status']}")
        print(
            "endpoint-8 forced by current evidence: "
            f"{summary['endpoint8_forced_by_current_evidence']}"
        )
        print(
            "private-halo-only basic survivors: "
            f"{summary['private_halo_only_basic_survivor_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: 151:6 endpoint-8 forcing preflight verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
