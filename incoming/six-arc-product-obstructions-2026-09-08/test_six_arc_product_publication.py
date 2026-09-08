"""Defensive publication tests; archived sources remain immutable."""
from __future__ import annotations

import copy
from fractions import Fraction as F
import importlib.util
import itertools
import json
from pathlib import Path
import shutil

import pytest

ROOT = Path(__file__).resolve().parent


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CHECKER = load("carrier_opposite_triangle_checker", ROOT / "snapshot/verify/check_opposite_triangles.py")
REPLAY = load("carrier_publication_replay", ROOT / "replay.py")
CERT = json.loads((ROOT / "snapshot/candidate_counterexamples/opposite_triangle_contradictions.json").read_text())


def test_original_manifest():
    assert REPLAY.check_manifest() == 18


def test_certificate_all_orders():
    result = CHECKER.verify(CERT)
    assert result["orders"] == 30
    assert result["contradiction_bounds"] == {"-1/18": 6, "-1/4": 3, "0": 15, "-1/12": 6}


@pytest.mark.parametrize("mutation", ["missing", "duplicate", "unexpected_order", "negative_weight",
                                    "zero_weights", "wrong_rhs", "inequality_length", "equality_length",
                                    "changed_coefficient", "nonrational_weight"])
def test_certificate_tampering_rejected(mutation):
    data = copy.deepcopy(CERT)
    row = data["certificates"][0]
    if mutation == "missing":
        data["certificates"].pop()
    elif mutation == "duplicate":
        data["certificates"].append(copy.deepcopy(row))
    elif mutation == "unexpected_order":
        row["order"] = [0, 1, 2, 3, 4, 5]
    elif mutation == "negative_weight":
        row["inequality_weights"][0] = "-1"
    elif mutation == "zero_weights":
        row["inequality_weights"] = ["0"] * len(row["inequality_weights"])
    elif mutation == "wrong_rhs":
        row["right_hand_side"] = "1"
    elif mutation == "inequality_length":
        row["inequality_weights"].pop()
    elif mutation == "equality_length":
        row["equality_weights"].pop()
    elif mutation == "changed_coefficient":
        row["equality_weights"][0] = str(F(row["equality_weights"][0]) + 1)
    elif mutation == "nonrational_weight":
        row["inequality_weights"][0] = "not-a-rational"
    with pytest.raises((AssertionError, ValueError)):
        CHECKER.verify(data)


CASES = [
    ((0, 1, 2, 3, 5, 4), [(1, 5, 0, 4), (1, 0, 5, 4), (1, 2, 4, 3)],
     [0, 0, 0, "-1/6", "-1/2", "1/2", "-1/3", 0, 0, "2/3", "1/3", 0], "-1/6", 6),
    ((0, 1, 2, 5, 4, 3), [(1, 0, 4, 3), (1, 2, 4, 5)],
     [0, 0, 0, "-1/6", "-1/2", "1/2", "-1/3", 0, 0, "-2/3", "-1/3", 0], "-1/2", 3),
    ((0, 1, 3, 2, 5, 4), [(1, 0, 3, 4), (2, 0, 2, 4), (2, 5, 0, 4), (2, 2, 3, 5), (1, 3, 5, 2)],
     [0, 0, 1, "-1/3", -1, 1, "-2/3", 1, 0, "-1/3", "-2/3", 0], "0", 6),
    ((0, 1, 4, 2, 3, 5), [(1, 0, 4, 5), (1, 2, 4, 3)],
     [0, 0, 0, "-1/6", "-1/2", "1/2", "-1/3", 0, 0, "2/3", "1/3", 0], "-1/6", 6),
    ((0, 1, 4, 3, 2, 5), [(2, 0, 1, 5), (1, 0, 3, 5), (2, 1, 3, 4), (1, 3, 5, 2)],
     [0, 1, 0, "-1/3", 0, 0, "-2/3", 0, 1, "2/3", "4/3", 0], "0", 6),
    ((0, 3, 1, 5, 2, 4), [(1, 0, 3, 4), (2, 1, 3, 5), (2, 3, 5, 1), (1, 2, 5, 4)],
     ["-2/3", 1, 0, "-1/3", 0, 0, 0, 0, -1, "-2/3", "-1/3", 0], "0", 3),
]


def angle_row(order, left, apex, right):
    pos = {v: i for i, v in enumerate(order)}
    i, j, k = sorted([pos[left], pos[apex], pos[right]])
    ij, ik, jk = [CHECKER.INDEX[p] for p in [(i, j), (i, k), (j, k)]]
    row = [F(0)] * 15
    if pos[apex] == i:
        row[ik] = 1
        row[ij] = -1
        constant = 0
    elif pos[apex] == k:
        row[jk] = 1
        row[ik] = -1
        constant = 0
    else:
        row[jk] = -1
        row[ij] = 1
        constant = 1
    return row, constant


@pytest.mark.parametrize("case", CASES, ids=list("ABCDEF"))
def test_six_printed_angle_identities(case):
    order, angles, weights, rhs, _ = case
    _, _, equations, constants = CHECKER.system(order)
    coeff = [F(0)] * 15
    constant = 0
    for multiplier, left, apex, right in angles:
        row, c = angle_row(order, left, apex, right)
        coeff = [a + multiplier * b for a, b in zip(coeff, row)]
        constant += multiplier * c
    weights = list(map(F, weights))
    assert len(weights) == 12
    assert coeff == [sum(v * e[j] for v, e in zip(weights, equations)) for j in range(15)]
    assert constant + sum(v * e for v, e in zip(weights, constants)) == F(rhs)


def test_six_symmetry_orbits_cover_thirty_orders():
    covered = set()
    for order, _, _, _, expected_size in CASES:
        orbit = set()
        for permutation in itertools.permutations(range(3)):
            transformed = [permutation[v % 3] + 3 * (v // 3) for v in order]
            if not CHECKER.ccw(transformed, (0, 1, 2)):
                transformed.reverse()
            zero = transformed.index(0)
            normalized = tuple(transformed[zero:] + transformed[:zero])
            assert CHECKER.ccw(normalized, (0, 1, 2))
            assert not CHECKER.ccw(normalized, (3, 4, 5))
            orbit.add(normalized)
        assert len(orbit) == expected_size
        assert not covered.intersection(orbit)
        covered.update(orbit)
    assert covered == {tuple(c["order"]) for c in CERT["certificates"]}


@pytest.mark.parametrize("mutation", ["changed", "missing", "extra"])
def test_manifest_tampering_rejected(tmp_path, mutation):
    shutil.copytree(ROOT / "snapshot", tmp_path / "snapshot")
    shutil.copy2(ROOT / "provenance.json", tmp_path / "provenance.json")
    target = tmp_path / "snapshot/research_log.md"
    if mutation == "changed":
        target.write_text(target.read_text() + "\nchanged\n")
    elif mutation == "missing":
        target.unlink()
    else:
        (tmp_path / "snapshot/extra.txt").write_text("unexpected")
    with pytest.raises(AssertionError):
        REPLAY.check_manifest(tmp_path)


def test_recorded_exploration_inventory():
    product = json.loads((ROOT / "snapshot/reports/product_probe.json").read_text())
    probe = json.loads((ROOT / "snapshot/reports/nonsymmetric_circulant_probe.json").read_text())
    caps = json.loads((ROOT / "snapshot/reports/off_carrier_caps.json").read_text())
    assert product["hull_size"] == 18
    assert len(probe["cases"]) == 8
    assert {row["n"] for row in probe["cases"]} == {12, 15}
    assert all(row["hull_size"] < row["n"] for row in probe["cases"])
    assert all(0 < row["min_separation"] < 1e-6 for row in probe["cases"])
    assert len(caps["records"]) == 100
    assert all(row["all_roots_hull_vertices"] < row["all_roots_point_count"] for row in caps["records"])
    # These assertions inventory archived diagnostics; they are not geometry certificates.


@pytest.mark.artifact
def test_complete_scoped_replay():
    report = REPLAY.run_replay()
    assert report["exact_certificate_orders"] == 30
    assert report["symbolic_identity_checks"] == 49
    assert report["nonconvex_control_distance_equalities"] == 108
    assert len(report["regenerated_comparisons"]) == 6
    assert not report["unrestricted_solution"]
