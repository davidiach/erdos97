# Bootstrap T12 One-Outside-Label Rows

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the one-outside-label subcase of the
[`bootstrap-t12-row-pressure.md`](bootstrap-t12-row-pressure.md) ledger:
missing `T12/F16` rows with two bootstrap-core witnesses, one singleton
outside-label support, and a row center that remains private in every deletion
closure.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_one_outside.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_one_outside.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_one_outside.json`.

## Scope

The input is fixed selected-row bookkeeping from the row-pressure diagnostic.
A singleton outside support is an activation record, not a Euclidean
rich-class certificate. This packet does not prove that any missing row is
forced in a real minimal counterexample.

The artifact records, for each isolated row:

- the source assignment and missing row center;
- the two witnesses already in the bootstrap core `[0,1,2,4]`;
- the singleton outside labels that make the row activation-ready;
- whether each singleton support is private in every deletion halo or already
  internal to one deletion closure;
- whether the row center remains private in all deletion closures.

## Results

Exactly three row-pressure gaps need one outside label.

| Source row | Role | Core witnesses | Singleton supports |
|---|---|---|---|
| `81:8` | equality connector | `[0,2]` | `5` private in all halos; `6` internal to core `2` closure |
| `151:5` | equality connector | `[2,4]` | `7` internal to core `2` closure; `8` private in all halos |
| `151:8` | strict edge, equality connector | `[1,2]` | `5` private in all halos; `7` internal to core `2` closure |

Across the three rows, labels `5` and `7` each appear as singleton support in
two rows; labels `6` and `8` appear once. Each row has one support private in
all deletion halos and one support already internal to the deletion closure
for core vertex `2`.

All three row centers remain private in every deletion closure. None of the
singleton supports has a direct private-pair ledger hit, which is expected:
this is a one-label activation problem, so pair capacity does not see it
directly.

## Reading

This packet narrows the next bridge question:

```text
Can genuine rich-class geometry force a private row center together with one
of its singleton outside supports, or is this only fixed selected-row
bookkeeping?
```

The packet does not answer that question. It separates the one-outside-label
rows from the closure-exposed rows and the single outside-pair row so future
bridge attempts can state exactly which hypothesis they need.
