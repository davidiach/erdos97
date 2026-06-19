#!/usr/bin/env python3
"""Exact dual certificates for the 151:6 target-sparse full-cone misses.

This is a self-contained repo-overlay checker.  It certifies, by exact integer
arithmetic, that the three assignment-0 endpoint rows left open by
``bootstrap_t12_151_6_label4_target_sparse_full_cone_misses`` admit no
normalized zero-sum or coordinatewise-nonpositive certificate from the current
natural-order Kalmanson/Altman strict-row family.

Important scope: this is route-pruning evidence only.  It proves that the
current row family cannot certify those three local quotients.  It is not a
counterexample, not a proof that the quotients are geometrically realizable,
not a proof of n=9, and not a proof of Erdos #97.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable, Mapping, MutableMapping, Sequence

SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_full_cone_"
    "dual_certificates.v1"
)
STATUS = "EXACT_DUAL_INFEASIBILITY_CERTIFICATES_FOR_CURRENT_FULL_CONE_SCREENS"
TRUST = "EXACT_ROUTE_PRUNING_CERTIFICATE"
BASE_REPO_SHA = "8f331b5f234cb1c4bfcd0eb134fca0b2120056e8"
N = 9
ORDER = list(range(N))
STRICT_ROW_FAMILY = "kalmanson_all_quads_plus_altman_gaps_natural_order"
KALMANSON_KINDS = ("K1_diag_gt_sides", "K2_diag_gt_other")
SOURCE_MISS_ARTIFACT = (
    "data/certificates/"
    "bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.json"
)
SOURCE_MISS_SCHEMA = (
    "erdos97.bootstrap_t12_151_6_label4_target_sparse_full_cone_misses.v1"
)
SOURCE_MISS_STATUS = (
    "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_FULL_CONE_MISSES_"
    "DIAGNOSTIC_ONLY"
)
DEFAULT_ARTIFACT = Path(
    "data/certificates/"
    "bootstrap_t12_151_6_label4_target_sparse_full_cone_dual_certificates.json"
)

Pair = tuple[int, int]
Term = tuple[Pair, int]

EXPECTED_MISSES: tuple[dict[str, Any], ...] = (
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 1, 4, 6],
        "endpoint_row_key": "0,1,4,6",
    },
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 2, 4, 6],
        "endpoint_row_key": "0,2,4,6",
    },
    {
        "assignment_index": 0,
        "source_pair_row_index": 0,
        "source_core_index": 1,
        "row_center": 2,
        "row_witnesses": [0, 3, 4, 8],
        "endpoint_center": 8,
        "endpoint_row_witnesses": [0, 4, 6, 7],
        "endpoint_row_key": "0,4,6,7",
    },
)

# These are exact integer separating potentials in the deterministic distance
# quotient class order built below.  Omitted classes have weight 0.  They were
# found by solving the dual LP and then replayed exactly here; the checker does
# not trust floating-point output.
POTENTIALS_BY_ENDPOINT: Mapping[str, Mapping[int, int]] = {
    "0,1,4,6": {
        1: 6,
        2: 11,
        3: 9,
        4: 23,
        5: 11,
        6: 11,
        7: 1,
        9: 6,
        10: 5,
        11: 20,
        12: 9,
        13: 10,
        14: 22,
        15: 12,
        16: 14,
        18: 17,
        19: 8,
        20: 11,
        21: 4,
        22: 3,
        23: 7,
        24: 16,
        25: 14,
    },
    "0,2,4,6": {
        2: 10,
        3: 8,
        4: 22,
        5: 10,
        6: 11,
        8: 11,
        9: 10,
        10: 25,
        11: 14,
        12: 16,
        13: 6,
        14: 16,
        15: 6,
        16: 9,
        18: 17,
        19: 8,
        20: 12,
        21: 4,
        22: 2,
        23: 7,
        24: 16,
        25: 13,
    },
    "0,4,6,7": {
        1: 5,
        2: 10,
        3: 8,
        4: 22,
        5: 10,
        6: 11,
        9: 6,
        10: 5,
        11: 20,
        12: 9,
        13: 11,
        14: 1,
        15: 21,
        16: 11,
        17: 14,
        19: 17,
        20: 8,
        21: 12,
        22: 4,
        23: 2,
        24: 7,
        25: 16,
        26: 13,
    },
}


@dataclass(frozen=True)
class DistanceQuotient:
    n: int
    pair_class: Mapping[Pair, int]
    class_members: tuple[tuple[Pair, ...], ...]

    @property
    def class_count(self) -> int:
        return len(self.class_members)


@dataclass(frozen=True)
class StrictRow:
    source: str
    vector: tuple[int, ...]
    terms: tuple[Term, ...]
    metadata: Mapping[str, object]


class UnionFind:
    def __init__(self, items: Iterable[Pair]) -> None:
        self.parent = {item: item for item in items}

    def find(self, item: Pair) -> Pair:
        parent = self.parent[item]
        if parent != item:
            self.parent[item] = self.find(parent)
        return self.parent[item]

    def union(self, left: Pair, right: Pair) -> None:
        root_left = self.find(left)
        root_right = self.find(right)
        if root_left == root_right:
            return
        if root_right < root_left:
            root_left, root_right = root_right, root_left
        self.parent[root_right] = root_left


def pair(left: int, right: int) -> Pair:
    if left == right:
        raise ValueError(f"loop pair is not allowed: ({left}, {right})")
    return (left, right) if left < right else (right, left)


def centered_classes_for_miss(miss: Mapping[str, Any]) -> tuple[tuple[int, tuple[int, ...]], ...]:
    return (
        (int(miss["row_center"]), tuple(int(x) for x in miss["row_witnesses"])),
        # Cascade support equalities from the support-cone packet.
        (5, (4, 6)),
        (6, (0, 5)),
        (int(miss["endpoint_center"]), tuple(int(x) for x in miss["endpoint_row_witnesses"])),
    )


def distance_quotient(
    n: int,
    centered_classes: Sequence[tuple[int, Sequence[int]]],
) -> DistanceQuotient:
    all_pairs = [pair(left, right) for left, right in combinations(range(n), 2)]
    uf = UnionFind(all_pairs)
    for center, witnesses in centered_classes:
        validate_centered_class(n, center, witnesses)
        witness_list = [int(witness) for witness in witnesses]
        base = pair(int(center), witness_list[0])
        for witness in witness_list[1:]:
            uf.union(base, pair(int(center), witness))

    root_index: MutableMapping[Pair, int] = {}
    pair_class: dict[Pair, int] = {}
    members: dict[int, list[Pair]] = {}
    for item in all_pairs:
        root = uf.find(item)
        class_index = root_index.setdefault(root, len(root_index))
        pair_class[item] = class_index
        members.setdefault(class_index, []).append(item)
    return DistanceQuotient(
        n=n,
        pair_class=pair_class,
        class_members=tuple(tuple(members[idx]) for idx in range(len(members))),
    )


def validate_centered_class(n: int, center: int, witnesses: Sequence[int]) -> None:
    witness_list = [int(witness) for witness in witnesses]
    if not 0 <= int(center) < n:
        raise ValueError(f"center out of range: {center}")
    if len(witness_list) < 2:
        raise ValueError("centered class must contain at least two witnesses")
    if len(set(witness_list)) != len(witness_list):
        raise ValueError(f"duplicate witness in {witness_list!r}")
    if int(center) in witness_list:
        raise ValueError(f"center appears as witness: {center} in {witness_list!r}")
    if any(not 0 <= witness < n for witness in witness_list):
        raise ValueError(f"witness out of range in {witness_list!r}")


def vector_from_terms(quotient: DistanceQuotient, terms: Sequence[Term]) -> tuple[int, ...]:
    vector = [0] * quotient.class_count
    for raw_pair, coefficient in terms:
        vector[quotient.pair_class[pair(*raw_pair)]] += int(coefficient)
    return tuple(vector)


def kalmanson_terms(kind: str, quad: Sequence[int]) -> tuple[Term, ...]:
    if len(quad) != 4 or len(set(quad)) != 4:
        raise ValueError(f"Kalmanson row needs four distinct vertices, got {quad!r}")
    a, b, c, d = (int(label) for label in quad)
    if kind == "K1_diag_gt_sides":
        return (
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, b), -1),
            (pair(c, d), -1),
        )
    if kind == "K2_diag_gt_other":
        return (
            (pair(a, c), +1),
            (pair(b, d), +1),
            (pair(a, d), -1),
            (pair(b, c), -1),
        )
    raise ValueError(f"unknown Kalmanson kind: {kind}")


def kalmanson_row(quotient: DistanceQuotient, kind: str, quad: Sequence[int]) -> StrictRow:
    terms = kalmanson_terms(kind, quad)
    return StrictRow(
        source="kalmanson",
        vector=vector_from_terms(quotient, terms),
        terms=terms,
        metadata={"kind": kind, "quad": [int(label) for label in quad]},
    )


def altman_gap_row(quotient: DistanceQuotient, order: Sequence[int], gap_order: int) -> StrictRow:
    n = quotient.n
    if not 1 <= gap_order < n // 2:
        raise ValueError(f"gap_order must be in [1,{n // 2 - 1}], got {gap_order}")
    if sorted(order) != list(range(n)):
        raise ValueError(f"order is not a permutation of 0..{n-1}: {order!r}")
    terms: list[Term] = []
    for idx, source in enumerate(order):
        left_target = order[(idx + gap_order) % n]
        right_target = order[(idx + gap_order + 1) % n]
        terms.append((pair(source, right_target), +1))
        terms.append((pair(source, left_target), -1))
    return StrictRow(
        source="altman_gap",
        vector=vector_from_terms(quotient, terms),
        terms=tuple(terms),
        metadata={"gap_order": gap_order},
    )


def strict_rows(quotient: DistanceQuotient, order: Sequence[int]) -> list[StrictRow]:
    rows: list[StrictRow] = []
    for quad in combinations(order, 4):
        for kind in KALMANSON_KINDS:
            rows.append(kalmanson_row(quotient, kind, quad))
    for gap_order in range(1, quotient.n // 2):
        rows.append(altman_gap_row(quotient, order, gap_order))
    return rows


def potential_for_endpoint(endpoint_key: str, class_count: int) -> tuple[int, ...]:
    raw = POTENTIALS_BY_ENDPOINT[endpoint_key]
    if any(index < 0 or index >= class_count for index in raw):
        raise AssertionError(f"potential index out of range for {endpoint_key}")
    return tuple(int(raw.get(index, 0)) for index in range(class_count))


def dot(left: Sequence[int], right: Sequence[int]) -> int:
    return sum(int(a) * int(b) for a, b in zip(left, right, strict=True))


def strict_row_json(row: StrictRow, dot_value: int | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {"source": row.source}
    if row.source == "kalmanson":
        payload["kind"] = str(row.metadata["kind"])
        payload["quad"] = [int(x) for x in row.metadata["quad"]]  # type: ignore[index]
    elif row.source == "altman_gap":
        payload["gap_order"] = int(row.metadata["gap_order"])
    else:
        payload["metadata"] = dict(row.metadata)
    if dot_value is not None:
        payload["potential_dot"] = int(dot_value)
    return payload


def verify_one_miss(miss: Mapping[str, Any]) -> dict[str, Any]:
    endpoint_key = str(miss["endpoint_row_key"])
    centered_classes = centered_classes_for_miss(miss)
    quotient = distance_quotient(N, centered_classes)
    rows = strict_rows(quotient, ORDER)
    potential = potential_for_endpoint(endpoint_key, quotient.class_count)

    if quotient.class_count != 28:
        raise AssertionError(f"{endpoint_key}: expected 28 classes, got {quotient.class_count}")
    if len(rows) != 255:
        raise AssertionError(f"{endpoint_key}: expected 255 strict rows, got {len(rows)}")
    if any(value < 0 for value in potential):
        raise AssertionError(f"{endpoint_key}: potential has a negative coefficient")

    dot_values = [dot(potential, row.vector) for row in rows]
    min_dot = min(dot_values)
    if min_dot < 1:
        bad_rows = [
            strict_row_json(row, value)
            for row, value in zip(rows, dot_values, strict=True)
            if value < 1
        ]
        raise AssertionError(f"{endpoint_key}: potential is not separating: {bad_rows[:5]!r}")

    active_rows = [
        strict_row_json(row, value)
        for row, value in zip(rows, dot_values, strict=True)
        if value == min_dot
    ]
    class_records = [
        {
            "class_index": index,
            "members": [[a, b] for a, b in members],
            "potential_weight": int(potential[index]),
        }
        for index, members in enumerate(quotient.class_members)
    ]
    return {
        **{key: miss[key] for key in (
            "assignment_index",
            "source_pair_row_index",
            "source_core_index",
            "row_center",
            "row_witnesses",
            "endpoint_center",
            "endpoint_row_witnesses",
            "endpoint_row_key",
        )},
        "centered_classes": [
            {"center": center, "witnesses": list(witnesses)}
            for center, witnesses in centered_classes
        ],
        "distance_class_count": quotient.class_count,
        "strict_row_family": STRICT_ROW_FAMILY,
        "strict_row_count": len(rows),
        "dual_potential": {
            "coordinate_system": "selected-distance quotient class order",
            "nonnegative_integer_weights_by_distance_class": class_records,
            "weight_sum": int(sum(potential)),
            "nonzero_weight_count": int(sum(1 for value in potential if value != 0)),
            "max_weight": int(max(potential)),
        },
        "exact_separation_check": {
            "minimum_strict_row_dot": int(min_dot),
            "maximum_strict_row_dot": int(max(dot_values)),
            "active_strict_row_count": len(active_rows),
            "active_strict_rows": active_rows,
            "all_strict_rows_have_positive_dot": True,
            "all_potential_weights_nonnegative": True,
        },
        "certified_lp_screens": {
            "zero_sum_equalities_normalized": "infeasible_exactly_certified",
            "nonpositive_inequalities_normalized": "infeasible_exactly_certified",
        },
        "claim_strength": (
            "Exact dual route-pruning certificate for this encoded local quotient "
            "and fixed natural cyclic order: it proves the current Kalmanson/Altman "
            "strict-row family cannot produce either a normalized zero-sum or a "
            "coordinatewise-nonpositive cone certificate."
        ),
    }


def build_payload() -> dict[str, Any]:
    records = [verify_one_miss(miss) for miss in EXPECTED_MISSES]
    payload = {
        "schema": SCHEMA,
        "status": STATUS,
        "trust": TRUST,
        "base_repo_sha": BASE_REPO_SHA,
        "source_artifacts": [
            {
                "path": SOURCE_MISS_ARTIFACT,
                "role": "source full-cone miss identities and LP-screen target",
                "expected_source_status": (
                    "BOOTSTRAP_T12_151_6_LABEL4_TARGET_SPARSE_FULL_CONE_MISSES_"
                    "DIAGNOSTIC_ONLY"
                ),
            }
        ],
        "claim_scope": (
            "Exact integer dual certificates for the three source-151 row-6 "
            "label-4 assignment-0 endpoint rows left uncovered by the full-cone "
            "LP-screen diagnostic. The certificates prove infeasibility of the "
            "current normalized zero-sum and coordinatewise-nonpositive LP screens "
            "over the fixed natural-order Kalmanson/Altman row family. They are "
            "route-pruning evidence only: they do not prove the local quotients are "
            "geometrically realizable, do not prove assignments 0 or 11 are possible "
            "or impossible, do not prove support existence, center migration, row "
            "forcing, endpoint-8 forcing, n=9, the bootstrap bridge, or Erdos #97, "
            "and they are not a counterexample."
        ),
        "proof_lemma": {
            "statement": (
                "For each miss, let v_j be every reduced strict-row coefficient "
                "vector in the current family. The listed nonnegative integer "
                "potential c satisfies <c,v_j> >= 1 for all j. Hence no normalized "
                "nonnegative combination of the v_j can be zero or coordinatewise "
                "nonpositive."
            ),
            "proof": [
                "Assume weights lambda_j >= 0 with sum lambda_j = 1.",
                "If sum lambda_j v_j = 0, then pairing with c gives 0 on the left but at least sum lambda_j = 1 on the right, contradiction.",
                "If x = sum lambda_j v_j is coordinatewise nonpositive, then c >= 0 gives <c,x> <= 0, while the row-wise lower bound gives <c,x> >= 1, contradiction.",
                "All entries of c and v_j are integers and the checker verifies the inequalities by exact integer arithmetic.",
            ],
        },
        "summary": {
            "miss_count": len(records),
            "assignment_indices": sorted({record["assignment_index"] for record in records}),
            "endpoint_rows": [record["endpoint_row_witnesses"] for record in records],
            "strict_row_family": STRICT_ROW_FAMILY,
            "strict_row_count_each": sorted({record["strict_row_count"] for record in records}),
            "distance_class_count_each": sorted({record["distance_class_count"] for record in records}),
            "minimum_strict_row_dot_each": [
                record["exact_separation_check"]["minimum_strict_row_dot"]
                for record in records
            ],
            "maximum_strict_row_dot_each": [
                record["exact_separation_check"]["maximum_strict_row_dot"]
                for record in records
            ],
            "potential_weight_sum_each": [
                record["dual_potential"]["weight_sum"] for record in records
            ],
            "zero_sum_equalities_infeasible_exactly_certified_count": len(records),
            "nonpositive_inequalities_infeasible_exactly_certified_count": len(records),
            "current_evidence_forces_target_sparse_obstruction": False,
            "solves_n9": False,
            "solves_erdos97": False,
        },
        "dual_certificate_records": records,
        "validation_status": "passed",
        "validation_errors": [],
    }
    payload["payload_sha256"] = sha256_without_self_hash(payload)
    return payload


def sha256_without_self_hash(payload: Mapping[str, Any]) -> str:
    stripped = dict(payload)
    stripped.pop("payload_sha256", None)
    blob = json.dumps(stripped, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def validate_payload(
    payload: Mapping[str, Any],
    *,
    source_misses_path: Path = Path(SOURCE_MISS_ARTIFACT),
) -> list[str]:
    errors: list[str] = []
    generated = build_payload()
    if payload != generated:
        errors.append("stored payload differs from deterministic regeneration")
    if payload.get("payload_sha256") != sha256_without_self_hash(payload):
        errors.append("payload_sha256 mismatch")
    _validate_source_misses(source_misses_path, errors)
    return errors


def _validate_source_misses(source_misses_path: Path, errors: list[str]) -> None:
    path = resolve_repo_path(source_misses_path)
    try:
        source = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        errors.append(f"source miss artifact could not be read: {exc}")
        return
    if source.get("schema") != SOURCE_MISS_SCHEMA:
        errors.append("source miss artifact schema mismatch")
    if source.get("status") != SOURCE_MISS_STATUS:
        errors.append("source miss artifact status mismatch")
    summary = source.get("summary")
    if not isinstance(summary, Mapping):
        errors.append("source miss artifact summary must be an object")
    else:
        if summary.get("exact_infeasibility_certificates_stored") is not False:
            errors.append("source miss artifact exact-certificate flag changed")
        if summary.get("strict_row_count") != 255:
            errors.append("source miss artifact strict-row count changed")
    raw_records = source.get("full_cone_probe_records")
    if not isinstance(raw_records, list):
        errors.append("source miss artifact records must be a list")
        return
    source_identities = [
        {
            "assignment_index": int(record["assignment_index"]),
            "source_pair_row_index": int(record["source_pair_row_index"]),
            "source_core_index": int(record["source_core_index"]),
            "row_center": int(record["row_center"]),
            "row_witnesses": [int(item) for item in record["row_witnesses"]],
            "endpoint_center": int(record["endpoint_center"]),
            "endpoint_row_witnesses": [
                int(item) for item in record["endpoint_row_witnesses"]
            ],
            "endpoint_row_key": str(record["endpoint_row_key"]),
        }
        for record in raw_records
    ]
    if source_identities != list(EXPECTED_MISSES):
        errors.append("source miss artifact identities changed")


def write_json(payload: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    # If invoked from repo root, keep paths repo-relative. If invoked from the
    # overlay script directory, climb to the overlay/repo root.
    if Path.cwd().name == "scripts":
        return Path.cwd().parent / path
    return Path.cwd() / path


def compact_summary(payload: Mapping[str, Any], errors: Sequence[str]) -> dict[str, Any]:
    summary = payload.get("summary", {})
    return {
        "schema": payload.get("schema"),
        "status": payload.get("status"),
        "trust": payload.get("trust"),
        "ok": not errors,
        "miss_count": summary.get("miss_count") if isinstance(summary, Mapping) else None,
        "endpoint_rows": summary.get("endpoint_rows") if isinstance(summary, Mapping) else None,
        "strict_row_count_each": summary.get("strict_row_count_each") if isinstance(summary, Mapping) else None,
        "distance_class_count_each": summary.get("distance_class_count_each") if isinstance(summary, Mapping) else None,
        "minimum_strict_row_dot_each": summary.get("minimum_strict_row_dot_each") if isinstance(summary, Mapping) else None,
        "potential_weight_sum_each": summary.get("potential_weight_sum_each") if isinstance(summary, Mapping) else None,
        "solves_n9": summary.get("solves_n9") if isinstance(summary, Mapping) else None,
        "solves_erdos97": summary.get("solves_erdos97") if isinstance(summary, Mapping) else None,
        "validation_errors": list(errors),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--source-misses", type=Path, default=Path(SOURCE_MISS_ARTIFACT))
    parser.add_argument("--write", action="store_true", help="write deterministic JSON artifact")
    parser.add_argument("--check", action="store_true", help="compare stored artifact to regeneration")
    parser.add_argument("--json", action="store_true", help="print compact JSON summary")
    args = parser.parse_args()

    generated = build_payload()
    artifact = resolve_repo_path(args.artifact)
    payload: Mapping[str, Any] = generated
    if args.write:
        write_json(generated, artifact)
    if args.check:
        payload = json.loads(artifact.read_text(encoding="utf-8"))
    errors = validate_payload(payload, source_misses_path=args.source_misses)
    summary = compact_summary(payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print("bootstrap/T12 151:6 target-sparse full-cone dual certificates")
        print(f"misses certified: {summary['miss_count']}")
        print(f"endpoint rows: {summary['endpoint_rows']}")
        print(f"minimum strict-row dots: {summary['minimum_strict_row_dot_each']}")
        print(f"potential weight sums: {summary['potential_weight_sum_each']}")
        if errors:
            print("validation errors:")
            for error in errors:
                print(f"- {error}")
        else:
            print("OK: exact dual infeasibility certificates verified")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
