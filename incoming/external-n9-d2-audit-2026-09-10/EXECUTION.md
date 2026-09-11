# Execution record

Status: `VERIFICATION_PENDING / NO_ACCEPTED_CLAIM_CHANGE`.

## Original preparation

The original editing shell had no Lean toolchain or outbound DNS access. A fresh hosted
build was therefore started in draft PR #946. Initial dependency/toolchain
setup succeeded and target compilation was reached; this is not a completed
axiom audit. Early bootstrap executions are not substitutes for the final
source-pinned harness run.

The 37 synthetic harness tests passed locally before integration. Those tests
exercise parsing, source/hash guards, failure receipts, stale-output rejection,
and process timeouts. They do not establish any Lean theorem.

Full repository checks and the hosted axiom audit must be recorded with their
actual outcomes and exact run/head identifiers before claiming a verified
import. A failed, canceled, timed-out, or still-running job is not a pass.

No accepted theorem, bound, or global status is changed by this packet.

## Repository review, 11 September 2026

The final original harness run
[34525126394](https://github.com/davidiach/erdos97/actions/runs/34525126394),
on `3ec8b348d033a334785add0b05be8f9bf56d6587`, was cancelled at its
45-minute job limit. Toolchain setup and dependency materialization passed;
the combined audit step did not finish. It supplied no passing final receipt.
The 45-minute job budget was shorter than the four permitted 30-minute command
budgets. The revised workflow allows two 60-minute builds, two five-minute
consumers, and setup/upload time within a 150-minute job budget.

The earlier combined-target bootstrap reported parser errors in the pinned
upstream `SurplusCOMPGBank.lean` (blob
`088c5201f0eb0d02fb4380c37f5824ff79844a64`) at `315:50`, `1964:36`,
`1987:15`, and `2010:77`. These were build findings before cancellation;
they do not refute either statement or establish separate group outcomes.
The upstream source pin has not been changed or patched.

Main now separately retains a successful n9-only reproduction in
[the external n9 audit note](../../docs/external-n9-reproduction-2026-09-10.md).
That evidence is for its own consumer and execution, not a completed run of
this six-declaration n9/D2 harness and not a D2 acceptance receipt.

Windows review exposed UTF-8 decoding failures in the synthetic tests and a
POSIX-only timeout cleanup path. Both have been repaired. Additional regression
controls cover complete axiom lines, all six required declarations, and changes
to either consumer before or after its own compilation. Interim receipts now
preserve non-verification when a job is interrupted. Final integration checks
and the revised hosted execution are tracked on PR #946.
