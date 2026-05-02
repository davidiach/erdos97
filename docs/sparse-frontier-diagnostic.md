# Sparse-Frontier Diagnostic

Status: exact fixed-order incidence diagnostic. No general proof and no
counterexample are claimed.

This note explains why the current minimum-radius and radius-propagation
filters do not see the live sparse/Sidon frontier in natural cyclic order.

For a row `i` and a witness pair `{a,b}` inside `S_i`, call the pair
**covered** if `b in S_a` or `a in S_b`. A covered short witness gap would force
a strict radius inequality. An uncovered short gap forces no such inequality.

The diagnostic counts covered and uncovered witness pairs, with special focus
on the three consecutive witness pairs in the supplied cyclic order.

## Reproducible command

```bash
python scripts/analyze_sparse_frontier.py --frontier --assert-empty-choice
```

This prints a compact table and asserts that every live frontier row has at
least one uncovered consecutive witness pair in the natural order.

## Snapshot

| Pattern | n | all witness-pair sources | consecutive-pair sources | rows with uncovered consecutive pair | order-free blocked rows | empty radius choice |
|---|---:|---|---|---:|---:|---|
| `C19_skew` | 19 | `{0: 76, 1: 38}` | `{0: 38, 1: 19}` | 19/19 | 0 | yes |
| `C13_sidon_1_2_4_10` | 13 | `{0: 26, 1: 52}` | `{0: 13, 1: 26}` | 13/13 | 0 | yes |
| `C25_sidon_2_5_9_14` | 25 | `{0: 100, 1: 50}` | `{0: 50, 1: 25}` | 25/25 | 0 | yes |
| `C29_sidon_1_3_7_15` | 29 | `{0: 145, 1: 29}` | `{0: 87}` | 29/29 | 0 | yes |

Here `{0: 76, 1: 38}` means 76 row-local witness pairs have no endpoint source,
and 38 have exactly one endpoint source. No pair in this table has two endpoint
sources.

## Interpretation

The radius-propagation filter chooses one possible short consecutive witness
pair per row. If every row has an uncovered consecutive pair, it can choose
those pairs and force no strict radius inequalities at all. That is the
`empty radius choice` column.

Thus the natural-order pass is not merely a subtle acyclic inequality graph.
For these frontier patterns, the current filter can pass vacuously: it has a
choice with no radius edges.

This is useful negative information. A sparse-overlap proof route needs a new
mechanism that does not rely on two-overlap `phi` edges or on short gaps whose
endpoints select each other.

## Example

For `C19_skew`, row `0` has:

```text
S_0 = {5, 9, 11, 16}
consecutive witness pairs in natural order:
  {5,9}:  uncovered
  {9,11}: uncovered
  {11,16}: covered by source 11
```

So row `0` alone already survives the minimum-radius row test. The diagnostic
checks that every row has the same kind of escape.
