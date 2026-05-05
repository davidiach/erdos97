from __future__ import annotations

import itertools
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import check_sparse_order_survivors as sparse_orders  # noqa: E402
from check_kalmanson_two_order_search import _prepare_vector_tables  # noqa: E402


ARTIFACT = ROOT / "data" / "certificates" / "c25_c29_sparse_frontier_probe.json"


def _has_kalmanson_inverse_pair(n: int, offsets: list[int], order: list[int]) -> bool:
    quad_ids, inverse_id = _prepare_vector_tables(n, offsets)
    seen: dict[int, tuple[int, tuple[int, int, int, int]]] = {}
    for quad in itertools.combinations(order, 4):
        for kind, vector_id in enumerate(quad_ids[quad]):
            inverse = inverse_id[vector_id]
            if inverse >= 0 and inverse in seen:
                return True
            seen.setdefault(vector_id, (kind, quad))
    return False


def test_c25_c29_sparse_frontier_probe_records_expected_cases() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    assert artifact["type"] == "c25_c29_sparse_frontier_probe_v1"
    assert artifact["trust"] == "FIXED_ORDER_DIAGNOSTIC"

    by_case = {row["case"]: row for row in artifact["cases"]}
    assert set(by_case) == {
        "C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor",
        "C29_sidon_1_3_7_15:z3_kalmanson_survivor",
    }

    c25 = by_case["C25_sidon_2_5_9_14:kalmanson_z3_step7_survivor"]
    assert c25["conclusion"] == "dead_end_for_this_order"
    assert c25["vertex_circle"]["obstructed"] is True
    assert c25["altman_linear_certificate"]["obstructed"] is True

    c29 = by_case["C29_sidon_1_3_7_15:z3_kalmanson_survivor"]
    assert c29["conclusion"] == "fixed_order_stress_test_for_stronger_filters"
    assert c29["sparse_order_filter_sweep"]["survives_current_exact_filters"] is True
    assert c29["metric_order_lp"]["status"] == "PASS_METRIC_ORDER_LP_RELAXATION"
    assert c29["row_circle_ptolemy_nlp"]["status"] == "NOT_COMPLETED_TOO_SLOW"


def test_c25_c29_sparse_frontier_probe_matches_exact_filter_sweep() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    patterns = sparse_orders.built_in_patterns()

    for row in artifact["cases"]:
        pattern = patterns[row["pattern"]]
        observed = sparse_orders.evaluate_order(pattern, row["order"], "artifact")

        assert observed["vertex_circle"]["obstructed"] == row["vertex_circle"][
            "obstructed"
        ]
        assert observed["altman_linear_certificate"]["obstructed"] == row[
            "altman_linear_certificate"
        ]["obstructed"]
        assert observed["survives_pre_kalmanson_filters"] == row[
            "sparse_order_filter_sweep"
        ]["survives_pre_kalmanson_filters"]


def test_c25_c29_orders_have_no_two_inequality_kalmanson_inverse_pair() -> None:
    artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
    by_pattern = {row["pattern"]: row for row in artifact["cases"]}

    assert not _has_kalmanson_inverse_pair(
        25,
        [2, 5, 9, 14],
        by_pattern["C25_sidon_2_5_9_14"]["order"],
    )
    assert not _has_kalmanson_inverse_pair(
        29,
        [1, 3, 7, 15],
        by_pattern["C29_sidon_1_3_7_15"]["order"],
    )
