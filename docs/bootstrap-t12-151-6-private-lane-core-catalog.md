# Bootstrap T12 151:6 Private-Lane Core Catalog

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note sharpens the selected-row diagnostic for the source-`151` row-`6`
private-halo-only outside-pair lane. The previous endpoint-`8` forcing
preflight records that endpoint `8` is not forced by current evidence because
the private pair `[3,5]` still survives the basic filters. This packet asks a
smaller follow-up question inside that lane:

```text
When the private target row is [0,3,5,7], how local are the exact
vertex-circle obstructions?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_private_lane_core_catalog.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_private_lane_core_catalog.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_private_lane_core_catalog.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_endpoint8_forcing_preflight.json`.

It uses the `12` basic-filter survivors in the private-halo-only target row:

```text
6 -> [0,3,5,7]
```

For each survivor, it enumerates row-subset-minimal vertex-circle obstruction
cores and then chooses one deterministic minimal core that includes center
`6`.

## Catalog Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| private-lane survivors | `12` |
| source survivor statuses | `self_edge: 10`, `strict_cycle: 2` |
| all minimal core occurrences | `282` |
| all minimal core sizes | `3: 124`, `4: 144`, `5: 14` |
| all minimal core statuses | `self_edge: 42`, `strict_cycle: 240` |
| row-`6` minimal core occurrences | `118` |
| row-`6` minimal core sizes | `3: 48`, `4: 64`, `5: 6` |
| row-`6` minimal core statuses | `self_edge: 6`, `strict_cycle: 112` |
| survivors with a row-`6` three-row core | `12` |
| chosen row-`6` core statuses | `strict_cycle: 12` |
| distinct chosen exact cores | `10` |

Thus every private-lane survivor has a three-row strict-cycle obstruction
core containing the private target row `6 -> [0,3,5,7]`.

## Reading

This is a useful narrowing of the `[3,5]` escape target. It says that, inside
the selected-row full-neighborhood diagnostic, the private lane does not need
a large global obstruction: row `6` plus two other rows already force an exact
vertex-circle strict cycle in each survivor.

The remaining proof-facing question is still support geometry. A bridge lemma
would need to explain why genuine minimal/rich-class hypotheses force one of
these row-`6` local cores, force endpoint `8`, or rule out the private pair
`[3,5]` directly.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove
row forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
