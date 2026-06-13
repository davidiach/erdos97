# Bootstrap T12 151:6 Label-4 Center-8 Source Crosswalk

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note is a source-routing check after the center-`8` rich-triple
preflight. The previous preflight recorded:

```text
The source-151 row-6 label-4 cascade has a conditional center-8 target
[0,4,6], but the current support ledger does not force that target.
```

This crosswalk asks the next narrow question:

```text
Can the existing source-151 row-8 singleton/one-outside packet be reused as
the source for the center-8 cascade triple [0,4,6]?
```

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_source_crosswalk.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_151_6_label4_center8_source_crosswalk.py --write --assert-expected
```

to:

```text
data/certificates/bootstrap_t12_151_6_label4_center8_source_crosswalk.json
```

## Inputs

This packet joins:

- `data/certificates/bootstrap_t12_151_6_label4_center8_rich_triple_preflight.json`;
- `data/certificates/bootstrap_t12_151_singleton_support_audit.json`;
- `data/certificates/bootstrap_t12_one_outside.json`;
- `data/certificates/bootstrap_t12_151_6_label4_cascade_endpoint8_targets.json`.

The distinction matters because two proof targets use center `8` language:

| Target phrase | Meaning |
| --- | --- |
| source-`151` row-`8` singleton packet | activation-family audit for rows containing core `[1,2]` and one singleton support from `[5,7]` |
| source-`151` row-`6` center-`8` cascade target | conditional rich-class target centered at `8` containing witnesses `[0,4,6]` |

## Gate Result

The crosswalk result is:

```text
NOT_READY_EXISTING_SOURCE151_CENTER8_SINGLETON_DOES_NOT_SUPPLY_CASCADE_TRIPLE
```

Pinned summary:

| Quantity | Value |
| --- | ---: |
| cascade target row | `151:6` |
| conditional center-`8` target | `[0,4,6]` |
| source-`151` named center-`8` row | `151:8` |
| source-`151` row-`8` bootstrap core | `[1,2]` |
| source-`151` row-`8` singleton supports | `[5,7]` |
| checked singleton candidate rows | `9` |
| candidate rows containing any one target label | `6` |
| candidate rows containing a target pair from `[0,4,6]` | `0` |
| candidate rows containing full `[0,4,6]` | `0` |
| maximum overlap with `[0,4,6]` | `1` |
| raw one-outside activation triples meeting `[0,4,6]` | `0` |

The reason is combinatorial within the checked activation-family source:
every row-`8` singleton candidate contains `[1,2]` and one of `[5,7]`, leaving
only one remaining label slot for the cascade triple `[0,4,6]`.

## Reading

The useful conclusion is:

```text
The existing source-151 row-8 singleton packet is not a source for the
center-8 cascade triple [0,4,6].
```

So the next bridge lemma still needs new geometry: prove a genuine center-`8`
rich class containing `[0,4,6]` in the source-`151` row-`6` cascade package, or
find a different support-rich obstruction.

## What This Does Not Prove

This artifact does not prove support existence, does not prove row forcing,
does not prove endpoint-`8` forcing, does not prove that pair `[3,5]` is
impossible, does not prove `n=9`, does not prove the bootstrap bridge, and
does not prove Erdos Problem #97.
