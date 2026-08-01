from __future__ import annotations

import json
from pathlib import Path

from erdos97.n9_vertex_circle_template_duals import (
    EXPECTED_ASSIGNMENT_COUNT,
    EXPECTED_FAMILY_COUNT,
    EXPECTED_SKELETON_COUNT,
    EXPECTED_TEMPLATE_COUNT,
    assert_expected_template_dual_counts,
    template_dual_payload,
)


ROOT = Path(__file__).resolve().parents[1]
RELATION_SKELETONS = (
    ROOT / "data" / "certificates" / "relation_skeleton_catalog.json"
)
FRONTIER_CLASSIFICATION = (
    ROOT
    / "data"
    / "certificates"
    / "n9_vertex_circle_frontier_motif_classification.json"
)
ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_vertex_circle_template_duals.json"
)


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _generated() -> dict[str, object]:
    return template_dual_payload(
        _load(RELATION_SKELETONS),
        _load(FRONTIER_CLASSIFICATION),
    )


def test_stored_template_duals_match_regeneration() -> None:
    generated = _generated()
    assert_expected_template_dual_counts(generated)
    assert _load(ARTIFACT) == generated


def test_all_dual_identities_are_positive_and_quotient_stable() -> None:
    payload = _generated()
    assert payload["skeleton_count"] == EXPECTED_SKELETON_COUNT
    assert payload["template_count"] == EXPECTED_TEMPLATE_COUNT
    assert payload["family_count"] == EXPECTED_FAMILY_COUNT
    assert payload["covered_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert payload["all_strict_coefficients_positive_unit"] is True
    assert payload["all_equality_multipliers_signed_unit"] is True
    assert payload["all_identity_balances_zero"] is True
    assert payload["all_active_pair_quotients_preserve_zero_balance"] is True
    assert payload["total_active_pair_quotient_partitions_checked"] == 2451

    certificates = payload["certificates"]
    assert isinstance(certificates, list)
    assert all(certificate["identity_balance"] == [] for certificate in certificates)
    assert all(
        certificate["active_pair_quotient_check"]["all_quotient_balances_zero"]
        for certificate in certificates
    )


def test_all_transformed_frontier_certificates_replay() -> None:
    coverage = _generated()["assignment_coverage"]
    assert coverage["assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert coverage["unique_assignment_count"] == EXPECTED_ASSIGNMENT_COUNT
    assert coverage["all_transformed_identities_verified_zero"] is True
    assert coverage["all_transformed_terms_supported_by_assignment_cores"] is True
    assert coverage["all_label_maps_verified_dihedral"] is True
    assert coverage["transformed_certificate_sha256"] == (
        "c60ce8833bd4b2fa7ad32e2e034091966369a77553614fffc2226dc4a0edf3eb"
    )
