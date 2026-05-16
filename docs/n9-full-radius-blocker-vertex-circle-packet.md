# n=9 full radius-blocker vertex-circle packet

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note records a finite exact-four row-option packet:

```text
n = 9
cyclic order = [0,1,2,3,4,5,6,7,8]
blocker U = {0,1,2,3}
```

For every center in `U`, the packet includes every exact four-row avoiding the
center and containing at most two vertices of `U`. For centers outside `U`, the
packet includes every exact four-row avoiding the center. Thus `U` is a
radius-blocker for the packet by construction.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_full_radius_blocker_vertex_circle_packet.json
```

Regenerate and verify it with:

```bash
python scripts/check_n9_full_radius_blocker_vertex_circle_packet.py --check --assert-expected
```

The exact search visits `58,742` packet nodes and finds `90` incidence survivors
after the row-pair cap, witness-pair cap, indegree cap, and two-overlap crossing
filters. Every survivor is obstructed by selected-distance vertex-circle replay:

| vertex-circle status | count |
| --- | ---: |
| `self_edge` | 70 |
| `strict_cycle` | 20 |

The row-option counts are:

```text
[65,65,65,65,70,70,70,70,70]
```

## Interpretation

This is stronger than the first fixed-row pilot because it quantifies over all
exact four-row choices compatible with the fixed blocker `U` in the fixed
natural order. It is still not a proof of the full adaptive blocker bridge,
because the cyclic order and blocker subset are fixed and the packet is
restricted to exact four-row classes.

The dihedral blocker-placement widening is now recorded in
`docs/n9-radius-blocker-shape-sweep.md`, and
`docs/n9-radius-blocker-order-reduction.md` records why arbitrary cyclic-order
placements of the same exact-four four-blocker packet reduce to that shape
sweep. The useful next widening is a replay semantics for rich classes larger
than four.
