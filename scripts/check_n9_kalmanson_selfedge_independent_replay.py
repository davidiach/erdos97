#!/usr/bin/env python3
"""Independently replay the stored n=9 Kalmanson self-edge certificate.

This script treats ``data/certificates/n9_kalmanson_selfedge.json`` as input
data. It intentionally does not import ``erdos97.n9_kalmanson_selfedge`` or
rerun the search brancher. The goal is a small reviewer-facing audit of the
checked-in certificate rows, not a promotion of the review-pending n=9 result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERTIFICATE = ROOT / "data" / "certificates" / "n9_kalmanson_selfedge.json"

EXPECTED_SCHEMA = "erdos97.n9_kalmanson_selfedge.v1"
EXPECTED_TRUST = "MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING"
EXPECTED_STATUS = "review_pending_n9_kalmanson_selfedge"
EXPECTED_N = 9
EXPECTED_ROW_SIZE = 4
EXPECTED_ROW_OPTIONS = 70
EXPECTED_NODES = 100_818
EXPECTED_TERMINALS = 184
EXPECTED_KILLS = 184
EXPECTED_UNKILLED = 0
EXPECTED_CERTIFICATE_SHA256 = (
    "8e5344265e774ce352d64e16e0480eaff4ad6051a69051a304a3f9145db0e3c5"
)
SUMMARY_JSON_KEYS = (
    "schema",
    "source_schema",
    "status",
    "trust",
    "claim_scope",
    "n",
    "certificates_checked",
    "unique_assignments_checked",
    "incidence_filter_failures",
    "self_edge_failures",
    "certificate_sha256",
    "digest_matches",
)

Pair = tuple[int, int]


class AuditError(ValueError):
    """Raised when the stored certificate fails an audit check."""


class DSU:
    """Tiny union-find over unordered distance-pair labels."""

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


def pair(a: int, b: int) -> Pair:
    """Return a normalized unordered pair."""
    if a == b:
        raise AuditError("distance pair requires distinct labels")
    return (a, b) if a < b else (b, a)


def cyclic_adjacent(n: int, a: int, b: int) -> bool:
    """Return whether ``a`` and ``b`` are adjacent in cyclic order."""
    return abs(a - b) == 1 or abs(a - b) == n - 1


def chords_cross(n: int, a: int, b: int, c: int, d: int) -> bool:
    """Return whether chords ``ab`` and ``cd`` cross in the natural order."""
    del n
    if len({a, b, c, d}) < 4:
        return False
    if a > b:
        a, b = b, a
    in_c = a < c < b
    in_d = a < d < b
    return in_c != in_d


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise AuditError(f"{path} must contain a JSON object")
    return payload


def certificate_digest(certificates: Sequence[dict[str, Any]]) -> str:
    """Return the stable certificate-list digest."""
    raw = json.dumps(certificates, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def expect_equal(label: str, actual: Any, expected: Any) -> None:
    """Raise if an expected scalar does not match."""
    if actual != expected:
        raise AuditError(f"{label}: expected {expected!r}, got {actual!r}")


def validate_row(n: int, center: int, raw_row: Any) -> tuple[int, int, int, int]:
    """Validate and return one selected row."""
    if not isinstance(raw_row, list):
        raise AuditError(f"row {center} is not a list")
    if len(raw_row) != EXPECTED_ROW_SIZE:
        raise AuditError(f"row {center} has size {len(raw_row)}")
    if any(not isinstance(label, int) for label in raw_row):
        raise AuditError(f"row {center} contains a non-integer label")
    if raw_row != sorted(raw_row):
        raise AuditError(f"row {center} is not sorted")
    if len(set(raw_row)) != EXPECTED_ROW_SIZE:
        raise AuditError(f"row {center} contains duplicate witnesses")
    if center in raw_row:
        raise AuditError(f"row {center} contains its center")
    if any(label < 0 or label >= n for label in raw_row):
        raise AuditError(f"row {center} contains a label outside 0..{n - 1}")
    return tuple(raw_row)  # type: ignore[return-value]


def validate_rows(n: int, raw_rows: Any) -> list[tuple[int, int, int, int]]:
    """Validate all selected rows in one certificate."""
    if not isinstance(raw_rows, list):
        raise AuditError("certificate rows field is not a list")
    if len(raw_rows) != n:
        raise AuditError(f"certificate has {len(raw_rows)} rows, expected {n}")
    return [validate_row(n, center, raw_rows[center]) for center in range(n)]


def validate_incidence_filters(n: int, rows: Sequence[Sequence[int]]) -> None:
    """Replay the exact necessary incidence/crossing filters on stored rows."""
    witness_pair_counts: dict[Pair, int] = {}
    for center, row in enumerate(rows):
        for a, b in combinations(row, 2):
            witness_pair = pair(a, b)
            witness_pair_counts[witness_pair] = witness_pair_counts.get(witness_pair, 0) + 1
            if witness_pair_counts[witness_pair] > 2:
                raise AuditError(
                    f"witness pair {witness_pair} appears in more than two rows"
                )

    for i, j in combinations(range(n), 2):
        shared = sorted(set(rows[i]).intersection(rows[j]))
        if len(shared) > 2:
            raise AuditError(f"rows {i},{j} share more than two witnesses")
        if cyclic_adjacent(n, i, j) and len(shared) > 1:
            raise AuditError(f"adjacent rows {i},{j} share two witnesses")
        if len(shared) == 2 and not chords_cross(n, i, j, shared[0], shared[1]):
            raise AuditError(
                f"two-overlap rows {i},{j} do not cross witness chord {shared}"
            )


def selected_distance_quotient(n: int, rows: Sequence[Sequence[int]]) -> DSU:
    """Build the selected-distance quotient from stored rows."""
    dsu = DSU(pair(i, j) for i in range(n) for j in range(i + 1, n))
    for center, row in enumerate(rows):
        base = pair(center, row[0])
        for witness in row[1:]:
            dsu.union(base, pair(center, witness))
    return dsu


def normalize_pair_list(raw_pairs: Any, label: str) -> list[Pair]:
    """Validate a JSON pair list and return normalized pairs."""
    if not isinstance(raw_pairs, list):
        raise AuditError(f"{label} is not a list")
    out: list[Pair] = []
    for index, raw_pair in enumerate(raw_pairs):
        if (
            not isinstance(raw_pair, list)
            or len(raw_pair) != 2
            or not all(isinstance(value, int) for value in raw_pair)
        ):
            raise AuditError(f"{label}[{index}] is not an integer pair")
        out.append(pair(raw_pair[0], raw_pair[1]))
    return out


def expected_kalmanson_pairs(quadruple: Sequence[int], inequality: str) -> tuple[list[Pair], list[Pair]]:
    """Return the displayed sides for one strict Kalmanson inequality."""
    if len(quadruple) != 4 or list(quadruple) != sorted(quadruple):
        raise AuditError(f"invalid cyclic Kalmanson quadruple {quadruple!r}")
    a, b, c, d = quadruple
    if inequality == "K1":
        return [pair(a, b), pair(c, d)], [pair(a, c), pair(b, d)]
    if inequality == "K2":
        return [pair(a, d), pair(b, c)], [pair(a, c), pair(b, d)]
    raise AuditError(f"unknown Kalmanson inequality {inequality!r}")


def quotient_multiset(dsu: DSU, pairs: Sequence[Pair]) -> list[Pair]:
    """Return a sorted quotient-class multiset for distance pairs."""
    return sorted(dsu.find(distance_pair) for distance_pair in pairs)


def validate_self_edge(n: int, rows: Sequence[Sequence[int]], raw_self_edge: Any) -> None:
    """Replay one stored Kalmanson self-edge certificate."""
    if not isinstance(raw_self_edge, dict):
        raise AuditError("self_edge field is not an object")
    raw_quadruple = raw_self_edge.get("quadruple")
    if (
        not isinstance(raw_quadruple, list)
        or len(raw_quadruple) != 4
        or not all(isinstance(label, int) for label in raw_quadruple)
        or len(set(raw_quadruple)) != 4
        or any(label < 0 or label >= n for label in raw_quadruple)
    ):
        raise AuditError(f"invalid quadruple {raw_quadruple!r}")

    inequality = raw_self_edge.get("inequality")
    if not isinstance(inequality, str):
        raise AuditError("self_edge.inequality is not a string")
    expected_lhs, expected_rhs = expected_kalmanson_pairs(raw_quadruple, inequality)
    lhs = normalize_pair_list(raw_self_edge.get("lhs_pairs"), "lhs_pairs")
    rhs = normalize_pair_list(raw_self_edge.get("rhs_pairs"), "rhs_pairs")
    if lhs != expected_lhs:
        raise AuditError(f"stored lhs pairs {lhs!r} do not match {expected_lhs!r}")
    if rhs != expected_rhs:
        raise AuditError(f"stored rhs pairs {rhs!r} do not match {expected_rhs!r}")

    dsu = selected_distance_quotient(n, rows)
    quotient_lhs = quotient_multiset(dsu, lhs)
    quotient_rhs = quotient_multiset(dsu, rhs)
    if quotient_lhs != quotient_rhs:
        raise AuditError(
            f"Kalmanson row is not a self-edge: {quotient_lhs!r} != {quotient_rhs!r}"
        )

    stored_multiset = normalize_pair_list(
        raw_self_edge.get("quotient_multiset"),
        "quotient_multiset",
    )
    if stored_multiset != quotient_lhs:
        raise AuditError(
            f"stored quotient multiset {stored_multiset!r} does not match {quotient_lhs!r}"
        )


def audit_certificate_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Replay the stored certificate payload with local-only logic."""
    expect_equal("schema", payload.get("schema"), EXPECTED_SCHEMA)
    expect_equal("trust", payload.get("trust"), EXPECTED_TRUST)
    expect_equal("status", payload.get("status"), EXPECTED_STATUS)
    expect_equal("n", payload.get("n"), EXPECTED_N)
    expect_equal("row_options_per_center", payload.get("row_options_per_center"), EXPECTED_ROW_OPTIONS)
    expect_equal("nodes_visited", payload.get("nodes_visited"), EXPECTED_NODES)
    expect_equal("terminal_assignments", payload.get("terminal_assignments"), EXPECTED_TERMINALS)
    expect_equal(
        "killed_by_kalmanson_self_edge",
        payload.get("killed_by_kalmanson_self_edge"),
        EXPECTED_KILLS,
    )
    expect_equal("unkilled", payload.get("unkilled"), EXPECTED_UNKILLED)
    expect_equal("certificate_sha256", payload.get("certificate_sha256"), EXPECTED_CERTIFICATE_SHA256)

    raw_certificates = payload.get("certificates")
    if not isinstance(raw_certificates, list):
        raise AuditError("certificates field is not a list")
    if len(raw_certificates) != EXPECTED_TERMINALS:
        raise AuditError(
            f"expected {EXPECTED_TERMINALS} certificates, got {len(raw_certificates)}"
        )
    digest = certificate_digest(raw_certificates)
    expect_equal("computed certificate digest", digest, EXPECTED_CERTIFICATE_SHA256)

    seen_assignments: set[tuple[tuple[int, ...], ...]] = set()
    first_self_edge: dict[str, Any] | None = None
    for index, raw_certificate in enumerate(raw_certificates):
        if not isinstance(raw_certificate, dict):
            raise AuditError(f"certificate {index} is not an object")
        rows = validate_rows(EXPECTED_N, raw_certificate.get("rows"))
        assignment_key = tuple(tuple(row) for row in rows)
        if assignment_key in seen_assignments:
            raise AuditError(f"duplicate assignment at certificate {index}")
        seen_assignments.add(assignment_key)
        validate_incidence_filters(EXPECTED_N, rows)
        raw_self_edge = raw_certificate.get("self_edge")
        validate_self_edge(EXPECTED_N, rows, raw_self_edge)
        if index == 0:
            first_self_edge = raw_self_edge

    raw_unkilled = payload.get("unkilled_assignments")
    if raw_unkilled != []:
        raise AuditError("unkilled_assignments must be an empty list")

    return {
        "schema": "erdos97.n9_kalmanson_selfedge_independent_replay.v1",
        "source_schema": payload.get("schema"),
        "status": "ok",
        "trust": "REVIEW_PENDING_DIAGNOSTIC",
        "claim_scope": (
            "Independent replay of stored n=9 Kalmanson self-edge certificates "
            "only; not brancher coverage, not a proof of n=9, and not a global "
            "status update."
        ),
        "n": EXPECTED_N,
        "certificates_checked": len(raw_certificates),
        "unique_assignments_checked": len(seen_assignments),
        "incidence_filter_failures": 0,
        "self_edge_failures": 0,
        "certificate_sha256": digest,
        "digest_matches": True,
        "first_self_edge": first_self_edge,
    }


def summary_json_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Return the compact reviewer-facing JSON view without example records."""

    return {key: payload[key] for key in SUMMARY_JSON_KEYS if key in payload}


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--certificate", type=Path, default=DEFAULT_CERTIFICATE)
    parser.add_argument("--check", action="store_true", help="run the replay audit")
    parser.add_argument("--assert-expected", action="store_true")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--json", action="store_true")
    output_group.add_argument(
        "--summary-json",
        action="store_true",
        help="emit compact reviewer-facing JSON without example records",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entrypoint."""
    args = parse_args(argv)
    if not args.check:
        raise SystemExit("pass --check to replay the certificate")
    certificate = args.certificate
    if not certificate.is_absolute():
        certificate = ROOT / certificate
    summary = audit_certificate_payload(load_json(certificate))
    if args.assert_expected:
        expect_equal("status", summary["status"], "ok")
        expect_equal("certificates_checked", summary["certificates_checked"], EXPECTED_TERMINALS)
        expect_equal("unique_assignments_checked", summary["unique_assignments_checked"], EXPECTED_TERMINALS)
        expect_equal("digest_matches", summary["digest_matches"], True)
    if args.summary_json:
        print(json.dumps(summary_json_payload(summary), indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("independent n=9 Kalmanson self-edge certificate replay")
        print(f"status: {summary['status']}")
        print(f"certificates checked: {summary['certificates_checked']}")
        print(f"unique assignments checked: {summary['unique_assignments_checked']}")
        print(f"certificate sha256: {summary['certificate_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
