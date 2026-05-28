"""Outside-pair connector contract for the bootstrap/T12 151:6 target.

This packet is the source-151 analogue of the 81:3 rich-triple contract.  It
records the exact local conditional needed by the T12/F16 equality connector:
at center 6, a genuine rich class containing witnesses 0 and 8 supplies the
connector equality [0,6]=[8,6].  It also partitions the three outside-pair
supports from the row-pressure packet into connector-forcing supports and the
private-halo-only connector escape.

The packet is diagnostic bookkeeping only.  It does not prove that any support
exists or that row 151:6 is forced.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_outside_pair import (
    DEFAULT_ARTIFACT as OUTSIDE_PAIR_ARTIFACT,
    LEDGER_HIT_MODE,
    PRIVATE_HALO_ONLY_MODE,
    SCHEMA as OUTSIDE_PAIR_SCHEMA,
    STATUS as OUTSIDE_PAIR_STATUS,
    TRUST as OUTSIDE_PAIR_TRUST,
    build_t12_outside_pair_payload,
)
from erdos97.bootstrap_t12_relation_sufficient_rows import (
    DEFAULT_ARTIFACT as RELATION_SUFFICIENT_ARTIFACT,
    GAP_OUTSIDE_PAIR_SUPPORT,
    SCHEMA as RELATION_SUFFICIENT_SCHEMA,
    STATUS as RELATION_SUFFICIENT_STATUS,
    TRUST as RELATION_SUFFICIENT_TRUST,
    build_t12_relation_sufficient_rows_payload,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_outside_pair_connector_contract.v1"
STATUS = "BOOTSTRAP_T12_151_6_OUTSIDE_PAIR_CONNECTOR_CONTRACT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused local connector contract for source 151 row 6: any genuine rich "
    "class at center 6 that contains witnesses 0 and 8 supplies the T12/F16 "
    "equality connector [0,6]=[8,6]. This proves only that exact local "
    "conditional and partitions the outside-pair support options into "
    "connector-forcing supports and a connector-avoiding private-halo-only "
    "escape; it does not prove support existence, does not prove row forcing, "
    "does not prove n=9, does not prove the bridge, and does not claim a "
    "counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_outside_pair_connector_contract.json"
)

TARGET_SOURCE_RECORD_ID = 151
TARGET_ROW_CENTER = 6
TARGET_ROW_KEY = "151:6"
TARGET_WITNESSES = [0, 3, 5, 8]
BOOTSTRAP_CORE_WITNESSES = [0]
CONNECTOR_ENDPOINT = 8
CONNECTOR_PAIR = [0, 8]
CONNECTOR_DISTANCE_PAIRS = [[0, 6], [8, 6]]
OUTSIDE_SUPPORT_PAIRS = [[3, 5], [3, 8], [5, 8]]
CONNECTOR_FORCING_SUPPORT_PAIRS = [[3, 8], [5, 8]]
CONNECTOR_AVOIDING_SUPPORT_PAIRS = [[3, 5]]
LEDGER_HIT_SUPPORT_PAIRS = [[3, 8], [5, 8]]
PRIVATE_HALO_ONLY_SUPPORT_PAIRS = [[3, 5]]
TARGET_REQUIREMENT_ID = "151:6:connector:2:0"
LOCAL_CONDITIONAL_STATUS = "EXACT_LOCAL_CONDITIONAL"
RICH_SUPPORT_EXISTENCE_STATUS = "OPEN_TARGET_NOT_PROVED"
ESCAPE_STATUS = "CONNECTOR_ESCAPE_REQUIRES_PRIVATE_HALO_ONLY_PAIR_3_5"
CONNECTOR_CONTRACT_GAP = "OUTSIDE_PAIR_CONNECTOR_CONTRACT_NOT_SUPPORT_EXISTENCE"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _target_outside_pair_record(
    outside_pair_payload: Mapping[str, Any],
) -> dict[str, Any]:
    records = outside_pair_payload.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("outside-pair payload records must be a sequence")
    matches = [
        record
        for record in records
        if int(record["source_record_id"]) == TARGET_SOURCE_RECORD_ID
        and int(record["row_center"]) == TARGET_ROW_CENTER
    ]
    if len(matches) != 1:
        raise AssertionError("expected exactly one 151:6 outside-pair record")
    match = matches[0]
    if not isinstance(match, Mapping):
        raise AssertionError("outside-pair record must be a mapping")
    return dict(match)


def _target_relation_record(
    relation_payload: Mapping[str, Any],
) -> dict[str, Any]:
    records = relation_payload.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("relation-sufficient records must be a sequence")
    matches = [
        record
        for record in records
        if int(record["source_record_id"]) == TARGET_SOURCE_RECORD_ID
        and int(record["row_center"]) == TARGET_ROW_CENTER
    ]
    if len(matches) != 1:
        raise AssertionError("expected exactly one 151:6 relation-sufficient record")
    match = matches[0]
    if not isinstance(match, Mapping):
        raise AssertionError("relation-sufficient record must be a mapping")
    return dict(match)


def _contains_connector_pair(activation_witnesses: Sequence[int]) -> bool:
    witness_set = set(int(label) for label in activation_witnesses)
    return set(CONNECTOR_PAIR) <= witness_set


def _support_partition_record(option: Mapping[str, Any]) -> dict[str, object]:
    support_pair = _int_list(option["support_pair"])
    activation_witnesses = _int_list(option["activation_witnesses_from_core_plus_pair"])
    forces_connector = _contains_connector_pair(activation_witnesses)
    mode = str(option["support_pair_mode"])
    expected_role = (
        "connector_forcing_support"
        if forces_connector
        else "connector_avoiding_escape_support"
    )
    return {
        "support_pair": support_pair,
        "support_pair_key": str(option["support_pair_key"]),
        "activation_witnesses": activation_witnesses,
        "contains_connector_pair": forces_connector,
        "connector_role": expected_role,
        "support_pair_mode": mode,
        "ledger_private_pair_hit": bool(option["ledger_private_pair_hit"]),
        "ledger_private_pair_core_vertices": _int_list(
            option["ledger_private_pair_core_vertices"]
        ),
        "pair_private_in_all_deletion_halos": bool(
            option["pair_private_in_all_deletion_halos"]
        ),
    }


def _support_pair_partition(
    outside_pair_record: Mapping[str, Any],
) -> dict[str, object]:
    options = outside_pair_record.get("support_pair_options")
    if not isinstance(options, Sequence):
        raise AssertionError("support_pair_options must be a sequence")
    partition = [
        _support_partition_record(option)
        for option in options
        if isinstance(option, Mapping)
    ]
    partition.sort(key=lambda record: str(record["support_pair_key"]))

    connector_forcing = [
        record["support_pair"]
        for record in partition
        if bool(record["contains_connector_pair"])
    ]
    connector_avoiding = [
        record["support_pair"]
        for record in partition
        if not bool(record["contains_connector_pair"])
    ]
    ledger_hits = [
        record["support_pair"]
        for record in partition
        if str(record["support_pair_mode"]) == LEDGER_HIT_MODE
    ]
    private_only = [
        record["support_pair"]
        for record in partition
        if str(record["support_pair_mode"]) == PRIVATE_HALO_ONLY_MODE
    ]

    return {
        "records": partition,
        "connector_forcing_support_pairs": connector_forcing,
        "connector_avoiding_support_pairs": connector_avoiding,
        "ledger_hit_support_pairs": ledger_hits,
        "private_halo_only_support_pairs": private_only,
        "connector_forcing_support_pair_count": len(connector_forcing),
        "connector_avoiding_support_pair_count": len(connector_avoiding),
    }


def _source_outside_summary(
    outside_pair_payload: Mapping[str, Any],
    outside_pair_record: Mapping[str, Any],
) -> dict[str, object]:
    return {
        "source_artifact": OUTSIDE_PAIR_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
        "source_schema": outside_pair_payload.get("schema"),
        "source_status": outside_pair_payload.get("status"),
        "source_trust": outside_pair_payload.get("trust"),
        "target_row_key": TARGET_ROW_KEY,
        "source_record_id": int(outside_pair_record["source_record_id"]),
        "row_center": int(outside_pair_record["row_center"]),
        "bootstrap_core_witnesses": _int_list(
            outside_pair_record["bootstrap_core_witnesses"]
        ),
        "outside_witnesses": _int_list(outside_pair_record["outside_witnesses"]),
        "support_pair_option_count": int(outside_pair_record["support_pair_option_count"]),
        "support_pairs": [
            _int_list(option["support_pair"])
            for option in outside_pair_record["support_pair_options"]
        ],
        "support_pair_modes": dict(outside_pair_record["support_pair_modes"]),
        "ledger_private_pair_support_hit_count": int(
            outside_pair_record["ledger_private_pair_support_hit_count"]
        ),
        "row_center_private_in_all_deletion_closures": bool(
            outside_pair_record["row_center_private_in_all_deletion_closures"]
        ),
    }


def _source_relation_summary(
    relation_payload: Mapping[str, Any],
    relation_record: Mapping[str, Any],
) -> dict[str, object]:
    requirements = relation_record.get("relation_sufficient_requirements")
    if not isinstance(requirements, Sequence):
        raise AssertionError("relation_sufficient_requirements must be a sequence")
    matching = [
        requirement
        for requirement in requirements
        if isinstance(requirement, Mapping)
        and str(requirement["requirement_id"]) == TARGET_REQUIREMENT_ID
    ]
    if len(matching) != 1:
        raise AssertionError("expected one 151:6 connector requirement")
    requirement = matching[0]
    return {
        "source_artifact": RELATION_SUFFICIENT_ARTIFACT.relative_to(
            REPO_ROOT
        ).as_posix(),
        "source_schema": relation_payload.get("schema"),
        "source_status": relation_payload.get("status"),
        "source_trust": relation_payload.get("trust"),
        "target_row_key": TARGET_ROW_KEY,
        "row_forcing_gap_type": relation_record.get("row_forcing_gap_type"),
        "row_target_status": relation_record.get("row_target_status"),
        "bridge_lemma_target": relation_record.get("bridge_lemma_target"),
        "requirement_id": str(requirement["requirement_id"]),
        "requirement_kind": str(requirement["kind"]),
        "required_witnesses": _int_list(requirement["required_witnesses"]),
        "relation_state": str(requirement["relation_state"]),
        "missing_from_bootstrap_core": _int_list(
            requirement["missing_from_bootstrap_core"]
        ),
        "support_sufficient_count": int(requirement["support_sufficient_count"]),
    }


def build_t12_151_6_outside_pair_connector_contract_payload() -> dict[str, object]:
    """Return the deterministic 151:6 outside-pair connector contract packet."""

    outside_pair_payload = build_t12_outside_pair_payload()
    relation_payload = build_t12_relation_sufficient_rows_payload()
    outside_pair_record = _target_outside_pair_record(outside_pair_payload)
    relation_record = _target_relation_record(relation_payload)
    partition = _support_pair_partition(outside_pair_record)

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet proves only the local conditional from a genuine rich class containing witnesses 0 and 8 to the connector equality [0,6]=[8,6].",
            "It does not prove that any outside-pair support exists at center 6.",
            "It does not prove full row 151:6, row forcing, n=9, the bridge, or a counterexample.",
            "The private-halo-only pair [3,5] remains an open connector-avoiding escape, not a ruled-out case.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [TARGET_SOURCE_RECORD_ID],
            "target_row_center": TARGET_ROW_CENTER,
            "target_witnesses": TARGET_WITNESSES,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "connector_pair": CONNECTOR_PAIR,
            "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
            "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
            "connector_forcing_support_pairs": CONNECTOR_FORCING_SUPPORT_PAIRS,
            "connector_avoiding_support_pairs": CONNECTOR_AVOIDING_SUPPORT_PAIRS,
            "ledger_hit_support_pairs": LEDGER_HIT_SUPPORT_PAIRS,
            "private_halo_only_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
            "support_pair_count": len(OUTSIDE_SUPPORT_PAIRS),
            "connector_forcing_support_pair_count": len(
                CONNECTOR_FORCING_SUPPORT_PAIRS
            ),
            "connector_avoiding_support_pair_count": len(
                CONNECTOR_AVOIDING_SUPPORT_PAIRS
            ),
            "full_row_forcing_required_for_connector": False,
            "local_conditional_lemma_status": LOCAL_CONDITIONAL_STATUS,
            "rich_support_existence_status": RICH_SUPPORT_EXISTENCE_STATUS,
            "escape_status": ESCAPE_STATUS,
            "connector_contract_gap_type": CONNECTOR_CONTRACT_GAP,
            "row_forcing_gap_type": GAP_OUTSIDE_PAIR_SUPPORT,
            "next_bridge_question": (
                "Can genuine outside-pair/rich-class geometry force one of "
                "the endpoint-8 supports [3,8] or [5,8], or can the "
                "private-halo-only pair [3,5] realize the connector-avoiding "
                "escape?"
            ),
        },
        "local_conditional_lemma": {
            "name": "151:6 outside-pair connector contract",
            "status": LOCAL_CONDITIONAL_STATUS,
            "hypothesis": (
                "At center 6, a genuine rich distance class contains witnesses "
                "0 and 8."
            ),
            "conclusion": "The selected-distance equality [0,6]=[8,6] holds.",
            "proof": (
                "A rich distance class at center 6 consists of vertices at one "
                "common distance from p_6. If witnesses 0 and 8 both belong to "
                "such a class, then |p_6-p_0|=|p_6-p_8|, which is exactly the "
                "connector equality [0,6]=[8,6]."
            ),
            "non_claims": [
                "does not prove any rich class contains witnesses 0 and 8",
                "does not prove either endpoint-8 outside support exists",
                "does not prove the full fixed row [0,3,5,8]",
                "does not prove the T12/F16 local packet is geometrically available",
            ],
        },
        "outside_pair_partition": {
            "status": ESCAPE_STATUS,
            "records": partition["records"],
            "connector_forcing_support_pairs": CONNECTOR_FORCING_SUPPORT_PAIRS,
            "connector_avoiding_support_pairs": CONNECTOR_AVOIDING_SUPPORT_PAIRS,
            "ledger_hit_support_pairs": LEDGER_HIT_SUPPORT_PAIRS,
            "private_halo_only_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
            "reading": (
                "The endpoint-8 supports [3,8] and [5,8] would place the "
                "bootstrap witness 0 and connector endpoint 8 in one center-6 "
                "rich class. The private-halo-only pair [3,5] activates the "
                "row without endpoint 8 and is therefore the connector-avoiding "
                "escape left open by this contract."
            ),
        },
        "escape_mechanism": {
            "status": ESCAPE_STATUS,
            "escape_condition": (
                "To avoid the connector equality at center 6, every genuine "
                "outside-pair support realizing row 151:6 must avoid endpoint 8."
            ),
            "connector_avoiding_support_pairs": CONNECTOR_AVOIDING_SUPPORT_PAIRS,
            "connector_avoiding_activation_witnesses": [[0, 3, 5]],
            "why_pair_3_5_matters": (
                "The bootstrap core supplies only witness 0. The support pair "
                "[3,5] makes row 6 activation-ready without adding endpoint 8, "
                "so it is the unique outside-pair support that avoids the "
                "stored connector pair [0,8]."
            ),
            "next_target": (
                "Prove an endpoint-8 outside support is forced, or isolate an "
                "exact geometric route by which the private-halo-only pair "
                "[3,5] can be the genuine support."
            ),
        },
        "source_outside_pair_packet": _source_outside_summary(
            outside_pair_payload, outside_pair_record
        ),
        "source_relation_sufficient_packet": _source_relation_summary(
            relation_payload, relation_record
        ),
        "source_artifacts": [
            {
                "path": OUTSIDE_PAIR_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
                "role": "source outside-pair support ledger",
                "schema": OUTSIDE_PAIR_SCHEMA,
                "status": OUTSIDE_PAIR_STATUS,
                "trust": OUTSIDE_PAIR_TRUST,
            },
            {
                "path": RELATION_SUFFICIENT_ARTIFACT.relative_to(
                    REPO_ROOT
                ).as_posix(),
                "role": "source relation-sufficient row record",
                "schema": RELATION_SUFFICIENT_SCHEMA,
                "status": RELATION_SUFFICIENT_STATUS,
                "trust": RELATION_SUFFICIENT_TRUST,
            },
        ],
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py"
            ),
            "command": (
                "python scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline values for the 151:6 connector contract."""

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
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "connector_pair": CONNECTOR_PAIR,
        "connector_distance_pairs": CONNECTOR_DISTANCE_PAIRS,
        "outside_support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "connector_forcing_support_pairs": CONNECTOR_FORCING_SUPPORT_PAIRS,
        "connector_avoiding_support_pairs": CONNECTOR_AVOIDING_SUPPORT_PAIRS,
        "ledger_hit_support_pairs": LEDGER_HIT_SUPPORT_PAIRS,
        "private_halo_only_support_pairs": PRIVATE_HALO_ONLY_SUPPORT_PAIRS,
        "support_pair_count": 3,
        "connector_forcing_support_pair_count": 2,
        "connector_avoiding_support_pair_count": 1,
        "full_row_forcing_required_for_connector": False,
        "local_conditional_lemma_status": LOCAL_CONDITIONAL_STATUS,
        "rich_support_existence_status": RICH_SUPPORT_EXISTENCE_STATUS,
        "escape_status": ESCAPE_STATUS,
        "connector_contract_gap_type": CONNECTOR_CONTRACT_GAP,
        "row_forcing_gap_type": GAP_OUTSIDE_PAIR_SUPPORT,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    warnings = payload.get("interpretation_warnings")
    if not isinstance(warnings, Sequence):
        raise AssertionError("interpretation_warnings must be a sequence")
    if not any("does not prove that any outside-pair support exists" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve support-existence gap")
    if not any("does not prove full row 151:6" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve no-row-forcing guardrail")

    lemma = payload.get("local_conditional_lemma")
    if not isinstance(lemma, Mapping):
        raise AssertionError("local_conditional_lemma must be a mapping")
    if lemma.get("status") != LOCAL_CONDITIONAL_STATUS:
        raise AssertionError("local conditional lemma status drifted")
    if lemma.get("conclusion") != "The selected-distance equality [0,6]=[8,6] holds.":
        raise AssertionError("connector conclusion drifted")
    non_claims = lemma.get("non_claims")
    if not isinstance(non_claims, Sequence):
        raise AssertionError("local conditional non_claims must be a sequence")
    if not any("does not prove any rich class" in str(item) for item in non_claims):
        raise AssertionError("local lemma must not claim rich-class existence")

    partition = payload.get("outside_pair_partition")
    if not isinstance(partition, Mapping):
        raise AssertionError("outside_pair_partition must be a mapping")
    if partition.get("status") != ESCAPE_STATUS:
        raise AssertionError("outside pair partition status drifted")
    if partition.get("connector_forcing_support_pairs") != (
        CONNECTOR_FORCING_SUPPORT_PAIRS
    ):
        raise AssertionError("connector-forcing support pairs drifted")
    if partition.get("connector_avoiding_support_pairs") != (
        CONNECTOR_AVOIDING_SUPPORT_PAIRS
    ):
        raise AssertionError("connector-avoiding support pairs drifted")
    records = partition.get("records")
    if not isinstance(records, Sequence) or len(records) != 3:
        raise AssertionError("outside-pair partition must have three records")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("partition record must be a mapping")
        support_pair = record.get("support_pair")
        contains_connector = bool(record.get("contains_connector_pair"))
        if support_pair in CONNECTOR_FORCING_SUPPORT_PAIRS and not contains_connector:
            raise AssertionError("endpoint-8 support must force connector")
        if support_pair in CONNECTOR_AVOIDING_SUPPORT_PAIRS and contains_connector:
            raise AssertionError("pair [3,5] must remain connector avoiding")

    escape = payload.get("escape_mechanism")
    if not isinstance(escape, Mapping):
        raise AssertionError("escape_mechanism must be a mapping")
    if escape.get("status") != ESCAPE_STATUS:
        raise AssertionError("escape mechanism status drifted")
    if escape.get("connector_avoiding_support_pairs") != (
        CONNECTOR_AVOIDING_SUPPORT_PAIRS
    ):
        raise AssertionError("connector-avoiding support pairs drifted")
    if escape.get("connector_avoiding_activation_witnesses") != [[0, 3, 5]]:
        raise AssertionError("connector-avoiding activation witnesses drifted")

    source_outside = payload.get("source_outside_pair_packet")
    if not isinstance(source_outside, Mapping):
        raise AssertionError("source_outside_pair_packet must be a mapping")
    expected_outside = {
        "source_schema": OUTSIDE_PAIR_SCHEMA,
        "source_status": OUTSIDE_PAIR_STATUS,
        "source_trust": OUTSIDE_PAIR_TRUST,
        "target_row_key": TARGET_ROW_KEY,
        "source_record_id": TARGET_SOURCE_RECORD_ID,
        "row_center": TARGET_ROW_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "outside_witnesses": [3, 5, 8],
        "support_pair_option_count": 3,
        "support_pairs": OUTSIDE_SUPPORT_PAIRS,
        "ledger_private_pair_support_hit_count": 2,
        "row_center_private_in_all_deletion_closures": True,
    }
    for key, expected in expected_outside.items():
        if source_outside.get(key) != expected:
            raise AssertionError(
                f"source_outside_pair_packet {key} is "
                f"{source_outside.get(key)!r}, expected {expected!r}"
            )

    source_relation = payload.get("source_relation_sufficient_packet")
    if not isinstance(source_relation, Mapping):
        raise AssertionError("source_relation_sufficient_packet must be a mapping")
    expected_relation = {
        "source_schema": RELATION_SUFFICIENT_SCHEMA,
        "source_status": RELATION_SUFFICIENT_STATUS,
        "source_trust": RELATION_SUFFICIENT_TRUST,
        "target_row_key": TARGET_ROW_KEY,
        "row_forcing_gap_type": GAP_OUTSIDE_PAIR_SUPPORT,
        "requirement_id": TARGET_REQUIREMENT_ID,
        "requirement_kind": "equality_connector_pair",
        "required_witnesses": CONNECTOR_PAIR,
        "relation_state": "SUPPORT_SUFFICIENT",
        "missing_from_bootstrap_core": [8],
        "support_sufficient_count": 2,
    }
    for key, expected in expected_relation.items():
        if source_relation.get(key) != expected:
            raise AssertionError(
                f"source_relation_sufficient_packet {key} is "
                f"{source_relation.get(key)!r}, expected {expected!r}"
            )

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_151_6_outside_pair_connector_contract.py"
    ):
        raise AssertionError("provenance generator drifted")
