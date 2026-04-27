# n=8 Incidence Completeness

Status: `INCIDENCE_COMPLETENESS`.

This note records the incidence layer for the `n=8` finite case. It is paired
with the exact survivor obstruction note in `docs/n8-exact-survivors.md`.

## Necessary Incidence Facts

For a selected-witness system `W_i`, every row has size 4 and excludes its own
center. The two basic caps are:

```text
|W_i cap W_j| <= 2
```

for distinct centers `i,j`, and:

```text
#{i : {a,b} subset W_i} <= 2
```

for each unordered witness pair `{a,b}`. The second cap follows because every
such center lies on the perpendicular bisector of segment `ab`, and a line meets
a strictly convex polygon in at most two vertices.

For `n=8`, this second cap forces every witness indegree to equal 4. If a fixed
vertex `v` appears in `d` rows, those rows contribute `3d` pairs `{v,a}`. There
are 7 possible partners `a`, and each pair can occur in at most two rows, so:

```text
3d <= 14
```

Thus `d <= 4`. Since the total indegree is `4n = 32`, all 8 indegrees are
exactly 4.

## Enumeration

The enumerator fixes row 0 to witnesses `{1,2,3,4}`. This loses no isomorphism
classes, because any selected-witness system can be relabelled so that a chosen
center is 0 and its four witnesses are 1,2,3,4.

It then exhaustively enumerates matrices satisfying:

```text
- zero diagonal;
- row sums 4;
- derived column sums 4;
- row-pair intersections at most 2;
- column-pair co-occurrences at most 2;
- no odd forced-perpendicularity cycle;
- no same-color forced-parallel chord class sharing an endpoint.
```

The last two filters are necessary geometric obstructions. If two rows share
exactly two witnesses, the center chord is perpendicular to the common-witness
chord. Odd cycles in this perpendicularity graph are impossible. Chords in the
same color class of a bipartite perpendicularity component are forced parallel;
two such chords sharing an endpoint would force three collinear polygon
vertices.

## Counts

The checked artifact records:

```text
balanced cap matrices with row 0 fixed:      117072
forced-perpendicular survivors with row 0 fixed: 4560
canonical survivor classes up to relabeling:    15
```

The 15 canonical classes match `data/incidence/n8_reconstructed_15_survivors.json`
exactly up to simultaneous relabeling.

## Reproduction

Run:

```bash
python scripts/enumerate_n8_incidence.py --summary
python scripts/enumerate_n8_incidence.py --check-data data/incidence/n8_incidence_completeness.json
python -m pytest tests/test_n8_incidence.py -q
```

The full checked artifact is:

```text
data/incidence/n8_incidence_completeness.json
```

The implementation lives in:

```text
src/erdos97/n8_incidence.py
scripts/enumerate_n8_incidence.py
tests/test_n8_incidence.py
```

Combining this incidence-completeness artifact with
`docs/n8-exact-survivors.md` gives the repo-local machine-checked finite case:
there is no selected-witness `n=8` strictly convex counterexample.
