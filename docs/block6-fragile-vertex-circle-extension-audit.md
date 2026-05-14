# Block-6 Fragile-cover Vertex-circle Extension Audit

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note audits one bounded obstruction to the forced-local-core bridge. It
does not claim a proof of Erdos Problem #97, does not claim a counterexample,
and does not update the official/global status.

## Subquestion

The minimal fragile-cover bridge shows that every minimal counterexample has
some exact critical 4-tie rows covering all vertices. The block-6 family shows
that fragile-cover hypergraph constraints alone are too weak.

The narrow question here is:

```text
For two disjoint block-6 fragile-cover blocks in the natural cyclic order, is
there a full selected-witness extension that also survives the vertex-circle
quotient self-edge / strict-cycle filter?
```

## Definitions

For each six-label block `b,...,b+5`, the block-6 fragile rows are

```text
b   -> {b+1,b+2,b+3,b+4}
b+3 -> {b,b+2,b+4,b+5}.
```

For two blocks, this gives `n=12` and fixed fragile centers

```text
0, 3, 6, 9.
```

A full selected extension assigns one 4-set row to every center, keeps the
four fixed fragile rows, and satisfies the standard incidence/order necessary
conditions used in the audit:

- self-exclusion and row size 4;
- pairwise selected-row intersection at most 2;
- radical-axis crossing for every two-overlap;
- witness-pair multiplicity at most 2;
- selected indegree at most `floor(2*(12-1)/(4-1)) = 7`.

A vertex-circle-clean extension is such an extension whose selected-distance
quotient strict graph has no self-edge and no directed strict cycle in the
natural cyclic order.

## Result

Exact bounded audit:
**Two-block Fragile-cover Vertex-circle Closure Lemma**.

The two-block block-6 fragile-cover family has an incidence-level full
selected extension, but no full selected extension survives the vertex-circle
quotient obstruction filter under the natural cyclic order and the stated
incidence/order necessary conditions.

## Audit Output

The existing fragile-cover checker confirms that one block is abstractly
allowed but has no full incidence extension, while two blocks have a full
incidence extension:

```text
blocks=1: fragile-cover ok, full selected extension false
blocks=2: fragile-cover ok, full selected extension true, nodes=17
```

The two-block vertex-circle-clean extension search fixed the four fragile rows
and searched all remaining row choices with minimum-remaining-options
branching. It used monotone vertex-circle partial pruning: once a partial
assignment has a quotient self-edge or directed strict cycle, no later rows can
repair it.

Reproduce the pruned audit with:

```bash
python scripts/check_block6_fragile_vertex_circle_extension.py \
  --check \
  --assert-expected \
  --json
```

The checked artifact is:

```text
data/certificates/block6_fragile_vertex_circle_extension_audit.json
```

Rewrite it after an intentional generator change with:

```bash
python scripts/check_block6_fragile_vertex_circle_extension.py \
  --assert-expected \
  --write
```

The audit reported:

```text
fixed rows {0: (1, 2, 3, 4), 3: (0, 2, 4, 5), 6: (7, 8, 9, 10), 9: (6, 8, 10, 11)}
initial_vc ok
result None
nodes 1752
zero_option_prunes 37
vc_prunes {'self_edge': 645, 'strict_cycle': 768}
solutions 0
```

Thus every branch either runs out of legal incidence/order rows or reaches a
monotone vertex-circle quotient obstruction.

As a terminal cross-check, the same fixed-row search was rerun without
vertex-circle partial pruning and classified every full incidence/order
extension at the end. It found no vertex-circle-clean terminal extension:

```bash
python scripts/check_block6_fragile_vertex_circle_extension.py \
  --terminal \
  --assert-expected \
  --json
```

```text
full_extensions 105978
nodes 320898
zero_option_prunes 79547
vertex_circle_status_counts {'self_edge': 105690, 'strict_cycle': 288}
strict_edge_count_histogram {108: 105978}
```

## Scope

This is a bounded natural-order audit of the two-block block-6 family. It does
not prove that every fragile-cover system, every full selected-witness system,
or every minimal counterexample forces a vertex-circle quotient obstruction.

It also does not prove Euclidean realizability or unrealizability of an
arbitrary abstract incidence system. The conclusion is only that this
particular fragile-cover obstruction to hypergraph-only reasoning is not an
obstruction to a stronger bridge that also uses the vertex-circle quotient
filter.

## Effect

The block-6 family still shows that pure fragile-cover hypergraph constraints
cannot prove Erdos Problem #97. The two-block audit narrows that warning:
after adding full selected-row extension plus vertex-circle quotient
obstructions in the natural cyclic order, the two-block family closes.

The next bridge target should test whether this closure is special to the
block-6 construction or reflects a broader principle for fragile-cover
extensions.

## Crosswalk

The fixed full-row survivor used by the row-Ptolemy, radius-propagation, and
Kalmanson diagnostics is one terminal extension inside this natural-order
audit. Reproduce the current filter-layer crosswalk with:

```bash
python scripts/check_block6_fragile_filter_crosswalk.py --assert-expected --json
```

That script records the exact quantifier split: natural-order vertex-circle
closes all full extensions for this block-6 benchmark, while Kalmanson closes
only the named fixed survivor across its four crossing-compatible cyclic
orders. It does not claim an all-extension, all-order obstruction.

The next bounded widening checks two deterministic windows of terminal full
extensions from this audit across all of their crossing-compatible cyclic
orders:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py \
  --check \
  --assert-expected \
  --json
```

The checked sample packet is:

```text
data/certificates/block6_terminal_crossing_vertex_circle_sample.json
```

Rewrite it after an intentional generator change with:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py \
  --write \
  --assert-expected
```

Across those two sampled windows, `200` terminal extensions produce `796`
crossing-compatible cyclic orders, and every one is vertex-circle obstructed
by a quotient self-edge. The largest frontier in the checked windows has `15`
crossing-compatible orders. This is a diagnostic sample only: it does not close
the remaining all-extension, all-order block-6 bridge gap.

The full natural-order terminal sweep is now also stored:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py \
  --full-sweep \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_terminal_crossing_vertex_circle_full_sweep.json
```

It exhausts the `105,978` terminal full extensions generated by the
natural-order two-block audit and enumerates every crossing-compatible cyclic
order each terminal extension admits. The sweep classifies `385,517` crossing
orders; `384,318` are killed by a quotient self-edge and `1,199` by a strict
cycle, with no vertex-circle-clean order found. The largest terminal extension
has `380` crossing-compatible orders.

This is a stronger bounded diagnostic, not a theorem-level closure. It does
not cover row systems outside the natural-order terminal generator, does not
prove all block-6 cyclic orders are obstructed, and does not prove the fragile
bridge.

The next fixed-order probe makes that generator gap concrete:

```bash
python scripts/check_block6_fixed_order_vertex_circle_probe.py \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_fixed_order_vertex_circle_probe.json
```

It checks the natural order plus three fixed non-natural cyclic orders. In
each non-natural order, the first legal terminal extension fails the natural
cyclic crossing rule, so it is genuinely outside the natural-order terminal
generator. Nevertheless, all four probed fixed orders close under the
order-specific vertex-circle-pruned full-extension search. The four probes
visit `3,917` pruned search nodes and close by `1,390` self-edge and `1,726`
strict-cycle quotient obstructions.

This is not all-order closure. Its value is to separate the next gap cleanly:
the natural-order generator is incomplete for fixed-order reasoning, but the
same vertex-circle gate survives several non-natural fixed orders.

The next bounded family sweep widens the fixed-order side:

```bash
python scripts/check_block6_shuffle_order_vertex_circle_sweep.py \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_shuffle_order_vertex_circle_sweep.json
```

This sweep checks all `462` normalized cyclic orders that keep the internal
order of labels `0,1,2,3,4,5` and `6,7,8,9,10,11` but shuffle the two blocks.
All `462` order-specific full-extension searches close under vertex-circle
quotient pruning. The artifact records `458` orders with a legal terminal
selected-row extension, `4` orders with no terminal extension, and `457` first
terminal extensions outside the natural-order terminal generator. The pruned
searches visit `735,652` nodes and close by `276,230` self-edge and `316,519`
strict-cycle quotient obstructions.

This is still a bounded fixed-order-family diagnostic, not all-order closure.
It does not cover cyclic orders that permute labels inside a block, arbitrary
block-6 full selected-row systems, or a genuine minimal/rich-class bridge.

The first oriented-block companion slice exposes the boundary of this gate:

```bash
python scripts/check_block6_reversed_block_shuffle_vertex_circle_escape.py \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_reversed_block_shuffle_vertex_circle_escape.json
```

Here the first block is kept in order `1,2,3,4,5` after label `0`, while the
second block is kept in reverse order `11,10,9,8,7,6`, and the two oriented
blocks are shuffled. Among the `462` normalized orders in this family, `446`
close under vertex-circle quotient pruning and `16` have a vertex-circle-clean
full selected-row extension. The artifact stores those 16 clean abstract row
systems as fixed-order escape targets.

These escapes are not counterexamples and not Euclidean realizations. They
show only that the vertex-circle quotient gate alone does not close this wider
oriented-block family; the next attack needs a stronger metric-order filter or
a genuine minimal/rich-class bridge condition on those clean rows.

A follow-up fixed-order metric-order packet attacks exactly those 16 clean
rows:

```bash
python scripts/check_block6_reversed_block_clean_kalmanson.py \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_reversed_block_clean_kalmanson.json
```

All 16 stored assignment/order pairs have exact Kalmanson quotient-cone
certificates. The packet records `394` strict Kalmanson rows in total, total
weight `16850`, and zero combined coefficient vector for every certificate
after quotienting by selected-distance equalities. This closes only the 16
stored fixed-order escape rows from the reversed-block negative control; it
does not prove all cyclic orders, all block-6 selected-row systems, the
fragile bridge, or Erdos Problem #97.

A compact two-stage crosswalk records the bounded-family closure arithmetic:

```bash
python scripts/check_block6_reversed_block_two_stage_closure.py \
  --check \
  --assert-expected \
  --json
```

```text
data/certificates/block6_reversed_block_two_stage_closure.json
```

It checks that the Kalmanson packet certifies exactly the 16 clean indices from
the vertex-circle negative control, so `446` vertex-circle closures plus `16`
Kalmanson closures cover the `462` reversed-second-block shuffle orders. This
is only a cross-artifact fixed-order-family closure, not a new bridge theorem.
