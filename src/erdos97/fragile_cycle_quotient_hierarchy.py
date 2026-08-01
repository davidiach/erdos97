"""Exact admissible-role quotients of small convex certificate templates.

The templates in this module are proof-mining objects.  They retain only the
distance equalities used by a strict Kalmanson certificate and forget all
unused witnesses.  A role quotient may identify formal labels except when an
identification would:

* collapse a distance pair used by a retained equality;
* collapse two vertices of one strict Kalmanson quadrilateral; or
* make the marked quadrilateral orders incompatible with one cyclic order.

The certificate then pushes forward to the role quotient.  Coordinatewise
nonpositive quotient coefficients remain nonpositive after quotient classes
are merged, so every enumerated quotient is checked with exact integer
arithmetic.  This is a local certificate diagnostic, not a bridge proving
that an arbitrary counterexample contains one of the templates.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Iterator, Mapping, Sequence

from erdos97.fragile_turn_pivot_guardrail import selected_rows as z16_rows
from erdos97.quotient_cone import (
    KALMANSON_KINDS,
    UnionFind,
    kalmanson_row,
    kalmanson_terms,
    pair,
    selected_distance_quotient,
)

Pair = tuple[int, int]
EqualityGroup = tuple[Pair, ...]

SCHEMA = "erdos97.fragile_cycle_quotient_hierarchy.v1"
STATUS = "EXACT_BRIDGE_TEMPLATE_DIAGNOSTIC"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact admissible-role-quotient classification for three stored convex "
    "certificate templates: the n=9 equilateral hinge, the fixed-order Z/16 "
    "marked-three-cycle inverse pair, and the scalable-family k=8 four-row "
    "circuit. The classification proves only certificate pushforward for "
    "these local templates. It does not force a template in an arbitrary "
    "counterexample, does not close a fragile-cycle bridge, does not prove "
    "n=9 or any arbitrary-size case, does not claim a Euclidean realization "
    "or counterexample, and does not update the official/global status of "
    "Erdos Problem #97."
)
CONCLUSION = (
    "The retained one-, two-, and four-inequality certificate templates are "
    "stable under every enumerated admissible role quotient. The hinge and "
    "Z/16 inverse templates are role-rigid under the stated marked-order "
    "rules. The scalable k=8 four-row template has exactly two nontrivial "
    "seven-role quotients, obtained by identifying roles 18 with 23 or roles "
    "23 with 27. This is quotient-closed proof-mining evidence only; the "
    "missing bridge must still force one of the certificate templates or a "
    "separate geometric alternative."
)
PROVENANCE = {
    "generator": "scripts/check_fragile_cycle_quotient_hierarchy.py",
    "command": (
        "python scripts/check_fragile_cycle_quotient_hierarchy.py "
        "--write --assert-expected"
    ),
}


@dataclass(frozen=True)
class TemplateStrictRow:
    """One weighted strict Kalmanson row on formal roles."""

    kind: str
    quad: tuple[int, int, int, int]
    weight: int = 1


@dataclass(frozen=True)
class CertificateTemplate:
    """A local equality quotient and its strict certificate."""

    name: str
    context: str
    labels: tuple[int, ...]
    equality_groups: tuple[EqualityGroup, ...]
    strict_rows: tuple[TemplateStrictRow, ...]
    selected_centers: tuple[int, ...]
    support_minimality: Mapping[str, object]


def certificate_templates() -> tuple[CertificateTemplate, ...]:
    """Return the three deterministic hierarchy benchmarks."""

    return (
        CertificateTemplate(
            name="n9_equilateral_hinge",
            context=(
                "The arbitrary-size local hinge extracted from all 184 "
                "review-pending n=9 frontier assignments."
            ),
            labels=(0, 1, 2, 3),
            equality_groups=(
                ((0, 1), (0, 2), (1, 2)),
                ((0, 3), (1, 3)),
            ),
            strict_rows=(
                TemplateStrictRow("K2_diag_gt_other", (0, 1, 2, 3)),
            ),
            selected_centers=(0, 1, 3),
            support_minimality={
                "strict_inequality_count": 1,
                "status": "tautologically_minimal_positive_support",
                "evidence": (
                    "One strict Kalmanson row reduces to zero after the three "
                    "retained rich-pair equalities."
                ),
            },
        ),
        CertificateTemplate(
            name="z16_marked_three_cycle_inverse",
            context=(
                "The exact fixed-order Kalmanson inverse pair rejecting the "
                "Z/16 fragile/turn/pivot marked-three-cycle guardrail."
            ),
            labels=(0, 3, 7, 9, 13),
            equality_groups=(
                ((0, 7), (7, 9)),
                ((0, 9), (0, 13)),
                ((3, 13), (0, 3)),
            ),
            strict_rows=(
                TemplateStrictRow("K1_diag_gt_sides", (0, 3, 7, 9)),
                TemplateStrictRow("K2_diag_gt_other", (0, 3, 9, 13)),
            ),
            selected_centers=(0, 3, 7),
            support_minimality={
                "strict_inequality_count": 2,
                "status": "fixed_order_minimal",
                "evidence": (
                    "An exhaustive scan of all 2*binom(16,4)=3640 strict "
                    "Kalmanson rows finds no one-row nonpositive quotient "
                    "certificate; the displayed inverse pair sums to zero."
                ),
            },
        ),
        CertificateTemplate(
            name="scalable_k8_four_circuit",
            context=(
                "The support-minimal four-inequality circuit in the k=8 "
                "member of the scalable strict-cycle bridge control."
            ),
            labels=(1, 8, 16, 18, 23, 27, 37, 44),
            equality_groups=(
                ((8, 27), (1, 8)),
                ((18, 37), (18, 27)),
                ((1, 23), (16, 23)),
                ((16, 44), (37, 44)),
            ),
            strict_rows=(
                TemplateStrictRow("K1_diag_gt_sides", (1, 8, 16, 27)),
                TemplateStrictRow("K2_diag_gt_other", (16, 18, 27, 37)),
                TemplateStrictRow("K2_diag_gt_other", (1, 16, 23, 37)),
                TemplateStrictRow("K1_diag_gt_sides", (1, 16, 37, 44)),
            ),
            selected_centers=(8, 18, 23, 44),
            support_minimality={
                "strict_inequality_count": 4,
                "status": "family_specific_minimal_by_existing_exact_control",
                "evidence": (
                    "The existing all-k Presburger replay excludes positive "
                    "Kalmanson circuits with at most three inequalities for "
                    "every k>=8, while these four rows sum to zero at k=8."
                ),
                "dependency_commands": [
                    (
                        "python scripts/check_scalable_kalmanson_inverse_control.py "
                        "--assert-expected --json"
                    ),
                    (
                        "python scripts/check_scalable_kalmanson_three_control.py "
                        "--assert-expected --json"
                    ),
                ],
            },
        ),
    )


def restricted_growth_partitions(size: int) -> Iterator[tuple[int, ...]]:
    """Yield every set partition as a restricted-growth string."""

    if size <= 0:
        raise ValueError("partition size must be positive")
    values = [0] * size

    def visit(index: int, maximum: int) -> Iterator[tuple[int, ...]]:
        if index == size:
            yield tuple(values)
            return
        for value in range(maximum + 2):
            values[index] = value
            yield from visit(index + 1, max(maximum, value))

    yield from visit(1, 0)


def _mapped_pair(role_index: Mapping[int, int], partition: Sequence[int], raw: Pair) -> Pair:
    return pair(partition[role_index[raw[0]]], partition[role_index[raw[1]]])


def _cyclically_ordered(quad: Sequence[int], positions: Mapping[int, int]) -> bool:
    size = len(positions)
    base = positions[int(quad[0])]
    offsets = [(positions[int(label)] - base) % size for label in quad]
    return offsets[0] == 0 and offsets[1] < offsets[2] < offsets[3]


def feasible_cyclic_orders(
    mapped_quads: Sequence[Sequence[int]],
    block_count: int,
) -> tuple[tuple[int, ...], ...]:
    """Return all rotation-normalized cyclic orders satisfying marked quads."""

    if block_count <= 0:
        raise ValueError("block_count must be positive")
    orders: list[tuple[int, ...]] = []
    for tail in permutations(range(1, block_count)):
        order = (0, *tail)
        positions = {label: index for index, label in enumerate(order)}
        if all(_cyclically_ordered(quad, positions) for quad in mapped_quads):
            orders.append(order)
    return tuple(orders)


def verify_mapped_certificate(
    template: CertificateTemplate,
    partition: Sequence[int],
    cyclic_order: Sequence[int],
) -> dict[str, object]:
    """Verify one role quotient by exact pushforward arithmetic."""

    role_index = {label: index for index, label in enumerate(template.labels)}
    block_count = max(partition) + 1
    all_pairs = [pair(left, right) for left, right in combinations(range(block_count), 2)]
    quotient = UnionFind(all_pairs)

    mapped_equality_groups: list[list[list[int]]] = []
    for equality_group in template.equality_groups:
        mapped = [_mapped_pair(role_index, partition, raw) for raw in equality_group]
        base = mapped[0]
        for other in mapped[1:]:
            quotient.union(base, other)
        mapped_equality_groups.append([[left, right] for left, right in mapped])

    combined: Counter[Pair] = Counter()
    mapped_rows: list[dict[str, object]] = []
    mapped_quads: list[tuple[int, int, int, int]] = []
    for strict_row in template.strict_rows:
        mapped_quad = tuple(
            partition[role_index[label]] for label in strict_row.quad
        )
        if len(set(mapped_quad)) != 4:
            raise ValueError("strict quadrilateral collapsed in role quotient")
        mapped_quads.append(mapped_quad)  # type: ignore[arg-type]
        for raw_pair, coefficient in kalmanson_terms(strict_row.kind, mapped_quad):
            combined[quotient.find(raw_pair)] += strict_row.weight * coefficient
        mapped_rows.append(
            {
                "kind": strict_row.kind,
                "quad": list(mapped_quad),
                "weight": strict_row.weight,
            }
        )

    positions = {label: index for index, label in enumerate(cyclic_order)}
    order_verified = all(
        _cyclically_ordered(mapped_quad, positions) for mapped_quad in mapped_quads
    )
    coefficients = [value for value in combined.values() if value]
    return {
        "mapped_equality_groups": mapped_equality_groups,
        "strict_rows": mapped_rows,
        "cyclic_order_verified": order_verified,
        "combined_nonzero_coefficient_count": len(coefficients),
        "combined_positive_coefficient_count": sum(value > 0 for value in coefficients),
        "zero_sum_verified": not coefficients,
        "nonpositive_sum_verified": all(value <= 0 for value in coefficients),
    }


def enumerate_admissible_quotients(template: CertificateTemplate) -> dict[str, object]:
    """Enumerate every admissible role partition and compatible cyclic order."""

    _validate_template(template)
    role_index = {label: index for index, label in enumerate(template.labels)}
    counters: Counter[str] = Counter()
    records: list[dict[str, object]] = []

    for partition in restricted_growth_partitions(len(template.labels)):
        counters["partitions_considered"] += 1
        mapped_quads = [
            tuple(partition[role_index[label]] for label in strict_row.quad)
            for strict_row in template.strict_rows
        ]
        if any(len(set(quad)) != 4 for quad in mapped_quads):
            counters["rejected_strict_quad_collision"] += 1
            continue
        if any(
            partition[role_index[left]] == partition[role_index[right]]
            for equality_group in template.equality_groups
            for left, right in equality_group
        ):
            counters["rejected_equality_pair_loop"] += 1
            continue

        block_count = max(partition) + 1
        orders = feasible_cyclic_orders(mapped_quads, block_count)
        if not orders:
            counters["rejected_cyclic_order_incompatibility"] += 1
            continue

        counters["admissible_partitions"] += 1
        counters["admissible_ordered_quotients"] += len(orders)
        counters[f"admissible_vertex_count_{block_count}"] += 1
        if block_count < len(template.labels):
            counters["nontrivial_admissible_partitions"] += 1

        role_blocks = [
            [
                label
                for label, block in zip(template.labels, partition)
                if block == block_index
            ]
            for block_index in range(block_count)
        ]
        certificate = verify_mapped_certificate(template, partition, orders[0])
        if not certificate["zero_sum_verified"]:
            raise AssertionError(
                f"{template.name} quotient certificate did not push forward"
            )
        records.append(
            {
                "partition": list(partition),
                "role_blocks": role_blocks,
                "vertex_count": block_count,
                "compatible_cyclic_order_count": len(orders),
                "canonical_cyclic_order": list(orders[0]),
                "certificate": certificate,
            }
        )

    records.sort(
        key=lambda record: (
            int(record["vertex_count"]),
            record["partition"],
            record["canonical_cyclic_order"],
        )
    )
    return {
        "partition_accounting": {
            key: counters[key]
            for key in (
                "partitions_considered",
                "rejected_strict_quad_collision",
                "rejected_equality_pair_loop",
                "rejected_cyclic_order_incompatibility",
                "admissible_partitions",
                "admissible_ordered_quotients",
                "nontrivial_admissible_partitions",
            )
        },
        "admissible_vertex_count_histogram": {
            key.removeprefix("admissible_vertex_count_"): value
            for key, value in sorted(counters.items())
            if key.startswith("admissible_vertex_count_")
        },
        "quotients": records,
    }


def _validate_template(template: CertificateTemplate) -> None:
    labels = set(template.labels)
    if len(labels) != len(template.labels):
        raise ValueError(f"{template.name}: duplicate formal labels")
    if not template.strict_rows:
        raise ValueError(f"{template.name}: no strict rows")
    for strict_row in template.strict_rows:
        if strict_row.kind not in KALMANSON_KINDS:
            raise ValueError(f"{template.name}: unknown kind {strict_row.kind}")
        if strict_row.weight <= 0:
            raise ValueError(f"{template.name}: nonpositive strict-row weight")
        if len(set(strict_row.quad)) != 4 or not set(strict_row.quad) <= labels:
            raise ValueError(f"{template.name}: invalid strict quadrilateral")
    for equality_group in template.equality_groups:
        if len(equality_group) < 2:
            raise ValueError(f"{template.name}: singleton equality group")
        for left, right in equality_group:
            if left == right or left not in labels or right not in labels:
                raise ValueError(f"{template.name}: invalid equality pair")


def _z16_one_row_scan() -> dict[str, object]:
    rows = z16_rows()
    quotient = selected_distance_quotient(rows)
    zero_rows = 0
    nonpositive_rows = 0
    strict_rows_checked = 0
    for quad in combinations(range(16), 4):
        for kind in KALMANSON_KINDS:
            strict_rows_checked += 1
            vector = kalmanson_row(quotient, kind, quad).vector
            zero_rows += all(value == 0 for value in vector)
            nonpositive_rows += all(value <= 0 for value in vector)
    return {
        "strict_rows_checked": strict_rows_checked,
        "zero_sum_row_count": zero_rows,
        "nonpositive_row_count": nonpositive_rows,
        "one_row_certificate_absent": nonpositive_rows == 0,
    }


def _template_payload(template: CertificateTemplate) -> dict[str, object]:
    enumeration = enumerate_admissible_quotients(template)
    role_index = {label: index for index, label in enumerate(template.labels)}
    identity_partition = tuple(range(len(template.labels)))
    identity_orders = feasible_cyclic_orders(
        [
            tuple(role_index[label] for label in strict_row.quad)
            for strict_row in template.strict_rows
        ],
        len(template.labels),
    )
    if not identity_orders:
        raise AssertionError(f"{template.name}: identity order is infeasible")
    identity_check = verify_mapped_certificate(
        template,
        identity_partition,
        identity_orders[0],
    )
    payload: dict[str, object] = {
        "name": template.name,
        "context": template.context,
        "formal_labels": list(template.labels),
        "selected_centers": list(template.selected_centers),
        "equality_groups": [
            [[left, right] for left, right in equality_group]
            for equality_group in template.equality_groups
        ],
        "strict_rows": [
            {
                "kind": strict_row.kind,
                "quad": list(strict_row.quad),
                "weight": strict_row.weight,
            }
            for strict_row in template.strict_rows
        ],
        "strict_inequality_support": len(template.strict_rows),
        "selected_center_support": len(template.selected_centers),
        "identity_certificate": identity_check,
        "support_minimality": dict(template.support_minimality),
        **enumeration,
    }
    if template.name == "z16_marked_three_cycle_inverse":
        payload["one_row_fixed_order_scan"] = _z16_one_row_scan()
    return payload


def hierarchy_payload() -> dict[str, object]:
    """Return the stable exact quotient-hierarchy artifact payload."""

    templates = [_template_payload(template) for template in certificate_templates()]
    quotient_records = [
        {
            "name": template["name"],
            "quotients": template["quotients"],
        }
        for template in templates
    ]
    digest = hashlib.sha256(
        json.dumps(
            quotient_records,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    return {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "hierarchy_definition": {
            "levels": [1, 2, 4],
            "coordinates": [
                "strict_inequality_support",
                "selected_center_support",
                "admissible_role_quotient_vertex_count",
            ],
            "admissibility": [
                "each strict Kalmanson quadrilateral remains injective",
                "each retained equal-distance pair remains a nonloop",
                "all marked quadrilateral orders fit one target cyclic order",
            ],
            "pushforward_principle": (
                "Merging role and distance classes sums source quotient "
                "coefficients. A nonnegative combination that is "
                "coordinatewise nonpositive remains so after every "
                "admissible quotient."
            ),
        },
        "templates": templates,
        "summary": {
            "template_count": len(templates),
            "strict_support_levels": [
                int(template["strict_inequality_support"])
                for template in templates
            ],
            "admissible_partition_count": sum(
                int(template["partition_accounting"]["admissible_partitions"])
                for template in templates
            ),
            "admissible_ordered_quotient_count": sum(
                int(
                    template["partition_accounting"][
                        "admissible_ordered_quotients"
                    ]
                )
                for template in templates
            ),
            "nontrivial_admissible_partition_count": sum(
                int(
                    template["partition_accounting"][
                        "nontrivial_admissible_partitions"
                    ]
                )
                for template in templates
            ),
            "all_quotient_certificates_zero_sum": all(
                quotient["certificate"]["zero_sum_verified"]
                for template in templates
                for quotient in template["quotients"]
            ),
            "quotient_catalog_sha256": digest,
        },
        "limitations": [
            "The three templates are benchmarks, not a complete fragile-cycle catalogue.",
            "Unused halo roles are forgotten; the artifact classifies quotients only of the retained certificate support.",
            "Admissibility preserves marked strict-quadrilateral order but does not assert Euclidean realizability.",
            "The scalable k=8 minimality statement depends on the separately checked all-k inverse/three-row controls.",
            "No arbitrary counterexample is proved to contain any template in this hierarchy.",
            "No proof, counterexample, n=9 promotion, or official/global status update is claimed.",
        ],
        "conclusion": CONCLUSION,
        "provenance": dict(PROVENANCE),
    }


EXPECTED_TEMPLATE_ACCOUNTING = {
    "n9_equilateral_hinge": {
        "partitions_considered": 15,
        "rejected_strict_quad_collision": 14,
        "rejected_equality_pair_loop": 0,
        "rejected_cyclic_order_incompatibility": 0,
        "admissible_partitions": 1,
        "admissible_ordered_quotients": 1,
        "nontrivial_admissible_partitions": 0,
    },
    "z16_marked_three_cycle_inverse": {
        "partitions_considered": 52,
        "rejected_strict_quad_collision": 50,
        "rejected_equality_pair_loop": 0,
        "rejected_cyclic_order_incompatibility": 1,
        "admissible_partitions": 1,
        "admissible_ordered_quotients": 1,
        "nontrivial_admissible_partitions": 0,
    },
    "scalable_k8_four_circuit": {
        "partitions_considered": 4140,
        "rejected_strict_quad_collision": 4088,
        "rejected_equality_pair_loop": 0,
        "rejected_cyclic_order_incompatibility": 49,
        "admissible_partitions": 3,
        "admissible_ordered_quotients": 5,
        "nontrivial_admissible_partitions": 2,
    },
}


def assert_expected_payload(payload: Mapping[str, object]) -> None:
    """Assert the stable pilot counts and claim boundaries."""

    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("conclusion", CONCLUSION),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            raise AssertionError(
                f"{key}: expected {expected!r}, got {payload.get(key)!r}"
            )

    templates = payload.get("templates")
    if not isinstance(templates, list) or len(templates) != 3:
        raise AssertionError("expected exactly three hierarchy templates")
    observed_names = [template.get("name") for template in templates]
    if observed_names != list(EXPECTED_TEMPLATE_ACCOUNTING):
        raise AssertionError(f"unexpected template order: {observed_names!r}")

    for template in templates:
        name = str(template["name"])
        if template.get("partition_accounting") != EXPECTED_TEMPLATE_ACCOUNTING[name]:
            raise AssertionError(f"{name}: partition accounting changed")
        identity = template.get("identity_certificate")
        if not isinstance(identity, Mapping) or identity.get("zero_sum_verified") is not True:
            raise AssertionError(f"{name}: identity certificate is not zero-sum")
        quotients = template.get("quotients")
        if not isinstance(quotients, list):
            raise AssertionError(f"{name}: quotient records must be a list")
        if not all(
            isinstance(record, Mapping)
            and isinstance(record.get("certificate"), Mapping)
            and record["certificate"].get("zero_sum_verified") is True
            for record in quotients
        ):
            raise AssertionError(f"{name}: quotient pushforward failed")

    z16 = templates[1]
    if z16.get("one_row_fixed_order_scan") != {
        "strict_rows_checked": 3640,
        "zero_sum_row_count": 0,
        "nonpositive_row_count": 0,
        "one_row_certificate_absent": True,
    }:
        raise AssertionError("Z/16 one-row scan changed")

    scalable = templates[2]
    nontrivial_blocks = [
        record["role_blocks"]
        for record in scalable["quotients"]
        if record["vertex_count"] == 7
    ]
    if nontrivial_blocks != [
        [[1], [8], [16], [18, 23], [27], [37], [44]],
        [[1], [8], [16], [18], [23, 27], [37], [44]],
    ]:
        raise AssertionError(f"unexpected scalable quotient blocks: {nontrivial_blocks!r}")

    summary = payload.get("summary")
    if not isinstance(summary, Mapping):
        raise AssertionError("summary must be an object")
    for key, expected in (
        ("template_count", 3),
        ("strict_support_levels", [1, 2, 4]),
        ("admissible_partition_count", 5),
        ("admissible_ordered_quotient_count", 7),
        ("nontrivial_admissible_partition_count", 2),
        ("all_quotient_certificates_zero_sum", True),
    ):
        if summary.get(key) != expected:
            raise AssertionError(
                f"summary.{key}: expected {expected!r}, got {summary.get(key)!r}"
            )
    digest = summary.get("quotient_catalog_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        raise AssertionError("summary quotient catalog digest is malformed")


def validate_payload(payload: Mapping[str, object]) -> list[str]:
    """Compare a stored payload with deterministic regeneration."""

    errors: list[str] = []
    try:
        assert_expected_payload(payload)
    except (AssertionError, KeyError, TypeError, ValueError) as exc:
        errors.append(str(exc))
        return errors
    if payload != hierarchy_payload():
        errors.append("stored payload differs from complete regenerated hierarchy")
    return errors


__all__ = [
    "CLAIM_SCOPE",
    "CONCLUSION",
    "PROVENANCE",
    "SCHEMA",
    "STATUS",
    "TRUST",
    "CertificateTemplate",
    "TemplateStrictRow",
    "assert_expected_payload",
    "certificate_templates",
    "enumerate_admissible_quotients",
    "feasible_cyclic_orders",
    "hierarchy_payload",
    "restricted_growth_partitions",
    "validate_payload",
    "verify_mapped_certificate",
]
