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


def test_sweep_can_run_geometry_smoke() -> None:
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
    assert item["geometry"]["status"] == "RAN"
    assert "eq_rms" in item["geometry"]
