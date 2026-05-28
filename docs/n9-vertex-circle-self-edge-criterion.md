# n=9 Vertex-circle Selected-path Self-edge Criterion

Status: `LEMMA` for the abstract selected-path self-edge criterion;
`REVIEW_PENDING_DIAGNOSTIC_ONLY` for the current `n=9` packet audit.

This note records the common local contradiction behind the `T01` through
`T09` vertex-circle self-edge packets. It does not claim a proof of `n=9`,
does not claim a counterexample, does not complete independent review of the
exhaustive checker, and does not update the official/global status.

The abstract criterion is n-independent and does not depend on the `T01` ...
`T09` template labels. The review-pending part is the finite packet audit
showing where the criterion appears in the stored `n=9` frontier artifacts.

## Criterion

Let `P` be a strictly convex polygon with labelled vertices, and let selected
rows be written

```text
S_c = {a,b,d,e}.
```

The row `S_c` means that the four spoke distances

```text
d(c,a), d(c,b), d(c,d), d(c,e)
```

are equal. These selected-row equalities generate an equivalence relation on
unordered vertex pairs. Write `D([x,y])` for the common distance value of the
selected-distance quotient class containing `{x,y}`.

A selected-distance equality path from an unordered pair `p` to an unordered
pair `q` is a finite sequence

```text
p = p_0, p_1, ..., p_k = q
```

where each equality `D(p_j) = D(p_{j+1})` is forced by one selected row.

A certified strict edge `p > q` is a separately checked vertex-circle
inequality saying that every realization of the displayed local row core has

```text
D(p) > D(q).
```

In the `n=9` self-edge packets, the strict edge comes from the usual
vertex-circle monotonicity lemma: on one selected circle, a chord whose
witness interval properly contains another witness interval is strictly
longer.

**Selected-path self-edge criterion.** If a local row core contains both

```text
p > q
```

and a selected-distance equality path from `p` to `q`, then that local core is
unrealizable.

Indeed, the equality path gives

```text
D(p) = D(q),
```

while the strict edge gives

```text
D(p) > D(q),
```

a contradiction.

Equivalently, after quotienting ordinary pair distances by the selected-row
equalities, the local row core has a reflexive strict edge.

## Current Packet Audit

The checked source artifact is
`data/certificates/n9_vertex_circle_self_edge_template_packet.json`. It is
derived into the combined template catalog
`data/certificates/n9_vertex_circle_template_lemma_catalog.json`.

The current self-edge packet records:

```text
self-edge templates:       9
self-edge family records: 13
covered assignments:     158
```

The criterion applies exactly to every family record in that packet: in each
record, the strict outer pair is the equality-path start pair, and the strict
inner pair is the equality-path end pair.

```text
T01/F09: assignments=6  path=3  strict [1,8] > [1,2]
T02/F01: assignments=18 path=3  strict [1,8] > [1,2]
T02/F04: assignments=18 path=3  strict [0,2] > [2,3]
T02/F08: assignments=2  path=3  strict [1,8] > [1,2]
T02/F14: assignments=2  path=3  strict [1,8] > [1,2]
T03/F05: assignments=18 path=3  strict [3,7] > [1,7]
T03/F15: assignments=2  path=3  strict [1,4] > [3,4]
T04/F13: assignments=2  path=3  strict [1,5] > [1,2]
T05/F10: assignments=18 path=3  strict [1,8] > [1,2]
T06/F11: assignments=18 path=4  strict [3,8] > [3,5]
T07/F06: assignments=18 path=4  strict [1,4] > [1,2]
T08/F02: assignments=18 path=5  strict [1,3] > [1,2]
T09/F03: assignments=18 path=6  strict [1,3] > [1,2]
```

The audit counts are:

```text
family-record path lengths:       {3: 9, 4: 2, 5: 1, 6: 1}
assignment-weighted path lengths: {3: 86, 4: 36, 5: 18, 6: 18}
mismatch count:                   0
audit digest: c76e76eea27c61eca04a755ef0c7f15d4cf77f9513f55697da5ad1aa105172b4
```

## Scope

This criterion is a local final-contradiction lemma. It applies only after
the local selected-row equalities and the local vertex-circle strict edge have
already been checked.

It does not prove the full `n=9` finite case, because the exhaustive checker
and assignment-to-template crosswalk are still needed to show that every
frontier assignment contains one of the recorded local obstruction templates.
It does not prove Erdos Problem #97 and does not give a counterexample.

## Commands

Check the source packet and the combined template catalog:

```bash
python scripts/check_n9_vertex_circle_self_edge_template_packet.py \
  --check \
  --assert-expected \
  --json

python scripts/check_n9_vertex_circle_template_lemma_catalog.py \
  --check \
  --assert-expected \
  --json
```

The family-record audit can be reproduced by parsing
`data/certificates/n9_vertex_circle_self_edge_template_packet.json` and
checking:

```text
strict_inequality.outer_pair == distance_equality.start_pair
strict_inequality.inner_pair == distance_equality.end_pair
```

for every family record.

## Review Standard

Before using this criterion in a proof, a reviewer should independently check
the two local inputs for the particular row core under discussion:

1. the selected rows really force the displayed equality path; and
2. the vertex-circle witness order really forces the displayed strict edge.

Once those two inputs are established, the contradiction in this note is just
the incompatibility of `D(p) = D(q)` with `D(p) > D(q)`.
