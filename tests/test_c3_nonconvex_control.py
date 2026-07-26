from __future__ import annotations

from scripts.check_c3_nonconvex_control import build_payload, validate_payload


def test_c3_nonconvex_control_exact_summary() -> None:
    payload = build_payload()
    summary = payload["summary"]

    assert validate_payload(payload) == []
    assert summary["point_count"] == 9
    assert summary["distinct_point_count"] == 9
    assert summary["common_squared_distance"] == 7
    assert summary["common_distance_pair_count"] == 18
    assert summary["common_distance_degree_histogram"] == {"4": 9}
    assert summary["convex_hull_vertex_count"] == 6


def test_c3_nonconvex_control_has_four_named_witnesses_per_center() -> None:
    payload = build_payload()

    assert len(payload["centers"]) == 9
    for record in payload["centers"]:
        assert len(record["witnesses"]) == 4
        assert record["squared_distances"] == [7, 7, 7, 7]


def test_c3_nonconvex_control_keeps_nonclaim_scope() -> None:
    payload = build_payload()

    assert payload["status"] == "EXACT_NONCONVEX_NEGATIVE_CONTROL"
    assert "not a counterexample" in payload["claim_scope"]
    assert "official/global open status" in payload["claim_scope"]
