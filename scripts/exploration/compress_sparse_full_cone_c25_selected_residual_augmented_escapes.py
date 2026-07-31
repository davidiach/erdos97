#!/usr/bin/env python3
"""Compress the eight C25 selected-residual augmented CEGAR escapes.

The source packet contains eight exact positive Kalmanson circuits learned
after 168 historical C25 orders and five active seed orbits were blocked. This
bounded follow-up samples deterministic alternative LP objectives, exactifies
every retained improvement, expands each compressed circuit through all
quotient-preserving translations, and measures exact reuse over the source
packet's sixteen probe orders and eight five-seed-escaping residual orders.

The objective search is deterministic-budget but not exhaustive. Retained
certificates, affine images, coverage relations, and minimum covers are exact
for this finite packet only. They do not prove an all-order obstruction,
geometric realizability, a counterexample, or Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from compress_sparse_full_cone_c25_persistent_augmented_residuals import (  # noqa: E402
    compression_summary,
)
from compress_sparse_full_cone_c25_persistent_escapes import (  # noqa: E402
    stable_json_sha256,
    validate_search_provenance,
)
from compress_sparse_full_cone_c25_transfer_residuals import (  # noqa: E402
    minimum_affine_source_cover,
    parse_trial_budgets,
)
from compress_sparse_full_cone_certificates import (  # noqa: E402
    compress_model,
    positive_circuit_audit,
)
from compress_sparse_full_cone_seeded_certificates import (  # noqa: E402
    aggregate_coverage,
    clause_coverage,
    quotient_vector_hashes,
    quotient_vector_reuse,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from run_sparse_full_cone_c25_selected_residual_augmented_cegar import (  # noqa: E402
    PATTERN,
    check_payload as check_source_payload,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    build_clause_orbit,
    file_sha256,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_selected_residual_augmented_cegar_2026-07-30"
    / "summary.json"
)
DEFAULT_TRIAL_BUDGETS = (64, 64, 112, 112, 112, 32, 32, 64)
DEFAULT_SMALL_CIRCUIT_MAX_WIDTH = 12
DEFAULT_SEED = 20_260_801
DEFAULT_MODEL_SEED_STRIDE = 1_000
DEFAULT_TOLERANCE = 1.0e-9
TARGET_ORDER_SELECTION = (
    "all 16 counterfactual probe and 8 five-seed residual models"
)
STOPPING_RULE = (
    "replace the selected width-three seed only when it has zero "
    "marginal target coverage beyond the four parent seeds and an "
    "exact minimum small new compressed residual cover completes "
    "the full source packet with those four parent seeds"
)
SELECTED_WIDTH3_SOURCE_TARGET_ID = "residual:2"
CONTINUE_DECISION = (
    "REPLACE_NONMARGINAL_WIDTH3_WITH_MINIMUM_COMPRESSED_ESCAPE_COVER"
)
REVIEW_DECISION = (
    "REVIEW_SELECTED_RESIDUAL_ESCAPE_COMPRESSION_BEFORE_CONTINUING"
)


def seed_indices(source: Mapping[str, Any]) -> tuple[set[int], int]:
    """Return the four parent source indices and selected width-three index."""

    parent = {
        int(record["source_model_index"])
        for record in source["transferred_seed_templates"]
    }
    parent.add(
        int(source["selected_persistent_seed_template"]["source_model_index"])
    )
    selected = int(
        source["selected_residual_seed_template"]["source_model_index"]
    )
    if len(parent) != 4 or selected in parent:
        raise AssertionError("selected-residual source seed indices drifted")
    return parent, selected


def active_seed_orbit_hashes(source: Mapping[str, Any]) -> set[str]:
    """Return canonical hashes for all five active source seed orbits."""

    records = [
        *source["transferred_seed_templates"],
        source["selected_persistent_seed_template"],
        source["selected_residual_seed_template"],
    ]
    hashes = {
        str(record["affine_clause_orbit"]["canonical_clause_sha256"])
        for record in records
    }
    if len(hashes) != 5:
        raise AssertionError("selected-residual active seed hashes drifted")
    return hashes


def target_orders(source: Mapping[str, Any]) -> list[dict[str, object]]:
    """Return the 16 probe and 8 five-seed-escaping residual orders."""

    parent_indices, selected_index = seed_indices(source)
    targets = []
    streams = (
        (
            "probe",
            "probe_model_index",
            source["counterfactual_probe"]["models"],
        ),
        ("residual", "model_index", source["seeded_cegar"]["models"]),
    )
    for stream, index_key, models in streams:
        for model in models:
            model_index = int(model[index_key])
            matches = model["seed_orbit_matches"]
            matched_sources = {
                int(match["source_model_index"]) for match in matches
            }
            parent_matches = matched_sources & parent_indices
            selected_matches = selected_index in matched_sources
            if len(matches) != len(parent_matches) + int(selected_matches):
                raise AssertionError("selected-residual seed match drifted")
            targets.append(
                {
                    "target_id": f"{stream}:{model_index}",
                    "stream": stream,
                    "model_index": model_index,
                    "order": [int(label) for label in model["order"]],
                    "order_sha256": str(model["order_sha256"]),
                    "dihedral_order_sha256": str(
                        model["dihedral_order_sha256"]
                    ),
                    "strong_lightweight_survivor": bool(
                        model["lightweight_filters"]["survives"]
                    ),
                    "parent_seed_orbit_match_count": len(parent_matches),
                    "selected_width3_seed_orbit_match_count": int(
                        selected_matches
                    ),
                    "active_seed_orbit_match_count": len(matches),
                }
            )
    ids = [str(target["target_id"]) for target in targets]
    dihedral = [str(target["dihedral_order_sha256"]) for target in targets]
    if len(ids) != 24 or len(ids) != len(set(ids)):
        raise AssertionError("selected-residual target identifiers drifted")
    if len(dihedral) != len(set(dihedral)):
        raise AssertionError("selected-residual target orders are duplicated")
    return targets


def coverage_comparison(
    rows: Sequence[Mapping[str, Any]],
    targets: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """Compare parent, selected, active, and compressed affine coverage."""

    compressed = aggregate_coverage(rows, targets)
    translated_by_target = {
        str(row["target_id"]): set(
            str(value)
            for value in row["translated_orbit_covering_source_ids"]
        )
        for row in compressed["target_coverage"]
    }
    target_rows = []
    for target in targets:
        target_id = str(target["target_id"])
        parent_covered = int(target["parent_seed_orbit_match_count"]) > 0
        selected_covered = (
            int(target["selected_width3_seed_orbit_match_count"]) > 0
        )
        active_covered = int(target["active_seed_orbit_match_count"]) > 0
        compressed_covered = bool(translated_by_target[target_id])
        target_rows.append(
            {
                "target_id": target_id,
                "stream": str(target["stream"]),
                "strong_lightweight_survivor": bool(
                    target["strong_lightweight_survivor"]
                ),
                "parent_seed_covered": parent_covered,
                "selected_width3_seed_covered": selected_covered,
                "active_seed_covered": active_covered,
                "compressed_affine_covered": compressed_covered,
                "selected_width3_marginal_over_parent": (
                    selected_covered and not parent_covered
                ),
                "compressed_marginal_over_active": (
                    compressed_covered and not active_covered
                ),
                "parent_plus_compressed_covered": (
                    parent_covered or compressed_covered
                ),
                "active_plus_compressed_covered": (
                    active_covered or compressed_covered
                ),
                "compressed_affine_covering_source_ids": sorted(
                    translated_by_target[target_id]
                ),
            }
        )

    parent_ids = [
        str(row["target_id"]) for row in target_rows if row["parent_seed_covered"]
    ]
    selected_ids = [
        str(row["target_id"])
        for row in target_rows
        if row["selected_width3_seed_covered"]
    ]
    active_ids = [
        str(row["target_id"]) for row in target_rows if row["active_seed_covered"]
    ]
    compressed_ids = [
        str(row["target_id"])
        for row in target_rows
        if row["compressed_affine_covered"]
    ]
    selected_marginal = [
        str(row["target_id"])
        for row in target_rows
        if row["selected_width3_marginal_over_parent"]
    ]
    compressed_marginal = [
        str(row["target_id"])
        for row in target_rows
        if row["compressed_marginal_over_active"]
    ]
    parent_plus_compressed = [
        str(row["target_id"])
        for row in target_rows
        if row["parent_plus_compressed_covered"]
    ]
    active_plus_compressed = [
        str(row["target_id"])
        for row in target_rows
        if row["active_plus_compressed_covered"]
    ]
    all_ids = [str(target["target_id"]) for target in targets]
    residual_ids = [
        str(target["target_id"])
        for target in targets
        if target["stream"] == "residual"
    ]
    return {
        "target_order_count": len(targets),
        "target_coverage": target_rows,
        "parent_seed_covered_target_count": len(parent_ids),
        "parent_seed_covered_target_ids": parent_ids,
        "selected_width3_seed_covered_target_count": len(selected_ids),
        "selected_width3_seed_covered_target_ids": selected_ids,
        "selected_width3_marginal_over_parent_target_ids": selected_marginal,
        "active_seed_covered_target_count": len(active_ids),
        "active_seed_covered_target_ids": active_ids,
        "compressed_affine_covered_target_count": len(compressed_ids),
        "compressed_affine_covered_target_ids": compressed_ids,
        "compressed_marginal_over_active_target_ids": compressed_marginal,
        "parent_plus_compressed_covered_target_count": len(
            parent_plus_compressed
        ),
        "parent_plus_compressed_uncovered_target_ids": sorted(
            set(all_ids) - set(parent_plus_compressed)
        ),
        "active_plus_compressed_covered_target_count": len(
            active_plus_compressed
        ),
        "active_plus_compressed_uncovered_target_ids": sorted(
            set(all_ids) - set(active_plus_compressed)
        ),
        "compressed_source_coverage": compressed,
        "minimum_affine_source_covers": {
            "residual_targets": minimum_affine_source_cover(
                rows,
                residual_ids,
            ),
            "compressed_marginal_over_active_targets": (
                minimum_affine_source_cover(rows, compressed_marginal)
            ),
        },
    }


def stopping_assessment(
    rows: Sequence[Mapping[str, Any]],
    comparison: Mapping[str, Any],
    *,
    small_circuit_max_width: int,
) -> dict[str, object]:
    """Select a replacement seed packet from exact bounded coverage."""

    new_small = sorted(
        str(row["source_target_id"])
        for row in rows
        if int(row["compressed_unique_ordered_quad_count"])
        <= small_circuit_max_width
        and not bool(row["matches_active_seed_orbit"])
    )
    residual_cover = comparison["minimum_affine_source_covers"][
        "residual_targets"
    ]
    selected = [
        str(value) for value in residual_cover["selected_source_target_ids"]
    ]
    selected_are_small_new = bool(selected) and set(selected) <= set(new_small)
    old_selected_marginal = comparison[
        "selected_width3_marginal_over_parent_target_ids"
    ]
    parent_replacement_complete = (
        int(comparison["parent_plus_compressed_covered_target_count"])
        == int(comparison["target_order_count"])
    )
    retire_old_selected = not old_selected_marginal
    if (
        residual_cover["status"]
        == "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND"
        and selected_are_small_new
        and retire_old_selected
        and parent_replacement_complete
    ):
        decision = CONTINUE_DECISION
    else:
        decision = REVIEW_DECISION
    return {
        "small_circuit_max_width": small_circuit_max_width,
        "new_small_source_target_ids": new_small,
        "minimum_residual_cover_source_target_ids": selected,
        "minimum_residual_cover_sources_are_new_and_small": selected_are_small_new,
        "selected_width3_marginal_target_ids": old_selected_marginal,
        "retire_selected_width3_seed": retire_old_selected,
        "parent_plus_replacement_cover_is_complete": (
            parent_replacement_complete
        ),
        "decision": decision,
    }


def compress_escapes(
    source: Mapping[str, Any],
    *,
    trial_budgets: Sequence[int],
    seed: int,
    model_seed_stride: int,
    tolerance: float,
    small_circuit_max_width: int,
) -> dict[str, object]:
    """Compress all eight source certificates and measure exact reuse."""

    models = source["seeded_cegar"]["models"]
    if len(models) != 8 or len(trial_budgets) != len(models):
        raise AssertionError("selected-residual compression requires eight budgets")
    n, offsets = PATTERNS[PATTERN]
    targets = target_orders(source)
    seed_hashes = active_seed_orbit_hashes(source)
    rows = []
    for model in models:
        model_index = int(model["model_index"])
        full = model["full_kalmanson"]
        if full.get("certificate") is None:
            raise AssertionError("selected-residual escape lacks certificate")
        model_seed = seed + model_index * model_seed_stride
        trial_budget = int(trial_budgets[model_index])
        compressed = compress_model(
            PATTERN,
            n,
            offsets,
            model,
            trials=trial_budget,
            seed=model_seed,
            tolerance=tolerance,
        )
        certificate = compressed["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        source_target_id = f"residual:{model_index}"
        hashes = quotient_vector_hashes(certificate)
        compressed.update(
            {
                "source_target_id": source_target_id,
                "source_certificate_sha256": str(
                    full["certificate_sha256"]
                ),
                "compressed_certificate_sha256": stable_json_sha256(
                    certificate
                ),
                "random_objective_seed": model_seed,
                "random_objective_trial_budget": trial_budget,
                "affine_clause_orbit": orbit.summary(),
                "matches_active_seed_orbit": (
                    orbit.canonical_clause_sha256 in seed_hashes
                ),
                "quotient_vector_support": {
                    "unique_vector_count": len(hashes),
                    "duplicate_inequality_vector_count": (
                        checked.positive_inequalities - len(hashes)
                    ),
                    "hashes": hashes,
                },
                "clause_coverage": clause_coverage(
                    certificate,
                    orbit,
                    targets,
                    source_target_id=source_target_id,
                ),
            }
        )
        rows.append(compressed)

    comparison = coverage_comparison(rows, targets)
    assessment = stopping_assessment(
        rows,
        comparison,
        small_circuit_max_width=small_circuit_max_width,
    )
    return {
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "target_orders": targets,
        "compressed_models": rows,
        "compression_summary": compression_summary(
            rows,
            small_circuit_max_width=small_circuit_max_width,
        ),
        "coverage_comparison": comparison,
        "quotient_vector_reuse": quotient_vector_reuse(rows),
        "stopping_assessment": assessment,
        "decision": assessment["decision"],
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_source_payload(source)
    run = compress_escapes(
        source,
        trial_budgets=args.trial_budgets,
        seed=args.seed,
        model_seed_stride=args.model_seed_stride,
        tolerance=args.tolerance,
        small_circuit_max_width=args.small_circuit_max_width,
    )
    return {
        "type": (
            "sparse_full_cone_c25_selected_residual_augmented_"
            "escape_compression_v1"
        ),
        "trust": "EXACT_COMPRESSED_CERTIFICATES_AND_AFFINE_COVERAGE_IN_BOUNDED_PACKET",
        "status": "BOUNDED_C25_SELECTED_RESIDUAL_ESCAPE_COMPRESSION",
        "claim_scope": (
            "Deterministic-budget alternative-objective compression of eight "
            "exact C25 five-seed-escaping circuits, followed by exact direct "
            "and quotient-preserving affine coverage over sixteen probe and "
            "eight residual orders. Retained certificates, affine images, "
            "coverage relations, and minimum covers are exact for this finite "
            "packet. The objective search is not exhaustive and this is not "
            "an all-order C25 obstruction, geometric realizability result, "
            "proof of Erdos Problem #97, counterexample, or official/global "
            "update."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "trial_budgets_by_model_index": list(args.trial_budgets),
            "seed": args.seed,
            "per_model_seed_stride": args.model_seed_stride,
            "tolerance": args.tolerance,
            "small_circuit_max_width": args.small_circuit_max_width,
            "target_order_selection": TARGET_ORDER_SELECTION,
            "stopping_rule": STOPPING_RULE,
        },
        "run": run,
        "decision": run["decision"],
        "next_target": (
            "Run a bounded 192-history-blocked C25 order CEGAR with the four "
            "parent seeds and only the exact minimum compressed escape cover "
            "selected here, retiring the nonmarginal prior width-three seed."
        ),
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    expected_type = (
        "sparse_full_cone_c25_selected_residual_augmented_"
        "escape_compression_v1"
    )
    if payload["type"] != expected_type:
        raise AssertionError("selected-residual compression type drifted")
    source_path = ROOT / str(payload["source_artifact"])
    if source_path.resolve() != DEFAULT_SOURCE.resolve():
        raise AssertionError("selected-residual source artifact drifted")
    configuration = payload["configuration"]
    expected_configuration = {
        "trial_budgets_by_model_index": list(DEFAULT_TRIAL_BUDGETS),
        "seed": DEFAULT_SEED,
        "per_model_seed_stride": DEFAULT_MODEL_SEED_STRIDE,
        "tolerance": DEFAULT_TOLERANCE,
        "small_circuit_max_width": DEFAULT_SMALL_CIRCUIT_MAX_WIDTH,
        "target_order_selection": TARGET_ORDER_SELECTION,
        "stopping_rule": STOPPING_RULE,
    }
    if configuration != expected_configuration:
        raise AssertionError("selected-residual configuration drifted")
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("selected-residual compression source hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_source_payload(source)

    budgets = list(DEFAULT_TRIAL_BUDGETS)
    base_seed = DEFAULT_SEED
    stride = DEFAULT_MODEL_SEED_STRIDE
    small_width = DEFAULT_SMALL_CIRCUIT_MAX_WIDTH

    targets = target_orders(source)
    run = payload["run"]
    if run["target_orders"] != targets:
        raise AssertionError("selected-residual target packet drifted")
    n, offsets = PATTERNS[PATTERN]
    if run["pattern"] != PATTERN or int(run["n"]) != n:
        raise AssertionError("selected-residual pattern drifted")
    if run["circulant_offsets"] != list(offsets):
        raise AssertionError("selected-residual offsets drifted")

    source_models = {
        int(model["model_index"]): model
        for model in source["seeded_cegar"]["models"]
    }
    rows = run["compressed_models"]
    if len(source_models) != 8 or len(rows) != len(source_models):
        raise AssertionError("selected-residual source count drifted")
    seed_hashes = active_seed_orbit_hashes(source)
    checked_rows = []
    verified_images = 0
    seen_indices: set[int] = set()
    for row in rows:
        model_index = int(row["source_model_index"])
        if model_index in seen_indices or model_index not in source_models:
            raise AssertionError("selected-residual source index drifted")
        seen_indices.add(model_index)
        source_model = source_models[model_index]
        source_full = source_model["full_kalmanson"]
        source_target_id = f"residual:{model_index}"
        if row["source_target_id"] != source_target_id:
            raise AssertionError("selected-residual target id drifted")
        order = [int(label) for label in row["order"]]
        if order != [int(label) for label in source_model["order"]]:
            raise AssertionError("selected-residual source order drifted")
        if row["source_certificate_sha256"] != source_full["certificate_sha256"]:
            raise AssertionError("selected-residual source hash drifted")
        if int(row["source_positive_inequalities"]) != int(
            source_full["positive_inequalities"]
        ):
            raise AssertionError("selected-residual source support drifted")
        trial_budget = budgets[model_index]
        expected_seed = base_seed + model_index * stride
        validate_search_provenance(
            row,
            trial_budget=trial_budget,
            expected_seed=expected_seed,
        )

        certificate = row["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("selected-residual compressed escape failed")
        if stable_json_sha256(certificate) != row["compressed_certificate_sha256"]:
            raise AssertionError("selected-residual compressed hash drifted")
        if int(row["compressed_positive_inequalities"]) != (
            checked.positive_inequalities
        ):
            raise AssertionError("selected-residual compressed support drifted")
        quads = certificate_order_quads(certificate, order)
        if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
            raise AssertionError("selected-residual compressed width drifted")
        source_quads = certificate_order_quads(source_full["certificate"], order)
        if len(source_quads) != int(row["source_unique_ordered_quad_count"]):
            raise AssertionError("selected-residual source width drifted")
        reduction = len(source_quads) - len(quads)
        if reduction != int(row["quad_reduction"]):
            raise AssertionError("selected-residual reduction drifted")
        if float(row["quad_reduction_fraction"]) != reduction / len(
            source_quads
        ):
            raise AssertionError("selected-residual reduction fraction drifted")
        audit = positive_circuit_audit(certificate)
        if row["positive_circuit_audit"] != audit:
            raise AssertionError("selected-residual circuit audit drifted")
        if not bool(audit["positive_circuit_verified"]):
            raise AssertionError("selected-residual escape is not a circuit")
        if not bool(row["support_is_exact_positive_circuit"]):
            raise AssertionError("selected-residual circuit flag drifted")

        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        if row["affine_clause_orbit"] != orbit.summary():
            raise AssertionError("selected-residual affine orbit drifted")
        if bool(row["matches_active_seed_orbit"]) != (
            orbit.canonical_clause_sha256 in seed_hashes
        ):
            raise AssertionError("selected-residual active seed match drifted")
        hashes = quotient_vector_hashes(certificate)
        expected_vectors = {
            "unique_vector_count": len(hashes),
            "duplicate_inequality_vector_count": (
                checked.positive_inequalities - len(hashes)
            ),
            "hashes": hashes,
        }
        if row["quotient_vector_support"] != expected_vectors:
            raise AssertionError("selected-residual vector support drifted")
        expected_coverage = clause_coverage(
            certificate,
            orbit,
            targets,
            source_target_id=source_target_id,
        )
        if row["clause_coverage"] != expected_coverage:
            raise AssertionError("selected-residual coverage drifted")
        checked_rows.append(row)
        verified_images += orbit.affine_map_count

    if seen_indices != set(source_models):
        raise AssertionError("selected-residual source set drifted")
    if run["compression_summary"] != compression_summary(
        checked_rows,
        small_circuit_max_width=small_width,
    ):
        raise AssertionError("selected-residual compression summary drifted")
    comparison = coverage_comparison(checked_rows, targets)
    if run["coverage_comparison"] != comparison:
        raise AssertionError("selected-residual coverage comparison drifted")
    if run["quotient_vector_reuse"] != quotient_vector_reuse(checked_rows):
        raise AssertionError("selected-residual vector reuse drifted")
    assessment = stopping_assessment(
        checked_rows,
        comparison,
        small_circuit_max_width=small_width,
    )
    if run["stopping_assessment"] != assessment:
        raise AssertionError("selected-residual assessment drifted")
    if run["decision"] != assessment["decision"]:
        raise AssertionError("selected-residual run decision drifted")
    if payload["decision"] != assessment["decision"]:
        raise AssertionError("selected-residual payload decision drifted")

    compressed = comparison["compressed_source_coverage"]
    residual_cover = comparison["minimum_affine_source_covers"][
        "residual_targets"
    ]
    return {
        "status": "OK",
        "verified_target_orders": len(targets),
        "verified_compressed_exact_certificates": len(checked_rows),
        "verified_exact_affine_certificate_images": verified_images,
        "verified_direct_cross_coverage_edges": int(
            compressed["direct_cross_reuse_edge_count"]
        ),
        "verified_affine_cross_coverage_edges": int(
            compressed["translated_orbit_cross_reuse_edge_count"]
        ),
        "selected_width3_marginal_target_count": len(
            comparison["selected_width3_marginal_over_parent_target_ids"]
        ),
        "minimum_residual_cover_source_count": int(
            residual_cover["minimum_source_count"]
        ),
        "decision": str(assessment["decision"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--trial-budgets",
        type=parse_trial_budgets,
        default=DEFAULT_TRIAL_BUDGETS,
        help="comma-separated deterministic LP objective counts by model index",
    )
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument(
        "--model-seed-stride",
        type=int,
        default=DEFAULT_MODEL_SEED_STRIDE,
    )
    parser.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE)
    parser.add_argument(
        "--small-circuit-max-width",
        type=int,
        default=DEFAULT_SMALL_CIRCUIT_MAX_WIDTH,
    )
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if len(args.trial_budgets) != 8 or any(
        value <= 0 for value in args.trial_budgets
    ):
        raise SystemExit("selected-residual compression needs 8 positive budgets")
    if args.model_seed_stride <= 0 or args.small_circuit_max_width <= 0:
        raise SystemExit("selected-residual compression limits must be positive")
    if args.check is not None:
        path = args.check if args.check.is_absolute() else ROOT / args.check
        payload = json.loads(path.read_text(encoding="utf-8"))
        print(json.dumps(check_payload(payload), indent=2, sort_keys=True))
        return 0

    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        path = args.out if args.out.is_absolute() else ROOT / args.out
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    if args.json or args.out is None:
        print(text, end="")
    else:
        run = payload["run"]
        comparison = run["coverage_comparison"]
        residual_cover = comparison["minimum_affine_source_covers"][
            "residual_targets"
        ]
        print(
            f"{PATTERN}: "
            f"widths={run['compression_summary']['compressed_widths']} "
            f"selected_width3_marginal="
            f"{len(comparison['selected_width3_marginal_over_parent_target_ids'])} "
            f"combined="
            f"{comparison['parent_plus_compressed_covered_target_count']}/"
            f"{comparison['target_order_count']} "
            f"minimum_residual_cover="
            f"{residual_cover['minimum_source_count']} "
            f"decision={payload['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
