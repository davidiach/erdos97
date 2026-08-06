# Fragile-cycle three-halo hinge/splice motif crosswalk

Status: exact bounded motif compression plus two direct local lemmas. This
note does not claim a geometric forcing theorem, a proof of `n=10`, a general
proof, or a counterexample.

## Purpose

The natural-order Kalmanson endgame gives one minimized three-selected-row
certificate for each of thirteen fixed deep-frontier states. The remaining
proof-facing question is whether those are thirteen genuinely different
local targets.

They are not. After unused witnesses are forgotten, the packet has only three
motif classes:

| Motif | States | Generic ordered roles |
| --- | ---: | ---: |
| Equilateral hinge | 11 | 4 |
| Five-role `K2/K1` splice | 1 (`S11`) | 5 |
| Six-role `K1/K2` splice | 1 (`S08`) | 6 |

Every one-inequality certificate is exactly one orientation of the existing
arbitrary-size equilateral-hinge lemma. Both splice states are hinge-free and
have exactly one order-preserving embedding of their respective template.

## Five-role splice lemma

Let `a<b<c<d<e` be five vertices in their polygonal cyclic order. Suppose
three rich classes contain these witness pairs:

```text
center a: {b,c}
center b: {c,e}
center d: {b,e}
```

The selected equalities are

```text
d(a,b) = d(a,c),
d(b,c) = d(b,e),
d(b,d) = d(d,e).
```

Add the strict inequalities `K2(a,b,c,d)` and `K1(a,b,d,e)`:

```text
[d(a,c)+d(b,d)-d(a,d)-d(b,c)]
+ [d(a,d)+d(b,e)-d(a,b)-d(d,e)] > 0.
```

The `d(a,d)` terms cancel directly and the three selected equalities cancel
everything else. The strict sum is exactly zero, a contradiction.

## Six-role splice lemma

Let `a<b<c<d<e<f` be six vertices in cyclic order, with rich-class pairs

```text
center b: {a,e}
center c: {a,f}
center d: {e,f}.
```

Add `K1(a,b,c,e)` and `K2(c,d,e,f)`:

```text
[d(a,c)+d(b,e)-d(a,b)-d(c,e)]
+ [d(c,e)+d(d,f)-d(c,f)-d(d,e)] > 0.
```

The `d(c,e)` terms cancel directly. The three centered equalities again make
the remaining sum exactly zero.

For both templates the checker verifies with exact integer coefficient
vectors that:

- neither strict inequality is individually a self-edge;
- their unit-weight sum reduces to zero;
- exactly one ordinary-distance pair cancels before quotienting; and
- removing any one of the three selected equalities leaves a nonzero vector.

Thus each splice footprint is inclusion-minimal in its three displayed
centered equalities. No numerical optimization result is used.

## Crosswalk details

For each source state the checker independently replays its stored Kalmanson
certificate, scans every cyclic quadrilateral for equilateral hinges, and
scans all order-preserving five- and six-role embeddings for the two splice
templates.

The exact classification is:

```text
S01-S07, S09, S10, S12, S13 -> equilateral hinge
S08                            -> six-role K1/K2 splice
S11                            -> five-role K2/K1 splice
```

Twelve full three-row cores contain one reciprocal selected-center pair;
`S08` contains none. This reciprocal-pair count is only descriptive: the
active splice footprint in `S11` does not use its core's reciprocal edge, and
a reciprocal pair by itself is not an obstruction.

## Sharpened entry target

Conditional on reaching the fixed three-halo deep catalog, thirteen terminal
states have now become three local alternatives:

```text
equilateral hinge
or five-role Kalmanson splice
or six-role Kalmanson splice.
```

The missing Contract F step is correspondingly narrower: force one of these
three pair-membership motifs from the `23=27` retained core and genuine active
halo geometry, or force a separately checked rich-class/deletion alternative.
The crosswalk does not prove that implication and does not control arbitrary
halo counts.

## Replay

```bash
python scripts/check_fragile_cycle_three_halo_motif_crosswalk.py \
  --check --assert-expected --summary-json

python scripts/check_fragile_cycle_three_halo_kalmanson_endgame.py \
  --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_cycle_three_halo_motif_crosswalk.json`; do not edit
it directly.
