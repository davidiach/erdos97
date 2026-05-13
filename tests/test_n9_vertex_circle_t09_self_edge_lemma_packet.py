from __future__ import annotations

import copy

from erdos97.n9_vertex_circle_t09_self_edge_lemma_packet import (
    assert_expected_t09_self_edge_lemma_packet,
)
from scripts.check_n9_vertex_circle_t09_self_edge_lemma_packet import (
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
        if template["template_id"] == "T09":
            return template
    raise AssertionError("missing T09 template")


def test_t09_self_edge_lemma_packet_counts_and_scope() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert_expected_t09_self_edge_lemma_packet(payload)
    assert payload["status"] == "REVIEW_PENDING_DIAGNOSTIC_ONLY"
    assert payload["trust"] == "REVIEW_PENDING_DIAGNOSTIC"
    assert "proof-mining scaffolding only" in payload["claim_scope"]
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a counterexample" in payload["claim_scope"]
    assert "not an independent review" in payload["claim_scope"]
    assert payload["template_id"] == "T09"
    assert payload["template_key"] == "self_edge|rows=6|strict_edges=54|conflicts=2:1:1x5,3:1:0x2,3:1:1x4,3:2:1x2"
    assert payload["assignment_count"] == 18
    assert payload["assignment_ids"] == [
        "A003",
        "A010",
        "A017",
        "A030",
        "A033",
        "A044",
        "A049",
        "A073",
        "A107",
        "A108",
        "A123",
        "A130",
        "A135",
        "A142",
        "A144",
        "A160",
        "A161",
        "A169",
    ]
    assert payload["family_count"] == 1
    assert payload["family_ids"] == ["F03"]
    assert payload["family_assignment_counts"] == {"F03": 18}
    assert payload["family_orbit_sizes"] == {"F03": 18}
    assert payload["orbit_size_sum"] == 18
    assert payload["core_size"] == 6
    assert payload["strict_edge_count"] == 54
    assert payload["path_length_counts"] == {"6": 18}
    assert payload["shared_endpoint_counts"] == {"1": 18}
    assert payload["selected_path_shape_counts"] == {"2:1:1:path=6": 18}


def test_t09_self_edge_lemma_packet_records_expected_local_shape() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)

    assert packet["family_id"] == "F03"
    assert packet["core_selected_rows"] == [
        [0, 1, 2, 3, 8],
        [1, 0, 3, 5, 7],
        [2, 1, 3, 4, 6],
        [3, 2, 4, 5, 8],
        [4, 0, 3, 6, 8],
        [8, 0, 1, 4, 7],
    ]
    assert packet["strict_inequality"]["row"] == 0  # type: ignore[index]
    assert packet["strict_inequality"]["witness_order"] == [1, 2, 3, 8]  # type: ignore[index]
    assert packet["strict_inequality"]["outer_pair"] == [1, 3]  # type: ignore[index]
    assert packet["strict_inequality"]["inner_pair"] == [1, 2]  # type: ignore[index]
    assert packet["strict_inequality"]["inner_interval"] == [0, 1]  # type: ignore[index]
    assert packet["equality_chain"] == [[1, 3], [0, 1], [0, 8], [4, 8], [3, 4], [2, 3], [1, 2]]
    assert packet["local_lemma"]["review_status"] == "review_pending"  # type: ignore[index]
    assert "six listed selected rows" in packet["local_lemma"]["hypothesis_scope"]  # type: ignore[index]
    assert packet["replay"]["status"] == "self_edge"  # type: ignore[index]
    assert packet["replay"]["selected_row_count"] == 6  # type: ignore[index]
    assert packet["replay"]["strict_edge_count"] == 54  # type: ignore[index]
    assert packet["replay"]["self_edge_conflict_count"] == 13  # type: ignore[index]
    assert packet["replay"]["cycle_edge_count"] == 0  # type: ignore[index]
    assert packet["replay"]["primary_self_edge_conflict"]["row"] == 0  # type: ignore[index]


def test_t09_self_edge_lemma_packet_checker_passes_lightweight() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload, recompute=False)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["template_id"] == "T09"
    assert summary["family_count"] == 1
    assert summary["assignment_count"] == 18
    assert summary["replay_statuses"] == ["self_edge"]


def test_t09_self_edge_lemma_packet_rejects_tampered_equality_path() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["distance_equality"]["path"][0]["next_pair"] = [3, 6]  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F03 distance_equality mismatch" in error for error in errors)
    assert any("expected T09 self-edge lemma packet" in error for error in errors)


def test_t09_self_edge_lemma_packet_rejects_tampered_strict_row() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["strict_inequality"]["row"] = 1  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F03 strict_inequality mismatch" in error for error in errors)


def test_t09_self_edge_lemma_packet_rejects_wrong_conflict_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet = _family_packet(payload)
    packet["replay"]["self_edge_conflict_count"] = 1  # type: ignore[index]

    errors = validate_payload(payload, recompute=False)

    assert any("F03 replay self_edge_conflict_count mismatch" in error for error in errors)


def test_t09_self_edge_lemma_packet_rejects_missing_no_proof_note() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["interpretation"] = [
        item for item in payload["interpretation"] if item != "No proof of the n=9 case is claimed."
    ]

    errors = validate_payload(payload, recompute=False)

    assert any("no-proof" in error for error in errors)


def test_t09_self_edge_lemma_packet_detects_source_packet_mismatch() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    sources = copy.deepcopy(load_source_payloads())
    template = _template_record(sources)
    template["family_records"][0]["strict_inequality"]["row"] = 1

    errors = validate_payload(payload, source_payloads=sources, recompute=False)

    assert any(
        "source self-edge template packet invalid" in error
        or "source-bound T09 self-edge lemma packet failed" in error
        for error in errors
    )
