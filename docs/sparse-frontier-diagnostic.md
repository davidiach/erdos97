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

To sample other cyclic orders:

```bash
python scripts/analyze_sparse_frontier.py \
  --frontier \
  --sample-orders 200 \
  --sample-seed 0
```

Sampling is not exhaustive; it is a smoke test for whether the natural-order
empty-gap escape is robust under order changes.

To additionally run the full radius-propagation filter on each sampled order:

```bash
python scripts/analyze_sparse_frontier.py \
  --frontier \
  --sample-orders 200 \
  --sample-seed 0 \
  --sample-radius-propagation
```

This distinguishes orders with an all-empty short-gap choice from orders that
still admit an acyclic strict-radius inequality choice.

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

## Order Sampling

With `--sample-orders 200 --sample-seed 0`, including natural order for 201
checked orders:

| Pattern | orders checked | empty-choice orders | minimum rows with an uncovered consecutive pair | row-count histogram |
|---|---:|---:|---:|---|
| `C19_skew` | 201 | 201 | 19 | `{19: 201}` |
| `C13_sidon_1_2_4_10` | 201 | 25 | 7 | `{7: 4, 8: 6, 9: 23, 10: 52, 11: 52, 12: 39, 13: 25}` |
| `C25_sidon_2_5_9_14` | 201 | 201 | 25 | `{25: 201}` |
| `C29_sidon_1_3_7_15` | 201 | 201 | 29 | `{29: 201}` |

This separates `C13` from the larger sparse frontier. The natural order of
`C13_sidon_1_2_4_10` has an empty radius choice, but many sampled orders do
not. In contrast, all sampled orders for `C19`, `C25`, and `C29` kept the empty
choice. This is still sampling only, not an abstract-order theorem.

With the same order sample and `--sample-radius-propagation`:

| Pattern | radius status histogram | no-empty-choice radius status histogram | maximum explored nodes |
|---|---|---|---:|
| `C19_skew` | `{PASS_ACYCLIC_CHOICE: 201}` | `{}` | 20 |
| `C13_sidon_1_2_4_10` | `{PASS_ACYCLIC_CHOICE: 201}` | `{PASS_ACYCLIC_CHOICE: 176}` | 14 |
| `C25_sidon_2_5_9_14` | `{PASS_ACYCLIC_CHOICE: 201}` | `{}` | 26 |
| `C29_sidon_1_3_7_15` | `{PASS_ACYCLIC_CHOICE: 201}` | `{}` | 30 |

Thus this sampled run found no strict radius-cycle obstruction. In particular,
the 176 sampled `C13` orders without an all-empty choice still passed by an
acyclic radius-inequality assignment. This is negative evidence about the
current radius-propagation filter, not evidence for geometric realizability.

## Adversarial Order Search

The random sampler can also seed a heuristic swap hill-climb that looks for
cyclic orders with fewer rows admitting uncovered consecutive witness pairs:

```bash
python scripts/analyze_sparse_frontier.py \
  --frontier \
  --adversarial-orders 50 \
  --sample-seed 0 \
  --adversarial-restarts 6 \
  --adversarial-steps 80
```

This is not exhaustive. It is a way to produce better stress tests for the
same fixed-order necessary filter.

With that deterministic run:

| Pattern | orders evaluated | minimum rows with an uncovered consecutive pair | radius status histogram | certified minimum acyclic edge count |
|---|---:|---:|---|---:|
| `C19_skew` | 529 | 19 | `{PASS_ACYCLIC_CHOICE: 529}` | 0 |
| `C13_sidon_1_2_4_10` | 496 | 5 | `{PASS_ACYCLIC_CHOICE: 496}` | 8 |
| `C25_sidon_2_5_9_14` | 530 | 25 | `{PASS_ACYCLIC_CHOICE: 530}` | 0 |
| `C29_sidon_1_3_7_15` | 531 | 29 | `{PASS_ACYCLIC_CHOICE: 531}` | 0 |

For `C13`, this produces much more adversarial cyclic orders than passive
sampling: only 5 of 13 rows retain an uncovered consecutive pair in the best
found orders. The minimum acyclic radius choice is certified at 8 strict
radius edges, matching the 8 rows without an uncovered consecutive pair. Even
then, the radius-propagation filter still finds an acyclic choice. For `C19`,
`C25`, and `C29`, the same heuristic did not break the all-empty escape.

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
