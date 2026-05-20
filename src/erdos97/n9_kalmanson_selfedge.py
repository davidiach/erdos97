"""Exact n=9 selected-witness/Kalmanson self-edge checker.

This module is a compact, review-pending finite-case artifact for Erdos
Problem #97.  It does not claim a general proof and does not claim a
counterexample.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import hashlib
import json
from typing import Iterable, Sequence


N = 9
ROW_SIZE = 4
EXPECTED_ROW_OPTIONS = 70
EXPECTED_NODES = 100_818
EXPECTED_TERMINALS = 184
EXPECTED_KILLS = 184
EXPECTED_UNKILLED = 0
EXPECTED_CERTIFICATE_SHA256 = (
    "8e5344265e774ce352d64e16e0480eaff4ad6051a69051a304a3f9145db0e3c5"
)
TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
STATUS = "review_pending_n9_kalmanson_selfedge"
CLAIM_SCOPE = (
    "Candidate repo-local selected-witness n=9 finite-case obstruction only; "
    "does not alter official/global status."
)

Pair = tuple[int, int]
RowMask = int


def bitset(items: Iterable[int]) -> int:
    """Return the integer bit mask with the listed labels set."""
    mask = 0
    for item in items:
        mask |= 1 << item
    return mask


def bits(mask: int) -> list[int]:
    """Return labels set in ``mask`` in increasing order."""
    out: list[int] = []
    label = 0
    while mask:
        if mask & 1:
            out.append(label)
        mask >>= 1
        label += 1
    return out


def pair(a: int, b: int) -> Pair:
    """Return a normalized unordered distance pair."""
    if a == b:
        raise ValueError("distance pair requires distinct labels")
    return (a, b) if a < b else (b, a)


def cyclic_adjacent(n: int, a: int, b: int) -> bool:
    """Return whether labels ``a`` and ``b`` are adjacent in cyclic order."""
    return abs(a - b) == 1 or abs(a - b) == n - 1


def chords_cross(n: int, a: int, b: int, c: int, d: int) -> bool:
    """Return whether chords ``ab`` and ``cd`` cross in natural cyclic order."""
    if len({a, b, c, d}) < 4:
        return False
    if a > b:
        a, b = b, a
    in_c = a < c < b
    in_d = a < d < b
    return in_c != in_d


def row_options(n: int, center: int) -> list[RowMask]:
    """Return all selected witness 4-subsets for ``center`` as bit masks."""
    others = [label for label in range(n) if label != center]
    return [bitset(combo) for combo in combinations(others, ROW_SIZE)]


def row_pair_is_necessary(
    n: int,
    i: int,
    row_i: RowMask,
    j: int,
    row_j: RowMask,
) -> bool:
    """Return whether two selected rows pass exact necessary filters."""
    intersection = row_i & row_j
    shared = intersection.bit_count()

    # Two distinct centered circles meet in at most two points.
    if shared > 2:
        return False

    # A two-overlap forces the center chord to cross the common-witness chord.
    if cyclic_adjacent(n, i, j) and shared > 1:
        return False
    if shared == 2:
        x, y = bits(intersection)
        if not chords_cross(n, i, j, x, y):
            return False

    return True


def witness_pair_capacity_ok(counts: dict[Pair, int], row: RowMask) -> bool:
    """Return whether adding ``row`` respects the witness-pair cap."""
    witnesses = bits(row)
    for a, b in combinations(witnesses, 2):
        if counts.get(pair(a, b), 0) >= 2:
            return False
    return True


def add_witness_pairs(counts: dict[Pair, int], row: RowMask) -> list[Pair]:
    """Add witness-pair occurrences from ``row`` and return touched pairs."""
    changed: list[Pair] = []
    for a, b in combinations(bits(row), 2):
        witness_pair = pair(a, b)
        counts[witness_pair] = counts.get(witness_pair, 0) + 1
        changed.append(witness_pair)
    return changed


def undo_witness_pairs(counts: dict[Pair, int], changed: Sequence[Pair]) -> None:
    """Undo ``add_witness_pairs`` for backtracking."""
    for witness_pair in changed:
        counts[witness_pair] -= 1
        if counts[witness_pair] == 0:
            del counts[witness_pair]


@dataclass(frozen=True)
class EnumerationResult:
    """Assignments and search-node count for the exact brancher."""

    assignments: list[list[RowMask]]
    nodes_visited: int


def enumerate_selected_systems(n: int = N) -> EnumerationResult:
    """Enumerate selected-row systems surviving the basic exact filters."""
    options = [row_options(n, center) for center in range(n)]
    selected: list[RowMask | None] = [None] * n
    witness_pair_counts: dict[Pair, int] = {}
    assignments: list[list[RowMask]] = []
    nodes_visited = 0

    def valid_options_for_center(center: int) -> list[RowMask]:
        out: list[RowMask] = []
        for row in options[center]:
            ok = True
            for other_center, other_row in enumerate(selected):
                if other_row is not None and not row_pair_is_necessary(
                    n,
                    center,
                    row,
                    other_center,
                    other_row,
                ):
                    ok = False
                    break
            if ok and witness_pair_capacity_ok(witness_pair_counts, row):
                out.append(row)
        return out

    def recurse(depth: int) -> None:
        nonlocal nodes_visited
        nodes_visited += 1
        if depth == n:
            assignments.append([int(row) for row in selected if row is not None])
            return

        best_center = -1
        best_options: list[RowMask] | None = None
        for center in range(n):
            if selected[center] is not None:
                continue
            current = valid_options_for_center(center)
            if best_options is None or len(current) < len(best_options):
                best_center = center
                best_options = current
                if not current:
                    break

        if not best_options:
            return

        for row in best_options:
            selected[best_center] = row
            changed = add_witness_pairs(witness_pair_counts, row)
            recurse(depth + 1)
            undo_witness_pairs(witness_pair_counts, changed)
            selected[best_center] = None

    recurse(0)
    return EnumerationResult(assignments=assignments, nodes_visited=nodes_visited)


class DSU:
    """Small deterministic union-find over distance-pair labels."""

    def __init__(self, items: Iterable[Pair]):
        self.parent: dict[Pair, Pair] = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, a: Pair, b: Pair) -> None:
        root_a = self.find(a)
        root_b = self.find(b)
        if root_a == root_b:
            return
        if root_b < root_a:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a


def selected_distance_quotient(n: int, rows: Sequence[RowMask]) -> DSU:
    """Build the quotient generated by selected center-witness equalities."""
    all_pairs = [pair(i, j) for i in range(n) for j in range(i + 1, n)]
    dsu = DSU(all_pairs)
    for center, row in enumerate(rows):
        witnesses = bits(row)
        base = pair(center, witnesses[0])
        for witness in witnesses[1:]:
            dsu.union(base, pair(center, witness))
    return dsu


def quotient_multiset(dsu: DSU, pairs: Sequence[Pair]) -> list[Pair]:
    """Return the sorted quotient-class multiset for ``pairs``."""
    return sorted(dsu.find(distance_pair) for distance_pair in pairs)


def first_kalmanson_self_edge(
    n: int,
    rows: Sequence[RowMask],
) -> dict[str, object] | None:
    """Find a strict Kalmanson inequality that collapses to a self-edge."""
    dsu = selected_distance_quotient(n, rows)
    for a, b, c, d in combinations(range(n), 4):
        inequalities = [
            ("K1", [pair(a, b), pair(c, d)], [pair(a, c), pair(b, d)]),
            ("K2", [pair(a, d), pair(b, c)], [pair(a, c), pair(b, d)]),
        ]
        for name, lhs, rhs in inequalities:
            quotient_lhs = quotient_multiset(dsu, lhs)
            quotient_rhs = quotient_multiset(dsu, rhs)
            if quotient_lhs == quotient_rhs:
                return {
                    "quadruple": [a, b, c, d],
                    "inequality": name,
                    "lhs_pairs": [list(distance_pair) for distance_pair in lhs],
                    "rhs_pairs": [list(distance_pair) for distance_pair in rhs],
                    "quotient_multiset": [
                        list(distance_pair) for distance_pair in quotient_lhs
                    ],
                }
    return None


def canonical_assignment_payload(rows: Sequence[RowMask]) -> list[list[int]]:
    """Return row masks as sorted witness-label lists."""
    return [bits(row) for row in rows]


def certificate_digest(certs: Sequence[dict[str, object]]) -> str:
    """Return the stable digest used for the certificate list."""
    digest_payload = json.dumps(certs, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(digest_payload).hexdigest()


def rows_from_payload(
    rows_payload: Sequence[Sequence[int]],
    expected_n: int | None = None,
) -> list[RowMask]:
    """Convert row-list payloads back to masks with light validation."""
    rows: list[RowMask] = []
    n = len(rows_payload)
    if expected_n is not None and n != expected_n:
        raise ValueError(f"payload has {n} rows, expected {expected_n}")
    for center, witnesses in enumerate(rows_payload):
        if len(witnesses) != ROW_SIZE:
            raise ValueError(f"row {center} has size {len(witnesses)}, expected 4")
        if center in witnesses:
            raise ValueError(f"row {center} contains its center")
        if sorted(witnesses) != list(witnesses):
            raise ValueError(f"row {center} witnesses are not sorted")
        if len(set(witnesses)) != ROW_SIZE:
            raise ValueError(f"row {center} has duplicate witnesses")
        if any(witness < 0 or witness >= n for witness in witnesses):
            raise ValueError(f"row {center} contains a label outside 0..{n - 1}")
        rows.append(bitset(witnesses))
    return rows


def run(n: int = N) -> dict[str, object]:
    """Run the exhaustive checker and return a stable JSON payload."""
    if n != N:
        raise ValueError("n9 Kalmanson self-edge artifacts must be generated with n=9")
    enumeration = enumerate_selected_systems(n)
    certs: list[dict[str, object]] = []
    unkilled: list[list[list[int]]] = []
    for rows in enumeration.assignments:
        cert = first_kalmanson_self_edge(n, rows)
        assignment = canonical_assignment_payload(rows)
        if cert is None:
            unkilled.append(assignment)
        else:
            certs.append({"rows": assignment, "self_edge": cert})

    digest = certificate_digest(certs)
    return {
        "schema": "erdos97.n9_kalmanson_selfedge.v1",
        "trust": TRUST,
        "status": STATUS,
        "claim_scope": CLAIM_SCOPE,
        "provenance": {
            "generator": "scripts/check_n9_kalmanson_selfedge.py",
            "command": (
                "python scripts/check_n9_kalmanson_selfedge.py "
                "--write --assert-expected --summary-only"
            ),
            "source": "2026-05-20 in-session exact checker/certificate import",
            "notes": (
                "The stable certificate_sha256 hashes only the certificates list, "
                "so runtime metadata can be audited separately."
            ),
        },
        "n": n,
        "row_options_per_center": len(row_options(n, 0)),
        "nodes_visited": enumeration.nodes_visited,
        "terminal_assignments": len(enumeration.assignments),
        "killed_by_kalmanson_self_edge": len(certs),
        "unkilled": len(unkilled),
        "certificate_sha256": digest,
        "certificates": certs,
        "unkilled_assignments": unkilled,
    }


def summary_payload(payload: dict[str, object]) -> dict[str, object]:
    """Return ``payload`` without bulky certificate arrays."""
    return {
        key: value
        for key, value in payload.items()
        if key not in {"certificates", "unkilled_assignments"}
    }


def assert_expected_summary(payload: dict[str, object]) -> None:
    """Assert the expected review-pending n=9 Kalmanson counts."""
    expected = {
        "schema": "erdos97.n9_kalmanson_selfedge.v1",
        "trust": TRUST,
        "status": STATUS,
        "n": N,
        "row_options_per_center": EXPECTED_ROW_OPTIONS,
        "nodes_visited": EXPECTED_NODES,
        "terminal_assignments": EXPECTED_TERMINALS,
        "killed_by_kalmanson_self_edge": EXPECTED_KILLS,
        "unkilled": EXPECTED_UNKILLED,
        "certificate_sha256": EXPECTED_CERTIFICATE_SHA256,
    }
    for key, expected_value in expected.items():
        actual = payload.get(key)
        if actual != expected_value:
            raise AssertionError(f"{key}: expected {expected_value!r}, got {actual!r}")


def verify_certificate_payload(payload: dict[str, object]) -> dict[str, object]:
    """Replay stored Kalmanson self-edge certificates without the brancher."""
    raw_certs = payload.get("certificates")
    if not isinstance(raw_certs, list):
        raise ValueError("certificate payload must contain a certificates list")
    n = payload.get("n")
    if not isinstance(n, int):
        raise ValueError("certificate payload must contain integer n")

    for index, raw_cert in enumerate(raw_certs):
        if not isinstance(raw_cert, dict):
            raise ValueError(f"certificate {index} is not an object")
        rows_payload = raw_cert.get("rows")
        self_edge = raw_cert.get("self_edge")
        if not isinstance(rows_payload, list) or not isinstance(self_edge, dict):
            raise ValueError(f"certificate {index} is malformed")
        rows = rows_from_payload(rows_payload, expected_n=n)
        recomputed = first_kalmanson_self_edge(n, rows)
        if recomputed is None:
            raise AssertionError(f"certificate {index} has no self-edge on replay")
        if recomputed != self_edge:
            raise AssertionError(
                f"certificate {index} mismatch: expected {self_edge!r}, "
                f"got {recomputed!r}"
            )

    digest = certificate_digest(raw_certs)
    stored_digest = payload.get("certificate_sha256")
    if digest != stored_digest:
        raise AssertionError(
            f"certificate digest mismatch: expected {stored_digest!r}, got {digest!r}"
        )

    summary = summary_payload(payload)
    summary["verified_certificates"] = len(raw_certs)
    return summary
