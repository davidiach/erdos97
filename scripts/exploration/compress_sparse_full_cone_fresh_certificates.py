#!/usr/bin/env python3
"""Compress fresh-order full-cone certificates and measure exact reuse.

The source packet contains exact positive Kalmanson circuits for 63 fixed
C25/C29 cyclic orders.  This bounded follow-up samples a small deterministic
set of alternative LP objectives for each order, retains an improvement only
after exact integer replay and a positive-circuit audit, expands every retained
certificate through the quotient-preserving affine group, and measures exact
direct and affine-orbit coverage inside the same fresh-order packet.

The randomized objective search is not exhaustive.  Its retained certificates
and coverage edges are exact fixed-pattern, fixed-order diagnostics only; they
do not prove an all-order obstruction, geometric realizability, a
counterexample, or Erdos Problem #97.
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
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    build_clause_orbit,
    file_sha256,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_order_screen_2026-07-29"
    / "summary.json"
)
DEFAULT_PRIOR_COMPRESSION = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)
DEFAULT_SMALL_CIRCUIT_MAX_WIDTH = 12


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def fresh_targets(run: Mapping[str, Any]) -> list[dict[str, object]]:
    """Return the exact-certificate records as a coverage target packet."""

    targets = []
    for record in run["records"]:
        if record["classification"] != "EXACT_POSITIVE_ZERO_SUM_CERTIFICATE":
            raise AssertionError("fresh compression source is not an exact circuit")
        model_index = int(record["fresh_model_index"])
        targets.append(
            {
                "target_id": f"fresh:{model_index}",
                "stream": "fresh",
                "model_index": model_index,
                "order": [int(label) for label in record["order"]],
                "strong_lightweight_survivor": True,
            }
        )
    ids = [str(target["target_id"]) for target in targets]
    if len(ids) != len(set(ids)):
        raise AssertionError("fresh target identifiers are not unique")
    return targets


def compression_model(record: Mapping[str, Any]) -> dict[str, object]:
    """Adapt one exact screen record to the shared compressor interface."""

    certificate = record["certificate"]
    return {
        "model_index": int(record["fresh_model_index"]),
        "order": [int(label) for label in record["order"]],
        "full_kalmanson": {
            "positive_inequalities": int(record["positive_inequalities"]),
            "certificate": certificate,
        },
    }


def prior_clause_orbit_hashes(
    payload: Mapping[str, Any],
) -> dict[str, set[str]]:
    """Return all canonical clause-orbit hashes from the prior compression."""

    result: dict[str, set[str]] = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        hashes = set()
        for row in run["compressed_models"]:
            hashes.add(
                build_clause_orbit(
                    name,
                    int(row["source_model_index"]),
                    row["compressed_certificate"],
                ).canonical_clause_sha256
            )
        result[name] = hashes
    return result


def stopping_assessment(
    rows: Sequence[Mapping[str, Any]],
    *,
    small_circuit_max_width: int,
) -> dict[str, object]:
    """Apply the predeclared small-or-reusable cluster-mining stopping rule."""

    small = []
    new_small = []
    direct_reusable = []
    affine_reusable = []
    for row in rows:
        source = str(row["source_target_id"])
        width = int(row["compressed_unique_ordered_quad_count"])
        if width <= small_circuit_max_width:
            small.append(source)
            if not bool(row["matches_prior_compression_clause_orbit"]):
                new_small.append(source)
        coverage = row["clause_coverage"]
        if int(coverage["direct_cross_target_count"]):
            direct_reusable.append(source)
        if int(coverage["translated_orbit_cross_target_count"]):
            affine_reusable.append(source)

    qualifying = sorted(set(new_small) | set(direct_reusable) | set(affine_reusable))
    return {
        "small_circuit_max_width": small_circuit_max_width,
        "small_source_target_ids": sorted(small),
        "new_small_source_target_ids": sorted(new_small),
        "direct_reusable_source_target_ids": sorted(direct_reusable),
        "affine_reusable_source_target_ids": sorted(affine_reusable),
        "qualifying_small_or_reusable_source_target_ids": qualifying,
        "decision": (
            "CONTINUE_CLUSTER_MINING"
            if qualifying
            else "STOP_CLUSTER_MINING_AFTER_BOUNDED_NEGATIVE_SCREEN"
        ),
    }


def compress_run(
    run: Mapping[str, Any],
    *,
    pattern_index: int,
    prior_hashes: set[str],
    trials: int,
    seed: int,
    tolerance: float,
    small_circuit_max_width: int,
) -> dict[str, object]:
    name = str(run["pattern"])
    n, offsets = PATTERNS[name]
    targets = fresh_targets(run)
    rows = []
    for record in run["records"]:
        model_index = int(record["fresh_model_index"])
        model_seed = seed + pattern_index * 100_000 + model_index * 1_000
        compressed = compress_model(
            name,
            n,
            offsets,
            compression_model(record),
            trials=trials,
            seed=model_seed,
            tolerance=tolerance,
        )
        certificate = compressed["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        orbit = build_clause_orbit(name, model_index, certificate)
        source_target_id = f"fresh:{model_index}"
        hashes = quotient_vector_hashes(certificate)
        compressed.update(
            {
                "source_target_id": source_target_id,
                "source_certificate_sha256": str(record["certificate_sha256"]),
                "compressed_certificate_sha256": stable_json_sha256(certificate),
                "random_objective_seed": model_seed,
                "affine_clause_orbit": orbit.summary(),
                "matches_prior_compression_clause_orbit": (
                    orbit.canonical_clause_sha256 in prior_hashes
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

    coverage = aggregate_coverage(rows, targets)
    assessment = stopping_assessment(
        rows,
        small_circuit_max_width=small_circuit_max_width,
    )
    widths = [int(row["compressed_unique_ordered_quad_count"]) for row in rows]
    reductions = [int(row["quad_reduction"]) for row in rows]
    return {
        "pattern": name,
        "n": n,
        "circulant_offsets": offsets,
        "target_orders": targets,
        "compressed_models": rows,
        "compression_summary": {
            "source_count": len(rows),
            "exact_improvement_count": sum(bool(value) for value in reductions),
            "minimum_compressed_unique_ordered_quad_count": min(widths),
            "maximum_compressed_unique_ordered_quad_count": max(widths),
            "minimum_quad_reduction": min(reductions),
            "maximum_quad_reduction": max(reductions),
        },
        "coverage_summary": coverage,
        "quotient_vector_reuse": quotient_vector_reuse(rows),
        "stopping_assessment": assessment,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    prior_path = (
        args.prior_compression
        if args.prior_compression.is_absolute()
        else ROOT / args.prior_compression
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    prior_hashes = prior_clause_orbit_hashes(prior)
    selected_runs = [
        (index, run)
        for index, run in enumerate(source["runs"])
        if not args.pattern or str(run["pattern"]) in args.pattern
    ]
    runs = [
        compress_run(
            run,
            pattern_index=index,
            prior_hashes=prior_hashes[str(run["pattern"])],
            trials=args.trials,
            seed=args.seed,
            tolerance=args.tolerance,
            small_circuit_max_width=args.small_circuit_max_width,
        )
        for index, run in selected_runs
    ]
    return {
        "type": "sparse_full_cone_fresh_clause_compression_v1",
        "trust": "EXACT_COMPRESSED_CERTIFICATES_IN_BOUNDED_RANDOMIZED_SEARCH",
        "status": "BOUNDED_FRESH_PACKET_COMPRESSION_AND_REUSE_DIAGNOSTIC",
        "claim_scope": (
            "Low-budget randomized alternative-circuit search for 63 fixed "
            "C25/C29 patterns and cyclic orders, followed by exact direct and "
            "quotient-preserving affine-orbit coverage within the same fresh "
            "packet. Retained certificates and coverage edges are exact, but "
            "the search is not exhaustive and does not prove an all-order "
            "obstruction, geometric realizability, a counterexample, or Erdos "
            "Problem #97."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "prior_compression_artifact": prior_path.relative_to(ROOT).as_posix(),
        "prior_compression_sha256": file_sha256(prior_path),
        "configuration": {
            "trials_per_model": args.trials,
            "seed": args.seed,
            "per_model_seed_stride": 1_000,
            "per_pattern_seed_stride": 100_000,
            "tolerance": args.tolerance,
            "small_circuit_max_width": args.small_circuit_max_width,
            "stopping_rule": (
                "continue only if a compressed clause has width at most the "
                "configured threshold and is absent from the prior compression "
                "packet, or directly/affinely covers another fresh target"
            ),
            "target_order_selection": (
                "all 63 exact-positive-certificate fresh lightweight survivors"
            ),
        },
        "runs": runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_fresh_clause_compression_v1":
        raise AssertionError("fresh compression artifact type drifted")
    source_path = ROOT / str(payload["source_artifact"])
    prior_path = ROOT / str(payload["prior_compression_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("fresh full-cone source artifact hash drifted")
    if file_sha256(prior_path) != str(payload["prior_compression_sha256"]):
        raise AssertionError("prior compression artifact hash drifted")

    source = json.loads(source_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    source_by_pattern = {str(run["pattern"]): run for run in source["runs"]}
    source_pattern_indices = {
        str(run["pattern"]): index for index, run in enumerate(source["runs"])
    }
    prior_hashes = prior_clause_orbit_hashes(prior)
    configuration = payload["configuration"]
    small_width = int(configuration["small_circuit_max_width"])
    base_seed = int(configuration["seed"])
    pattern_stride = int(configuration["per_pattern_seed_stride"])
    model_stride = int(configuration["per_model_seed_stride"])

    verified_targets = 0
    verified_certificates = 0
    verified_affine_images = 0
    direct_cross_edges = 0
    affine_cross_edges = 0
    qualifying_sources = 0
    decisions = []
    seen_patterns: set[str] = set()
    for run in payload["runs"]:
        name = str(run["pattern"])
        if name in seen_patterns or name not in source_by_pattern:
            raise AssertionError(f"invalid or duplicate fresh compression pattern: {name}")
        seen_patterns.add(name)
        source_run = source_by_pattern[name]
        expected_targets = fresh_targets(source_run)
        if run["target_orders"] != expected_targets:
            raise AssertionError(f"{name} fresh target packet drifted")
        verified_targets += len(expected_targets)
        source_records = {
            int(record["fresh_model_index"]): record for record in source_run["records"]
        }
        rows = run["compressed_models"]
        if len(rows) != len(source_records):
            raise AssertionError(f"{name} compressed source count drifted")
        checked_rows = []
        seen_model_indices: set[int] = set()
        for row in rows:
            model_index = int(row["source_model_index"])
            if model_index in seen_model_indices or model_index not in source_records:
                raise AssertionError(f"{name} invalid or duplicate source model index")
            seen_model_indices.add(model_index)
            source_record = source_records[model_index]
            source_target_id = f"fresh:{model_index}"
            if row["source_target_id"] != source_target_id:
                raise AssertionError(f"{name} source target id drifted")
            order = [int(label) for label in row["order"]]
            if order != [int(label) for label in source_record["order"]]:
                raise AssertionError(f"{name} compression source order drifted")
            if row["source_certificate_sha256"] != source_record["certificate_sha256"]:
                raise AssertionError(f"{name} source certificate hash drifted")
            expected_seed = (
                base_seed
                + source_pattern_indices[name] * pattern_stride
                + model_index * model_stride
            )
            if int(row["random_objective_seed"]) != expected_seed:
                raise AssertionError(f"{name} random objective seed drifted")

            certificate = row["compressed_certificate"]
            checked = check_certificate_dict(certificate)
            if not checked.zero_sum_verified:
                raise AssertionError(f"{name} compressed certificate failed")
            if stable_json_sha256(certificate) != row["compressed_certificate_sha256"]:
                raise AssertionError(f"{name} compressed certificate hash drifted")
            quads = certificate_order_quads(certificate, order)
            if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
                raise AssertionError(f"{name} compressed width drifted")
            source_certificate = source_record["certificate"]
            source_quads = certificate_order_quads(source_certificate, order)
            if len(source_quads) != int(row["source_unique_ordered_quad_count"]):
                raise AssertionError(f"{name} source width drifted")
            if len(source_quads) - len(quads) != int(row["quad_reduction"]):
                raise AssertionError(f"{name} compression reduction drifted")
            circuit_audit = positive_circuit_audit(certificate)
            if circuit_audit != row["positive_circuit_audit"]:
                raise AssertionError(f"{name} circuit audit drifted")
            if not circuit_audit["positive_circuit_verified"]:
                raise AssertionError(f"{name} compressed support is not a circuit")

            orbit = build_clause_orbit(name, model_index, certificate)
            if row["affine_clause_orbit"] != orbit.summary():
                raise AssertionError(f"{name} affine clause orbit drifted")
            expected_prior_match = orbit.canonical_clause_sha256 in prior_hashes[name]
            if (
                bool(row["matches_prior_compression_clause_orbit"])
                != expected_prior_match
            ):
                raise AssertionError(f"{name} prior clause match drifted")
            hashes = quotient_vector_hashes(certificate)
            expected_vector_support = {
                "unique_vector_count": len(hashes),
                "duplicate_inequality_vector_count": (
                    checked.positive_inequalities - len(hashes)
                ),
                "hashes": hashes,
            }
            if row["quotient_vector_support"] != expected_vector_support:
                raise AssertionError(f"{name} quotient-vector support drifted")
            expected_coverage = clause_coverage(
                certificate,
                orbit,
                expected_targets,
                source_target_id=source_target_id,
            )
            if row["clause_coverage"] != expected_coverage:
                raise AssertionError(f"{name} clause coverage drifted")
            checked_rows.append(row)
            verified_certificates += 1
            verified_affine_images += orbit.affine_map_count

        if seen_model_indices != set(source_records):
            raise AssertionError(f"{name} compressed source set drifted")
        widths = [
            int(row["compressed_unique_ordered_quad_count"]) for row in checked_rows
        ]
        reductions = [int(row["quad_reduction"]) for row in checked_rows]
        expected_compression_summary = {
            "source_count": len(checked_rows),
            "exact_improvement_count": sum(bool(value) for value in reductions),
            "minimum_compressed_unique_ordered_quad_count": min(widths),
            "maximum_compressed_unique_ordered_quad_count": max(widths),
            "minimum_quad_reduction": min(reductions),
            "maximum_quad_reduction": max(reductions),
        }
        if run["compression_summary"] != expected_compression_summary:
            raise AssertionError(f"{name} compression summary drifted")
        coverage = aggregate_coverage(checked_rows, expected_targets)
        if run["coverage_summary"] != coverage:
            raise AssertionError(f"{name} aggregate coverage drifted")
        if run["quotient_vector_reuse"] != quotient_vector_reuse(checked_rows):
            raise AssertionError(f"{name} quotient-vector reuse drifted")
        assessment = stopping_assessment(
            checked_rows,
            small_circuit_max_width=small_width,
        )
        if run["stopping_assessment"] != assessment:
            raise AssertionError(f"{name} stopping assessment drifted")
        direct_cross_edges += int(coverage["direct_cross_reuse_edge_count"])
        affine_cross_edges += int(coverage["translated_orbit_cross_reuse_edge_count"])
        qualifying_sources += len(
            assessment["qualifying_small_or_reusable_source_target_ids"]
        )
        decisions.append(str(assessment["decision"]))

    return {
        "status": "OK",
        "verified_fresh_target_orders": verified_targets,
        "verified_compressed_exact_certificates": verified_certificates,
        "verified_exact_affine_certificate_images": verified_affine_images,
        "verified_direct_cross_reuse_edges": direct_cross_edges,
        "verified_affine_cross_reuse_edges": affine_cross_edges,
        "qualifying_small_or_reusable_source_count": qualifying_sources,
        "cluster_mining_decisions": decisions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--prior-compression",
        type=Path,
        default=DEFAULT_PRIOR_COMPRESSION,
    )
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--trials", type=int, default=6)
    parser.add_argument("--seed", type=int, default=20260731)
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
    if args.trials <= 0 or args.tolerance <= 0 or args.small_circuit_max_width <= 0:
        raise SystemExit("trials, tolerance, and small-circuit width must be positive")
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
        for run in payload["runs"]:
            compression = run["compression_summary"]
            coverage = run["coverage_summary"]
            assessment = run["stopping_assessment"]
            print(
                f"{run['pattern']}: "
                f"sources={compression['source_count']} "
                f"improved={compression['exact_improvement_count']} "
                f"width="
                f"{compression['minimum_compressed_unique_ordered_quad_count']}-"
                f"{compression['maximum_compressed_unique_ordered_quad_count']} "
                f"direct_cross={coverage['direct_cross_reuse_edge_count']} "
                f"affine_cross="
                f"{coverage['translated_orbit_cross_reuse_edge_count']} "
                f"decision={assessment['decision']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
