# Bootstrap T12 151:6 Label-4 Center-8 Core Route

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note is a route map after the center-`8` rich-triple preflight and source
crosswalk. The previous checks recorded two constraints:

```text
The center-8 cascade target [0,4,6] is sufficient only conditionally, and the
existing source-151 row-8 singleton packet does not supply it.
```

This packet asks the next narrow question:

```text
Inside the source-151 row-6 private-lane strict-core split, which local cores
would actually supply a center-8 row containing [0,4,6]?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_core_route.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_core_route.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_core_route.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_private_lane_strict_core_split.json`;
- `data/certificates/bootstrap_t12_151_6_label4_cascade_endpoint8_targets.json`.

## Gate Result

The route gate is:

```text
NOT_READY_CENTER8_TARGET_COMPATIBLE_CORE_NOT_FORCED
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| private-lane assignments | `12` |
| row-`6` three-row strict cores | `44` |
| label-`8`-visible cores | `32` |
| center-`8` cores | `9` |
| center-`8` target-compatible cores | `8` |
| label-`8`-visible target-compatible cores | `4` |
| assignments with any center-`8` target core | `6` |
| assignments without any center-`8` target core | `6` |
| label-`8`-visible cores that are not center-`8` cores | `27` |

The target-compatible exact rows are:

| Center-`8` row | Count |
| --- | ---: |
| `[0,1,4,6]` | `4` |
| `[0,2,4,6]` | `2` |
| `[0,4,6,7]` | `2` |

The endpoint packet allows five exact center-`8` rows containing `[0,4,6]`;
this route map covers three of them and leaves `[0,3,4,6]` and `[0,4,5,6]`
unseen in the private-lane strict-core split.

## Reading

The useful conclusion is:

```text
Forcing an arbitrary label-8-visible row-6 local core is not enough. A future
bridge step must force a target-compatible center-8 local core, or provide a
separate support-rich obstruction for the remaining private-lane assignments.
```

This is slightly sharper than the earlier preflight. It shows that the desired
center-`8` route does occur in the checked local-core catalog, but it is not
universal: half of the private-lane assignments still have no center-`8` core
containing `[0,4,6]`, and most label-`8`-visible cores use label `8` only as an
auxiliary-row witness rather than as row center `8`.

## What This Does Not Prove

This artifact does not prove support existence, does not prove row forcing,
does not prove endpoint-`8` forcing, does not prove that pair `[3,5]` is
impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
