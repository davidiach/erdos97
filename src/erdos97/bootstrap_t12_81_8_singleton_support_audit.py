"""Singleton-support audit for the bootstrap/T12 81:8 target.

The one-outside-label packet says source 81 row 8 has bootstrap-core witnesses
[0,2] and singleton outside supports 5 and 6.  This audit asks a narrow
proof-mining question: if center 8 is activated by either singleton support,
can its selected row differ from the fixed source-81 row while the surrounding
source-81 selected rows are preserved, or while one additional row is allowed
to move?

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
    _base_selected_rows,
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


SCHEMA = "erdos97.bootstrap_t12_81_8_singleton_support_audit.v1"
STATUS = "BOOTSTRAP_T12_81_8_SINGLETON_SUPPORT_AUDIT_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "ONLY_ORIGINAL_ROW8_SURVIVES_FIXED_AND_ONE_ROW_DROP_SUPPORT_AUDITS"
CLAIM_SCOPE = (
    "Fixed selected-row-neighborhood singleton-support audit for source 81 row "
    "8. It enumerates the nine center-8 selected rows containing bootstrap-core "
    "witnesses [0,2] and one singleton support label, then checks the fixed "
    "source-81 neighborhood and a one-row-drop relaxation by row-pair, "
    "witness-pair, and crossing filters. The only survivors keep the original "
    "row 8 and, in the one-row-drop scan, also keep the dropped row equal to "
    "its original source-81 row. This does not prove singleton support "
    "existence, row forcing, does not prove n=9, does not prove the bridge, "
    "and is not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_8_singleton_support_audit.json"
)

SOURCE_RECORD_ID = 81
TARGET_ROW_KEY = "81:8"
TARGET_ROW_CENTER = 8
BOOTSTRAP_CORE_WITNESSES = [0, 2]
SINGLETON_SUPPORT_LABELS = [5, 6]
ORIGINAL_ROW = [0, 2, 5, 6]
ONE_ROW_DROP_CENTERS = list(range(8))

EXPECTED_FIXED_REJECTION_COUNTS = {
    "row_pair+witness_pair+crossing": 6,
    "survive": 1,
    "witness_pair+crossing": 2,
}
EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS = {
    "crossing": 47,
    "row_pair+crossing": 11,
    "row_pair+witness_pair": 36,
    "row_pair+witness_pair+crossing": 4692,
    "survive": 8,
    "witness_pair+crossing": 246,
}
EXPECTED_ONE_ROW_DROP_PER_ROW8 = {
    "0,1,2,5": {
        "crossing": 3,
        "row_pair+crossing": 1,
        "row_pair+witness_pair+crossing": 552,
        "witness_pair+crossing": 4,
    },
    "0,1,2,6": {
        "crossing": 4,
        "row_pair+crossing": 3,
        "row_pair+witness_pair+crossing": 548,
        "witness_pair+crossing": 5,
    },
    "0,2,3,5": {
        "crossing": 5,
        "row_pair+witness_pair+crossing": 550,
        "witness_pair+crossing": 5,
    },
    "0,2,3,6": {
        "row_pair+witness_pair+crossing": 553,
        "witness_pair+crossing": 7,
    },
    "0,2,4,5": {
        "crossing": 4,
        "row_pair+witness_pair+crossing": 472,
        "witness_pair+crossing": 84,
    },
    "0,2,4,6": {
        "crossing": 3,
        "row_pair+crossing": 4,
        "row_pair+witness_pair+crossing": 548,
        "witness_pair+crossing": 5,
    },
    "0,2,5,6": {
        "crossing": 24,
        "row_pair+witness_pair": 32,
        "row_pair+witness_pair+crossing": 448,
        "survive": 8,
        "witness_pair+crossing": 48,
    },
    "0,2,5,7": {
        "crossing": 1,
        "row_pair+crossing": 3,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 546,
        "witness_pair+crossing": 6,
    },
    "0,2,6,7": {
        "crossing": 3,
        "row_pair+witness_pair+crossing": 475,
        "witness_pair+crossing": 82,
    },
}
EXPECTED_ONE_ROW_DROP_PER_DROPPED = {
    0: {
        "crossing": 3,
        "row_pair+crossing": 3,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 593,
        "survive": 1,
        "witness_pair+crossing": 26,
    },
    1: {
        "crossing": 4,
        "row_pair+crossing": 3,
        "row_pair+witness_pair": 8,
        "row_pair+witness_pair+crossing": 590,
        "survive": 1,
        "witness_pair+crossing": 24,
    },
    2: {
        "crossing": 8,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 582,
        "survive": 1,
        "witness_pair+crossing": 35,
    },
    3: {
        "crossing": 13,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 573,
        "survive": 1,
        "witness_pair+crossing": 39,
    },
    4: {
        "crossing": 9,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 578,
        "survive": 1,
        "witness_pair+crossing": 38,
    },
    5: {
        "crossing": 3,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 587,
        "survive": 1,
        "witness_pair+crossing": 35,
    },
    6: {
        "crossing": 4,
        "row_pair+crossing": 4,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 595,
        "survive": 1,
        "witness_pair+crossing": 22,
    },
    7: {
        "crossing": 3,
        "row_pair+crossing": 1,
        "row_pair+witness_pair": 4,
        "row_pair+witness_pair+crossing": 594,
        "survive": 1,
        "witness_pair+crossing": 27,
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _target_one_outside_record() -> dict[str, object]:
    one_outside = build_t12_one_outside_payload()
    records = one_outside.get("records")
    if not isinstance(records, Sequence):
        raise AssertionError("one-outside packet records must be a sequence")
    for record in records:
        if not isinstance(record, Mapping):
            raise AssertionError("one-outside records must be mappings")
        if (
            int(record["source_record_id"]) == SOURCE_RECORD_ID
            and int(record["row_center"]) == TARGET_ROW_CENTER
        ):
            support_labels = [
                int(option["support_label"]) for option in record["support_options"]
            ]
            return {
                "source_record_id": int(record["source_record_id"]),
                "row_center": int(record["row_center"]),
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
    raise AssertionError("could not find source 81 row 8 in one-outside packet")


def _target_row_candidates() -> list[list[int]]:
    candidates: set[tuple[int, ...]] = set()
    core = set(BOOTSTRAP_CORE_WITNESSES)
    for support_label in SINGLETON_SUPPORT_LABELS:
        required = core | {support_label}
        for fourth in CYCLIC_ORDER:
            if fourth != TARGET_ROW_CENTER and fourth not in required:
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
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for candidate in _target_row_candidates():
        rows = [list(row) for row in base_rows]
        rows[TARGET_ROW_CENTER] = list(candidate)
        rejection = _rejection_data(rows)
        records.append(
            {
                "target_center": TARGET_ROW_CENTER,
                "target_center_class": candidate,
                "is_original_row": candidate == ORIGINAL_ROW,
                **rejection,
            }
        )
    return records


def _scan_one_row_drop(base_rows: Sequence[Sequence[int]]) -> dict[str, object]:
    total_counts: Counter[str] = Counter()
    per_target_row_counts: dict[str, Counter[str]] = {
        _row_key(candidate): Counter() for candidate in _target_row_candidates()
    }
    per_dropped_counts: dict[int, Counter[str]] = {
        center: Counter() for center in ONE_ROW_DROP_CENTERS
    }
    survivors: list[dict[str, object]] = []

    for target_row in _target_row_candidates():
        target_key = _row_key(target_row)
        for dropped_center in ONE_ROW_DROP_CENTERS:
            for replacement_row in _all_replacement_rows(dropped_center):
                rows = [list(row) for row in base_rows]
                rows[TARGET_ROW_CENTER] = list(target_row)
                rows[dropped_center] = list(replacement_row)
                category = str(_rejection_data(rows)["rejection_category"])
                total_counts[category] += 1
                per_target_row_counts[target_key][category] += 1
                per_dropped_counts[dropped_center][category] += 1
                if category == "survive":
                    survivors.append(
                        {
                            "target_center_class": list(target_row),
                            "target_center_class_is_original": (
                                target_row == ORIGINAL_ROW
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
        "per_target_center_class": [
            {
                "target_center_class": list(candidate),
                "target_center_class_is_original": candidate == ORIGINAL_ROW,
                "candidate_count": sum(
                    per_target_row_counts[_row_key(candidate)].values()
                ),
                "surviving_candidate_count": per_target_row_counts[
                    _row_key(candidate)
                ].get("survive", 0),
                "rejection_category_counts": _json_counter(
                    per_target_row_counts[_row_key(candidate)]
                ),
            }
            for candidate in _target_row_candidates()
        ],
        "per_dropped_center": [
            {
                "dropped_center": center,
                "source_row": list(base_rows[center]),
                "replacement_row_count": len(_all_replacement_rows(center)),
                "candidate_count": sum(per_dropped_counts[center].values()),
                "surviving_candidate_count": per_dropped_counts[center].get(
                    "survive", 0
                ),
                "rejection_category_counts": _json_counter(per_dropped_counts[center]),
            }
            for center in ONE_ROW_DROP_CENTERS
        ],
        "survivors": survivors,
    }


def build_t12_81_8_singleton_support_audit_payload() -> dict[str, object]:
    """Return the deterministic source-81 row-8 singleton-support audit."""

    base_rows = _base_selected_rows()
    target_one_outside_record = _target_one_outside_record()
    if target_one_outside_record["bootstrap_core_witnesses"] != BOOTSTRAP_CORE_WITNESSES:
        raise AssertionError("source one-outside bootstrap-core witnesses drifted")
    if target_one_outside_record["support_labels"] != SINGLETON_SUPPORT_LABELS:
        raise AssertionError("source one-outside singleton supports drifted")
    if base_rows[TARGET_ROW_CENTER] != ORIGINAL_ROW:
        raise AssertionError("source-81 row 8 drifted")

    fixed_records = _fixed_candidate_records(base_rows)
    fixed_counts = Counter(str(record["rejection_category"]) for record in fixed_records)
    fixed_survivors = [
        record
        for record in fixed_records
        if record["passes_basic_incidence_crossing_filters"]
    ]
    one_row_drop = _scan_one_row_drop(base_rows)
    one_row_drop_survivors = one_row_drop["survivors"]
    if not isinstance(one_row_drop_survivors, Sequence):
        raise AssertionError("one-row-drop survivors must be a sequence")
    non_original_one_drop_survivors = [
        survivor
        for survivor in one_row_drop_survivors
        if not survivor["target_center_class_is_original"]
    ]

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "This audit preserves the source-81 selected-row neighborhood, or drops exactly one non-target row in the relaxation.",
            "A row containing bootstrap-core witnesses plus a singleton support is activation bookkeeping, not a proof that a genuine rich class exists.",
            "The audit uses incidence and crossing filters only, not Euclidean realizability.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": CYCLIC_ORDER,
            "target_center": TARGET_ROW_CENTER,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
            "original_target_center_class": ORIGINAL_ROW,
            "target_center_candidate_count": len(_target_row_candidates()),
            "fixed_neighborhood_candidate_count": len(fixed_records),
            "fixed_neighborhood_surviving_candidate_count": len(fixed_survivors),
            "fixed_neighborhood_non_original_survivor_count": sum(
                1 for survivor in fixed_survivors if not survivor["is_original_row"]
            ),
            "fixed_neighborhood_rejection_category_counts": _json_counter(
                fixed_counts
            ),
            "one_row_drop_centers": ONE_ROW_DROP_CENTERS,
            "one_row_drop_replacement_count_per_center": 70,
            "one_row_drop_candidate_count": one_row_drop["candidate_count"],
            "one_row_drop_surviving_candidate_count": len(one_row_drop_survivors),
            "one_row_drop_non_original_row8_survivor_count": len(
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
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not allow two or more other rows to move, and does not "
                "model additional auxiliary rich supports."
            ),
        },
        "source_rows": {str(center): base_rows[center] for center in CYCLIC_ORDER},
        "candidate_generation": {
            "target_center_candidate_classes": _target_row_candidates(),
            "candidate_rule": (
                "4-sets at center 8 containing bootstrap-core witnesses [0,2] "
                "and at least one singleton support label from [5,6]."
            ),
        },
        "source_one_outside_record": target_one_outside_record,
        "fixed_neighborhood_candidates": fixed_records,
        "one_row_drop": one_row_drop,
        "source_one_outside_packet": {
            "path": ONE_OUTSIDE_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": ONE_OUTSIDE_SCHEMA,
            "status": ONE_OUTSIDE_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_8_singleton_support_audit.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_8_singleton_support_audit.py "
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
        "target_row_key": TARGET_ROW_KEY,
        "source_record_ids": [SOURCE_RECORD_ID],
        "cyclic_order": CYCLIC_ORDER,
        "target_center": TARGET_ROW_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
        "original_target_center_class": ORIGINAL_ROW,
        "target_center_candidate_count": 9,
        "fixed_neighborhood_candidate_count": 9,
        "fixed_neighborhood_surviving_candidate_count": 1,
        "fixed_neighborhood_non_original_survivor_count": 0,
        "fixed_neighborhood_rejection_category_counts": (
            EXPECTED_FIXED_REJECTION_COUNTS
        ),
        "one_row_drop_centers": ONE_ROW_DROP_CENTERS,
        "one_row_drop_replacement_count_per_center": 70,
        "one_row_drop_candidate_count": 5040,
        "one_row_drop_surviving_candidate_count": 8,
        "one_row_drop_non_original_row8_survivor_count": 0,
        "one_row_drop_survivors_all_original_rows": True,
        "one_row_drop_rejection_category_counts": (
            EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS
        ),
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    one_outside = payload.get("source_one_outside_record")
    if not isinstance(one_outside, Mapping):
        raise AssertionError("source_one_outside_record must be a mapping")
    if one_outside.get("support_labels") != SINGLETON_SUPPORT_LABELS:
        raise AssertionError("source one-outside support labels drifted")

    fixed_candidates = payload.get("fixed_neighborhood_candidates")
    if not isinstance(fixed_candidates, Sequence) or len(fixed_candidates) != 9:
        raise AssertionError("expected nine fixed-neighborhood candidates")
    fixed_survivors = [
        record
        for record in fixed_candidates
        if isinstance(record, Mapping)
        and record.get("passes_basic_incidence_crossing_filters")
    ]
    if len(fixed_survivors) != 1:
        raise AssertionError("expected exactly one fixed-neighborhood survivor")
    if fixed_survivors[0].get("target_center_class") != ORIGINAL_ROW:
        raise AssertionError("fixed-neighborhood survivor should be the original row")

    one_row_drop = payload.get("one_row_drop")
    if not isinstance(one_row_drop, Mapping):
        raise AssertionError("one_row_drop must be a mapping")
    if one_row_drop.get("rejection_category_counts") != (
        EXPECTED_ONE_ROW_DROP_REJECTION_COUNTS
    ):
        raise AssertionError("one-row-drop rejection counts drifted")

    per_target = one_row_drop.get("per_target_center_class")
    if not isinstance(per_target, Sequence) or len(per_target) != 9:
        raise AssertionError("expected nine per-target-center-class summaries")
    for record in per_target:
        if not isinstance(record, Mapping):
            raise AssertionError("per-target-center-class summaries must be mappings")
        row_key = _row_key(_int_list(record["target_center_class"]))
        expected_counts = EXPECTED_ONE_ROW_DROP_PER_ROW8[row_key]
        if record.get("rejection_category_counts") != expected_counts:
            raise AssertionError(f"one-row-drop counts drifted for row {row_key}")

    per_dropped = one_row_drop.get("per_dropped_center")
    if not isinstance(per_dropped, Sequence) or len(per_dropped) != 8:
        raise AssertionError("expected eight dropped-center summaries")
    for record in per_dropped:
        if not isinstance(record, Mapping):
            raise AssertionError("dropped-center summaries must be mappings")
        center = int(record["dropped_center"])
        if record.get("replacement_row_count") != 70:
            raise AssertionError(f"dropped center {center} has bad row count")
        if record.get("candidate_count") != 630:
            raise AssertionError(f"dropped center {center} has bad candidate count")
        if record.get("rejection_category_counts") != (
            EXPECTED_ONE_ROW_DROP_PER_DROPPED[center]
        ):
            raise AssertionError(f"dropped center {center} counts drifted")

    survivors = one_row_drop.get("survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 8:
        raise AssertionError("expected eight one-row-drop survivors")
    if any(
        not isinstance(survivor, Mapping)
        or not survivor.get("target_center_class_is_original")
        or not survivor.get("dropped_center_class_is_original")
        for survivor in survivors
    ):
        raise AssertionError("one-row-drop survivors should keep original rows")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_8_singleton_support_audit.py"
    ):
        raise AssertionError("provenance generator drifted")
