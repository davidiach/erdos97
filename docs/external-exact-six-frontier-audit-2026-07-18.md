# External exact-six frontier audit (2026-07-18)

Status: `EXTERNAL_PROVENANCE_AND_STATUS_AUDIT_ONLY` and
`INDEPENDENT_EXTERNAL_ARTIFACT_REPLAY`.

This packet rebases the external formalization intake after sixteen upstream
commits. It does not prove the mutual exact-six branch, Erdos Problem #97, or
any new finite case.

## Pinned snapshot

Repository:
[`mysticflounder/erdos-97-96-formalization`](https://github.com/mysticflounder/erdos-97-96-formalization)

```text
commit  b6f8af856dd1d44ba9e11ea43033d14e3f214f9e
```

Run the local provenance/status audit with:

```bash
python scripts/audit_external_exact_six_frontier.py \
  PATH/TO/erdos-97-96-formalization --assert-expected --json
```

The audit normalizes CRLF to LF before hashing, so a Windows checkout matches
the committed text without weakening content checks.

## What changed

The external theorem
`false_of_fullParentExactFiveAllReverseData_of_secondCap_card_eq_six` is now
present in production source. It closes the all-reverse half of the exact-six
slice. The companion dispatcher makes the remaining obligation explicit:

```text
FullParentExactFiveMutualData L profile -> False
```

This audit checked the source digest and theorem markers. A local Lean build
was not independently rerun because neither the Windows environment nor the
available Ubuntu environment exposes `lake`. Therefore the packet does not
claim an independent Lean build.

The mutual branch remains open. The current card-14 abstraction has seven
distinguished role orbits:

```text
continuationOrder
reverseContinuationOrder
sharesFirstAtSource
sharesFirstAtTarget
sharesSecondAtSource
sharesSecondAtTarget
fourDistinct
```

All seven direct exact-SMT runs ended `UNKNOWN` by timeout. There is no saved
ALIVE sidecar and no UNSAT proof.

## Independently replayed artifacts

The following checks were rerun from a blob-faithful LF checkout:

```text
minimized metric schemas                    263
compact schemas with at most eight roles     30
all minimized cores exact-LRA UNSAT          yes
every single-core deletion exact-LRA SAT     yes

cross-bank weighted cuts                  12509
shell-conditioned cuts                      302
exact vector replays passed               12509
verified ALIVE witnesses                      0

direct exact-SMT role orbits                   7
SAT results                                    0
UNSAT proof packages                           0
UNKNOWN results                                7
```

The upstream minimized-schema verifier has a Windows-only path-key mismatch:
it stores source keys with `str(Path)` but the artifact provenance uses POSIX
paths. The replay used an in-memory one-line normalization to
`Path.as_posix()`. No certificate, source hash, core, or solver assertion was
changed. The 12,509-cut verifier ran unmodified.

These replays establish the exact local arithmetic of the stored cuts and the
integrity/status of the direct portfolio. They do not establish structural
coverage, Euclidean realizability, MEC geometry, or correspondence with the
full Lean parent.

## Retired route

The earlier six-slot partition result remains exact:

> Four reverse-pair endpoint slots in one first-apex radius class force a
> complete co-radial reverse pair, and three do not.

It is no longer the primary research route. The production exact-six
all-reverse branch has a direct cap-order proof, while a separate exact-seven
finite abstraction preserves the current incidence, radius-color, and
abstract-minimality data without producing a co-radial reverse pair. Thus the
proposed equal-radius escape argument cannot be justified from those layers
alone.

## Next proof-facing target

The best remaining route is the aggregate all-center Kalmanson question on the
mutual exact-six surface. Its proof-ready form asks for a nonzero nonnegative
combination of strict Kalmanson vectors whose boundary lies in the span of the
four-point row equalities. Ordinary directed strong connectivity is too weak:
32 of the 263 minimized cores require branching and recombination rather than
an ordinal cycle.

The missing combinatorial object is an oriented contour on the triangular
distance grid, including the seam of its unordered-pair Mobius strip. A valid
uniform theorem must orient row-fiber paths into a nonzero cycle with a
nonnegative cell filling. The exact bare all-center decision is externally
UNSAT through `n = 10` but `UNKNOWN` from `n = 11` onward under the recorded
budget, so this remains a conjectural route rather than a theorem.

Two outcomes are acceptable:

- a uniform aggregate Kalmanson theorem with a kernel-checkable weighted-cut
  consumer; or
- checked finite coverage of all seven source-mapped card-14 orbits, followed
  by a proved lift to the live parent.

If an independently replayed exact ALIVE table appears, the route changes:
apply common planar rank-two/Cayley-Menger constraints, then MEC, full-fiber
provenance, minimality, and global non-`IsM44`. Do not add another broad round
of literal schemas or anonymous local rows.

## Status boundary

No general proof or counterexample is claimed. The official/global problem
status remains open unless manually rechecked from the official source. The
repo-local machine-checked result remains `n <= 8`.
