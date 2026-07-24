from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from erdos97.fragile_turn_pivot_guardrail import (
    CLAIM_SCOPE,
    assert_expected_payload,
    cycle_type,
    guardrail_payload,
    inverse_permutation,
    matching_permutation,
    selected_rows,
    validate_payload,
)
from erdos97.json_io import load_json

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "data" / "certificates" / "fragile_turn_pivot_guardrail.json"
)


def test_matching_has_marked_three_cycle_and_three_witness_halos() -> None:
    rows = selected_rows()
    matching = matching_permutation()
    inverse = inverse_permutation(matching)

    assert cycle_type(matching) == (3, 13)
    assert sorted(matching) == list(range(16))
    assert sorted(inverse) == list(range(16))
    assert all(matching[center] in rows[center] for center in range(16))
    assert all(
        len(set(rows[center]) - {matching[center]}) == 3
        for center in range(16)
    )


def test_generated_guardrail_has_expected_exact_checks() -> None:
    payload = guardrail_payload()

    assert_expected_payload(payload)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["fragile_hypergraph"]["ok"] is True
    assert payload["good_deletion"]["all_seeds_have_good_survivor"] is True
    assert payload["hinge_guardrail"]["reciprocal_selected_pair_count"] == 0
    assert payload["weak_turn_replay"]["all_weak_terms_strictly_satisfied"] is True
    assert payload["vertex_circle_replay"]["status"] == "ok"
    assert payload["kalmanson_inverse"]["zero_sum_verified"] is True


def test_complete_stored_guardrail_regenerates_exactly() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)

    assert validate_payload(payload) == []


def test_guardrail_validation_rejects_counterexample_overclaim() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)
    payload["claim_scope"] = "A counterexample to Erdos Problem #97."

    assert "claim_scope:" in validate_payload(payload)[0]


def test_guardrail_cli_summary_json_is_compact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_fragile_turn_pivot_guardrail.py",
            "--check",
            "--assert-expected",
            "--summary-json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["essential_matching"]["cycle_type"] == [3, 13]
    assert payload["vertex_circle_replay"]["strict_edge_count"] == 144
    assert payload["kalmanson_inverse"]["combined_nonzero_coefficient_count"] == 0
    assert "selected_rows" not in payload
    assert "halos" not in payload["essential_matching"]
