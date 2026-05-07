#!/usr/bin/env python3
"""Analyze clause templates in the checked C19 all-order Z3 certificate.

This diagnostic replays the stored C19_skew all-order Kalmanson SMT
certificate, then summarizes the exact forbidden ordered-quadrilateral clauses
by translation families, modular step patterns, kind pairs, label overlap, and
label frequencies.

It is a structural diagnostic for one already-checked fixed abstract selected
witness pattern. It does not prove Erdos Problem #97.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from check_kalmanson_certificate import build_distance_classes  # noqa: E402
from check_kalmanson_two_order_search import KINDS, _sparse_vector  # noqa: E402
from check_kalmanson_two_order_z3 import (  # noqa: E402
    Clause,
    Quad,
    _clause_key,
    _json_clause,
    _parse_clause,
    _prepare_vector_tables,
    verify_certificate,
)


DEFAULT_CERTIFICATE = ROOT / "data" / "certificates" / "c19_skew_all_orders_kalmanson_z3.json"
DEFAULT_ARTIFACT = ROOT / "reports" / "c19_kalmanson_z3_clause_diagnostics.json"
DEFAULT_COMMAND = (
    "python scripts/analyze_kalmanson_z3_clauses.py --assert-expected "
    "--out reports/c19_kalmanson_z3_clause_diagnostics.json"
)
EXPECTED_TYPE = "c19_kalmanson_z3_clause_diagnostics_v1"
EXPECTED_STATUS = "ALL_ORDER_C19_Z3_CLAUSE_DIAGNOSTIC_ONLY"
EXPECTED_TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"


def relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def quad_steps(quad: Quad, n: int) -> tuple[int, int, int, int]:
    """Return ordered modular label steps around a quadrilateral."""

    return tuple((quad[(idx + 1) % 4] - quad[idx]) % n for idx in range(4))  # type: ignore[return-value]


def shift_quad(quad: Quad, shift: int, n: int) -> Quad:
    return tuple((label + shift) % n for label in quad)  # type: ignore[return-value]


def translation_family(clause: Clause, n: int) -> Clause:
    """Canonicalize a clause under simultaneous cyclic label translation."""

    return min(
        _clause_key(shift_quad(clause[0], shift, n), shift_quad(clause[1], shift, n))
        for shift in range(n)
    )


def clause_step_signature(clause: Clause, n: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    return tuple(sorted((quad_steps(clause[0], n), quad_steps(clause[1], n))))  # type: ignore[return-value]


def inverse_kind_pairs(
    clause: Clause,
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> tuple[tuple[str, str], ...]:
    """Return kind-name pairs that make this clause a valid inverse pair."""

    left_ids = quad_ids[clause[0]]
    right_ids = quad_ids[clause[1]]
    pairs: list[tuple[str, str]] = []
    for left_kind, left_vector_id in enumerate(left_ids):
        for right_kind, right_vector_id in enumerate(right_ids):
            if inverse_id[left_vector_id] == right_vector_id:
                pairs.append((KINDS[left_kind], KINDS[right_kind]))
    return tuple(sorted(pairs))


def inverse_vector_matches(
    clause: Clause,
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> tuple[tuple[int, int], ...]:
    """Return vector-id pairs that justify the clause."""

    left_ids = quad_ids[clause[0]]
    right_ids = quad_ids[clause[1]]
    matches = []
    for left_vector_id in left_ids:
        for right_vector_id in right_ids:
            if inverse_id[left_vector_id] == right_vector_id:
                matches.append((left_vector_id, right_vector_id))
    return tuple(sorted(matches))


def inverse_vector_match_details(
    clause: Clause,
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
) -> tuple[tuple[int, int, str, str], ...]:
    """Return vector-id and kind pairs that justify the clause."""

    left_ids = quad_ids[clause[0]]
    right_ids = quad_ids[clause[1]]
    details = []
    for left_kind, left_vector_id in enumerate(left_ids):
        for right_kind, right_vector_id in enumerate(right_ids):
            if inverse_id[left_vector_id] == right_vector_id:
                details.append(
                    (
                        left_vector_id,
                        right_vector_id,
                        KINDS[left_kind],
                        KINDS[right_kind],
                    )
                )
    return tuple(sorted(details))


def clause_literals(clause: Clause) -> list[tuple[int, int]]:
    literals = []
    for quad in clause:
        literals.extend(
            [
                (quad[0], quad[1]),
                (quad[1], quad[2]),
                (quad[2], quad[3]),
            ]
        )
    return literals


def vector_support_sizes(
    n: int,
    offsets: Sequence[int],
    quad_ids: Mapping[Quad, tuple[int, int]],
) -> dict[int, int]:
    """Return sparse support sizes for all vector ids in the quad table."""

    classes = dict(build_distance_classes(n, offsets))
    support_sizes: dict[int, int] = {}
    for quad, ids in quad_ids.items():
        for kind_idx, vector_id in enumerate(ids):
            if vector_id not in support_sizes:
                support_sizes[vector_id] = len(_sparse_vector(classes, KINDS[kind_idx], quad))
    return support_sizes


def distance_quotient_summary(
    n: int,
    offsets: Sequence[int],
    quad_ids: Mapping[Quad, tuple[int, int]],
    inverse_id: Sequence[int],
    used_vector_pairs: set[tuple[int, int]],
) -> dict[str, object]:
    """Return compact counts for the selected-distance quotient vector table."""

    classes = dict(build_distance_classes(n, offsets))
    class_sizes = Counter(classes.values())
    class_size_histogram = Counter(class_sizes.values())
    inverse_pair_count = sum(
        1 for vector_id, inverse in enumerate(inverse_id) if inverse >= 0 and vector_id < inverse
    )
    return {
        "ordered_quad_table_size": len(quad_ids),
        "vector_id_count": len(inverse_id),
        "inverse_vector_pair_count": inverse_pair_count,
        "selected_distance_class_count": len(set(classes.values())),
        "selected_distance_class_size_histogram": {
            str(size): class_size_histogram[size] for size in sorted(class_size_histogram)
        },
        "unique_inverse_vector_pairs_used_by_stored_clauses": len(used_vector_pairs),
        "vector_id_note": (
            "Vector-id counts are deterministic for the current table builder, "
            "but individual ids are not a mathematical invariant."
        ),
    }


def inverse_vector_pair_support_summary(
    vector_pair_clause_counts: Counter[tuple[int, int]],
    pair_kind_patterns: Mapping[tuple[int, int], set[tuple[str, str]]],
    pair_support_size_by_pair: Mapping[tuple[int, int], int],
    pair_support_size_mismatches: set[tuple[int, int]],
    oriented_clause_support_counts: Counter[tuple[int, int]],
    *,
    top: int,
) -> dict[str, object]:
    """Return compact support data for inverse vector pairs used by clauses."""

    unique_support_counts = Counter(pair_support_size_by_pair.values())
    kind_pattern_count_distribution = Counter(
        len(pair_kind_patterns[pair]) for pair in vector_pair_clause_counts
    )
    clause_counts = list(vector_pair_clause_counts.values())
    return {
        "used_inverse_vector_pair_count": len(vector_pair_clause_counts),
        "pair_support_size_mismatch_count": len(pair_support_size_mismatches),
        "unique_pair_support_size_distribution": {
            str(key): unique_support_counts[key] for key in sorted(unique_support_counts)
        },
        "clause_count_by_inverse_vector_pair_support_size": {
            str(key): sum(
                count
                for pair, count in vector_pair_clause_counts.items()
                if pair_support_size_by_pair[pair] == key
            )
            for key in sorted(unique_support_counts)
        },
        "oriented_clause_support_size_distribution": {
            f"{left},{right}": oriented_clause_support_counts[(left, right)]
            for left, right in sorted(oriented_clause_support_counts)
        },
        "clause_count_per_inverse_vector_pair_min": min(clause_counts),
        "clause_count_per_inverse_vector_pair_max": max(clause_counts),
        "kind_pattern_count_per_inverse_vector_pair_distribution": {
            str(key): kind_pattern_count_distribution[key]
            for key in sorted(kind_pattern_count_distribution)
        },
        "top_inverse_vector_pairs_by_clause_count": [
            {
                "inverse_vector_pair": list(pair),
                "clause_count": count,
                "support_size": pair_support_size_by_pair[pair],
                "kind_patterns": [
                    {"left_kind": left, "right_kind": right}
                    for left, right in sorted(pair_kind_patterns[pair])
                ],
            }
            for pair, count in sorted(
                vector_pair_clause_counts.items(),
                key=lambda item: (-item[1], item[0]),
            )[:top]
        ],
        "note": (
            "Vector ids are deterministic for this diagnostic generator, but they are "
            "implementation identifiers rather than mathematical invariants."
        ),
    }


def top_translation_families(
    family_counts: Counter[Clause],
    step_counts: Counter[tuple[tuple[int, ...], tuple[int, ...]]],
    *,
    n: int,
    top: int,
) -> list[dict[str, object]]:
    rows = []
    for family, count in sorted(
        family_counts.items(),
        key=lambda item: (-item[1], _json_clause(item[0])),
    )[:top]:
        step_signature = clause_step_signature(family, n)
        rows.append(
            {
                "canonical_clause": _json_clause(family),
                "count": count,
                "ordered_quad_step_signature": [list(steps) for steps in step_signature],
                "step_signature_count": step_counts[step_signature],
            }
        )
    return rows


def top_quad_steps(
    step_counts: Counter[tuple[int, int, int, int]],
    *,
    top: int,
) -> list[dict[str, object]]:
    return [
        {"ordered_quad_steps": list(steps), "count": count}
        for steps, count in sorted(step_counts.items(), key=lambda item: (-item[1], item[0]))[:top]
    ]


def top_ordered_quads(
    quad_counts: Counter[Quad],
    *,
    top: int,
) -> list[dict[str, object]]:
    return [
        {"ordered_quad": list(quad), "count": count}
        for quad, count in sorted(quad_counts.items(), key=lambda item: (-item[1], item[0]))[:top]
    ]


def diagnostic_payload(
    certificate: Path = DEFAULT_CERTIFICATE,
    *,
    top: int = 12,
) -> dict[str, object]:
    """Return the deterministic C19 Z3 clause diagnostic payload."""

    raw_payload = load_json(certificate)
    verified = verify_certificate(raw_payload)
    pattern = verified["pattern"]
    if not isinstance(pattern, dict):
        raise AssertionError("verified pattern must be an object")
    n = int(pattern["n"])
    offsets = [int(offset) for offset in pattern["circulant_offsets"]]  # type: ignore[index]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    clauses = [_parse_clause(item) for item in raw_payload["forbidden_order_pairs"]]
    if len(set(clauses)) != len(clauses):
        raise AssertionError("duplicate forbidden clauses in source certificate")
    support_sizes = vector_support_sizes(n, offsets, quad_ids)

    family_counts: Counter[Clause] = Counter()
    step_signature_counts: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    quad_step_counts: Counter[tuple[int, int, int, int]] = Counter()
    quad_counts: Counter[Quad] = Counter()
    kind_pair_counts: Counter[tuple[tuple[str, str], ...]] = Counter()
    matches_per_clause_counts: Counter[int] = Counter()
    matched_vector_support_counts: Counter[int] = Counter()
    shared_label_counts: Counter[int] = Counter()
    union_label_counts: Counter[int] = Counter()
    quads_with_label0_counts: Counter[int] = Counter()
    label0_position_counts: Counter[int] = Counter()
    effective_literal_counts: Counter[int] = Counter()
    effective_unique_literal_counts: Counter[int] = Counter()
    raw_unique_literal_counts: Counter[int] = Counter()
    label_occurrences: Counter[int] = Counter()
    label_clause_touches: Counter[int] = Counter()
    used_vector_pairs: set[tuple[int, int]] = set()
    vector_pair_clause_counts: Counter[tuple[int, int]] = Counter()
    vector_pair_kind_patterns: dict[tuple[int, int], set[tuple[str, str]]] = {}
    pair_support_size_by_pair: dict[tuple[int, int], int] = {}
    pair_support_size_mismatches: set[tuple[int, int]] = set()
    oriented_clause_support_counts: Counter[tuple[int, int]] = Counter()

    for clause in clauses:
        family_counts[translation_family(clause, n)] += 1
        step_signature_counts[clause_step_signature(clause, n)] += 1
        match_details = inverse_vector_match_details(clause, quad_ids, inverse_id)
        kind_matches = tuple(
            sorted((left_kind, right_kind) for _, _, left_kind, right_kind in match_details)
        )
        vector_matches = tuple(
            sorted(
                (left_vector_id, right_vector_id)
                for left_vector_id, right_vector_id, _, _ in match_details
            )
        )
        kind_pair_counts[kind_matches] += 1
        matches_per_clause_counts[len(vector_matches)] += 1
        for left_vector_id, right_vector_id, left_kind, right_kind in match_details:
            vector_pair = tuple(sorted((left_vector_id, right_vector_id)))
            left_support_size = support_sizes[left_vector_id]
            right_support_size = support_sizes[right_vector_id]
            used_vector_pairs.add(vector_pair)
            vector_pair_clause_counts[vector_pair] += 1
            vector_pair_kind_patterns.setdefault(vector_pair, set()).add((left_kind, right_kind))
            pair_support_size_by_pair[vector_pair] = left_support_size
            if left_support_size != right_support_size:
                pair_support_size_mismatches.add(vector_pair)
            oriented_clause_support_counts[(left_support_size, right_support_size)] += 1
            matched_vector_support_counts[left_support_size] += 1
        shared_label_counts[len(set(clause[0]) & set(clause[1]))] += 1
        union_label_counts[len(set(clause[0]) | set(clause[1]))] += 1
        quads_with_label0_counts[sum(1 for quad in clause if 0 in quad)] += 1
        for quad in clause:
            for idx, label in enumerate(quad):
                if label == 0:
                    label0_position_counts[idx] += 1
        literals = clause_literals(clause)
        effective_literals = [literal for literal in literals if literal[0] != 0]
        effective_literal_counts[len(effective_literals)] += 1
        effective_unique_literal_counts[len(set(effective_literals))] += 1
        raw_unique_literal_counts[len(set(literals))] += 1
        for quad in clause:
            quad_counts[quad] += 1
            quad_step_counts[quad_steps(quad, n)] += 1
            label_occurrences.update(quad)
        label_clause_touches.update(set(clause[0]) | set(clause[1]))

    label_frequencies = [
        {
            "label": label,
            "ordered_quad_occurrences": label_occurrences[label],
            "clause_touch_count": label_clause_touches[label],
        }
        for label in range(n)
    ]
    return {
        "type": EXPECTED_TYPE,
        "trust": EXPECTED_TRUST,
        "status": EXPECTED_STATUS,
        "claim_scope": (
            "Structural diagnostic for the checked C19_skew all-order Z3 "
            "Kalmanson certificate only; not a proof of Erdos Problem #97."
        ),
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "The source certificate is replayed with Z3 before clause templates are summarized.",
            "Translation families quotient simultaneous cyclic relabeling only; reversal is not quotiented.",
            "Template frequencies are diagnostic search guidance, not a statement about all C19-like patterns.",
        ],
        "source_certificate": {
            "path": relative_path(certificate),
            "type": raw_payload.get("type"),
            "pattern": verified["pattern"],
            "status": verified["status"],
            "trust": verified["trust"],
            "solver_result": verified["solver_result"],
            "smt_solver": raw_payload.get("smt_solver"),
            "iterations": raw_payload.get("iterations"),
            "conflict_cap": raw_payload.get("conflict_cap"),
            "forbidden_clause_count": verified["forbidden_clause_count"],
            "rotation_quotient": raw_payload.get("rotation_quotient"),
            "reversal_quotient": raw_payload.get("reversal_quotient"),
        },
        "clause_validation_summary": {
            "source_forbidden_clause_count": raw_payload.get("forbidden_clause_count"),
            "parsed_clause_count": len(clauses),
            "unique_clause_count": len(set(clauses)),
            "lexicographically_sorted": clauses == sorted(clauses),
            "solver_replay_result": verified["solver_result"],
            "verified_status": verified["status"],
            "verified_trust": verified["trust"],
        },
        "distance_quotient_table_summary": distance_quotient_summary(
            n,
            offsets,
            quad_ids,
            inverse_id,
            used_vector_pairs,
        ),
        "template_summary": {
            "clause_count": len(clauses),
            "translation_family_count": len(family_counts),
            "translation_family_coverage_histogram": {
                str(count): frequency
                for count, frequency in sorted(Counter(family_counts.values()).items())
            },
            "ordered_quad_step_signature_count": len(step_signature_counts),
            "ordered_quad_step_pattern_count": len(quad_step_counts),
            "ordered_quad_count": len(quad_counts),
            "shared_label_count_distribution": {
                str(key): shared_label_counts[key] for key in sorted(shared_label_counts)
            },
            "matches_per_clause_distribution": {
                str(key): matches_per_clause_counts[key] for key in sorted(matches_per_clause_counts)
            },
            "matched_vector_support_size_distribution": {
                str(key): matched_vector_support_counts[key]
                for key in sorted(matched_vector_support_counts)
            },
            "inverse_kind_pair_distribution": [
                {
                    "kind_pairs": [
                        {"left_kind": left, "right_kind": right}
                        for left, right in kind_pairs
                    ],
                    "count": kind_pair_counts[kind_pairs],
                }
                for kind_pairs in sorted(kind_pair_counts)
            ],
            "label_ordered_quad_occurrence_min": min(label_occurrences.values()),
            "label_ordered_quad_occurrence_max": max(label_occurrences.values()),
            "label_clause_touch_min": min(label_clause_touches.values()),
            "label_clause_touch_max": max(label_clause_touches.values()),
        },
        "inverse_vector_pair_support_summary": inverse_vector_pair_support_summary(
            vector_pair_clause_counts,
            vector_pair_kind_patterns,
            pair_support_size_by_pair,
            pair_support_size_mismatches,
            oriented_clause_support_counts,
            top=top,
        ),
        "rotation_quotient_literal_summary": {
            "quads_containing_label0_per_clause": {
                str(key): quads_with_label0_counts[key] for key in sorted(quads_with_label0_counts)
            },
            "label0_positions_inside_ordered_quads": {
                str(key): label0_position_counts[key] for key in sorted(label0_position_counts)
            },
            "label0_non_first_occurrences": sum(
                count for position, count in label0_position_counts.items() if position != 0
            ),
            "effective_literal_count_distribution": {
                str(key): effective_literal_counts[key] for key in sorted(effective_literal_counts)
            },
            "effective_unique_literal_count_distribution": {
                str(key): effective_unique_literal_counts[key]
                for key in sorted(effective_unique_literal_counts)
            },
        },
        "clause_shape_summary": {
            "union_label_count_distribution": {
                str(key): union_label_counts[key] for key in sorted(union_label_counts)
            },
            "left_right_shared_label_count_distribution": {
                str(key): shared_label_counts[key] for key in sorted(shared_label_counts)
            },
            "raw_unique_precedence_literal_count_distribution": {
                str(key): raw_unique_literal_counts[key] for key in sorted(raw_unique_literal_counts)
            },
        },
        "label_frequencies": label_frequencies,
        "top_translation_families": top_translation_families(
            family_counts,
            step_signature_counts,
            n=n,
            top=top,
        ),
        "top_ordered_quad_step_patterns": top_quad_steps(quad_step_counts, top=top),
        "top_ordered_quads": top_ordered_quads(quad_counts, top=top),
        "interpretation_note": (
            "This report makes the stored C19_skew Z3 clause set easier to inspect. "
            "It does not add clauses, search new cyclic orders, or transfer the "
            "obstruction to any other selected-witness pattern."
        ),
        "provenance": {
            "generator": "scripts/analyze_kalmanson_z3_clauses.py",
            "command": DEFAULT_COMMAND,
        },
    }


def assert_expected(payload: Mapping[str, object]) -> None:
    expected_top = {
        "type": EXPECTED_TYPE,
        "trust": EXPECTED_TRUST,
        "status": EXPECTED_STATUS,
        "claim_scope": (
            "Structural diagnostic for the checked C19_skew all-order Z3 "
            "Kalmanson certificate only; not a proof of Erdos Problem #97."
        ),
    }
    for key, expected in expected_top.items():
        if payload.get(key) != expected:
            raise AssertionError(f"{key} is {payload.get(key)!r}, expected {expected!r}")

    source = payload.get("source_certificate")
    if not isinstance(source, Mapping):
        raise AssertionError("source_certificate must be an object")
    expected_source = {
        "path": "data/certificates/c19_skew_all_orders_kalmanson_z3.json",
        "type": "kalmanson_two_order_z3_refinement_v1",
        "status": "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
        "trust": "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
        "solver_result": "unsat",
        "smt_solver": "z3",
        "iterations": 142,
        "conflict_cap": 1024,
        "forbidden_clause_count": 7981,
    }
    for key, expected in expected_source.items():
        if source.get(key) != expected:
            raise AssertionError(
                f"source_certificate[{key!r}] is {source.get(key)!r}, expected {expected!r}"
            )
    if source.get("pattern") != {
        "name": "C19_skew",
        "n": 19,
        "circulant_offsets": [-8, -3, 5, 9],
    }:
        raise AssertionError(f"unexpected source pattern: {source.get('pattern')!r}")

    validation = payload.get("clause_validation_summary")
    if not isinstance(validation, Mapping):
        raise AssertionError("clause_validation_summary must be an object")
    expected_validation = {
        "source_forbidden_clause_count": 7981,
        "parsed_clause_count": 7981,
        "unique_clause_count": 7981,
        "lexicographically_sorted": True,
        "solver_replay_result": "unsat",
        "verified_status": "EXACT_ALL_ORDER_TWO_INEQUALITY_KALMANSON_OBSTRUCTION",
        "verified_trust": "SMT_EXACT_ALL_ORDER_OBSTRUCTION_FOR_FIXED_PATTERN",
    }
    for key, expected in expected_validation.items():
        if validation.get(key) != expected:
            raise AssertionError(
                f"clause_validation_summary[{key!r}] is {validation.get(key)!r}, expected {expected!r}"
            )

    distance_summary = payload.get("distance_quotient_table_summary")
    if not isinstance(distance_summary, Mapping):
        raise AssertionError("distance_quotient_table_summary must be an object")
    expected_distance_summary = {
        "ordered_quad_table_size": 93024,
        "vector_id_count": 22344,
        "inverse_vector_pair_count": 11172,
        "selected_distance_class_count": 114,
        "selected_distance_class_size_histogram": {"1": 95, "4": 19},
        "unique_inverse_vector_pairs_used_by_stored_clauses": 285,
    }
    for key, expected in expected_distance_summary.items():
        if distance_summary.get(key) != expected:
            raise AssertionError(
                f"distance_quotient_table_summary[{key!r}] is {distance_summary.get(key)!r}, "
                f"expected {expected!r}"
            )

    summary = payload.get("template_summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("template_summary must be an object")
    expected_summary = {
        "clause_count": 7981,
        "translation_family_count": 1946,
        "translation_family_coverage_histogram": {
            "1": 198,
            "2": 305,
            "3": 354,
            "4": 358,
            "5": 266,
            "6": 206,
            "7": 109,
            "8": 71,
            "9": 36,
            "10": 22,
            "11": 18,
            "12": 1,
            "14": 2,
        },
        "ordered_quad_step_signature_count": 1946,
        "ordered_quad_step_pattern_count": 576,
        "ordered_quad_count": 7535,
        "shared_label_count_distribution": {"2": 7310, "3": 671},
        "matches_per_clause_distribution": {"1": 7981},
        "matched_vector_support_size_distribution": {"2": 7780, "4": 201},
        "label_ordered_quad_occurrence_min": 1934,
        "label_ordered_quad_occurrence_max": 3964,
        "label_clause_touch_min": 1530,
        "label_clause_touch_max": 2938,
    }
    for key, expected in expected_summary.items():
        if summary.get(key) != expected:
            raise AssertionError(
                f"template_summary[{key!r}] is {summary.get(key)!r}, expected {expected!r}"
            )
    expected_kind_counts = {
        ("K1_diag_gt_sides", "K1_diag_gt_sides"): 1928,
        ("K1_diag_gt_sides", "K2_diag_gt_other"): 2061,
        ("K2_diag_gt_other", "K1_diag_gt_sides"): 2092,
        ("K2_diag_gt_other", "K2_diag_gt_other"): 1900,
    }
    observed_kind_counts: dict[tuple[str, str], int] = {}
    rows = summary.get("inverse_kind_pair_distribution")
    if not isinstance(rows, list):
        raise AssertionError("inverse_kind_pair_distribution must be a list")
    for row in rows:
        if not isinstance(row, Mapping):
            raise AssertionError("inverse kind-pair rows must be objects")
        pairs = row.get("kind_pairs")
        if not isinstance(pairs, list) or len(pairs) != 1 or not isinstance(pairs[0], Mapping):
            raise AssertionError(f"unexpected kind_pairs row: {row!r}")
        pair = pairs[0]
        observed_kind_counts[(str(pair["left_kind"]), str(pair["right_kind"]))] = int(row["count"])
    if observed_kind_counts != expected_kind_counts:
        raise AssertionError(f"unexpected kind-pair distribution: {observed_kind_counts!r}")

    support = payload.get("inverse_vector_pair_support_summary")
    if not isinstance(support, Mapping):
        raise AssertionError("inverse_vector_pair_support_summary must be an object")
    expected_support = {
        "used_inverse_vector_pair_count": 285,
        "pair_support_size_mismatch_count": 0,
        "unique_pair_support_size_distribution": {"2": 266, "4": 19},
        "clause_count_by_inverse_vector_pair_support_size": {"2": 7780, "4": 201},
        "oriented_clause_support_size_distribution": {"2,2": 7780, "4,4": 201},
        "clause_count_per_inverse_vector_pair_min": 4,
        "clause_count_per_inverse_vector_pair_max": 86,
        "kind_pattern_count_per_inverse_vector_pair_distribution": {
            "2": 4,
            "3": 14,
            "4": 267,
        },
    }
    for key, expected in expected_support.items():
        if support.get(key) != expected:
            raise AssertionError(
                f"inverse_vector_pair_support_summary[{key!r}] is {support.get(key)!r}, "
                f"expected {expected!r}"
            )
    top_pairs = support.get("top_inverse_vector_pairs_by_clause_count")
    if not isinstance(top_pairs, list) or not top_pairs:
        raise AssertionError("top inverse-vector-pair rows changed")
    first_pair = top_pairs[0]
    if not isinstance(first_pair, Mapping):
        raise AssertionError("top inverse-vector-pair rows must be objects")
    expected_first_pair = {
        "inverse_vector_pair": [7001, 7037],
        "clause_count": 86,
        "support_size": 2,
    }
    for key, expected in expected_first_pair.items():
        if first_pair.get(key) != expected:
            raise AssertionError(
                f"top_inverse_vector_pairs_by_clause_count[0][{key!r}] is "
                f"{first_pair.get(key)!r}, expected {expected!r}"
            )

    rotation = payload.get("rotation_quotient_literal_summary")
    if not isinstance(rotation, Mapping):
        raise AssertionError("rotation_quotient_literal_summary must be an object")
    expected_rotation = {
        "quads_containing_label0_per_clause": {"0": 6451, "1": 1126, "2": 404},
        "label0_positions_inside_ordered_quads": {"0": 1934},
        "label0_non_first_occurrences": 0,
        "effective_literal_count_distribution": {"4": 404, "5": 1126, "6": 6451},
        "effective_unique_literal_count_distribution": {
            "3": 15,
            "4": 466,
            "5": 1734,
            "6": 5766,
        },
    }
    for key, expected in expected_rotation.items():
        if rotation.get(key) != expected:
            raise AssertionError(
                f"rotation_quotient_literal_summary[{key!r}] is {rotation.get(key)!r}, "
                f"expected {expected!r}"
            )

    shape = payload.get("clause_shape_summary")
    if not isinstance(shape, Mapping):
        raise AssertionError("clause_shape_summary must be an object")
    expected_shape = {
        "union_label_count_distribution": {"5": 671, "6": 7310},
        "left_right_shared_label_count_distribution": {"2": 7310, "3": 671},
        "raw_unique_precedence_literal_count_distribution": {"5": 799, "6": 7182},
    }
    for key, expected in expected_shape.items():
        if shape.get(key) != expected:
            raise AssertionError(
                f"clause_shape_summary[{key!r}] is {shape.get(key)!r}, expected {expected!r}"
            )

    provenance = payload.get("provenance")
    if not isinstance(provenance, Mapping) or provenance.get("command") != DEFAULT_COMMAND:
        raise AssertionError("provenance command changed")
    notes = payload.get("notes")
    if not isinstance(notes, list) or "No general proof of Erdos Problem #97 is claimed." not in notes:
        raise AssertionError("nonclaiming notes changed")


def check_artifact(path: Path, payload: Mapping[str, object]) -> None:
    artifact = load_json(path)
    if artifact != payload:
        raise AssertionError(f"{relative_path(path)} does not match regenerated diagnostic payload")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--out", type=Path, help="write generated JSON to this path")
    parser.add_argument("--check-artifact", type=Path, help="compare generated JSON to this stored artifact")
    parser.add_argument("--top", type=int, default=12, help="number of top diagnostic rows to retain")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top <= 0:
        raise SystemExit("--top must be positive")
    certificate = args.certificate if args.certificate.is_absolute() else ROOT / args.certificate
    payload = diagnostic_payload(certificate, top=args.top)
    if args.assert_expected:
        assert_expected(payload)
    if args.check_artifact:
        artifact = args.check_artifact if args.check_artifact.is_absolute() else ROOT / args.check_artifact
        check_artifact(artifact, payload)
    if args.out:
        out = args.out if args.out.is_absolute() else ROOT / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        summary = payload["template_summary"]  # type: ignore[index]
        print("C19 Z3 clause-template diagnostic")
        print(f"clauses: {summary['clause_count']}")  # type: ignore[index]
        print(f"translation families: {summary['translation_family_count']}")  # type: ignore[index]
        print(f"ordered quad step patterns: {summary['ordered_quad_step_pattern_count']}")  # type: ignore[index]
        if args.assert_expected:
            print("OK: C19 Z3 clause-template diagnostic matches expected values")
        if args.check_artifact:
            print(f"OK: {relative_path(args.check_artifact)} matches regenerated payload")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
