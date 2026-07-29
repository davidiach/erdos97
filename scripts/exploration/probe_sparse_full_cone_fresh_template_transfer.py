#!/usr/bin/env python3
"""Audit transfer of the new fresh-packet full-cone templates.

The source compression packet contains three new circuits of width at most
twelve and one width-fourteen C25 circuit with broad source-packet coverage.
This bounded follow-up canonicalizes those four exact circuits, replays them
against the prior 48-order packet, and probes a second deterministic
inverse-pair-escape stream that is dihedrally disjoint from both the prior
packet and the first 64-order fresh stream.

Templates are evaluated only after order generation; they are never asserted
as solver blockers.  Every retained certificate, affine image, order identity,
and coverage match is replayed exactly.  The bounded streams remain
fixed-pattern diagnostics, not all-order obstructions, geometric realizability
results, counterexamples, or a proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    inverse_pair_audit,
    lightweight_summary,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    canonical_certificate_for_orbit,
    collect_fresh_orders,
    dihedral_order_key,
    historical_orders_by_pattern,
    order_record_hashes,
    template_matches,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    build_clause_orbit,
    clause_hash,
    file_sha256,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_compression_2026-07-29"
    / "summary.json"
)
DEFAULT_PRIOR_PACKET = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)
DEFAULT_FIRST_FRESH_STREAM = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_small_template_fresh_stream_2026-07-29"
    / "summary.json"
)
DEFAULT_MAX_SMALL_WIDTH = 12
DEFAULT_BROAD_SOURCE_COVERAGE_MIN = 24


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_transfer_templates(
    payload: Mapping[str, Any],
    *,
    max_small_width: int,
    broad_source_coverage_min: int,
) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[ClauseOrbit]]]:
    """Canonicalize the predeclared small-or-broad source circuits."""

    templates_by_pattern: dict[str, list[dict[str, object]]] = {}
    orbits_by_pattern: dict[str, list[ClauseOrbit]] = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        templates = []
        orbits = []
        seen_hashes: set[str] = set()
        for row in run["compressed_models"]:
            width = int(row["compressed_unique_ordered_quad_count"])
            source_coverage = len(
                row["clause_coverage"]["translated_orbit_covered_targets"]
            )
            reasons = []
            if width <= max_small_width:
                reasons.append("WIDTH_AT_MOST_CONFIGURED_SMALL_THRESHOLD")
            if source_coverage >= broad_source_coverage_min:
                reasons.append("AFFINE_SOURCE_COVERAGE_AT_LEAST_CONFIGURED_MINIMUM")
            if not reasons:
                continue

            source_model_index = int(row["source_model_index"])
            certificate = row["compressed_certificate"]
            orbit = build_clause_orbit(name, source_model_index, certificate)
            canonical, clause = canonical_certificate_for_orbit(certificate, orbit)
            canonical_hash = clause_hash(clause)
            if canonical_hash != orbit.canonical_clause_sha256:
                raise AssertionError("canonical transfer-template hash drifted")
            if canonical_hash in seen_hashes:
                raise AssertionError(f"{name} duplicate transfer-template orbit")
            seen_hashes.add(canonical_hash)
            checked = check_certificate_dict(canonical)
            templates.append(
                {
                    "template_id": (
                        f"{name}:fresh-{source_model_index}:"
                        f"w{width}:{canonical_hash[:16]}"
                    ),
                    "pattern": name,
                    "source_target_id": str(row["source_target_id"]),
                    "source_model_index": source_model_index,
                    "selection_reasons": reasons,
                    "source_affine_covered_target_count": source_coverage,
                    "ordered_quad_count": width,
                    "canonical_clause_sha256": canonical_hash,
                    "canonical_ordered_quadrilaterals": [list(quad) for quad in clause],
                    "canonical_certificate_sha256": stable_json_sha256(canonical),
                    "canonical_certificate": canonical,
                    "positive_inequalities": checked.positive_inequalities,
                    "weight_sum": checked.weight_sum,
                    "max_weight": checked.max_weight,
                    "affine_clause_orbit": orbit.summary(),
                }
            )
            orbits.append(orbit)

        templates_by_pattern[name] = sorted(
            templates,
            key=lambda row: str(row["template_id"]),
        )
        orbits_by_pattern[name] = sorted(
            orbits,
            key=lambda orbit: orbit.source_model_index,
        )
    return templates_by_pattern, orbits_by_pattern


def first_stream_orders_by_pattern(
    payload: Mapping[str, Any],
) -> dict[str, list[list[int]]]:
    result = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        orders = [
            [int(label) for label in model["order"]]
            for model in run["fresh_stream"]["models"]
        ]
        keys = [dihedral_order_key(order) for order in orders]
        if len(keys) != len(set(keys)):
            raise AssertionError(f"{name} first fresh stream has dihedral repeats")
        result[name] = orders
    return result


def source_orders_by_pattern(
    payload: Mapping[str, Any],
) -> dict[str, list[tuple[str, list[int]]]]:
    result = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        result[name] = [
            (
                str(target["target_id"]),
                [int(label) for label in target["order"]],
            )
            for target in run["target_orders"]
        ]
    return result


def prior_order_records_by_pattern(
    payload: Mapping[str, Any],
) -> dict[str, list[tuple[str, list[int]]]]:
    result = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        result[name] = [
            (
                str(target["target_id"]),
                [int(label) for label in target["order"]],
            )
            for target in run["target_orders"]
        ]
    return result


def evaluated_order(
    name: str,
    packet_order_id: str,
    order: Sequence[int],
    templates: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> dict[str, object]:
    n, offsets = PATTERNS[name]
    values = [int(label) for label in order]
    audit = inverse_pair_audit(name, n, offsets, values)
    if audit["inverse_pair_conflicts"] != 0:
        raise AssertionError(f"{name} transfer target is not an inverse-pair escape")
    return {
        "packet_order_id": packet_order_id,
        "order": values,
        **order_record_hashes(values),
        "lightweight_filters": lightweight_summary(name, values),
        "inverse_pair_audit": audit,
        "template_matches": template_matches(values, templates, orbits),
    }


def coverage_summary(
    records: Sequence[Mapping[str, Any]],
    templates: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    by_template = {
        str(template["template_id"]): {
            "matched_orders": 0,
            "matched_strong_orders": 0,
            "matching_orbit_clause_occurrences": 0,
        }
        for template in templates
    }
    hit_histogram: Counter[int] = Counter()
    covered = 0
    strong = 0
    covered_strong = 0
    for record in records:
        matches = record["template_matches"]
        is_strong = bool(record["lightweight_filters"]["survives"])
        strong += int(is_strong)
        covered += int(bool(matches))
        covered_strong += int(bool(matches) and is_strong)
        hit_histogram[len(matches)] += 1
        for match in matches:
            row = by_template[str(match["template_id"])]
            row["matched_orders"] += 1
            row["matched_strong_orders"] += int(is_strong)
            row["matching_orbit_clause_occurrences"] += int(
                match["matching_orbit_clause_count"]
            )
    count = len(records)
    return {
        "order_count": count,
        "strong_order_count": strong,
        "covered_order_count": covered,
        "covered_order_fraction": covered / count if count else None,
        "covered_strong_order_count": covered_strong,
        "covered_strong_order_fraction": (covered_strong / strong if strong else None),
        "template_hit_count_histogram": {
            str(key): hit_histogram[key] for key in sorted(hit_histogram)
        },
        "by_template": [
            {"template_id": template_id, **by_template[template_id]}
            for template_id in sorted(by_template)
        ],
    }


def evaluate_packet(
    name: str,
    packet: Sequence[tuple[str, Sequence[int]]],
    templates: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> dict[str, object]:
    records = [
        evaluated_order(name, packet_order_id, order, templates, orbits)
        for packet_order_id, order in packet
    ]
    return {
        "records": records,
        "coverage": coverage_summary(records, templates),
    }


def transfer_decision(
    prior_coverage: Mapping[str, Any],
    second_coverage: Mapping[str, Any],
) -> dict[str, object]:
    prior_hits = int(prior_coverage["covered_order_count"])
    second_hits = int(second_coverage["covered_order_count"])
    return {
        "prior_packet_covered_order_count": prior_hits,
        "second_stream_covered_order_count": second_hits,
        "outside_source_packet_covered_order_count": prior_hits + second_hits,
        "decision": (
            "CONTINUE_EXACT_TEMPLATE_TRANSFER"
            if prior_hits + second_hits
            else "STOP_PACKET_SPECIFIC_TEMPLATE_MINING"
        ),
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    prior_path = (
        args.prior_packet
        if args.prior_packet.is_absolute()
        else ROOT / args.prior_packet
    )
    first_path = (
        args.first_fresh_stream
        if args.first_fresh_stream.is_absolute()
        else ROOT / args.first_fresh_stream
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    first = json.loads(first_path.read_text(encoding="utf-8"))

    templates_by_pattern, orbits_by_pattern = build_transfer_templates(
        source,
        max_small_width=args.max_small_width,
        broad_source_coverage_min=args.broad_source_coverage_min,
    )
    prior_records = prior_order_records_by_pattern(prior)
    prior_orders = historical_orders_by_pattern(prior)
    first_orders = first_stream_orders_by_pattern(first)
    source_orders = source_orders_by_pattern(source)

    selected_names = args.pattern or list(PATTERNS)
    runs = []
    for pattern_index, name in enumerate(selected_names):
        templates = templates_by_pattern[name]
        orbits = orbits_by_pattern[name]
        history = [*prior_orders[name], *first_orders[name]]
        history_keys = [dihedral_order_key(order) for order in history]
        if len(history_keys) != len(set(history_keys)):
            raise AssertionError(f"{name} combined transfer history is not disjoint")

        source_packet = evaluate_packet(
            name,
            source_orders[name],
            templates,
            orbits,
        )
        prior_packet = evaluate_packet(
            name,
            prior_records[name],
            templates,
            orbits,
        )
        random_seed = args.random_seed + pattern_index * args.pattern_seed_stride
        second = collect_fresh_orders(
            name,
            templates,
            orbits,
            history,
            order_limit=args.order_limit,
            max_iterations=args.max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=random_seed,
        )
        second["coverage"] = coverage_summary(second["models"], templates)
        n, offsets = PATTERNS[name]
        runs.append(
            {
                "pattern": name,
                "n": n,
                "circulant_offsets": offsets,
                "canonical_transfer_templates": templates,
                "source_packet": source_packet,
                "prior_packet": prior_packet,
                "combined_history_order_count": len(history),
                "combined_history_dihedral_order_count": len(set(history_keys)),
                "second_fresh_stream": second,
                "transfer_decision": transfer_decision(
                    prior_packet["coverage"],
                    second["coverage"],
                ),
            }
        )

    return {
        "type": "sparse_full_cone_fresh_template_transfer_v1",
        "trust": "EXACT_TEMPLATES_AND_BOUNDED_OUTSIDE_PACKET_TRANSFER_AUDIT",
        "status": "BOUNDED_PRIOR_PACKET_AND_SECOND_STREAM_TRANSFER_DIAGNOSTIC",
        "claim_scope": (
            "Four exact C25/C29 positive-circuit templates selected by a "
            "predeclared width-or-source-coverage rule are canonicalized and "
            "replayed against the prior 48-order packet and a second bounded "
            "deterministic stream dihedrally disjoint from both that packet and "
            "the first 64-order fresh stream. This is not an all-order "
            "obstruction, geometric realizability result, counterexample, proof "
            "of Erdos Problem #97, or official/global status update."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "prior_packet_artifact": prior_path.relative_to(ROOT).as_posix(),
        "prior_packet_sha256": file_sha256(prior_path),
        "first_fresh_stream_artifact": first_path.relative_to(ROOT).as_posix(),
        "first_fresh_stream_sha256": file_sha256(first_path),
        "configuration": {
            "max_small_width": args.max_small_width,
            "broad_source_coverage_min": args.broad_source_coverage_min,
            "fresh_order_limit_per_pattern": args.order_limit,
            "max_iterations_per_pattern": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "pattern_seed_stride": args.pattern_seed_stride,
            "freshness_equivalence": "cyclic rotation and reversal",
            "generation_filter": "exact two-inequality inverse-pair escape",
            "template_selection": (
                "compressed width at most max_small_width OR affine source "
                "coverage at least broad_source_coverage_min"
            ),
            "stopping_rule": (
                "stop packet-specific template mining only if both the prior "
                "packet and second history-disjoint stream have zero hits"
            ),
        },
        "runs": runs,
    }


def check_evaluated_packet(
    name: str,
    packet: Mapping[str, Any],
    expected_orders: Sequence[tuple[str, Sequence[int]]],
    templates: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> None:
    expected = evaluate_packet(name, expected_orders, templates, orbits)
    if packet != expected:
        raise AssertionError(f"{name} evaluated transfer packet drifted")


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_fresh_template_transfer_v1":
        raise AssertionError("fresh transfer artifact type drifted")
    source_path = ROOT / str(payload["source_artifact"])
    prior_path = ROOT / str(payload["prior_packet_artifact"])
    first_path = ROOT / str(payload["first_fresh_stream_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("fresh compression source hash drifted")
    if file_sha256(prior_path) != str(payload["prior_packet_sha256"]):
        raise AssertionError("prior packet hash drifted")
    if file_sha256(first_path) != str(payload["first_fresh_stream_sha256"]):
        raise AssertionError("first fresh stream hash drifted")

    source = json.loads(source_path.read_text(encoding="utf-8"))
    prior = json.loads(prior_path.read_text(encoding="utf-8"))
    first = json.loads(first_path.read_text(encoding="utf-8"))
    configuration = payload["configuration"]
    order_limit = int(configuration["fresh_order_limit_per_pattern"])
    max_iterations = int(configuration["max_iterations_per_pattern"])
    conflict_cap = int(configuration["conflict_cap"])
    base_seed = int(configuration["random_seed"])
    pattern_seed_stride = int(configuration["pattern_seed_stride"])
    templates_by_pattern, orbits_by_pattern = build_transfer_templates(
        source,
        max_small_width=int(configuration["max_small_width"]),
        broad_source_coverage_min=int(configuration["broad_source_coverage_min"]),
    )
    prior_records = prior_order_records_by_pattern(prior)
    prior_orders = historical_orders_by_pattern(prior)
    first_orders = first_stream_orders_by_pattern(first)
    source_orders = source_orders_by_pattern(source)

    verified_templates = 0
    verified_images = 0
    verified_source_orders = 0
    verified_prior_orders = 0
    verified_second_orders = 0
    outside_hits = 0
    decisions = []
    seen_patterns: set[str] = set()
    for pattern_index, run in enumerate(payload["runs"]):
        name = str(run["pattern"])
        if name in seen_patterns or name not in PATTERNS:
            raise AssertionError(f"invalid or duplicate transfer pattern: {name}")
        seen_patterns.add(name)
        templates = templates_by_pattern[name]
        orbits = orbits_by_pattern[name]
        if run["canonical_transfer_templates"] != templates:
            raise AssertionError(f"{name} transfer template packet drifted")
        verified_templates += len(templates)
        verified_images += sum(orbit.affine_map_count for orbit in orbits)

        check_evaluated_packet(
            name,
            run["source_packet"],
            source_orders[name],
            templates,
            orbits,
        )
        check_evaluated_packet(
            name,
            run["prior_packet"],
            prior_records[name],
            templates,
            orbits,
        )
        verified_source_orders += len(source_orders[name])
        verified_prior_orders += len(prior_records[name])

        history = [*prior_orders[name], *first_orders[name]]
        history_keys = {dihedral_order_key(order) for order in history}
        if len(history_keys) != len(history):
            raise AssertionError(f"{name} combined transfer history overlaps")
        if int(run["combined_history_order_count"]) != len(history):
            raise AssertionError(f"{name} combined history count drifted")
        if int(run["combined_history_dihedral_order_count"]) != len(history_keys):
            raise AssertionError(f"{name} combined dihedral count drifted")

        second = run["second_fresh_stream"]
        expected_seed = base_seed + pattern_index * pattern_seed_stride
        if int(second["random_seed"]) != expected_seed:
            raise AssertionError(f"{name} second-stream random seed drifted")
        iterations = int(second["iterations"])
        if not 1 <= iterations <= max_iterations:
            raise AssertionError(f"{name} second-stream iteration count drifted")
        inverse_clause_count = int(second["inverse_pair_clause_count"])
        if not 0 <= inverse_clause_count <= iterations * conflict_cap:
            raise AssertionError(f"{name} second-stream clause count drifted")
        models = second["models"]
        if int(second["fresh_inverse_pair_escape_order_count"]) != len(models):
            raise AssertionError(f"{name} second-stream count drifted")

        seen = set(history_keys)
        checked_models = []
        previous_z3_iteration = 0
        for expected_model_index, model in enumerate(models):
            if int(model["fresh_model_index"]) != expected_model_index:
                raise AssertionError(f"{name} second-stream model index drifted")
            z3_iteration = int(model["z3_iteration"])
            if not previous_z3_iteration < z3_iteration <= iterations:
                raise AssertionError(f"{name} second-stream iteration provenance drifted")
            previous_z3_iteration = z3_iteration
            order = [int(label) for label in model["order"]]
            n, offsets = PATTERNS[name]
            if sorted(order) != list(range(n)) or order[0] != 0:
                raise AssertionError(f"{name} invalid second-stream order")
            key = dihedral_order_key(order)
            if key in seen:
                raise AssertionError(f"{name} second stream is not history-disjoint")
            seen.add(key)
            for field, value in order_record_hashes(order).items():
                if model[field] != value:
                    raise AssertionError(f"{name} second-stream {field} drifted")
            audit = inverse_pair_audit(name, n, offsets, order)
            if model["inverse_pair_audit"] != audit:
                raise AssertionError(f"{name} second-stream inverse audit drifted")
            if audit["inverse_pair_conflicts"] != 0:
                raise AssertionError(f"{name} second stream has an inverse pair")
            if model["lightweight_filters"] != lightweight_summary(name, order):
                raise AssertionError(f"{name} second lightweight filters drifted")
            if model["template_matches"] != template_matches(order, templates, orbits):
                raise AssertionError(f"{name} second template matches drifted")
            checked_models.append(model)
            verified_second_orders += 1

        if len(checked_models) >= order_limit:
            if len(checked_models) != order_limit:
                raise AssertionError(f"{name} second-stream order limit drifted")
            if second["status"] != "BOUNDED_FRESH_ORDER_LIMIT_REACHED":
                raise AssertionError(f"{name} second-stream bounded status drifted")
            if (
                second["solver_result"]
                != "bounded_after_fresh_inverse_pair_escape_orders"
            ):
                raise AssertionError(f"{name} second-stream bounded result drifted")
            if iterations != previous_z3_iteration:
                raise AssertionError(f"{name} second-stream terminal iteration drifted")
        elif iterations == max_iterations:
            if second["status"] != "BOUNDED_FRESH_STREAM_ITERATION_LIMIT":
                raise AssertionError(f"{name} second-stream limit status drifted")
            if second["solver_result"] != "iteration_limit":
                raise AssertionError(f"{name} second-stream limit result drifted")
        elif second["status"] == "FRESH_STREAM_SOLVER_UNSAT":
            if second["solver_result"] != "unsat":
                raise AssertionError(f"{name} second-stream unsat result drifted")
        elif second["status"] != "UNKNOWN_FRESH_STREAM_SMT_RESULT":
            raise AssertionError(f"{name} second-stream termination status drifted")
        if inverse_clause_count < iterations - len(checked_models):
            raise AssertionError(f"{name} second-stream clause provenance drifted")
        if int(second["historical_dihedral_order_count"]) != len(history_keys):
            raise AssertionError(f"{name} second-stream history count drifted")
        expected_coverage = coverage_summary(checked_models, templates)
        if second["coverage"] != expected_coverage:
            raise AssertionError(f"{name} second-stream coverage drifted")
        expected_decision = transfer_decision(
            run["prior_packet"]["coverage"],
            expected_coverage,
        )
        if run["transfer_decision"] != expected_decision:
            raise AssertionError(f"{name} transfer decision drifted")
        outside_hits += int(
            expected_decision["outside_source_packet_covered_order_count"]
        )
        decisions.append(str(expected_decision["decision"]))

    return {
        "status": "OK",
        "verified_canonical_exact_templates": verified_templates,
        "verified_exact_affine_template_images": verified_images,
        "verified_source_packet_orders": verified_source_orders,
        "verified_prior_packet_orders": verified_prior_orders,
        "verified_second_history_disjoint_orders": verified_second_orders,
        "verified_outside_source_packet_covered_orders": outside_hits,
        "transfer_decisions": decisions,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--prior-packet", type=Path, default=DEFAULT_PRIOR_PACKET)
    parser.add_argument(
        "--first-fresh-stream",
        type=Path,
        default=DEFAULT_FIRST_FRESH_STREAM,
    )
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--max-small-width", type=int, default=12)
    parser.add_argument(
        "--broad-source-coverage-min",
        type=int,
        default=24,
    )
    parser.add_argument("--order-limit", type=int, default=32)
    parser.add_argument("--max-iterations", type=int, default=16_000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=20260802)
    parser.add_argument("--pattern-seed-stride", type=int, default=1000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    positive = (
        args.max_small_width,
        args.broad_source_coverage_min,
        args.order_limit,
        args.max_iterations,
        args.conflict_cap,
        args.pattern_seed_stride,
    )
    if any(value <= 0 for value in positive):
        raise SystemExit(
            "thresholds, limits, conflict cap, and stride must be positive"
        )
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
            source = run["source_packet"]["coverage"]
            prior = run["prior_packet"]["coverage"]
            second = run["second_fresh_stream"]["coverage"]
            decision = run["transfer_decision"]
            print(
                f"{run['pattern']}: "
                f"templates={len(run['canonical_transfer_templates'])} "
                f"source={source['covered_order_count']}/{source['order_count']} "
                f"prior={prior['covered_order_count']}/{prior['order_count']} "
                f"second={second['covered_order_count']}/{second['order_count']} "
                f"decision={decision['decision']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
