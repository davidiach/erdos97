# n=10 Vertex-circle Exhaustive Check (integrated)

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`.

This note records a repo-native integrated `GenericVertexSearch` run at n=10
covering all 126 row0 choices in a single recursion (no row0 slicing). It does
not claim a general proof of Erdos Problem #97 and does not claim a
counterexample. The official/global status remains falsifiable/open. The
established source-of-truth local result remains the repo-local,
machine-checked selected-witness `n <= 8` artifact until this n=10 package gets
independent review.

The independent companion is the singleton-slice artifact
`data/certificates/n10_vertex_circle_singleton_slices.json` and the doc
`docs/n10-vertex-circle-singleton-slices.md`. The singleton-slice artifact runs
each row0 choice as its own search; this artifact runs the integrated search
that uses the same exact necessary filters but without row0 slicing.

## What is checked

Same exact necessary filters as n=9 (`docs/n9-vertex-circle-exhaustive.md`):

- two selected rows share at most two witnesses;
- if two selected rows share exactly two witnesses, the source chord and
  witness chord cross in the cyclic order;
- each witness pair appears in at most two selected rows;
- each target vertex has selected indegree at most
  `floor(2*(10-1)/(4-1)) = 6`;
- vertex-circle strict chord monotonicity creates no self-edge or strict
  directed cycle after quotienting by selected-distance equalities.

The integrated search uses the dynamic minimum-remaining-options center
ordering inside `GenericVertexSearch.exhaustive_search`, so the visited node
count differs from the singleton-slice run that fixes row0 first and works
strictly cyclically.

## Reproduced counts

The checked-in artifact is
`data/certificates/n10_vertex_circle_exhaustive.json`.

```text
[Pending: filled in once the combined run completes.]
```

Both runs are deterministic given the row order and the
minimum-remaining-options branching.

The cross-check separates the earlier incidence/order filters from the
vertex-circle filter, mirroring the n=9 cross-check.

## Commands

Run the integrated checker and write the artifact:

```bash
python scripts/check_n10_vertex_circle_exhaustive.py --write
```

Run only the main search (vertex-circle pruning) or only the cross-check:

```bash
python scripts/check_n10_vertex_circle_exhaustive.py --main-only
python scripts/check_n10_vertex_circle_exhaustive.py --cross-check-only
```

Apply a per-phase node limit (each phase aborts at this many visited nodes,
useful for partial sweeps):

```bash
python scripts/check_n10_vertex_circle_exhaustive.py --node-limit 50000000
```

## Review standard

Before promoting this to the same source-of-truth status as the `n <= 8`
artifact, an independent review should check:

- the geometric necessity of every pruning rule;
- that the integrated dynamic minimum-remaining-options ordering does not omit
  cases (compare against the singleton-slice artifact totals);
- that row0 is not quotienting by a hidden symmetry in the integrated run;
- that vertex-circle partial pruning uses only already-fixed selected rows and
  selected-distance equalities;
- that the integrated run and singleton-slice run agree on `full_assignments=0`
  and on the cross-check `full_assignments` count (only the partial prune
  totals are expected to differ because the search trees differ).
