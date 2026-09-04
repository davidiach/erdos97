from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

from erdos97.json_io import load_json
from erdos97.perimeter_relaxation_guardrail import (
    CLAIM_SCOPE,
    EXPECTED_NEGATIVE_TYPE_VIOLATION,
    EXPECTED_SHIFT_GAP,
    assert_expected_payload,
    control_payload,
    selected_rows,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "data" / "certificates" / "perimeter_relaxation_guardrail.json"
)


def test_even_rows_have_the_forbidden_m10_k3_pattern() -> None:
    rows = selected_rows()

    for center in range(0, 20, 2):
        assert set(rows[center]) == {
            (center - 1) % 20,
            (center + 1) % 20,
            (center - 6) % 20,
            (center + 6) % 20,
        }


def test_generated_guardrail_has_expected_exact_checks() -> None:
    payload = control_payload()

    assert_expected_payload(payload)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["strict_triangle_replay"]["minimum_slack"] == 2
    assert payload["strict_kalmanson_replay"]["minimum_slack"] == 1
    assert (
        payload["incidence_replay"]["selected_digraph_strongly_connected"]
        is True
    )
    assert payload["weak_turn_replay"]["minimum_slack"] == "1/10"
    obstruction = payload["unshifted_euclidean_obstruction"]
    assert (
        obstruction["squared_distance_energy"]
        == EXPECTED_NEGATIVE_TYPE_VIOLATION
    )
    lift = payload["shifted_high_dimensional_euclidean_lift"]
    assert lift["strict_conditional_negative_type_gap"] == EXPECTED_SHIFT_GAP


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
            "scripts/check_perimeter_relaxation_guardrail.py",
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
    forbidden = payload["incidence_replay"][
        "alternate_vertex_forbidden_subsystem"
    ]
    assert forbidden["k"] == 3
    lift = payload["shifted_high_dimensional_euclidean_lift"]
    assert lift["certified_affine_embedding_dimension"] == 19
    assert "selected_rows" not in payload
    assert "records" not in payload["rich_classes"]
    assert "coefficients" not in payload["unshifted_euclidean_obstruction"]
