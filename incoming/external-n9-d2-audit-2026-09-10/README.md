# External general-n9 and D2 audit

Status: `AUDIT_PREPARED / REVIEW_PENDING / NO_ACCEPTED_CLAIM_CHANGE`.
This packet is a reproducible audit interface, not a new proof or counterexample
to unrestricted Erdos #97. A hosted build and the axiom checks must finish before
a verification receipt can be described as passing. The harness tests use
synthetic compiler output and do not verify the mathematical theorems.

## Provenance and scope

Local base: `982e5a363be60cfd805db5ae40d4b258e53f9dfb`.

External project: `mysticflounder/erdos-97-96-formalization`, by Adam McKenna.
Pinned source: `76559d59f934d81e5081b40e0e621b39f759f7fa`.
Upstream toolchain: `leanprover/lean4:v4.33.1`.
The local pilot remains on its existing toolchain and gains no Lake dependency.
This pin is the immediate successor of the original audited source. Its five-file
diff only removes or repositions declaration documentation; the statements,
proofs, toolchain, and dependency lock are unchanged. The original failed
execution remains recorded in [EXECUTION.md](EXECUTION.md).

[manifest.json](manifest.json) is the machine-readable target and source-pin
roster. Upstream proof bodies are not copied into this packet. The initial
source review inspected the pinned definitions and proof consumers; it is not
an independent rebuild receipt.

| Group | Audited consumers | Exact scope |
|---|---|---|
| n9 | `Problem97.FiniteN9Closure`, `counterexample_card_ge_ten`, and two local statement adapters | General convex-independent planar sets, including different positive radii at different centers; no equilateral or symmetry assumption |
| D2 | `ATailTwoRadiusGridNestedEscapeTerminal.false_of_nestedEscape_packet` and `false_of_twoRadiusGrid_zeroCut_nestedEscape` | The named, conditional nested-escape terminals only; every reflection, radius, ordering, and packet hypothesis is retained |

`N9Audit.lean` independently states the n=9 and nonempty n<=9 claims using
mathlib vocabulary, then asks the external proofs to discharge them. In
particular, the radius existential is **inside** the quantifier over centers.
A positive radius excludes counting the center itself.

`D2Audit.lean` prints the two exact external signatures and audits their
transitive axiom closures. It does **not** provide a mathlib-only restatement
of their geometry predicates or prove that an arbitrary local configuration
produces the required packet. That distinction is recorded in the manifest.

## D2 hypothesis map

The reusable named-points theorem is independent of the source-selection
machinery. It assumes a nondegenerate axis `(o,a)`, reflection identities for
`(s,sMinus)` and `(L,LMinus)`, a shared scaled squared norm for `s` and `t`,
and one of two explicitly signed nesting/orientation packets.

The stronger geometric wrapper has additional `CounterexampleData` and
`SurplusCapPacket` inputs. These carry their own geometric and all-richness
assumptions; they must not be silently removed. In that wrapper:

| External role or hypothesis | Required meaning |
|---|---|
| `o = S.oppApex1`, with `o != a` | The chosen physical apex and distinct blocker define the coordinate axis |
| `s`, `L` | Both lie in `S.capInteriorByIndex S.oppIndex1` |
| `sMinus` | Lies in the designated left-adjacent cap |
| `t` | Lies in the designated right-adjacent cap |
| `LMinus` | Belongs to the carrier, but is outside the designated cap interior |
| Two reflection identities | Equal longitudinal coordinates and opposite transverse coordinates for each pair |
| `hsO`, `hsA`, `hLO`, `hLA` | Both reflection pairs have the stated equal distances from the apex and blocker |
| `hRadius` | `dist o s < dist o L`; the physical radii are strictly ordered |
| `hCommonBlocker` | `dist a s = dist a L` |
| `hNorm` | `t` has the smaller pair's scaled squared norm |
| Named inequalities | All distinctness hypotheses in the external signature remain required |

The geometric assembly must produce the signed nesting and orientation packet;
a picture or an abstract incidence grid is not a substitute. The final algebra
uses the norm equality together with strict sign information. This audit does
not identify the D2 packet with the unresolved transverse D1 configuration.

The historical local entry point is
[the August 6 frontier note](../../docs/conversation-frontier-and-failed-routes-2026-08-06.md).
That dated note is retained unchanged. This packet records an external successor
candidate for its grid-formalization task, not a retroactive change to the
historical note or a proof that all of its unresolved cases are covered.

## What a passing receipt establishes

The audit checks the full upstream commit, selected Git blob identities, clean
source state, the exact toolchain version, and every materialized Git dependency
against the committed Lake manifest. It refuses pre-existing project proof
outputs; upstream dependency caches are allowed and explicitly part of the
build environment. No `lake update` is run.

It builds the two target modules separately, compiles the harnesses, and
requires exactly one complete axiom report for every named declaration. The
only permitted axioms are `propext`, `Classical.choice`, and `Quot.sound`.
Missing, duplicate, malformed, unexpected, `sorryAx`, custom-axiom, and
compiler-trusted reports fail closed. The source and dependency pins are checked
again after the build. Logs and harnesses receive SHA-256 identifiers in the
receipt, and an existing evidence directory cannot be silently reused.
Both harnesses are hashed before any external command runs and checked before
use and after all commands. The manifest must retain all six named declarations.
Complete report lines are required; trailing malformed text is not accepted.

An interim `NOT_VERIFIED` receipt is saved before execution and after each
target stage. Cancellation therefore leaves an explicit incomplete record.
Only a completed run with `inputs_rechecked_after_execution: true` can pass.
Each build uses `--timeout` seconds; each consumer has at most 300 seconds.
The hosted run allows 60 minutes per build plus setup and evidence upload.
On POSIX, timeout and Python interruption cleanup also stops workers whose
group leader has already exited, before closing the shared command log.

`CORE_AXIOM_AUDIT_PASSED` means that these particular consumers compiled and
met that axiom budget in the recorded run. It does not mean a full-project
comparator run, an independent second-kernel replay, an informal mathematical
review, or an accepted local status transition. No such replay is performed by
this harness. A module build without the subsequent axiom checks is insufficient.

The ten- and eleven-point compiler-trusted endpoints, the unrestricted theorem
root, and the transverse D1 branch are outside this audit. The accepted local
n<=8 frontier and general-n9 review status remain unchanged.

## Reproduce

Use an isolated checkout of the pinned external commit and its own toolchain.
Materialize its locked dependencies and fetch their cache from its `lean/`
directory with `lake exe cache get`. Do not restore or reuse the external
project's `.lake/build` proof outputs. The audit is intentionally outside the
local dependency-free Lean pilot.

From this repository's root:

```bash
PYTHONPATH=src python scripts/audit_external_n9_d2.py \
  --checkout /absolute/path/to/pinned-upstream \
  --packet incoming/external-n9-d2-audit-2026-09-10 \
  --output /absolute/path/to/new-empty-evidence-directory

PYTHONPATH=src python -m pytest -q tests/test_external_lean_audit.py
make verify-fast
make verify-artifacts
```

The hosted workflow is
[external-n9-d2-audit.yml](../../.github/workflows/external-n9-d2-audit.yml).
It uses a fresh runner, does not persist checkout credentials, has read-only
repository permission, pins the external source, and uploads logs even when
verification fails. Bootstrap failures remain non-verification, not a pass.

On Windows, timeout cleanup uses `taskkill /T /F` on the child PID created by
the audit; a restricted process sandbox may deny that operation. Run the audit
where it can manage its own child processes. Failure to clean up is an audit
error, not a verification pass. Lean source and output text use UTF-8.

Observed executions and remaining limitations belong in
[EXECUTION.md](EXECUTION.md). Any stronger accepted claim must follow the
[status-transition contract](../../docs/status-transitions.md).

## Pinned primary sources

- [General n9 assembly](https://github.com/mysticflounder/erdos-97-96-formalization/blob/76559d59f934d81e5081b40e0e621b39f759f7fa/lean/Erdos9796Proof/P97/N9Endpoint/Closure.lean).
- [General small-cardinality consumers](https://github.com/mysticflounder/erdos-97-96-formalization/blob/76559d59f934d81e5081b40e0e621b39f759f7fa/lean/Erdos9796Proof/P97/SmallCardinality.lean).
- [D2 nested-escape terminals and algebra](https://github.com/mysticflounder/erdos-97-96-formalization/blob/76559d59f934d81e5081b40e0e621b39f759f7fa/lean/Erdos9796Proof/P97/ATail/TwoRadiusGridNestedEscapeTerminal.lean).
- [Nesting/orientation assembly](https://github.com/mysticflounder/erdos-97-96-formalization/blob/76559d59f934d81e5081b40e0e621b39f759f7fa/lean/Erdos9796Proof/P97/ATail/TwoRadiusGridZeroCutAssembly.lean).
