#!/usr/bin/env python3
"""Check the source-151 center-8 source crosswalk for the 151:6 cascade."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.bootstrap_t12_151_singleton_support_audit import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SINGLETON_AUDIT,
    SCAN_STATUS as SOURCE_SINGLETON_SCAN_STATUS,
    SCHEMA as SOURCE_SINGLETON_SCHEMA,
    STATUS as SOURCE_SINGLETON_STATUS,
    assert_expected_payload as assert_expected_singleton_audit,
)
from erdos97.bootstrap_t12_one_outside import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_ONE_OUTSIDE,
    SCHEMA as SOURCE_ONE_OUTSIDE_SCHEMA,
    STATUS as SOURCE_ONE_OUTSIDE_STATUS,
    assert_expected_payload as assert_expected_one_outside,
)
from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    SCHEMA as SOURCE_CASCADE_ENDPOINT8_SCHEMA,
    STATUS as SOURCE_CASCADE_ENDPOINT8_STATUS,
    TARGET_STATUS as SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    assert_expected_cascade_endpoint8_targets,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_rich_triple_preflight import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    GATE_STATUS as SOURCE_CENTER8_PREFLIGHT_GATE_STATUS,
    SCHEMA as SOURCE_CENTER8_PREFLIGHT_SCHEMA,
    STATUS as SOURCE_CENTER8_PREFLIGHT_STATUS,
    assert_expected_center8_rich_triple_preflight,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_center8_source_crosswalk.v1"
STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_CENTER8_SOURCE_CROSSWALK_DIAGNOSTIC_ONLY"
)
GATE_STATUS = (
    "NOT_READY_EXISTING_SOURCE151_CENTER8_SINGLETON_DOES_NOT_SUPPLY_CASCADE_TRIPLE"
)
DECISION_STATUS = (
    "CENTER8_SOURCE151_SINGLETON_PACKET_IS_DISJOINT_FROM_CASCADE_TRIPLE"
)
SOURCE151_CENTER8_KEY = "151:8"
SOURCE151_CENTER8_CORE = [1, 2]
SOURCE151_CENTER8_SUPPORTS = [5, 7]
SOURCE151_CENTER8_ORIGINAL_ROW = [1, 2, 5, 7]
CLAIM_SCOPE = (
    "Proof-mining source crosswalk for the source-151 row-6 label-4 "
    "center-8 cascade target. It joins the center-8 rich-triple preflight, "
    "the source-151 singleton-support audit, the one-outside packet, and the "
    "cascade endpoint-8 target packet to check whether the existing "
    "source-151 named center-8 singleton/one-outside evidence supplies a "
    "center-8 rich class containing [0,4,6]. It records that it does not: "
    "the source-151 row-8 singleton target has bootstrap core [1,2] and "
    "singleton supports [5,7], so every checked activation candidate contains "
    "at most one label from [0,4,6] and no pair from that triple. This does "
    "not prove support existence, does not prove row forcing, does not prove "
    "endpoint-8 forcing, does not prove that pair [3,5] is impossible, does "
    "not prove n=9, does not prove the bootstrap bridge, is not a "
    "counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_center8_source_crosswalk.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_center8_source_crosswalk.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_center8_source_crosswalk.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "decision",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "source_crosswalk_records",
    "status",
    "summary",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "cascade_source_record_id": 151,
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "conditional_center8_target_status": SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS,
    "conditional_center8_preflight_gate_status": SOURCE_CENTER8_PREFLIGHT_GATE_STATUS,
    "source151_named_center8_target_row_key": SOURCE151_CENTER8_KEY,
    "source151_named_center8_bootstrap_core_witnesses": SOURCE151_CENTER8_CORE,
    "source151_named_center8_singleton_support_labels": SOURCE151_CENTER8_SUPPORTS,
    "source151_named_center8_original_row": SOURCE151_CENTER8_ORIGINAL_ROW,
    "source151_named_center8_candidate_count": 9,
    "source151_named_center8_candidate_overlap_histogram": {"0": 3, "1": 6},
    "source151_named_center8_candidate_rows_with_any_target_label_count": 6,
    "source151_named_center8_candidate_rows_with_target_pair_count": 0,
    "source151_named_center8_candidate_rows_with_full_target_triple_count": 0,
    "source151_named_center8_max_target_triple_overlap": 1,
    "source151_one_outside_support_option_count": 2,
    "source151_one_outside_activation_overlap_histogram": {"0": 2},
    "source151_one_outside_activation_rows_with_any_target_label_count": 0,
    "source151_one_outside_activation_rows_with_full_target_triple_count": 0,
    "same_center_as_conditional_target": True,
    "same_source_record_as_cascade": True,
    "current_source151_named_center8_evidence_supplies_cascade_triple": False,
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


def build_center8_source_crosswalk_payload(
    center8_preflight: Mapping[str, Any],
    singleton_audit: Mapping[str, Any],
    one_outside: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    *,
    center8_preflight_path: Path = DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    singleton_audit_path: Path = DEFAULT_SOURCE_SINGLETON_AUDIT,
    one_outside_path: Path = DEFAULT_SOURCE_ONE_OUTSIDE,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> dict[str, Any]:
    """Return the deterministic center-8 source crosswalk payload."""

    errors: list[str] = []
    assert_expected_center8_rich_triple_preflight(center8_preflight)
    assert_expected_singleton_audit(singleton_audit)
    assert_expected_one_outside(one_outside)
    assert_expected_cascade_endpoint8_targets(cascade_endpoint8_targets)
    _validate_sources(
        center8_preflight,
        singleton_audit,
        one_outside,
        cascade_endpoint8_targets,
        errors,
    )

    summary, crosswalk_records = _summary_and_crosswalk_records(
        center8_preflight,
        singleton_audit,
        one_outside,
        cascade_endpoint8_targets,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Can the existing source-151 row-8 singleton/one-outside "
                "packet be reused as the source for the 151:6 cascade "
                "center-8 rich triple [0,4,6]?"
            ),
            "answer": (
                "do_not_reuse_source151_row8_singleton_packet_as_center8_"
                "cascade_source"
            ),
            "gate_status": GATE_STATUS,
            "decision_status": DECISION_STATUS,
            "current_source151_named_center8_evidence_supplies_cascade_triple": False,
            "blocking_reason": (
                "The existing source-151 row-8 singleton target is centered "
                "at 8, but its activation family is built from core [1,2] "
                "and singleton supports [5,7]. The checked row candidates "
                "therefore contain no pair, and no full triple, from [0,4,6]."
            ),
            "required_next_lemma": (
                "Add a genuine geometric source for a center-8 rich class "
                "containing [0,4,6] in the source-151 row-6 cascade package, "
                "or find a different support-rich obstruction."
            ),
        },
        "source_crosswalk_records": crosswalk_records,
        "interpretation": [
            (
                "The source-151 row-8 singleton packet and the source-151 "
                "row-6 cascade target share center 8 but require different "
                "witness geometry."
            ),
            (
                "The singleton packet proves only an activation-family audit "
                "for rows containing [1,2] and one of [5,7]; it does not "
                "supply the cascade endpoint triple [0,4,6]."
            ),
            (
                "The center-8 cascade target remains conditional: a future "
                "bridge lemma must supply [0,4,6] from genuine minimal/"
                "rich-class geometry or bypass this target."
            ),
        ],
        "source_artifacts": [
            _source_summary(
                center8_preflight_path,
                "source 151:6 center-8 rich-triple preflight",
                center8_preflight,
            ),
            _source_summary(
                singleton_audit_path,
                "source 151 singleton-support audit",
                singleton_audit,
            ),
            _source_summary(
                one_outside_path,
                "bootstrap/T12 one-outside packet",
                one_outside,
            ),
            _source_summary(
                cascade_endpoint8_targets_path,
                "source 151:6 cascade endpoint-8 target packet",
                cascade_endpoint8_targets,
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_center8_source_crosswalk(payload)
    return payload


def assert_expected_center8_source_crosswalk(payload: Mapping[str, Any]) -> None:
    """Assert the pinned center-8 source crosswalk packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    center8_preflight_path: Path = DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    singleton_audit_path: Path = DEFAULT_SOURCE_SINGLETON_AUDIT,
    one_outside_path: Path = DEFAULT_SOURCE_ONE_OUTSIDE,
    cascade_endpoint8_targets_path: Path = DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
) -> list[str]:
    """Return validation errors for a center-8 source crosswalk payload."""

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
            "existing source-151 named center-8 singleton/one-outside evidence",
            "center-8 rich class containing [0,4,6]",
            "bootstrap core [1,2]",
            "singleton supports [5,7]",
            "at most one label from [0,4,6]",
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
    records = payload.get("source_crosswalk_records")
    if not isinstance(records, list):
        errors.append("source_crosswalk_records must be a list")
    else:
        _validate_crosswalk_records(records, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("remains conditional" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the conditional target")

    if recompute and not errors:
        generated = build_center8_source_crosswalk_payload(
            load_artifact(center8_preflight_path),
            load_artifact(singleton_audit_path),
            load_artifact(one_outside_path),
            load_artifact(cascade_endpoint8_targets_path),
            center8_preflight_path=center8_preflight_path,
            singleton_audit_path=singleton_audit_path,
            one_outside_path=one_outside_path,
            cascade_endpoint8_targets_path=cascade_endpoint8_targets_path,
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
    return {
        "artifact": display_path(path, ROOT),
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "target_row_key": summary.get("target_row_key"),
        "conditional_center8_triple": summary.get("conditional_center8_triple"),
        "source151_named_center8_target_row_key": summary.get(
            "source151_named_center8_target_row_key"
        ),
        "source151_named_center8_max_target_triple_overlap": summary.get(
            "source151_named_center8_max_target_triple_overlap"
        ),
        "source151_named_center8_candidate_rows_with_target_pair_count": summary.get(
            "source151_named_center8_candidate_rows_with_target_pair_count"
        ),
        "source151_named_center8_candidate_rows_with_full_target_triple_count": (
            summary.get(
                "source151_named_center8_candidate_rows_with_full_target_triple_count"
            )
        ),
        "gate_status": summary.get("gate_status"),
        "validation_errors": list(errors),
    }


def _summary_and_crosswalk_records(
    center8_preflight: Mapping[str, Any],
    singleton_audit: Mapping[str, Any],
    one_outside: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    preflight_summary = _required_mapping(
        center8_preflight.get("summary"), "center-8 preflight summary"
    )
    cascade_summary = _required_mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary"
    )
    singleton_record = _source151_center8_singleton_record(singleton_audit)
    one_outside_record = _source151_center8_one_outside_record(one_outside)

    candidate_rows = _int_rows(singleton_record["target_center_candidate_classes"])
    support_activations = [
        _int_list(option["activation_witnesses_from_core_plus_support"])
        for option in one_outside_record["support_options"]
    ]
    target_pairs = [list(pair) for pair in combinations(ENDPOINT_TRIPLE, 2)]
    candidate_profiles = [
        _row_profile(row, ENDPOINT_TRIPLE, target_pairs) for row in candidate_rows
    ]
    activation_profiles = [
        _row_profile(row, ENDPOINT_TRIPLE, target_pairs) for row in support_activations
    ]

    candidate_overlap_histogram = _overlap_histogram(candidate_profiles)
    activation_overlap_histogram = _overlap_histogram(activation_profiles)
    candidate_pair_rows = [
        profile for profile in candidate_profiles if profile["target_pair_overlap"]
    ]
    candidate_full_rows = [
        profile for profile in candidate_profiles if profile["contains_full_target_triple"]
    ]
    activation_full_rows = [
        profile for profile in activation_profiles if profile["contains_full_target_triple"]
    ]

    crosswalk_records = [
        {
            "source_name": "source-151 row-8 singleton activation candidates",
            "source_doc": "docs/bootstrap-t12-151-singleton-support-audit.md",
            "source_record_id": 151,
            "target_row_key": SOURCE151_CENTER8_KEY,
            "row_center": ENDPOINT_CENTER,
            "uses_label_8_as_center": True,
            "bootstrap_core_witnesses": _int_list(
                singleton_record["bootstrap_core_witnesses"]
            ),
            "singleton_support_labels": _int_list(
                singleton_record["singleton_support_labels"]
            ),
            "original_target_center_class": _int_list(
                singleton_record["original_target_center_class"]
            ),
            "candidate_count": len(candidate_profiles),
            "candidate_profiles": candidate_profiles,
            "target_label_overlap_histogram": candidate_overlap_histogram,
            "candidate_rows_with_target_pair_count": len(candidate_pair_rows),
            "candidate_rows_with_full_target_triple_count": len(candidate_full_rows),
            "max_target_triple_overlap": max(
                int(profile["target_label_overlap_count"])
                for profile in candidate_profiles
            ),
            "supplies_cascade_triple": False,
            "blocking_reason": (
                "Every candidate contains [1,2] and one of [5,7], leaving "
                "only one remaining label slot for the cascade triple [0,4,6]."
            ),
        },
        {
            "source_name": "source-151 row-8 one-outside support activations",
            "source_doc": "docs/bootstrap-t12-one-outside.md",
            "source_record_id": 151,
            "target_row_key": SOURCE151_CENTER8_KEY,
            "row_center": ENDPOINT_CENTER,
            "uses_label_8_as_center": True,
            "bootstrap_core_witnesses": _int_list(
                one_outside_record["bootstrap_core_witnesses"]
            ),
            "support_labels": [
                int(option["support_label"])
                for option in one_outside_record["support_options"]
            ],
            "activation_profiles": activation_profiles,
            "target_label_overlap_histogram": activation_overlap_histogram,
            "activation_rows_with_full_target_triple_count": len(activation_full_rows),
            "support_option_count": int(one_outside_record["support_option_count"]),
            "supplies_cascade_triple": False,
            "blocking_reason": (
                "The raw one-outside activation triples are [1,2,5] and "
                "[1,2,7], so they contain no label from [0,4,6]."
            ),
        },
    ]
    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "cascade_source_record_id": 151,
        "conditional_center8_target_center": int(
            cascade_summary["endpoint_center"]
        ),
        "conditional_center8_triple": list(cascade_summary["endpoint_triple"]),
        "conditional_center8_target_status": cascade_summary["target_status"],
        "conditional_center8_preflight_gate_status": preflight_summary["gate_status"],
        "source151_named_center8_target_row_key": SOURCE151_CENTER8_KEY,
        "source151_named_center8_bootstrap_core_witnesses": _int_list(
            singleton_record["bootstrap_core_witnesses"]
        ),
        "source151_named_center8_singleton_support_labels": _int_list(
            singleton_record["singleton_support_labels"]
        ),
        "source151_named_center8_original_row": _int_list(
            singleton_record["original_target_center_class"]
        ),
        "source151_named_center8_candidate_count": len(candidate_profiles),
        "source151_named_center8_candidate_overlap_histogram": (
            candidate_overlap_histogram
        ),
        "source151_named_center8_candidate_rows_with_any_target_label_count": sum(
            1 for profile in candidate_profiles if profile["target_label_overlap"]
        ),
        "source151_named_center8_candidate_rows_with_target_pair_count": len(
            candidate_pair_rows
        ),
        "source151_named_center8_candidate_rows_with_full_target_triple_count": len(
            candidate_full_rows
        ),
        "source151_named_center8_max_target_triple_overlap": max(
            int(profile["target_label_overlap_count"]) for profile in candidate_profiles
        ),
        "source151_one_outside_support_option_count": int(
            one_outside_record["support_option_count"]
        ),
        "source151_one_outside_activation_overlap_histogram": (
            activation_overlap_histogram
        ),
        "source151_one_outside_activation_rows_with_any_target_label_count": sum(
            1 for profile in activation_profiles if profile["target_label_overlap"]
        ),
        "source151_one_outside_activation_rows_with_full_target_triple_count": len(
            activation_full_rows
        ),
        "same_center_as_conditional_target": True,
        "same_source_record_as_cascade": True,
        "current_source151_named_center8_evidence_supplies_cascade_triple": False,
        "gate_status": GATE_STATUS,
        "decision_status": DECISION_STATUS,
    }
    return summary, crosswalk_records


def _source151_center8_singleton_record(
    singleton_audit: Mapping[str, Any],
) -> Mapping[str, Any]:
    records = singleton_audit.get("target_audits")
    if not isinstance(records, list):
        raise AssertionError("singleton target_audits must be a list")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("singleton audit record must be an object")
        if record.get("target_row_key") == SOURCE151_CENTER8_KEY:
            return record
    raise AssertionError(f"missing singleton target {SOURCE151_CENTER8_KEY}")


def _source151_center8_one_outside_record(
    one_outside: Mapping[str, Any],
) -> Mapping[str, Any]:
    records = one_outside.get("records")
    if not isinstance(records, list):
        raise AssertionError("one-outside records must be a list")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("one-outside record must be an object")
        if int(record["source_record_id"]) == 151 and int(record["row_center"]) == 8:
            return record
    raise AssertionError("missing source-151 row-8 one-outside record")


def _row_profile(
    row: Sequence[int],
    target_triple: Sequence[int],
    target_pairs: Sequence[Sequence[int]],
) -> dict[str, Any]:
    row_set = set(row)
    overlap = sorted(row_set.intersection(int(label) for label in target_triple))
    pair_overlap = [
        list(pair) for pair in target_pairs if set(int(label) for label in pair) <= row_set
    ]
    return {
        "row": list(row),
        "target_label_overlap": overlap,
        "target_label_overlap_count": len(overlap),
        "target_pair_overlap": pair_overlap,
        "contains_full_target_triple": set(target_triple) <= row_set,
    }


def _overlap_histogram(profiles: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    counts = Counter(
        int(profile["target_label_overlap_count"]) for profile in profiles
    )
    return {str(count): int(counts[count]) for count in sorted(counts)}


def _validate_sources(
    center8_preflight: Mapping[str, Any],
    singleton_audit: Mapping[str, Any],
    one_outside: Mapping[str, Any],
    cascade_endpoint8_targets: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = [
        (
            "center-8 preflight",
            center8_preflight,
            SOURCE_CENTER8_PREFLIGHT_SCHEMA,
            SOURCE_CENTER8_PREFLIGHT_STATUS,
        ),
        (
            "source-151 singleton audit",
            singleton_audit,
            SOURCE_SINGLETON_SCHEMA,
            SOURCE_SINGLETON_STATUS,
        ),
        (
            "one-outside packet",
            one_outside,
            SOURCE_ONE_OUTSIDE_SCHEMA,
            SOURCE_ONE_OUTSIDE_STATUS,
        ),
        (
            "cascade endpoint-8 target packet",
            cascade_endpoint8_targets,
            SOURCE_CASCADE_ENDPOINT8_SCHEMA,
            SOURCE_CASCADE_ENDPOINT8_STATUS,
        ),
    ]
    for label, payload, schema, status in expected:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")

    preflight_summary = _mapping(
        center8_preflight.get("summary"), "center-8 preflight summary", errors
    )
    if preflight_summary.get("gate_status") != SOURCE_CENTER8_PREFLIGHT_GATE_STATUS:
        errors.append("center-8 preflight gate status mismatch")
    singleton_summary = _mapping(
        singleton_audit.get("summary"), "source-151 singleton summary", errors
    )
    if singleton_summary.get("scan_status") != SOURCE_SINGLETON_SCAN_STATUS:
        errors.append("source-151 singleton scan status mismatch")
    cascade_summary = _mapping(
        cascade_endpoint8_targets.get("summary"), "cascade endpoint summary", errors
    )
    if cascade_summary.get("target_status") != SOURCE_CASCADE_ENDPOINT8_TARGET_STATUS:
        errors.append("cascade endpoint target status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": (
            "do_not_reuse_source151_row8_singleton_packet_as_center8_"
            "cascade_source"
        ),
        "gate_status": GATE_STATUS,
        "decision_status": DECISION_STATUS,
        "current_source151_named_center8_evidence_supplies_cascade_triple": False,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    question = decision.get("decision_question")
    if not isinstance(question, str) or "[0,4,6]" not in question:
        errors.append("decision.decision_question must name [0,4,6]")
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "genuine geometric source" not in required_next:
        errors.append("decision.required_next_lemma must keep the geometric gap open")


def _validate_crosswalk_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != 2:
        errors.append("source_crosswalk_records must contain two records")
        return
    names = [record.get("source_name") for record in records if isinstance(record, Mapping)]
    expected_names = [
        "source-151 row-8 singleton activation candidates",
        "source-151 row-8 one-outside support activations",
    ]
    if names != expected_names:
        errors.append(f"source crosswalk names mismatch: got {names!r}")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"source_crosswalk_records[{index}] must be an object")
            continue
        if record.get("supplies_cascade_triple") is not False:
            errors.append(f"source_crosswalk_records[{index}] overclaims supply")
        if record.get("row_center") != ENDPOINT_CENTER:
            errors.append(f"source_crosswalk_records[{index}] row_center mismatch")
        if record.get("source_record_id") != 151:
            errors.append(f"source_crosswalk_records[{index}] source id mismatch")
    singleton_record = records[0]
    if isinstance(singleton_record, Mapping):
        if singleton_record.get("candidate_rows_with_target_pair_count") != 0:
            errors.append("singleton candidates must not contain target pairs")
        if singleton_record.get("candidate_rows_with_full_target_triple_count") != 0:
            errors.append("singleton candidates must not contain full target triple")
        if singleton_record.get("max_target_triple_overlap") != 1:
            errors.append("singleton candidates should overlap the target by at most one")


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
        "gate_status": summary.get("gate_status"),
        "scan_status": summary.get("scan_status"),
        "target_status": summary.get("target_status"),
    }


def _int_list(values: object) -> list[int]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise AssertionError("expected a sequence of integers")
    return [int(value) for value in values]


def _int_rows(rows: object) -> list[list[int]]:
    if not isinstance(rows, Sequence) or isinstance(rows, (str, bytes)):
        raise AssertionError("expected a sequence of rows")
    return [_int_list(row) for row in rows]


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
        "--source-center8-preflight",
        type=Path,
        default=DEFAULT_SOURCE_CENTER8_PREFLIGHT,
    )
    parser.add_argument(
        "--source-singleton-audit",
        type=Path,
        default=DEFAULT_SOURCE_SINGLETON_AUDIT,
    )
    parser.add_argument(
        "--source-one-outside",
        type=Path,
        default=DEFAULT_SOURCE_ONE_OUTSIDE,
    )
    parser.add_argument(
        "--source-cascade-endpoint8-targets",
        type=Path,
        default=DEFAULT_SOURCE_CASCADE_ENDPOINT8_TARGETS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_center8_preflight = _resolve(args.source_center8_preflight)
    source_singleton_audit = _resolve(args.source_singleton_audit)
    source_one_outside = _resolve(args.source_one_outside)
    source_cascade_endpoint8_targets = _resolve(args.source_cascade_endpoint8_targets)

    generated = build_center8_source_crosswalk_payload(
        load_artifact(source_center8_preflight),
        load_artifact(source_singleton_audit),
        load_artifact(source_one_outside),
        load_artifact(source_cascade_endpoint8_targets),
        center8_preflight_path=source_center8_preflight,
        singleton_audit_path=source_singleton_audit,
        one_outside_path=source_one_outside,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        center8_preflight_path=source_center8_preflight,
        singleton_audit_path=source_singleton_audit,
        one_outside_path=source_one_outside,
        cascade_endpoint8_targets_path=source_cascade_endpoint8_targets,
    )
    if args.assert_expected:
        assert_expected_center8_source_crosswalk(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 center-8 source crosswalk")
        print(f"target row: {summary['target_row_key']}")
        print(f"cascade target: {summary['conditional_center8_triple']}")
        print(
            "source-151 row-8 singleton max overlap: "
            f"{summary['source151_named_center8_max_target_triple_overlap']}"
        )
        print(
            "source-151 row-8 target-pair rows: "
            f"{summary['source151_named_center8_candidate_rows_with_target_pair_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: center-8 source crosswalk verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
