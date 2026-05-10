from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from scripts.check_n9_t10_paired_square_entry import (
    DEFAULT_ARTIFACT,
    DEFAULT_CLASSIFICATION,
    DEFAULT_STRICT_CYCLE_PACKET,
    load_json,
    payload,
    validate_payload,
)

ROOT = Path(__file__).resolve().parents[1]


def test_n9_t10_paired_square_entry_counts_and_scope() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)

    errors = validate_payload(object_payload, recompute=False)

    assert errors == []
    assert object_payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert object_payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "not a proof of n=9" in object_payload["claim_scope"]
    assert "not a counterexample" in object_payload["claim_scope"]
    assert object_payload["template_id"] == "T10"
    assert object_payload["assignment_count"] == 18
    assert object_payload["hit_assignment_count"] == 18
    assert object_payload["miss_assignment_count"] == 0
    assert object_payload["total_hit_count"] == 54
    assert (
        object_payload["records_digest"]
        == "e32ff6014b1388fa733ad1fdb244c945114e91d059374259c6eeb1742ba89558"
    )


def test_n9_t10_paired_square_entry_records_literal_singleton_entries() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)

    for record in object_payload["records"]:
        assert record["status"] == "paired_square_entry_found"
        entry = record["paired_square_entry"]
        assert entry["nonselected_class_is_singleton"] is True
        assert entry["nonselected_class_members"] == [entry["residual_pair"]]
        selected_key = entry["selected_class_key"]
        nonselected_key = entry["nonselected_class_key"]

        a_square = entry["a_square"]
        assert a_square["forced_orientation"] == "A"
        assert a_square["literal_square_lift"] is True
        assert a_square["quotient_vector"] == {
            selected_key: 1,
            nonselected_key: -1,
        }

        b_square = entry["b_square"]
        assert b_square["forced_orientation"] == "B"
        assert b_square["literal_square_lift"] is True
        assert b_square["quotient_vector"] == {
            selected_key: -1,
            nonselected_key: 1,
        }


def test_n9_t10_paired_square_entry_matches_recomputed_payload() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)
    expected_payload = payload(
        classification=load_json(DEFAULT_CLASSIFICATION),
        strict_cycle_packet=load_json(DEFAULT_STRICT_CYCLE_PACKET),
    )

    assert object_payload == expected_payload


def test_n9_t10_paired_square_entry_rejects_tampered_vector() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)
    tampered = copy.deepcopy(object_payload)
    tampered["records"][0]["paired_square_entry"]["a_square"]["quotient_vector"] = {}

    errors = validate_payload(tampered, recompute=False)

    assert any("invalid A-square reduction" in error for error in errors)


def test_n9_t10_paired_square_entry_rejects_tampered_raw_pairs() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)
    tampered = copy.deepcopy(object_payload)
    tampered["records"][0]["paired_square_entry"]["b_square"]["positive_pairs"] = []

    errors = validate_payload(tampered, recompute=False)

    assert any("invalid B-square reduction" in error for error in errors)


def test_n9_t10_paired_square_entry_rejects_tampered_orientation() -> None:
    object_payload = load_json(DEFAULT_ARTIFACT)
    tampered = copy.deepcopy(object_payload)
    tampered["records"][0]["paired_square_entry"]["a_square"]["selected_witness"] = (
        tampered["records"][0]["paired_square_entry"]["b_square"]["selected_witness"]
    )

    errors = validate_payload(tampered, recompute=False)

    assert any("invalid A-square reduction" in error for error in errors)


def test_n9_t10_paired_square_entry_checker_cli() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_t10_paired_square_entry.py",
            "--check",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    summary = json.loads(result.stdout)
    assert summary["assignment_count"] == 18
    assert summary["hit_assignment_count"] == 18
    assert summary["total_hit_count"] == 54
