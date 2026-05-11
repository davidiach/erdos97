# Bootstrap T12 81:3 Closure Target

Status: `REVIEW_PENDING_DIAGNOSTIC`. No general proof of Erdos Problem #97 is
claimed. No counterexample is claimed.

This note isolates the current first bootstrap/T12 bridge target: source `81`,
row center `3`. It is the only row that is both relation-sufficient and fully
contained in a deletion closure. It also supplies the final equality connector
in the review-pending `T12/F16` strict-cycle local packet.

The checked artifact is:

```bash
python scripts/check_bootstrap_t12_81_3_closure_target.py --check --assert-expected --json
```

The generator writes:

```bash
python scripts/check_bootstrap_t12_81_3_closure_target.py --write --assert-expected
```

to `data/certificates/bootstrap_t12_81_3_closure_target.json`.

## Scope

The input packets are:

- `data/certificates/bootstrap_t12_closure_exposed.json`;
- `data/certificates/bootstrap_t12_relation_sufficient_rows.json`;
- `data/certificates/n9_vertex_circle_t12_strict_cycle_lemma_packet.json`.

This packet is still fixed selected-row bookkeeping. Full containment of a
stored selected row in a deletion closure is not a theorem that a real rich
distance class must contain that row. The T12 connector role is useful only
conditionally: it matters if a future bridge proves row `81:3` as a genuine
rich class, or at least proves the equality connector supplied by that row.

## Target Record

For source `81` / assignment `A082`, the row is:

```text
center 3 -> witnesses [0,1,4,6]
```

The exposing deletion closure is for core vertex `2`:

```text
seed [0,1,4]
closure labels [0,1,3,4,6]
```

So the closure contains the row center and all four fixed selected witnesses.
The relation-sufficient packet records the connector requirement:

```text
81:3:connector:2:0
required witnesses [0,1]
relation state BOOTSTRAP_CORE_SUFFICIENT
```

The focused packet records the remaining gap as:

```text
FIXED_FULL_ROW_CLOSURE_NOT_RICH_CLASS_FORCING
```

## T12 Role

In the `T12/F16` local strict-cycle packet, row `3` is the one-step equality
connector:

```text
[1,3] = [0,3]
```

This closes the third strict-cycle step, where row `0` gives the strict edge

```text
[1,7] > [1,3].
```

If row `81:3` is genuinely available as a rich selected row, then the stored
T12 local packet can use it to identify the inner pair `[1,3]` with the next
outer pair `[0,3]`. The packet does not prove that availability.

## Candidate Lemma Contract

A future proof-facing lemma should prove one of the following:

- center `3` has a rich class containing witnesses `[0,1,4,6]`;
- center `3` forces at least the equality connector `[1,3]=[0,3]`;
- or there is a precise rich-class escape mechanism showing how the fixed row
  can be present in the closure ledger without becoming a usable connector.

The first two outcomes would move this target toward the obstruction machinery.
The third would sharpen the blocker side of the bridge.

## What This Does Not Prove

This artifact does not prove that row `81:3`, the connector pair, or any rich
class is forced. It does not prove `n=9`, does not prove the bootstrap bridge,
does not independently review the vertex-circle checker, and does not alter
the official/global status of Erdos Problem #97.

## Reviewer Focus

The next useful question is no longer "is `81:3` relation-sufficient?" The
artifact pins that down. The useful question is:

```text
Can the 81:3 full-row deletion-closure exposure be promoted to genuine
rich-class or equality-connector forcing?
```

If not, the escape packet should say exactly how a realizable rich-class
catalogue avoids the connector despite the fixed-row closure evidence.

The follow-up packet
`docs/bootstrap-t12-81-3-rich-triple-contract.md` records the first reduction
of this question: full-row forcing is not needed for the stored connector. It
is enough for a genuine rich class at center `3` to contain witnesses `0` and
`1`; avoiding that connector requires every such rich class to avoid the pair
`[0,1]`, so any connector-avoiding activation through the fixed witness set
must expose label `6` first.
