# Bootstrap T12 Forcing Targets

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note is a second-pass diagnostic on
[`bootstrap-vertex-circle-overlay.md`](bootstrap-vertex-circle-overlay.md). The
checked artifact is:

```bash
python scripts/check_bootstrap_t12_forcing_targets.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_forcing_targets.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_forcing_targets.json`.

## Scope

The input records are still fixed selected-row diagnostics. They are not full
rich-class data for a hypothetical polygon, they do not certify Euclidean
realizability, and they do not promote the review-pending `n=9`
vertex-circle checker. The purpose is narrower: name exactly what a future
bridge lemma would need to force after the two tight non-ear bootstrap rows
both land on the `T12/F16` strict-cycle template.

The artifact records:

- which `T12/F16` row centers are outside the bootstrap core `[0,1,2,4]`;
- whether those outside rows are strict-edge rows or equality-connector rows;
- where the strict-cycle quotient pairs sit relative to the bootstrap core;
- which strict-cycle pairs are direct private-pair hits in the bootstrap
  private-halo ledger.

## Results

Both tight rows still need row centers beyond the bootstrap core.

| Bridge source id | Classification id | Capacity margin | Missing T12 row centers | Row-gap roles | Direct private-pair hits |
|---:|---|---:|---|---|---|
| `81` | `A082` | `8` | `[3,8]` | two equality-connector rows | none |
| `151` | `A152` | `6` | `[5,6,7,8]` | two strict-edge rows and three equality-connector rows | `[5,8]`, `[6,8]` |

For source `81`, every strict-edge row is already in the bootstrap core, but
the equality connector uses row centers `3` and `8`. Its unique T12 cycle pairs
have location counts:

```text
core_core: 2
core_outside: 5
outside_outside: 0
```

None of those unique cycle pairs is a direct private-pair hit.

For source `151`, the strict cycle itself uses strict-edge rows outside the
bootstrap core. Its unique T12 cycle pairs have location counts:

```text
core_core: 1
core_outside: 3
outside_outside: 3
```

Only two outside-outside pairs, `[5,8]` and `[6,8]`, are direct private-pair
hits.

## Reading

This refines the next conjectural bridge target from the overlay note:

```text
bootstrap core [0,1,2,4] + tight private-halo geometry
  -> force the missing T12/F16 row centers or equivalent equality connectors
```

The negative controls are as useful as the positive contact:

- a core-only contradiction is blocked, because both records require rows
  outside `[0,1,2,4]`;
- a private-pair-only contradiction is also blocked, because source `81` has
  no direct private-pair hit and source `151` has only partial direct hits.

So the promising route is not simply to spend the existing capacity ledger
harder. A future bridge needs an extra metric/order ingredient that turns
private halos, row-center placement, or equality-connector availability into
the missing `T12/F16` local rows.
