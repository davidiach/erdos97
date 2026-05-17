# n=9 radius-blocker richer-class projection pilot

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records a first bounded check beyond the exact-four radius-blocker
packet. It does not add full rich-class quotient semantics. Instead it uses a
forgetful projection: a rich class of size larger than four contributes every
exact four-subset as a possible selected row, and the existing finite packet
replay checks those selected-row options.

The pilot starts from the checked `U = {0,1,2,3}` obstruction example in
`data/certificates/n9_radius_blocker_shape_sweep.json`. At every center, the
source exact four-row is enlarged to one synthetic size-five rich class by
adding a label that keeps the blocker condition valid for centers in `U`.
Thus the projected packet has row-option counts

```text
[5,5,5,5,5,5,5,5,5],
```

for a raw upper bound of `5^9 = 1,953,125` selected-row projections.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_projection_pilot.json
```

Regenerate and verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_projection_pilot.py --check --assert-expected
```

The exact search visits `20` packet nodes after the incidence/order filters.
It finds `1` incidence survivor, and that survivor is obstructed by
selected-distance vertex-circle replay with status `self_edge`.

## Projection Boundary

This pilot is deliberately weaker than the missing rich-class bridge. The
projection checks selected four-subsets of larger rich classes, but it forgets
the equality data involving vertices omitted from a chosen four-subset. It
therefore does not prove that arbitrary richer-than-four rich-class systems
reduce to exact-four packets, and it does not classify `n=9`.

The useful next target is a full rich-class quotient replay, or a bridge lemma
showing that a suitable four-subset projection is sound for the obstruction
being used.
