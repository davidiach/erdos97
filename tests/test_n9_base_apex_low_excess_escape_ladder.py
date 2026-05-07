from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_base_apex_low_excess_escape_ladder import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_INTERPRETATION,
    expected_ladder_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_expected_low_excess_escape_ladder_counts_are_pinned() -> None:
    payload = expected_ladder_payload()

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
    assert payload["interpretation"] == EXPECTED_INTERPRETATION

    rows = payload["ladder_rows"]
    assert len(rows) == 7
    assert sum(row["unlabeled_profile_ledger_count"] for row in rows) == 30
    assert sum(row["labelled_profile_sequence_count"] for row in rows) == 5005
    assert sum(row["dihedral_profile_orbit_count"] for row in rows) == 318
    assert payload["strict_escape_slice"]["labelled_escape_placement_count"] == 108
    assert payload["strict_escape_slice"]["dihedral_escape_class_count"] == 8
    assert sum(row["labelled_profile_escape_pair_count"] for row in rows) == 540540
    assert sum(row["common_dihedral_pair_class_count"] for row in rows) == 30184


def test_expected_low_excess_escape_ladder_rungs_match_d3_top_rung() -> None:
    payload = expected_ladder_payload()

    assert [row["total_profile_excess"] for row in payload["ladder_rows"]] == list(range(7))
    assert [row["capacity_deficit"] for row in payload["ladder_rows"]] == [
        9,
        8,
        7,
        6,
        5,
        4,
        3,
    ]
    assert [
        row["unassigned_capacity_after_minimum_relevant_escape"]
        for row in payload["ladder_rows"]
    ] == [
        6,
        5,
        4,
        3,
        2,
        1,
        0,
    ]

    top = payload["ladder_rows"][-1]
    assert top["labelled_profile_sequence_count"] == 3003
    assert top["dihedral_profile_orbit_count"] == 185
    assert top["labelled_profile_escape_pair_count"] == 324324
    assert top["common_dihedral_pair_class_count"] == 18088


def test_low_excess_escape_ladder_payload_passes_independent_checker() -> None:
    payload = expected_ladder_payload()

    errors = validate_payload(payload)

    assert errors == []


def test_low_excess_escape_ladder_summary_is_nonclaiming() -> None:
    payload = expected_ladder_payload()
    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_ladder.json",
        payload,
        errors,
    )

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["rung_count"] == 7
    assert summary["total_unlabeled_profile_ledger_count"] == 30
    assert summary["labelled_escape_placement_count"] == 108
    assert summary["total_common_dihedral_pair_class_count"] == 30184


def test_low_excess_escape_ladder_checker_rejects_unknown_top_level_key() -> None:
    payload = expected_ladder_payload()
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_tampered_claim_scope() -> None:
    payload = expected_ladder_payload()
    payload["claim_scope"] = (
        "Focused n=9 bookkeeping; not a proof of n=9 and not a global status update."
    )

    errors = validate_payload(payload)

    assert any("claim_scope mismatch" in error for error in errors)
    assert any("not a counterexample" in error for error in errors)
    assert any("not a geometric realizability test" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_tampered_interpretation() -> None:
    payload = expected_ladder_payload()
    payload["interpretation"][-1] = "This closes n=9."

    errors = validate_payload(payload)

    assert any("interpretation mismatch" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_tampered_provenance() -> None:
    payload = expected_ladder_payload()
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_base_apex_low_excess_escape_ladder.py"
    )

    errors = validate_payload(payload)

    assert any("provenance mismatch" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_bool_top_level_int() -> None:
    payload = expected_ladder_payload()
    payload["n"] = True

    errors = validate_payload(payload)

    assert any("payload.n must be int" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_bool_nested_int() -> None:
    payload = expected_ladder_payload()
    payload["ladder_rows"][0]["labelled_profile_sequence_count"] = True

    errors = validate_payload(payload)

    assert any("labelled_profile_sequence_count must be int" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_string_rung_key_without_crashing() -> None:
    payload = expected_ladder_payload()
    payload["ladder_rows"][0]["total_profile_excess"] = "0"

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_ladder.json",
        payload,
        errors,
    )

    assert any("total_profile_excess must be an int" in error for error in errors)
    assert summary["ok"] is False


def test_low_excess_escape_ladder_summary_tolerates_string_count_tampering() -> None:
    payload = expected_ladder_payload()
    payload["ladder_rows"][0]["common_dihedral_pair_class_count"] = "8"

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT / "data" / "certificates" / "n9_base_apex_low_excess_escape_ladder.json",
        payload,
        errors,
    )

    assert any("common_dihedral_pair_class_count must be int" in error for error in errors)
    assert summary["total_common_dihedral_pair_class_count"] is None


def test_low_excess_escape_ladder_checker_rejects_rung_reordering() -> None:
    payload = expected_ladder_payload()
    payload["ladder_rows"] = list(reversed(payload["ladder_rows"]))

    errors = validate_payload(payload)

    assert any("ladder_rows must be ordered by total_profile_excess" in error for error in errors)
    assert any("payload.ladder_rows[0].total_profile_excess" in error for error in errors)


def test_low_excess_escape_ladder_checker_rejects_bad_unassigned_capacity() -> None:
    payload = expected_ladder_payload()
    payload["ladder_rows"][0]["unassigned_capacity_after_minimum_relevant_escape"] = 5

    errors = validate_payload(payload)

    assert any("wrong unassigned capacity" in error for error in errors)


def test_low_excess_escape_ladder_checker_cli_json(tmp_path: Path) -> None:
    artifact = tmp_path / "n9_base_apex_low_excess_escape_ladder.json"
    artifact.write_text(
        json.dumps(expected_ladder_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_low_excess_escape_ladder.py",
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
    assert payload["rung_count"] == 7
    assert payload["total_common_dihedral_pair_class_count"] == 30184
