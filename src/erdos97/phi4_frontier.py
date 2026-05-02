"""Phi 4-cycle rectangle-trap frontier scans.

The scanner applies the exact phi4 rectangle-trap filter to registered fixed
selected-witness patterns and fixed cyclic orders. It is a filter diagnostic:
no general proof and no counterexample are claimed.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from erdos97.incidence_filters import (
    phi4_rectangle_trap_certificates,
    phi_directed_4_cycles,
    phi_map,
)
from erdos97.search import PatternInfo

Pattern = Sequence[Sequence[int]]

N9_RECTANGLE_TRAP_PATTERN: list[list[int]] = [
    [1, 2, 3, 8],
    [0, 2, 4, 7],
    [1, 3, 5, 7],
    [1, 4, 6, 8],
    [0, 2, 5, 6],
    [3, 4, 6, 7],
    [2, 5, 7, 8],
    [0, 3, 6, 8],
    [0, 1, 4, 5],
]


def validate_case_order(case: str, n: int, order: Sequence[int]) -> None:
    """Validate that a fixed-order scan case uses a full cyclic permutation."""
    expected = set(range(n))
    seen = set(order)
    if len(order) != n or seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise ValueError(
            f"{case}: order is not a permutation of 0..{n - 1}; "
            f"missing={missing}, extra={extra}"
        )


@dataclass(frozen=True)
class Phi4ScanCase:
    """One fixed selected-witness pattern and cyclic order to scan."""

    case: str
    pattern: str
    order_label: str
    n: int
    S: Pattern
    order: list[int]
    source: str


def n9_rectangle_trap_case() -> Phi4ScanCase:
    """Return the registered n=9 positive rectangle-trap case."""
    return Phi4ScanCase(
        case="N9_phi4_rectangle_trap_selected_witness_pattern:natural_order",
        pattern="N9_phi4_rectangle_trap_selected_witness_pattern",
        order_label="natural_order",
        n=9,
        S=N9_RECTANGLE_TRAP_PATTERN,
        order=list(range(9)),
        source="data/certificates/n9_phi4_rectangle_trap.json",
    )


def built_in_natural_order_cases(
    patterns: dict[str, PatternInfo],
) -> list[Phi4ScanCase]:
    """Return natural-order scan cases for all built-in candidate patterns."""
    return [
        Phi4ScanCase(
            case=f"{pattern.name}:natural_order",
            pattern=pattern.name,
            order_label="natural_order",
            n=pattern.n,
            S=pattern.S,
            order=list(range(pattern.n)),
            source="erdos97.search.built_in_patterns",
        )
        for pattern in patterns.values()
    ]


def sparse_order_cases_from_payload(
    payload: dict[str, object],
    patterns: dict[str, PatternInfo],
) -> list[Phi4ScanCase]:
    """Return cases from data/certificates/sparse_order_survivors.json."""
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("sparse-order payload should contain a cases list")

    out: list[Phi4ScanCase] = []
    for row in cases:
        if not isinstance(row, dict):
            raise ValueError("sparse-order case should be a mapping")
        pattern_name = row.get("pattern")
        order = row.get("order")
        order_label = row.get("order_label")
        if not isinstance(pattern_name, str) or pattern_name not in patterns:
            raise ValueError(f"unknown sparse-order pattern: {pattern_name}")
        if not isinstance(order, list) or not all(isinstance(x, int) for x in order):
            raise ValueError(f"{pattern_name}: order should be a list of integers")
        if not isinstance(order_label, str):
            raise ValueError(f"{pattern_name}: order_label should be a string")

        pattern = patterns[pattern_name]
        case = f"{pattern_name}:{order_label}"
        validate_case_order(case, pattern.n, order)
        out.append(
            Phi4ScanCase(
                case=case,
                pattern=pattern_name,
                order_label=order_label,
                n=pattern.n,
                S=pattern.S,
                order=[int(x) for x in order],
                source="data/certificates/sparse_order_survivors.json",
            )
        )
    return out


def case_to_json(case: Phi4ScanCase) -> dict[str, object]:
    """Return a JSON-serializable phi4 scan row."""
    validate_case_order(case.case, case.n, case.order)
    cycles = phi_directed_4_cycles(case.S)
    certs = phi4_rectangle_trap_certificates(case.S, case.order)
    return {
        "case": case.case,
        "pattern": case.pattern,
        "order_label": case.order_label,
        "n": case.n,
        "source": case.source,
        "order": [int(x) for x in case.order],
        "phi_edges": len(phi_map(case.S)),
        "directed_phi_4_cycles": [
            [[int(a), int(b)] for a, b in cycle] for cycle in cycles
        ],
        "directed_phi_4_cycle_count": len(cycles),
        "rectangle_trap_4_cycles": len(certs),
        "rectangle_trap_certificates": certs,
        "obstructed_by_phi4_rectangle_trap": bool(certs),
    }


def scan_cases(cases: Sequence[Phi4ScanCase]) -> list[dict[str, object]]:
    """Scan all cases and return JSON rows."""
    return [case_to_json(case) for case in cases]


def scan_payload(rows: list[dict[str, object]]) -> dict[str, object]:
    """Wrap scan rows in a reproducibility payload."""
    return {
        "type": "phi4_frontier_scan_v1",
        "trust": "FIXED_ORDER_EXACT_FILTER_DIAGNOSTIC",
        "notes": [
            "No general proof of Erdos Problem #97 is claimed.",
            "No counterexample is claimed.",
            "A phi4 rectangle-trap hit is an exact fixed-pattern obstruction.",
            "A phi4 miss is not evidence of geometric realizability.",
        ],
        "case_count": len(rows),
        "obstructed_case_count": sum(
            1 for row in rows if row["obstructed_by_phi4_rectangle_trap"]
        ),
        "cases": rows,
    }
