from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FLOAT_FIELDS = {"max_margin"}
ACTIVE_SET_FIELDS = {
    "tight_altman_gap_count",
    "tight_triangle_inequality_count",
    "tight_vertex_strict_count",
}


def assert_payload_matches_artifact(
    artifact: dict[str, object], payload: dict[str, object]
) -> None:
    assert artifact.keys() == payload.keys()
    assert artifact["type"] == payload["type"]
    assert artifact["trust"] == payload["trust"]
    assert artifact["notes"] == payload["notes"]

    artifact_cases = artifact["cases"]
    payload_cases = payload["cases"]
    assert isinstance(artifact_cases, list)
    assert isinstance(payload_cases, list)
    assert len(artifact_cases) == len(payload_cases)

    for artifact_case, payload_case in zip(artifact_cases, payload_cases):
        assert isinstance(artifact_case, dict)
        assert isinstance(payload_case, dict)
        assert artifact_case.keys() == payload_case.keys()
        for key in artifact_case:
            if key in FLOAT_FIELDS:
                assert math.isclose(
                    artifact_case[key],
                    payload_case[key],
                    rel_tol=1e-12,
                    abs_tol=1e-15,
                )
            elif key in ACTIVE_SET_FIELDS:
                # HiGHS may return a different optimal point on the same LP
                # face across SciPy/Python builds, so near-threshold active-set
                # counts are diagnostics rather than stable artifact identity.
                assert isinstance(payload_case[key], int)
                assert payload_case[key] >= 0
            else:
                assert artifact_case[key] == payload_case[key]


def test_registered_metric_order_lp_survivors_match_artifact() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_metric_order_lp.py",
            "--assert-expected",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    artifact = json.loads(
        (ROOT / "data" / "certificates" / "metric_order_lp_survivors.json")
        .read_text(encoding="utf-8")
    )

    assert_payload_matches_artifact(artifact, payload)
    by_case = {row["case"]: row for row in payload["cases"]}
    c13 = by_case["C13_sidon_1_2_4_10:sample_full_filter_survivor"]
    c19 = by_case["C19_skew:vertex_circle_survivor"]

    assert c13["status"] == "PASS_METRIC_ORDER_LP_RELAXATION"
    assert c13["triangle_inequality_count"] == 858
    assert c13["max_margin"] > 0.002
    assert c19["status"] == "PASS_METRIC_ORDER_LP_RELAXATION"
    assert c19["triangle_inequality_count"] == 2907
    assert c19["max_margin"] > 0.001
