from __future__ import annotations

from dataclasses import replace
import hashlib

import pytest

from erdos97.n9_hinge_forcing import (
    AXIOMS,
    EXPECTED_BASELINE_EXTENSIONS,
    EXPECTED_BASELINE_MAXIMUM_DEPTH,
    EXPECTED_BASELINE_NODES,
    EXPECTED_BASELINE_OPTION_CHECKS,
    EXPECTED_BASELINE_REJECTIONS,
    EXPECTED_BASELINE_SHA256,
    EXPECTED_HINGE_COMPILER_REQUIREMENTS,
    EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES,
    EXPECTED_HINGE_COMPILER_SHA256,
    Axiom,
    AxiomConfig,
    SearchResult,
    SearchStats,
    audit_compiled_hinge_semantics,
    assert_expected_baseline,
    baseline_result,
    chords_cross,
    drop_one_result,
    hinge_instances,
    theorem_config,
    validate_terminal,
)


RECTANGLE_TRAP_ROWS = (
    (1, 2, 3, 8),
    (0, 2, 4, 7),
    (1, 3, 5, 7),
    (1, 4, 6, 8),
    (0, 2, 5, 6),
    (3, 4, 6, 7),
    (2, 5, 7, 8),
    (0, 3, 6, 8),
    (0, 1, 4, 5),
)


@pytest.fixture(scope="module")
def baseline() -> SearchResult:
    return baseline_result()


def test_chord_crossing_uses_proper_cyclic_crossing() -> None:
    assert chords_cross((0, 4), (1, 7))
    assert chords_cross((4, 0), (1, 7))
    assert not chords_cross((0, 4), (1, 3))
    assert not chords_cross((0, 4), (4, 7))
    assert not chords_cross((0, 1), (3, 7))


def test_compiled_hinge_count_matches_public_semantics() -> None:
    rows: list[list[int]] = [[] for _ in range(9)]
    rows[0] = [1, 2]
    rows[1] = [0, 2]
    rows[3] = [0, 1]

    assert hinge_instances(rows) == 1


@pytest.mark.artifact
def test_theorem_strength_search_is_complete_and_zero_terminal(
    baseline: SearchResult,
) -> None:
    assert_expected_baseline(baseline)
    assert baseline.config == theorem_config()
    assert baseline.search_complete
    assert not baseline.satisfiable
    assert baseline.witness is None
    assert baseline.stats == SearchStats(
        nodes_visited=EXPECTED_BASELINE_NODES,
        row_options_examined=EXPECTED_BASELINE_OPTION_CHECKS,
        extensions_visited=EXPECTED_BASELINE_EXTENSIONS,
        terminal_assignments=0,
        terminal_assignment_sha256=hashlib.sha256(b"[]").hexdigest(),
        maximum_depth=EXPECTED_BASELINE_MAXIMUM_DEPTH,
        rejection_counts=EXPECTED_BASELINE_REJECTIONS,
    )
    assert baseline.sha256 == EXPECTED_BASELINE_SHA256


def test_pair_capacity_and_indegree_are_derived_not_assumed(
    baseline: SearchResult,
) -> None:
    assert not baseline.config.indegree_exact_4
    assert not baseline.config.witness_pair_capacity_2
    assert baseline.config.row_intersection_cap_2
    assert baseline.config.two_overlap_chord_crossing
    assert baseline.indegree_exact_4_is_derived
    assert baseline.witness_pair_capacity_2_is_derived

    payload = baseline.to_dict()
    assert payload["indegree_balance"] == {
        "explicitly_enforced": False,
        "derived_from_other_enforced_axioms": True,
    }
    assert payload["witness_pair_capacity"] == {
        "explicitly_enforced": False,
        "derived_from_other_enforced_axioms": True,
    }


@pytest.mark.artifact
def test_all_compiled_hinge_triggers_match_public_semantics() -> None:
    audit = audit_compiled_hinge_semantics()

    assert audit.requirement_count == EXPECTED_HINGE_COMPILER_REQUIREMENTS
    assert audit.public_exact_match_count == EXPECTED_HINGE_COMPILER_REQUIREMENTS
    assert (
        audit.satisfaction_table_entry_count
        == EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES
    )
    assert audit.compiler_sha256 == EXPECTED_HINGE_COMPILER_SHA256


def test_each_axiom_can_be_independently_disabled() -> None:
    full = AxiomConfig()
    for dropped in AXIOMS:
        config = full.drop(dropped)
        assert not config.enforces(dropped)
        assert config.dropped_axioms == (dropped,)
        assert set(config.enforced_axioms) == set(AXIOMS) - {dropped}

    with pytest.raises(ValueError):
        full.drop("not_an_axiom")


def test_drop_hinge_returns_deterministic_sat_frontier() -> None:
    result = drop_one_result(Axiom.KALMANSON_EQUILATERAL_HINGE_FREE)

    assert result.satisfiable
    assert not result.search_complete
    assert result.stats.terminal_assignments == 1
    assert result.witness == RECTANGLE_TRAP_ROWS
    assert hinge_instances(RECTANGLE_TRAP_ROWS) == 6
    assert result.sha256 == (
        "8a4ad59841f38969d3f092a4a75282a5b72ac965c4e6cf67ca6471216252a564"
    )
    validate_terminal(RECTANGLE_TRAP_ROWS, result.config)
    with pytest.raises(ValueError, match="hinge-free"):
        validate_terminal(RECTANGLE_TRAP_ROWS, AxiomConfig())


def test_terminal_validation_rejects_malformed_and_unbalanced_rows() -> None:
    with pytest.raises(ValueError, match="expected 9 rows"):
        validate_terminal(RECTANGLE_TRAP_ROWS[:-1], AxiomConfig())

    malformed = list(RECTANGLE_TRAP_ROWS)
    malformed[0] = (0, 1, 2, 3)
    with pytest.raises(ValueError, match="invalid witness"):
        validate_terminal(malformed, AxiomConfig())

    unbalanced = list(RECTANGLE_TRAP_ROWS)
    unbalanced[0] = (1, 2, 3, 4)
    config = replace(
        AxiomConfig(),
        row_intersection_cap_2=False,
        two_overlap_chord_crossing=False,
        witness_pair_capacity_2=False,
        kalmanson_equilateral_hinge_free=False,
    )
    with pytest.raises(ValueError, match="indegree axiom"):
        validate_terminal(unbalanced, config)


def test_search_input_types_are_strict() -> None:
    from erdos97.n9_hinge_forcing import search

    with pytest.raises(TypeError, match="AxiomConfig"):
        search(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="bool"):
        search(stop_after_first=1)  # type: ignore[arg-type]
