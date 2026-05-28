# Closure Activation Negative Controls

Status: `EXACT_NEGATIVE_CONTROL` / `PROVENANCE`. No general proof of Erdos
Problem #97 is claimed. No counterexample is claimed.

This note records RS-2026-05-10-A stress tests for closure-activation
bridge work. Their purpose is narrow: prevent a proof route from silently
upgrading deletion-closure exposure into a fixed selected-row forcing lemma.

Run the wrong-fourth replay checker with:

```bash
python scripts/check_closure_activation_wrong_fourth_negative_control.py --check --assert-expected --json
```

Run the aggregate rich-class replay checker with:

```bash
python scripts/check_closure_activation_negative_controls.py --check --assert-expected --json
```

Run the full selected-row anti-activation checker with:

```bash
python scripts/check_bootstrap_t12_anti_activation_negative_control.py --check --assert-expected --json
```

Run the closure-visibility replay checker with:

```bash
python scripts/check_closure_visibility_anti_activation_control.py --check --assert-expected --json
```

Regenerate the checked JSON artifacts with:

```bash
python scripts/check_closure_activation_wrong_fourth_negative_control.py --write
python scripts/check_closure_activation_negative_controls.py --write
python scripts/check_bootstrap_t12_anti_activation_negative_control.py --write
python scripts/check_closure_visibility_anti_activation_control.py --write
```

## Wrong-fourth control

The checked artifact is
`data/certificates/closure_activation_wrong_fourth_negative_control.json`.
It uses cyclic order:

```text
0,1,2,3,4,5,6,7,8,9
```

and selected rows:

```text
0 -> {1,2,6,9}
1 -> {0,2,4,7}
2 -> {3,4,8,9}
3 -> {1,4,5,6}
4 -> {2,5,7,9}
5 -> {0,3,6,8}
6 -> {1,3,5,7}
7 -> {0,1,4,9}
8 -> {3,6,7,9}
9 -> {0,2,5,8}
```

Starting from seed `{0,1,4}`, the rich-triple closure rule adds any center
whose selected row already has at least three witnesses in the current closure.
The computed closure is:

```text
cl({0,1,4}) = {0,1,4,7}
```

Thus the closure exposes center `7` and the triple `{0,1,4}`. But row `7` is
`{0,1,4,9}`, not `{0,1,4,6}`. The target fourth `6` remains outside the
closure, and the target row `{0,1,4,6}` is absent from the selected-row system.

## Checked hypotheses

The replay checker verifies:

- every row has four distinct witnesses;
- no center appears in its own row;
- row-pair intersections have size at most two;
- witness-pairs occur together in at most two rows;
- every two-overlap source chord crosses its common-witness chord in the
  supplied cyclic order;
- the seed closure is exactly `{0,1,4,7}`;
- the exposed row has the wrong fourth witness `9`, while the target fourth
  `6` is not forced.

These are abstract finite checks only. They do not use Euclidean coordinates,
critical-radius ordering, exact rich-class uniqueness, triangle inequalities,
Ptolemy identities, or Kalmanson inequalities.

## Bridge lesson

This control blocks only the overstrong activation principle:

```text
center plus three target witnesses visible in a deletion closure
=> the fixed selected row with the desired fourth witness is forced.
```

It does not refute the T12 strict-cycle local lemma packet, because that packet
assumes exact selected rows. It also does not refute a future activation lemma
with an additional condition that identifies the fourth witness, such as
criticality, rich-class uniqueness, radius ordering, row-substitution
obstructions, or an all-fourth obstruction check.

## Rich-class fourth-switch controls

The checked aggregate artifact is
`data/certificates/closure_activation_negative_controls.json`. It records four
small abstract rich-class controls from runs `RS-2026-05-10-CE-A` and
`RS-2026-05-10-A`.

Two minimal role-focused controls are named directly:

```text
NC1_three_core_trigger_unpinned_fourth
NC2_full_label_visibility_without_center_class_membership
```

`NC1` uses rich class `{0,1,4,5}` at center `7` to activate the center from
seed `{0,1,4}` while leaving the target row `{0,1,4,6}` inactive. `NC2` uses
rich classes `{0,1,4,5}` at center `3` and `{1,3,4,7}` at center `6`; closure
then contains all labels of target row `{0,1,4,6}`, but label `6` entered for
an independent reason and still is not in center `3`'s rich class.

The first control targets the source-151 strict-edge row-pressure shape:

```text
seed = {0,1,4}
target center = 7
target row = 7 -> {0,1,4,6}
rich class at 7 = {0,1,4,8}
closure = {0,1,4,7}
```

The center and core witnesses are closure-exposed, and the center is activated
by the exposed triple, but the fourth witness is `8` rather than the target
private witness `6`. Thus closure activation through the core triple still
does not identify the exact strict-edge row.

The second control targets the source-81 row-pressure shape:

```text
seed = {0,1,4}
target center = 3
target row = 3 -> {0,1,4,6}
rich class at 3 = {0,1,4,8}
rich class at 6 = {0,3,4,5}
closure = {0,1,3,4,6}
```

Here the closure contains the target center and all four target row labels
`{0,1,4,6}`, but the target row is still inactive at center `3`. The listed
rich rows share `{0,4}`, and the source chord `{3,6}` crosses the witness chord
`{0,4}` in the supplied cyclic order.

These controls motivate a sharper row-pressure split:

```text
pair_connector_activated:
  needed equality endpoints lie inside the triggering triple.

pinned_fourth_needed:
  the named fourth witness is certified to lie in the same rich class.

interval_stability_needed:
  the actual activated row supports the same vertex-circle strict inequality.
```

The aggregate checker intentionally proves neither side of that split. It only
keeps the abstract countermodels replayable.

## Full selected-row anti-activation control

The checked artifact is
`data/certificates/bootstrap_t12_anti_activation_negative_control.json`. It is
a full abstract selected-row incidence system on cyclic order:

```text
0,1,2,3,4,5,6,7,8,9
```

with selected rows:

```text
0 -> {1,2,5,9}
1 -> {0,2,4,7}
2 -> {1,3,5,7}
3 -> {1,4,8,9}
4 -> {0,2,5,8}
5 -> {2,6,7,9}
6 -> {4,5,7,8}
7 -> {0,1,3,4}
8 -> {0,5,6,9}
9 -> {2,3,6,8}
```

The closure seed is `{0,1,4}`. Row `7` contains all three seed witnesses, so
closure adds center `7` and then stops:

```text
cl({0,1,4}) = {0,1,4,7}
```

But the row at center `7` is `{0,1,3,4}`, not the target row `{0,1,4,6}`. This
is a full-row incidence-level anti-activation object: it verifies
four-uniformity, self-exclusion, vertex cover, row-pair cap, two-overlap
crossing in the supplied cyclic order, and adjacent row-pair intersections of
size at most one.

It is still not a Euclidean realization certificate and not evidence of a
counterexample. It only rules out deriving the pinned fourth witness `6` from
these abstract incidence and closure checks alone.

## Closure-visibility anti-activation control

The checked artifact is
`data/certificates/closure_visibility_anti_activation_control.json`.
It uses cyclic order:

```text
0,1,2,3,4,5,6,7,8
```

and two sparse rich rows:

```text
3 -> {0,1,4,6}
7 -> {0,3,4,8}
```

The target row-pressure shape is center `7`, target witnesses `{0,1,4}`,
private target witness `6`, and target row `{0,1,4,6}`. Starting from seed
`{0,1,4}`, closure proceeds as:

```text
{0,1,4}
  -> add 3 via {0,1,4}
  -> {0,1,3,4}
  -> add 7 via {0,3,4}
  -> {0,1,3,4,7}
```

At the end, the closure contains center `7` and all target witnesses
`{0,1,4}`. But center `7` entered through the different triple `{0,3,4}`; its
row is `{0,3,4,8}`, which contains neither the target triple `{0,1,4}` nor the
target row `{0,1,4,6}`.

The replay checker verifies four-uniformity, self-exclusion, the row-pair cap,
the witness-pair cap, and the two-overlap crossing of source chord `{3,7}` with
witness chord `{0,4}` in the supplied cyclic order.

This control blocks only the overstrong visibility principle:

```text
center c in cl(A) and target triple T subset cl(A)
=> c has a selected/rich row containing T.
```

It does not refute a bridge lemma that includes activation provenance, such as
"center `c` entered closure because of target triple `T`", nor a lemma that
adds critical-row uniqueness or an all-fourth obstruction check.
