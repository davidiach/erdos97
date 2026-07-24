from __future__ import annotations

import math
from pathlib import Path
import random
import subprocess
import sys

import pytest

from erdos97.json_io import load_json
from erdos97.n9_equilateral_chord_obstruction import (
    CHORDS,
    EXPECTED_ADMISSIBLE_GRAPH_COUNT,
    EXPECTED_DEGREE_GRAPH_COUNT,
    EXPECTED_DIHEDRAL_CLASS_COUNT,
    N,
    STEP4_TURN_LOWER_BOUND,
    admissible_graphs,
    assert_expected_payload,
    canonical_form,
    certificate_data,
    chord_graphs,
    chord_span,
    isolated_count,
    ledger_admissible,
    step_count,
    transport,
    validate_payload,
    verify_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = ROOT / "data" / "certificates" / "n9_equilateral_chord_obstruction.json"


def _chain(turns: list[float], start: int, step: int) -> float:
    """Return the chord length spanned by ``step`` unit edges from ``start``.

    ``turns[j]`` is the exterior turn at vertex ``j``, so the edge from vertex
    ``j`` to vertex ``j+1`` points along ``turns[1] + ... + turns[j]``.
    """

    point = (0.0, 0.0)
    angle = 0.0
    for index in range(start, start + step):
        point = (point[0] + math.cos(angle), point[1] + math.sin(angle))
        angle += turns[(index + 1) % N]
    return math.hypot(*point)


def _random_turns(rng: random.Random) -> list[float]:
    turns = [rng.uniform(0.05, 1.2) for _ in range(N)]
    scale = 2 * math.pi / sum(turns)
    return [turn * scale for turn in turns]


def test_chord_span_matches_the_geometry() -> None:
    """The three turn laws hold for the spans this module computes."""

    rng = random.Random(20260724)
    lower = {step: 2 * math.acos(1 / step) for step in (2, 3, 4)}
    for _ in range(400):
        turns = _random_turns(rng)
        if not all(0.0 < turn < math.pi for turn in turns):
            continue
        for low, high, step in CHORDS:
            # A random turn vector need not close up, so only the chords whose
            # short arc runs forward from ``low`` describe a genuine chain.
            if (high - low) % N != step:
                continue
            length = _chain(turns, low, step)
            spanned = sum(turns[vertex] for vertex in chord_span((low, high, step)))
            if step == 2:
                assert length == pytest.approx(2 * math.cos(spanned / 2), abs=1e-9)
            if abs(length - 1.0) < 1e-7:
                assert spanned >= lower[step] - 1e-9
                if step == 3:
                    assert spanned == pytest.approx(math.pi, abs=1e-5)


def test_step_three_law_is_an_equivalence() -> None:
    """Two interior turns summing to pi give a side-length step-3 chord."""

    rng = random.Random(11)
    for _ in range(200):
        first = rng.uniform(0.05, math.pi - 0.05)
        turns = [0.01] * N
        turns[1], turns[2] = first, math.pi - first
        assert _chain(turns, 0, 3) == pytest.approx(1.0, abs=1e-9)


def test_step_four_threshold_is_a_valid_under_approximation() -> None:
    assert STEP4_TURN_LOWER_BOUND < 2 * math.acos(0.25) / (2 * math.pi)


def test_enumeration_counts_and_degrees() -> None:
    graphs = chord_graphs()
    assert len(graphs) == EXPECTED_DEGREE_GRAPH_COUNT
    assert len(set(graphs)) == len(graphs)
    for graph in graphs:
        degree = [0] * N
        for low, high, _step in graph:
            degree[low] += 1
            degree[high] += 1
        assert set(degree) <= {0, 2}
        assert degree.count(0) == isolated_count(graph) <= 4


def test_ledger_filter_keeps_exactly_the_admissible_graphs() -> None:
    admissible = admissible_graphs()
    assert len(admissible) == EXPECTED_ADMISSIBLE_GRAPH_COUNT
    for graph in admissible:
        assert isolated_count(graph) <= 2 * step_count(graph, 2)
    dropped = [g for g in chord_graphs() if not ledger_admissible(g)]
    assert dropped
    for graph in dropped:
        assert isolated_count(graph) > 2 * step_count(graph, 2)


def test_verify_certificate_rejects_unsound_multipliers() -> None:
    graph = next(g for g in admissible_graphs() if step_count(g, 4) > 0)
    zero = [0] * len(graph)
    assert not verify_certificate(graph, zero)
    negative = list(zero)
    negative[next(i for i, c in enumerate(graph) if c[2] == 4)] = -1
    # A step-4 chord is only a lower bound, so a negative weight is unusable.
    assert not verify_certificate(graph, negative)


def test_certificate_arithmetic_matches_a_direct_recount() -> None:
    records = load_json(ARTIFACT)["classes"]
    for record in records[:25]:
        graph = tuple(tuple(chord) for chord in record["chords"])
        total, counts = certificate_data(graph, record["multipliers"])
        recount = [0] * N
        for chord, weight in zip(graph, record["multipliers"]):
            for vertex in chord_span(chord):
                recount[vertex] += weight
        assert counts == recount == record["span_counts"]
        assert str(total) == record["bound_total"]
        assert (total > max(counts)) == record["strict"]
        assert total >= max(counts)


def test_every_admissible_graph_is_refuted_by_a_stored_certificate() -> None:
    records = {
        tuple(tuple(chord) for chord in record["chords"]): record
        for record in load_json(ARTIFACT)["classes"]
    }
    assert len(records) == EXPECTED_DIHEDRAL_CLASS_COUNT
    for graph in admissible_graphs():
        key, relabel = canonical_form(graph)
        moved = transport(graph, relabel, records[key]["multipliers"])
        assert verify_certificate(graph, moved)


@pytest.mark.artifact
def test_stored_artifact_validates() -> None:
    data = load_json(ARTIFACT)
    assert validate_payload(data) == []
    assert_expected_payload(data)


@pytest.mark.artifact
def test_checker_cli_replays_the_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "check_n9_equilateral_chord_obstruction.py"),
            "--check",
            "--assert-expected",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert "surviving graphs: 0" in result.stdout
