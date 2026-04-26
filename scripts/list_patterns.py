#!/usr/bin/env python3
"""List built-in incidence patterns and basic obstruction statistics."""
from __future__ import annotations

from erdos97.search import built_in_patterns, incidence_obstruction_stats


def main() -> None:
    for p in built_in_patterns().values():
        stats = incidence_obstruction_stats(p.S)
        print(f"{p.name}: n={p.n}, family={p.family}, formula={p.formula}")
        print(
            "  max_common={max_common_selected_neighbors}, indegree=[{indegree_min},{indegree_max}]".format(
                **stats
            )
        )


if __name__ == "__main__":
    main()
