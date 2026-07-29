#!/usr/bin/env python3
"""Compress the eight C25 transfer-CEGAR residual certificates.

The source packet contains eight exact positive Kalmanson circuits learned
after three transferred C25 clause orbits and 88 prior orders were blocked.
This bounded follow-up samples deterministic alternative LP objectives for
each of those eight fixed orders, exactifies every retained improvement,
expands each compressed circuit through the quotient-preserving translations,
and measures exact coverage across the source packet's sixteen probe orders
and eight residual orders.

The randomized objective search is not exhaustive.  Every retained
certificate and affine image is exact, but the results remain fixed-pattern,
fixed-order diagnostics.  They do not prove an all-order obstruction,
geometric realizability, a counterexample, or Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
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
from run_sparse_full_cone_c25_transfer_cegar import (  # noqa: E402
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
    / "sparse_full_cone_c25_transfer_cegar_2026-08-03"
    / "summary.json"
)
DEFAULT_TRIAL_BUDGETS = (32, 32, 32, 32, 64, 64, 32, 112)
DEFAULT_SMALL_CIRCUIT_MAX_WIDTH = 12


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


def target_orders(source: Mapping[str, Any]) -> list[dict[str, object]]:
    """Return the 16 probe and 8 residual orders used for exact coverage."""

    targets = []
    streams = (
        ("probe", "probe_model_index", source["counterfactual_probe"]["models"]),
        ("seeded", "model_index", source["seeded_cegar"]["models"]),
    )
    for stream, index_key, models in streams:
        for model in models:
            model_index = int(model[index_key])
            targets.append(
                {
                    "target_id": f"{stream}:{model_index}",
                    "stream": stream,
                    "model_index": model_index,
                    "order": [int(label) for label in model["order"]],
                    "order_sha256": str(model["order_sha256"]),
                    "strong_lightweight_survivor": bool(
                        model["lightweight_filters"]["survives"]
                    ),
                    "transferred_seed_orbit_match_count": len(
                        model["seed_orbit_matches"]
                    ),
                }
            )
    ids = [str(target["target_id"]) for target in targets]
    if len(ids) != len(set(ids)):
        raise AssertionError("C25 residual target identifiers are not unique")
    return targets


def active_seed_orbit_hashes(source: Mapping[str, Any]) -> set[str]:
    hashes = {
        str(record["canonical_clause_sha256"]) for record in source["seed_templates"]
    }
    if len(hashes) != len(source["seed_templates"]):
        raise AssertionError("active C25 seed orbit hashes are not distinct")
    return hashes


def coverage_by_stream(
    rows: Sequence[Mapping[str, Any]],
    targets: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    """Summarize exact direct and affine coverage by target stream."""

    aggregate = aggregate_coverage(rows, targets)
    target_coverage = {
        str(record["target_id"]): record for record in aggregate["target_coverage"]
    }
    streams = []
    for stream in sorted({str(target["stream"]) for target in targets}):
        stream_targets = [
            target for target in targets if str(target["stream"]) == stream
        ]
        direct_edges = 0
        affine_edges = 0
        direct_covered = 0
        affine_covered = 0
        for target in stream_targets:
            target_id = str(target["target_id"])
            coverage = target_coverage[target_id]
            direct_sources = [
                str(value) for value in coverage["direct_covering_source_ids"]
            ]
            affine_sources = [
                str(value) for value in coverage["translated_orbit_covering_source_ids"]
            ]
            direct_covered += int(bool(direct_sources))
            affine_covered += int(bool(affine_sources))
            direct_edges += sum(source != target_id for source in direct_sources)
            affine_edges += sum(source != target_id for source in affine_sources)
        streams.append(
            {
                "stream": stream,
                "target_count": len(stream_targets),
                "direct_covered_target_count": direct_covered,
                "affine_covered_target_count": affine_covered,
                "direct_cross_coverage_edge_count": direct_edges,
                "affine_cross_coverage_edge_count": affine_edges,
            }
        )

    seed_uncovered_probe_ids = sorted(
        str(target["target_id"])
        for target in targets
        if str(target["stream"]) == "probe"
        and int(target["transferred_seed_orbit_match_count"]) == 0
    )
    return {
        "streams": streams,
        "transferred_seed_uncovered_probe_target_ids": seed_uncovered_probe_ids,
        "compressed_direct_covered_seed_uncovered_probe_target_ids": [
            target_id
            for target_id in seed_uncovered_probe_ids
            if target_coverage[target_id]["direct_covering_source_ids"]
        ],
        "compressed_affine_covered_seed_uncovered_probe_target_ids": [
            target_id
            for target_id in seed_uncovered_probe_ids
            if target_coverage[target_id]["translated_orbit_covering_source_ids"]
        ],
    }


def minimum_affine_source_cover(
    rows: Sequence[Mapping[str, Any]],
    target_ids: Sequence[str],
) -> dict[str, object]:
    """Enumerate the exact minimum source-orbit cover of a target subset."""

    requested = set(target_ids)
    source_cover: dict[str, set[str]] = {}
    source_width: dict[str, int] = {}
    for row in rows:
        source = str(row["source_target_id"])
        source_cover[source] = {
            str(record["target_id"])
            for record in row["clause_coverage"]["translated_orbit_covered_targets"]
            if str(record["target_id"]) in requested
        }
        source_width[source] = int(row["compressed_unique_ordered_quad_count"])

    coverable = set().union(*source_cover.values()) if source_cover else set()
    uncovered = sorted(requested - coverable)
    common = {
        "target_ids": sorted(requested),
        "target_count": len(requested),
        "coverable_target_count": len(requested) - len(uncovered),
        "uncovered_target_ids": uncovered,
    }
    if uncovered:
        return {
            **common,
            "status": "TARGET_SET_NOT_COVERED_BY_STORED_AFFINE_ORBITS",
            "minimum_source_count": None,
            "minimum_total_width": None,
            "selected_source_target_ids": [],
        }

    sources = sorted(source_cover)
    best: tuple[int, tuple[str, ...]] | None = None
    for count in range(len(sources) + 1):
        for selected in combinations(sources, count):
            covered = set().union(*(source_cover[source] for source in selected))
            if requested <= covered:
                candidate = (
                    sum(source_width[source] for source in selected),
                    selected,
                )
                if best is None or candidate < best:
                    best = candidate
        if best is not None:
            break
    if best is None:
        raise AssertionError("exact C25 affine-cover enumeration failed")
    total_width, selected = best
    return {
        **common,
        "status": "EXACT_MINIMUM_AFFINE_SOURCE_COVER_FOUND",
        "minimum_source_count": len(selected),
        "minimum_total_width": total_width,
        "selected_source_target_ids": list(selected),
    }


def source_cover_packet(
    rows: Sequence[Mapping[str, Any]],
    targets: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    all_ids = [str(target["target_id"]) for target in targets]
    residual_ids = [
        str(target["target_id"])
        for target in targets
        if str(target["stream"]) == "seeded"
    ]
    seed_uncovered_probe_ids = [
        str(target["target_id"])
        for target in targets
        if str(target["stream"]) == "probe"
        and int(target["transferred_seed_orbit_match_count"]) == 0
    ]
    return {
        "all_probe_and_residual_targets": minimum_affine_source_cover(rows, all_ids),
        "residual_targets": minimum_affine_source_cover(rows, residual_ids),
        "transferred_seed_uncovered_probe_targets": minimum_affine_source_cover(
            rows, seed_uncovered_probe_ids
        ),
    }


def stopping_assessment(
    rows: Sequence[Mapping[str, Any]],
    *,
    small_circuit_max_width: int,
) -> dict[str, object]:
    """Apply the predeclared small-or-reusable continuation rule."""

    small_new = []
    direct_residual_reuse = []
    affine_residual_reuse = []
    probe_transfer = []
    for row in rows:
        source = str(row["source_target_id"])
        if int(
            row["compressed_unique_ordered_quad_count"]
        ) <= small_circuit_max_width and not bool(
            row["matches_active_transferred_seed_orbit"]
        ):
            small_new.append(source)
        direct_targets = {
            str(value) for value in row["clause_coverage"]["direct_covered_target_ids"]
        }
        affine_targets = {
            str(record["target_id"])
            for record in row["clause_coverage"]["translated_orbit_covered_targets"]
        }
        if any(
            target.startswith("seeded:") and target != source
            for target in direct_targets
        ):
            direct_residual_reuse.append(source)
        if any(
            target.startswith("seeded:") and target != source
            for target in affine_targets
        ):
            affine_residual_reuse.append(source)
        if any(target.startswith("probe:") for target in affine_targets):
            probe_transfer.append(source)

    qualifying = sorted(
        set(small_new)
        | set(direct_residual_reuse)
        | set(affine_residual_reuse)
        | set(probe_transfer)
    )
    return {
        "small_circuit_max_width": small_circuit_max_width,
        "new_small_source_target_ids": sorted(small_new),
        "direct_residual_reusable_source_target_ids": sorted(direct_residual_reuse),
        "affine_residual_reusable_source_target_ids": sorted(affine_residual_reuse),
        "probe_transferring_source_target_ids": sorted(probe_transfer),
        "qualifying_small_or_reusable_source_target_ids": qualifying,
        "decision": (
            "CONTINUE_C25_CLAUSE_EXPANSION_WITH_COMPRESSED_RESIDUALS"
            if qualifying
            else "STOP_C25_RESIDUAL_CLAUSE_EXPANSION_AFTER_BOUNDED_SCREEN"
        ),
    }


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
        "active_seed_orbit_match_count": sum(
            bool(row["matches_active_transferred_seed_orbit"]) for row in rows
        ),
    }


def compress_residuals(
    source: Mapping[str, Any],
    *,
    trial_budgets: Sequence[int],
    seed: int,
    model_seed_stride: int,
    tolerance: float,
    small_circuit_max_width: int,
) -> dict[str, object]:
    models = source["seeded_cegar"]["models"]
    if len(trial_budgets) != len(models):
        raise AssertionError("one deterministic trial budget is required per residual")
    n, offsets = PATTERNS[PATTERN]
    targets = target_orders(source)
    seed_hashes = active_seed_orbit_hashes(source)
    rows = []
    for model in models:
        model_index = int(model["model_index"])
        full = model["full_kalmanson"]
        if full.get("certificate") is None:
            raise AssertionError("C25 residual source lacks an exact certificate")
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
        source_target_id = f"seeded:{model_index}"
        hashes = quotient_vector_hashes(certificate)
        compressed.update(
            {
                "source_target_id": source_target_id,
                "source_certificate_sha256": str(full["certificate_sha256"]),
                "compressed_certificate_sha256": stable_json_sha256(certificate),
                "random_objective_seed": model_seed,
                "random_objective_trial_budget": trial_budget,
                "affine_clause_orbit": orbit.summary(),
                "matches_active_transferred_seed_orbit": (
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

    return {
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "target_orders": targets,
        "compressed_models": rows,
        "compression_summary": compression_summary(
            rows, small_circuit_max_width=small_circuit_max_width
        ),
        "coverage_summary": aggregate_coverage(rows, targets),
        "coverage_by_stream": coverage_by_stream(rows, targets),
        "minimum_affine_source_covers": source_cover_packet(rows, targets),
        "quotient_vector_reuse": quotient_vector_reuse(rows),
        "stopping_assessment": stopping_assessment(
            rows, small_circuit_max_width=small_circuit_max_width
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    if source["type"] != "sparse_full_cone_c25_transferred_seed_cegar_v1":
        raise AssertionError("unexpected C25 residual-compression source type")
    check_source_payload(source)
    run = compress_residuals(
        source,
        trial_budgets=args.trial_budgets,
        seed=args.seed,
        model_seed_stride=args.model_seed_stride,
        tolerance=args.tolerance,
        small_circuit_max_width=args.small_circuit_max_width,
    )
    return {
        "type": "sparse_full_cone_c25_transfer_residual_compression_v1",
        "trust": "EXACT_COMPRESSED_CERTIFICATES_IN_BOUNDED_RANDOMIZED_SEARCH",
        "status": "BOUNDED_C25_RESIDUAL_COMPRESSION_AND_REUSE_DIAGNOSTIC",
        "claim_scope": (
            "Deterministic-budget alternative-objective search for eight fixed "
            "C25 residual orders, followed by exact direct and "
            "quotient-preserving translation-orbit coverage over sixteen probe "
            "and eight residual orders. Retained certificates, affine images, "
            "coverage edges, and minimum covers are exact for this finite packet, "
            "but the objective search is not exhaustive and does not prove an "
            "all-order obstruction, geometric realizability, a counterexample, "
            "or Erdos Problem #97."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "trial_budgets_by_model_index": list(args.trial_budgets),
            "seed": args.seed,
            "per_model_seed_stride": args.model_seed_stride,
            "tolerance": args.tolerance,
            "small_circuit_max_width": args.small_circuit_max_width,
            "target_order_selection": (
                "all 16 counterfactual probe and 8 seeded residual models"
            ),
            "stopping_rule": (
                "continue only if a compressed orbit is new relative to the "
                "three active transferred seeds and has width at most the "
                "configured threshold, or directly/affinely reuses across "
                "residual orders, or affinely transfers to a probe order"
            ),
        },
        "run": run,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_transfer_residual_compression_v1":
        raise AssertionError("C25 residual-compression artifact type drifted")
    source_path = ROOT / str(payload["source_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("C25 residual-compression source hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_source_payload(source)

    configuration = payload["configuration"]
    trial_budgets = [
        int(value) for value in configuration["trial_budgets_by_model_index"]
    ]
    base_seed = int(configuration["seed"])
    model_seed_stride = int(configuration["per_model_seed_stride"])
    small_width = int(configuration["small_circuit_max_width"])
    targets = target_orders(source)
    run = payload["run"]
    if run["target_orders"] != targets:
        raise AssertionError("C25 residual target packet drifted")
    if str(run["pattern"]) != PATTERN:
        raise AssertionError("C25 residual pattern drifted")

    source_models = {
        int(model["model_index"]): model for model in source["seeded_cegar"]["models"]
    }
    seed_hashes = active_seed_orbit_hashes(source)
    checked_rows = []
    verified_certificates = 0
    verified_images = 0
    for row in run["compressed_models"]:
        model_index = int(row["source_model_index"])
        source_model = source_models[model_index]
        source_full = source_model["full_kalmanson"]
        order = [int(label) for label in row["order"]]
        if order != [int(label) for label in source_model["order"]]:
            raise AssertionError("C25 residual compression source order drifted")
        if row["source_certificate_sha256"] != source_full["certificate_sha256"]:
            raise AssertionError("C25 residual source certificate hash drifted")
        if int(row["random_objective_trial_budget"]) != trial_budgets[model_index]:
            raise AssertionError("C25 residual trial budget drifted")
        expected_seed = base_seed + model_index * model_seed_stride
        if int(row["random_objective_seed"]) != expected_seed:
            raise AssertionError("C25 residual objective seed drifted")

        certificate = row["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("C25 compressed residual certificate failed")
        if stable_json_sha256(certificate) != row["compressed_certificate_sha256"]:
            raise AssertionError("C25 compressed residual certificate hash drifted")
        quads = certificate_order_quads(certificate, order)
        if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
            raise AssertionError("C25 compressed residual width drifted")
        source_quads = certificate_order_quads(source_full["certificate"], order)
        if len(source_quads) != int(row["source_unique_ordered_quad_count"]):
            raise AssertionError("C25 residual source width drifted")
        if len(source_quads) - len(quads) != int(row["quad_reduction"]):
            raise AssertionError("C25 residual compression reduction drifted")
        circuit_audit = positive_circuit_audit(certificate)
        if circuit_audit != row["positive_circuit_audit"]:
            raise AssertionError("C25 residual circuit audit drifted")
        if not circuit_audit["positive_circuit_verified"]:
            raise AssertionError("C25 compressed residual is not a circuit")

        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        if row["affine_clause_orbit"] != orbit.summary():
            raise AssertionError("C25 residual affine clause orbit drifted")
        if bool(row["matches_active_transferred_seed_orbit"]) != (
            orbit.canonical_clause_sha256 in seed_hashes
        ):
            raise AssertionError("C25 residual active-seed match drifted")
        hashes = quotient_vector_hashes(certificate)
        expected_vector_support = {
            "unique_vector_count": len(hashes),
            "duplicate_inequality_vector_count": (
                checked.positive_inequalities - len(hashes)
            ),
            "hashes": hashes,
        }
        if row["quotient_vector_support"] != expected_vector_support:
            raise AssertionError("C25 residual quotient-vector support drifted")
        source_target_id = f"seeded:{model_index}"
        expected_coverage = clause_coverage(
            certificate,
            orbit,
            targets,
            source_target_id=source_target_id,
        )
        if row["clause_coverage"] != expected_coverage:
            raise AssertionError("C25 compressed residual coverage drifted")
        checked_rows.append(row)
        verified_certificates += 1
        verified_images += orbit.affine_map_count

    if run["compression_summary"] != compression_summary(
        checked_rows, small_circuit_max_width=small_width
    ):
        raise AssertionError("C25 residual compression summary drifted")
    if run["coverage_summary"] != aggregate_coverage(checked_rows, targets):
        raise AssertionError("C25 residual aggregate coverage drifted")
    if run["coverage_by_stream"] != coverage_by_stream(checked_rows, targets):
        raise AssertionError("C25 residual stream coverage drifted")
    if run["minimum_affine_source_covers"] != source_cover_packet(
        checked_rows, targets
    ):
        raise AssertionError("C25 residual minimum affine covers drifted")
    if run["quotient_vector_reuse"] != quotient_vector_reuse(checked_rows):
        raise AssertionError("C25 residual quotient-vector reuse drifted")
    if run["stopping_assessment"] != stopping_assessment(
        checked_rows, small_circuit_max_width=small_width
    ):
        raise AssertionError("C25 residual stopping assessment drifted")

    coverage = run["coverage_summary"]
    assessment = run["stopping_assessment"]
    return {
        "status": "OK",
        "verified_target_orders": len(targets),
        "verified_compressed_exact_certificates": verified_certificates,
        "verified_exact_affine_certificate_images": verified_images,
        "verified_direct_cross_coverage_edges": int(
            coverage["direct_cross_reuse_edge_count"]
        ),
        "verified_affine_cross_coverage_edges": int(
            coverage["translated_orbit_cross_reuse_edge_count"]
        ),
        "small_or_reusable_source_count": len(
            assessment["qualifying_small_or_reusable_source_target_ids"]
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
    parser.add_argument("--seed", type=int, default=20260804)
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
        raise SystemExit("tolerance, seed stride, and width threshold must be positive")
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
        summary = run["compression_summary"]
        coverage = run["coverage_summary"]
        assessment = run["stopping_assessment"]
        print(
            f"{PATTERN}: "
            f"widths={summary['compressed_widths']} "
            f"targets={coverage['translated_orbit_covered_target_count']}/"
            f"{coverage['target_order_count']} "
            f"direct_cross={coverage['direct_cross_reuse_edge_count']} "
            f"affine_cross={coverage['translated_orbit_cross_reuse_edge_count']} "
            f"decision={assessment['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
