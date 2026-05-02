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

To exactly optimize the row-local empty-gap count over cyclic orders:

```bash
python scripts/analyze_sparse_frontier.py \
  --frontier \
  --certify-empty-gap-bound
```

This branch-and-bound search fixes label `0` to quotient cyclic rotations. It
does not quotient reversal. The objective is still only the current
minimum-radius/radius-propagation filter's empty-gap row count.

To certify that the sparse single-target frontier always passes the current
radius-propagation cycle filter:

```bash
python scripts/analyze_sparse_frontier.py \
  --frontier \
  --certify-single-target-radius-pass
```

This uses the fact that every covered row-local witness pair in these sparse
patterns has at most one endpoint source. In that single-target setting, a
fixed cyclic order is radius-cycle obstructed only if it realizes a nonempty
closed target set.

To check registered abstract-order survivors against the current exact
fixed-order filters:

```bash
python scripts/check_sparse_order_survivors.py --assert-expected
```

This combines crossing constraints, Altman signature and linear-certificate
filters, vertex-circle strict-cycle checks, minimum-radius checks, and
radius-propagation checks for each registered order.

## Snapshot

| Pattern | n | all witness-pair sources | consecutive-pair sources | rows with uncovered consecutive pair | order-free blocked rows | order-free empty-gap rows | empty radius choice |
|---|---:|---|---|---:|---:|---:|---|
| `C19_skew` | 19 | `{0: 76, 1: 38}` | `{0: 38, 1: 19}` | 19/19 | 0 | 19/19 | yes |
| `C13_sidon_1_2_4_10` | 13 | `{0: 26, 1: 52}` | `{0: 13, 1: 26}` | 13/13 | 0 | 0/13 | yes |
| `C25_sidon_2_5_9_14` | 25 | `{0: 100, 1: 50}` | `{0: 50, 1: 25}` | 25/25 | 0 | 25/25 | yes |
| `C29_sidon_1_3_7_15` | 29 | `{0: 145, 1: 29}` | `{0: 87}` | 29/29 | 0 | 29/29 | yes |

Here `{0: 76, 1: 38}` means 76 row-local witness pairs have no endpoint source,
and 38 have exactly one endpoint source. No pair in this table has two endpoint
sources.

The order-free empty-gap column is an exact row-local certificate. For a row,
form the covered-pair graph on its four witnesses. If that graph has no
Hamiltonian path, then every possible local witness order has at least one
uncovered consecutive pair. Thus the `C19`, `C25`, and `C29` entries certify
that the all-empty radius choice exists for every cyclic order. The `C13` entry
does not have this certificate: every `C13` row has covered witness paths, so
some cyclic orders can block its empty-gap escape in selected rows.

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
choice; the order-free empty-gap certificate above upgrades that observation
for those three patterns to an exact abstract-order statement about the
current radius-propagation filter.

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
`C25`, and `C29`, the exact order-free empty-gap certificate explains why this
heuristic cannot break the all-empty escape.

The exact empty-gap bound below supersedes this heuristic as the sharp
row-local benchmark for `C13`; the heuristic remains useful as a cheap stress
test.

## Exact Empty-Gap Bound

With `--certify-empty-gap-bound`:

| Pattern | status | explored nodes | certified minimum rows with an uncovered consecutive pair | certified maximum blocked rows | best radius status | optimized minimum acyclic edge count |
|---|---|---:|---:|---:|---|---:|
| `C19_skew` | `CERTIFIED_OPTIMUM` | 1 | 19 | 0 | `PASS_ACYCLIC_CHOICE` | 0 |
| `C13_sidon_1_2_4_10` | `CERTIFIED_OPTIMUM` | 39610 | 3 | 10 | `PASS_ACYCLIC_CHOICE` | 10 |
| `C25_sidon_2_5_9_14` | `CERTIFIED_OPTIMUM` | 1 | 25 | 0 | `PASS_ACYCLIC_CHOICE` | 0 |
| `C29_sidon_1_3_7_15` | `CERTIFIED_OPTIMUM` | 1 | 29 | 0 | `PASS_ACYCLIC_CHOICE` | 0 |

For `C19`, `C25`, and `C29`, the one-node certificate comes from the
order-free empty-gap row certificates above: no row can be blocked in any
cyclic order. For `C13`, the exact search proves that at least 3 rows must
retain an uncovered consecutive pair in every cyclic order, and gives this
extremal order:

```text
0, 1, 3, 11, 7, 5, 8, 10, 12, 2, 6, 4, 9
```

The three rows retaining an uncovered consecutive pair in that order are
`0, 1, 7`. The remaining 10 rows are blocked for the local empty-gap test, but
the radius-propagation optimizer still finds an acyclic choice with 10 strict
radius edges. This is an exact benchmark for this filter, not a realization
claim.

## Single-Target Radius Pass

With `--certify-single-target-radius-pass`:

| Pattern | status | all orders pass radius filter | active rows | checked subsets | candidate closed subsets | compatibility nodes | compatible closed target set |
|---|---|---|---:|---:|---:|---:|---|
| `C19_skew` | `CERTIFIED_PASS_ALL_ORDERS` | yes | 0 | 0 | 0 | 0 | none |
| `C13_sidon_1_2_4_10` | `CERTIFIED_PASS_ALL_ORDERS` | yes | 13 | 8191 | 1 | 429 | none |
| `C25_sidon_2_5_9_14` | `CERTIFIED_PASS_ALL_ORDERS` | yes | 0 | 0 | 0 | 0 | none |
| `C29_sidon_1_3_7_15` | `CERTIFIED_PASS_ALL_ORDERS` | yes | 0 | 0 | 0 | 0 | none |

For `C19`, `C25`, and `C29`, no row has a covered local witness path, so the
empty-radius escape already proves the pass. For `C13`, all 13 rows are active.
The subset scan finds one row-local closed target candidate, the full vertex
set, but a 429-node cyclic-order compatibility search proves that candidate is
not realizable by any cyclic order. Therefore no cyclic order of `C13` can be
obstructed by the current single-target radius-cycle filter.

This closes the radius-propagation route for the sparse frontier as currently
implemented. A proof or counterexample must use additional geometry or a
strictly stronger sparse-overlap mechanism.

## Registered Sparse-Filter Survivors

The combined exact-filter sweep is checked in at
`data/certificates/sparse_order_survivors.json`. It records two non-natural
cyclic orders that survive the older sparse-frontier fixed-order filters
(crossing, Altman, vertex-circle, minimum-radius, and radius-propagation). Both
registered orders are now killed when fixed-order Kalmanson/Farkas certificates
are included.

| Pattern | Order label | n | Pre-Kalmanson filters | Kalmanson status |
|---|---|---:|---|---|
| `C13_sidon_1_2_4_10` | `sample_full_filter_survivor` | 13 | pass | exact fixed-order obstruction, 34 inequalities |
| `C19_skew` | `vertex_circle_survivor` | 19 | pass | exact fixed-order obstruction, 94 inequalities |

The `C13` order is:

```text
5,0,10,8,9,7,4,6,2,11,12,3,1
```

The `C19` order is:

```text
18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1
```

These remain adversarial objects for filter development, not counterexamples.
In particular, the fixed-order Kalmanson kills do not prove either abstract
incidence pattern impossible across all cyclic orders.

The first constrained numerical run on the registered `C13` sparse-filter order
is:

```bash
python -m erdos97.search \
  --pattern C13_sidon_1_2_4_10 \
  --cyclic-order 5,0,10,8,9,7,4,6,2,11,12,3,1 \
  --ordered-name C13_sidon_order_survivor_20260502 \
  --optimizer slsqp \
  --mode polar \
  --restarts 20 \
  --max-nfev 2000 \
  --margin 1e-4 \
  --seed 20260502 \
  --out data/runs/C13_sidon_order_survivor_slsqp_m1e-4_seed20260502.json
```

It returns `eq_rms = 0.6569` and `max_spread = 2.728` with convexity margin
`1e-4`. This is still a large residual, so it is negative numerical evidence
for this particular order as a counterexample target, not a near-miss.

The first constrained numerical run on the registered `C19` sparse-filter order
is:

```bash
python -m erdos97.search \
  --pattern C19_skew \
  --cyclic-order 18,10,7,17,6,3,5,9,14,11,2,13,4,16,12,15,0,8,1 \
  --ordered-name C19_skew_order_survivor_20260502 \
  --optimizer slsqp \
  --mode polar \
  --restarts 20 \
  --max-nfev 2000 \
  --margin 1e-4 \
  --seed 20260502 \
  --out data/runs/C19_skew_order_survivor_slsqp_m1e-4_seed20260502.json
```

It returns `eq_rms = 0.9031` and `max_spread = 4.149` with convexity margin
`1e-4`. The verifier reports `ok_at_tol = false`, no validation errors, and
all empirical `E` values equal to `1` at tolerance `1e-8`. Light direct and
support-parameter SLSQP probes at the same margin found no feasible restart,
while a trust-region polar probe only improved the residual by becoming
nonconvex. This is again negative numerical evidence for this fixed order, not
a proof of non-realizability and not a counterexample.

## Metric LP Combination

The combined fixed-order LP diagnostic in `docs/metric-order-lp.md` adds all
ordinary triangle inequalities to the Altman adjacent-gap and vertex-circle
strict inequalities. It still passes both registered sparse orders before
Kalmanson/Farkas certificates are included:

| Pattern order | Max margin | Distance classes | Inequalities |
|---|---:|---:|---:|
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | `0.0021978` | 39 | 980 |
| `C19_skew:vertex_circle_survivor` | `0.00143164` | 114 | 3086 |

This is another negative diagnostic: the sparse-overlap wall is not removed by
combining the current Altman, vertex-circle, and metric-triangle linear
constraints.

The Ptolemy-strengthened nonlinear diagnostic in `docs/ptolemy-order-nlp.md`
adds every cyclic-quadrilateral Ptolemy inequality. It still passes both
registered sparse orders before Kalmanson/Farkas certificates are included:

| Pattern order | Max margin | Linear inequalities | Ptolemy inequalities |
|---|---:|---:|---:|
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | `0.00176461` | 980 | 715 |
| `C19_skew:vertex_circle_survivor` | `0.00106142` | 3086 | 3876 |

This is a numerical nonlinear diagnostic only. It shows that Ptolemy
constraints by themselves are still too weak, not that either order is
realizable.

The row-circle Ptolemy diagnostic in `docs/row-circle-ptolemy-nlp.md` adds the
Ptolemy equality forced by each selected witness quadruple lying on a circle
around its center. This is the first current distance-class diagnostic to
numerically obstruct one registered sparse-order survivor:

| Pattern order | Status | Max margin | Row Ptolemy residual |
|---|---|---:|---:|
| `C13_sidon_1_2_4_10:sample_full_filter_survivor` | optimizer failed | `-0.0225187` | `0.000244748` |
| `C19_skew:vertex_circle_survivor` | numerical obstruction | `-0.00264843` | `2.98e-19` |

This is not an exact obstruction. The `C19` result is an exactification target;
the `C13` result is only an optimizer-failure diagnostic.

The follow-up active-set snapshot
`data/certificates/c19_row_circle_ptolemy_active_set.json` records the
optimized C19 quotient distances together with the 22 tight linear rows, 74
tight global Ptolemy rows, 19 row-circle equality rows, and the SLSQP
multiplier summary. It is numerical support data only, intended to make a later
exact certificate search reproducible.

The companion multiplier-reduction artifact
`data/certificates/c19_row_circle_multiplier_reduction.json` pairs every
row-circle equality with the duplicate tight global Ptolemy row on the same
four witnesses. Combining those duplicate multipliers reduces the maximum
absolute multiplier from about `2.95e17` to `24`, so the huge weights in the raw
snapshot should be treated as redundancy noise, not as a stable exact
certificate.

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
