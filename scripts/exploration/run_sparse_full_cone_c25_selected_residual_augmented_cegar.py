#!/usr/bin/env python3
"""Run C25 CEGAR with the selected compressed residual width-three seed.

The source compression packet selects the affine orbit of residual:2 as the
exact one-source minimum cover of all eight active-seed escapes in its
24-order source packet.  This bounded follow-up blocks the complete current
168-order history, activates the three transferred seeds, the persistent
width-four seed, and only that selected residual width-three seed, then tests
fresh-order transfer and learns new exact full-cone certificate orbits.

History blocking and finite limits make this a fixed-pattern search diagnostic
only.  No solver status here is an all-order obstruction, geometric
realizability result, counterexample, or proof of Erdos Problem #97.
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
from compress_sparse_full_cone_c25_persistent_augmented_residuals import (  # noqa: E402
    check_payload as check_compression_payload,
)
from compress_sparse_full_cone_c25_persistent_escapes import (  # noqa: E402
    stable_json_sha256,
)
from compress_sparse_full_cone_certificates import (  # noqa: E402
    order_satisfies_quads,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    dihedral_order_key,
)
from run_sparse_full_cone_c25_persistent_augmented_cegar import (  # noqa: E402
    PATTERN,
    blocked_history as parent_blocked_history,
    check_order_record,
    check_payload as check_parent_payload,
    check_probe,
    collect_history_disjoint_probe,
    coverage_for,
    history_identity,
    load_sources as load_parent_sources,
    run_history_disjoint_seeded_cegar,
    seed_selection as parent_seed_selection,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    FullClause,
    build_clause_orbit,
    clause_matches,
    file_sha256,
    unique_clauses,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_c25_persistent_augmented_residual_compression_2026-07-30"
    / "summary.json"
)
DEFAULT_PROBE_ORDER_LIMIT = 16
DEFAULT_PROBE_MAX_ITERATIONS = 12_000
DEFAULT_FULL_CERTIFICATE_LIMIT = 8
DEFAULT_MAX_ITERATIONS = 12_000
DEFAULT_CONFLICT_CAP = 1_024
DEFAULT_RANDOM_SEED = 20_260_731
SELECTED_RESIDUAL_SOURCE_TARGET_ID = "residual:2"
CERTIFICATE_LIMIT_STATUS = (
    "BOUNDED_C25_SELECTED_RESIDUAL_AUGMENTED_CERTIFICATE_LIMIT_REACHED"
)
CONTINUE_DECISION = (
    "COMPRESS_NEW_C25_SELECTED_RESIDUAL_AUGMENTED_ESCAPES"
)
REVIEW_DECISION = (
    "REVIEW_C25_SELECTED_RESIDUAL_AUGMENTED_CEGAR_BEFORE_CONTINUING"
)


def load_sources(
    source_path: Path,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    """Replay the compression and return its complete parent provenance."""

    source = json.loads(source_path.read_text(encoding="utf-8"))
    check_compression_payload(source)
    parent_path = ROOT / str(source["source_artifact"])
    parent = json.loads(parent_path.read_text(encoding="utf-8"))
    check_parent_payload(parent)
    parent_source_path = ROOT / str(parent["source_compression_artifact"])
    (
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = load_parent_sources(parent_source_path)
    return (
        source,
        parent,
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    )


def blocked_history(
    parent: Mapping[str, Any],
    augmentation: Mapping[str, Any],
    prior_cegar: Mapping[str, Any],
    transfer: Mapping[str, Any],
    first: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Return 144 parent histories plus its 16 probe and 8 residual orders."""

    history = parent_blocked_history(
        augmentation,
        prior_cegar,
        transfer,
        first,
    )
    streams = (
        (
            "persistent_augmented_probe",
            "probe_model_index",
            parent["counterfactual_probe"]["models"],
        ),
        (
            "persistent_augmented_residual",
            "model_index",
            parent["seeded_cegar"]["models"],
        ),
    )
    for packet, index_key, models in streams:
        for model in models:
            model_index = int(model[index_key])
            history.append(
                {
                    "history_id": f"{packet}:{model_index}",
                    "packet": packet,
                    "order": [int(label) for label in model["order"]],
                    "order_sha256": str(model["order_sha256"]),
                    "dihedral_order_sha256": str(
                        model["dihedral_order_sha256"]
                    ),
                }
            )
    keys = {dihedral_order_key(record["order"]) for record in history}
    if len(history) != 168 or len(keys) != len(history):
        raise AssertionError("selected-residual history must have 168 classes")
    return history


def selected_residual_seed_record(
    row: Mapping[str, Any],
    orbit: ClauseOrbit,
) -> dict[str, object]:
    """Return an exact summary of the selected width-three seed."""

    certificate = row["compressed_certificate"]
    checked = check_certificate_dict(certificate)
    if not checked.zero_sum_verified:
        raise AssertionError("selected residual seed failed exact replay")
    if int(row["compressed_unique_ordered_quad_count"]) != 3:
        raise AssertionError("selected residual seed width drifted")
    return {
        "seed_id": "persistent_augmented_residual_compressed:2",
        "seed_role": "EXACT_MINIMUM_ACTIVE_SEED_ESCAPE_COVER",
        "source_target_id": str(row["source_target_id"]),
        "source_model_index": int(row["source_model_index"]),
        "ordered_quad_count": int(row["compressed_unique_ordered_quad_count"]),
        "source_certificate_sha256": str(row["source_certificate_sha256"]),
        "compressed_certificate_sha256": str(
            row["compressed_certificate_sha256"]
        ),
        "positive_inequalities": checked.positive_inequalities,
        "weight_sum": checked.weight_sum,
        "max_weight": checked.max_weight,
        "affine_clause_orbit": orbit.summary(),
    }


def inactive_new_residual_records(
    rows: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    """Summarize the seven compressed residual orbits not selected."""

    return [
        {
            "seed_id": (
                "persistent_augmented_residual_compressed:"
                f"{int(row['source_model_index'])}"
            ),
            "source_target_id": str(row["source_target_id"]),
            "source_model_index": int(row["source_model_index"]),
            "ordered_quad_count": int(
                row["compressed_unique_ordered_quad_count"]
            ),
            "compressed_certificate_sha256": str(
                row["compressed_certificate_sha256"]
            ),
            "canonical_clause_sha256": str(
                row["affine_clause_orbit"]["canonical_clause_sha256"]
            ),
            "inactive_reason": (
                "NOT_SELECTED_BY_EXACT_MINIMUM_RESIDUAL_AFFINE_COVER"
            ),
        }
        for row in rows
        if str(row["source_target_id"]) != SELECTED_RESIDUAL_SOURCE_TARGET_ID
    ]


def seed_selection(
    source: Mapping[str, Any],
    parent_source: Mapping[str, Any],
    residual_compression: Mapping[str, Any],
    transfer: Mapping[str, Any],
) -> tuple[
    list[dict[str, object]],
    dict[str, object],
    dict[str, object],
    list[ClauseOrbit],
    list[dict[str, object]],
]:
    """Return the five active orbits and sixteen inactive summaries."""

    (
        transferred_records,
        parent_orbits,
        persistent_record,
        inherited_inactive,
    ) = parent_seed_selection(
        parent_source,
        residual_compression,
        transfer,
    )
    residual_cover = source["run"]["coverage_comparison"][
        "minimum_affine_source_covers"
    ]["residual_targets"]
    if residual_cover["selected_source_target_ids"] != [
        SELECTED_RESIDUAL_SOURCE_TARGET_ID
    ]:
        raise AssertionError("selected residual minimum cover drifted")
    rows = {
        str(row["source_target_id"]): row
        for row in source["run"]["compressed_models"]
    }
    expected_ids = {f"residual:{index}" for index in range(8)}
    if set(rows) != expected_ids:
        raise AssertionError("selected residual compressed packet drifted")

    selected_row = rows[SELECTED_RESIDUAL_SOURCE_TARGET_ID]
    selected_orbit = build_clause_orbit(
        PATTERN,
        int(selected_row["source_model_index"]),
        selected_row["compressed_certificate"],
    )
    if selected_orbit.summary() != selected_row["affine_clause_orbit"]:
        raise AssertionError("selected residual affine orbit drifted")
    active_orbits = [*parent_orbits, selected_orbit]
    hashes = [orbit.canonical_clause_sha256 for orbit in active_orbits]
    if len(hashes) != len(set(hashes)):
        raise AssertionError("selected residual active seed orbit duplicated")

    selected_record = selected_residual_seed_record(
        selected_row,
        selected_orbit,
    )
    inactive_new = inactive_new_residual_records(list(rows.values()))
    if len(inherited_inactive) != 9 or len(inactive_new) != 7:
        raise AssertionError("selected residual inactive packet drifted")
    return (
        transferred_records,
        persistent_record,
        selected_record,
        active_orbits,
        [*inherited_inactive, *inactive_new],
    )


def probe_packet_comparison(
    models: Sequence[Mapping[str, Any]],
    parent_orbits: Sequence[ClauseOrbit],
    selected_orbit: ClauseOrbit,
) -> dict[str, object]:
    """Compare the four parent seeds with the selected residual orbit."""

    active_orbits = [*parent_orbits, selected_orbit]
    parent = coverage_for(models, parent_orbits)
    selected = coverage_for(models, [selected_orbit])
    active = coverage_for(models, active_orbits)
    model_indices = {int(model["probe_model_index"]) for model in models}
    parent_covered = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], parent_orbits)
    }
    selected_covered = {
        int(model["probe_model_index"])
        for model in models
        if clause_matches(model["order"], [selected_orbit])
    }
    return {
        "parent_four_seeds": parent,
        "selected_width3_only": selected,
        "parent_plus_selected_width3": active,
        "parent_covered_probe_model_indices": sorted(parent_covered),
        "selected_width3_covered_probe_model_indices": sorted(
            selected_covered
        ),
        "selected_width3_marginal_over_parent_probe_model_indices": sorted(
            selected_covered - parent_covered
        ),
        "selected_width3_overlap_with_parent_probe_model_indices": sorted(
            selected_covered & parent_covered
        ),
        "parent_uncovered_probe_model_indices": sorted(
            model_indices - parent_covered
        ),
        "active_uncovered_probe_model_indices": sorted(
            model_indices - (parent_covered | selected_covered)
        ),
    }


def route_decision(
    probe: Mapping[str, Any],
    comparison: Mapping[str, Any],
    seeded: Mapping[str, Any],
    *,
    full_certificate_limit: int,
) -> str:
    """Return the predeclared finite-packet continuation decision."""

    probe_count = int(probe["inverse_pair_escape_order_count"])
    parent_covered = int(
        comparison["parent_four_seeds"]["covered_probe_order_count"]
    )
    selected_covered = int(
        comparison["selected_width3_only"]["covered_probe_order_count"]
    )
    active_covered = int(
        comparison["parent_plus_selected_width3"]["covered_probe_order_count"]
    )
    marginal = comparison[
        "selected_width3_marginal_over_parent_probe_model_indices"
    ]
    certificates = int(seeded["new_full_certificate_count"])
    unresolved = sum(
        "certificate" not in model["full_kalmanson"]
        for model in seeded["models"]
    )
    if (
        probe_count > 0
        and parent_covered == probe_count
        and 0 < selected_covered < probe_count
        and active_covered == probe_count
        and not marginal
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
        parent,
        parent_source,
        augmentation,
        residual_compression,
        prior_cegar,
        transfer,
        first,
    ) = load_sources(source_path)
    history = blocked_history(
        parent,
        augmentation,
        prior_cegar,
        transfer,
        first,
    )
    (
        transferred_records,
        persistent_record,
        selected_record,
        active_orbits,
        inactive_records,
    ) = seed_selection(
        source,
        parent_source,
        residual_compression,
        transfer,
    )
    parent_orbits = active_orbits[:-1]
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
        parent_orbits,
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
        "type": "sparse_full_cone_c25_selected_residual_augmented_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_168_HISTORY_C25_CEGAR",
        "status": "BOUNDED_C25_SELECTED_RESIDUAL_WIDTH3_AUGMENTED_CEGAR",
        "claim_scope": (
            "Three transferred exact C25 certificate orbits, one persistent "
            "width-four seed, and the selected exact residual width-three "
            "orbit seed a bounded order CEGAR after 168 known C25 orders are "
            "blocked under rotation and reversal. Probe coverage, newly "
            "learned certificates, and affine images are exact, but finite "
            "limits and history blocking preclude any all-order obstruction, "
            "geometric realizability result, counterexample, proof of Erdos "
            "Problem #97, or official/global status update."
        ),
        "source_residual_compression_artifact": (
            source_path.relative_to(ROOT).as_posix()
        ),
        "source_residual_compression_sha256": file_sha256(source_path),
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
                "three transferred orbits plus persistent width-four orbit "
                "plus exact minimum residual-cover width-three orbit only"
            ),
            "inactive_seed_policy": (
                "nine inherited inactive orbits plus seven nonselected "
                "persistent-augmented compressed residual orbits"
            ),
        },
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": list(offsets),
        "transferred_seed_templates": transferred_records,
        "selected_persistent_seed_template": persistent_record,
        "selected_residual_seed_template": selected_record,
        "inactive_seed_templates": inactive_records,
        "active_seed_orbit_count": len(active_orbits),
        "active_exact_affine_seed_image_count": sum(
            orbit.affine_map_count for orbit in active_orbits
        ),
        "distinct_active_seed_orbit_class_count": len(
            {orbit.canonical_clause_sha256 for orbit in active_orbits}
        ),
        "unique_active_seed_orbit_clause_count": len(
            unique_clauses(active_orbits)
        ),
        "blocked_history": {
            "order_count": len(history),
            "dihedral_order_count": len(
                {dihedral_order_key(record["order"]) for record in history}
            ),
            "packet_histogram": dict(
                sorted(
                    Counter(
                        str(record["packet"]) for record in history
                    ).items()
                )
            ),
            "identities": history_identity(history),
        },
        "counterfactual_probe": probe,
        "counterfactual_seed_packet_coverage": comparison,
        "seeded_cegar": seeded,
        "decision": decision,
        "next_target": (
            "Compress the eight newly learned exact C25 certificates, build "
            "their quotient-preserving affine orbits, and compare marginal "
            "coverage against the four parent seeds and the selected width-"
            "three orbit before choosing a 192-history CEGAR seed packet."
        ),
    }


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
    """Replay the bounded learned certificate packet exactly."""

    n, offsets = PATTERNS[PATTERN]
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    if int(seeded["blocked_history_dihedral_order_count"]) != len(history_keys):
        raise AssertionError("selected residual seeded history drifted")
    if int(seeded["active_unique_seed_orbit_clause_count"]) != len(
        unique_clauses(active_orbits)
    ):
        raise AssertionError("selected residual active clauses drifted")
    iterations = int(seeded["iterations"])
    if not 1 <= iterations <= max_iterations:
        raise AssertionError("selected residual seeded iterations drifted")
    if int(seeded["initial_probe_inverse_clause_count"]) != initial_inverse_count:
        raise AssertionError("selected residual initial clauses drifted")
    final_inverse_count = int(seeded["final_inverse_pair_clause_count"])
    if not initial_inverse_count <= final_inverse_count <= (
        initial_inverse_count + iterations * conflict_cap
    ):
        raise AssertionError("selected residual final clauses drifted")

    learned_clauses: set[FullClause] = set()
    seen = set(history_keys)
    verified_certificates = 0
    verified_images = sum(orbit.affine_map_count for orbit in active_orbits)
    previous_iteration = 0
    previous_clause_count = initial_inverse_count
    models = seeded["models"]
    for expected_index, model in enumerate(models):
        if int(model["model_index"]) != expected_index:
            raise AssertionError("selected residual model index drifted")
        iteration = int(model["z3_iteration"])
        if not previous_iteration < iteration <= iterations:
            raise AssertionError("selected residual model provenance drifted")
        previous_iteration = iteration
        discovery_count = int(model["inverse_clause_count_at_discovery"])
        if not previous_clause_count <= discovery_count <= final_inverse_count:
            raise AssertionError("selected residual clause provenance drifted")
        previous_clause_count = discovery_count
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("selected residual model is not disjoint")
        seen.add(key)
        expected_matches = clause_matches(order, active_orbits)
        if model["seed_orbit_matches"] != expected_matches or expected_matches:
            raise AssertionError("selected residual active seed match drifted")
        prior_matches = sum(
            order_satisfies_quads(order, clause) for clause in learned_clauses
        )
        if int(model["prior_learned_orbit_clause_matches"]) != prior_matches:
            raise AssertionError("selected residual learned match drifted")
        if prior_matches:
            raise AssertionError("selected residual prior clause admitted model")

        full = model["full_kalmanson"]
        certificate = full.get("certificate")
        if certificate is None:
            raise AssertionError("selected residual stored unresolved model")
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("selected residual certificate failed")
        for field, value in {
            "status": checked.status,
            "positive_inequalities": checked.positive_inequalities,
            "weight_sum": checked.weight_sum,
            "max_weight": checked.max_weight,
            "zero_sum_verified": checked.zero_sum_verified,
        }.items():
            if full[field] != value:
                raise AssertionError(
                    f"selected residual certificate {field} drifted"
                )
        if stable_json_sha256(certificate) != full["certificate_sha256"]:
            raise AssertionError("selected residual certificate hash drifted")
        quads = certificate_order_quads(certificate, order)
        if len(quads) != int(full["unique_ordered_quad_count"]):
            raise AssertionError("selected residual certificate width drifted")
        orbit = build_clause_orbit(PATTERN, expected_index, certificate)
        if orbit.summary() != full["affine_clause_orbit"]:
            raise AssertionError("selected residual learned orbit drifted")
        new_clauses = [
            clause for clause in orbit.clauses if clause not in learned_clauses
        ]
        if len(new_clauses) != int(
            full["new_unique_affine_orbit_clauses_added"]
        ):
            raise AssertionError("selected residual learned clauses drifted")
        learned_clauses.update(new_clauses)
        verified_certificates += 1
        verified_images += orbit.affine_map_count

    if verified_certificates != full_certificate_limit:
        raise AssertionError("selected residual certificate limit drifted")
    if int(seeded["new_full_certificate_count"]) != verified_certificates:
        raise AssertionError("selected residual certificate count drifted")
    if int(seeded["new_unique_affine_orbit_clause_count"]) != len(
        learned_clauses
    ):
        raise AssertionError("selected residual learned clause total drifted")
    if seeded["status"] != CERTIFICATE_LIMIT_STATUS:
        raise AssertionError("selected residual terminal status drifted")
    if seeded["solver_result"] != "bounded_after_new_exact_certificates":
        raise AssertionError("selected residual terminal result drifted")
    if iterations != previous_iteration:
        raise AssertionError("selected residual terminal iteration drifted")
    return {
        "verified_certificates": verified_certificates,
        "verified_images": verified_images,
        "verified_learned_clauses": len(learned_clauses),
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    expected_type = (
        "sparse_full_cone_c25_selected_residual_augmented_cegar_v1"
    )
    if payload["type"] != expected_type:
        raise AssertionError("selected residual artifact type drifted")
    source_path = ROOT / str(payload["source_residual_compression_artifact"])
    if source_path.resolve() != DEFAULT_SOURCE.resolve():
        raise AssertionError("selected residual source artifact drifted")
    if file_sha256(source_path) != str(
        payload["source_residual_compression_sha256"]
    ):
        raise AssertionError("selected residual source hash drifted")
    (
        source,
        parent,
        parent_source,
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
            "three transferred orbits plus persistent width-four orbit "
            "plus exact minimum residual-cover width-three orbit only"
        ),
        "inactive_seed_policy": (
            "nine inherited inactive orbits plus seven nonselected "
            "persistent-augmented compressed residual orbits"
        ),
    }
    if configuration != expected_configuration:
        raise AssertionError("selected residual configuration drifted")
    n, offsets = PATTERNS[PATTERN]
    if payload["pattern"] != PATTERN or int(payload["n"]) != n:
        raise AssertionError("selected residual pattern drifted")
    if payload["circulant_offsets"] != list(offsets):
        raise AssertionError("selected residual offsets drifted")

    history = blocked_history(
        parent,
        augmentation,
        prior_cegar,
        transfer,
        first,
    )
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
        raise AssertionError("selected residual history drifted")

    (
        transferred_records,
        persistent_record,
        selected_record,
        active_orbits,
        inactive_records,
    ) = seed_selection(
        source,
        parent_source,
        residual_compression,
        transfer,
    )
    if payload["transferred_seed_templates"] != transferred_records:
        raise AssertionError("selected residual transferred seeds drifted")
    if payload["selected_persistent_seed_template"] != persistent_record:
        raise AssertionError("selected residual persistent seed drifted")
    if payload["selected_residual_seed_template"] != selected_record:
        raise AssertionError("selected residual selected seed drifted")
    if payload["inactive_seed_templates"] != inactive_records:
        raise AssertionError("selected residual inactive seeds drifted")
    if int(payload["active_seed_orbit_count"]) != len(active_orbits):
        raise AssertionError("selected residual active count drifted")
    if int(payload["active_exact_affine_seed_image_count"]) != sum(
        orbit.affine_map_count for orbit in active_orbits
    ):
        raise AssertionError("selected residual seed images drifted")
    if int(payload["distinct_active_seed_orbit_class_count"]) != len(
        {orbit.canonical_clause_sha256 for orbit in active_orbits}
    ):
        raise AssertionError("selected residual seed classes drifted")
    if int(payload["unique_active_seed_orbit_clause_count"]) != len(
        unique_clauses(active_orbits)
    ):
        raise AssertionError("selected residual seed clauses drifted")

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
        raise AssertionError("selected residual coverage drifted")

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
        raise AssertionError("selected residual decision drifted")
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
        raise SystemExit("all selected residual CEGAR limits must be positive")
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
        probe_count = payload["counterfactual_probe"][
            "inverse_pair_escape_order_count"
        ]
        print(
            f"{PATTERN}: "
            f"history={payload['blocked_history']['order_count']} "
            f"probe_parent="
            f"{comparison['parent_four_seeds']['covered_probe_order_count']}/"
            f"{probe_count} "
            f"probe_width3="
            f"{comparison['selected_width3_only']['covered_probe_order_count']}/"
            f"{probe_count} "
            f"width3_marginal="
            f"{len(comparison['selected_width3_marginal_over_parent_probe_model_indices'])} "
            f"new_certificates={seeded['new_full_certificate_count']} "
            f"status={seeded['status']} "
            f"decision={payload['decision']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
