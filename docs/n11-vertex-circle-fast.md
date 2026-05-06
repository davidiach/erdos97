# n=11 vertex-circle fast checker

Status: `MACHINE_CHECKED_FINITE_CASE_ARTIFACT_REVIEW_PENDING`. The wrapper
script is `scripts/check_n11_vertex_circle_fast.py` and the underlying
implementation is `scripts/n11_fast.c`. This is a finite-case
selected-witness checker for Erdos Problem #97; it does not claim a proof of
the general problem and does not claim a counterexample.

## What is checked

Given `n` (default `11`) and `row_size = 4`, the checker labels the candidate
strictly convex polygon vertices `0,...,n-1` in cyclic order and enumerates
selected-witness rows `S_i` for each center vertex `i`. Each row is a
`row_size`-subset of the other vertices. The pruning rules are exactly the
ones recorded in `src/erdos97/n9_vertex_circle_exhaustive.py` and
`src/erdos97/generic_vertex_search.py`:

- two selected rows share at most two witnesses (pair-cap);
- if two selected rows share exactly two witnesses, the source chord and the
  shared-witness chord cross in cyclic order;
- each unordered witness pair occurs in at most `pair_cap = 2` selected rows;
- each target vertex has selected indegree at most
  `floor(2 * (n - 1) / (row_size - 1))` (for `n = 11` this is `6`);
- vertex-circle nested chord strict-monotonicity yields no self-edge or
  strict directed cycle on the quotient graph after fusing the four selected
  pairs at each center.

The same `vertex_circle_status` quotient/cycle check used by the generic
Python checker is reproduced bit-exactly in C.

## Implementation

`scripts/n11_fast.c` is a stand-alone C program that:

- precomputes for the chosen `n` the option list per center, mask bit
  expansions, witness-pair indices, cyclic ordering of witnesses, strict-edge
  list per `(center, mask)`, and a symmetric pairwise compatibility bitset
  table indexed by `(i, j, mi_idx)` returning a 64-bit bitset over
  `options[j]`;
- runs a backtracking search with min-remaining-options center selection
  using a stacked `allowed[depth][center]` bitset that intersects pairwise
  compatibility on every assignment;
- emits one JSON line per `row0` index with the deterministic counts
  `nodes_visited`, `full_assignments`, `partial_self_edge_prunes`,
  `partial_strict_cycle_prunes`, and `elapsed_seconds`.

The Python wrapper `scripts/check_n11_vertex_circle_fast.py` compiles the C
source for the requested `n`, shards `row0` indices across worker processes
with `concurrent.futures`, aggregates per-`row0` counts into a single JSON
artifact, and runs an `n = 9` cross-check against the reference counts in
`src/erdos97/n9_vertex_circle_exhaustive.py`
(`16752` nodes visited, `0` full, `11271` self-edge prunes, `11011`
strict-cycle prunes). For `n = 10` the same binary reproduces the
`4_142_738` total nodes and `0` full assignments recorded in
`data/certificates/n10_vertex_circle_singleton_slices.json`.

The `--fwd-check` switch enables a forward-checking short-circuit: when any
unassigned center's allowed bitset becomes empty after intersecting in the
just-assigned row's compatibility, the recursive call is skipped. This
strictly shrinks `nodes_visited` (because Python recurses there before
detecting the dead-end at depth `+ 1`) but does not alter
`full_assignments`, `partial_self_edge_prunes`, or
`partial_strict_cycle_prunes`. Cross-checks for both `n = 9` and `n = 10`
have been run with and without `--fwd-check` and the deterministic counts
match in every case.

## Reproduction commands

Compile and run the `n = 9` reference cross-check:

```bash
python scripts/check_n11_vertex_circle_fast.py --n 9 --skip-n9-verify --out /tmp/n9_check.json
```

Run a `n = 11` sample (first 30 of 210 row0 choices) with forward checking:

```bash
python scripts/check_n11_vertex_circle_fast.py \
  --n 11 --row0-end 30 --workers 4 --fwd-check
```

The output JSON is written to
`data/certificates/n11_vertex_circle_partial.json` if the slice is not
exhaustive, or `data/certificates/n11_vertex_circle_exhaustive.json` if it
is.

To do a full `n = 11` sweep on a quiet host:

```bash
python scripts/check_n11_vertex_circle_fast.py --n 11 --workers 4 --fwd-check
```

Direct invocation of the C binary (after a one-time compile) is also
supported:

```bash
gcc -O3 -march=native -DNDEBUG -DN_VAL=11 -o /tmp/n11_fast scripts/n11_fast.c
/tmp/n11_fast --start 0 --end 5 --fwd-check
```

The binary emits a JSON-line per `row0` index plus a `_meta` and `_summary`
line. The wrapper aggregates these into the artifact.

## Honest scope notes

- This is a review-pending artifact. Public theorem-style claims still need
  independent review of the necessary-condition pruning rules and their
  geometric necessity, as discussed in `docs/n9-vertex-circle-exhaustive.md`.
- Unlike `n = 9` and `n = 10`, the `n = 11` selected-witness search has
  necessary-condition full survivors at the row0 indices we have measured.
  These survivors are not counterexamples to Erdos #97; they only mean the
  necessary filters in this checker do not, by themselves, suffice to rule
  out `n = 11` and a deeper geometric or sufficiency-style argument is
  required to interpret them.
- The artifact records per-`row0` deterministic counts so partial runs can
  be resumed and aggregated.
