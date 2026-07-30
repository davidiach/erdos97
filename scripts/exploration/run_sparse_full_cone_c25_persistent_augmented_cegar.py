#!/usr/bin/env python3
"""Run C25 CEGAR with the selected persistent width-four seed orbit.

The source compression packet selects one exact width-four positive-circuit
orbit as the minimum cover of every target marginal over the eleven older C25
seed orbits.  This bounded follow-up blocks the complete current 144-order
history, keeps only the three transferred seeds plus that width-four orbit
active, compares their coverage on a fresh inverse-pair-escape probe, and
learns new exact full-cone certificate orbits from seed-escaping orders.

The dominated width-five persistent orbit and all eight zero-marginal
compressed residual orbits are explicitly inactive.  History blocking and
finite limits make this a fixed-pattern search diagnostic only.  No solver
status here is an all-order obstruction, geometric realizability result,
counterexample, or proof of Erdos Problem #97.
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
from compress_sparse_full_cone_c25_persistent_escapes import (  # noqa: E402
    check_payload as check_compression_payload,
    current_c25_targets,
    load_source_chain,
    stable_json_sha256,
)
from compress_sparse_full_cone_certificates import (  # noqa: E402
    order_satisfies_quads,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from probe_sparse_full_cone_c25_residual_seed_augmentation import (  # noqa: E402
    seed_packets,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    dihedral_order_key,
)
from run_sparse_full_cone_c25_transfer_cegar import (  # noqa: E402
    PATTERN,
    c25_seed_packet,
    check_order_record,
    collect_history_disjoint_probe,
    history_identity,
    run_history_disjoint_seeded_cegar,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    FullClause,
    build_clause_orbit,
    clause_matches,
    file_sha256,
    probe_coverage_summary,
    unique_clauses,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_escape_compression_2026-07-30"
    / "summary.json"
)
DEFAULT_PROBE_ORDER_LIMIT = 16
DEFAULT_PROBE_MAX_ITERATIONS = 12_000
DEFAULT_FULL_CERTIFICATE_LIMIT = 8
DEFAULT_MAX_ITERATIONS = 12_000
DEFAULT_CONFLICT_CAP = 1_024
DEFAULT_RANDOM_SEED = 20_260_730
SELECTED_SOURCE_TARGET_ID = "transfer_cegar_probe:0"
INACTIVE_PERSISTENT_SOURCE_TARGET_ID = "transfer_cegar_probe:1"
CERTIFICATE_LIMIT_STATUS = (
    "BOUNDED_C25_PERSISTENT_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
)
CONTINUE_DECISION = "COMPRESS_NEW_C25_PERSISTENT_AUGMENTED_RESIDUALS"
REVIEW_DECISION = "REVIEW_C25_PERSISTENT_AUGMENTED_CEGAR_BEFORE_CONTINUING"


def load_sources(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Replay the compression source and return its C25 provenance payloads."""

    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_compression_payload(source)
    screen_path = ROOT / str(source["source_screen_artifact"])
    (
        _screen,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = load_source_chain(screen_path)
    return (
        source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    )


def blocked_history(
    augmentation: Mapping[str, Any],
    prior_cegar: Mapping[str, Any],
    transfer: Mapping[str, Any],
    first: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Return the complete current 144-order C25 history."""

    targets = current_c25_targets(augmentation, prior_cegar, transfer, first)
    history = [
        {
            "history_id": str(target["target_id"]),
            "packet": str(target["stream"]),
            "order": [int(label) for label in target["order"]],
            "order_sha256": str(target["order_sha256"]),
            "dihedral_order_sha256": str(target["dihedral_order_sha256"]),
        }
        for target in targets
    ]
    keys = {dihedral_order_key(record["order"]) for record in history}
    if len(history) != 144 or len(keys) != len(history):
        raise AssertionError("persistent augmented history must have 144 classes")
    return history


def selected_seed_record(
    row: Mapping[str, Any],
    orbit: ClauseOrbit,
) -> dict[str, object]:
    certificate = row["compressed_certificate"]
    checked = check_certificate_dict(certificate)
    if not checked.zero_sum_verified:
        raise AssertionError("selected persistent seed failed exact replay")
    return {
        "seed_id": "persistent_compressed:0",
        "seed_role": "PRIMARY_MINIMUM_NEW_MARGINAL_COVER",
        "source_target_id": str(row["source_target_id"]),
        "source_screen_target_id": str(row["source_screen_target_id"]),
        "source_model_index": int(row["source_model_index"]),
        "ordered_quad_count": int(row["compressed_unique_ordered_quad_count"]),
        "compressed_certificate_sha256": str(
            row["compressed_certificate_sha256"]
        ),
        "positive_inequalities": checked.positive_inequalities,
        "weight_sum": checked.weight_sum,
        "max_weight": checked.max_weight,
        "affine_clause_orbit": orbit.summary(),
    }


def inactive_persistent_record(row: Mapping[str, Any]) -> dict[str, object]:
    return {
        "seed_id": "persistent_compressed:1",
        "source_target_id": str(row["source_target_id"]),
        "source_screen_target_id": str(row["source_screen_target_id"]),
        "source_model_index": int(row["source_model_index"]),
        "ordered_quad_count": int(row["compressed_unique_ordered_quad_count"]),
        "compressed_certificate_sha256": str(
            row["compressed_certificate_sha256"]
        ),
        "inactive_reason": (
            "ZERO_MARGINAL_TARGETS_BEYOND_SELECTED_WIDTH4_ON_144_ORDER_PACKET"
        ),
    }


def inactive_residual_records(
    residual_records: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    return [
        {
            "seed_id": str(record["seed_id"]),
            "source_target_id": str(record["source_target_id"]),
            "source_model_index": int(record["source_model_index"]),
            "ordered_quad_count": int(record["ordered_quad_count"]),
            "compressed_certificate_sha256": str(
                record["compressed_certificate_sha256"]
            ),
            "canonical_clause_sha256": str(
                record["affine_clause_orbit"]["canonical_clause_sha256"]
            ),
            "inactive_reason": (
                "ZERO_MARGINAL_COVERAGE_ON_32_ORDER_AUGMENTATION_PROBE"
            ),
        }
        for record in residual_records
    ]


def seed_selection(
    source: Mapping[str, Any],
    residual_compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[
    list[dict[str, object]],
    list[ClauseOrbit],
    dict[str, object],
    list[dict[str, object]],
]:
    """Return the four active orbits and the explicitly inactive packet."""

    transferred_records, transferred_orbits = c25_seed_packet(transfer)
    selected_ids = source["stopping_assessment"][
        "minimum_new_marginal_cover_source_target_ids"
    ]
    if selected_ids != [SELECTED_SOURCE_TARGET_ID]:
        raise AssertionError("persistent minimum marginal cover selection drifted")
    rows = {
        str(row["source_target_id"]): row for row in source["compressed_models"]
    }
    if set(rows) != {
        SELECTED_SOURCE_TARGET_ID,
        INACTIVE_PERSISTENT_SOURCE_TARGET_ID,
    }:
        raise AssertionError("persistent compressed source packet drifted")

    selected_row = rows[SELECTED_SOURCE_TARGET_ID]
    selected_orbit = build_clause_orbit(
        PATTERN,
        int(selected_row["source_model_index"]),
        selected_row["compressed_certificate"],
    )
    if selected_orbit.summary() != selected_row["affine_clause_orbit"]:
        raise AssertionError("selected persistent affine orbit drifted")
    active_orbits = [*transferred_orbits, selected_orbit]
    hashes = [orbit.canonical_clause_sha256 for orbit in active_orbits]
    if len(hashes) != len(set(hashes)):
        raise AssertionError("persistent augmented active seed orbit duplicated")

    (
        residual_transferred_records,
        residual_transferred_orbits,
        residual_records,
        _residual_orbits,
    ) = seed_packets(residual_compression, transfer)
    if residual_transferred_records != transferred_records:
        raise AssertionError("persistent transferred seed summaries drifted")
    if [
        orbit.canonical_clause_sha256 for orbit in residual_transferred_orbits
    ] != [
        orbit.canonical_clause_sha256 for orbit in transferred_orbits
    ]:
        raise AssertionError("persistent transferred seed orbits drifted")

    selected_record = selected_seed_record(selected_row, selected_orbit)
    inactive_persistent = inactive_persistent_record(
        rows[INACTIVE_PERSISTENT_SOURCE_TARGET_ID]
    )
    inactive_residuals = inactive_residual_records(residual_records)
    if len(inactive_residuals) != 8:
        raise AssertionError("persistent augmented residual packet drifted")
    return (
        transferred_records,
        active_orbits,
        selected_record,
        [inactive_persistent, *inactive_residuals],
    )


def coverage_for(
    models: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> dict[str, object]:
    rows = [
        {
            **model,
            "seed_orbit_matches": clause_matches(model["order"], orbits),
        }
        for model in models
    ]
    return probe_coverage_summary(rows, orbits)


def probe_packet_comparison(
    models: Sequence[Mapping[str, Any]],
    transferred_orbits: Sequence[ClauseOrbit],
    selected_orbit: ClauseOrbit,
) -> dict[str, object]:
    active_orbits = [*transferred_orbits, selected_orbit]
    transferred = coverage_for(models, transferred_orbits)
    selected = coverage_for(models, [selected_orbit])
    active = coverage_for(models, active_orbits)
    transferred_covered = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], transferred_orbits)
    }
    selected_covered = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], [selected_orbit])
    }
    return {
        "transferred_only": transferred,
        "selected_width4_only": selected,
        "transferred_plus_selected_width4": active,
        "selected_width4_marginal_over_transferred_probe_model_indices": sorted(
            selected_covered - transferred_covered
        ),
        "transferred_uncovered_probe_model_indices": sorted(
            set(range(len(models))) - transferred_covered
        ),
        "active_uncovered_probe_model_indices": sorted(
            set(range(len(models))) - (transferred_covered | selected_covered)
        ),
    }


def route_decision(
    probe: Mapping[str, Any],
    comparison: Mapping[str, Any],
    seeded: Mapping[str, Any],
    *,
    full_certificate_limit: int,
) -> str:
    probe_count = int(probe["inverse_pair_escape_order_count"])
    transferred_covered = int(
        comparison["transferred_only"]["covered_probe_order_count"]
    )
    selected_covered = int(
        comparison["selected_width4_only"]["covered_probe_order_count"]
    )
    active_covered = int(
        comparison["transferred_plus_selected_width4"][
            "covered_probe_order_count"
        ]
    )
    certificates = int(seeded["new_full_certificate_count"])
    unresolved = sum(
        "certificate" not in model["full_kalmanson"]
        for model in seeded["models"]
    )
    if (
        probe_count > 0
        and transferred_covered == 0
        and selected_covered == probe_count
        and active_covered == probe_count
        and certificates == full_certificate_limit
        and unresolved == 0
        and seeded["status"] == CERTIFICATE_LIMIT_STATUS
    ):
        return CONTINUE_DECISION
    return REVIEW_DECISION


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    (
        source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = load_sources(source_path)
    history = blocked_history(augmentation, prior_cegar, transfer, first)
    (
        transferred_records,
        active_orbits,
        selected_record,
        inactive_records,
    ) = seed_selection(source, residual_compression, transfer)
    transferred_orbits = active_orbits[:-1]
    selected_orbit = active_orbits[-1]

    probe, inverse_clauses = collect_history_disjoint_probe(
        active_orbits,
        history,
        order_limit=args.probe_order_limit,
        max_iterations=args.probe_max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
    )
    comparison = probe_packet_comparison(
        probe["models"],
        transferred_orbits,
        selected_orbit,
    )
    seeded = run_history_disjoint_seeded_cegar(
        active_orbits,
        history,
        inverse_clauses,
        full_certificate_limit=args.full_certificate_limit,
        max_iterations=args.max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
        certificate_limit_status=CERTIFICATE_LIMIT_STATUS,
    )
    decision = route_decision(
        probe,
        comparison,
        seeded,
        full_certificate_limit=args.full_certificate_limit,
    )
    n, offsets = PATTERNS[PATTERN]
    return {
        "type": "sparse_full_cone_c25_persistent_augmented_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_144_HISTORY_C25_CEGAR",
        "status": "BOUNDED_C25_PERSISTENT_WIDTH4_AUGMENTED_CEGAR",
        "claim_scope": (
            "Three transferred exact C25 certificate orbits plus one selected "
            "exact width-four persistent orbit seed a bounded order CEGAR "
            "after 144 known C25 orders are blocked under rotation and "
            "reversal. Probe coverage, newly learned certificates, and affine "
            "images are exact, but finite limits and history blocking preclude "
            "any all-order obstruction, geometric realizability result, "
            "counterexample, proof of Erdos Problem #97, or official/global "
            "status update."
        ),
        "source_compression_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_compression_sha256": file_sha256(source_path),
        "configuration": {
            "pattern": PATTERN,
            "probe_order_limit": args.probe_order_limit,
            "probe_max_iterations": args.probe_max_iterations,
            "full_certificate_limit": args.full_certificate_limit,
            "max_iterations": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "tolerance": 1.0e-9,
            "history_equivalence": "cyclic rotation and reversal",
            "active_seed_policy": (
                "three transferred orbits plus exact minimum new-marginal "
                "persistent width-four orbit only"
            ),
            "inactive_seed_policy": (
                "dominated persistent width-five orbit and eight zero-marginal "
                "compressed residual orbits"
            ),
        },
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "transferred_seed_templates": transferred_records,
        "selected_persistent_seed_template": selected_record,
        "inactive_seed_templates": inactive_records,
        "active_seed_orbit_count": len(active_orbits),
        "active_exact_affine_seed_image_count": sum(
            orbit.affine_map_count for orbit in active_orbits
        ),
        "distinct_active_seed_orbit_class_count": len(
            {orbit.canonical_clause_sha256 for orbit in active_orbits}
        ),
        "unique_active_seed_orbit_clause_count": len(unique_clauses(active_orbits)),
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
        "counterfactual_probe": probe,
        "counterfactual_seed_packet_coverage": comparison,
        "seeded_cegar": seeded,
        "decision": decision,
        "next_target": (
            "Compress the eight newly learned exact C25 residual certificates, "
            "construct their quotient-preserving affine orbits, and measure "
            "marginal reuse before increasing the order-search budget."
        ),
    }


def check_probe(
    probe: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
    active_orbits: Sequence[ClauseOrbit],
    *,
    order_limit: int,
    max_iterations: int,
    conflict_cap: int,
) -> int:
    n, offsets = PATTERNS[PATTERN]
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    if int(probe["blocked_history_dihedral_order_count"]) != len(history_keys):
        raise AssertionError("persistent augmented probe history count drifted")
    iterations = int(probe["iterations"])
    if not 1 <= iterations <= max_iterations:
        raise AssertionError("persistent augmented probe iterations drifted")
    inverse_count = int(probe["inverse_pair_clause_count"])
    if not 0 <= inverse_count <= iterations * conflict_cap:
        raise AssertionError("persistent augmented probe inverse clauses drifted")

    models = probe["models"]
    seen = set(history_keys)
    previous_iteration = 0
    for expected_index, model in enumerate(models):
        if int(model["probe_model_index"]) != expected_index:
            raise AssertionError("persistent augmented probe index drifted")
        iteration = int(model["z3_iteration"])
        if not previous_iteration < iteration <= iterations:
            raise AssertionError("persistent augmented probe provenance drifted")
        previous_iteration = iteration
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("persistent augmented probe is not disjoint")
        seen.add(key)
        expected_matches = clause_matches(order, active_orbits)
        if model["seed_orbit_matches"] != expected_matches:
            raise AssertionError("persistent augmented probe matches drifted")

    if int(probe["inverse_pair_escape_order_count"]) != len(models):
        raise AssertionError("persistent augmented probe count drifted")
    if len(models) != order_limit:
        raise AssertionError("persistent augmented probe did not reach limit")
    if probe["status"] != "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED":
        raise AssertionError("persistent augmented probe status drifted")
    if probe["solver_result"] != "bounded_after_inverse_pair_escape_models":
        raise AssertionError("persistent augmented probe result drifted")
    if iterations != previous_iteration:
        raise AssertionError("persistent augmented probe terminal iteration drifted")
    return inverse_count


def check_seeded_cegar(
    seeded: Mapping[str, Any],
    history: Sequence[Mapping[str, Any]],
    active_orbits: Sequence[ClauseOrbit],
    *,
    initial_inverse_count: int,
    full_certificate_limit: int,
    max_iterations: int,
    conflict_cap: int,
) -> dict[str, int]:
    n, offsets = PATTERNS[PATTERN]
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    if int(seeded["blocked_history_dihedral_order_count"]) != len(history_keys):
        raise AssertionError("persistent augmented seeded history drifted")
    if int(seeded["active_unique_seed_orbit_clause_count"]) != len(
        unique_clauses(active_orbits)
    ):
        raise AssertionError("persistent augmented active clauses drifted")
    iterations = int(seeded["iterations"])
    if not 1 <= iterations <= max_iterations:
        raise AssertionError("persistent augmented seeded iterations drifted")
    if int(seeded["initial_probe_inverse_clause_count"]) != initial_inverse_count:
        raise AssertionError("persistent augmented initial clauses drifted")
    final_inverse_count = int(seeded["final_inverse_pair_clause_count"])
    if not initial_inverse_count <= final_inverse_count <= (
        initial_inverse_count + iterations * conflict_cap
    ):
        raise AssertionError("persistent augmented final clauses drifted")

    learned_clauses: set[FullClause] = set()
    seen = set(history_keys)
    verified_certificates = 0
    verified_images = sum(orbit.affine_map_count for orbit in active_orbits)
    previous_iteration = 0
    previous_clause_count = initial_inverse_count
    models = seeded["models"]
    for expected_index, model in enumerate(models):
        if int(model["model_index"]) != expected_index:
            raise AssertionError("persistent augmented model index drifted")
        iteration = int(model["z3_iteration"])
        if not previous_iteration < iteration <= iterations:
            raise AssertionError("persistent augmented model provenance drifted")
        previous_iteration = iteration
        discovery_count = int(model["inverse_clause_count_at_discovery"])
        if not previous_clause_count <= discovery_count <= final_inverse_count:
            raise AssertionError("persistent augmented clause provenance drifted")
        previous_clause_count = discovery_count
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("persistent augmented model is not disjoint")
        seen.add(key)
        expected_matches = clause_matches(order, active_orbits)
        if model["seed_orbit_matches"] != expected_matches or expected_matches:
            raise AssertionError("persistent augmented active seed match drifted")
        prior_matches = sum(
            order_satisfies_quads(order, clause) for clause in learned_clauses
        )
        if int(model["prior_learned_orbit_clause_matches"]) != prior_matches:
            raise AssertionError("persistent augmented learned match drifted")
        if prior_matches:
            raise AssertionError("persistent augmented prior clause admitted model")

        full = model["full_kalmanson"]
        certificate = full.get("certificate")
        if certificate is None:
            raise AssertionError("persistent augmented stored unresolved model")
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("persistent augmented certificate failed")
        for field, value in {
            "status": checked.status,
            "positive_inequalities": checked.positive_inequalities,
            "weight_sum": checked.weight_sum,
            "max_weight": checked.max_weight,
            "zero_sum_verified": checked.zero_sum_verified,
        }.items():
            if full[field] != value:
                raise AssertionError(
                    f"persistent augmented certificate {field} drifted"
                )
        if stable_json_sha256(certificate) != full["certificate_sha256"]:
            raise AssertionError("persistent augmented certificate hash drifted")
        quads = certificate_order_quads(certificate, order)
        if len(quads) != int(full["unique_ordered_quad_count"]):
            raise AssertionError("persistent augmented certificate width drifted")
        orbit = build_clause_orbit(PATTERN, expected_index, certificate)
        if orbit.summary() != full["affine_clause_orbit"]:
            raise AssertionError("persistent augmented learned orbit drifted")
        new_clauses = [
            clause for clause in orbit.clauses if clause not in learned_clauses
        ]
        if len(new_clauses) != int(
            full["new_unique_affine_orbit_clauses_added"]
        ):
            raise AssertionError("persistent augmented learned clauses drifted")
        learned_clauses.update(new_clauses)
        verified_certificates += 1
        verified_images += orbit.affine_map_count

    if verified_certificates != full_certificate_limit:
        raise AssertionError("persistent augmented certificate limit drifted")
    if int(seeded["new_full_certificate_count"]) != verified_certificates:
        raise AssertionError("persistent augmented certificate count drifted")
    if int(seeded["new_unique_affine_orbit_clause_count"]) != len(
        learned_clauses
    ):
        raise AssertionError("persistent augmented learned clause total drifted")
    if seeded["status"] != CERTIFICATE_LIMIT_STATUS:
        raise AssertionError("persistent augmented terminal status drifted")
    if seeded["solver_result"] != "bounded_after_new_exact_certificates":
        raise AssertionError("persistent augmented terminal result drifted")
    if iterations != previous_iteration:
        raise AssertionError("persistent augmented terminal iteration drifted")
    return {
        "verified_certificates": verified_certificates,
        "verified_images": verified_images,
        "verified_learned_clauses": len(learned_clauses),
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_persistent_augmented_cegar_v1":
        raise AssertionError("persistent augmented artifact type drifted")
    source_path = ROOT / str(payload["source_compression_artifact"])
    if file_sha256(source_path) != str(payload["source_compression_sha256"]):
        raise AssertionError("persistent augmented source hash drifted")
    (
        source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = load_sources(source_path)
    configuration = payload["configuration"]
    expected_configuration = {
        "pattern": PATTERN,
        "probe_order_limit": DEFAULT_PROBE_ORDER_LIMIT,
        "probe_max_iterations": DEFAULT_PROBE_MAX_ITERATIONS,
        "full_certificate_limit": DEFAULT_FULL_CERTIFICATE_LIMIT,
        "max_iterations": DEFAULT_MAX_ITERATIONS,
        "conflict_cap": DEFAULT_CONFLICT_CAP,
        "random_seed": DEFAULT_RANDOM_SEED,
        "tolerance": 1.0e-9,
        "history_equivalence": "cyclic rotation and reversal",
        "active_seed_policy": (
            "three transferred orbits plus exact minimum new-marginal "
            "persistent width-four orbit only"
        ),
        "inactive_seed_policy": (
            "dominated persistent width-five orbit and eight zero-marginal "
            "compressed residual orbits"
        ),
    }
    if configuration != expected_configuration:
        raise AssertionError("persistent augmented configuration drifted")
    n, offsets = PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or int(payload["n"]) != n:
        raise AssertionError("persistent augmented pattern drifted")
    if payload["circulant_offsets"] != list(offsets):
        raise AssertionError("persistent augmented offsets drifted")

    history = blocked_history(augmentation, prior_cegar, transfer, first)
    expected_history = {
        "order_count": len(history),
        "dihedral_order_count": len(
            {dihedral_order_key(record["order"]) for record in history}
        ),
        "packet_histogram": dict(
            sorted(Counter(str(record["packet"]) for record in history).items())
        ),
        "identities": history_identity(history),
    }
    if payload["blocked_history"] != expected_history:
        raise AssertionError("persistent augmented history drifted")

    (
        transferred_records,
        active_orbits,
        selected_record,
        inactive_records,
    ) = seed_selection(source, residual_compression, transfer)
    if payload["transferred_seed_templates"] != transferred_records:
        raise AssertionError("persistent augmented transferred seeds drifted")
    if payload["selected_persistent_seed_template"] != selected_record:
        raise AssertionError("persistent augmented selected seed drifted")
    if payload["inactive_seed_templates"] != inactive_records:
        raise AssertionError("persistent augmented inactive seeds drifted")
    if int(payload["active_seed_orbit_count"]) != len(active_orbits):
        raise AssertionError("persistent augmented seed count drifted")
    if int(payload["active_exact_affine_seed_image_count"]) != sum(
        orbit.affine_map_count for orbit in active_orbits
    ):
        raise AssertionError("persistent augmented seed images drifted")
    if int(payload["distinct_active_seed_orbit_class_count"]) != len(
        {orbit.canonical_clause_sha256 for orbit in active_orbits}
    ):
        raise AssertionError("persistent augmented seed classes drifted")
    if int(payload["unique_active_seed_orbit_clause_count"]) != len(
        unique_clauses(active_orbits)
    ):
        raise AssertionError("persistent augmented seed clauses drifted")

    probe = payload["counterfactual_probe"]
    initial_inverse_count = check_probe(
        probe,
        history,
        active_orbits,
        order_limit=DEFAULT_PROBE_ORDER_LIMIT,
        max_iterations=DEFAULT_PROBE_MAX_ITERATIONS,
        conflict_cap=DEFAULT_CONFLICT_CAP,
    )
    expected_comparison = probe_packet_comparison(
        probe["models"],
        active_orbits[:-1],
        active_orbits[-1],
    )
    if payload["counterfactual_seed_packet_coverage"] != expected_comparison:
        raise AssertionError("persistent augmented coverage drifted")

    seeded = payload["seeded_cegar"]
    seeded_audit = check_seeded_cegar(
        seeded,
        history,
        active_orbits,
        initial_inverse_count=initial_inverse_count,
        full_certificate_limit=DEFAULT_FULL_CERTIFICATE_LIMIT,
        max_iterations=DEFAULT_MAX_ITERATIONS,
        conflict_cap=DEFAULT_CONFLICT_CAP,
    )
    decision = route_decision(
        probe,
        expected_comparison,
        seeded,
        full_certificate_limit=DEFAULT_FULL_CERTIFICATE_LIMIT,
    )
    if payload["decision"] != decision:
        raise AssertionError("persistent augmented decision drifted")
    return {
        "status": "OK",
        "verified_blocked_history_orders": len(history),
        "verified_active_seed_certificates": len(active_orbits),
        "verified_inactive_seed_certificates": len(inactive_records),
        "verified_counterfactual_probe_orders": len(probe["models"]),
        "verified_new_exact_full_cone_certificates": seeded_audit[
            "verified_certificates"
        ],
        "verified_exact_affine_certificate_images": seeded_audit[
            "verified_images"
        ],
        "verified_new_unique_affine_orbit_clauses": seeded_audit[
            "verified_learned_clauses"
        ],
        "decision": decision,
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
    parser.add_argument(
        "--full-certificate-limit",
        type=int,
        default=DEFAULT_FULL_CERTIFICATE_LIMIT,
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=DEFAULT_MAX_ITERATIONS,
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
        args.full_certificate_limit,
        args.max_iterations,
        args.conflict_cap,
    )
    if any(value <= 0 for value in limits):
        raise SystemExit("all persistent augmented CEGAR limits must be positive")
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
        comparison = payload["counterfactual_seed_packet_coverage"]
        seeded = payload["seeded_cegar"]
        print(
            f"{PATTERN}: "
            f"history={payload['blocked_history']['order_count']} "
            f"probe_transferred="
            f"{comparison['transferred_only']['covered_probe_order_count']}/"
            f"{payload['counterfactual_probe']['inverse_pair_escape_order_count']} "
            f"probe_width4="
            f"{comparison['selected_width4_only']['covered_probe_order_count']}/"
            f"{payload['counterfactual_probe']['inverse_pair_escape_order_count']} "
            f"new_certificates={seeded['new_full_certificate_count']} "
            f"status={seeded['status']} "
            f"decision={payload['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
