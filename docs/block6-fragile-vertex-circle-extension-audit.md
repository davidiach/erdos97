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
  --assert-expected \
  --json
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

The next bounded widening checks the first 100 deterministic terminal full
extensions from this audit across all of their crossing-compatible cyclic
orders:

```bash
python scripts/check_block6_terminal_crossing_vertex_circle_sample.py \
  --assert-expected \
  --json
```

In that sample, the crossing-order frontiers contain `440` total cyclic orders
and every one is vertex-circle obstructed by a quotient self-edge. The largest
frontier in the sample has `15` crossing-compatible orders. This is a
diagnostic sample only: it does not close the remaining all-extension,
all-order block-6 bridge gap.
