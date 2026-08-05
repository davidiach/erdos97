"""Hinge/splice motif crosswalk for the three-halo Kalmanson endgame."""

from __future__ import annotations

from collections import Counter
from itertools import combinations
from hashlib import sha256
import json
from typing import Any, Mapping, Sequence

from erdos97.fragile_cycle_three_halo_kalmanson_endgame import (
    N,
    replay_kalmanson_certificate,
)
from erdos97.kalmanson_equilateral_hinge import find_hinge_instances
from erdos97.kalmanson_splice import (
    SPLICE_TEMPLATES,
    find_splice_embeddings,
    verify_splice_template,
)


SOURCE_SCHEMA = "erdos97.fragile_cycle_three_halo_kalmanson_endgame.v1"
SOURCE_CATALOG_SHA256 = (
    "ef3fe4aea1975f491f25af286a69e52ad239f15320538044b1803e0adcca10bf"
)
SCHEMA = "erdos97.fragile_cycle_three_halo_motif_crosswalk.v1"
STATUS = "EXACT_BOUNDED_HINGE_SPLICE_MOTIF_CROSSWALK"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact motif compression of the thirteen fixed three-halo Kalmanson "
    "endgame certificates into the generic equilateral hinge and two generic "
    "two-inequality splice templates. This does not force any motif, quotient, "
    "or halo placement from minimal-counterexample geometry, does not prove "
    "n=10 or Erdos Problem #97, and is not a counterexample."
)
CONCLUSION = (
    "The thirteen fixed metric endgames reduce to three local motifs: eleven "
    "equilateral hinges, one six-role K1/K2 splice, and one five-role K2/K1 "
    "splice. The two splice states are hinge-free and each has one unique "
    "order-preserving template embedding."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_three_halo_motif_crosswalk.py",
    "command": (
        "python scripts/check_fragile_cycle_three_halo_motif_crosswalk.py "
        "--write --assert-expected --summary-json"
    ),
}

EXPECTED_STATE_COUNT = 13
EXPECTED_MOTIF_COUNTS = {
    "equilateral_hinge": 11,
    "five_role_K2_K1_splice": 1,
    "six_role_K1_K2_splice": 1,
}
EXPECTED_RECIPROCAL_PAIR_HISTOGRAM = {"0": 1, "1": 12}
EXPECTED_CATALOG_SHA256 = (
    "995db4351e5fddcaaaf33dc7ee700ed370bad33f8d6f69a6c82cce237da6f3d9"
)


def _rows(certificate: Mapping[str, Any]) -> dict[int, tuple[int, ...]]:
    raw_rows = certificate.get("selected_core_rows_natural_order")
    if not isinstance(raw_rows, list):
        raise ValueError("source certificate has no selected core rows")
    return {
        int(row[0]): tuple(int(witness) for witness in row[1:]) for row in raw_rows
    }


def _reciprocal_pairs(rows: Mapping[int, Sequence[int]]) -> list[list[int]]:
    centers = sorted(rows)
    return [
        [left, right]
        for left, right in combinations(centers, 2)
        if right in rows[left] and left in rows[right]
    ]


def _hinge_record(hinge: Any) -> dict[str, Any]:
    payload = hinge.as_dict()
    return {
        "motif": "equilateral_hinge",
        "role_count": 4,
        "quadruple": payload["quadruple"],
        "inequality_kind": payload["inequality_kind"],
        "centers": payload["centers"],
        "active_equalities": payload["equalities"],
    }


def _validate_source(source: Mapping[str, Any]) -> None:
    if source.get("schema") != SOURCE_SCHEMA:
        raise ValueError("unexpected Kalmanson endgame source schema")
    if source.get("kalmanson_endgame_catalog_sha256") != SOURCE_CATALOG_SHA256:
        raise ValueError("unexpected Kalmanson endgame source digest")
    certificates = source.get("state_certificates")
    if not isinstance(certificates, list) or len(certificates) != EXPECTED_STATE_COUNT:
        raise ValueError("unexpected Kalmanson endgame certificate catalog")


def motif_crosswalk_payload(source: Mapping[str, Any]) -> dict[str, Any]:
    """Compress all source certificates to hinge and splice motifs."""

    _validate_source(source)
    template_replays = [verify_splice_template(template) for template in SPLICE_TEMPLATES]
    records: list[dict[str, Any]] = []
    motif_counts: Counter[str] = Counter()
    reciprocal_histogram: Counter[int] = Counter()
    for source_certificate in source["state_certificates"]:
        if not isinstance(source_certificate, Mapping):
            raise ValueError("source certificate record must be an object")
        replay = replay_kalmanson_certificate(N, source_certificate)
        rows = _rows(source_certificate)
        hinges = find_hinge_instances(rows, tuple(range(N)))
        embeddings = find_splice_embeddings(
            rows,
            tuple(range(N)),
            source_certificate["strict_rows"],
        )
        strict_count = int(source_certificate["strict_row_count"])
        if strict_count == 1:
            if len(hinges) != 1 or embeddings:
                raise AssertionError("one-row source must have one hinge and no splice")
            hinge = hinges[0]
            strict_row = source_certificate["strict_rows"][0]
            short_kind = "K1" if str(strict_row["kind"]).startswith("K1") else "K2"
            if hinge.kind != short_kind or list(hinge.quadruple) != strict_row[
                "quad_natural_order"
            ]:
                raise AssertionError("hinge does not replay the selected strict row")
            motif = _hinge_record(hinge)
        elif strict_count == 2:
            if hinges or len(embeddings) != 1:
                raise AssertionError("two-row source must have one hinge-free splice")
            motif = embeddings[0].as_dict()
            motif["role_count"] = len(embeddings[0].role_map)
        else:
            raise AssertionError("unexpected source strict support")

        reciprocal_pairs = _reciprocal_pairs(rows)
        reciprocal_histogram[len(reciprocal_pairs)] += 1
        motif_name = str(motif["motif"] if "motif" in motif else motif["template"])
        motif_counts[motif_name] += 1
        records.append(
            {
                "state_id": str(source_certificate["state_id"]),
                "source_terminal_type": str(
                    source_certificate["source_terminal_type"]
                ),
                "source_obstruction_type": str(
                    source_certificate["obstruction_type"]
                ),
                "selected_core_rows_natural_order": [
                    [center, *rows[center]] for center in sorted(rows)
                ],
                "reciprocal_selected_center_pairs": reciprocal_pairs,
                "motif_class": motif_name,
                "motif_embedding": motif,
                "source_certificate_replay": replay,
            }
        )

    catalog_material = {
        "splice_template_replays": template_replays,
        "state_motif_crosswalk": records,
    }
    digest = sha256(
        json.dumps(catalog_material, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "source_artifact": {
            "path": (
                "data/certificates/"
                "fragile_cycle_three_halo_kalmanson_endgame.json"
            ),
            "schema": SOURCE_SCHEMA,
            "kalmanson_endgame_catalog_sha256": SOURCE_CATALOG_SHA256,
        },
        "splice_template_replays": template_replays,
        "state_motif_crosswalk": records,
        "motif_class_count": len(motif_counts),
        "motif_class_counts": dict(sorted(motif_counts.items())),
        "reciprocal_selected_center_pair_count_histogram": {
            str(count): states for count, states in sorted(reciprocal_histogram.items())
        },
        "motif_crosswalk_catalog_sha256": digest,
        "summary": {
            "source_states_checked": len(records),
            "equilateral_hinge_states": motif_counts["equilateral_hinge"],
            "five_role_splice_states": motif_counts["five_role_K2_K1_splice"],
            "six_role_splice_states": motif_counts["six_role_K1_K2_splice"],
            "hinge_free_splice_states": sum(
                count for motif, count in motif_counts.items() if "splice" in motif
            ),
            "distinct_local_motif_classes": len(motif_counts),
            "all_source_certificates_replayed": all(
                record["source_certificate_replay"]["zero_sum_verified"]
                for record in records
            ),
            "all_states_classified_once": len(records) == sum(motif_counts.values()),
        },
        "limitations": [
            "The crosswalk compresses a fixed thirteen-state source catalog and does not force catalog entry.",
            "The splice lemmas are direct local contradictions only when their ordered roles and centered equalities occur.",
            "The reciprocal-pair census is descriptive; a reciprocal pair alone is not an obstruction.",
            "No proof of n=10, general proof, counterexample, or official/global status update is claimed.",
        ],
        "conclusion": CONCLUSION,
        "provenance": PROVENANCE,
    }


def assert_expected_payload(payload: Mapping[str, Any]) -> None:
    """Check stable motif counts, exact template lemmas, and source replays."""

    assert payload["schema"] == SCHEMA
    assert payload["status"] == STATUS
    assert payload["trust"] == TRUST
    assert payload["claim_scope"] == CLAIM_SCOPE
    assert payload["motif_class_count"] == 3
    assert payload["motif_class_counts"] == EXPECTED_MOTIF_COUNTS
    assert (
        payload["reciprocal_selected_center_pair_count_histogram"]
        == EXPECTED_RECIPROCAL_PAIR_HISTOGRAM
    )
    assert payload["motif_crosswalk_catalog_sha256"] == EXPECTED_CATALOG_SHA256
    summary = payload["summary"]
    assert summary["source_states_checked"] == EXPECTED_STATE_COUNT
    assert summary["equilateral_hinge_states"] == 11
    assert summary["five_role_splice_states"] == 1
    assert summary["six_role_splice_states"] == 1
    assert summary["hinge_free_splice_states"] == 2
    assert summary["distinct_local_motif_classes"] == 3
    assert summary["all_source_certificates_replayed"] is True
    assert summary["all_states_classified_once"] is True
    for template, stored in zip(
        SPLICE_TEMPLATES,
        payload["splice_template_replays"],
        strict=True,
    ):
        assert verify_splice_template(template) == stored
    assert payload["conclusion"] == CONCLUSION
    assert payload["provenance"] == PROVENANCE
