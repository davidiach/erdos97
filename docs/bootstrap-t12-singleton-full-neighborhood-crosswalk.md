# Bootstrap/T12 singleton full-neighborhood crosswalk

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This crosswalk joins the current full-neighborhood vertex-circle diagnostics
for the three one-outside-label singleton-support row targets:

```text
81:8
151:5
151:8
```

Run the checker with:

```bash
python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py --check --assert-expected --json
```

Regenerate the artifact with:

```bash
python scripts/check_bootstrap_t12_singleton_full_neighborhood_crosswalk.py --write --assert-expected
```

## Scope

The source packets are:

```text
data/certificates/bootstrap_t12_81_8_full_neighborhood_vertex_circle.json
data/certificates/bootstrap_t12_151_singleton_full_neighborhood_vertex_circle.json
```

The crosswalk checks only that these stored packets agree on the natural
`n=9` cyclic order, full-neighborhood row-option semantics, target rows, and
aggregate vertex-circle closure counts. It does not rerun the full-neighborhood
searches. It does not prove singleton-support existence, row forcing, `n=9`,
the bootstrap bridge, Erdos Problem #97, or any official/global status update.

## Counts

| Quantity | Value |
|---|---:|
| target rows | 3 |
| target row candidates | 27 |
| implicit selected-assignment space | 15,564,962,700,000,000 |
| search nodes in source packets | 38,719 |
| empty domains in source packets | 20,395 |
| basic-filter complete assignments | 84 |
| non-original target-row complete assignments | 63 |
| vertex-circle self-edges | 64 |
| vertex-circle strict cycles | 20 |
| vertex-circle survivors | 0 |

Target-row split:

| target | basic survivors | non-original target survivors | vertex-circle statuses |
|---|---:|---:|---|
| `81:8` | 34 | 27 | `27` self-edge, `7` strict cycle |
| `151:5` | 34 | 27 | `27` self-edge, `7` strict cycle |
| `151:8` | 16 | 9 | `10` self-edge, `6` strict cycle |

## Interpretation

This packet is a bridge-facing boundary marker. Across the current
one-outside-label singleton-support targets, the full selected-row
neighborhood is not forced back to the original target rows by the basic
incidence/crossing filters alone: `63` complete assignments use non-original
target rows. The stored source packets show that exact vertex-circle quotient
replay kills all complete basic-filter assignments.

The remaining gap is therefore still the genuine minimal/rich-class bridge:
prove or exclude singleton-support existence and row forcing before, or in
addition to, these selected-row neighborhood moves.
