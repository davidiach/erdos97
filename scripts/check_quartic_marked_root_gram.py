#!/usr/bin/env python3
"""Generate and replay the exact fixed-grid quartic marked-root Gram pilot."""

from __future__ import annotations

import argparse
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from erdos97.quartic_marked_root_gram import (  # noqa: E402
    SCHEMA,
    equations_hold,
    gram_upper_from_coefficients,
    lifted_squared_distance,
    marked_root_divisibility_check,
    marked_row_equations,
    quartic_closure_pilot,
    rank_one_psd_check,
    second_derivative_has_constant_sign,
)


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
    summary = quartic_closure_pilot(
        parameters=PARAMETERS,
        anchor_centers=ANCHOR_CENTERS,
    )
    anchor = summary.anchor
    if summary.strict_finite_full_closure_candidate_count:
        status = "EXACT_FIXED_GRID_CLOSURE_CANDIDATE"
        trust = "EXACT_CERTIFICATE_DIAGNOSTIC"
    elif summary.unresolved_affine_state_count:
        status = "INCONCLUSIVE_FIXED_GRID_WITH_UNRESOLVED_AFFINE_STATES"
        trust = "EXACT_CERTIFICATE_DIAGNOSTIC"
    else:
        status = "NO_STRICTLY_CONVEX_DEGREE_FOUR_CLOSURE_ON_FIXED_GRID"
        trust = "EXACT_OBSTRUCTION"

    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "status": status,
        "trust": trust,
        "claim_scope": (
            "Exact fixed-parameter obstruction or survivor accounting for graph samples "
            "gamma(t)=(t,sum_{k=1}^4 a_k t^k) on T={-4,-3,...,4}."
        ),
        "does_not_check": [
            "arbitrary or irregular real parameter sets",
            "other nine-point x-coordinate grids",
            "polynomial graphs of degree greater than four",
            "parametric or implicit quartic curves",
            "multi-arc constructions",
            "general strictly convex polygons",
            "a proof or counterexample for Erdos Problem #97",
        ],
        "decisive_test_card": {
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
            "arithmetic": "fractions.Fraction exact rational elimination",
            "summary_type": type(summary).__name__,
        },
    }
    return normalize_payload(payload)


def check_payload(payload: dict[str, Any], *, assert_expected: bool) -> None:
    if payload.get("schema") != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload.get('schema')!r}")
    if payload.get("trust") not in {"EXACT_OBSTRUCTION", "EXACT_CERTIFICATE_DIAGNOSTIC"}:
        raise AssertionError(f"unexpected trust label: {payload.get('trust')!r}")
    anchor = payload.get("anchor_scan")
    outcome = payload.get("outcome")
    controls = payload.get("controls")
    if not isinstance(anchor, dict) or not isinstance(outcome, dict):
        raise AssertionError("artifact is missing anchor_scan or outcome")
    if not isinstance(controls, dict):
        raise AssertionError("artifact is missing controls")
    if anchor.get("raw_marked_triples") != 343000:
        raise AssertionError("expected 70^3 raw anchor triples")
    if anchor.get("raw_marked_triples") != (
        anchor.get("overlap_admissible_marked_triples", 0)
        + anchor.get("overlap_filtered_marked_triples", 0)
    ):
        raise AssertionError("anchor overlap accounting does not reconcile")
    if assert_expected:
        if payload.get("status") != "NO_STRICTLY_CONVEX_DEGREE_FOUR_CLOSURE_ON_FIXED_GRID":
            raise AssertionError(f"unexpected default status: {payload.get('status')!r}")
        if payload.get("trust") != "EXACT_OBSTRUCTION":
            raise AssertionError(f"unexpected default trust: {payload.get('trust')!r}")
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
        outcome = payload["outcome"]
        print(
            f"{payload['status']} unresolved={outcome['unresolved_affine_states']} "
            f"closures={outcome['strict_finite_full_closures']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
