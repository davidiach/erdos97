#!/usr/bin/env python3
"""Run a longer sparse full-cone CEGAR seeded by exact clause orbits.

The compressed C25/C29 certificates are expanded only through affine label
maps that preserve the selected-distance quotient.  Every transformed
certificate is checked exactly before its ordered-quadrilateral clause is
used.  A separate counterfactual inverse-pair-escape stream measures which
seed orbits would fire; the seeded CEGAR then activates all of those clauses
from the start and learns symmetry-expanded clauses from new exact
certificates.

All results remain bounded and fixed-pattern.  A certificate-limit result is
not an all-order obstruction, a geometric counterexample, or a proof of Erdos
Problem #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Mapping, Sequence

try:
    from z3 import Or, sat, unsat
except ImportError as exc:  # pragma: no cover - optional development dependency
    Or = sat = unsat = None  # type: ignore[assignment]
    Z3_IMPORT_ERROR: ImportError | None = exc
else:
    Z3_IMPORT_ERROR = None


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SRC, SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import (  # noqa: E402
    build_distance_classes,
    check_certificate_dict,
    inequality_terms,
)
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
from kalmanson_order_utils import KINDS  # noqa: E402
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    add_full_certificate_clause,
    certificate_order_quads,
    inverse_pair_audit,
    lightweight_summary,
)


DEFAULT_SEED_SOURCE = (
    ROOT / "data" / "runs" / "sparse_full_cone_compression_2026-07-23" / "summary.json"
)

Quad = tuple[int, int, int, int]
FullClause = tuple[Quad, ...]
InverseClause = tuple[Quad, Quad]


@dataclass(frozen=True)
class ClauseOrbit:
    pattern: str
    source_model_index: int
    source_order: tuple[int, ...]
    source_certificate: Mapping[str, Any]
    multipliers: tuple[int, ...]
    affine_map_count: int
    clauses: tuple[FullClause, ...]
    canonical_clause_sha256: str

    def summary(self) -> dict[str, object]:
        return {
            "source_model_index": self.source_model_index,
            "source_order": list(self.source_order),
            "source_unique_ordered_quad_count": len(self.clauses[0]),
            "quotient_automorphism_multipliers": list(self.multipliers),
            "affine_map_count": self.affine_map_count,
            "unique_orbit_clause_count": len(self.clauses),
            "affine_stabilizer_size": self.affine_map_count // len(self.clauses),
            "canonical_clause_sha256": self.canonical_clause_sha256,
        }


def require_z3() -> None:
    if Z3_IMPORT_ERROR is not None:
        raise RuntimeError(
            "z3-solver is required for this experiment"
        ) from Z3_IMPORT_ERROR


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def rotate_order_to_zero(order: Sequence[int]) -> list[int]:
    values = [int(label) for label in order]
    zero = values.index(0)
    return values[zero:] + values[:zero]


def quotient_automorphism_multipliers(n: int, offsets: Sequence[int]) -> list[int]:
    """Return multipliers that permute the exact distance-class partition."""

    classes = build_distance_classes(n, offsets)
    pairs = list(combinations(range(n), 2))
    accepted = []
    for multiplier in range(1, n):
        if math.gcd(multiplier, n) != 1:
            continue
        class_map: dict[int, int] = {}
        valid = True
        for a, b in pairs:
            source_class = classes[(a, b)]
            target_pair = pair(
                (multiplier * a) % n,
                (multiplier * b) % n,
            )
            target_class = classes[target_pair]
            previous = class_map.setdefault(source_class, target_class)
            if previous != target_class:
                valid = False
                break
        if valid and len(set(class_map.values())) == len(class_map):
            accepted.append(multiplier)
    return accepted


def transformed_terms(
    kind: str,
    quad: Sequence[int],
    *,
    n: int,
    multiplier: int,
    translation: int,
) -> Counter[tuple[int, int]]:
    result: Counter[tuple[int, int]] = Counter()
    for (a, b), coefficient in inequality_terms(kind, quad):
        mapped = pair(
            (multiplier * a + translation) % n,
            (multiplier * b + translation) % n,
        )
        result[mapped] += coefficient
    return result


def transform_certificate(
    certificate: Mapping[str, Any],
    *,
    multiplier: int,
    translation: int,
) -> dict[str, object]:
    """Relabel and cyclically re-anchor one exact certificate."""

    pattern = certificate["pattern"]
    n = int(pattern["n"])
    mapped_order = [
        (multiplier * int(label) + translation) % n
        for label in certificate["cyclic_order"]
    ]
    order = rotate_order_to_zero(mapped_order)
    positions = {label: index for index, label in enumerate(order)}
    inequalities = []
    for item in certificate["inequalities"]:
        mapped_labels = [
            (multiplier * int(label) + translation) % n for label in item["quad"]
        ]
        quad = tuple(sorted(mapped_labels, key=positions.__getitem__))
        source_terms = transformed_terms(
            str(item["kind"]),
            item["quad"],
            n=n,
            multiplier=multiplier,
            translation=translation,
        )
        matching_kinds = [
            kind
            for kind in KINDS
            if Counter(dict(inequality_terms(kind, quad))) == source_terms
        ]
        if len(matching_kinds) != 1:
            raise AssertionError(
                "transformed Kalmanson inequality did not match one exact row"
            )
        inequalities.append(
            {
                "kind": matching_kinds[0],
                "quad": list(quad),
                "weight": int(item["weight"]),
            }
        )

    transformed = dict(certificate)
    transformed["cyclic_order"] = order
    transformed["inequalities"] = inequalities
    transformed["num_inequalities"] = len(inequalities)
    transformed["weight_sum"] = sum(int(item["weight"]) for item in inequalities)
    check_certificate_dict(transformed)
    return transformed


def clause_hash(clause: FullClause) -> str:
    encoded = json.dumps(clause, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def build_clause_orbit(
    name: str,
    source_model_index: int,
    certificate: Mapping[str, Any],
) -> ClauseOrbit:
    n, offsets = PATTERNS[name]
    checked = check_certificate_dict(certificate)
    if not checked.zero_sum_verified:
        raise AssertionError("source seed certificate did not verify")
    multipliers = quotient_automorphism_multipliers(n, offsets)
    clauses: set[FullClause] = set()
    for multiplier in multipliers:
        for translation in range(n):
            transformed = transform_certificate(
                certificate,
                multiplier=multiplier,
                translation=translation,
            )
            quads = certificate_order_quads(
                transformed,
                transformed["cyclic_order"],
            )
            clauses.add(tuple(quads))
    ordered_clauses = tuple(sorted(clauses))
    if not ordered_clauses:
        raise AssertionError("certificate orbit is empty")
    affine_map_count = n * len(multipliers)
    if affine_map_count % len(ordered_clauses):
        raise AssertionError("affine orbit size does not divide the acting group")
    return ClauseOrbit(
        pattern=name,
        source_model_index=source_model_index,
        source_order=tuple(int(label) for label in certificate["cyclic_order"]),
        source_certificate=certificate,
        multipliers=tuple(multipliers),
        affine_map_count=affine_map_count,
        clauses=ordered_clauses,
        canonical_clause_sha256=clause_hash(ordered_clauses[0]),
    )


def load_seed_orbits(path: Path) -> dict[str, list[ClauseOrbit]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    result: dict[str, list[ClauseOrbit]] = defaultdict(list)
    for run in payload["runs"]:
        name = str(run["pattern"])
        for row in run["compressed_models"]:
            result[name].append(
                build_clause_orbit(
                    name,
                    int(row["source_model_index"]),
                    row["compressed_certificate"],
                )
            )
    return {
        name: sorted(orbits, key=lambda orbit: orbit.source_model_index)
        for name, orbits in result.items()
    }


def unique_clauses(orbits: Sequence[ClauseOrbit]) -> list[FullClause]:
    return sorted({clause for orbit in orbits for clause in orbit.clauses})


def clause_matches(
    order: Sequence[int], orbits: Sequence[ClauseOrbit]
) -> list[dict[str, int]]:
    matches = []
    for orbit in orbits:
        count = sum(order_satisfies_quads(order, clause) for clause in orbit.clauses)
        if count:
            matches.append(
                {
                    "source_model_index": orbit.source_model_index,
                    "matching_orbit_clause_count": count,
                }
            )
    return matches


def add_exact_order_block(
    solver: object, positions: Sequence[object], order: Sequence[int]
) -> None:
    require_z3()
    assert Or is not None
    solver.add(
        Or(*[positions[int(label)] != index for index, label in enumerate(order)])
    )


def collect_probe_orders(
    name: str,
    orbits: Sequence[ClauseOrbit],
    *,
    order_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> tuple[dict[str, object], set[InverseClause]]:
    n, offsets = PATTERNS[name]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    inverse_clauses: set[InverseClause] = set()
    models = []
    status = "BOUNDED_PROBE_ITERATION_LIMIT"
    solver_result = "iteration_limit"
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            status = "PROBE_SOLVER_UNSAT"
            solver_result = "unsat"
            break
        if result != sat:
            status = "UNKNOWN_PROBE_SMT_RESULT"
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

        audit = inverse_pair_audit(name, n, offsets, order)
        if audit["inverse_pair_conflicts"] != 0:
            raise AssertionError(
                "probe model did not independently escape inverse pairs"
            )
        models.append(
            {
                "probe_model_index": len(models),
                "z3_iteration": iteration,
                "order": order,
                "lightweight_filters": lightweight_summary(name, order),
                "seed_orbit_matches": clause_matches(order, orbits),
            }
        )
        add_exact_order_block(solver, positions, order)
        if len(models) >= order_limit:
            status = "BOUNDED_PROBE_ORDER_LIMIT_REACHED"
            solver_result = "bounded_after_inverse_pair_escape_models"
            break

    return (
        {
            "status": status,
            "solver_result": solver_result,
            "iterations": iterations,
            "inverse_pair_clause_count": len(inverse_clauses),
            "inverse_pair_escape_order_count": len(models),
            "models": models,
        },
        inverse_clauses,
    )


def probe_coverage_summary(
    models: Sequence[Mapping[str, Any]],
    orbits: Sequence[ClauseOrbit],
) -> dict[str, object]:
    covered = 0
    strong = 0
    covered_strong = 0
    overlap_histogram: Counter[int] = Counter()
    by_source: dict[int, dict[str, int]] = {
        orbit.source_model_index: {
            "matched_probe_orders": 0,
            "matched_strong_probe_orders": 0,
            "matching_orbit_clause_occurrences": 0,
        }
        for orbit in orbits
    }
    for model in models:
        matches = model["seed_orbit_matches"]
        is_strong = bool(model["lightweight_filters"]["survives"])
        strong += int(is_strong)
        covered += int(bool(matches))
        covered_strong += int(bool(matches) and is_strong)
        overlap_histogram[len(matches)] += 1
        for match in matches:
            row = by_source[int(match["source_model_index"])]
            row["matched_probe_orders"] += 1
            row["matched_strong_probe_orders"] += int(is_strong)
            row["matching_orbit_clause_occurrences"] += int(
                match["matching_orbit_clause_count"]
            )
    count = len(models)
    return {
        "probe_order_count": count,
        "strong_probe_order_count": strong,
        "covered_probe_order_count": covered,
        "covered_probe_order_fraction": covered / count if count else None,
        "covered_strong_probe_order_count": covered_strong,
        "covered_strong_probe_order_fraction": (
            covered_strong / strong if strong else None
        ),
        "seed_source_overlap_histogram": {
            str(key): overlap_histogram[key] for key in sorted(overlap_histogram)
        },
        "by_seed_source": [
            {"source_model_index": source, **by_source[source]}
            for source in sorted(by_source)
        ],
    }


def run_seeded_cegar(
    name: str,
    seed_orbits: Sequence[ClauseOrbit],
    initial_inverse_clauses: set[InverseClause],
    *,
    full_certificate_limit: int,
    max_iterations: int,
    conflict_cap: int,
    random_seed: int,
) -> dict[str, object]:
    n, offsets = PATTERNS[name]
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    solver, positions = _make_solver(n, random_seed)
    inverse_clauses = set(initial_inverse_clauses)
    for clause in sorted(inverse_clauses):
        _add_clause(solver, positions, clause)

    seed_clauses = unique_clauses(seed_orbits)
    for clause in seed_clauses:
        add_full_certificate_clause(solver, positions, clause)

    learned_orbits: list[ClauseOrbit] = []
    active_learned_clauses: set[FullClause] = set()
    models = []
    status = "BOUNDED_SEEDED_CEGAR_ITERATION_LIMIT"
    solver_result = "iteration_limit"
    iterations = 0

    for iteration in range(1, max_iterations + 1):
        iterations = iteration
        result = solver.check()
        if result == unsat:
            status = "REVIEW_PENDING_SEEDED_EXACT_SOLVER_UNSAT"
            solver_result = "unsat"
            break
        if result != sat:
            status = "UNKNOWN_SEEDED_SMT_RESULT"
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

        seed_matches = clause_matches(order, seed_orbits)
        if seed_matches:
            raise AssertionError("active seed clause admitted a matching order")
        prior_learned_matches = sum(
            order_satisfies_quads(order, clause) for clause in active_learned_clauses
        )
        if prior_learned_matches:
            raise AssertionError(
                "active learned orbit clause admitted a matching order"
            )
        audit = inverse_pair_audit(name, n, offsets, order)
        if audit["inverse_pair_conflicts"] != 0:
            raise AssertionError("seeded CEGAR model did not escape inverse pairs")

        certificate = find_certificate(name, n, offsets, order, 1.0e-9)
        if certificate is None:
            models.append(
                {
                    "model_index": len(models),
                    "z3_iteration": iteration,
                    "order": order,
                    "lightweight_filters": lightweight_summary(name, order),
                    "seed_orbit_matches": [],
                    "prior_learned_orbit_clause_matches": 0,
                    "full_kalmanson": {
                        "status": "NO_EXACT_FIXED_ORDER_CERTIFICATE_FOUND"
                    },
                }
            )
            status = "NO_EXACT_FULL_CONE_CERTIFICATE_FOUND_FOR_SEEDED_MODEL"
            solver_result = "sat"
            break

        checked = check_certificate_dict(certificate)
        if not checked.zero_sum_verified:
            raise AssertionError("new full-cone certificate did not verify")
        quads = certificate_order_quads(certificate, order)
        orbit = build_clause_orbit(name, len(models), certificate)
        new_orbit_clauses = [
            clause for clause in orbit.clauses if clause not in active_learned_clauses
        ]
        for clause in new_orbit_clauses:
            add_full_certificate_clause(solver, positions, clause)
            active_learned_clauses.add(clause)
        learned_orbits.append(orbit)
        models.append(
            {
                "model_index": len(models),
                "z3_iteration": iteration,
                "inverse_clause_count_at_discovery": len(inverse_clauses),
                "order": order,
                "lightweight_filters": lightweight_summary(name, order),
                "inverse_pair_audit": audit,
                "seed_orbit_matches": [],
                "prior_learned_orbit_clause_matches": 0,
                "full_kalmanson": {
                    "status": checked.status,
                    "positive_inequalities": checked.positive_inequalities,
                    "unique_ordered_quad_count": len(quads),
                    "weight_sum": checked.weight_sum,
                    "max_weight": checked.max_weight,
                    "zero_sum_verified": checked.zero_sum_verified,
                    "affine_clause_orbit": orbit.summary(),
                    "new_unique_affine_orbit_clauses_added": len(new_orbit_clauses),
                    "certificate": certificate,
                },
            }
        )
        if len(learned_orbits) >= full_certificate_limit:
            status = "BOUNDED_SEEDED_FULL_CERTIFICATE_LIMIT_REACHED"
            solver_result = "bounded_after_new_exact_certificates"
            break

    return {
        "status": status,
        "solver_result": solver_result,
        "iterations": iterations,
        "initial_probe_inverse_clause_count": len(initial_inverse_clauses),
        "final_inverse_pair_clause_count": len(inverse_clauses),
        "active_unique_seed_orbit_clause_count": len(seed_clauses),
        "new_full_certificate_count": len(learned_orbits),
        "new_unique_affine_orbit_clause_count": len(active_learned_clauses),
        "models": models,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    seed_path = (
        args.seed_source if args.seed_source.is_absolute() else ROOT / args.seed_source
    )
    all_seed_orbits = load_seed_orbits(seed_path)
    names = args.pattern or list(PATTERNS)
    runs = []
    for name in names:
        seed_orbits = all_seed_orbits[name]
        probe, inverse_clauses = collect_probe_orders(
            name,
            seed_orbits,
            order_limit=args.probe_order_limit,
            max_iterations=args.probe_max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=args.random_seed,
        )
        coverage = probe_coverage_summary(probe["models"], seed_orbits)
        seeded = run_seeded_cegar(
            name,
            seed_orbits,
            inverse_clauses,
            full_certificate_limit=args.full_certificate_limit,
            max_iterations=args.max_iterations,
            conflict_cap=args.conflict_cap,
            random_seed=args.random_seed,
        )
        n, offsets = PATTERNS[name]
        canonical_hashes = Counter(
            orbit.canonical_clause_sha256 for orbit in seed_orbits
        )
        runs.append(
            {
                "pattern": name,
                "n": n,
                "circulant_offsets": offsets,
                "seed_orbits": [orbit.summary() for orbit in seed_orbits],
                "distinct_seed_orbit_class_count": len(canonical_hashes),
                "seed_orbit_class_multiplicities": {
                    key: canonical_hashes[key] for key in sorted(canonical_hashes)
                },
                "unique_seed_orbit_clause_count": len(unique_clauses(seed_orbits)),
                "counterfactual_probe": probe,
                "counterfactual_seed_coverage": coverage,
                "seeded_cegar": seeded,
            }
        )

    return {
        "type": "sparse_full_cone_seeded_affine_cegar_v1",
        "trust": "EXACT_CLAUSES_IN_BOUNDED_FIXED_PATTERN_SEEDED_CEGAR",
        "status": "BOUNDED_DIAGNOSTIC_REQUIRING_REVIEW_FOR_ANY_UNSAT",
        "claim_scope": (
            "Exact compressed seed certificates and quotient-preserving affine "
            "images in bounded fixed-pattern C25/C29 order searches. Probe hit "
            "rates and certificate-limit results are not all-order obstructions, "
            "geometric realizability results, counterexamples, or a proof of "
            "Erdos Problem #97."
        ),
        "seed_source_artifact": seed_path.relative_to(ROOT).as_posix(),
        "seed_source_sha256": file_sha256(seed_path),
        "configuration": {
            "probe_order_limit": args.probe_order_limit,
            "probe_max_iterations": args.probe_max_iterations,
            "full_certificate_limit": args.full_certificate_limit,
            "max_iterations": args.max_iterations,
            "conflict_cap": args.conflict_cap,
            "random_seed": args.random_seed,
            "tolerance": 1.0e-9,
        },
        "runs": runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    seed_path = ROOT / str(payload["seed_source_artifact"])
    if file_sha256(seed_path) != str(payload["seed_source_sha256"]):
        raise AssertionError("seed source artifact hash drifted")
    all_seed_orbits = load_seed_orbits(seed_path)
    verified_probe_orders = 0
    verified_new_certificates = 0
    verified_affine_certificate_images = 0

    for run in payload["runs"]:
        name = str(run["pattern"])
        n, offsets = PATTERNS[name]
        seed_orbits = all_seed_orbits[name]
        expected_seed_summaries = [orbit.summary() for orbit in seed_orbits]
        if run["seed_orbits"] != expected_seed_summaries:
            raise AssertionError(f"{name} seed orbit summary drifted")
        if int(run["unique_seed_orbit_clause_count"]) != len(
            unique_clauses(seed_orbits)
        ):
            raise AssertionError(f"{name} seed orbit clause count drifted")
        verified_affine_certificate_images += sum(
            orbit.affine_map_count for orbit in seed_orbits
        )

        probe_models = run["counterfactual_probe"]["models"]
        for model in probe_models:
            order = [int(label) for label in model["order"]]
            audit = inverse_pair_audit(name, n, offsets, order)
            if audit["inverse_pair_conflicts"] != 0:
                raise AssertionError(f"{name} probe order has an inverse pair")
            if clause_matches(order, seed_orbits) != model["seed_orbit_matches"]:
                raise AssertionError(f"{name} probe seed matches drifted")
            if lightweight_summary(name, order) != model["lightweight_filters"]:
                raise AssertionError(f"{name} probe lightweight filters drifted")
            verified_probe_orders += 1
        if (
            probe_coverage_summary(probe_models, seed_orbits)
            != run["counterfactual_seed_coverage"]
        ):
            raise AssertionError(f"{name} probe coverage summary drifted")

        learned_clauses: set[FullClause] = set()
        for model in run["seeded_cegar"]["models"]:
            order = [int(label) for label in model["order"]]
            audit = inverse_pair_audit(name, n, offsets, order)
            if audit["inverse_pair_conflicts"] != 0:
                raise AssertionError(f"{name} seeded model has an inverse pair")
            if clause_matches(order, seed_orbits):
                raise AssertionError(f"{name} seeded model matches a seed clause")
            if any(order_satisfies_quads(order, clause) for clause in learned_clauses):
                raise AssertionError(
                    f"{name} seeded model matches a prior learned orbit clause"
                )
            full = model["full_kalmanson"]
            certificate = full.get("certificate")
            if certificate is None:
                continue
            checked = check_certificate_dict(certificate)
            if not checked.zero_sum_verified:
                raise AssertionError(f"{name} new certificate did not verify")
            quads = certificate_order_quads(certificate, order)
            if len(quads) != int(full["unique_ordered_quad_count"]):
                raise AssertionError(f"{name} new full-clause width drifted")
            orbit = build_clause_orbit(name, int(model["model_index"]), certificate)
            if orbit.summary() != full["affine_clause_orbit"]:
                raise AssertionError(f"{name} learned affine orbit drifted")
            new_clauses = [
                clause for clause in orbit.clauses if clause not in learned_clauses
            ]
            if len(new_clauses) != int(full["new_unique_affine_orbit_clauses_added"]):
                raise AssertionError(f"{name} new affine clause count drifted")
            learned_clauses.update(new_clauses)
            verified_new_certificates += 1
            verified_affine_certificate_images += orbit.affine_map_count
        if len(learned_clauses) != int(
            run["seeded_cegar"]["new_unique_affine_orbit_clause_count"]
        ):
            raise AssertionError(f"{name} final learned orbit count drifted")

    return {
        "status": "OK",
        "verified_counterfactual_inverse_pair_escape_orders": verified_probe_orders,
        "verified_new_exact_full_cone_certificates": verified_new_certificates,
        "verified_exact_affine_certificate_images": (
            verified_affine_certificate_images
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed-source", type=Path, default=DEFAULT_SEED_SOURCE)
    parser.add_argument("--pattern", action="append", choices=sorted(PATTERNS))
    parser.add_argument("--probe-order-limit", type=int, default=16)
    parser.add_argument("--probe-max-iterations", type=int, default=8000)
    parser.add_argument("--full-certificate-limit", type=int, default=8)
    parser.add_argument("--max-iterations", type=int, default=8000)
    parser.add_argument("--conflict-cap", type=int, default=1024)
    parser.add_argument("--random-seed", type=int, default=19)
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
        raise SystemExit("all limits and the conflict cap must be positive")
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
            coverage = run["counterfactual_seed_coverage"]
            seeded = run["seeded_cegar"]
            print(
                f"{run['pattern']}: probe_covered="
                f"{coverage['covered_probe_order_count']}/"
                f"{coverage['probe_order_count']} "
                f"seed_orbit_clauses={run['unique_seed_orbit_clause_count']} "
                f"new_certificates={seeded['new_full_certificate_count']} "
                f"status={seeded['status']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
