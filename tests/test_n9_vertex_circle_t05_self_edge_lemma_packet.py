from __future__ import annotations

import copy

from erdos97.n9_vertex_circle_t05_self_edge_lemma_packet import (
    assert_expected_t05_self_edge_lemma_packet,
)
from scripts.check_n9_vertex_circle_t05_self_edge_lemma_packet import (
    DEFAULT_ARTIFACT,
    load_artifact,
    load_source_payloads,
    summary_payload,
    validate_payload,
)


def _family_packet(payload: dict[str, object]) -> dict[str, object]:
    packets = payload["family_packets"]  # type: ignore[index]
    assert isinstance(packets, list)
    assert len(packets) == 1
    return packets[0]  # type: ignore[return-value]


def _template_record(source_payloads: dict[str, object]) -> dict[str, object]:
    for template in source_payloads["self_edge_packet"]["templates"]:  # type: ignore[index]
        if template["template_id"] == "T05":
            return template
    raise AssertionError("missing T05 template")


def test_t05_self_edge_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t05_self_edge_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T05"
    assert payload["template_key"] == "self_edge|rows=4|strict_edges=36|conflicts=3:1:0x1,3:1:1x1"
    assert payload["assignment_count"] == 18
    assert payload["assignment_ids"] == [
        "A013",
        "A029",
        "A036",
        "A038",
        "A053",
        "A057",
        "A059",
        "A062",
        "A072",
        "A088",
        "A090",
        "A100",
        "A105",
        "A120",
        "A129",
        "A133",
        "A162",
        "A170",
    ]
    assert payload["family_count"] == 1
    assert payload["family_ids"] == ["F10"]
    assert payload["family_assignment_counts"] == {"F10": 18}
    assert payload["family_orbit_sizes"] == {"F10": 18}
    assert payload["orbit_size_sum"] == 18
    assert payload["core_size"] == 4
    assert payload["strict_edge_count"] == 36
    assert payload["path_length_counts"] == {"3": 18}
    assert payload["shared_endpoint_counts"] == {"1": 18}
    assert payload["selected_path_shape_counts"] == {"3:1:1:path=3": 18}


def test_t05_self_edge_lemma_packet_records_expected_local_shape() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)

    assert packet["family_id"] == "F10"
    assert packet["core_selected_rows"] == [
        [0, 1, 2, 4, 8],
        [2, 1, 3, 4, 7],
        [7, 2, 5, 6, 8],
        [8, 0, 1, 6, 7],
    ]
    assert packet["strict_inequality"]["row"] == 0  # type: ignore[index]
    assert packet["strict_inequality"]["witness_order"] == [1, 2, 4, 8]  # type: ignore[index]
    assert packet["strict_inequality"]["outer_pair"] == [1, 8]  # type: ignore[index]
    assert packet["strict_inequality"]["inner_pair"] == [1, 2]  # type: ignore[index]
    assert packet["strict_inequality"]["inner_interval"] == [0, 1]  # type: ignore[index]
    assert packet["equality_chain"] == [[1, 8], [7, 8], [2, 7], [1, 2]]
    assert packet["local_lemma"]["review_status"] == "review_pending"  # type: ignore[index]
    assert "four listed selected rows" in packet["local_lemma"]["hypothesis_scope"]  # type: ignore[index]
    assert packet["replay"]["status"] == "self_edge"  # type: ignore[index]
    assert packet["replay"]["selected_row_count"] == 4  # type: ignore[index]
    assert packet["replay"]["strict_edge_count"] == 36  # type: ignore[index]
    assert packet["replay"]["self_edge_conflict_count"] == 2  # type: ignore[index]
    assert packet["replay"]["cycle_edge_count"] == 0  # type: ignore[index]
    assert packet["replay"]["primary_self_edge_conflict"]["row"] == 0  # type: ignore[index]


def test_t05_self_edge_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T05"
    assert summary["family_count"] == 1
    assert summary["assignment_count"] == 18
    assert summary["replay_statuses"] == ["self_edge"]


def test_t05_self_edge_lemma_packet_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["distance_equality"]["path"][0]["next_pair"] = [3, 6]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F10 distance_equality mismatch" in error for error in errors)
    assert any("expected T05 self-edge lemma packet" in error for error in errors)


def test_t05_self_edge_lemma_packet_rejects_tampered_strict_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["strict_inequality"]["row"] = 1  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F10 strict_inequality mismatch" in error for error in errors)


def test_t05_self_edge_lemma_packet_rejects_wrong_conflict_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["replay"]["self_edge_conflict_count"] = 1  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F10 replay self_edge_conflict_count mismatch" in error for error in errors)


def test_t05_self_edge_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t05_self_edge_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    template = _template_record(sources)
    template["family_records"][0]["strict_inequality"]["row"] = 1

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source self-edge template packet invalid" in error
        or "source-bound T05 self-edge lemma packet failed" in error
        for error in errors
    )
