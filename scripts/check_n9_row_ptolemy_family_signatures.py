#!/usr/bin/env python3
"""Generate or check n=9 row-Ptolemy per-family signature diagnostics."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Sequence

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
SCRIPTS = ROOT / "scripts"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from erdos97.path_display import display_path  # noqa: E402
from scripts.check_n9_row_ptolemy_product_cancellations import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_ROW_PTOLEMY_ARTIFACT,
    load_artifact,
    validate_payload as validate_row_ptolemy_payload,
)
from scripts.check_n9_vertex_circle_core_templates import (  # noqa: E402
    DEFAULT_ARTIFACT as DEFAULT_CORE_TEMPLATE_ARTIFACT,
    SCHEMA as CORE_TEMPLATE_SCHEMA,
    STATUS as CORE_TEMPLATE_STATUS,
    TRUST as CORE_TEMPLATE_TRUST,
    validate_payload as validate_core_template_payload,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_family_signatures.json"
)
SCHEMA = "erdos97.n9_row_ptolemy_family_signatures.v2"
STATUS = "EXPLORATORY_LEDGER_ONLY"
TRUST = "FINITE_BOOKKEEPING_NOT_A_PROOF"
CLAIM_SCOPE = (
    "Derived n=9 row-Ptolemy per-family certificate-signature diagnostic for "
    "the fixed natural cyclic order; not a proof of n=9, not a counterexample, "
    "not an orderless abstract-incidence obstruction, and not a global status "
    "update."
)
PROVENANCE = {
    "generator": "scripts/check_n9_row_ptolemy_family_signatures.py",
    "command": (
        "python scripts/check_n9_row_ptolemy_family_signatures.py "
        "--assert-expected --write"
    ),
}
ROW_PTOLEMY_SOURCE_PATH = "data/certificates/n9_row_ptolemy_product_cancellations.json"
CORE_TEMPLATE_SOURCE_PATH = "data/certificates/n9_vertex_circle_core_templates.json"
EXPECTED_SOURCE_ARTIFACTS = [
    {
        "path": ROW_PTOLEMY_SOURCE_PATH,
        "role": "row-Ptolemy product-cancellation hit records",
        "schema": "erdos97.n9_row_ptolemy_product_cancellations.v2",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
    },
    {
        "path": CORE_TEMPLATE_SOURCE_PATH,
        "role": "review-pending local-core template shape labels",
        "schema": CORE_TEMPLATE_SCHEMA,
        "status": CORE_TEMPLATE_STATUS,
        "trust": CORE_TEMPLATE_TRUST,
    },
]
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "cyclic_order",
    "family_count",
    "hit_assignment_count",
    "hit_certificate_count",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "signature_rows",
    "source_artifacts",
    "status",
    "trust",
    "witness_size",
}
EXPECTED_SIGNATURE_ROWS = [
    {
        "family_id": "F02",
        "template_id": "T08",
        "template_status": "self_edge",
        "family_orbit_size": 18,
        "hit_assignment_count": 18,
        "hit_certificate_count": 108,
        "certificate_count_per_assignment": 6,
        "hit_row_count_per_assignment": 3,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"3": 18},
        "certificate_count_by_center": {str(center): 12 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 3,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 3,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 6},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 6},
        "signature_key": (
            "row_ptolemy_product|hit_rows=3|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
        "template_core_size": 6,
        "template_key": (
            "self_edge|rows=6|strict_edges=54|"
            "conflicts=2:1:1x4,3:1:0x2,3:1:1x2,3:2:1x1"
        ),
        "template_self_edge_conflict_count": 9,
        "template_self_edge_shape_counts": [
            {
                "count": 4,
                "inner_span": 1,
                "outer_span": 2,
                "shared_endpoint_count": 1,
            },
            {
                "count": 2,
                "inner_span": 1,
                "outer_span": 3,
                "shared_endpoint_count": 0,
            },
            {
                "count": 2,
                "inner_span": 1,
                "outer_span": 3,
                "shared_endpoint_count": 1,
            },
            {
                "count": 1,
                "inner_span": 2,
                "outer_span": 3,
                "shared_endpoint_count": 1,
            },
        ],
        "template_strict_edge_count": 54,
    },
    {
        "family_id": "F09",
        "template_id": "T01",
        "template_status": "self_edge",
        "family_orbit_size": 6,
        "hit_assignment_count": 6,
        "hit_certificate_count": 72,
        "certificate_count_per_assignment": 12,
        "hit_row_count_per_assignment": 6,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"6": 6},
        "certificate_count_by_center": {str(center): 8 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 6,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 6,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 12},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 12},
        "signature_key": (
            "row_ptolemy_product|hit_rows=6|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
        "template_core_size": 3,
        "template_key": (
            "self_edge|rows=3|strict_edges=27|conflicts=3:1:0x1,3:1:1x1"
        ),
        "template_self_edge_conflict_count": 2,
        "template_self_edge_shape_counts": [
            {
                "count": 1,
                "inner_span": 1,
                "outer_span": 3,
                "shared_endpoint_count": 0,
            },
            {
                "count": 1,
                "inner_span": 1,
                "outer_span": 3,
                "shared_endpoint_count": 1,
            },
        ],
        "template_strict_edge_count": 27,
    },
    {
        "family_id": "F13",
        "template_id": "T04",
        "template_status": "self_edge",
        "family_orbit_size": 2,
        "hit_assignment_count": 2,
        "hit_certificate_count": 36,
        "certificate_count_per_assignment": 18,
        "hit_row_count_per_assignment": 9,
        "certificate_count_per_hit_row": 2,
        "rows_with_certificates_per_assignment_counts": {"9": 2},
        "certificate_count_by_center": {str(center): 4 for center in range(9)},
        "variant_counts_per_assignment": {
            "cancel_d01_d23_via_d02_eq_d01_and_d13_eq_d23": 9,
            "cancel_d01_d23_via_d02_eq_d23_and_d13_eq_d01": 9,
        },
        "cancelled_product_counts_per_assignment": {"d01*d23": 18},
        "zero_product_expression_counts_per_assignment": {"d03*d12": 18},
        "signature_key": (
            "row_ptolemy_product|hit_rows=9|certs_per_row=2|"
            "cancelled=d01*d23|zero=d03*d12"
        ),
        "template_core_size": 4,
        "template_key": (
            "self_edge|rows=4|strict_edges=36|conflicts=2:1:1x2"
        ),
        "template_self_edge_conflict_count": 2,
        "template_self_edge_shape_counts": [
            {
                "count": 2,
                "inner_span": 1,
                "outer_span": 2,
                "shared_endpoint_count": 1,
            },
        ],
        "template_strict_edge_count": 36,
    },
]


def write_json(payload: object, path: Path) -> None:
    """Write stable LF-terminated JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _same_counter(
    errors: list[str],
    *,
    label: str,
    family_id: str,
    counters: Sequence[Counter[str] | Counter[int]],
) -> dict[str, int]:
    rows = [_json_counter(counter) for counter in counters]
    if not rows:
        errors.append(f"{label} has no rows for {family_id}")
        return {}
    first = rows[0]
    for index, row in enumerate(rows[1:], start=1):
        if row != first:
            errors.append(
                f"{label} is not stable for {family_id}: "
                f"record 0 has {first!r}, record {index} has {row!r}"
            )
    return first


def _source_artifacts(
    row_ptolemy_source: dict[str, Any],
    template_source: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "path": ROW_PTOLEMY_SOURCE_PATH,
            "role": "row-Ptolemy product-cancellation hit records",
            "schema": row_ptolemy_source.get("schema"),
            "status": row_ptolemy_source.get("status"),
            "trust": row_ptolemy_source.get("trust"),
        },
        {
            "path": CORE_TEMPLATE_SOURCE_PATH,
            "role": "review-pending local-core template shape labels",
            "schema": template_source.get("schema"),
            "status": template_source.get("status"),
            "trust": template_source.get("trust"),
        },
    ]


def _template_crosswalk_source_artifact(template_source: dict[str, Any]) -> dict[str, Any]:
    return {
        "path": CORE_TEMPLATE_SOURCE_PATH,
        "schema": template_source.get("schema"),
        "status": template_source.get("status"),
        "trust": template_source.get("trust"),
    }


def _template_maps(
    template_source: Any,
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(template_source, dict):
        errors.append("local-core template source top level must be an object")
        return {}, {}
    template_errors = validate_core_template_payload(template_source, recompute=False)
    errors.extend(f"local-core template source invalid: {error}" for error in template_errors)

    raw_families = template_source.get("families")
    raw_templates = template_source.get("templates")
    if not isinstance(raw_families, list):
        errors.append("local-core template source families must be a list")
        return {}, {}
    if not isinstance(raw_templates, list):
        errors.append("local-core template source templates must be a list")
        return {}, {}

    families_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_family in enumerate(raw_families):
        if not isinstance(raw_family, dict):
            errors.append(f"local-core template source families[{index}] must be an object")
            continue
        family_id = raw_family.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(
                f"local-core template source families[{index}] has invalid family_id"
            )
            continue
        if family_id in families_by_id:
            errors.append(f"duplicate local-core template family id {family_id}")
        families_by_id[family_id] = raw_family

    templates_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_template in enumerate(raw_templates):
        if not isinstance(raw_template, dict):
            errors.append(f"local-core template source templates[{index}] must be an object")
            continue
        template_id = raw_template.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            errors.append(
                f"local-core template source templates[{index}] has invalid template_id"
            )
            continue
        if template_id in templates_by_id:
            errors.append(f"duplicate local-core template id {template_id}")
        templates_by_id[template_id] = raw_template
    return families_by_id, templates_by_id


def _int_field(errors: list[str], row: dict[str, Any], key: str, label: str) -> int:
    value = row.get(key)
    if isinstance(value, int) and not isinstance(value, bool):
        return int(value)
    errors.append(f"{label} {key} must be an integer")
    return 0


def _self_edge_shape_fields(
    errors: list[str],
    *,
    family_id: str,
    template_id: str,
    family_template: dict[str, Any],
    template: dict[str, Any],
) -> dict[str, Any]:
    if template.get("status") != "self_edge":
        errors.append(
            f"family {family_id} template {template_id} is not a self_edge template"
        )
        return {
            "template_key": template.get("template_key"),
            "template_core_size": _int_field(
                errors, template, "core_size", f"template {template_id}"
            ),
            "template_strict_edge_count": _int_field(
                errors, template, "strict_edge_count", f"template {template_id}"
            ),
            "template_self_edge_conflict_count": 0,
            "template_self_edge_shape_counts": [],
        }

    obstruction = family_template.get("obstruction_summary")
    if not isinstance(obstruction, dict):
        errors.append(f"family {family_id} obstruction_summary must be an object")
        obstruction = {}
    shape_counts = template.get("self_edge_shape_counts")
    if not isinstance(shape_counts, list):
        errors.append(f"template {template_id} self_edge_shape_counts must be a list")
        shape_counts = []
    copied_shape_counts = [
        dict(row)
        for row in shape_counts
        if isinstance(row, dict)
    ]
    if obstruction.get("self_edge_shape_counts") != shape_counts:
        errors.append(
            f"family {family_id} self_edge_shape_counts do not match template {template_id}"
        )

    conflict_count = sum(
        int(row.get("count", 0))
        for row in shape_counts
        if isinstance(row, dict) and isinstance(row.get("count"), int)
    )
    if obstruction.get("self_edge_conflict_count") != conflict_count:
        errors.append(
            f"family {family_id} self_edge conflict count does not match template shapes"
        )

    return {
        "template_key": template.get("template_key"),
        "template_core_size": _int_field(
            errors, template, "core_size", f"template {template_id}"
        ),
        "template_strict_edge_count": _int_field(
            errors, template, "strict_edge_count", f"template {template_id}"
        ),
        "template_self_edge_conflict_count": conflict_count,
        "template_self_edge_shape_counts": copied_shape_counts,
    }


def _signature_rows(
    source: dict[str, Any],
    template_source: dict[str, Any],
    errors: list[str],
) -> list[dict[str, Any]]:
    families_by_id, templates_by_id = _template_maps(template_source, errors)
    records_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in source.get("hit_records", []):
        if isinstance(record, dict) and isinstance(record.get("family_id"), str):
            records_by_family[str(record["family_id"])].append(record)

    crosswalk = source.get("template_crosswalk", {})
    crosswalk_rows = {}
    if isinstance(crosswalk, dict) and isinstance(crosswalk.get("hit_family_rows"), list):
        crosswalk_rows = {
            str(row["family_id"]): row
            for row in crosswalk["hit_family_rows"]
            if isinstance(row, dict) and "family_id" in row
        }
    expect_equal(
        errors,
        "row-Ptolemy template_crosswalk source_artifact",
        crosswalk.get("source_artifact") if isinstance(crosswalk, dict) else None,
        _template_crosswalk_source_artifact(template_source),
    )

    rows = []
    for family_id in sorted(records_by_family):
        records = records_by_family[family_id]
        family_crosswalk = crosswalk_rows.get(family_id, {})
        template_id = family_crosswalk.get("template_id")
        template_shape_fields: dict[str, Any] = {}
        if not isinstance(template_id, str):
            errors.append(f"missing template id for {family_id}")
        else:
            family_template = families_by_id.get(family_id)
            template = templates_by_id.get(template_id)
            if family_template is None:
                errors.append(f"local-core template source missing family {family_id}")
            elif template is None:
                errors.append(f"local-core template source missing template {template_id}")
            else:
                expect_equal(
                    errors,
                    f"{family_id} local-core template id",
                    family_template.get("template_id"),
                    template_id,
                )
                expect_equal(
                    errors,
                    f"{family_id} local-core template status",
                    family_template.get("status"),
                    family_crosswalk.get("template_status"),
                )
                template_shape_fields = _self_edge_shape_fields(
                    errors,
                    family_id=family_id,
                    template_id=template_id,
                    family_template=family_template,
                    template=template,
                )
        certificate_count = sum(int(record["certificate_count"]) for record in records)
        certificate_counts = [int(record["certificate_count"]) for record in records]
        if len(set(certificate_counts)) != 1:
            errors.append(f"certificate count is not stable for {family_id}")

        row_count_counters = []
        variant_counters = []
        cancelled_counters = []
        zero_counters = []
        center_counter: Counter[int] = Counter()
        certificate_count_per_hit_row_values = set()
        for record in records:
            row_counter = Counter(
                int(certificate["row"])
                for certificate in record.get("certificates", [])
                if isinstance(certificate, dict)
            )
            row_count_counters.append(Counter({len(row_counter): 1}))
            variant_counters.append(
                Counter(
                    str(certificate.get("variant"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                )
            )
            cancelled_counters.append(
                Counter(
                    str(certificate.get("cancelled_product"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                )
            )
            zero_counters.append(
                Counter(
                    str(certificate.get("zero_product", {}).get("expression"))
                    for certificate in record.get("certificates", [])
                    if isinstance(certificate, dict)
                    and isinstance(certificate.get("zero_product"), dict)
                )
            )
            center_counter.update(row_counter)
            certificate_count_per_hit_row_values.update(row_counter.values())

        row_count_distribution: Counter[int] = Counter()
        for counter in row_count_counters:
            row_count_distribution.update(counter)
        hit_row_count = next(iter(row_count_counters[0]))
        certs_per_hit_row = (
            next(iter(certificate_count_per_hit_row_values))
            if len(certificate_count_per_hit_row_values) == 1
            else None
        )
        if certs_per_hit_row is None:
            errors.append(f"certificate count per hit row is not stable for {family_id}")

        signature_key = (
            f"row_ptolemy_product|hit_rows={hit_row_count}|"
            f"certs_per_row={certs_per_hit_row}|cancelled=d01*d23|zero=d03*d12"
        )
        rows.append(
            {
                "family_id": family_id,
                "template_id": family_crosswalk.get("template_id"),
                "template_status": family_crosswalk.get("template_status"),
                "family_orbit_size": int(records[0]["family_orbit_size"]),
                "hit_assignment_count": len(records),
                "hit_certificate_count": certificate_count,
                "certificate_count_per_assignment": certificate_counts[0],
                "hit_row_count_per_assignment": int(hit_row_count),
                "certificate_count_per_hit_row": int(certs_per_hit_row or 0),
                "rows_with_certificates_per_assignment_counts": _json_counter(
                    row_count_distribution,
                ),
                "certificate_count_by_center": _json_counter(center_counter),
                "variant_counts_per_assignment": _same_counter(
                    errors,
                    label="variant_counts_per_assignment",
                    family_id=family_id,
                    counters=variant_counters,
                ),
                "cancelled_product_counts_per_assignment": _same_counter(
                    errors,
                    label="cancelled_product_counts_per_assignment",
                    family_id=family_id,
                    counters=cancelled_counters,
                ),
                "zero_product_expression_counts_per_assignment": _same_counter(
                    errors,
                    label="zero_product_expression_counts_per_assignment",
                    family_id=family_id,
                    counters=zero_counters,
                ),
                "signature_key": signature_key,
                **template_shape_fields,
            }
        )
    return rows


def signature_payload(
    source: dict[str, Any],
    template_source: dict[str, Any],
) -> dict[str, Any]:
    """Return a derived per-family signature diagnostic."""

    errors = validate_row_ptolemy_payload(source, recompute=False)
    if errors:
        raise ValueError(f"source row-Ptolemy artifact invalid: {errors[0]}")
    signature_errors: list[str] = []
    signature_rows = _signature_rows(source, template_source, signature_errors)
    if signature_errors:
        raise ValueError(f"signature derivation failed: {signature_errors[0]}")

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": source["n"],
        "witness_size": source["witness_size"],
        "cyclic_order": source["cyclic_order"],
        "family_count": len(signature_rows),
        "hit_assignment_count": sum(
            int(row["hit_assignment_count"]) for row in signature_rows
        ),
        "hit_certificate_count": sum(
            int(row["hit_certificate_count"]) for row in signature_rows
        ),
        "signature_rows": signature_rows,
        "interpretation": [
            "Rows summarize stable certificate histograms within each row-Ptolemy hit family.",
            "The signatures are prompts for local-lemma extraction, not local lemmas by themselves.",
            "Each underlying certificate remains fixed-pattern and fixed-row-order only.",
            "The local-core shape fields are copied from the review-pending template diagnostic for comparison only.",
            "No proof of the n=9 case is claimed.",
        ],
        "source_artifacts": _source_artifacts(source, template_source),
        "provenance": PROVENANCE,
    }
    assert_expected_signature_counts(payload)
    return payload


def assert_expected_signature_counts(payload: dict[str, Any]) -> None:
    """Assert stable expected values for the signature diagnostic."""

    if payload["schema"] != SCHEMA:
        raise AssertionError(f"unexpected schema: {payload['schema']}")
    if payload["status"] != STATUS:
        raise AssertionError(f"unexpected status: {payload['status']}")
    if payload["trust"] != TRUST:
        raise AssertionError(f"unexpected trust: {payload['trust']}")
    if payload["claim_scope"] != CLAIM_SCOPE:
        raise AssertionError("claim scope changed")
    if payload["family_count"] != 3:
        raise AssertionError(f"unexpected family count: {payload['family_count']}")
    if payload["hit_assignment_count"] != 26:
        raise AssertionError(
            f"unexpected hit assignment count: {payload['hit_assignment_count']}",
        )
    if payload["hit_certificate_count"] != 216:
        raise AssertionError(
            f"unexpected hit certificate count: {payload['hit_certificate_count']}",
        )
    if payload["signature_rows"] != EXPECTED_SIGNATURE_ROWS:
        raise AssertionError("unexpected signature rows")


def validate_payload(
    payload: Any,
    *,
    source: Any | None = None,
    template_source: Any | None = None,
    recompute: bool = True,
) -> list[str]:
    """Return validation errors for a loaded signature artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    if set(payload) != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(payload)!r}"
        )
    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": 9,
        "witness_size": 4,
        "cyclic_order": list(range(9)),
        "family_count": 3,
        "hit_assignment_count": 26,
        "hit_certificate_count": 216,
        "signature_rows": EXPECTED_SIGNATURE_ROWS,
        "provenance": PROVENANCE,
        "source_artifacts": EXPECTED_SOURCE_ARTIFACTS,
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    interpretation = payload.get("interpretation")
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
    else:
        required = (
            "The signatures are prompts for local-lemma extraction, not local lemmas by themselves.",
            "The local-core shape fields are copied from the review-pending template diagnostic for comparison only.",
            "No proof of the n=9 case is claimed.",
        )
        for phrase in required:
            if phrase not in interpretation:
                errors.append(f"interpretation must include {phrase!r}")

    try:
        assert_expected_signature_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected signature counts failed: {exc}")

    if recompute:
        if source is None:
            try:
                source = load_artifact(DEFAULT_ROW_PTOLEMY_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load source row-Ptolemy artifact: {exc}")
                source = None
        if template_source is None:
            try:
                template_source = load_artifact(DEFAULT_CORE_TEMPLATE_ARTIFACT)
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"failed to load local-core template artifact: {exc}")
                template_source = None
        if isinstance(source, dict):
            if not isinstance(template_source, dict):
                errors.append("local-core template artifact must be an object")
            else:
                try:
                    expected_payload = signature_payload(source, template_source)
                except (AssertionError, TypeError, ValueError) as exc:
                    errors.append(f"recomputed signature diagnostic failed: {exc}")
                else:
                    expect_equal(errors, "signature diagnostic", payload, expected_payload)
        else:
            errors.append("source row-Ptolemy artifact must be an object")
    return errors


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    return {
        "ok": not errors,
        "artifact": display_path(path, ROOT),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "family_count": object_payload.get("family_count"),
        "hit_assignment_count": object_payload.get("hit_assignment_count"),
        "hit_certificate_count": object_payload.get("hit_certificate_count"),
        "signature_keys": [
            row.get("signature_key")
            for row in object_payload.get("signature_rows", [])
            if isinstance(row, dict)
        ],
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source", type=Path, default=DEFAULT_ROW_PTOLEMY_ARTIFACT)
    parser.add_argument(
        "--template-source",
        type=Path,
        default=DEFAULT_CORE_TEMPLATE_ARTIFACT,
        help="local-core template diagnostic used for shape metadata",
    )
    parser.add_argument("--out", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--write", action="store_true", help="write generated diagnostic")
    parser.add_argument("--check", action="store_true", help="validate an existing diagnostic")
    parser.add_argument("--json", action="store_true", help="print stable JSON summary")
    parser.add_argument("--assert-expected", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    template_source_path = (
        args.template_source
        if args.template_source.is_absolute()
        else ROOT / args.template_source
    )
    out = args.out if args.out.is_absolute() else ROOT / args.out

    try:
        source = load_artifact(source_path)
    except (OSError, json.JSONDecodeError) as exc:
        source = {}
        source_errors = [str(exc)]
    else:
        source_errors = validate_row_ptolemy_payload(source, recompute=False)

    try:
        template_source = load_artifact(template_source_path)
    except (OSError, json.JSONDecodeError) as exc:
        template_source = {}
        template_source_errors = [str(exc)]
    else:
        template_source_errors = validate_core_template_payload(
            template_source,
            recompute=False,
        )

    if args.write:
        if source_errors:
            for error in source_errors:
                print(f"source artifact invalid: {error}", file=sys.stderr)
            return 1
        if template_source_errors:
            for error in template_source_errors:
                print(f"local-core template artifact invalid: {error}", file=sys.stderr)
            return 1
        payload = signature_payload(source, template_source)
        if args.assert_expected:
            assert_expected_signature_counts(payload)
        write_json(payload, out)
        if not args.check:
            if args.json:
                print(json.dumps(summary_payload(out, payload, []), indent=2, sort_keys=True))
            else:
                print(f"wrote {display_path(out, ROOT)}")
            return 0

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(
            payload,
            source=source,
            template_source=template_source,
            recompute=args.check or args.assert_expected,
        )
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]
    if source_errors:
        errors.extend(f"source artifact invalid: {error}" for error in source_errors)
    if template_source_errors:
        errors.extend(
            f"local-core template artifact invalid: {error}"
            for error in template_source_errors
        )

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact, ROOT)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy family-signature diagnostic")
        print(f"artifact: {summary['artifact']}")
        print(f"families: {summary['family_count']}")
        print(f"hit assignments: {summary['hit_assignment_count']}")
        print(f"hit certificates: {summary['hit_certificate_count']}")
        if args.check or args.assert_expected:
            print("OK: row-Ptolemy family-signature checks passed")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
