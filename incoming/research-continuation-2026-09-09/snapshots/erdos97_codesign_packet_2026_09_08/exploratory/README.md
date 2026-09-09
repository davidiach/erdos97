# Bounded numerical co-design search

These files are **exploration, not exact evidence**. Python, NumPy, and SciPy
are required. The exact packet does not import these files.

```sh
OPENBLAS_NUM_THREADS=1 python exploratory/search_codesign.py
```

Eight trajectories were run: two each at 12 and 15 vertices, two free
18-vertex starts, and two independently perturbed starts at the exact
18-point repair. Each has two stages with a potentially changed four-witness
table. All coordinates are free; no C3 symmetry or inherited witness row is
imposed on the optimizer. Starting-table selection uses circulant label
patterns as a fallback, followed by independently tested row mutations.

Preflight is exact **only for the implemented necessary conditions**: valid
rows, three common circle witnesses after distance-equality closure, and
strict Kalmanson contradictions that reduce directly to equality of the
same two distance classes. It is not full Kalmanson-cone feasibility or a
complete geometric preflight.

The optimizer uses hard inequalities for supporting determinants and pair
separation, plus centroid and scale equalities. SLSQP outputs, success flags,
and small constraint residuals are numerical diagnostics, never exact
certificates. No near-zero all-rich realization was found; final maximum
selected squared-distance spreads remained large. This weakens confidence
in this particular search heuristic, not in the existence of a counterexample.

An initial soft-penalty optimizer repeatedly sacrificed scale, separation,
and convexity. It was replaced rather than counting those degeneracies as
near-misses. Likewise, initially choosing near-distance quartets
independently frequently failed exact preflight before optimization. Neither
observation is an exhaustive obstruction.

The eight final coordinate arrays, all selected rows, preflight counts,
solver termination details, and before/after measurements are retained in
`codesign_search.json`. Timings and solver iterations may vary across
numerical environments. No publication or global-status claim depends on
reproducing them bit-for-bit.

Final delivery replay used NumPy 2.3.5 and SciPy 1.17.0 with
`OPENBLAS_NUM_THREADS=1` and reproduced the complete JSON report byte-for-byte.
The eight summary lines are preserved in `replay_output.txt`. This is
repeated execution of a heuristic, not independent validation of a solution.
