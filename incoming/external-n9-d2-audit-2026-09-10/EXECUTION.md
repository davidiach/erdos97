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

The retained artifact from the final original run was downloaded during this
review. It supplies more specific pre-cancellation evidence: `n9-build.log`
ends with `AUDIT COMMAND TIMED OUT` after job 8967/8983, and the separate
`d2-build.log` contains the same four upstream parser errors plus
`Lean exited with code 1`. The D2 build was still processing other jobs when
the workflow was cancelled, so no final group receipt or axiom audit exists.
SHA-256 of the downloaded log bytes:

- `n9-build.log`: `3e8d2ec3ee81760ba6ee7619a3a98df71857c7bfd4e15c03fa9b3f6871372f3e`
- `d2-build.log`: `63bb171f1578dd65fc06c53d0249817159bb67449539c8d28947ec8c98bb4544`

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

All 45 focused audit-tool regressions pass on Windows/Python 3.12.2 when the
process can terminate its own timeout-test child. The existing workflow-gate
tests also needed explicit shell resolution and preservation of the OS
environment. They now prefer Bash bundled with Git on Windows, avoiding the
system32 WSL launcher; all 14 tests in that module pass without a PATH override. These
are tooling results only. At that original pin the D2 source errors remained a
merge blocker for verified-import acceptance; no failing check was bypassed.

## Completed original-pin audit and upstream repair

Hosted run [34576340728](https://github.com/davidiach/erdos97/actions/runs/34576340728)
finished on local head `270bc182daad426fac4e845bd9fb9b3ece424913` with
`NOT_VERIFIED`, after rechecking the source, consumers, and dependency pins.
The original receipt and provenance are retained byte-for-byte under
[`evidence/34576340728/`](evidence/34576340728/receipt.json).

- n9: the module and both independent statement adapters compiled. All four
  named declarations passed with exactly `propext`, `Classical.choice`, and
  `Quot.sound`. The complete axiom output is retained beside the receipt.
- D2: the module build completed with exit code 1 and the same four parser
  errors in `SurplusCOMPGBank.lean`. Its consumer was not executed.

Downloaded evidence SHA-256 identifiers:

| File | SHA-256 |
|---|---|
| `receipt.json` | `1fa89088cc76d7c6d2928608831ba406b805bd3790b0f7e647f480911c4188f7` |
| `n9-build.log` | `284fae7ab9454d49e508a6c9b4a67f4a4adbd558337a9251c39f869bdcde0390` |
| `n9-axioms.log` | `02b38df37020ed6fbd27155907269ff3aa618793f126f57aa6f0cb2062c40a24` |
| `d2-build.log` | `d5f4139b86cea7047ddf3cdd5d2399f603853d07a2c4260d1ff46ea9a3fc827e` |

The full build logs were inspected in the downloaded
[artifact 10192053739](https://github.com/davidiach/erdos97/actions/runs/34576340728/artifacts/10192053739).
They are subject to its 14-day retention limit; only the compact receipt,
bootstrap provenance, and complete n9 axiom output are retained in this packet.

Upstream then published
[`76559d59f934d81e5081b40e0e621b39f759f7fa`](https://github.com/mysticflounder/erdos-97-96-formalization/commit/76559d59f934d81e5081b40e0e621b39f759f7fa),
the immediate child of the original pin. Review of its complete five-file diff
confirmed ten redundant docstring removals and two docstring/attribute
reorderings. There are no statement, proof, binder, toolchain, or dependency
changes. The manifest now pins that published repair and additionally pins
`SurplusCOMPGBank.lean` at blob `99c520da9308497f5064d8bea639cb408d46e41b`.
No local patch is applied to upstream. The retained original-pin receipt does
not verify the repaired pin; a fresh complete run remains required.

The local review also repaired POSIX subprocess cleanup: timeout and Python
interruption now stop any remaining workers even when the group leader exits
first. Both new regression controls failed before the fix and pass afterward.
These process-lifecycle tests are separate from Lean verification.
