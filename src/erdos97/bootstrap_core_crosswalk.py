"""Bootstrap-core crosswalk diagnostics for current frontier motifs.

This module applies the rich-triple closure and private-halo capacity ledger to
fixed selected-row benchmark patterns.  It is finite bridge bookkeeping only:
it does not prove Erdos Problem #97, does not refute any bridge theorem, and
does not claim a counterexample.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path
from typing import Sequence

from erdos97.adaptive_blockers import RichClasses, singleton_rich_classes_from_pattern
from erdos97.bootstrap_cores import (
    BootstrapCoreAudit,
    ClosureResult,
    audit_bootstrap_core,
    closure,
    validate_full_rich_classes,
)
from erdos97.search import PatternInfo, built_in_patterns


SCHEMA = "erdos97.bootstrap_core_crosswalk.v1"
STATUS = "BOOTSTRAP_CORE_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Bootstrap-core rank and private-halo capacity crosswalk for selected "
    "fixed-row frontier motifs; not a proof of the bridge, not a proof of "
    "Erdos Problem #97, not a counterexample, and not a global status update."
)
REPO_ROOT = Path(__file__).resolve().parents[2]
BASE_APEX_D3_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "n9_base_apex_d3_incidence_capacity_packet.json"
)
BRIDGE_LEMMA_FRONTIER_ARTIFACT = (
    REPO_ROOT / "data" / "certificates" / "bridge_lemma_frontier.json"
)

REGISTERED_ORDER_CASES: dict[str, dict[str, list[int]]] = {
    "C13_sidon_1_2_4_10": {
        "sample_full_filter_survivor": [5, 0, 10, 8, 9, 7, 4, 6, 2, 11, 12, 3, 1],
    },
    "C19_skew": {
        "vertex_circle_survivor": [
            18,
            10,
            7,
            17,
            6,
            3,
            5,
            9,
            14,
            11,
            2,
            13,
            4,
            16,
            12,
            15,
            0,
            8,
            1,
        ],
    },
}

N9_NON_EAR_FRONTIER_IDS = (81, 151)


def _closure_json(result: ClosureResult) -> dict[str, object]:
    return {
        "seed": result.seed,
        "closure_size": len(result.closure),
        "closure": result.closure,
        "order": result.order,
        "step_count": len(result.steps),
        "generates_all": result.generates_all,
    }


def _mask(vertices: Sequence[int]) -> int:
    out = 0
    for vertex in vertices:
        out |= 1 << int(vertex)
    return out


def _vertices(mask: int, n: int) -> list[int]:
    return [vertex for vertex in range(n) if mask & (1 << vertex)]


def _row_masks(rich_classes: RichClasses) -> list[list[int]]:
    return [
        [_mask([int(label) for label in row]) for row in classes]
        for classes in rich_classes
    ]


def _fast_closure(seed: Sequence[int], row_masks: Sequence[Sequence[int]], n: int) -> list[int]:
    """Return closure vertices with prevalidated rows and precomputed masks."""

    closure_mask = _mask(seed)
    changed = True
    while changed:
        changed = False
        for center in range(n):
            if closure_mask & (1 << center):
                continue
            for row_mask in row_masks[center]:
                if (row_mask & closure_mask).bit_count() >= 3:
                    closure_mask |= 1 << center
                    changed = True
                    break
    return _vertices(closure_mask, n)


def search_rank_limit_summary(
    rich_classes: RichClasses,
    limit: int = 3,
) -> dict[str, object]:
    """Fast rank-at-most-limit summary for crosswalk records."""

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    row_masks = _row_masks(rich_classes)
    checked = 0
    largest_closure_size = 0
    largest_closure_seed: list[int] | None = None
    for size in range(1, min(limit, n) + 1):
        for seed in combinations(range(n), size):
            checked += 1
            closed = _fast_closure(seed, row_masks, n)
            if len(closed) > largest_closure_size:
                largest_closure_size = len(closed)
                largest_closure_seed = list(seed)
            if len(closed) == n:
                return {
                    "rank_leq_limit": True,
                    "checked_seed_count": checked,
                    "largest_closure_size": len(closed),
                    "largest_closure_seed": list(seed),
                    "generating_seed": list(seed),
                }
    return {
        "rank_leq_limit": False,
        "checked_seed_count": checked,
        "largest_closure_size": largest_closure_size,
        "largest_closure_seed": largest_closure_seed,
        "generating_seed": None,
    }


def _audit_json(audit: BootstrapCoreAudit) -> dict[str, object]:
    deletion_summaries = []
    for deletion in audit.deletion_closures:
        private_pair_count = sum(
            rich_slice.private_pair_count
            for rich_slice in deletion.rich_class_slices
        )
        deletion_summaries.append(
            {
                "core_vertex": deletion.core_vertex,
                "deletion_seed": deletion.seed,
                "closure_size": len(deletion.closure),
                "core_vertex_not_generated": deletion.core_vertex_not_generated,
                "private_halo": deletion.private_halo,
                "private_halo_size": len(deletion.private_halo),
                "private_pair_count": private_pair_count,
                "rich_class_private_slices": [
                    {
                        "rich_class_index": rich_slice.rich_class_index,
                        "intersection_with_deletion_closure": (
                            rich_slice.intersection_with_deletion_closure
                        ),
                        "private_halo_witnesses": rich_slice.private_halo_witnesses,
                        "private_pair_count": rich_slice.private_pair_count,
                    }
                    for rich_slice in deletion.rich_class_slices
                ],
            }
        )

    return {
        "core": audit.core,
        "core_size": len(audit.core),
        "outside_size": len(audit.outside),
        "outside": audit.outside,
        "core_generates_all": audit.core_generates_all,
        "inclusion_minimal": audit.inclusion_minimal,
        "private_halo_requirement_ok": audit.private_halo_requirement_ok,
        "private_pair_lower_bound": audit.private_pair_lower_bound,
        "private_pair_count": audit.private_pair_count,
        "cyclic_capacity_sum": audit.cyclic_capacity_sum,
        "capacity_margin": audit.cyclic_capacity_sum - audit.private_pair_count,
        "lower_bound_capacity_margin": (
            audit.cyclic_capacity_sum - audit.private_pair_lower_bound
        ),
        "lower_bound_capacity_ok": audit.lower_bound_capacity_ok,
        "weighted_capacity_ok": audit.weighted_capacity_ok,
        "outside_runs": audit.outside_runs,
        "outside_run_lengths": [len(run) for run in audit.outside_runs],
        "deletion_closures": deletion_summaries,
    }


def search_first_minimum_generator(
    rich_classes: RichClasses,
    max_size: int | None = None,
) -> dict[str, object]:
    """Return the first generator after exhausting all smaller seed sizes."""

    validate_full_rich_classes(rich_classes)
    n = len(rich_classes)
    row_masks = _row_masks(rich_classes)
    if max_size is None:
        max_size = n

    checked = 0
    largest_closure_size = 0
    largest_closure_seed: list[int] | None = None
    for size in range(1, min(max_size, n) + 1):
        for seed in combinations(range(n), size):
            checked += 1
            closed = _fast_closure(seed, row_masks, n)
            if len(closed) > largest_closure_size:
                largest_closure_size = len(closed)
                largest_closure_seed = list(seed)
            if len(closed) == n:
                result = closure(seed, rich_classes)
                return {
                    "found": True,
                    "minimum_rank": size,
                    "first_generator": list(seed),
                    "checked_seed_count": checked,
                    "largest_closure_size_before_stop": largest_closure_size,
                    "largest_closure_seed_before_stop": largest_closure_seed,
                    "generating_closure": _closure_json(result),
                }

    return {
        "found": False,
        "minimum_rank": None,
        "first_generator": None,
        "checked_seed_count": checked,
        "largest_closure_size_before_stop": largest_closure_size,
        "largest_closure_seed_before_stop": largest_closure_seed,
        "generating_closure": None,
    }


def _pattern_status(pattern: PatternInfo) -> dict[str, object]:
    return {
        "family": pattern.family,
        "formula": pattern.formula,
        "status": pattern.status,
        "trust": pattern.trust,
        "lifecycle": pattern.lifecycle,
    }


def _bridge_frontier_n9_records() -> list[dict[str, object]]:
    """Return selected n=9 non-ear records from the bridge-frontier artifact."""

    payload = json.loads(BRIDGE_LEMMA_FRONTIER_ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AssertionError("bridge-lemma frontier artifact must be a JSON object")
    targets = payload.get("proof_mining_targets")
    if not isinstance(targets, list):
        raise AssertionError("bridge-lemma frontier artifact has no proof_mining_targets")
    by_id: dict[int, dict[str, object]] = {}
    for target in targets:
        if not isinstance(target, dict) or int(target.get("n", -1)) != 9:
            continue
        source_record_id = target.get("source_record_id")
        if not isinstance(source_record_id, int):
            continue
        by_id[source_record_id] = target
    missing = [record_id for record_id in N9_NON_EAR_FRONTIER_IDS if record_id not in by_id]
    if missing:
        raise AssertionError(f"missing n=9 bridge-frontier records {missing}")
    return [by_id[record_id] for record_id in N9_NON_EAR_FRONTIER_IDS]


def _analyze_rows(
    *,
    name: str,
    selected_rows: Sequence[Sequence[int]],
    order_label: str,
    order: Sequence[int],
    source: str,
    source_record_id: int | str | None,
    source_status: str,
    pattern_status: dict[str, object] | None = None,
) -> dict[str, object]:
    rich_classes = singleton_rich_classes_from_pattern(selected_rows)
    rank3 = search_rank_limit_summary(rich_classes, limit=3)
    minimum = search_first_minimum_generator(rich_classes)
    if not minimum["found"]:
        raise AssertionError(f"{name} has no generating core")
    core = minimum["first_generator"]
    if not isinstance(core, list):
        raise AssertionError(f"{name} generator core is malformed")
    audit = audit_bootstrap_core(core, rich_classes, order=order)
    return {
        "case_id": f"{name}:{order_label}",
        "pattern": name,
        "source": source,
        "source_record_id": source_record_id,
        "source_status": source_status,
        "order_label": order_label,
        "order": [int(label) for label in order],
        "n": len(selected_rows),
        "selected_rows": [[int(label) for label in row] for row in selected_rows],
        "pattern_status": pattern_status or {},
        "rank_search_limit_3": {
            "rank_leq_limit": rank3["rank_leq_limit"],
            "checked_seed_count": rank3["checked_seed_count"],
            "largest_closure_size": rank3["largest_closure_size"],
            "largest_closure_seed": rank3["largest_closure_seed"],
            "generating_seed": rank3["generating_seed"],
        },
        "minimum_generator": minimum,
        "bootstrap_core_audit": _audit_json(audit),
        "interpretation": (
            "Fixed selected-row singleton-rich diagnostic only. Passing the "
            "bootstrap-core capacity ledger is not a Euclidean realization "
            "certificate."
        ),
    }


def fixed_row_order_cases() -> list[dict[str, object]]:
    """Return bootstrap-core records for current fixed-row motifs."""

    patterns = built_in_patterns()
    rows: list[dict[str, object]] = []

    for name in (
        "C13_sidon_1_2_4_10",
        "C19_skew",
        "C25_sidon_2_5_9_14",
        "C29_sidon_1_3_7_15",
    ):
        pattern = patterns[name]
        source_status = pattern.status or "registered fixed selected-row pattern"
        source = "data/patterns/candidate_patterns.json"
        row_cases = {"natural": list(range(pattern.n))}
        row_cases.update(REGISTERED_ORDER_CASES.get(name, {}))
        for order_label, order in row_cases.items():
            rows.append(
                _analyze_rows(
                    name=name,
                    selected_rows=pattern.S,
                    order_label=order_label,
                    order=order,
                    source=source,
                    source_record_id=name,
                    source_status=source_status,
                    pattern_status=_pattern_status(pattern),
                )
            )

    for record in _bridge_frontier_n9_records():
        selected_rows = record["selected_rows"]
        if not isinstance(selected_rows, list):
            raise AssertionError("n9 selected rows are malformed")
        source_record_id = record["source_record_id"]
        name = f"n9_vertex_circle_assignment_{source_record_id}"
        vertex_status = str(record["vertex_circle_status"])
        rows.append(
            _analyze_rows(
                name=name,
                selected_rows=selected_rows,
                order_label="natural",
                order=list(range(len(selected_rows))),
                source="data/certificates/bridge_lemma_frontier.json",
                source_record_id=source_record_id,
                source_status=f"review-pending vertex-circle {vertex_status}",
                pattern_status={
                    "trust": "REVIEW_PENDING_DIAGNOSTIC",
                    "lifecycle": "n9_vertex_circle_frontier_assignment",
                    "source": record["source"],
                },
            )
        )

    return rows


def base_apex_d3_reference() -> dict[str, object]:
    """Return the existing base-apex D=3 packet summary as a reference row."""

    packet = json.loads(BASE_APEX_D3_ARTIFACT.read_text(encoding="utf-8"))
    if not isinstance(packet, dict):
        raise AssertionError("D=3 base-apex packet must be a JSON object")
    return {
        "source_artifact": "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json",
        "schema": packet["schema"],
        "status": packet["status"],
        "trust": packet["trust"],
        "representative_count": packet["representative_count"],
        "profile_multiset_count": packet["profile_multiset_count"],
        "escape_class_count": packet["escape_class_count"],
        "capacity_deficit": packet["capacity_deficit"],
        "target_capacity_total": packet["target_capacity_total"],
        "realizability_state": packet["realizability_state"],
        "incidence_state": packet["incidence_state"],
        "bootstrap_core_audited": False,
        "reason_not_audited": (
            "The D=3 packet records base-apex profile/capacity ledgers rather "
            "than full selected rows or full rich classes, so it is included "
            "as a capacity-reference packet only."
        ),
    }


def build_crosswalk_payload() -> dict[str, object]:
    """Build the deterministic bootstrap-core frontier crosswalk payload."""

    records = fixed_row_order_cases()
    rank_counts: dict[str, int] = {}
    capacity_obstructions = 0
    for record in records:
        rank = record["minimum_generator"]["minimum_rank"]  # type: ignore[index]
        rank_counts[str(rank)] = rank_counts.get(str(rank), 0) + 1
        audit = record["bootstrap_core_audit"]  # type: ignore[assignment]
        if not isinstance(audit, dict):
            raise AssertionError("bootstrap audit record is malformed")
        if not audit["weighted_capacity_ok"]:
            capacity_obstructions += 1

    unique_patterns = sorted({str(record["pattern"]) for record in records})
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "interpretation_warnings": [
            "The fixed-row records use singleton rich classes, not full geometric rich-class data.",
            "Capacity margins are necessary-condition ledgers only; positive margins do not certify realizability.",
            "The base-apex D=3 packet is referenced but not bootstrap-core audited because it is not a full selected-row object.",
            "No general proof and no counterexample are claimed.",
        ],
        "summary": {
            "unique_selected_patterns": len(unique_patterns),
            "unique_selected_pattern_names": unique_patterns,
            "order_case_count": len(records),
            "rank_gt_3_order_cases": sum(
                1
                for record in records
                if not record["rank_search_limit_3"]["rank_leq_limit"]  # type: ignore[index]
            ),
            "minimum_rank_counts": dict(sorted(rank_counts.items())),
            "weighted_capacity_obstruction_count": capacity_obstructions,
            "weighted_capacity_survivor_count": len(records) - capacity_obstructions,
        },
        "records": records,
        "base_apex_d3_reference": base_apex_d3_reference(),
        "provenance": {
            "generator": "scripts/check_bootstrap_core_crosswalk.py",
            "command": (
                "python scripts/check_bootstrap_core_crosswalk.py "
                "--write --assert-expected"
            ),
            "sources": [
                "data/patterns/candidate_patterns.json",
                "data/certificates/bridge_lemma_frontier.json",
                "data/certificates/n9_base_apex_d3_incidence_capacity_packet.json",
            ],
        },
    }
    assert_expected_payload(payload)
    return payload


def assert_expected_payload(payload: dict[str, object]) -> None:
    """Assert the current expected crosswalk counts and guardrails."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError("unexpected bootstrap-core crosswalk schema")
    if payload.get("status") != STATUS:
        raise AssertionError("unexpected bootstrap-core crosswalk status")

    summary = payload.get("summary")
    if not isinstance(summary, dict):
        raise AssertionError("summary must be a mapping")
    expected_summary = {
        "unique_selected_patterns": 6,
        "order_case_count": 8,
        "rank_gt_3_order_cases": 8,
        "minimum_rank_counts": {"4": 4, "5": 3, "6": 1},
        "weighted_capacity_obstruction_count": 0,
        "weighted_capacity_survivor_count": 8,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(f"summary {key} is {summary.get(key)!r}, expected {expected!r}")

    records = payload.get("records")
    if not isinstance(records, list):
        raise AssertionError("records must be a list")
    by_case = {record["case_id"]: record for record in records}
    expected_cases = {
        "C13_sidon_1_2_4_10:natural": (4, 6, 36),
        "C13_sidon_1_2_4_10:sample_full_filter_survivor": (4, 6, 56),
        "C19_skew:natural": (5, 19, 134),
        "C19_skew:vertex_circle_survivor": (5, 19, 156),
        "C25_sidon_2_5_9_14:natural": (6, 30, 221),
        "C29_sidon_1_3_7_15:natural": (5, 21, 494),
        "n9_vertex_circle_assignment_81:natural": (4, 6, 14),
        "n9_vertex_circle_assignment_151:natural": (4, 8, 14),
    }
    if set(by_case) != set(expected_cases):
        raise AssertionError("unexpected crosswalk case set")
    for case_id, (rank, private_pairs, capacity) in expected_cases.items():
        record = by_case[case_id]
        rank3 = record["rank_search_limit_3"]
        minimum = record["minimum_generator"]
        audit = record["bootstrap_core_audit"]
        if rank3["rank_leq_limit"]:
            raise AssertionError(f"{case_id} unexpectedly has rank <= 3")
        if minimum["minimum_rank"] != rank:
            raise AssertionError(f"{case_id} minimum rank changed")
        if audit["private_pair_count"] != private_pairs:
            raise AssertionError(f"{case_id} private pair count changed")
        if audit["cyclic_capacity_sum"] != capacity:
            raise AssertionError(f"{case_id} cyclic capacity changed")
        if not audit["weighted_capacity_ok"]:
            raise AssertionError(f"{case_id} should pass weighted capacity")

    base_apex = payload.get("base_apex_d3_reference")
    if not isinstance(base_apex, dict):
        raise AssertionError("base-apex reference must be a mapping")
    if base_apex.get("representative_count") != 88:
        raise AssertionError("unexpected D=3 base-apex representative count")
    if base_apex.get("bootstrap_core_audited") is not False:
        raise AssertionError("base-apex D=3 packet should be reference-only")
