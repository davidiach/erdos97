from __future__ import annotations

import json
from pathlib import Path

import pytest

from erdos97.phi4_frontier import (
    built_in_natural_order_cases,
    n9_rectangle_trap_case,
    scan_cases,
    scan_payload,
    sparse_order_cases_from_payload,
)
from erdos97.search import built_in_patterns


def sparse_order_payload() -> dict[str, object]:
    path = Path("data/certificates/sparse_order_survivors.json")
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def test_phi4_frontier_scan_has_only_registered_n9_hit() -> None:
    patterns = built_in_patterns()
    cases = [n9_rectangle_trap_case()]
    cases.extend(built_in_natural_order_cases(patterns))
    cases.extend(sparse_order_cases_from_payload(sparse_order_payload(), patterns))

    rows = scan_cases(cases)
    payload = scan_payload(rows)
    hits = [row for row in rows if row["obstructed_by_phi4_rectangle_trap"]]

    assert payload["case_count"] == 17
    assert payload["obstructed_case_count"] == 1
    assert [row["case"] for row in hits] == [
        "N9_phi4_rectangle_trap_selected_witness_pattern:natural_order"
    ]
    assert hits[0]["rectangle_trap_certificates"][0]["phi_cycle"] == [
        [0, 6],
        [2, 8],
        [1, 5],
        [4, 7],
    ]


def test_sparse_order_frontier_cases_are_phi4_blind_spots() -> None:
    patterns = built_in_patterns()
    cases = sparse_order_cases_from_payload(sparse_order_payload(), patterns)

    rows = scan_cases(cases)

    assert {row["case"] for row in rows} == {
        "C13_sidon_1_2_4_10:sample_full_filter_survivor",
        "C19_skew:vertex_circle_survivor",
    }
    assert all(row["phi_edges"] == 0 for row in rows)
    assert all(not row["obstructed_by_phi4_rectangle_trap"] for row in rows)


def test_sparse_order_frontier_rejects_malformed_order() -> None:
    patterns = built_in_patterns()
    payload = sparse_order_payload()
    cases = payload["cases"]
    assert isinstance(cases, list)
    bad_case = dict(cases[0])
    bad_order = list(bad_case["order"])
    bad_order[-1] = bad_order[0]
    bad_case["order"] = bad_order
    payload["cases"] = [bad_case]

    with pytest.raises(ValueError, match="order is not a permutation"):
        sparse_order_cases_from_payload(payload, patterns)
