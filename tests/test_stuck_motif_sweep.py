from __future__ import annotations

from erdos97.stuck_motif_sweep import SweepConfig, sweep_stuck_motifs


def test_sweep_finds_motif_in_n9() -> None:
    payload = sweep_stuck_motifs(
        SweepConfig(
            n_values=[9],
            stuck_sizes=[4],
            max_models=5,
            solver_seed=0,
        )
    )

    assert payload["summary"]["found"] == 1
    item = payload["items"][0]
    assert item["status"] == "FOUND"
    assert item["radius_status"] == "PASS_ACYCLIC_CHOICE"


def test_sweep_skips_exactly_obstructed_geometry(monkeypatch) -> None:
    def forbidden(*args, **kwargs):
        raise AssertionError("optimizer called for an exactly obstructed motif")

    monkeypatch.setattr("erdos97.stuck_motif_sweep.search_pattern", forbidden)
    payload = sweep_stuck_motifs(
        SweepConfig(
            n_values=[9],
            stuck_sizes=[4],
            max_models=5,
            run_geometry=True,
            geometry_restarts=1,
            geometry_max_nfev=50,
            geometry_optimizer="trf",
        )
    )

    item = payload["items"][0]
    assert item["status"] == "FOUND"
    assert item["geometry"]["status"] == "SKIPPED_EXACT_PREFLIGHT_OBSTRUCTION"
    assert item["geometry"]["preflight"]["reason"] == "kalmanson_zero"
    assert item["geometry"]["preflight"]["realization_certified"] is False


def test_sweep_records_stable_item_variable_prefix() -> None:
    sweep = sweep_stuck_motifs(
        SweepConfig(
            n_values=[9],
            stuck_sizes=[4],
            max_models=5,
            solver_seed=0,
            variable_prefix="sweep_contract",
        )
    )

    assert sweep["config"]["variable_prefix"] == "sweep_contract"
    assert sweep["config"]["require_no_rectangle_trap"] is True
    assert sweep["items"][0]["variable_prefix"] == "sweep_contract_9_4_0"
    assert sweep["items"][0]["status"] == "FOUND"
