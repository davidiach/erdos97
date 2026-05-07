from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from erdos97.n10_secondary_singleton_replay import (
    ROW0_CHOICES_COVERED,
    TOTAL_COUNTS,
    TOTAL_FULL,
    TOTAL_NODES,
    TRUST,
    validate_secondary_payload,
)
from scripts.check_n10_secondary_singleton_replay import (
    DEFAULT_ARTIFACT,
    DEFAULT_PRIMARY_ARTIFACT,
    load_artifact,
    summary_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def _payloads() -> tuple[dict[str, object], dict[str, object]]:
    return load_artifact(DEFAULT_ARTIFACT), load_artifact(DEFAULT_PRIMARY_ARTIFACT)


def test_n10_secondary_replay_expected_counts_and_primary_prefix() -> None:
    payload, primary = _payloads()

    errors = validate_secondary_payload(payload, primary)
    summary = summary_payload(DEFAULT_ARTIFACT, DEFAULT_PRIMARY_ARTIFACT, payload, primary, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["primary_prefix_match"] is True
    assert payload["trust"] == TRUST
    assert payload["row0_choices_covered"] == ROW0_CHOICES_COVERED
    assert payload["total_nodes"] == TOTAL_NODES
    assert payload["total_full"] == TOTAL_FULL
    assert payload["total_counts"] == TOTAL_COUNTS


def test_n10_secondary_replay_rows_are_first_five_singletons() -> None:
    payload, primary = _payloads()

    for idx, row in enumerate(payload["rows"]):  # type: ignore[index]
        primary_row = primary["rows"][idx]  # type: ignore[index]
        assert row["row0_index"] == idx
        assert row["row0_witnesses"] == primary_row["row0_witnesses"]
        assert row["nodes"] == primary_row["nodes"]
        assert row["full"] == primary_row["full"] == 0
        assert row["counts"] == primary_row["counts"]
        assert row["full_survivors"] == []


def test_n10_secondary_replay_rejects_wrong_trust() -> None:
    payload, primary = _payloads()
    payload["trust"] = "MACHINE_CHECKED_FINITE_CASE_DRAFT_REVIEW_PENDING"

    errors = validate_secondary_payload(payload, primary)

    assert any("trust mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_wrong_static_parameters() -> None:
    payload, primary = _payloads()
    payload["type"] = "n10_vertex_circle_singleton_slices_v1"
    payload["n"] = 9
    payload["row_size"] = 3
    payload["pair_cap"] = 3
    payload["max_indegree"] = 7
    payload["triple_cap"] = 2
    payload["row0_choices_covered"] = 6

    errors = validate_secondary_payload(payload, primary)

    assert any("type mismatch" in error for error in errors)
    assert any("n mismatch" in error for error in errors)
    assert any("row_size mismatch" in error for error in errors)
    assert any("pair_cap mismatch" in error for error in errors)
    assert any("max_indegree mismatch" in error for error in errors)
    assert any("triple_cap mismatch" in error for error in errors)
    assert any("row0_choices_covered mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_non_prefix_row_index() -> None:
    payload, primary = _payloads()
    payload["rows"][3]["row0_index"] = 6  # type: ignore[index]

    errors = validate_secondary_payload(payload, primary)

    assert any("row 3 row0_index mismatch" in error for error in errors)
    assert any("row0 indices mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_nonempty_full_survivors() -> None:
    payload, primary = _payloads()
    payload["rows"][0]["full_survivors"] = [{"selected_rows": []}]  # type: ignore[index]

    errors = validate_secondary_payload(payload, primary)

    assert any("row 0 full_survivors mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_changed_row_counts() -> None:
    payload, primary = _payloads()
    payload["rows"][1]["counts"]["partial_self_edge"] += 1  # type: ignore[index]

    errors = validate_secondary_payload(payload, primary)

    assert any("row 1 counts mismatch" in error for error in errors)
    assert any("row count sum mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_top_level_total_mismatch() -> None:
    payload, primary = _payloads()
    payload["total_nodes"] += 1  # type: ignore[operator]

    errors = validate_secondary_payload(payload, primary)

    assert any("total_nodes mismatch" in error for error in errors)
    assert not any("row node sum mismatch" in error for error in errors)


def test_n10_secondary_replay_rejects_bool_elapsed_metadata() -> None:
    payload, primary = _payloads()
    payload["total_elapsed_seconds"] = True
    payload["rows"][0]["elapsed_seconds"] = False  # type: ignore[index]

    errors = validate_secondary_payload(payload, primary)

    assert any("total_elapsed_seconds must be nonnegative numeric metadata" in error for error in errors)
    assert any("row 0 elapsed_seconds must be nonnegative numeric metadata" in error for error in errors)


def test_n10_secondary_replay_does_not_bless_legacy_purpose_text() -> None:
    payload, primary = _payloads()
    payload["purpose"] = "legacy text not treated as an expected scoped claim"

    errors = validate_secondary_payload(payload, primary)

    assert errors == []


def test_n10_secondary_replay_rejects_primary_prefix_mismatch() -> None:
    payload, primary = _payloads()
    primary = copy.deepcopy(primary)
    primary["rows"][2]["nodes"] += 1  # type: ignore[index,operator]

    errors = validate_secondary_payload(payload, primary)

    assert any(
        "primary n=10 singleton artifact invalid" in error
        or "row 2 primary-prefix nodes mismatch" in error
        for error in errors
    )


def test_n10_secondary_replay_rejects_witness_mismatch() -> None:
    payload, primary = _payloads()
    payload["rows"][4]["row0_witnesses"] = [1, 2, 3, 9]  # type: ignore[index]

    errors = validate_secondary_payload(payload, primary)

    assert any("row 4 row0_witnesses mismatch" in error for error in errors)
    assert any("row 4 generic witness order mismatch" in error for error in errors)


def test_n10_secondary_replay_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n10_secondary_singleton_replay.py",
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
    summary = json.loads(result.stdout)
    assert summary["ok"] is True
    assert summary["primary_prefix_match"] is True
    assert summary["row0_choices_covered"] == 5
