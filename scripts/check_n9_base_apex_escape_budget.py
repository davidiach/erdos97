#!/usr/bin/env python3
"""Independently validate the n=9 base-apex escape-budget artifact."""

from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_base_apex_escape_budget_report.json"
EXPECTED_TOP_LEVEL_KEYS = {
    "base_apex_slack",
    "capacity_deficit_distribution",
    "claim_scope",
    "interpretation",
    "n",
    "provenance",
    "relevant_cyclic_lengths",
    "schema",
    "status",
    "strict_positive_threshold",
    "sum_exceeds_threshold",
    "trust",
    "witness_size",
}
EXPECTED_CLAIM_SCOPE = (
    "Focused n=9 base-apex escape-budget bookkeeping; not a proof of n=9, "
    "not a counterexample, and not a global status update."
)
EXPECTED_INTERPRETATION = [
    "Capacity deficit D is the total unused base-apex capacity in E + D = 9.",
    "Relevant deficits are only deficits placed on length-2 or length-3 bases.",
    "Extra budget not spent on relevant deficits is not assigned to sides or length-4 bases here.",
    "The counts are finite turn-cover escape bookkeeping, not geometric realizability counts.",
    "No proof of the n=9 case is claimed.",
]
EXPECTED_PROVENANCE = {
    "generator": "scripts/explore_n9_base_apex.py",
    "command": (
        "python scripts/explore_n9_base_apex.py --escape-budget-report "
        "--out data/certificates/n9_base_apex_escape_budget_report.json"
    ),
}


def binom2(value: int) -> int:
    """Return binom(value, 2)."""

    if value < 0:
        raise ValueError(f"value must be nonnegative, got {value}")
    return value * (value - 1) // 2


def integer_partitions(total: int, minimum: int = 1) -> Iterable[tuple[int, ...]]:
    """Yield nondecreasing positive integer partitions of total."""

    if total < 0:
        raise ValueError(f"total must be nonnegative, got {total}")
    if total == 0:
        yield ()
        return
    for first in range(minimum, total + 1):
        for rest in integer_partitions(total - first, first):
            yield (first, *rest)


def distance_profiles(n: int, witness_size: int) -> list[tuple[int, tuple[int, ...]]]:
    """Return independently enumerated profile-excess rows."""

    baseline = binom2(witness_size)
    rows = []
    for ascending_parts in integer_partitions(n - 1):
        parts = tuple(reversed(ascending_parts))
        if max(parts, default=0) < witness_size:
            continue
        excess = sum(binom2(part) for part in parts) - baseline
        rows.append((excess, parts))
    return sorted(rows, key=lambda row: (row[0], row[1]))


def base_apex_slack(n: int, witness_size: int) -> int:
    """Return the upper-minus-baseline base-apex slack."""

    return n * (n - 2) - binom2(witness_size) * n


def excess_distributions(
    n: int,
    witness_size: int,
) -> list[tuple[tuple[int, ...], int, int]]:
    """Return sorted unlabeled profile-excess distributions within slack."""

    slack = base_apex_slack(n, witness_size)
    values = [
        excess
        for excess, _parts in distance_profiles(n, witness_size)
        if excess <= slack
    ]
    out: list[tuple[tuple[int, ...], int, int]] = []

    def search(start_index: int, slots_left: int, remaining: int, current: list[int]) -> None:
        if slots_left == 0:
            total = sum(current)
            out.append((tuple(current), total, slack - total))
            return
        for index in range(start_index, len(values)):
            value = values[index]
            if value > remaining:
                break
            current.append(value)
            search(index, slots_left - 1, remaining - value, current)
            current.pop()

    search(0, n, slack, [])
    return sorted(out, key=lambda row: (row[1], row[0]))


def capacity_deficit_distribution(n: int, witness_size: int) -> list[dict[str, int]]:
    """Return profile-ledger counts by capacity deficit."""

    slack = base_apex_slack(n, witness_size)
    counts = Counter(deficit for _excesses, _total, deficit in excess_distributions(n, witness_size))
    return [
        {
            "capacity_deficit": deficit,
            "total_profile_excess": slack - deficit,
            "profile_ledger_count": counts[deficit],
        }
        for deficit in range(slack + 1)
    ]


def turn_clauses_from_saturation(
    n: int,
    saturated_length2: Iterable[int],
    saturated_length3: Iterable[int],
) -> tuple[tuple[int, int], ...]:
    """Return turn-cover clauses forced by length-2 and length-3 saturation."""

    saturated2 = {index % n for index in saturated_length2}
    saturated3 = {index % n for index in saturated_length3}
    clauses = []
    for index in range(n):
        if index in saturated3 and index in saturated2 and (index + 1) % n in saturated2:
            clauses.append(((index + 1) % n, (index + 2) % n))
    return tuple(clauses)


def minimum_turn_hitting_set_size(
    n: int,
    clauses: Iterable[tuple[int, int]],
) -> int:
    """Return the minimum number of turns hitting all two-turn clauses."""

    clause_tuple = tuple(clauses)
    if not clause_tuple:
        return 0
    for size in range(n + 1):
        for selected in itertools.combinations(range(n), size):
            selected_set = set(selected)
            if all(left in selected_set or right in selected_set for left, right in clause_tuple):
                return size
    raise RuntimeError("no hitting set found")


def turn_cover_diagnostic(
    n: int,
    *,
    spoiled_length2: Iterable[int] = (),
    spoiled_length3: Iterable[int] = (),
    contradiction_threshold: int,
) -> dict[str, Any]:
    """Return the independent turn-cover diagnostic for spoiled bases."""

    all_indices = set(range(n))
    saturated_length2 = tuple(sorted(all_indices - {idx % n for idx in spoiled_length2}))
    saturated_length3 = tuple(sorted(all_indices - {idx % n for idx in spoiled_length3}))
    clauses = turn_clauses_from_saturation(n, saturated_length2, saturated_length3)
    minimum_forced_turns = minimum_turn_hitting_set_size(n, clauses)
    return {
        "turn_clauses": clauses,
        "minimum_forced_turns": minimum_forced_turns,
        "forces_turn_contradiction": minimum_forced_turns >= contradiction_threshold,
    }


@lru_cache(maxsize=None)
def minimum_capacity_deficit_to_escape_turn_cover(
    n: int,
    *,
    contradiction_threshold: int,
) -> int:
    """Return the least relevant deficit escaping the turn-cover diagnostic."""

    masks_by_size: dict[int, list[tuple[int, ...]]] = {size: [] for size in range(n + 1)}
    for mask in range(1 << n):
        spoiled = tuple(index for index in range(n) if (mask >> index) & 1)
        masks_by_size[len(spoiled)].append(spoiled)

    for cost in range(2 * n + 1):
        for cost2 in range(max(0, cost - n), min(n, cost) + 1):
            cost3 = cost - cost2
            for spoiled2 in masks_by_size[cost2]:
                for spoiled3 in masks_by_size[cost3]:
                    diagnostic = turn_cover_diagnostic(
                        n,
                        spoiled_length2=spoiled2,
                        spoiled_length3=spoiled3,
                        contradiction_threshold=contradiction_threshold,
                    )
                    if not diagnostic["forces_turn_contradiction"]:
                        return cost
    raise RuntimeError("no escaping deficit pattern found")


def transform_base_index(
    n: int,
    index: int,
    cyclic_length: int,
    *,
    rotation: int,
    reflected: bool,
) -> int:
    """Transform a cyclic base index under a dihedral relabeling."""

    if reflected:
        return (rotation - index - cyclic_length) % n
    return (index + rotation) % n


def canonical_deficit_placement(
    n: int,
    spoiled_length2: Iterable[int],
    spoiled_length3: Iterable[int],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Return a dihedral canonical key for spoiled length-2/length-3 bases."""

    spoiled2 = tuple(spoiled_length2)
    spoiled3 = tuple(spoiled_length3)
    keys = []
    for rotation in range(n):
        for reflected in (False, True):
            keys.append(
                (
                    tuple(
                        sorted(
                            transform_base_index(
                                n,
                                index,
                                2,
                                rotation=rotation,
                                reflected=reflected,
                            )
                            for index in spoiled2
                        )
                    ),
                    tuple(
                        sorted(
                            transform_base_index(
                                n,
                                index,
                                3,
                                rotation=rotation,
                                reflected=reflected,
                            )
                            for index in spoiled3
                        )
                    ),
                )
            )
    return min(keys)


def deficit_placement_classes(
    n: int,
    *,
    relevant_deficit_count: int,
    contradiction_threshold: int,
) -> list[dict[str, Any]]:
    """Return escaping deficit-placement classes up to dihedral symmetry."""

    grouped: Counter[tuple[tuple[int, ...], tuple[int, ...]]] = Counter()
    for count2 in range(max(0, relevant_deficit_count - n), min(n, relevant_deficit_count) + 1):
        count3 = relevant_deficit_count - count2
        for spoiled2 in itertools.combinations(range(n), count2):
            for spoiled3 in itertools.combinations(range(n), count3):
                diagnostic = turn_cover_diagnostic(
                    n,
                    spoiled_length2=spoiled2,
                    spoiled_length3=spoiled3,
                    contradiction_threshold=contradiction_threshold,
                )
                if diagnostic["forces_turn_contradiction"]:
                    continue
                grouped[canonical_deficit_placement(n, spoiled2, spoiled3)] += 1

    out = []
    for (spoiled2, spoiled3), placement_count in grouped.items():
        diagnostic = turn_cover_diagnostic(
            n,
            spoiled_length2=spoiled2,
            spoiled_length3=spoiled3,
            contradiction_threshold=contradiction_threshold,
        )
        out.append(
            {
                "contradiction_threshold": contradiction_threshold,
                "n": n,
                "placement_count": placement_count,
                "relevant_deficit_count": relevant_deficit_count,
                "remaining_minimum_forced_turns": diagnostic["minimum_forced_turns"],
                "remaining_turn_clause_count": len(diagnostic["turn_clauses"]),
                "spoiled_length2": list(spoiled2),
                "spoiled_length3": list(spoiled3),
            }
        )
    return sorted(
        out,
        key=lambda row: (
            len(row["spoiled_length2"]),
            row["spoiled_length2"],
            row["spoiled_length3"],
        ),
    )


def escape_relevant_deficit_counts(
    n: int,
    *,
    relevant_deficit_count: int,
    contradiction_threshold: int,
) -> dict[str, Any]:
    """Return aggregate escape counts for a relevant deficit count."""

    classes = deficit_placement_classes(
        n,
        relevant_deficit_count=relevant_deficit_count,
        contradiction_threshold=contradiction_threshold,
    )
    remaining_counts: Counter[int] = Counter()
    for row in classes:
        remaining_counts[int(row["remaining_minimum_forced_turns"])] += int(row["placement_count"])
    return {
        "total_relevant_placement_count": math.comb(2 * n, relevant_deficit_count),
        "labelled_placement_count": sum(int(row["placement_count"]) for row in classes),
        "dihedral_class_count": len(classes),
        "remaining_minimum_forced_turn_count": {
            str(turns): remaining_counts[turns]
            for turns in sorted(remaining_counts)
        },
    }


def budget_rows(
    n: int,
    witness_size: int,
    *,
    contradiction_threshold: int,
) -> list[dict[str, Any]]:
    """Return independently recomputed escape-budget rows."""

    slack = base_apex_slack(n, witness_size)
    minimum_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    unresolved_counts = Counter(
        deficit
        for _excesses, _total, deficit in excess_distributions(n, witness_size)
        if deficit >= minimum_escape
    )
    counts_by_relevant_deficit = {
        relevant_deficit_count: escape_relevant_deficit_counts(
            n,
            relevant_deficit_count=relevant_deficit_count,
            contradiction_threshold=contradiction_threshold,
        )
        for relevant_deficit_count in range(slack + 1)
    }

    rows = []
    for capacity_budget in range(slack + 1):
        available_counts = [
            relevant_deficit_count
            for relevant_deficit_count in range(capacity_budget + 1)
            if counts_by_relevant_deficit[relevant_deficit_count]["labelled_placement_count"] > 0
        ]
        rows.append(
            {
                "available_relevant_deficit_counts": available_counts,
                "can_spoil_turn_cover_with_relevant_deficits": bool(available_counts),
                "capacity_deficit_budget": capacity_budget,
                "escaping_dihedral_relevant_class_count_by_relevant_deficit": {
                    str(relevant_deficit_count): counts_by_relevant_deficit[
                        relevant_deficit_count
                    ]["dihedral_class_count"]
                    for relevant_deficit_count in available_counts
                },
                "escaping_labelled_relevant_placement_count_by_relevant_deficit": {
                    str(relevant_deficit_count): counts_by_relevant_deficit[
                        relevant_deficit_count
                    ]["labelled_placement_count"]
                    for relevant_deficit_count in available_counts
                },
                "escaping_remaining_forced_turn_counts_by_relevant_deficit": {
                    str(relevant_deficit_count): counts_by_relevant_deficit[
                        relevant_deficit_count
                    ]["remaining_minimum_forced_turn_count"]
                    for relevant_deficit_count in available_counts
                },
                "minimum_relevant_deficit_count_to_spoil": (
                    min(available_counts) if available_counts else None
                ),
                "total_relevant_placement_count_by_relevant_deficit": {
                    str(relevant_deficit_count): counts_by_relevant_deficit[
                        relevant_deficit_count
                    ]["total_relevant_placement_count"]
                    for relevant_deficit_count in range(capacity_budget + 1)
                },
                "unassigned_capacity_after_minimum_relevant_escape": (
                    capacity_budget - minimum_escape
                    if available_counts
                    else None
                ),
                "unresolved_profile_ledger_count_at_budget": unresolved_counts[
                    capacity_budget
                ],
            }
        )
    return rows


def escape_budget_section(
    n: int,
    witness_size: int,
    *,
    contradiction_threshold: int,
) -> dict[str, Any]:
    """Return one independently recomputed threshold section."""

    minimum_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    return {
        "budget_rows": budget_rows(
            n,
            witness_size,
            contradiction_threshold=contradiction_threshold,
        ),
        "contradiction_threshold": contradiction_threshold,
        "minimum_escape_motif_classes": deficit_placement_classes(
            n,
            relevant_deficit_count=minimum_escape,
            contradiction_threshold=contradiction_threshold,
        ),
        "minimum_relevant_deficit_count_to_spoil": minimum_escape,
    }


def expect_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    """Append a compact mismatch error."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded escape-budget artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    top_level_keys = set(payload)
    if top_level_keys != EXPECTED_TOP_LEVEL_KEYS:
        errors.append(
            "top-level keys mismatch: "
            f"expected {sorted(EXPECTED_TOP_LEVEL_KEYS)!r}, got {sorted(top_level_keys)!r}"
        )

    expected_meta = {
        "schema": "erdos97.n9_base_apex_escape_budget_report.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "n": 9,
        "witness_size": 4,
        "base_apex_slack": 9,
        "relevant_cyclic_lengths": [2, 3],
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    n = payload.get("n")
    witness_size = payload.get("witness_size")
    if not isinstance(n, int) or not isinstance(witness_size, int):
        return errors + ["artifact must contain integer n and witness_size"]

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        expect_equal(errors, "claim_scope", claim_scope, EXPECTED_CLAIM_SCOPE)
        lowered = claim_scope.lower()
        for phrase in ("not a proof", "not a counterexample", "not a global status update"):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")

    interpretation = payload.get("interpretation")
    expect_equal(errors, "interpretation", interpretation, EXPECTED_INTERPRETATION)

    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        expect_equal(errors, "provenance", provenance, EXPECTED_PROVENANCE)

    expect_equal(
        errors,
        "capacity_deficit_distribution",
        payload.get("capacity_deficit_distribution"),
        capacity_deficit_distribution(n, witness_size),
    )
    expect_equal(
        errors,
        "strict_positive_threshold",
        payload.get("strict_positive_threshold"),
        escape_budget_section(n, witness_size, contradiction_threshold=3),
    )
    expect_equal(
        errors,
        "sum_exceeds_threshold",
        payload.get("sum_exceeds_threshold"),
        escape_budget_section(n, witness_size, contradiction_threshold=4),
    )
    return errors


def load_artifact(path: Path) -> Any:
    """Load a JSON artifact."""

    return json.loads(path.read_text(encoding="utf-8"))


def display_path(path: Path) -> str:
    """Return a stable repo-relative path when possible."""

    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(path)


def summary_payload(path: Path, payload: Any, errors: Sequence[str]) -> dict[str, Any]:
    """Return a compact checker summary."""

    object_payload = payload if isinstance(payload, dict) else {}
    strict = object_payload.get("strict_positive_threshold", {})
    conservative = object_payload.get("sum_exceeds_threshold", {})
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "n": object_payload.get("n"),
        "witness_size": object_payload.get("witness_size"),
        "strict_minimum_relevant_deficit_count_to_spoil": (
            strict.get("minimum_relevant_deficit_count_to_spoil")
            if isinstance(strict, dict)
            else None
        ),
        "conservative_minimum_relevant_deficit_count_to_spoil": (
            conservative.get("minimum_relevant_deficit_count_to_spoil")
            if isinstance(conservative, dict)
            else None
        ),
        "strict_minimum_escape_motif_class_count": (
            len(strict.get("minimum_escape_motif_classes", []))
            if isinstance(strict, dict)
            else None
        ),
        "conservative_minimum_escape_motif_class_count": (
            len(conservative.get("minimum_escape_motif_classes", []))
            if isinstance(conservative, dict)
            else None
        ),
        "validation_errors": list(errors),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact", type=Path, default=DEFAULT_ARTIFACT)
    parser.add_argument("--check", action="store_true", help="fail if validation fails")
    parser.add_argument("--json", action="store_true", help="print stable JSON")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    artifact = args.artifact if args.artifact.is_absolute() else ROOT / args.artifact

    try:
        payload = load_artifact(artifact)
        errors = validate_payload(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        payload = {}
        errors = [str(exc)]

    summary = summary_payload(artifact, payload, errors)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    elif errors:
        print(f"FAILED: {display_path(artifact)}", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print("n=9 base-apex escape-budget artifact")
        print(f"artifact: {summary['artifact']}")
        print(
            "minimum relevant deficits: "
            f"strict={summary['strict_minimum_relevant_deficit_count_to_spoil']}, "
            f"conservative={summary['conservative_minimum_relevant_deficit_count_to_spoil']}"
        )
        print(
            "minimum escape motif classes: "
            f"strict={summary['strict_minimum_escape_motif_class_count']}, "
            f"conservative={summary['conservative_minimum_escape_motif_class_count']}"
        )
        if args.check:
            print("OK: independent escape-budget checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
