# Bootstrap T12 151:6 Endpoint-8 Forcing Preflight

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note records the current gate decision for the source-`151` row-`6`
outside-pair question:

```text
Can current checked evidence force endpoint 8 into every genuine outside-pair
support at center 6?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_endpoint8_forcing_preflight.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_endpoint8_forcing_preflight.json
```

## Inputs

This preflight is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_outside_pair_connector_contract.json`;
- `data/certificates/bootstrap_t12_151_6_outside_pair_escape_partition.json`.

The connector contract says that an endpoint-`8` support would be enough:
if a genuine rich class at center `6` contains witnesses `0` and `8`, then
the connector equality `[0,6]=[8,6]` is available.

The escape partition says that the current selected-row diagnostics do not
force such an endpoint support: the private-halo-only connector-avoiding lane
with support pair `[3,5]` has `12` complete assignments after the basic
incidence/crossing filters.

## Gate Result

The preflight result is:

```text
NOT_READY_PRIVATE_HALO_ONLY_ESCAPE_SURVIVES_BASIC_FILTERS
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| endpoint-`8` support pairs | `[[3,8], [5,8]]` |
| connector-avoiding support pairs | `[[3,5]]` |
| private-halo-only target rows | `4` |
| private-halo-only basic survivors | `12` |
| private-halo-only vertex-circle survivors | `0` |
| endpoint-`8` connector-available basic survivors | `16` |
| endpoint-`8` forced by current evidence | `false` |

The red-light reason is not that endpoint-`8` supports are useless. They would
supply the connector conditionally. The reason is that current evidence still
has a connector-avoiding support lane, and that lane is not killed by the
basic filters.

## Remaining Target

The next proof-facing lemma is still one of:

```text
Force an endpoint-8 outside-pair support under genuine minimal/rich-class
hypotheses.
```

or:

```text
Prove that the private-halo-only pair [3,5] cannot occur under those
hypotheses.
```

The vertex-circle replay killing all selected-row survivors is useful
diagnostic evidence, but it is not a support-existence theorem, not a row
forcing theorem, and not an endpoint-`8` forcing theorem.

## What This Does Not Prove

This artifact does not prove endpoint-`8` support existence, does not prove
row forcing, does not prove that pair `[3,5]` is impossible, does not prove
`n=9`, does not prove the bootstrap bridge, and does not prove Erdos Problem
#97.
