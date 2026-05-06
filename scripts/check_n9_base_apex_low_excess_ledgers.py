#!/usr/bin/env python3
"""Independently validate the n=9 base-apex low-excess ledger artifact."""

from __future__ import annotations

import argparse
import itertools
import json
import sys
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ARTIFACT = ROOT / "data" / "certificates" / "n9_base_apex_low_excess_ledgers.json"


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


def profile_by_excess(n: int, witness_size: int) -> dict[int, tuple[int, ...]]:
    """Return the unique n=9 profile for each excess value."""

    grouped: dict[int, list[tuple[int, ...]]] = {}
    for excess, parts in distance_profiles(n, witness_size):
        grouped.setdefault(excess, []).append(parts)
    ambiguous = {excess: parts for excess, parts in grouped.items() if len(parts) != 1}
    if ambiguous:
        raise ValueError(f"profile excess is not unique: {ambiguous}")
    return {excess: parts[0] for excess, parts in grouped.items()}


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


def capacity_deficit_forces_turn_cover(
    capacity_deficit: int,
    n: int,
    *,
    contradiction_threshold: int,
) -> bool:
    """Return whether every placement of this deficit still forces closure."""

    escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    return capacity_deficit < escape


def turn_cover_distribution_summary(
    n: int,
    witness_size: int,
    *,
    contradiction_threshold: int,
) -> dict[str, Any]:
    """Summarize distributions closed by the turn-cover diagnostic."""

    distributions = excess_distributions(n, witness_size)
    escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=contradiction_threshold,
    )
    forced_count = sum(
        1
        for _excesses, _total, deficit in distributions
        if deficit < escape
    )
    deficit_counts = Counter(deficit for _excesses, _total, deficit in distributions)
    return {
        "capacity_deficit_counts": {
            str(deficit): deficit_counts[deficit]
            for deficit in sorted(deficit_counts)
        },
        "contradiction_threshold": contradiction_threshold,
        "distribution_count": len(distributions),
        "forced_by_turn_cover_count": forced_count,
        "minimum_capacity_deficit_to_escape": escape,
        "unresolved_by_turn_cover_count": len(distributions) - forced_count,
    }


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


def unresolved_ledger_rows(
    n: int,
    witness_size: int,
    *,
    contradiction_threshold: int,
) -> list[dict[str, Any]]:
    """Return independently recomputed unresolved profile-ledger rows."""

    profiles = profile_by_excess(n, witness_size)
    rows = []
    for excesses, total, deficit in excess_distributions(n, witness_size):
        forced = capacity_deficit_forces_turn_cover(
            deficit,
            n,
            contradiction_threshold=contradiction_threshold,
        )
        if forced:
            continue
        rows.append(
            {
                "capacity_deficit": deficit,
                "excesses": list(excesses),
                "forced_by_turn_cover": False,
                "profile_multiset": [
                    list(profiles[excess])
                    for excess in excesses
                ],
                "total_profile_excess": total,
            }
        )
    return rows


def count_by_key(rows: Sequence[dict[str, Any]], key: str) -> dict[str, int]:
    """Count integer row values with JSON string keys."""

    counts = Counter(int(row[key]) for row in rows)
    return {str(value): counts[value] for value in sorted(counts)}


def expect_equal(
    errors: list[str],
    label: str,
    actual: Any,
    expected: Any,
) -> None:
    """Append a compact mismatch error."""

    if actual != expected:
        errors.append(f"{label} mismatch: expected {expected!r}, got {actual!r}")


def validate_payload(payload: Any) -> list[str]:
    """Return validation errors for a loaded ledger artifact."""

    if not isinstance(payload, dict):
        return ["artifact top level must be a JSON object"]

    errors: list[str] = []
    n = payload.get("n")
    witness_size = payload.get("witness_size")
    if not isinstance(n, int) or not isinstance(witness_size, int):
        return ["artifact must contain integer n and witness_size"]

    expected_meta = {
        "schema": "erdos97.n9_base_apex_low_excess_ledgers.v1",
        "status": "EXPLORATORY_LEDGER_ONLY",
        "trust": "FINITE_BOOKKEEPING_NOT_A_PROOF",
        "n": 9,
        "witness_size": 4,
        "base_apex_slack": base_apex_slack(9, 4),
    }
    for key, expected in expected_meta.items():
        expect_equal(errors, key, payload.get(key), expected)

    claim_scope = payload.get("claim_scope")
    if not isinstance(claim_scope, str):
        errors.append("claim_scope must be a string")
    else:
        lowered = claim_scope.lower()
        for phrase in ("not a proof", "not a counterexample", "not a global status update"):
            if phrase not in lowered:
                errors.append(f"claim_scope must include {phrase!r}")

    notes = payload.get("notes")
    if not isinstance(notes, list) or "No proof of the n=9 case is claimed." not in notes:
        errors.append("notes must preserve the explicit no-proof statement")

    provenance = payload.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance must be an object")
    else:
        expect_equal(
            errors,
            "provenance.generator",
            provenance.get("generator"),
            "scripts/explore_n9_base_apex.py",
        )
        command = provenance.get("command")
        if not isinstance(command, str) or "--low-excess-report" not in command:
            errors.append("provenance.command must name the low-excess generator command")

    computed_profiles = distance_profiles(n, witness_size)
    used_profile_excesses = {
        excess
        for row in payload.get("strict_unresolved_profile_ledgers", [])
        if isinstance(row, dict)
        for excess in row.get("excesses", [])
    }
    available_excesses = {excess for excess, _parts in computed_profiles}
    if not used_profile_excesses.issubset(available_excesses):
        errors.append("ledger uses profile excess values outside the partition table")
    artifact_slack = payload.get("base_apex_slack")
    if isinstance(artifact_slack, int) and any(
        excess > artifact_slack for excess in used_profile_excesses
    ):
        errors.append("ledger uses profile excess values above the base-apex slack")

    strict_summary = turn_cover_distribution_summary(
        n,
        witness_size,
        contradiction_threshold=3,
    )
    conservative_summary = turn_cover_distribution_summary(
        n,
        witness_size,
        contradiction_threshold=4,
    )
    expect_equal(errors, "strict_turn_cover_summary", payload.get("strict_turn_cover_summary"), strict_summary)
    expect_equal(
        errors,
        "conservative_turn_cover_summary",
        payload.get("conservative_turn_cover_summary"),
        conservative_summary,
    )

    expected_rows = unresolved_ledger_rows(n, witness_size, contradiction_threshold=3)
    actual_rows = payload.get("strict_unresolved_profile_ledgers")
    expect_equal(errors, "strict_unresolved_profile_ledgers", actual_rows, expected_rows)
    expect_equal(
        errors,
        "strict_unresolved_profile_ledger_count",
        payload.get("strict_unresolved_profile_ledger_count"),
        len(expected_rows),
    )
    expect_equal(
        errors,
        "strict_unresolved_count_by_total_profile_excess",
        payload.get("strict_unresolved_count_by_total_profile_excess"),
        count_by_key(expected_rows, "total_profile_excess"),
    )
    expect_equal(
        errors,
        "strict_unresolved_count_by_capacity_deficit",
        payload.get("strict_unresolved_count_by_capacity_deficit"),
        count_by_key(expected_rows, "capacity_deficit"),
    )
    if any(row.get("forced_by_turn_cover") is not False for row in expected_rows):
        errors.append("internal error: expected rows must all be unresolved")

    strict_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=3,
    )
    conservative_escape = minimum_capacity_deficit_to_escape_turn_cover(
        n,
        contradiction_threshold=4,
    )
    expect_equal(
        errors,
        "strict_minimum_escape_motif_classes",
        payload.get("strict_minimum_escape_motif_classes"),
        deficit_placement_classes(
            n,
            relevant_deficit_count=strict_escape,
            contradiction_threshold=3,
        ),
    )
    expect_equal(
        errors,
        "conservative_minimum_escape_motif_classes",
        payload.get("conservative_minimum_escape_motif_classes"),
        deficit_placement_classes(
            n,
            relevant_deficit_count=conservative_escape,
            contradiction_threshold=4,
        ),
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
    strict_motifs = object_payload.get("strict_minimum_escape_motif_classes", [])
    conservative_motifs = object_payload.get(
        "conservative_minimum_escape_motif_classes",
        [],
    )
    return {
        "ok": not errors,
        "artifact": display_path(path),
        "schema": object_payload.get("schema"),
        "status": object_payload.get("status"),
        "trust": object_payload.get("trust"),
        "n": object_payload.get("n"),
        "witness_size": object_payload.get("witness_size"),
        "strict_unresolved_profile_ledger_count": object_payload.get(
            "strict_unresolved_profile_ledger_count"
        ),
        "strict_minimum_escape_motif_class_count": (
            len(strict_motifs) if isinstance(strict_motifs, list) else None
        ),
        "conservative_minimum_escape_motif_class_count": (
            len(conservative_motifs) if isinstance(conservative_motifs, list) else None
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
        print("n=9 base-apex low-excess ledger artifact")
        print(f"artifact: {summary['artifact']}")
        print(f"strict unresolved ledgers: {summary['strict_unresolved_profile_ledger_count']}")
        print(
            "minimum escape motif classes: "
            f"strict={summary['strict_minimum_escape_motif_class_count']}, "
            f"conservative={summary['conservative_minimum_escape_motif_class_count']}"
        )
        if args.check:
            print("OK: independent ledger checks passed")

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
