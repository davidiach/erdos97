#!/usr/bin/env python3
"""Classify inverse-pair coefficient templates for C13 and C19 Kalmanson pilots."""

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
from check_kalmanson_two_order_search import (  # noqa: E402
    KINDS,
    _prepare_vector_tables,
    _sparse_vector,
    assert_c13_expected,
)
from check_kalmanson_two_order_z3 import verify_certificate  # noqa: E402
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.kalmanson_inverse_pair_templates.v1"
STATUS = "KALMANSON_INVERSE_PAIR_TEMPLATE_DIAGNOSTIC"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Coefficient-template diagnostic for the checked all-order C13_sidon and "
    "C19_skew Kalmanson inverse-pair pilots. It classifies quotient-vector "
    "inverse pairs available to those fixed abstract selected-witness patterns. "
    "It does not search new cyclic orders, does not prove Erdos Problem #97, "
    "does not claim a counterexample, and does not transfer the obstruction to "
    "other patterns."
)
PROVENANCE = {
    "generator": "scripts/analyze_kalmanson_inverse_pair_templates.py",
    "command": (
        "python scripts/analyze_kalmanson_inverse_pair_templates.py "
        "--assert-expected --json"
    ),
}

DEFAULT_C13 = ROOT / "data" / "certificates" / "c13_sidon_all_orders_kalmanson_two_search.json"
DEFAULT_C19 = ROOT / "data" / "certificates" / "c19_skew_all_orders_kalmanson_z3.json"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def diagnostic_payload(
    *,
    c13_artifact: Path = DEFAULT_C13,
    c19_artifact: Path = DEFAULT_C19,
    top: int = 6,
) -> dict[str, Any]:
    """Return a deterministic C13/C19 inverse-pair template diagnostic."""

    c13 = load_json(c13_artifact)
    if not isinstance(c13, dict):
        raise TypeError("C13 artifact must be a JSON object")
    assert_c13_expected(c13)
    c19_raw = load_json(c19_artifact)
    if not isinstance(c19_raw, dict):
        raise TypeError("C19 artifact must be a JSON object")
    c19_verified = verify_certificate(c19_raw)

    summaries = [
        pattern_template_summary(c13["pattern"], top=top),
        pattern_template_summary(c19_verified["pattern"], top=top),
    ]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifacts": [
            {
                "path": display_path(c13_artifact, ROOT),
                "type": c13.get("type"),
                "status": c13.get("status"),
                "trust": c13.get("trust"),
                "pattern": c13.get("pattern"),
                "nodes_visited": c13.get("nodes_visited"),
                "branches_pruned_by_completed_two_certificate": c13.get(
                    "branches_pruned_by_completed_two_certificate"
                ),
            },
            {
                "path": display_path(c19_artifact, ROOT),
                "type": c19_raw.get("type"),
                "status": c19_verified.get("status"),
                "trust": c19_verified.get("trust"),
                "pattern": c19_verified.get("pattern"),
                "solver_result": c19_verified.get("solver_result"),
                "forbidden_clause_count": c19_verified.get("forbidden_clause_count"),
            },
        ],
        "pattern_summaries": summaries,
        "cross_pattern_summary": cross_pattern_summary(summaries),
        "interpretation": (
            "Both fixed-pattern pilots use the same two quotient coefficient "
            "template shapes: a one-class-vs-one-class cancellation and a "
            "two-classes-vs-two-classes cancellation. Counts are table "
            "diagnostics for these fixed selected-witness patterns only."
        ),
        "provenance": dict(PROVENANCE),
    }


def pattern_template_summary(pattern: Mapping[str, Any], *, top: int) -> dict[str, Any]:
    """Summarize quotient-vector inverse-pair templates for one pattern."""

    name = str(pattern["name"])
    n = int(pattern["n"])
    offsets = [int(offset) for offset in pattern["circulant_offsets"]]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    classes = dict(build_distance_classes(n, offsets))

    vector_by_id: dict[int, tuple[tuple[int, int], ...]] = {}
    vector_occurrences: Counter[int] = Counter()
    kind_occurrences: dict[int, Counter[str]] = {}
    for quad, vector_ids in quad_ids.items():
        for kind_index, vector_id in enumerate(vector_ids):
            kind = KINDS[kind_index]
            vector_occurrences[vector_id] += 1
            kind_occurrences.setdefault(vector_id, Counter())[kind] += 1
            if vector_id not in vector_by_id:
                vector_by_id[vector_id] = _sparse_vector(classes, kind, quad)

    inverse_pair_count = 0
    support_distribution: Counter[int] = Counter()
    coefficient_template_counts: Counter[str] = Counter()
    potential_clause_counts: Counter[str] = Counter()
    kind_pair_potential_counts: Counter[tuple[str, str, str]] = Counter()
    occurrence_counts = []
    top_pairs: list[dict[str, Any]] = []

    for vector_id, inverse in enumerate(inverse_id):
        if inverse < 0 or vector_id >= inverse:
            continue
        inverse_pair_count += 1
        vector = vector_by_id[vector_id]
        template = coefficient_template_id(vector)
        potential_count = vector_occurrences[vector_id] * vector_occurrences[inverse]
        support_distribution[len(vector)] += 1
        coefficient_template_counts[template] += 1
        potential_clause_counts[template] += potential_count
        occurrence_counts.append(vector_occurrences[vector_id])
        occurrence_counts.append(vector_occurrences[inverse])
        for left_kind, left_count in kind_occurrences[vector_id].items():
            for right_kind, right_count in kind_occurrences[inverse].items():
                kind_pair_potential_counts[(template, left_kind, right_kind)] += (
                    left_count * right_count
                )
        top_pairs.append(
            {
                "inverse_vector_pair": [vector_id, inverse],
                "coefficient_template": template,
                "support_size": len(vector),
                "potential_ordered_quad_pair_count": potential_count,
                "left_vector_occurrences": vector_occurrences[vector_id],
                "right_vector_occurrences": vector_occurrences[inverse],
                "left_kind_occurrences": dict(sorted(kind_occurrences[vector_id].items())),
                "right_kind_occurrences": dict(sorted(kind_occurrences[inverse].items())),
                "left_sparse_vector": [
                    {"class_id": class_id, "coefficient": coefficient}
                    for class_id, coefficient in vector
                ],
            }
        )

    class_sizes = Counter(classes.values())
    class_size_histogram = Counter(class_sizes.values())
    return {
        "pattern": {
            "name": name,
            "n": n,
            "circulant_offsets": offsets,
        },
        "ordered_quad_table_size": len(quad_ids),
        "vector_id_count": len(inverse_id),
        "inverse_vector_pair_count": inverse_pair_count,
        "selected_distance_class_count": len(set(classes.values())),
        "selected_distance_class_size_histogram": {
            str(size): class_size_histogram[size]
            for size in sorted(class_size_histogram)
        },
        "inverse_pair_support_size_distribution": {
            str(size): support_distribution[size]
            for size in sorted(support_distribution)
        },
        "coefficient_template_distribution": [
            coefficient_template_row(template, coefficient_template_counts[template])
            for template in sorted(coefficient_template_counts)
        ],
        "potential_ordered_quad_pair_count_by_template": {
            template: potential_clause_counts[template]
            for template in sorted(potential_clause_counts)
        },
        "kind_pair_potential_counts": [
            {
                "coefficient_template": template,
                "left_kind": left_kind,
                "right_kind": right_kind,
                "count": kind_pair_potential_counts[(template, left_kind, right_kind)],
            }
            for template, left_kind, right_kind in sorted(kind_pair_potential_counts)
        ],
        "vector_occurrence_count_min": min(occurrence_counts),
        "vector_occurrence_count_max": max(occurrence_counts),
        "top_inverse_vector_pairs_by_potential_count": sorted(
            top_pairs,
            key=lambda item: (
                -int(item["potential_ordered_quad_pair_count"]),
                item["inverse_vector_pair"],
            ),
        )[:top],
        "note": (
            "Vector ids and class ids are deterministic for this checker, but "
            "the reusable part is the coefficient template, support size, and "
            "selected-distance quotient structure."
        ),
    }


def coefficient_template_id(vector: Sequence[tuple[int, int]]) -> str:
    positive = sorted(coefficient for _, coefficient in vector if coefficient > 0)
    negative = sorted(-coefficient for _, coefficient in vector if coefficient < 0)
    if positive == [1] and negative == [1]:
        return "one_class_equals_one_class"
    if positive == [1, 1] and negative == [1, 1]:
        return "two_classes_equal_two_classes"
    return f"positive_{positive}_negative_{negative}"


def coefficient_template_row(template: str, count: int) -> dict[str, Any]:
    if template == "one_class_equals_one_class":
        return {
            "template": template,
            "inverse_vector_pair_count": count,
            "support_size": 2,
            "positive_coefficients": [1],
            "negative_coefficients": [1],
            "interpretation": (
                "After selected-distance quotienting, one Kalmanson row is "
                "D_A > D_B and its inverse is D_B > D_A."
            ),
        }
    if template == "two_classes_equal_two_classes":
        return {
            "template": template,
            "inverse_vector_pair_count": count,
            "support_size": 4,
            "positive_coefficients": [1, 1],
            "negative_coefficients": [1, 1],
            "interpretation": (
                "After selected-distance quotienting, one Kalmanson row is "
                "D_A + D_B > D_C + D_D and its inverse reverses the two sides."
            ),
        }
    return {
        "template": template,
        "inverse_vector_pair_count": count,
        "support_size": None,
        "interpretation": "Unclassified coefficient template.",
    }


def cross_pattern_summary(summaries: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    template_sets = []
    for summary in summaries:
        rows = summary["coefficient_template_distribution"]
        if not isinstance(rows, list):
            raise TypeError("coefficient_template_distribution must be a list")
        template_sets.append(
            {str(row["template"]) for row in rows if isinstance(row, Mapping)}
        )
    shared = set.intersection(*template_sets) if template_sets else set()
    union = set.union(*template_sets) if template_sets else set()
    return {
        "shared_coefficient_templates": sorted(shared),
        "all_coefficient_templates": sorted(union),
        "patterns_have_same_template_set": len({tuple(sorted(items)) for items in template_sets})
        == 1,
    }


def assert_expected(payload: Mapping[str, Any]) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"schema mismatch: {payload.get('schema')!r}")
    if payload.get("status") != STATUS:
        raise AssertionError(f"status mismatch: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        raise AssertionError(f"trust mismatch: {payload.get('trust')!r}")
    if payload.get("provenance") != PROVENANCE:
        raise AssertionError(f"provenance mismatch: {payload.get('provenance')!r}")
    if payload.get("claim_scope") != CLAIM_SCOPE:
        raise AssertionError(f"claim_scope mismatch: {payload.get('claim_scope')!r}")
    claim_scope = CLAIM_SCOPE
    for required in (
        "does not search new cyclic orders",
        "does not prove Erdos Problem #97",
        "does not claim a counterexample",
        "does not transfer the obstruction to other patterns",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")

    summaries = payload.get("pattern_summaries")
    if not isinstance(summaries, list) or len(summaries) != 2:
        raise AssertionError("expected exactly two pattern summaries")
    expected_by_name = {
        "C13_sidon_1_2_4_10": {
            "ordered_quad_table_size": 17160,
            "vector_id_count": 3458,
            "inverse_vector_pair_count": 1729,
            "selected_distance_class_count": 39,
            "selected_distance_class_size_histogram": {"1": 26, "4": 13},
            "inverse_pair_support_size_distribution": {"2": 390, "4": 1339},
            "potential_ordered_quad_pair_count_by_template": {
                "one_class_equals_one_class": 159744,
                "two_classes_equal_two_classes": 90688,
            },
            "vector_occurrence_count_min": 8,
            "vector_occurrence_count_max": 40,
        },
        "C19_skew": {
            "ordered_quad_table_size": 93024,
            "vector_id_count": 22344,
            "inverse_vector_pair_count": 11172,
            "selected_distance_class_count": 114,
            "selected_distance_class_size_histogram": {"1": 95, "4": 19},
            "inverse_pair_support_size_distribution": {"2": 1387, "4": 9785},
            "potential_ordered_quad_pair_count_by_template": {
                "one_class_equals_one_class": 196992,
                "two_classes_equal_two_classes": 629888,
            },
            "vector_occurrence_count_min": 8,
            "vector_occurrence_count_max": 32,
        },
    }
    for summary in summaries:
        if not isinstance(summary, Mapping):
            raise AssertionError("pattern summaries must be objects")
        pattern = summary.get("pattern")
        if not isinstance(pattern, Mapping):
            raise AssertionError("summary pattern must be an object")
        name = str(pattern.get("name"))
        expected = expected_by_name.pop(name)
        for key, value in expected.items():
            if summary.get(key) != value:
                raise AssertionError(
                    f"{name} {key} mismatch: expected {value!r}, got {summary.get(key)!r}"
                )
        rows = summary.get("coefficient_template_distribution")
        if not isinstance(rows, list):
            raise AssertionError(f"{name} coefficient_template_distribution must be a list")
        observed_counts = {
            str(row["template"]): int(row["inverse_vector_pair_count"])
            for row in rows
            if isinstance(row, Mapping)
        }
        expected_counts = (
            {"one_class_equals_one_class": 390, "two_classes_equal_two_classes": 1339}
            if name == "C13_sidon_1_2_4_10"
            else {"one_class_equals_one_class": 1387, "two_classes_equal_two_classes": 9785}
        )
        if observed_counts != expected_counts:
            raise AssertionError(f"{name} coefficient template counts changed: {observed_counts}")
    if expected_by_name:
        raise AssertionError(f"missing summaries for {sorted(expected_by_name)}")

    cross = payload.get("cross_pattern_summary")
    if cross != {
        "shared_coefficient_templates": [
            "one_class_equals_one_class",
            "two_classes_equal_two_classes",
        ],
        "all_coefficient_templates": [
            "one_class_equals_one_class",
            "two_classes_equal_two_classes",
        ],
        "patterns_have_same_template_set": True,
    }:
        raise AssertionError(f"cross pattern summary changed: {cross!r}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c13-artifact", type=Path, default=DEFAULT_C13)
    parser.add_argument("--c19-artifact", type=Path, default=DEFAULT_C19)
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top <= 0:
        raise SystemExit("--top must be positive")
    c13_artifact = args.c13_artifact if args.c13_artifact.is_absolute() else ROOT / args.c13_artifact
    c19_artifact = args.c19_artifact if args.c19_artifact.is_absolute() else ROOT / args.c19_artifact
    payload = diagnostic_payload(
        c13_artifact=c13_artifact,
        c19_artifact=c19_artifact,
        top=args.top,
    )
    if args.assert_expected:
        assert_expected(payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Kalmanson inverse-pair coefficient-template diagnostic")
        for summary in payload["pattern_summaries"]:
            pattern = summary["pattern"]
            print(
                f"{pattern['name']}: inverse pairs={summary['inverse_vector_pair_count']} "
                f"templates={summary['inverse_pair_support_size_distribution']}"
            )
        if args.assert_expected:
            print("OK: Kalmanson inverse-pair template diagnostic matches expected values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
