# Bootstrap T12 Closure-Exposed Rows

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the easiest subcase of the
[`bootstrap-t12-row-pressure.md`](bootstrap-t12-row-pressure.md) ledger: missing
`T12/F16` rows whose row center and at least three selected witnesses are
already visible inside a deletion closure.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_closure_exposed.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_closure_exposed.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_closure_exposed.json`.

## Scope

The input is fixed selected-row bookkeeping from the row-pressure diagnostic.
A closure-exposed row is not a Euclidean certificate and does not prove that a
real rich-class/minimal-counterexample geometry must contain that selected
row. It only records a local activation-ready state inside the existing
deletion-closure ledger.

The artifact records, for each isolated row:

- the source assignment and missing row center;
- the deletion closure exposing the row center;
- the three bootstrap-core witnesses already in that closure;
- whether the full selected row is contained in the same closure or whether
  only the row center plus three core witnesses are present.

## Results

Exactly two row-pressure gaps are closure-exposed.

| Source row | Role | Exposing deletion core | Closure mode |
|---|---|---:|---|
| `81:3` | equality connector | `2` | center and full selected row in closure |
| `151:7` | strict edge | `2` | center and three core witnesses in closure |

Both rows use the same core witness signature:

```text
[0,1,4]
```

For source `81`, the deletion closure for core vertex `2` is
`[0,1,3,4,6]`. It contains row center `3` and the whole selected row
`{0,1,4,6}`.

For source `151`, the deletion closure for core vertex `2` is `[0,1,4,7]`.
It contains row center `7` and three witnesses `[0,1,4]`; the outside witness
`6` remains private.

## Reading

This packet narrows one small target for a future bridge lemma:

```text
Can deletion-closure activation readiness force an actual rich-class row, or
is it only an artifact of the fixed selected-row overlay?
```

The packet does not answer that question. It simply separates the two
closure-exposed rows from the harder one-outside-label and outside-pair cases
so future proof attempts can state their hypotheses more sharply.
