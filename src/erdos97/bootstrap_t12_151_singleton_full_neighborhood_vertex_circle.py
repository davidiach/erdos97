"""Full-neighborhood vertex-circle packet for bootstrap/T12 source-151 rows.

The earlier source-151 singleton-support audit keeps the surrounding selected-row
neighborhood fixed, or allows one or two additional rows to move. This packet
widens that boundary for the two source-151 singleton-support targets: it fixes
center 5 or center 8 to each bootstrap-core-plus-singleton-support activation
row while every other center may choose an arbitrary selected 4-set.

Basic incidence/crossing/cap filters alone leave complete assignments, including
assignments with non-original target rows. The packet records that all such
full-neighborhood survivors are then killed by the exact vertex-circle quotient
self-edge/strict-cycle replay. It is proof-mining bookkeeping only, not a
Euclidean realizability theorem and not a proof of row forcing.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from erdos97.bootstrap_t12_151_singleton_support_audit import (
    DEFAULT_ARTIFACT as SINGLETON_AUDIT_ARTIFACT,
    SCAN_STATUS as SINGLETON_AUDIT_SCAN_STATUS,
    SCHEMA as SINGLETON_AUDIT_SCHEMA,
    SOURCE_RECORD_ID,
    STATUS as SINGLETON_AUDIT_STATUS,
    TARGET_SPECS,
    _bootstrap_core_witnesses,
    _original_row,
    _singleton_support_labels,
    _target_row_candidates,
    _target_row_key,
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


SCHEMA = "erdos97.bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.v1"
STATUS = "BOOTSTRAP_T12_151_SINGLETON_FULL_NEIGHBORHOOD_VERTEX_CIRCLE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
SCAN_STATUS = "FULL_NEIGHBORHOOD_BASIC_SURVIVORS_ALL_VERTEX_CIRCLE_OBSTRUCTED"
CLAIM_SCOPE = (
    "Full-neighborhood diagnostic for the source-151 singleton-support targets "
    "151:5 and 151:8. It fixes each target center to each 4-set containing its "
    "bootstrap-core witnesses and at least one singleton support label, lets "
    "all other centers use arbitrary selected 4-sets, and applies row-pair, "
    "witness-pair, selected-indegree, crossing, and exact vertex-circle quotient "
    "replay. Basic filters leave 50 complete assignments, including 36 with "
    "non-original target rows, but all 50 are killed by vertex-circle self-edge "
    "or strict-cycle obstructions. This is not a proof of singleton support "
    "existence, not a proof of row forcing, not a proof of n=9, not a proof of "
    "the bridge, and not a counterexample."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT = (
    REPO_ROOT
    / "data"
    / "certificates"
    / "bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.json"
)

TARGET_CENTERS = sorted(TARGET_SPECS)
ROW_REPLACEMENT_COUNT_PER_CENTER = 70
IMPLICIT_ASSIGNMENT_SPACE_SIZE_PER_TARGET = 9 * (
    ROW_REPLACEMENT_COUNT_PER_CENTER ** (N - 1)
)
IMPLICIT_ASSIGNMENT_SPACE_SIZE = (
    len(TARGET_CENTERS) * IMPLICIT_ASSIGNMENT_SPACE_SIZE_PER_TARGET
)
EXPECTED_VERTEX_CIRCLE_STATUS_COUNTS = {"self_edge": 37, "strict_cycle": 13}
EXPECTED_EMPTY_DOMAIN_DEPTH_HISTOGRAM = {
    "1": 41,
    "2": 797,
    "3": 2230,
    "4": 3926,
    "5": 2772,
    "6": 1654,
    "7": 539,
}
EXPECTED_BY_KEY: dict[str, dict[str, object]] = {
    "151:5": {
        "target_center": 5,
        "search_node_count": 15_674,
        "empty_domain_count": 8_148,
        "basic_filter_complete_assignment_count": 34,
        "non_original_target_basic_assignment_count": 27,
        "vertex_circle_status_counts": {"self_edge": 27, "strict_cycle": 7},
        "empty_domain_depth_histogram": {
            "1": 21,
            "2": 328,
            "3": 1281,
            "4": 2668,
            "5": 2130,
            "6": 1303,
            "7": 417,
        },
    },
    "151:8": {
        "target_center": 8,
        "search_node_count": 7_035,
        "empty_domain_count": 3_811,
        "basic_filter_complete_assignment_count": 16,
        "non_original_target_basic_assignment_count": 9,
        "vertex_circle_status_counts": {"self_edge": 10, "strict_cycle": 6},
        "empty_domain_depth_histogram": {
            "1": 20,
            "2": 469,
            "3": 949,
            "4": 1258,
            "5": 642,
            "6": 351,
            "7": 122,
        },
    },
}
EXPECTED_PER_TARGET_ROW: dict[str, dict[str, dict[str, object]]] = {
    "151:5": {
        "0,2,4,7": {
            "search_node_count": 1099,
            "empty_domain_count": 537,
            "basic_filter_complete_assignment_count": 5,
            "vertex_circle_status_counts": {"self_edge": 4, "strict_cycle": 1},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 27,
                "3": 79,
                "4": 162,
                "5": 163,
                "6": 73,
                "7": 32,
            },
        },
        "0,2,4,8": {
            "search_node_count": 392,
            "empty_domain_count": 207,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 5,
                "2": 27,
                "3": 61,
                "4": 61,
                "5": 43,
                "6": 4,
                "7": 6,
            },
        },
        "1,2,4,7": {
            "search_node_count": 937,
            "empty_domain_count": 472,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 29,
                "3": 83,
                "4": 170,
                "5": 110,
                "6": 58,
                "7": 21,
            },
        },
        "1,2,4,8": {
            "search_node_count": 414,
            "empty_domain_count": 209,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 5,
                "2": 29,
                "3": 53,
                "4": 50,
                "5": 44,
                "6": 27,
                "7": 1,
            },
        },
        "2,3,4,7": {
            "search_node_count": 808,
            "empty_domain_count": 445,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 24,
                "3": 105,
                "4": 183,
                "5": 95,
                "6": 37,
            },
        },
        "2,3,4,8": {
            "search_node_count": 475,
            "empty_domain_count": 227,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 5,
                "2": 27,
                "3": 49,
                "4": 51,
                "5": 53,
                "6": 29,
                "7": 13,
            },
        },
        "2,4,6,7": {
            "search_node_count": 5426,
            "empty_domain_count": 2859,
            "basic_filter_complete_assignment_count": 10,
            "vertex_circle_status_counts": {"self_edge": 10},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 55,
                "3": 389,
                "4": 1006,
                "5": 729,
                "6": 486,
                "7": 193,
            },
        },
        "2,4,6,8": {
            "search_node_count": 5290,
            "empty_domain_count": 2772,
            "basic_filter_complete_assignment_count": 12,
            "vertex_circle_status_counts": {"self_edge": 10, "strict_cycle": 2},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 66,
                "3": 354,
                "4": 870,
                "5": 809,
                "6": 538,
                "7": 134,
            },
        },
        "2,4,7,8": {
            "search_node_count": 833,
            "empty_domain_count": 420,
            "basic_filter_complete_assignment_count": 7,
            "vertex_circle_status_counts": {"self_edge": 3, "strict_cycle": 4},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 44,
                "3": 108,
                "4": 115,
                "5": 84,
                "6": 51,
                "7": 17,
            },
        },
    },
    "151:8": {
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
        "0,1,2,7": {
            "search_node_count": 2299,
            "empty_domain_count": 1266,
            "basic_filter_complete_assignment_count": 3,
            "vertex_circle_status_counts": {"self_edge": 3},
            "empty_domain_depth_histogram": {
                "1": 6,
                "2": 88,
                "3": 272,
                "4": 477,
                "5": 236,
                "6": 140,
                "7": 47,
            },
        },
        "1,2,3,5": {
            "search_node_count": 239,
            "empty_domain_count": 161,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 2,
                "2": 70,
                "3": 49,
                "4": 32,
                "5": 2,
                "6": 6,
            },
        },
        "1,2,3,7": {
            "search_node_count": 461,
            "empty_domain_count": 272,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 2,
                "2": 63,
                "3": 62,
                "4": 110,
                "5": 25,
                "6": 9,
                "7": 1,
            },
        },
        "1,2,4,5": {
            "search_node_count": 325,
            "empty_domain_count": 203,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 60,
                "3": 87,
                "4": 40,
                "5": 5,
                "6": 10,
            },
        },
        "1,2,4,7": {
            "search_node_count": 786,
            "empty_domain_count": 427,
            "basic_filter_complete_assignment_count": 3,
            "vertex_circle_status_counts": {"self_edge": 2, "strict_cycle": 1},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 44,
                "3": 108,
                "4": 149,
                "5": 83,
                "6": 40,
                "7": 2,
            },
        },
        "1,2,5,6": {
            "search_node_count": 603,
            "empty_domain_count": 330,
            "basic_filter_complete_assignment_count": 0,
            "vertex_circle_status_counts": {},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 46,
                "3": 108,
                "4": 100,
                "5": 41,
                "6": 20,
                "7": 14,
            },
        },
        "1,2,5,7": {
            "search_node_count": 907,
            "empty_domain_count": 464,
            "basic_filter_complete_assignment_count": 7,
            "vertex_circle_status_counts": {"self_edge": 3, "strict_cycle": 4},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 44,
                "3": 104,
                "4": 147,
                "5": 91,
                "6": 57,
                "7": 20,
            },
        },
        "1,2,6,7": {
            "search_node_count": 927,
            "empty_domain_count": 460,
            "basic_filter_complete_assignment_count": 3,
            "vertex_circle_status_counts": {"self_edge": 2, "strict_cycle": 1},
            "empty_domain_depth_histogram": {
                "1": 1,
                "2": 42,
                "3": 106,
                "4": 139,
                "5": 104,
                "6": 44,
                "7": 24,
            },
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


def _require_mapping(value: Any, name: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise AssertionError(f"{name} must be a mapping")
    return value


def _require_sequence(value: Any, name: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise AssertionError(f"{name} must be a sequence")
    return value


def _validate_source_singleton_artifact(
    source_artifact: Path = SINGLETON_AUDIT_ARTIFACT,
) -> None:
    payload = _load_json(source_artifact)
    if payload.get("schema") != SINGLETON_AUDIT_SCHEMA:
        raise AssertionError("source singleton-support artifact schema drifted")
    if payload.get("status") != SINGLETON_AUDIT_STATUS:
        raise AssertionError("source singleton-support artifact status drifted")

    summary = _require_mapping(payload.get("summary"), "source summary")
    if summary.get("scan_status") != SINGLETON_AUDIT_SCAN_STATUS:
        raise AssertionError("source singleton-support scan status drifted")
    if summary.get("source_record_ids") != [SOURCE_RECORD_ID]:
        raise AssertionError("source singleton-support record ids drifted")

    records = _require_sequence(payload.get("target_audits"), "target_audits")
    by_key = {
        str(_require_mapping(record, "target_audit")["target_row_key"]): _require_mapping(
            record, "target_audit"
        )
        for record in records
    }
    if sorted(by_key) != [_target_row_key(center) for center in TARGET_CENTERS]:
        raise AssertionError("source singleton-support target keys drifted")

    for center in TARGET_CENTERS:
        key = _target_row_key(center)
        record = by_key[key]
        if record.get("target_center") != center:
            raise AssertionError(f"source singleton-support center drifted for {key}")
        if record.get("bootstrap_core_witnesses") != _bootstrap_core_witnesses(center):
            raise AssertionError(f"source singleton-support core drifted for {key}")
        if record.get("singleton_support_labels") != _singleton_support_labels(center):
            raise AssertionError(f"source singleton-support labels drifted for {key}")
        if record.get("original_target_center_class") != _original_row(center):
            raise AssertionError(f"source singleton-support original row drifted for {key}")
        source_candidates = [
            _int_list(row)
            for row in _require_sequence(
                record.get("target_center_candidate_classes"),
                "target_center_candidate_classes",
            )
        ]
        if source_candidates != _target_row_candidates(center):
            raise AssertionError(f"source singleton-support candidates drifted for {key}")


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


def _search_with_fixed_target(
    target_center: int,
    target_row: Sequence[int],
) -> dict[str, object]:
    target_mask = _row_mask(target_row)
    original_row = _original_row(target_center)
    free_row_centers = [center for center in range(N) if center != target_center]
    assigned: dict[int, int] = {target_center: target_mask}
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
                    "target_center_class_is_original": list(target_row) == original_row,
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
        for center in free_row_centers:
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
        "target_center_class_is_original": list(target_row) == original_row,
        "search_node_count": stats["search_node_count"],
        "empty_domain_count": stats["empty_domain_count"],
        "empty_domain_depth_histogram": _json_counter(empty_depths),
        "basic_filter_complete_assignment_count": stats[
            "basic_filter_complete_assignment_count"
        ],
        "non_original_target_basic_assignment_count": (
            0
            if list(target_row) == original_row
            else stats["basic_filter_complete_assignment_count"]
        ),
        "vertex_circle_status_counts": vertex_circle_counts,
        "vertex_circle_surviving_assignment_count": vertex_circle_counts.get("ok", 0),
        "basic_filter_survivors": survivors,
    }


def _scan_target(target_center: int) -> dict[str, object]:
    target_row_key = _target_row_key(target_center)
    per_target_class = [
        _search_with_fixed_target(target_center, row)
        for row in _target_row_candidates(target_center)
    ]
    aggregate: Counter[str] = Counter()
    empty_depths: Counter[str] = Counter()
    vertex_circle_counts: Counter[str] = Counter()
    survivors: list[dict[str, object]] = []
    for record in per_target_class:
        aggregate["search_node_count"] += int(record["search_node_count"])
        aggregate["empty_domain_count"] += int(record["empty_domain_count"])
        aggregate["basic_filter_complete_assignment_count"] += int(
            record["basic_filter_complete_assignment_count"]
        )
        aggregate["non_original_target_basic_assignment_count"] += int(
            record["non_original_target_basic_assignment_count"]
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
        "target_row_key": target_row_key,
        "target_center": target_center,
        "bootstrap_core_witnesses": _bootstrap_core_witnesses(target_center),
        "singleton_support_labels": _singleton_support_labels(target_center),
        "original_target_center_class": _original_row(target_center),
        "target_center_candidate_classes": _target_row_candidates(target_center),
        "target_center_candidate_count": len(_target_row_candidates(target_center)),
        "free_row_centers": [center for center in range(N) if center != target_center],
        "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
        "implicit_assignment_space_size": IMPLICIT_ASSIGNMENT_SPACE_SIZE_PER_TARGET,
        "search_node_count": aggregate["search_node_count"],
        "empty_domain_count": aggregate["empty_domain_count"],
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "basic_filter_complete_assignment_count": aggregate[
            "basic_filter_complete_assignment_count"
        ],
        "non_original_target_basic_assignment_count": aggregate[
            "non_original_target_basic_assignment_count"
        ],
        "vertex_circle_status_counts": dict(sorted(vertex_circle_counts.items())),
        "vertex_circle_surviving_assignment_count": int(
            vertex_circle_counts.get("ok", 0)
        ),
        "per_target_center_class": per_target_class,
        "basic_filter_survivors": survivors,
    }


def _aggregate_records(records: Sequence[Mapping[str, object]]) -> dict[str, object]:
    aggregate: Counter[str] = Counter()
    empty_depths: Counter[str] = Counter()
    vertex_circle_counts: Counter[str] = Counter()
    for record in records:
        aggregate["search_node_count"] += int(record["search_node_count"])
        aggregate["empty_domain_count"] += int(record["empty_domain_count"])
        aggregate["basic_filter_complete_assignment_count"] += int(
            record["basic_filter_complete_assignment_count"]
        )
        aggregate["non_original_target_basic_assignment_count"] += int(
            record["non_original_target_basic_assignment_count"]
        )
        for depth, count in dict(record["empty_domain_depth_histogram"]).items():
            empty_depths[str(depth)] += int(count)
        for status, count in dict(record["vertex_circle_status_counts"]).items():
            vertex_circle_counts[str(status)] += int(count)
    return {
        "search_node_count": aggregate["search_node_count"],
        "empty_domain_count": aggregate["empty_domain_count"],
        "empty_domain_depth_histogram": dict(sorted(empty_depths.items())),
        "basic_filter_complete_assignment_count": aggregate[
            "basic_filter_complete_assignment_count"
        ],
        "non_original_target_basic_assignment_count": aggregate[
            "non_original_target_basic_assignment_count"
        ],
        "vertex_circle_status_counts": dict(sorted(vertex_circle_counts.items())),
        "vertex_circle_surviving_assignment_count": int(
            vertex_circle_counts.get("ok", 0)
        ),
    }


def build_t12_151_singleton_full_neighborhood_vertex_circle_payload() -> dict[str, object]:
    """Return the deterministic source-151 full-neighborhood packet."""

    _validate_source_singleton_artifact()
    target_audits = [_scan_target(center) for center in TARGET_CENTERS]
    aggregate = _aggregate_records(target_audits)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "Full-neighborhood basic filters leave non-original source-151 target-row survivors.",
            (
                "All recorded full-neighborhood survivors close only after exact "
                "vertex-circle quotient replay."
            ),
            "The packet does not prove singleton support existence or row/rich-class forcing.",
            (
                "No n=9 finite-case status, bridge status, official status, "
                "or counterexample status changes."
            ),
        ],
        "summary": {
            "source_record_ids": [SOURCE_RECORD_ID],
            "cyclic_order": list(range(N)),
            "target_row_keys": [_target_row_key(center) for center in TARGET_CENTERS],
            "target_centers": TARGET_CENTERS,
            "target_count": len(TARGET_CENTERS),
            "target_center_candidate_count_by_key": {
                _target_row_key(center): len(_target_row_candidates(center))
                for center in TARGET_CENTERS
            },
            "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
            "implicit_assignment_space_size_per_target": (
                IMPLICIT_ASSIGNMENT_SPACE_SIZE_PER_TARGET
            ),
            "implicit_assignment_space_size": IMPLICIT_ASSIGNMENT_SPACE_SIZE,
            "search_node_count": aggregate["search_node_count"],
            "empty_domain_count": aggregate["empty_domain_count"],
            "basic_filter_complete_assignment_count": aggregate[
                "basic_filter_complete_assignment_count"
            ],
            "basic_filter_non_original_target_assignment_count": aggregate[
                "non_original_target_basic_assignment_count"
            ],
            "vertex_circle_status_counts": aggregate["vertex_circle_status_counts"],
            "vertex_circle_surviving_assignment_count": aggregate[
                "vertex_circle_surviving_assignment_count"
            ],
            "non_original_vertex_circle_surviving_assignment_count": 0,
            "scan_status": SCAN_STATUS,
            "remaining_gap": (
                "This does not prove singleton support existence, does not "
                "prove the rows are forced by minimal or rich-class geometry, "
                "does not model additional auxiliary rich supports, and does "
                "not promote the review-pending n=9 checker."
            ),
        },
        "empty_domain_depth_histogram": aggregate["empty_domain_depth_histogram"],
        "target_audits": target_audits,
        "source_singleton_support_audit": {
            "path": SINGLETON_AUDIT_ARTIFACT.relative_to(REPO_ROOT).as_posix(),
            "schema": SINGLETON_AUDIT_SCHEMA,
            "status": SINGLETON_AUDIT_STATUS,
            "scan_status": SINGLETON_AUDIT_SCAN_STATUS,
        },
        "provenance": {
            "generator": (
                "scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py"
            ),
            "command": (
                "python "
                "scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py "
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
        "cyclic_order": list(range(N)),
        "target_row_keys": ["151:5", "151:8"],
        "target_centers": [5, 8],
        "target_count": 2,
        "target_center_candidate_count_by_key": {"151:5": 9, "151:8": 9},
        "free_row_replacement_count_per_center": ROW_REPLACEMENT_COUNT_PER_CENTER,
        "implicit_assignment_space_size_per_target": 5_188_320_900_000_000,
        "implicit_assignment_space_size": 10_376_641_800_000_000,
        "search_node_count": 22_709,
        "empty_domain_count": 11_959,
        "basic_filter_complete_assignment_count": 50,
        "basic_filter_non_original_target_assignment_count": 36,
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

    records = payload.get("target_audits")
    if not isinstance(records, Sequence) or len(records) != 2:
        raise AssertionError("expected two source-151 full-neighborhood audits")
    by_key = {
        str(record["target_row_key"]): record
        for record in records
        if isinstance(record, Mapping)
    }
    if sorted(by_key) != ["151:5", "151:8"]:
        raise AssertionError("unexpected source-151 full-neighborhood audit keys")

    for key, expected in EXPECTED_BY_KEY.items():
        record = by_key[key]
        for expected_key, expected_value in expected.items():
            if record.get(expected_key) != expected_value:
                raise AssertionError(
                    f"{key} {expected_key} is {record.get(expected_key)!r}, "
                    f"expected {expected_value!r}"
                )
        if record.get("target_center_candidate_count") != 9:
            raise AssertionError(f"{key} candidate count drifted")
        if record.get("free_row_replacement_count_per_center") != 70:
            raise AssertionError(f"{key} free-row replacement count drifted")
        if record.get("implicit_assignment_space_size") != 5_188_320_900_000_000:
            raise AssertionError(f"{key} implicit assignment-space size drifted")
        if record.get("vertex_circle_surviving_assignment_count") != 0:
            raise AssertionError(f"{key} has vertex-circle survivors")

        per_target = record.get("per_target_center_class")
        if not isinstance(per_target, Sequence) or len(per_target) != 9:
            raise AssertionError(f"{key} should have nine target-center class summaries")
        expected_per_row = EXPECTED_PER_TARGET_ROW[key]
        for item in per_target:
            if not isinstance(item, Mapping):
                raise AssertionError(f"{key} target-center class summaries must be mappings")
            target_class = item.get("target_center_class")
            if not isinstance(target_class, Sequence):
                raise AssertionError(f"{key} target_center_class must be a sequence")
            row_key = _row_key(_int_list(target_class))
            expected_item = expected_per_row.get(row_key)
            if expected_item is None:
                raise AssertionError(f"{key} unexpected target-center class {row_key!r}")
            for expected_item_key, expected_item_value in expected_item.items():
                if item.get(expected_item_key) != expected_item_value:
                    raise AssertionError(
                        f"{key} target {row_key} {expected_item_key} is "
                        f"{item.get(expected_item_key)!r}, "
                        f"expected {expected_item_value!r}"
                    )
            if item.get("vertex_circle_surviving_assignment_count") != 0:
                raise AssertionError(f"{key} target {row_key} has vertex-circle survivors")

        survivors = record.get("basic_filter_survivors")
        if not isinstance(survivors, Sequence):
            raise AssertionError(f"{key} basic_filter_survivors must be a sequence")
        if len(survivors) != expected["basic_filter_complete_assignment_count"]:
            raise AssertionError(f"{key} survivor list length drifted")
        if any(
            isinstance(survivor, Mapping) and survivor.get("vertex_circle_status") == "ok"
            for survivor in survivors
        ):
            raise AssertionError(f"{key} has a vertex-circle-clean survivor")

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
        "scripts/check_bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.py"
    ):
        raise AssertionError("provenance generator drifted")
