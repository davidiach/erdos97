# n=9 radius-blocker shape sweep

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records the natural-order widening of the full exact-four
radius-blocker packet. Instead of fixing only

```text
U = {0,1,2,3},
```

it checks all `10` four-vertex blocker shapes up to cyclic-dihedral symmetry in
the natural cyclic order `[0,1,2,3,4,5,6,7,8]`. Their orbit sizes sum to
`126 = binom(9,4)`, so every labelled four-vertex blocker in this fixed order
is represented.

For each blocker `U`, the packet includes every exact four-row avoiding the
center and containing at most two vertices of `U` for centers in `U`; centers
outside `U` keep every exact four-row avoiding the center. Thus `U` is a
radius-blocker for each packet by construction.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_shape_sweep.json
```

Regenerate and verify it with:

```bash
python scripts/check_n9_radius_blocker_shape_sweep.py --check --assert-expected
```

The exact search visits `754,505` packet nodes across the `10` shape
representatives and finds `1,358` incidence survivors after the row-pair cap,
witness-pair cap, indegree cap, and two-overlap crossing filters. Every
incidence survivor is obstructed by selected-distance vertex-circle replay:

| vertex-circle status | count |
| --- | ---: |
| `self_edge` | 1,164 |
| `strict_cycle` | 194 |

The per-shape counts are:

| blocker representative | orbit size | incidence survivors | self-edge | strict-cycle |
| --- | ---: | ---: | ---: | ---: |
| `[0,1,2,3]` | 9 | 90 | 70 | 20 |
| `[0,1,2,4]` | 18 | 118 | 97 | 21 |
| `[0,1,2,5]` | 18 | 111 | 93 | 18 |
| `[0,1,3,4]` | 9 | 148 | 134 | 14 |
| `[0,1,3,5]` | 18 | 142 | 121 | 21 |
| `[0,1,3,6]` | 18 | 141 | 125 | 16 |
| `[0,1,3,7]` | 9 | 136 | 120 | 16 |
| `[0,1,4,5]` | 9 | 168 | 144 | 24 |
| `[0,1,4,6]` | 9 | 158 | 136 | 22 |
| `[0,2,4,6]` | 9 | 146 | 124 | 22 |

## Interpretation

This widens the previous full `{0,1,2,3}` packet from one blocker placement to
all dihedrally distinct four-vertex blocker shapes in the fixed natural order.
It is still not a proof of the full adaptive blocker bridge, because the cyclic
order is fixed and the packet is restricted to exact four-row rich classes.

The order-reduction crosswalk in `docs/n9-radius-blocker-order-reduction.md`
records why arbitrary cyclic-order placements of a four-blocker reduce to this
natural-order shape sweep for the exact-four packet. The useful next widening
is therefore a rich-class replay semantics that handles classes larger than
four without prematurely choosing one exact four-subset.
