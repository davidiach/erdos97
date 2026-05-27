#!/usr/bin/env python3
"""Check Kalmanson inverse-pair template availability in sparse frontier patterns."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from analyze_kalmanson_inverse_pair_templates import (  # noqa: E402
    coefficient_template_row,
    cross_pattern_summary,
    pattern_template_summary,
)
from erdos97.path_display import display_path  # noqa: E402

SCHEMA = "erdos97.kalmanson_sparse_frontier_templates.v1"
STATUS = "KALMANSON_SPARSE_FRONTIER_TEMPLATE_AVAILABILITY_DIAGNOSTIC"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact coefficient-template availability diagnostic for the registered "
    "C25_sidon_2_5_9_14 and C29_sidon_1_3_7_15 sparse-frontier selected-witness "
    "patterns. It only classifies quotient-vector inverse pairs available to "
    "these fixed abstract patterns. It does not search cyclic orders, does not "
    "prove an all-order obstruction, does not prove Erdos Problem #97, does not "
    "claim a counterexample, and does not transfer the obstruction to arbitrary "
    "selected-witness systems."
)
PROVENANCE = {
    "generator": "scripts/analyze_kalmanson_sparse_frontier_templates.py",
    "command": (
        "python scripts/analyze_kalmanson_sparse_frontier_templates.py "
        "--assert-expected --json"
    ),
}
DEFAULT_CATALOG = ROOT / "data" / "patterns" / "candidate_patterns.json"
FRONTIER_PATTERNS = (
    ("C25_sidon_2_5_9_14", 25, (2, 5, 9, 14)),
    ("C29_sidon_1_3_7_15", 29, (1, 3, 7, 15)),
)
CHECKED_PILOT_TEMPLATE_ROWS = [
    coefficient_template_row("one_class_equals_one_class", 0),
    coefficient_template_row("two_classes_equal_two_classes", 0),
]
CHECKED_PILOT_TEMPLATE_SET = [
    "one_class_equals_one_class",
    "two_classes_equal_two_classes",
]


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog_entries(catalog_path: Path) -> dict[str, Mapping[str, Any]]:
    raw = load_json(catalog_path)
    if not isinstance(raw, list):
        raise TypeError("candidate pattern catalog must be a JSON list")
    entries: dict[str, Mapping[str, Any]] = {}
    for entry in raw:
        if not isinstance(entry, Mapping):
            raise TypeError("candidate pattern catalog entries must be JSON objects")
        name = str(entry.get("name"))
        entries[name] = entry
    return entries


def diagnostic_payload(*, catalog_path: Path = DEFAULT_CATALOG, top: int = 4) -> dict[str, Any]:
    """Return the sparse-frontier inverse-pair template availability diagnostic."""

    catalog = catalog_entries(catalog_path)
    summaries = []
    source_patterns = []
    for name, n, offsets in FRONTIER_PATTERNS:
        catalog_entry = catalog.get(name)
        if catalog_entry is None:
            raise ValueError(f"candidate pattern catalog is missing {name}")
        if int(catalog_entry.get("n", -1)) != n:
            raise ValueError(f"candidate pattern catalog has wrong n for {name}")
        source_patterns.append(
            {
                "name": name,
                "n": n,
                "formula": catalog_entry.get("formula"),
                "status": catalog_entry.get("status"),
                "trust": catalog_entry.get("trust"),
                "lifecycle": catalog_entry.get("lifecycle"),
            }
        )
        summaries.append(
            pattern_template_summary(
                {
                    "name": name,
                    "n": n,
                    "circulant_offsets": list(offsets),
                },
                top=top,
            )
        )

    cross = cross_pattern_summary(summaries)
    frontier_templates = cross["all_coefficient_templates"]
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_catalog": display_path(catalog_path, ROOT),
        "source_catalog_patterns": source_patterns,
        "frontier_pattern_summaries": summaries,
        "frontier_cross_pattern_summary": cross,
        "checked_pilot_template_rows": CHECKED_PILOT_TEMPLATE_ROWS,
        "comparison_to_checked_c13_c19_pilots": {
            "checked_pilot_template_set": CHECKED_PILOT_TEMPLATE_SET,
            "frontier_template_set": frontier_templates,
            "frontier_exposes_only_checked_pilot_templates": (
                frontier_templates == CHECKED_PILOT_TEMPLATE_SET
            ),
            "frontier_exposes_all_checked_pilot_templates": (
                set(CHECKED_PILOT_TEMPLATE_SET).issubset(set(frontier_templates))
            ),
        },
        "interpretation": (
            "The larger Sidon frontier exposes the same two quotient coefficient "
            "template shapes seen in the checked C13/C19 all-order pilots, but "
            "this is only availability. It does not say that every cyclic order "
            "contains such a pair, and it does not obstruct C25 or C29."
        ),
        "provenance": dict(PROVENANCE),
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
        "does not search cyclic orders",
        "does not prove an all-order obstruction",
        "does not prove Erdos Problem #97",
        "does not claim a counterexample",
        "does not transfer the obstruction",
    ):
        if required not in claim_scope:
            raise AssertionError(f"claim_scope missing {required!r}")

    summaries = payload.get("frontier_pattern_summaries")
    if not isinstance(summaries, list) or len(summaries) != 2:
        raise AssertionError("expected exactly two frontier pattern summaries")
    expected_by_name = {
        "C25_sidon_2_5_9_14": {
            "ordered_quad_table_size": 303600,
            "vector_id_count": 74950,
            "inverse_vector_pair_count": 37475,
            "selected_distance_class_count": 225,
            "selected_distance_class_size_histogram": {"1": 200, "4": 25},
            "inverse_pair_support_size_distribution": {"2": 2850, "4": 34625},
            "potential_ordered_quad_pair_count_by_template": {
                "one_class_equals_one_class": 284800,
                "two_classes_equal_two_classes": 2220800,
            },
            "vector_occurrence_count_min": 8,
            "vector_occurrence_count_max": 32,
            "template_counts": {
                "one_class_equals_one_class": 2850,
                "two_classes_equal_two_classes": 34625,
            },
        },
        "C29_sidon_1_3_7_15": {
            "ordered_quad_table_size": 570024,
            "vector_id_count": 141404,
            "inverse_vector_pair_count": 70702,
            "selected_distance_class_count": 319,
            "selected_distance_class_size_histogram": {"1": 290, "4": 29},
            "inverse_pair_support_size_distribution": {"2": 3973, "4": 66729},
            "potential_ordered_quad_pair_count_by_template": {
                "one_class_equals_one_class": 389760,
                "two_classes_equal_two_classes": 4270656,
            },
            "vector_occurrence_count_min": 8,
            "vector_occurrence_count_max": 32,
            "template_counts": {
                "one_class_equals_one_class": 3973,
                "two_classes_equal_two_classes": 66729,
            },
        },
    }
    for summary in summaries:
        if not isinstance(summary, Mapping):
            raise AssertionError("frontier pattern summaries must be objects")
        pattern = summary.get("pattern")
        if not isinstance(pattern, Mapping):
            raise AssertionError("summary pattern must be an object")
        name = str(pattern.get("name"))
        expected = expected_by_name.pop(name)
        for key, value in expected.items():
            if key == "template_counts":
                continue
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
        if observed_counts != expected["template_counts"]:
            raise AssertionError(f"{name} coefficient template counts changed: {observed_counts}")
    if expected_by_name:
        raise AssertionError(f"missing frontier summaries for {sorted(expected_by_name)}")

    if payload.get("frontier_cross_pattern_summary") != {
        "shared_coefficient_templates": CHECKED_PILOT_TEMPLATE_SET,
        "all_coefficient_templates": CHECKED_PILOT_TEMPLATE_SET,
        "patterns_have_same_template_set": True,
    }:
        raise AssertionError(
            f"frontier cross summary changed: {payload.get('frontier_cross_pattern_summary')!r}"
        )
    if payload.get("comparison_to_checked_c13_c19_pilots") != {
        "checked_pilot_template_set": CHECKED_PILOT_TEMPLATE_SET,
        "frontier_template_set": CHECKED_PILOT_TEMPLATE_SET,
        "frontier_exposes_only_checked_pilot_templates": True,
        "frontier_exposes_all_checked_pilot_templates": True,
    }:
        raise AssertionError(
            "comparison to checked C13/C19 pilots changed: "
            f"{payload.get('comparison_to_checked_c13_c19_pilots')!r}"
        )


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--top", type=int, default=4)
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.top <= 0:
        raise SystemExit("--top must be positive")
    catalog = args.catalog if args.catalog.is_absolute() else ROOT / args.catalog
    payload = diagnostic_payload(catalog_path=catalog, top=args.top)
    if args.assert_expected:
        assert_expected(payload)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("Kalmanson sparse-frontier template availability diagnostic")
        for summary in payload["frontier_pattern_summaries"]:
            pattern = summary["pattern"]
            print(
                f"{pattern['name']}: inverse pairs={summary['inverse_vector_pair_count']} "
                f"templates={summary['inverse_pair_support_size_distribution']}"
            )
        if args.assert_expected:
            print("OK: sparse-frontier template availability matches expected values")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
