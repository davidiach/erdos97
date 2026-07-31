#!/usr/bin/env python3
"""Compare compressed C25 residual seed packets on a fresh order probe.

The source compression packet supplies eight exact residual circuits of widths
three through nine.  This bounded experiment blocks all 112 previously stored
C25 orders under rotation and reversal, generates a new inverse-pair-escape
probe without activating any full-cone seed clauses, and compares:

* the three transferred seed orbits;
* those three seeds plus the unique width-three residual orbit; and
* those three seeds plus all eight compressed residual orbits.

Every seed certificate and affine image is exact.  The Z3 order probe is
finite, history-blocked, and bounded, so no all-order obstruction, geometric
realizability result, counterexample, or proof of Erdos Problem #97 is claimed.
"""

from __future__ import annotations

import argparse
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
from compress_sparse_full_cone_c25_transfer_residuals import (  # noqa: E402
    check_payload as check_compression_payload,
    stable_json_sha256,
)
from pilot_sparse_full_cone_order_cegar import PATTERNS  # noqa: E402
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    dihedral_order_key,
    order_record_hashes,
)
from run_sparse_full_cone_c25_transfer_cegar import (  # noqa: E402
    PATTERN,
    c25_history,
    c25_seed_packet,
    check_order_record,
    check_payload as check_cegar_payload,
    collect_history_disjoint_probe,
    first_fresh_stream_path,
    history_identity,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    build_clause_orbit,
    clause_matches,
    file_sha256,
    unique_clauses,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_transfer_residual_compression_2026-07-29"
    / "summary.json"
)
DEFAULT_PROBE_ORDER_LIMIT = 32
DEFAULT_PROBE_MAX_ITERATIONS = 12_000
DEFAULT_CONFLICT_CAP = 1_024
DEFAULT_RANDOM_SEED = 20_260_729
DEFAULT_HISTORY_ORDER_COUNT = 112
HISTORY_EQUIVALENCE = "cyclic rotation and reversal"
PACKET_COMPARISON = (
    "transferred_only",
    "transferred_plus_width3",
    "transferred_plus_all_residuals",
)


def load_source_chain(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    Path,
    dict[str, Any],
    Path,
    dict[str, Any],
    Path,
    dict[str, Any],
]:
    """Load and validate the compression, CEGAR, transfer, and first stream."""

    compression = json.loads(source_path.read_text(encoding="utf-8"))
    check_compression_payload(compression)

    cegar_path = ROOT / str(compression["source_artifact"])
    if file_sha256(cegar_path) != str(compression["source_sha256"]):
        raise AssertionError("C25 augmentation CEGAR source hash drifted")
    cegar = json.loads(cegar_path.read_text(encoding="utf-8"))
    check_cegar_payload(cegar)

    transfer_path = ROOT / str(cegar["source_transfer_artifact"])
    if file_sha256(transfer_path) != str(cegar["source_transfer_sha256"]):
        raise AssertionError("C25 augmentation transfer source hash drifted")
    transfer = json.loads(transfer_path.read_text(encoding="utf-8"))

    first_path = first_fresh_stream_path(transfer)
    first = json.loads(first_path.read_text(encoding="utf-8"))
    return (
        compression,
        cegar_path,
        cegar,
        transfer_path,
        transfer,
        first_path,
        first,
    )


def augmented_history(
    transfer: Mapping[str, Any],
    first: Mapping[str, Any],
    cegar: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Return the 88 prior orders plus 16 probe and 8 residual orders."""

    history = c25_history(transfer, first)
    additions = (
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
    )
    seen = {dihedral_order_key(record["order"]) for record in history}
    for packet, index_key, models in additions:
        for model in models:
            index = int(model[index_key])
            order = [int(label) for label in model["order"]]
            key = dihedral_order_key(order)
            if key in seen:
                raise AssertionError("C25 augmented history has a dihedral duplicate")
            seen.add(key)
            hashes = order_record_hashes(order)
            if any(model[field] != value for field, value in hashes.items()):
                raise AssertionError("C25 augmented history order hash drifted")
            history.append(
                {
                    "history_id": f"{packet}:{index}",
                    "packet": packet,
                    "order": order,
                    **hashes,
                }
            )
    if len(history) != DEFAULT_HISTORY_ORDER_COUNT:
        raise AssertionError("C25 augmented history must contain 112 orders")
    return history


def seed_packets(
    compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[
    list[dict[str, object]],
    list[ClauseOrbit],
    list[dict[str, object]],
    list[ClauseOrbit],
]:
    """Reconstruct the three transferred and eight compressed residual seeds."""

    transferred_records, transferred_orbits = c25_seed_packet(transfer)
    residual_records = []
    residual_orbits = []
    seen_hashes = {orbit.canonical_clause_sha256 for orbit in transferred_orbits}
    for row in compression["run"]["compressed_models"]:
        model_index = int(row["source_model_index"])
        certificate = row["compressed_certificate"]
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("C25 residual augmentation seed failed exact replay")
        orbit = build_clause_orbit(PATTERN, model_index, certificate)
        if orbit.summary() != row["affine_clause_orbit"]:
            raise AssertionError("C25 residual augmentation orbit drifted")
        if orbit.canonical_clause_sha256 in seen_hashes:
            raise AssertionError("C25 augmentation seed orbit is duplicated")
        seen_hashes.add(orbit.canonical_clause_sha256)
        width = int(row["compressed_unique_ordered_quad_count"])
        residual_records.append(
            {
                "seed_id": f"residual:{model_index}",
                "source_target_id": str(row["source_target_id"]),
                "source_model_index": model_index,
                "ordered_quad_count": width,
                "compressed_certificate_sha256": stable_json_sha256(certificate),
                "positive_inequalities": checked.positive_inequalities,
                "weight_sum": checked.weight_sum,
                "max_weight": checked.max_weight,
                "affine_clause_orbit": orbit.summary(),
            }
        )
        residual_orbits.append(orbit)

    if len(transferred_orbits) != 3 or len(residual_orbits) != 8:
        raise AssertionError("unexpected C25 augmentation seed packet size")
    width_three = [
        record for record in residual_records if int(record["ordered_quad_count"]) == 3
    ]
    if len(width_three) != 1:
        raise AssertionError("C25 augmentation requires one width-three residual")
    return (
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    )


def packet_definitions(
    transferred_orbits: Sequence[ClauseOrbit],
    residual_records: Sequence[Mapping[str, Any]],
    residual_orbits: Sequence[ClauseOrbit],
) -> dict[str, list[ClauseOrbit]]:
    width_three_indices = [
        index
        for index, record in enumerate(residual_records)
        if int(record["ordered_quad_count"]) == 3
    ]
    if len(width_three_indices) != 1:
        raise AssertionError("C25 width-three packet selection drifted")
    width_three_orbit = residual_orbits[width_three_indices[0]]
    return {
        "transferred_only": list(transferred_orbits),
        "transferred_plus_width3": [*transferred_orbits, width_three_orbit],
        "transferred_plus_all_residuals": [
            *transferred_orbits,
            *residual_orbits,
        ],
    }


def model_packet_matches(
    order: Sequence[int],
    packets: Mapping[str, Sequence[ClauseOrbit]],
) -> dict[str, list[dict[str, object]]]:
    return {
        packet_id: clause_matches(order, orbits)
        for packet_id, orbits in packets.items()
    }


def packet_coverage(
    models: Sequence[Mapping[str, Any]],
    packets: Mapping[str, Sequence[ClauseOrbit]],
) -> list[dict[str, object]]:
    result = []
    for packet_id, orbits in packets.items():
        covered = []
        strong_covered = []
        occurrences = 0
        for model in models:
            matches = model["seed_packet_matches"][packet_id]
            if matches:
                index = int(model["probe_model_index"])
                covered.append(index)
                if bool(model["lightweight_filters"]["survives"]):
                    strong_covered.append(index)
                occurrences += sum(
                    int(match["matching_orbit_clause_count"]) for match in matches
                )
        result.append(
            {
                "packet_id": packet_id,
                "probe_order_count": len(models),
                "seed_orbit_count": len(orbits),
                "exact_affine_image_count": sum(
                    orbit.affine_map_count for orbit in orbits
                ),
                "unique_clause_count": len(unique_clauses(orbits)),
                "covered_probe_model_indices": covered,
                "covered_probe_order_count": len(covered),
                "covered_strong_probe_model_indices": strong_covered,
                "covered_strong_probe_order_count": len(strong_covered),
                "matching_orbit_clause_occurrences": occurrences,
            }
        )
    return result


def per_seed_coverage(
    models: Sequence[Mapping[str, Any]],
    transferred_records: Sequence[Mapping[str, Any]],
    transferred_orbits: Sequence[ClauseOrbit],
    residual_records: Sequence[Mapping[str, Any]],
    residual_orbits: Sequence[ClauseOrbit],
) -> list[dict[str, object]]:
    """Return exact individual-orbit coverage inside the fresh probe."""

    result = []
    families = (
        ("transferred", transferred_records, transferred_orbits),
        ("residual", residual_records, residual_orbits),
    )
    for family, records, orbits in families:
        for record, orbit in zip(records, orbits):
            covered = []
            strong_covered = []
            occurrences = 0
            for model in models:
                matches = clause_matches(model["order"], [orbit])
                if matches:
                    index = int(model["probe_model_index"])
                    covered.append(index)
                    if bool(model["lightweight_filters"]["survives"]):
                        strong_covered.append(index)
                    occurrences += int(matches[0]["matching_orbit_clause_count"])
            seed_id = (
                str(record["template_id"])
                if family == "transferred"
                else str(record["seed_id"])
            )
            result.append(
                {
                    "seed_family": family,
                    "seed_id": seed_id,
                    "source_model_index": orbit.source_model_index,
                    "ordered_quad_count": int(record["ordered_quad_count"]),
                    "exact_affine_image_count": orbit.affine_map_count,
                    "unique_clause_count": len(orbit.clauses),
                    "covered_probe_model_indices": covered,
                    "covered_probe_order_count": len(covered),
                    "covered_strong_probe_model_indices": strong_covered,
                    "covered_strong_probe_order_count": len(strong_covered),
                    "matching_orbit_clause_occurrences": occurrences,
                }
            )
    return result


def comparison_summary(
    coverage: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    by_packet = {str(record["packet_id"]): record for record in coverage}
    transferred = set(
        int(value)
        for value in by_packet["transferred_only"]["covered_probe_model_indices"]
    )
    width_three = set(
        int(value)
        for value in by_packet["transferred_plus_width3"]["covered_probe_model_indices"]
    )
    all_residuals = set(
        int(value)
        for value in by_packet["transferred_plus_all_residuals"][
            "covered_probe_model_indices"
        ]
    )
    if not transferred <= width_three <= all_residuals:
        raise AssertionError("C25 seed packet coverage is not monotone")
    probe_counts = {int(record["probe_order_count"]) for record in coverage}
    if len(probe_counts) != 1:
        raise AssertionError("C25 seed packet probe counts drifted")
    probe_order_count = probe_counts.pop()
    width_three_marginal = sorted(width_three - transferred)
    remaining_residual_marginal = sorted(all_residuals - width_three)
    if remaining_residual_marginal:
        decision = "CONTINUE_C25_CEGAR_WITH_ALL_RESIDUAL_ORBITS"
    elif width_three_marginal:
        decision = "CONTINUE_C25_CEGAR_WITH_WIDTH3_RESIDUAL_ORBIT_ONLY"
    else:
        decision = "STOP_C25_RESIDUAL_SEED_AUGMENTATION_AFTER_BOUNDED_PROBE"
    return {
        "width3_marginal_over_transferred_probe_model_indices": (width_three_marginal),
        "width3_marginal_over_transferred_order_count": len(width_three_marginal),
        "other_residuals_marginal_over_width3_probe_model_indices": (
            remaining_residual_marginal
        ),
        "other_residuals_marginal_over_width3_order_count": len(
            remaining_residual_marginal
        ),
        "full_packet_uncovered_probe_model_indices": sorted(
            set(range(probe_order_count)) - all_residuals
        ),
        "decision": decision,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    (
        compression,
        cegar_path,
        cegar,
        transfer_path,
        transfer,
        first_path,
        first,
    ) = load_source_chain(source_path)
    history = augmented_history(transfer, first, cegar)
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
    probe, _inverse_clauses = collect_history_disjoint_probe(
        all_orbits,
        history,
        order_limit=args.probe_order_limit,
        max_iterations=args.probe_max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
    )
    for model in probe["models"]:
        model["seed_packet_matches"] = model_packet_matches(model["order"], packets)
    coverage = packet_coverage(probe["models"], packets)
    comparison = comparison_summary(coverage)
    individual_coverage = per_seed_coverage(
        probe["models"],
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    )
    n, offsets = PATTERNS[PATTERN]
    return {
        "type": "sparse_full_cone_c25_residual_seed_augmentation_probe_v1",
        "trust": "EXACT_CLAUSE_COVERAGE_IN_BOUNDED_HISTORY_DISJOINT_C25_PROBE",
        "status": "BOUNDED_C25_RESIDUAL_SEED_PACKET_COMPARISON",
        "claim_scope": (
            "Exact coverage comparison for three nested C25 seed packets over "
            "one bounded inverse-pair-escape probe after 112 stored orders are "
            "blocked under rotation and reversal. Seed certificates and affine "
            "images are exact, but history blocking and finite limits preclude "
            "any all-order obstruction, geometric realizability result, "
            "counterexample, proof of Erdos Problem #97, or official/global "
            "status update."
        ),
        "source_compression_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_compression_sha256": file_sha256(source_path),
        "source_cegar_artifact": cegar_path.relative_to(ROOT).as_posix(),
        "source_cegar_sha256": file_sha256(cegar_path),
        "source_transfer_artifact": transfer_path.relative_to(ROOT).as_posix(),
        "source_transfer_sha256": file_sha256(transfer_path),
        "first_fresh_stream_artifact": first_path.relative_to(ROOT).as_posix(),
        "first_fresh_stream_sha256": file_sha256(first_path),
        "configuration": {
            "pattern": PATTERN,
            "probe_order_limit": args.probe_order_limit,
            "probe_max_iterations": args.probe_max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "history_equivalence": HISTORY_EQUIVALENCE,
            "history_order_count": len(history),
            "packet_comparison": list(PACKET_COMPARISON),
        },
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "transferred_seed_templates": transferred_records,
        "compressed_residual_seed_templates": residual_records,
        "blocked_history": {
            "order_count": len(history),
            "dihedral_order_count": len(
                {dihedral_order_key(record["order"]) for record in history}
            ),
            "packet_histogram": dict(
                sorted(Counter(str(record["packet"]) for record in history).items())
            ),
            "identities": history_identity(history),
        },
        "probe": probe,
        "packet_coverage": coverage,
        "per_seed_coverage": individual_coverage,
        "comparison": comparison,
    }


def check_source_chain_references(
    payload: Mapping[str, Any],
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    source_path = ROOT / str(payload["source_compression_artifact"])
    if file_sha256(source_path) != str(payload["source_compression_sha256"]):
        raise AssertionError("C25 augmentation compression hash drifted")
    (
        compression,
        cegar_path,
        cegar,
        transfer_path,
        transfer,
        first_path,
        first,
    ) = load_source_chain(source_path)
    expected = (
        (cegar_path, "source_cegar_artifact", "source_cegar_sha256"),
        (transfer_path, "source_transfer_artifact", "source_transfer_sha256"),
        (
            first_path,
            "first_fresh_stream_artifact",
            "first_fresh_stream_sha256",
        ),
    )
    for path, artifact_field, hash_field in expected:
        if payload[artifact_field] != path.relative_to(ROOT).as_posix():
            raise AssertionError(f"C25 augmentation {artifact_field} drifted")
        if payload[hash_field] != file_sha256(path):
            raise AssertionError(f"C25 augmentation {hash_field} drifted")
    return compression, cegar, transfer, first


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_residual_seed_augmentation_probe_v1":
        raise AssertionError("C25 augmentation artifact type drifted")
    source_path = ROOT / str(payload["source_compression_artifact"])
    if source_path.resolve() != DEFAULT_SOURCE.resolve():
        raise AssertionError("C25 augmentation source artifact drifted")
    configuration = payload["configuration"]
    expected_configuration = {
        "pattern": PATTERN,
        "probe_order_limit": DEFAULT_PROBE_ORDER_LIMIT,
        "probe_max_iterations": DEFAULT_PROBE_MAX_ITERATIONS,
        "conflict_cap": DEFAULT_CONFLICT_CAP,
        "random_seed": DEFAULT_RANDOM_SEED,
        "history_equivalence": HISTORY_EQUIVALENCE,
        "history_order_count": DEFAULT_HISTORY_ORDER_COUNT,
        "packet_comparison": list(PACKET_COMPARISON),
    }
    if configuration != expected_configuration:
        raise AssertionError("C25 augmentation configuration drifted")
    compression, cegar, transfer, first = check_source_chain_references(payload)
    n, offsets = PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or configuration["pattern"] != PATTERN:
        raise AssertionError("C25 augmentation pattern drifted")
    if int(payload["n"]) != n or payload["circulant_offsets"] != list(offsets):
        raise AssertionError("C25 augmentation circulant metadata drifted")

    history = augmented_history(transfer, first, cegar)
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    expected_history = {
        "order_count": len(history),
        "dihedral_order_count": len(history_keys),
        "packet_histogram": dict(
            sorted(Counter(str(record["packet"]) for record in history).items())
        ),
        "identities": history_identity(history),
    }
    if payload["blocked_history"] != expected_history:
        raise AssertionError("C25 augmentation history drifted")
    if int(configuration["history_order_count"]) != len(history):
        raise AssertionError("C25 augmentation history configuration drifted")

    (
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    ) = seed_packets(compression, transfer)
    if payload["transferred_seed_templates"] != transferred_records:
        raise AssertionError("C25 transferred augmentation seeds drifted")
    if payload["compressed_residual_seed_templates"] != residual_records:
        raise AssertionError("C25 residual augmentation seeds drifted")
    packets = packet_definitions(
        transferred_orbits,
        residual_records,
        residual_orbits,
    )
    if configuration["packet_comparison"] != list(packets):
        raise AssertionError("C25 augmentation packet comparison drifted")

    probe = payload["probe"]
    models = probe["models"]
    probe_order_limit = DEFAULT_PROBE_ORDER_LIMIT
    probe_max_iterations = DEFAULT_PROBE_MAX_ITERATIONS
    conflict_cap = DEFAULT_CONFLICT_CAP
    iterations = int(probe["iterations"])
    if not 1 <= iterations <= probe_max_iterations:
        raise AssertionError("C25 augmentation probe iteration count drifted")
    inverse_count = int(probe["inverse_pair_clause_count"])
    if not 0 <= inverse_count <= iterations * conflict_cap:
        raise AssertionError("C25 augmentation inverse clause count drifted")
    if int(probe["blocked_history_dihedral_order_count"]) != len(history_keys):
        raise AssertionError("C25 augmentation blocked history count drifted")

    seen = set(history_keys)
    previous_iteration = 0
    verified_orders = 0
    all_orbits = packets["transferred_plus_all_residuals"]
    for expected_index, model in enumerate(models):
        if int(model["probe_model_index"]) != expected_index:
            raise AssertionError("C25 augmentation probe model index drifted")
        z3_iteration = int(model["z3_iteration"])
        if not previous_iteration < z3_iteration <= iterations:
            raise AssertionError("C25 augmentation probe iteration drifted")
        previous_iteration = z3_iteration
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("C25 augmentation probe is not history-disjoint")
        seen.add(key)
        if model["seed_orbit_matches"] != clause_matches(order, all_orbits):
            raise AssertionError("C25 augmentation all-seed matches drifted")
        expected_matches = model_packet_matches(order, packets)
        if model["seed_packet_matches"] != expected_matches:
            raise AssertionError("C25 augmentation packet matches drifted")
        verified_orders += 1

    if int(probe["inverse_pair_escape_order_count"]) != len(models):
        raise AssertionError("C25 augmentation probe order count drifted")
    if len(models) >= probe_order_limit:
        if len(models) != probe_order_limit:
            raise AssertionError("C25 augmentation probe limit drifted")
        if probe["status"] != "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED":
            raise AssertionError("C25 augmentation bounded status drifted")
        if probe["solver_result"] != "bounded_after_inverse_pair_escape_models":
            raise AssertionError("C25 augmentation bounded result drifted")
        if iterations != previous_iteration:
            raise AssertionError("C25 augmentation terminal iteration drifted")
    elif iterations == probe_max_iterations:
        if probe["status"] != "BOUNDED_HISTORY_DISJOINT_PROBE_ITERATION_LIMIT":
            raise AssertionError("C25 augmentation iteration-limit status drifted")
        if probe["solver_result"] != "iteration_limit":
            raise AssertionError("C25 augmentation iteration-limit result drifted")
    elif probe["status"] == "HISTORY_DISJOINT_PROBE_SOLVER_UNSAT":
        if probe["solver_result"] != "unsat":
            raise AssertionError("C25 augmentation unsat result drifted")
    elif probe["status"] != "UNKNOWN_HISTORY_DISJOINT_PROBE_SMT_RESULT":
        raise AssertionError("C25 augmentation termination status drifted")

    expected_coverage = packet_coverage(models, packets)
    if payload["packet_coverage"] != expected_coverage:
        raise AssertionError("C25 augmentation packet coverage drifted")
    expected_individual_coverage = per_seed_coverage(
        models,
        transferred_records,
        transferred_orbits,
        residual_records,
        residual_orbits,
    )
    if payload["per_seed_coverage"] != expected_individual_coverage:
        raise AssertionError("C25 augmentation individual seed coverage drifted")
    expected_comparison = comparison_summary(expected_coverage)
    if payload["comparison"] != expected_comparison:
        raise AssertionError("C25 augmentation comparison drifted")
    return {
        "status": "OK",
        "verified_blocked_history_orders": len(history),
        "verified_probe_orders": verified_orders,
        "verified_transferred_seed_certificates": len(transferred_orbits),
        "verified_residual_seed_certificates": len(residual_orbits),
        "verified_exact_affine_seed_images": sum(
            orbit.affine_map_count for orbit in all_orbits
        ),
        "decision": str(expected_comparison["decision"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument(
        "--probe-order-limit",
        type=int,
        default=DEFAULT_PROBE_ORDER_LIMIT,
    )
    parser.add_argument(
        "--probe-max-iterations",
        type=int,
        default=DEFAULT_PROBE_MAX_ITERATIONS,
    )
    parser.add_argument("--conflict-cap", type=int, default=DEFAULT_CONFLICT_CAP)
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    limits = (
        args.probe_order_limit,
        args.probe_max_iterations,
        args.conflict_cap,
    )
    if any(value <= 0 for value in limits):
        raise SystemExit("all probe limits and conflict cap must be positive")
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
        coverage = {
            str(record["packet_id"]): int(record["covered_probe_order_count"])
            for record in payload["packet_coverage"]
        }
        print(
            f"{PATTERN}: "
            f"history={payload['blocked_history']['order_count']} "
            f"probe={payload['probe']['inverse_pair_escape_order_count']} "
            f"coverage={coverage} "
            f"decision={payload['comparison']['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
