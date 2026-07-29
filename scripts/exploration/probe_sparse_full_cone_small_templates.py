#!/usr/bin/env python3
"""Probe canonical small full-cone templates on fresh C25/C29 order streams.

The source compression packet contains seven exact positive circuits with
three to eight ordered quadrilaterals.  This script chooses one explicit
canonical certificate from each quotient-preserving affine orbit, then
collects deterministic inverse-pair-escape orders that are dihedrally distinct
from all forty-eight source orders.  Template coverage and lightweight filter
status are recomputed exactly for every retained order.

The stream is fresh and history-disjoint, not statistically independent.
Results are bounded fixed-pattern diagnostics, not all-order obstructions,
geometric realizability results, counterexamples, or a proof of Erdos
Problem #97.
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
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
    inverse_pair_audit,
    lightweight_summary,
)
from run_sparse_full_cone_seeded_cegar import (  # noqa: E402
    ClauseOrbit,
    add_exact_order_block,
    build_clause_orbit,
    clause_hash,
    file_sha256,
    rotate_order_to_zero,
    transform_certificate,
)


DEFAULT_SOURCE = (
    ROOT
    / "data"
    / "runs"
    / "sparse_full_cone_seeded_compression_2026-07-29"
    / "summary.json"
)

Quad = tuple[int, int, int, int]
FullClause = tuple[Quad, ...]


def require_z3() -> None:
    if Z3_IMPORT_ERROR is not None:
        raise RuntimeError("z3-solver is required for fresh-order generation") from (
            Z3_IMPORT_ERROR
        )


def stable_json_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def reverse_anchored_order(order: Sequence[int]) -> list[int]:
    anchored = rotate_order_to_zero(order)
    return [0, *reversed(anchored[1:])]


def dihedral_order_key(order: Sequence[int]) -> tuple[int, ...]:
    """Canonicalize a cyclic order under rotation and reversal only."""

    anchored = rotate_order_to_zero(order)
    reverse = reverse_anchored_order(anchored)
    return min(tuple(anchored), tuple(reverse))


def order_record_hashes(order: Sequence[int]) -> dict[str, str]:
    anchored = rotate_order_to_zero(order)
    return {
        "order_sha256": stable_json_sha256(anchored),
        "dihedral_order_sha256": stable_json_sha256(dihedral_order_key(anchored)),
    }


def historical_orders_by_pattern(
    payload: Mapping[str, Any],
) -> dict[str, list[list[int]]]:
    result: dict[str, list[list[int]]] = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        orders = [
            [int(label) for label in target["order"]] for target in run["target_orders"]
        ]
        keys = [dihedral_order_key(order) for order in orders]
        if len(keys) != len(set(keys)):
            raise AssertionError(f"{name} historical order packet has dihedral repeats")
        result[name] = orders
    return result


def canonical_certificate_for_orbit(
    certificate: Mapping[str, Any],
    orbit: ClauseOrbit,
) -> tuple[dict[str, object], FullClause]:
    """Return the lexicographically first exact certificate for the orbit clause."""

    pattern = certificate["pattern"]
    n = int(pattern["n"])
    canonical_clause = orbit.clauses[0]
    candidates: list[tuple[str, dict[str, object]]] = []
    for multiplier in orbit.multipliers:
        for translation in range(n):
            transformed = transform_certificate(
                certificate,
                multiplier=multiplier,
                translation=translation,
            )
            clause = tuple(
                certificate_order_quads(
                    transformed,
                    transformed["cyclic_order"],
                )
            )
            if clause == canonical_clause:
                key = json.dumps(
                    {
                        "cyclic_order": transformed["cyclic_order"],
                        "inequalities": transformed["inequalities"],
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                candidates.append((key, transformed))
    if not candidates:
        raise AssertionError("canonical orbit clause has no certificate image")
    canonical = min(candidates, key=lambda item: item[0])[1]
    checked = check_certificate_dict(canonical)
    if not checked.zero_sum_verified:
        raise AssertionError("canonical template certificate failed exact replay")
    return canonical, canonical_clause


def build_small_templates(
    payload: Mapping[str, Any],
    *,
    max_width: int,
) -> tuple[dict[str, list[dict[str, object]]], dict[str, list[ClauseOrbit]]]:
    records: dict[str, list[dict[str, object]]] = {}
    orbits_by_pattern: dict[str, list[ClauseOrbit]] = {}
    for run in payload["runs"]:
        name = str(run["pattern"])
        pattern_records = []
        pattern_orbits = []
        seen_hashes: set[str] = set()
        for row in run["compressed_models"]:
            width = int(row["compressed_unique_ordered_quad_count"])
            if width > max_width:
                continue
            source_model_index = int(row["source_model_index"])
            source_certificate = row["compressed_certificate"]
            orbit = build_clause_orbit(name, source_model_index, source_certificate)
            canonical, clause = canonical_certificate_for_orbit(
                source_certificate,
                orbit,
            )
            canonical_hash = clause_hash(clause)
            if canonical_hash != orbit.canonical_clause_sha256:
                raise AssertionError("canonical template clause hash drifted")
            if canonical_hash in seen_hashes:
                raise AssertionError(f"{name} duplicate canonical template orbit")
            seen_hashes.add(canonical_hash)
            checked = check_certificate_dict(canonical)
            template_id = (
                f"{name}:seeded-{source_model_index}:w{width}:{canonical_hash[:16]}"
            )
            pattern_records.append(
                {
                    "template_id": template_id,
                    "pattern": name,
                    "source_model_index": source_model_index,
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
            pattern_orbits.append(orbit)
        records[name] = sorted(
            pattern_records,
            key=lambda row: str(row["template_id"]),
        )
        orbits_by_pattern[name] = sorted(
            pattern_orbits,
            key=lambda orbit: orbit.source_model_index,
        )
    return records, orbits_by_pattern


def template_matches(
    order: Sequence[int],
    templates: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> list[dict[str, object]]:
    template_by_source = {
        int(template["source_model_index"]): template for template in templates
    }
    matches = []
    for orbit in orbits:
        count = sum(order_satisfies_quads(order, clause) for clause in orbit.clauses)
        if count:
            template = template_by_source[orbit.source_model_index]
            matches.append(
                {
                    "template_id": str(template["template_id"]),
                    "matching_orbit_clause_count": count,
                }
            )
    return sorted(matches, key=lambda row: str(row["template_id"]))


def coverage_summary(
    models: Sequence[Mapping[str, Any]],
    templates: Sequence[Mapping[str, Any]],
) -> dict[str, object]:
    by_template = {
        str(template["template_id"]): {
            "matched_fresh_orders": 0,
            "matched_strong_fresh_orders": 0,
            "matching_orbit_clause_occurrences": 0,
        }
        for template in templates
    }
    hit_histogram: Counter[int] = Counter()
    covered = 0
    strong = 0
    covered_strong = 0
    for model in models:
        matches = model["template_matches"]
        is_strong = bool(model["lightweight_filters"]["survives"])
        strong += int(is_strong)
        covered += int(bool(matches))
        covered_strong += int(bool(matches) and is_strong)
        hit_histogram[len(matches)] += 1
        for match in matches:
            row = by_template[str(match["template_id"])]
            row["matched_fresh_orders"] += 1
            row["matched_strong_fresh_orders"] += int(is_strong)
            row["matching_orbit_clause_occurrences"] += int(
                match["matching_orbit_clause_count"]
            )
    count = len(models)
    return {
        "fresh_order_count": count,
        "strong_fresh_order_count": strong,
        "covered_fresh_order_count": covered,
        "covered_fresh_order_fraction": covered / count if count else None,
        "covered_strong_fresh_order_count": covered_strong,
        "covered_strong_fresh_order_fraction": (
            covered_strong / strong if strong else None
        ),
        "template_hit_count_histogram": {
            str(key): hit_histogram[key] for key in sorted(hit_histogram)
        },
        "by_template": [
            {"template_id": template_id, **by_template[template_id]}
            for template_id in sorted(by_template)
        ],
    }


def block_dihedral_order(
    solver: object,
    positions: Sequence[object],
    order: Sequence[int],
) -> None:
    anchored = rotate_order_to_zero(order)
    add_exact_order_block(solver, positions, anchored)
    reverse = reverse_anchored_order(anchored)
    if reverse != anchored:
        add_exact_order_block(solver, positions, reverse)


def collect_fresh_orders(
    name: str,
    templates: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
    historical_orders: Sequence[Sequence[int]],
    *,
    order_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> dict[str, object]:
    require_z3()
    n, offsets = PATTERNS[name]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    excluded_keys = {dihedral_order_key(order) for order in historical_orders}
    for order in historical_orders:
        block_dihedral_order(solver, positions, order)

    inverse_clauses: set[tuple[Quad, Quad]] = set()
    models = []
    status = "BOUNDED_FRESH_STREAM_ITERATION_LIMIT"
    solver_result = "iteration_limit"
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            status = "FRESH_STREAM_SOLVER_UNSAT"
            solver_result = "unsat"
            break
        if result != sat:
            status = "UNKNOWN_FRESH_STREAM_SMT_RESULT"
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
        if key in excluded_keys:
            raise AssertionError("fresh solver admitted an excluded dihedral order")
        audit = inverse_pair_audit(name, n, offsets, order)
        if audit["inverse_pair_conflicts"] != 0:
            raise AssertionError("fresh order did not escape inverse pairs")
        model = {
            "fresh_model_index": len(models),
            "z3_iteration": iteration,
            "order": order,
            **order_record_hashes(order),
            "lightweight_filters": lightweight_summary(name, order),
            "inverse_pair_audit": audit,
            "template_matches": template_matches(order, templates, orbits),
        }
        models.append(model)
        excluded_keys.add(key)
        block_dihedral_order(solver, positions, order)
        if len(models) >= order_limit:
            status = "BOUNDED_FRESH_ORDER_LIMIT_REACHED"
            solver_result = "bounded_after_fresh_inverse_pair_escape_orders"
            break

    return {
        "status": status,
        "solver_result": solver_result,
        "iterations": iterations,
        "random_seed": random_seed,
        "historical_dihedral_order_count": len(
            {dihedral_order_key(order) for order in historical_orders}
        ),
        "inverse_pair_clause_count": len(inverse_clauses),
        "fresh_inverse_pair_escape_order_count": len(models),
        "models": models,
        "coverage": coverage_summary(models, templates),
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    templates_by_pattern, orbits_by_pattern = build_small_templates(
        source,
        max_width=args.max_template_width,
    )
    history_by_pattern = historical_orders_by_pattern(source)
    selected_names = args.pattern or list(PATTERNS)
    runs = []
    for pattern_index, name in enumerate(selected_names):
        random_seed = args.random_seed + pattern_index * args.pattern_seed_stride
        templates = templates_by_pattern[name]
        history = history_by_pattern[name]
        fresh = collect_fresh_orders(
            name,
            templates,
            orbits_by_pattern[name],
            history,
            order_limit=args.order_limit,
            max_iterations=args.max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=random_seed,
        )
        n, offsets = PATTERNS[name]
        runs.append(
            {
                "pattern": name,
                "n": n,
                "circulant_offsets": offsets,
                "historical_order_count": len(history),
                "historical_dihedral_order_count": len(
                    {dihedral_order_key(order) for order in history}
                ),
                "canonical_small_templates": templates,
                "fresh_stream": fresh,
            }
        )

    return {
        "type": "sparse_full_cone_small_template_fresh_stream_v1",
        "trust": "EXACT_TEMPLATES_AND_BOUNDED_HISTORY_DISJOINT_ORDER_PROBE",
        "status": "BOUNDED_FRESH_STREAM_TEMPLATE_TRANSFER_DIAGNOSTIC",
        "claim_scope": (
            "Seven exact three-to-eight-quad C25/C29 positive-circuit templates "
            "are canonicalized under quotient-preserving affine maps and replayed "
            "against bounded deterministic order streams that are dihedrally "
            "disjoint from forty-eight historical orders. Fresh means "
            "history-disjoint, not statistically independent. This is not an "
            "all-order obstruction, geometric realizability result, counterexample, "
            "proof of Erdos Problem #97, or official/global status update."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "source_sha256": file_sha256(source_path),
        "configuration": {
            "max_template_width": args.max_template_width,
            "fresh_order_limit_per_pattern": args.order_limit,
            "max_iterations_per_pattern": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "pattern_seed_stride": args.pattern_seed_stride,
            "freshness_equivalence": "cyclic rotation and reversal",
            "generation_filter": "exact two-inequality inverse-pair escape",
        },
        "runs": runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    if payload["type"] != "sparse_full_cone_small_template_fresh_stream_v1":
        raise AssertionError("fresh-stream artifact type drifted")
    source_path = ROOT / str(payload["source_artifact"])
    if file_sha256(source_path) != str(payload["source_sha256"]):
        raise AssertionError("source compression artifact hash drifted")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    configuration = payload["configuration"]
    max_width = int(configuration["max_template_width"])
    order_limit = int(configuration["fresh_order_limit_per_pattern"])
    max_iterations = int(configuration["max_iterations_per_pattern"])
    conflict_cap = int(configuration["conflict_cap"])
    base_seed = int(configuration["random_seed"])
    pattern_seed_stride = int(configuration["pattern_seed_stride"])
    templates_by_pattern, orbits_by_pattern = build_small_templates(
        source,
        max_width=max_width,
    )
    history_by_pattern = historical_orders_by_pattern(source)
    verified_templates = 0
    verified_images = 0
    verified_fresh_orders = 0
    seen_patterns: set[str] = set()

    for pattern_index, run in enumerate(payload["runs"]):
        name = str(run["pattern"])
        if name in seen_patterns or name not in PATTERNS:
            raise AssertionError(f"invalid or duplicate fresh-stream pattern: {name}")
        seen_patterns.add(name)
        templates = templates_by_pattern[name]
        orbits = orbits_by_pattern[name]
        if run["canonical_small_templates"] != templates:
            raise AssertionError(f"{name} canonical template packet drifted")
        history = history_by_pattern[name]
        history_keys = {dihedral_order_key(order) for order in history}
        if int(run["historical_order_count"]) != len(history):
            raise AssertionError(f"{name} historical order count drifted")
        if int(run["historical_dihedral_order_count"]) != len(history_keys):
            raise AssertionError(f"{name} historical dihedral count drifted")

        fresh = run["fresh_stream"]
        expected_seed = base_seed + pattern_index * pattern_seed_stride
        if int(fresh["random_seed"]) != expected_seed:
            raise AssertionError(f"{name} random seed drifted")
        iterations = int(fresh["iterations"])
        if not 1 <= iterations <= max_iterations:
            raise AssertionError(f"{name} iteration count drifted")
        inverse_clause_count = int(fresh["inverse_pair_clause_count"])
        if not 0 <= inverse_clause_count <= iterations * conflict_cap:
            raise AssertionError(f"{name} inverse-pair clause count drifted")
        models = fresh["models"]
        if int(fresh["fresh_inverse_pair_escape_order_count"]) != len(models):
            raise AssertionError(f"{name} fresh order count drifted")

        verified_templates += len(templates)
        verified_images += sum(orbit.affine_map_count for orbit in orbits)
        seen = set(history_keys)
        checked_models = []
        previous_z3_iteration = 0
        for expected_model_index, model in enumerate(models):
            if int(model["fresh_model_index"]) != expected_model_index:
                raise AssertionError(f"{name} fresh model index drifted")
            z3_iteration = int(model["z3_iteration"])
            if not previous_z3_iteration < z3_iteration <= iterations:
                raise AssertionError(f"{name} model iteration provenance drifted")
            previous_z3_iteration = z3_iteration
            order = [int(label) for label in model["order"]]
            n = int(run["n"])
            if sorted(order) != list(range(n)) or order[0] != 0:
                raise AssertionError(f"{name} invalid anchored cyclic order")
            key = dihedral_order_key(order)
            if key in seen:
                raise AssertionError(f"{name} fresh stream has a dihedral repeat")
            seen.add(key)
            if model | {"order": order} != model:
                raise AssertionError(f"{name} order labels are not stored as integers")
            expected_hashes = order_record_hashes(order)
            for field, value in expected_hashes.items():
                if model[field] != value:
                    raise AssertionError(f"{name} {field} drifted")
            n_expected, offsets = PATTERNS[name]
            if n != n_expected:
                raise AssertionError(f"{name} n drifted")
            audit = inverse_pair_audit(name, n, offsets, order)
            if audit != model["inverse_pair_audit"]:
                raise AssertionError(f"{name} inverse-pair audit drifted")
            if audit["inverse_pair_conflicts"] != 0:
                raise AssertionError(f"{name} fresh order has an inverse pair")
            if lightweight_summary(name, order) != model["lightweight_filters"]:
                raise AssertionError(f"{name} lightweight filter summary drifted")
            expected_matches = template_matches(order, templates, orbits)
            if model["template_matches"] != expected_matches:
                raise AssertionError(f"{name} exact template matches drifted")
            checked_models.append(model)
            verified_fresh_orders += 1

        if len(checked_models) >= order_limit:
            if len(checked_models) != order_limit:
                raise AssertionError(f"{name} fresh order limit drifted")
            if fresh["status"] != "BOUNDED_FRESH_ORDER_LIMIT_REACHED":
                raise AssertionError(f"{name} bounded status drifted")
            if (
                fresh["solver_result"]
                != "bounded_after_fresh_inverse_pair_escape_orders"
            ):
                raise AssertionError(f"{name} bounded solver result drifted")
            if iterations != previous_z3_iteration:
                raise AssertionError(f"{name} terminal iteration drifted")
        elif iterations == max_iterations:
            if fresh["status"] != "BOUNDED_FRESH_STREAM_ITERATION_LIMIT":
                raise AssertionError(f"{name} iteration-limit status drifted")
            if fresh["solver_result"] != "iteration_limit":
                raise AssertionError(f"{name} iteration-limit result drifted")
        elif fresh["status"] == "FRESH_STREAM_SOLVER_UNSAT":
            if fresh["solver_result"] != "unsat":
                raise AssertionError(f"{name} unsat result drifted")
        elif fresh["status"] != "UNKNOWN_FRESH_STREAM_SMT_RESULT":
            raise AssertionError(f"{name} solver termination status drifted")
        if inverse_clause_count < iterations - len(checked_models):
            raise AssertionError(f"{name} inverse-pair clause provenance drifted")
        if int(fresh["historical_dihedral_order_count"]) != len(history_keys):
            raise AssertionError(f"{name} stream history count drifted")
        if fresh["coverage"] != coverage_summary(checked_models, templates):
            raise AssertionError(f"{name} fresh coverage summary drifted")

    return {
        "status": "OK",
        "verified_canonical_exact_templates": verified_templates,
        "verified_exact_affine_template_images": verified_images,
        "verified_history_disjoint_fresh_orders": verified_fresh_orders,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--max-template-width", type=int, default=8)
    parser.add_argument("--order-limit", type=int, default=32)
    parser.add_argument("--max-iterations", type=int, default=16_000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=20260730)
    parser.add_argument("--pattern-seed-stride", type=int, default=1000)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    positive = (
        args.max_template_width,
        args.order_limit,
        args.max_iterations,
        args.conflict_cap,
        args.pattern_seed_stride,
    )
    if any(value <= 0 for value in positive):
        raise SystemExit(
            "width, limits, conflict cap, and seed stride must be positive"
        )
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
            coverage = run["fresh_stream"]["coverage"]
            print(
                f"{run['pattern']}: "
                f"templates={len(run['canonical_small_templates'])} "
                f"fresh={coverage['fresh_order_count']} "
                f"strong={coverage['strong_fresh_order_count']} "
                f"covered={coverage['covered_fresh_order_count']} "
                f"covered_strong={coverage['covered_strong_fresh_order_count']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
