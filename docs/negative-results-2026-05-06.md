# 2026-05-06 negative diagnostics archive

Status: `REVIEW_PENDING_PROVENANCE`.

This note archives a small, CI-clean subset of the 2026-05-06 negative-result
drafts. It records diagnostics that did not produce a proof, a counterexample,
or a source-of-truth status change.

The official/global Erdős #97 status remains falsifiable/open. The strongest
local finite-case result remains the repo-local `n <= 8` selected-witness
artifact. Numerical or heuristic failures below are not exact obstructions
unless a verifier says so.

## Q-L9 Diagnostic

`scripts/check_q_l9_filter.py` scans coordinate-bearing artifacts in
`data/runs/` and computes the ratio

```text
eps(P) / delta_min(P)
```

where `eps(P)` is radial deviation from a best-fit circle and `delta_min(P)`
is minimum vertex separation. The diagnostic threshold used here is `0.25`.

The checked artifact is
`data/certificates/2026-05-06/q_l9_filter_results.json`. On the current
coordinate-bearing run artifacts it records:

```text
n_artifacts: 9
n_pass_filter: 9
n_blocked: 0
threshold: 0.25
```

This is negative filter information only: it does not certify realizability,
and passing the diagnostic is not evidence of a counterexample.

Run:

```bash
python scripts/check_q_l9_filter.py --threshold 0.25 --write data/certificates/2026-05-06/q_l9_filter_results.json
```

## Two-Orbit Large-M Ansatz

`data/certificates/2026-05-06/two_orbit_large_m.json` records a two-orbit
ansatz scan for

```text
m in {14, 15, 16, 18, 20, 25, 30}
n in {28, 30, 32, 36, 40, 50, 60}
```

The archived artifact reports no strictly convex survivors and an empty
`survivors` list for every tested `m`. This is an ansatz-level negative
result only. It does not rule out other incidence patterns, other cyclic
orders, or arbitrary `n`.

The broad PR draft included a generator with an absolute local output path.
That script is intentionally not imported here; the archived JSON is kept as
provenance until a repo-native generator is written.

## Affine Stretch Search

`data/certificates/2026-05-06/affine_stretch_search.json` records another
negative numerical/search diagnostic from the same draft round. It is retained
as search-history provenance only and should not be cited as an exact
obstruction.

## Fast Vertex Search

`src/erdos97/fast_vertex_search.py` is a bitset-based selected-witness search
prototype intended to make larger vertex-circle searches cheaper. This branch
adds it as an experimental implementation with a smoke test only. It is not
wired into the source-of-truth finite-case pipeline.

Audit expectations before relying on it:

- compare its full counts against `GenericVertexSearch` on n=9 and n=10 slices;
- review the row-0 reflection symmetry and orbit-factor handling;
- verify that incremental union-find rollback is sound;
- keep performance improvements separate from mathematical claim promotion.
