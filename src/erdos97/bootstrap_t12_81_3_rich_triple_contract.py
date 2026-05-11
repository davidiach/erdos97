"""Rich-triple connector contract for the bootstrap/T12 81:3 target.

This packet is the next rung after the focused 81:3 closure-target packet.
It records a weaker exact local contract than full-row forcing: the T12/F16
connector only needs witnesses ``0`` and ``1`` to lie in one rich class at
center ``3``.  The packet also records the precise escape shape left open by
that observation.  It is diagnostic bookkeeping only and does not prove that
any rich class is forced.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_closure_target import (
    DEFAULT_ARTIFACT as CLOSURE_TARGET_ARTIFACT,
    ROW_FORCING_GAP as CLOSURE_TARGET_ROW_FORCING_GAP,
    SCHEMA as CLOSURE_TARGET_SCHEMA,
    STATUS as CLOSURE_TARGET_STATUS,
    TARGET_CLOSURE_LABELS,
    TARGET_DELETION_SEED,
    TARGET_EXPOSED_CORE_VERTEX,
    TARGET_REQUIREMENT_ID,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    TARGET_SOURCE_RECORD_ID,
    TARGET_WITNESSES,
    TRUST as CLOSURE_TARGET_TRUST,
    build_t12_81_3_closure_target_payload,
)


SCHEMA = "erdos97.bootstrap_t12_81_3_rich_triple_contract.v1"
STATUS = "BOOTSTRAP_T12_81_3_RICH_TRIPLE_CONTRACT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Focused local connector contract for source 81 row 3: any genuine rich "
    "class at center 3 that contains witnesses 0 and 1 supplies the T12/F16 "
    "equality connector [1,3]=[0,3]. This proves only that exact local "
    "conditional and the remaining escape shape; it does not prove the rich "
    "class exists, does not prove row forcing, does not prove n=9, does not "
    "prove the bridge, and does not claim a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_3_rich_triple_contract.json"
)

CONNECTOR_PAIR = [0, 1]
CONNECTOR_DISTANCE_PAIRS = [[1, 3], [0, 3]]
CONNECTOR_FORCING_TRIPLES = [[0, 1, 4], [0, 1, 6]]
CONNECTOR_AVOIDING_ACTIVATION_TRIPLES = [[0, 4, 6], [1, 4, 6]]
SEED_ACTIVATION_TRIPLE = [0, 1, 4]
ESCAPE_STATUS = "CONNECTOR_ESCAPE_REQUIRES_RICH_CLASSES_AVOID_PAIR_0_1"
LOCAL_CONDITIONAL_STATUS = "EXACT_LOCAL_CONDITIONAL"
RICH_CLASS_EXISTENCE_STATUS = "OPEN_TARGET_NOT_PROVED"
RICH_TRIPLE_GAP = "PAIR_CONNECTOR_CONTRACT_NOT_RICH_CLASS_EXISTENCE"


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _triples(values: Sequence[int]) -> list[list[int]]:
    return [list(triple) for triple in itertools.combinations(sorted(values), 3)]


def _contains_connector_pair(triple: Sequence[int]) -> bool:
    return all(label in triple for label in CONNECTOR_PAIR)


def _activation_triples() -> dict[str, object]:
    all_triples = _triples(TARGET_WITNESSES)
    connector_forcing = [
        triple for triple in all_triples if _contains_connector_pair(triple)
    ]
    connector_avoiding = [
        triple for triple in all_triples if not _contains_connector_pair(triple)
    ]
    return {
        "target_witnesses": TARGET_WITNESSES,
        "all_witness_triples": all_triples,
        "connector_pair": CONNECTOR_PAIR,
        "connector_forcing_triples": connector_forcing,
        "connector_avoiding_activation_triples": connector_avoiding,
        "seed_activation_triple": SEED_ACTIVATION_TRIPLE,
        "seed_activation_uses_connector_pair": _contains_connector_pair(
            SEED_ACTIVATION_TRIPLE
        ),
        "seed_activation_uses_outside_witness_6": 6 in SEED_ACTIVATION_TRIPLE,
        "connector_avoiding_triples_all_use_outside_witness_6": all(
            6 in triple for triple in connector_avoiding
        ),
    }


def _closure_target_summary(
    closure_target: Mapping[str, Any],
) -> dict[str, object]:
    summary = closure_target.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("closure target summary must be a mapping")
    target = closure_target.get("target_record")
    if not isinstance(target, Mapping):
        raise AssertionError("closure target record must be a mapping")
    source_artifact = CLOSURE_TARGET_ARTIFACT.relative_to(REPO_ROOT).as_posix()
    return {
        "source_artifact": source_artifact,
        "source_schema": closure_target.get("schema"),
        "source_status": closure_target.get("status"),
        "source_trust": closure_target.get("trust"),
        "target_row_key": summary.get("target_row_key"),
        "target_row_center": summary.get("target_row_center"),
        "target_witnesses": summary.get("target_witnesses"),
        "deletion_seed": summary.get("deletion_seed"),
        "exposed_core_vertex": summary.get("exposed_core_vertex"),
        "closure_labels": summary.get("closure_labels"),
        "required_connector_pair": summary.get("required_connector_pair"),
        "t12_connector_pair_chain": summary.get("t12_connector_pair_chain"),
        "row_forcing_gap_type": summary.get("row_forcing_gap_type"),
        "relation_requirement_id": TARGET_REQUIREMENT_ID,
        "t12_role": target.get("t12_strict_cycle_role"),
    }


def build_t12_81_3_rich_triple_contract_payload() -> dict[str, object]:
    """Return the deterministic rich-triple connector contract packet."""

    closure_target = build_t12_81_3_closure_target_payload()
    activation = _activation_triples()
    closure_summary = _closure_target_summary(closure_target)

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This packet proves only the local conditional from a genuine rich class containing witnesses 0 and 1 to the connector equality [1,3]=[0,3].",
            "It does not prove that such a rich class exists at center 3.",
            "It does not prove full row 81:3, row/rich-class forcing, n=9, the bridge, or a counterexample.",
            "Connector-avoiding activation remains an open exact escape mechanism requiring separate analysis.",
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
            "seed_activation_triple": SEED_ACTIVATION_TRIPLE,
            "seed_activation_forces_connector": True,
            "full_row_forcing_required_for_connector": False,
            "local_conditional_lemma_status": LOCAL_CONDITIONAL_STATUS,
            "rich_class_existence_status": RICH_CLASS_EXISTENCE_STATUS,
            "escape_status": ESCAPE_STATUS,
            "rich_triple_gap_type": RICH_TRIPLE_GAP,
            "next_bridge_question": (
                "Can the real rich-class closure force activation at center 3 "
                "from the connector triple [0,1,4], or must any connector-"
                "avoiding activation first expose label 6?"
            ),
        },
        "local_conditional_lemma": {
            "name": "81:3 connector-pair rich-class contract",
            "status": LOCAL_CONDITIONAL_STATUS,
            "hypothesis": (
                "At center 3, a genuine rich distance class contains witnesses "
                "0 and 1."
            ),
            "conclusion": "The selected-distance equality [1,3]=[0,3] holds.",
            "proof": (
                "A rich distance class at center 3 consists of vertices at one "
                "common distance from p_3. If witnesses 0 and 1 both belong to "
                "such a class, then |p_3-p_1|=|p_3-p_0|, which is exactly the "
                "connector equality [1,3]=[0,3]."
            ),
            "non_claims": [
                "does not prove any rich class contains witnesses 0 and 1",
                "does not prove the full fixed row [0,1,4,6]",
                "does not prove the T12/F16 local packet is geometrically available",
            ],
        },
        "activation_triple_analysis": activation,
        "escape_mechanism": {
            "status": ESCAPE_STATUS,
            "escape_condition": (
                "To avoid the connector equality at center 3, every genuine "
                "rich class centered at 3 must avoid containing witnesses 0 "
                "and 1 together."
            ),
            "available_connector_avoiding_triples_in_fixed_row": (
                CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
            ),
            "outside_label_required_before_connector_avoiding_activation": 6,
            "why_label_6_matters": (
                "The deletion seed [0,1,4] already contains the connector "
                "pair. The only triples from the fixed witness set that avoid "
                "that pair are [0,4,6] and [1,4,6], both of which require "
                "label 6 to be available before center 3 activates."
            ),
            "next_target": (
                "Order-resolved rich-class closure: either force the seed "
                "activation [0,1,4] at center 3, or certify how label 6 becomes "
                "available first without already entering the connector."
            ),
        },
        "source_closure_target": closure_summary,
        "source_artifacts": [
            {
                "path": CLOSURE_TARGET_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
                "role": "source focused 81:3 closure target packet",
                "schema": CLOSURE_TARGET_SCHEMA,
                "status": CLOSURE_TARGET_STATUS,
                "trust": CLOSURE_TARGET_TRUST,
            }
        ],
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_3_rich_triple_contract.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Assert stable headline values for the rich-triple contract packet."""

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
        "seed_activation_triple": SEED_ACTIVATION_TRIPLE,
        "seed_activation_forces_connector": True,
        "full_row_forcing_required_for_connector": False,
        "local_conditional_lemma_status": LOCAL_CONDITIONAL_STATUS,
        "rich_class_existence_status": RICH_CLASS_EXISTENCE_STATUS,
        "escape_status": ESCAPE_STATUS,
        "rich_triple_gap_type": RICH_TRIPLE_GAP,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    warnings = payload.get("interpretation_warnings")
    if not isinstance(warnings, Sequence):
        raise AssertionError("interpretation_warnings must be a sequence")
    if not any("does not prove that such a rich class exists" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve the rich-class existence gap")
    if not any("does not prove full row 81:3" in str(w) for w in warnings):
        raise AssertionError("warnings must preserve the no-row-forcing guardrail")

    lemma = payload.get("local_conditional_lemma")
    if not isinstance(lemma, Mapping):
        raise AssertionError("local_conditional_lemma must be a mapping")
    if lemma.get("status") != LOCAL_CONDITIONAL_STATUS:
        raise AssertionError("local conditional lemma status drifted")
    if lemma.get("conclusion") != "The selected-distance equality [1,3]=[0,3] holds.":
        raise AssertionError("connector conclusion drifted")
    non_claims = lemma.get("non_claims")
    if not isinstance(non_claims, Sequence):
        raise AssertionError("local conditional non_claims must be a sequence")
    if not any("does not prove any rich class" in str(item) for item in non_claims):
        raise AssertionError("local lemma must not claim rich-class existence")

    activation = payload.get("activation_triple_analysis")
    if not isinstance(activation, Mapping):
        raise AssertionError("activation_triple_analysis must be a mapping")
    expected_activation = {
        "target_witnesses": TARGET_WITNESSES,
        "all_witness_triples": [
            [0, 1, 4],
            [0, 1, 6],
            [0, 4, 6],
            [1, 4, 6],
        ],
        "connector_pair": CONNECTOR_PAIR,
        "connector_forcing_triples": CONNECTOR_FORCING_TRIPLES,
        "connector_avoiding_activation_triples": (
            CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
        ),
        "seed_activation_triple": SEED_ACTIVATION_TRIPLE,
        "seed_activation_uses_connector_pair": True,
        "seed_activation_uses_outside_witness_6": False,
        "connector_avoiding_triples_all_use_outside_witness_6": True,
    }
    for key, expected in expected_activation.items():
        if activation.get(key) != expected:
            raise AssertionError(
                f"activation {key} is {activation.get(key)!r}, expected {expected!r}"
            )

    escape = payload.get("escape_mechanism")
    if not isinstance(escape, Mapping):
        raise AssertionError("escape_mechanism must be a mapping")
    if escape.get("status") != ESCAPE_STATUS:
        raise AssertionError("escape mechanism status drifted")
    if escape.get("available_connector_avoiding_triples_in_fixed_row") != (
        CONNECTOR_AVOIDING_ACTIVATION_TRIPLES
    ):
        raise AssertionError("connector-avoiding triples drifted")
    if escape.get("outside_label_required_before_connector_avoiding_activation") != 6:
        raise AssertionError("connector-avoiding escape must require label 6")

    source = payload.get("source_closure_target")
    if not isinstance(source, Mapping):
        raise AssertionError("source_closure_target must be a mapping")
    expected_source = {
        "source_schema": CLOSURE_TARGET_SCHEMA,
        "source_status": CLOSURE_TARGET_STATUS,
        "source_trust": CLOSURE_TARGET_TRUST,
        "target_row_key": TARGET_ROW_KEY,
        "target_row_center": TARGET_ROW_CENTER,
        "target_witnesses": TARGET_WITNESSES,
        "deletion_seed": TARGET_DELETION_SEED,
        "exposed_core_vertex": TARGET_EXPOSED_CORE_VERTEX,
        "closure_labels": TARGET_CLOSURE_LABELS,
        "required_connector_pair": CONNECTOR_PAIR,
        "t12_connector_pair_chain": CONNECTOR_DISTANCE_PAIRS,
        "row_forcing_gap_type": CLOSURE_TARGET_ROW_FORCING_GAP,
        "relation_requirement_id": TARGET_REQUIREMENT_ID,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise AssertionError(
                f"source_closure_target {key} is {source.get(key)!r}, "
                f"expected {expected!r}"
            )

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_3_rich_triple_contract.py"
    ):
        raise AssertionError("provenance generator drifted")
