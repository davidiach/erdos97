from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import scripts.check_n9_base_apex_d3_p19_incidence_capacity_pilot as checker
from scripts.check_n9_base_apex_d3_p19_incidence_capacity_pilot import (
    EXPECTED_CLAIM_SCOPE,
    EXPECTED_INTERPRETATION_WARNING,
    expected_pilot_payload,
    summary_payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_p19_pilot_counts_are_pinned() -> None:
    payload = expected_pilot_payload()

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert payload["profile_ledger_id"] == "P19"
    assert payload["profile_multiset"] == [0, 0, 0, 0, 0, 0, 0, 0, 6]
    assert payload["representative_count"] == 8
    assert payload["escape_class_count"] == 8
    assert payload["labelled_profile_sequence_count"] == 9
    assert payload["common_dihedral_pair_class_count"] == 56
    assert [row["common_dihedral_pair_class_count"] for row in payload["rows"]] == [
        9,
        5,
        5,
        9,
        9,
        5,
        5,
        9,
    ]


def test_p19_pilot_nonclaiming_wording_and_unknown_states() -> None:
    payload = expected_pilot_payload()

    assert payload["claim_scope"] == EXPECTED_CLAIM_SCOPE
    lowered = payload["claim_scope"].lower()
    for phrase in (
        "not a proof",
        "not a counterexample",
        "not an incidence-completeness result",
        "not a geometric realizability test",
        "not a global status update",
    ):
        assert phrase in lowered
    assert payload["realizability_state"] == "UNKNOWN"
    assert payload["incidence_state"] == "UNKNOWN"
    assert payload["state_scope"] == "bookkeeping-only"
    assert payload["interpretation_warning"] == EXPECTED_INTERPRETATION_WARNING
    assert all(row["realizability_state"] == "UNKNOWN" for row in payload["rows"])
    assert all(row["incidence_state"] == "UNKNOWN" for row in payload["rows"])
    assert all(row["state_scope"] == "bookkeeping-only" for row in payload["rows"])


def test_p19_pilot_rows_are_r000_through_r007() -> None:
    payload = expected_pilot_payload()
    rows = payload["rows"]

    assert [row["representative_id"] for row in rows] == [
        f"R{index:03d}" for index in range(8)
    ]
    assert [row["escape_class_id"] for row in rows] == [
        f"X{index:02d}" for index in range(8)
    ]


def test_p19_pilot_target_capacity_totals_are_pinned() -> None:
    payload = expected_pilot_payload()
    rows = payload["rows"]

    assert payload["full_capacity_totals_by_cyclic_length"] == {
        "1": 9,
        "2": 18,
        "3": 18,
        "4": 18,
    }
    assert payload["target_capacity_total"] == 60
    assert [row["target_capacity_totals_by_cyclic_length"] for row in rows] == [
        {"1": 9, "2": 16, "3": 17, "4": 18},
        {"1": 9, "2": 16, "3": 17, "4": 18},
        {"1": 9, "2": 16, "3": 17, "4": 18},
        {"1": 9, "2": 16, "3": 17, "4": 18},
        {"1": 9, "2": 15, "3": 18, "4": 18},
        {"1": 9, "2": 15, "3": 18, "4": 18},
        {"1": 9, "2": 15, "3": 18, "4": 18},
        {"1": 9, "2": 15, "3": 18, "4": 18},
    ]
    assert all(
        sum(row["target_capacity_totals_by_cyclic_length"].values()) == 60
        for row in rows
    )


def test_p19_pilot_deficient_base_chords_are_pinned() -> None:
    payload = expected_pilot_payload()

    assert payload["rows"][0]["deficient_base_chords"] == [
        {"cyclic_length": 2, "base_index": 0, "chord": [0, 2]},
        {"cyclic_length": 2, "base_index": 2, "chord": [2, 4]},
        {"cyclic_length": 3, "base_index": 3, "chord": [3, 6]},
    ]
    assert payload["rows"][7]["deficient_base_chords"] == [
        {"cyclic_length": 2, "base_index": 0, "chord": [0, 2]},
        {"cyclic_length": 2, "base_index": 2, "chord": [2, 4]},
        {"cyclic_length": 2, "base_index": 5, "chord": [5, 7]},
    ]


def test_p19_pilot_profile_option_counts_are_pinned() -> None:
    payload = expected_pilot_payload()
    expected = {
        "0": {
            "distance_profile": [4, 1, 1, 1, 1],
            "labelled_option_count": 70,
        },
        "6": {
            "distance_profile": [4, 4],
            "labelled_option_count": 35,
        },
    }

    assert payload["profile_option_counts"] == expected
    assert all(row["profile_option_counts"] == expected for row in payload["rows"])


def test_p19_pilot_payload_passes_independent_checker() -> None:
    payload = expected_pilot_payload()

    errors = validate_payload(payload)

    assert errors == []


def test_p19_pilot_summary_is_nonclaiming() -> None:
    payload = expected_pilot_payload()
    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT
        / "data"
        / "certificates"
        / "n9_base_apex_d3_p19_incidence_capacity_pilot.json",
        payload,
        errors,
    )

    assert summary["ok"] is True
    assert summary["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert summary["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert summary["profile_ledger_id"] == "P19"
    assert summary["representative_count"] == 8
    assert summary["common_dihedral_pair_class_count"] == 56
    assert summary["summary_common_dihedral_pair_class_count"] == 56
    assert summary["realizability_state"] == "UNKNOWN"
    assert summary["incidence_state"] == "UNKNOWN"


def test_p19_pilot_checker_rejects_tampered_claim_scope() -> None:
    payload = expected_pilot_payload()
    payload["claim_scope"] = (
        "Focused P19 ledger; not a proof and not a global status update."
    )

    errors = validate_payload(payload)

    assert any("claim_scope mismatch" in error for error in errors)
    assert any("not a counterexample" in error for error in errors)
    assert any("incidence-completeness" in error for error in errors)
    assert any("geometric realizability" in error for error in errors)


def test_p19_pilot_checker_rejects_tampered_provenance() -> None:
    payload = expected_pilot_payload()
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py"
    )

    errors = validate_payload(payload)

    assert any("provenance mismatch" in error for error in errors)


def test_p19_pilot_checker_rejects_tampered_source_artifacts() -> None:
    payload = expected_pilot_payload()
    payload["source_artifacts"]["d3_escape_frontier_packet"] = (
        "data/certificates/n9_base_apex_d3_escape_slice.json"
    )

    errors = validate_payload(payload)

    assert any("source_artifacts mismatch" in error for error in errors)


def test_p19_pilot_checker_rejects_drifted_d3_packet_source(monkeypatch) -> None:
    payload = expected_pilot_payload()
    source_path = (
        ROOT / checker.EXPECTED_SOURCE_ARTIFACTS["d3_escape_frontier_packet"]
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    source["representatives"][0]["common_dihedral_pair_class_count"] += 1
    original_load = checker.load_source_artifact

    def fake_load_source_artifact(path: Path, label: str, errors: list[str]) -> object:
        if label == "d3_escape_frontier_packet":
            return source
        return original_load(path, label, errors)

    monkeypatch.setattr(checker, "load_source_artifact", fake_load_source_artifact)

    errors = validate_payload(payload)

    assert any(
        "does not match d3_escape_frontier_packet source field "
        "common_dihedral_pair_class_count" in error
        for error in errors
    )


def test_p19_pilot_checker_rejects_drifted_crosswalk_source(monkeypatch) -> None:
    payload = expected_pilot_payload()
    source_path = (
        ROOT / checker.EXPECTED_SOURCE_ARTIFACTS["low_excess_escape_crosswalk"]
    )
    source = json.loads(source_path.read_text(encoding="utf-8"))
    for row in source["crosswalk_rows"]:
        if row["profile_ledger_id"] == "P19" and row["escape_class_id"] == "X00":
            row["common_dihedral_pair_class_count"] += 1
            break
    original_load = checker.load_source_artifact

    def fake_load_source_artifact(path: Path, label: str, errors: list[str]) -> object:
        if label == "low_excess_escape_crosswalk":
            return source
        return original_load(path, label, errors)

    monkeypatch.setattr(checker, "load_source_artifact", fake_load_source_artifact)

    errors = validate_payload(payload)

    assert any(
        "does not match low_excess_escape_crosswalk source field "
        "common_dihedral_pair_class_count" in error
        for error in errors
    )


def test_p19_pilot_checker_rejects_unknown_top_level_key() -> None:
    payload = expected_pilot_payload()
    payload["extra_claim"] = "none"

    errors = validate_payload(payload)

    assert any("top-level keys" in error for error in errors)


def test_p19_pilot_checker_rejects_bool_top_level_int() -> None:
    payload = expected_pilot_payload()
    payload["n"] = True

    errors = validate_payload(payload)

    assert any("n must be int" in error for error in errors)


def test_p19_pilot_checker_rejects_bool_nested_int() -> None:
    payload = expected_pilot_payload()
    payload["rows"][0]["common_dihedral_pair_class_count"] = True

    errors = validate_payload(payload)

    assert any(
        "common_dihedral_pair_class_count must be an int" in error for error in errors
    )


def test_p19_pilot_checker_rejects_representative_reordering() -> None:
    payload = expected_pilot_payload()
    payload["rows"] = list(reversed(payload["rows"]))

    errors = validate_payload(payload)

    assert any("rows[0].representative_id" in error for error in errors)
    assert any("rows must be ordered R000..R007" in error for error in errors)
    assert any("payload.rows[0].representative_id" in error for error in errors)


def test_p19_pilot_checker_rejects_malformed_row_without_crashing() -> None:
    payload = expected_pilot_payload()
    payload["rows"][0]["deficient_base_chords"] = [{"cyclic_length": True}]

    errors = validate_payload(payload)
    summary = summary_payload(
        ROOT
        / "data"
        / "certificates"
        / "n9_base_apex_d3_p19_incidence_capacity_pilot.json",
        payload,
        errors,
    )

    assert any("deficient_base_chords[0] keys mismatch" in error for error in errors)
    assert any("cyclic_length must be an int" in error for error in errors)
    assert summary["ok"] is False


def test_p19_pilot_checker_rejects_malformed_escape_without_crashing() -> None:
    payload = expected_pilot_payload()
    payload["rows"][0]["canonical_escape_placement"] = {
        "spoiled_length2": [0, 0],
        "spoiled_length3": [9],
    }

    errors = validate_payload(payload)

    assert any("spoiled_length2 must be sorted unique ints" in error for error in errors)
    assert any("indices must be in range" in error for error in errors)


def test_p19_pilot_checker_cli_json(tmp_path: Path) -> None:
    artifact = tmp_path / "n9_base_apex_d3_p19_incidence_capacity_pilot.json"
    artifact.write_text(
        json.dumps(expected_pilot_payload(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_base_apex_d3_p19_incidence_capacity_pilot.py",
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
    assert payload["representative_count"] == 8
    assert payload["common_dihedral_pair_class_count"] == 56


def test_p19_pilot_analyzer_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_n9_base_apex_d3_p19_incidence_capacity_pilot.py",
            "--assert-expected",
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
    assert payload["profile_ledger_id"] == "P19"
    assert payload["common_dihedral_pair_class_count"] == 56
