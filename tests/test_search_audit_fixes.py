"""Regression controls for the 2026-09-05 search audit (not k=4 evidence)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from erdos97 import search
from erdos97.search_preflight import chords_cross, preflight, validate_rows


def three_witness_control():
    """Exact radical seeds evaluated in double precision; three witnesses only."""
    omega = complex(-0.5, np.sqrt(3) / 2)
    seeds = [2j, (-8991 * np.sqrt(3) - 26503j) / 10927,
             (-10753 * np.sqrt(3) - 44665j) / 18529]
    points = [omega**k * z for k in range(3) for z in seeds]
    order = sorted(range(9), key=lambda j: np.angle(points[j]))
    position = {old: new for new, old in enumerate(order)}
    rows = []
    for old in order:
        k, j = divmod(old, 3)
        extra = [3 * ((k + 1) % 3) + 1, 3 * ((k + 1) % 3) + 2, 3 * k][j]
        witnesses = [3 * ((k + 1) % 3) + j, 3 * ((k + 2) % 3) + j, extra]
        rows.append([position[w] for w in witnesses])
    p = np.array([[points[j].real, points[j].imag] for j in order])
    return search.normalize_points(p), rows


def test_exact_control_is_not_pushed_by_feasibility_penalties():
    p, rows = three_witness_control()
    assert search.convexity_margin(p) > 0.08
    assert search.min_pair_distance(p) > 0.16
    eq = search.equality_residual(p.ravel(), 9, rows, "direct")
    assert np.max(np.abs(eq)) < 2e-14
    residual = search.residual_vector(p.ravel(), 9, rows, "direct", search.LossWeights())
    assert np.array_equal(residual[len(eq):], np.zeros(len(residual) - len(eq)))
    assert float(residual @ residual) < 1e-25
    legacy = search.residual_vector(p.ravel(), 9, rows, "direct", search.LossWeights(),
                                    penalty="legacy-softplus")
    assert float(legacy @ legacy) > 0.03
    # Every nearby feasible perturbation has nonnegative loss, unlike the old
    # objective, which has a geometry-penalty gradient even at the exact seed.
    rng = np.random.default_rng(970905)
    for _ in range(8):
        q = p + rng.normal(size=p.shape) * 1e-4
        other = search.residual_vector(q.ravel(), 9, rows, "direct", search.LossWeights())
        assert float(other @ other) > float(residual @ residual)


def test_hinge_and_legacy_penalty_contracts():
    values = np.array([-1.0, 0.0, 1.0])
    assert np.array_equal(search.violation_penalty(values), [0, 0, 1])
    assert np.all(search.violation_penalty(values, "legacy-softplus") > 0)
    with pytest.raises(ValueError, match="unknown penalty"):
        search.violation_penalty(values, "typo")


def test_default_pattern_obstruction_is_recomputed_without_metadata():
    pattern = search.circulant_pattern(12, [-5, -2, 2, 5], "untrusted_name")
    report = preflight(pattern.n, pattern.S)
    assert report["reason"] == "crossing_bisector"
    assert report["evidence"] == {"centers": [0, 3], "witnesses": [5, 10]}
    assert report["scope"] == "selected rows in supplied cyclic order only"


def test_crossing_changes_with_order_and_is_rotation_reversal_invariant():
    assert not chords_cross(12, 0, 3, 5, 10)
    assert chords_cross(12, 0, 5, 3, 10)
    for shift in range(12):
        for sign in (1, -1):
            labels = [(sign * j + shift) % 12 for j in (0, 5, 3, 10)]
            assert chords_cross(12, *labels)
    assert not chords_cross(12, 0, 5, 0, 10)


def test_metric_inverse_detects_sidon_pattern_without_two_overlaps():
    pattern = search.circulant_pattern(13, [1, 2, 4, 10])
    assert all(len(set(pattern.S[a]) & set(pattern.S[b])) == 1
               for a in range(13) for b in range(a))
    assert preflight(pattern.n, pattern.S)["reason"] == "kalmanson_inverse"


def test_preflight_never_claims_realizability_for_a_survivor():
    # Repo's scalable negative control k=8; not a planar realization.
    pattern = search.circulant_pattern(47, [9, 19, 25, 40])
    report = preflight(pattern.n, pattern.S)
    assert report["status"] == "not_obstructed_by_preflight"
    assert report["realization_certified"] is False


def test_obstructed_search_never_calls_optimizer(monkeypatch):
    def forbidden(*args, **kwargs):
        pytest.fail("optimizer called for an exactly obstructed pattern")
    monkeypatch.setattr(search, "least_squares", forbidden)
    monkeypatch.setattr(search, "minimize", forbidden)
    pattern = search.built_in_patterns()["C12_pm_2_5"]
    for optimizer in ("trf", "slsqp"):
        with pytest.raises(ValueError, match="exact preflight obstruction"):
            search.search_pattern(pattern, optimizer=optimizer)
    with pytest.raises(ValueError, match="exact preflight obstruction"):
        search.slsqp_search(pattern, "direct", 1, 0, 1, 1e-3)


def test_feasible_restart_wins_even_with_larger_equality_loss(monkeypatch):
    pattern = search.circulant_pattern(9, [-4, -2, 2, 4])
    angle = np.arange(9) * 2 * np.pi / 9
    feasible = np.column_stack((np.cos(angle), np.sin(angle))).ravel()
    degenerate = np.zeros(18)
    choices = iter([feasible, degenerate])
    monkeypatch.setattr(search, "least_squares", lambda *a, **k: SimpleNamespace(
        x=next(choices), fun=np.zeros(1), success=True, message="test"))
    with pytest.warns(RuntimeWarning, match="obstructed benchmark"):
        result = search.search_pattern(pattern, mode="direct", restarts=2,
                                       allow_obstructed=True,
                                       weights=search.LossWeights(convex=0, edge=0, pair=0))
    assert result.feasible_at_margin
    assert result.benchmark_only
    assert result.eq_rms > 0.1
    assert result.objective == "feasibility_hinge"
    assert result.loss > 0


@pytest.mark.parametrize("value", [0, -1, float("nan"), float("inf")])
def test_invalid_margin_fails_before_search(value):
    with pytest.raises(ValueError, match="margin"):
        search.search_pattern(search.built_in_patterns()["C12_pm_2_5"], margin=value)


def test_override_does_not_bypass_malformed_rows():
    pattern = search.circulant_pattern(9, [-4, -2, 2, 4])
    pattern.S[0] = [1, 1, 2, 3]
    with pytest.raises(ValueError, match="distinct other labels"):
        search.search_pattern(pattern, allow_obstructed=True)
    with pytest.raises(ValueError, match="integer"):
        validate_rows(True, [])


def run_cli(*args):
    return subprocess.run([sys.executable, "-m", "erdos97.search", *args],
                          text=True, capture_output=True, check=False)


def test_no_implicit_impossible_default():
    result = run_cli()
    assert result.returncode == 2
    assert "select --pattern-json or an explicit --pattern" in result.stderr


def test_supplied_pattern_cli_preflight(tmp_path: Path):
    path = tmp_path / "pattern.json"
    pattern = search.circulant_pattern(12, [-5, -2, 2, 5])
    path.write_text(json.dumps({"n": 12, "S": pattern.S}))
    result = run_cli("--pattern-json", str(path), "--preflight-only")
    assert result.returncode == 1
    assert json.loads(result.stdout)["reason"] == "crossing_bisector"


def test_boolean_heuristics_are_opt_in():
    import inspect
    defaults = inspect.signature(search.z3_incidence_search).parameters
    assert defaults["balance_indegree"].default is False
    assert defaults["symmetry_break"].default is False


def test_json_wrapper_reports_exact_preflight_without_traceback(tmp_path):
    path = tmp_path / "pattern.json"
    pattern = search.circulant_pattern(12, [-5, -2, 2, 5])
    path.write_text(json.dumps({"n": 12, "S": pattern.S}))
    for extra in ([], ["--preflight-only"]):
        result = subprocess.run([sys.executable, "scripts/search_pattern_json.py",
                                 "--input", str(path), "--json", *extra],
                                text=True, capture_output=True, check=False)
        assert result.returncode == 1
        assert json.loads(result.stdout)["reason"] == "crossing_bisector"
        assert "Traceback" not in result.stderr


def test_json_wrapper_records_explicit_benchmark(tmp_path):
    path = tmp_path / "pattern.json"
    pattern = search.circulant_pattern(12, [-5, -2, 2, 5])
    path.write_text(json.dumps({"S": pattern.S}))
    result = subprocess.run([sys.executable, "scripts/search_pattern_json.py",
                             "--input", str(path), "--json", "--allow-obstructed",
                             "--optimizer", "trf", "--restarts", "1", "--max-nfev", "1"],
                            text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr
    data = json.loads(result.stdout)
    assert data["benchmark_only"] is True
    assert data["preflight"]["status"] == "obstructed"
    assert data["objective"] == "feasibility_hinge"


def test_feasibility_does_not_relax_requested_margin():
    margin = 1e-3
    diag = dict(convexity_margin=margin, min_edge_length=1.0, min_pair_distance=1.0)
    assert search.feasible_at_margin(diag, margin)
    diag["convexity_margin"] = np.nextafter(margin, 0.0)
    assert not search.feasible_at_margin(diag, margin)
