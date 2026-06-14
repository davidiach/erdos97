#!/usr/bin/env python3
"""Check bounded support-cone probes for 151:6 target-sparse cases."""

from __future__ import annotations

import argparse
from collections import Counter
from itertools import combinations
import json
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.path_display import display_path  # noqa: E402
from erdos97.quotient_cone import (  # noqa: E402
    DistanceQuotient,
    KALMANSON_KINDS,
    Pair,
    StrictRow,
    altman_gap_row,
    kalmanson_row,
    pair,
)

from scripts.check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets import (  # noqa: E402
    ENDPOINT_CENTER,
    ENDPOINT_TRIPLE,
    EXACT_FOUR_ENDPOINT_ROWS,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_residual_target_rows import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    GATE_STATUS as SOURCE_RESIDUAL_GATE_STATUS,
    SCHEMA as SOURCE_RESIDUAL_SCHEMA,
    STATUS as SOURCE_RESIDUAL_STATUS,
    assert_expected_center8_residual_target_rows,
)
from scripts.check_bootstrap_t12_151_6_label4_center8_target_sparse_completions import (  # noqa: E402
    COMPLETION_STATUS as SOURCE_COMPLETION_STATUS,
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_COMPLETIONS,
    GATE_STATUS as SOURCE_COMPLETION_GATE_STATUS,
    SCHEMA as SOURCE_COMPLETION_SCHEMA,
    STATUS as SOURCE_COMPLETION_PACKET_STATUS,
    assert_expected_target_sparse_completions,
)
from scripts.check_bootstrap_t12_151_6_label4_support_hypothesis_ledger import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_SOURCE_SUPPORT_LEDGER,
    LEDGER_STATUS as SOURCE_LEDGER_STATUS,
    SCHEMA as SOURCE_LEDGER_SCHEMA,
    STATUS as SOURCE_LEDGER_PACKET_STATUS,
    assert_expected_support_hypothesis_ledger,
)
from scripts.check_bootstrap_t12_151_6_private_lane_core_catalog import (  # noqa: E402
    PRIVATE_SUPPORT_PAIR,
    PRIVATE_TARGET_CLASS,
    TARGET_CENTER,
    TARGET_ROW_KEY,
    TRUST,
)
from scripts.check_bootstrap_t12_151_6_private_lane_strict_core_split import (  # noqa: E402
    load_artifact,
)


SCHEMA = "erdos97.bootstrap_t12_151_6_label4_target_sparse_support_cone.v1"
STATUS = "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_SUPPORT_CONE_DIAGNOSTIC_ONLY"
GATE_STATUS = "NOT_READY_SUPPORT_CONE_PARTIAL_ENDPOINT_COVERAGE"
PROBE_STATUS = "TARGET_SPARSE_SUPPORT_CONE_BOUND_2_PARTIAL_ENDPOINT_ONLY"
STRICT_ROW_FAMILY = "kalmanson_all_quads_plus_altman_gaps_natural_order"
MAX_CERTIFICATE_ROW_COUNT = 2
CLAIM_SCOPE = (
    "Proof-mining support-cone diagnostic for the source-151 row-6 label-4 "
    "center-8 target-sparse residual cases. It converts the row-5 [4,6] and "
    "row-6 [0,5] cascade support hypotheses into exact selected-distance "
    "quotient equalities, probes the assignment-0 and assignment-11 "
    "target-pair rows and their one-row target completions with a bounded "
    "one- or two-row Kalmanson/Altman cone search, and then repeats the "
    "probe after adding each center-8 exact target row containing [0,4,6]. "
    "The local target-pair and completion probes have no bounded certificate; "
    "the endpoint-augmented probes have bounded certificates for 27 of 30 "
    "cases, leaving three assignment-0 endpoint rows uncovered. This does "
    "not prove assignments 0 and 11 are impossible, does not prove support "
    "existence, does not prove center migration, does not prove row forcing, "
    "does not prove endpoint-8 forcing, does not prove that pair [3,5] is "
    "impossible, does not prove n=9, does not prove the bootstrap bridge, is "
    "not a counterexample, and is not a global status update."
)
PROVENANCE = {
    "generator": (
        "scripts/"
        "check_bootstrap_t12_151_6_label4_target_sparse_support_cone.py"
    ),
    "command": (
        "python scripts/"
        "check_bootstrap_t12_151_6_label4_target_sparse_support_cone.py "
        "--write --assert-expected"
    ),
}

DEFAULT_ARTIFACT = (
    ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_6_label4_target_sparse_support_cone.json"
)

EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "completion_probe_records",
    "decision",
    "endpoint_augmented_probe_records",
    "interpretation",
    "provenance",
    "schema",
    "source_artifacts",
    "status",
    "summary",
    "support_hypothesis_records",
    "target_pair_probe_records",
    "trust",
    "validation_errors",
    "validation_status",
}
EXPECTED_SUMMARY = {
    "target_row_key": TARGET_ROW_KEY,
    "target_center": TARGET_CENTER,
    "private_target_center_class": PRIVATE_TARGET_CLASS,
    "private_support_pair": PRIVATE_SUPPORT_PAIR,
    "conditional_center8_target_center": ENDPOINT_CENTER,
    "conditional_center8_triple": ENDPOINT_TRIPLE,
    "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
    "source_residual_gate_status": SOURCE_RESIDUAL_GATE_STATUS,
    "source_completion_gate_status": SOURCE_COMPLETION_GATE_STATUS,
    "source_completion_status": SOURCE_COMPLETION_STATUS,
    "source_support_ledger_status": SOURCE_LEDGER_STATUS,
    "cascade_support_requirements": [
        {"center": 5, "witness_pair": [4, 6]},
        {"center": 6, "witness_pair": [0, 5]},
    ],
    "target_sparse_assignment_indices": [0, 11],
    "strict_row_family": STRICT_ROW_FAMILY,
    "strict_row_count": 255,
    "max_certificate_row_count": MAX_CERTIFICATE_ROW_COUNT,
    "target_pair_probe_count": 6,
    "target_pair_bounded_certificate_count": 0,
    "target_pair_probe_without_certificate_count": 6,
    "completion_probe_count": 12,
    "completion_bounded_certificate_count": 0,
    "completion_probe_without_certificate_count": 12,
    "endpoint_augmented_probe_count": 30,
    "endpoint_augmented_bounded_certificate_count": 27,
    "endpoint_augmented_probe_without_certificate_count": 3,
    "endpoint_augmented_assignment_certificate_counts": {"0": 2, "11": 25},
    "endpoint_augmented_assignment_miss_counts": {"0": 3},
    "endpoint_augmented_exact_row_certificate_counts": {
        "0,1,4,6": 5,
        "0,2,4,6": 5,
        "0,3,4,6": 6,
        "0,4,5,6": 6,
        "0,4,6,7": 5,
    },
    "endpoint_augmented_exact_row_miss_counts": {
        "0,1,4,6": 1,
        "0,2,4,6": 1,
        "0,4,6,7": 1,
    },
    "endpoint_augmented_uncovered_assignment_rows": [
        {
            "assignment_index": 0,
            "source_pair_row_index": 0,
            "row_center": 2,
            "row_witnesses": [0, 3, 4, 8],
            "uncovered_endpoint_rows": [
                [0, 1, 4, 6],
                [0, 2, 4, 6],
                [0, 4, 6, 7],
            ],
        }
    ],
    "all_target_pair_and_completion_probes_have_no_bounded_certificate": True,
    "all_assignment11_endpoint_augmented_probes_have_bounded_certificate": True,
    "assignment0_endpoint_augmented_probe_miss_count": 3,
    "current_evidence_forces_target_sparse_obstruction": False,
    "gate_status": GATE_STATUS,
    "probe_status": PROBE_STATUS,
}


class UnionFind:
    """Deterministic union-find over unordered pair variables."""

    def __init__(self, items: Iterable[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: Pair, right: Pair) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if root_right < root_left:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def build_target_sparse_support_cone_payload(
    residual_target_rows: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    *,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    source_completions_path: Path = DEFAULT_SOURCE_COMPLETIONS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> dict[str, Any]:
    """Return the deterministic target-sparse support-cone payload."""

    errors: list[str] = []
    assert_expected_center8_residual_target_rows(residual_target_rows)
    assert_expected_target_sparse_completions(source_completions)
    assert_expected_support_hypothesis_ledger(support_ledger)
    _validate_sources(residual_target_rows, source_completions, support_ledger, errors)
    support_requirements = _cascade_support_requirements(support_ledger)
    (
        summary,
        target_pair_records,
        completion_records,
        endpoint_records,
    ) = _probe_records(
        residual_target_rows,
        source_completions,
        support_requirements,
    )
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "summary": summary,
        "decision": {
            "decision_question": (
                "Do the pinned cascade support equalities already give a "
                "bounded one- or two-row Kalmanson/Altman cone certificate "
                "for the target-sparse local rows?"
            ),
            "answer": (
                "no_not_without_endpoint_target_rows_partial_with_endpoint_rows"
            ),
            "gate_status": GATE_STATUS,
            "probe_status": PROBE_STATUS,
            "current_evidence_forces_target_sparse_obstruction": False,
            "blocking_reason": (
                "The target-pair rows and their one-row target completions "
                "have no bounded certificate under the row-5 [4,6] and "
                "row-6 [0,5] cascade support equalities. Adding a center-8 "
                "exact target row gives bounded certificates for all "
                "assignment-11 endpoint augmentations and two assignment-0 "
                "endpoint augmentations, but misses three assignment-0 "
                "endpoint rows."
            ),
            "required_next_lemma": (
                "Either find a stronger exact cone/Farkas certificate for the "
                "three uncovered assignment-0 endpoint rows, prove a genuine "
                "center-8 target source excluding those rows, or add a "
                "different support-geometry lemma for assignments 0 and 11."
            ),
        },
        "support_hypothesis_records": support_requirements,
        "target_pair_probe_records": target_pair_records,
        "completion_probe_records": completion_records,
        "endpoint_augmented_probe_records": endpoint_records,
        "source_artifacts": [
            _source_summary(
                residual_target_rows_path,
                "source 151:6 center-8 residual target rows",
                residual_target_rows,
            ),
            _source_summary(
                source_completions_path,
                "source 151:6 target-sparse one-row completions",
                source_completions,
            ),
            _source_summary(
                support_ledger_path,
                "source 151:6 label-4 support hypothesis ledger",
                support_ledger,
            ),
        ],
        "interpretation": [
            (
                "The cascade support equalities alone do not give the current "
                "bounded cone checker a local target-sparse obstruction."
            ),
            (
                "The endpoint-augmented probe is sharply partial: assignment "
                "11 is covered, while assignment 0 misses exactly the "
                "center-8 rows [0,1,4,6], [0,2,4,6], and [0,4,6,7]."
            ),
            (
                "This packet is a bounded exact certificate search over a "
                "local quotient input, not a proof of support existence or "
                "a proof that the target-sparse assignments are impossible."
            ),
            (
                "The next experiment should attack the three uncovered "
                "assignment-0 endpoint rows with a higher-row Farkas cone, "
                "an endpoint-source lemma, or a geometric support condition."
            ),
        ],
        "validation_status": "passed" if not errors else "failed",
        "validation_errors": errors,
        "provenance": PROVENANCE,
    }
    assert_expected_target_sparse_support_cone(payload)
    return payload


def assert_expected_target_sparse_support_cone(payload: Mapping[str, Any]) -> None:
    """Assert the pinned target-sparse support-cone packet."""

    errors = validate_payload(payload, recompute=False)
    if errors:
        raise AssertionError("; ".join(errors))


def validate_payload(
    payload: Mapping[str, Any],
    *,
    recompute: bool = True,
    residual_target_rows_path: Path = DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    source_completions_path: Path = DEFAULT_SOURCE_COMPLETIONS,
    support_ledger_path: Path = DEFAULT_SOURCE_SUPPORT_LEDGER,
) -> list[str]:
    """Return validation errors for a target-sparse support-cone payload."""

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
            "assignments 0 and 11",
            "no bounded certificate",
            "27 of 30",
            "three assignment-0 endpoint rows uncovered",
            "does not prove assignments 0 and 11 are impossible",
            "does not prove support existence",
            "does not prove center migration",
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
    _validate_records(payload, errors)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list):
        errors.append("interpretation must be a list")
    elif not any("uncovered assignment-0 endpoint rows" in str(item) for item in interpretation):
        errors.append("interpretation must preserve the uncovered-row target")

    if recompute and not errors:
        generated = build_target_sparse_support_cone_payload(
            load_artifact(residual_target_rows_path),
            load_artifact(source_completions_path),
            load_artifact(support_ledger_path),
            residual_target_rows_path=residual_target_rows_path,
            source_completions_path=source_completions_path,
            support_ledger_path=support_ledger_path,
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
        "target_sparse_assignment_indices": summary.get(
            "target_sparse_assignment_indices"
        ),
        "target_pair_probe_count": summary.get("target_pair_probe_count"),
        "target_pair_bounded_certificate_count": summary.get(
            "target_pair_bounded_certificate_count"
        ),
        "completion_probe_count": summary.get("completion_probe_count"),
        "completion_bounded_certificate_count": summary.get(
            "completion_bounded_certificate_count"
        ),
        "endpoint_augmented_probe_count": summary.get(
            "endpoint_augmented_probe_count"
        ),
        "endpoint_augmented_bounded_certificate_count": summary.get(
            "endpoint_augmented_bounded_certificate_count"
        ),
        "endpoint_augmented_probe_without_certificate_count": summary.get(
            "endpoint_augmented_probe_without_certificate_count"
        ),
        "gate_status": summary.get("gate_status"),
        "probe_status": summary.get("probe_status"),
        "validation_errors": list(errors),
    }


def _probe_records(
    residual_target_rows: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    support_requirements: Sequence[Mapping[str, Any]],
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    support_classes = [
        (int(record["center"]), _int_list(record["witness_pair"]))
        for record in support_requirements
    ]
    sparse_records = _required_list(
        residual_target_rows.get("target_sparse_assignment_records"),
        "target-sparse assignment records",
    )
    completion_records = _required_list(
        source_completions.get("completion_records"),
        "source completion records",
    )

    target_pair_probe_records: list[dict[str, Any]] = []
    endpoint_augmented_probe_records: list[dict[str, Any]] = []
    for raw_sparse in sparse_records:
        sparse = _required_mapping(raw_sparse, "target-sparse record")
        assignment_index = int(sparse["assignment_index"])
        pair_rows = _required_list(sparse.get("target_pair_rows"), "target pair rows")
        for source_pair_row_index, raw_pair_row in enumerate(pair_rows):
            pair_row = _required_mapping(raw_pair_row, "target pair row")
            row_center = int(pair_row["row_center"])
            row_witnesses = _int_list(pair_row["row_witnesses"])
            probe = _cone_probe([(row_center, row_witnesses), *support_classes])
            target_pair_probe_records.append(
                {
                    "assignment_index": assignment_index,
                    "source_pair_row_index": source_pair_row_index,
                    "source_core_index": int(pair_row["core_index"]),
                    "row_center": row_center,
                    "row_witnesses": row_witnesses,
                    "source_target_overlap": _int_list(pair_row["target_overlap"]),
                    **probe,
                }
            )
            for endpoint_row in EXACT_FOUR_ENDPOINT_ROWS:
                endpoint_probe = _cone_probe(
                    [
                        (row_center, row_witnesses),
                        *support_classes,
                        (ENDPOINT_CENTER, endpoint_row),
                    ]
                )
                endpoint_augmented_probe_records.append(
                    {
                        "assignment_index": assignment_index,
                        "source_pair_row_index": source_pair_row_index,
                        "source_core_index": int(pair_row["core_index"]),
                        "row_center": row_center,
                        "row_witnesses": row_witnesses,
                        "source_target_overlap": _int_list(
                            pair_row["target_overlap"]
                        ),
                        "endpoint_center": ENDPOINT_CENTER,
                        "endpoint_row_witnesses": list(endpoint_row),
                        "endpoint_row_key": _row_key(endpoint_row),
                        **endpoint_probe,
                    }
                )

    completion_probe_records = []
    for source_completion_index, raw_completion in enumerate(completion_records):
        completion = _required_mapping(raw_completion, "source completion")
        row_center = int(completion["row_center"])
        row_witnesses = _int_list(completion["completion_row_witnesses"])
        probe = _cone_probe([(row_center, row_witnesses), *support_classes])
        completion_probe_records.append(
            {
                "source_completion_index": source_completion_index,
                "assignment_index": int(completion["assignment_index"]),
                "source_pair_row_index": int(completion["source_pair_row_index"]),
                "source_core_index": int(completion["source_core_index"]),
                "row_center": row_center,
                "completion_row_witnesses": row_witnesses,
                "completion_row_key": str(completion["completion_row_key"]),
                "completion_missing_target_label": int(
                    completion["missing_target_label"]
                ),
                "completion_replaced_label": int(completion["replaced_label"]),
                **probe,
            }
        )

    summary = _summary(
        target_pair_probe_records,
        completion_probe_records,
        endpoint_augmented_probe_records,
        residual_target_rows,
        source_completions,
        support_requirements,
    )
    return (
        summary,
        target_pair_probe_records,
        completion_probe_records,
        endpoint_augmented_probe_records,
    )


def _summary(
    target_pair_records: Sequence[Mapping[str, Any]],
    completion_records: Sequence[Mapping[str, Any]],
    endpoint_records: Sequence[Mapping[str, Any]],
    residual_target_rows: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    support_requirements: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    residual_summary = _required_mapping(
        residual_target_rows.get("summary"), "residual target-row summary"
    )
    completion_summary = _required_mapping(
        source_completions.get("summary"), "source completion summary"
    )
    endpoint_hits = [
        record for record in endpoint_records if record["bounded_certificate_found"]
    ]
    endpoint_misses = [
        record for record in endpoint_records if not record["bounded_certificate_found"]
    ]
    uncovered_by_assignment_row: dict[tuple[int, int], dict[str, Any]] = {}
    for record in endpoint_misses:
        key = (int(record["assignment_index"]), int(record["source_pair_row_index"]))
        bucket = uncovered_by_assignment_row.setdefault(
            key,
            {
                "assignment_index": int(record["assignment_index"]),
                "source_pair_row_index": int(record["source_pair_row_index"]),
                "row_center": int(record["row_center"]),
                "row_witnesses": _int_list(record["row_witnesses"]),
                "uncovered_endpoint_rows": [],
            },
        )
        bucket["uncovered_endpoint_rows"].append(
            _int_list(record["endpoint_row_witnesses"])
        )

    return {
        "target_row_key": TARGET_ROW_KEY,
        "target_center": TARGET_CENTER,
        "private_target_center_class": PRIVATE_TARGET_CLASS,
        "private_support_pair": PRIVATE_SUPPORT_PAIR,
        "conditional_center8_target_center": ENDPOINT_CENTER,
        "conditional_center8_triple": ENDPOINT_TRIPLE,
        "conditional_center8_exact_four_rows": EXACT_FOUR_ENDPOINT_ROWS,
        "source_residual_gate_status": residual_summary["gate_status"],
        "source_completion_gate_status": completion_summary["gate_status"],
        "source_completion_status": completion_summary["completion_status"],
        "source_support_ledger_status": SOURCE_LEDGER_STATUS,
        "cascade_support_requirements": [
            {
                "center": int(record["center"]),
                "witness_pair": _int_list(record["witness_pair"]),
            }
            for record in support_requirements
        ],
        "target_sparse_assignment_indices": residual_summary[
            "target_sparse_assignment_indices"
        ],
        "strict_row_family": STRICT_ROW_FAMILY,
        "strict_row_count": len(_strict_rows(_distance_quotient(9, []), list(range(9)))),
        "max_certificate_row_count": MAX_CERTIFICATE_ROW_COUNT,
        "target_pair_probe_count": len(target_pair_records),
        "target_pair_bounded_certificate_count": _certificate_count(
            target_pair_records
        ),
        "target_pair_probe_without_certificate_count": _miss_count(
            target_pair_records
        ),
        "completion_probe_count": len(completion_records),
        "completion_bounded_certificate_count": _certificate_count(
            completion_records
        ),
        "completion_probe_without_certificate_count": _miss_count(
            completion_records
        ),
        "endpoint_augmented_probe_count": len(endpoint_records),
        "endpoint_augmented_bounded_certificate_count": len(endpoint_hits),
        "endpoint_augmented_probe_without_certificate_count": len(endpoint_misses),
        "endpoint_augmented_assignment_certificate_counts": _json_counter(
            Counter(str(record["assignment_index"]) for record in endpoint_hits)
        ),
        "endpoint_augmented_assignment_miss_counts": _json_counter(
            Counter(str(record["assignment_index"]) for record in endpoint_misses)
        ),
        "endpoint_augmented_exact_row_certificate_counts": _json_counter(
            Counter(str(record["endpoint_row_key"]) for record in endpoint_hits)
        ),
        "endpoint_augmented_exact_row_miss_counts": _json_counter(
            Counter(str(record["endpoint_row_key"]) for record in endpoint_misses)
        ),
        "endpoint_augmented_uncovered_assignment_rows": [
            {
                **record,
                "uncovered_endpoint_rows": sorted(record["uncovered_endpoint_rows"]),
            }
            for _, record in sorted(uncovered_by_assignment_row.items())
        ],
        "all_target_pair_and_completion_probes_have_no_bounded_certificate": (
            _certificate_count(target_pair_records) == 0
            and _certificate_count(completion_records) == 0
        ),
        "all_assignment11_endpoint_augmented_probes_have_bounded_certificate": all(
            bool(record["bounded_certificate_found"])
            for record in endpoint_records
            if int(record["assignment_index"]) == 11
        ),
        "assignment0_endpoint_augmented_probe_miss_count": sum(
            1
            for record in endpoint_misses
            if int(record["assignment_index"]) == 0
        ),
        "current_evidence_forces_target_sparse_obstruction": False,
        "gate_status": GATE_STATUS,
        "probe_status": PROBE_STATUS,
    }


def _cone_probe(centered_classes: Sequence[tuple[int, Sequence[int]]]) -> dict[str, Any]:
    quotient = _distance_quotient(9, centered_classes)
    strict_rows = _strict_rows(quotient, list(range(9)))
    single_count, two_row_count, first_certificate = _bounded_certificates(strict_rows)
    return {
        "centered_class_count": len(centered_classes),
        "centered_classes": [
            {"center": int(center), "witnesses": _int_list(witnesses)}
            for center, witnesses in centered_classes
        ],
        "distance_class_count": quotient.class_count,
        "strict_row_count": len(strict_rows),
        "bounded_single_certificate_count": single_count,
        "bounded_two_row_certificate_count": two_row_count,
        "bounded_certificate_found": single_count > 0 or two_row_count > 0,
        "first_bounded_certificate": first_certificate,
    }


def _distance_quotient(
    n: int,
    centered_classes: Sequence[tuple[int, Sequence[int]]],
) -> DistanceQuotient:
    all_pairs = [pair(left, right) for left, right in combinations(range(n), 2)]
    uf = UnionFind(all_pairs)
    for center, witnesses in centered_classes:
        _validate_centered_class(n, center, witnesses)
        witness_list = [int(witness) for witness in witnesses]
        base = pair(int(center), witness_list[0])
        for witness in witness_list[1:]:
            uf.union(base, pair(int(center), witness))

    root_index: MutableMapping[Pair, int] = {}
    pair_class: dict[Pair, int] = {}
    members: dict[int, list[Pair]] = {}
    for item in all_pairs:
        root = uf.find(item)
        class_index = root_index.setdefault(root, len(root_index))
        pair_class[item] = class_index
        members.setdefault(class_index, []).append(item)
    return DistanceQuotient(
        n=n,
        pair_class=pair_class,
        class_members=tuple(tuple(members[idx]) for idx in range(len(members))),
    )


def _strict_rows(quotient: DistanceQuotient, order: Sequence[int]) -> list[StrictRow]:
    rows: list[StrictRow] = []
    for quad in combinations(order, 4):
        for kind in KALMANSON_KINDS:
            rows.append(kalmanson_row(quotient, kind, quad))
    for gap_order in range(1, quotient.n // 2):
        rows.append(altman_gap_row(quotient, order, gap_order))
    return rows


def _bounded_certificates(
    strict_rows: Sequence[StrictRow],
) -> tuple[int, int, dict[str, Any] | None]:
    single_count = 0
    two_row_count = 0
    first_certificate: dict[str, Any] | None = None
    for row in strict_rows:
        if not _nonpositive(row.vector):
            continue
        single_count += 1
        if first_certificate is None:
            first_certificate = _certificate_json([row])

    for left_index, left_row in enumerate(strict_rows):
        for right_row in strict_rows[left_index:]:
            if not _nonpositive(
                [
                    left_value + right_value
                    for left_value, right_value in zip(
                        left_row.vector, right_row.vector, strict=True
                    )
                ]
            ):
                continue
            two_row_count += 1
            if first_certificate is None:
                first_certificate = _certificate_json([left_row, right_row])
    return single_count, two_row_count, first_certificate


def _certificate_json(rows: Sequence[StrictRow]) -> dict[str, Any]:
    combined = [
        sum(row.vector[index] for row in rows) for index in range(len(rows[0].vector))
    ]
    return {
        "certificate_row_count": len(rows),
        "strict_rows": [_strict_row_json(row) for row in rows],
        "coefficient_positive_count": sum(1 for value in combined if value > 0),
        "coefficient_negative_count": sum(1 for value in combined if value < 0),
        "coefficient_zero_count": sum(1 for value in combined if value == 0),
        "combined_nonzero_coefficient_count": sum(
            1 for value in combined if value != 0
        ),
        "nonpositive_sum_verified": _nonpositive(combined),
        "claim_strength": (
            "Bounded exact local cone certificate for this encoded quotient "
            "input and fixed cyclic order only."
        ),
    }


def _strict_row_json(row: StrictRow) -> dict[str, Any]:
    item: dict[str, Any] = {"source": row.source, "weight": 1}
    if row.source == "kalmanson":
        item["kind"] = str(row.metadata["kind"])
        item["quad"] = _int_list(row.metadata["quad"])
    elif row.source == "altman_gap":
        item["gap_order"] = int(row.metadata["gap_order"])
    else:  # pragma: no cover - defensive against future strict-row sources.
        item["metadata"] = dict(row.metadata)
    return item


def _cascade_support_requirements(
    support_ledger: Mapping[str, Any],
) -> list[dict[str, Any]]:
    records = _required_list(
        support_ledger.get("support_requirement_records"),
        "support requirement records",
    )
    cascade_requirements = []
    for raw_record in records:
        record = _required_mapping(raw_record, "support requirement")
        component_keys = {
            str(component_key) for component_key in record.get("component_keys", [])
        }
        if "D[0,6]=D[4,5]=D[5,6]" not in component_keys:
            continue
        cascade_requirements.append(
            {
                "requirement_key": str(record["requirement_key"]),
                "center": int(record["center"]),
                "witness_pair": _int_list(record["witness_pair"]),
                "obligation_role": str(record["obligation_role"]),
                "support_hypothesis": str(record["support_hypothesis"]),
            }
        )
    cascade_requirements.sort(
        key=lambda item: (int(item["center"]), item["witness_pair"])
    )
    if [
        {"center": item["center"], "witness_pair": item["witness_pair"]}
        for item in cascade_requirements
    ] != EXPECTED_SUMMARY["cascade_support_requirements"]:
        raise AssertionError("cascade support requirements changed")
    return cascade_requirements


def _validate_sources(
    residual_target_rows: Mapping[str, Any],
    source_completions: Mapping[str, Any],
    support_ledger: Mapping[str, Any],
    errors: list[str],
) -> None:
    expected_sources = [
        (
            "residual target rows",
            residual_target_rows,
            SOURCE_RESIDUAL_SCHEMA,
            SOURCE_RESIDUAL_STATUS,
        ),
        (
            "target-sparse completions",
            source_completions,
            SOURCE_COMPLETION_SCHEMA,
            SOURCE_COMPLETION_PACKET_STATUS,
        ),
        (
            "support ledger",
            support_ledger,
            SOURCE_LEDGER_SCHEMA,
            SOURCE_LEDGER_PACKET_STATUS,
        ),
    ]
    for label, payload, schema, status in expected_sources:
        if payload.get("schema") != schema:
            errors.append(f"{label} schema mismatch")
        if payload.get("status") != status:
            errors.append(f"{label} status mismatch")
        if payload.get("trust") != TRUST:
            errors.append(f"{label} trust mismatch")

    residual_summary = _mapping(
        residual_target_rows.get("summary"), "residual target-row summary", errors
    )
    if residual_summary.get("gate_status") != SOURCE_RESIDUAL_GATE_STATUS:
        errors.append("residual target-row gate status mismatch")
    completion_summary = _mapping(
        source_completions.get("summary"), "source completion summary", errors
    )
    if completion_summary.get("gate_status") != SOURCE_COMPLETION_GATE_STATUS:
        errors.append("source completion gate status mismatch")
    ledger_summary = _mapping(
        support_ledger.get("summary"), "support ledger summary", errors
    )
    if ledger_summary.get("ledger_status") != SOURCE_LEDGER_STATUS:
        errors.append("support ledger status mismatch")


def _validate_summary(summary: Mapping[str, Any], errors: list[str]) -> None:
    for key, expected in EXPECTED_SUMMARY.items():
        if summary.get(key) != expected:
            errors.append(
                f"summary.{key} mismatch: expected {expected!r}, "
                f"got {summary.get(key)!r}"
            )


def _validate_decision(decision: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "answer": "no_not_without_endpoint_target_rows_partial_with_endpoint_rows",
        "gate_status": GATE_STATUS,
        "probe_status": PROBE_STATUS,
        "current_evidence_forces_target_sparse_obstruction": False,
    }
    for key, expected_value in expected.items():
        if decision.get(key) != expected_value:
            errors.append(
                f"decision.{key} mismatch: expected {expected_value!r}, "
                f"got {decision.get(key)!r}"
            )
    required_next = decision.get("required_next_lemma")
    if not isinstance(required_next, str) or "three uncovered assignment-0" not in required_next:
        errors.append("decision.required_next_lemma must name the three misses")


def _validate_records(payload: Mapping[str, Any], errors: list[str]) -> None:
    support_records = payload.get("support_hypothesis_records")
    if not isinstance(support_records, list):
        errors.append("support_hypothesis_records must be a list")
    elif [
        {"center": record.get("center"), "witness_pair": record.get("witness_pair")}
        for record in support_records
        if isinstance(record, Mapping)
    ] != EXPECTED_SUMMARY["cascade_support_requirements"]:
        errors.append("support_hypothesis_records cascade pair mismatch")

    target_records = payload.get("target_pair_probe_records")
    if not isinstance(target_records, list):
        errors.append("target_pair_probe_records must be a list")
    else:
        _validate_probe_records(
            target_records,
            EXPECTED_SUMMARY["target_pair_probe_count"],
            False,
            "target_pair_probe_records",
            errors,
        )

    completion_records = payload.get("completion_probe_records")
    if not isinstance(completion_records, list):
        errors.append("completion_probe_records must be a list")
    else:
        _validate_probe_records(
            completion_records,
            EXPECTED_SUMMARY["completion_probe_count"],
            False,
            "completion_probe_records",
            errors,
        )

    endpoint_records = payload.get("endpoint_augmented_probe_records")
    if not isinstance(endpoint_records, list):
        errors.append("endpoint_augmented_probe_records must be a list")
    else:
        if len(endpoint_records) != EXPECTED_SUMMARY["endpoint_augmented_probe_count"]:
            errors.append("endpoint_augmented_probe_records length mismatch")
        hits = [
            record
            for record in endpoint_records
            if isinstance(record, Mapping)
            and bool(record.get("bounded_certificate_found"))
        ]
        misses = [
            record
            for record in endpoint_records
            if isinstance(record, Mapping)
            and not bool(record.get("bounded_certificate_found"))
        ]
        if len(hits) != EXPECTED_SUMMARY["endpoint_augmented_bounded_certificate_count"]:
            errors.append("endpoint_augmented_probe_records hit count mismatch")
        if len(misses) != EXPECTED_SUMMARY[
            "endpoint_augmented_probe_without_certificate_count"
        ]:
            errors.append("endpoint_augmented_probe_records miss count mismatch")
        for record in hits:
            if not isinstance(record.get("first_bounded_certificate"), Mapping):
                errors.append("endpoint hit must include first_bounded_certificate")
        for record in misses:
            if record.get("assignment_index") != 0:
                errors.append("endpoint miss must belong to assignment 0")


def _validate_probe_records(
    records: Sequence[object],
    expected_count: int,
    expected_certificate_found: bool,
    label: str,
    errors: list[str],
) -> None:
    if len(records) != expected_count:
        errors.append(f"{label} length mismatch")
        return
    for index, record in enumerate(records):
        if not isinstance(record, Mapping):
            errors.append(f"{label}[{index}] must be an object")
            continue
        if bool(record.get("bounded_certificate_found")) != expected_certificate_found:
            errors.append(f"{label}[{index}] certificate flag mismatch")
        if record.get("strict_row_count") != EXPECTED_SUMMARY["strict_row_count"]:
            errors.append(f"{label}[{index}] strict row count mismatch")
        if record.get("first_bounded_certificate") is not None:
            errors.append(f"{label}[{index}] must not include a certificate")


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
        "completion_status": summary.get("completion_status"),
        "ledger_status": summary.get("ledger_status"),
    }


def _certificate_count(records: Sequence[Mapping[str, Any]]) -> int:
    return sum(1 for record in records if record["bounded_certificate_found"])


def _miss_count(records: Sequence[Mapping[str, Any]]) -> int:
    return sum(1 for record in records if not record["bounded_certificate_found"])


def _validate_centered_class(
    n: int,
    center: int,
    witnesses: Sequence[int],
) -> None:
    if int(center) < 0 or int(center) >= n:
        raise ValueError(f"center out of range: {center}")
    witness_list = [int(witness) for witness in witnesses]
    if len(witness_list) < 2:
        raise ValueError("centered class must contain at least two witnesses")
    if len(set(witness_list)) != len(witness_list):
        raise ValueError(f"repeated witness in centered class: {witnesses!r}")
    if int(center) in witness_list:
        raise ValueError(f"centered class includes its center: {center}")
    bad = [witness for witness in witness_list if witness < 0 or witness >= n]
    if bad:
        raise ValueError(f"witness out of range: {bad[0]}")


def _nonpositive(values: Sequence[int]) -> bool:
    return all(value <= 0 for value in values)


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _int_list(values: object) -> list[int]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise AssertionError("expected a sequence of integers")
    return [int(value) for value in values]


def _mapping(value: object, name: str, errors: list[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        errors.append(f"{name} must be an object")
        return {}
    return value


def _required_mapping(value: object, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"{name} must be an object")
    return value


def _required_list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise AssertionError(f"{name} must be a list")
    return value


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument(
        "--source-residual-target-rows",
        type=Path,
        default=DEFAULT_SOURCE_RESIDUAL_TARGET_ROWS,
    )
    parser.add_argument(
        "--source-completions",
        type=Path,
        default=DEFAULT_SOURCE_COMPLETIONS,
    )
    parser.add_argument(
        "--source-support-ledger",
        type=Path,
        default=DEFAULT_SOURCE_SUPPORT_LEDGER,
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    artifact = _resolve(args.artifact)
    source_residual_target_rows = _resolve(args.source_residual_target_rows)
    source_completions = _resolve(args.source_completions)
    source_support_ledger = _resolve(args.source_support_ledger)
    generated = build_target_sparse_support_cone_payload(
        load_artifact(source_residual_target_rows),
        load_artifact(source_completions),
        load_artifact(source_support_ledger),
        residual_target_rows_path=source_residual_target_rows,
        source_completions_path=source_completions,
        support_ledger_path=source_support_ledger,
    )
    payload = generated

    if args.check:
        stored = load_artifact(artifact)
        if stored != generated:
            raise AssertionError(f"{display_path(artifact, ROOT)} is stale")
        payload = stored

    errors = validate_payload(
        payload,
        residual_target_rows_path=source_residual_target_rows,
        source_completions_path=source_completions,
        support_ledger_path=source_support_ledger,
    )
    if args.assert_expected:
        assert_expected_target_sparse_support_cone(payload)
    if args.write:
        write_json(generated, artifact)

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 label-4 target-sparse support cone")
        print(f"target row: {summary['target_row_key']}")
        print(
            "target-sparse assignments: "
            f"{summary['target_sparse_assignment_indices']}"
        )
        print(f"target-pair probes: {summary['target_pair_probe_count']}")
        print(f"completion probes: {summary['completion_probe_count']}")
        print(
            "endpoint-augmented certificates: "
            f"{summary['endpoint_augmented_bounded_certificate_count']} / "
            f"{summary['endpoint_augmented_probe_count']}"
        )
        print(f"gate status: {summary['gate_status']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: target-sparse support-cone diagnostic verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
