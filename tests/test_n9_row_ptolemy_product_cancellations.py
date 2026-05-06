from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest

from erdos97.n9_row_ptolemy_product_cancellations import (
    EXPECTED_HIT_FAMILY_TEMPLATE_IDS,
    EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS,
    EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS,
    EXPECTED_NONHIT_TEMPLATE_IDS,
    row_ptolemy_product_cancellation_report,
)
from scripts.check_n9_row_ptolemy_product_cancellations import (
    DEFAULT_ARTIFACT,
    DEFAULT_TEMPLATE_ARTIFACT,
    load_artifact,
    summary_payload,
    validate_payload,
)


ROOT = Path(__file__).resolve().parents[1]


def test_row_ptolemy_product_artifact_summary_is_nonclaiming() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)

    assert payload["status"] == "EXPLORATORY_LEDGER_ONLY"
    assert payload["trust"] == "FINITE_BOOKKEEPING_NOT_A_PROOF"
    assert "not a proof of n=9" in payload["claim_scope"]
    assert "not a geometric realizability test" in payload["claim_scope"]
    assert any(
        "not an orderless abstract-incidence obstruction" in item
        for item in payload["interpretation"]
    )
    assert payload["source_frontier"]["assignment_count"] == 184
    assert payload["hit_summary"]["hit_assignment_count"] == 26
    assert payload["hit_summary"]["hit_certificate_count"] == 216
    assert payload["hit_summary"]["hit_family_count"] == 3


def test_row_ptolemy_product_artifact_records_family_counts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    family_counts = {
        row["family_id"]: row["hit_assignment_count"]
        for row in payload["hit_summary"]["hit_family_counts"]
    }
    certificate_counts = {}
    representative_counts = {}
    for record in payload["hit_records"]:
        family_id = record["family_id"]
        certificate_counts[family_id] = (
            certificate_counts.get(family_id, 0) + record["certificate_count"]
        )
        representative_counts.setdefault(family_id, record["certificate_count"])

    assert family_counts == {"F02": 18, "F09": 6, "F13": 2}
    assert certificate_counts == {"F02": 108, "F09": 72, "F13": 36}
    assert representative_counts == {"F02": 6, "F09": 12, "F13": 18}
    assert payload["hit_summary"]["hit_assignment_vertex_circle_status_counts"] == {
        "self_edge": 26,
    }
    assert payload["hit_summary"]["certificates_per_hit_assignment_counts"] == {
        "6": 18,
        "12": 6,
        "18": 2,
    }
    assert payload["hit_summary"]["certificate_count_by_center"] == {
        str(center): 24 for center in range(9)
    }


def test_row_ptolemy_product_negative_control_families_have_no_hits() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    packet_path = ROOT / "data" / "certificates" / "n9_vertex_circle_local_core_packet.json"
    packet = json.loads(packet_path.read_text(encoding="utf-8"))
    all_family_orbits = {
        row["family_id"]: row["orbit_size"] for row in packet["certificates"]
    }
    hit_families = {record["family_id"] for record in payload["hit_records"]}
    negative_family_orbits = {
        family_id: orbit_size
        for family_id, orbit_size in sorted(all_family_orbits.items())
        if family_id not in hit_families
    }
    negative_certificate_counts = {
        family_id: sum(
            record["certificate_count"]
            for record in payload["hit_records"]
            if record["family_id"] == family_id
        )
        for family_id in negative_family_orbits
    }

    assert hit_families == {"F02", "F09", "F13"}
    assert negative_family_orbits == {
        "F01": 18,
        "F03": 18,
        "F04": 18,
        "F05": 18,
        "F06": 18,
        "F07": 6,
        "F08": 2,
        "F10": 18,
        "F11": 18,
        "F12": 18,
        "F14": 2,
        "F15": 2,
        "F16": 2,
    }
    assert len(negative_family_orbits) == 13
    assert sum(negative_family_orbits.values()) == 158
    assert negative_certificate_counts == {
        family_id: 0 for family_id in negative_family_orbits
    }


def test_row_ptolemy_product_crosswalks_to_core_templates() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    crosswalk = payload["template_crosswalk"]

    assert crosswalk["claim_scope"].startswith("Diagnostic join")
    assert crosswalk["source_artifact"] == {
        "path": "data/certificates/n9_vertex_circle_core_templates.json",
        "schema": "erdos97.n9_vertex_circle_core_templates.v1",
        "status": "REVIEW_PENDING_DIAGNOSTIC_ONLY",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
    }
    assert crosswalk["hit_template_count"] == 3
    assert crosswalk["hit_family_template_ids"] == EXPECTED_HIT_FAMILY_TEMPLATE_IDS
    assert (
        crosswalk["hit_template_assignment_counts"]
        == EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS
    )
    assert (
        crosswalk["hit_template_certificate_counts"]
        == EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS
    )


def test_row_ptolemy_product_crosswalk_hit_counts_match_template_orbits() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    family_rows = {
        row["family_id"]: row for row in payload["template_crosswalk"]["hit_family_rows"]
    }

    assert family_rows["F02"]["template_id"] == "T08"
    assert family_rows["F02"]["family_orbit_size"] == 18
    assert family_rows["F02"]["hit_assignment_count"] == 18
    assert family_rows["F02"]["hit_certificate_count"] == 108
    assert family_rows["F09"]["template_id"] == "T01"
    assert family_rows["F09"]["family_orbit_size"] == 6
    assert family_rows["F09"]["hit_assignment_count"] == 6
    assert family_rows["F09"]["hit_certificate_count"] == 72
    assert family_rows["F13"]["template_id"] == "T04"
    assert family_rows["F13"]["family_orbit_size"] == 2
    assert family_rows["F13"]["hit_assignment_count"] == 2
    assert family_rows["F13"]["hit_certificate_count"] == 36


def test_row_ptolemy_product_crosswalk_strict_cycle_templates_have_no_hits() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    template_payload = load_artifact(DEFAULT_TEMPLATE_ARTIFACT)
    strict_cycle_families = {
        family["family_id"]
        for family in template_payload["families"]
        if family["status"] == "strict_cycle"
    }

    assert strict_cycle_families == {"F07", "F12", "F16"}
    assert not (strict_cycle_families & set(payload["template_crosswalk"]["hit_family_template_ids"]))
    assert payload["template_crosswalk"]["strict_cycle_hit_family_count"] == 0
    assert payload["template_crosswalk"]["strict_cycle_nonhit_family_count"] == 3
    assert payload["template_crosswalk"]["nonhit_template_ids"] == EXPECTED_NONHIT_TEMPLATE_IDS


def test_row_ptolemy_product_certificate_shape_is_exact_and_ordered() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    cert = payload["hit_records"][0]["certificates"][0]

    assert cert["type"] == "row_ptolemy_product_cancellation"
    assert cert["status"] == "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER"
    assert cert["ptolemy_identity"] == "d02*d13 = d01*d23 + d03*d12"
    assert cert["zero_product"]["expression"] == "d03*d12"
    assert "supplied/certified row order" in cert["scope"]


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_artifact_matches_generator() -> None:
    checked_in = load_artifact(DEFAULT_ARTIFACT)

    assert checked_in == row_ptolemy_product_cancellation_report()


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_checker_passes() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    errors = validate_payload(payload)
    summary = summary_payload(DEFAULT_ARTIFACT, payload, errors)

    assert errors == []
    assert summary["ok"] is True
    assert summary["hit_assignment_count"] == 26
    assert summary["hit_certificate_count"] == 216


def test_row_ptolemy_product_checker_rejects_tampered_provenance() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["provenance"]["command"] = (
        "python scripts/analyze_n9_row_ptolemy_product_cancellations.py"
    )

    errors = validate_payload(payload, recompute=False)

    assert any("provenance" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_source_artifacts() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["source_artifacts"] = []

    errors = validate_payload(payload, recompute=False)

    assert any("source_artifacts" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_unknown_top_level_key() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["unchecked_schema_drift"] = {"ok": False}

    errors = validate_payload(payload, recompute=False)

    assert any("top-level keys" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_count() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_summary"]["hit_assignment_count"] = 27

    errors = validate_payload(payload, recompute=False)

    assert any("hit assignment count" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_template_crosswalk() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["template_crosswalk"]["hit_family_template_ids"]["F02"] = "T01"

    errors = validate_payload(payload, recompute=False)

    assert any("template_crosswalk hit_family_template_ids" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_stale_template_source_status() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    template_payload = load_artifact(DEFAULT_TEMPLATE_ARTIFACT)
    for family in template_payload["families"]:
        if family["family_id"] == "F02":
            family["status"] = "strict_cycle"
            break

    errors = validate_payload(
        payload,
        recompute=False,
        template_payload=template_payload,
    )

    assert any("template_crosswalk" in error for error in errors)


def test_row_ptolemy_product_checker_reports_malformed_template_source() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    template_payload = load_artifact(DEFAULT_TEMPLATE_ARTIFACT)
    for family in template_payload["families"]:
        if family["family_id"] == "F02":
            del family["core_size"]
            break

    errors = validate_payload(
        payload,
        recompute=False,
        template_payload=template_payload,
    )

    assert any("template crosswalk source invalid" in error for error in errors)
    assert any("missing core_size" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_out_of_range_assignment_index() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_records"][0]["assignment_index"] = -1

    errors = validate_payload(payload, recompute=False)

    assert any("assignment_index -1 is outside" in error for error in errors)


def test_row_ptolemy_product_checker_binds_rows_to_assignment_index() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    donor = copy.deepcopy(payload["hit_records"][1])
    payload["hit_records"][0]["selected_rows"] = donor["selected_rows"]
    payload["hit_records"][0]["certificates"] = donor["certificates"]
    payload["hit_records"][0]["certificate_count"] = donor["certificate_count"]

    errors = validate_payload(payload, recompute=False)

    assert any("selected_rows for assignment_index 1" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_witness_order() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_records"][0]["certificates"][0]["witness_order"] = [1, 3, 2, 8]

    errors = validate_payload(payload, recompute=False)

    assert any("witness_order" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_forced_pair() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_records"][0]["certificates"][0]["forced_equalities"][0][
        "left_pair"
    ] = [1, 4]

    errors = validate_payload(payload, recompute=False)

    assert any("forced_equalities[0] left_pair" in error for error in errors)


def test_row_ptolemy_product_checker_rejects_tampered_zero_product_pair() -> None:
    payload = load_artifact(DEFAULT_ARTIFACT)
    payload["hit_records"][0]["certificates"][0]["zero_product"]["factors"][0][
        "pair"
    ] = [2, 8]

    errors = validate_payload(payload, recompute=False)

    assert any("zero_product.factors[0] pair" in error for error in errors)


@pytest.mark.artifact
@pytest.mark.exhaustive
def test_row_ptolemy_product_checker_cli_json() -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/check_n9_row_ptolemy_product_cancellations.py",
            "--check",
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
    assert payload["hit_certificate_count"] == 216
