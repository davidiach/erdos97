from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np

from erdos97.interval_verify import verify_interval_json


ROOT = Path(__file__).resolve().parents[1]
B12 = ROOT / "data" / "runs" / "best_B12_slsqp_m1e-6.json"


def write_candidate(path: Path, coordinates: list[list[float]], rows: list[list[int]], **extra: object) -> None:
    payload = {"coordinates": coordinates, "S": rows, **extra}
    path.write_text(json.dumps(payload), encoding="utf-8")


def test_b12_near_miss_is_not_interval_certified() -> None:
    result = verify_interval_json(B12)

    assert result["ok"] is False
    assert result["failure_mode"] == "floating_near_miss"
    assert result["convexity_certified"] is True
    assert result["distance_equalities_certified"] is False
    assert result["residual_bounds"]["definite_nonzero_residuals"] > 0
    assert "counterexample to Erdos Problem #97" in result["does_not_claim"]


def test_negative_interval_parameters_are_malformed() -> None:
    result = verify_interval_json(B12, coord_abs_radius=-1e-12, coord_rel_radius=0.0)

    assert result["ok"] is False
    assert result["failure_mode"] == "malformed"
    assert result["claim_strength"] == "MALFORMED_INPUT"
    assert "coord_abs_radius must be nonnegative" in result["validation_errors"][0]


def test_wider_coordinate_radius_documents_uncertified_convexity() -> None:
    result = verify_interval_json(B12, coord_abs_radius=1e-6, coord_rel_radius=0.0)

    assert result["ok"] is False
    assert result["failure_mode"] == "uncertified"
    assert result["convexity_certified"] is False
    assert result["claim_strength"] == "NUMERICAL_EVIDENCE_OR_NEAR_MISS_NOT_A_COUNTEREXAMPLE"
    assert "counterexample to Erdos Problem #97" in result["does_not_claim"]


def test_malformed_candidate_is_reported(tmp_path: Path) -> None:
    candidate = tmp_path / "bad.json"
    write_candidate(candidate, [[0.0, 0.0], [1.0, 0.0]], [[1, 1, 1, 1], [0, 0, 0, 0]])

    result = verify_interval_json(candidate)

    assert result["ok"] is False
    assert result["failure_mode"] == "malformed"
    assert result["claim_strength"] == "MALFORMED_INPUT"
    assert result["validation_errors"]


def test_exact_coordinates_do_not_require_float_coordinates(tmp_path: Path) -> None:
    candidate = tmp_path / "exact.json"
    n = 9
    payload = {
        "coordinates_exact": [
            [str(i), str(i * i)]
            for i in range(n)
        ],
        "S": [
            sorted((i + offset) % n for offset in (-4, -2, 2, 4))
            for i in range(n)
        ],
    }
    candidate.write_text(json.dumps(payload), encoding="utf-8")

    result = verify_interval_json(candidate)

    assert result["ok"] is False
    assert result["failure_mode"] == "exact_algebraic_rejected"
    assert result["claim_strength"] == "EXACT_OR_ALGEBRAIC_INPUT_REJECTED"


def test_convex_float_without_equalities_is_not_certified(tmp_path: Path) -> None:
    candidate = tmp_path / "c9.json"
    n = 9
    coordinates = [
        [float(np.cos(2.0 * np.pi * i / n)), float(np.sin(2.0 * np.pi * i / n))]
        for i in range(n)
    ]
    rows = [
        sorted((i + offset) % n for offset in (-4, -2, 2, 4))
        for i in range(n)
    ]
    write_candidate(candidate, coordinates, rows)

    result = verify_interval_json(candidate)

    assert result["ok"] is False
    assert result["failure_mode"] == "interval_convexity_certified_equality_uncertified"
    assert result["convexity_certified"] is True
    assert result["distance_equalities_certified"] is False


def test_interval_verify_cli_check_rejects_b12() -> None:
    result = subprocess.run(
        [sys.executable, "scripts/interval_verify_candidate.py", str(B12), "--check"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["failure_mode"] == "floating_near_miss"


def test_interval_verify_cli_reports_negative_radius_as_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/interval_verify_candidate.py",
            str(B12),
            "--coord-abs-radius=-1e-12",
            "--coord-rel-radius",
            "0",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["failure_mode"] == "malformed"
    assert payload["claim_strength"] == "MALFORMED_INPUT"
