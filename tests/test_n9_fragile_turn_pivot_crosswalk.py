from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys

from erdos97.json_io import load_json
from erdos97.n9_fragile_turn_pivot_crosswalk import (
    CLAIM_SCOPE,
    EXPECTED_INVERSION_COVER_SIZE_HISTOGRAM,
    EXPECTED_PAIR_HIT_CENTER_HISTOGRAM,
    EXPECTED_PIVOT_HALO_LAMBDA_HISTOGRAM,
    EXPECTED_THREE_PIVOT_ASSIGNMENTS,
    assert_expected_payload,
    binary_turn_witness,
    crosswalk_payload,
    hit_centers,
    permutation_cycle_type,
    validate_payload,
    verify_binary_turn_vector,
    verify_pivot_halo_certificate,
)

ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_fragile_turn_pivot_crosswalk.json"
)
TURN_SOURCE = (
    ROOT / "data" / "certificates" / "n9_turn_inequality_frontier.json"
)
MOTIF_SOURCE = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)


def _file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _source_payloads() -> tuple[dict[str, object], dict[str, object]]:
    turn_payload = load_json(TURN_SOURCE)
    motif_payload = load_json(MOTIF_SOURCE)
    assert isinstance(turn_payload, dict)
    assert isinstance(motif_payload, dict)
    return turn_payload, motif_payload


def test_generated_crosswalk_has_expected_headline_counts() -> None:
    turn_payload, motif_payload = _source_payloads()
    payload = crosswalk_payload(
        turn_payload,
        motif_payload,
        turn_source_file_sha256=_file_sha256(TURN_SOURCE),
        motif_source_file_sha256=_file_sha256(MOTIF_SOURCE),
    )

    assert_expected_payload(payload)
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["pivot_halo_turn_certificates"]["lambda_histogram"] == (
        EXPECTED_PIVOT_HALO_LAMBDA_HISTOGRAM
    )
    assert payload["inversion_row_pivot_covers"]["minimum_cover_size_histogram"] == (
        EXPECTED_INVERSION_COVER_SIZE_HISTOGRAM
    )
    assert payload["inversion_row_pivot_covers"]["three_pivot_assignment_ids"] == (
        EXPECTED_THREE_PIVOT_ASSIGNMENTS
    )
    assert payload["three_pivot_exception"]["pair_hit_center_count_histogram"] == (
        EXPECTED_PAIR_HIT_CENTER_HISTOGRAM
    )


def test_stored_hamiltonian_matchings_and_exception_witnesses_replay() -> None:
    payload = load_json(ARTIFACT)
    assert isinstance(payload, dict)

    pivot_halo_records = payload["pivot_halo_turn_certificates"]["records"]
    assert len(pivot_halo_records) == 184
    assert all(
        permutation_cycle_type(record["matching"]) == (9,)
        for record in pivot_halo_records
    )
    _turn_payload, motif_payload = _source_payloads()
    motif_rows = [
        [row[1:] for row in assignment["selected_rows"]]
        for assignment in motif_payload["assignments"]
    ]
    for rows, record in zip(motif_rows, pivot_halo_records):
        verify_pivot_halo_certificate(
            rows,
            record["matching"],
            record["certificate"],
        )

    for exception in payload["three_pivot_exception"]["records"]:
        rows = [row[1:] for row in exception["selected_rows"]]
        for pair_record in exception["two_pivot_restrictions"]:
            centers = hit_centers(rows, pair_record["pivots"])
            assert list(centers) == pair_record["hit_centers"]
            assert binary_turn_witness(rows, centers) == tuple(
                pair_record["binary_turn_vector"]
            )
            verify_binary_turn_vector(
                rows,
                centers,
                pair_record["binary_turn_vector"],
            )


def test_complete_stored_payload_regenerates_exactly() -> None:
    payload = load_json(ARTIFACT)
    turn_payload, motif_payload = _source_payloads()
    assert isinstance(payload, dict)

    assert validate_payload(
        payload,
        turn_payload,
        motif_payload,
        turn_source_file_sha256=_file_sha256(TURN_SOURCE),
        motif_source_file_sha256=_file_sha256(MOTIF_SOURCE),
    ) == []


def test_validation_rejects_claim_scope_drift() -> None:
    payload = load_json(ARTIFACT)
    turn_payload, motif_payload = _source_payloads()
    assert isinstance(payload, dict)
    payload["claim_scope"] = "This proves n=9."

    errors = validate_payload(
        payload,
        turn_payload,
        motif_payload,
        turn_source_file_sha256=_file_sha256(TURN_SOURCE),
        motif_source_file_sha256=_file_sha256(MOTIF_SOURCE),
    )

    assert "claim_scope mismatch" in errors


def test_cli_summary_json_omits_assignment_records() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_fragile_turn_pivot_crosswalk.py",
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
    assert payload["witness_pivot_matching"]["perfect_matching_count"] == 82_720
    assert payload["inversion_row_pivot_covers"]["minimum_cover_size_histogram"] == {
        "2": 182,
        "3": 2,
    }
    assert "records" not in payload["pivot_halo_turn_certificates"]
    assert "records" not in payload["inversion_row_pivot_covers"]
    assert "records" not in payload["three_pivot_exception"]
