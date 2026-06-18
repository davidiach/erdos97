from __future__ import annotations

import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

from erdos97.brp_boundary_probe import (
    Quad,
    assert_expected_counts,
    brp_seed_vertices,
    build_payload,
    exact_squared_distance,
    quad_to_json,
    seed_convexity_summary,
)


ROOT = Path(__file__).resolve().parents[1]


def test_seed_vertices_are_three_rotated_copies() -> None:
    vertices = brp_seed_vertices()

    assert [vertex.label for vertex in vertices[:4]] == ["A1", "A2", "A3", "A4"]
    assert [vertex.label for vertex in vertices[4:8]] == ["B1", "B2", "B3", "B4"]
    assert [vertex.label for vertex in vertices[8:]] == ["C1", "C2", "C3", "C4"]
    assert seed_convexity_summary(vertices)["strictly_convex_in_seed_order"] is True


def test_exact_distance_detects_rotation_symmetry() -> None:
    vertices = brp_seed_vertices()
    by_label = {vertex.label: vertex for vertex in vertices}

    assert exact_squared_distance(by_label["A1"], by_label["A2"]) == exact_squared_distance(
        by_label["B1"], by_label["B2"]
    )
    assert exact_squared_distance(by_label["A1"], by_label["B1"]) == Quad(
        Fraction(3000000)
    )


def test_payload_keeps_vertexization_gap_explicit() -> None:
    payload = build_payload()

    assert payload["schema"] == "erdos97.brp_boundary_vertexization_probe.v2"
    assert payload["trust"] == "NUMERICAL_GEOMETRIC_DIAGNOSTIC"
    assert payload["provenance"]["generator"] == "scripts/check_brp_boundary_probe.py"
    assert_expected_counts(payload)
    assert payload["summary"]["max_boundary_hits_on_seed_edges"] >= 4
    assert payload["summary"]["circles_with_at_least_four_seed_vertices"] == 0
    candidates = payload["synthetic_a5_scan"]["candidates"]
    assert {candidate["normal_side"] for candidate in candidates} == {"left", "right"}
    assert payload["synthetic_a5_scan"]["candidate_count"] == 36
    assert payload["synthetic_a5_scan"]["strictly_convex_candidate_count"] == 0
    assert payload["synthetic_a5_scan"]["candidates_with_at_least_four_vertices"] == 0
    preflight = payload["lemma31_preflight"]
    assert preflight["status"] == "LEMMA31_ROLE_PREFLIGHT_ONLY_A5_NOT_CONSTRUCTED"
    assert preflight["role_mapping"] == {
        "A": "A3",
        "B": "A4",
        "C": "B1",
        "D": "B2",
        "candidate_C1_name_in_paper_construction": "A5",
    }
    assert preflight["role_order"]["strictly_convex_counterclockwise"] is True
    assert preflight["role_order"]["clockwise_target_without_C1_verified"] is True
    assert preflight["angle_ABC"]["acute"] is True
    assert preflight["angle_ABC"]["degrees"] == 87.7725247
    assert preflight["bprime_neighbourhood_budget"]["default_tau"] == "1/100"
    assert preflight["bprime_neighbourhood_budget"]["default_tau_inside_ceiling"] is True
    assert (
        preflight["bprime_neighbourhood_budget"]["C_outside_default_S_Bprime"]
        is True
    )
    a5_scan = payload["lemma31_a5_constraint_scan"]
    assert a5_scan["status"] == "SAMPLED_NUMERICAL_A5_CONSTRAINT_PROBE"
    assert a5_scan["parameterization"]["sample_count"] == 2000
    assert a5_scan["filter_counts"] == {
        "D_C_A5_B_A_extreme_clockwise": 700,
        "plus_A5_outside_S_A": 290,
        "plus_angle_A_B_A5_acute": 3,
        "plus_segment_C_A5_intersects_default_S_Bprime_twice": 1,
        "plus_rotated_15gon_strictly_convex": 1,
    }
    assert a5_scan["individual_condition_counts"] == {
        "D_C_A5_B_A_extreme_clockwise": 700,
        "A5_outside_S_A": 590,
        "angle_A_B_A5_acute": 1413,
        "segment_C_A5_intersects_default_S_Bprime_twice": 41,
    }
    assert len(a5_scan["sampled_witnesses"]) == 1
    witness = a5_scan["sampled_witnesses"][0]
    assert witness["t"] == "3/125"
    assert witness["normal_offset"] == "-1/200"
    assert witness["normal_side"] == "right"
    assert witness["lemma31_N1_bullets"] == {
        "D_C_A5_B_A_extreme_clockwise": True,
        "A5_outside_S_A": True,
        "angle_A_B_A5_acute": True,
        "segment_C_A5_intersects_default_S_Bprime_twice": True,
        "S_Bprime_roots_on_segment_C_A5": [0.86294581, 0.995615477],
        "largest_clockwise_turn_area2": -0.026807931,
    }
    assert witness["rotated_15gon"] == {
        "strictly_convex": True,
        "min_turn_area2": 0.026807931,
        "max_vertex_hits": 2,
        "max_boundary_hits": 6,
        "circles_with_at_least_four_vertices": 0,
        "circles_with_at_least_four_boundary_hits": 87,
    }
    assert "counterexample to Erdos Problem #97" in payload["does_not_claim"]
    assert "the A5 insertion" in str(payload["source"]["not_modeled"])


def test_quad_display_is_stable() -> None:
    assert quad_to_json(Quad(Fraction(3))) == "3"
    assert quad_to_json(Quad(Fraction(0), Fraction(-2, 3))) == "-2/3*sqrt3"
    assert quad_to_json(Quad(Fraction(5, 2), Fraction(7, 3))) == "5/2 + 7/3*sqrt3"


def test_cli_write_check_roundtrip(tmp_path: Path) -> None:
    artifact = tmp_path / "brp_probe.json"

    write = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--artifact",
            str(artifact),
            "--write",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert write.returncode == 0, write.stderr
    stored = json.loads(artifact.read_text(encoding="utf-8"))
    assert stored["summary"]["seed_vertex_count"] == 12

    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--artifact",
            str(artifact),
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr


def test_cli_default_artifact_check_is_reproducible() -> None:
    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr


def test_cli_check_tolerates_tiny_float_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "brp_probe.json"
    payload = build_payload()
    payload["convexity"]["min_turn_area2"] += 1e-12
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--artifact",
            str(artifact),
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode == 0, check.stderr


def test_cli_check_rejects_material_float_drift(tmp_path: Path) -> None:
    artifact = tmp_path / "brp_probe.json"
    payload = build_payload()
    payload["convexity"]["min_turn_area2"] += 1e-4
    artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    check = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--artifact",
            str(artifact),
            "--check",
            "--assert-expected",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert check.returncode != 0
    assert "$.convexity.min_turn_area2" in check.stderr


def test_cli_write_check_modes_are_exclusive(tmp_path: Path) -> None:
    artifact = tmp_path / "brp_probe.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_brp_boundary_probe.py",
            "--artifact",
            str(artifact),
            "--write",
            "--check",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert result.returncode != 0
    assert "not allowed with argument" in result.stderr
