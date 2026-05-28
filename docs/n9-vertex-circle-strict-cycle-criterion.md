# n=9 Vertex-circle Directed Strict-cycle Criterion

Status: `LEMMA` for the abstract directed strict-cycle criterion;
`REVIEW_PENDING_DIAGNOSTIC_ONLY` for the current `n=9` packet audit.

This note records the common local contradiction behind the `T10` through
`T12` vertex-circle strict-cycle packets. It does not claim a proof of `n=9`,
does not claim a counterexample, does not complete independent review of the
exhaustive checker, and does not update the official/global status.

The abstract criterion is n-independent and does not depend on the `T10` ...
`T12` template labels. The review-pending part is the finite packet audit
showing where the criterion appears in the stored `n=9` frontier artifacts.

## Criterion

Let selected rows generate a selected-distance quotient relation on unordered
vertex pairs, as in the self-edge criterion. Write `D(p)` for the common
distance value of a pair or quotient class `p`.

A strict-cycle packet consists of a cyclic list of pairs

```text
p_0, p_1, ..., p_{k-1}
```

and, for each index `i` modulo `k`,

1. a certified vertex-circle strict edge

   ```text
   p_i > q_i,
   ```

2. a selected-distance equality path from `q_i` to `p_{i+1}`.

Then the local row core is unrealizable.

Indeed, each equality path gives

```text
D(q_i) = D(p_{i+1}),
```

while each strict edge gives

```text
D(p_i) > D(q_i).
```

Combining around the cycle yields

```text
D(p_0) > D(p_1) > ... > D(p_{k-1}) > D(p_0),
```

which is impossible for real distances.

Equivalently, after quotienting ordinary pair distances by the selected-row
equalities, the local row core has a directed strict cycle.

## Two-edge Cross-wired Schema

The smallest strict-cycle case has two vertex-circle rows. It is useful to
state it without the packet labels.

Suppose a selected row centered at `r` has four distinct witnesses in angular
order

```text
a, b, c, d
```

and another selected row centered at `s` has four distinct witnesses in angular
order

```text
e, f, g, h
```

The vertex-circle nesting lemma gives the two proper span inequalities

```text
D_ac > D_ab,
D_fh > D_gh.
```

If selected-distance paths identify the inner pair of each strict edge with
the outer pair of the other strict edge,

```text
D_ab = D_fh,
D_gh = D_ac,
```

then the local core is unrealizable. Indeed,

```text
D_ac > D_ab = D_fh > D_gh = D_ac,
```

which is a strict two-cycle among real distance values.

This schema is not a new completeness result. It is the `k=2` instance of the
strict-cycle criterion with a concrete span-nesting certificate for each
strict edge. It is useful because it separates the reusable proof object from
the specific `T10/F12` labels: any selected-row core, in any larger polygon,
that supplies the two nested chord inequalities and the two cross-wired
selected-distance paths is impossible.

The `T10/F12` focused packet is exactly one instance. The row centered at `8`
has witness order `[0,3,6,7]`, giving `D_06 > D_03`; the row centered at `3`
has witness order `[4,6,0,1]`, giving `D_16 > D_01`. Rows `3` and `6`
identify `D_03 = D_36 = D_16`, and row `0` identifies `D_01 = D_06`, so the
cross-wired schema gives

```text
D_06 > D_16 > D_06.
```

### Why connector rows are needed

A nondegenerate two-edge schema cannot be forced by the two strict rows alone.
Here nondegenerate means that the four strict-edge endpoint pairs

```text
{a,c}, {a,b}, {f,h}, {g,h}
```

are pairwise distinct, and neither strict edge is already a quotient self-edge
using only the two selected rows centered at `r` and `s`.

Indeed, the two selected rows generate at most two star equivalence classes:

```text
A = {{r,x} : x in {a,b,c,d}},
B = {{s,y} : y in {e,f,g,h}},
```

possibly merged if they share a pair. The row-`r` strict pairs `{a,c}` and
`{a,b}` do not lie in `A`, and the row-`s` strict pairs `{f,h}` and `{g,h}` do
not lie in `B`.

For a nontrivial cross-wire `{a,b} ~ {f,h}` to hold, `{a,b}` must lie in `B`,
`{f,h}` must lie in `A`, and the two stars must be merged. Similarly, the
other cross-wire `{g,h} ~ {a,c}` forces `{a,c}` to lie in `B` and `{g,h}` to
lie in `A`. But then both row-`r` strict pairs lie in `B`, so
`{a,c} ~ {a,b}` and the first strict edge is already a self-edge; likewise
both row-`s` strict pairs lie in `A`, so the second strict edge is also a
self-edge. This contradicts nondegeneracy.

Thus a genuine two-edge quotient cycle needs either an additional connector
row, a longer selected-distance path, or it has already collapsed to a simpler
self-edge obstruction. The `T10/F12` instance uses rows `0` and `6` as the
connector rows beyond the two strict rows centered at `8` and `3`.

### One-connector caveat

The previous paragraph does not rule out a one-extra-row pattern by quotient
combinatorics alone. Write a two-edge schema abstractly as

```text
A > B,
C > D,
B = C,
A ~ D.
```

Here `B = C` is a literal shared unordered pair, while `A ~ D` is supplied by
one connector row. This can be nondegenerate as an abstract selected-distance
quotient if the connector row does not also contain the literal shared pair.

For example, use labels `0,...,6` and stipulate the following local rows:

```text
row centered at 4 has witness order 0,1,2,5,
row centered at 6 has witness order 2,1,3,0,
row centered at 0 has selected witnesses 2,3,4,5.
```

The two strict rows give

```text
D_02 > D_01,
D_01 > D_03.
```

The connector row centered at `0` identifies `D_02 = D_03`, but it does not
identify either of them with `D_01`, because label `1` is not selected in that
connector row. Thus the quotient has a nondegenerate two-cycle

```text
D_02 > D_01 > D_03 = D_02.
```

This is only a local quotient model with stipulated witness orders; it is not
a Euclidean realization, not a selected-witness counterexample, and not a
proof that such a pattern must occur. Its use is negative: excluding the
one-connector case requires an additional cyclic-order or geometric hypothesis,
not just the selected-distance quotient.

There is a related trap to avoid. If the proposed geometric hypothesis already
includes both strict vertex-circle inequalities and the connector equality,
then the two-edge strict-cycle criterion above has already made the local core
unrealizable:

```text
D(A) > D(P) > D(D) = D(A).
```

Thus any additional claim that the connector row must also contain the shared
pair `P` is vacuous under those hypotheses. The useful proof target is not to
collapse the one-connector pattern after the strict cycle is present; it is to
prove an entry lemma that forces one of these strict-cycle patterns from
independent incidence, cyclic-order, or metric-order assumptions.

## Current Packet Audit

The checked source artifact is
`data/certificates/n9_vertex_circle_strict_cycle_template_packet.json`. It is
derived into the combined template catalog
`data/certificates/n9_vertex_circle_template_lemma_catalog.json`.

The current strict-cycle packet records:

```text
strict-cycle templates:       3
strict-cycle family records:  3
covered assignments:        26
```

The criterion applies exactly to every family record in that packet: in each
cycle step, the strict inner pair is the connector start pair, and the
connector end pair is the next strict outer pair.

```text
T10/F12: assignments=18 cycle=2 connectors=[2,1]
T11/F07: assignments=6  cycle=3 connectors=[0,1,2]
T12/F16: assignments=2  cycle=3 connectors=[1,2,1]
```

The audit counts are:

```text
family-record cycle lengths:       {2: 1, 3: 2}
assignment-weighted cycle lengths: {2: 18, 3: 8}
connector path lengths:            {0: 1, 1: 4, 2: 3}
mismatch count:                    0
audit digest: 49363955d3efebad841d4898d0d4695696fc4016dbad2a4c6d532edf15b667ab
```

## Paired-square Entry Side Audit

The `T10/F12` family also has a focused paired-square entry audit at
`data/certificates/n9_t10_paired_square_entry_audit.json`. The audit checks
the 18 `T10/F12` assignment instances against the Abstract Paired-Square Entry
Lemma target from the Kalmanson route.

For each assignment, the checker requires a literal incident residual pair
`{i,n}` whose nonselected quotient class is the singleton `{i,n}`. It then
requires two selected-center squares for that same residual pair, with
opposite Kalmanson diagonal orientations, and verifies from the actual quotient
class keys that their reduced vectors are exactly

```text
R_i - X_{i,n},
X_{i,n} - R_i.
```

The resulting exact diagnostic counts are:

```text
assignments audited:          18
assignments with an entry:    18
assignments without an entry:  0
literal singleton entries:    54
audit digest: e32ff6014b1388fa733ad1fdb244c945114e91d059374259c6eeb1742ba89558
```

The artifact stores one representative paired-square entry for each assignment
with a hit; the `literal singleton entries` count is the total number of
surviving entries found across the assignments.

This is a side audit, not the primary `T10/F12` contradiction and not a proof
of `n=9`. The strict-cycle packet already supplies the local contradiction for
these assignments. The paired-square audit only records that the Kalmanson
entry mechanism has exact positive instances on the same 18 assignments after
the singleton residual condition is enforced; it does not show that arbitrary
vertex-circle connector states must expose such an entry.

## Scope

This criterion is a local final-contradiction lemma. It applies only after
the local selected-row equality connectors and the local vertex-circle strict
edges have already been checked.

It does not prove the full `n=9` finite case, because the exhaustive checker
and assignment-to-template crosswalk are still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.
It does not prove Erdos Problem #97 and does not give a counterexample.

## Commands

Check the source packet and the combined template catalog:

```bash
python scripts/check_n9_vertex_circle_strict_cycle_template_packet.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_vertex_circle_template_lemma_catalog.py \
  --check \
  --assert-expected \
  --json
```

The family-record audit can be reproduced by parsing
`data/certificates/n9_vertex_circle_strict_cycle_template_packet.json` and
checking, for every cycle step:

```text
strict_inequality.inner_pair == equality_to_next_outer_pair.start_pair
equality_to_next_outer_pair.end_pair == next strict_inequality.outer_pair
```

with the next strict outer pair taken cyclically.

## Review Standard

Before using this criterion in a proof, a reviewer should independently check
the two local inputs for the particular row core under discussion:

1. every displayed connector path is forced by selected rows; and
2. every displayed strict edge is forced by the stated vertex-circle witness
   order.

Once those inputs are established, the contradiction in this note is just the
impossibility of a strict cycle among real distance values.
