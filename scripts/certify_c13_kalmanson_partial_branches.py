#!/usr/bin/env python3
"""Certify C13 prefix branches using only prefix-forced Kalmanson rows.

This is a partial-order extension of the C13 prefix branch pilot.  For each
two-sided boundary prefix, it keeps only those convex-quadrilateral Kalmanson
inequalities whose vertex order is already forced by the prefix, independent
of the order of the still-unplaced middle labels.  A found certificate closes
every completion of that one boundary prefix.

The output is not an exhaustive all-order C13 search.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, MutableMapping, NamedTuple, Sequence

from branch_c13_kalmanson_prefix_pilot import (
    BoundaryState,
    generate_boundary_states,
)
from check_kalmanson_certificate import (
    build_distance_classes,
    inequality_terms,
)
from find_kalmanson_certificate import (
    InequalityRow,
    KINDS,
    exact_positive_weights,
    lp_support,
)

PATTERN_NAME = "C13_sidon_1_2_4_10"
N = 13
OFFSETS = [1, 2, 4, 10]
DEFAULT_BOUNDARY_PAIRS = 2
DEFAULT_EXAMPLE_COUNT = 12


class PartialBranchCheckResult(NamedTuple):
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
class BranchClosure:
    label: str
    state: BoundaryState
    forced_row_count: int
    certificate: dict[str, object] | None
    summary: dict[str, object] | None


def branch_label(index: int) -> str:
    return f"partial_branch_{index:04d}"


def state_from_boundary(left: Sequence[int], right: Sequence[int]) -> BoundaryState:
    left_tuple = tuple(int(v) for v in left)
    right_tuple = tuple(int(v) for v in right)
    used = set(left_tuple) | set(right_tuple)
    if len(used) != len(left_tuple) + len(right_tuple):
        raise ValueError("boundary labels must be distinct")
    if 0 in used:
        raise ValueError("boundary labels must not include anchor 0")
    if any(label < 1 or label >= N for label in used):
        raise ValueError("boundary labels outside 1..12")
    remaining = tuple(label for label in range(1, N) if label not in used)
    return BoundaryState(left=left_tuple, right=right_tuple, remaining=remaining)


def forced_order_quad(state: BoundaryState, labels: Sequence[int]) -> tuple[int, int, int, int] | None:
    """Return the forced anchored order for a quadrilateral, if unique.

    The branch state represents cyclic orders of the form:

      0, left[0], left[1], ..., middle permutation, ..., right[1], right[0].

    More than one unplaced middle label makes the relative order non-forced.
    """

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


def partial_kalmanson_rows(
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


def partial_certificate_payload(
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
            "two-sided boundary prefix; not an all-order C13 obstruction."
        ),
    }


def check_partial_certificate_dict(cert: Mapping[str, object]) -> PartialBranchCheckResult:
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

    return PartialBranchCheckResult(
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
    result = check_partial_certificate_dict(cert)
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


def branch_record(label: str, state: BoundaryState) -> dict[str, object]:
    return {
        "label": label,
        "boundary_left": list(state.left),
        "boundary_right_reflection_side": list(state.right),
    }


def label_digest(labels: Sequence[str]) -> str:
    payload = "".join(f"{label}\n" for label in labels)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def scan_branches(
    *,
    boundary_pairs: int,
    max_branches: int | None,
    include_certificates: bool,
    closed_example_count: int,
    tol: float,
) -> dict[str, object]:
    if max_branches is not None and max_branches < 0:
        raise ValueError("max_branches must be nonnegative")
    if closed_example_count < 0:
        raise ValueError("closed_example_count must be nonnegative")

    states, counts = generate_boundary_states(boundary_pairs)
    selected_states = states if max_branches is None else states[:max_branches]
    classes = build_distance_classes(N, OFFSETS)
    branches: list[BranchClosure] = []
    unclosed: list[str] = []
    support_histogram: Counter[int] = Counter()
    forced_row_counts: Counter[int] = Counter()

    for idx, state in enumerate(selected_states):
        label = branch_label(idx)
        rows = partial_kalmanson_rows(state, classes)
        forced_row_counts[len(rows)] += 1
        support = lp_support(rows, tol)
        cert = None
        summary = None
        if support is not None:
            weights = exact_positive_weights(rows, support)
            if weights is not None:
                cert = partial_certificate_payload(
                    label=label,
                    state=state,
                    rows=rows,
                    support=support,
                    weights=weights,
                )
                summary = summarize_certificate(cert)
                support_histogram[int(summary["positive_inequalities"])] += 1
        if cert is None:
            unclosed.append(label)
        branches.append(
            BranchClosure(
                label=label,
                state=state,
                forced_row_count=len(rows),
                certificate=cert,
                summary=summary,
            )
        )

    closed_branches = [item for item in branches if item.certificate is not None]
    closed_examples = []
    for item in closed_branches[:closed_example_count]:
        record = branch_record(item.label, item.state)
        record["certificate_summary"] = item.summary
        if include_certificates:
            record["certificate"] = item.certificate
        closed_examples.append(record)

    payload = {
        "type": "c13_kalmanson_partial_branch_closures_v1",
        "trust": "EXACT_OBSTRUCTION",
        "pattern": {
            "name": PATTERN_NAME,
            "n": N,
            "circulant_offsets": OFFSETS,
        },
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "This is not an exhaustive all-order cyclic-order search.",
            "Each closed branch is certified using only Kalmanson inequalities whose order is forced by the recorded boundary prefix.",
            "Unclosed branches are not counterexamples and are not numerical evidence of realizability.",
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
            "raw_boundary_state_count": counts.raw_boundary_state_count,
            "canonical_boundary_state_count": counts.canonical_boundary_state_count,
            "scanned_boundary_state_count": len(selected_states),
            "partial_branch_certified_count": len(closed_branches),
            "unclosed_branch_count": len(unclosed),
            "exhaustive_two_pair_boundary_scan": (
                boundary_pairs == DEFAULT_BOUNDARY_PAIRS and max_branches is None
            ),
            "exhaustive_all_orders": False,
        },
        "forced_row_count_histogram": {
            str(key): forced_row_counts[key] for key in sorted(forced_row_counts)
        },
        "closed_support_size_histogram": {
            str(key): support_histogram[key] for key in sorted(support_histogram)
        },
        "closed_certificate_examples": closed_examples,
        "unclosed_branch_label_digest": label_digest(unclosed),
        "unclosed_branch_label_examples": {
            "first": unclosed[:20],
            "last": unclosed[-20:],
        },
    }
    return payload


def assert_expected(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise AssertionError("branch_accounting must be an object")
    expected_accounting = {
        "raw_boundary_state_count": 11880,
        "canonical_boundary_state_count": 5940,
        "scanned_boundary_state_count": 5940,
        "partial_branch_certified_count": 5108,
        "unclosed_branch_count": 832,
        "exhaustive_two_pair_boundary_scan": True,
        "exhaustive_all_orders": False,
    }
    for key, expected in expected_accounting.items():
        if accounting[key] != expected:
            raise AssertionError(f"{key} changed: {accounting[key]} != {expected}")

    forced_histogram = data["forced_row_count_histogram"]
    if forced_histogram != {"170": 5940}:
        raise AssertionError(f"forced row histogram changed: {forced_histogram}")

    expected_support_histogram = {
        "2": 884,
        "3": 864,
        "4": 871,
        "5": 660,
        "6": 615,
        "7": 462,
        "8": 332,
        "9": 224,
        "10": 103,
        "11": 56,
        "12": 28,
        "13": 7,
        "15": 2,
    }
    if data["closed_support_size_histogram"] != expected_support_histogram:
        raise AssertionError("closed support-size histogram changed")

    examples = data["closed_certificate_examples"]
    if not isinstance(examples, list) or len(examples) != DEFAULT_EXAMPLE_COUNT:
        raise AssertionError("closed certificate examples changed")
    for item in examples:
        if not isinstance(item, Mapping):
            raise AssertionError("closed example must be an object")
        summary = item["certificate_summary"]
        if not isinstance(summary, Mapping):
            raise AssertionError("closed example missing certificate summary")
        if summary["status"] != "EXACT_OBSTRUCTION_FOR_PREFIX_BRANCH_COMPLETIONS":
            raise AssertionError("closed example status changed")
        if summary["zero_sum_verified"] is not True:
            raise AssertionError("closed example did not verify")

    expected_digest = "94ef5e480813402fdef3d31a9f48f2a48680695564ab504c8374e2395c3b1893"
    if data["unclosed_branch_label_digest"] != expected_digest:
        raise AssertionError("unclosed branch label digest changed")
    examples_obj = data["unclosed_branch_label_examples"]
    if not isinstance(examples_obj, Mapping):
        raise AssertionError("unclosed branch label examples must be an object")
    first = examples_obj["first"]
    last = examples_obj["last"]
    if not isinstance(first, list) or not isinstance(last, list):
        raise AssertionError("unclosed branch label examples must be lists")
    if first[0] != "partial_branch_0012":
        raise AssertionError(f"first unclosed branch changed: {first[0]}")
    if last[-1] != "partial_branch_5915":
        raise AssertionError(f"last unclosed branch changed: {last[-1]}")


def print_table(data: Mapping[str, object]) -> None:
    accounting = data["branch_accounting"]
    if not isinstance(accounting, Mapping):
        raise TypeError("branch_accounting must be an object")
    print(
        "partial branches: "
        f"closed={accounting['partial_branch_certified_count']} "
        f"unclosed={accounting['unclosed_branch_count']} "
        f"scanned={accounting['scanned_boundary_state_count']}"
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
    parser.add_argument("--max-branches", type=int)
    parser.add_argument("--tol", type=float, default=1e-9, help="LP support threshold")
    parser.add_argument("--out", type=Path, help="write JSON payload to this path")
    parser.add_argument("--json", action="store_true", help="print JSON payload")
    parser.add_argument(
        "--include-certificates",
        action="store_true",
        help="include full certificates for the closed examples",
    )
    parser.add_argument(
        "--closed-example-count",
        type=int,
        default=DEFAULT_EXAMPLE_COUNT,
        help="number of closed certificate examples to store",
    )
    parser.add_argument("--assert-expected", action="store_true")
    args = parser.parse_args()

    data = scan_branches(
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
            print("OK: C13 partial branch closures matched expected frontier")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
