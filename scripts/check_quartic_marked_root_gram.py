#!/usr/bin/env python3
"""Generate and replay the exact quartic marked-root Gram obstruction."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path
from typing import Any

from erdos97.quartic_marked_root_gram import (
    E11_UPPER,
    SCHEMA,
    UNIVERSAL_PHANTOM_UPPER,
    equations_hold,
    gram_upper_from_coefficients,
    lifted_squared_distance,
    marked_root_divisibility_check,
    marked_row_equations,
    quartic_closure_pilot,
    rank_one_psd_check,
    second_derivative_has_constant_sign,
)

ROOT = Path(__file__).resolve().parents[1]

DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "quartic_marked_root_gram.json"
PARAMETERS = tuple(range(-4, 5))
ANCHOR_CENTERS = (0, 3, 4)
POSITIVE_COEFFICIENTS = (
    Fraction(-51017, 6552),
    Fraction(337469, 393120),
    Fraction(-2503, 65520),
    Fraction(253, 393120),
)
POSITIVE_WITNESSES = (7, 15, 20, 24)
HIGH_RANK_DIRECTION = (-15180, 1553, -66, 1)
EXPECTED_SCHEMA = "erdos97.quartic_marked_root_gram.v2"
EXPECTED_STATUS = (
    "NO_PAIRWISE_DISTINCT_PLANAR_DEGREE_AT_MOST_FOUR_SAMPLE_RICH_AT_ALL_"
    "FOUR_TEST_CENTERS_ON_NINE_TERM_ARITHMETIC_PROGRESSION"
)

EXPECTED_ANCHOR_FULL_GRAM_CENSUS = {
    "rank_2": 279,
    "rank_3": 91,
    "rank_4": 198979,
    "determinant_negative": 101793,
    "determinant_positive": 97186,
    "determinant_zero": 370,
    "inertia_1_1_2": 277,
    "inertia_2_0_2": 2,
    "inertia_1_2_1": 5,
    "inertia_2_1_1": 86,
    "inertia_1_3_0": 7051,
    "inertia_3_1_0": 94742,
    "inertia_2_2_0": 95884,
    "inertia_4_0_0": 1302,
    "planar_kernel_lines": 2,
    "unique_kernel_lines": 190895,
    "phantom_roots": 199349,
    "other_rank_one_roots": 0,
}

EXPECTED_EXTENSION_FULL_GRAM_CENSUS = {
    "raw_affine_rank_9_branches": 320,
    "raw_affine_rank_10_branches": 190710,
    "affine_rank_9_states": 314,
    "affine_rank_10_states": 1,
    "kernel_rank_2": 11,
    "kernel_rank_3": 0,
    "kernel_rank_4": 303,
    "determinant_negative": 231,
    "determinant_positive": 72,
    "determinant_zero": 11,
    "inertia_1_1_2": 11,
    "inertia_2_0_2": 0,
    "inertia_1_2_1": 0,
    "inertia_2_1_1": 0,
    "inertia_1_3_0": 99,
    "inertia_3_1_0": 132,
    "inertia_2_2_0": 6,
    "inertia_4_0_0": 66,
    "planar_kernel_lines": 0,
    "phantom_line_roots": 314,
    "phantom_singletons": 1,
    "other_rank_one_roots": 0,
}

EXPECTED_PLANAR_ANCHOR_CANDIDATES = [
    {
        "full_gram_upper": [
            "2308",
            "108",
            "-232",
            "24",
            "183",
            "18",
            "-21",
            "28",
            "-6",
            "3",
        ],
        "rank": 2,
        "center_multiplicities": [2, 4, 4, 4, 4, 4, 4, 4, 4],
        "collision_pairs": [["-3", "4"], ["-2", "-1"], ["2", "3"]],
        "pairwise_distinct": False,
        "strictly_convex_sample": False,
    },
    {
        "full_gram_upper": [
            "292",
            "-248",
            "-88",
            "44",
            "211",
            "74",
            "-37",
            "28",
            "-14",
            "7",
        ],
        "rank": 2,
        "center_multiplicities": [2, 4, 4, 4, 4, 4, 4, 4, 4],
        "collision_pairs": [
            ["-3", "4"],
            ["-2", "3"],
            ["-1", "2"],
            ["0", "1"],
        ],
        "pairwise_distinct": False,
        "strictly_convex_sample": False,
    },
]


def fraction_text(value: Fraction | int) -> str:
    exact = value if isinstance(value, Fraction) else Fraction(value)
    if exact.denominator == 1:
        return str(exact.numerator)
    return f"{exact.numerator}/{exact.denominator}"


def normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    # Normalize nested tuples before comparison with a JSON-loaded artifact.
    # This also keeps optional survivor/candidate records replay-stable.
    normalized = json.loads(json.dumps(payload, sort_keys=True))
    if not isinstance(normalized, dict):
        raise AssertionError("normalized payload must remain a JSON object")
    return normalized


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError(f"{path} must contain one JSON object")
    return payload


def required_summary_attribute(summary: object, name: str) -> Any:
    """Read one schema-v2 summary field without silently accepting v1 data."""

    if not hasattr(summary, name):
        raise AssertionError(
            f"schema-v2 generator requires summary field {name!r}; "
            "the exact full-Gram implementation is incomplete"
        )
    return getattr(summary, name)


def control_summary() -> dict[str, Any]:
    positive_gram = gram_upper_from_coefficients(POSITIVE_COEFFICIENTS)
    positive_equations = marked_row_equations(0, POSITIVE_WITNESSES)
    distances = tuple(
        lifted_squared_distance(positive_gram, 0, witness)
        for witness in POSITIVE_WITNESSES
    )
    if distances != (Fraction(625),) * 4:
        raise AssertionError("positive control no longer has squared radius 625")
    if not equations_hold(positive_equations, positive_gram):
        raise AssertionError("positive control fails its affine marked-row equations")
    if not marked_root_divisibility_check(0, POSITIVE_WITNESSES, positive_gram):
        raise AssertionError("positive control fails independent marked-root divisibility")
    positive_check = rank_one_psd_check(positive_gram)
    if not positive_check.quartic_gram:
        raise AssertionError("positive control fails the rank-one quartic Gram gate")
    if not second_derivative_has_constant_sign(POSITIVE_COEFFICIENTS, 0, 24):
        raise AssertionError("positive control fails exact interval convexity")

    high_rank_component = gram_upper_from_coefficients(HIGH_RANK_DIRECTION)
    high_rank_gram = tuple(
        base + component
        for base, component in zip(positive_gram, high_rank_component, strict=True)
    )
    high_rank_check = rank_one_psd_check(high_rank_gram)
    if not equations_hold(positive_equations, high_rank_gram):
        raise AssertionError("high-rank relaxation trap should satisfy the marked row")
    if not high_rank_check.positive_semidefinite or high_rank_check.rank_one:
        raise AssertionError("high-rank relaxation trap did not exercise the planar gate")

    return {
        "positive_one_rich_row": {
            "coefficients": [fraction_text(value) for value in POSITIVE_COEFFICIENTS],
            "center": "0",
            "witnesses": [str(value) for value in POSITIVE_WITNESSES],
            "squared_radius": "625",
            "marked_equations_hold": True,
            "independent_divisibility_holds": True,
            "rank_one_psd_degree_four": True,
            "strictly_convex_on_0_24": True,
            "claim_boundary": "ONE_RICH_ROW_ONLY_NOT_FINITE_CLOSURE",
        },
        "higher_rank_psd_relaxation_trap": {
            "extra_direction": [str(value) for value in HIGH_RANK_DIRECTION],
            "marked_equations_hold": True,
            "positive_semidefinite": True,
            "rank_one": False,
            "rejected_as_planar_quartic_graph": True,
        },
    }


def build_payload() -> dict[str, Any]:
    if SCHEMA != EXPECTED_SCHEMA:
        raise AssertionError(f"source schema {SCHEMA!r} != {EXPECTED_SCHEMA!r}")
    summary = quartic_closure_pilot(
        parameters=PARAMETERS,
        anchor_centers=ANCHOR_CENTERS,
    )
    anchor = summary.anchor
    anchor_full_gram_census = dict(
        required_summary_attribute(anchor, "full_gram_kernel_census")
    )
    anchor_planar_candidates = list(
        required_summary_attribute(anchor, "full_gram_planar_candidates")
    )
    extension_full_gram_census = dict(
        required_summary_attribute(summary, "full_gram_extension_census")
    )
    four_center_unresolved_states = required_summary_attribute(
        summary,
        "full_gram_four_center_unresolved_state_count",
    )
    pairwise_distinct_full_gram_candidates = required_summary_attribute(
        summary,
        "full_gram_pairwise_distinct_candidate_count",
    )
    strictly_convex_full_gram_candidates = required_summary_attribute(
        summary,
        "full_gram_strictly_convex_candidate_count",
    )

    if summary.strict_finite_full_closure_candidate_count:
        original_graph_status = "EXACT_FIXED_GRID_CLOSURE_CANDIDATE"
    elif summary.unresolved_affine_state_count:
        original_graph_status = "INCONCLUSIVE_FIXED_GRID_WITH_UNRESOLVED_AFFINE_STATES"
    else:
        original_graph_status = "NO_STRICTLY_CONVEX_DEGREE_FOUR_CLOSURE_ON_FIXED_GRID"

    if pairwise_distinct_full_gram_candidates:
        status = (
            "PAIRWISE_DISTINCT_PLANAR_DEGREE_AT_MOST_FOUR_"
            "FOUR_TEST_CENTER_CANDIDATE"
        )
        trust = "EXACT_CERTIFICATE_DIAGNOSTIC"
    elif four_center_unresolved_states:
        status = "INCONCLUSIVE_FULL_GRAM_WITH_UNRESOLVED_AFFINE_STATES"
        trust = "EXACT_CERTIFICATE_DIAGNOSTIC"
    else:
        status = EXPECTED_STATUS
        trust = "EXACT_OBSTRUCTION"

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": status,
        "trust": trust,
        "claim_scope": {
            "statement": (
                "For every real planar polynomial map gamma of degree at most four, "
                "sampled at nine equally spaced parameters, if the nine sample points "
                "are pairwise distinct then at least one of the four positions "
                "corresponding after affine reparameterization to -4,0,3,4 is not "
                "four-rich within the sample."
            ),
            "ambient_dimension": 2,
            "maximum_coordinate_degree": 4,
            "sample_size": 9,
            "parameter_sets": "NINE_TERM_REAL_ARITHMETIC_PROGRESSIONS",
            "pairwise_distinctness_required": True,
            "convexity_used": False,
            "test_center_set_guaranteed_to_contain_a_non_rich_position_"
            "after_normalization": ["-4", "0", "3", "4"],
        },
        "does_not_check": [
            "arbitrary or irregular real parameter sets",
            "polynomial parametrizations of degree greater than four",
            "higher-dimensional Euclidean samples",
            (
                "implicit or general algebraic quartic curves not given by one "
                "polynomial parametrization"
            ),
            "multi-arc constructions",
            "general strictly convex polygons",
            "a proof or counterexample for Erdos Problem #97",
        ],
        "decisive_test_card": {
            "classification": "PREDECLARED_ORIGINAL_GRAPH_TEST",
            "question": (
                "Can the one-rich-row quartic flexibility close all nine rows on the "
                "smallest equally spaced parameter grid not already covered by n<=8?"
            ),
            "hypotheses": {
                "local_only": (
                    "anchor affine systems fail the planar rank-one gate or their "
                    "exceptional states die under further rows"
                ),
                "fixed_grid_closure": (
                    "one rank-one PSD degree-four Gram survives every center and the "
                    "finite strict-convexity gate"
                ),
            },
            "predeclared_stopping_rule": (
                "Report an exact fixed-grid obstruction only when the exceptional affine "
                "frontier is empty; otherwise preserve unresolved states."
            ),
            "result_status": original_graph_status,
        },
        "post_hoc_structural_upgrade_card": {
            "classification": "POST_HOC_FULL_GRAM_STRUCTURAL_UPGRADE",
            "predeclared": False,
            "derivation": (
                "Translate A to the homogeneous full coefficient Gram B=A+E11, "
                "classify every one-dimensional kernel by exact rank and inertia, "
                "and check pairwise distinctness of the only two planar anchor rays."
            ),
            "stronger_than_original_graph_test": (
                "Covers arbitrary planar polynomial parametrizations of degree at most "
                "four on every nine-term arithmetic progression and does not use convexity."
            ),
        },
        "model": {
            "parameters": [str(value) for value in PARAMETERS],
            "anchor_centers": [str(value) for value in ANCHOR_CENTERS],
            "extension_centers": [fraction_text(value) for value in summary.extension_centers],
            "gram_variable_order": [
                "A11",
                "A12",
                "A13",
                "A14",
                "A22",
                "A23",
                "A24",
                "A33",
                "A34",
                "A44",
            ],
            "row_equations_per_marked_quartet": 3,
            "planar_gate": "A=a*a^T, rank one, positive semidefinite, A44>0",
            "full_gram_upgrade": {
                "identity": "B=A+E11",
                "E11_upper": [fraction_text(value) for value in E11_UPPER],
                "B_variable_order": [
                    "B11",
                    "B12",
                    "B13",
                    "B14",
                    "B22",
                    "B23",
                    "B24",
                    "B33",
                    "B34",
                    "B44",
                ],
                "translated_marked_rows": "HOMOGENEOUS_LINEAR_EQUATIONS_IN_B",
                "planar_gate": "B=C^T*C, B nonzero PSD, rank(B)<=2",
                "constant_coefficients": "OMITTED_BECAUSE_TRANSLATIONS_PRESERVE_DISTANCES",
            },
        },
        "controls": control_summary(),
        "anchor_scan": {
            "quartets_per_center": anchor.quartet_count_per_center,
            "raw_marked_triples": anchor.raw_triple_count,
            "overlap_admissible_marked_triples": anchor.overlap_admissible_count,
            "overlap_filtered_marked_triples": (
                anchor.raw_triple_count - anchor.overlap_admissible_count
            ),
            "pair_inconsistent_pruned_triples": (
                anchor.pair_inconsistent_pruned_triple_count
            ),
            "third_row_inconsistent_triples": anchor.inconsistent_count,
            "rank_counts": {str(rank): count for rank, count in anchor.rank_counts},
            "rank_nine_marked_triples": dict(anchor.rank_counts).get(9, 0),
            "rank_nine_without_real_rank_at_most_one": (
                anchor.line_without_real_rank_at_most_one_count
            ),
            "rank_nine_zero_matrix_roots": anchor.line_zero_matrix_root_count,
            "rank_nine_negative_semidefinite_rank_one_roots": (
                anchor.line_negative_semidefinite_rank_one_root_count
            ),
            "rank_nine_lower_degree_rank_one_psd_roots": (
                anchor.line_lower_degree_rank_one_psd_root_count
            ),
            "rank_nine_rational_quartic_grams": anchor.line_rational_quartic_gram_count,
            "rank_nine_irrational_components": (
                anchor.line_irrational_rank_at_most_one_component_count
            ),
            "rank_nine_whole_rank_at_most_one_lines": (
                anchor.line_all_rank_at_most_one_count
            ),
            "exceptional_affine_states": anchor.exceptional_affine_state_count,
            "sample_survivors": list(anchor.sample_survivors),
        },
        "extension_steps": list(summary.extension_steps),
        "post_hoc_full_gram_upgrade": {
            "classification": "POST_HOC_FULL_GRAM_STRUCTURAL_UPGRADE",
            "homogeneous_identity": {
                "formula": "B=A+E11",
                "universal_graph_gram_phantom_upper": [
                    fraction_text(value) for value in UNIVERSAL_PHANTOM_UPPER
                ],
                "phantom_full_gram_upper": ["0"] * 10,
                "phantom_interpretation": (
                    "A*=-E11 is the zero full Gram B=0, not a realizable "
                    "nonzero planar coefficient Gram."
                ),
                "every_marked_row_contains_phantom": True,
                "every_translated_marked_row_is_homogeneous": True,
            },
            "anchor_kernel_census": anchor_full_gram_census,
            "anchor_planar_rank_two_psd_candidates": anchor_planar_candidates,
            "extension_kernel_census": extension_full_gram_census,
            "outcome": {
                "unresolved_affine_states_after_four_test_centers": (
                    four_center_unresolved_states
                ),
                "pairwise_distinct_planar_candidates_rich_at_all_four_test_centers": (
                    pairwise_distinct_full_gram_candidates
                ),
                "strictly_convex_planar_candidates_rich_at_all_four_test_centers": (
                    strictly_convex_full_gram_candidates
                ),
                "specific_center_set_forced_to_contain_non_rich_position": [
                    "-4",
                    "0",
                    "3",
                    "4",
                ],
                "affine_reparameterization_scope": (
                    "ALL_NINE_TERM_REAL_ARITHMETIC_PROGRESSIONS"
                ),
            },
        },
        "outcome": {
            "unresolved_affine_states": summary.unresolved_affine_state_count,
            "rank_one_quartic_grams": summary.rank_one_quartic_candidate_count,
            "continuously_convex_rank_one_quartic_grams": (
                summary.convex_rank_one_candidate_count
            ),
            "all_row_quartic_grams": summary.all_row_quartic_candidate_count,
            "strict_finite_full_closures": (
                summary.strict_finite_full_closure_candidate_count
            ),
            "continuous_convex_full_closures": (
                summary.continuous_convex_full_closure_candidate_count
            ),
            "sample_candidates": list(summary.sample_candidates),
        },
        "provenance": {
            "generator": "scripts/check_quartic_marked_root_gram.py",
            "command": (
                "python scripts/check_quartic_marked_root_gram.py "
                "--write-artifact --check --assert-expected --json"
            ),
            "check_command": (
                "python scripts/check_quartic_marked_root_gram.py "
                "--check --assert-expected --json"
            ),
            "arithmetic": (
                "fractions.Fraction exact rational elimination plus primitive "
                "integer symmetric-matrix rank and inertia"
            ),
            "summary_type": type(summary).__name__,
            "original_test_phase": "PREDECLARED",
            "full_gram_upgrade_phase": "POST_HOC",
        },
    }
    return normalize_payload(payload)


def check_payload(payload: dict[str, Any], *, assert_expected: bool) -> None:
    if payload.get("schema") != EXPECTED_SCHEMA or SCHEMA != EXPECTED_SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("trust") not in {"EXACT_OBSTRUCTION", "EXACT_CERTIFICATE_DIAGNOSTIC"}:
        raise AssertionError(f"unexpected trust label: {payload.get('trust')!r}")
    anchor = payload.get("anchor_scan")
    outcome = payload.get("outcome")
    controls = payload.get("controls")
    decisive_card = payload.get("decisive_test_card")
    structural_card = payload.get("post_hoc_structural_upgrade_card")
    full_gram = payload.get("post_hoc_full_gram_upgrade")
    if not isinstance(anchor, dict) or not isinstance(outcome, dict):
        raise AssertionError("artifact is missing anchor_scan or outcome")
    if not isinstance(controls, dict):
        raise AssertionError("artifact is missing controls")
    if not isinstance(decisive_card, dict) or (
        decisive_card.get("classification") != "PREDECLARED_ORIGINAL_GRAPH_TEST"
    ):
        raise AssertionError("artifact must preserve the predeclared graph test")
    if not isinstance(structural_card, dict) or (
        structural_card.get("classification")
        != "POST_HOC_FULL_GRAM_STRUCTURAL_UPGRADE"
    ):
        raise AssertionError("artifact must label the full-Gram upgrade as post hoc")
    if not isinstance(full_gram, dict):
        raise AssertionError("artifact is missing post_hoc_full_gram_upgrade")

    homogeneous = full_gram.get("homogeneous_identity")
    anchor_full_gram = full_gram.get("anchor_kernel_census")
    extension_full_gram = full_gram.get("extension_kernel_census")
    planar_candidates = full_gram.get("anchor_planar_rank_two_psd_candidates")
    full_gram_outcome = full_gram.get("outcome")
    if not all(
        isinstance(value, dict)
        for value in (
            homogeneous,
            anchor_full_gram,
            extension_full_gram,
            full_gram_outcome,
        )
    ) or not isinstance(planar_candidates, list):
        raise AssertionError("artifact has malformed full-Gram structural data")
    if homogeneous.get("formula") != "B=A+E11":
        raise AssertionError("artifact lost the full-Gram homogenization identity")
    if homogeneous.get("universal_graph_gram_phantom_upper") != ["-1"] + ["0"] * 9:
        raise AssertionError("artifact lost the universal phantom A*=-E11")
    if homogeneous.get("phantom_full_gram_upper") != ["0"] * 10:
        raise AssertionError("universal phantom must translate to B=0")
    if payload.get("trust") == "EXACT_OBSTRUCTION" and full_gram_outcome.get(
        "unresolved_affine_states_after_four_test_centers"
    ):
        raise AssertionError(
            "an exact full-Gram obstruction cannot retain a four-center state"
        )
    if anchor.get("raw_marked_triples") != 343000:
        raise AssertionError("expected 70^3 raw anchor triples")
    if anchor.get("raw_marked_triples") != (
        anchor.get("overlap_admissible_marked_triples", 0)
        + anchor.get("overlap_filtered_marked_triples", 0)
    ):
        raise AssertionError("anchor overlap accounting does not reconcile")
    if (
        anchor_full_gram.get("rank_2", 0)
        + anchor_full_gram.get("rank_3", 0)
        + anchor_full_gram.get("rank_4", 0)
        != anchor.get("rank_nine_marked_triples")
    ):
        raise AssertionError("anchor full-Gram rank census does not reconcile")
    if (
        anchor_full_gram.get("determinant_negative", 0)
        + anchor_full_gram.get("determinant_positive", 0)
        + anchor_full_gram.get("determinant_zero", 0)
        != anchor.get("rank_nine_marked_triples")
    ):
        raise AssertionError("anchor full-Gram determinant census does not reconcile")
    if (
        extension_full_gram.get("affine_rank_9_states", 0)
        + extension_full_gram.get("affine_rank_10_states", 0)
        != 315
    ):
        raise AssertionError("extension affine-rank census does not reconcile")
    if (
        extension_full_gram.get("kernel_rank_2", 0)
        + extension_full_gram.get("kernel_rank_3", 0)
        + extension_full_gram.get("kernel_rank_4", 0)
        != extension_full_gram.get("affine_rank_9_states")
    ):
        raise AssertionError("extension kernel-rank census does not reconcile")
    if assert_expected:
        if payload.get("status") != EXPECTED_STATUS:
            raise AssertionError(f"unexpected default status: {payload.get('status')!r}")
        if payload.get("trust") != "EXACT_OBSTRUCTION":
            raise AssertionError(f"unexpected default trust: {payload.get('trust')!r}")
        if (
            decisive_card.get("result_status")
            != "NO_STRICTLY_CONVEX_DEGREE_FOUR_CLOSURE_ON_FIXED_GRID"
        ):
            raise AssertionError("unexpected original predeclared graph result")
        expected_anchor = {
            "quartets_per_center": 70,
            "raw_marked_triples": 343000,
            "overlap_admissible_marked_triples": 202080,
            "overlap_filtered_marked_triples": 140920,
            "pair_inconsistent_pruned_triples": 0,
            "third_row_inconsistent_triples": 0,
            "rank_counts": {"8": 2731, "9": 199349},
            "rank_nine_marked_triples": 199349,
            "rank_nine_without_real_rank_at_most_one": 0,
            "rank_nine_zero_matrix_roots": 0,
            "rank_nine_negative_semidefinite_rank_one_roots": 199349,
            "rank_nine_lower_degree_rank_one_psd_roots": 0,
            "rank_nine_rational_quartic_grams": 0,
            "rank_nine_irrational_components": 0,
            "rank_nine_whole_rank_at_most_one_lines": 0,
            "exceptional_affine_states": 2729,
        }
        for key, expected in expected_anchor.items():
            if anchor.get(key) != expected:
                raise AssertionError(
                    f"unexpected anchor field {key}: {anchor.get(key)!r} != {expected!r}"
                )
        steps = payload.get("extension_steps")
        if not isinstance(steps, list) or len(steps) != 1:
            raise AssertionError("expected exactly one extension step")
        expected_step = {
            "center": "-4",
            "input_affine_states": 2729,
            "row_options_per_state": 70,
            "raw_state_row_branches": 191030,
            "linearly_inconsistent_branches": 0,
            "linearly_consistent_branches": 191030,
            "deduplicated_consistent_affine_states": 315,
            "states_without_real_rank_at_most_one": 0,
            "zero_matrix_roots": 0,
            "negative_semidefinite_rank_one_roots": 315,
            "lower_degree_rank_one_psd_roots": 0,
            "specified_non_rank_one_grams": 0,
            "unique_rank_one_quartic_gram_states": 0,
            "rational_line_rank_one_quartic_grams": 0,
            "irrational_or_rank_one_line_states_retained": 0,
            "higher_dimensional_states_retained": 0,
            "deduplicated_affine_states_out": 0,
        }
        for key, expected in expected_step.items():
            if steps[0].get(key) != expected:
                raise AssertionError(
                    f"unexpected extension field {key}: {steps[0].get(key)!r} != {expected!r}"
                )
        expected_outcome = {
            "unresolved_affine_states": 0,
            "rank_one_quartic_grams": 0,
            "continuously_convex_rank_one_quartic_grams": 0,
            "all_row_quartic_grams": 0,
            "strict_finite_full_closures": 0,
            "continuous_convex_full_closures": 0,
            "sample_candidates": [],
        }
        if outcome != expected_outcome:
            raise AssertionError(f"unexpected default outcome: {outcome!r}")

        if anchor_full_gram != EXPECTED_ANCHOR_FULL_GRAM_CENSUS:
            raise AssertionError(
                f"unexpected anchor full-Gram census: {anchor_full_gram!r}"
            )
        if extension_full_gram != EXPECTED_EXTENSION_FULL_GRAM_CENSUS:
            raise AssertionError(
                f"unexpected extension full-Gram census: {extension_full_gram!r}"
            )
        normalized_candidates = sorted(
            planar_candidates,
            key=lambda candidate: tuple(candidate.get("full_gram_upper", ())),
        )
        expected_candidates = sorted(
            EXPECTED_PLANAR_ANCHOR_CANDIDATES,
            key=lambda candidate: tuple(candidate["full_gram_upper"]),
        )
        if normalized_candidates != expected_candidates:
            raise AssertionError(
                f"unexpected planar anchor candidates: {planar_candidates!r}"
            )
        expected_full_gram_outcome = {
            "unresolved_affine_states_after_four_test_centers": 0,
            "pairwise_distinct_planar_candidates_rich_at_all_four_test_centers": 0,
            "strictly_convex_planar_candidates_rich_at_all_four_test_centers": 0,
            "specific_center_set_forced_to_contain_non_rich_position": [
                "-4",
                "0",
                "3",
                "4",
            ],
            "affine_reparameterization_scope": (
                "ALL_NINE_TERM_REAL_ARITHMETIC_PROGRESSIONS"
            ),
        }
        if full_gram_outcome != expected_full_gram_outcome:
            raise AssertionError(
                f"unexpected full-Gram outcome: {full_gram_outcome!r}"
            )

        claim_scope = payload.get("claim_scope")
        if not isinstance(claim_scope, dict):
            raise AssertionError("schema-v2 claim_scope must be structured")
        expected_scope_fields = {
            "ambient_dimension": 2,
            "maximum_coordinate_degree": 4,
            "sample_size": 9,
            "parameter_sets": "NINE_TERM_REAL_ARITHMETIC_PROGRESSIONS",
            "pairwise_distinctness_required": True,
            "convexity_used": False,
            "test_center_set_guaranteed_to_contain_a_non_rich_position_"
            "after_normalization": [
                "-4",
                "0",
                "3",
                "4",
            ],
        }
        for key, expected in expected_scope_fields.items():
            if claim_scope.get(key) != expected:
                raise AssertionError(
                    f"unexpected claim-scope field {key}: "
                    f"{claim_scope.get(key)!r} != {expected!r}"
                )
        exclusions = payload.get("does_not_check")
        required_exclusions = {
            "arbitrary or irregular real parameter sets",
            "polynomial parametrizations of degree greater than four",
            "higher-dimensional Euclidean samples",
            "general strictly convex polygons",
            "a proof or counterexample for Erdos Problem #97",
        }
        if not isinstance(exclusions, list) or not required_exclusions.issubset(exclusions):
            raise AssertionError("schema-v2 strict claim exclusions are incomplete")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write-artifact", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.write_artifact:
        payload = build_payload()
        args.artifact.parent.mkdir(parents=True, exist_ok=True)
        args.artifact.write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if args.check and load_json(args.artifact) != payload:
            raise AssertionError("serialized artifact differs from generated payload")
    elif args.check:
        stored = load_json(args.artifact)
        replayed = build_payload()
        if replayed != stored:
            raise AssertionError("stored quartic marked-root artifact differs from exact replay")
        payload = stored
    else:
        payload = load_json(args.artifact)

    check_payload(payload, assert_expected=args.assert_expected)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        full_gram_outcome = payload["post_hoc_full_gram_upgrade"]["outcome"]
        candidate_count = full_gram_outcome[
            "pairwise_distinct_planar_candidates_rich_at_all_four_test_centers"
        ]
        print(
            f"{payload['status']} pairwise_distinct_planar_candidates="
            f"{candidate_count}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
