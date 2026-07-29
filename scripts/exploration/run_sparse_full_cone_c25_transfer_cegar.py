#!/usr/bin/env python3
"""Run a history-disjoint C25 CEGAR seeded by transferred exact clauses.

The source transfer audit identifies C25 circuits of widths three and five
that recur in both prior and second-stream packets, plus a width-fourteen
secondary clause that transfers to the prior packet.  This bounded follow-up
activates all quotient-preserving affine images of those exact certificates,
excludes every known C25 order from the prior, first-fresh, and second-fresh
packets under rotation and reversal, and learns new exact full-cone
certificate orbits from seed-escaping orders.

C29 is deliberately out of scope because its transfer audit triggered the
packet-specific stopping rule.  History blocking and finite limits make this
a search diagnostic only.  No solver status here is an all-order obstruction,
geometric realizability result, counterexample, or proof of Erdos Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from z3 import sat, unsat
except ImportError as exc:  # pragma: no cover - optional development dependency
    sat = unsat = None  # type: ignore[assignment]
    Z3_IMPORT_ERROR: ImportError | None = exc
else:
    Z3_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import check_certificate_dict  # noqa: E402
from check_kalmanson_two_order_search import _prepare_vector_tables  # noqa: E402
from check_kalmanson_two_order_z3 import (  # noqa: E402
    _add_clause,
    _clause_key,
    _collect_conflicts,
    _make_solver,
    _order_from_model,
)
from compress_sparse_full_cone_certificates import (  # noqa: E402
    order_satisfies_quads,
)
from find_kalmanson_certificate import find_certificate  # noqa: E402
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    add_full_certificate_clause,
    certificate_order_quads,
    inverse_pair_audit,
    lightweight_summary,
)
from probe_sparse_full_cone_small_templates import (  # noqa: E402
    block_dihedral_order,
    dihedral_order_key,
    order_record_hashes,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    FullClause,
    InverseClause,
    build_clause_orbit,
    clause_matches,
    file_sha256,
    probe_coverage_summary,
    unique_clauses,
)


PATTERN = "C25_sidon_2_5_9_14"
DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_fresh_template_transfer_2026-08-02"
    / "summary.json"
)


def require_z3() -> None:
    if Z3_IMPORT_ERROR is not None:
        raise RuntimeError("z3-solver is required for the C25 CEGAR") from (
            Z3_IMPORT_ERROR
        )


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def source_run(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    runs = [run for run in payload["runs"] if str(run["pattern"]) == PATTERN]
    if len(runs) != 1:
        raise AssertionError("transfer source must contain exactly one C25 run")
    run = runs[0]
    if run["transfer_decision"]["decision"] != "CONTINUE_EXACT_TEMPLATE_TRANSFER":
        raise AssertionError("C25 transfer source is not marked for continuation")
    c29_runs = [
        run for run in payload["runs"] if str(run["pattern"]) == "C29_sidon_1_3_7_15"
    ]
    if (
        len(c29_runs) != 1
        or c29_runs[0]["transfer_decision"]["decision"]
        != "STOP_PACKET_SPECIFIC_TEMPLATE_MINING"
    ):
        raise AssertionError("C29 stopping decision drifted")
    return run


def c25_seed_packet(
    payload: Mapping[str, Any],
) -> tuple[list[dict[str, object]], list[ClauseOrbit]]:
    """Return the transferred C25 seeds with primary/secondary roles."""

    records = []
    orbits = []
    for template in source_run(payload)["canonical_transfer_templates"]:
        width = int(template["ordered_quad_count"])
        if width in (3, 5):
            role = "PRIMARY_CROSS_STREAM_TRANSFER"
        elif width == 14:
            role = "SECONDARY_PRIOR_PACKET_TRANSFER"
        else:
            raise AssertionError(f"unexpected C25 transfer-template width: {width}")
        certificate = template["canonical_certificate"]
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("C25 seed certificate failed exact replay")
        source_model_index = int(template["source_model_index"])
        orbit = build_clause_orbit(PATTERN, source_model_index, certificate)
        source_orbit = template["affine_clause_orbit"]
        if (
            orbit.canonical_clause_sha256 != str(template["canonical_clause_sha256"])
            or orbit.affine_map_count != int(source_orbit["affine_map_count"])
            or len(orbit.clauses) != int(source_orbit["unique_orbit_clause_count"])
        ):
            raise AssertionError("C25 transfer seed orbit drifted")
        records.append(
            {
                "template_id": str(template["template_id"]),
                "seed_role": role,
                "source_target_id": str(template["source_target_id"]),
                "source_model_index": source_model_index,
                "ordered_quad_count": width,
                "canonical_clause_sha256": str(template["canonical_clause_sha256"]),
                "canonical_certificate_sha256": stable_json_sha256(certificate),
                "positive_inequalities": checked.positive_inequalities,
                "weight_sum": checked.weight_sum,
                "max_weight": checked.max_weight,
                "affine_clause_orbit": orbit.summary(),
            }
        )
        orbits.append(orbit)
    order = sorted(
        range(len(records)), key=lambda index: int(records[index]["ordered_quad_count"])
    )
    return [records[index] for index in order], [orbits[index] for index in order]


def first_fresh_stream_path(payload: Mapping[str, Any]) -> Path:
    path = ROOT / str(payload["first_fresh_stream_artifact"])
    if file_sha256(path) != str(payload["first_fresh_stream_sha256"]):
        raise AssertionError("first fresh stream hash drifted through transfer source")
    return path


def c25_history(
    payload: Mapping[str, Any],
    first_payload: Mapping[str, Any],
) -> list[dict[str, object]]:
    """Return 88 known C25 orders with exact dihedral identities."""

    run = source_run(payload)
    first_runs = [
        item for item in first_payload["runs"] if str(item["pattern"]) == PATTERN
    ]
    if len(first_runs) != 1:
        raise AssertionError("first fresh source must contain one C25 run")
    packets: list[tuple[str, str, Sequence[int]]] = []
    for record in run["prior_packet"]["records"]:
        packets.append(
            (
                "prior",
                str(record["packet_order_id"]),
                record["order"],
            )
        )
    for model in first_runs[0]["fresh_stream"]["models"]:
        packets.append(
            (
                "first_fresh",
                f"fresh:{int(model['fresh_model_index'])}",
                model["order"],
            )
        )
    for model in run["second_fresh_stream"]["models"]:
        packets.append(
            (
                "second_fresh",
                f"fresh:{int(model['fresh_model_index'])}",
                model["order"],
            )
        )

    history = []
    seen = set()
    for packet, order_id, raw_order in packets:
        order = [int(label) for label in raw_order]
        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("C25 blocked history has a dihedral duplicate")
        seen.add(key)
        history.append(
            {
                "history_id": f"{packet}:{order_id}",
                "packet": packet,
                "order": order,
                **order_record_hashes(order),
            }
        )
    return history


def history_identity(
    history: Sequence[Mapping[str, Any]],
) -> list[dict[str, object]]:
    return [
        {
            "history_id": str(record["history_id"]),
            "packet": str(record["packet"]),
            "order_sha256": str(record["order_sha256"]),
            "dihedral_order_sha256": str(record["dihedral_order_sha256"]),
        }
        for record in history
    ]


def collect_history_disjoint_probe(
    seed_orbits: Sequence[ClauseOrbit],
    history: Sequence[Mapping[str, Any]],
    *,
    order_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> tuple[dict[str, object], set[InverseClause]]:
    require_z3()
    n, offsets = PATTERNS[PATTERN]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    for record in history:
        block_dihedral_order(solver, positions, record["order"])

    inverse_clauses: set[InverseClause] = set()
    seen = set(history_keys)
    models = []
    status = "BOUNDED_HISTORY_DISJOINT_PROBE_ITERATION_LIMIT"
    solver_result = "iteration_limit"
    iterations = 0
    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            status = "HISTORY_DISJOINT_PROBE_SOLVER_UNSAT"
            solver_result = "unsat"
            break
        if result != sat:
            status = "UNKNOWN_HISTORY_DISJOINT_PROBE_SMT_RESULT"
            solver_result = str(result)
            break
        order = _order_from_model(solver.model(), positions, n)
        conflicts = _collect_conflicts(order, quad_ids, inverse_id, conflict_cap)
        if conflicts:
            for conflict in conflicts:
                clause = _clause_key(conflict.left_quad, conflict.right_quad)
                if clause not in inverse_clauses:
                    inverse_clauses.add(clause)
                    _add_clause(solver, positions, clause)
            continue

        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("probe admitted a blocked or repeated order")
        audit = inverse_pair_audit(PATTERN, n, offsets, order)
        if audit["inverse_pair_conflicts"] != 0:
            raise AssertionError("probe order did not escape inverse pairs")
        models.append(
            {
                "probe_model_index": len(models),
                "z3_iteration": iteration,
                "order": order,
                **order_record_hashes(order),
                "lightweight_filters": lightweight_summary(PATTERN, order),
                "inverse_pair_audit": audit,
                "seed_orbit_matches": clause_matches(order, seed_orbits),
            }
        )
        seen.add(key)
        block_dihedral_order(solver, positions, order)
        if len(models) >= order_limit:
            status = "BOUNDED_HISTORY_DISJOINT_PROBE_ORDER_LIMIT_REACHED"
            solver_result = "bounded_after_inverse_pair_escape_models"
            break

    return (
        {
            "status": status,
            "solver_result": solver_result,
            "iterations": iterations,
            "blocked_history_dihedral_order_count": len(history_keys),
            "inverse_pair_clause_count": len(inverse_clauses),
            "inverse_pair_escape_order_count": len(models),
            "models": models,
        },
        inverse_clauses,
    )


def run_history_disjoint_seeded_cegar(
    seed_orbits: Sequence[ClauseOrbit],
    history: Sequence[Mapping[str, Any]],
    initial_inverse_clauses: set[InverseClause],
    *,
    full_certificate_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> dict[str, object]:
    require_z3()
    n, offsets = PATTERNS[PATTERN]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    history_keys = {dihedral_order_key(record["order"]) for record in history}
    for record in history:
        block_dihedral_order(solver, positions, record["order"])

    inverse_clauses = set(initial_inverse_clauses)
    for clause in sorted(inverse_clauses):
        _add_clause(solver, positions, clause)
    seed_clauses = unique_clauses(seed_orbits)
    for clause in seed_clauses:
        add_full_certificate_clause(solver, positions, clause)

    learned_orbits: list[ClauseOrbit] = []
    active_learned_clauses: set[FullClause] = set()
    seen = set(history_keys)
    models = []
    status = "BOUNDED_HISTORY_DISJOINT_SEEDED_CEGAR_ITERATION_LIMIT"
    solver_result = "iteration_limit"
    iterations = 0
    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            status = "REVIEW_PENDING_BOUNDED_HISTORY_DISJOINT_SOLVER_UNSAT"
            solver_result = "unsat"
            break
        if result != sat:
            status = "UNKNOWN_HISTORY_DISJOINT_SEEDED_SMT_RESULT"
            solver_result = str(result)
            break

        order = _order_from_model(solver.model(), positions, n)
        conflicts = _collect_conflicts(order, quad_ids, inverse_id, conflict_cap)
        if conflicts:
            for conflict in conflicts:
                clause = _clause_key(conflict.left_quad, conflict.right_quad)
                if clause not in inverse_clauses:
                    inverse_clauses.add(clause)
                    _add_clause(solver, positions, clause)
            continue

        key = dihedral_order_key(order)
        if key in seen:
            raise AssertionError("seeded CEGAR admitted blocked or repeated order")
        if clause_matches(order, seed_orbits):
            raise AssertionError("active transferred seed admitted a matching order")
        if any(
            order_satisfies_quads(order, clause) for clause in active_learned_clauses
        ):
            raise AssertionError("active learned clause admitted a matching order")
        audit = inverse_pair_audit(PATTERN, n, offsets, order)
        if audit["inverse_pair_conflicts"] != 0:
            raise AssertionError("seeded CEGAR order did not escape inverse pairs")

        certificate = find_certificate(PATTERN, n, offsets, order, 1.0e-9)
        common = {
            "model_index": len(models),
            "z3_iteration": iteration,
            "inverse_clause_count_at_discovery": len(inverse_clauses),
            "order": order,
            **order_record_hashes(order),
            "lightweight_filters": lightweight_summary(PATTERN, order),
            "inverse_pair_audit": audit,
            "seed_orbit_matches": [],
            "prior_learned_orbit_clause_matches": 0,
        }
        if certificate is None:
            models.append(
                {
                    **common,
                    "full_kalmanson": {
                        "status": "NO_EXACT_FIXED_ORDER_CERTIFICATE_FOUND"
                    },
                }
            )
            status = "NO_EXACT_FULL_CONE_CERTIFICATE_FOUND_FOR_C25_MODEL"
            solver_result = "sat"
            break

        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("learned C25 certificate failed exact replay")
        quads = certificate_order_quads(certificate, order)
        orbit = build_clause_orbit(PATTERN, len(models), certificate)
        new_clauses = [
            clause for clause in orbit.clauses if clause not in active_learned_clauses
        ]
        for clause in new_clauses:
            add_full_certificate_clause(solver, positions, clause)
            active_learned_clauses.add(clause)
        models.append(
            {
                **common,
                "full_kalmanson": {
                    "status": checked.status,
                    "positive_inequalities": checked.positive_inequalities,
                    "unique_ordered_quad_count": len(quads),
                    "weight_sum": checked.weight_sum,
                    "max_weight": checked.max_weight,
                    "zero_sum_verified": checked.zero_sum_verified,
                    "certificate_sha256": stable_json_sha256(certificate),
                    "affine_clause_orbit": orbit.summary(),
                    "new_unique_affine_orbit_clauses_added": len(new_clauses),
                    "certificate": certificate,
                },
            }
        )
        learned_orbits.append(orbit)
        seen.add(key)
        block_dihedral_order(solver, positions, order)
        if len(learned_orbits) >= full_certificate_limit:
            status = "BOUNDED_C25_TRANSFER_SEEDED_CERTIFICATE_LIMIT_REACHED"
            solver_result = "bounded_after_new_exact_certificates"
            break

    return {
        "status": status,
        "solver_result": solver_result,
        "iterations": iterations,
        "blocked_history_dihedral_order_count": len(history_keys),
        "initial_probe_inverse_clause_count": len(initial_inverse_clauses),
        "final_inverse_pair_clause_count": len(inverse_clauses),
        "active_unique_seed_orbit_clause_count": len(seed_clauses),
        "new_full_certificate_count": len(learned_orbits),
        "new_unique_affine_orbit_clause_count": len(active_learned_clauses),
        "models": models,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    first_path = first_fresh_stream_path(source)
    first = json.loads(first_path.read_text(encoding="utf-8"))
    seed_records, seed_orbits = c25_seed_packet(source)
    history = c25_history(source, first)
    probe, inverse_clauses = collect_history_disjoint_probe(
        seed_orbits,
        history,
        order_limit=args.probe_order_limit,
        max_iterations=args.probe_max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
    )
    probe_coverage = probe_coverage_summary(probe["models"], seed_orbits)
    seeded = run_history_disjoint_seeded_cegar(
        seed_orbits,
        history,
        inverse_clauses,
        full_certificate_limit=args.full_certificate_limit,
        max_iterations=args.max_iterations,
        conflict_cap=args.conflict_cap,
        random_seed=args.random_seed,
    )
    n, offsets = PATTERNS[PATTERN]
    return {
        "type": "sparse_full_cone_c25_transferred_seed_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_HISTORY_DISJOINT_C25_CEGAR",
        "status": "BOUNDED_C25_TRANSFER_CLAUSE_SEARCH_DIAGNOSTIC",
        "claim_scope": (
            "Exact transferred C25 certificate orbits seed a bounded order "
            "CEGAR search after 88 known C25 orders are blocked under rotation "
            "and reversal. Newly learned certificates and affine images are "
            "exact, but finite limits and history blocking preclude any "
            "all-order obstruction, geometric realizability result, "
            "counterexample, proof of Erdos Problem #97, or official/global "
            "status update."
        ),
        "source_transfer_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_transfer_sha256": file_sha256(source_path),
        "first_fresh_stream_artifact": first_path.relative_to(ROOT).as_posix(),
        "first_fresh_stream_sha256": file_sha256(first_path),
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
            "primary_seed_widths": [3, 5],
            "secondary_seed_widths": [14],
        },
        "pattern": PATTERN,
        "n": n,
        "circulant_offsets": offsets,
        "seed_templates": seed_records,
        "distinct_seed_orbit_class_count": len(
            {orbit.canonical_clause_sha256 for orbit in seed_orbits}
        ),
        "unique_seed_orbit_clause_count": len(unique_clauses(seed_orbits)),
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
        "counterfactual_seed_coverage": probe_coverage,
        "seeded_cegar": seeded,
    }


def check_order_record(
    record: Mapping[str, Any],
    *,
    n: int,
    offsets: Sequence[int],
) -> list[int]:
    order = [int(label) for label in record["order"]]
    if sorted(order) != list(range(n)) or order[0] != 0:
        raise AssertionError("invalid anchored C25 order")
    for field, value in order_record_hashes(order).items():
        if record[field] != value:
            raise AssertionError(f"C25 {field} drifted")
    audit = inverse_pair_audit(PATTERN, n, offsets, order)
    if audit["inverse_pair_conflicts"] != 0:
        raise AssertionError("C25 order has an inverse-pair conflict")
    if record["inverse_pair_audit"] != audit:
        raise AssertionError("C25 inverse-pair audit drifted")
    if record["lightweight_filters"] != lightweight_summary(PATTERN, order):
        raise AssertionError("C25 lightweight filters drifted")
    return order


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_c25_transferred_seed_cegar_v1":
        raise AssertionError("C25 transferred-seed artifact type drifted")
    source_path = ROOT / str(payload["source_transfer_artifact"])
    first_path = ROOT / str(payload["first_fresh_stream_artifact"])
    if file_sha256(source_path) != str(payload["source_transfer_sha256"]):
        raise AssertionError("C25 transfer source hash drifted")
    if file_sha256(first_path) != str(payload["first_fresh_stream_sha256"]):
        raise AssertionError("C25 first fresh stream hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    first = json.loads(first_path.read_text(encoding="utf-8"))
    expected_seed_records, seed_orbits = c25_seed_packet(source)
    if payload["seed_templates"] != expected_seed_records:
        raise AssertionError("C25 transferred seed packet drifted")
    if int(payload["distinct_seed_orbit_class_count"]) != len(
        {orbit.canonical_clause_sha256 for orbit in seed_orbits}
    ):
        raise AssertionError("C25 distinct seed orbit count drifted")
    if int(payload["unique_seed_orbit_clause_count"]) != len(
        unique_clauses(seed_orbits)
    ):
        raise AssertionError("C25 unique seed clause count drifted")

    history = c25_history(source, first)
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
        raise AssertionError("C25 blocked history drifted")
    for section in ("counterfactual_probe", "seeded_cegar"):
        if int(payload[section]["blocked_history_dihedral_order_count"]) != len(
            history_keys
        ):
            raise AssertionError(f"C25 {section} history count drifted")

    n, offsets = PATTERNS[PATTERN]
    verified_probe_orders = 0
    seen_probe = set(history_keys)
    probe_models = payload["counterfactual_probe"]["models"]
    for model in probe_models:
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen_probe:
            raise AssertionError("C25 probe is not history-disjoint")
        seen_probe.add(key)
        if model["seed_orbit_matches"] != clause_matches(order, seed_orbits):
            raise AssertionError("C25 probe seed matches drifted")
        verified_probe_orders += 1
    if int(payload["counterfactual_probe"]["inverse_pair_escape_order_count"]) != len(
        probe_models
    ):
        raise AssertionError("C25 probe order count drifted")
    if payload["counterfactual_seed_coverage"] != probe_coverage_summary(
        probe_models, seed_orbits
    ):
        raise AssertionError("C25 probe coverage drifted")

    seeded = payload["seeded_cegar"]
    if int(seeded["active_unique_seed_orbit_clause_count"]) != len(
        unique_clauses(seed_orbits)
    ):
        raise AssertionError("C25 active seed clause count drifted")
    learned_clauses: set[FullClause] = set()
    seen_seeded = set(history_keys)
    verified_certificates = 0
    verified_images = sum(orbit.affine_map_count for orbit in seed_orbits)
    for model in payload["seeded_cegar"]["models"]:
        order = check_order_record(model, n=n, offsets=offsets)
        key = dihedral_order_key(order)
        if key in seen_seeded:
            raise AssertionError("C25 seeded order is not history-disjoint")
        seen_seeded.add(key)
        if clause_matches(order, seed_orbits):
            raise AssertionError("C25 seeded order matches a transferred seed")
        if any(order_satisfies_quads(order, clause) for clause in learned_clauses):
            raise AssertionError("C25 seeded order matches a prior learned clause")
        full = model["full_kalmanson"]
        certificate = full.get("certificate")
        if certificate is None:
            continue
        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("C25 learned certificate failed exact replay")
        if stable_json_sha256(certificate) != full["certificate_sha256"]:
            raise AssertionError("C25 learned certificate hash drifted")
        quads = certificate_order_quads(certificate, order)
        if len(quads) != int(full["unique_ordered_quad_count"]):
            raise AssertionError("C25 learned certificate width drifted")
        orbit = build_clause_orbit(
            PATTERN,
            int(model["model_index"]),
            certificate,
        )
        if orbit.summary() != full["affine_clause_orbit"]:
            raise AssertionError("C25 learned affine orbit drifted")
        new_clauses = [
            clause for clause in orbit.clauses if clause not in learned_clauses
        ]
        if len(new_clauses) != int(full["new_unique_affine_orbit_clauses_added"]):
            raise AssertionError("C25 learned affine clause count drifted")
        learned_clauses.update(new_clauses)
        verified_certificates += 1
        verified_images += orbit.affine_map_count
    if int(seeded["new_full_certificate_count"]) != verified_certificates:
        raise AssertionError("C25 learned certificate count drifted")
    if int(seeded["new_unique_affine_orbit_clause_count"]) != len(learned_clauses):
        raise AssertionError("C25 final learned clause count drifted")

    return {
        "status": "OK",
        "verified_blocked_history_orders": len(history),
        "verified_transferred_seed_certificates": len(seed_orbits),
        "verified_counterfactual_probe_orders": verified_probe_orders,
        "verified_new_exact_full_cone_certificates": verified_certificates,
        "verified_exact_affine_certificate_images": verified_images,
        "seeded_cegar_status": str(seeded["status"]),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--probe-order-limit", type=int, default=16)
    parser.add_argument("--probe-max-iterations", type=int, default=8000)
    parser.add_argument("--full-certificate-limit", type=int, default=8)
    parser.add_argument("--max-iterations", type=int, default=8000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=20260803)
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
        raise SystemExit("all C25 CEGAR limits and conflict cap must be positive")
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
        probe = payload["counterfactual_seed_coverage"]
        seeded = payload["seeded_cegar"]
        print(
            f"{PATTERN}: "
            f"history={payload['blocked_history']['order_count']} "
            f"probe_covered={probe['covered_probe_order_count']}/"
            f"{probe['probe_order_count']} "
            f"seed_clauses={payload['unique_seed_orbit_clause_count']} "
            f"new_certificates={seeded['new_full_certificate_count']} "
            f"status={seeded['status']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
