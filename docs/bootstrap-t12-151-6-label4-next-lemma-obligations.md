# Bootstrap T12 151:6 Label-4 Next-Lemma Obligations

Status: `REVIEW_PENDING_DIAGNOSTIC`.

No general proof of Erdos Problem #97 is claimed. No counterexample is claimed.

This note is a bridge-work contract for the source-`151`, row-`6`, label-`4`
private-lane target. It joins the latest three route-decision packets:

- `docs/bootstrap-t12-151-6-endpoint8-forcing-preflight.md`;
- `docs/bootstrap-t12-151-6-label4-center8-migration-support-crosswalk.md`;
- `docs/bootstrap-t12-151-6-label4-target-sparse-order-sensitivity-crosswalk.md`.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_next_lemma_obligations.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_next_lemma_obligations.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_next_lemma_obligations.json
```

## Open Obligations

The packet records three still-open obligations:

| Obligation | Current blocker | Useful success criterion |
| --- | --- | --- |
| `private_halo_endpoint8_exclusion` | private-halo pair `[3,5]` has `12` basic-filter survivors | force endpoint `8`, or prove `[3,5]` cannot occur under genuine support hypotheses |
| `center8_migration_or_source` | current support requirements are centered at `5`, `6`, and `7`, with no center-`8` support requirement | prove center migration, or supply an independent center-`8` rich class containing `[0,4,6]` |
| `target_sparse_order_or_geometry` | the natural-order `255`-row strict-family route is exactly blocked, while one alternate order is exactly obstructed | prove useful cyclic-order structure, add stronger exact strict rows, or prove endpoint/source geometry |

Pinned summary:

```json
{
  "open_obligation_count": 3,
  "open_obligation_ids": [
    "private_halo_endpoint8_exclusion",
    "center8_migration_or_source",
    "target_sparse_order_or_geometry"
  ],
  "private_halo_only_basic_survivor_count": 12,
  "support_requirement_center8_count": 0,
  "current_row_family_all_order_route_ready": false,
  "all_order_obstruction_proved": false,
  "solves_n9": false,
  "solves_erdos97": false
}
```

## Dead-End Guards

The packet also records shortcuts that should not be reused as bridge progress:

```text
endpoint-8 support forced by current evidence
selected-row vertex-circle replay as support existence
same-center support backing as center-8 migration
the source-151 row-8 singleton packet as a source for [0,4,6]
label-8 visibility as a target-compatible center-8 core
natural-order dual certificates as realizability evidence
alternate-order certificates as all-order obstruction
another solver-only cone screen over the same 255-row family
```

## Reading

The useful next work must add a genuine ingredient. The current route cannot
advance by another selected-row neighborhood widening or by another solver-only
screen around the same `151:6` cone. The three productive directions are:

```text
exclude the private-halo pair [3,5] or force endpoint 8
prove center-8 migration or an independent center-8 [0,4,6] source
prove order forcing, stronger exact rows, or endpoint/source geometry for the
target-sparse lane
```

## What This Does Not Prove

This artifact does not prove support existence, does not prove center
migration, does not prove row forcing, does not prove endpoint-`8` forcing,
does not prove pair `[3,5]` impossible, does not prove assignments `0` or `11`
possible or impossible, does not prove an all-order obstruction, does not prove
`n=9`, does not prove the bootstrap bridge, and does not prove Erdos Problem
#97.
