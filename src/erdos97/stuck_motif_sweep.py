"""Sweep bounded stuck-motif searches over small parameter grids."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from erdos97.search import PatternInfo, result_to_json as geometry_result_to_json, search_pattern
from erdos97.stuck_motif_search import (
    MotifSearchConfig,
    mine_stuck_motif,
    search_result_to_json as motif_result_to_json,
)


@dataclass(frozen=True)
class SweepConfig:
    n_values: Sequence[int]
    stuck_sizes: Sequence[int]
    max_models: int = 100
    solver_seed: int = 0
    variable_prefix: str = "sweep"
    require_no_forward_ear_order: bool = False
    radius_node_limit: int = 100_000
    fragile_cover_max_size: int | None = None
    run_geometry: bool = False
    geometry_optimizer: Literal["trf", "slsqp"] = "trf"
    geometry_mode: Literal["polar", "direct", "support"] = "polar"
    geometry_restarts: int = 3
    geometry_max_nfev: int = 300
    geometry_margin: float = 1e-3
    geometry_seed: int = 0


def _geometry_summary(
    motif: dict[str, object],
    config: SweepConfig,
) -> dict[str, object]:
    rows = motif.get("selected_rows")
    if not isinstance(rows, list):
        return {
            "status": "SKIPPED_NO_SELECTED_ROWS",
            "success": False,
        }

    pattern = PatternInfo(
        name=str(motif["pattern"]),
        n=int(motif["n"]),
        S=[[int(label) for label in row] for row in rows],
        family="mined",
        formula="stuck motif sweep",
        notes="numerical smoke search only",
    )
    try:
        result = search_pattern(
            pattern,
            mode=config.geometry_mode,
            restarts=config.geometry_restarts,
            seed=config.geometry_seed,
            max_nfev=config.geometry_max_nfev,
            optimizer=config.geometry_optimizer,
            margin=config.geometry_margin,
        )
    except RuntimeError as exc:
        return {
            "status": "OPTIMIZER_FAILED",
            "success": False,
            "message": str(exc),
            "interpretation": (
                "Numerical optimizer failure is not an exact obstruction or a "
                "counterexample."
            ),
        }

    data = geometry_result_to_json(result)
    return {
        "status": "RAN",
        "success": bool(data["success"]),
        "mode": data["mode"],
        "loss": data["loss"],
        "eq_rms": data["eq_rms"],
        "max_spread": data["max_spread"],
        "convexity_margin": data["convexity_margin"],
        "min_edge_length": data["min_edge_length"],
        "min_pair_distance": data["min_pair_distance"],
        "elapsed_sec": data["elapsed_sec"],
        "interpretation": "NUMERICAL_EVIDENCE only.",
    }


def sweep_stuck_motifs(config: SweepConfig) -> dict[str, object]:
    """Run a bounded stuck-motif sweep and return JSON-ready data."""

    items: list[dict[str, object]] = []
    for n, stuck_size in (
        (int(n), int(stuck_size))
        for n in config.n_values
        for stuck_size in config.stuck_sizes
    ):
        resolved_prefix = f"{config.variable_prefix}_{n}_{stuck_size}_{config.solver_seed}"
        result = mine_stuck_motif(
            MotifSearchConfig(
                n=n,
                stuck_size=stuck_size,
                max_models=config.max_models,
                solver_seed=config.solver_seed,
                variable_prefix=resolved_prefix,
                radius_node_limit=config.radius_node_limit,
                require_no_forward_ear_order=config.require_no_forward_ear_order,
                fragile_cover_max_size=config.fragile_cover_max_size,
            )
        )
        payload = motif_result_to_json(result)
        motif = payload.get("motif")
        geometry = None
        if config.run_geometry and isinstance(motif, dict):
            geometry = _geometry_summary(motif, config)
        items.append(
            {
                "n": int(n),
                "stuck_size": int(stuck_size),
                "status": payload["status"],
                "models_checked": payload["models_checked"],
                "rejection_counts": payload["rejection_counts"],
                "motif_pattern": motif.get("pattern") if isinstance(motif, dict) else None,
                "motif_forward_ear_order": (
                    motif["forward_ear_order"]["exists"] if isinstance(motif, dict) else None
                ),
                "motif_minimal_stuck_size": (
                    motif["stuck_search"]["minimal_size"] if isinstance(motif, dict) else None
                ),
                "variable_prefix": resolved_prefix,
                "radius_status": (
                    motif["filters"]["radius_propagation"]["status"]
                    if isinstance(motif, dict)
                    else None
                ),
                "geometry": geometry,
                "motif": motif,
            }
        )

    return {
        "type": "bounded_stuck_motif_sweep",
        "config": {
            "n_values": [int(n) for n in config.n_values],
            "stuck_sizes": [int(size) for size in config.stuck_sizes],
            "max_models": config.max_models,
            "solver_seed": config.solver_seed,
            "variable_prefix": config.variable_prefix,
            "require_no_forward_ear_order": config.require_no_forward_ear_order,
            "run_geometry": config.run_geometry,
            "geometry_optimizer": config.geometry_optimizer,
            "geometry_mode": config.geometry_mode,
            "geometry_restarts": config.geometry_restarts,
            "geometry_max_nfev": config.geometry_max_nfev,
            "geometry_margin": config.geometry_margin,
            "geometry_seed": config.geometry_seed,
        },
        "items": items,
        "summary": {
            "total": len(items),
            "found": sum(1 for item in items if item["status"] == "FOUND"),
            "unique_found_cyclic_dihedral_fingerprints": len(
                {
                    item["motif"]["fingerprint"]["cyclic_dihedral_sha256"]
                    for item in items
                    if isinstance(item.get("motif"), dict)
                }
            ),
            "exhausted": sum(1 for item in items if item["status"] == "EXHAUSTED"),
            "model_limit": sum(1 for item in items if item["status"] == "MODEL_LIMIT"),
            "unsat": sum(1 for item in items if item["status"] == "UNSAT"),
        },
        "semantics": (
            "Bounded search diagnostics only. FOUND motifs are fixed-selection "
            "incidence targets surviving configured necessary filters, not "
            "Euclidean realization certificates."
        ),
    }
