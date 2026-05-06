#!/usr/bin/env python3
"""Validate the n=9 row-Ptolemy product-cancellation artifact."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from functools import lru_cache
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

from erdos97 import n9_vertex_circle_exhaustive as n9  # noqa: E402
from erdos97.incidence_filters import (  # noqa: E402
    row_ptolemy_product_cancellation_certificates,
)
from erdos97.n9_row_ptolemy_product_cancellations import (  # noqa: E402
    CLAIM_SCOPE,
    EXPECTED_CERTIFICATE_COUNT_BY_CENTER,
    EXPECTED_CERTIFICATES_PER_HIT_ASSIGNMENT,
    EXPECTED_HIT_ASSIGNMENT_STATUS_COUNTS,
    EXPECTED_HIT_ASSIGNMENTS,
    EXPECTED_HIT_CERTIFICATES,
    EXPECTED_HIT_FAMILIES,
    EXPECTED_HIT_FAMILY_COUNTS,
    EXPECTED_HIT_FAMILY_TEMPLATE_IDS,
    EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS,
    EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS,
    EXPECTED_HIT_TEMPLATE_STATUS_COUNTS,
    EXPECTED_NONHIT_FAMILY_COUNT,
    EXPECTED_NONHIT_FAMILY_ORBIT_SIZE_SUM,
    EXPECTED_NONHIT_TEMPLATE_IDS,
    EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
    EXPECTED_PRE_VERTEX_CIRCLE_NODES,
    EXPECTED_STRICT_CYCLE_HIT_FAMILY_COUNT,
    EXPECTED_STRICT_CYCLE_NONHIT_FAMILY_COUNT,
    PROVENANCE,
    SCHEMA,
    STATUS,
    TEMPLATE_CROSSWALK_CLAIM_SCOPE,
    TEMPLATE_CROSSWALK_SOURCE_PATH,
    TRUST,
    _family_labels,
    assert_expected_counts,
    row_ptolemy_product_cancellation_report,
)
from erdos97.n9_vertex_circle_obstruction_shapes import (  # noqa: E402
    _rows_from_assignment,
    canonical_dihedral_rows,
    pre_vertex_circle_assignments,
)
from scripts.check_n9_vertex_circle_core_templates import (  # noqa: E402
    validate_payload as validate_template_payload,
)

DEFAULT_ARTIFACT = (
    ROOT / "data" / "certificates" / "n9_row_ptolemy_product_cancellations.json"
)
DEFAULT_TEMPLATE_ARTIFACT = ROOT / TEMPLATE_CROSSWALK_SOURCE_PATH
EXPECTED_TOP_LEVEL_KEYS = {
    "claim_scope",
    "cyclic_order",
    "filter",
    "hit_records",
    "hit_summary",
    "interpretation",
    "n",
    "provenance",
    "schema",
    "source_artifacts",
    "source_frontier",
    "status",
    "template_crosswalk",
    "trust",
    "witness_size",
}
EXPECTED_SOURCE_ARTIFACTS = [
    {
        "path": "data/certificates/n9_vertex_circle_exhaustive.json",
        "role": "review-pending source frontier count target",
    },
    {
        "path": "data/certificates/n9_vertex_circle_motif_families.json",
        "role": "deterministic family-id convention used for F02/F09/F13 labels",
    },
    {
        "path": TEMPLATE_CROSSWALK_SOURCE_PATH,
        "role": "review-pending local-core template labels used for the diagnostic crosswalk",
    },
    {
        "path": "data/runs/2026-05-05/new_obstructions.md",
        "role": "archived exploratory memo for the historical F15 alias",
    },
]
EXPECTED_CERTIFICATE_TYPE = "row_ptolemy_product_cancellation"
EXPECTED_CERTIFICATE_STATUS = "EXACT_OBSTRUCTION_FOR_FIXED_PATTERN_AND_FIXED_ROW_ORDER"
EXPECTED_PTOLEMY_IDENTITY = "d02*d13 = d01*d23 + d03*d12"
EXPECTED_CERTIFICATE_SCOPE = (
    "Exact obstruction for this fixed selected-witness row "
    "under the supplied/certified row order only."
)
EXPECTED_CONTRADICTION = (
    "Ptolemy cancellation forces a product of two ordinary distances to be "
    "zero, but distinct strictly convex vertices have positive Euclidean "
    "distances."
)
EXPECTED_ZERO_PRODUCT_BY_CANCELLED = {
    "d01*d23": "d03*d12",
    "d03*d12": "d01*d23",
}
PAIR_NAMES = {"d01", "d02", "d03", "d12", "d13", "d23"}

SourceAssignmentRecord = dict[str, object]


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a mismatch error when values differ."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def _validate_claim_scope(errors: list[str], claim_scope: Any) -> None:
    expect_equal(errors, "claim_scope", claim_scope, CLAIM_SCOPE)
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
        return
    lowered = claim_scope.lower()
    for phrase in (
        "not a proof",
        "not a counterexample",
        "not a geometric realizability test",
        "not a global status update",
    ):
        if phrase not in lowered:
            errors.append(f"claim_scope must include {phrase!r}")


def _validate_interpretation(errors: list[str], interpretation: Any) -> None:
    if not isinstance(interpretation, list) or not all(
        isinstance(item, str) for item in interpretation
    ):
        errors.append("interpretation must be a list of strings")
        return
    required = (
        "No proof of the n=9 case is claimed.",
        "The row order must be supplied or certified. This is not an orderless abstract-incidence obstruction.",
    )
    for phrase in required:
        if phrase not in interpretation:
            errors.append(f"interpretation must include {phrase!r}")


def _is_int(value: Any) -> bool:
    return type(value) is int


def _json_counter(counter: Counter[int] | Counter[str]) -> dict[str, int]:
    return {str(key): int(counter[key]) for key in sorted(counter)}


def _json_pair(pair: tuple[int, int]) -> list[int]:
    return [int(pair[0]), int(pair[1])]


def _normalize_pair(left: int, right: int) -> tuple[int, int]:
    return (left, right) if left < right else (right, left)


def _parse_cyclic_order(errors: list[str], raw_order: Any, n: int) -> list[int] | None:
    if not isinstance(raw_order, list) or len(raw_order) != n:
        errors.append(f"cyclic_order must be a list of length {n}")
        return None
    if not all(_is_int(label) for label in raw_order):
        errors.append("cyclic_order must contain integer labels")
        return None
    if sorted(raw_order) != list(range(n)):
        errors.append(f"cyclic_order must be a permutation of 0..{n - 1}")
        return None
    return [int(label) for label in raw_order]


def _row_witness_order(
    order: Sequence[int],
    center: int,
    witnesses: Sequence[int],
) -> list[int]:
    positions = {label: index for index, label in enumerate(order)}
    if center not in positions:
        raise ValueError(f"center {center} is missing from cyclic order")
    missing = [witness for witness in witnesses if witness not in positions]
    if missing:
        raise ValueError(f"witness {missing[0]} is missing from cyclic order")
    center_pos = positions[center]
    return sorted(witnesses, key=lambda witness: (positions[witness] - center_pos) % len(order))


def _ptolemy_pairs(witness_order: Sequence[int]) -> dict[str, tuple[int, int]]:
    w0, w1, w2, w3 = witness_order
    return {
        "d01": _normalize_pair(w0, w1),
        "d02": _normalize_pair(w0, w2),
        "d03": _normalize_pair(w0, w3),
        "d12": _normalize_pair(w1, w2),
        "d13": _normalize_pair(w1, w3),
        "d23": _normalize_pair(w2, w3),
    }


def _rows_key(rows: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(int(label) for label in row) for row in rows)


@lru_cache(maxsize=1)
def _source_assignment_records() -> tuple[SourceAssignmentRecord, ...]:
    assignments, nodes = pre_vertex_circle_assignments()
    rows_by_assignment = [_rows_from_assignment(assign) for assign in assignments]
    family_labels, family_orbit_sizes = _family_labels(rows_by_assignment)

    if nodes != EXPECTED_PRE_VERTEX_CIRCLE_NODES:
        raise AssertionError(f"unexpected source nodes: {nodes}")
    if len(assignments) != EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS:
        raise AssertionError(f"unexpected source assignments: {len(assignments)}")

    rows = []
    for assignment_index, (assign, selected_rows) in enumerate(
        zip(assignments, rows_by_assignment),
    ):
        family_id = family_labels[canonical_dihedral_rows(selected_rows)]
        rows.append(
            {
                "assignment_index": assignment_index,
                "selected_rows": _rows_key(selected_rows),
                "family_id": family_id,
                "family_orbit_size": family_orbit_sizes[family_id],
                "vertex_circle_status": n9.vertex_circle_status(assign),
            }
        )
    return tuple(rows)


def _source_records_or_errors(errors: list[str]) -> tuple[SourceAssignmentRecord, ...]:
    try:
        return _source_assignment_records()
    except (AssertionError, ValueError) as exc:
        errors.append(f"source assignment replay failed: {exc}")
        return ()


def _parse_selected_rows(
    errors: list[str],
    raw_rows: Any,
    *,
    label: str,
    n: int,
    witness_size: int,
) -> list[list[int]] | None:
    if not isinstance(raw_rows, list) or len(raw_rows) != n:
        errors.append(f"{label} selected_rows must be a list of {n} rows")
        return None

    rows: list[list[int]] = []
    for row_index, raw_row in enumerate(raw_rows):
        row_label = f"{label} selected_rows[{row_index}]"
        if not isinstance(raw_row, list) or len(raw_row) != witness_size:
            errors.append(f"{row_label} must contain {witness_size} witnesses")
            return None
        if not all(_is_int(witness) for witness in raw_row):
            errors.append(f"{row_label} must contain integer labels")
            return None
        row = [int(witness) for witness in raw_row]
        if len(set(row)) != witness_size:
            errors.append(f"{row_label} must not repeat witnesses")
            return None
        if row_index in row:
            errors.append(f"{row_label} must not select its center")
            return None
        if any(witness < 0 or witness >= n for witness in row):
            errors.append(f"{row_label} contains a label outside 0..{n - 1}")
            return None
        rows.append(row)
    return rows


def _validate_named_pair(
    errors: list[str],
    *,
    label: str,
    name: Any,
    pair: Any,
    expected_pairs: dict[str, tuple[int, int]],
) -> None:
    if not isinstance(name, str):
        errors.append(f"{label} has invalid Ptolemy pair name {name!r}")
        return
    if name not in expected_pairs:
        errors.append(f"{label} has unknown Ptolemy pair name {name!r}")
        return
    if pair != _json_pair(expected_pairs[str(name)]):
        errors.append(
            f"{label} pair mismatch for {name}: "
            f"expected {_json_pair(expected_pairs[str(name)])!r}, got {pair!r}"
        )


def _validate_certificate_shape(
    errors: list[str],
    *,
    record_label: str,
    certificate_index: int,
    certificate: Any,
    selected_rows: Sequence[Sequence[int]],
    cyclic_order: Sequence[int],
) -> int | None:
    cert_label = f"{record_label} certificates[{certificate_index}]"
    if not isinstance(certificate, dict):
        errors.append(f"{cert_label} must be an object")
        return None

    expect_equal(errors, f"{cert_label} type", certificate.get("type"), EXPECTED_CERTIFICATE_TYPE)
    expect_equal(
        errors,
        f"{cert_label} status",
        certificate.get("status"),
        EXPECTED_CERTIFICATE_STATUS,
    )
    expect_equal(
        errors,
        f"{cert_label} Ptolemy identity",
        certificate.get("ptolemy_identity"),
        EXPECTED_PTOLEMY_IDENTITY,
    )
    expect_equal(errors, f"{cert_label} scope", certificate.get("scope"), EXPECTED_CERTIFICATE_SCOPE)
    expect_equal(
        errors,
        f"{cert_label} contradiction",
        certificate.get("contradiction"),
        EXPECTED_CONTRADICTION,
    )

    row = certificate.get("row")
    if not _is_int(row) or not 0 <= int(row) < len(selected_rows):
        errors.append(f"{cert_label} row must be an integer in 0..{len(selected_rows) - 1}")
        return None
    row = int(row)

    try:
        expected_witness_order = _row_witness_order(cyclic_order, row, selected_rows[row])
    except ValueError as exc:
        errors.append(f"{cert_label} witness_order could not be checked: {exc}")
        return row
    expect_equal(
        errors,
        f"{cert_label} witness_order",
        certificate.get("witness_order"),
        expected_witness_order,
    )
    expected_pairs = _ptolemy_pairs(expected_witness_order)

    forced_equalities = certificate.get("forced_equalities")
    if not isinstance(forced_equalities, list) or len(forced_equalities) != 2:
        errors.append(f"{cert_label} forced_equalities must contain two rows")
    else:
        for equality_index, equality in enumerate(forced_equalities):
            equality_label = f"{cert_label} forced_equalities[{equality_index}]"
            if not isinstance(equality, dict):
                errors.append(f"{equality_label} must be an object")
                continue
            _validate_named_pair(
                errors,
                label=f"{equality_label} left_pair",
                name=equality.get("left"),
                pair=equality.get("left_pair"),
                expected_pairs=expected_pairs,
            )
            _validate_named_pair(
                errors,
                label=f"{equality_label} right_pair",
                name=equality.get("right"),
                pair=equality.get("right_pair"),
                expected_pairs=expected_pairs,
            )
            if not isinstance(equality.get("left"), str) or not isinstance(
                equality.get("right"),
                str,
            ):
                continue
            if equality.get("left") not in PAIR_NAMES or equality.get("right") not in PAIR_NAMES:
                continue
            if not _is_int(equality.get("distance_class")):
                errors.append(f"{equality_label} distance_class must be an integer")
            if not _is_int(equality.get("class_member_count")):
                errors.append(f"{equality_label} class_member_count must be an integer")

    cancelled_product = certificate.get("cancelled_product")
    if isinstance(cancelled_product, str):
        expected_zero_product = EXPECTED_ZERO_PRODUCT_BY_CANCELLED.get(cancelled_product)
    else:
        expected_zero_product = None
    if expected_zero_product is None:
        errors.append(f"{cert_label} has unknown cancelled_product {cancelled_product!r}")

    zero_product = certificate.get("zero_product")
    if not isinstance(zero_product, dict):
        errors.append(f"{cert_label} zero_product must be an object")
    else:
        factors = zero_product.get("factors")
        if not isinstance(factors, list) or len(factors) != 2:
            errors.append(f"{cert_label} zero_product factors must contain two rows")
        else:
            names = []
            for factor_index, factor in enumerate(factors):
                factor_label = f"{cert_label} zero_product.factors[{factor_index}]"
                if not isinstance(factor, dict):
                    errors.append(f"{factor_label} must be an object")
                    continue
                names.append(factor.get("name"))
                _validate_named_pair(
                    errors,
                    label=f"{factor_label} pair",
                    name=factor.get("name"),
                    pair=factor.get("pair"),
                    expected_pairs=expected_pairs,
                )
                if not _is_int(factor.get("distance_class")):
                    errors.append(f"{factor_label} distance_class must be an integer")
            expression = "*".join(str(name) for name in names)
            expect_equal(
                errors,
                f"{cert_label} zero_product expression",
                zero_product.get("expression"),
                expression,
            )
            if expected_zero_product is not None:
                expect_equal(
                    errors,
                    f"{cert_label} zero_product for cancelled product",
                    zero_product.get("expression"),
                    expected_zero_product,
                )

    return row


def _validate_hit_records(
    errors: list[str],
    payload: dict[str, Any],
    *,
    bind_source_assignments: bool,
) -> None:
    summary = payload.get("hit_summary")
    records = payload.get("hit_records")
    if not isinstance(summary, dict):
        errors.append("hit_summary must be an object")
        return
    if not isinstance(records, list):
        errors.append("hit_records must be a list")
        return

    n = payload.get("n")
    witness_size = payload.get("witness_size")
    if not _is_int(n) or not _is_int(witness_size):
        errors.append("n and witness_size must be integers before hit_records can be checked")
        return
    cyclic_order = _parse_cyclic_order(errors, payload.get("cyclic_order"), int(n))
    if cyclic_order is None:
        return

    assignment_indices: list[int] = []
    status_counts: Counter[str] = Counter()
    family_hit_counts: Counter[str] = Counter()
    certificate_count_by_center: Counter[int] = Counter()
    certificates_per_hit: Counter[int] = Counter()
    family_orbit_sizes: dict[str, int] = {}
    total_certificates = 0
    source_records = _source_records_or_errors(errors) if bind_source_assignments else ()
    source_assignment_count = (
        len(source_records) if source_records else EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS
    )
    selected_row_keys: Counter[tuple[tuple[int, ...], ...]] = Counter()

    for record_index, record in enumerate(records):
        record_label = f"hit_records[{record_index}]"
        if not isinstance(record, dict):
            errors.append(f"{record_label} must be an object")
            continue

        assignment_index = record.get("assignment_index")
        if not _is_int(assignment_index):
            errors.append(f"{record_label} assignment_index must be an integer")
            assignment_index = None
        else:
            assignment_index = int(assignment_index)
            assignment_indices.append(assignment_index)
            if not 0 <= assignment_index < source_assignment_count:
                errors.append(
                    f"{record_label} assignment_index {assignment_index} is outside "
                    f"the source range 0..{source_assignment_count - 1}"
                )

        family_id = record.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(f"{record_label} family_id must be a non-empty string")
            family_id = ""
        family_orbit_size = record.get("family_orbit_size")
        if not _is_int(family_orbit_size) or int(family_orbit_size) <= 0:
            errors.append(f"{record_label} family_orbit_size must be a positive integer")
        elif family_id:
            previous = family_orbit_sizes.setdefault(family_id, int(family_orbit_size))
            if previous != int(family_orbit_size):
                errors.append(f"{record_label} family_orbit_size conflicts for {family_id}")

        vertex_circle_status = record.get("vertex_circle_status")
        if not isinstance(vertex_circle_status, str) or not vertex_circle_status:
            errors.append(f"{record_label} vertex_circle_status must be a non-empty string")
            vertex_circle_status = ""

        selected_rows = _parse_selected_rows(
            errors,
            record.get("selected_rows"),
            label=record_label,
            n=int(n),
            witness_size=int(witness_size),
        )
        certificates = record.get("certificates")
        if not isinstance(certificates, list):
            errors.append(f"{record_label} certificates must be a list")
            continue
        certificate_count = record.get("certificate_count")
        expect_equal(
            errors,
            f"{record_label} certificate_count",
            certificate_count,
            len(certificates),
        )

        if vertex_circle_status:
            status_counts[vertex_circle_status] += 1
        if family_id:
            family_hit_counts[family_id] += 1
        certificates_per_hit[len(certificates)] += 1
        total_certificates += len(certificates)

        if selected_rows is None:
            continue
        selected_rows_key = _rows_key(selected_rows)
        selected_row_keys[selected_rows_key] += 1
        if (
            bind_source_assignments
            and source_records
            and assignment_index is not None
            and 0 <= assignment_index < len(source_records)
        ):
            source_record = source_records[assignment_index]
            expect_equal(
                errors,
                f"{record_label} selected_rows for assignment_index {assignment_index}",
                selected_rows_key,
                source_record["selected_rows"],
            )
            expect_equal(
                errors,
                f"{record_label} family_id for assignment_index {assignment_index}",
                family_id,
                source_record["family_id"],
            )
            expect_equal(
                errors,
                f"{record_label} family_orbit_size for assignment_index {assignment_index}",
                family_orbit_size,
                source_record["family_orbit_size"],
            )
            expect_equal(
                errors,
                f"{record_label} vertex_circle_status for assignment_index {assignment_index}",
                vertex_circle_status,
                source_record["vertex_circle_status"],
            )
        for certificate_index, certificate in enumerate(certificates):
            row = _validate_certificate_shape(
                errors,
                record_label=record_label,
                certificate_index=certificate_index,
                certificate=certificate,
                selected_rows=selected_rows,
                cyclic_order=cyclic_order,
            )
            if row is not None:
                certificate_count_by_center[row] += 1

        try:
            expected_certificates = row_ptolemy_product_cancellation_certificates(
                selected_rows,
                cyclic_order,
            )
        except ValueError as exc:
            errors.append(f"{record_label} certificates could not be replayed: {exc}")
        else:
            expect_equal(
                errors,
                f"{record_label} replayed certificates",
                certificates,
                expected_certificates,
            )

    if len(assignment_indices) != len(set(assignment_indices)):
        errors.append("hit_records assignment_index values must be unique")
    if assignment_indices != sorted(assignment_indices):
        errors.append("hit_records assignment_index values must be sorted")
    duplicate_rows = [rows for rows, count in selected_row_keys.items() if count > 1]
    if duplicate_rows:
        errors.append("hit_records selected_rows values must be unique")

    family_rows = [
        {
            "family_id": family_id,
            "hit_assignment_count": int(family_hit_counts[family_id]),
            "family_orbit_size": int(family_orbit_sizes.get(family_id, 0)),
        }
        for family_id in sorted(family_hit_counts)
    ]

    expect_equal(errors, "hit_records count", len(records), summary.get("hit_assignment_count"))
    expect_equal(
        errors,
        "hit_records certificate total",
        total_certificates,
        summary.get("hit_certificate_count"),
    )
    expect_equal(errors, "hit_records family count", len(family_hit_counts), summary.get("hit_family_count"))
    expect_equal(
        errors,
        "hit_records status counts",
        dict(sorted(status_counts.items())),
        summary.get("hit_assignment_vertex_circle_status_counts"),
    )
    expect_equal(errors, "hit_records family counts", family_rows, summary.get("hit_family_counts"))
    expect_equal(
        errors,
        "hit_records certificate center counts",
        _json_counter(certificate_count_by_center),
        summary.get("certificate_count_by_center"),
    )
    expect_equal(
        errors,
        "hit_records certificates-per-hit histogram",
        _json_counter(certificates_per_hit),
        summary.get("certificates_per_hit_assignment_counts"),
    )


def _template_family_maps(
    errors: list[str],
    template_payload: Any,
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    if not isinstance(template_payload, dict):
        errors.append("template crosswalk source top level must be an object")
        return {}, {}
    template_errors = validate_template_payload(template_payload, recompute=False)
    errors.extend(f"template crosswalk source invalid: {error}" for error in template_errors)

    raw_families = template_payload.get("families")
    raw_templates = template_payload.get("templates")
    if not isinstance(raw_families, list):
        errors.append("template crosswalk source families must be a list")
        return {}, {}
    if not isinstance(raw_templates, list):
        errors.append("template crosswalk source templates must be a list")
        return {}, {}

    families_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_family in enumerate(raw_families):
        if not isinstance(raw_family, dict):
            errors.append(f"template crosswalk source families[{index}] must be an object")
            continue
        family_id = raw_family.get("family_id")
        if not isinstance(family_id, str) or not family_id:
            errors.append(f"template crosswalk source families[{index}] has invalid family_id")
            continue
        families_by_id[family_id] = raw_family

    templates_by_id: dict[str, dict[str, Any]] = {}
    for index, raw_template in enumerate(raw_templates):
        if not isinstance(raw_template, dict):
            errors.append(f"template crosswalk source templates[{index}] must be an object")
            continue
        template_id = raw_template.get("template_id")
        if not isinstance(template_id, str) or not template_id:
            errors.append(f"template crosswalk source templates[{index}] has invalid template_id")
            continue
        templates_by_id[template_id] = raw_template
    return families_by_id, templates_by_id


def _template_family_row(errors: list[str], family: dict[str, Any], key: str) -> Any:
    if key not in family:
        errors.append(f"template crosswalk source family {family.get('family_id')!r} missing {key}")
        return None
    return family[key]


def _template_int_field(errors: list[str], row: dict[str, Any], key: str, label: str) -> int:
    value = row.get(key)
    if _is_int(value):
        return int(value)
    errors.append(f"{label} {key} must be an integer")
    return 0


def _hit_family_counts_from_records(
    payload: dict[str, Any],
) -> tuple[Counter[str], Counter[str]]:
    family_hit_counts: Counter[str] = Counter()
    family_certificate_counts: Counter[str] = Counter()
    records = payload.get("hit_records")
    if not isinstance(records, list):
        return family_hit_counts, family_certificate_counts
    for record in records:
        if not isinstance(record, dict):
            continue
        family_id = record.get("family_id")
        certificate_count = record.get("certificate_count")
        if isinstance(family_id, str) and _is_int(certificate_count):
            family_hit_counts[family_id] += 1
            family_certificate_counts[family_id] += int(certificate_count)
    return family_hit_counts, family_certificate_counts


def _expected_template_crosswalk(
    *,
    errors: list[str],
    payload: dict[str, Any],
    families_by_id: dict[str, dict[str, Any]],
    templates_by_id: dict[str, dict[str, Any]],
    template_payload: dict[str, Any],
) -> dict[str, Any]:
    family_hit_counts, family_certificate_counts = _hit_family_counts_from_records(payload)

    hit_family_template_ids: dict[str, str] = {}
    hit_family_rows = []
    template_assignment_counts: Counter[str] = Counter()
    template_certificate_counts: Counter[str] = Counter()

    for family_id in sorted(family_hit_counts):
        family = families_by_id[family_id]
        template_id = _template_family_row(errors, family, "template_id")
        status = _template_family_row(errors, family, "status")
        core_size = _template_family_row(errors, family, "core_size")
        strict_edge_count = _template_family_row(errors, family, "strict_edge_count")
        orbit_size = _template_family_row(errors, family, "orbit_size")
        if template_id is None:
            continue
        template_id = str(template_id)
        template = templates_by_id.get(template_id)
        if template is None:
            errors.append(f"template crosswalk source missing template {template_id!r}")
            continue
        hit_assignment_count = int(family_hit_counts[family_id])
        hit_certificate_count = int(family_certificate_counts[family_id])
        template_assignment_counts[template_id] += hit_assignment_count
        template_certificate_counts[template_id] += hit_certificate_count
        hit_family_template_ids[family_id] = template_id
        hit_family_rows.append(
            {
                "family_id": family_id,
                "template_id": template_id,
                "template_status": str(status),
                "template_core_size": int(core_size) if _is_int(core_size) else 0,
                "template_strict_edge_count": (
                    int(strict_edge_count) if _is_int(strict_edge_count) else 0
                ),
                "family_orbit_size": int(orbit_size) if _is_int(orbit_size) else 0,
                "hit_assignment_count": hit_assignment_count,
                "hit_certificate_count": hit_certificate_count,
                "certificate_count_per_hit_assignment": (
                    hit_certificate_count // hit_assignment_count
                ),
                "template_family_count": _template_int_field(
                    errors,
                    template,
                    "family_count",
                    f"template crosswalk source template {template_id}",
                ),
                "template_orbit_size_sum": _template_int_field(
                    errors,
                    template,
                    "orbit_size_sum",
                    f"template crosswalk source template {template_id}",
                ),
            }
        )

    template_status_counts = Counter(
        str(templates_by_id[template_id].get("status"))
        for template_id in template_assignment_counts
    )
    hit_template_rows = []
    for template_id in sorted(template_assignment_counts):
        template = templates_by_id[template_id]
        hit_families = sorted(
            family_id
            for family_id, row_template_id in hit_family_template_ids.items()
            if row_template_id == template_id
        )
        hit_template_rows.append(
            {
                "template_id": template_id,
                "template_status": str(template.get("status")),
                "families": hit_families,
                "hit_family_count": len(hit_families),
                "hit_assignment_count": int(template_assignment_counts[template_id]),
                "hit_certificate_count": int(template_certificate_counts[template_id]),
            }
        )

    all_family_ids = set(families_by_id)
    hit_family_ids = set(hit_family_template_ids)
    nonhit_family_ids = sorted(all_family_ids - hit_family_ids)
    return {
        "claim_scope": TEMPLATE_CROSSWALK_CLAIM_SCOPE,
        "source_artifact": {
            "path": TEMPLATE_CROSSWALK_SOURCE_PATH,
            "schema": template_payload.get("schema"),
            "status": template_payload.get("status"),
            "trust": template_payload.get("trust"),
        },
        "hit_template_count": len(template_assignment_counts),
        "hit_family_template_ids": hit_family_template_ids,
        "hit_template_assignment_counts": {
            template_id: int(template_assignment_counts[template_id])
            for template_id in sorted(template_assignment_counts)
        },
        "hit_template_certificate_counts": {
            template_id: int(template_certificate_counts[template_id])
            for template_id in sorted(template_certificate_counts)
        },
        "hit_template_status_counts": {
            status: int(template_status_counts[status])
            for status in sorted(template_status_counts)
        },
        "strict_cycle_hit_family_count": sum(
            1
            for family_id in hit_family_ids
            if families_by_id[family_id].get("status") == "strict_cycle"
        ),
        "nonhit_family_count": len(nonhit_family_ids),
        "nonhit_family_orbit_size_sum": sum(
            _template_int_field(
                errors,
                families_by_id[family_id],
                "orbit_size",
                f"template crosswalk source family {family_id}",
            )
            for family_id in nonhit_family_ids
        ),
        "strict_cycle_nonhit_family_count": sum(
            1
            for family_id in nonhit_family_ids
            if families_by_id[family_id].get("status") == "strict_cycle"
        ),
        "nonhit_template_ids": sorted(
            {
                str(families_by_id[family_id].get("template_id"))
                for family_id in nonhit_family_ids
                if families_by_id[family_id].get("template_id") is not None
            }
        ),
        "hit_family_rows": hit_family_rows,
        "hit_template_rows": hit_template_rows,
    }


def _validate_template_crosswalk(
    errors: list[str],
    payload: dict[str, Any],
    template_payload: Any,
) -> None:
    crosswalk = payload.get("template_crosswalk")
    if not isinstance(crosswalk, dict):
        errors.append("template_crosswalk must be an object")
        return

    if not isinstance(template_payload, dict):
        _template_family_maps(errors, template_payload)
        return
    families_by_id, templates_by_id = _template_family_maps(errors, template_payload)
    if not families_by_id or not templates_by_id:
        return

    family_hit_counts, _certificate_counts = _hit_family_counts_from_records(payload)
    missing_families = sorted(set(family_hit_counts) - set(families_by_id))
    if missing_families:
        errors.append(
            "template_crosswalk missing source family rows for "
            f"{missing_families!r}"
        )
        return
    missing_template_ids = sorted(
        {
            str(families_by_id[family_id].get("template_id"))
            for family_id in family_hit_counts
        }
        - set(templates_by_id)
    )
    if missing_template_ids:
        errors.append(
            "template_crosswalk missing source template rows for "
            f"{missing_template_ids!r}"
        )
        return

    expected = _expected_template_crosswalk(
        errors=errors,
        payload=payload,
        families_by_id=families_by_id,
        templates_by_id=templates_by_id,
        template_payload=template_payload,
    )
    expect_equal(errors, "template_crosswalk", crosswalk, expected)

    expect_equal(
        errors,
        "template_crosswalk hit_family_template_ids",
        crosswalk.get("hit_family_template_ids"),
        EXPECTED_HIT_FAMILY_TEMPLATE_IDS,
    )
    expect_equal(
        errors,
        "template_crosswalk hit_template_assignment_counts",
        crosswalk.get("hit_template_assignment_counts"),
        EXPECTED_HIT_TEMPLATE_ASSIGNMENT_COUNTS,
    )
    expect_equal(
        errors,
        "template_crosswalk hit_template_certificate_counts",
        crosswalk.get("hit_template_certificate_counts"),
        EXPECTED_HIT_TEMPLATE_CERTIFICATE_COUNTS,
    )
    expect_equal(
        errors,
        "template_crosswalk hit_template_status_counts",
        crosswalk.get("hit_template_status_counts"),
        EXPECTED_HIT_TEMPLATE_STATUS_COUNTS,
    )
    expect_equal(
        errors,
        "template_crosswalk strict_cycle_hit_family_count",
        crosswalk.get("strict_cycle_hit_family_count"),
        EXPECTED_STRICT_CYCLE_HIT_FAMILY_COUNT,
    )
    expect_equal(
        errors,
        "template_crosswalk nonhit_family_count",
        crosswalk.get("nonhit_family_count"),
        EXPECTED_NONHIT_FAMILY_COUNT,
    )
    expect_equal(
        errors,
        "template_crosswalk nonhit_family_orbit_size_sum",
        crosswalk.get("nonhit_family_orbit_size_sum"),
        EXPECTED_NONHIT_FAMILY_ORBIT_SIZE_SUM,
    )
    expect_equal(
        errors,
        "template_crosswalk strict_cycle_nonhit_family_count",
        crosswalk.get("strict_cycle_nonhit_family_count"),
        EXPECTED_STRICT_CYCLE_NONHIT_FAMILY_COUNT,
    )
    expect_equal(
        errors,
        "template_crosswalk nonhit_template_ids",
        crosswalk.get("nonhit_template_ids"),
        EXPECTED_NONHIT_TEMPLATE_IDS,
    )


def validate_payload(
    payload: Any,
    *,
    recompute: bool = True,
    template_payload: Any | None = None,
) -> list[str]:
    """Return validation errors for a loaded cancellation artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, "
            f"got {sorted(top_level_keys)!r}"
        )

    expected_meta = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "n": 9,
        "witness_size": 4,
        "cyclic_order": list(range(9)),
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    _validate_claim_scope(errors, payload.get("claim_scope"))
    _validate_interpretation(errors, payload.get("interpretation"))
    expect_equal(errors, "provenance", payload.get("provenance"), PROVENANCE)
    expect_equal(
        errors,
        "source_artifacts",
        payload.get("source_artifacts"),
        EXPECTED_SOURCE_ARTIFACTS,
    )

    source = payload.get("source_frontier")
    if isinstance(source, dict):
        expect_equal(
            errors,
            "source assignment count",
            source.get("assignment_count"),
            EXPECTED_PRE_VERTEX_CIRCLE_ASSIGNMENTS,
        )
        expect_equal(
            errors,
            "source nodes",
            source.get("nodes_visited"),
            EXPECTED_PRE_VERTEX_CIRCLE_NODES,
        )
        expect_equal(errors, "source families", source.get("dihedral_family_count"), 16)
    else:
        errors.append("source_frontier must be an object")

    summary = payload.get("hit_summary")
    if isinstance(summary, dict):
        expect_equal(
            errors,
            "hit assignment count",
            summary.get("hit_assignment_count"),
            EXPECTED_HIT_ASSIGNMENTS,
        )
        expect_equal(
            errors,
            "hit certificate count",
            summary.get("hit_certificate_count"),
            EXPECTED_HIT_CERTIFICATES,
        )
        expect_equal(
            errors,
            "hit family count",
            summary.get("hit_family_count"),
            EXPECTED_HIT_FAMILIES,
        )
        expect_equal(
            errors,
            "hit status counts",
            summary.get("hit_assignment_vertex_circle_status_counts"),
            EXPECTED_HIT_ASSIGNMENT_STATUS_COUNTS,
        )
        raw_family_counts = summary.get("hit_family_counts")
        if isinstance(raw_family_counts, list):
            family_counts = {}
            for index, row in enumerate(raw_family_counts):
                if not isinstance(row, dict):
                    errors.append(f"hit_family_counts[{index}] must be an object")
                    continue
                family_id = row.get("family_id")
                hit_assignment_count = row.get("hit_assignment_count")
                if not isinstance(family_id, str):
                    errors.append(f"hit_family_counts[{index}] family_id must be a string")
                    continue
                if not _is_int(hit_assignment_count):
                    errors.append(
                        f"hit_family_counts[{index}] hit_assignment_count must be an integer"
                    )
                    continue
                family_counts[family_id] = int(hit_assignment_count)
            expect_equal(errors, "hit family counts", family_counts, EXPECTED_HIT_FAMILY_COUNTS)
        else:
            errors.append("hit_family_counts must be a list")
        expect_equal(
            errors,
            "certificate center counts",
            summary.get("certificate_count_by_center"),
            EXPECTED_CERTIFICATE_COUNT_BY_CENTER,
        )
        expect_equal(
            errors,
            "certificates-per-hit histogram",
            summary.get("certificates_per_hit_assignment_counts"),
            EXPECTED_CERTIFICATES_PER_HIT_ASSIGNMENT,
        )
    else:
        errors.append("hit_summary must be an object")

    try:
        assert_expected_counts(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(f"expected row-Ptolemy counts failed: {exc}")
    _validate_hit_records(errors, payload, bind_source_assignments=not recompute)
    if template_payload is None:
        try:
            template_payload = load_artifact(DEFAULT_TEMPLATE_ARTIFACT)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"failed to load template crosswalk source: {exc}")
            template_payload = {}
    _validate_template_crosswalk(errors, payload, template_payload)

    if recompute:
        try:
            expected_payload = row_ptolemy_product_cancellation_report()
        except (AssertionError, ValueError) as exc:
            errors.append(f"recomputed row-Ptolemy report failed: {exc}")
        else:
            expect_equal(
                errors,
                "row-Ptolemy product-cancellation payload",
                payload,
                expected_payload,
            )
    return errors


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    source = object_payload.get("source_frontier", {})
    hit_summary = object_payload.get("hit_summary", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "source_assignment_count": (
            source.get("assignment_count") if isinstance(source, dict) else None
        ),
        "hit_assignment_count": (
            hit_summary.get("hit_assignment_count")
            if isinstance(hit_summary, dict)
            else None
        ),
        "hit_certificate_count": (
            hit_summary.get("hit_certificate_count")
            if isinstance(hit_summary, dict)
            else None
        ),
        "hit_family_count": (
            hit_summary.get("hit_family_count") if isinstance(hit_summary, dict) else None
        ),
        "hit_template_count": (
            object_payload.get("template_crosswalk", {}).get("hit_template_count")
            if isinstance(object_payload.get("template_crosswalk"), dict)
            else None
        ),
        "hit_family_template_ids": (
            object_payload.get("template_crosswalk", {}).get("hit_family_template_ids")
            if isinstance(object_payload.get("template_crosswalk"), dict)
            else None
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 row-Ptolemy product-cancellation artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"source assignments: {summary['source_assignment_count']}")
        print(f"hit assignments: {summary['hit_assignment_count']}")
        print(f"hit certificates: {summary['hit_certificate_count']}")
        print(f"hit families: {summary['hit_family_count']}")
        if args.check:
            print("OK: row-Ptolemy product-cancellation checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
