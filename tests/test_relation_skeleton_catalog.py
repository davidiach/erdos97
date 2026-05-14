from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.relation_skeleton_catalog import (
    EXPECTED_SKELETON_IDS,
    EXPECTED_SOURCE_ARTIFACTS,
    assert_expected_relation_skeleton_catalog,
    relation_skeleton_catalog_payload,
)
from scripts.check_relation_skeleton_catalog import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def _skeletons_by_id(payload: dict[str, object]) -> dict[str, dict[str, object]]:
    return {item["skeleton_id"]: item for item in payload["skeletons"]}  # type: ignore[index]


def test_relation_skeleton_catalog_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_relation_skeleton_catalog(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["skeleton_count"] == 7
    assert payload["skeleton_ids"] == list(EXPECTED_SKELETON_IDS)
    assert payload["contradiction_type_counts"] == {
        "strict_directed_cycle": 3,
        "strict_self_edge": 4,
    }


def test_relation_skeleton_catalog_records_t01_self_edge() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeleton = _skeletons_by_id(payload)["VC-T01-F09-strict-self-edge"]

    assert skeleton["source_packet"] == EXPECTED_SOURCE_ARTIFACTS[0]
    assert skeleton["source_template_id"] == "T01"
    assert skeleton["source_family_id"] == "F09"
    assert skeleton["contradiction_type"] == "strict_self_edge"
    assert skeleton["coverage"]["assignment_count"] == 6  # type: ignore[index]
    assert skeleton["hypotheses"]["selected_rows"] == [  # type: ignore[index]
        [0, 1, 2, 4, 8],
        [1, 0, 3, 5, 8],
        [2, 0, 1, 4, 6],
    ]
    assert skeleton["relation_quotient"]["equality_chains"] == [  # type: ignore[index]
        [[1, 8], [0, 1], [0, 2], [1, 2]]
    ]
    assert skeleton["relation_quotient"]["strict_edges"] == [  # type: ignore[index]
        {
            "source": "vertex_circle_chord_monotonicity",
            "row": 0,
            "witness_order": [1, 2, 4, 8],
            "outer_pair": [1, 8],
            "inner_pair": [1, 2],
            "outer_class": [0, 1],
            "inner_class": [0, 1],
            "outer_span": 3,
            "inner_span": 1,
        }
    ]
    assert skeleton["conclusion"]["kind"] == "strict_self_edge"  # type: ignore[index]
    assert skeleton["conclusion"]["quotient_class"] == [0, 1]  # type: ignore[index]


def test_relation_skeleton_catalog_records_t10_strict_cycle() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeleton = _skeletons_by_id(payload)["VC-T10-F12-strict-directed-cycle"]

    assert skeleton["source_packet"] == EXPECTED_SOURCE_ARTIFACTS[3]
    assert skeleton["source_template_id"] == "T10"
    assert skeleton["source_family_id"] == "F12"
    assert skeleton["contradiction_type"] == "strict_directed_cycle"
    assert skeleton["coverage"]["assignment_count"] == 18  # type: ignore[index]
    assert skeleton["hypotheses"]["selected_rows"] == [  # type: ignore[index]
        [0, 1, 2, 5, 6],
        [3, 0, 1, 4, 6],
        [6, 1, 3, 4, 7],
        [8, 0, 3, 6, 7],
    ]
    assert skeleton["relation_quotient"]["equality_chains"] == [  # type: ignore[index]
        [[0, 3], [3, 6], [1, 6]],
        [[0, 1], [0, 6]],
    ]
    assert skeleton["conclusion"]["kind"] == "strict_directed_cycle"  # type: ignore[index]
    assert skeleton["conclusion"]["cycle_length"] == 2  # type: ignore[index]
    assert skeleton["conclusion"]["quotient_cycle"] == [  # type: ignore[index]
        {
            "cycle_step": 0,
            "strict_from_pair": [0, 6],
            "strict_to_pair": [0, 3],
            "equality_chain_to_next_outer_pair": [[0, 3], [3, 6], [1, 6]],
            "next_outer_pair": [1, 6],
        },
        {
            "cycle_step": 1,
            "strict_from_pair": [1, 6],
            "strict_to_pair": [0, 1],
            "equality_chain_to_next_outer_pair": [[0, 1], [0, 6]],
            "next_outer_pair": [0, 6],
        },
    ]


def test_relation_skeleton_catalog_records_new_self_edge_families() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeletons = _skeletons_by_id(payload)

    expected = {
        "VC-T03-F05-strict-self-edge": (
            EXPECTED_SOURCE_ARTIFACTS[1],
            "T03",
            "F05",
            18,
            [[3, 7], [2, 3], [1, 2], [1, 7]],
        ),
        "VC-T03-F15-strict-self-edge": (
            EXPECTED_SOURCE_ARTIFACTS[1],
            "T03",
            "F15",
            2,
            [[1, 4], [1, 2], [2, 3], [3, 4]],
        ),
        "VC-T04-F13-strict-self-edge": (
            EXPECTED_SOURCE_ARTIFACTS[2],
            "T04",
            "F13",
            2,
            [[1, 5], [3, 5], [1, 3], [1, 2]],
        ),
    }
    for skeleton_id, (source_packet, template_id, family_id, assignment_count, equality_chain) in expected.items():
        skeleton = skeletons[skeleton_id]
        assert skeleton["source_packet"] == source_packet
        assert skeleton["source_template_id"] == template_id
        assert skeleton["source_family_id"] == family_id
        assert skeleton["contradiction_type"] == "strict_self_edge"
        assert skeleton["coverage"]["assignment_count"] == assignment_count  # type: ignore[index]
        assert skeleton["relation_quotient"]["equality_chains"] == [equality_chain]  # type: ignore[index]
        assert len(skeleton["relation_quotient"]["strict_edges"]) == 1  # type: ignore[index]
        assert skeleton["conclusion"]["kind"] == "strict_self_edge"  # type: ignore[index]


def test_relation_skeleton_catalog_records_new_strict_cycle_families() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeletons = _skeletons_by_id(payload)

    expected = {
        "VC-T11-F07-strict-directed-cycle": (EXPECTED_SOURCE_ARTIFACTS[4], "T11", "F07", 6, 3),
        "VC-T12-F16-strict-directed-cycle": (EXPECTED_SOURCE_ARTIFACTS[5], "T12", "F16", 2, 3),
    }
    for skeleton_id, (source_packet, template_id, family_id, assignment_count, cycle_length) in expected.items():
        skeleton = skeletons[skeleton_id]
        assert skeleton["source_packet"] == source_packet
        assert skeleton["source_template_id"] == template_id
        assert skeleton["source_family_id"] == family_id
        assert skeleton["contradiction_type"] == "strict_directed_cycle"
        assert skeleton["coverage"]["assignment_count"] == assignment_count  # type: ignore[index]
        assert skeleton["conclusion"]["kind"] == "strict_directed_cycle"  # type: ignore[index]
        assert skeleton["conclusion"]["cycle_length"] == cycle_length  # type: ignore[index]
        assert len(skeleton["relation_quotient"]["strict_edges"]) == cycle_length  # type: ignore[index]


def test_relation_skeleton_catalog_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["skeleton_count"] == 7
    assert summary["skeleton_ids"] == list(EXPECTED_SKELETON_IDS)


def test_relation_skeleton_catalog_rejects_missing_global_guardrail() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if not item.startswith("No proof of Erdos")
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("global no-proof" in error for error in errors)


def test_relation_skeleton_catalog_rejects_tampered_t01_conclusion() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeleton = _skeletons_by_id(payload)["VC-T01-F09-strict-self-edge"]
    skeleton["conclusion"]["quotient_class"] = [0, 3]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("T01 quotient_class mismatch" in error for error in errors)
    assert any("expected relation skeleton catalog constants failed" in error for error in errors)


def test_relation_skeleton_catalog_rejects_tampered_t10_cycle() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    skeleton = _skeletons_by_id(payload)["VC-T10-F12-strict-directed-cycle"]
    skeleton["conclusion"]["cycle_length"] = 3  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("T10 cycle_length mismatch" in error for error in errors)
    assert any("expected relation skeleton catalog constants failed" in error for error in errors)


def test_relation_skeleton_catalog_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    sources["t01_packet"]["assignment_count"] = 7

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any("source T01 packet invalid" in error for error in errors)


@pytest.mark.artifact
def test_relation_skeleton_catalog_artifact_matches_generator() -> None:
    sources = load_source_payloads()
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == relation_skeleton_catalog_payload(
        sources["t01_packet"],
        sources["t03_packet"],
        sources["t04_packet"],
        sources["t10_packet"],
        sources["t11_packet"],
        sources["t12_packet"],
    )


@pytest.mark.artifact
def test_relation_skeleton_catalog_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_relation_skeleton_catalog.py",
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
    assert payload["skeleton_count"] == 7
    assert payload["skeleton_ids"] == list(EXPECTED_SKELETON_IDS)


@pytest.mark.artifact
def test_relation_skeleton_catalog_write_check_out(tmp_path: Path) -> None:
    out = tmp_path / "relation_skeleton_catalog.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_relation_skeleton_catalog.py",
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
    assert payload["artifact"] == str(out.resolve())


def test_relation_skeleton_catalog_write_check_rejects_mismatched_paths(tmp_path: Path) -> None:
    out = tmp_path / "relation_skeleton_catalog.json"

    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_relation_skeleton_catalog.py",
            "--write",
            "--check",
            "--assert-expected",
            "--artifact",
            str(DEFAULT_ARTIFACT),
            "--out",
            str(out),
            "--json",
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    assert "--write --check requires matching --artifact/--out" in result.stderr
