from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_vertex_circle_quotient,
    result_to_json,
)
from scripts.check_n9_row_ptolemy_admissible_gap_replay import (
    DEFAULT_ARTIFACT as DEFAULT_GAP_REPLAY_ARTIFACT,
    load_artifact,
)
from scripts.check_n9_row_ptolemy_gap_self_edge_cores import (
    DEFAULT_ARTIFACT,
    EXPECTED_CORE_CONFLICT_HISTOGRAM,
    EXPECTED_CORE_SIZE_COUNTS,
    EXPECTED_CORE_STRICT_EDGE_HISTOGRAM,
    EXPECTED_EQUALITY_PATH_LENGTH_HISTOGRAM,
    EXPECTED_MINIMAL_CORE_COUNT_HISTOGRAM,
    assert_expected_counts,
    self_edge_core_payload,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_gap_self_edge_core_scope_and_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_counts(payload)
    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an all-order obstruction" in payload["claim_scope"]
    assert "not an orderless abstract-incidence obstruction" in payload["claim_scope"]
    assert "not a geometric realizability count" in payload["claim_scope"]
    assert payload["assignment_indices"] == [22, 173]
    assert payload["core_row_index_sets"] == [[0, 2, 4], [0, 2, 4]]
    assert payload["core_size_counts"] == EXPECTED_CORE_SIZE_COUNTS
    assert payload["core_strict_edge_count_histogram"] == EXPECTED_CORE_STRICT_EDGE_HISTOGRAM
    assert (
        payload["core_self_edge_conflict_count_histogram"]
        == EXPECTED_CORE_CONFLICT_HISTOGRAM
    )
    assert (
        payload["equality_path_length_histogram"]
        == EXPECTED_EQUALITY_PATH_LENGTH_HISTOGRAM
    )
    assert (
        payload["minimal_self_edge_core_count_histogram"]
        == EXPECTED_MINIMAL_CORE_COUNT_HISTOGRAM
    )


def test_gap_self_edge_core_records_replay_and_are_minimal() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    for record in payload["records"]:
        replay = result_to_json(
            replay_vertex_circle_quotient(
                9,
                record["order"],
                parse_selected_rows(record["core_rows"]),
            )
        )

        assert record["family_id"] == "F13"
        assert record["template_id"] == "T04"
        assert replay == record["core_replay"]
        assert replay["status"] == "self_edge"
        assert replay["strict_edge_count"] == 27
        assert len(replay["self_edge_conflicts"]) == 1
        assert record["self_edge_conflict"] == replay["self_edge_conflicts"][0]
        assert record["minimality"]["minimal_self_edge_core_size"] == 3
        assert record["minimality"]["minimal_self_edge_core_count"] == 9
        assert record["minimality"]["proper_self_edge_subcore_count"] == 0
        assert record["minimality"]["proper_subcore_status_counts"] == {"ok": 6}
        assert len(record["selected_distance_equality_path"]) == 3


def test_gap_self_edge_core_equality_paths_connect_conflict_pairs() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    for record in payload["records"]:
        conflict = record["self_edge_conflict"]
        path = record["selected_distance_equality_path"]

        assert path[0]["from_pair"] == conflict["outer_pair"]
        assert path[-1]["to_pair"] == conflict["inner_pair"]
        for left, right in zip(path, path[1:]):
            assert left["to_pair"] == right["from_pair"]
        assert conflict["outer_class"] == conflict["inner_class"]


@pytest.mark.artifact
def test_gap_self_edge_core_artifact_matches_generator() -> None:
    gap_replay = load_artifact(DEFAULT_GAP_REPLAY_ARTIFACT)
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == self_edge_core_payload(gap_replay)


def test_gap_self_edge_core_checker_passes_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["record_count"] == 2
    assert summary["core_size_counts"] == {"3": 2}


def test_gap_self_edge_core_rejects_tampered_core_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["core_rows"][0]["witnesses"] = [1, 2, 3, 7]

    errors = validate_payload(payload, recompute=False)

    assert any("core_replay" in error or "equality path" in error for error in errors)


def test_gap_self_edge_core_rejects_core_rows_not_matching_source_indices() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    source = load_artifact(DEFAULT_GAP_REPLAY_ARTIFACT)
    source_record = source["records"][0]
    payload["records"][0]["core_rows"] = [
        {"row": index, "witnesses": source_record["selected_rows"][index]}
        for index in [1, 3, 5]
    ]

    errors = validate_payload(payload, source=source, recompute=False)

    assert any("core_rows" in error for error in errors)


def test_gap_self_edge_core_rejects_stale_minimality_and_source_summary() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["source_record"]["strict_edge_count"] = 80
    payload["records"][0]["minimality"]["minimal_self_edge_core_count"] = 8
    payload["records"][0]["minimality"]["lexicographic_min_core_row_indices"] = [
        1,
        3,
        5,
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("source_record" in error for error in errors)
    assert any("minimal_self_edge_core_count" in error for error in errors)
    assert any("lexicographic_min_core_row_indices" in error for error in errors)


def test_gap_self_edge_core_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"][0]["selected_distance_equality_path"][0]["to_pair"] = [0, 7]

    errors = validate_payload(payload, recompute=False)

    assert any("selected_distance_equality_path" in error for error in errors)


def test_gap_self_edge_core_rejects_duplicate_record_without_recompute() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["records"].append(dict(payload["records"][0]))

    errors = validate_payload(payload, recompute=False)

    assert any("record count" in error for error in errors)
    assert any("record assignment indices" in error for error in errors)


def test_gap_self_edge_core_rejects_missing_nonclaiming_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if "No proof" not in item
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("No proof" in error for error in errors)


def test_gap_self_edge_core_rejects_source_metadata_tamper() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifact"]["schema"] = "erdos97.stale"

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifact" in error for error in errors)


def test_gap_self_edge_core_write_check_validates_out_path(tmp_path: Path) -> None:
    out = tmp_path / "cores-out.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_gap_self_edge_cores.py",
            "--write",
            "--check",
            "--assert-expected",
            "--out",
            str(out),
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
    assert payload["artifact"].endswith("cores-out.json")
    assert out.exists()


def test_gap_self_edge_core_write_check_rejects_mismatched_artifact(
    tmp_path: Path,
) -> None:
    out = tmp_path / "cores-out.json"
    artifact = tmp_path / "other.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_gap_self_edge_cores.py",
            "--write",
            "--check",
            "--out",
            str(out),
            "--artifact",
            str(artifact),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "requires --artifact to match --out" in result.stderr


@pytest.mark.artifact
def test_gap_self_edge_core_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_gap_self_edge_cores.py",
            "--check",
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
    assert payload["ok"] is True
    assert payload["record_count"] == 2
