from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_base_apex_low_excess_escape_crosswalk import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_INTERPRETATION,
    expected_crosswalk_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_expected_low_excess_escape_crosswalk_counts_are_pinned() -> None:
    payload = expected_crosswalk_payload()
    summary = payload["matrix_summary"]

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert payload["interpretation"] == EXPECTED_INTERPRETATION
    assert summary["profile_ledger_count"] == 30
    assert summary["escape_class_count"] == 8
    assert summary["matrix_cell_count"] == 240
    assert summary["nonzero_matrix_cell_count"] == 240
    assert summary["total_labelled_profile_sequence_count"] == 5005
    assert summary["labelled_escape_placement_count"] == 108
    assert summary["total_labelled_profile_escape_pair_count"] == 540540
    assert summary["total_common_dihedral_pair_class_count"] == 30184


def test_expected_low_excess_escape_crosswalk_rows_match_ladder_rungs() -> None:
    payload = expected_crosswalk_payload()
    summary = payload["matrix_summary"]

    assert summary["profile_ledger_count_by_total_profile_excess"] == {
        "0": 1,
        "1": 1,
        "2": 2,
        "3": 3,
        "4": 5,
        "5": 7,
        "6": 11,
    }
    assert summary["labelled_profile_sequence_count_by_total_profile_excess"] == {
        "0": 1,
        "1": 9,
        "2": 45,
        "3": 165,
        "4": 495,
        "5": 1287,
        "6": 3003,
    }
    assert summary["common_dihedral_pair_class_count_by_total_profile_excess"] == {
        "0": 8,
        "1": 56,
        "2": 280,
        "3": 1000,
        "4": 3000,
        "5": 7752,
        "6": 18088,
    }
    assert [row["capacity_deficit"] for row in payload["profile_ledger_rows"]] == [
        9 - row["total_profile_excess"]
        for row in payload["profile_ledger_rows"]
    ]


def test_expected_low_excess_escape_crosswalk_escape_classes_are_pinned() -> None:
    payload = expected_crosswalk_payload()

    assert [row["escape_class_id"] for row in payload["escape_classes"]] == [
        f"X{index:02d}" for index in range(8)
    ]
    assert [row["labelled_placement_count"] for row in payload["escape_classes"]] == [
        18,
        9,
        9,
        18,
        18,
        9,
        9,
        18,
    ]
    assert payload["matrix_summary"]["common_dihedral_pair_class_count_by_escape_class"] == {
        "X00": 5005,
        "X01": 2541,
        "X02": 2541,
        "X03": 5005,
        "X04": 5005,
        "X05": 2541,
        "X06": 2541,
        "X07": 5005,
    }


def test_low_excess_escape_crosswalk_payload_passes_independent_checker() -> None:
    payload = expected_crosswalk_payload()

    errors = validate_payload(payload)

    assert errors == []


def test_low_excess_escape_crosswalk_summary_is_nonclaiming() -> None:
    payload = expected_crosswalk_payload()
    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_crosswalk.json",
        payload,
        errors,
    )

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["profile_ledger_count"] == 30
    assert summary["escape_class_count"] == 8
    assert summary["matrix_cell_count"] == 240
    assert summary["total_common_dihedral_pair_class_count"] == 30184
    assert summary["summary_total_common_dihedral_pair_class_count"] == 30184


def test_low_excess_escape_crosswalk_checker_rejects_unknown_top_level_key() -> None:
    payload = expected_crosswalk_payload()
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_tampered_claim_scope() -> None:
    payload = expected_crosswalk_payload()
    payload["claim_scope"] = (
        "Focused n=9 bookkeeping; not a proof of n=9 and not a global status update."
    )

    errors = validate_payload(payload)

    assert any("claim_scope mismatch" in error for error in errors)
    assert any("not a counterexample" in error for error in errors)
    assert any("not a geometric realizability test" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_tampered_interpretation() -> None:
    payload = expected_crosswalk_payload()
    payload["interpretation"][-1] = "This closes n=9."

    errors = validate_payload(payload)

    assert any("interpretation mismatch" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_tampered_provenance() -> None:
    payload = expected_crosswalk_payload()
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_base_apex_low_excess_escape_crosswalk.py"
    )

    errors = validate_payload(payload)

    assert any("provenance mismatch" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_bool_top_level_int() -> None:
    payload = expected_crosswalk_payload()
    payload["n"] = True

    errors = validate_payload(payload)

    assert any("payload.n must be int" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_bool_nested_int() -> None:
    payload = expected_crosswalk_payload()
    payload["crosswalk_rows"][0]["common_dihedral_pair_class_count"] = True

    errors = validate_payload(payload)

    assert any("common_dihedral_pair_class_count must be an int" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_scalar_escape_classes() -> None:
    payload = expected_crosswalk_payload()
    payload["escape_classes"] = 1

    errors = validate_payload(payload)

    assert any("escape_classes must be a list" in error for error in errors)
    assert any("payload.escape_classes must be a list" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_profile_row_reordering() -> None:
    payload = expected_crosswalk_payload()
    payload["profile_ledger_rows"] = list(reversed(payload["profile_ledger_rows"]))

    errors = validate_payload(payload)

    assert any("profile_ledger_rows[0].profile_ledger_id" in error for error in errors)
    assert any("profile_ledger_rows must be ordered" in error for error in errors)
    assert any("payload.profile_ledger_rows[0].profile_ledger_id" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_crosswalk_row_reordering() -> None:
    payload = expected_crosswalk_payload()
    payload["crosswalk_rows"] = list(reversed(payload["crosswalk_rows"]))

    errors = validate_payload(payload)

    assert any("crosswalk_rows must be ordered" in error for error in errors)
    assert any("payload.crosswalk_rows[0].profile_ledger_id" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_matrix_row_reordering() -> None:
    payload = expected_crosswalk_payload()
    payload["crosswalk_matrix"]["rows"] = list(reversed(payload["crosswalk_matrix"]["rows"]))

    errors = validate_payload(payload)

    assert any("crosswalk_matrix.rows[0].profile_ledger_id" in error for error in errors)
    assert any("payload.crosswalk_matrix.rows[0].profile_ledger_id" in error for error in errors)


def test_low_excess_escape_crosswalk_checker_rejects_tampered_matrix_count() -> None:
    payload = expected_crosswalk_payload()
    payload["crosswalk_matrix"]["rows"][0]["common_dihedral_pair_class_counts"]["X00"] = 10

    errors = validate_payload(payload)

    assert any("payload.crosswalk_matrix.rows[0]" in error for error in errors)


def test_low_excess_escape_crosswalk_summary_tolerates_string_count_tampering() -> None:
    payload = expected_crosswalk_payload()
    payload["crosswalk_rows"][0]["common_dihedral_pair_class_count"] = "1"

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_crosswalk.json",
        payload,
        errors,
    )

    assert any("common_dihedral_pair_class_count must be an int" in error for error in errors)
    assert summary["total_common_dihedral_pair_class_count"] is None


def test_low_excess_escape_crosswalk_checker_cli_json(tmp_path: Path) -> None:
    artifact = tmp_path / "n9_base_apex_low_excess_escape_crosswalk.json"
    artifact.write_text(
        json.dumps(expected_crosswalk_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_low_excess_escape_crosswalk.py",
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
    assert payload["profile_ledger_count"] == 30
    assert payload["escape_class_count"] == 8
    assert payload["total_common_dihedral_pair_class_count"] == 30184
