#!/usr/bin/env python3
"""Compress the seeded C25/C29 certificates and measure exact cross-coverage.

The source packet contains eight newly learned exact full-cone certificates
for each sparse pattern, plus sixteen counterfactual probe orders per pattern.
This bounded follow-up samples alternative LP extreme points for each of the
sixteen certificates, exactifies every retained improvement, expands each
compressed circuit through all quotient-preserving translations, and measures
direct and translated-clause coverage across all forty-eight stored orders.

Randomized objective sampling is not exhaustive.  Every retained certificate
and every translated image is exact, but all conclusions remain fixed-pattern,
fixed-order diagnostics rather than an all-order obstruction, counterexample,
or proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import (  # noqa: E402
    build_distance_classes,
    check_certificate_dict,
    inequality_terms,
)
from compress_sparse_full_cone_certificates import (  # noqa: E402
    compress_model,
    order_satisfies_quads,
    positive_circuit_audit,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    build_clause_orbit,
    file_sha256,
)


DEFAULT_SOURCE = (
    ROOT / "data" / "runs" / "sparse_full_cone_seeded_cegar_2026-07-23" / "summary.json"
)


def target_orders(run: Mapping[str, Any]) -> list[dict[str, object]]:
    """Return the 16 probe and 8 seeded orders for one pattern."""

    targets = []
    streams = (
        ("probe", run["counterfactual_probe"]["models"]),
        ("seeded", run["seeded_cegar"]["models"]),
    )
    for stream, models in streams:
        for model in models:
            index_key = "probe_model_index" if stream == "probe" else "model_index"
            index = int(model[index_key])
            targets.append(
                {
                    "target_id": f"{stream}:{index}",
                    "stream": stream,
                    "model_index": index,
                    "order": [int(label) for label in model["order"]],
                    "strong_lightweight_survivor": bool(
                        model["lightweight_filters"]["survives"]
                    ),
                }
            )
    ids = [str(target["target_id"]) for target in targets]
    if len(ids) != len(set(ids)):
        raise AssertionError("target order identifiers are not unique")
    return targets


def quotient_vector_hashes(
    certificate: Mapping[str, Any],
) -> list[str]:
    """Hash the distinct exact quotient vectors used by one certificate."""

    pattern = certificate["pattern"]
    n = int(pattern["n"])
    offsets = [int(value) for value in pattern["circulant_offsets"]]
    classes = build_distance_classes(n, offsets)
    class_count = len(set(classes.values()))
    hashes = set()
    for inequality in certificate["inequalities"]:
        vector = [0] * class_count
        for pair, coefficient in inequality_terms(
            str(inequality["kind"]), inequality["quad"]
        ):
            vector[classes[pair]] += coefficient
        encoded = json.dumps(vector, separators=(",", ":")).encode("ascii")
        hashes.add(hashlib.sha256(encoded).hexdigest())
    return sorted(hashes)


def clause_coverage(
    certificate: Mapping[str, Any],
    orbit: ClauseOrbit,
    targets: Sequence[Mapping[str, Any]],
    *,
    source_target_id: str,
) -> dict[str, object]:
    order = [int(label) for label in certificate["cyclic_order"]]
    direct_quads = certificate_order_quads(certificate, order)
    direct = [
        str(target["target_id"])
        for target in targets
        if order_satisfies_quads(target["order"], direct_quads)
    ]
    translated = []
    for target in targets:
        matching = sum(
            order_satisfies_quads(target["order"], clause) for clause in orbit.clauses
        )
        if matching:
            translated.append(
                {
                    "target_id": str(target["target_id"]),
                    "matching_translation_count": matching,
                }
            )
    translated_ids = [str(row["target_id"]) for row in translated]
    if source_target_id not in direct or source_target_id not in translated_ids:
        raise AssertionError("compressed clause does not cover its source order")
    return {
        "source_target_id": source_target_id,
        "direct_covered_target_ids": direct,
        "direct_cross_target_count": sum(
            target_id != source_target_id for target_id in direct
        ),
        "translated_orbit_covered_targets": translated,
        "translated_orbit_cross_target_count": sum(
            target_id != source_target_id for target_id in translated_ids
        ),
    }


def aggregate_coverage(
    rows: Sequence[Mapping[str, Any]],
    targets: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    direct_sources: dict[str, list[str]] = defaultdict(list)
    translated_sources: dict[str, list[str]] = defaultdict(list)
    direct_cross_edges = 0
    translated_cross_edges = 0
    for row in rows:
        source = str(row["source_target_id"])
        coverage = row["clause_coverage"]
        for target_id in coverage["direct_covered_target_ids"]:
            target_id = str(target_id)
            direct_sources[target_id].append(source)
            direct_cross_edges += int(target_id != source)
        for target in coverage["translated_orbit_covered_targets"]:
            target_id = str(target["target_id"])
            translated_sources[target_id].append(source)
            translated_cross_edges += int(target_id != source)

    target_rows = []
    for target in targets:
        target_id = str(target["target_id"])
        target_rows.append(
            {
                "target_id": target_id,
                "stream": str(target["stream"]),
                "strong_lightweight_survivor": bool(
                    target["strong_lightweight_survivor"]
                ),
                "direct_covering_source_ids": sorted(direct_sources[target_id]),
                "translated_orbit_covering_source_ids": sorted(
                    translated_sources[target_id]
                ),
            }
        )
    return {
        "target_order_count": len(targets),
        "compressed_source_count": len(rows),
        "direct_covered_target_count": sum(
            bool(row["direct_covering_source_ids"]) for row in target_rows
        ),
        "translated_orbit_covered_target_count": sum(
            bool(row["translated_orbit_covering_source_ids"]) for row in target_rows
        ),
        "direct_cross_reuse_edge_count": direct_cross_edges,
        "translated_orbit_cross_reuse_edge_count": translated_cross_edges,
        "target_coverage": target_rows,
    }


def quotient_vector_reuse(
    rows: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    supports = {
        str(row["source_target_id"]): set(
            str(value) for value in row["quotient_vector_support"]["hashes"]
        )
        for row in rows
    }
    frequency: Counter[str] = Counter()
    sources_by_hash: dict[str, list[str]] = defaultdict(list)
    for source, hashes in supports.items():
        for vector_hash in hashes:
            frequency[vector_hash] += 1
            sources_by_hash[vector_hash].append(source)

    pairwise = []
    per_source_best: dict[str, int] = {source: 0 for source in supports}
    for left, right in combinations(sorted(supports), 2):
        intersection = len(supports[left] & supports[right])
        union = len(supports[left] | supports[right])
        per_source_best[left] = max(per_source_best[left], intersection)
        per_source_best[right] = max(per_source_best[right], intersection)
        if intersection:
            pairwise.append(
                {
                    "left_source_target_id": left,
                    "right_source_target_id": right,
                    "shared_vector_count": intersection,
                    "jaccard_fraction": intersection / union,
                }
            )

    shared = [
        {
            "sha256": vector_hash,
            "certificate_count": frequency[vector_hash],
            "source_target_ids": sorted(sources_by_hash[vector_hash]),
        }
        for vector_hash in sorted(frequency)
        if frequency[vector_hash] >= 2
    ]
    return {
        "distinct_vector_count": len(frequency),
        "shared_vector_count": len(shared),
        "max_certificate_frequency": max(frequency.values(), default=0),
        "shared_vectors": shared,
        "nonzero_pairwise_overlaps": pairwise,
        "per_source_max_pairwise_shared_vector_count": [
            {
                "source_target_id": source,
                "max_pairwise_shared_vector_count": per_source_best[source],
            }
            for source in sorted(per_source_best)
        ],
    }


def compress_run(
    run: Mapping[str, Any],
    *,
    pattern_index: int,
    trials: int,
    seed: int,
    tolerance: float,
) -> dict[str, object]:
    name = str(run["pattern"])
    n, offsets = PATTERNS[name]
    targets = target_orders(run)
    compressed_rows = []
    for model in run["seeded_cegar"]["models"]:
        model_index = int(model["model_index"])
        if model["full_kalmanson"].get("certificate") is None:
            raise AssertionError("seeded source model lacks an exact certificate")
        model_seed = seed + pattern_index * 100_000 + model_index * 1_000
        compressed = compress_model(
            name,
            n,
            offsets,
            model,
            trials=trials,
            seed=model_seed,
            tolerance=tolerance,
        )
        certificate = compressed["compressed_certificate"]
        orbit = build_clause_orbit(name, model_index, certificate)
        source_target_id = f"seeded:{model_index}"
        compressed["source_target_id"] = source_target_id
        compressed["random_objective_seed"] = model_seed
        compressed["affine_clause_orbit"] = orbit.summary()
        hashes = quotient_vector_hashes(certificate)
        compressed["quotient_vector_support"] = {
            "unique_vector_count": len(hashes),
            "duplicate_inequality_vector_count": (
                int(compressed["compressed_positive_inequalities"]) - len(hashes)
            ),
            "hashes": hashes,
        }
        compressed["clause_coverage"] = clause_coverage(
            certificate,
            orbit,
            targets,
            source_target_id=source_target_id,
        )
        compressed_rows.append(compressed)

    return {
        "pattern": name,
        "n": n,
        "circulant_offsets": offsets,
        "target_orders": targets,
        "compressed_models": compressed_rows,
        "coverage_summary": aggregate_coverage(compressed_rows, targets),
        "quotient_vector_reuse": quotient_vector_reuse(compressed_rows),
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    selected_runs = [
        (index, run)
        for index, run in enumerate(source["runs"])
        if not args.pattern or str(run["pattern"]) in args.pattern
    ]
    runs = [
        compress_run(
            run,
            pattern_index=index,
            trials=args.trials,
            seed=args.seed,
            tolerance=args.tolerance,
        )
        for index, run in selected_runs
    ]
    return {
        "type": "sparse_full_cone_seeded_clause_compression_v1",
        "trust": "EXACT_COMPRESSED_CERTIFICATES_IN_BOUNDED_RANDOMIZED_SEARCH",
        "status": "BOUNDED_CROSS_ORDER_CLAUSE_REUSE_DIAGNOSTIC",
        "claim_scope": (
            "Randomized alternative-circuit search for sixteen fixed C25/C29 "
            "patterns and orders, followed by exact direct and translation-orbit "
            "coverage over forty-eight stored orders. Retained certificates and "
            "images are exact, but the search is not exhaustive and does not prove "
            "an all-order obstruction, geometric realizability, a counterexample, "
            "or Erdos Problem #97."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "trials_per_model": args.trials,
            "seed": args.seed,
            "per_model_seed_stride": 1_000,
            "per_pattern_seed_stride": 100_000,
            "tolerance": args.tolerance,
            "target_order_selection": (
                "all counterfactual probe and seeded CEGAR models"
            ),
        },
        "runs": runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    source_path = ROOT / str(payload["source_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("source seeded-CEGAR artifact hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source_by_pattern = {str(run["pattern"]): run for run in source["runs"]}
    verified_certificates = 0
    verified_affine_images = 0
    verified_target_orders = 0

    for run in payload["runs"]:
        name = str(run["pattern"])
        source_run = source_by_pattern[name]
        expected_targets = target_orders(source_run)
        if run["target_orders"] != expected_targets:
            raise AssertionError(f"{name} target-order packet drifted")
        verified_target_orders += len(expected_targets)
        source_models = {
            int(model["model_index"]): model
            for model in source_run["seeded_cegar"]["models"]
        }
        checked_rows = []
        for row in run["compressed_models"]:
            model_index = int(row["source_model_index"])
            source_model = source_models[model_index]
            order = [int(label) for label in row["order"]]
            if order != [int(label) for label in source_model["order"]]:
                raise AssertionError(f"{name} compression source order drifted")
            certificate = row["compressed_certificate"]
            checked = check_certificate_dict(certificate)
            if not checked.zero_sum_verified:
                raise AssertionError(f"{name} compressed certificate failed")
            quads = certificate_order_quads(certificate, order)
            if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
                raise AssertionError(f"{name} compressed width drifted")
            source_width = int(row["source_unique_ordered_quad_count"])
            if source_width - len(quads) != int(row["quad_reduction"]):
                raise AssertionError(f"{name} compression reduction drifted")
            circuit_audit = positive_circuit_audit(certificate)
            if circuit_audit != row["positive_circuit_audit"]:
                raise AssertionError(f"{name} positive-circuit audit drifted")
            if not circuit_audit["positive_circuit_verified"]:
                raise AssertionError(f"{name} compressed support is not a circuit")

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

            orbit = build_clause_orbit(name, model_index, certificate)
            if row["affine_clause_orbit"] != orbit.summary():
                raise AssertionError(f"{name} compressed affine orbit drifted")
            source_target_id = f"seeded:{model_index}"
            expected_coverage = clause_coverage(
                certificate,
                orbit,
                expected_targets,
                source_target_id=source_target_id,
            )
            if row["clause_coverage"] != expected_coverage:
                raise AssertionError(f"{name} compressed clause coverage drifted")
            checked_rows.append(row)
            verified_certificates += 1
            verified_affine_images += orbit.affine_map_count

        if run["coverage_summary"] != aggregate_coverage(
            checked_rows, expected_targets
        ):
            raise AssertionError(f"{name} aggregate coverage drifted")
        if run["quotient_vector_reuse"] != quotient_vector_reuse(checked_rows):
            raise AssertionError(f"{name} quotient-vector reuse drifted")

    return {
        "status": "OK",
        "verified_target_orders": verified_target_orders,
        "verified_compressed_exact_certificates": verified_certificates,
        "verified_exact_affine_certificate_images": verified_affine_images,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--trials", type=int, default=24)
    parser.add_argument("--seed", type=int, default=20260729)
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trials <= 0 or args.tolerance <= 0:
        raise SystemExit("trials and tolerance must be positive")
    if args.check is not None:
        payload = json.loads(args.check.read_text(encoding="utf-8"))
        print(json.dumps(check_payload(payload), indent=2, sort_keys=True))
        return 0

    payload = build_payload(args)

    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    if args.json or args.out is None:
        print(text, end="")
    else:
        for run in payload["runs"]:
            sizes = [
                f"{row['source_unique_ordered_quad_count']}->"
                f"{row['compressed_unique_ordered_quad_count']}"
                for row in run["compressed_models"]
            ]
            coverage = run["coverage_summary"]
            print(
                f"{run['pattern']}: {', '.join(sizes)} "
                f"direct_cross={coverage['direct_cross_reuse_edge_count']} "
                f"translated_cross="
                f"{coverage['translated_orbit_cross_reuse_edge_count']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
