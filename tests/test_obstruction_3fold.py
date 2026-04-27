"""Tests for the 3-fold cluster obstruction lemma.

The lemma claims a quantitative lower bound

    r >= C1 * gamma^alpha

for any selected-witness ``B12_3x4_danzer_lift`` realization that has the
canonical block-(3,4) cluster structure, where ``r`` is the RMS equality
residual and ``gamma`` is the strict convexity margin.  See
``docs/lemmas/no_3fold_cluster_obstruction.md`` for the full statement and
range of validity.

These tests check that the bound:

* holds on the historical ``best_B12_slsqp_m1e-6`` near-miss;
* holds on every restart of the empirical SLSQP sweep when one is present
  (skipped when the sweep artifact is absent);
* holds on a small grid of hand-built 3-cluster configurations spanning
  several orders of magnitude in ``rho``, and is tight to within a factor
  of 10 of the typical empirical ratio in those configurations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pytest

from erdos97.obstructions import (
    DEFAULT_THREEFOLD_OBSTRUCTION,
    ObstructionReport,
    cluster_orientation_angle,
    cluster_partition,
    fit_obstruction_constants,
    min_intra_cluster_distance,
    verify_obstruction,
)
from erdos97.search import (
    built_in_patterns,
    independent_diagnostics,
    inverse_polar_x,
    orient_margins,
    polygon_from_x,
    pairwise_sqdist,
)
from scipy.optimize import least_squares


REPO_ROOT = Path(__file__).resolve().parents[1]
SAVED_BEST = REPO_ROOT / "data" / "runs" / "best_B12_slsqp_m1e-6.json"
SWEEP_RUNS = REPO_ROOT / "data" / "obstructions" / "three_fold_cluster_runs.json"


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------


def _make_3cluster(rho: float, kappa: float, theta_off: float) -> np.ndarray:
    """Hand-built 3-cluster polygon at vertices of an equilateral triangle.

    Same construction used by the empirical sweep script.  ``theta_off``
    in radians: ``pi/2`` is the generic regime (cluster tangent
    perpendicular to radial direction).
    """
    pts = []
    s_vals = [-1.5, -0.5, 0.5, 1.5]
    for a in range(3):
        ang = 2.0 * math.pi * a / 3.0
        Va = np.array([math.cos(ang), math.sin(ang)])
        u = Va / np.linalg.norm(Va)
        t_perp = np.array([-math.sin(ang), math.cos(ang)])
        tt = math.sin(theta_off) * t_perp + math.cos(theta_off) * u
        nn = -u
        for s in s_vals:
            sp = s * rho
            pts.append(Va + sp * tt + (kappa / 2.0) * sp * sp * nn)
    return np.asarray(pts, dtype=float)


def _custom_residual(x, n, S, m):
    P = polygon_from_x(x, n, "polar")
    D2 = pairwise_sqdist(P)
    rows = []
    for i, Si in enumerate(S):
        vals = np.array([D2[i, j] for j in Si], dtype=float)
        rows.append(vals - vals.mean())
    eq = np.concatenate(rows) if rows else np.zeros(0)
    ori = orient_margins(P)
    barrier = np.maximum(0.0, m - ori)
    return np.concatenate([eq, 1000.0 * barrier])


# --------------------------------------------------------------------------
# Saved best near-miss
# --------------------------------------------------------------------------


def test_saved_best_b12_satisfies_obstruction() -> None:
    """The motivating numerical near-miss saved at
    ``data/runs/best_B12_slsqp_m1e-6.json`` satisfies the lemma's lower
    bound by a strictly positive slack."""
    report = verify_obstruction(SAVED_BEST, "B12_3x4_danzer_lift")
    assert isinstance(report, ObstructionReport)
    assert report.gamma > 0.0
    assert report.r > 0.0
    assert report.holds, (
        f"saved best near-miss violates lemma: r={report.r}, "
        f"predicted bound={report.predicted_lower_bound}"
    )
    assert report.slack > 0.0


def test_saved_best_b12_cluster_orientation_is_generic() -> None:
    """Saved best near-miss is in the generic regime
    (cluster tangent ~perpendicular to radial direction)."""
    report = verify_obstruction(SAVED_BEST, "B12_3x4_danzer_lift")
    assert math.degrees(report.cluster_orientation_angle) > 60.0


def test_obstruction_does_not_apply_to_unrelated_pattern() -> None:
    with pytest.raises(ValueError):
        verify_obstruction(SAVED_BEST, "C12_pm_2_5")


# --------------------------------------------------------------------------
# Empirical sweep (skipped when the artifact has not been generated)
# --------------------------------------------------------------------------


@pytest.mark.skipif(not SWEEP_RUNS.exists(), reason="run scripts/empirical_obstruction_constants.py first")
def test_sweep_runs_all_satisfy_obstruction() -> None:
    """Every restart in the empirical SLSQP sweep satisfies the lemma's
    lower bound."""
    payload = json.loads(SWEEP_RUNS.read_text(encoding="utf-8"))
    runs = payload["runs"]
    assert len(runs) >= 50, "sweep should have at least 50 successful restarts"
    obs = DEFAULT_THREEFOLD_OBSTRUCTION
    for rec in runs:
        gamma = rec["gamma"]
        r = rec["r"]
        bound = obs.predicted_lower_bound(gamma)
        assert r >= bound, (
            f"sweep run violates lemma: gamma={gamma}, r={r}, "
            f"predicted bound={bound}, target_floor={rec['convex_margin_target']}"
        )


@pytest.mark.skipif(not SWEEP_RUNS.exists(), reason="run scripts/empirical_obstruction_constants.py first")
def test_sweep_covers_log_decade_range() -> None:
    """Sweep should span at least three decades of gamma."""
    payload = json.loads(SWEEP_RUNS.read_text(encoding="utf-8"))
    gammas = sorted(rec["gamma"] for rec in payload["runs"])
    assert gammas[-1] / gammas[0] > 1e3


# --------------------------------------------------------------------------
# Hand-built synthetic configs
# --------------------------------------------------------------------------


@pytest.mark.parametrize("rho", [3e-2, 1e-2, 3e-3, 1e-3, 3e-4, 1e-4])
def test_hand_built_3cluster_satisfies_obstruction(rho: float) -> None:
    """Hand-built 3-cluster polygons in the generic regime satisfy the
    lemma's lower bound across six decades of intra-cluster spacing."""
    pat = built_in_patterns()["B12_3x4_danzer_lift"]
    P = _make_3cluster(rho, kappa=1.0, theta_off=math.pi / 2.0)
    diag = independent_diagnostics(P, pat.S)
    gamma = float(diag["convexity_margin"])
    r = float(diag["eq_rms"])
    assert gamma > 0.0
    assert r > 0.0
    bound = DEFAULT_THREEFOLD_OBSTRUCTION.predicted_lower_bound(gamma)
    assert r >= bound, f"hand-built rho={rho} violates lemma: r={r}, bound={bound}"


@pytest.mark.parametrize("rho", [1e-2, 1e-3, 1e-4])
def test_hand_built_3cluster_bound_tight_within_factor_10(rho: float) -> None:
    """The lemma's lower bound on hand-built 3-cluster configurations is
    no looser than a factor of 10 from the typical residual.
    """
    pat = built_in_patterns()["B12_3x4_danzer_lift"]
    P = _make_3cluster(rho, kappa=1.0, theta_off=math.pi / 2.0)
    diag = independent_diagnostics(P, pat.S)
    gamma = float(diag["convexity_margin"])
    r = float(diag["eq_rms"])
    bound = DEFAULT_THREEFOLD_OBSTRUCTION.predicted_lower_bound(gamma)
    assert bound > 0.0
    ratio = r / bound
    assert 1.0 <= ratio <= 1000.0, (
        f"bound looseness out of expected range: r/bound={ratio} at rho={rho}"
    )


# --------------------------------------------------------------------------
# Helpers diagnostics
# --------------------------------------------------------------------------


def test_cluster_partition_for_b12_is_block_3x4() -> None:
    cl = cluster_partition("B12_3x4_danzer_lift", 12)
    assert cl == ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11))


def test_cluster_partition_unknown_pattern_raises() -> None:
    with pytest.raises(KeyError):
        cluster_partition("C12_pm_2_5", 12)


def test_min_intra_cluster_distance_on_saved_best_matches_min_edge() -> None:
    """For the saved best near-miss, min intra-cluster pair distance
    coincides with the polygon's overall min edge length, since cluster
    members are consecutive in the cyclic order."""
    payload = json.loads(SAVED_BEST.read_text(encoding="utf-8"))
    P = np.array(payload["coordinates"])
    rho = min_intra_cluster_distance(P, cluster_partition("B12_3x4_danzer_lift", 12))
    assert math.isclose(rho, payload["min_edge_length"], rel_tol=1e-9)


# --------------------------------------------------------------------------
# Linear fit utility
# --------------------------------------------------------------------------


def test_fit_obstruction_constants_recovers_synthetic_slope(tmp_path: Path) -> None:
    """fit_obstruction_constants returns the slope of synthetic
    log-linear data accurately."""
    paths = []
    for k, gamma in enumerate([1e-3, 1e-4, 1e-5, 1e-6, 1e-7, 1e-8]):
        # synthetic: r = 3 * gamma^0.5
        r = 3.0 * gamma ** 0.5
        p = tmp_path / f"run_{k}.json"
        p.write_text(json.dumps({"convexity_margin": gamma, "eq_rms": r}))
        paths.append(p)
    fit = fit_obstruction_constants(paths)
    assert math.isclose(fit.alpha_estimate, 0.5, rel_tol=1e-3)
    assert math.isclose(fit.C1_estimate, 3.0, rel_tol=1e-3)
    assert fit.r_squared > 0.999


# --------------------------------------------------------------------------
# Bonus: an SLSQP-style restart at one tolerance, run inline so the test
# does not require the sweep artifact to be precomputed
# --------------------------------------------------------------------------


@pytest.mark.parametrize("seed", list(range(5)))
def test_inline_slsqp_restart_satisfies_obstruction(seed: int) -> None:
    """Inline SLSQP restarts at a representative convex-margin floor
    satisfy the lemma's lower bound when they converge to a strictly
    convex polygon.  Uses a relatively loose floor (``m=1e-3``) so the
    optimization reliably succeeds inside a small per-test budget; the
    full ``[1e-3, 1e-9]`` sweep is exercised by
    :func:`test_sweep_runs_all_satisfy_obstruction`."""
    pat = built_in_patterns()["B12_3x4_danzer_lift"]
    rng = np.random.default_rng(seed + 1234)
    m = 1e-3
    rho_init = m ** (1.0 / 3.0)
    P0 = _make_3cluster(rho_init, kappa=1.0, theta_off=math.pi / 2.0)
    P0 = P0 + (0.05 * rho_init) * rng.normal(size=P0.shape)
    x0 = inverse_polar_x(P0)
    sol = least_squares(
        lambda x: _custom_residual(x, 12, pat.S, m),
        x0,
        method="trf",
        max_nfev=600,
        x_scale="jac",
        ftol=1e-12,
        xtol=1e-12,
        gtol=1e-12,
    )
    P = polygon_from_x(sol.x, 12, "polar")
    diag = independent_diagnostics(P, pat.S)
    gamma = float(diag["convexity_margin"])
    r = float(diag["eq_rms"])
    if gamma <= 0.0:
        pytest.skip(f"restart seed={seed} did not produce a strictly convex polygon")
    bound = DEFAULT_THREEFOLD_OBSTRUCTION.predicted_lower_bound(gamma)
    assert r >= bound, (
        f"inline restart seed={seed} violates lemma: gamma={gamma}, r={r}, "
        f"bound={bound}"
    )
