#!/usr/bin/env python3
"""Exact finite verifier for the n=9 checkpoint in the Erdős 97 search.

The script enumerates selected-witness patterns W_i for a cyclically labelled
nonagon subject only to three necessary conditions for a strictly convex bad
nonagon:

1. each row W_i is a 4-subset of {0,...,8}\{i};
2. two selected circles share at most two selected witnesses;
3. for every base pair {a,b}, at most one selected apex over {a,b} lies on
   each side of the chord ab (equivalently, each cyclic arc between a and b).

It then quotients the complete graph distances by the selected equalities
|i-a|=|i-b| for a,b in W_i.  A strict convex nonagon must satisfy the strict
Kalmanson inequalities for distances.  The verifier checks that every remaining
pattern forces at least one strict Kalmanson gap to be identically zero after
this quotient.

No floating point arithmetic or optimization is used.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from itertools import combinations

N = 9
VERTICES = tuple(range(N))
PAIRS = tuple(combinations(VERTICES, 2))
PAIR_INDEX = {pair: idx for idx, pair in enumerate(PAIRS)}
QUADS = tuple(combinations(VERTICES, 4))


def pair(a: int, b: int) -> tuple[int, int]:
    return (a, b) if a < b else (b, a)


def side_of_base(a: int, b: int, c: int) -> int:
    """Return which cyclic side of the base {a,b} contains c.

    For a<b, side 0 is the open interval a<c<b in the chosen cyclic labelling;
    side 1 is the complementary open arc.  This matches the two sides of the
    chord in a strictly convex polygon.
    """

    a, b = pair(a, b)
    return 0 if a < c < b else 1


def build_row_choices() -> list[list[tuple[int, int, tuple[int, ...]]]]:
    """Return row choices with bitmasks for fast exact backtracking."""

    slot_index: dict[tuple[int, int, int], int] = {}
    slot_count = 0
    for a, b in PAIRS:
        for side in (0, 1):
            slot_index[(a, b, side)] = slot_count
            slot_count += 1

    choices: list[list[tuple[int, int, tuple[int, ...]]]] = []
    for center in VERTICES:
        row: list[tuple[int, int, tuple[int, ...]]] = []
        others = [v for v in VERTICES if v != center]
        for witnesses in combinations(others, 4):
            vertex_mask = sum(1 << v for v in witnesses)
            slot_mask = 0
            for a, b in combinations(witnesses, 2):
                aa, bb = pair(a, b)
                slot_mask |= 1 << slot_index[(aa, bb, side_of_base(aa, bb, center))]
            row.append((vertex_mask, slot_mask, witnesses))
        choices.append(row)
    return choices


def enumerate_patterns() -> list[tuple[tuple[int, ...], ...]]:
    """Enumerate all labelled selected-witness patterns satisfying the filters."""

    choices = build_row_choices()
    remaining = set(VERTICES)
    selected: list[tuple[int, int, tuple[int, ...]] | None] = [None] * N
    patterns: list[tuple[tuple[int, ...], ...]] = []

    def search(used_slots: int) -> None:
        if not remaining:
            patterns.append(tuple(item[2] for item in selected if item is not None))
            return

        best_center = None
        best_valid = None
        for center in list(remaining):
            valid = []
            for vertex_mask, slot_mask, witnesses in choices[center]:
                if used_slots & slot_mask:
                    continue
                if any(
                    item is not None and (vertex_mask & item[0]).bit_count() > 2
                    for item in selected
                ):
                    continue
                valid.append((vertex_mask, slot_mask, witnesses))
            if best_valid is None or len(valid) < len(best_valid):
                best_center = center
                best_valid = valid
                if not valid:
                    break

        if not best_valid or best_center is None:
            return

        remaining.remove(best_center)
        for item in best_valid:
            selected[best_center] = item
            search(used_slots | item[1])
            selected[best_center] = None
        remaining.add(best_center)

    search(0)
    return patterns


def transform_label(x: int, rotation: int, reflected: bool) -> int:
    return (rotation - x) % N if reflected else (x + rotation) % N


def canonical_pattern(pattern: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    """Return the lexicographically least dihedral relabelling."""

    keys = []
    for rotation in VERTICES:
        for reflected in (False, True):
            transformed: list[tuple[int, ...] | None] = [None] * N
            for center, witnesses in enumerate(pattern):
                new_center = transform_label(center, rotation, reflected)
                transformed[new_center] = tuple(
                    sorted(transform_label(w, rotation, reflected) for w in witnesses)
                )
            keys.append(tuple(row for row in transformed if row is not None))
    return min(keys)


class DSU:
    def __init__(self, size: int) -> None:
        self.parent = list(range(size))

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> None:
        ra = self.find(a)
        rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra


def equality_dsu(pattern: tuple[tuple[int, ...], ...]) -> DSU:
    """Build the quotient of distance variables forced by selected rows."""

    dsu = DSU(len(PAIRS))
    for center, witnesses in enumerate(pattern):
        base = PAIR_INDEX[pair(center, witnesses[0])]
        for witness in witnesses[1:]:
            dsu.union(base, PAIR_INDEX[pair(center, witness)])
    return dsu


def distance_class(dsu: DSU, a: int, b: int) -> int:
    return dsu.find(PAIR_INDEX[pair(a, b)])


def zero_kalmanson_gap(
    pattern: tuple[tuple[int, ...], ...]
) -> tuple[int, int, int, int, str] | None:
    """Find a strict Kalmanson inequality forced to equality, if any."""

    dsu = equality_dsu(pattern)
    for a, b, c, d in QUADS:
        plus = sorted((distance_class(dsu, a, c), distance_class(dsu, b, d)))
        minus_a = sorted((distance_class(dsu, a, b), distance_class(dsu, c, d)))
        if plus == minus_a:
            return (a, b, c, d, "A")
        minus_b = sorted((distance_class(dsu, a, d), distance_class(dsu, b, c)))
        if plus == minus_b:
            return (a, b, c, d, "B")
    return None


def row_string(pattern: tuple[tuple[int, ...], ...]) -> str:
    return "; ".join(f"{i}:{''.join(map(str, row))}" for i, row in enumerate(pattern))


def gap_string(gap: tuple[int, int, int, int, str]) -> str:
    a, b, c, d, kind = gap
    if kind == "A":
        return f"K_A({a},{b},{c},{d}): d{a}{c}+d{b}{d} > d{a}{b}+d{c}{d}"
    return f"K_B({a},{b},{c},{d}): d{a}{c}+d{b}{d} > d{a}{d}+d{b}{c}"


def main() -> None:
    patterns = enumerate_patterns()
    classes: dict[tuple[tuple[int, ...], ...], list[tuple[tuple[int, ...], ...]]] = defaultdict(list)
    for pattern in patterns:
        classes[canonical_pattern(pattern)].append(pattern)

    certified = []
    for canonical, orbit in sorted(classes.items()):
        gap = zero_kalmanson_gap(canonical)
        if gap is None:
            raise AssertionError(f"No zero Kalmanson gap found for {canonical}")
        certified.append((canonical, len(orbit), gap))

    orbit_sizes = Counter(size for _, size, _ in certified)
    print(f"labelled_patterns={len(patterns)}")
    print(f"dihedral_classes={len(certified)}")
    print(f"orbit_size_distribution={dict(sorted(orbit_sizes.items()))}")
    print("certificates:")
    for idx, (canonical, orbit_size, gap) in enumerate(certified, start=1):
        print(f"{idx:02d}. orbit={orbit_size:2d}; {gap_string(gap)}; rows={row_string(canonical)}")

    assert len(patterns) == 184
    assert len(certified) == 16
    assert sum(size for _, size, _ in certified) == 184
    print("status=PASS")


if __name__ == "__main__":
    main()
