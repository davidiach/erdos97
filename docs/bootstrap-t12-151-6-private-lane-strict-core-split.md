# Bootstrap T12 151:6 Private-Lane Strict-Core Split

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note turns the source-`151` row-`6` private-halo-only core catalog into a
smaller proof-target map. The previous catalog shows that every private-lane
basic-filter survivor has a three-row strict-cycle core containing:

```text
6 -> [0,3,5,7]
```

This packet asks which of those row-`6` three-row strict-cycle cores make label
`8` visible through an auxiliary row, and which remain label-`8`-free.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_private_lane_strict_core_split.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_private_lane_strict_core_split.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_private_lane_strict_core_split.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_outside_pair_full_neighborhood_vertex_circle.json`;
- `data/certificates/bootstrap_t12_151_6_private_lane_core_catalog.json`.

It recomputes all row-`6` three-row strict-cycle minimal cores from the
private-halo-only target lane, not just the deterministic chosen core recorded
in the previous catalog.

## Split Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| private-lane survivors | `12` |
| row-`6` three-row strict-cycle cores | `44` |
| survivors with a row-`6` three-row strict-cycle core | `12` |
| label-`8`-visible cores | `32` |
| label-`8`-free cores | `12` |
| survivors with a label-`8`-visible core | `12` |
| survivors with a label-`8`-free core | `8` |
| survivors without a label-`8`-free core | `4` |
| distinct exact cores | `36` |
| distinct label-`8`-visible exact cores | `26` |
| distinct label-`8`-free exact cores | `10` |

The important correction is that endpoint-`8` visibility is available in every
survivor, but it is not the whole story: `8` survivors also have label-`8`-free
strict-cycle alternatives. Those `10` distinct exact label-`8`-free signatures
are now listed directly in the artifact.

## Reading

This is a bridge-target map, not a bridge proof. It says the private `[3,5]`
lane can be attacked in two smaller ways:

- prove that genuine support geometry must instantiate one of the
  label-`8`-visible auxiliary-row cores, thereby making endpoint `8` relevant
  outside the private target row; or
- prove that the residual label-`8`-free exact signatures cannot arise from
  genuine minimal/rich-class support geometry.

The second bullet is the hard residual case. It is now finite and explicit:
`12` label-`8`-free core occurrences, with `10` distinct exact row signatures.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
