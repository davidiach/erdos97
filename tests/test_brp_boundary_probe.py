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

    assert payload["schema"] == "erdos97.brp_boundary_vertexization_probe.v1"
    assert payload["trust"] == "NUMERICAL_GEOMETRIC_DIAGNOSTIC"
    assert_expected_counts(payload)
    assert payload["summary"]["max_boundary_hits_on_seed_edges"] >= 4
    assert payload["summary"]["circles_with_at_least_four_seed_vertices"] == 0
    assert payload["synthetic_a5_scan"]["strictly_convex_candidate_count"] == 0
    assert payload["synthetic_a5_scan"]["candidates_with_at_least_four_vertices"] == 0
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
