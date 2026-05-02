"""Bounded adversarial stuck-motif search.

This module asks an SMT solver for fixed selected-witness systems with a
prescribed stuck subset, then runs the repo's exact necessary filters on each
model.  A found motif is an incidence/search object only; it is not a geometric
realization certificate.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from erdos97.incidence_filters import chords_cross_in_order, normalize_chord
from erdos97.stuck_sets import (
    find_minimal_stuck_sets,
    forward_ear_order,
    greedy_peeling_run,
    pattern_filter_snapshot,
    result_to_json,
    validate_selected_pattern,
)

Pattern = list[list[int]]


@dataclass(frozen=True)
class MotifSearchConfig:
    n: int
    stuck_size: int
    max_models: int = 100
    solver_seed: int = 0
    variable_prefix: str = "x"
    radius_node_limit: int = 100_000
    require_all_rows_cover: bool = True
    require_adjacent_overlap: bool = True
    require_crossing: bool = True
    require_no_odd_cycle: bool = True
    require_radius_pass: bool = True
    require_fragile_cover: bool = True
    require_no_forward_ear_order: bool = False
    fragile_cover_max_size: int | None = None


@dataclass(frozen=True)
class MotifSearchResult:
    config: MotifSearchConfig
    status: str
    models_checked: int
    rejection_counts: dict[str, int]
    motif: dict[str, object] | None
    rejected_examples: list[dict[str, object]]


def _z3():
    try:
        import z3  # type: ignore
    except Exception as exc:  # pragma: no cover - depends on optional dev dep
        raise RuntimeError("z3-solver is required for stuck motif search") from exc
    return z3


def _validate_config(config: MotifSearchConfig) -> None:
    if config.n < 5:
        raise ValueError(f"n must be at least 5, got {config.n}")
    if config.stuck_size < 4:
        raise ValueError(f"stuck_size must be at least 4, got {config.stuck_size}")
    if config.stuck_size > config.n:
        raise ValueError("stuck_size cannot exceed n")
    if config.max_models <= 0:
        raise ValueError("max_models must be positive")
    if config.radius_node_limit <= 0:
        raise ValueError("radius_node_limit must be positive")


def _model_to_rows(model, variables: Sequence[Sequence[object]]) -> Pattern:
    z3 = _z3()
    rows: Pattern = []
    for row in variables:
        rows.append(
            [
                int(label)
                for label, variable in enumerate(row)
                if z3.is_true(model.evaluate(variable, model_completion=True))
            ]
        )
    return rows


def _block_model(solver, variables: Sequence[Sequence[object]], rows: Pattern) -> None:
    z3 = _z3()
    ctx = variables[0][0].ctx
    differences = []
    row_sets = [set(row) for row in rows]
    for center, row in enumerate(variables):
        for label, variable in enumerate(row):
            value = label in row_sets[center]
            differences.append(variable != z3.BoolVal(value, ctx=ctx))
    solver.add(z3.Or(differences))


def _candidate_rejection(
    rows: Pattern,
    snapshot: dict[str, object],
    config: MotifSearchConfig,
) -> str | None:
    if not snapshot["row_pair_cap_ok"]:
        return "row_pair_cap"
    if not snapshot["column_pair_cap_ok"]:
        return "column_pair_cap"
    if config.require_all_rows_cover and not snapshot["all_rows_cover_vertices"]:
        return "all_rows_cover"
    if config.require_adjacent_overlap and snapshot["adjacent_two_overlap_violations"]:
        return "adjacent_two_overlap"
    if config.require_crossing and snapshot["crossing_bisector_violations"]:
        return "crossing_bisector"
    if (
        config.require_no_odd_cycle
        and snapshot["odd_forced_perpendicular_cycle_length"] is not None
    ):
        return "odd_forced_perpendicular_cycle"

    radius = snapshot["radius_propagation"]
    if config.require_radius_pass and radius["obstructed"] is not False:
        return "radius_propagation"

    fragile = snapshot["fragile_cover"]["cover_stats"]
    if config.require_fragile_cover:
        if fragile["status"] != "SEARCHED":
            return "fragile_cover_not_searched"
        if not fragile["cover_exists"] and fragile.get("search_complete"):
            return "fragile_cover"
        if not fragile["cover_exists"]:
            return "fragile_cover_not_found_in_window"

    if config.require_no_forward_ear_order and forward_ear_order(rows).exists:
        return "forward_ear_order"

    validate_selected_pattern(rows)
    return None


def _analysis_payload(
    name: str,
    rows: Pattern,
    snapshot: dict[str, object],
) -> dict[str, object]:
    stuck = find_minimal_stuck_sets(rows, max_examples=4)
    forward = forward_ear_order(rows)
    greedy = greedy_peeling_run(rows)
    return result_to_json(name, rows, stuck, forward, greedy_result=greedy, filters=snapshot)


def mine_stuck_motif(config: MotifSearchConfig) -> MotifSearchResult:
    """Return the first solver model surviving the configured filters."""

    _validate_config(config)
    z3 = _z3()
    n = config.n
    stuck_vertices = list(range(config.stuck_size))
    prefix = config.variable_prefix
    ctx = z3.Context()
    X = [
        [z3.Bool(f"{prefix}_{i}_{j}", ctx=ctx) for j in range(n)]
        for i in range(n)
    ]
    solver = z3.Solver(ctx=ctx)
    solver.set("random_seed", int(config.solver_seed))

    for i in range(n):
        solver.add(z3.Not(X[i][i]))
        solver.add(z3.PbEq([(X[i][j], 1) for j in range(n)], 4))

    for a in range(n):
        for b in range(a + 1, n):
            solver.add(z3.PbLe([(z3.And(X[a][j], X[b][j]), 1) for j in range(n)], 2))
            solver.add(z3.PbLe([(z3.And(X[i][a], X[i][b]), 1) for i in range(n)], 2))

    if config.require_all_rows_cover:
        for target in range(n):
            solver.add(z3.PbGe([(X[i][target], 1) for i in range(n)], 1))

    natural_order = list(range(n))
    if config.require_adjacent_overlap:
        for i in range(n):
            j = (i + 1) % n
            solver.add(z3.PbLe([(z3.And(X[i][a], X[j][a]), 1) for a in range(n)], 1))

    if config.require_crossing:
        for i in range(n):
            for j in range(i + 1, n):
                source = normalize_chord(i, j)
                possible_targets = [a for a in range(n) if a not in source]
                for a_idx, a in enumerate(possible_targets):
                    for b in possible_targets[a_idx + 1 :]:
                        target = normalize_chord(a, b)
                        if not chords_cross_in_order(source, target, natural_order):
                            solver.add(
                                z3.Not(
                                    z3.And(
                                        X[i][a],
                                        X[j][a],
                                        X[i][b],
                                        X[j][b],
                                    )
                                )
                            )

    if config.require_no_forward_ear_order:
        for seed in combinations(range(n), 3):
            outside = [vertex for vertex in range(n) if vertex not in seed]
            solver.add(
                z3.Or(
                    [
                        z3.PbLe([(X[vertex][target], 1) for target in seed], 2)
                        for vertex in outside
                    ]
                )
            )

    for center in stuck_vertices:
        solver.add(z3.PbLe([(X[center][j], 1) for j in stuck_vertices], 2))

    checked = 0
    rejection_counts: dict[str, int] = {}
    rejected_examples: list[dict[str, object]] = []
    while checked < config.max_models:
        check = solver.check()
        if check != z3.sat:
            status = "UNSAT" if checked == 0 else "EXHAUSTED"
            return MotifSearchResult(
                config=config,
                status=status,
                models_checked=checked,
                rejection_counts=rejection_counts,
                motif=None,
                rejected_examples=rejected_examples,
            )

        rows = _model_to_rows(solver.model(), X)
        checked += 1
        snapshot = pattern_filter_snapshot(
            rows,
            radius_node_limit=config.radius_node_limit,
            fragile_cover_max_size=config.fragile_cover_max_size,
            fragile_cover_max_examples=0,
        )
        reason = _candidate_rejection(rows, snapshot, config)
        if reason is None:
            motif = _analysis_payload(f"mined_n{n}_stuck{config.stuck_size}", rows, snapshot)
            motif["motif_search"] = {
                "stuck_vertices_forced": stuck_vertices,
                "models_checked": checked,
                "filters_required": filters_required_to_json(config),
            }
            return MotifSearchResult(
                config=config,
                status="FOUND",
                models_checked=checked,
                rejection_counts=rejection_counts,
                motif=motif,
                rejected_examples=rejected_examples,
            )

        rejection_counts[reason] = rejection_counts.get(reason, 0) + 1
        if len(rejected_examples) < 5:
            rejected_examples.append(
                {
                    "reason": reason,
                    "rows": rows,
                }
            )
        _block_model(solver, X, rows)

    return MotifSearchResult(
        config=config,
        status="MODEL_LIMIT",
        models_checked=checked,
        rejection_counts=rejection_counts,
        motif=None,
        rejected_examples=rejected_examples,
    )


def filters_required_to_json(config: MotifSearchConfig) -> dict[str, object]:
    return {
        "require_all_rows_cover": config.require_all_rows_cover,
        "require_adjacent_overlap": config.require_adjacent_overlap,
        "require_crossing": config.require_crossing,
        "require_no_odd_cycle": config.require_no_odd_cycle,
        "require_radius_pass": config.require_radius_pass,
        "require_fragile_cover": config.require_fragile_cover,
        "require_no_forward_ear_order": config.require_no_forward_ear_order,
        "fragile_cover_max_size": config.fragile_cover_max_size,
        "solver_seed": config.solver_seed,
    }


def search_result_to_json(result: MotifSearchResult) -> dict[str, object]:
    config = result.config
    return {
        "type": "bounded_stuck_motif_search",
        "status": result.status,
        "n": config.n,
        "stuck_size": config.stuck_size,
        "fixed_stuck_vertices": list(range(config.stuck_size)),
        "models_checked": result.models_checked,
        "max_models": config.max_models,
        "solver_seed": config.solver_seed,
        "rejection_counts": result.rejection_counts,
        "rejected_examples": result.rejected_examples,
        "filters_required": filters_required_to_json(config),
        "motif": result.motif,
        "semantics": (
            "Bounded SMT search with the stuck subset fixed to labels "
            "0..stuck_size-1. FOUND gives an incidence motif surviving the "
            "configured necessary filters; it is not a Euclidean realization "
            "certificate and does not settle Erdos Problem #97."
        ),
    }
