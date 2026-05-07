from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_base_apex_d3_escape_frontier_packet import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_INTERPRETATION,
    expected_packet_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_expected_d3_escape_frontier_packet_counts_are_pinned() -> None:
    payload = expected_packet_payload()

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert payload["interpretation"] == EXPECTED_INTERPRETATION
    assert payload["total_profile_excess"] == 6
    assert payload["capacity_deficit"] == 3
    assert payload["relevant_deficit_count"] == 3
    assert payload["profile_multiset_count"] == 11
    assert payload["escape_class_count"] == 8
    assert payload["representative_count"] == 88
    assert payload["labelled_profile_sequence_count"] == 3003
    assert payload["labelled_escape_placement_count"] == 108
    assert payload["common_dihedral_pair_class_count"] == 18088
    assert payload["common_dihedral_pair_orbit_size_counts"] == {
        "18": 17948,
        "9": 140,
    }


def test_expected_d3_escape_frontier_packet_rows_are_ordered() -> None:
    payload = expected_packet_payload()
    rows = payload["representatives"]

    assert [row["representative_id"] for row in rows] == [
        f"R{index:03d}" for index in range(88)
    ]
    assert [row["escape_class_id"] for row in rows[:8]] == [
        f"X{index:02d}" for index in range(8)
    ]
    assert rows[0]["representative_profile_sequence"] == [0, 0, 0, 0, 0, 0, 0, 0, 6]
    assert rows[-1]["representative_profile_sequence"] == [0, 0, 0, 1, 1, 1, 1, 1, 1]
    assert sum(row["common_dihedral_pair_class_count"] for row in rows) == 18088


def test_d3_escape_frontier_packet_payload_passes_independent_checker() -> None:
    payload = expected_packet_payload()

    errors = validate_payload(payload)

    assert errors == []


def test_d3_escape_frontier_packet_summary_is_nonclaiming() -> None:
    payload = expected_packet_payload()
    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT
        / "data"
        / "certificates"
        / "n9_base_apex_d3_escape_frontier_packet.json",
        payload,
        errors,
    )

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["profile_multiset_count"] == 11
    assert summary["escape_class_count"] == 8
    assert summary["representative_count"] == 88
    assert summary["common_dihedral_pair_class_count"] == 18088
    assert summary["summary_common_dihedral_pair_class_count"] == 18088


def test_d3_escape_frontier_packet_checker_rejects_unknown_top_level_key() -> None:
    payload = expected_packet_payload()
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_tampered_claim_scope() -> None:
    payload = expected_packet_payload()
    payload["claim_scope"] = (
        "Focused n=9 packet bookkeeping; not a proof of n=9 and not a global status update."
    )

    errors = validate_payload(payload)

    assert any("claim_scope mismatch" in error for error in errors)
    assert any("not a counterexample" in error for error in errors)
    assert any("not a geometric realizability test" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_tampered_interpretation() -> None:
    payload = expected_packet_payload()
    payload["interpretation"][-1] = "This proves n=9."

    errors = validate_payload(payload)

    assert any("interpretation mismatch" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_tampered_provenance() -> None:
    payload = expected_packet_payload()
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_base_apex_d3_escape_frontier_packet.py"
    )

    errors = validate_payload(payload)

    assert any("provenance mismatch" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_bool_top_level_int() -> None:
    payload = expected_packet_payload()
    payload["n"] = True

    errors = validate_payload(payload)

    assert any("payload.n must be int" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_bool_nested_int() -> None:
    payload = expected_packet_payload()
    payload["representatives"][0]["common_dihedral_pair_class_count"] = True

    errors = validate_payload(payload)

    assert any(
        "common_dihedral_pair_class_count must be an int" in error for error in errors
    )


def test_d3_escape_frontier_packet_checker_rejects_representative_reordering() -> None:
    payload = expected_packet_payload()
    payload["representatives"] = list(reversed(payload["representatives"]))

    errors = validate_payload(payload)

    assert any("representatives[0].representative_id" in error for error in errors)
    assert any("representatives must be ordered" in error for error in errors)
    assert any("payload.representatives[0].representative_id" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_scalar_representative() -> None:
    payload = expected_packet_payload()
    payload["representatives"][0] = 1

    errors = validate_payload(payload)

    assert any("representatives[0] must be an object" in error for error in errors)
    assert any("payload.representatives[0] must be an object" in error for error in errors)


def test_d3_escape_frontier_packet_checker_rejects_malformed_profile_without_crashing() -> None:
    payload = expected_packet_payload()
    payload["representatives"][0]["representative_profile_sequence"] = [0, True]

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT
        / "data"
        / "certificates"
        / "n9_base_apex_d3_escape_frontier_packet.json",
        payload,
        errors,
    )

    assert any("representative_profile_sequence must be a list of ints" in error for error in errors)
    assert summary["ok"] is False


def test_d3_escape_frontier_packet_checker_rejects_malformed_escape_without_crashing() -> None:
    payload = expected_packet_payload()
    payload["representatives"][0]["canonical_escape_placement"] = {
        "spoiled_length2": [0, 0],
        "spoiled_length3": [9],
    }

    errors = validate_payload(payload)

    assert any("spoiled_length2 must be sorted unique ints" in error for error in errors)
    assert any("indices must be in range" in error for error in errors)


def test_d3_escape_frontier_packet_summary_tolerates_string_count_tampering() -> None:
    payload = expected_packet_payload()
    payload["representatives"][0]["common_dihedral_pair_class_count"] = "1"

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT
        / "data"
        / "certificates"
        / "n9_base_apex_d3_escape_frontier_packet.json",
        payload,
        errors,
    )

    assert any("common_dihedral_pair_class_count must be an int" in error for error in errors)
    assert summary["common_dihedral_pair_class_count"] is None


def test_d3_escape_frontier_packet_checker_cli_json(tmp_path: Path) -> None:
    artifact = tmp_path / "n9_base_apex_d3_escape_frontier_packet.json"
    artifact.write_text(
        json.dumps(expected_packet_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_d3_escape_frontier_packet.py",
            "--artifact",
            str(artifact),
            "--check",
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 0
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["representative_count"] == 88
    assert payload["common_dihedral_pair_class_count"] == 18088
