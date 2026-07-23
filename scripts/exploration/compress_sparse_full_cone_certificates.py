#!/usr/bin/env python3
"""Search smaller exact circuits for sparse-frontier full-cone clauses.

The source CEGAR certificates are already positive circuits, so deleting a row
from one stored support cannot preserve its dependency.  This bounded search
instead changes the LP objective to sample alternative extreme positive
dependencies over all fixed-order Kalmanson rows, exactifies every improving
support, and keeps the smallest exact ordered-quadrilateral clause found.

Randomized objective sampling is not exhaustive.  Exactified output
certificates are fixed-pattern, fixed-order obstructions only.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np
from scipy.optimize import linprog


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "scripts"
EXPLORATION = Path(__file__).resolve().parent
for path in (SCRIPTS, EXPLORATION):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from check_kalmanson_certificate import (  # noqa: E402
    build_distance_classes,
    check_certificate_dict,
    inequality_terms,
)
from find_kalmanson_certificate import exact_positive_weights  # noqa: E402
from kalmanson_order_utils import (  # noqa: E402
    InequalityRow,
    all_kalmanson_rows,
    certificate_payload,
)
from pilot_sparse_full_cone_order_cegar import (  # noqa: E402
    PATTERNS,
    certificate_order_quads,
)


DEFAULT_SOURCE = ROOT / "data" / "runs" / "sparse_full_cone_cegar_2026-07-22" / "summary.json"


def random_lp_support(
    rows: Sequence[InequalityRow],
    equality_matrix: np.ndarray,
    equality_rhs: np.ndarray,
    *,
    seed: int,
    tolerance: float,
) -> list[int] | None:
    rng = np.random.default_rng(seed)
    result = linprog(
        rng.random(len(rows)),
        A_eq=equality_matrix,
        b_eq=equality_rhs,
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        return None
    return [index for index, weight in enumerate(result.x) if weight > tolerance]


def exact_certificate_for_support(
    name: str,
    n: int,
    offsets: Sequence[int],
    order: Sequence[int],
    rows: Sequence[InequalityRow],
    support: Sequence[int],
) -> dict[str, object] | None:
    weights = exact_positive_weights(rows, support)
    if weights is None:
        return None
    certificate = certificate_payload(name, n, offsets, order, rows, support, weights)
    checked = check_certificate_dict(certificate)
    if not checked.zero_sum_verified:
        raise AssertionError("exactified compressed certificate did not verify")
    return certificate


def order_satisfies_quads(
    order: Sequence[int], quads: Sequence[tuple[int, int, int, int]]
) -> bool:
    positions = {int(label): index for index, label in enumerate(order)}
    return all(
        positions[a] < positions[b] < positions[c] < positions[d]
        for a, b, c, d in quads
    )


def modular_rank(rows: Sequence[Sequence[int]], prime: int = 1_000_000_007) -> int:
    """Return matrix row rank over a prime field."""

    basis: dict[int, list[int]] = {}
    for raw_row in rows:
        row = [int(value) % prime for value in raw_row]
        while True:
            pivot = next((index for index, value in enumerate(row) if value), None)
            if pivot is None:
                break
            existing = basis.get(pivot)
            if existing is not None:
                factor = row[pivot]
                row = [
                    (value - factor * base_value) % prime
                    for value, base_value in zip(row, existing)
                ]
                continue
            inverse = pow(row[pivot], prime - 2, prime)
            basis[pivot] = [(value * inverse) % prime for value in row]
            break
    return len(basis)


def positive_circuit_audit(certificate: Mapping[str, Any]) -> dict[str, object]:
    """Certify nullity one using an exact zero sum plus modular rank."""

    pattern = certificate["pattern"]
    n = int(pattern["n"])
    offsets = [int(value) for value in pattern["circulant_offsets"]]
    classes = build_distance_classes(n, offsets)
    class_count = len(set(classes.values()))
    columns = []
    weights = []
    for inequality in certificate["inequalities"]:
        vector = [0] * class_count
        for pair, coefficient in inequality_terms(
            str(inequality["kind"]), inequality["quad"]
        ):
            vector[classes[pair]] += coefficient
        columns.append(vector)
        weights.append(int(inequality["weight"]))
    support_size = len(columns)
    rank = modular_rank(columns)
    positive_weights = all(weight > 0 for weight in weights)
    verified = bool(positive_weights and rank == support_size - 1)
    return {
        "support_size": support_size,
        "rank_mod_1000000007": rank,
        "exact_zero_sum_gives_nullity_at_least": 1,
        "modular_rank_gives_rational_rank_at_least": rank,
        "all_weights_positive": positive_weights,
        "positive_circuit_verified": verified,
    }


def compress_model(
    name: str,
    n: int,
    offsets: Sequence[int],
    model: Mapping[str, Any],
    *,
    trials: int,
    seed: int,
    tolerance: float,
) -> dict[str, object]:
    order = [int(label) for label in model["order"]]
    source_full = model["full_kalmanson"]
    source_certificate = source_full.get("certificate")
    if not isinstance(source_certificate, Mapping):
        raise AssertionError("compression source model lacks an exact certificate")
    source_quads = certificate_order_quads(source_certificate, order)
    source_support_size = int(source_full["positive_inequalities"])

    rows = all_kalmanson_rows(n, offsets, order)
    matrix = np.asarray([row.vector for row in rows], dtype=float)
    equality_matrix = np.vstack([matrix.T, np.ones((1, len(rows)))])
    equality_rhs = np.zeros(matrix.shape[1] + 1)
    equality_rhs[-1] = 1.0

    best_certificate = dict(source_certificate)
    best_quads = source_quads
    best_trial: int | None = None
    numerical_sizes = []
    exact_improvements = []
    for trial in range(trials):
        trial_seed = seed + trial
        support = random_lp_support(
            rows,
            equality_matrix,
            equality_rhs,
            seed=trial_seed,
            tolerance=tolerance,
        )
        if support is None:
            continue
        numerical_sizes.append(len(support))
        candidate_quad_count = len({rows[index].quad for index in support})
        if candidate_quad_count >= len(best_quads):
            continue
        certificate = exact_certificate_for_support(
            name,
            n,
            offsets,
            order,
            rows,
            support,
        )
        if certificate is None:
            continue
        quads = certificate_order_quads(certificate, order)
        if len(quads) >= len(best_quads):
            continue
        best_certificate = certificate
        best_quads = quads
        best_trial = trial
        exact_improvements.append(
            {
                "trial": trial,
                "seed": trial_seed,
                "positive_inequalities": len(support),
                "unique_ordered_quad_count": len(quads),
            }
        )

    histogram = Counter(numerical_sizes)
    checked = check_certificate_dict(best_certificate)
    circuit_audit = positive_circuit_audit(best_certificate)
    if not circuit_audit["positive_circuit_verified"]:
        raise AssertionError("compressed support did not verify as a positive circuit")
    return {
        "source_model_index": int(model["model_index"]),
        "order": order,
        "source_positive_inequalities": source_support_size,
        "source_unique_ordered_quad_count": len(source_quads),
        "trial_count": trials,
        "successful_numerical_trials": len(numerical_sizes),
        "numerical_support_size_min": min(numerical_sizes) if numerical_sizes else None,
        "numerical_support_size_max": max(numerical_sizes) if numerical_sizes else None,
        "numerical_support_size_histogram": {
            str(size): histogram[size] for size in sorted(histogram)
        },
        "exact_improvements": exact_improvements,
        "best_trial": best_trial,
        "compressed_positive_inequalities": checked.positive_inequalities,
        "compressed_unique_ordered_quad_count": len(best_quads),
        "quad_reduction": len(source_quads) - len(best_quads),
        "quad_reduction_fraction": (
            (len(source_quads) - len(best_quads)) / len(source_quads)
        ),
        "support_is_exact_positive_circuit": circuit_audit["positive_circuit_verified"],
        "positive_circuit_audit": circuit_audit,
        "compressed_certificate": best_certificate,
    }


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    source_path = args.source if args.source.is_absolute() else ROOT / args.source
    source = json.loads(source_path.read_text(encoding="utf-8"))
    compressed_runs = []
    for run in source["runs"]:
        name = str(run["pattern"])
        n, offsets = PATTERNS[name]
        strong_models = [
            model
            for model in run["models"]
            if bool(model["lightweight_filters"]["survives"])
        ]
        compressed = [
            compress_model(
                name,
                n,
                offsets,
                model,
                trials=args.trials,
                seed=args.seed,
                tolerance=args.tolerance,
            )
            for model in strong_models
        ]
        coverage = []
        for row in compressed:
            certificate = row["compressed_certificate"]
            quads = certificate_order_quads(certificate, row["order"])
            covered = [
                int(target["model_index"])
                for target in strong_models
                if order_satisfies_quads(target["order"], quads)
            ]
            coverage.append(
                {
                    "source_model_index": row["source_model_index"],
                    "covered_strong_model_indices": covered,
                }
            )
        compressed_runs.append(
            {
                "pattern": name,
                "n": n,
                "circulant_offsets": offsets,
                "strong_source_model_count": len(strong_models),
                "compressed_models": compressed,
                "compressed_clause_coverage": coverage,
            }
        )

    return {
        "type": "sparse_full_cone_clause_compression_v1",
        "trust": "EXACT_COMPRESSED_CERTIFICATES_IN_BOUNDED_RANDOMIZED_SEARCH",
        "status": "BOUNDED_CLAUSE_COMPRESSION_DIAGNOSTIC",
        "claim_scope": (
            "Randomized alternative-circuit search for fixed C25/C29 patterns and "
            "fixed cyclic orders. Every retained certificate is exact, but the search "
            "is not exhaustive and does not prove an all-order obstruction, geometric "
            "realizability, a counterexample, or Erdos Problem #97."
        ),
        "source_artifact": source_path.relative_to(ROOT).as_posix(),
        "configuration": {
            "trials": args.trials,
            "seed": args.seed,
            "tolerance": args.tolerance,
            "selection": "models surviving vertex-circle and Altman filters",
        },
        "runs": compressed_runs,
    }


def check_payload(payload: Mapping[str, Any]) -> dict[str, object]:
    verified = 0
    for run in payload.get("runs", []):
        for row in run.get("compressed_models", []):
            certificate = row["compressed_certificate"]
            checked = check_certificate_dict(certificate)
            if not checked.zero_sum_verified:
                raise AssertionError("compressed certificate did not verify")
            quads = certificate_order_quads(certificate, row["order"])
            if len(quads) != int(row["compressed_unique_ordered_quad_count"]):
                raise AssertionError("compressed ordered-quad count drifted")
            expected_reduction = int(row["source_unique_ordered_quad_count"]) - len(quads)
            if expected_reduction != int(row["quad_reduction"]):
                raise AssertionError("compressed quad reduction drifted")
            circuit_audit = positive_circuit_audit(certificate)
            if not circuit_audit["positive_circuit_verified"]:
                raise AssertionError("compressed support is not a positive circuit")
            if circuit_audit != row["positive_circuit_audit"]:
                raise AssertionError("compressed positive-circuit audit drifted")
            verified += 1

        by_index = {
            int(row["source_model_index"]): row
            for row in run.get("compressed_models", [])
        }
        for coverage in run.get("compressed_clause_coverage", []):
            source_index = int(coverage["source_model_index"])
            row = by_index[source_index]
            quads = certificate_order_quads(
                row["compressed_certificate"], row["order"]
            )
            observed = sorted(
                target_index
                for target_index, target in by_index.items()
                if order_satisfies_quads(target["order"], quads)
            )
            expected = sorted(int(value) for value in coverage["covered_strong_model_indices"])
            if observed != expected:
                raise AssertionError("compressed clause coverage drifted")
    return {"status": "OK", "verified_compressed_exact_certificates": verified}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--trials", type=int, default=24)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--tolerance", type=float, default=1.0e-9)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--check", type=Path)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.trials <= 0 or args.tolerance <= 0:
        raise SystemExit("trials and tolerance must be positive")
    if args.check is not None:
        payload = json.loads(args.check.read_text(encoding="utf-8"))
        print(json.dumps(check_payload(payload), indent=2, sort_keys=True))
        return 0
    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8", newline="\n")
    if args.json or args.out is None:
        print(text, end="")
    else:
        for run in payload["runs"]:
            sizes = [
                f"{row['source_unique_ordered_quad_count']}->{row['compressed_unique_ordered_quad_count']}"
                for row in run["compressed_models"]
            ]
            print(f"{run['pattern']}: {', '.join(sizes)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
