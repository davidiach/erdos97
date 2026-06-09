# Bootstrap T12 151:6 Label-4 Transfer Paths

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the source-`151` row-`6` private-lane residual target from
quotient-class incidence to explicit selected-distance equality paths. The
previous quotient-role ledger shows that every label-`8`-free residual strict
cycle has a label-`4`-bearing quotient class. This packet records how label
`4` reaches the actual strict-cycle endpoint pairs inside those classes.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_paths.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_transfer_paths.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_transfer_paths.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label8_free_residual_targets.json`;
- `data/certificates/bootstrap_t12_151_6_label4_quotient_roles.json`.

For each residual signature, the checker rebuilds the selected-distance
equality graph from the stored selected rows. It then records a shortest path
from a label-`4` pair in each label-`4` cycle quotient class to a strict-cycle
endpoint pair in the same class.

## Transfer-Path Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| label-`4` transfer class incidences | `19` |
| occurrence-weighted class incidences | `23` |
| direct endpoint class incidences | `11` |
| occurrence-weighted direct endpoint incidences | `14` |
| one-equality-edge class incidences | `5` |
| occurrence-weighted one-edge incidences | `5` |
| two-equality-edge class incidences | `3` |
| occurrence-weighted two-edge incidences | `4` |
| signatures with a positive-length transfer class | `8` |
| occurrences with a positive-length transfer class | `9` |

Transfer length histogram:

| Equality edges in shortest transfer | Signature incidences | Occurrence incidences |
| ---: | ---: | ---: |
| `0` | `11` | `14` |
| `1` | `5` | `5` |
| `2` | `3` | `4` |

The positive transfer-path edges occur only in rows `5`, `6`, and `7`:

| Row | Signature-edge count | Occurrence-edge count |
| ---: | ---: | ---: |
| `5` | `6` | `7` |
| `6` | `3` | `4` |
| `7` | `2` | `2` |

The two quotient-equality-only residual signatures both have one-edge transfer
paths through row `5`. The two-edge transfers appear only inside
direct-cycle-edge access signatures, where another cycle class already has a
direct label-`4` endpoint hit.

## Reading

The next proof-facing target is now row-local:

```text
Any genuine source-151 row-6 private-halo residual support must realize
one of the recorded label-4 transfer paths through rows 5, 6, and 7,
or else force endpoint 8 / a label-8-visible row-6 local core.
```

This does not prove that the residual support geometry is impossible. It does
turn the residual label-`4` transfer into explicit selected-distance row
equalities that a support-geometry argument can attack.

## What This Does Not Prove

This artifact does not prove outside-pair support existence, does not prove row
forcing, does not prove that pair `[3,5]` is impossible, does not prove
endpoint-`8` forcing, does not prove `n=9`, does not prove the bootstrap
bridge, and does not prove Erdos Problem #97.
