# Fragile Critical-radius Midpoint Diagnostic

Status: `EXACT_LOCAL_RADIUS_MIDPOINT_TRICHOTOMY_DIAGNOSTIC`.

This note isolates one genuine metric consequence of a two-overlap pair of
selected rows and tests it on the standing fragile-cover controls. It is a
partial bridge diagnostic. It does not force entry into the three-halo
hinge/splice catalog, prove geometric realizability, prove Erdos Problem #97,
or give a counterexample.

## Local lemma

Let distinct selected-row centers `y,z` share the two witnesses `{u,v}`. Write
their selected radii as `r_y,r_z`, and let `m=(u+v)/2`. Both centers are on the
perpendicular bisector of `uv`. Subtracting the two Pythagorean identities gives

```text
r_y^2-r_z^2 = |y-m|^2-|z-m|^2.
```

This gives an exact trichotomy:

- `r_y=r_z`: because the two chords cross at `m`, the point `m` is also the
  midpoint of `yz`. Thus `uv` and `yz` are mutual perpendicular bisectors and
  the four alternating labels form a rhombus. On either coordinate axis,

  ```text
  X_y+X_z-X_u-X_v=0.
  ```

- `r_y<r_z`: the center `y` is strictly closer to `m` than `z`.
- `r_z<r_y`: the center `z` is strictly closer to `m` than `y`.

The equal-radius conclusion is a rhombus, not generally a rectangle.

The checker replays the polynomial identity exactly. If

```text
F_y=|y-u|^2-|y-v|^2,
F_z=|z-u|^2-|z-v|^2,
```

then direct expansion verifies

```text
2*((r_y^2-r_z^2)-(|y-m|^2-|z-m|^2)) = F_y-F_z.
```

Both `F_y` and `F_z` vanish on the common perpendicular bisector.

## Branch certificate

For a fixed selected-row system, the diagnostic chooses one of the three
branches at every two-overlap relation.

Equal branches are closed under transitivity of radius equality. Their
midpoint equations are row-reduced exactly over the rationals. If those
equations force two distinct point labels to have the same value on both
coordinate axes, that branch is impossible for a strictly convex polygon.

The remaining strict branches are oriented by a displayed total order of the
equal-radius components. This is an explicit acyclic radius-order witness. Its
existence means only that this local diagnostic has not found a contradiction;
it is not a metric or Euclidean realization.

## Exact control results

The checked packet contains three fixed benchmarks.

| Benchmark | Two-overlaps | All-equal branch | Block-atom equalities, other branches strict |
|---|---:|---|---|
| exact six-label block-6 atom | 1 | survives; realized by the existing exact atom | survives |
| no-forward-ear two-block full extension | 18 | rank 11; all 12 point labels collapse | survives with 2 equal and 16 strict relations |
| fixed block-6 survivor extension 3 | 18 | rank 11; all 12 point labels collapse | survives with 2 equal and 16 strict relations |

For each twelve-row system, the mixed escape keeps the two genuine block
relations

```text
(0,3) -> {2,4}
(6,9) -> {8,10}
```

on their equal-radius rhombus branches. The other 16 relations admit the
displayed acyclic strict-radius orientation. Therefore the lemma rejects the
global all-equal branch but does not reject either full-row control.

## Reproduction

```bash
python scripts/check_fragile_radius_midpoint.py --check --assert-expected --summary-json
```

The generated artifact is
`data/certificates/fragile_radius_midpoint.json`. Rewrite it only after an
intentional generator change:

```bash
python scripts/check_fragile_radius_midpoint.py --write --assert-expected --summary-json
```

## What this changes

The midpoint lemma supplies a reusable exact metric branch that was absent
from the fragile-cover hypergraph axioms. It also identifies the remaining
forcing obligation sharply: the `23=27` active-halo geometry must force enough
equal-radius midpoint equations or strict-radius directions to eliminate the
mixed branch escapes. Merely finding more two-overlap relations cannot do
that, because an arbitrary relation graph always admits an acyclic all-strict
orientation.

No general proof, counterexample, finite-case promotion, or official/global
status update is claimed.
