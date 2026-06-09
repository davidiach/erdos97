#!/usr/bin/env python3
"""Check row-local obligations in the 151:6 label-4 transfer paths."""

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

from scripts.check_bootstrap_t12_151_6_label4_transfer_paths import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_TRANSFER_PATHS,
    SCHEMA as SOURCE_TRANSFER_PATHS_SCHEMA,
    STATUS as SOURCE_TRANSFER_PATHS_STATUS,
    TRANSFER_STATUS as SOURCE_TRANSFER_STATUS,
    assert_expected_label4_transfer_paths,
    load_artifact,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
    _json_counter,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_transfer_obligations.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_TRANSFER_OBLIGATIONS_DIAGNOSTIC_ONLY"
OBLIGATION_STATUS = "ROW_LOCAL_LABEL4_TRANSFER_OBLIGATIONS_PINNED"
CLAIM_SCOPE = (
    "Proof-target diagnostic for the source-151 row-6 private-halo-only "
    "outside-pair lane. It refines the label-4 transfer-path ledger into "
    "row-local selected-distance equality obligations. Every positive "
    "transfer starts with a label-4 spoke swap at row 5 or row 7; the only "
    "row-6 obligations are the second step of a repeated row-5 to row-6 "
    "connector cascade. This does not prove outside-pair support existence, "
    "does not prove row forcing, does not prove pair [3,5] impossible, does "
    "not prove endpoint-8 forcing, does not prove n=9, does not prove the "
    "bridge, is not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py"
    ),
    "command": (
        "python scripts/check_bootstrap_t12_151_6_label4_transfer_obligations.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_transfer_obligations.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "interpretation",
    "path_motif_records",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "transfer_obligation_records",
    "trust",
    "unique_edge_obligation_records",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "source_label4_transfer_path_class_signature_incidence_count": 19,
    "source_positive_transfer_class_signature_incidence_count": 8,
    "source_positive_transfer_class_occurrence_incidence_count": 9,
    "row_local_transfer_obligation_record_count": 8,
    "row_local_transfer_obligation_occurrence_count": 9,
    "row_local_transfer_edge_signature_count": 11,
    "row_local_transfer_edge_occurrence_count": 13,
    "unique_path_motif_count": 6,
    "unique_edge_obligation_count": 7,
    "label4_spoke_swap_edge_signature_count": 8,
    "label4_spoke_swap_edge_occurrence_count": 9,
    "target_center_touching_edge_signature_count": 6,
    "target_center_touching_edge_occurrence_count": 8,
    "row6_connector_step_signature_count": 3,
    "row6_connector_step_occurrence_count": 4,
    "two_edge_connector_cascade_signature_count": 3,
    "two_edge_connector_cascade_occurrence_count": 4,
    "quotient_equality_only_transfer_record_count": 2,
    "quotient_equality_only_transfer_occurrence_count": 2,
    "direct_cycle_access_positive_transfer_record_count": 6,
    "direct_cycle_access_positive_transfer_occurrence_count": 7,
    "positive_transfer_edge_signature_counts_by_row": {
        "5": 6,
        "6": 3,
        "7": 2,
    },
    "positive_transfer_edge_occurrence_counts_by_row": {
        "5": 7,
        "6": 4,
        "7": 2,
    },
    "path_shape_signature_counts": {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 3,
    },
    "path_shape_occurrence_counts": {
        "one_edge_row5_label4_spoke_swap": 3,
        "one_edge_row7_label4_spoke_swap": 2,
        "two_edge_row5_row6_connector_cascade": 4,
    },
    "obligation_status": OBLIGATION_STATUS,
}


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_label4_transfer_obligations_payload(
    source_transfer_paths: Mapping[str, Any],
    *,
    source_transfer_paths_path: Path = DEFAULT_SOURCE_TRANSFER_PATHS,
) -> dict[str, Any]:
    """Return the deterministic row-local transfer-obligation payload."""

    errors: list[str] = []
    assert_expected_label4_transfer_paths(source_transfer_paths)
    _validate_source_transfer_paths(source_transfer_paths, errors)
    (
        transfer_records,
        unique_edges,
        path_motifs,
        summary,
    ) = _obligation_records(source_transfer_paths)
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "transfer_obligation_records": transfer_records,
        "unique_edge_obligation_records": unique_edges,
        "path_motif_records": path_motifs,
        "source_artifacts": [
            _source_summary(
                source_transfer_paths_path,
                "source 151:6 label-4 transfer paths",
                source_transfer_paths,
            )
        ],
        "interpretation": [
            (
                "This packet records only positive-length transfer paths; "
                "direct endpoint hits have no row-local equality obligation "
                "beyond the already visible strict-cycle endpoint."
            ),
            (
                "All positive transfers start with a row-5 or row-7 equality "
                "from a label-4 spoke to a non-label-4 spoke at the same "
                "center."
            ),
            (
                "The only row-6 obligation is the connector step "
                "[5,6]=[0,6], and it appears only after the row-5 step "
                "[4,5]=[5,6]."
            ),
            (
                "This is a bridge-target obligation ledger only; it does not "
                "prove support existence, row forcing, endpoint-8 forcing, "
                "or impossibility of the private pair."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_label4_transfer_obligations(payload)
    return payload


def assert_expected_label4_transfer_obligations(
    payload: Mapping[str, Any],
) -> None:
    """Assert the pinned row-local label-4 transfer obligations."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    source_transfer_paths_path: Path = DEFAULT_SOURCE_TRANSFER_PATHS,
) -> list[str]:
    """Return validation errors for a row-local transfer-obligation payload."""

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
    transfer_records = payload.get("transfer_obligation_records")
    if not isinstance(transfer_records, list):
        errors.append("transfer_obligation_records must be a list")
    else:
        _validate_transfer_obligation_records(transfer_records, errors)
    unique_edges = payload.get("unique_edge_obligation_records")
    if not isinstance(unique_edges, list):
        errors.append("unique_edge_obligation_records must be a list")
    else:
        _validate_unique_edge_records(unique_edges, errors)
    path_motifs = payload.get("path_motif_records")
    if not isinstance(path_motifs, list):
        errors.append("path_motif_records must be a list")
    else:
        _validate_path_motif_records(path_motifs, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("does not prove support existence" in item for item in interpretation):
        errors.append("interpretation must preserve the support-existence nonclaim")

    if recompute and not errors:
        generated = build_label4_transfer_obligations_payload(
            load_artifact(source_transfer_paths_path),
            source_transfer_paths_path=source_transfer_paths_path,
        )
        if dict(payload) != generated:
            errors.append("stored artifact is stale relative to source artifact")
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
        "row_local_transfer_obligation_record_count": summary.get(
            "row_local_transfer_obligation_record_count"
        ),
        "unique_edge_obligation_count": summary.get("unique_edge_obligation_count"),
        "unique_path_motif_count": summary.get("unique_path_motif_count"),
        "row6_connector_step_signature_count": summary.get(
            "row6_connector_step_signature_count"
        ),
        "obligation_status": summary.get("obligation_status"),
        "validation_errors": list(errors),
    }


def _obligation_records(
    source_transfer_paths: Mapping[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    source_records = source_transfer_paths["transfer_path_records"]
    transfer_records: list[dict[str, Any]] = []
    edge_buckets: dict[str, dict[str, Any]] = {}
    path_buckets: dict[str, dict[str, Any]] = {}
    edge_signature_counts_by_row: Counter[int] = Counter()
    edge_occurrence_counts_by_row: Counter[int] = Counter()
    path_shape_signature_counts: Counter[str] = Counter()
    path_shape_occurrence_counts: Counter[str] = Counter()
    positive_occurrences = 0
    edge_signature_count = 0
    edge_occurrence_count = 0
    label4_spoke_edge_count = 0
    label4_spoke_occurrence_count = 0
    target_center_touching_edge_count = 0
    target_center_touching_occurrence_count = 0
    row6_connector_step_count = 0
    row6_connector_step_occurrence_count = 0
    quotient_equality_only_count = 0
    quotient_equality_only_occurrence_count = 0
    direct_cycle_access_count = 0
    direct_cycle_access_occurrence_count = 0
    two_edge_connector_cascade_count = 0
    two_edge_connector_cascade_occurrence_count = 0

    for record in source_records:
        transfer_path = record["transfer_path"]
        if not transfer_path:
            continue
        multiplicity = int(record["multiplicity"])
        positive_occurrences += multiplicity
        if record["access_mode"] == "quotient_equality_only":
            quotient_equality_only_count += 1
            quotient_equality_only_occurrence_count += multiplicity
        elif record["access_mode"] == "direct_cycle_edge":
            direct_cycle_access_count += 1
            direct_cycle_access_occurrence_count += multiplicity
        path_shape = _path_shape(transfer_path)
        path_shape_signature_counts[path_shape] += 1
        path_shape_occurrence_counts[path_shape] += multiplicity
        if path_shape == "two_edge_row5_row6_connector_cascade":
            two_edge_connector_cascade_count += 1
            two_edge_connector_cascade_occurrence_count += multiplicity
        obligation_edges: list[dict[str, Any]] = []
        path_keys: list[str] = []
        for edge_index, edge in enumerate(transfer_path):
            obligation = _edge_obligation(edge, edge_index)
            obligation_edges.append(obligation)
            path_keys.append(obligation["obligation_key"])
            row = int(obligation["row"])
            edge_signature_counts_by_row[row] += 1
            edge_occurrence_counts_by_row[row] += multiplicity
            edge_signature_count += 1
            edge_occurrence_count += multiplicity
            if obligation["label4_spoke_swap"]:
                label4_spoke_edge_count += 1
                label4_spoke_occurrence_count += multiplicity
            if obligation["touches_target_center"]:
                target_center_touching_edge_count += 1
                target_center_touching_occurrence_count += multiplicity
            if obligation["row6_connector_step"]:
                row6_connector_step_count += 1
                row6_connector_step_occurrence_count += multiplicity
            _add_edge_bucket(edge_buckets, obligation, record, multiplicity)
        motif_key = " -> ".join(path_keys)
        _add_path_bucket(
            path_buckets,
            motif_key,
            path_shape,
            path_keys,
            record,
            multiplicity,
        )
        transfer_records.append(
            {
                "transfer_record_index": record["transfer_record_index"],
                "signature_index": record["signature_index"],
                "multiplicity": multiplicity,
                "auxiliary_center_pair": record["auxiliary_center_pair"],
                "access_mode": record["access_mode"],
                "transfer_mode": record["transfer_mode"],
                "transfer_edge_count": record["transfer_edge_count"],
                "path_shape": path_shape,
                "chosen_label4_pair": record["chosen_label4_pair"],
                "chosen_cycle_endpoint_pair": record["chosen_cycle_endpoint_pair"],
                "row_obligations": obligation_edges,
            }
        )

    summary = {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "source_label4_transfer_path_class_signature_incidence_count": len(
            source_records
        ),
        "source_positive_transfer_class_signature_incidence_count": len(
            transfer_records
        ),
        "source_positive_transfer_class_occurrence_incidence_count": (
            positive_occurrences
        ),
        "row_local_transfer_obligation_record_count": len(transfer_records),
        "row_local_transfer_obligation_occurrence_count": positive_occurrences,
        "row_local_transfer_edge_signature_count": edge_signature_count,
        "row_local_transfer_edge_occurrence_count": edge_occurrence_count,
        "unique_path_motif_count": len(path_buckets),
        "unique_edge_obligation_count": len(edge_buckets),
        "label4_spoke_swap_edge_signature_count": label4_spoke_edge_count,
        "label4_spoke_swap_edge_occurrence_count": label4_spoke_occurrence_count,
        "target_center_touching_edge_signature_count": (
            target_center_touching_edge_count
        ),
        "target_center_touching_edge_occurrence_count": (
            target_center_touching_occurrence_count
        ),
        "row6_connector_step_signature_count": row6_connector_step_count,
        "row6_connector_step_occurrence_count": row6_connector_step_occurrence_count,
        "two_edge_connector_cascade_signature_count": two_edge_connector_cascade_count,
        "two_edge_connector_cascade_occurrence_count": (
            two_edge_connector_cascade_occurrence_count
        ),
        "quotient_equality_only_transfer_record_count": quotient_equality_only_count,
        "quotient_equality_only_transfer_occurrence_count": (
            quotient_equality_only_occurrence_count
        ),
        "direct_cycle_access_positive_transfer_record_count": (
            direct_cycle_access_count
        ),
        "direct_cycle_access_positive_transfer_occurrence_count": (
            direct_cycle_access_occurrence_count
        ),
        "positive_transfer_edge_signature_counts_by_row": _json_counter(
            edge_signature_counts_by_row
        ),
        "positive_transfer_edge_occurrence_counts_by_row": _json_counter(
            edge_occurrence_counts_by_row
        ),
        "path_shape_signature_counts": _json_counter(path_shape_signature_counts),
        "path_shape_occurrence_counts": _json_counter(path_shape_occurrence_counts),
        "obligation_status": OBLIGATION_STATUS,
    }
    unique_edges = [
        _finalize_edge_bucket(bucket)
        for _, bucket in sorted(edge_buckets.items(), key=lambda item: item[0])
    ]
    path_motifs = [
        _finalize_path_bucket(bucket)
        for _, bucket in sorted(path_buckets.items(), key=lambda item: item[0])
    ]
    return transfer_records, unique_edges, path_motifs, summary


def _edge_obligation(edge: Mapping[str, Any], edge_index: int) -> dict[str, Any]:
    row = int(edge["row"])
    from_pair = _int_list(edge["from_pair"])
    to_pair = _int_list(edge["to_pair"])
    row_witness_pair = _int_list(edge["row_witness_pair"])
    label4_spoke_swap = 4 in row_witness_pair and 4 in from_pair and 4 not in to_pair
    touches_target_center = TARGET_CENTER in from_pair or TARGET_CENTER in to_pair
    row6_connector_step = (
        row == TARGET_CENTER
        and row_witness_pair == [0, 5]
        and from_pair == [5, 6]
        and to_pair == [0, 6]
    )
    return {
        "edge_index": edge_index,
        "obligation_key": _obligation_key(row, from_pair, to_pair),
        "row": row,
        "from_pair": from_pair,
        "to_pair": to_pair,
        "row_witness_pair": row_witness_pair,
        "centered_distance_equality": {
            "center": row,
            "witness_pair": row_witness_pair,
            "left_pair": from_pair,
            "right_pair": to_pair,
        },
        "label4_spoke_swap": label4_spoke_swap,
        "touches_target_center": touches_target_center,
        "row6_connector_step": row6_connector_step,
        "obligation_role": _obligation_role(
            row,
            label4_spoke_swap,
            touches_target_center,
            row6_connector_step,
        ),
    }


def _obligation_role(
    row: int,
    label4_spoke_swap: bool,
    touches_target_center: bool,
    row6_connector_step: bool,
) -> str:
    if row6_connector_step:
        return "row6_target_connector_step"
    if row == 5 and label4_spoke_swap and touches_target_center:
        return "row5_label4_to_target_center_step"
    if row == 5 and label4_spoke_swap:
        return "row5_label4_spoke_swap"
    if row == 7 and label4_spoke_swap:
        return "row7_label4_spoke_swap"
    return "other_transfer_equality"


def _path_shape(transfer_path: Sequence[Mapping[str, Any]]) -> str:
    rows = [int(edge["row"]) for edge in transfer_path]
    if rows == [5, 6]:
        return "two_edge_row5_row6_connector_cascade"
    if rows == [5]:
        return "one_edge_row5_label4_spoke_swap"
    if rows == [7]:
        return "one_edge_row7_label4_spoke_swap"
    return "other_transfer_path_shape"


def _add_edge_bucket(
    buckets: dict[str, dict[str, Any]],
    obligation: Mapping[str, Any],
    record: Mapping[str, Any],
    multiplicity: int,
) -> None:
    key = str(obligation["obligation_key"])
    if key not in buckets:
        buckets[key] = {
            **{k: obligation[k] for k in obligation if k != "edge_index"},
            "signature_incidence_count": 0,
            "occurrence_incidence_count": 0,
            "transfer_record_indices": [],
            "signature_indices": [],
            "access_mode_counts": Counter(),
            "path_shape_counts": Counter(),
        }
    bucket = buckets[key]
    bucket["signature_incidence_count"] += 1
    bucket["occurrence_incidence_count"] += multiplicity
    bucket["transfer_record_indices"].append(record["transfer_record_index"])
    bucket["signature_indices"].append(record["signature_index"])
    bucket["access_mode_counts"][record["access_mode"]] += 1
    bucket["path_shape_counts"][_path_shape(record["transfer_path"])] += 1


def _add_path_bucket(
    buckets: dict[str, dict[str, Any]],
    motif_key: str,
    path_shape: str,
    path_keys: Sequence[str],
    record: Mapping[str, Any],
    multiplicity: int,
) -> None:
    if motif_key not in buckets:
        buckets[motif_key] = {
            "path_motif_key": motif_key,
            "path_shape": path_shape,
            "path_obligation_keys": list(path_keys),
            "transfer_edge_count": len(path_keys),
            "signature_incidence_count": 0,
            "occurrence_incidence_count": 0,
            "transfer_record_indices": [],
            "signature_indices": [],
            "access_mode_counts": Counter(),
        }
    bucket = buckets[motif_key]
    bucket["signature_incidence_count"] += 1
    bucket["occurrence_incidence_count"] += multiplicity
    bucket["transfer_record_indices"].append(record["transfer_record_index"])
    bucket["signature_indices"].append(record["signature_index"])
    bucket["access_mode_counts"][record["access_mode"]] += 1


def _finalize_edge_bucket(bucket: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(bucket)
    result["transfer_record_indices"] = sorted(result["transfer_record_indices"])
    result["signature_indices"] = sorted(result["signature_indices"])
    result["access_mode_counts"] = _json_counter(result["access_mode_counts"])
    result["path_shape_counts"] = _json_counter(result["path_shape_counts"])
    return result


def _finalize_path_bucket(bucket: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(bucket)
    result["transfer_record_indices"] = sorted(result["transfer_record_indices"])
    result["signature_indices"] = sorted(result["signature_indices"])
    result["access_mode_counts"] = _json_counter(result["access_mode_counts"])
    return result


def _obligation_key(row: int, from_pair: Sequence[int], to_pair: Sequence[int]) -> str:
    return (
        f"row{row}:"
        f"[{from_pair[0]},{from_pair[1]}]=[{to_pair[0]},{to_pair[1]}]"
    )


def _validate_source_transfer_paths(
    source_transfer_paths: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected = {
        "schema": SOURCE_TRANSFER_PATHS_SCHEMA,
        "status": SOURCE_TRANSFER_PATHS_STATUS,
        "trust": TRUST,
    }
    for key, expected_value in expected.items():
        if source_transfer_paths.get(key) != expected_value:
            errors.append(
                "source transfer paths "
                f"{key} mismatch: expected {expected_value!r}, "
                f"got {source_transfer_paths.get(key)!r}"
            )
    summary = _mapping(
        source_transfer_paths.get("summary"),
        "source transfer paths summary",
        errors,
    )
    expected_counts = {
        "label4_transfer_path_class_signature_incidence_count": 19,
        "signatures_with_positive_transfer_class": 8,
        "occurrences_with_positive_transfer_class": 9,
        "transfer_status": SOURCE_TRANSFER_STATUS,
    }
    for key, expected_value in expected_counts.items():
        if summary.get(key) != expected_value:
            errors.append(
                "source transfer paths "
                f"summary.{key} mismatch: expected {expected_value!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, got {summary.get(key)!r}"
            )


def _validate_transfer_obligation_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    expected_count = EXPECTED_SUMMARY["row_local_transfer_obligation_record_count"]
    if len(records) != expected_count:
        errors.append("transfer_obligation_records length mismatch")
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"transfer_obligation_records[{index}] must be an object")
            continue
        if not record.get("row_obligations"):
            errors.append(f"transfer_obligation_records[{index}] must be positive")
        path = record.get("row_obligations")
        if not isinstance(path, list):
            errors.append(f"transfer_obligation_records[{index}] path must be a list")
            continue
        if record.get("transfer_edge_count") != len(path):
            errors.append(
                f"transfer_obligation_records[{index}] transfer length mismatch"
            )
        expected_shape = _path_shape(path)
        if record.get("path_shape") != expected_shape:
            errors.append(f"transfer_obligation_records[{index}] path shape mismatch")
        for edge_index, obligation in enumerate(path):
            if not isinstance(obligation, Mapping):
                errors.append(
                    f"transfer_obligation_records[{index}] obligation must be object"
                )
                continue
            if obligation.get("edge_index") != edge_index:
                errors.append(
                    f"transfer_obligation_records[{index}] obligation index mismatch"
                )
            if obligation.get("row") not in {5, 6, 7}:
                errors.append(
                    f"transfer_obligation_records[{index}] unexpected obligation row"
                )


def _validate_unique_edge_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    expected_count = EXPECTED_SUMMARY["unique_edge_obligation_count"]
    if len(records) != expected_count:
        errors.append("unique_edge_obligation_records length mismatch")
    seen_keys: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"unique_edge_obligation_records[{index}] must be an object")
            continue
        key = record.get("obligation_key")
        if not isinstance(key, str) or not key:
            errors.append(f"unique_edge_obligation_records[{index}] key missing")
            continue
        if key in seen_keys:
            errors.append(f"unique_edge_obligation_records[{index}] duplicate key")
        seen_keys.add(key)
        if record.get("row6_connector_step") and record.get("row") != TARGET_CENTER:
            errors.append(
                f"unique_edge_obligation_records[{index}] invalid row6 connector step"
            )


def _validate_path_motif_records(
    records: Sequence[object],
    errors: list[str],
) -> None:
    expected_count = EXPECTED_SUMMARY["unique_path_motif_count"]
    if len(records) != expected_count:
        errors.append("path_motif_records length mismatch")
    seen_keys: set[str] = set()
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"path_motif_records[{index}] must be an object")
            continue
        key = record.get("path_motif_key")
        if not isinstance(key, str) or not key:
            errors.append(f"path_motif_records[{index}] key missing")
            continue
        if key in seen_keys:
            errors.append(f"path_motif_records[{index}] duplicate key")
        seen_keys.add(key)
        path_keys = record.get("path_obligation_keys")
        if not isinstance(path_keys, list):
            errors.append(f"path_motif_records[{index}] path keys must be a list")
        elif record.get("transfer_edge_count") != len(path_keys):
            errors.append(f"path_motif_records[{index}] path length mismatch")


def _source_summary(path: Path, role: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    summary = payload.get("summary")
    return {
        "path": display_path(path, ROOT),
        "role": role,
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "transfer_status": (
            summary.get("transfer_status") if isinstance(summary, Mapping) else None
        ),
    }


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _int_list(value: object) -> list[int]:
    if not isinstance(value, Sequence) or isinstance(value, str):
        raise AssertionError(f"{value!r} is not an integer sequence")
    return [int(item) for item in value]


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-transfer-paths",
        type=Path,
        default=DEFAULT_SOURCE_TRANSFER_PATHS,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_transfer_paths = _resolve(args.source_transfer_paths)

    generated = build_label4_transfer_obligations_payload(
        load_artifact(source_transfer_paths),
        source_transfer_paths_path=source_transfer_paths,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        source_transfer_paths_path=source_transfer_paths,
    )
    if args.assert_expected:
        assert_expected_label4_transfer_obligations(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 transfer obligations")
        print(f"target row: {summary['target_row_key']}")
        print(
            "positive transfer obligations: "
            f"{summary['row_local_transfer_obligation_record_count']}"
        )
        print(
            "unique edge obligations: "
            f"{summary['unique_edge_obligation_count']}"
        )
        print(f"unique path motifs: {summary['unique_path_motif_count']}")
        print(
            "row-6 connector steps: "
            f"{summary['row6_connector_step_signature_count']}"
        )
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
