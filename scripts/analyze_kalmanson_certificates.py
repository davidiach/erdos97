#!/usr/bin/env python3
"""Analyze checked Kalmanson/Farkas certificate support structure.

This diagnostic is deliberately certificate-facing: it reuses the exact
Kalmanson checker, then summarizes the already-checked positive dependency.
It does not search all cyclic orders and does not strengthen any certificate
beyond its fixed selected-witness pattern and fixed cyclic order.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Mapping, Sequence

from check_kalmanson_certificate import (
    build_distance_classes,
    check_certificate_file,
    inequality_terms,
    row_witnesses,
)

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CERTIFICATES = (
    ROOT / "data" / "certificates" / "c13_sidon_order_survivor_kalmanson_unsat.json",
    ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_unsat.json",
)
DEFAULT_C19_LEGACY = (
    ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_unsat.json"
)
DEFAULT_C19_COMPACT = (
    ROOT / "data" / "certificates" / "round2" / "c19_kalmanson_known_order_two_unsat.json"
)
RANK_PRIMES = (1_000_003, 1_000_033, 1_000_037)


def _relative_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def _normalise_cycle(values: Sequence[int]) -> tuple[int, ...]:
    vals = tuple(int(value) for value in values)
    rotations = [vals[idx:] + vals[:idx] for idx in range(len(vals))]
    rev = tuple(reversed(vals))
    rotations.extend(rev[idx:] + rev[:idx] for idx in range(len(rev)))
    return min(rotations)


def _quad_gaps(order: Sequence[int], quad: Sequence[int]) -> tuple[int, ...]:
    pos = {label: idx for idx, label in enumerate(order)}
    positions = [pos[int(label)] for label in quad]
    n = len(order)
    return tuple(
        (positions[(idx + 1) % 4] - positions[idx]) % n
        for idx in range(4)
    )


def _modular_rank(rows: Sequence[Sequence[int]], prime: int) -> int:
    matrix = [[int(value) % prime for value in row] for row in rows]
    if not matrix:
        return 0
    row_count = len(matrix)
    col_count = len(matrix[0])
    rank = 0
    for col in range(col_count):
        pivot = None
        for row in range(rank, row_count):
            if matrix[row][col] % prime:
                pivot = row
                break
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        inv = pow(matrix[rank][col], -1, prime)
        matrix[rank] = [(value * inv) % prime for value in matrix[rank]]
        for row in range(row_count):
            if row == rank:
                continue
            factor = matrix[row][col] % prime
            if factor:
                matrix[row] = [
                    (value - factor * pivot_value) % prime
                    for value, pivot_value in zip(matrix[row], matrix[rank])
                ]
        rank += 1
        if rank == row_count:
            break
    return rank


def _weight_stats(weights: Sequence[int]) -> dict[str, int]:
    gcd = 0
    for weight in weights:
        gcd = math.gcd(gcd, abs(int(weight)))
    return {
        "min": min(weights),
        "max": max(weights),
        "sum": sum(weights),
        "distinct_count": len(set(weights)),
        "gcd": gcd,
    }


def _inequality_signature(item: Mapping[str, object]) -> tuple[str, tuple[int, ...]]:
    return (
        str(item["kind"]),
        tuple(int(label) for label in item["quad"]),  # type: ignore[index]
    )


def _compact_certificate_summary(path: Path) -> dict[str, object]:
    diagnostic = analyze_certificate(path, top=1)
    cert = json.loads(path.read_text(encoding="utf-8"))
    inequalities = cert["inequalities"]
    return {
        "path": diagnostic["path"],
        "pattern": diagnostic["pattern"],
        "n": diagnostic["n"],
        "status": diagnostic["status"],
        "claim_strength": diagnostic["claim_strength"],
        "cyclic_order": diagnostic["cyclic_order"],
        "circulant_offsets": diagnostic["circulant_offsets"],
        "positive_inequalities": diagnostic["positive_inequalities"],
        "distance_classes_after_selected_equalities": diagnostic[
            "distance_classes_after_selected_equalities"
        ],
        "distance_class_size_histogram": diagnostic["distance_class_size_histogram"],
        "zero_sum_verified": diagnostic["max_abs_weighted_sum_coefficient"] == 0,
        "max_abs_weighted_sum_coefficient": diagnostic[
            "max_abs_weighted_sum_coefficient"
        ],
        "weight_stats": diagnostic["weight_stats"],
        "kind_counts": diagnostic["kind_counts"],
        "kind_weight_sums": diagnostic["kind_weight_sums"],
        "support_rank_mod_primes": diagnostic["support_rank_mod_primes"],
        "support_nullity_mod_primes": diagnostic["support_nullity_mod_primes"],
        "support_signatures": [
            {
                "kind": kind,
                "quad": list(quad),
                "weight": int(item["weight"]),
            }
            for item in inequalities
            for kind, quad in [_inequality_signature(item)]
        ],
    }


def _class_sources(n: int, offsets: Sequence[int], classes: Mapping[tuple[int, int], int]) -> dict[int, set[int]]:
    sources: dict[int, set[int]] = defaultdict(set)
    for center in range(n):
        for witness in row_witnesses(n, offsets, center):
            p = (center, witness) if center < witness else (witness, center)
            sources[classes[p]].add(center)
    return sources


def analyze_certificate(path: Path, *, top: int = 12) -> dict[str, object]:
    checked = check_certificate_file(path)
    cert = json.loads(path.read_text(encoding="utf-8"))
    pattern = cert["pattern"]
    n = int(pattern["n"])
    offsets = [int(offset) for offset in pattern["circulant_offsets"]]
    order = [int(label) for label in cert["cyclic_order"]]
    inequalities = cert["inequalities"]
    classes = build_distance_classes(n, offsets)
    class_count = len(set(classes.values()))
    class_pairs: dict[int, list[tuple[int, int]]] = defaultdict(list)
    for p, class_id in classes.items():
        class_pairs[class_id].append(p)
    sources = _class_sources(n, offsets, classes)

    kind_counts: Counter[str] = Counter()
    kind_weight_sums: Counter[str] = Counter()
    gap_counts: Counter[tuple[str, tuple[int, ...]]] = Counter()
    gap_weight_sums: Counter[tuple[str, tuple[int, ...]]] = Counter()
    label_counts: Counter[int] = Counter()
    label_weight_sums: Counter[int] = Counter()
    class_balance: dict[int, dict[str, int]] = {
        class_id: {
            "positive_weight": 0,
            "negative_weight": 0,
            "signed_total": 0,
            "term_count": 0,
        }
        for class_id in range(class_count)
    }
    row_vectors: list[list[int]] = []

    for item in inequalities:
        kind = str(item["kind"])
        quad = [int(label) for label in item["quad"]]
        weight = int(item["weight"])
        kind_counts[kind] += 1
        kind_weight_sums[kind] += weight
        gaps = _normalise_cycle(_quad_gaps(order, quad))
        gap_counts[(kind, gaps)] += 1
        gap_weight_sums[(kind, gaps)] += weight
        for label in quad:
            label_counts[label] += 1
            label_weight_sums[label] += weight

        vector = [0] * class_count
        for p, coefficient in inequality_terms(kind, quad):
            class_id = classes[p]
            vector[class_id] += coefficient
            signed = coefficient * weight
            if signed > 0:
                class_balance[class_id]["positive_weight"] += signed
            elif signed < 0:
                class_balance[class_id]["negative_weight"] += -signed
            class_balance[class_id]["signed_total"] += signed
            class_balance[class_id]["term_count"] += 1
        row_vectors.append(vector)

    weighted_totals = {
        class_id: values["signed_total"]
        for class_id, values in class_balance.items()
        if values["signed_total"] != 0
    }
    rank_by_prime = {
        str(prime): _modular_rank(row_vectors, prime)
        for prime in RANK_PRIMES
    }
    support_count = len(row_vectors)
    nullity_by_prime = {
        prime: support_count - rank
        for prime, rank in rank_by_prime.items()
    }
    class_size_histogram = Counter(len(pairs) for pairs in class_pairs.values())

    top_gap_patterns = [
        {
            "kind": kind,
            "normalized_cyclic_gaps": list(gaps),
            "count": gap_counts[(kind, gaps)],
            "weight_sum": gap_weight_sums[(kind, gaps)],
        }
        for kind, gaps in sorted(
            gap_counts,
            key=lambda key: (-gap_counts[key], -gap_weight_sums[key], key[0], key[1]),
        )[:top]
    ]
    top_cancellations = []
    for class_id, values in sorted(
        class_balance.items(),
        key=lambda item: (
            -(item[1]["positive_weight"] + item[1]["negative_weight"]),
            item[0],
        ),
    )[:top]:
        pairs = sorted(class_pairs[class_id])
        top_cancellations.append(
            {
                "class_id": class_id,
                "pair_count": len(pairs),
                "representative_pairs": [list(pair) for pair in pairs[:8]],
                "representative_pairs_truncated": len(pairs) > 8,
                "selected_centers": sorted(sources[class_id]),
                "positive_weight": values["positive_weight"],
                "negative_weight": values["negative_weight"],
                "signed_total": values["signed_total"],
                "term_count": values["term_count"],
            }
        )

    return {
        "path": _relative_path(path),
        "pattern": checked.pattern,
        "n": checked.n,
        "status": checked.status,
        "claim_strength": checked.claim_strength,
        "cyclic_order": order,
        "circulant_offsets": offsets,
        "positive_inequalities": checked.positive_inequalities,
        "distance_classes_after_selected_equalities": (
            checked.distance_classes_after_selected_equalities
        ),
        "kind_counts": dict(sorted(kind_counts.items())),
        "kind_weight_sums": dict(sorted(kind_weight_sums.items())),
        "weight_stats": _weight_stats([int(item["weight"]) for item in inequalities]),
        "support_rank_mod_primes": rank_by_prime,
        "support_nullity_mod_primes": nullity_by_prime,
        "distance_class_size_histogram": {
            str(size): count for size, count in sorted(class_size_histogram.items())
        },
        "max_abs_weighted_sum_coefficient": (
            max((abs(value) for value in weighted_totals.values()), default=0)
        ),
        "nonzero_weighted_sum_class_count": len(weighted_totals),
        "top_gap_patterns_by_count": top_gap_patterns,
        "label_frequencies": [
            {
                "label": label,
                "count": label_counts[label],
                "weight_sum": label_weight_sums[label],
            }
            for label in range(n)
        ],
        "top_distance_class_cancellations": top_cancellations,
        "interpretation_note": (
            "This is a structural diagnostic for one checked fixed-order "
            "Kalmanson/Farkas certificate. Rank/nullity and cancellation "
            "summaries do not imply an abstract all-order obstruction."
        ),
    }


def payload(paths: Sequence[Path], *, top: int) -> dict[str, object]:
    return {
        "type": "kalmanson_certificate_diagnostics_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Each entry first verifies an existing fixed-order Kalmanson/Farkas certificate exactly.",
            "These diagnostics summarize certificate support; they are not all-order cyclic-order searches.",
        ],
        "certificates": [analyze_certificate(path, top=top) for path in paths],
    }


def c19_compact_vs_legacy_payload(
    *,
    legacy: Path = DEFAULT_C19_LEGACY,
    compact: Path = DEFAULT_C19_COMPACT,
) -> dict[str, object]:
    legacy_summary = _compact_certificate_summary(legacy)
    compact_summary = _compact_certificate_summary(compact)
    legacy_cert = json.loads(legacy.read_text(encoding="utf-8"))
    compact_cert = json.loads(compact.read_text(encoding="utf-8"))
    legacy_support = {
        _inequality_signature(item): int(item["weight"])
        for item in legacy_cert["inequalities"]
    }
    compact_support = {
        _inequality_signature(item): int(item["weight"])
        for item in compact_cert["inequalities"]
    }
    common_support = sorted(set(legacy_support) & set(compact_support))

    return {
        "type": "c19_kalmanson_compact_vs_legacy_diagnostic_v1",
        "trust": "EXACT_CERTIFICATE_DIAGNOSTIC",
        "status": "FIXED_ORDER_CERTIFICATE_COMPARISON_ONLY",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "Both inputs are checked fixed-order C19_skew Kalmanson/Farkas certificates.",
            "This report compares support shape only; it does not derive the compact certificate from the legacy certificate.",
            "The all-order C19_skew Z3 certificate is a separate artifact and is not replayed here.",
        ],
        "legacy": legacy_summary,
        "compact": compact_summary,
        "comparison": {
            "same_pattern": legacy_summary["pattern"] == compact_summary["pattern"],
            "same_cyclic_order": legacy_summary["cyclic_order"] == compact_summary["cyclic_order"],
            "same_status": legacy_summary["status"] == compact_summary["status"],
            "same_distance_class_count": (
                legacy_summary["distance_classes_after_selected_equalities"]
                == compact_summary["distance_classes_after_selected_equalities"]
            ),
            "legacy_inequality_count": legacy_summary["positive_inequalities"],
            "compact_inequality_count": compact_summary["positive_inequalities"],
            "legacy_weight_sum": legacy_summary["weight_stats"]["sum"],  # type: ignore[index]
            "compact_weight_sum": compact_summary["weight_stats"]["sum"],  # type: ignore[index]
            "legacy_max_weight": legacy_summary["weight_stats"]["max"],  # type: ignore[index]
            "compact_max_weight": compact_summary["weight_stats"]["max"],  # type: ignore[index]
            "support_signature_overlap_count": len(common_support),
            "compact_support_subset_of_legacy": set(compact_support).issubset(
                set(legacy_support)
            ),
            "common_support_signatures": [
                {"kind": kind, "quad": list(quad)}
                for kind, quad in common_support
            ],
        },
        "interpretation_note": (
            "The compact two-inequality certificate and the legacy 94-inequality "
            "certificate obstruct the same fixed C19_skew cyclic order after the "
            "same selected-distance quotienting. Their supports are not literally "
            "nested, so this report should not be read as a derivation of one "
            "certificate from the other."
        ),
    }


def assert_expected(data: Mapping[str, object]) -> None:
    certs = data["certificates"]
    if not isinstance(certs, list):
        raise AssertionError("certificates must be a list")
    by_pattern = {str(cert["pattern"]): cert for cert in certs}
    expected = {
        "C13_sidon_1_2_4_10": (34, 39),
        "C19_skew": (94, 114),
    }
    missing = sorted(set(expected) - set(by_pattern))
    if missing:
        raise AssertionError(f"missing expected diagnostic(s): {', '.join(missing)}")
    for pattern, (inequality_count, class_count) in expected.items():
        cert = by_pattern[pattern]
        if cert["positive_inequalities"] != inequality_count:
            raise AssertionError(f"{pattern} inequality count changed")
        if cert["distance_classes_after_selected_equalities"] != class_count:
            raise AssertionError(f"{pattern} distance class count changed")
        if cert["max_abs_weighted_sum_coefficient"] != 0:
            raise AssertionError(f"{pattern} weighted coefficient sum is nonzero")
        nullities = cert["support_nullity_mod_primes"]
        if not isinstance(nullities, dict) or set(nullities.values()) != {1}:
            raise AssertionError(f"{pattern} support nullity is not 1 over checked primes")


def assert_c19_compact_vs_legacy_expected(data: Mapping[str, object]) -> None:
    if data.get("type") != "c19_kalmanson_compact_vs_legacy_diagnostic_v1":
        raise AssertionError("unexpected C19 compact-vs-legacy report type")
    expected_c19_summary = {
        "pattern": "C19_skew",
        "n": 19,
        "circulant_offsets": [-8, -3, 5, 9],
        "cyclic_order": [
            18,
            10,
            7,
            17,
            6,
            3,
            5,
            9,
            14,
            11,
            2,
            13,
            4,
            16,
            12,
            15,
            0,
            8,
            1,
        ],
    }
    for label in ("legacy", "compact"):
        summary = data[label]
        if not isinstance(summary, Mapping):
            raise AssertionError(f"{label} summary must be an object")
        for key, expected_value in expected_c19_summary.items():
            if summary.get(key) != expected_value:
                raise AssertionError(
                    f"{label}[{key!r}] is {summary.get(key)!r}, expected {expected_value!r}"
                )
    comparison = data["comparison"]
    if not isinstance(comparison, Mapping):
        raise AssertionError("comparison must be an object")
    expected = {
        "same_pattern": True,
        "same_cyclic_order": True,
        "same_status": True,
        "same_distance_class_count": True,
        "legacy_inequality_count": 94,
        "compact_inequality_count": 2,
        "legacy_weight_sum": 6_283_316_065,
        "compact_weight_sum": 2,
        "legacy_max_weight": 334_665_404,
        "compact_max_weight": 1,
        "support_signature_overlap_count": 0,
        "compact_support_subset_of_legacy": False,
    }
    for key, expected_value in expected.items():
        if comparison.get(key) != expected_value:
            raise AssertionError(
                f"comparison[{key!r}] is {comparison.get(key)!r}, expected {expected_value!r}"
            )


def print_table(data: Mapping[str, object]) -> None:
    certs = data["certificates"]
    if not isinstance(certs, list):
        raise TypeError("certificates must be a list")
    headers = ["pattern", "n", "ineq", "classes", "max_weight", "nullity"]
    rows = []
    for cert in certs:
        if not isinstance(cert, Mapping):
            raise TypeError("certificate entry must be an object")
        nullities = cert["support_nullity_mod_primes"]
        if not isinstance(nullities, Mapping):
            raise TypeError("nullity field must be an object")
        rows.append(
            [
                str(cert["pattern"]),
                str(cert["n"]),
                str(cert["positive_inequalities"]),
                str(cert["distance_classes_after_selected_equalities"]),
                str(cert["weight_stats"]["max"]),  # type: ignore[index]
                ",".join(str(value) for value in nullities.values()),
            ]
        )
    widths = [
        max(len(headers[col]), *(len(row[col]) for row in rows))
        for col in range(len(headers))
    ]
    print("  ".join(headers[col].ljust(widths[col]) for col in range(len(headers))))
    print("  ".join("-" * widths[col] for col in range(len(headers))))
    for row in rows:
        print("  ".join(row[col].ljust(widths[col]) for col in range(len(headers))))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificates",
        nargs="*",
        type=Path,
        help="Kalmanson certificate JSON paths. Defaults to the registered C13 and C19 fixed-order certificates.",
    )
    parser.add_argument("--top", type=int, default=12, help="number of top diagnostic rows to retain")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument("--assert-expected", action="store_true")
    parser.add_argument(
        "--c19-compact-vs-legacy",
        action="store_true",
        help="emit the C19 compact two-inequality vs legacy 94-inequality diagnostic",
    )
    args = parser.parse_args()

    if args.top <= 0:
        raise SystemExit("--top must be positive")
    if args.c19_compact_vs_legacy:
        if args.certificates:
            raise SystemExit("--c19-compact-vs-legacy does not accept positional certificates")
        data = c19_compact_vs_legacy_payload()
        if args.assert_expected:
            assert_c19_compact_vs_legacy_expected(data)
    else:
        paths = tuple(args.certificates) if args.certificates else DEFAULT_CERTIFICATES
        data = payload(paths, top=args.top)
        if args.assert_expected:
            assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    elif args.c19_compact_vs_legacy:
        comparison = data["comparison"]  # type: ignore[index]
        print("C19 compact-vs-legacy fixed-order certificate diagnostic")
        print(f"legacy inequalities: {comparison['legacy_inequality_count']}")  # type: ignore[index]
        print(f"compact inequalities: {comparison['compact_inequality_count']}")  # type: ignore[index]
        print(f"support overlap: {comparison['support_signature_overlap_count']}")  # type: ignore[index]
        if args.assert_expected:
            print("OK: C19 compact-vs-legacy diagnostic matches expected values")
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: Kalmanson certificate diagnostics match expected fixed-order certificates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
