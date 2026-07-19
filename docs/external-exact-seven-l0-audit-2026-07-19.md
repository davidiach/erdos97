# External exact-seven L0 audit (2026-07-19)

Status: `EXTERNAL_L0_ENUMERATOR_PROVENANCE_AUDIT_ONLY` and
`EXACT_FINITE_SCHEMA_MECHANICS`.

This packet records the current public external frontier after literal
exact-six cut mining was declared nonconvergent under the optimized engine.
It checks the new exact-seven all-fresh L0 enumerator exactly. It does not
establish full exact-seven coverage, replay a public Lean proof of the named
cap normal form, or close any branch of Erdos Problem #97.

## Pinned snapshot

Repository:
[`mysticflounder/erdos-97-96-formalization`](https://github.com/mysticflounder/erdos-97-96-formalization)

```text
commit  b46c14df95b6509240f1083bb16beba30dd780be
```

Run the independent source-and-schema audit with:

```bash
python scripts/audit_external_exact_seven_l0.py \
  PATH/TO/erdos-97-96-formalization --assert-expected --json
```

The audit pins normalized-LF SHA-256 digests for the enumerator, encoder,
fact table, report, smoke fixture/results, and census runner. It executes the
enumerator only after its source matches the pinned digest.

## Exact L0 mechanics

The external L0 layer fixes the named strict-cap chain, up to reflection, as

```text
s0 < b0 < s1 < b1 < s2
```

and enumerates the all-fresh placement of two exact-five extras and the three
reverse-row outside pairs. The extras have eight unordered landing pairs; each
outside pair has five. Therefore the generator has

```text
8 * 5^3 = 1000 schemas.
```

The local checker independently reconstructs every expected schema, including
its point list, symbolic boundary blocks, four complete radius classes,
support exclusions, unique K4 class at `O`, and timeout. Every generated schema
matched that contract, all 1,000 identifiers were distinct, and the compact
canonical JSON digest was

```text
6832099d275e3bc934bb1dff31ffa625824cb8596fe657643db9ba8a1179a256
```

The point-count census is:

| points | schemas |
|---:|---:|
| 11 | 8 |
| 12 | 68 |
| 13 | 222 |
| 14 | 351 |
| 15 | 270 |
| 16 | 81 |

These are exact finite-schema mechanics, not a geometric verdict. L0 omits
identifications between fresh roles, first-apex rows, the unused critical row,
and endpoint blockers. The promised merge refinement and L1 layer have not
been built in the pinned public snapshot.

## Smoke replay

The current fixture contains seven gates, despite its docstring and report
still saying five. A live local replay through the external production encoder
passed all seven:

```text
A_fixed_full       UNSAT
B_named_fixed      SAT
C_symbolic_full    UNSAT
D_named_symbolic   SAT
E_fixed_hingefree  UNSAT
F_named_floating   SAT
G_uniq4_unit       UNSAT
```

The audit pins and checks the committed verdict table. The audit command itself
does not invoke Z3, so its JSON correctly distinguishes the recorded verdict
check from this separate live replay.

## Public source-fidelity gap

The fact table and report cite a Lean theorem named
`Round188ExactSevenNamedInteriorNormalForm.lean`, give an author-local path and
digest, and describe it as proved. That source file is not tracked anywhere in
the pinned public repository. Consequently the cap-chain theorem cannot be
independently source-audited or rebuilt from the public snapshot. The report
is also stale: it says the enumerator is not built and records only five smoke
gates, while the public tree contains the enumerator and seven-gate fixture.

No generated `l0_schemas.json` or terminal census ledger is committed. The
runner is resumable, but its ledger intake only collects completed schema IDs;
it does not reject duplicate or conflicting entries or pin the input-schema
digest. A future verdict-bearing census therefore needs a fail-closed ledger
checker and run manifest in addition to the solver output.

These are reproducibility findings, not evidence that the cited theorem is
false or that any schema verdict is wrong.

## Research decision

The previous aggregate all-center Kalmanson target is no longer the next best
use of effort for this external branch. The current public redirect explicitly
retires further literal exact-six rounds: 737,100 cyclic-dihedral applications
produced only 28 new replayed cuts and neither an exhausted proof nor an ALIVE
witness. Any return to exact-six now needs nonlinear Euclidean/MEC information,
full-fiber provenance, or global minimality rather than more literal cuts.

For exact seven, the next acceptance gate is source fidelity plus coverage:

1. commit the named-interior Lean theorem and make its build reproducible;
2. enumerate and audit the fresh-role coincidence/merge cases;
3. add the L1 first-apex constraints on every L0 SAT survivor; and
4. either close every source-faithful case with checked cores or hand a checked
   SAT survivor to nonlinear Euclidean, MEC, full-fiber, or minimality analysis.

Until those steps exist, an L0 census is only a relaxation census. In
particular, an L0 UNSAT table would not cover omitted coincidence cases, while
an L0 SAT result would not be a counterexample or even a Euclidean realization.

## Status boundary

No general proof or counterexample is claimed. The official/global problem
status remains open unless manually rechecked from the official source. The
repo-local machine-checked result remains `n <= 8`.
