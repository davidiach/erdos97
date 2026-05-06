from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.analyze_kalmanson_z3_clauses import (
    DEFAULT_ARTIFACT,
    assert_expected,
    check_artifact,
    diagnostic_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_c19_z3_clause_diagnostic_matches_artifact() -> None:
    payload = diagnostic_payload()

    assert_expected(payload)
    check_artifact(DEFAULT_ARTIFACT, payload)
    assert payload["source_certificate"]["pattern"] == {
        "circulant_offsets": [-8, -3, 5, 9],
        "n": 19,
        "name": "C19_skew",
    }
    assert payload["template_summary"]["clause_count"] == 7981
    assert payload["template_summary"]["translation_family_count"] == 1946
    assert payload["template_summary"]["ordered_quad_step_pattern_count"] == 576
    assert payload["template_summary"]["shared_label_count_distribution"] == {
        "2": 7310,
        "3": 671,
    }
    assert payload["clause_validation_summary"]["lexicographically_sorted"] is True
    assert payload["template_summary"]["matches_per_clause_distribution"] == {"1": 7981}
    assert payload["template_summary"]["matched_vector_support_size_distribution"] == {
        "2": 7780,
        "4": 201,
    }
    assert payload["distance_quotient_table_summary"][
        "unique_inverse_vector_pairs_used_by_stored_clauses"
    ] == 285
    assert payload["rotation_quotient_literal_summary"][
        "label0_non_first_occurrences"
    ] == 0
    assert payload["clause_shape_summary"]["union_label_count_distribution"] == {
        "5": 671,
        "6": 7310,
    }


def test_c19_z3_clause_diagnostic_rejects_tampered_counts() -> None:
    payload = diagnostic_payload()
    payload["template_summary"]["translation_family_count"] = 1947

    try:
        assert_expected(payload)
    except AssertionError as exc:
        assert "translation_family_count" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered diagnostic unexpectedly passed")


def test_c19_z3_clause_diagnostic_rejects_tampered_provenance() -> None:
    payload = diagnostic_payload()
    payload["provenance"]["command"] = "python scripts/analyze_kalmanson_z3_clauses.py"

    try:
        assert_expected(payload)
    except AssertionError as exc:
        assert "provenance" in str(exc)
    else:  # pragma: no cover - defensive assertion shape
        raise AssertionError("tampered provenance unexpectedly passed")


def test_c19_z3_clause_diagnostic_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/analyze_kalmanson_z3_clauses.py",
            "--assert-expected",
            "--check-artifact",
            "reports/c19_kalmanson_z3_clause_diagnostics.json",
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
    assert payload["trust"] == "EXACT_CERTIFICATE_DIAGNOSTIC"
    assert payload["status"] == "ALL_ORDER_C19_Z3_CLAUSE_DIAGNOSTIC_ONLY"
