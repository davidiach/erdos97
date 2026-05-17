# n=9 radius-blocker rich-extension product pilot

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite packet diagnostic. No general
proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note widens `docs/n9-radius-blocker-rich-extension-neighborhood.md` for
one generated source packet. The full `20`-packet extension product has
`2,899,968` variants, so this pilot chooses the first maximum-size source
packet in stable source-artifact order and exhausts that packet first.

The selected packet is:

```text
n9_full_exact_four_radius_blocker_shape_U0135_natural_order:self_edge:0
```

Its row option counts are:

```text
[3,4,4,4,4,4,4,4,4]
```

This gives `196,608` radius-blocker-preserving size-five extension variants.

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_extension_product_pilot.json
```

Verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_extension_product_pilot.py --check --assert-expected --json
```

All `196,608` variants are obstructed by quotient self-edges. The replay checks
`1,769,472` size-five rich classes and `44,236,800` strict vertex-circle edges,
with `33,895,908` total self-edge conflicts. The first self-edge row is row
`0` in every variant.

The Hamming-distance distribution from the baseline packet is:

```text
distance 0:      1
distance 1:     26
distance 2:    300
distance 3:  2,016
distance 4:  8,694
distance 5: 24,948
distance 6: 47,628
distance 7: 58,320
distance 8: 41,553
distance 9: 13,122
```

## Boundary

This is a full Cartesian product only for one selected source packet. It does
not enumerate the full product for all `20` generated packets, does not
enumerate arbitrary rich-class catalogues, does not prove that all
radius-blockers are impossible, does not prove `n=9`, does not prove the
adaptive radius-blocker bridge, and does not prove Erdos Problem #97.

The next useful widening is another selected-packet product replay, a batched
full-product sweep with stronger pruning, or a genuine minimal/rich-class
bridge hypothesis that narrows which richer catalogues must be checked.
