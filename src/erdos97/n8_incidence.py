"""Finite n=8 selected-witness incidence enumeration.

This module enumerates the incidence layer for the n=8 frontier.  It starts
from selected witness systems with row size four and uses only necessary
incidence/geometric filters:

- no loops;
- row-pair intersection cap;
- column-pair cap;
- the n=8 indegree-regularity consequence of the column-pair cap;
- no odd forced-perpendicularity cycle;
- no forced-parallel same-color chord class sharing an endpoint.

The enumeration fixes row 0 to {1,2,3,4}.  This loses no isomorphism classes:
any selected-witness system can be relabelled so that an arbitrary row becomes
row 0 and its four targets become 1,2,3,4.
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable

N = 8
ROW0_CANONICAL_MASK = sum(1 << j for j in [1, 2, 3, 4])
CHORDS = tuple((a, b) for a in range(N) for b in range(a + 1, N))
CHORD_INDEX = {chord: idx for idx, chord in enumerate(CHORDS)}


@dataclass(frozen=True)
class N8IncidenceEnumeration:
    """Compact result of the n=8 incidence enumeration."""

    balanced_cap_matrices_with_row0_fixed: int
    forced_perpendicular_survivors_with_row0_fixed: int
    canonical_survivor_classes: tuple[tuple[int, ...], ...]

    @property
    def class_count(self) -> int:
        return len(self.canonical_survivor_classes)


def bits(mask: int) -> list[int]:
    return [idx for idx in range(N) if (mask >> idx) & 1]


def row_masks_to_matrix(rows: Iterable[int]) -> list[list[int]]:
    return [[1 if (mask >> j) & 1 else 0 for j in range(N)] for mask in rows]


def matrix_to_row_masks(matrix: Iterable[Iterable[int]]) -> tuple[int, ...]:
    out = []
    for row in matrix:
        mask = 0
        for idx, value in enumerate(row):
            if value:
                mask |= 1 << idx
        out.append(mask)
    return tuple(out)


def row_masks_to_strings(rows: Iterable[int]) -> list[str]:
    return ["".join("1" if (mask >> j) & 1 else "0" for j in range(N)) for mask in rows]


def chord(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def n8_column_sum_proof_summary() -> dict[str, object]:
    """Return the finite counting proof that n=8 witness indegrees are all four."""

    max_pair_uses_per_target_pair = 2
    witness_pairs_per_incidence = 3
    possible_partners_for_fixed_vertex = N - 1
    max_pair_uses_for_fixed_vertex = (
        max_pair_uses_per_target_pair * possible_partners_for_fixed_vertex
    )
    max_indegree = max_pair_uses_for_fixed_vertex // witness_pairs_per_incidence
    total_indegree = 4 * N
    return {
        "reason": (
            "If a fixed vertex v occurs in d witness rows, those rows contain "
            "3d pairs {v,a}. For each of the n-1 partners a, the column-pair "
            "cap allows at most two rows containing both v and a. For n=8 this "
            "gives 3d <= 14, hence d <= 4. Since total indegree is 32 across "
            "8 vertices, all indegrees equal 4."
        ),
        "max_pair_uses_per_target_pair": max_pair_uses_per_target_pair,
        "witness_pairs_per_incidence": witness_pairs_per_incidence,
        "possible_partners_for_fixed_vertex": possible_partners_for_fixed_vertex,
        "max_pair_uses_for_fixed_vertex": max_pair_uses_for_fixed_vertex,
        "max_indegree": max_indegree,
        "total_indegree": total_indegree,
        "forced_indegrees": [4] * N,
    }


def _row_options() -> list[list[tuple[int, tuple[int, ...]]]]:
    options = []
    for center in range(N):
        center_options = []
        targets = [j for j in range(N) if j != center]
        for selected in itertools.combinations(targets, 4):
            mask = sum(1 << j for j in selected)
            pair_indices = tuple(CHORD_INDEX[pair] for pair in itertools.combinations(selected, 2))
            center_options.append((mask, pair_indices))
        options.append(center_options)
    options[0] = [
        (
            ROW0_CANONICAL_MASK,
            tuple(CHORD_INDEX[pair] for pair in itertools.combinations([1, 2, 3, 4], 2)),
        )
    ]
    return options


@lru_cache(maxsize=1)
def _canonical_candidate_maps() -> dict[tuple[int, int], tuple[tuple[tuple[int, ...], bytes], ...]]:
    """Maps that make a chosen center row lexicographically minimal.

    A canonical relabelling must send some center to 0 and that center's four
    witnesses to labels 1,2,3,4, because this is the smallest possible first
    row.  This reduces the canonical search from 8! relabellings per pattern to
    8 * 4! * 3! candidates.
    """

    perms4 = list(itertools.permutations(range(1, 5)))
    perms3 = list(itertools.permutations(range(5, 8)))
    transform_cache: dict[tuple[int, ...], tuple[tuple[int, ...], bytes]] = {}
    candidates: dict[tuple[int, int], tuple[tuple[tuple[int, ...], bytes], ...]] = {}

    for center in range(N):
        other_vertices = [j for j in range(N) if j != center]
        for selected in itertools.combinations(other_vertices, 4):
            selected_mask = sum(1 << j for j in selected)
            unselected = [j for j in other_vertices if j not in selected]
            maps = []
            for selected_labels in perms4:
                base = [0] * N
                base[center] = 0
                for old, new in zip(selected, selected_labels):
                    base[old] = new
                for unselected_labels in perms3:
                    old_to_new = base[:]
                    for old, new in zip(unselected, unselected_labels):
                        old_to_new[old] = new
                    old_to_new_key = tuple(old_to_new)
                    item = transform_cache.get(old_to_new_key)
                    if item is None:
                        transformed_masks = bytearray(1 << N)
                        for old_mask in range(1 << N):
                            new_mask = 0
                            work = old_mask
                            while work:
                                lsb = work & -work
                                old_idx = lsb.bit_length() - 1
                                work -= lsb
                                new_mask |= 1 << old_to_new_key[old_idx]
                            transformed_masks[old_mask] = new_mask
                        item = (old_to_new_key, bytes(transformed_masks))
                        transform_cache[old_to_new_key] = item
                    maps.append(item)
            candidates[(center, selected_mask)] = tuple(maps)
    return candidates


def canonical_key(rows: tuple[int, ...]) -> tuple[int, ...]:
    """Canonical simultaneous-relabeling key for an n=8 incidence matrix."""

    best: tuple[int, ...] | None = None
    candidates = _canonical_candidate_maps()
    r0, r1, r2, r3, r4, r5, r6, r7 = rows
    for center in range(N):
        for old_to_new, transformed_mask in candidates[(center, rows[center])]:
            relabelled = [0] * N
            relabelled[old_to_new[0]] = transformed_mask[r0]
            relabelled[old_to_new[1]] = transformed_mask[r1]
            relabelled[old_to_new[2]] = transformed_mask[r2]
            relabelled[old_to_new[3]] = transformed_mask[r3]
            relabelled[old_to_new[4]] = transformed_mask[r4]
            relabelled[old_to_new[5]] = transformed_mask[r5]
            relabelled[old_to_new[6]] = transformed_mask[r6]
            relabelled[old_to_new[7]] = transformed_mask[r7]
            key = tuple(relabelled)
            if best is None or key < best:
                best = key
    assert best is not None
    return best


def forced_perpendicularity_edges(rows: tuple[int, ...]) -> list[tuple[tuple[int, int], tuple[int, int]]]:
    edges = []
    for i in range(N):
        for j in range(i + 1, N):
            common = rows[i] & rows[j]
            if common.bit_count() == 2:
                a, b = bits(common)
                edges.append(((i, j), chord(a, b)))
    return edges


def passes_forced_perpendicularity_filters(rows: tuple[int, ...]) -> bool:
    """Check odd perpendicularity cycles and impossible parallel endpoint sharing."""

    adjacency = [0] * len(CHORDS)
    for source, target in forced_perpendicularity_edges(rows):
        source_idx = CHORD_INDEX[source]
        target_idx = CHORD_INDEX[target]
        adjacency[source_idx] |= 1 << target_idx
        adjacency[target_idx] |= 1 << source_idx

    color = [-1] * len(CHORDS)
    for start in range(len(CHORDS)):
        if color[start] >= 0:
            continue
        color[start] = 0
        stack = [start]
        used_endpoints_by_color = [0, 0]
        while stack:
            current = stack.pop()
            current_color = color[current]
            a, b = CHORDS[current]
            endpoint_bits = (1 << a) | (1 << b)
            if used_endpoints_by_color[current_color] & endpoint_bits:
                return False
            used_endpoints_by_color[current_color] |= endpoint_bits

            neighbors = adjacency[current]
            while neighbors:
                lsb = neighbors & -neighbors
                neighbor = lsb.bit_length() - 1
                neighbors -= lsb
                if color[neighbor] < 0:
                    color[neighbor] = 1 - current_color
                    stack.append(neighbor)
                elif color[neighbor] == current_color:
                    return False
    return True


def enumerate_n8_incidence_classes() -> N8IncidenceEnumeration:
    """Enumerate all n=8 incidence survivor classes under the proved filters."""

    row_options = _row_options()
    rows: list[int] = []
    column_counts = [0] * N
    column_pair_counts = [0] * len(CHORDS)
    balanced_cap_matrices = 0
    forced_survivors = 0
    classes: dict[tuple[int, ...], tuple[int, ...]] = {}

    def search(center: int) -> None:
        nonlocal balanced_cap_matrices, forced_survivors
        if center == N:
            balanced_cap_matrices += 1
            row_tuple = tuple(rows)
            if passes_forced_perpendicularity_filters(row_tuple):
                forced_survivors += 1
                key = canonical_key(row_tuple)
                classes.setdefault(key, key)
            return

        remaining_rows_after_this = N - center - 1
        for mask, pair_indices in row_options[center]:
            if any((mask & previous).bit_count() > 2 for previous in rows):
                continue

            changed_columns = []
            column_ok = True
            for target in range(N):
                if (mask >> target) & 1:
                    if column_counts[target] >= 4:
                        column_ok = False
                        break
                    changed_columns.append(target)
            if not column_ok:
                continue

            for target in changed_columns:
                column_counts[target] += 1

            for target in range(N):
                future_rows_that_can_use_target = remaining_rows_after_this
                if target > center:
                    future_rows_that_can_use_target -= 1
                if column_counts[target] + future_rows_that_can_use_target < 4:
                    column_ok = False
                    break

            pair_ok = column_ok
            changed_pairs = []
            if pair_ok:
                for pair_idx in pair_indices:
                    if column_pair_counts[pair_idx] >= 2:
                        pair_ok = False
                        break
                    changed_pairs.append(pair_idx)

            if pair_ok:
                for pair_idx in changed_pairs:
                    column_pair_counts[pair_idx] += 1
                rows.append(mask)
                search(center + 1)
                rows.pop()
                for pair_idx in changed_pairs:
                    column_pair_counts[pair_idx] -= 1

            for target in changed_columns:
                column_counts[target] -= 1

    search(0)
    return N8IncidenceEnumeration(
        balanced_cap_matrices_with_row0_fixed=balanced_cap_matrices,
        forced_perpendicular_survivors_with_row0_fixed=forced_survivors,
        canonical_survivor_classes=tuple(sorted(classes)),
    )


def existing_reconstructed_survivor_keys(path: Path) -> tuple[tuple[int, ...], ...]:
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    return tuple(sorted(canonical_key(matrix_to_row_masks(record["rows"])) for record in data))


def enumeration_data(existing_survivors_path: Path | None = None) -> dict[str, object]:
    enumeration = enumerate_n8_incidence_classes()
    payload: dict[str, object] = {
        "n": N,
        "status": "INCIDENCE_COMPLETENESS",
        "symmetry_break": {
            "row": 0,
            "witnesses": [1, 2, 3, 4],
            "lossless_reason": (
                "Every selected-witness system can be relabelled so that a chosen "
                "center is 0 and its four selected witnesses are 1,2,3,4."
            ),
        },
        "column_sum_derivation": n8_column_sum_proof_summary(),
        "filters": [
            "zero diagonal",
            "row sums 4",
            "derived column sums 4",
            "row-pair intersections at most 2",
            "column-pair co-occurrences at most 2",
            "no odd forced-perpendicularity cycle",
            "no same-color forced-parallel chords sharing an endpoint",
        ],
        "balanced_cap_matrices_with_row0_fixed": (
            enumeration.balanced_cap_matrices_with_row0_fixed
        ),
        "forced_perpendicular_survivors_with_row0_fixed": (
            enumeration.forced_perpendicular_survivors_with_row0_fixed
        ),
        "canonical_survivor_class_count": enumeration.class_count,
        "canonical_survivor_classes": [
            {
                "canonical_id": idx,
                "rows": row_masks_to_matrix(rows),
                "row_strings": row_masks_to_strings(rows),
            }
            for idx, rows in enumerate(enumeration.canonical_survivor_classes)
        ],
    }
    if existing_survivors_path is not None:
        existing_keys = existing_reconstructed_survivor_keys(existing_survivors_path)
        enumerated_keys = enumeration.canonical_survivor_classes
        payload["matches_existing_reconstructed_survivors"] = existing_keys == enumerated_keys
        payload["existing_reconstructed_survivor_count"] = len(existing_keys)
    return payload


def enumeration_summary(existing_survivors_path: Path | None = None) -> dict[str, object]:
    data = enumeration_data(existing_survivors_path)
    return {
        "n": data["n"],
        "status": data["status"],
        "balanced_cap_matrices_with_row0_fixed": data[
            "balanced_cap_matrices_with_row0_fixed"
        ],
        "forced_perpendicular_survivors_with_row0_fixed": data[
            "forced_perpendicular_survivors_with_row0_fixed"
        ],
        "canonical_survivor_class_count": data["canonical_survivor_class_count"],
        "matches_existing_reconstructed_survivors": data.get(
            "matches_existing_reconstructed_survivors"
        ),
    }
