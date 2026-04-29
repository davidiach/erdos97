# Prompt 3 Run 01 Audit

Status: heuristic/audit note. This file records local review of an AI-generated
prompt result. It is not a proof of Erdos Problem #97 and does not claim a
counterexample.

## Verdict

The run is useful, but mostly as a clarification of what the
minimal-counterexample/fragile-cover route can and cannot do.

Safe takeaways:

1. The fragile-cover lemma is valid and matches the existing
   `docs/claims.md` "Minimal-counterexample critical tie" claim.
2. The pointed `4`-uniform hypergraph translation is valid:
   fragile centers cover all vertices, so a minimal bad polygon has at least
   `n/4` fragile centers.
3. The row-intersection, pair-codegree, overlap-counting, and directed-cycle
   consequences are valid as structural filters.
4. These ingredients are not by themselves contradictory. The run gives
   explicit abstract and geometric warning examples showing why an additional
   metric filter is needed.

Promotion decision:

- Do not add this run as a new theorem-style result.
- Keep it as provenance for the fragile-hypergraph computation route.
- If promoted later, promote only the reviewed filters, with generated
  survivor artifacts or exact infeasibility certificates.

## Checked Claims

### Fragile-Cover Lemma

Claim reviewed:

For a bad polygon `P`, deleting `x` makes a surviving vertex `u` non-bad if
and only if `u` has a unique distance class of size exactly `4` and `x` lies in
that class.

This is correct. The proof properly handles the possible shift of the
maximizing radius after deletion. The key observation is row-local: deleting
`x` removes exactly one entry from the distance multiset at `u`.

For a minimal bad polygon, deleting any vertex `v` makes the remaining polygon
non-bad. Therefore some surviving vertex loses badness, so every `v` lies in
the unique critical `4`-tie of some fragile center.

This is already represented in `docs/claims.md` as the
"Minimal-counterexample critical tie" lemma.

### Hypergraph Translation

Let `F` be the set of fragile centers and let `S_u` be the unique size-`4`
cohort for `u in F`.

The conclusions are valid:

- `|S_u| = 4`;
- `u notin S_u`;
- `V = union_{u in F} S_u`;
- `sum_v d(v) = 4|F|`;
- `|F| >= n/4`.

### Intersection And Codegree Bounds

For distinct fragile centers `u,w`,

`|S_u cap S_w| <= 2`

because two distinct centered circles meet in at most two points.

If equality holds, the convex-position crossing lemma forces the row pair
`{u,w}` to separate the shared column pair.

For a fixed vertex pair `{a,b}`, at most two fragile cohorts can contain both
`a` and `b`, because their centers must lie on the perpendicular bisector of
`p_a p_b`, and strict convexity allows at most two polygon vertices on any
line.

These are valid, and they align with the existing pair-sharing discipline in
the repo.

### Overlap Counting

The identity

`O = sum_{u,w subset F} |S_u cap S_w| = sum_v binom(d(v), 2)`

is valid. The convexity lower bound obtained by balancing cover degrees is
also valid.

Important limitation: overlap counting does not force a double row
intersection. All overlap can be made of single intersections, in which case
the crossing lemma never activates.

### Directed Fragile-Dependency Cycle

Define `u -> w` when `w in S_u`, restricted to `F`.

Since every fragile center is covered by some fragile cohort, every vertex in
this directed graph has indegree at least `1`, so a directed cycle exists.

A shortest directed cycle has no directed chord among its cycle vertices. This
is valid: any non-successor edge on the cycle would shortcut to a shorter
directed cycle.

Scope note: this chordlessness is only inside the selected cycle vertices. The
cycle rows may still contain non-cycle vertices, and non-cycle fragile centers
may interact with the cycle.

## Verified Obstruction Examples

### `Z_13` Linear Cover

The abstract pattern

`S_i = {i+2, i+3, i+5, i+11} mod 13`

was checked locally:

- every row has size `4`;
- `i notin S_i`;
- every column degree is `4`;
- every two rows intersect in exactly one column.

Thus it satisfies the fragile-cover style hypergraph constraints while making
the double-intersection crossing lemma vacuous. It is not claimed to be
geometrically realizable.

### Convex Octagon Warning Example

The run's octagon with cyclic order

`c, u, w, d, e, f, a, b`

was checked locally for strict convexity using oriented edge tests. The stated
unit-distance cohorts also check out:

- `S_u = {w, a, b, c}`;
- `S_w = {u, d, e, f}`.

This demonstrates that even a convex fragile-cover pattern with two disjoint
fragile cohorts can be geometrically harmless. It is not a bad polygon, but it
is a useful guardrail against overinterpreting the cover lemma.

## Recommended Next Use

This run supports the repo's Priority 1 direction: certified
fragile-hypergraph computation.

The next useful step is not more prose around cover/crossing alone. It is a
finite abstraction with an additional metric filter, for example:

1. enumerate pointed `4`-uniform covers satisfying self-exclusion,
   row-intersection, pair-codegree, and cyclic crossing;
2. add filters that encode more geometry than A/B, such as row-wise
   perpendicular-bisector concurrence or angle/side constraints;
3. emit JSON survivors and tests;
4. hand surviving patterns to exact distance-system tooling.

The current result is best treated as a validated filter plus a warning:
fragility alone is real, but it does not close the problem.
