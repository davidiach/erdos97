# Stronger incidence filters for selected-witness search at n >= 11

Status: `DEVELOPMENT_NOTE_FILTER_PROPOSALS_REVIEW_PENDING`.

This note records three new partial-assignment filters intended to be combined
with the existing pair-cap, two-overlap crossing, witness-pair indegree cap,
column indegree cap, and vertex-circle nested-chord filters in
`src/erdos97/generic_vertex_search.py`. None of these filters prove the global
Erdos Problem #97. They prune the selected-witness search tree more
aggressively at `n >= 11`, where the existing filters alone produce roughly
`3.6M` nodes per row0 and `~40` core-hours of total work for full coverage in
pure Python.

The implementation lives in `src/erdos97/stronger_filters.py`. The benchmark
artifact is `data/certificates/stronger_filters_test.json` and is produced by
`scripts/test_stronger_filters.py`.

## Geometric setup recap

For a strictly convex polygon `P` with vertices labeled `0,...,n-1` in cyclic
order, each vertex `i` selects a set `S_i` of four other labels lying on a
common circle centered at `p_i`. The polygon falsifies Erdos Problem #97 iff
every `S_i` has size at least 4. Combinatorial necessary conditions on the
selected sets are:

- L1 (pair-cap): two distinct centers share at most two witnesses (otherwise
  three points have a common pair of equidistant centers, forcing a unique
  circumcenter).
- L2 (no three collinear): three vertices of a strictly convex polygon are
  noncollinear.
- L6 (crossing-bisector): if `S_x cap S_y = {a,b}`, the line `p_x p_y` is the
  perpendicular bisector of `p_a p_b`, so chords `{x,y}` and `{a,b}` cross at
  the midpoint of `p_a p_b`.

## Filter F1: Triple uniqueness

Statement.
A triple `{a,b,c}` of distinct labels appears in at most one row `S_i`.

Proof.
Suppose `{a,b,c} subset S_i cap S_j` for distinct centers `i,j`. By L1, this is
already excluded only if `|S_i cap S_j| >= 3`, but the combinatorial pair-cap
filter does not actually prevent the triple `{a,b,c}` from occurring inside
two different rows when it shares only `<= 2` labels with each. The
straightforward consequence: if the triple sits in both rows, then `p_i` and
`p_j` are both equidistant from `p_a, p_b, p_c`. By L2, `(p_a,p_b,p_c)` are
noncollinear, so they have a unique circumcenter, forcing `p_i = p_j` and
contradicting that polygon vertices are distinct.

Note. This is independent of the existing pair-cap filter because the existing
filter only counts pair overlaps, not triple overlaps.

Implementation. Maintain a counter `triple_counts[T]`. A candidate row mask is
rejected if any of its four 3-subsets already has count `>= 1`. Cost is
`O(binom(4,3)) = O(4)` per node.

## Filter F2: Forced-perpendicularity 2-coloring

Statement.
Build the "forced perpendicularity" graph on chord labels with an undirected
edge `{x,y} -- {a,b}` whenever rows `S_x, S_y` are both assigned and
`|S_x cap S_y| = 2` with shared witnesses `{a,b}`. Then this graph is
2-colorable.

Proof.
By L6, every such edge encodes the geometric assertion "the line `p_x p_y` is
perpendicular to the line `p_a p_b`." Pick any common rotation that makes one
edge horizontal-vertical. Then every chord has a direction that is either
horizontal or vertical (modulo the same rotation), and "perpendicular to" is
exactly "different direction." This is a 2-coloring by horizontal vs.
vertical. Hence an odd cycle in this graph contradicts the existence of any
realization.

Implementation. Run BFS from each chord. A back edge connecting two
same-colored endpoints means odd cycle. Cost is `O(|edges|) = O(|assign|^2)`
worst case per node, but typically far less since the graph is sparse.

Note. This catches the same obstruction as the existing
`odd_forced_perpendicular_cycle` whole-pattern check in
`src/erdos97/incidence_filters.py`, but applied incrementally during the
search instead of only at full-pattern time. It catches contradictions at
shallower depth.

## Filter F3: Mutual-rhombus rational closure

Statement.
For each pair of unordered chords `e = {x,y}` and `f = {a,b}` with both
`phi(e) = f` and `phi(f) = e` in the partial assignment, we have
`p_x + p_y = p_a + p_b`. If exact rational row reduction of the resulting
linear system forces `X_u = X_v` for distinct labels `u, v`, then the partial
assignment cannot be realized by a strictly convex polygon (since `p_u = p_v`
collapses two vertices).

Proof.
This is the mutual-rhombus lemma documented in
`docs/mutual-rhombus-filter.md`. Two reciprocal `phi` images give a pair of
mutual perpendicular bisectors, which forces the midpoints to coincide:
`(p_x+p_y)/2 = (p_a+p_b)/2`. Equivalently, the integer vector
`[1,1,-1,-1]` on labels `(x,y,a,b)` annihilates each coordinate of the vertex
positions. Stacking such rows for every reciprocal pair gives an integer
linear system. If the rational nullspace of the system forces two coordinate
variables to be equal, then no realization exists.

Implementation. Build an integer matrix per partial assignment, run
`Fraction`-based Gaussian elimination, extract a nullspace basis, and union
labels that are forced equal in every basis vector. Cost is dominated by row
reduction, `O(rows * n^2)` per node, and matters only when at least one
mutual-`phi` pair already sits in the partial assignment. The existing
whole-pattern check `mutual_midpoint_matrix` from
`src/erdos97/incidence_filters.py` does the same job at the leaf only.

## Comparison with existing filters

The existing filters `pair-cap`, `two-overlap crossing`, `witness-pair
indegree <= 2`, `column indegree <= 6` (for n=11), and `vertex-circle
nested-chord strict-monotonicity` are pairwise or per-row local. The new
filters F2 and F3 use cross-row consistency on the forced-perpendicularity
graph and on mutual-rhombus midpoints. F1 enforces a triple constraint that
the pair-cap filter cannot see.

At n=9 with vertex-circle pruning, F1 and F3 do not fire (vertex-circle is
strictly stronger here), but F2 produces 4 additional partial-perp odd-cycle
prunes. Without vertex-circle pruning, the combination F1+F2+F3 still leaves
some n=9 patterns alive (only the existing vertex-circle check kills them
all).

At n=11 row0=0 the new filters fire much more often because the partial
assignments are denser. The artifact records concrete counts.

## Trade-offs

F1 is essentially free (constant work per candidate). F2 is cheap on sparse
partial graphs. F3 is the most expensive: each rebuild does rational
elimination. The artifact reports the per-variant elapsed time so the
trade-off can be inspected directly.

If F2 alone gives a 2x or 3x reduction in node count, it is worth its small
per-node cost. If F3 gives an additional 2x but doubles the per-node cost, it
is still net positive.

## Reproduction

```bash
python scripts/test_stronger_filters.py --n11-node-limit 5000
python -m pytest tests/test_stronger_filters.py -q
```

## Caveats

- All three filters are per-pattern necessary conditions, not sufficient.
- The filters do not prove or disprove Erdos #97. The official/global status
  remains falsifiable/open.
- The repo-local source-of-truth result remains the machine-checked
  selected-witness `n <= 8` artifact. The vertex-circle artifacts at n=9 and
  n=10 are review-pending. The n=11 work is exploratory.
- F3 uses pure-Python `fractions.Fraction` arithmetic. For large partial
  assignments (n >= 14) it would benefit from a SymPy or Flint backend.
