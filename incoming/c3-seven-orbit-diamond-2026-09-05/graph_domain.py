"""Exact radial-domain enumeration and local-rule replay, with no solver."""
from __future__ import annotations
from itertools import permutations
from common_supplier_background import enumerate_radial_graphs, copair_obstructions

def contains_diamond(rows: list[int]) -> tuple[int, int, int, int] | None:
    for a, b, c, d in permutations(range(len(rows)), 4):
        if rows[a] >> b & 1 and rows[a] >> c & 1 and rows[b] >> c & 1 and rows[b] >> d & 1 and rows[c] >> d & 1:
            return (a, b, c, d)
    return None

def ascending_transitive(rows: list[int]) -> tuple[int, int, int] | None:
    for a in range(len(rows)):
        for b in range(a + 1, len(rows)):
            for c in range(b + 1, len(rows)):
                if rows[a] >> b & 1 and rows[b] >> c & 1 and rows[a] >> c & 1:
                    return (a, b, c)
    return None

def generate(n: int=7) -> tuple[list[list[int]], dict]:
    rows, stats = enumerate_radial_graphs(n)
    pair_clean = [g for g in rows if not copair_obstructions(g)]
    diamond_clean = [g for g in pair_clean if contains_diamond(g) is None]
    final = sorted((g for g in diamond_clean if ascending_transitive(g) is None))
    return (final, {'orbits': n, 'after_radial_path': len(rows), 'after_common_supplier': len(pair_clean), 'after_diamond': len(diamond_clean), 'after_transitive_radius_order': len(final), 'brancher_counters': stats})

def target_graph() -> list[int]:
    return [sum((1 << j for j in row)) for row in [(1, 2), (4, 6), (1, 6), (0, 6), (2, 3), (1, 3), (4, 5)]]

def phase_count(graphs: list[list[int]]) -> int:
    from math import factorial
    return sum((factorial(len(g) - 1) * 2 ** sum((g[a] >> b & 1 for a in range(len(g)) for b in range(a + 1, len(g)))) for g in graphs))

def input_text(graphs: list[list[int]]) -> str:
    return ''.join((' '.join((str(j) for i in range(len(g)) for j in range(len(g)) if g[i] >> j & 1)) + '\n' for g in graphs))
