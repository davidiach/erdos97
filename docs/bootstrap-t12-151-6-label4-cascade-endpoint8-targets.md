# Bootstrap T12 151:6 Label-4 Cascade Endpoint-8 Targets

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines the row-`8` obligation from the source-`151` row-`6`
label-`4` cascade row-criticality packet. The previous packet showed that the
three stored cascade signatures need all three local rows `{5,6,8}`. This
packet asks a slightly richer question:

```text
If rows 5 and 6 are the stored cascade package, how much of row 8 is enough
to keep the quotient obstruction?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_cascade_endpoint8_targets.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_cascade_endpoint8_targets.json
```

## Inputs

This packet is a derivative check over:

- `data/certificates/bootstrap_t12_151_6_label4_cascade_row_criticality.json`.

For each of the three cascade signatures, rows `5` and `6` are kept as the
stored cascade package. Row `8` is replaced by every rich class at center `8`
whose witness set contains the triple:

```text
[0,4,6]
```

The remaining endpoint labels are drawn from `[1,2,3,5,7]`, so there are `31`
rich-class supersets per cascade signature.

## Endpoint Target Result

Pinned summary:

| Quantity | Value |
| --- | ---: |
| cascade signature indices | `7, 8, 9` |
| endpoint center | `8` |
| endpoint rich triple | `[0,4,6]` |
| rich supersets per signature | `31` |
| signature-level rich supersets checked | `93` |
| occurrence-weighted rich supersets checked | `124` |
| signature-level obstructed rich supersets | `93` |
| occurrence-weighted obstructed rich supersets | `124` |
| signature-level status counts | `72` self-edge, `21` strict cycle |
| occurrence-weighted status counts | `96` self-edge, `28` strict cycle |

The three endpoint rows already present in the row-criticality packet are:

```text
[0,2,4,6], [0,4,6,7], [0,1,4,6]
```

They are only three of the five exact four-set extensions of `[0,4,6]`:

```text
[0,1,4,6], [0,2,4,6], [0,3,4,6], [0,4,5,6], [0,4,6,7]
```

Across those exact four-set rows, the packet records `9` strict-cycle
obstructions and `6` self-edge obstructions. The two additional exact rows
`[0,3,4,6]` and `[0,4,5,6]` are already self-edge obstructed against the same
row-`5`/row-`6` cascade equalities.

## Reading

The useful narrowing is:

```text
For the stored label-4 cascade packages, a genuine center-8 rich class
containing witnesses [0,4,6] is enough to close the quotient graph.
```

So the next bridge target is sharper than forcing one of the three previously
seen row-`8` exact rows. It is enough, conditionally, to force the rich endpoint
triple `[0,4,6]` at center `8` alongside the row-`5`/row-`6` cascade package.

This is still a conditional target. It does not show that a minimal or
bootstrap-core counterexample must contain that rich class.

## What This Does Not Prove

This artifact does not prove support existence, does not prove row forcing,
does not prove that pair `[3,5]` is impossible, does not prove endpoint-`8`
forcing, does not prove `n=9`, does not prove the bootstrap bridge, and does
not prove Erdos Problem #97.
