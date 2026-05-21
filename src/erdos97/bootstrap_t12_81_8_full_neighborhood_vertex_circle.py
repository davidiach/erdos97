"""Full-neighborhood vertex-circle packet for bootstrap/T12 source 81 row 8.

The earlier singleton-support audit for source 81 row 8 keeps the surrounding
source-81 selected-row neighborhood fixed, or drops one additional row.  This
packet widens that boundary: it fixes center 8 to each activation row containing
bootstrap-core witnesses [0,2] and at least one singleton support label from
[5,6], while every other center may choose an arbitrary selected 4-set.

Basic incidence/crossing filters alone leave non-original row-8 complete
assignments.  The packet records that all such full-neighborhood survivors are
then killed by the exact vertex-circle quotient self-edge/strict-cycle filter.
It is proof-mining bookkeeping only, not a Euclidean realizability theorem and
not a proof of row forcing.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_81_8_singleton_support_audit import (
    BOOTSTRAP_CORE_WITNESSES,
    DEFAULT_ARTIFACT as SINGLETON_AUDIT_ARTIFACT,
    ORIGINAL_ROW,
    SCAN_STATUS as SINGLETON_AUDIT_SCAN_STATUS,
    SCHEMA as SINGLETON_AUDIT_SCHEMA,
    SINGLETON_SUPPORT_LABELS,
    SOURCE_RECORD_ID,
    STATUS as SINGLETON_AUDIT_STATUS,
    TARGET_ROW_CENTER,
    TARGET_ROW_KEY,
    _target_row_candidates,
)
from erdos97.n9_vertex_circle_exhaustive import (
    MASK_BITS,
    MAX_INDEGREE,
    N,
    OPTIONS,
    PAIR_CAP,
    PAIRS,
    ROW_PAIR_INDICES,
    rows_compatible,
    vertex_circle_status,
)


SCHEMA = "erdos97.bootstrap_t12_81_8_full_neighborhood_vertex_circle.v1"
STATUS = "BOOTSTRAP_T12_81_8_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"
CLAIM_SCOPE = (
    "Full-neighborhood diagnostic for the source-81 row-8 singleton-support "
    "target. It fixes center 8 to each 4-set containing bootstrap-core "
    "witnesses [0,2] and at least one singleton support label from [5,6], "
    "lets all other centers use arbitrary selected 4-sets, and applies "
    "row-pair, witness-pair, crossing, and selected-indegree filters before "
    "exact vertex-circle quotient replay. Basic filters leave 34 complete "
    "assignments, including 27 with non-original row 8, but all 34 are killed "
    "by vertex-circle self-edge or strict-cycle obstructions. This is not a "
    "proof of singleton support existence, not a proof of row forcing, not a "
    "proof of n=9, not a proof of the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_81_8_full_neighborhood_vertex_circle.json"
)

FREE_ROW_CENTERS = [center for center in range(N) if center != TARGET_ROW_CENTER]
ROW_REPLACEMENT_COUNT_PER_CENTER = 70
IMPLICIT_ASSIGNMENT_SPACE_SIZE = len(_target_row_candidates()) * (
    ROW_REPLACEMENT_COUNT_PER_CENTER ** len(FREE_ROW_CENTERS)
)
EXPECTED_VERTEX_CIRCLE_STATUS_COUNTS = {"self_edge": 27, "strict_cycle": 7}
EXPECTED_EMPTY_DOMAIN_DEPTH_HISTOGRAM = {
    "1": 23,
    "2": 273,
    "3": 1306,
    "4": 2879,
    "5": 2272,
    "6": 1340,
    "7": 343,
}
EXPECTED_PER_TARGET_ROW: dict[str, dict[str, object]] = {
    "0,1,2,5": {
        "search_node_count": 488,
        "empty_domain_count": 228,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 12,
            "3": 53,
            "4": 64,
            "5": 55,
            "6": 25,
            "7": 14,
        },
    },
    "0,1,2,6": {
        "search_node_count": 768,
        "empty_domain_count": 420,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 25,
            "3": 96,
            "4": 194,
            "5": 74,
            "6": 27,
            "7": 3,
        },
    },
    "0,2,3,5": {
        "search_node_count": 427,
        "empty_domain_count": 200,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 18,
            "3": 36,
            "4": 72,
            "5": 51,
            "6": 18,
        },
    },
    "0,2,3,6": {
        "search_node_count": 1046,
        "empty_domain_count": 545,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 29,
            "3": 83,
            "4": 180,
            "5": 132,
            "6": 95,
            "7": 25,
        },
    },
    "0,2,4,5": {
        "search_node_count": 382,
        "empty_domain_count": 196,
        "basic_filter_complete_assignment_count": 0,
        "vertex_circle_status_counts": {},
        "empty_domain_depth_histogram": {
            "1": 5,
            "2": 28,
            "3": 43,
            "4": 63,
            "5": 48,
            "6": 7,
            "7": 2,
        },
    },
    "0,2,4,6": {
        "search_node_count": 1065,
        "empty_domain_count": 526,
        "basic_filter_complete_assignment_count": 5,
        "vertex_circle_status_counts": {"self_edge": 4, "strict_cycle": 1},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 33,
            "3": 67,
            "4": 176,
            "5": 151,
            "6": 76,
            "7": 22,
        },
    },
    "0,2,5,6": {
        "search_node_count": 885,
        "empty_domain_count": 442,
        "basic_filter_complete_assignment_count": 7,
        "vertex_circle_status_counts": {"self_edge": 3, "strict_cycle": 4},
        "empty_domain_depth_histogram": {
            "1": 1,
            "2": 44,
            "3": 94,
            "4": 145,
            "5": 101,
            "6": 44,
            "7": 13,
        },
    },
    "0,2,5,7": {
        "search_node_count": 5455,
        "empty_domain_count": 2937,
        "basic_filter_complete_assignment_count": 12,
        "vertex_circle_status_counts": {"self_edge": 10, "strict_cycle": 2},
        "empty_domain_depth_histogram": {
            "1": 2,
            "2": 39,
            "3": 395,
            "4": 970,
            "5": 855,
            "6": 566,
            "7": 110,
        },
    },
    "0,2,6,7": {
        "search_node_count": 5494,
        "empty_domain_count": 2942,
        "basic_filter_complete_assignment_count": 10,
        "vertex_circle_status_counts": {"self_edge": 10},
        "empty_domain_depth_histogram": {
            "1": 2,
            "2": 45,
            "3": 439,
            "4": 1015,
            "5": 805,
            "6": 482,
            "7": 154,
        },
    },
}


def _int_list(values: Iterable[Any]) -> list[int]:
    return [int(value) for value in values]


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def _json_counter(counter: Counter[Any]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _row_key(row: Sequence[int]) -> str:
    return ",".join(str(label) for label in row)


def _row_mask(row: Iterable[int]) -> int:
    mask = 0
    for label in row:
        mask |= 1 << int(label)
    return mask


def _mask_to_row(row_mask: int) -> list[int]:
    return _int_list(MASK_BITS[row_mask])


def _update_counts(
    row_mask: int,
    column_counts: list[int],
    witness_pair_counts: list[int],
    delta: int,
) -> None:
    for witness in MASK_BITS[row_mask]:
        column_counts[witness] += delta
    for pair_index in ROW_PAIR_INDICES[row_mask]:
        witness_pair_counts[pair_index] += delta


def _compatible_with_assignment(
    center: int,
    row_mask: int,
    assigned: Mapping[int, int],
    column_counts: Sequence[int],
    witness_pair_counts: Sequence[int],
) -> bool:
    if any(column_counts[witness] >= MAX_INDEGREE for witness in MASK_BITS[row_mask]):
        return False
    if any(
        witness_pair_counts[pair_index] >= PAIR_CAP
        for pair_index in ROW_PAIR_INDICES[row_mask]
    ):
        return False
    return all(
        rows_compatible(center, row_mask, other_center, other_row)
        for other_center, other_row in assigned.items()
    )


def _search_with_fixed_target(target_row: Sequence[int]) -> dict[str, object]:
    target_mask = _row_mask(target_row)
    assigned: dict[int, int] = {TARGET_ROW_CENTER: target_mask}
    column_counts = [0] * N
    witness_pair_counts = [0] * len(PAIRS)
    _update_counts(target_mask, column_counts, witness_pair_counts, 1)

    stats: Counter[str] = Counter()
    empty_depths: Counter[int] = Counter()
    survivors: list[dict[str, object]] = []

    def search() -> None:
        stats["search_node_count"] += 1
        if len(assigned) == N:
            status = vertex_circle_status(assigned)
            stats["basic_filter_complete_assignment_count"] += 1
            stats[f"vertex_circle_status:{status}"] += 1
            survivors.append(
                {
                    "target_center_class": list(target_row),
                    "target_center_class_is_original": list(target_row) == ORIGINAL_ROW,
                    "vertex_circle_status": status,
                    "selected_rows": {
                        str(center): _mask_to_row(assigned[center])
                        for center in range(N)
                    },
                }
            )
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in FREE_ROW_CENTERS:
            if center in assigned:
                continue
            options = [
                row_mask
                for row_mask in OPTIONS[center]
                if _compatible_with_assignment(
                    center,
                    row_mask,
                    assigned,
                    column_counts,
                    witness_pair_counts,
                )
            ]
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
            if not options:
                stats["empty_domain_count"] += 1
                empty_depths[len(assigned) - 1] += 1
                return

        if best_center is None or best_options is None:
            raise AssertionError("search reached inconsistent assignment state")
        for row_mask in best_options:
            assigned[best_center] = row_mask
            _update_counts(row_mask, column_counts, witness_pair_counts, 1)
            search()
            _update_counts(row_mask, column_counts, witness_pair_counts, -1)
            del assigned[best_center]

    search()
    vertex_circle_counts = {
        key.removeprefix("vertex_circle_status:"): value
        for key, value in sorted(stats.items())
        if key.startswith("vertex_circle_status:")
    }
    return {
        "target_center_class": list(target_row),
        "target_center_class_is_original": list(target_row) == ORIGINAL_ROW,
        "search_node_count": stats["search_node_count"],
        "empty_domain_count": stats["empty_domain_count"],
        "empty_domain_depth_histogram": _json_counter(empty_depths),
        "basic_filter_complete_assignment_count": stats[
            "basic_filter_complete_assignment_count"
        ],
        "non_original_row8_basic_assignment_count": (
            0
            if list(target_row) == ORIGINAL_ROW
            else stats["basic_filter_complete_assignment_count"]
        ),
        "vertex_circle_status_counts": vertex_circle_counts,
        "vertex_circle_surviving_assignment_count": vertex_circle_counts.get("ok", 0),
        "basic_filter_survivors": survivors,
    }


def _scan_payload() -> dict[str, object]:
    per_target = [_search_with_fixed_target(row) for row in _target_row_candidates()]
    aggregate: Counter[str] = Counter()
    empty_depths: Counter[str] = Counter()
    vertex_circle_counts: Counter[str] = Counter()
    survivors: list[dict[str, object]] = []
    for record in per_target:
        aggregate["search_node_count"] += int(record["search_node_count"])
        aggregate["empty_domain_count"] += int(record["empty_domain_count"])
        aggregate["basic_filter_complete_assignment_count"] += int(
            record["basic_filter_complete_assignment_count"]
        )
        aggregate["non_original_row8_basic_assignment_count"] += int(
            record["non_original_row8_basic_assignment_count"]
        )
        for depth, count in dict(record["empty_domain_depth_histogram"]).items():
            empty_depths[str(depth)] += int(count)
        for status, count in dict(record["vertex_circle_status_counts"]).items():
            vertex_circle_counts[str(status)] += int(count)
        basic_survivors = record["basic_filter_survivors"]
        if not isinstance(basic_survivors, Sequence):
            raise AssertionError("basic_filter_survivors must be a sequence")
        survivors.extend(list(basic_survivors))

    return {
        "per_target_center_class": per_target,
        "aggregate": dict(sorted(aggregate.items())),
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "vertex_circle_status_counts": dict(sorted(vertex_circle_counts.items())),
        "basic_filter_survivors": survivors,
    }


def build_t12_81_8_full_neighborhood_vertex_circle_payload() -> dict[str, object]:
    """Return the deterministic source-81 row-8 full-neighborhood packet."""

    scan = _scan_payload()
    aggregate = scan["aggregate"]
    if not isinstance(aggregate, Mapping):
        raise AssertionError("aggregate must be a mapping")
    vertex_circle_counts = scan["vertex_circle_status_counts"]
    if not isinstance(vertex_circle_counts, Mapping):
        raise AssertionError("vertex_circle_status_counts must be a mapping")

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "Full-neighborhood basic incidence/crossing filters alone leave non-original row-8 survivors.",
            "All recorded full-neighborhood survivors close only after exact vertex-circle quotient replay.",
            "The packet does not prove singleton support existence or row/rich-class forcing.",
            "No n=9 finite-case status, bridge status, official status, or counterexample status changes.",
        ],
        "summary": {
            "target_row_key": TARGET_ROW_KEY,
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": list(range(N)),
            "target_center": TARGET_ROW_CENTER,
            "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
            "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
            "original_target_center_class": ORIGINAL_ROW,
            "target_center_candidate_count": len(_target_row_candidates()),
            "free_row_centers": FREE_ROW_CENTERS,
            "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
            "implicit_assignment_space_size": IMPLICIT_ASSIGNMENT_SPACE_SIZE,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "basic_filter_complete_assignment_count": aggregate[
                "basic_filter_complete_assignment_count"
            ],
            "basic_filter_non_original_row8_assignment_count": aggregate[
                "non_original_row8_basic_assignment_count"
            ],
            "vertex_circle_status_counts": dict(vertex_circle_counts),
            "vertex_circle_surviving_assignment_count": int(
                vertex_circle_counts.get("ok", 0)
            ),
            "non_original_vertex_circle_surviving_assignment_count": 0,
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the row is forced by minimal or rich-class geometry, "
                "does not model additional auxiliary rich supports, and does "
                "not promote the review-pending n=9 checker."
            ),
        },
        "candidate_generation": {
            "target_center_candidate_classes": _target_row_candidates(),
            "candidate_rule": (
                "4-sets at center 8 containing bootstrap-core witnesses [0,2] "
                "and at least one singleton support label from [5,6]."
            ),
        },
        "empty_domain_depth_histogram": scan["empty_domain_depth_histogram"],
        "per_target_center_class": scan["per_target_center_class"],
        "basic_filter_survivors": scan["basic_filter_survivors"],
        "source_singleton_support_audit": {
            "path": SINGLETON_AUDIT_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": SINGLETON_AUDIT_SCHEMA,
            "status": SINGLETON_AUDIT_STATUS,
            "scan_status": SINGLETON_AUDIT_SCAN_STATUS,
        },
        "provenance": {
            "generator": "scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py",
            "command": (
                "python scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py "
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
        "cyclic_order": list(range(N)),
        "target_center": TARGET_ROW_CENTER,
        "bootstrap_core_witnesses": BOOTSTRAP_CORE_WITNESSES,
        "singleton_support_labels": SINGLETON_SUPPORT_LABELS,
        "original_target_center_class": ORIGINAL_ROW,
        "target_center_candidate_count": 9,
        "free_row_centers": FREE_ROW_CENTERS,
        "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
        "implicit_assignment_space_size": 5188320900000000,
        "search_node_count": 16010,
        "empty_domain_count": 8436,
        "basic_filter_complete_assignment_count": 34,
        "basic_filter_non_original_row8_assignment_count": 27,
        "vertex_circle_status_counts": EXPECTED_VERTEX_CIRCLE_STATUS_COUNTS,
        "vertex_circle_surviving_assignment_count": 0,
        "non_original_vertex_circle_surviving_assignment_count": 0,
        "scan_status": SCAN_STATUS,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary {key} is {summary.get(key)!r}, expected {expected!r}"
            )

    if payload.get("empty_domain_depth_histogram") != EXPECTED_EMPTY_DOMAIN_DEPTH_HISTOGRAM:
        raise AssertionError("empty-domain depth histogram drifted")

    per_target = payload.get("per_target_center_class")
    if not isinstance(per_target, Sequence) or len(per_target) != 9:
        raise AssertionError("expected nine target-center class summaries")
    for record in per_target:
        if not isinstance(record, Mapping):
            raise AssertionError("target-center class summaries must be mappings")
        target_class = record.get("target_center_class")
        if not isinstance(target_class, Sequence):
            raise AssertionError("target_center_class must be a sequence")
        key = _row_key(_int_list(target_class))
        expected = EXPECTED_PER_TARGET_ROW.get(key)
        if expected is None:
            raise AssertionError(f"unexpected target-center class {key!r}")
        for expected_key, expected_value in expected.items():
            if record.get(expected_key) != expected_value:
                raise AssertionError(
                    f"target {key} {expected_key} is {record.get(expected_key)!r}, expected {expected_value!r}"
                )
        if record.get("vertex_circle_surviving_assignment_count") != 0:
            raise AssertionError(f"target {key} has vertex-circle survivors")

    survivors = payload.get("basic_filter_survivors")
    if not isinstance(survivors, Sequence) or len(survivors) != 34:
        raise AssertionError("expected 34 full-neighborhood basic-filter survivors")
    if any(
        isinstance(survivor, Mapping) and survivor.get("vertex_circle_status") == "ok"
        for survivor in survivors
    ):
        raise AssertionError("all basic-filter survivors must be vertex-circle obstructed")
    non_original_survivors = [
        survivor
        for survivor in survivors
        if isinstance(survivor, Mapping)
        and not survivor.get("target_center_class_is_original")
    ]
    if len(non_original_survivors) != 27:
        raise AssertionError("expected 27 non-original row-8 basic-filter survivors")

    source = payload.get("source_singleton_support_audit")
    if not isinstance(source, Mapping):
        raise AssertionError("source_singleton_support_audit must be a mapping")
    if source.get("schema") != SINGLETON_AUDIT_SCHEMA:
        raise AssertionError("source singleton-support schema drifted")
    if source.get("scan_status") != SINGLETON_AUDIT_SCAN_STATUS:
        raise AssertionError("source singleton-support scan status drifted")

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping):
        raise AssertionError("provenance must be a mapping")
    if provenance.get("generator") != (
        "scripts/check_bootstrap_t12_81_8_full_neighborhood_vertex_circle.py"
    ):
        raise AssertionError("provenance generator drifted")
