# n=9 radius-blocker rich-extension product sweep

Status: `REVIEW_PENDING_DIAGNOSTIC` / finite generated-packet diagnostic. No
general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note widens the one-packet replay in
`docs/n9-radius-blocker-rich-extension-product-pilot.md` to all `20` generated
source packets from `docs/n9-radius-blocker-rich-quotient-sweep.md`. For each
source packet, the checker enumerates the full Cartesian product of
radius-blocker-preserving added labels, turning every exact-four row into a
synthetic size-five rich class.

The full generated product contains `2,899,968` variants. The source packet
product sizes are:

```text
110,592 variants: 8 packets
147,456 variants: 7 packets
196,608 variants: 5 packets
```

## Checked Result

The checked artifact is:

```text
data/certificates/n9_radius_blocker_rich_extension_product_sweep.json
```

Verify it with:

```bash
python scripts/check_n9_radius_blocker_rich_extension_product_sweep.py --check --assert-expected --json
```

All `2,899,968` variants are obstructed by quotient self-edges. The replay
checks `26,099,712` size-five rich classes and `652,492,800` strict
vertex-circle edges, with `467,149,054` total self-edge conflicts. The first
self-edge row is row `0` in every variant.

The Hamming-distance distribution from the baseline packets is:

```text
distance 0:      20
distance 1:     497
distance 2:   5,479
distance 3:  35,167
distance 4: 144,819
distance 5: 396,765
distance 6: 723,141
distance 7: 845,397
distance 8: 575,181
distance 9: 173,502
```

## Boundary

This exhausts the full extension product only for the `20` generated source
packets. It does not enumerate arbitrary rich-class catalogues, does not prove
that all radius-blockers are impossible, does not prove `n=9`, does not prove
the adaptive radius-blocker bridge, and does not prove Erdos Problem #97.

The next useful step is no longer another copy of the same generated-packet
product. It is a principled minimal/rich-class bridge hypothesis or a checker
that leaves this generated packet family and reaches arbitrary rich-class
catalogues.
