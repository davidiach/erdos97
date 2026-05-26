"""Review-pending n=9 turn-inequality frontier replay.

This module checks a candidate finite-case obstruction for the 184 complete
selected-witness assignments that survive the n=9 pair/crossing/count filters.
It does not prove Erdos Problem #97 and does not promote the n=9 source-of-truth
status. The geometric turn lemma behind these inequalities still needs
independent review.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
import json
from typing import Sequence

from erdos97.generic_vertex_search import GenericVertexSearch
from erdos97.incidence_filters import normalize_chord
from erdos97.n9_incidence_frontier import classify_pattern

N = 9
ROW_SIZE = 4
PAIR_CAP = 2
EXPECTED_FRONTIER_ASSIGNMENTS = 184
EXPECTED_TURN_UNSAT = 184
EXPECTED_TURN_INEQUALITY_COUNT = 108
EXPECTED_SIDE_CAP_PATTERN_INDEX = 4
EXPECTED_FRONTIER_SHA256 = (
    "d7807b69b9de27da17fa851b3325b1e26cfa0b6d86277abeda4bc4e3454b8e01"
)
EXPECTED_FARKAS_CERTIFICATE_SHA256 = (
    "1aed1b1f78178b967f93a3894e67cf9a0c314441a94423c8f24f2e0b8cb9bf89"
)
EXPECTED_FARKAS_LAMBDA_HISTOGRAM = {"1": 180, "2": 4}
EXPECTED_FARKAS_TERM_COUNT_HISTOGRAM = {"5": 180, "9": 4}
EXPECTED_FARKAS_DEFICIT_HISTOGRAM = {"1": 184}
STATUS = "REVIEW_PENDING_TURN_INEQUALITY_FRONTIER_REPLAY"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Candidate n=9 selected-witness turn-inequality frontier replay; "
    "not a proof of Erdos Problem #97, not a counterexample, not an "
    "independent review, and not a source-of-truth status update."
)
CLAIM_SCOPE_REQUIRED_PHRASES = (
    "Candidate n=9 selected-witness turn-inequality frontier replay",
    "not a proof of Erdos Problem #97",
    "not a counterexample",
    "not an independent review",
    "not a source-of-truth status update",
)
REVIEW_REQUIREMENTS = [
    "Review the geometric turn lemma and indexing conventions.",
    "Review the regenerated n=9 source frontier and lack of hidden symmetry quotienting.",
    "Review the stored integer dual certificates and their arithmetic verifier.",
    "Keep this scoped as review-pending n=9 finite-case evidence only.",
]
PROVENANCE = {
    "generator": "scripts/check_n9_turn_inequality_frontier.py",
    "command": (
        "python scripts/check_n9_turn_inequality_frontier.py "
        "--assert-expected --write"
    ),
}

SIDE_CAP_BENCHMARK_PATTERN: list[list[int]] = [
    [1, 2, 4, 6],
    [0, 2, 3, 5],
    [1, 3, 4, 8],
    [0, 2, 4, 7],
    [2, 5, 6, 8],
    [1, 3, 6, 7],
    [4, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 5, 7],
]


def _mask_from_row(row: Sequence[int]) -> int:
    mask = 0
    for value in row:
        mask |= 1 << int(value)
    return mask


def normalize_pattern(rows: Sequence[Sequence[int]]) -> list[list[int]]:
    """Return a selected-row pattern as sorted JSON-friendly rows."""
    return [sorted(int(value) for value in row) for row in rows]


def _pattern_key(rows: Sequence[Sequence[int]]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple(row) for row in normalize_pattern(rows))


def enumerate_pair_crossing_count_frontier() -> list[list[list[int]]]:
    """Regenerate the 184 n=9 assignments before vertex-circle pruning."""
    searcher = GenericVertexSearch(N, row_size=ROW_SIZE, pair_cap=PAIR_CAP)
    frontier: list[list[list[int]]] = []

    def collect(
        assign: dict[int, int],
        column_counts: list[int],
        witness_pair_counts: list[int],
    ) -> None:
        if len(assign) == searcher.n:
            frontier.append(
                [list(searcher.mask_bits[assign[center]]) for center in range(searcher.n)]
            )
            return

        best_center = None
        best_options = None
        for center in range(searcher.n):
            if center in assign:
                continue
            opts = searcher.valid_options_for_center(
                center,
                assign,
                column_counts,
                witness_pair_counts,
            )
            if best_options is None or len(opts) < len(best_options):
                best_center = center
                best_options = opts
                if not opts:
                    break
        if not best_options:
            return

        center = best_center
        assert center is not None
        for mask in best_options:
            assign[center] = mask
            for target in searcher.mask_bits[mask]:
                column_counts[target] += 1
            for pair_index in searcher.row_pair_indices[mask]:
                witness_pair_counts[pair_index] += 1

            collect(assign, column_counts, witness_pair_counts)

            for pair_index in searcher.row_pair_indices[mask]:
                witness_pair_counts[pair_index] -= 1
            for target in searcher.mask_bits[mask]:
                column_counts[target] -= 1
            del assign[center]

    for row0 in searcher.options[0]:
        assign = {0: row0}
        column_counts = [0] * searcher.n
        witness_pair_counts = [0] * len(searcher.pairs)
        for target in searcher.mask_bits[row0]:
            column_counts[target] += 1
        for pair_index in searcher.row_pair_indices[row0]:
            witness_pair_counts[pair_index] += 1
        collect(assign, column_counts, witness_pair_counts)

    return frontier


def frontier_sha256(frontier: Sequence[Sequence[Sequence[int]]]) -> str:
    """Return a stable SHA-256 hash for a frontier row list."""
    blob = json.dumps(normalize_pattern_list(frontier), separators=(",", ":"), sort_keys=True)
    return sha256(blob.encode("utf-8")).hexdigest()


def normalize_pattern_list(
    frontier: Sequence[Sequence[Sequence[int]]],
) -> list[list[list[int]]]:
    """Return a stable JSON-friendly copy of a frontier pattern list."""
    return [normalize_pattern(rows) for rows in frontier]


def indegrees(rows: Sequence[Sequence[int]], n: int = N) -> list[int]:
    """Return selected indegrees for a row system."""
    return [sum(1 for row in rows if target in row) for target in range(n)]


def _in_open_arc(a: int, b: int, x: int, n: int = N) -> bool:
    return ((x - a) % n) < ((b - a) % n) and x not in (a, b)


def side_sensitive_pair_cap_violations(
    rows: Sequence[Sequence[int]],
    n: int = N,
) -> list[dict[str, object]]:
    """Return side-sensitive pair-cap violations for a cyclic row system."""
    pair_to_centers: dict[tuple[int, int], list[int]] = defaultdict(list)
    for center, row in enumerate(rows):
        for a, b in combinations(sorted(row), 2):
            pair_to_centers[normalize_chord(a, b)].append(center)

    violations: list[dict[str, object]] = []
    for (a, b), centers in sorted(pair_to_centers.items()):
        arc_ab = [center for center in centers if _in_open_arc(a, b, center, n=n)]
        arc_ba = [center for center in centers if _in_open_arc(b, a, center, n=n)]
        if len(arc_ab) > 1 or len(arc_ba) > 1:
            violations.append(
                {
                    "witness_pair": [a, b],
                    "source_centers": centers,
                    "arc_ab_centers": arc_ab,
                    "arc_ba_centers": arc_ba,
                }
            )
    return violations


def turn_inequality_terms_for_pattern(
    rows: Sequence[Sequence[int]],
    n: int = N,
) -> list[dict[str, object]]:
    """Return normalized weak turn inequalities for one row system.

    For each selected offset pair ``a < b`` in a row centered at ``i``, the
    candidate turn lemma gives:

    ``sum_{h=1}^{b-1} t_{i+h} >= 1``
    ``sum_{h=a+1}^{n-1} t_{i+h} >= 1``.
    """
    terms: list[dict[str, object]] = []
    for center, row in enumerate(rows):
        offsets = sorted((target - center) % n for target in row)
        if len(offsets) != ROW_SIZE or any(offset <= 0 for offset in offsets):
            raise ValueError(f"invalid row {center}: {row}")
        for left_index, right_index in combinations(range(ROW_SIZE), 2):
            a = offsets[left_index]
            b = offsets[right_index]
            forward = sorted((center + h) % n for h in range(1, b))
            reverse = sorted((center + h) % n for h in range(a + 1, n))
            terms.append(
                {
                    "center": center,
                    "selected_offsets": [a, b],
                    "support": forward,
                    "bound": 1,
                    "orientation": "forward",
                }
            )
            terms.append(
                {
                    "center": center,
                    "selected_offsets": [a, b],
                    "support": reverse,
                    "bound": 1,
                    "orientation": "reverse",
                }
            )
    return terms


def turn_z3_status(rows: Sequence[Sequence[int]], n: int = N) -> str:
    """Check weak turn-inequality feasibility with exact Z3 rationals."""
    import z3

    variables = [z3.Real(f"t_{idx}") for idx in range(n)]
    solver = z3.Solver()
    solver.add(z3.Sum(variables) == 4)
    for variable in variables:
        solver.add(variable >= 0)
    for term in turn_inequality_terms_for_pattern(rows, n=n):
        support = [int(value) for value in term["support"]]
        solver.add(z3.Sum([variables[index] for index in support]) >= int(term["bound"]))
    return str(solver.check())


def _support_mask(term: dict[str, object]) -> int:
    mask = 0
    for value in term["support"]:
        mask |= 1 << int(value)
    return mask


def _certificate_summary_from_indices(
    term_indices: Sequence[int],
    masks: Sequence[int],
    lambda_bound: int,
    n: int = N,
) -> dict[str, object]:
    coefficients = [0] * n
    for term_index in term_indices:
        mask = masks[term_index]
        for variable_index in range(n):
            if (mask >> variable_index) & 1:
                coefficients[variable_index] += 1
    rhs_sum = len(term_indices)
    return {
        "lambda": lambda_bound,
        "term_count": rhs_sum,
        "rhs_sum": rhs_sum,
        "max_variable_coefficient": max(coefficients, default=0),
        "deficit": rhs_sum - 4 * lambda_bound,
        "variable_coefficients": coefficients,
    }


def find_turn_farkas_certificate(
    rows: Sequence[Sequence[int]],
    assignment_index_1based: int | None = None,
    n: int = N,
) -> dict[str, object]:
    """Find a compact integer dual certificate for one turn LP.

    A certificate consists of unit weights on selected interval inequalities and
    an integer ``lambda`` such that each turn variable is used at most
    ``lambda`` times, while the number of selected inequalities is greater than
    ``4*lambda``. Summing those inequalities gives a lower bound larger than
    the upper bound forced by ``sum_i t_i = 4`` and ``t_i >= 0``.
    """
    terms = turn_inequality_terms_for_pattern(rows, n=n)
    masks = [_support_mask(term) for term in terms]
    items = [
        (term_index, mask, mask.bit_count())
        for term_index, mask in enumerate(masks)
        if mask
    ]
    items.sort(key=lambda item: (item[2], item[0]))

    for lambda_bound in (1, 2):
        target_count = 4 * lambda_bound + 1
        chosen: list[int] = []
        coefficients = [0] * n

        def search(start: int) -> bool:
            if len(chosen) == target_count:
                return True
            if len(chosen) + (len(items) - start) < target_count:
                return False
            for item_pos in range(start, len(items)):
                term_index, mask, _support_size = items[item_pos]
                changed: list[int] = []
                for variable_index in range(n):
                    if (mask >> variable_index) & 1:
                        if coefficients[variable_index] >= lambda_bound:
                            break
                        changed.append(variable_index)
                else:
                    for variable_index in changed:
                        coefficients[variable_index] += 1
                    chosen.append(term_index)
                    if search(item_pos + 1):
                        return True
                    chosen.pop()
                    for variable_index in changed:
                        coefficients[variable_index] -= 1
            return False

        if search(0):
            term_indices = sorted(chosen)
            summary = _certificate_summary_from_indices(
                term_indices,
                masks,
                lambda_bound,
                n=n,
            )
            certificate: dict[str, object] = {
                "lambda": lambda_bound,
                "term_weight": 1,
                "term_indices": term_indices,
                **summary,
            }
            if assignment_index_1based is not None:
                certificate["assignment_index_1based"] = assignment_index_1based
            return certificate

    raise ValueError("no bounded unit-weight turn Farkas certificate found")


def verify_turn_farkas_certificate(
    rows: Sequence[Sequence[int]],
    certificate: dict[str, object],
    n: int = N,
) -> dict[str, object]:
    """Verify one stored turn dual certificate by integer arithmetic only."""
    terms = turn_inequality_terms_for_pattern(rows, n=n)
    masks = [_support_mask(term) for term in terms]
    lambda_bound = certificate.get("lambda")
    term_weight = certificate.get("term_weight", 1)
    term_indices = certificate.get("term_indices")
    if not isinstance(lambda_bound, int) or lambda_bound <= 0:
        raise ValueError(f"invalid lambda: {lambda_bound!r}")
    if term_weight != 1:
        raise ValueError(f"unsupported term weight: {term_weight!r}")
    if not isinstance(term_indices, list) or not term_indices:
        raise ValueError("term_indices must be a nonempty list")
    if len(set(term_indices)) != len(term_indices):
        raise ValueError(f"duplicate term index in certificate: {term_indices!r}")
    if any(
        not isinstance(term_index, int)
        or term_index < 0
        or term_index >= len(terms)
        for term_index in term_indices
    ):
        raise ValueError(f"term index out of range: {term_indices!r}")

    summary = _certificate_summary_from_indices(term_indices, masks, lambda_bound, n=n)
    if summary["rhs_sum"] <= 4 * lambda_bound:
        raise ValueError("certificate has no positive Farkas deficit")
    if summary["max_variable_coefficient"] > lambda_bound:
        raise ValueError("certificate exceeds its variable coefficient bound")
    for key in (
        "term_count",
        "rhs_sum",
        "max_variable_coefficient",
        "deficit",
        "variable_coefficients",
    ):
        if key in certificate and certificate[key] != summary[key]:
            raise ValueError(
                f"stored certificate field {key}={certificate[key]!r} "
                f"does not match recomputed {summary[key]!r}"
            )
    return summary


def farkas_certificate_sha256(certificates: Sequence[dict[str, object]]) -> str:
    """Return a stable SHA-256 hash for stored Farkas certificates."""
    blob = json.dumps(certificates, separators=(",", ":"), sort_keys=True)
    return sha256(blob.encode("utf-8")).hexdigest()


def validate_farkas_certificates(
    payload: dict[str, object],
    frontier: Sequence[Sequence[Sequence[int]]] | None = None,
) -> list[str]:
    """Validate stored Farkas certificates against the regenerated frontier."""
    if frontier is None:
        frontier = normalize_pattern_list(enumerate_pair_crossing_count_frontier())
    certificates = payload.get("farkas_certificates")
    if not isinstance(certificates, list):
        return ["missing farkas_certificates list"]
    if len(certificates) != len(frontier):
        return [
            "certificate count mismatch: "
            f"{len(certificates)} stored vs {len(frontier)} frontier assignments"
        ]

    errors: list[str] = []
    for index, (rows, certificate) in enumerate(zip(frontier, certificates), start=1):
        if not isinstance(certificate, dict):
            errors.append(f"certificate {index} is not an object")
            continue
        if certificate.get("assignment_index_1based") != index:
            errors.append(
                f"certificate {index} has assignment index "
                f"{certificate.get('assignment_index_1based')!r}"
            )
            continue
        try:
            verify_turn_farkas_certificate(rows, certificate)
        except ValueError as exc:
            errors.append(f"certificate {index}: {exc}")
    return errors


def vertex_circle_status_for_pattern(rows: Sequence[Sequence[int]]) -> str:
    """Replay GenericVertexSearch's vertex-circle status for a complete pattern."""
    searcher = GenericVertexSearch(N, row_size=ROW_SIZE, pair_cap=PAIR_CAP)
    assign = {center: _mask_from_row(row) for center, row in enumerate(rows)}
    return searcher.vertex_circle_status(assign)


def _histogram(values: Sequence[object]) -> dict[str, int]:
    return {str(key): int(value) for key, value in sorted(Counter(values).items())}


def _find_pattern_index(
    frontier: Sequence[Sequence[Sequence[int]]],
    pattern: Sequence[Sequence[int]],
) -> int | None:
    target = _pattern_key(pattern)
    for index, rows in enumerate(frontier, start=1):
        if _pattern_key(rows) == target:
            return index
    return None


def side_cap_benchmark_summary(frontier: Sequence[Sequence[Sequence[int]]]) -> dict[str, object]:
    """Return replay data for the side-cap benchmark from GPT Pro output 10."""
    rows = normalize_pattern(SIDE_CAP_BENCHMARK_PATTERN)
    classification = classify_pattern(rows, order=list(range(N)), max_details=3)
    turn_status = turn_z3_status(rows)
    return {
        "name": "gpt_pro_output_10_side_cap_pattern",
        "rows": rows,
        "frontier_assignment_index_1based": _find_pattern_index(frontier, rows),
        "indegrees": indegrees(rows),
        "side_sensitive_pair_cap_violation_count": len(side_sensitive_pair_cap_violations(rows)),
        "natural_order_classify_status": classification["status"],
        "natural_order_phi_edges": classification["phi_edges"],
        "natural_order_row_ptolemy_product_cancellation_count": classification[
            "row_ptolemy_product_cancellation_count"
        ],
        "natural_order_rectangle_trap_4_cycles": classification["rectangle_trap_4_cycles"],
        "vertex_circle_status": vertex_circle_status_for_pattern(rows),
        "turn_z3_status": turn_status,
        "turn_inequality_count": len(turn_inequality_terms_for_pattern(rows)),
    }


def summary_payload() -> dict[str, object]:
    """Return the stable JSON payload for the turn-inequality frontier replay."""
    frontier = enumerate_pair_crossing_count_frontier()
    normalized_frontier = normalize_pattern_list(frontier)
    farkas_certificates = [
        find_turn_farkas_certificate(rows, assignment_index_1based=index)
        for index, rows in enumerate(normalized_frontier, start=1)
    ]
    farkas_summaries = [
        verify_turn_farkas_certificate(rows, certificate)
        for rows, certificate in zip(normalized_frontier, farkas_certificates)
    ]
    z3_statuses = [turn_z3_status(rows) for rows in normalized_frontier]
    indegree_rows = [tuple(indegrees(rows)) for rows in normalized_frontier]
    turn_counts = [
        len(turn_inequality_terms_for_pattern(rows)) for rows in normalized_frontier
    ]
    side_cap_violations = [
        len(side_sensitive_pair_cap_violations(rows)) for rows in normalized_frontier
    ]

    return {
        "schema": "erdos97.n9_turn_inequality_frontier.v1",
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(range(N)),
        "source_frontier": {
            "description": (
                "Complete selected-witness assignments surviving pair/crossing/count "
                "filters before vertex-circle pruning."
            ),
            "generator": "GenericVertexSearch(n=9).valid_options_for_center",
            "assignment_count": len(normalized_frontier),
            "assignment_sha256": frontier_sha256(normalized_frontier),
            "indegree_distribution": _histogram(indegree_rows),
            "side_sensitive_pair_cap_violation_count_histogram": _histogram(
                side_cap_violations
            ),
        },
        "turn_system": {
            "normalized_variables": "t_i = 2*tau_i/pi",
            "sum_constraint": "sum_i t_i = 4",
            "nonnegativity": "t_i >= 0",
            "weak_inequality_template": [
                "sum_{h=1}^{b-1} t_{i+h} >= 1",
                "sum_{h=a+1}^{8} t_{i+h} >= 1",
            ],
            "strict_geometry_note": (
                "The geometric lemma gives strict inequalities; this replay uses "
                "weak rational inequalities, so UNSAT is stronger than needed."
            ),
            "inequality_count_histogram": _histogram(turn_counts),
        },
        "z3_replay": {
            "solver": "z3",
            "arithmetic": "exact rational linear real arithmetic",
            "role": "cross-check; stored Farkas certificates are verified by integer arithmetic",
            "status_counts": _histogram(z3_statuses),
            "sat_count": z3_statuses.count("sat"),
            "unsat_count": z3_statuses.count("unsat"),
            "unknown_count": z3_statuses.count("unknown"),
        },
        "farkas_replay": {
            "certificate_type": "unit_weight_interval_dual",
            "certificate_count": len(farkas_certificates),
            "certificate_sha256": farkas_certificate_sha256(farkas_certificates),
            "arithmetic": "integer coefficient check; no solver needed for replay",
            "lambda_histogram": _histogram(
                [summary["lambda"] for summary in farkas_summaries]
            ),
            "term_count_histogram": _histogram(
                [summary["term_count"] for summary in farkas_summaries]
            ),
            "deficit_histogram": _histogram(
                [summary["deficit"] for summary in farkas_summaries]
            ),
            "max_variable_coefficient_histogram": _histogram(
                [
                    summary["max_variable_coefficient"]
                    for summary in farkas_summaries
                ]
            ),
            "certificate_explanation": (
                "For each assignment, summing the listed interval inequalities "
                "gives RHS > 4*lambda while every turn variable has coefficient "
                "at most lambda. Since t_i >= 0 and sum_i t_i = 4, the same "
                "left-hand side is at most 4*lambda, a contradiction."
            ),
        },
        "farkas_certificates": farkas_certificates,
        "benchmarks": [side_cap_benchmark_summary(normalized_frontier)],
        "conclusion": (
            "All 184 regenerated n=9 pair/crossing/count frontier assignments "
            "have stored integer dual certificates proving infeasibility of "
            "the candidate weak turn inequalities."
        ),
        "review_requirements": list(REVIEW_REQUIREMENTS),
        "provenance": dict(PROVENANCE),
    }


def _compare_expected_fields(
    errors: list[str],
    section_name: str,
    section: dict[str, object],
    expected_fields: dict[str, object],
) -> None:
    for key, expected in expected_fields.items():
        if section.get(key) != expected:
            errors.append(
                f"{section_name}.{key} mismatch: "
                f"{section.get(key)!r} != {expected!r}"
            )


def validate_payload(payload: dict[str, object]) -> list[str]:
    """Validate a stored n=9 turn-inequality frontier payload."""
    errors: list[str] = []
    if payload.get("schema") != "erdos97.n9_turn_inequality_frontier.v1":
        errors.append("unexpected schema")
    if payload.get("status") != STATUS:
        errors.append(f"unexpected status: {payload.get('status')!r}")
    if payload.get("trust") != TRUST:
        errors.append(f"unexpected trust: {payload.get('trust')!r}")
    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("missing claim_scope string")
    else:
        missing_phrases = [
            phrase
            for phrase in CLAIM_SCOPE_REQUIRED_PHRASES
            if phrase not in claim_scope
        ]
        if missing_phrases:
            errors.append(f"claim_scope missing guard phrases: {missing_phrases!r}")
    if payload.get("review_requirements") != REVIEW_REQUIREMENTS:
        errors.append("review_requirements mismatch")
    if payload.get("provenance") != PROVENANCE:
        errors.append("provenance mismatch")
    if payload.get("n") != N:
        errors.append(f"unexpected n: {payload.get('n')!r}")
    if payload.get("row_size") != ROW_SIZE:
        errors.append(f"unexpected row_size: {payload.get('row_size')!r}")

    source = payload.get("source_frontier")
    turn_system = payload.get("turn_system")
    z3_replay = payload.get("z3_replay")
    farkas_replay = payload.get("farkas_replay")
    farkas_certificates = payload.get("farkas_certificates")
    benchmarks = payload.get("benchmarks")
    if not isinstance(source, dict):
        errors.append("missing source_frontier object")
    if not isinstance(turn_system, dict):
        errors.append("missing turn_system object")
    if not isinstance(z3_replay, dict):
        errors.append("missing z3_replay object")
    if not isinstance(farkas_replay, dict):
        errors.append("missing farkas_replay object")
    if not isinstance(farkas_certificates, list):
        errors.append("missing farkas_certificates list")
    if not isinstance(benchmarks, list):
        errors.append("missing benchmarks list")
    if errors:
        return errors

    assert isinstance(source, dict)
    assert isinstance(turn_system, dict)
    assert isinstance(z3_replay, dict)
    assert isinstance(farkas_replay, dict)
    assert isinstance(farkas_certificates, list)
    assert isinstance(benchmarks, list)

    frontier = normalize_pattern_list(enumerate_pair_crossing_count_frontier())
    indegree_rows = [tuple(indegrees(rows)) for rows in frontier]
    side_cap_violations = [
        len(side_sensitive_pair_cap_violations(rows)) for rows in frontier
    ]
    turn_counts = [len(turn_inequality_terms_for_pattern(rows)) for rows in frontier]

    _compare_expected_fields(
        errors,
        "source_frontier",
        source,
        {
            "assignment_count": len(frontier),
            "assignment_sha256": frontier_sha256(frontier),
            "indegree_distribution": _histogram(indegree_rows),
            "side_sensitive_pair_cap_violation_count_histogram": _histogram(
                side_cap_violations
            ),
        },
    )
    _compare_expected_fields(
        errors,
        "turn_system",
        turn_system,
        {"inequality_count_histogram": _histogram(turn_counts)},
    )

    certificate_errors: list[str] = []
    certificate_summaries: list[dict[str, object]] = []
    if len(farkas_certificates) != len(frontier):
        certificate_errors.append(
            "certificate count mismatch: "
            f"{len(farkas_certificates)} stored vs {len(frontier)} frontier assignments"
        )
    for index, (rows, certificate) in enumerate(
        zip(frontier, farkas_certificates), start=1
    ):
        if not isinstance(certificate, dict):
            certificate_errors.append(f"certificate {index} is not an object")
            continue
        if certificate.get("assignment_index_1based") != index:
            certificate_errors.append(
                f"certificate {index} has assignment index "
                f"{certificate.get('assignment_index_1based')!r}"
            )
            continue
        try:
            certificate_summaries.append(
                verify_turn_farkas_certificate(rows, certificate)
            )
        except ValueError as exc:
            certificate_errors.append(f"certificate {index}: {exc}")
    errors.extend(certificate_errors)

    _compare_expected_fields(
        errors,
        "z3_replay",
        z3_replay,
        {
            "status_counts": {"unsat": len(frontier)},
            "sat_count": 0,
            "unsat_count": len(frontier),
            "unknown_count": 0,
        },
    )
    _compare_expected_fields(
        errors,
        "farkas_replay",
        farkas_replay,
        {
            "certificate_count": len(farkas_certificates),
            "certificate_sha256": farkas_certificate_sha256(farkas_certificates),
            "lambda_histogram": _histogram(
                [summary["lambda"] for summary in certificate_summaries]
            ),
            "term_count_histogram": _histogram(
                [summary["term_count"] for summary in certificate_summaries]
            ),
            "deficit_histogram": _histogram(
                [summary["deficit"] for summary in certificate_summaries]
            ),
            "max_variable_coefficient_histogram": _histogram(
                [
                    summary["max_variable_coefficient"]
                    for summary in certificate_summaries
                ]
            ),
        },
    )

    expected_benchmark = side_cap_benchmark_summary(frontier)
    if benchmarks != [expected_benchmark]:
        errors.append("benchmarks mismatch")
    return errors


def assert_expected_payload(payload: dict[str, object] | None = None) -> None:
    """Assert stable counts and benchmark fields for the replay artifact."""
    if payload is None:
        payload = summary_payload()
    validation_errors = validate_payload(payload)
    if validation_errors:
        raise AssertionError(validation_errors[:5])
    if payload.get("schema") != "erdos97.n9_turn_inequality_frontier.v1":
        raise AssertionError("unexpected schema")
    source = payload.get("source_frontier")
    turn_system = payload.get("turn_system")
    z3_replay = payload.get("z3_replay")
    farkas_replay = payload.get("farkas_replay")
    farkas_certificates = payload.get("farkas_certificates")
    benchmarks = payload.get("benchmarks")
    if not isinstance(source, dict) or not isinstance(turn_system, dict):
        raise AssertionError("malformed source or turn-system summary")
    if (
        not isinstance(z3_replay, dict)
        or not isinstance(farkas_replay, dict)
        or not isinstance(farkas_certificates, list)
        or not isinstance(benchmarks, list)
    ):
        raise AssertionError("malformed z3, Farkas, or benchmark summary")
    if source.get("assignment_count") != EXPECTED_FRONTIER_ASSIGNMENTS:
        raise AssertionError(f"unexpected frontier count: {source.get('assignment_count')}")
    if source.get("assignment_sha256") != EXPECTED_FRONTIER_SHA256:
        raise AssertionError(f"unexpected frontier hash: {source.get('assignment_sha256')}")
    if source.get("indegree_distribution") != {
        "(4, 4, 4, 4, 4, 4, 4, 4, 4)": EXPECTED_FRONTIER_ASSIGNMENTS
    }:
        raise AssertionError(f"unexpected indegree distribution: {source.get('indegree_distribution')}")
    if source.get("side_sensitive_pair_cap_violation_count_histogram") != {
        "0": EXPECTED_FRONTIER_ASSIGNMENTS
    }:
        raise AssertionError("unexpected side-sensitive pair-cap histogram")
    if turn_system.get("inequality_count_histogram") != {
        str(EXPECTED_TURN_INEQUALITY_COUNT): EXPECTED_FRONTIER_ASSIGNMENTS
    }:
        raise AssertionError("unexpected turn inequality count histogram")
    if z3_replay.get("unsat_count") != EXPECTED_TURN_UNSAT:
        raise AssertionError(f"unexpected unsat count: {z3_replay.get('unsat_count')}")
    if z3_replay.get("sat_count") != 0 or z3_replay.get("unknown_count") != 0:
        raise AssertionError(f"unexpected z3 status counts: {z3_replay}")
    if farkas_replay.get("certificate_count") != EXPECTED_FRONTIER_ASSIGNMENTS:
        raise AssertionError("unexpected Farkas certificate count")
    if (
        farkas_replay.get("certificate_sha256")
        != EXPECTED_FARKAS_CERTIFICATE_SHA256
    ):
        raise AssertionError(
            "unexpected Farkas certificate hash: "
            f"{farkas_replay.get('certificate_sha256')}"
        )
    if farkas_replay.get("lambda_histogram") != EXPECTED_FARKAS_LAMBDA_HISTOGRAM:
        raise AssertionError("unexpected Farkas lambda histogram")
    if (
        farkas_replay.get("term_count_histogram")
        != EXPECTED_FARKAS_TERM_COUNT_HISTOGRAM
    ):
        raise AssertionError("unexpected Farkas term-count histogram")
    if farkas_replay.get("deficit_histogram") != EXPECTED_FARKAS_DEFICIT_HISTOGRAM:
        raise AssertionError("unexpected Farkas deficit histogram")
    if (
        farkas_certificate_sha256(farkas_certificates)
        != EXPECTED_FARKAS_CERTIFICATE_SHA256
    ):
        raise AssertionError("stored Farkas certificates do not match expected hash")
    benchmark = benchmarks[0]
    if not isinstance(benchmark, dict):
        raise AssertionError("malformed benchmark")
    expected_benchmark = {
        "frontier_assignment_index_1based": EXPECTED_SIDE_CAP_PATTERN_INDEX,
        "natural_order_classify_status": "accepted_frontier",
        "vertex_circle_status": "self_edge",
        "turn_z3_status": "unsat",
        "side_sensitive_pair_cap_violation_count": 0,
        "natural_order_row_ptolemy_product_cancellation_count": 0,
        "natural_order_rectangle_trap_4_cycles": 0,
    }
    for key, expected in expected_benchmark.items():
        if benchmark.get(key) != expected:
            raise AssertionError(
                f"unexpected benchmark {key}: {benchmark.get(key)!r}, expected {expected!r}"
            )
