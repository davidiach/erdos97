"""Review-pending n=9 fragile/turn/inversion-pivot crosswalk.

This module joins three already review-pending finite layers:

* exact-four selected-witness rows on the 184 n=9 frontier assignments;
* weak turn-inequality Farkas certificates;
* exact vertex-circle quotient replays.

It adds two bounded diagnostics.  First, every one of the 184 4-regular
frontier row systems has a Hamiltonian perfect row-to-witness matching that
can be made compatible with a compact pivot-to-halo turn certificate.  Second,
the rows used by the stored turn certificates require two inversion pivots in
182 assignments and three in exactly the two orientations of motif family
F15.  Every two-pivot weak-turn restriction of those two exceptions remains
feasible, while their full selected rows have exact vertex-circle self-edges.

Nothing here proves the geometric turn lemma, the n=9 case, or a general
three-pivot reduction for minimal counterexamples.
"""

from __future__ import annotations

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from itertools import combinations
import json
from typing import Any, Sequence

from erdos97.n9_turn_inequality_frontier import (
    EXPECTED_FARKAS_CERTIFICATE_SHA256,
    EXPECTED_FRONTIER_ASSIGNMENTS,
    EXPECTED_FRONTIER_SHA256,
    frontier_sha256,
    normalize_pattern_list,
    turn_inequality_terms_for_pattern,
    verify_turn_farkas_certificate,
)
from erdos97.n9_vertex_circle_frontier_motif_classification import (
    compact_to_indexed_rows,
)
from erdos97.vertex_circle_quotient_replay import (
    parse_selected_rows,
    replay_vertex_circle_quotient,
)

N = 9
ROW_SIZE = 4
CYCLIC_ORDER = tuple(range(N))

SCHEMA = "erdos97.n9_fragile_turn_pivot_crosswalk.v1"
STATUS = "REVIEW_PENDING_N9_FRAGILE_TURN_PIVOT_CROSSWALK"
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
CLAIM_SCOPE = (
    "Finite n=9 crosswalk from exact-four selected-witness rows to a "
    "witness-perfect-matching layer, candidate weak-turn certificates, "
    "inversion row-pivot covers, and vertex-circle replay for the unique "
    "three-pivot dihedral exception; not a proof of n=9, not a proof of the "
    "geometric turn lemma, not a minimal-counterexample bridge beyond n=9, "
    "not a counterexample, and not a source-of-truth or official/global "
    "status update."
)
CONCLUSION = (
    "All 184 n=9 frontier assignments admit a Hamiltonian perfect "
    "row-to-witness matching compatible with a pivot-to-halo integer turn "
    "certificate. The stored turn certificates need two inversion row pivots "
    "for 182 assignments and three for the two orientations of family F15. "
    "Every F15 two-pivot weak-turn subsystem has an exact binary feasible "
    "witness, while both full F15 row systems replay exact vertex-circle "
    "self-edges."
)
REVIEW_REQUIREMENTS = [
    "Review the source-frontier alignment and exact-four incidence interpretation.",
    "Review the geometric turn lemma and all interval-indexing conventions.",
    "Review the perfect-matching, pivot-to-halo, and inversion row-pivot definitions.",
    "Review the exhaustive F15 two-pivot feasibility and vertex-circle replays.",
    "Do not generalize this finite n=9 diagnostic to arbitrary minimal counterexamples.",
]
PROVENANCE = {
    "generator": "scripts/check_n9_fragile_turn_pivot_crosswalk.py",
    "command": (
        "python scripts/check_n9_fragile_turn_pivot_crosswalk.py "
        "--assert-expected --write"
    ),
}

EXPECTED_TURN_SOURCE_FILE_SHA256 = (
    "c18927110eeb7eaaa8ce00c61573b0c72c4b81c0aed29f054b46cd9b8658ee55"
)
EXPECTED_MOTIF_SOURCE_FILE_SHA256 = (
    "382c4b5bbd70229c5484ff18b049d430d1ce4e6d11a1ca20dc21a99ebbfb21d3"
)
EXPECTED_TOTAL_PERFECT_MATCHINGS = 82_720
EXPECTED_PERFECT_MATCHING_COUNT_HISTOGRAM = {"448": 148, "456": 36}
EXPECTED_HAMILTONIAN_MATCHINGS = 27_704
EXPECTED_HAMILTONIAN_COUNT_HISTOGRAM = {
    "115": 18,
    "117": 36,
    "125": 18,
    "136": 6,
    "141": 2,
    "145": 18,
    "154": 4,
    "155": 6,
    "176": 20,
    "180": 18,
    "186": 18,
    "190": 18,
    "195": 2,
}
EXPECTED_MATCHING_CYCLE_TYPE_ASSIGNMENT_COUNTS = {
    "2+2+2+3": 178,
    "2+2+5": 184,
    "2+3+4": 182,
    "2+7": 184,
    "3+3+3": 184,
    "3+6": 184,
    "4+5": 184,
    "9": 184,
}
EXPECTED_MATCHING_CYCLE_TYPE_COUNTS = {
    "2+2+2+3": 1_290,
    "2+2+5": 4_680,
    "2+3+4": 7_686,
    "2+7": 14_778,
    "3+3+3": 1_694,
    "3+6": 13_080,
    "4+5": 11_808,
    "9": 27_704,
}
EXPECTED_PIVOT_HALO_LAMBDA_HISTOGRAM = {"1": 180, "2": 4}
EXPECTED_PIVOT_HALO_TERM_COUNT_HISTOGRAM = {"5": 180, "9": 4}
EXPECTED_PIVOT_HALO_LAMBDA_TWO_ASSIGNMENTS = ["A068", "A082", "A131", "A152"]
EXPECTED_PIVOT_HALO_CERTIFICATE_SHA256 = (
    "9262eb31f88675e7a01bfc199b12544f211230684baad782ae10c29663e57792"
)
EXPECTED_INVERSION_COVER_RECORD_SHA256 = (
    "460373745c10dfcc4d71d79c5263ef595782422208bd6f10bfcf07ef531c9e5f"
)
EXPECTED_EXCEPTION_RECORD_SHA256 = (
    "cf792f78c168e75c22b78b66c046df3b6a8a6e1de1b4246905251f0f1bf74cd8"
)
EXPECTED_INVERSION_COVER_SIZE_HISTOGRAM = {"2": 182, "3": 2}
EXPECTED_THREE_PIVOT_ASSIGNMENTS = ["A068", "A131"]
EXPECTED_EXCEPTION_FAMILY_ID = "F15"
EXPECTED_EXCEPTION_TEMPLATE_ID = "T03"
EXPECTED_EXCEPTION_PAIR_CASES = 72
EXPECTED_PAIR_HIT_CENTER_HISTOGRAM = {"6": 36, "7": 36}
EXPECTED_EXCEPTION_MINIMUM_TRIPLES = 24
EXPECTED_EXCEPTION_STRICT_EDGES = 162
EXPECTED_EXCEPTION_SELF_EDGES = 54


def _histogram(values: Sequence[Any]) -> dict[str, int]:
    return {str(key): int(count) for key, count in sorted(Counter(values).items())}


def _stable_sha256(value: Any) -> str:
    blob = json.dumps(value, separators=(",", ":"), sort_keys=True)
    return sha256(blob.encode("utf-8")).hexdigest()


def indegrees(rows: Sequence[Sequence[int]]) -> tuple[int, ...]:
    """Return the witness indegrees of a selected-row system."""

    return tuple(
        sum(1 for row in rows if witness in row) for witness in range(N)
    )


def enumerate_perfect_matchings(
    rows: Sequence[Sequence[int]],
) -> list[tuple[int, ...]]:
    """Enumerate row-to-witness perfect matchings in lexicographic order."""

    if len(rows) != N:
        raise ValueError(f"expected {N} rows, got {len(rows)}")
    choices = [tuple(sorted(int(value) for value in row)) for row in rows]
    if any(len(row) != ROW_SIZE for row in choices):
        raise ValueError("every selected row must have exactly four witnesses")

    matchings: list[tuple[int, ...]] = []
    chosen: list[int] = []

    def search(center: int, used_mask: int) -> None:
        if center == N:
            matchings.append(tuple(chosen))
            return
        for witness in choices[center]:
            bit = 1 << witness
            if used_mask & bit:
                continue
            chosen.append(witness)
            search(center + 1, used_mask | bit)
            chosen.pop()

    search(0, 0)
    return matchings


def permutation_cycle_type(permutation: Sequence[int]) -> tuple[int, ...]:
    """Return the sorted cycle lengths of a permutation."""

    if sorted(int(value) for value in permutation) != list(range(len(permutation))):
        raise ValueError("matching is not a permutation")
    seen: set[int] = set()
    lengths: list[int] = []
    for start in range(len(permutation)):
        if start in seen:
            continue
        cursor = start
        length = 0
        while cursor not in seen:
            seen.add(cursor)
            length += 1
            cursor = int(permutation[cursor])
        lengths.append(length)
    return tuple(sorted(lengths))


def _cycle_type_key(cycle_type: Sequence[int]) -> str:
    return "+".join(str(value) for value in cycle_type)


def _term_support_mask(term: dict[str, object]) -> int:
    mask = 0
    for raw_value in term["support"]:
        mask |= 1 << int(raw_value)
    return mask


def _term_selected_witnesses(term: dict[str, object]) -> tuple[int, int]:
    center = int(term["center"])
    offsets = term["selected_offsets"]
    if not isinstance(offsets, list) or len(offsets) != 2:
        raise ValueError("turn term must have two selected offsets")
    return tuple((center + int(offset)) % N for offset in offsets)


def _restricted_certificate_indices(
    rows: Sequence[Sequence[int]],
    matching: Sequence[int],
    lambda_bound: int,
) -> tuple[int, ...] | None:
    """Find one term per used row with the matched witness as an endpoint."""

    terms = turn_inequality_terms_for_pattern(rows)
    options: list[tuple[tuple[int, int], ...]] = []
    for center in range(N):
        center_options = []
        pivot = int(matching[center])
        for term_index, term in enumerate(terms):
            if int(term["center"]) != center:
                continue
            if pivot not in _term_selected_witnesses(term):
                continue
            mask = _term_support_mask(term)
            center_options.append((term_index, mask))
        center_options.sort(key=lambda item: (item[1].bit_count(), item[0]))
        if not center_options:
            return None
        options.append(tuple(center_options))

    target_count = 4 * lambda_bound + 1

    @lru_cache(maxsize=None)
    def search(
        center: int,
        chosen_count: int,
        coefficients: tuple[int, ...],
    ) -> tuple[int, ...] | None:
        if chosen_count == target_count:
            return ()
        if center == N or chosen_count + (N - center) < target_count:
            return None

        for term_index, mask in options[center]:
            updated = list(coefficients)
            for variable in range(N):
                if not ((mask >> variable) & 1):
                    continue
                if updated[variable] >= lambda_bound:
                    break
                updated[variable] += 1
            else:
                tail = search(center + 1, chosen_count + 1, tuple(updated))
                if tail is not None:
                    return (term_index, *tail)

        if chosen_count + (N - center - 1) >= target_count:
            return search(center + 1, chosen_count, coefficients)
        return None

    return search(0, 0, (0,) * N)


def pivot_halo_certificate(
    rows: Sequence[Sequence[int]],
    matching: Sequence[int],
) -> dict[str, object] | None:
    """Return a compact turn certificate restricted to pivot-to-halo pairs."""

    for lambda_bound in (1, 2):
        indices = _restricted_certificate_indices(rows, matching, lambda_bound)
        if indices is None:
            continue
        certificate: dict[str, object] = {
            "lambda": lambda_bound,
            "term_weight": 1,
            "term_indices": sorted(indices),
        }
        summary = verify_turn_farkas_certificate(rows, certificate)
        certificate.update(summary)
        return certificate
    return None


def verify_pivot_halo_certificate(
    rows: Sequence[Sequence[int]],
    matching: Sequence[int],
    certificate: dict[str, object],
) -> dict[str, object]:
    """Verify matching incidence, halo endpoints, and Farkas arithmetic."""

    if len(matching) != N or sorted(int(value) for value in matching) != list(
        range(N)
    ):
        raise ValueError("witness-pivot matching must be a permutation")
    if permutation_cycle_type(matching) != (N,):
        raise ValueError("stored witness-pivot matching is not a single 9-cycle")
    for center, raw_pivot in enumerate(matching):
        pivot = int(raw_pivot)
        if pivot not in rows[center]:
            raise ValueError(
                f"matching pivot {pivot} does not belong to row {center}"
            )

    summary = verify_turn_farkas_certificate(rows, certificate)
    raw_indices = certificate.get("term_indices")
    if not isinstance(raw_indices, list):
        raise ValueError("certificate term_indices must be a list")
    terms = turn_inequality_terms_for_pattern(rows)
    used_centers: set[int] = set()
    for term_index in raw_indices:
        term = terms[int(term_index)]
        center = int(term["center"])
        if center in used_centers:
            raise ValueError(
                f"pivot-to-halo certificate repeats center {center}"
            )
        used_centers.add(center)
        endpoints = _term_selected_witnesses(term)
        pivot = int(matching[center])
        if pivot not in endpoints:
            raise ValueError(
                f"turn term {term_index} does not contain matched pivot {pivot}"
            )
        halo_endpoint = endpoints[0] if endpoints[1] == pivot else endpoints[1]
        if halo_endpoint not in set(rows[center]) - {pivot}:
            raise ValueError(
                f"turn term {term_index} does not join pivot to its halo"
            )
    return summary


def find_hamiltonian_pivot_halo_certificate(
    rows: Sequence[Sequence[int]],
    matchings: Sequence[Sequence[int]],
) -> tuple[tuple[int, ...], dict[str, object], int]:
    """Prefer a lambda-one certificate over all Hamiltonian matchings."""

    hamiltonian = [
        tuple(int(value) for value in matching)
        for matching in matchings
        if permutation_cycle_type(matching) == (N,)
    ]
    examined = 0
    for lambda_bound in (1, 2):
        for matching in hamiltonian:
            examined += 1
            indices = _restricted_certificate_indices(
                rows,
                matching,
                lambda_bound,
            )
            if indices is None:
                continue
            certificate: dict[str, object] = {
                "lambda": lambda_bound,
                "term_weight": 1,
                "term_indices": sorted(indices),
            }
            certificate.update(
                verify_pivot_halo_certificate(
                    rows,
                    matching,
                    certificate,
                )
            )
            return matching, certificate, examined
    raise ValueError("no Hamiltonian pivot-to-halo turn certificate found")


def used_certificate_centers(
    rows: Sequence[Sequence[int]],
    certificate: dict[str, object],
) -> tuple[int, ...]:
    """Return centers used by a turn certificate."""

    verify_turn_farkas_certificate(rows, certificate)
    terms = turn_inequality_terms_for_pattern(rows)
    raw_indices = certificate["term_indices"]
    if not isinstance(raw_indices, list):
        raise ValueError("certificate term_indices must be a list")
    return tuple(sorted({int(terms[index]["center"]) for index in raw_indices}))


def inversion_row_pivot_covers(
    rows: Sequence[Sequence[int]],
    used_centers: Sequence[int],
) -> list[tuple[int, ...]]:
    """Return all minimum vertex sets hitting the indicated full rows."""

    centers = tuple(int(center) for center in used_centers)
    for size in range(1, N + 1):
        covers = [
            pivot_set
            for pivot_set in combinations(range(N), size)
            if all(set(pivot_set).intersection(rows[center]) for center in centers)
        ]
        if covers:
            return covers
    raise ValueError("no inversion row-pivot cover found")


def hit_centers(
    rows: Sequence[Sequence[int]],
    pivots: Sequence[int],
) -> tuple[int, ...]:
    """Return centers whose selected circle contains an inversion pivot."""

    pivot_set = set(int(pivot) for pivot in pivots)
    return tuple(
        center
        for center, row in enumerate(rows)
        if pivot_set.intersection(int(value) for value in row)
    )


def binary_turn_witness(
    rows: Sequence[Sequence[int]],
    centers: Sequence[int],
) -> tuple[int, ...] | None:
    """Find a binary sum-four turn vector for all terms at ``centers``."""

    center_set = set(int(center) for center in centers)
    supports = [
        set(int(value) for value in term["support"])
        for term in turn_inequality_terms_for_pattern(rows)
        if int(term["center"]) in center_set
    ]
    for support in combinations(range(N), 4):
        support_set = set(support)
        if all(support_set.intersection(interval) for interval in supports):
            return tuple(1 if index in support_set else 0 for index in range(N))
    return None


def verify_binary_turn_vector(
    rows: Sequence[Sequence[int]],
    centers: Sequence[int],
    vector: Sequence[int],
) -> None:
    """Verify one exact binary sum-four weak-turn feasibility witness."""

    normalized = tuple(int(value) for value in vector)
    if len(normalized) != N or any(value not in (0, 1) for value in normalized):
        raise ValueError("binary turn vector must contain nine zero/one entries")
    if sum(normalized) != 4:
        raise ValueError("binary turn vector must have weight four")
    center_set = set(int(center) for center in centers)
    for term_index, term in enumerate(turn_inequality_terms_for_pattern(rows)):
        if int(term["center"]) not in center_set:
            continue
        support_sum = sum(normalized[int(value)] for value in term["support"])
        if support_sum < int(term["bound"]):
            raise ValueError(
                f"binary turn vector violates restricted term {term_index}"
            )


def _source_rows(
    motif_payload: dict[str, Any],
) -> tuple[list[list[list[int]]], list[dict[str, Any]]]:
    raw_assignments = motif_payload.get("assignments")
    if not isinstance(raw_assignments, list):
        raise ValueError("motif source must contain assignments")
    rows: list[list[list[int]]] = []
    assignments: list[dict[str, Any]] = []
    for index, raw_assignment in enumerate(raw_assignments, start=1):
        if not isinstance(raw_assignment, dict):
            raise ValueError(f"motif assignment {index} must be an object")
        assignment_id = f"A{index:03d}"
        if raw_assignment.get("assignment_id") != assignment_id:
            raise ValueError(f"motif assignment id mismatch at {index}")
        selected_rows = raw_assignment.get("selected_rows")
        if not isinstance(selected_rows, list):
            raise ValueError(f"{assignment_id} selected_rows must be a list")
        rows.append(compact_to_indexed_rows(selected_rows))
        assignments.append(raw_assignment)
    return rows, assignments


def _source_farkas_certificates(
    turn_payload: dict[str, Any],
) -> list[dict[str, object]]:
    raw_certificates = turn_payload.get("farkas_certificates")
    if not isinstance(raw_certificates, list):
        raise ValueError("turn source must contain Farkas certificates")
    certificates = []
    for index, raw_certificate in enumerate(raw_certificates, start=1):
        if not isinstance(raw_certificate, dict):
            raise ValueError(f"turn certificate {index} must be an object")
        certificates.append(raw_certificate)
    return certificates


def crosswalk_payload(
    turn_payload: dict[str, Any],
    motif_payload: dict[str, Any],
    *,
    turn_source_file_sha256: str,
    motif_source_file_sha256: str,
) -> dict[str, Any]:
    """Generate the stable n=9 fragile/turn/pivot crosswalk."""

    rows_list, motif_assignments = _source_rows(motif_payload)
    certificates = _source_farkas_certificates(turn_payload)
    if len(rows_list) != len(certificates):
        raise ValueError("source assignment and certificate counts differ")
    if frontier_sha256(normalize_pattern_list(rows_list)) != EXPECTED_FRONTIER_SHA256:
        raise ValueError("motif assignments do not match the expected n=9 frontier")
    if turn_payload.get("source_frontier", {}).get(
        "assignment_sha256"
    ) != EXPECTED_FRONTIER_SHA256:
        raise ValueError("turn source records an unexpected frontier hash")
    if turn_payload.get("farkas_replay", {}).get(
        "certificate_sha256"
    ) != EXPECTED_FARKAS_CERTIFICATE_SHA256:
        raise ValueError("turn source records an unexpected certificate hash")

    perfect_counts: list[int] = []
    hamiltonian_counts: list[int] = []
    cycle_type_counts: Counter[str] = Counter()
    cycle_type_assignment_counts: Counter[str] = Counter()
    pivot_halo_records = []
    pivot_halo_lambdas: list[int] = []
    pivot_halo_term_counts: list[int] = []
    matching_search_counts: list[int] = []
    inversion_records = []
    inversion_cover_sizes: list[int] = []
    exceptions = []
    pair_hit_counts: list[int] = []

    for index, (rows, certificate, motif_assignment) in enumerate(
        zip(rows_list, certificates, motif_assignments),
        start=1,
    ):
        assignment_id = f"A{index:03d}"
        if indegrees(rows) != (ROW_SIZE,) * N:
            raise ValueError(f"{assignment_id} does not have 4-regular incidence")

        matchings = enumerate_perfect_matchings(rows)
        matching_cycle_types = [
            _cycle_type_key(permutation_cycle_type(matching))
            for matching in matchings
        ]
        perfect_counts.append(len(matchings))
        hamiltonian_count = matching_cycle_types.count(str(N))
        hamiltonian_counts.append(hamiltonian_count)
        cycle_type_counts.update(matching_cycle_types)
        cycle_type_assignment_counts.update(set(matching_cycle_types))

        matching, pivot_halo, matching_search_count = (
            find_hamiltonian_pivot_halo_certificate(rows, matchings)
        )
        pivot_halo["assignment_id"] = assignment_id
        pivot_halo_records.append(
            {
                "assignment_id": assignment_id,
                "matching": list(matching),
                "matching_cycle_type": [N],
                "certificate": pivot_halo,
            }
        )
        pivot_halo_lambdas.append(int(pivot_halo["lambda"]))
        pivot_halo_term_counts.append(int(pivot_halo["term_count"]))
        matching_search_counts.append(matching_search_count)

        used_centers = used_certificate_centers(rows, certificate)
        covers = inversion_row_pivot_covers(rows, used_centers)
        inversion_cover_sizes.append(len(covers[0]))
        inversion_records.append(
            {
                "assignment_id": assignment_id,
                "used_centers": list(used_centers),
                "minimum_cover_size": len(covers[0]),
                "lexicographic_minimum_cover": list(covers[0]),
            }
        )

        if len(covers[0]) != 3:
            continue

        pair_records = []
        for pivots in combinations(range(N), 2):
            centers = hit_centers(rows, pivots)
            witness = binary_turn_witness(rows, centers)
            if witness is None:
                raise ValueError(
                    f"{assignment_id} pair {pivots} has no binary turn witness"
                )
            verify_binary_turn_vector(rows, centers, witness)
            pair_hit_counts.append(len(centers))
            pair_records.append(
                {
                    "pivots": list(pivots),
                    "hit_centers": list(centers),
                    "binary_turn_vector": list(witness),
                }
            )

        selected_rows = motif_assignment["selected_rows"]
        replay = replay_vertex_circle_quotient(
            N,
            CYCLIC_ORDER,
            parse_selected_rows(selected_rows),
        )
        exceptions.append(
            {
                "assignment_id": assignment_id,
                "family_id": str(motif_assignment["family_id"]),
                "template_id": str(motif_assignment["template_id"]),
                "motif_status": str(motif_assignment["status"]),
                "selected_rows": selected_rows,
                "stored_certificate_term_indices": list(certificate["term_indices"]),
                "minimum_pivot_triples": [list(cover) for cover in covers],
                "two_pivot_restrictions": pair_records,
                "vertex_circle_replay": {
                    "status": replay.status,
                    "strict_edge_count": replay.strict_edge_count,
                    "self_edge_conflict_count": len(replay.self_edge_conflicts),
                    "strict_cycle_edge_count": len(replay.cycle_edges),
                },
            }
        )

    pivot_halo_hash_rows = [
        {
            "assignment_id": record["assignment_id"],
            "matching": record["matching"],
            "certificate": record["certificate"],
        }
        for record in pivot_halo_records
    ]

    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "claim_scope": CLAIM_SCOPE,
        "n": N,
        "row_size": ROW_SIZE,
        "cyclic_order": list(CYCLIC_ORDER),
        "source_artifacts": [
            {
                "path": "data/certificates/n9_turn_inequality_frontier.json",
                "role": "stored weak-turn Farkas certificates",
                "file_sha256": turn_source_file_sha256,
                "frontier_sha256": EXPECTED_FRONTIER_SHA256,
                "farkas_certificate_sha256": EXPECTED_FARKAS_CERTIFICATE_SHA256,
            },
            {
                "path": (
                    "data/certificates/"
                    "n9_vertex_circle_frontier_motif_classification.json"
                ),
                "role": "labelled frontier rows and motif/template crosswalk",
                "file_sha256": motif_source_file_sha256,
            },
        ],
        "regular_incidence": {
            "assignment_count": len(rows_list),
            "indegree_histogram": _histogram(
                [str(indegrees(rows)) for rows in rows_list]
            ),
            "interpretation": (
                "At n=9, nine exact-four rows with total incidence 36 and the "
                "all-rich counting lower bound force witness indegree four. "
                "The resulting 4-regular bipartite incidence graph has perfect "
                "matchings."
            ),
        },
        "witness_pivot_matching": {
            "definition": (
                "A bijection q from row centers to witnesses with q(y) in S_y; "
                "the stored choice is a single directed 9-cycle."
            ),
            "perfect_matching_count": sum(perfect_counts),
            "perfect_matching_count_histogram": _histogram(perfect_counts),
            "hamiltonian_matching_count": sum(hamiltonian_counts),
            "hamiltonian_matching_count_histogram": _histogram(
                hamiltonian_counts
            ),
            "matching_cycle_type_counts": {
                key: int(cycle_type_counts[key])
                for key in sorted(cycle_type_counts)
            },
            "matching_cycle_type_assignment_counts": {
                key: int(cycle_type_assignment_counts[key])
                for key in sorted(cycle_type_assignment_counts)
            },
            "assignment_count_with_hamiltonian_matching": sum(
                count > 0 for count in hamiltonian_counts
            ),
        },
        "pivot_halo_turn_certificates": {
            "definition": (
                "Each selected turn term has one endpoint q(y) and its other "
                "selected endpoint in the three-witness halo S_y minus {q(y)}."
            ),
            "certificate_count": len(pivot_halo_records),
            "certificate_sha256": _stable_sha256(pivot_halo_hash_rows),
            "lambda_histogram": _histogram(pivot_halo_lambdas),
            "term_count_histogram": _histogram(pivot_halo_term_counts),
            "hamiltonian_matchings_examined": sum(matching_search_counts),
            "records": pivot_halo_records,
        },
        "inversion_row_pivot_covers": {
            "definition": (
                "A pivot set P covers a stored turn certificate when "
                "P intersects every full selected row S_y whose center y "
                "occurs in that certificate. Inversion at such a pivot maps "
                "the corresponding selected row circle to a line. Different "
                "rows may use different inversion charts; this does not put "
                "all supporting circles into one common inverted plane."
            ),
            "certificate_count": len(inversion_records),
            "record_sha256": _stable_sha256(inversion_records),
            "minimum_cover_size_histogram": _histogram(inversion_cover_sizes),
            "three_pivot_assignment_ids": [
                record["assignment_id"]
                for record in inversion_records
                if record["minimum_cover_size"] == 3
            ],
            "records": inversion_records,
        },
        "three_pivot_exception": {
            "assignment_count": len(exceptions),
            "record_sha256": _stable_sha256(exceptions),
            "family_ids": sorted({row["family_id"] for row in exceptions}),
            "template_ids": sorted({row["template_id"] for row in exceptions}),
            "minimum_pivot_triple_count": sum(
                len(row["minimum_pivot_triples"]) for row in exceptions
            ),
            "two_pivot_case_count": sum(
                len(row["two_pivot_restrictions"]) for row in exceptions
            ),
            "two_pivot_binary_feasible_count": sum(
                len(row["two_pivot_restrictions"]) for row in exceptions
            ),
            "two_pivot_feasibility_scope": (
                "Nonnegative weak-turn relaxation only; stored binary "
                "witnesses may have zero coordinates and are not geometric "
                "strictly convex turn vectors."
            ),
            "pair_hit_center_count_histogram": _histogram(pair_hit_counts),
            "vertex_circle_status_counts": _histogram(
                [
                    row["vertex_circle_replay"]["status"]
                    for row in exceptions
                ]
            ),
            "strict_edge_count": sum(
                int(row["vertex_circle_replay"]["strict_edge_count"])
                for row in exceptions
            ),
            "self_edge_conflict_count": sum(
                int(row["vertex_circle_replay"]["self_edge_conflict_count"])
                for row in exceptions
            ),
            "records": exceptions,
        },
        "limitations": [
            "The perfect matching and pivot census are finite n=9 facts.",
            "The weak turn inequalities remain review-pending geometry.",
            "A pivot-to-halo certificate does not force the pivot to be an endpoint of every inclusion-minimal turn interval.",
            "An inversion row-pivot cover may use different inversion charts for different rows.",
            "Binary two-pivot witnesses certify only the nonnegative weak-turn relaxation and may have zero turns.",
            "Current fragile-cover, incidence, crossing, weak-turn, and vertex-circle abstractions do not imply a general three-pivot reduction.",
            "No n=9, minimal-counterexample, counterexample, or global theorem claim is promoted.",
        ],
        "conclusion": CONCLUSION,
        "review_requirements": list(REVIEW_REQUIREMENTS),
        "provenance": dict(PROVENANCE),
    }
    return payload


def _expected_headline_fields() -> dict[str, Any]:
    return {
        "regular_incidence.assignment_count": EXPECTED_FRONTIER_ASSIGNMENTS,
        "witness_pivot_matching.perfect_matching_count": (
            EXPECTED_TOTAL_PERFECT_MATCHINGS
        ),
        "witness_pivot_matching.perfect_matching_count_histogram": (
            EXPECTED_PERFECT_MATCHING_COUNT_HISTOGRAM
        ),
        "witness_pivot_matching.hamiltonian_matching_count": (
            EXPECTED_HAMILTONIAN_MATCHINGS
        ),
        "witness_pivot_matching.hamiltonian_matching_count_histogram": (
            EXPECTED_HAMILTONIAN_COUNT_HISTOGRAM
        ),
        "witness_pivot_matching.matching_cycle_type_counts": (
            EXPECTED_MATCHING_CYCLE_TYPE_COUNTS
        ),
        "witness_pivot_matching.matching_cycle_type_assignment_counts": (
            EXPECTED_MATCHING_CYCLE_TYPE_ASSIGNMENT_COUNTS
        ),
        "witness_pivot_matching.assignment_count_with_hamiltonian_matching": (
            EXPECTED_FRONTIER_ASSIGNMENTS
        ),
        "pivot_halo_turn_certificates.lambda_histogram": (
            EXPECTED_PIVOT_HALO_LAMBDA_HISTOGRAM
        ),
        "pivot_halo_turn_certificates.term_count_histogram": (
            EXPECTED_PIVOT_HALO_TERM_COUNT_HISTOGRAM
        ),
        "pivot_halo_turn_certificates.certificate_sha256": (
            EXPECTED_PIVOT_HALO_CERTIFICATE_SHA256
        ),
        "inversion_row_pivot_covers.record_sha256": (
            EXPECTED_INVERSION_COVER_RECORD_SHA256
        ),
        "inversion_row_pivot_covers.minimum_cover_size_histogram": (
            EXPECTED_INVERSION_COVER_SIZE_HISTOGRAM
        ),
        "inversion_row_pivot_covers.three_pivot_assignment_ids": (
            EXPECTED_THREE_PIVOT_ASSIGNMENTS
        ),
        "three_pivot_exception.assignment_count": 2,
        "three_pivot_exception.record_sha256": EXPECTED_EXCEPTION_RECORD_SHA256,
        "three_pivot_exception.family_ids": [EXPECTED_EXCEPTION_FAMILY_ID],
        "three_pivot_exception.template_ids": [EXPECTED_EXCEPTION_TEMPLATE_ID],
        "three_pivot_exception.minimum_pivot_triple_count": (
            EXPECTED_EXCEPTION_MINIMUM_TRIPLES
        ),
        "three_pivot_exception.two_pivot_case_count": (
            EXPECTED_EXCEPTION_PAIR_CASES
        ),
        "three_pivot_exception.two_pivot_binary_feasible_count": (
            EXPECTED_EXCEPTION_PAIR_CASES
        ),
        "three_pivot_exception.pair_hit_center_count_histogram": (
            EXPECTED_PAIR_HIT_CENTER_HISTOGRAM
        ),
        "three_pivot_exception.vertex_circle_status_counts": {"self_edge": 2},
        "three_pivot_exception.strict_edge_count": EXPECTED_EXCEPTION_STRICT_EDGES,
        "three_pivot_exception.self_edge_conflict_count": (
            EXPECTED_EXCEPTION_SELF_EDGES
        ),
    }


def _nested_value(payload: dict[str, Any], dotted_key: str) -> Any:
    value: Any = payload
    for key in dotted_key.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def validate_payload(
    payload: dict[str, Any],
    turn_payload: dict[str, Any],
    motif_payload: dict[str, Any],
    *,
    turn_source_file_sha256: str,
    motif_source_file_sha256: str,
) -> list[str]:
    """Regenerate and compare the complete stored crosswalk."""

    errors: list[str] = []
    for key, expected in (
        ("schema", SCHEMA),
        ("status", STATUS),
        ("trust", TRUST),
        ("claim_scope", CLAIM_SCOPE),
        ("n", N),
        ("row_size", ROW_SIZE),
        ("cyclic_order", list(CYCLIC_ORDER)),
        ("conclusion", CONCLUSION),
        ("review_requirements", REVIEW_REQUIREMENTS),
        ("provenance", PROVENANCE),
    ):
        if payload.get(key) != expected:
            errors.append(f"{key} mismatch")
    if errors:
        return errors

    try:
        regenerated = crosswalk_payload(
            turn_payload,
            motif_payload,
            turn_source_file_sha256=turn_source_file_sha256,
            motif_source_file_sha256=motif_source_file_sha256,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return [f"source replay failed: {exc}"]
    if payload != regenerated:
        errors.append("stored payload differs from complete regenerated crosswalk")
    return errors


def assert_expected_payload(payload: dict[str, Any]) -> None:
    """Assert the stable, bounded headline counts of a generated payload."""

    for key, expected in _expected_headline_fields().items():
        actual = _nested_value(payload, key)
        if actual != expected:
            raise AssertionError(f"{key}: expected {expected!r}, got {actual!r}")

    records = payload["pivot_halo_turn_certificates"]["records"]
    lambda_two_ids = [
        record["assignment_id"]
        for record in records
        if record["certificate"]["lambda"] == 2
    ]
    if lambda_two_ids != EXPECTED_PIVOT_HALO_LAMBDA_TWO_ASSIGNMENTS:
        raise AssertionError(
            "unexpected pivot-to-halo lambda-two assignments: "
            f"{lambda_two_ids!r}"
        )

    source_artifacts = payload.get("source_artifacts")
    if not isinstance(source_artifacts, list) or len(source_artifacts) != 2:
        raise AssertionError("expected two source-artifact records")
    source_hashes = [record.get("file_sha256") for record in source_artifacts]
    expected_hashes = [
        EXPECTED_TURN_SOURCE_FILE_SHA256,
        EXPECTED_MOTIF_SOURCE_FILE_SHA256,
    ]
    if source_hashes != expected_hashes:
        raise AssertionError(
            f"unexpected source file hashes: {source_hashes!r}"
        )
