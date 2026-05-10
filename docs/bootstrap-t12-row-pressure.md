# Bootstrap T12 Row Pressure

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note refines
[`bootstrap-t12-forcing-targets.md`](bootstrap-t12-forcing-targets.md) by
classifying each missing `T12/F16` row center against the bootstrap core,
deletion closures, and private halos. The checked artifact is:

```bash
python scripts/check_bootstrap_t12_row_pressure.py --check --assert-expected
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_row_pressure.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_row_pressure.json`.

## Scope

The input is still fixed selected-row bookkeeping. A row-pressure class is not
a Euclidean certificate and does not prove that a missing row is forced in a
real minimal counterexample. The diagnostic only records which kind of bridge
ingredient would be needed for each missing `T12/F16` row.

The artifact records, for each missing row center:

- how many selected witnesses already lie in the bootstrap core `[0,1,2,4]`;
- the outside-label deficit needed to activate the row from that core;
- whether the row center is already exposed in a deletion closure;
- whether the row center stays private in every deletion closure;
- whether an outside-pair deficit has direct private-pair ledger support.

## Results

The six missing row centers split into three pressure classes.

| Pressure class | Count | Rows |
|---|---:|---|
| Already present in a deletion closure | `2` | `81:3`, `151:7` |
| Needs one outside label and a private center | `3` | `81:8`, `151:5`, `151:8` |
| Needs an outside pair and a private center | `1` | `151:6` |

Equivalently, the bootstrap-core activation deficits are:

```text
deficit 0: 2 rows
deficit 1: 3 rows
deficit 2: 1 row
```

The rows `81:3` and `151:7` each have three core witnesses and are already
visible in the deletion closure for core vertex `2`. These are not the hard
part of the row-center bridge.

The focused closure-exposed packet
[`bootstrap-t12-closure-exposed.md`](bootstrap-t12-closure-exposed.md) records
this subcase separately. It distinguishes `81:3`, whose full selected row is
inside the exposing deletion closure, from `151:7`, whose row center and three
core witnesses are present while the outside witness remains private.

The rows `81:8`, `151:5`, and `151:8` each have two core witnesses. They need
one outside label to become activation-ready from the bootstrap core, while
their row centers remain private across all deletion closures.

The focused one-outside-label packet
[`bootstrap-t12-one-outside.md`](bootstrap-t12-one-outside.md) records this
subcase separately. It distinguishes, for each row, the singleton support that
is private in all deletion halos from the singleton support that is already
internal to the deletion closure for core vertex `2`.

The row `151:6` has only one core witness. It needs an outside pair, and two
of its possible outside pairs, `[3,8]` and `[5,8]`, hit the existing
private-pair ledger.

The focused outside-pair packet
[`bootstrap-t12-outside-pair.md`](bootstrap-t12-outside-pair.md) records this
last subcase separately. It distinguishes the two ledger-hit support pairs
from the private-halo-only support pair `[3,5]`.

## Reading

This narrows the next proof-mining question:

```text
Can closure-exposed rows, one-outside-label rows, and the single outside-pair
row be forced from genuine rich-class geometry, rather than from fixed
selected-row bookkeeping?
```

The answer is not supplied here. The ledger says only that a future bridge
lemma probably needs more than the current weighted private-pair count:

- two rows are deletion-closure bookkeeping rows;
- three rows are single-outside-label problems, so pair capacity alone does
  not see them directly;
- one row is a genuine outside-pair problem with partial private-pair support.
