# n=9 radius-blocker rich-extension neighborhood

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note widens `docs/n9-radius-blocker-rich-quotient-sweep.md` by replacing
the single deterministic added label in the generated size-five rich classes.
For each of the `20` stored shape-sweep obstruction examples, the checker first
builds the deterministic baseline packet, then enumerates every added-label
variant at Hamming distance `1` or `2` from that baseline.

The row catalogue contains every extra label that preserves the actual
radius-blocker condition: if a row center is inside the blocker, the enlarged
rich class must still contain fewer than three blocker vertices. For centers
outside the blocker, blocker intersection is recorded but is not constrained
by the radius-blocker definition.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_extension_neighborhood.json
```

Verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_extension_neighborhood.py --check --assert-expected --json
```

The neighborhood has `5,996` radius-blocker-preserving variants:

```text
distance 0:    20
distance 1:   497
distance 2: 5,479
```

All `5,996` variants are obstructed by quotient self-edges. The replay checks
`53,964` size-five rich classes and `1,349,100` strict vertex-circle edges,
with `1,017,368` total self-edge conflicts. The first self-edge row is row `0`
in every variant.

## Boundary

This is a Hamming-distance `<= 2` neighborhood around the generated baseline
packets, not the full Cartesian product of every size-five row extension and
not an enumeration of arbitrary rich-class catalogues. It does not prove that
all radius-blockers are impossible, does not prove `n=9`, does not prove the
adaptive radius-blocker bridge, and does not prove Erdos Problem #97.

The next useful widening is either the full extension-product catalogue for a
carefully chosen small packet, or a genuine minimal/rich-class bridge
hypothesis that narrows which richer catalogues must be checked.
