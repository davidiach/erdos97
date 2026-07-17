#!/usr/bin/env python3
"""Rigorous bounded verifier for the real two-mode cyclic family.

The family is

    z_i = w**i + t*w**(k*i),   w = exp(2*pi*I/n),   t real.

For every ``9 <= n <= max_n`` and ``2 <= k <= n-2`` the verifier
enumerates every real root of every non-identity row-zero distance collision.
Identity classes are checked to have size at most two, so this root list
covers every parameter at which row zero has a fourfold distance class.

Each root occurrence is rejected by one of the following rigorous tests:

* a complete row is partitioned into certified disjoint value bands of size
  at most three; or
* two regular rotation orbits satisfy the exact incircle obstruction; or
* an exact polynomial gcd proves that two labelled points coincide.

SymPy supplies exact arithmetic in Q(2*cos(2*pi/n)).  python-flint/Arb is
used only for outward-rounded real-root enclosures and strict inequalities.
Rows and orbit phases are considered in canonical deterministic order; no
binary floating-point value makes or selects a proof decision.

This proves only a bounded obstruction for this restricted real-coefficient
family.  It is not a proof of Erdos Problem 97.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import sys
from dataclasses import dataclass
from decimal import Decimal
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any, Iterable, Sequence

try:
    from flint import arb, ctx, fmpq
except ImportError as exc:  # pragma: no cover - exercised by CLI failure path
    raise SystemExit(
        "python-flint is required; install the exact artifact dependencies"
    ) from exc

try:
    from sympy import Poly, QQ, cos, pi, symbols
except ImportError as exc:  # pragma: no cover - exercised by CLI failure path
    raise SystemExit(
        "SymPy is required; install the exact artifact dependencies"
    ) from exc


T = symbols("T")
SCHEMA = "erdos97.two_mode_cyclic_exact_bounded.v1"
STATUS = "exact_bounded_family_obstruction_review_pending"
INCOMPLETE_STATUS = "incomplete_exact_bounded_family_diagnostic"
TRUST = "EXACT_CERTIFICATE_DIAGNOSTIC"
DEFAULT_MIN_N = 9
DEFAULT_MAX_N = 80
CANONICAL_PYTHON = (3, 12)
PINNED_DISTRIBUTIONS = {
    "mpmath": "1.3.0",
    "python-flint": "0.8.0",
    "sympy": "1.14.0",
}
PRECISIONS = (40, 70, 110, 170)
GENERATOR = "scripts/check_two_mode_cyclic_exact.py"
CANONICAL_ARTIFACT = "data/certificates/two_mode_cyclic_exact_n80.json"
PLAN_PATH = "docs/two-mode-cyclic-exact-n80.md"
LOCK_PATH = "requirements-lock.txt"


@dataclass(frozen=True)
class ExactField:
    n: int
    domain: Any
    cosine: tuple[Any, ...]


@dataclass(frozen=True)
class RootOccurrence:
    index: int
    branch: str
    ball: Any


def build_field(n: int) -> ExactField:
    """Return K=Q(S_1) and S_m=2*cos(2*pi*m/n), 0<=m<n."""
    generator = 2 * cos(2 * pi / n)
    domain = QQ.algebraic_field(generator)
    theta = domain.from_sympy(generator)
    values = [domain(2), theta]
    for _ in range(1, n - 1):
        values.append(theta * values[-1] - values[-2])
    assert len(values) == n
    assert values[0] == domain(2)
    return ExactField(n=n, domain=domain, cosine=tuple(values))


def s_exact(field: ExactField, index: int) -> Any:
    return field.cosine[index % field.n]


def distance_coefficients(
    field: ExactField, k: int, center: int, shift: int
) -> tuple[Any, Any, Any]:
    """Exact coefficients (constant, linear, quadratic) of one distance."""
    two = field.domain(2)
    a = two - s_exact(field, shift)
    c = two - s_exact(field, k * shift)
    q = (k - 1) * center
    b = (
        s_exact(field, (k - 1) * (center + shift))
        - s_exact(field, q - shift)
        - s_exact(field, q + k * shift)
        + s_exact(field, q)
    )
    return a, b, c


def subtract_coefficients(
    left: Sequence[Any], right: Sequence[Any]
) -> tuple[Any, Any, Any]:
    return tuple(a - b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


def exact_degree(coefficients: Sequence[Any]) -> int:
    for degree in range(2, -1, -1):
        if coefficients[degree]:
            return degree
    return -1


def polynomial(field: ExactField, coefficients: Sequence[Any]) -> Any:
    degree = exact_degree(coefficients)
    if degree < 0:
        return Poly(0, T, domain=field.domain)
    return Poly.from_list(
        list(reversed(coefficients[: degree + 1])),
        T,
        domain=field.domain,
    )


def row_zero_identity_classes(
    field: ExactField, k: int
) -> list[tuple[tuple[Any, Any, Any], tuple[int, ...]]]:
    classes: dict[tuple[Any, Any, Any], list[int]] = {}
    for shift in range(1, field.n):
        coefficients = distance_coefficients(field, k, 0, shift)
        classes.setdefault(coefficients, []).append(shift)
    return sorted(
        ((coefficients, tuple(shifts)) for coefficients, shifts in classes.items()),
        key=lambda item: item[1],
    )


def anp_to_arb(value: Any, theta: Any) -> Any:
    result = arb(0)
    for coefficient in value.to_list():
        result = result * theta + arb(str(coefficient))
    return result


def cosine_balls(n: int) -> tuple[Any, ...]:
    return tuple(2 * arb.cos_pi_fmpq(fmpq(2 * index, n)) for index in range(n))


def roots_of_collision(
    field: ExactField,
    coefficients: tuple[Any, Any, Any],
    decimal_precision: int,
    theta: Any | None = None,
) -> tuple[RootOccurrence, ...] | None:
    """Enclose every real root, or return None if the precision is ambiguous."""
    ctx.dps = decimal_precision
    degree = exact_degree(coefficients)
    if degree <= 0:
        return ()

    if theta is None:
        theta = 2 * arb.cos_pi_fmpq(fmpq(2, field.n))
    c0, c1, c2 = (anp_to_arb(value, theta) for value in coefficients)

    if degree == 1:
        if not (c1 > 0 or c1 < 0):
            return None
        return (RootOccurrence(0, "linear", -c0 / c1),)

    discriminant_exact = (
        coefficients[1] * coefficients[1] - 4 * coefficients[2] * coefficients[0]
    )
    if not discriminant_exact:
        if not (c2 > 0 or c2 < 0):
            return None
        return (RootOccurrence(0, "double", -c1 / (2 * c2)),)

    discriminant = c1 * c1 - 4 * c2 * c0
    if discriminant < 0:
        return ()
    if not discriminant > 0 or not (c2 > 0 or c2 < 0):
        return None

    square_root = discriminant.sqrt()
    first = (-c1 - square_root) / (2 * c2)
    second = (-c1 + square_root) / (2 * c2)
    if first < second:
        ordered = (first, second)
    elif second < first:
        ordered = (second, first)
    else:
        return None
    return (
        RootOccurrence(0, "lower", ordered[0]),
        RootOccurrence(1, "upper", ordered[1]),
    )


def arb_decimal_interval(value: Any) -> tuple[Decimal, Decimal, Decimal]:
    midpoint, radius, exponent = value.mid_rad_10exp()
    lower = Decimal(f"{int(midpoint) - int(radius)}e{int(exponent)}")
    upper = Decimal(f"{int(midpoint) + int(radius)}e{int(exponent)}")
    middle = Decimal(f"{int(midpoint)}e{int(exponent)}")
    return lower, upper, middle


def certified_small_bands(
    values: Sequence[Any], limit: int = 3
) -> tuple[tuple[int, ...], ...] | None:
    """Partition intervals into rigorously separated bands of size <= limit."""
    intervals = [
        (*arb_decimal_interval(value), index) for index, value in enumerate(values)
    ]
    intervals.sort(key=lambda item: (item[2], item[3]))
    count = len(intervals)
    if count == 0:
        return ()

    prefix_upper: list[Decimal] = []
    current_upper = intervals[0][1]
    for lower, upper, _middle, _index in intervals:
        del lower
        current_upper = max(current_upper, upper)
        prefix_upper.append(current_upper)

    suffix_lower: list[Decimal] = [Decimal(0)] * count
    current_lower = intervals[-1][0]
    for position in range(count - 1, -1, -1):
        current_lower = min(current_lower, intervals[position][0])
        suffix_lower[position] = current_lower

    valid_cut = [False] * (count + 1)
    valid_cut[0] = True
    valid_cut[count] = True
    for position in range(1, count):
        valid_cut[position] = prefix_upper[position - 1] < suffix_lower[position]

    predecessor: list[int | None] = [None] * (count + 1)
    predecessor[0] = -1
    for end in range(1, count + 1):
        if not valid_cut[end]:
            continue
        for start in range(max(0, end - limit), end):
            if predecessor[start] is not None and valid_cut[start]:
                predecessor[end] = start
                break
    if predecessor[count] is None:
        return None

    bands: list[tuple[int, ...]] = []
    end = count
    while end:
        start = predecessor[end]
        assert start is not None and start >= 0
        bands.append(
            tuple(sorted(intervals[position][3] for position in range(start, end)))
        )
        end = start
    bands.reverse()
    assert max(map(len, bands), default=0) <= limit
    return tuple(bands)


def row_distance_balls(
    n: int,
    k: int,
    center: int,
    parameter: Any,
    s_values: Sequence[Any],
) -> tuple[Any, ...]:
    result = []
    parameter_squared = parameter * parameter
    q = (k - 1) * center
    for shift in range(1, n):
        a = 2 - s_values[shift % n]
        c = 2 - s_values[(k * shift) % n]
        b = (
            s_values[((k - 1) * (center + shift)) % n]
            - s_values[(q - shift) % n]
            - s_values[(q + k * shift) % n]
            + s_values[q % n]
        )
        result.append(a + b * parameter + c * parameter_squared)
    return tuple(result)


def certify_inradius(
    n: int,
    k: int,
    parameter: Any,
    s_values: Sequence[Any],
) -> dict[str, int | str] | None:
    g = math.gcd(n, k - 1)
    d = n // g
    if g < 3 or d < 2:
        return None

    # S_(g*j)=2*cos(2*pi*j/d).  Its canonical maximum is j=0 and a
    # canonical minimum is j=floor(d/2), so the sign of t determines the
    # extreme-radius phases without a floating-point choice.
    if parameter > 0:
        small_phase, large_phase = d // 2, 0
    elif parameter < 0:
        small_phase, large_phase = 0, d // 2
    else:
        return None

    radius_squared = [
        1 + parameter * parameter + parameter * s_values[(g * phase) % n]
        for phase in range(d)
    ]

    sd = s_values[d % n]
    h_value = (2 - sd) * (1 + parameter * parameter) + parameter * (
        4 * s_values[(g * small_phase) % n] - (2 + sd) * s_values[(g * large_phase) % n]
    )
    if h_value < 0 and radius_squared[large_phase] > 0:
        return {
            "kind": "inradius_strict",
            "small_phase": small_phase,
            "large_phase": large_phase,
        }
    return None


def root_matches_common_factor(
    field: ExactField,
    defining_coefficients: tuple[Any, Any, Any],
    query_coefficients: tuple[Any, Any, Any],
    root_index: int,
    decimal_precision: int,
) -> bool:
    """Prove that the selected defining root also zeros the query polynomial."""
    defining = polynomial(field, defining_coefficients)
    query = polynomial(field, query_coefficients)
    common = defining.gcd(query)
    if common.degree() <= 0:
        return False
    if common.degree() == defining.degree():
        return True
    if common.degree() != 1:
        return False

    common_coefficients = tuple(
        field.domain.from_sympy(common.nth(degree)) for degree in range(3)
    )
    common_roots = roots_of_collision(field, common_coefficients, decimal_precision)
    defining_roots = roots_of_collision(field, defining_coefficients, decimal_precision)
    if common_roots is None or defining_roots is None or len(common_roots) != 1:
        return False
    if root_index >= len(defining_roots):
        return False
    common_ball = common_roots[0].ball
    selected_ball = defining_roots[root_index].ball
    if not common_ball.overlaps(selected_ball):
        return False
    return all(
        index == root_index or not common_ball.overlaps(candidate.ball)
        for index, candidate in enumerate(defining_roots)
    )


def evaluate_at_arb(
    coefficients: Sequence[Any],
    parameter: Any,
    theta: Any,
) -> Any:
    """Evaluate exact field coefficients over outward-rounded Arb balls."""
    result = arb(0)
    for coefficient in reversed(coefficients):
        result = result * parameter + anp_to_arb(coefficient, theta)
    return result


def certify_duplicate(
    field: ExactField,
    k: int,
    defining_coefficients: tuple[Any, Any, Any],
    root_index: int,
    decimal_precision: int,
    parameter: Any,
    theta: Any,
) -> dict[str, int | str] | None:
    """Find an exact coincident-label certificate at the selected root."""
    for center in range(field.n):
        for shift in range(1, field.n):
            query = distance_coefficients(field, k, center, shift)
            # Interval evaluation is a one-sided sieve only: exclusion of zero
            # skips an impossible gcd, while every surviving query is still
            # proved by exact polynomial arithmetic below.
            query_value = evaluate_at_arb(query, parameter, theta)
            if query_value > 0 or query_value < 0:
                continue
            if root_matches_common_factor(
                field,
                defining_coefficients,
                query,
                root_index,
                decimal_precision,
            ):
                return {
                    "kind": "duplicate",
                    "center": center,
                    "shift": shift,
                }
    return None


def certify_root_at_precision(
    field: ExactField,
    k: int,
    defining_coefficients: tuple[Any, Any, Any],
    root: RootOccurrence,
    decimal_precision: int,
    s_values: Sequence[Any],
) -> dict[str, Any] | None:
    ctx.dps = decimal_precision
    n = field.n

    inradius = certify_inradius(n, k, root.ball, s_values)
    if inradius is not None:
        return inradius

    d = n // math.gcd(n, k - 1)
    for center in range(d):
        values = row_distance_balls(n, k, center, root.ball, s_values)
        bands = certified_small_bands(values)
        if bands is not None:
            return {
                "kind": "row_failure",
                "center": center,
                "bands": [[index + 1 for index in band] for band in bands],
            }
    return certify_duplicate(
        field,
        k,
        defining_coefficients,
        root.index,
        decimal_precision,
        root.ball,
        s_values[1],
    )


def canonical_line(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode()


def verify_case(
    n: int,
    k: int,
    field: ExactField | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if field is None:
        field = build_field(n)
    elif field.n != n:
        raise ValueError("field/case size mismatch")
    identity_classes = row_zero_identity_classes(field, k)
    maximum_identity_size = max(
        len(shifts) for _coefficients, shifts in identity_classes
    )
    if maximum_identity_size > 2:
        return (
            {
                "n": n,
                "k": k,
                "identity_classes": len(identity_classes),
                "maximum_identity_size": maximum_identity_size,
                "seed_pairs": 0,
                "real_root_occurrences": 0,
                "row_failures": 0,
                "inradius_strict": 0,
                "duplicates": 0,
                "unresolved": 1,
                "digest": hashlib.sha256(b"").hexdigest(),
            },
            [
                {
                    "n": n,
                    "k": k,
                    "reason": "identity_class_size",
                    "size": maximum_identity_size,
                }
            ],
        )

    seed_pairs = 0
    real_roots = 0
    row_failures = 0
    inradius_strict = 0
    duplicates = 0
    unresolved: list[dict[str, Any]] = []
    digest = hashlib.sha256()
    cosine_cache: dict[int, tuple[Any, ...]] = {}

    def balls_at(precision: int) -> tuple[Any, ...]:
        if precision not in cosine_cache:
            ctx.dps = precision
            cosine_cache[precision] = cosine_balls(n)
        return cosine_cache[precision]

    for right in range(len(identity_classes)):
        for left in range(right):
            seed_pairs += 1
            left_coefficients, left_shifts = identity_classes[left]
            right_coefficients, right_shifts = identity_classes[right]
            collision = subtract_coefficients(right_coefficients, left_coefficients)
            degree = exact_degree(collision)
            if degree <= 0:
                if degree == -1:
                    unresolved.append(
                        {
                            "n": n,
                            "k": k,
                            "reason": "unexpected_zero_between_identity_classes",
                            "left": left_shifts,
                            "right": right_shifts,
                        }
                    )
                continue

            roots: tuple[RootOccurrence, ...] | None = None
            for precision in PRECISIONS:
                s_values = balls_at(precision)
                roots = roots_of_collision(
                    field,
                    collision,
                    precision,
                    theta=s_values[1],
                )
                if roots is not None:
                    break
            if roots is None:
                unresolved.append(
                    {
                        "n": n,
                        "k": k,
                        "reason": "root_isolation",
                        "left": left_shifts,
                        "right": right_shifts,
                    }
                )
                continue

            for root_stub in roots:
                real_roots += 1
                decision = None
                root = root_stub
                for precision in PRECISIONS:
                    s_values = balls_at(precision)
                    refreshed = roots_of_collision(
                        field,
                        collision,
                        precision,
                        theta=s_values[1],
                    )
                    if refreshed is None or root_stub.index >= len(refreshed):
                        continue
                    root = refreshed[root_stub.index]
                    decision = certify_root_at_precision(
                        field,
                        k,
                        collision,
                        root,
                        precision,
                        s_values,
                    )
                    if decision is not None:
                        break
                record = {
                    "n": n,
                    "k": k,
                    "left": list(left_shifts),
                    "right": list(right_shifts),
                    "root_index": root.index,
                    "root_branch": root.branch,
                }
                if decision is None:
                    unresolved_record = {**record, "reason": "no_terminal_certificate"}
                    unresolved.append(unresolved_record)
                    digest.update(canonical_line({**record, "decision": "unresolved"}))
                else:
                    kind = decision["kind"]
                    if kind == "row_failure":
                        row_failures += 1
                    elif kind == "inradius_strict":
                        inradius_strict += 1
                    elif kind == "duplicate":
                        duplicates += 1
                    else:  # pragma: no cover - guards future decision additions
                        raise AssertionError(kind)
                    digest.update(canonical_line({**record, "decision": decision}))

    summary = {
        "n": n,
        "k": k,
        "identity_classes": len(identity_classes),
        "maximum_identity_size": maximum_identity_size,
        "seed_pairs": seed_pairs,
        "real_root_occurrences": real_roots,
        "row_failures": row_failures,
        "inradius_strict": inradius_strict,
        "duplicates": duplicates,
        "unresolved": len(unresolved),
        "digest": digest.hexdigest(),
    }
    assert real_roots == row_failures + inradius_strict + duplicates + len(unresolved)
    return summary, unresolved


def verify_n(n: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    field = build_field(n)
    cases: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    for k in range(2, n - 1):
        case, misses = verify_case(n, k, field)
        cases.append(case)
        unresolved.extend(misses)
    return cases, unresolved


def aggregate(min_n: int, max_n: int, jobs: int = 1) -> dict[str, Any]:
    cases: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    sizes = list(range(min_n, max_n + 1))
    if jobs == 1:
        results = map(verify_n, sizes)
        for n_cases, n_unresolved in results:
            cases.extend(n_cases)
            unresolved.extend(n_unresolved)
    else:
        with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as executor:
            by_n = {
                n: result
                for n, result in zip(sizes, executor.map(verify_n, sizes), strict=True)
            }
        for n in sizes:
            n_cases, n_unresolved = by_n[n]
            cases.extend(n_cases)
            unresolved.extend(n_unresolved)

    totals = {
        "parameter_pairs": len(cases),
        "identity_classes": sum(case["identity_classes"] for case in cases),
        "seed_pairs": sum(case["seed_pairs"] for case in cases),
        "real_root_occurrences": sum(case["real_root_occurrences"] for case in cases),
        "row_failures": sum(case["row_failures"] for case in cases),
        "inradius_strict": sum(case["inradius_strict"] for case in cases),
        "duplicates": sum(case.get("duplicates", 0) for case in cases),
        "unresolved": len(unresolved),
    }
    global_digest = hashlib.sha256()
    for case in cases:
        global_digest.update(canonical_line(case))

    artifact_path = (
        CANONICAL_ARTIFACT
        if (min_n, max_n) == (DEFAULT_MIN_N, DEFAULT_MAX_N)
        else "<output-path>"
    )
    canonical_prefix = (
        f"python {GENERATOR} --min-n {min_n} --max-n {max_n} --jobs 4 --assert-closed"
    )

    return {
        "schema": SCHEMA,
        "status": STATUS if not unresolved else INCOMPLETE_STATUS,
        "trust": TRUST,
        "claim_scope": (
            f"Real t in z_i=w^i+t*w^(k*i), all {min_n}<=n<={max_n} and "
            "2<=k<=n-2; bounded restricted-family result only, not Erdos 97."
        ),
        "range": {"min_n": min_n, "max_n": max_n},
        "method": {
            "field": "Q(2*cos(2*pi/n)) exact arithmetic via SymPy",
            "root_bounds": "outward-rounded Arb quadratic enclosures",
            "terminal_tests": [
                "row_value_band_partition",
                "orbit_inradius_strict",
                "exact_duplicate",
            ],
            "candidate_completeness": (
                "row-zero identity classes have weight at most two; every "
                "fourfold class therefore forces a root of an enumerated "
                "non-identity collision polynomial"
            ),
        },
        "toolchain": {
            "python": ".".join(map(str, CANONICAL_PYTHON)),
            "sympy": PINNED_DISTRIBUTIONS["sympy"],
            "python_flint": PINNED_DISTRIBUTIONS["python-flint"],
            "mpmath": PINNED_DISTRIBUTIONS["mpmath"],
        },
        "provenance": {
            "generator": GENERATOR,
            "command": f"{canonical_prefix} --output {artifact_path}",
            "check_command": f"{canonical_prefix} --check-artifact {artifact_path}",
            "dependency_lock": LOCK_PATH,
            "run_plan": PLAN_PATH,
        },
        "totals": totals,
        "case_digest": global_digest.hexdigest(),
        "cases": cases,
        "unresolved": unresolved,
        "nonclaims": [
            "No statement about arbitrary point configurations.",
            "No statement about complex coefficients or additional Fourier modes.",
            "No proof or counterexample for Erdos Problem 97.",
        ],
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(text, encoding="utf-8", newline="")
    temporary.replace(path)


def check_payload(actual: dict[str, Any], expected_path: Path) -> None:
    expected = json.loads(expected_path.read_text(encoding="utf-8"))
    if actual != expected:
        raise SystemExit(f"certificate mismatch: {expected_path}")


def canonical_toolchain_error() -> str | None:
    """Return a reproducibility error for the retained artifact toolchain."""
    if sys.version_info[:2] != CANONICAL_PYTHON:
        return (
            "the retained n=9..80 artifact is pinned to CPython 3.12; "
            f"running {sys.version_info.major}.{sys.version_info.minor}"
        )
    for distribution, expected in PINNED_DISTRIBUTIONS.items():
        try:
            actual = version(distribution)
        except PackageNotFoundError:
            return f"the retained artifact requires {distribution}=={expected}"
        if actual != expected:
            return (
                f"the retained artifact requires {distribution}=={expected}; "
                f"running {actual}"
            )
    return None


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--min-n", type=int, default=DEFAULT_MIN_N)
    parser.add_argument("--max-n", type=int, default=DEFAULT_MAX_N)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", "--check-artifact", dest="check", type=Path)
    parser.add_argument("--jobs", type=int, default=1)
    parser.add_argument("--assert-closed", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)
    if args.min_n < 3 or args.max_n < args.min_n:
        parser.error("require 3 <= min_n <= max_n")
    if args.jobs < 1:
        parser.error("--jobs must be at least one")
    if (args.min_n, args.max_n) == (DEFAULT_MIN_N, DEFAULT_MAX_N) and (
        args.output is not None or args.check is not None
    ):
        toolchain_error = canonical_toolchain_error()
        if toolchain_error is not None:
            parser.error(toolchain_error)

    payload = aggregate(args.min_n, args.max_n, jobs=args.jobs)
    if args.assert_closed and payload["totals"]["unresolved"]:
        print(
            json.dumps(payload["unresolved"][:20], indent=2, sort_keys=True),
            file=sys.stderr,
        )
        raise SystemExit(
            f"unresolved root occurrences: {payload['totals']['unresolved']}"
        )
    if args.output is not None:
        write_json(args.output, payload)
    if args.check is not None:
        check_payload(payload, args.check)
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "range": payload["range"],
                "totals": payload["totals"],
                "case_digest": payload["case_digest"],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
