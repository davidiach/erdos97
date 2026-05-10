# Bootstrap T12 Outside-Pair Row

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the outside-pair subcase of the
[`bootstrap-t12-row-pressure.md`](bootstrap-t12-row-pressure.md) ledger: the
single missing `T12/F16` row with one bootstrap-core witness, two needed
outside labels, and a row center that remains private in every deletion
closure.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_outside_pair.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_outside_pair.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_outside_pair.json`.

## Scope

The input is fixed selected-row bookkeeping from the row-pressure diagnostic.
An outside-pair support is an activation record, not a Euclidean rich-class
certificate. A private-pair ledger hit is a useful contact with the
bootstrap-core capacity ledger, but it does not prove that the row is forced
in a real minimal counterexample.

The artifact records:

- the source assignment and missing row center;
- the one witness already in the bootstrap core `[0,1,2,4]`;
- the three outside-pair supports that make the row activation-ready;
- which supports hit the private-pair ledger;
- whether each support pair is private in every deletion halo;
- whether the row center remains private in all deletion closures.

## Results

Exactly one row-pressure gap needs an outside pair.

| Source row | Role | Core witnesses | Outside pair supports |
|---|---|---|---|
| `151:6` | equality connector | `[0]` | `[3,5]` private-halo only; `[3,8]` ledger hit at core `0`; `[5,8]` ledger hit at core `2` |

All three outside pairs are private in every deletion halo. Two pairs,
`[3,8]` and `[5,8]`, also hit the existing private-pair ledger. The remaining
pair, `[3,5]`, is private-halo-only.

The row center `6` remains private in every deletion closure. No deletion
closure contains more than one witness from the row, so this is the hardest
row-pressure subcase left after the closure-exposed and one-outside-label
packets.

## Reading

This packet narrows the next bridge question:

```text
Can genuine rich-class geometry force an equality-connector row from one
bootstrap-core witness plus an outside pair with partial private-pair ledger
support?
```

The packet does not answer that question. It records that the outside-pair
case is the only subcase where the existing private-pair ledger makes direct
contact with the missing `T12/F16` row-pressure gaps.
