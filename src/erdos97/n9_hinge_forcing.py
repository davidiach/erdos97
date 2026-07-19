"""Exact n=9 incidence search with the Kalmanson equilateral hinge forbidden.

The search domain has one selected four-witness row at each of nine cyclically
ordered centers.  It is deliberately small and self-contained: all labels are
fixed, no geometric realization is assumed, and no symmetry quotient is used.

This module proves only a finite implication between the listed combinatorial
axioms.  In particular, it does not prove Erdős Problem #97 and it does not
promote the repository's review-pending n=9 evidence.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
from itertools import combinations
import json
from typing import Iterable, Sequence

from erdos97.kalmanson_equilateral_hinge import (
    dihedral_orientations,
    find_hinge_instances,
)


N = 9
ROW_SIZE = 4
INDEGREE = 4
ROW_INTERSECTION_CAP = 2
WITNESS_PAIR_CAPACITY = 2
ORDER = tuple(range(N))

EXPECTED_BASELINE_NODES = 26_746
EXPECTED_BASELINE_OPTION_CHECKS = 6_710_620
EXPECTED_BASELINE_EXTENSIONS = 26_745
EXPECTED_BASELINE_MAXIMUM_DEPTH = 8
EXPECTED_BASELINE_REJECTIONS = (
    ("indegree_exact_4", 0),
    ("row_intersection_cap_2", 2_588_395),
    ("two_overlap_chord_crossing", 3_359_793),
    ("witness_pair_capacity_2", 0),
    ("kalmanson_equilateral_hinge_free", 206_905),
)
EXPECTED_BASELINE_SHA256 = (
    "3cc536f266fc0c6f563881a63aafdc80a731d1031091054d737334744dcf5b20"
)
EXPECTED_HINGE_COMPILER_REQUIREMENTS = 1_008
EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES = 45_360
EXPECTED_HINGE_COMPILER_SHA256 = (
    "2346b023f8a99f7c45772bb29c19612d0062630e23eeee69d3e1475407df3b03"
)

RowMask = int
Pair = tuple[int, int]
Rows = tuple[tuple[int, ...], ...]


class Axiom(str, Enum):
    """Independently switchable axioms in the fixed n=9 row-system domain."""

    INDEGREE_EXACT_4 = "indegree_exact_4"
    ROW_INTERSECTION_CAP_2 = "row_intersection_cap_2"
    TWO_OVERLAP_CHORD_CROSSING = "two_overlap_chord_crossing"
    WITNESS_PAIR_CAPACITY_2 = "witness_pair_capacity_2"
    KALMANSON_EQUILATERAL_HINGE_FREE = "kalmanson_equilateral_hinge_free"


AXIOMS = tuple(Axiom)


@dataclass(frozen=True)
class AxiomConfig:
    """The five exact constraints enforced by one search."""

    indegree_exact_4: bool = True
    row_intersection_cap_2: bool = True
    two_overlap_chord_crossing: bool = True
    witness_pair_capacity_2: bool = True
    kalmanson_equilateral_hinge_free: bool = True

    def enforces(self, axiom: Axiom | str) -> bool:
        """Return whether ``axiom`` is enabled."""
        normalized = Axiom(axiom)
        return bool(getattr(self, normalized.value))

    def drop(self, axiom: Axiom | str) -> AxiomConfig:
        """Return a copy with exactly ``axiom`` disabled."""
        normalized = Axiom(axiom)
        return replace(self, **{normalized.value: False})

    @property
    def enforced_axioms(self) -> tuple[Axiom, ...]:
        """Return enabled axioms in their stable declaration order."""
        return tuple(axiom for axiom in AXIOMS if self.enforces(axiom))

    @property
    def dropped_axioms(self) -> tuple[Axiom, ...]:
        """Return disabled axioms in their stable declaration order."""
        return tuple(axiom for axiom in AXIOMS if not self.enforces(axiom))


@dataclass(frozen=True)
class SearchStats:
    """Deterministic counters from one exact backtracking traversal."""

    nodes_visited: int
    row_options_examined: int
    extensions_visited: int
    terminal_assignments: int
    terminal_assignment_sha256: str
    maximum_depth: int
    rejection_counts: tuple[tuple[str, int], ...]

    def rejection_count(self, axiom: Axiom | str) -> int:
        """Return the number of option evaluations first rejected by ``axiom``."""
        key = Axiom(axiom).value
        return dict(self.rejection_counts).get(key, 0)

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible representation."""
        return {
            "nodes_visited": self.nodes_visited,
            "row_options_examined": self.row_options_examined,
            "extensions_visited": self.extensions_visited,
            "terminal_assignments": self.terminal_assignments,
            "terminal_assignment_sha256": self.terminal_assignment_sha256,
            "maximum_depth": self.maximum_depth,
            "rejection_counts": dict(self.rejection_counts),
        }


@dataclass(frozen=True)
class SearchResult:
    """Result of a complete UNSAT count or a deterministic first-witness scan."""

    config: AxiomConfig
    stop_after_first: bool
    search_complete: bool
    stats: SearchStats
    witness: Rows | None

    @property
    def satisfiable(self) -> bool:
        """Return whether at least one terminal assignment was found."""
        return self.witness is not None

    @property
    def indegree_exact_4_is_derived(self) -> bool:
        """Return whether the other incidence axioms force exact balance.

        For fixed ``x``, let ``m_xy`` count selected rows containing ``{x,y}``.
        The two boundary pairs have ``m_xy <= 1``: equality two would give two
        rows sharing exactly that pair (the row cap excludes larger overlap),
        whose center chord cannot properly cross the boundary chord.  The six
        other pairs have ``m_xy <= 2`` by witness-pair capacity.  Therefore
        ``3 d_x = sum_y m_xy <= 14``, so ``d_x <= 4``.  The nine row sizes sum
        to 36, forcing every ``d_x`` to equal four.
        """
        return self.witness_pair_capacity_2_is_derived

    @property
    def witness_pair_capacity_2_is_derived(self) -> bool:
        """Return whether row intersection and crossing force pair capacity.

        If three rows contained one witness pair, the three centers would have
        to be pairwise separated by the two open arcs cut by its chord.  Three
        vertices cannot be pairwise separated by a two-part partition.  A
        boundary chord has an empty side, so its capacity is at most one.
        """
        return (
            self.config.row_intersection_cap_2
            and self.config.two_overlap_chord_crossing
        )

    def to_dict(self) -> dict[str, object]:
        """Return the stable payload hashed by :attr:`sha256`."""
        return {
            "schema": "erdos97.n9_hinge_forcing.search_result.v1",
            "n": N,
            "row_size": ROW_SIZE,
            "cyclic_order": list(ORDER),
            "enforced_axioms": [axiom.value for axiom in self.config.enforced_axioms],
            "dropped_axioms": [axiom.value for axiom in self.config.dropped_axioms],
            "indegree_balance": {
                "explicitly_enforced": self.config.indegree_exact_4,
                "derived_from_other_enforced_axioms": self.indegree_exact_4_is_derived,
            },
            "witness_pair_capacity": {
                "explicitly_enforced": self.config.witness_pair_capacity_2,
                "derived_from_other_enforced_axioms": (
                    self.witness_pair_capacity_2_is_derived
                ),
            },
            "stop_after_first": self.stop_after_first,
            "search_complete": self.search_complete,
            "satisfiable": self.satisfiable,
            "stats": self.stats.to_dict(),
            "witness": (
                None if self.witness is None else [list(row) for row in self.witness]
            ),
        }

    @property
    def sha256(self) -> str:
        """Return a stable digest of configuration, counters, and witness."""
        encoded = json.dumps(
            self.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()


@dataclass(frozen=True)
class _HingeRequirement:
    centers: tuple[int, int, int]
    required_masks: tuple[RowMask, RowMask, RowMask]


@dataclass(frozen=True)
class HingeCompilerAudit:
    """Exhaustive comparison of compiled triggers with the public recognizer."""

    requirement_count: int
    public_exact_match_count: int
    satisfaction_table_entry_count: int
    compiler_sha256: str

    def to_dict(self) -> dict[str, object]:
        """Return a deterministic JSON-compatible representation."""
        return {
            "requirement_count": self.requirement_count,
            "public_exact_match_count": self.public_exact_match_count,
            "satisfaction_table_entry_count": self.satisfaction_table_entry_count,
            "compiler_sha256": self.compiler_sha256,
        }


@dataclass
class _MutableStats:
    nodes_visited: int = 0
    row_options_examined: int = 0
    extensions_visited: int = 0
    terminal_assignments: int = 0
    maximum_depth: int = 0


def _mask(values: Iterable[int]) -> RowMask:
    mask = 0
    for value in values:
        mask |= 1 << value
    return mask


def _bits(mask: RowMask) -> tuple[int, ...]:
    return tuple(label for label in ORDER if mask & (1 << label))


def _pair(a: int, b: int) -> Pair:
    return (a, b) if a < b else (b, a)


def _in_open_arc(a: int, b: int, x: int) -> bool:
    return x not in {a, b} and (x - a) % N < (b - a) % N


def chords_cross(first: Pair, second: Pair) -> bool:
    """Return whether two disjoint chords cross in the fixed cyclic order."""
    a, b = first
    c, d = second
    if len({a, b, c, d}) != 4:
        return False
    return _in_open_arc(a, b, c) != _in_open_arc(a, b, d)


PAIRS = tuple(combinations(ORDER, 2))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
ROW_OPTIONS = tuple(
    tuple(
        _mask(witnesses)
        for witnesses in combinations(
            (label for label in ORDER if label != center),
            ROW_SIZE,
        )
    )
    for center in ORDER
)
MASK_BITS = {
    mask: _bits(mask)
    for center_options in ROW_OPTIONS
    for mask in center_options
}
ROW_PAIR_INDICES = {
    mask: tuple(
        PAIR_INDEX[_pair(a, b)] for a, b in combinations(MASK_BITS[mask], 2)
    )
    for center_options in ROW_OPTIONS
    for mask in center_options
}


def _pairwise_flag_tables() -> tuple[
    tuple[tuple[tuple[int, ...], ...] | None, ...],
    ...,
]:
    """Compile row-cap/crossing failures for every ordered center pair."""
    tables: list[list[tuple[tuple[int, ...], ...] | None]] = [
        [None] * N for _ in ORDER
    ]
    for first in ORDER:
        for second in ORDER:
            if first == second:
                continue
            matrix: list[tuple[int, ...]] = []
            for first_row in ROW_OPTIONS[first]:
                flags: list[int] = []
                for second_row in ROW_OPTIONS[second]:
                    shared = first_row & second_row
                    shared_count = shared.bit_count()
                    value = 1 if shared_count > ROW_INTERSECTION_CAP else 0
                    if shared_count == ROW_INTERSECTION_CAP and not chords_cross(
                        _pair(first, second),
                        _pair(*_bits(shared)),
                    ):
                        value |= 2
                    flags.append(value)
                matrix.append(tuple(flags))
            tables[first][second] = tuple(matrix)
    return tuple(tuple(row) for row in tables)


PAIRWISE_FLAGS = _pairwise_flag_tables()


def _compile_hinge_requirements() -> tuple[_HingeRequirement, ...]:
    requirements: list[_HingeRequirement] = []
    for quadruple in combinations(ORDER, 4):
        for a, b, c, d in dihedral_orientations(quadruple):
            requirements.append(
                _HingeRequirement(
                    centers=(a, b, d),
                    required_masks=(
                        _mask((b, c)),
                        _mask((a, c)),
                        _mask((a, b)),
                    ),
                )
            )
    return tuple(requirements)


HINGE_REQUIREMENTS = _compile_hinge_requirements()
SATISFIED_HINGES = tuple(
    tuple(
        tuple(
            index
            for index, requirement in enumerate(HINGE_REQUIREMENTS)
            for required_center, required_mask in zip(
                requirement.centers,
                requirement.required_masks,
            )
            if required_center == center and row & required_mask == required_mask
        )
        for row in ROW_OPTIONS[center]
    )
    for center in ORDER
)


def _would_complete_hinge(
    center: int,
    option_index: int,
    hinge_counts: Sequence[int],
) -> bool:
    return any(
        hinge_counts[index] == 2
        for index in SATISFIED_HINGES[center][option_index]
    )


def _rows_payload(selected: Sequence[RowMask | None]) -> Rows:
    if any(row is None for row in selected):
        raise ValueError("a terminal row payload requires all nine centers")
    return tuple(MASK_BITS[int(row)] for row in selected)


def hinge_instances(rows: Sequence[Sequence[int]]) -> int:
    """Return the public hinge recognizer's exact instance count for ``rows``."""
    return len(find_hinge_instances(rows, ORDER))


def audit_compiled_hinge_semantics() -> HingeCompilerAudit:
    """Replay every compiled hinge trigger through the public recognizer.

    Each of the 1,008 cyclic-quadruple orientations is materialized as three
    minimal rows.  The public API must return exactly that one orientation.
    The option-to-trigger incidence table used during search is also rebuilt
    literally and compared entry-for-entry.
    """
    records: list[dict[str, object]] = []
    for index, requirement in enumerate(HINGE_REQUIREMENTS):
        rows: list[list[int]] = [[] for _ in ORDER]
        for center, required_mask in zip(
            requirement.centers,
            requirement.required_masks,
        ):
            rows[center] = list(_bits(required_mask))
        found = find_hinge_instances(rows, ORDER)
        public_signatures = tuple(
            (
                instance.centers,
                tuple(_mask(pair) for pair in instance.required_pairs),
            )
            for instance in found
        )
        expected_signature = (
            requirement.centers,
            requirement.required_masks,
        )
        if public_signatures != (expected_signature,):
            raise AssertionError(
                f"compiled hinge {index} disagrees with public semantics: "
                f"{public_signatures!r}"
            )
        records.append(
            {
                "centers": list(requirement.centers),
                "required_rows": [
                    list(_bits(required_mask))
                    for required_mask in requirement.required_masks
                ],
            }
        )

    satisfaction_entries = 0
    satisfaction_payload: list[list[list[int]]] = []
    for center in ORDER:
        center_payload: list[list[int]] = []
        for option_index, row in enumerate(ROW_OPTIONS[center]):
            expected = tuple(
                index
                for index, requirement in enumerate(HINGE_REQUIREMENTS)
                for required_center, required_mask in zip(
                    requirement.centers,
                    requirement.required_masks,
                )
                if required_center == center and row & required_mask == required_mask
            )
            actual = SATISFIED_HINGES[center][option_index]
            if actual != expected:
                raise AssertionError(
                    f"satisfaction table mismatch at center {center}, "
                    f"option {option_index}"
                )
            satisfaction_entries += len(actual)
            center_payload.append(list(actual))
        satisfaction_payload.append(center_payload)

    encoded = json.dumps(
        {
            "requirements": records,
            "satisfaction_table": satisfaction_payload,
        },
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return HingeCompilerAudit(
        requirement_count=len(records),
        public_exact_match_count=len(records),
        satisfaction_table_entry_count=satisfaction_entries,
        compiler_sha256=hashlib.sha256(encoded).hexdigest(),
    )


def validate_terminal(rows: Sequence[Sequence[int]], config: AxiomConfig) -> None:
    """Raise ``ValueError`` unless ``rows`` satisfies every enabled axiom."""
    if len(rows) != N:
        raise ValueError(f"expected {N} rows, got {len(rows)}")
    normalized: list[tuple[int, ...]] = []
    for center, row in enumerate(rows):
        values = tuple(row)
        if len(values) != ROW_SIZE or len(set(values)) != ROW_SIZE:
            raise ValueError(f"row {center} must contain four distinct witnesses")
        invalid_type = any(
            isinstance(value, bool) or not isinstance(value, int) for value in values
        )
        if (
            invalid_type
            or center in values
            or any(value not in ORDER for value in values)
        ):
            raise ValueError(f"row {center} contains an invalid witness")
        normalized.append(tuple(sorted(values)))

    if config.indegree_exact_4:
        indegrees = [sum(target in row for row in normalized) for target in ORDER]
        if indegrees != [INDEGREE] * N:
            raise ValueError(f"indegree axiom fails: {indegrees}")

    pair_counts = [0] * len(PAIRS)
    for center, other in combinations(ORDER, 2):
        shared = set(normalized[center]) & set(normalized[other])
        if config.row_intersection_cap_2 and len(shared) > ROW_INTERSECTION_CAP:
            raise ValueError(f"row-intersection axiom fails at {(center, other)}")
        if config.two_overlap_chord_crossing and len(shared) == 2:
            witness_chord = _pair(*tuple(shared))
            if not chords_cross(_pair(center, other), witness_chord):
                raise ValueError(
                    f"two-overlap crossing axiom fails at {(center, other)}"
                )
    for row in normalized:
        for a, b in combinations(row, 2):
            pair_counts[PAIR_INDEX[_pair(a, b)]] += 1
    if config.witness_pair_capacity_2 and max(pair_counts) > WITNESS_PAIR_CAPACITY:
        raise ValueError("witness-pair capacity axiom fails")
    if config.kalmanson_equilateral_hinge_free and hinge_instances(normalized):
        raise ValueError("Kalmanson equilateral hinge-free axiom fails")


def search(
    config: AxiomConfig = AxiomConfig(),
    *,
    stop_after_first: bool = False,
) -> SearchResult:
    """Search the fixed-label domain exactly.

    With ``stop_after_first=False`` the traversal is exhaustive and
    ``terminal_assignments`` is an exact count.  With ``stop_after_first=True``
    a found witness stops the traversal; failure is still an exhaustive UNSAT
    result.
    """
    if not isinstance(config, AxiomConfig):
        raise TypeError("config must be an AxiomConfig")
    if not isinstance(stop_after_first, bool):
        raise TypeError("stop_after_first must be bool")

    selected: list[int | None] = [None] * N
    indegrees = [0] * N
    witness_pair_counts = [0] * len(PAIRS)
    hinge_counts = [0] * len(HINGE_REQUIREMENTS)
    stats = _MutableStats()
    rejection_counts: Counter[str] = Counter({axiom.value: 0 for axiom in AXIOMS})
    terminal_rows: list[Rows] = []
    witness: Rows | None = None
    stopped = False
    dropped = config.dropped_axioms
    priority_axiom = dropped[0] if stop_after_first and len(dropped) == 1 else None

    def relaxation_score(center: int, option_index: int) -> int:
        """Prefer options that actually exercise one dropped axiom."""
        row = ROW_OPTIONS[center][option_index]
        if priority_axiom is Axiom.INDEGREE_EXACT_4:
            return sum(indegrees[target] >= INDEGREE for target in MASK_BITS[row])
        if priority_axiom is Axiom.WITNESS_PAIR_CAPACITY_2:
            return sum(
                witness_pair_counts[index] >= WITNESS_PAIR_CAPACITY
                for index in ROW_PAIR_INDICES[row]
            )
        if priority_axiom is Axiom.KALMANSON_EQUILATERAL_HINGE_FREE:
            return int(_would_complete_hinge(center, option_index, hinge_counts))

        score = 0
        for other_center, other_index in enumerate(selected):
            if other_index is None:
                continue
            table = PAIRWISE_FLAGS[center][other_center]
            assert table is not None
            flags = table[option_index][other_index]
            if priority_axiom is Axiom.ROW_INTERSECTION_CAP_2:
                score += int(bool(flags & 1))
            elif priority_axiom is Axiom.TWO_OVERLAP_CHORD_CROSSING:
                score += int(bool(flags & 2))
        return score

    def first_rejection(center: int, option_index: int) -> Axiom | None:
        stats.row_options_examined += 1
        row = ROW_OPTIONS[center][option_index]
        for other_center, other_index in enumerate(selected):
            if other_index is None:
                continue
            table = PAIRWISE_FLAGS[center][other_center]
            assert table is not None
            flags = table[option_index][other_index]
            if config.row_intersection_cap_2 and flags & 1:
                return Axiom.ROW_INTERSECTION_CAP_2
            if config.two_overlap_chord_crossing and flags & 2:
                return Axiom.TWO_OVERLAP_CHORD_CROSSING

        if config.indegree_exact_4 and any(
            indegrees[target] >= INDEGREE for target in MASK_BITS[row]
        ):
            return Axiom.INDEGREE_EXACT_4
        if config.witness_pair_capacity_2 and any(
            witness_pair_counts[index] >= WITNESS_PAIR_CAPACITY
            for index in ROW_PAIR_INDICES[row]
        ):
            return Axiom.WITNESS_PAIR_CAPACITY_2
        if config.kalmanson_equilateral_hinge_free and _would_complete_hinge(
            center,
            option_index,
            hinge_counts,
        ):
            return Axiom.KALMANSON_EQUILATERAL_HINGE_FREE
        return None

    def valid_options(center: int) -> list[int]:
        valid: list[int] = []
        for option_index in range(len(ROW_OPTIONS[center])):
            rejection = first_rejection(center, option_index)
            if rejection is None:
                valid.append(option_index)
            else:
                rejection_counts[rejection.value] += 1
        if priority_axiom is not None:
            valid.sort(key=lambda index: (-relaxation_score(center, index), index))
        return valid

    def add(center: int, option_index: int) -> None:
        row = ROW_OPTIONS[center][option_index]
        for target in MASK_BITS[row]:
            indegrees[target] += 1
        for index in ROW_PAIR_INDICES[row]:
            witness_pair_counts[index] += 1
        for index in SATISFIED_HINGES[center][option_index]:
            hinge_counts[index] += 1

    def remove(center: int, option_index: int) -> None:
        row = ROW_OPTIONS[center][option_index]
        for index in SATISFIED_HINGES[center][option_index]:
            hinge_counts[index] -= 1
        for index in ROW_PAIR_INDICES[row]:
            witness_pair_counts[index] -= 1
        for target in MASK_BITS[row]:
            indegrees[target] -= 1

    def recurse(depth: int) -> None:
        nonlocal stopped, witness
        if stopped:
            return
        stats.nodes_visited += 1
        stats.maximum_depth = max(stats.maximum_depth, depth)
        if depth == N:
            rows = _rows_payload(
                [
                    None if index is None else ROW_OPTIONS[center][index]
                    for center, index in enumerate(selected)
                ]
            )
            # Replay terminal hinge semantics through the public recognizer.
            validate_terminal(rows, config)
            stats.terminal_assignments += 1
            terminal_rows.append(rows)
            if witness is None:
                witness = rows
            if stop_after_first:
                stopped = True
            return

        best_center: int | None = None
        best_options: list[int] | None = None
        for center in ORDER:
            if selected[center] is not None:
                continue
            options = valid_options(center)
            if best_options is None or len(options) < len(best_options):
                best_center = center
                best_options = options
                if not options:
                    break
        if not best_options:
            return

        assert best_center is not None
        for option_index in best_options:
            selected[best_center] = option_index
            add(best_center, option_index)
            stats.extensions_visited += 1
            recurse(depth + 1)
            remove(best_center, option_index)
            selected[best_center] = None
            if stopped:
                return

    recurse(0)
    terminal_assignment_sha256 = hashlib.sha256(
        json.dumps(
            sorted(terminal_rows),
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    frozen_stats = SearchStats(
        nodes_visited=stats.nodes_visited,
        row_options_examined=stats.row_options_examined,
        extensions_visited=stats.extensions_visited,
        terminal_assignments=stats.terminal_assignments,
        terminal_assignment_sha256=terminal_assignment_sha256,
        maximum_depth=stats.maximum_depth,
        rejection_counts=tuple(
            (axiom.value, int(rejection_counts[axiom.value])) for axiom in AXIOMS
        ),
    )
    return SearchResult(
        config=config,
        stop_after_first=stop_after_first,
        search_complete=not stopped,
        stats=frozen_stats,
        witness=witness,
    )


def baseline_result() -> SearchResult:
    """Return the theorem-strength result without assuming indegree balance."""
    return search(theorem_config())


def assert_expected_baseline(result: SearchResult | None = None) -> None:
    """Assert the pinned exact theorem-strength traversal and digest."""
    if result is None:
        result = baseline_result()
    expected_stats = SearchStats(
        nodes_visited=EXPECTED_BASELINE_NODES,
        row_options_examined=EXPECTED_BASELINE_OPTION_CHECKS,
        extensions_visited=EXPECTED_BASELINE_EXTENSIONS,
        terminal_assignments=0,
        terminal_assignment_sha256=hashlib.sha256(b"[]").hexdigest(),
        maximum_depth=EXPECTED_BASELINE_MAXIMUM_DEPTH,
        rejection_counts=EXPECTED_BASELINE_REJECTIONS,
    )
    if result.config != theorem_config():
        raise AssertionError(f"unexpected baseline config: {result.config!r}")
    if not result.search_complete or result.satisfiable or result.witness is not None:
        raise AssertionError("baseline must be a complete zero-terminal search")
    if result.stats != expected_stats:
        raise AssertionError(f"unexpected baseline stats: {result.stats!r}")
    if result.sha256 != EXPECTED_BASELINE_SHA256:
        raise AssertionError(f"unexpected baseline digest: {result.sha256}")


def theorem_config() -> AxiomConfig:
    """Return hinge forcing from only row intersection, crossing, and no hinge."""
    return AxiomConfig(
        indegree_exact_4=False,
        witness_pair_capacity_2=False,
    )


def drop_one_result(axiom: Axiom | str) -> SearchResult:
    """Drop one axiom and seek the deterministic first SAT witness.

    If no witness exists, the returned result is a complete exhaustive UNSAT
    certificate count rather than a bounded or heuristic failure.
    """
    normalized = Axiom(axiom)
    return search(AxiomConfig().drop(normalized), stop_after_first=True)


def drop_one_results() -> tuple[tuple[Axiom, SearchResult], ...]:
    """Run every single-axiom deletion in stable declaration order."""
    return tuple((axiom, drop_one_result(axiom)) for axiom in AXIOMS)


__all__ = [
    "AXIOMS",
    "EXPECTED_BASELINE_EXTENSIONS",
    "EXPECTED_BASELINE_MAXIMUM_DEPTH",
    "EXPECTED_BASELINE_NODES",
    "EXPECTED_BASELINE_OPTION_CHECKS",
    "EXPECTED_BASELINE_REJECTIONS",
    "EXPECTED_BASELINE_SHA256",
    "EXPECTED_HINGE_COMPILER_REQUIREMENTS",
    "EXPECTED_HINGE_COMPILER_SATISFACTION_ENTRIES",
    "EXPECTED_HINGE_COMPILER_SHA256",
    "N",
    "ORDER",
    "ROW_SIZE",
    "Rows",
    "Axiom",
    "AxiomConfig",
    "SearchResult",
    "SearchStats",
    "HingeCompilerAudit",
    "audit_compiled_hinge_semantics",
    "assert_expected_baseline",
    "baseline_result",
    "chords_cross",
    "drop_one_result",
    "drop_one_results",
    "hinge_instances",
    "search",
    "theorem_config",
    "validate_terminal",
]
