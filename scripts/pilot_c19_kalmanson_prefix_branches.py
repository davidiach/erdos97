#!/usr/bin/env python3
"""Bounded C19 prefix-forced Kalmanson branch pilot.

This script samples the first deterministic reflection-pruned three-boundary
prefixes for the fixed selected-witness pattern `C19_skew`.  For each sampled
prefix, it keeps only Kalmanson inequalities whose cyclic order is forced by
the prefix and searches for an exact positive-integer Farkas certificate.

The output is not an all-order C19 search.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, Mapping, MutableMapping, NamedTuple, Sequence

from check_kalmanson_certificate import build_distance_classes, inequality_terms
from find_kalmanson_certificate import (
    KINDS,
    InequalityRow,
    exact_positive_weights,
    lp_support,
)

PATTERN_NAME = "C19_skew"
N = 19
OFFSETS = [-8, -3, 5, 9]
DEFAULT_BOUNDARY_PAIRS = 3
DEFAULT_MAX_BRANCHES = 128
DEFAULT_CLOSED_EXAMPLE_COUNT = 12
MAX_BOUNDARY_PAIRS = 4


class PrefixBranchCheckResult(NamedTuple):
    label: str
    status: str
    positive_inequalities: int
    forced_inequalities_available: int
    distance_classes_after_selected_equalities: int
    weight_sum: int
    max_weight: int
    zero_sum_verified: bool
    claim_strength: str


@dataclass(frozen=True)
class BoundaryState:
    left: tuple[int, ...]
    right: tuple[int, ...]
    remaining: tuple[int, ...]


def branch_label(index: int) -> str:
    return f"c19_prefix_branch_{index:04d}"


def label_digest(labels: Sequence[str]) -> str:
    payload = "".join(f"{label}\n" for label in labels)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def reflection_prefix_compare(left: Sequence[int], right: Sequence[int]) -> int:
    for a, b in zip(left, right):
        if a < b:
            return -1
        if a > b:
            return 1
    return 0


def count_boundary_states(boundary_pairs: int) -> tuple[int, int]:
    raw = math.perm(N - 1, 2 * boundary_pairs)
    return raw, raw // 2


def iter_boundary_states(boundary_pairs: int) -> Iterator[BoundaryState]:
    if boundary_pairs < 1:
        raise ValueError("boundary_pairs must be positive")
    if boundary_pairs > MAX_BOUNDARY_PAIRS:
        raise ValueError(f"boundary_pairs is capped at {MAX_BOUNDARY_PAIRS}")
    if 2 * boundary_pairs > N - 1:
        raise ValueError("boundary_pairs uses more labels than available")

    labels = tuple(range(1, N))

    def dfs(
        left: tuple[int, ...],
        right: tuple[int, ...],
        remaining: tuple[int, ...],
    ) -> Iterator[BoundaryState]:
        if len(left) == boundary_pairs:
            yield BoundaryState(left=left, right=right, remaining=remaining)
            return

        for left_label in remaining:
            after_left = tuple(label for label in remaining if label != left_label)
            for right_label in after_left:
                new_left = left + (left_label,)
                new_right = right + (right_label,)
                if reflection_prefix_compare(new_left, new_right) > 0:
                    continue
                new_remaining = tuple(label for label in after_left if label != right_label)
                yield from dfs(new_left, new_right, new_remaining)

    yield from dfs((), (), labels)


def state_from_boundary(left: Sequence[int], right: Sequence[int]) -> BoundaryState:
    left_tuple = tuple(int(v) for v in left)
    right_tuple = tuple(int(v) for v in right)
    used = set(left_tuple) | set(right_tuple)
    if len(used) != len(left_tuple) + len(right_tuple):
        raise ValueError("boundary labels must be distinct")
    if 0 in used:
        raise ValueError("boundary labels must not include anchor 0")
    if any(label < 1 or label >= N for label in used):
        raise ValueError("boundary labels outside 1..18")
    remaining = tuple(label for label in range(1, N) if label not in used)
    return BoundaryState(left=left_tuple, right=right_tuple, remaining=remaining)


def forced_order_quad(state: BoundaryState, labels: Sequence[int]) -> tuple[int, int, int, int] | None:
    if len(labels) != 4 or len(set(labels)) != 4:
        raise ValueError(f"bad quadrilateral labels: {labels!r}")
    unknown_count = sum(1 for label in labels if label in state.remaining)
    if unknown_count > 1:
        return None

    def key(label: int) -> tuple[int, int]:
        if label == 0:
            return (0, 0)
        if label in state.left:
            return (1, state.left.index(label))
        if label in state.remaining:
            return (2, 0)
        if label in state.right:
            return (3, len(state.right) - 1 - state.right.index(label))
        raise ValueError(f"label outside branch state: {label}")

    ordered = tuple(sorted((int(label) for label in labels), key=key))
    return ordered  # type: ignore[return-value]


def prefix_kalmanson_rows(
    state: BoundaryState,
    classes: Mapping[tuple[int, int], int],
) -> list[InequalityRow]:
    class_count = len(set(classes.values()))
    rows: list[InequalityRow] = []
    for labels in itertools.combinations(range(N), 4):
        quad = forced_order_quad(state, labels)
        if quad is None:
            continue
        for kind in KINDS:
            vector = [0] * class_count
            for pair, coeff in inequality_terms(kind, quad):
                vector[classes[pair]] += coeff
            rows.append(InequalityRow(kind, quad, tuple(vector)))
    return rows


def certificate_payload(
    *,
    label: str,
    state: BoundaryState,
    rows: Sequence[InequalityRow],
    support: Sequence[int],
    weights: Sequence[int],
) -> dict[str, object]:
    inequalities = [
        {
            "weight": int(weight),
            "quad": list(rows[idx].quad),
            "kind": rows[idx].kind,
        }
        for idx, weight in zip(support, weights)
    ]
    return {
        "certificate_type": "kalmanson_prefix_forced_farkas",
        "status": "EXACT_OBSTRUCTION_FOR_PREFIX_BRANCH_COMPLETIONS",
        "label": label,
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "boundary_prefix": {
            "anchor_label": 0,
            "left": list(state.left),
            "right_reflection_side": list(state.right),
            "middle_labels_unordered": list(state.remaining),
        },
        "selected_witness_rule": "S_i={(i+d) mod n: d in circulant_offsets}",
        "forced_order_model": (
            "orders start with 0,left..., end with reversed(right), and put "
            "all middle labels between those fixed boundary blocks"
        ),
        "inequality_lemma": (
            "for every convex quadrilateral a,b,c,d in cyclic order, "
            "d(a,c)+d(b,d)>d(a,b)+d(c,d) and "
            "d(a,c)+d(b,d)>d(a,d)+d(b,c)"
        ),
        "certificate_logic": (
            "every listed inequality has a vertex order forced by the boundary "
            "prefix; the listed positive integer combination has zero total "
            "coefficient after quotienting by selected-distance equalities, "
            "giving 0 > 0 for every completion of this branch"
        ),
        "forced_inequalities_available": len(rows),
        "num_inequalities": len(inequalities),
        "weight_sum": int(sum(weights)),
        "inequalities": inequalities,
        "claim_strength": (
            "Exact obstruction for every completion of this one fixed "
            "C19 boundary prefix; not an all-order C19 obstruction."
        ),
    }


def check_prefix_certificate_dict(cert: Mapping[str, object]) -> PrefixBranchCheckResult:
    pattern = cert["pattern"]
    if not isinstance(pattern, Mapping):
        raise ValueError("pattern must be an object")
    if str(pattern["name"]) != PATTERN_NAME:
        raise ValueError("unexpected pattern")
    if int(pattern["n"]) != N:
        raise ValueError("unexpected n")
    offsets = [int(v) for v in pattern["circulant_offsets"]]
    if offsets != OFFSETS:
        raise ValueError("unexpected offsets")

    boundary = cert["boundary_prefix"]
    if not isinstance(boundary, Mapping):
        raise ValueError("boundary_prefix must be an object")
    if int(boundary["anchor_label"]) != 0:
        raise ValueError("only anchor label 0 is supported")
    state = state_from_boundary(
        [int(v) for v in boundary["left"]],
        [int(v) for v in boundary["right_reflection_side"]],
    )
    stored_middle = [int(v) for v in boundary["middle_labels_unordered"]]
    if stored_middle != list(state.remaining):
        raise ValueError("stored middle labels do not match boundary complement")

    classes = build_distance_classes(N, OFFSETS)
    class_count = len(set(classes.values()))
    total: MutableMapping[int, int] = Counter()
    positive_count = 0
    weight_sum = 0
    max_weight = 0

    inequalities = cert["inequalities"]
    if not isinstance(inequalities, list):
        raise ValueError("inequalities must be a list")

    for item in inequalities:
        if not isinstance(item, Mapping):
            raise ValueError(f"inequality item is not an object: {item!r}")
        weight = int(item["weight"])
        if weight <= 0:
            raise ValueError("weights must be positive")
        quad = tuple(int(v) for v in item["quad"])
        forced = forced_order_quad(state, quad)
        if forced is None or forced != quad:
            raise ValueError(f"quad order is not forced by prefix: {quad}")
        positive_count += 1
        weight_sum += weight
        max_weight = max(max_weight, weight)
        for pair, coeff in inequality_terms(str(item["kind"]), quad):
            total[classes[pair]] += weight * coeff

    if "num_inequalities" in cert and int(cert["num_inequalities"]) != positive_count:
        raise ValueError("stored num_inequalities does not match listed inequalities")
    if "weight_sum" in cert and int(cert["weight_sum"]) != weight_sum:
        raise ValueError("stored weight_sum does not match listed weights")

    nonzero = {key: value for key, value in total.items() if value != 0}
    if nonzero:
        raise AssertionError(f"weighted coefficient sum is not zero: {nonzero}")

    return PrefixBranchCheckResult(
        label=str(cert["label"]),
        status=str(cert["status"]),
        positive_inequalities=positive_count,
        forced_inequalities_available=int(cert["forced_inequalities_available"]),
        distance_classes_after_selected_equalities=class_count,
        weight_sum=weight_sum,
        max_weight=max_weight,
        zero_sum_verified=True,
        claim_strength=str(cert["claim_strength"]),
    )


def summarize_certificate(cert: Mapping[str, object]) -> dict[str, object]:
    result = check_prefix_certificate_dict(cert)
    return {
        "status": result.status,
        "positive_inequalities": result.positive_inequalities,
        "forced_inequalities_available": result.forced_inequalities_available,
        "distance_classes_after_selected_equalities": (
            result.distance_classes_after_selected_equalities
        ),
        "weight_sum": result.weight_sum,
        "max_weight": result.max_weight,
        "zero_sum_verified": result.zero_sum_verified,
        "claim_strength": result.claim_strength,
    }


def find_certificate_for_state(
    *,
    label: str,
    state: BoundaryState,
    classes: Mapping[tuple[int, int], int],
    tol: float,
) -> tuple[int, dict[str, object] | None, dict[str, object] | None]:
    rows = prefix_kalmanson_rows(state, classes)
    support = lp_support(rows, tol)
    if support is None:
        return len(rows), None, None
    weights = exact_positive_weights(rows, support)
    if weights is None:
        return len(rows), None, None
    cert = certificate_payload(
        label=label,
        state=state,
        rows=rows,
        support=support,
        weights=weights,
    )
    summary = summarize_certificate(cert)
    return len(rows), cert, summary


def scan_pilot(
    *,
    boundary_pairs: int,
    max_branches: int,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if max_branches < 0:
        raise ValueError("max_branches must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    raw_count, canonical_count = count_boundary_states(boundary_pairs)
    classes = build_distance_classes(N, OFFSETS)

    support_histogram: Counter[int] = Counter()
    row_count_histogram: Counter[int] = Counter()
    closed_examples: list[dict[str, object]] = []
    unclosed_branches: list[dict[str, object]] = []
    unclosed_examples: list[dict[str, object]] = []
    sampled_labels: list[str] = []
    closed_count = 0

    for idx, state in enumerate(iter_boundary_states(boundary_pairs)):
        if idx >= max_branches:
            break
        label = branch_label(idx)
        sampled_labels.append(label)
        row_count, cert, summary = find_certificate_for_state(
            label=label,
            state=state,
            classes=classes,
            tol=tol,
        )
        row_count_histogram[row_count] += 1
        record: dict[str, object] = {
            "label": label,
            "boundary_left": list(state.left),
            "boundary_right_reflection_side": list(state.right),
            "middle_label_count": len(state.remaining),
        }
        if cert is None or summary is None:
            unclosed_branches.append(record)
            if len(unclosed_examples) < closed_example_count:
                unclosed_examples.append(record)
        else:
            closed_count += 1
            support_histogram[int(summary["positive_inequalities"])] += 1
            if len(closed_examples) < closed_example_count:
                record["certificate_summary"] = summary
                if include_certificates:
                    record["certificate"] = cert
                closed_examples.append(record)

    return {
        "type": "c19_kalmanson_prefix_branch_pilot_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is a bounded prefix-branch pilot, not an exhaustive all-order C19 search.",
            "Each closed sampled branch is certified using only Kalmanson inequalities whose order is forced by the recorded boundary prefix.",
            "Unclosed sampled branches are not counterexamples and are not evidence of realizability.",
        ],
        "parameters": {
            "boundary_pairs": boundary_pairs,
            "max_branches": max_branches,
            "include_certificates_in_examples": include_certificates,
            "closed_example_count": closed_example_count,
            "lp_support_tolerance": tol,
            "anchor_label": 0,
        },
        "branch_accounting": {
            "raw_boundary_state_count": raw_count,
            "canonical_boundary_state_count": canonical_count,
            "sampled_branch_count": len(sampled_labels),
            "sampled_branch_certified_count": closed_count,
            "sampled_branch_unclosed_count": len(sampled_labels) - closed_count,
            "exhaustive_prefix_scan": len(sampled_labels) == canonical_count,
            "exhaustive_all_orders": False,
        },
        "forced_row_count_histogram": {
            str(key): row_count_histogram[key] for key in sorted(row_count_histogram)
        },
        "closed_support_size_histogram": {
            str(key): support_histogram[key] for key in sorted(support_histogram)
        },
        "closed_certificate_examples": closed_examples,
        "unclosed_sampled_branches": unclosed_branches,
        "unclosed_branch_examples": unclosed_examples,
        "sampled_branch_label_digest": label_digest(sampled_labels),
    }


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "raw_boundary_state_count": 13366080,
        "canonical_boundary_state_count": 6683040,
        "sampled_branch_count": 128,
        "sampled_branch_certified_count": 100,
        "sampled_branch_unclosed_count": 28,
        "exhaustive_prefix_scan": False,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    if data["forced_row_count_histogram"] != {"910": 128}:
        raise AssertionError("forced row histogram changed")

    support_histogram = data["closed_support_size_histogram"]
    if not isinstance(support_histogram, Mapping):
        raise AssertionError("closed support-size histogram must be an object")
    support_count = sum(int(value) for value in support_histogram.values())
    if support_count != expected_accounting["sampled_branch_certified_count"]:
        raise AssertionError("closed support-size histogram total changed")

    expected_digest = "79fa7c236754647fd7ed844475896ee61ff1eef0ab66c14410221891773db37b"
    if data["sampled_branch_label_digest"] != expected_digest:
        raise AssertionError("sampled branch label digest changed")

    closed_examples = data["closed_certificate_examples"]
    if not isinstance(closed_examples, list) or len(closed_examples) != DEFAULT_CLOSED_EXAMPLE_COUNT:
        raise AssertionError("closed examples changed")
    unclosed_examples = data["unclosed_branch_examples"]
    if not isinstance(unclosed_examples, list) or len(unclosed_examples) != DEFAULT_CLOSED_EXAMPLE_COUNT:
        raise AssertionError("unclosed examples changed")
    unclosed_branches = data["unclosed_sampled_branches"]
    if not isinstance(unclosed_branches, list) or len(unclosed_branches) != 28:
        raise AssertionError("unclosed branch list changed")
    if closed_examples[0]["label"] != "c19_prefix_branch_0000":
        raise AssertionError("first closed example changed")
    if unclosed_examples[0]["label"] != "c19_prefix_branch_0013":
        raise AssertionError("first unclosed example changed")
    if unclosed_branches[-1]["label"] != "c19_prefix_branch_0109":
        raise AssertionError("last unclosed branch changed")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "sampled C19 prefixes: "
        f"closed={accounting['sampled_branch_certified_count']} "
        f"unclosed={accounting['sampled_branch_unclosed_count']} "
        f"sampled={accounting['sampled_branch_count']}"
    )
    print("support-size histogram:")
    histogram = data["closed_support_size_histogram"]
    if not isinstance(histogram, Mapping):
        raise TypeError("closed_support_size_histogram must be an object")
    for size, count in histogram.items():
        print(f"  {size}: {count}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--boundary-pairs", type=int, default=DEFAULT_BOUNDARY_PAIRS)
    parser.add_argument("--max-branches", type=int, default=DEFAULT_MAX_BRANCHES)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--include-certificates",
        action="store_true",
        help="include full certificates for stored closed examples",
    )
    parser.add_argument(
        "--closed-example-count",
        type=int,
        default=DEFAULT_CLOSED_EXAMPLE_COUNT,
        help="number of closed and unclosed examples to store",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = scan_pilot(
        boundary_pairs=args.boundary_pairs,
        max_branches=args.max_branches,
        include_certificates=args.include_certificates,
        closed_example_count=args.closed_example_count,
        tol=args.tol,
    )
    if args.assert_expected:
        assert_expected(data)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(data, indent=2, sort_keys=True))
    else:
        print_table(data)
        if args.assert_expected:
            print("OK: bounded C19 prefix branch pilot matched expected sample")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
