#!/usr/bin/env python3
"""Compress the two persistent C25 circuits and audit exact affine reuse.

The source screen stores exact positive Kalmanson circuits for transfer-CEGAR
``probe:0`` and ``probe:1``.  This bounded follow-up samples a fixed number of
deterministic alternative LP objectives for each order, exactifies every
retained improvement, expands the best certificates through all
quotient-preserving affine maps, and measures exact coverage over all 144
currently stored C25 orders.

The objective search is bounded and non-exhaustive.  Only the retained exact
certificates, affine images, and coverage relations are mathematical outputs.
Nothing here establishes an all-order C25 obstruction, geometric
realizability, a counterexample, or a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
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
from compress_sparse_full_cone_c25_transfer_residuals import (  # noqa: E402
    minimum_affine_source_cover,
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
from probe_sparse_full_cone_c25_residual_seed_augmentation import (  # noqa: E402
    augmented_history,
    check_source_chain_references,
    packet_definitions,
    seed_packets,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    dihedral_order_key,
    order_record_hashes,
)
from run_sparse_full_cone_c25_transfer_cegar import (  # noqa: E402
    PATTERN,
    source_run,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    build_clause_orbit,
    clause_matches,
    file_sha256,
)
from screen_sparse_full_cone_c25_persistent_escapes import (  # noqa: E402
    check_payload as check_screen_payload,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_escape_screen_2026-07-30"
    / "summary.json"
)
DEFAULT_TRIAL_BUDGETS = (64, 64)
DEFAULT_SMALL_CIRCUIT_MAX_WIDTH = 12
PERSISTENT_TARGET_IDS = (
    "transfer_cegar_probe:0",
    "transfer_cegar_probe:1",
)


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def parse_trial_budgets(value: str) -> tuple[int, ...]:
    try:
        budgets = tuple(int(part) for part in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("trial budgets must be integers") from exc
    if not budgets or any(budget <= 0 for budget in budgets):
        raise argparse.ArgumentTypeError("trial budgets must be positive")
    return budgets


def load_source_chain(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Replay the source screen and recover its augmentation provenance."""

    screen = json.loads(source_path.read_text(encoding="utf-8"))
    check_screen_payload(screen)
    augmentation_path = ROOT / str(screen["source_augmentation_artifact"])
    if file_sha256(augmentation_path) != str(screen["source_augmentation_sha256"]):
        raise AssertionError("persistent compression augmentation hash drifted")
    augmentation = json.loads(augmentation_path.read_text(encoding="utf-8"))
    compression, cegar, transfer, first = check_source_chain_references(augmentation)
    return screen, augmentation, compression, cegar, transfer, first


def c25_first_run(first: Mapping[str, Any]) -> Mapping[str, Any]:
    runs = [run for run in first["runs"] if str(run["pattern"]) == PATTERN]
    if len(runs) != 1:
        raise AssertionError("persistent compression requires one first C25 run")
    return runs[0]


def target_record(
    *,
    target_id: str,
    stream: str,
    model: Mapping[str, Any],
) -> dict[str, object]:
    order = [int(label) for label in model["order"]]
    hashes = order_record_hashes(order)
    if any(model[field] != value for field, value in hashes.items()):
        raise AssertionError("persistent compression target order hash drifted")
    return {
        "target_id": target_id,
        "stream": stream,
        "order": order,
        **hashes,
        "strong_lightweight_survivor": bool(
            model["lightweight_filters"]["survives"]
        ),
    }


def current_c25_targets(
    augmentation: Mapping[str, Any],
    cegar: Mapping[str, Any],
    transfer: Mapping[str, Any],
    first: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Return the complete 112-order history plus the 32 latest probe orders."""

    transfer_run = source_run(transfer)
    first_run = c25_first_run(first)
    targets = []
    packets: Sequence[tuple[str, str, Sequence[Mapping[str, Any]]]] = (
        ("prior", "packet_order_id", transfer_run["prior_packet"]["records"]),
        (
            "first_fresh",
            "fresh_model_index",
            first_run["fresh_stream"]["models"],
        ),
        (
            "second_fresh",
            "fresh_model_index",
            transfer_run["second_fresh_stream"]["models"],
        ),
        (
            "transfer_cegar_probe",
            "probe_model_index",
            cegar["counterfactual_probe"]["models"],
        ),
        (
            "transfer_cegar_residual",
            "model_index",
            cegar["seeded_cegar"]["models"],
        ),
        (
            "augmentation_probe",
            "probe_model_index",
            augmentation["probe"]["models"],
        ),
    )
    for stream, index_key, models in packets:
        for model in models:
            raw_index = model[index_key]
            if stream in {"first_fresh", "second_fresh"}:
                order_id = f"fresh:{int(raw_index)}"
            else:
                order_id = str(raw_index)
            targets.append(
                target_record(
                    target_id=f"{stream}:{order_id}",
                    stream=stream,
                    model=model,
                )
            )

    ids = [str(target["target_id"]) for target in targets]
    if len(targets) != 144 or len(ids) != len(set(ids)):
        raise AssertionError("persistent compression requires 144 unique target ids")
    keys = [dihedral_order_key(target["order"]) for target in targets]
    if len(keys) != len(set(keys)):
        raise AssertionError("persistent compression target packet has duplicates")

    history = augmented_history(transfer, first, cegar)
    expected_history = [
        (
            str(record["history_id"]),
            str(record["order_sha256"]),
            str(record["dihedral_order_sha256"]),
        )
        for record in history
    ]
    actual_history = [
        (
            str(record["target_id"]),
            str(record["order_sha256"]),
            str(record["dihedral_order_sha256"]),
        )
        for record in targets[:112]
    ]
    if actual_history != expected_history:
        raise AssertionError("persistent compression 112-order history drifted")
    return targets


def source_model(record: Mapping[str, Any]) -> dict[str, object]:
    if record["classification"] != "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE":
        raise AssertionError("persistent compression source is not a circuit")
    return {
        "model_index": int(record["probe_model_index"]),
        "order": [int(label) for label in record["order"]],
        "full_kalmanson": {
            "positive_inequalities": int(record["positive_inequalities"]),
            "certificate": record["certificate"],
        },
    }


def existing_seed_packet(
    compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[dict[str, object], list[ClauseOrbit]]:
    (
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    ) = seed_packets(compression, transfer)
    packets = packet_definitions(
        transferred_orbits,
        residual_records,
        residual_orbits,
    )
    all_orbits = packets["transferred_plus_all_residuals"]
    hashes = [orbit.canonical_clause_sha256 for orbit in all_orbits]
    if len(hashes) != len(set(hashes)):
        raise AssertionError("persistent compression seed hashes are duplicated")
    summary = {
        "transferred_seed_orbit_count": len(transferred_records),
        "compressed_residual_seed_orbit_count": len(residual_records),
        "all_seed_orbit_count": len(all_orbits),
        "all_seed_exact_affine_image_count": sum(
            orbit.affine_map_count for orbit in all_orbits
        ),
        "canonical_clause_sha256s": hashes,
    }
    return summary, all_orbits


def compression_summary(
    rows: Sequence[Mapping[str, Any]],
    *,
    small_circuit_max_width: int,
) -> dict[str, object]:
    source_widths = [int(row["source_unique_ordered_quad_count"]) for row in rows]
    compressed_widths = [
        int(row["compressed_unique_ordered_quad_count"]) for row in rows
    ]
    return {
        "source_count": len(rows),
        "source_widths": source_widths,
        "compressed_widths": compressed_widths,
        "exact_improvement_count": sum(
            compressed < source
            for source, compressed in zip(source_widths, compressed_widths)
        ),
        "minimum_compressed_width": min(compressed_widths),
        "maximum_compressed_width": max(compressed_widths),
        "compressed_width_at_most_threshold_count": sum(
            width <= small_circuit_max_width for width in compressed_widths
        ),
        "existing_seed_orbit_match_count": sum(
            bool(row["matches_existing_seed_orbit"]) for row in rows
        ),
    }


def compress_sources(
    screen: Mapping[str, Any],
    targets: Sequence[Mapping[str, Any]],
    existing_seed_orbits: Sequence[ClauseOrbit],
    *,
    trial_budgets: Sequence[int],
    seed: int,
    model_seed_stride: int,
    tolerance: float,
) -> list[dict[str, object]]:
    records = screen["records"]
    if len(records) != 2 or len(trial_budgets) != len(records):
        raise AssertionError("persistent compression requires two source budgets")
    n, offsets = PATTERNS[PATTERN]
    seed_hashes = {
        orbit.canonical_clause_sha256 for orbit in existing_seed_orbits
    }
    rows = []
    for ordinal, record in enumerate(records):
        model_index = int(record["probe_model_index"])
        model_seed = seed + model_index * model_seed_stride
        trial_budget = int(trial_budgets[ordinal])
        compressed = compress_model(
            PATTERN,
            n,
            offsets,
            source_model(record),
            trials=trial_budget,
            seed=model_seed,
            tolerance=tolerance,
        )
        certificate = compressed["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        source_target_id = f"transfer_cegar_probe:{model_index}"
        hashes = quotient_vector_hashes(certificate)
        compressed.update(
            {
                "source_target_id": source_target_id,
                "source_screen_target_id": str(record["target_id"]),
                "source_certificate_sha256": str(record["certificate_sha256"]),
                "compressed_certificate_sha256": stable_json_sha256(certificate),
                "random_objective_seed": model_seed,
                "random_objective_trial_budget": trial_budget,
                "affine_clause_orbit": orbit.summary(),
                "matches_existing_seed_orbit": (
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
    return rows


def coverage_comparison(
    rows: Sequence[Mapping[str, Any]],
    targets: Sequence[Mapping[str, Any]],
    existing_seed_orbits: Sequence[ClauseOrbit],
) -> dict[str, object]:
    new_coverage = aggregate_coverage(rows, targets)
    new_by_target = {
        str(record["target_id"]): record
        for record in new_coverage["target_coverage"]
    }
    target_rows = []
    for target in targets:
        target_id = str(target["target_id"])
        matches = clause_matches(target["order"], existing_seed_orbits)
        existing_occurrences = sum(
            int(match["matching_orbit_clause_count"]) for match in matches
        )
        new = new_by_target[target_id]
        new_sources = [
            str(value) for value in new["translated_orbit_covering_source_ids"]
        ]
        target_rows.append(
            {
                "target_id": target_id,
                "stream": str(target["stream"]),
                "existing_seed_covered": bool(matches),
                "existing_seed_matching_orbit_count": len(matches),
                "existing_seed_matching_clause_occurrences": existing_occurrences,
                "new_compressed_direct_covering_source_ids": [
                    str(value) for value in new["direct_covering_source_ids"]
                ],
                "new_compressed_affine_covering_source_ids": new_sources,
                "new_compressed_affine_covered": bool(new_sources),
                "combined_seed_covered": bool(matches or new_sources),
                "new_marginal_over_existing_seeds": bool(new_sources and not matches),
            }
        )

    streams = []
    for stream in sorted({str(target["stream"]) for target in targets}):
        selected = [row for row in target_rows if row["stream"] == stream]
        streams.append(
            {
                "stream": stream,
                "target_count": len(selected),
                "existing_seed_covered_target_count": sum(
                    bool(row["existing_seed_covered"]) for row in selected
                ),
                "new_compressed_affine_covered_target_count": sum(
                    bool(row["new_compressed_affine_covered"]) for row in selected
                ),
                "combined_seed_covered_target_count": sum(
                    bool(row["combined_seed_covered"]) for row in selected
                ),
                "new_marginal_target_count": sum(
                    bool(row["new_marginal_over_existing_seeds"]) for row in selected
                ),
            }
        )

    existing_uncovered = sorted(
        str(row["target_id"])
        for row in target_rows
        if not bool(row["existing_seed_covered"])
    )
    marginal = sorted(
        str(row["target_id"])
        for row in target_rows
        if bool(row["new_marginal_over_existing_seeds"])
    )
    combined_uncovered = sorted(
        str(row["target_id"])
        for row in target_rows
        if not bool(row["combined_seed_covered"])
    )
    return {
        "target_order_count": len(targets),
        "existing_seed_covered_target_count": sum(
            bool(row["existing_seed_covered"]) for row in target_rows
        ),
        "new_compressed_affine_covered_target_count": sum(
            bool(row["new_compressed_affine_covered"]) for row in target_rows
        ),
        "combined_seed_covered_target_count": sum(
            bool(row["combined_seed_covered"]) for row in target_rows
        ),
        "existing_seed_uncovered_target_ids": existing_uncovered,
        "new_marginal_target_ids": marginal,
        "combined_seed_uncovered_target_ids": combined_uncovered,
        "streams": streams,
        "target_coverage": target_rows,
        "new_source_coverage": new_coverage,
        "minimum_affine_source_covers": {
            "persistent_targets": minimum_affine_source_cover(
                rows,
                PERSISTENT_TARGET_IDS,
            ),
            "new_marginal_targets": minimum_affine_source_cover(
                rows,
                marginal,
            ),
            "all_existing_seed_uncovered_targets": minimum_affine_source_cover(
                rows,
                existing_uncovered,
            ),
        },
    }


def stopping_assessment(
    rows: Sequence[Mapping[str, Any]],
    comparison: Mapping[str, Any],
    *,
    small_circuit_max_width: int,
) -> dict[str, object]:
    new_small = sorted(
        str(row["source_target_id"])
        for row in rows
        if int(row["compressed_unique_ordered_quad_count"])
        <= small_circuit_max_width
        and not bool(row["matches_existing_seed_orbit"])
    )
    covers = comparison["minimum_affine_source_covers"]
    persistent_cover = covers["persistent_targets"]
    marginal_cover = covers["new_marginal_targets"]
    persistent_selected = [
        str(value) for value in persistent_cover["selected_source_target_ids"]
    ]
    selected = [
        str(value) for value in marginal_cover["selected_source_target_ids"]
    ]
    if (
        marginal_cover["status"] == "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND"
        and selected
        and new_small
    ):
        decision = (
            "ADD_MINIMUM_COMPRESSED_MARGINAL_COVER_BEFORE_C25_ORDER_SEARCH"
        )
    else:
        decision = "STOP_BEFORE_C25_ORDER_SEARCH_FOR_COMPRESSION_REVIEW"
    return {
        "small_circuit_max_width": small_circuit_max_width,
        "new_small_source_target_ids": new_small,
        "persistent_target_ids": list(PERSISTENT_TARGET_IDS),
        "minimum_persistent_cover_source_target_ids": persistent_selected,
        "minimum_new_marginal_cover_source_target_ids": selected,
        "new_marginal_target_ids": comparison["new_marginal_target_ids"],
        "decision": decision,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    screen, augmentation, compression, cegar, transfer, first = load_source_chain(
        source_path
    )
    targets = current_c25_targets(augmentation, cegar, transfer, first)
    seed_summary, seed_orbits = existing_seed_packet(compression, transfer)
    rows = compress_sources(
        screen,
        targets,
        seed_orbits,
        trial_budgets=args.trial_budgets,
        seed=args.seed,
        model_seed_stride=args.model_seed_stride,
        tolerance=args.tolerance,
    )
    comparison = coverage_comparison(rows, targets, seed_orbits)
    assessment = stopping_assessment(
        rows,
        comparison,
        small_circuit_max_width=args.small_circuit_max_width,
    )
    n, offsets = PATTERNS[PATTERN]
    augmentation_path = ROOT / str(screen["source_augmentation_artifact"])
    return {
        "type": "sparse_full_cone_c25_persistent_escape_compression_v1",
        "trust": "EXACT_COMPRESSED_CERTIFICATES_AND_AFFINE_COVERAGE_IN_BOUNDED_PACKET",
        "status": "BOUNDED_C25_PERSISTENT_CIRCUIT_COMPRESSION_AND_REUSE_DIAGNOSTIC",
        "claim_scope": (
            "Deterministic-budget alternative-objective compression of two "
            "exact positive circuits for fixed C25 transfer-CEGAR orders, "
            "followed by exact direct and quotient-preserving affine coverage "
            "over 144 stored C25 orders. Retained certificates, affine images, "
            "coverage relations, and minimum covers are exact for this finite "
            "packet. The objective search is not exhaustive and this is not an "
            "all-order C25 obstruction, geometric realizability result, proof "
            "of Erdos Problem #97, counterexample, or official/global update."
        ),
        "source_screen_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_screen_sha256": file_sha256(source_path),
        "source_augmentation_artifact": augmentation_path.relative_to(ROOT).as_posix(),
        "source_augmentation_sha256": file_sha256(augmentation_path),
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "configuration": {
            "trial_budgets_by_source_ordinal": list(args.trial_budgets),
            "seed": args.seed,
            "per_model_seed_stride": args.model_seed_stride,
            "tolerance": args.tolerance,
            "small_circuit_max_width": args.small_circuit_max_width,
            "target_order_selection": (
                "all 112 stored history orders plus all 32 residual-augmentation "
                "probe orders"
            ),
            "stopping_rule": (
                "add the exact minimum compressed source-orbit cover of every "
                "target marginal over all eleven existing seeds when at least "
                "one retained circuit is new relative to those seeds and has "
                "width at most the configured threshold"
            ),
        },
        "existing_seed_packet": seed_summary,
        "target_orders": targets,
        "compressed_models": rows,
        "compression_summary": compression_summary(
            rows,
            small_circuit_max_width=args.small_circuit_max_width,
        ),
        "coverage_comparison": comparison,
        "quotient_vector_reuse": quotient_vector_reuse(rows),
        "stopping_assessment": assessment,
        "decision": assessment["decision"],
        "next_target": (
            "Run a bounded 144-history-blocked C25 order CEGAR using the three "
            "transferred seed orbits plus only the exact minimum compressed "
            "new-marginal cover; keep the eight zero-marginal residual "
            "orbits inactive."
        ),
    }


def validate_search_provenance(
    row: Mapping[str, Any],
    *,
    trial_budget: int,
    expected_seed: int,
) -> None:
    if int(row["random_objective_trial_budget"]) != trial_budget:
        raise AssertionError("persistent compression trial budget drifted")
    if int(row["trial_count"]) != trial_budget:
        raise AssertionError("persistent compression trial count drifted")
    if int(row["random_objective_seed"]) != expected_seed:
        raise AssertionError("persistent compression objective seed drifted")
    histogram = {
        int(size): int(count)
        for size, count in row["numerical_support_size_histogram"].items()
    }
    successful = int(row["successful_numerical_trials"])
    if sum(histogram.values()) != successful or not 0 <= successful <= trial_budget:
        raise AssertionError("persistent compression numerical trials drifted")
    if row["numerical_support_size_min"] != (
        min(histogram) if histogram else None
    ):
        raise AssertionError("persistent compression support minimum drifted")
    if row["numerical_support_size_max"] != (
        max(histogram) if histogram else None
    ):
        raise AssertionError("persistent compression support maximum drifted")
    previous_trial = -1
    previous_width = int(row["source_unique_ordered_quad_count"])
    for improvement in row["exact_improvements"]:
        trial = int(improvement["trial"])
        width = int(improvement["unique_ordered_quad_count"])
        if not previous_trial < trial < trial_budget:
            raise AssertionError("persistent compression improvement trial drifted")
        if int(improvement["seed"]) != expected_seed + trial:
            raise AssertionError("persistent compression improvement seed drifted")
        if not 0 < width < previous_width:
            raise AssertionError("persistent compression improvement width drifted")
        if int(improvement["positive_inequalities"]) <= 0:
            raise AssertionError("persistent compression support drifted")
        previous_trial = trial
        previous_width = width
    if row["best_trial"] != (
        previous_trial if row["exact_improvements"] else None
    ):
        raise AssertionError("persistent compression best trial drifted")
    if previous_width != int(row["compressed_unique_ordered_quad_count"]):
        raise AssertionError("persistent compression terminal width drifted")


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    expected_type = "sparse_full_cone_c25_persistent_escape_compression_v1"
    if payload["type"] != expected_type:
        raise AssertionError("persistent compression artifact type drifted")
    source_path = ROOT / str(payload["source_screen_artifact"])
    if file_sha256(source_path) != str(payload["source_screen_sha256"]):
        raise AssertionError("persistent compression screen hash drifted")
    screen, augmentation, compression, cegar, transfer, first = load_source_chain(
        source_path
    )
    augmentation_path = ROOT / str(payload["source_augmentation_artifact"])
    if augmentation_path != ROOT / str(screen["source_augmentation_artifact"]):
        raise AssertionError("persistent compression augmentation path drifted")
    if file_sha256(augmentation_path) != str(payload["source_augmentation_sha256"]):
        raise AssertionError("persistent compression augmentation hash drifted")

    n, offsets = PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or int(payload["n"]) != n:
        raise AssertionError("persistent compression pattern drifted")
    if payload["circulant_offsets"] != list(offsets):
        raise AssertionError("persistent compression offsets drifted")
    targets = current_c25_targets(augmentation, cegar, transfer, first)
    if payload["target_orders"] != targets:
        raise AssertionError("persistent compression target packet drifted")
    seed_summary, seed_orbits = existing_seed_packet(compression, transfer)
    if payload["existing_seed_packet"] != seed_summary:
        raise AssertionError("persistent compression seed packet drifted")

    configuration = payload["configuration"]
    budgets = [
        int(value) for value in configuration["trial_budgets_by_source_ordinal"]
    ]
    if budgets != list(DEFAULT_TRIAL_BUDGETS):
        raise AssertionError("persistent compression budgets drifted")
    base_seed = int(configuration["seed"])
    stride = int(configuration["per_model_seed_stride"])
    threshold = int(configuration["small_circuit_max_width"])
    records = screen["records"]
    rows = payload["compressed_models"]
    if len(rows) != len(records) or len(rows) != 2:
        raise AssertionError("persistent compression source count drifted")
    seed_hashes = {
        orbit.canonical_clause_sha256 for orbit in seed_orbits
    }
    verified_images = 0
    seen_indices: set[int] = set()
    for ordinal, (row, record) in enumerate(zip(rows, records, strict=True)):
        model_index = int(row["source_model_index"])
        if model_index in seen_indices or model_index != int(
            record["probe_model_index"]
        ):
            raise AssertionError("persistent compression source index drifted")
        seen_indices.add(model_index)
        source_target_id = f"transfer_cegar_probe:{model_index}"
        if row["source_target_id"] != source_target_id:
            raise AssertionError("persistent compression source target drifted")
        if row["source_screen_target_id"] != record["target_id"]:
            raise AssertionError("persistent compression screen target drifted")
        if row["order"] != record["order"]:
            raise AssertionError("persistent compression source order drifted")
        if row["source_certificate_sha256"] != record["certificate_sha256"]:
            raise AssertionError("persistent compression source hash drifted")
        if int(row["source_positive_inequalities"]) != int(
            record["positive_inequalities"]
        ):
            raise AssertionError("persistent compression source support drifted")
        source_quads = certificate_order_quads(record["certificate"], row["order"])
        if len(source_quads) != int(row["source_unique_ordered_quad_count"]):
            raise AssertionError("persistent compression source width drifted")
        expected_seed = base_seed + model_index * stride
        validate_search_provenance(
            row,
            trial_budget=budgets[ordinal],
            expected_seed=expected_seed,
        )

        certificate = row["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("persistent compressed certificate failed")
        if stable_json_sha256(certificate) != row["compressed_certificate_sha256"]:
            raise AssertionError("persistent compressed certificate hash drifted")
        if int(row["compressed_positive_inequalities"]) != checked.positive_inequalities:
            raise AssertionError("persistent compressed support drifted")
        quads = certificate_order_quads(certificate, row["order"])
        if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
            raise AssertionError("persistent compressed width drifted")
        reduction = len(source_quads) - len(quads)
        if reduction != int(row["quad_reduction"]):
            raise AssertionError("persistent compression reduction drifted")
        if float(row["quad_reduction_fraction"]) != reduction / len(source_quads):
            raise AssertionError("persistent compression fraction drifted")
        audit = positive_circuit_audit(certificate)
        if row["positive_circuit_audit"] != audit:
            raise AssertionError("persistent compression circuit audit drifted")
        if not bool(audit["positive_circuit_verified"]):
            raise AssertionError("persistent compressed support is not a circuit")
        if not bool(row["support_is_exact_positive_circuit"]):
            raise AssertionError("persistent compression circuit flag drifted")

        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        if row["affine_clause_orbit"] != orbit.summary():
            raise AssertionError("persistent compression affine orbit drifted")
        if bool(row["matches_existing_seed_orbit"]) != (
            orbit.canonical_clause_sha256 in seed_hashes
        ):
            raise AssertionError("persistent compression seed match drifted")
        hashes = quotient_vector_hashes(certificate)
        expected_vectors = {
            "unique_vector_count": len(hashes),
            "duplicate_inequality_vector_count": (
                checked.positive_inequalities - len(hashes)
            ),
            "hashes": hashes,
        }
        if row["quotient_vector_support"] != expected_vectors:
            raise AssertionError("persistent compression vector support drifted")
        expected_coverage = clause_coverage(
            certificate,
            orbit,
            targets,
            source_target_id=source_target_id,
        )
        if row["clause_coverage"] != expected_coverage:
            raise AssertionError("persistent compression coverage drifted")
        verified_images += orbit.affine_map_count

    if payload["compression_summary"] != compression_summary(
        rows,
        small_circuit_max_width=threshold,
    ):
        raise AssertionError("persistent compression summary drifted")
    comparison = coverage_comparison(rows, targets, seed_orbits)
    if payload["coverage_comparison"] != comparison:
        raise AssertionError("persistent compression comparison drifted")
    if payload["quotient_vector_reuse"] != quotient_vector_reuse(rows):
        raise AssertionError("persistent compression vector reuse drifted")
    assessment = stopping_assessment(
        rows,
        comparison,
        small_circuit_max_width=threshold,
    )
    if payload["stopping_assessment"] != assessment:
        raise AssertionError("persistent compression assessment drifted")
    if payload["decision"] != assessment["decision"]:
        raise AssertionError("persistent compression decision drifted")
    new_coverage = comparison["new_source_coverage"]
    return {
        "status": "OK",
        "verified_target_orders": len(targets),
        "verified_compressed_exact_certificates": len(rows),
        "verified_exact_affine_certificate_images": verified_images,
        "verified_direct_cross_coverage_edges": int(
            new_coverage["direct_cross_reuse_edge_count"]
        ),
        "verified_affine_cross_coverage_edges": int(
            new_coverage["translated_orbit_cross_reuse_edge_count"]
        ),
        "new_marginal_target_count": len(comparison["new_marginal_target_ids"]),
        "minimum_persistent_cover_source_count": int(
            comparison["minimum_affine_source_covers"]["persistent_targets"][
                "minimum_source_count"
            ]
        ),
        "minimum_new_marginal_cover_source_count": int(
            comparison["minimum_affine_source_covers"]["new_marginal_targets"][
                "minimum_source_count"
            ]
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
        help="comma-separated deterministic LP objective counts by source order",
    )
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument("--model-seed-stride", type=int, default=1_000)
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
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
    if (
        args.tolerance <= 0
        or args.model_seed_stride <= 0
        or args.small_circuit_max_width <= 0
    ):
        raise SystemExit("tolerance, seed stride, and threshold must be positive")
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
        summary = payload["compression_summary"]
        comparison = payload["coverage_comparison"]
        print(
            f"sources={summary['source_count']} "
            f"widths={summary['compressed_widths']} "
            f"marginal={len(comparison['new_marginal_target_ids'])} "
            f"decision={payload['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
