"""Exact dual identities for the n=9 vertex-circle relation skeletons.

The source relation-skeleton catalog records strict inequalities between
ordinary pair distances together with selected-row equality paths.  This
module turns each stored obstruction into one explicit positive-circuit
identity

    sum(strict distance differences) + sum(equality differences) = 0.

Every strict coefficient is one.  The equality multipliers are signed unit
coefficients obtained by orienting the stored equality paths.  The resulting
identity is an exact Farkas-style contradiction and is preserved when more
ordinary distance variables are identified.

This is proof-mining support for review-pending local packets.  It does not
prove that an arbitrary counterexample contains one of the source skeletons.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from typing import Any, Iterable, Iterator, Mapping, Sequence


SCHEMA = "erdos97.n9_vertex_circle_template_duals.v1"
STATUS = "REVIEW_PENDING_DIAGNOSTIC_ONLY"
TRUST = "REVIEW_PENDING_DIAGNOSTIC"
CLAIM_SCOPE = (
    "Exact unit-positive dual identities for the 16 stored n=9 vertex-circle "
    "relation skeletons, with transformed-certificate coverage of the 184 "
    "review-pending frontier assignments and exhaustive active-variable "
    "quotient-coarsening checks; not local-template forcing, not a proof of "
    "n=9, not a bridge proof, not a proof of Erdos Problem #97, not a "
    "counterexample, and not independent review of the source packets."
)
PROVENANCE = {
    "generator": "scripts/check_n9_vertex_circle_template_duals.py",
    "command": (
        "python scripts/check_n9_vertex_circle_template_duals.py "
        "--assert-expected --write"
    ),
}

RELATION_SKELETON_SCHEMA = "erdos97.relation_skeleton_catalog.v1"
FRONTIER_CLASSIFICATION_SCHEMA = (
    "erdos97.n9_vertex_circle_frontier_motif_classification.v1"
)

EXPECTED_N = 9
EXPECTED_SKELETON_COUNT = 16
EXPECTED_TEMPLATE_COUNT = 12
EXPECTED_FAMILY_COUNT = 16
EXPECTED_ASSIGNMENT_COUNT = 184
EXPECTED_CONTRADICTION_TYPE_COUNTS = {
    "strict_directed_cycle": 3,
    "strict_self_edge": 13,
}
EXPECTED_STRICT_TERM_COUNT_COUNTS = {"1": 13, "2": 1, "3": 2}
EXPECTED_EQUALITY_TERM_COUNT_COUNTS = {"3": 11, "4": 3, "5": 1, "6": 1}
EXPECTED_ACTIVE_PAIR_COUNT_COUNTS = {"4": 9, "5": 3, "6": 2, "7": 2}
EXPECTED_MAXIMUM_EQUALITY_TERM_COUNT = 6
EXPECTED_MAXIMUM_ACTIVE_PAIR_COUNT = 7
EXPECTED_TOTAL_QUOTIENT_PARTITIONS = 2451
EXPECTED_TRANSFORMED_CERTIFICATE_SHA256 = (
    "c60ce8833bd4b2fa7ad32e2e034091966369a77553614fffc2226dc4a0edf3eb"
)

Pair = tuple[int, int]
Vector = dict[Pair, int]


def _pair(value: Sequence[int]) -> Pair:
    if len(value) != 2:
        raise ValueError(f"pair must contain two labels: {value!r}")
    left, right = (int(value[0]), int(value[1]))
    if left == right:
        raise ValueError(f"pair labels must be distinct: {value!r}")
    if not (0 <= left < EXPECTED_N and 0 <= right < EXPECTED_N):
        raise ValueError(f"pair label outside 0..{EXPECTED_N - 1}: {value!r}")
    return (left, right) if left < right else (right, left)


def _pair_json(pair: Pair) -> list[int]:
    return [pair[0], pair[1]]


def _selected_rows(skeleton: Mapping[str, Any]) -> tuple[tuple[int, ...], ...]:
    hypotheses = skeleton.get("hypotheses")
    if not isinstance(hypotheses, Mapping):
        raise ValueError("skeleton hypotheses must be an object")
    raw_rows = hypotheses.get("selected_rows")
    if not isinstance(raw_rows, list):
        raise ValueError("skeleton selected_rows must be a list")
    rows = []
    for raw_row in raw_rows:
        if not isinstance(raw_row, list) or len(raw_row) != 5:
            raise ValueError(f"selected row must contain a center and four witnesses: {raw_row!r}")
        row = tuple(int(label) for label in raw_row)
        if len(set(row)) != 5:
            raise ValueError(f"selected row labels must be distinct: {raw_row!r}")
        rows.append(row)
    if len({row[0] for row in rows}) != len(rows):
        raise ValueError("local skeleton selected-row centers must be distinct")
    return tuple(rows)


def _row_key(row: Sequence[int]) -> tuple[int, tuple[int, ...]]:
    return int(row[0]), tuple(sorted(int(label) for label in row[1:]))


def _row_distance_pairs(row: Sequence[int]) -> set[Pair]:
    center = int(row[0])
    return {_pair((center, int(witness))) for witness in row[1:]}


def _supporting_rows(
    rows: Sequence[Sequence[int]],
    left_pair: Pair,
    right_pair: Pair,
) -> tuple[int, ...]:
    centers = []
    for row in rows:
        distances = _row_distance_pairs(row)
        if left_pair in distances and right_pair in distances:
            centers.append(int(row[0]))
    return tuple(sorted(centers))


def _add_pair_difference(
    vector: Vector,
    left_pair: Pair,
    right_pair: Pair,
    coefficient: int,
) -> None:
    vector[left_pair] = vector.get(left_pair, 0) + coefficient
    vector[right_pair] = vector.get(right_pair, 0) - coefficient
    if vector[left_pair] == 0:
        del vector[left_pair]
    if vector.get(right_pair) == 0:
        vector.pop(right_pair, None)


def _strict_edge_index(skeleton: Mapping[str, Any]) -> dict[tuple[Pair, Pair], dict[str, Any]]:
    relation = skeleton.get("relation_quotient")
    if not isinstance(relation, Mapping):
        raise ValueError("skeleton relation_quotient must be an object")
    raw_edges = relation.get("strict_edges")
    if not isinstance(raw_edges, list):
        raise ValueError("skeleton strict_edges must be a list")
    rows = _selected_rows(skeleton)
    row_keys = {_row_key(row) for row in rows}
    index: dict[tuple[Pair, Pair], dict[str, Any]] = {}
    for raw_edge in raw_edges:
        if not isinstance(raw_edge, Mapping):
            raise ValueError("strict edge must be an object")
        outer_pair = _pair(raw_edge["outer_pair"])
        inner_pair = _pair(raw_edge["inner_pair"])
        key = (outer_pair, inner_pair)
        if key in index:
            raise ValueError(f"duplicate displayed strict edge: {key!r}")
        row = int(raw_edge["row"])
        witness_order = tuple(int(label) for label in raw_edge["witness_order"])
        if len(witness_order) != 4 or len(set(witness_order)) != 4:
            raise ValueError("strict-edge witness_order must contain four distinct labels")
        if (row, tuple(sorted(witness_order))) not in row_keys:
            raise ValueError("strict edge is not supported by a listed selected row")
        if not set(outer_pair).issubset(witness_order):
            raise ValueError("strict outer pair is not contained in witness_order")
        if not set(inner_pair).issubset(witness_order):
            raise ValueError("strict inner pair is not contained in witness_order")
        outer_span = int(raw_edge["outer_span"])
        inner_span = int(raw_edge["inner_span"])
        if not (outer_span > inner_span >= 1):
            raise ValueError("strict edge must have a strictly larger outer span")
        index[key] = {
            "row": row,
            "witness_order": list(witness_order),
            "outer_span": outer_span,
            "inner_span": inner_span,
            "source": str(raw_edge["source"]),
        }
    return index


def _oriented_chain(
    raw_chain: Sequence[Sequence[int]],
    start_pair: Pair,
    end_pair: Pair,
) -> tuple[list[Pair], int]:
    chain = [_pair(raw_pair) for raw_pair in raw_chain]
    if len(chain) == 1:
        if chain[0] == start_pair == end_pair:
            return chain, 1
        raise ValueError("singleton equality chain must already join identical endpoint pairs")
    if chain[0] == start_pair and chain[-1] == end_pair:
        return chain, 1
    if chain[0] == end_pair and chain[-1] == start_pair:
        return list(reversed(chain)), -1
    raise ValueError(
        f"equality chain endpoints {chain[0]!r}, {chain[-1]!r} do not match "
        f"{start_pair!r}, {end_pair!r}"
    )


def _strict_term(
    outer_pair: Pair,
    inner_pair: Pair,
    edge_index: Mapping[tuple[Pair, Pair], Mapping[str, Any]],
) -> dict[str, Any]:
    metadata = edge_index.get((outer_pair, inner_pair))
    if metadata is None:
        raise ValueError(
            f"displayed strict edge missing for {outer_pair!r} > {inner_pair!r}"
        )
    return {
        "coefficient": 1,
        "outer_pair": _pair_json(outer_pair),
        "inner_pair": _pair_json(inner_pair),
        "row": int(metadata["row"]),
        "witness_order": list(metadata["witness_order"]),
        "outer_span": int(metadata["outer_span"]),
        "inner_span": int(metadata["inner_span"]),
        "source": str(metadata["source"]),
    }


def _equality_terms_for_chain(
    chain: Sequence[Pair],
    coefficient: int,
    rows: Sequence[Sequence[int]],
) -> list[dict[str, Any]]:
    terms = []
    for left_pair, right_pair in zip(chain, chain[1:]):
        supporting_rows = _supporting_rows(rows, left_pair, right_pair)
        if not supporting_rows:
            raise ValueError(
                f"equality {left_pair!r} = {right_pair!r} is unsupported by the local rows"
            )
        terms.append(
            {
                "coefficient": coefficient,
                "left_pair": _pair_json(left_pair),
                "right_pair": _pair_json(right_pair),
                "supporting_rows": list(supporting_rows),
            }
        )
    return terms


def _identity_balance(
    strict_terms: Sequence[Mapping[str, Any]],
    equality_terms: Sequence[Mapping[str, Any]],
) -> Vector:
    vector: Vector = {}
    for term in strict_terms:
        _add_pair_difference(
            vector,
            _pair(term["outer_pair"]),
            _pair(term["inner_pair"]),
            int(term["coefficient"]),
        )
    for term in equality_terms:
        _add_pair_difference(
            vector,
            _pair(term["left_pair"]),
            _pair(term["right_pair"]),
            int(term["coefficient"]),
        )
    return vector


def _balance_json(vector: Mapping[Pair, int]) -> list[dict[str, Any]]:
    return [
        {"pair": _pair_json(pair), "coefficient": int(vector[pair])}
        for pair in sorted(vector)
        if vector[pair]
    ]


def _restricted_growth_partitions(size: int) -> Iterator[tuple[int, ...]]:
    """Yield every set partition as a restricted-growth block-label tuple."""

    if size < 0:
        raise ValueError("partition size must be nonnegative")
    if size == 0:
        yield ()
        return
    labels = [0] * size

    def visit(index: int, maximum: int) -> Iterator[tuple[int, ...]]:
        if index == size:
            yield tuple(labels)
            return
        for label in range(maximum + 2):
            labels[index] = label
            yield from visit(index + 1, max(maximum, label))

    yield from visit(1, 0)


def _quotient_partition_check(
    strict_terms: Sequence[Mapping[str, Any]],
    equality_terms: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    active_pairs = sorted(
        {
            _pair(raw_pair)
            for term in (*strict_terms, *equality_terms)
            for raw_pair in (
                (term["outer_pair"], term["inner_pair"])
                if "outer_pair" in term
                else (term["left_pair"], term["right_pair"])
            )
        }
    )
    pair_index = {pair: index for index, pair in enumerate(active_pairs)}
    checked = 0
    for partition in _restricted_growth_partitions(len(active_pairs)):
        quotient_balance: dict[int, int] = {}

        def add(left: Pair, right: Pair, coefficient: int) -> None:
            left_block = partition[pair_index[left]]
            right_block = partition[pair_index[right]]
            quotient_balance[left_block] = quotient_balance.get(left_block, 0) + coefficient
            quotient_balance[right_block] = quotient_balance.get(right_block, 0) - coefficient

        for term in strict_terms:
            add(
                _pair(term["outer_pair"]),
                _pair(term["inner_pair"]),
                int(term["coefficient"]),
            )
        for term in equality_terms:
            add(
                _pair(term["left_pair"]),
                _pair(term["right_pair"]),
                int(term["coefficient"]),
            )
        if any(quotient_balance.values()):
            raise AssertionError("dual identity failed after an active-pair quotient")
        checked += 1
    return {
        "active_pair_count": len(active_pairs),
        "active_pairs": [_pair_json(pair) for pair in active_pairs],
        "set_partition_count": checked,
        "all_quotient_balances_zero": True,
    }


def _self_edge_certificate(skeleton: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    conclusion = skeleton.get("conclusion")
    relation = skeleton.get("relation_quotient")
    if not isinstance(conclusion, Mapping) or not isinstance(relation, Mapping):
        raise ValueError("self-edge skeleton conclusion/relation must be objects")
    outer_pair = _pair(conclusion["strict_from_pair"])
    inner_pair = _pair(conclusion["strict_to_pair"])
    raw_chains = relation.get("equality_chains")
    if not isinstance(raw_chains, list) or len(raw_chains) != 1:
        raise ValueError("self-edge skeleton must contain one equality chain")
    chain, orientation = _oriented_chain(raw_chains[0], outer_pair, inner_pair)
    rows = _selected_rows(skeleton)
    strict_terms = [_strict_term(outer_pair, inner_pair, _strict_edge_index(skeleton))]
    equality_terms = _equality_terms_for_chain(chain, -orientation, rows)
    return strict_terms, equality_terms


def _strict_cycle_certificate(skeleton: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    conclusion = skeleton.get("conclusion")
    if not isinstance(conclusion, Mapping):
        raise ValueError("strict-cycle skeleton conclusion must be an object")
    raw_steps = conclusion.get("quotient_cycle")
    if not isinstance(raw_steps, list) or len(raw_steps) < 2:
        raise ValueError("strict-cycle skeleton must contain at least two cycle steps")
    edge_index = _strict_edge_index(skeleton)
    rows = _selected_rows(skeleton)
    strict_terms: list[dict[str, Any]] = []
    equality_terms: list[dict[str, Any]] = []
    strict_from_pairs = [_pair(step["strict_from_pair"]) for step in raw_steps]
    for index, raw_step in enumerate(raw_steps):
        if not isinstance(raw_step, Mapping):
            raise ValueError("strict-cycle step must be an object")
        outer_pair = strict_from_pairs[index]
        inner_pair = _pair(raw_step["strict_to_pair"])
        next_outer_pair = _pair(raw_step["next_outer_pair"])
        if next_outer_pair != strict_from_pairs[(index + 1) % len(raw_steps)]:
            raise ValueError("strict-cycle next_outer_pair does not match the next strict edge")
        chain, orientation = _oriented_chain(
            raw_step["equality_chain_to_next_outer_pair"],
            inner_pair,
            next_outer_pair,
        )
        strict_terms.append(_strict_term(outer_pair, inner_pair, edge_index))
        equality_terms.extend(_equality_terms_for_chain(chain, orientation, rows))
    return strict_terms, equality_terms


def _certificate_record(skeleton: Mapping[str, Any]) -> dict[str, Any]:
    contradiction_type = str(skeleton["contradiction_type"])
    if contradiction_type == "strict_self_edge":
        strict_terms, equality_terms = _self_edge_certificate(skeleton)
    elif contradiction_type == "strict_directed_cycle":
        strict_terms, equality_terms = _strict_cycle_certificate(skeleton)
    else:
        raise ValueError(f"unsupported contradiction type: {contradiction_type!r}")
    balance = _identity_balance(strict_terms, equality_terms)
    if balance:
        raise AssertionError(
            f"{skeleton['skeleton_id']} dual identity does not cancel: {balance!r}"
        )
    if any(int(term["coefficient"]) <= 0 for term in strict_terms):
        raise AssertionError("every strict dual coefficient must be positive")
    if any(abs(int(term["coefficient"])) != 1 for term in equality_terms):
        raise AssertionError("every equality multiplier must be signed unit")
    quotient_check = _quotient_partition_check(strict_terms, equality_terms)
    coverage = skeleton.get("coverage")
    if not isinstance(coverage, Mapping):
        raise ValueError("skeleton coverage must be an object")
    return {
        "skeleton_id": str(skeleton["skeleton_id"]),
        "template_id": str(skeleton["source_template_id"]),
        "family_id": str(skeleton["source_family_id"]),
        "contradiction_type": contradiction_type,
        "coverage": {
            "assignment_count": int(coverage["assignment_count"]),
            "assignment_ids": [str(item) for item in coverage.get("assignment_ids", [])],
            "orbit_size_sum": int(coverage["orbit_size_sum"]),
        },
        "strict_terms": strict_terms,
        "equality_terms": equality_terms,
        "identity_balance": _balance_json(balance),
        "identity_verified_zero": True,
        "strict_coefficient_sum": sum(int(term["coefficient"]) for term in strict_terms),
        "equality_multiplier_l1": sum(abs(int(term["coefficient"])) for term in equality_terms),
        "positive_circuit_interpretation": (
            "Each strict term is d(outer)-d(inner)>0; equality terms vanish; "
            "the displayed exact coefficient identity equals zero."
        ),
        "active_pair_quotient_check": quotient_check,
    }


def _is_dihedral_label_map(label_map: Sequence[int]) -> bool:
    if sorted(int(label) for label in label_map) != list(range(EXPECTED_N)):
        return False
    step = (int(label_map[1]) - int(label_map[0])) % EXPECTED_N
    if step not in {1, EXPECTED_N - 1}:
        return False
    return all(
        int(label_map[index]) % EXPECTED_N
        == (int(label_map[0]) + step * index) % EXPECTED_N
        for index in range(EXPECTED_N)
    )


def _inverse_label_map(to_canonical: Sequence[int]) -> tuple[int, ...]:
    if not _is_dihedral_label_map(to_canonical):
        raise ValueError("assignment-to-canonical label map must be dihedral")
    inverse = [0] * EXPECTED_N
    for assignment_label, canonical_label in enumerate(to_canonical):
        inverse[int(canonical_label)] = assignment_label
    return tuple(inverse)


def _map_pair(pair: Pair, label_map: Sequence[int]) -> Pair:
    return _pair((int(label_map[pair[0]]), int(label_map[pair[1]])))


def _mapped_certificate_digest_record(
    assignment: Mapping[str, Any],
    certificate: Mapping[str, Any],
) -> dict[str, Any]:
    inverse = _inverse_label_map(assignment["to_canonical_label_map"])
    raw_core_rows = assignment.get("core_selected_rows")
    if not isinstance(raw_core_rows, list):
        raise ValueError("assignment core_selected_rows must be a list")
    core_row_keys = {_row_key(row) for row in raw_core_rows}
    transformed_strict_terms = []
    for term in certificate["strict_terms"]:
        row = inverse[int(term["row"])]
        witness_order = [inverse[int(label)] for label in term["witness_order"]]
        if (row, tuple(sorted(witness_order))) not in core_row_keys:
            raise ValueError("transformed strict term is not supported by the assignment core")
        transformed_strict_terms.append(
            {
                "coefficient": int(term["coefficient"]),
                "outer_pair": _pair_json(_map_pair(_pair(term["outer_pair"]), inverse)),
                "inner_pair": _pair_json(_map_pair(_pair(term["inner_pair"]), inverse)),
                "row": row,
            }
        )
    transformed_equality_terms = []
    core_rows = [tuple(int(label) for label in row) for row in raw_core_rows]
    for term in certificate["equality_terms"]:
        left_pair = _map_pair(_pair(term["left_pair"]), inverse)
        right_pair = _map_pair(_pair(term["right_pair"]), inverse)
        supporting_rows = _supporting_rows(core_rows, left_pair, right_pair)
        if not supporting_rows:
            raise ValueError("transformed equality term is not supported by the assignment core")
        transformed_equality_terms.append(
            {
                "coefficient": int(term["coefficient"]),
                "left_pair": _pair_json(left_pair),
                "right_pair": _pair_json(right_pair),
                "supporting_rows": list(supporting_rows),
            }
        )
    if _identity_balance(transformed_strict_terms, transformed_equality_terms):
        raise AssertionError("transformed assignment dual identity does not cancel")
    return {
        "assignment_id": str(assignment["assignment_id"]),
        "family_id": str(assignment["family_id"]),
        "template_id": str(assignment["template_id"]),
        "skeleton_id": str(certificate["skeleton_id"]),
        "strict_terms": transformed_strict_terms,
        "equality_terms": transformed_equality_terms,
    }


def _assignment_coverage(
    classification_payload: Mapping[str, Any],
    certificates: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    raw_assignments = classification_payload.get("assignments")
    if not isinstance(raw_assignments, list):
        raise ValueError("frontier classification assignments must be a list")
    by_family = {str(certificate["family_id"]): certificate for certificate in certificates}
    if len(by_family) != len(certificates):
        raise ValueError("template-dual certificates must have unique family ids")
    records = []
    family_counts: Counter[str] = Counter()
    template_counts: Counter[str] = Counter()
    seen_ids: set[str] = set()
    for raw_assignment in raw_assignments:
        if not isinstance(raw_assignment, Mapping):
            raise ValueError("frontier classification assignment must be an object")
        assignment_id = str(raw_assignment["assignment_id"])
        if assignment_id in seen_ids:
            raise ValueError(f"duplicate assignment id: {assignment_id}")
        seen_ids.add(assignment_id)
        family_id = str(raw_assignment["family_id"])
        certificate = by_family.get(family_id)
        if certificate is None:
            raise ValueError(f"no dual certificate for assignment family {family_id}")
        if str(raw_assignment["template_id"]) != str(certificate["template_id"]):
            raise ValueError(f"{assignment_id} template/family dual mismatch")
        source_assignment_ids = certificate["coverage"]["assignment_ids"]
        if source_assignment_ids and assignment_id not in source_assignment_ids:
            raise ValueError(f"{assignment_id} absent from source skeleton coverage")
        records.append(_mapped_certificate_digest_record(raw_assignment, certificate))
        family_counts[family_id] += 1
        template_counts[str(raw_assignment["template_id"])] += 1
    for family_id, certificate in by_family.items():
        expected_count = int(certificate["coverage"]["assignment_count"])
        if family_counts[family_id] != expected_count:
            raise ValueError(
                f"{family_id} assignment coverage mismatch: "
                f"expected {expected_count}, got {family_counts[family_id]}"
            )
    records.sort(key=lambda record: record["assignment_id"])
    encoded = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {
        "assignment_count": len(records),
        "unique_assignment_count": len(seen_ids),
        "family_count": len(family_counts),
        "template_count": len(template_counts),
        "family_assignment_counts": dict(sorted(family_counts.items())),
        "template_assignment_counts": dict(sorted(template_counts.items())),
        "transformed_certificate_sha256": sha256(encoded).hexdigest(),
        "all_transformed_identities_verified_zero": True,
        "all_transformed_terms_supported_by_assignment_cores": True,
        "all_label_maps_verified_dihedral": True,
    }


def _json_counter(values: Iterable[int | str]) -> dict[str, int]:
    counts = Counter(str(value) for value in values)
    return {key: int(counts[key]) for key in sorted(counts, key=lambda item: (len(item), item))}


def template_dual_payload(
    relation_skeleton_payload: Mapping[str, Any],
    frontier_classification_payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Build the exact template-dual certificate packet."""

    if relation_skeleton_payload.get("schema") != RELATION_SKELETON_SCHEMA:
        raise ValueError("unexpected relation-skeleton catalog schema")
    if frontier_classification_payload.get("schema") != FRONTIER_CLASSIFICATION_SCHEMA:
        raise ValueError("unexpected frontier-classification schema")
    raw_skeletons = relation_skeleton_payload.get("skeletons")
    if not isinstance(raw_skeletons, list):
        raise ValueError("relation-skeleton catalog must contain skeletons")
    certificates = sorted(
        (_certificate_record(skeleton) for skeleton in raw_skeletons),
        key=lambda record: str(record["skeleton_id"]),
    )
    assignment_coverage = _assignment_coverage(
        frontier_classification_payload,
        certificates,
    )
    contradiction_type_counts = _json_counter(
        str(certificate["contradiction_type"]) for certificate in certificates
    )
    strict_term_count_counts = _json_counter(
        len(certificate["strict_terms"]) for certificate in certificates
    )
    equality_term_count_counts = _json_counter(
        len(certificate["equality_terms"]) for certificate in certificates
    )
    active_pair_count_counts = _json_counter(
        int(certificate["active_pair_quotient_check"]["active_pair_count"])
        for certificate in certificates
    )
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": EXPECTED_N,
        "skeleton_count": len(certificates),
        "template_count": len({str(record["template_id"]) for record in certificates}),
        "family_count": len({str(record["family_id"]) for record in certificates}),
        "covered_assignment_count": int(assignment_coverage["assignment_count"]),
        "contradiction_type_counts": contradiction_type_counts,
        "strict_term_count_counts": strict_term_count_counts,
        "equality_term_count_counts": equality_term_count_counts,
        "active_pair_count_counts": active_pair_count_counts,
        "maximum_equality_term_count": max(
            len(certificate["equality_terms"]) for certificate in certificates
        ),
        "maximum_active_pair_count": max(
            int(certificate["active_pair_quotient_check"]["active_pair_count"])
            for certificate in certificates
        ),
        "total_active_pair_quotient_partitions_checked": sum(
            int(certificate["active_pair_quotient_check"]["set_partition_count"])
            for certificate in certificates
        ),
        "all_strict_coefficients_positive_unit": all(
            int(term["coefficient"]) == 1
            for certificate in certificates
            for term in certificate["strict_terms"]
        ),
        "all_equality_multipliers_signed_unit": all(
            abs(int(term["coefficient"])) == 1
            for certificate in certificates
            for term in certificate["equality_terms"]
        ),
        "all_identity_balances_zero": all(
            certificate["identity_verified_zero"] for certificate in certificates
        ),
        "all_active_pair_quotients_preserve_zero_balance": all(
            certificate["active_pair_quotient_check"]["all_quotient_balances_zero"]
            for certificate in certificates
        ),
        "quotient_stability_lemma": {
            "statement": (
                "If a finite strict/equality system has an identity sum_i "
                "a_i L_i + sum_j b_j E_j = 0 with every a_i > 0, every "
                "L_i > 0, and every E_j = 0, then the system is infeasible. "
                "Adding equalities or inequalities, or identifying additional "
                "ordinary distance variables while retaining the strict "
                "constraints, preserves the same certificate."
            ),
            "proof": (
                "The equality contribution vanishes and the strict contribution "
                "is positive, contradicting the zero identity. Applying any "
                "variable-identification map to the identity keeps its balance "
                "zero; a collapsed strict edge is already 0 > 0."
            ),
            "admissible_scope": (
                "coarsenings of ordinary pair-distance variables only; vertices, "
                "cyclic-order hypotheses, and strict-edge validity are not quotiented"
            ),
        },
        "certificates": certificates,
        "assignment_coverage": assignment_coverage,
        "interpretation": [
            "The 16 family certificates use one unit coefficient on every displayed strict edge and signed unit selected-row equality transfers.",
            "The exact coefficient balance is zero in ordinary pair-distance coordinates, so each record is a positive-circuit contradiction rather than only a quotient-graph picture.",
            "Every transformed certificate is checked against the compact core of each of the 184 source frontier assignments.",
            "All set partitions of the active pair variables are enumerated as a defensive check of quotient stability; the general algebraic lemma supplies the proof.",
            "The packet does not prove that arbitrary or minimal counterexamples contain one of the 16 source skeletons.",
            "No proof of n=9 or Erdos Problem #97 is claimed.",
        ],
        "source_artifacts": [
            {
                "path": "data/certificates/relation_skeleton_catalog.json",
                "schema": relation_skeleton_payload.get("schema"),
                "role": "16 canonical relation skeletons and local equality/strict paths",
            },
            {
                "path": "data/certificates/n9_vertex_circle_frontier_motif_classification.json",
                "schema": frontier_classification_payload.get("schema"),
                "role": "184 assignment-to-family maps and compact transformed cores",
            },
        ],
        "provenance": PROVENANCE,
    }
    assert_expected_template_dual_counts(payload)
    return payload


def assert_expected_template_dual_counts(payload: Mapping[str, Any]) -> None:
    """Assert stable headline and exact-certificate invariants."""

    expected_scalars = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": EXPECTED_N,
        "skeleton_count": EXPECTED_SKELETON_COUNT,
        "template_count": EXPECTED_TEMPLATE_COUNT,
        "family_count": EXPECTED_FAMILY_COUNT,
        "covered_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "contradiction_type_counts": EXPECTED_CONTRADICTION_TYPE_COUNTS,
        "strict_term_count_counts": EXPECTED_STRICT_TERM_COUNT_COUNTS,
        "equality_term_count_counts": EXPECTED_EQUALITY_TERM_COUNT_COUNTS,
        "active_pair_count_counts": EXPECTED_ACTIVE_PAIR_COUNT_COUNTS,
        "maximum_equality_term_count": EXPECTED_MAXIMUM_EQUALITY_TERM_COUNT,
        "maximum_active_pair_count": EXPECTED_MAXIMUM_ACTIVE_PAIR_COUNT,
        "total_active_pair_quotient_partitions_checked": EXPECTED_TOTAL_QUOTIENT_PARTITIONS,
        "all_strict_coefficients_positive_unit": True,
        "all_equality_multipliers_signed_unit": True,
        "all_identity_balances_zero": True,
        "all_active_pair_quotients_preserve_zero_balance": True,
    }
    for key, expected in expected_scalars.items():
        if payload.get(key) != expected:
            raise AssertionError(
                f"unexpected {key}: expected {expected!r}, got {payload.get(key)!r}"
            )
    coverage = payload.get("assignment_coverage")
    if not isinstance(coverage, Mapping):
        raise AssertionError("assignment_coverage must be an object")
    for key, expected in {
        "assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "unique_assignment_count": EXPECTED_ASSIGNMENT_COUNT,
        "family_count": EXPECTED_FAMILY_COUNT,
        "template_count": EXPECTED_TEMPLATE_COUNT,
        "all_transformed_identities_verified_zero": True,
        "all_transformed_terms_supported_by_assignment_cores": True,
        "all_label_maps_verified_dihedral": True,
        "transformed_certificate_sha256": EXPECTED_TRANSFORMED_CERTIFICATE_SHA256,
    }.items():
        if coverage.get(key) != expected:
            raise AssertionError(
                f"unexpected assignment_coverage.{key}: "
                f"expected {expected!r}, got {coverage.get(key)!r}"
            )
