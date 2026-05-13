"""Singleton-support audit for the bootstrap/T12 source-151 targets.

Rows 151:5 and 151:8 are the source-151 one-outside-label targets.  This audit
asks whether either target can use a singleton-support activation row different
from its fixed source-151 row while the surrounding source-151 selected rows
are preserved, or while one additional row is allowed to move.

The answer is no under the basic selected-row incidence and crossing filters.
This is not a Euclidean realizability theorem and not a proof of row forcing.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_3_escape_candidates import (
    CYCLIC_ORDER,
    _crossing_violations,
    _row_pair_cap_violations,
    _witness_pair_cap_violations,
)
from erdos97.bootstrap_t12_one_outside import (
    DEFAULT_ARTIFACT as ONE_OUTSIDE_ARTIFACT,
    SCHEMA as ONE_OUTSIDE_SCHEMA,
    STATUS as ONE_OUTSIDE_STATUS,
    build_t12_one_outside_payload,
)
from erdos97.bootstrap_vertex_circle_overlay import (
    SCHEMA as OVERLAY_SCHEMA,
    STATUS as OVERLAY_STATUS,
    build_overlay_payload,
)


SCHEMA = "erdos97.bootstrap_t12_151_singleton_support_audit.v1"
STATUS = "BOOTSTRAP_T12_151_SINGLETON_SUPPORT_AUDIT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_SOURCE151_SINGLETON_ROWS_SURVIVE_SUPPORT_AUDITS"
CLAIM_SCOPE = (
    "Fixed selected-row-neighborhood singleton-support audit for source 151 "
    "rows 5 and 8. It enumerates activation rows containing each target's "
    "bootstrap-core witnesses plus one singleton support label, then checks "
    "the fixed source-151 neighborhood and a one-row-drop relaxation by "
    "row-pair, witness-pair, and crossing filters. The only survivors keep the "
    "original target row and, in the one-row-drop scans, also keep the dropped "
    "row equal to its original source-151 row. This does not prove singleton "
    "support existence, row forcing, does not prove n=9, does not prove the "
    "bridge, and is not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_singleton_support_audit.json"
)

SOURCE_RECORD_ID = 151
TARGET_SPECS: dict[int, dict[str, object]] = {
    5: {
        "target_row_key": "151:5",
        "bootstrap_core_witnesses": [2, 4],
        "singleton_support_labels": [7, 8],
        "original_row": [2, 4, 7, 8],
        "fixed_counts": {
            "row_pair+witness_pair+crossing": 6,
            "survive": 1,
            "witness_pair+crossing": 2,
        },
        "one_row_drop_counts": {
            "crossing": 47,
            "row_pair+crossing": 11,
            "row_pair+witness_pair": 36,
            "row_pair+witness_pair+crossing": 4692,
            "survive": 8,
            "witness_pair+crossing": 246,
        },
    },
    8: {
        "target_row_key": "151:8",
        "bootstrap_core_witnesses": [1, 2],
        "singleton_support_labels": [5, 7],
        "original_row": [1, 2, 5, 7],
        "fixed_counts": {
            "crossing": 2,
            "row_pair+witness_pair+crossing": 6,
            "survive": 1,
        },
        "one_row_drop_counts": {
            "crossing": 105,
            "row_pair+crossing": 11,
            "row_pair+witness_pair": 32,
            "row_pair+witness_pair+crossing": 4704,
            "survive": 8,
            "witness_pair+crossing": 180,
        },
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _source_151_rows() -> list[list[int]]:
    overlay = build_overlay_payload()
    records = overlay.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("overlay records must be a sequence")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("overlay records must be mappings")
        if int(record["source_record_id"]) == SOURCE_RECORD_ID:
            return [_int_list(row) for row in record["selected_rows"]]
    raise AssertionError("could not find source 151 in overlay packet")


def _target_one_outside_records() -> dict[int, dict[str, object]]:
    one_outside = build_t12_one_outside_payload()
    records = one_outside.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("one-outside packet records must be a sequence")
    target_records: dict[int, dict[str, object]] = {}
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("one-outside records must be mappings")
        if int(record["source_record_id"]) != SOURCE_RECORD_ID:
            continue
        row_center = int(record["row_center"])
        if row_center not in TARGET_SPECS:
            continue
        support_labels = [
            int(option["support_label"]) for option in record["support_options"]
        ]
        target_records[row_center] = {
            "source_record_id": int(record["source_record_id"]),
            "row_center": row_center,
            "witnesses": _int_list(record["witnesses"]),
            "bootstrap_core_witnesses": _int_list(
                record["bootstrap_core_witnesses"]
            ),
            "outside_witnesses": _int_list(record["outside_witnesses"]),
            "support_labels": sorted(support_labels),
            "support_label_modes": record["support_label_modes"],
            "pressure_class": str(record["pressure_class"]),
            "row_center_private_in_all_deletion_closures": bool(
                record["row_center_private_in_all_deletion_closures"]
            ),
        }
    missing = sorted(set(TARGET_SPECS) - set(target_records))
    if missing:
        raise AssertionError(f"missing source-151 one-outside rows: {missing}")
    return target_records


def _target_row_key(center: int) -> str:
    return str(TARGET_SPECS[center]["target_row_key"])


def _bootstrap_core_witnesses(center: int) -> list[int]:
    return _int_list(TARGET_SPECS[center]["bootstrap_core_witnesses"])


def _singleton_support_labels(center: int) -> list[int]:
    return _int_list(TARGET_SPECS[center]["singleton_support_labels"])


def _original_row(center: int) -> list[int]:
    return _int_list(TARGET_SPECS[center]["original_row"])


def _target_row_candidates(center: int) -> list[list[int]]:
    candidates: set[tuple[int, ...]] = set()
    core = set(_bootstrap_core_witnesses(center))
    for support_label in _singleton_support_labels(center):
        required = core | {support_label}
        for fourth in CYCLIC_ORDER:
            if fourth != center and fourth not in required:
                candidates.add(tuple(sorted(required | {fourth})))
    return [list(candidate) for candidate in sorted(candidates)]


def _all_replacement_rows(center: int) -> list[list[int]]:
    labels = [label for label in CYCLIC_ORDER if label != center]
    return [list(row) for row in combinations(labels, 4)]


def _rejection_data(rows: Sequence[Sequence[int]]) -> dict[str, object]:
    row_pair_violations = _row_pair_cap_violations(rows)
    witness_pair_violations = _witness_pair_cap_violations(rows)
    crossing_violations = _crossing_violations(rows)
    reasons = []
    if row_pair_violations:
        reasons.append("row_pair")
    if witness_pair_violations:
        reasons.append("witness_pair")
    if crossing_violations:
        reasons.append("crossing")
    return {
        "row_pair_cap_violations": row_pair_violations,
        "witness_pair_cap_violations": witness_pair_violations,
        "crossing_violations": crossing_violations,
        "rejection_reasons": reasons,
        "rejection_category": "+".join(reasons) if reasons else "survive",
        "passes_basic_incidence_crossing_filters": not reasons,
    }


def _fixed_candidate_records(
    base_rows: Sequence[Sequence[int]],
    center: int,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for candidate in _target_row_candidates(center):
        rows = [list(row) for row in base_rows]
        rows[center] = list(candidate)
        rejection = _rejection_data(rows)
        records.append(
            {
                "target_row_key": _target_row_key(center),
                "target_center": center,
                "target_center_class": candidate,
                "is_original_row": candidate == _original_row(center),
                **rejection,
            }
        )
    return records


def _scan_one_row_drop(
    base_rows: Sequence[Sequence[int]],
    center: int,
) -> dict[str, object]:
    total_counts: Counter[str] = Counter()
    per_dropped_counts: dict[int, Counter[str]] = {
        dropped: Counter() for dropped in CYCLIC_ORDER if dropped != center
    }
    survivors: list[dict[str, object]] = []

    for target_row in _target_row_candidates(center):
        for dropped_center in [label for label in CYCLIC_ORDER if label != center]:
            for replacement_row in _all_replacement_rows(dropped_center):
                rows = [list(row) for row in base_rows]
                rows[center] = list(target_row)
                rows[dropped_center] = list(replacement_row)
                category = str(_rejection_data(rows)["rejection_category"])
                total_counts[category] += 1
                per_dropped_counts[dropped_center][category] += 1
                if category == "survive":
                    survivors.append(
                        {
                            "target_row_key": _target_row_key(center),
                            "target_center_class": list(target_row),
                            "target_center_class_is_original": (
                                target_row == _original_row(center)
                            ),
                            "dropped_center": dropped_center,
                            "dropped_center_class": list(replacement_row),
                            "dropped_center_class_is_original": (
                                replacement_row == list(base_rows[dropped_center])
                            ),
                        }
                    )

    return {
        "candidate_count": sum(total_counts.values()),
        "rejection_category_counts": _json_counter(total_counts),
        "per_dropped_center": [
            {
                "dropped_center": dropped_center,
                "source_row": list(base_rows[dropped_center]),
                "replacement_row_count": len(_all_replacement_rows(dropped_center)),
                "candidate_count": sum(per_dropped_counts[dropped_center].values()),
                "surviving_candidate_count": per_dropped_counts[dropped_center].get(
                    "survive", 0
                ),
                "rejection_category_counts": _json_counter(
                    per_dropped_counts[dropped_center]
                ),
            }
            for dropped_center in CYCLIC_ORDER
            if dropped_center != center
        ],
        "survivors": survivors,
    }


def _target_audit_record(
    base_rows: Sequence[Sequence[int]],
    one_outside_record: Mapping[str, object],
    center: int,
) -> dict[str, object]:
    fixed_records = _fixed_candidate_records(base_rows, center)
    fixed_counts = Counter(str(record["rejection_category"]) for record in fixed_records)
    fixed_survivors = [
        record
        for record in fixed_records
        if record["passes_basic_incidence_crossing_filters"]
    ]
    one_row_drop = _scan_one_row_drop(base_rows, center)
    one_row_drop_survivors = one_row_drop["survivors"]
    if not isinstance(one_row_drop_survivors, Sequence):
        raise AssertionError("one-row-drop survivors must be a sequence")
    non_original_one_drop_survivors = [
        survivor
        for survivor in one_row_drop_survivors
        if not survivor["target_center_class_is_original"]
    ]

    return {
        "target_row_key": _target_row_key(center),
        "target_center": center,
        "bootstrap_core_witnesses": _bootstrap_core_witnesses(center),
        "singleton_support_labels": _singleton_support_labels(center),
        "original_target_center_class": _original_row(center),
        "target_center_candidate_classes": _target_row_candidates(center),
        "target_center_candidate_count": len(_target_row_candidates(center)),
        "fixed_neighborhood_candidate_count": len(fixed_records),
        "fixed_neighborhood_surviving_candidate_count": len(fixed_survivors),
        "fixed_neighborhood_non_original_survivor_count": sum(
            1 for survivor in fixed_survivors if not survivor["is_original_row"]
        ),
        "fixed_neighborhood_rejection_category_counts": _json_counter(fixed_counts),
        "one_row_drop_centers": [
            dropped_center for dropped_center in CYCLIC_ORDER if dropped_center != center
        ],
        "one_row_drop_replacement_count_per_center": 70,
        "one_row_drop_candidate_count": one_row_drop["candidate_count"],
        "one_row_drop_surviving_candidate_count": len(one_row_drop_survivors),
        "one_row_drop_non_original_target_row_survivor_count": len(
            non_original_one_drop_survivors
        ),
        "one_row_drop_survivors_all_original_rows": all(
            survivor["target_center_class_is_original"]
            and survivor["dropped_center_class_is_original"]
            for survivor in one_row_drop_survivors
        ),
        "one_row_drop_rejection_category_counts": one_row_drop[
            "rejection_category_counts"
        ],
        "source_one_outside_record": dict(one_outside_record),
        "fixed_neighborhood_candidates": fixed_records,
        "one_row_drop": one_row_drop,
    }


def build_t12_151_singleton_support_audit_payload() -> dict[str, object]:
    """Return the deterministic source-151 singleton-support audit."""

    base_rows = _source_151_rows()
    target_records = _target_one_outside_records()
    audit_records = []
    for center in sorted(TARGET_SPECS):
        one_outside_record = target_records[center]
        if (
            one_outside_record["bootstrap_core_witnesses"]
            != _bootstrap_core_witnesses(center)
        ):
            raise AssertionError(f"source one-outside core drifted for {center}")
        if one_outside_record["support_labels"] != _singleton_support_labels(center):
            raise AssertionError(f"source one-outside supports drifted for {center}")
        if base_rows[center] != _original_row(center):
            raise AssertionError(f"source-151 row {center} drifted")
        audit_records.append(_target_audit_record(base_rows, one_outside_record, center))

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit preserves the source-151 selected-row neighborhood, or drops exactly one non-target row in each relaxation.",
            "A row containing bootstrap-core witnesses plus a singleton support is activation bookkeeping, not a proof that a genuine rich class exists.",
            "The audit uses incidence and crossing filters only, not Euclidean realizability.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": CYCLIC_ORDER,
            "target_row_keys": [_target_row_key(center) for center in sorted(TARGET_SPECS)],
            "target_centers": sorted(TARGET_SPECS),
            "target_count": len(audit_records),
            "target_center_candidate_count_by_key": {
                record["target_row_key"]: record["target_center_candidate_count"]
                for record in audit_records
            },
            "fixed_neighborhood_candidate_count": sum(
                int(record["fixed_neighborhood_candidate_count"])
                for record in audit_records
            ),
            "fixed_neighborhood_surviving_candidate_count": sum(
                int(record["fixed_neighborhood_surviving_candidate_count"])
                for record in audit_records
            ),
            "fixed_neighborhood_non_original_survivor_count": sum(
                int(record["fixed_neighborhood_non_original_survivor_count"])
                for record in audit_records
            ),
            "one_row_drop_candidate_count": sum(
                int(record["one_row_drop_candidate_count"]) for record in audit_records
            ),
            "one_row_drop_surviving_candidate_count": sum(
                int(record["one_row_drop_surviving_candidate_count"])
                for record in audit_records
            ),
            "one_row_drop_non_original_target_row_survivor_count": sum(
                int(record["one_row_drop_non_original_target_row_survivor_count"])
                for record in audit_records
            ),
            "one_row_drop_survivors_all_original_rows": all(
                bool(record["one_row_drop_survivors_all_original_rows"])
                for record in audit_records
            ),
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the rows are forced by minimal or rich-class geometry, "
                "does not allow two or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): base_rows[center] for center in CYCLIC_ORDER},
        "target_audits": audit_records,
        "source_one_outside_packet": {
            "path": ONE_OUTSIDE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_OUTSIDE_SCHEMA,
            "status": ONE_OUTSIDE_STATUS,
        },
        "source_overlay_packet": {
            "path": "data/certificates/bootstrap_vertex_circle_overlay.json",
            "schema": OVERLAY_SCHEMA,
            "status": OVERLAY_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_151_singleton_support_audit.py",
            "command": (
                "python scripts/check_bootstrap_t12_151_singleton_support_audit.py "
                "--write --assert-expected"
            ),
        },
    }
    assert_expected_payload(payload)
    return payload


def load_artifact(path: Path = DEFAULT_ARTIFACT) -> dict[str, Any]:
    return _load_json(path)


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
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
        "source_record_ids": [SOURCE_RECORD_ID],
        "cyclic_order": CYCLIC_ORDER,
        "target_row_keys": ["151:5", "151:8"],
        "target_centers": [5, 8],
        "target_count": 2,
        "target_center_candidate_count_by_key": {"151:5": 9, "151:8": 9},
        "fixed_neighborhood_candidate_count": 18,
        "fixed_neighborhood_surviving_candidate_count": 2,
        "fixed_neighborhood_non_original_survivor_count": 0,
        "one_row_drop_candidate_count": 10080,
        "one_row_drop_surviving_candidate_count": 16,
        "one_row_drop_non_original_target_row_survivor_count": 0,
        "one_row_drop_survivors_all_original_rows": True,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    records = payload.get("target_audits")
    if not isinstance(records, Sequence) or len(records) != 2:
        raise AssertionError("expected two source-151 singleton target audits")
    by_key = {
        str(record["target_row_key"]): record
        for record in records
        if isinstance(record, Mapping)
    }
    if sorted(by_key) != ["151:5", "151:8"]:
        raise AssertionError("unexpected source-151 singleton audit keys")

    for center in sorted(TARGET_SPECS):
        key = _target_row_key(center)
        record = by_key[key]
        spec = TARGET_SPECS[center]
        if record.get("bootstrap_core_witnesses") != spec["bootstrap_core_witnesses"]:
            raise AssertionError(f"{key} bootstrap core drifted")
        if record.get("singleton_support_labels") != spec["singleton_support_labels"]:
            raise AssertionError(f"{key} support labels drifted")
        if record.get("original_target_center_class") != spec["original_row"]:
            raise AssertionError(f"{key} original row drifted")
        if record.get("target_center_candidate_count") != 9:
            raise AssertionError(f"{key} candidate count drifted")
        if record.get("fixed_neighborhood_candidate_count") != 9:
            raise AssertionError(f"{key} fixed candidate count drifted")
        if record.get("fixed_neighborhood_surviving_candidate_count") != 1:
            raise AssertionError(f"{key} fixed survivor count drifted")
        if record.get("fixed_neighborhood_non_original_survivor_count") != 0:
            raise AssertionError(f"{key} fixed non-original survivor drifted")
        if record.get("fixed_neighborhood_rejection_category_counts") != spec[
            "fixed_counts"
        ]:
            raise AssertionError(f"{key} fixed rejection counts drifted")
        if record.get("one_row_drop_candidate_count") != 5040:
            raise AssertionError(f"{key} one-row-drop candidate count drifted")
        if record.get("one_row_drop_surviving_candidate_count") != 8:
            raise AssertionError(f"{key} one-row-drop survivor count drifted")
        if record.get("one_row_drop_non_original_target_row_survivor_count") != 0:
            raise AssertionError(f"{key} one-row-drop non-original drifted")
        if record.get("one_row_drop_survivors_all_original_rows") is not True:
            raise AssertionError(f"{key} one-row-drop survivors drifted")
        if record.get("one_row_drop_rejection_category_counts") != spec[
            "one_row_drop_counts"
        ]:
            raise AssertionError(f"{key} one-row-drop counts drifted")

        fixed_candidates = record.get("fixed_neighborhood_candidates")
        if not isinstance(fixed_candidates, Sequence) or len(fixed_candidates) != 9:
            raise AssertionError(f"{key} fixed-neighborhood candidates malformed")
        fixed_survivors = [
            candidate
            for candidate in fixed_candidates
            if isinstance(candidate, Mapping)
            and candidate.get("passes_basic_incidence_crossing_filters")
        ]
        if len(fixed_survivors) != 1:
            raise AssertionError(f"{key} fixed survivor list drifted")
        if fixed_survivors[0].get("target_center_class") != spec["original_row"]:
            raise AssertionError(f"{key} fixed survivor should be original")

        one_row_drop = record.get("one_row_drop")
        if not isinstance(one_row_drop, Mapping):
            raise AssertionError(f"{key} one_row_drop must be a mapping")
        survivors = one_row_drop.get("survivors")
        if not isinstance(survivors, Sequence) or len(survivors) != 8:
            raise AssertionError(f"{key} should have eight one-row-drop survivors")
        if any(
            not isinstance(survivor, Mapping)
            or not survivor.get("target_center_class_is_original")
            or not survivor.get("dropped_center_class_is_original")
            for survivor in survivors
        ):
            raise AssertionError(f"{key} one-row-drop survivors should be original")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_151_singleton_support_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
