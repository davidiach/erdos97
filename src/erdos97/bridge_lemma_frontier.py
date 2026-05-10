"""Bridge Lemma A' frontier diagnostics.

This module regenerates small finite ear-orderability diagnostics used for the
Bridge Lemma A' / key-peeling program.  It is a research diagnostic only: it
does not prove the bridge, does not prove Erdos Problem #97, and does not claim
a counterexample.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence

from erdos97 import n9_vertex_circle_exhaustive as n9
from erdos97.fragile_hypergraph import rows_from_zero_one_matrix
from erdos97.search import PatternInfo, result_to_json, search_pattern
from erdos97.stuck_sets import ForwardEarOrderResult, forward_ear_order


SCHEMA = "erdos97.bridge_lemma_frontier.v1"
STATUS = "BRIDGE_LEMMA_FRONTIER_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Finite n=8/n=9 ear-orderability and obstruction cross-tab for Bridge "
    "Lemma A' proof mining; not a proof of the bridge, not a proof of Erdos "
    "Problem #97, not a counterexample, and not an official/global status "
    "update."
)
DEFAULT_SOURCE_N8 = "data/incidence/n8_reconstructed_15_survivors.json"
DEFAULT_SOURCE_N9 = "src/erdos97/n9_vertex_circle_exhaustive.py"

EXPECTED_N8_TOTAL = 15
EXPECTED_N8_EAR = 11
EXPECTED_N8_NON_EAR_IDS = [0, 1, 2, 3]
EXPECTED_N9_TOTAL = 184
EXPECTED_N9_EAR = 182
EXPECTED_N9_NON_EAR_INDICES = [81, 151]
EXPECTED_N9_STATUS_COUNTS = {"self_edge": 158, "strict_cycle": 26}
EXPECTED_CROSS_TAB = {
    "ear|ok": 0,
    "ear|self_edge": 158,
    "ear|strict_cycle": 24,
    "non_ear|ok": 0,
    "non_ear|self_edge": 0,
    "non_ear|strict_cycle": 2,
}


Pattern = list[list[int]]


@dataclass(frozen=True)
class GeometryConfig:
    """Configuration for optional numerical smoke probes."""

    run: bool = False
    mode: str = "polar"
    optimizer: str = "slsqp"
    restarts: int = 3
    seed: int = 0
    max_nfev: int = 1000
    margin: float = 1e-3


def _ear_json(result: ForwardEarOrderResult) -> dict[str, object]:
    return {
        "exists": result.exists,
        "seed": result.seed,
        "order": result.order,
        "largest_closure_size": result.largest_closure_size,
        "largest_closure_seed": result.largest_closure_seed,
        "largest_closure": result.largest_closure,
    }


def _short_ear_json(result: ForwardEarOrderResult) -> dict[str, object]:
    return {
        "exists": result.exists,
        "seed": result.seed,
        "order": result.order,
        "largest_closure_size": result.largest_closure_size,
    }


def _n8_selected_rows(record: Mapping[str, object]) -> Pattern:
    rows = record.get("rows")
    if not isinstance(rows, list):
        raise ValueError("n=8 survivor record is missing rows")
    matrix = [[int(value) for value in row] for row in rows]
    converted = rows_from_zero_one_matrix(matrix)
    return [converted[center] for center in range(len(converted))]


def _n9_assignment_rows(assign: n9.Assignment) -> Pattern:
    return [list(n9.MASK_BITS[assign[center]]) for center in range(n9.N)]


def collect_n9_frontier_assignments() -> list[tuple[int, Pattern, str]]:
    """Return full n=9 assignments before vertex-circle pruning.

    The traversal mirrors ``exhaustive_search(use_vertex_circle=False)`` so the
    assignment indices are stable against the checked n=9 review artifact.
    """

    assignments: list[tuple[int, Pattern, str]] = []

    def search(
        assign: n9.Assignment,
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        if len(assign) == n9.N:
            rows = _n9_assignment_rows(assign)
            status = n9.vertex_circle_status(assign)
            assignments.append((len(assignments), rows, status))
            return

        best_center = None
        best_options = None
        for center in range(n9.N):
            if center in assign:
                continue
            opts = n9.valid_options_for_center(
                center,
                assign,
                column_counts,
                witness_pair_counts,
            )
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return

        center = best_center
        assert center is not None
        for row_mask in best_options:
            assign[center] = row_mask
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] += 1
            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] += 1

            search(assign, column_counts, witness_pair_counts)

            for pair_index in n9.ROW_PAIR_INDICES[row_mask]:
                witness_pair_counts[pair_index] -= 1
            for target in n9.MASK_BITS[row_mask]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in n9.OPTIONS[0]:
        assign: n9.Assignment = {0: row0}
        column_counts = [0] * n9.N
        witness_pair_counts = [0] * len(n9.PAIRS)
        for target in n9.MASK_BITS[row0]:
            column_counts[target] += 1
        for pair_index in n9.ROW_PAIR_INDICES[row0]:
            witness_pair_counts[pair_index] += 1
        if n9.vertex_circle_status(assign) == "ok":
            search(assign, column_counts, witness_pair_counts)

    return assignments


def circulant_offsets(rows: Pattern) -> list[int] | None:
    """Return common row offsets when a selected pattern is circulant."""

    n = len(rows)
    offsets = sorted((target - 0) % n for target in rows[0])
    for center, row in enumerate(rows):
        if sorted((target - center) % n for target in row) != offsets:
            return None
    return offsets


def _geometry_payload_for_target(
    target: Mapping[str, object],
    config: GeometryConfig,
) -> dict[str, object]:
    rows = target.get("selected_rows")
    if not isinstance(rows, list):
        return {"status": "SKIPPED_NO_SELECTED_ROWS", "success": False}
    pattern = PatternInfo(
        name=str(target["target_id"]),
        n=int(target["n"]),
        S=[[int(label) for label in row] for row in rows],
        family="bridge-frontier",
        formula="non-ear proof-mining target",
        notes="numerical smoke probe only",
    )
    try:
        result = search_pattern(
            pattern,
            mode=config.mode,
            restarts=config.restarts,
            seed=config.seed,
            max_nfev=config.max_nfev,
            optimizer=config.optimizer,
            margin=config.margin,
        )
    except RuntimeError as exc:
        return {
            "target_id": target["target_id"],
            "status": "OPTIMIZER_FAILED",
            "success": False,
            "message": str(exc),
            "interpretation": (
                "Numerical optimizer failure is not an exact obstruction or a "
                "counterexample."
            ),
        }

    data = result_to_json(result)
    keys = [
        "pattern_name",
        "n",
        "mode",
        "loss",
        "eq_rms",
        "max_spread",
        "max_rel_spread",
        "convexity_margin",
        "min_edge_length",
        "min_pair_distance",
        "success",
        "elapsed_sec",
    ]
    return {
        "target_id": target["target_id"],
        "status": "RAN",
        **{key: data[key] for key in keys},
        "interpretation": (
            "NUMERICAL_EVIDENCE only. A low residual is not a counterexample "
            "without exact or interval certificates."
        ),
    }


def _geometry_section(
    targets: Sequence[Mapping[str, object]],
    config: GeometryConfig,
) -> dict[str, object]:
    if not config.run:
        return {
            "status": "NOT_RUN",
            "interpretation": (
                "Run scripts/check_bridge_lemma_frontier.py --run-geometry "
                "for optional numerical smoke probes. Numerical output is "
                "evidence only."
            ),
        }
    return {
        "status": "RAN",
        "config": {
            "mode": config.mode,
            "optimizer": config.optimizer,
            "restarts": config.restarts,
            "seed": config.seed,
            "max_nfev": config.max_nfev,
            "margin": config.margin,
        },
        "records": [_geometry_payload_for_target(target, config) for target in targets],
        "interpretation": "NUMERICAL_EVIDENCE only.",
    }


def build_payload(
    n8_survivors: Sequence[Mapping[str, object]],
    n8_exact_obstructions: Mapping[int, Sequence[Mapping[str, object]]],
    geometry_config: GeometryConfig | None = None,
) -> dict[str, object]:
    """Build a deterministic Bridge Lemma A' frontier payload."""

    geometry_config = geometry_config or GeometryConfig()

    n8_records: list[dict[str, object]] = []
    proof_targets: list[dict[str, object]] = []
    for raw_record in n8_survivors:
        class_id = int(raw_record["id"])
        rows = _n8_selected_rows(raw_record)
        ear = forward_ear_order(rows)
        obstructions = list(n8_exact_obstructions.get(class_id, []))
        record = {
            "id": class_id,
            "n": 8,
            "ear_orderable": ear.exists,
            "ear_order": _short_ear_json(ear),
            "exact_obstructions": obstructions,
        }
        n8_records.append(record)
        if not ear.exists:
            proof_targets.append(
                {
                    "target_id": f"n8-class-{class_id}",
                    "n": 8,
                    "source": DEFAULT_SOURCE_N8,
                    "source_record_id": class_id,
                    "selected_rows": rows,
                    "ear_order": _ear_json(ear),
                    "exact_obstructions": obstructions,
                    "why": (
                        "Non-ear-orderable n=8 selected-witness survivor; "
                        "small fixed-selection stuck target for Bridge Lemma "
                        "A' proof mining."
                    ),
                }
            )

    n8_ear_count = sum(1 for record in n8_records if record["ear_orderable"])
    n8_non_ear_ids = [
        int(record["id"]) for record in n8_records if not record["ear_orderable"]
    ]

    n9_assignments = collect_n9_frontier_assignments()
    n9_records: list[dict[str, object]] = []
    n9_status_counts: Counter[str] = Counter()
    cross_tab: Counter[str] = Counter()
    for index, rows, status in n9_assignments:
        ear = forward_ear_order(rows)
        label = "ear" if ear.exists else "non_ear"
        n9_status_counts[status] += 1
        cross_tab[f"{label}|{status}"] += 1
        offsets = circulant_offsets(rows)
        record: dict[str, object] = {
            "assignment_index": index,
            "n": 9,
            "ear_orderable": ear.exists,
            "vertex_circle_status": status,
        }
        if not ear.exists and offsets is not None:
            record["circulant_offsets"] = offsets
        n9_records.append(record)
        if not ear.exists:
            proof_targets.append(
                {
                    "target_id": f"n9-assignment-{index}",
                    "n": 9,
                    "source": DEFAULT_SOURCE_N9,
                    "source_record_id": index,
                    "selected_rows": rows,
                    "ear_order": _ear_json(ear),
                    "vertex_circle_status": status,
                    "circulant_offsets": offsets,
                    "exact_obstructions": [
                        {
                            "method": f"vertex_circle_{status}",
                            "status": "EXACT_OBSTRUCTION_REVIEW_PENDING",
                            "scope": "n=9 selected-witness assignment in the review-pending checker",
                        }
                    ],
                    "why": (
                        "Non-ear-orderable n=9 selected-witness frontier "
                        "assignment; killed by the review-pending exact "
                        "vertex-circle obstruction and useful as an edge-case "
                        "target for Bridge Lemma A' proof mining."
                    ),
                }
            )

    n9_ear_count = sum(1 for record in n9_records if record["ear_orderable"])
    n9_non_ear_indices = [
        int(record["assignment_index"])
        for record in n9_records
        if not record["ear_orderable"]
    ]
    cross_tab_payload = {
        key: cross_tab.get(key, 0)
        for key in [
            "ear|self_edge",
            "ear|strict_cycle",
            "ear|ok",
            "non_ear|self_edge",
            "non_ear|strict_cycle",
            "non_ear|ok",
        ]
    }

    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "bridge_lemma_a_prime_status": "OPEN_NOT_PROVED_OR_REFUTED",
        "interpretation_warnings": [
            "All results are finite-frontier diagnostics, not a proof of Bridge Lemma A'.",
            "The n=9 vertex-circle obstruction remains review-pending.",
            "Numerical geometry probes, when enabled, are evidence only.",
            "No general proof and no counterexample are claimed.",
        ],
        "summary": {
            "n8_total": len(n8_records),
            "n8_ear_orderable": n8_ear_count,
            "n8_non_ear_orderable": len(n8_records) - n8_ear_count,
            "n8_non_ear_ids": n8_non_ear_ids,
            "n9_total": len(n9_records),
            "n9_ear_orderable": n9_ear_count,
            "n9_non_ear_orderable": len(n9_records) - n9_ear_count,
            "n9_non_ear_indices": n9_non_ear_indices,
            "n9_vertex_circle_status_counts": dict(sorted(n9_status_counts.items())),
            "n9_cross_tabulation": cross_tab_payload,
            "proof_mining_target_count": len(proof_targets),
        },
        "n8": {
            "source": DEFAULT_SOURCE_N8,
            "records": n8_records,
        },
        "n9": {
            "source": DEFAULT_SOURCE_N9,
            "records": n9_records,
        },
        "proof_mining_targets": proof_targets,
        "geometry": _geometry_section(proof_targets, geometry_config),
        "provenance": {
            "generator": "scripts/check_bridge_lemma_frontier.py",
            "command": "python scripts/check_bridge_lemma_frontier.py --write --assert-expected",
            "sources": [
                DEFAULT_SOURCE_N8,
                "scripts/analyze_n8_exact_survivors.py",
                DEFAULT_SOURCE_N9,
                "src/erdos97/stuck_sets.py",
            ],
        },
    }


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert stable frontier counts used by the checked artifact."""

    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"unexpected status: {payload.get('status')!r}")
    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("payload summary is missing or malformed")

    expected = {
        "n8_total": EXPECTED_N8_TOTAL,
        "n8_ear_orderable": EXPECTED_N8_EAR,
        "n8_non_ear_orderable": EXPECTED_N8_TOTAL - EXPECTED_N8_EAR,
        "n8_non_ear_ids": EXPECTED_N8_NON_EAR_IDS,
        "n9_total": EXPECTED_N9_TOTAL,
        "n9_ear_orderable": EXPECTED_N9_EAR,
        "n9_non_ear_orderable": EXPECTED_N9_TOTAL - EXPECTED_N9_EAR,
        "n9_non_ear_indices": EXPECTED_N9_NON_EAR_INDICES,
        "n9_vertex_circle_status_counts": EXPECTED_N9_STATUS_COUNTS,
        "n9_cross_tabulation": EXPECTED_CROSS_TAB,
        "proof_mining_target_count": 6,
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise AssertionError(f"summary {key!r} is {summary.get(key)!r}, expected {value!r}")

    targets = payload.get("proof_mining_targets")
    if not isinstance(targets, list) or len(targets) != 6:
        raise AssertionError("expected exactly six proof-mining targets")
    for target in targets:
        if not isinstance(target, Mapping):
            raise AssertionError("proof-mining target is malformed")
        if target.get("exact_obstructions") in (None, []):
            raise AssertionError(f"target lacks obstruction status: {target.get('target_id')!r}")
