# n=9 Vertex-circle Directed Strict-cycle Criterion

Status: `REVIEW_PENDING_DIAGNOSTIC_ONLY`.

This note records the common local contradiction behind the `T10` through
`T12` vertex-circle strict-cycle packets. It does not claim a proof of `n=9`,
does not claim a counterexample, does not complete independent review of the
exhaustive checker, and does not update the official/global status.

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
