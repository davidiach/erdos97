#!/usr/bin/env python3
"""Check support hypotheses for the 151:6 label-4 transfer components."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402

from scripts.check_bootstrap_t12_151_6_label4_transfer_component_feasibility import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_FEASIBILITY,
    FEASIBILITY_STATUS as SOURCE_FEASIBILITY_STATUS,
    SCHEMA as SOURCE_FEASIBILITY_SCHEMA,
    STATUS as SOURCE_FEASIBILITY_STATUS_TEXT,
    assert_expected_component_feasibility,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_label4_transfer_length_components import (  # noqa: E402
    COMPONENT_STATUS as SOURCE_COMPONENT_STATUS,
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_COMPONENTS,
    SCHEMA as SOURCE_COMPONENTS_SCHEMA,
    STATUS as SOURCE_COMPONENTS_STATUS,
    assert_expected_label4_transfer_length_components,
)
from scripts.check_bootstrap_t12_151_6_label4_transfer_obligations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_OBLIGATIONS,
    OBLIGATION_STATUS as SOURCE_OBLIGATION_STATUS,
    SCHEMA as SOURCE_OBLIGATIONS_SCHEMA,
    STATUS as SOURCE_OBLIGATIONS_STATUS,
    assert_expected_label4_transfer_obligations,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _json_counter,
)


LABEL4 = 4
LABEL8 = 8

SCHEMA = "erdos97.bootstrap_t12_151_6_label4_support_hypothesis_ledger.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_SUPPORT_HYPOTHESIS_LEDGER_DIAGNOSTIC_ONLY"
LEDGER_STATUS = "LABEL4_SUPPORT_HYPOTHESES_PINNED_NOT_DISCHARGED"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It refines the six label-4 transfer length "
    "components into the genuine centered support hypotheses that a future "
    "support-geometry exclusion must add. The ledger records that the only "
    "component using the target center is the cascade "
    "D[0,6]=D[4,5]=D[5,6], and that no label-4 transfer support requirement "
    "is the exact private support pair [3,5]. This does not discharge those "
    "support hypotheses, does not prove outside-pair support existence, does "
    "not prove row forcing, does not prove pair [3,5] impossible, does not "
    "prove endpoint-8 forcing, does not prove n=9, does not prove the "
    "bridge, is not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_support_hypothesis_ledger.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_support_hypothesis_ledger.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "support_need_records",
    "support_requirement_records",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_length_component_count": 6,
    "source_unique_segment_count": 9,
    "source_feasible_component_count": 6,
    "support_need_record_count": 6,
    "unique_centered_support_requirement_count": 7,
    "component_count_by_required_support_center_count": {
        "1": 5,
        "2": 1,
    },
    "component_incidence_count_by_required_center": {
        "5": 4,
        "6": 1,
        "7": 2,
    },
    "unique_support_requirement_count_by_center": {
        "5": 4,
        "6": 1,
        "7": 2,
    },
    "support_requirement_signature_count_by_center": {
        "5": 6,
        "6": 3,
        "7": 2,
    },
    "support_requirement_occurrence_count_by_center": {
        "5": 7,
        "6": 4,
        "7": 2,
    },
    "unique_support_requirement_count_by_role": {
        "row5_label4_spoke_swap": 3,
        "row5_label4_to_target_center_step": 1,
        "row6_target_connector_step": 1,
        "row7_label4_spoke_swap": 2,
    },
    "support_requirement_signature_count_by_role": {
        "row5_label4_spoke_swap": 3,
        "row5_label4_to_target_center_step": 3,
        "row6_target_connector_step": 3,
        "row7_label4_spoke_swap": 2,
    },
    "support_requirement_occurrence_count_by_role": {
        "row5_label4_spoke_swap": 3,
        "row5_label4_to_target_center_step": 4,
        "row6_target_connector_step": 4,
        "row7_label4_spoke_swap": 2,
    },
    "components_requiring_row6_target_connector_count": 1,
    "components_requiring_private_target_class_witness_subset_count": 1,
    "unique_requirements_with_private_target_class_witness_subset_count": 1,
    "components_requiring_exact_private_support_pair_count": 0,
    "unique_requirements_with_exact_private_support_pair_count": 0,
    "components_requiring_target_center_as_auxiliary_witness_count": 1,
    "components_requiring_label4_witness_count": 6,
    "components_requiring_label8_witness_count": 0,
    "components_with_center8_auxiliary_center_count": 1,
    "positive_transfer_signature_counts_by_auxiliary_center_pair": {
        "2,5": 1,
        "2,7": 1,
        "3,5": 1,
        "3,7": 1,
        "4,5": 1,
        "5,8": 3,
    },
    "positive_transfer_occurrence_counts_by_auxiliary_center_pair": {
        "2,5": 1,
        "2,7": 1,
        "3,5": 1,
        "3,7": 1,
        "4,5": 1,
        "5,8": 4,
    },
    "component_count_by_access_mode": {
        "direct_cycle_edge": 4,
        "quotient_equality_only": 2,
    },
    "positive_transfer_signature_count_by_access_mode": {
        "direct_cycle_edge": 6,
        "quotient_equality_only": 2,
    },
    "component_alone_obstruction_status": SOURCE_FEASIBILITY_STATUS,
    "cascade_component_key": "D[0,6]=D[4,5]=D[5,6]",
    "cascade_component_signature_count": 3,
    "cascade_component_occurrence_count": 4,
    "cascade_required_support_centers": [5, 6],
    "cascade_required_witness_pairs": [[4, 6], [0, 5]],
    "cascade_auxiliary_center_pair_signature_counts": {"5,8": 3},
    "cascade_auxiliary_center_pair_occurrence_counts": {"5,8": 4},
    "source_component_status": SOURCE_COMPONENT_STATUS,
    "source_obligation_status": SOURCE_OBLIGATION_STATUS,
    "ledger_status": LEDGER_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_support_hypothesis_ledger_payload(
    source_components: Mapping[str, Any],
    source_obligations: Mapping[str, Any],
    source_feasibility: Mapping[str, Any],
    *,
    source_components_path: Path = DEFAULT_SOURCE_COMPONENTS,
    source_obligations_path: Path = DEFAULT_SOURCE_OBLIGATIONS,
    source_feasibility_path: Path = DEFAULT_SOURCE_FEASIBILITY,
) -> dict[str, Any]:
    """Return the deterministic support-hypothesis ledger payload."""

    errors: list[str] = []
    assert_expected_label4_transfer_length_components(source_components)
    assert_expected_label4_transfer_obligations(source_obligations)
    assert_expected_component_feasibility(source_feasibility)
    _validate_sources(source_components, source_obligations, source_feasibility, errors)
    support_needs, support_requirements, summary = _support_hypothesis_records(
        source_components,
        source_obligations,
        source_feasibility,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "support_need_records": support_needs,
        "support_requirement_records": support_requirements,
        "source_artifacts": [
            _source_summary(
                source_components_path,
                "source 151:6 label-4 transfer length components",
                source_components,
            ),
            _source_summary(
                source_obligations_path,
                "source 151:6 label-4 transfer obligations",
                source_obligations,
            ),
            _source_summary(
                source_feasibility_path,
                "source 151:6 component-alone feasibility controls",
                source_feasibility,
            ),
        ],
        "interpretation": [
            (
                "Each support requirement is a centered equal-distance "
                "hypothesis from the row-local transfer-obligation ledger."
            ),
            (
                "The row-6 cascade requires two support centers: center 5 "
                "with witnesses [4,6], and center 6 with witnesses [0,5]."
            ),
            (
                "None of the seven centered support requirements is the exact "
                "private pair [3,5], so the private-pair hypothesis remains "
                "an additional geometric input."
            ),
            (
                "The component-alone cyclic witnesses remain negative "
                "controls; this packet only names the extra hypotheses a "
                "future exclusion must use."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_support_hypothesis_ledger(payload)
    return payload


def assert_expected_support_hypothesis_ledger(payload: Mapping[str, Any]) -> None:
    """Assert the pinned support-hypothesis ledger."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_components_path: Path = DEFAULT_SOURCE_COMPONENTS,
    source_obligations_path: Path = DEFAULT_SOURCE_OBLIGATIONS,
    source_feasibility_path: Path = DEFAULT_SOURCE_FEASIBILITY,
) -> list[str]:
    """Return validation errors for a support-hypothesis ledger payload."""

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
            "does not discharge those support hypotheses",
            "does not prove outside-pair support existence",
            "does not prove row forcing",
            "does not prove pair [3,5] impossible",
            "does not prove endpoint-8 forcing",
            "does not prove n=9",
            "does not prove the bridge",
            "not a counterexample",
            "not a global status update",
        ):
            if phrase not in claim_scope:
                errors.append(f"claim_scope must contain {phrase!r}")

    summary = _mapping(payload.get("summary"), "summary", errors)
    _validate_summary(summary, errors)

    support_needs = payload.get("support_need_records")
    if not isinstance(support_needs, list):
        errors.append("support_need_records must be a list")
    else:
        _validate_support_need_records(support_needs, errors)

    support_requirements = payload.get("support_requirement_records")
    if not isinstance(support_requirements, list):
        errors.append("support_requirement_records must be a list")
    else:
        _validate_support_requirement_records(support_requirements, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any(
        "private-pair hypothesis remains an additional" in str(item)
        for item in interpretation
    ):
        errors.append("interpretation must preserve the private-pair gap")

    if recompute and not errors:
        generated = build_support_hypothesis_ledger_payload(
            load_artifact(source_components_path),
            load_artifact(source_obligations_path),
            load_artifact(source_feasibility_path),
            source_components_path=source_components_path,
            source_obligations_path=source_obligations_path,
            source_feasibility_path=source_feasibility_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source artifacts")
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
        "support_need_record_count": summary.get("support_need_record_count"),
        "unique_centered_support_requirement_count": summary.get(
            "unique_centered_support_requirement_count"
        ),
        "components_requiring_row6_target_connector_count": summary.get(
            "components_requiring_row6_target_connector_count"
        ),
        "components_requiring_exact_private_support_pair_count": summary.get(
            "components_requiring_exact_private_support_pair_count"
        ),
        "cascade_component_key": summary.get("cascade_component_key"),
        "ledger_status": summary.get("ledger_status"),
        "validation_errors": list(errors),
    }


def _support_hypothesis_records(
    source_components: Mapping[str, Any],
    source_obligations: Mapping[str, Any],
    source_feasibility: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    edge_by_key = {
        str(edge["obligation_key"]): edge
        for edge in source_obligations["unique_edge_obligation_records"]
    }
    transfer_by_index = {
        int(record["transfer_record_index"]): record
        for record in source_obligations["transfer_obligation_records"]
    }
    feasibility_by_component = {
        str(record["component_key"]): record
        for record in source_feasibility["witness_records"]
    }

    support_needs: list[dict[str, Any]] = []
    requirement_buckets: dict[str, dict[str, Any]] = {}
    required_center_count_by_component: Counter[int] = Counter()
    component_center_incidence_counts: Counter[int] = Counter()
    component_access_mode_counts: Counter[str] = Counter()
    access_mode_signature_counts: Counter[str] = Counter()
    auxiliary_pair_signature_counts: Counter[str] = Counter()
    auxiliary_pair_occurrence_counts: Counter[str] = Counter()
    components_requiring_row6 = 0
    components_requiring_private_target_subset = 0
    components_requiring_exact_private_pair = 0
    components_requiring_target_center_witness = 0
    components_requiring_label4 = 0
    components_requiring_label8 = 0
    components_with_center8_auxiliary = 0
    cascade_record: dict[str, Any] | None = None

    for component in source_components["length_component_records"]:
        component_key = str(component["component_key"])
        transfer_records = [
            transfer_by_index[int(index)]
            for index in component["transfer_record_indices"]
        ]
        support_requirements = [
            _support_requirement(edge_by_key[str(key)])
            for key in component["source_obligation_keys"]
        ]
        required_centers = sorted(
            {int(requirement["center"]) for requirement in support_requirements}
        )
        required_roles = sorted(
            {str(requirement["obligation_role"]) for requirement in support_requirements}
        )
        required_witness_pairs = [
            list(requirement["witness_pair"])
            for requirement in sorted(
                support_requirements,
                key=lambda item: (int(item["center"]), item["witness_pair"]),
            )
        ]
        access_modes = {
            key: int(value)
            for key, value in sorted(component["access_mode_counts"].items())
        }
        component_aux_signature_counts = Counter(
            str(record["auxiliary_center_pair"]) for record in transfer_records
        )
        component_aux_occurrence_counts = Counter()
        for record in transfer_records:
            pair_key = str(record["auxiliary_center_pair"])
            multiplicity = int(record["multiplicity"])
            component_aux_occurrence_counts[pair_key] += multiplicity
            auxiliary_pair_signature_counts[pair_key] += 1
            auxiliary_pair_occurrence_counts[pair_key] += multiplicity
        access_mode_signature_counts.update(access_modes)
        for mode in access_modes:
            component_access_mode_counts[mode] += 1

        requires_row6 = any(
            bool(requirement["center_is_target_center"])
            for requirement in support_requirements
        )
        requires_private_subset = any(
            bool(requirement["witness_pair_subset_of_private_target_class"])
            for requirement in support_requirements
        )
        requires_exact_private_pair = any(
            bool(requirement["witness_pair_equals_private_support_pair"])
            for requirement in support_requirements
        )
        requires_target_center_witness = any(
            bool(requirement["target_center_as_auxiliary_witness"])
            for requirement in support_requirements
        )
        requires_label4 = any(
            bool(requirement["label4_as_witness"])
            for requirement in support_requirements
        )
        requires_label8 = any(
            bool(requirement["label8_as_witness"])
            for requirement in support_requirements
        )
        center8_auxiliary = any(
            _pair_contains_label(str(record["auxiliary_center_pair"]), LABEL8)
            for record in transfer_records
        )

        if requires_row6:
            components_requiring_row6 += 1
        if requires_private_subset:
            components_requiring_private_target_subset += 1
        if requires_exact_private_pair:
            components_requiring_exact_private_pair += 1
        if requires_target_center_witness:
            components_requiring_target_center_witness += 1
        if requires_label4:
            components_requiring_label4 += 1
        if requires_label8:
            components_requiring_label8 += 1
        if center8_auxiliary:
            components_with_center8_auxiliary += 1

        required_center_count_by_component[len(required_centers)] += 1
        for center in required_centers:
            component_center_incidence_counts[center] += 1

        feasibility = feasibility_by_component[component_key]
        need_record = {
            "component_key": component_key,
            "source_path_motif_key": component["source_path_motif_key"],
            "path_shape": component["path_shape"],
            "geometry_class": component["geometry_class"],
            "signature_incidence_count": component["signature_incidence_count"],
            "occurrence_incidence_count": component["occurrence_incidence_count"],
            "signature_indices": component["signature_indices"],
            "transfer_record_indices": component["transfer_record_indices"],
            "access_mode_counts": access_modes,
            "auxiliary_center_pair_signature_counts": _json_counter(
                component_aux_signature_counts
            ),
            "auxiliary_center_pair_occurrence_counts": _json_counter(
                component_aux_occurrence_counts
            ),
            "required_support_center_count": len(required_centers),
            "required_support_centers": required_centers,
            "required_support_roles": required_roles,
            "required_witness_pairs": required_witness_pairs,
            "support_requirements": support_requirements,
            "requires_row6_target_connector": requires_row6,
            "requires_private_target_class_witness_subset": requires_private_subset,
            "requires_exact_private_support_pair": requires_exact_private_pair,
            "requires_target_center_as_auxiliary_witness": (
                requires_target_center_witness
            ),
            "requires_label4_witness": requires_label4,
            "requires_label8_witness": requires_label8,
            "component_alone_feasible": (
                feasibility["witness_status"] == "feasible"
            ),
            "component_alone_witness_modulus": (
                feasibility["regular_polygon_modulus"]
            ),
            "component_alone_witness_scope": feasibility["witness_scope"],
            "next_proof_obligation": _next_proof_obligation(component_key, requires_row6),
        }
        support_needs.append(need_record)
        if component_key == EXPECTED_SUMMARY["cascade_component_key"]:
            cascade_record = need_record
        for requirement in support_requirements:
            _add_requirement_bucket(requirement_buckets, requirement, need_record)

    requirement_records = [
        _finalize_requirement_bucket(bucket)
        for _, bucket in sorted(requirement_buckets.items(), key=lambda item: item[0])
    ]
    if cascade_record is None:
        raise AssertionError("cascade support need missing")

    unique_center_counts = Counter(
        int(record["center"]) for record in requirement_records
    )
    signature_count_by_center = Counter()
    occurrence_count_by_center = Counter()
    unique_role_counts: Counter[str] = Counter()
    signature_count_by_role: Counter[str] = Counter()
    occurrence_count_by_role: Counter[str] = Counter()
    private_subset_requirement_count = 0
    exact_private_pair_requirement_count = 0
    for record in requirement_records:
        center = int(record["center"])
        role = str(record["obligation_role"])
        signature_count = int(record["signature_incidence_count"])
        occurrence_count = int(record["occurrence_incidence_count"])
        signature_count_by_center[center] += signature_count
        occurrence_count_by_center[center] += occurrence_count
        unique_role_counts[role] += 1
        signature_count_by_role[role] += signature_count
        occurrence_count_by_role[role] += occurrence_count
        if record["witness_pair_subset_of_private_target_class"]:
            private_subset_requirement_count += 1
        if record["witness_pair_equals_private_support_pair"]:
            exact_private_pair_requirement_count += 1

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_length_component_count": source_components["summary"][
            "length_component_count"
        ],
        "source_unique_segment_count": source_components["summary"][
            "unique_segment_count"
        ],
        "source_feasible_component_count": source_feasibility["summary"][
            "feasible_component_count"
        ],
        "support_need_record_count": len(support_needs),
        "unique_centered_support_requirement_count": len(requirement_records),
        "component_count_by_required_support_center_count": _json_counter(
            required_center_count_by_component
        ),
        "component_incidence_count_by_required_center": _json_counter(
            component_center_incidence_counts
        ),
        "unique_support_requirement_count_by_center": _json_counter(
            unique_center_counts
        ),
        "support_requirement_signature_count_by_center": _json_counter(
            signature_count_by_center
        ),
        "support_requirement_occurrence_count_by_center": _json_counter(
            occurrence_count_by_center
        ),
        "unique_support_requirement_count_by_role": _json_counter(unique_role_counts),
        "support_requirement_signature_count_by_role": _json_counter(
            signature_count_by_role
        ),
        "support_requirement_occurrence_count_by_role": _json_counter(
            occurrence_count_by_role
        ),
        "components_requiring_row6_target_connector_count": (
            components_requiring_row6
        ),
        "components_requiring_private_target_class_witness_subset_count": (
            components_requiring_private_target_subset
        ),
        "unique_requirements_with_private_target_class_witness_subset_count": (
            private_subset_requirement_count
        ),
        "components_requiring_exact_private_support_pair_count": (
            components_requiring_exact_private_pair
        ),
        "unique_requirements_with_exact_private_support_pair_count": (
            exact_private_pair_requirement_count
        ),
        "components_requiring_target_center_as_auxiliary_witness_count": (
            components_requiring_target_center_witness
        ),
        "components_requiring_label4_witness_count": components_requiring_label4,
        "components_requiring_label8_witness_count": components_requiring_label8,
        "components_with_center8_auxiliary_center_count": (
            components_with_center8_auxiliary
        ),
        "positive_transfer_signature_counts_by_auxiliary_center_pair": _json_counter(
            auxiliary_pair_signature_counts
        ),
        "positive_transfer_occurrence_counts_by_auxiliary_center_pair": _json_counter(
            auxiliary_pair_occurrence_counts
        ),
        "component_count_by_access_mode": _json_counter(component_access_mode_counts),
        "positive_transfer_signature_count_by_access_mode": _json_counter(
            access_mode_signature_counts
        ),
        "component_alone_obstruction_status": source_feasibility["summary"][
            "component_alone_obstruction_status"
        ],
        "cascade_component_key": cascade_record["component_key"],
        "cascade_component_signature_count": cascade_record[
            "signature_incidence_count"
        ],
        "cascade_component_occurrence_count": cascade_record[
            "occurrence_incidence_count"
        ],
        "cascade_required_support_centers": cascade_record[
            "required_support_centers"
        ],
        "cascade_required_witness_pairs": cascade_record["required_witness_pairs"],
        "cascade_auxiliary_center_pair_signature_counts": cascade_record[
            "auxiliary_center_pair_signature_counts"
        ],
        "cascade_auxiliary_center_pair_occurrence_counts": cascade_record[
            "auxiliary_center_pair_occurrence_counts"
        ],
        "source_component_status": SOURCE_COMPONENT_STATUS,
        "source_obligation_status": SOURCE_OBLIGATION_STATUS,
        "ledger_status": LEDGER_STATUS,
    }
    support_needs = sorted(support_needs, key=lambda record: record["component_key"])
    return support_needs, requirement_records, summary


def _support_requirement(edge: Mapping[str, Any]) -> dict[str, Any]:
    center = int(edge["row"])
    witness_pair = [int(item) for item in edge["row_witness_pair"]]
    witness_set = set(witness_pair)
    private_target_set = set(PRIVATE_TARGET_CLASS)
    private_pair = sorted(int(item) for item in PRIVATE_SUPPORT_PAIR)
    left_pair = [int(item) for item in edge["from_pair"]]
    right_pair = [int(item) for item in edge["to_pair"]]
    return {
        "requirement_key": edge["obligation_key"],
        "center": center,
        "witness_pair": witness_pair,
        "left_pair": left_pair,
        "right_pair": right_pair,
        "centered_distance_equality": {
            "center": center,
            "witness_pair": witness_pair,
            "left_pair": left_pair,
            "right_pair": right_pair,
        },
        "obligation_role": edge["obligation_role"],
        "signature_incidence_count": int(edge["signature_incidence_count"]),
        "occurrence_incidence_count": int(edge["occurrence_incidence_count"]),
        "signature_indices": edge["signature_indices"],
        "transfer_record_indices": edge["transfer_record_indices"],
        "center_is_target_center": center == TARGET_CENTER,
        "witness_pair_subset_of_private_target_class": (
            witness_set <= private_target_set
        ),
        "witness_pair_equals_private_support_pair": sorted(witness_pair) == private_pair,
        "target_center_as_auxiliary_witness": (
            center != TARGET_CENTER and TARGET_CENTER in witness_set
        ),
        "label4_as_witness": LABEL4 in witness_set,
        "label8_as_witness": LABEL8 in witness_set,
        "support_hypothesis": _support_hypothesis_text(center, witness_pair),
    }


def _support_hypothesis_text(center: int, witness_pair: Sequence[int]) -> str:
    return (
        f"center {center} has a selected-distance support class containing "
        f"witnesses {int(witness_pair[0])} and {int(witness_pair[1])}"
    )


def _next_proof_obligation(component_key: str, requires_row6: bool) -> str:
    if requires_row6:
        return (
            "Exclude the cascade only after adding the genuine row-5 [4,6] "
            "support, row-6 private-class [0,5] support, and private-pair "
            "[3,5] or rich-class hypotheses."
        )
    return (
        f"Exclude {component_key} only after adding the genuine auxiliary "
        "label-4 support and the private target-row support hypotheses."
    )


def _add_requirement_bucket(
    buckets: dict[str, dict[str, Any]],
    requirement: Mapping[str, Any],
    component: Mapping[str, Any],
) -> None:
    key = str(requirement["requirement_key"])
    if key not in buckets:
        buckets[key] = {
            **requirement,
            "component_keys": [],
            "component_path_shape_counts": Counter(),
            "component_geometry_class_counts": Counter(),
        }
    bucket = buckets[key]
    bucket["component_keys"].append(component["component_key"])
    bucket["component_path_shape_counts"][component["path_shape"]] += 1
    bucket["component_geometry_class_counts"][component["geometry_class"]] += 1


def _finalize_requirement_bucket(bucket: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(bucket)
    result["component_keys"] = sorted(set(result["component_keys"]))
    result["component_count"] = len(result["component_keys"])
    result["component_path_shape_counts"] = _json_counter(
        result["component_path_shape_counts"]
    )
    result["component_geometry_class_counts"] = _json_counter(
        result["component_geometry_class_counts"]
    )
    return result


def _validate_sources(
    source_components: Mapping[str, Any],
    source_obligations: Mapping[str, Any],
    source_feasibility: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected_sources = (
        (
            "source length components",
            source_components,
            SOURCE_COMPONENTS_SCHEMA,
            SOURCE_COMPONENTS_STATUS,
        ),
        (
            "source obligations",
            source_obligations,
            SOURCE_OBLIGATIONS_SCHEMA,
            SOURCE_OBLIGATIONS_STATUS,
        ),
        (
            "source feasibility",
            source_feasibility,
            SOURCE_FEASIBILITY_SCHEMA,
            SOURCE_FEASIBILITY_STATUS_TEXT,
        ),
    )
    for name, payload, schema, status in expected_sources:
        if payload.get("schema") != schema:
            errors.append(f"{name} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{name} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{name} trust mismatch")
    components_summary = _mapping(
        source_components.get("summary"), "source components summary", errors
    )
    obligations_summary = _mapping(
        source_obligations.get("summary"), "source obligations summary", errors
    )
    feasibility_summary = _mapping(
        source_feasibility.get("summary"), "source feasibility summary", errors
    )
    expected_counts = {
        "source components length_component_count": (
            components_summary.get("length_component_count"),
            6,
        ),
        "source obligations unique_edge_obligation_count": (
            obligations_summary.get("unique_edge_obligation_count"),
            7,
        ),
        "source feasibility feasible_component_count": (
            feasibility_summary.get("feasible_component_count"),
            6,
        ),
    }
    for name, (actual, expected) in expected_counts.items():
        if actual != expected:
            errors.append(f"{name} mismatch: expected {expected!r}, got {actual!r}")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_support_need_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["support_need_record_count"]:
        errors.append("support_need_records length mismatch")
    seen: set[str] = set()
    cascade_seen = False
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"support_need_records[{index}] must be an object")
            continue
        key = record.get("component_key")
        if not isinstance(key, str) or not key:
            errors.append(f"support_need_records[{index}] component key missing")
            continue
        if key in seen:
            errors.append(f"support_need_records[{index}] duplicate component key")
        seen.add(key)
        requirements = record.get("support_requirements")
        if not isinstance(requirements, list):
            errors.append(f"support_need_records[{index}] requirements must be a list")
            continue
        if record.get("required_support_center_count") != len(
            set(record.get("required_support_centers", []))
        ):
            errors.append(f"support_need_records[{index}] support center count drift")
        if any(
            isinstance(requirement, Mapping)
            and requirement.get("witness_pair_equals_private_support_pair")
            for requirement in requirements
        ):
            errors.append(f"support_need_records[{index}] unexpectedly uses [3,5]")
        if key == EXPECTED_SUMMARY["cascade_component_key"]:
            cascade_seen = True
            if not record.get("requires_row6_target_connector"):
                errors.append("cascade must require row-6 target connector")
            if record.get("required_support_centers") != [5, 6]:
                errors.append("cascade support centers mismatch")
    if not cascade_seen:
        errors.append("cascade support need missing")


def _validate_support_requirement_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    if len(records) != EXPECTED_SUMMARY["unique_centered_support_requirement_count"]:
        errors.append("support_requirement_records length mismatch")
    seen: set[str] = set()
    private_pair_count = 0
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"support_requirement_records[{index}] must be an object")
            continue
        key = record.get("requirement_key")
        if not isinstance(key, str) or not key:
            errors.append(f"support_requirement_records[{index}] key missing")
            continue
        if key in seen:
            errors.append(f"support_requirement_records[{index}] duplicate key")
        seen.add(key)
        if record.get("witness_pair_equals_private_support_pair"):
            private_pair_count += 1
        center = record.get("center")
        if center not in {5, 6, 7}:
            errors.append(f"support_requirement_records[{index}] unexpected center")
        witness_pair = record.get("witness_pair")
        if not _is_pair_list(witness_pair):
            errors.append(f"support_requirement_records[{index}] bad witness pair")
    if private_pair_count != 0:
        errors.append("private pair [3,5] should remain unhit")


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "component_status": (
            summary.get("component_status") if isinstance(summary, Mapping) else None
        ),
        "obligation_status": (
            summary.get("obligation_status") if isinstance(summary, Mapping) else None
        ),
        "component_alone_obstruction_status": (
            summary.get("component_alone_obstruction_status")
            if isinstance(summary, Mapping)
            else None
        ),
    }


def _pair_contains_label(pair_key: str, label: int) -> bool:
    return label in {int(item) for item in pair_key.split(",")}


def _is_pair_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and len(value) == 2
        and all(isinstance(item, int) for item in value)
    )


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-components",
        type=Path,
        default=DEFAULT_SOURCE_COMPONENTS,
    )
    parser.add_argument(
        "--source-obligations",
        type=Path,
        default=DEFAULT_SOURCE_OBLIGATIONS,
    )
    parser.add_argument(
        "--source-feasibility",
        type=Path,
        default=DEFAULT_SOURCE_FEASIBILITY,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_components = _resolve(args.source_components)
    source_obligations = _resolve(args.source_obligations)
    source_feasibility = _resolve(args.source_feasibility)

    generated = build_support_hypothesis_ledger_payload(
        load_artifact(source_components),
        load_artifact(source_obligations),
        load_artifact(source_feasibility),
        source_components_path=source_components,
        source_obligations_path=source_obligations,
        source_feasibility_path=source_feasibility,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_components_path=source_components,
        source_obligations_path=source_obligations,
        source_feasibility_path=source_feasibility,
    )
    if args.assert_expected:
        assert_expected_support_hypothesis_ledger(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 support hypothesis ledger")
        print(f"target row: {summary['target_row_key']}")
        print(f"support needs: {summary['support_need_record_count']}")
        print(
            "unique support requirements: "
            f"{summary['unique_centered_support_requirement_count']}"
        )
        print(f"cascade: {summary['cascade_component_key']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
