# Row-Ptolemy Product Filter

Status: `EXACT_OBSTRUCTION` for fixed selected-witness patterns with a supplied
or certified row witness order. The generated n=9 sweep is exploratory
bookkeeping only; it is not a proof of `n=9`, not a counterexample, not a
geometric realizability test, and not a global status update.

## Lemma

Let one selected row have center `i` and four distinct witnesses
`w0,w1,w2,w3` in cyclic order around `i`. Because the witnesses lie on the
circle centered at `i`, Ptolemy's theorem gives

```text
d02*d13 = d01*d23 + d03*d12,
```

where `dab` denotes the Euclidean distance `|w_a w_b|`.

If the selected-distance quotient forces

```text
d02 = d23
d13 = d01
```

then substituting into Ptolemy cancels the left product with the first product
on the right, leaving `d03*d12 = 0`. That is impossible for distinct vertices
in a strictly convex polygon. Thus the fixed selected-witness pattern is
obstructed under the supplied row order.

The row order is part of the hypothesis. The selected-distance quotient alone
does not determine which witness pairs are sides and diagonals in Ptolemy, so
this is not an orderless abstract-incidence obstruction unless all compatible
orders have been checked separately.

## n=9 Sweep

The artifact
`data/certificates/n9_row_ptolemy_product_cancellations.json` applies the
filter to the 184 complete `n=9` selected-witness assignments that survive the
pair/crossing/count filters before the vertex-circle filter.

It records:

- `26` hit assignments out of `184`;
- `216` row-local certificates after checking all cyclic rotations of the row
  Ptolemy cancellation;
- `3` deterministic dihedral family labels: `F02`, `F09`, and `F13`;
- all hits are vertex-circle `self_edge` cases in the current n=9 frontier.

This gives an independent Ptolemy-equality certificate for those fixed-order
assignments, but it does not dominate or replace the vertex-circle checker and
does not prove the full `n=9` finite case.

The same artifact now includes a crosswalk to
`data/certificates/n9_vertex_circle_core_templates.json`. This is a diagnostic
join on deterministic family/template labels only:

```text
F02 -> T08, self_edge, orbit 18, row-Ptolemy certificates 108
F09 -> T01, self_edge, orbit  6, row-Ptolemy certificates  72
F13 -> T04, self_edge, orbit  2, row-Ptolemy certificates  36
```

The hit assignment count matches the full dihedral orbit size for each of
these three family labels. The crosswalk is useful for comparing local lemma
shapes, but the template ids are artifact labels, not theorem names, and this
does not promote the review-pending n=9 status.

## Negative Controls And Order Guardrails

The checked artifact now has regression coverage for both the positive and
negative family labels in the current `n=9` frontier. The row-Ptolemy sweep
hits only `F02`, `F09`, and `F13`. The remaining 13 deterministic family labels
are kept as negative controls with zero row-Ptolemy certificates:

```text
F01,F03,F04,F05,F06,F07,F08,F10,F11,F12,F14,F15,F16
```

Those negative controls cover `158` of the `184` pre-vertex-circle assignments.
They are bookkeeping guardrails, not evidence that those assignments are
geometrically realizable or that the vertex-circle obstruction is unnecessary.
They occupy nine local-core template ids with no row-Ptolemy hits:

```text
T02,T03,T05,T06,T07,T09,T10,T11,T12
```

All strict-cycle local-core families, currently `F07`, `F12`, and `F16`, are in
this no-hit side of the crosswalk.

## Family-Signature Diagnostic

The companion artifact
`data/certificates/n9_row_ptolemy_family_signatures.json` compresses the
row-Ptolemy hit records into per-family certificate histograms. It is a
proof-search aid for spotting reusable-looking local shapes, not a proof and
not a lemma statement.

For the current fixed natural order, all row-Ptolemy hits use the same
Ptolemy-side signature: the two stored `cancel_d01_d23...` variants cancel
`d01*d23` and force the zero product `d03*d12`. The family-level distinction
is how many rows in each assignment carry this two-certificate local pattern:

```text
F02 -> T08: 3 hit rows per assignment,  6 certificates per assignment
F09 -> T01: 6 hit rows per assignment, 12 certificates per assignment
F13 -> T04: 9 hit rows per assignment, 18 certificates per assignment
```

Across each full dihedral family orbit, every center label appears equally
often in the stored certificates. These uniform histograms are prompts for
local-lemma extraction only; each underlying certificate remains tied to the
fixed selected-witness pattern and supplied row order.

The checker also replays every stored hit record against its fixed cyclic
order. It verifies that each certificate's `witness_order`, forced-equality
pair names, and zero-product pair names match the supplied row order. A
scrambled non-dihedral order for the first `F02` representative has zero
row-Ptolemy product-cancellation certificates, while the stored natural order
has six. This is why the row order remains part of the certificate hypothesis.

## Reproduction

```bash
python scripts/analyze_n9_row_ptolemy_product_cancellations.py \
  --assert-expected \
  --out data/certificates/n9_row_ptolemy_product_cancellations.json

python scripts/check_n9_row_ptolemy_product_cancellations.py --check --json

python scripts/check_n9_row_ptolemy_family_signatures.py \
  --assert-expected \
  --write

python scripts/check_n9_row_ptolemy_family_signatures.py \
  --check \
  --assert-expected \
  --json
```
