# External removable-vertex frontier audit (2026-07-18)

Status: `EXTERNAL_PROVENANCE_AUDIT_ONLY` and `BRIDGE_ROADMAP_ONLY`.

This note does not prove Erdos Problem #97, prove an `n=9` case, or change a
local result. It records a reproducible source-level audit of an external
formalization and refines the next research target.

## Audited source

Repository:
[`mysticflounder/erdos-97-96-formalization`](https://github.com/mysticflounder/erdos-97-96-formalization)

```text
commit  5e43baeb6fb5f5c51745e05696a7f1b29bf52b0a
source  lean/Erdos9796Proof/P97/U1LargeCapRouteBTail.lean
LF-SHA256  03478c4ba4bd2b5019ea047b96748c333408d487857bdcc227ba5ae534227e48
README LF-SHA256  6625641332bdb1d18ba11459158ee77951e7d50fc7a575c735a94974a8a10004
```

The digests are computed after normalizing checkout CRLF line endings to LF,
matching the canonical Git blob bytes on both Windows and POSIX checkouts.

Run:

```bash
python scripts/audit_external_removable_vertex_frontier.py \
  PATH/TO/erdos-97-96-formalization --assert-expected --json
```

The checker strips Lean comments and strings, groups direct source-level
`sorry` tokens by declaration, checks the expected names, pins the commit and
file digests, and compares source counts with the README. It does not build
Lean, inspect transitive axioms, validate theorem statements, or certify the
external mathematics.

## Reproduced frontier

The pinned tail has 12 directly open declarations and 32 textual holes:

| Family | Declarations | Holes | Role |
|---|---:|---:|---|
| Legacy K-A endpoint | 1 | 1 | Shared-radius compatibility endpoint |
| LIVE-Q | 4 | 24 | Six quantitative inputs in each branch |
| LIVE-C | 7 | 7 | One contradiction per center/source case |
| Total | 12 | 32 | Source-level count only |

The live route seeks a direct contradiction from
`FrontierLargeOppositeCapsBiApexRobustResidual`. The legacy
`DoubleApexOffSurplusSharedRadiusPair` is still open, but no longer describes
the whole frontier.

## Cross-repository bridge map

| External object | Local analogue | Information absent locally |
|---|---|---|
| Four equal distances at every center | 4-bad selected rows | Full radius classes |
| No removable vertex | Minimality/deletion obstruction | More than a necessary deletion witness |
| Source-indexed critical-shell system | Witness map and fragile rows | Common-source shell geometry |
| Opposite MEC caps and surplus cap | No complete analogue | Enclosing-circle geometry |
| Exact classes at two apices | Row-circle constraints | Metric equality beyond incidence overlap |

The local fragile-cover bridge is necessary but cannot replace these retained
geometric hypotheses.

## Negative controls

Three weaker targets are already falsified at their intended local scope.

1. A large cap need not contain an abstractly uncovered vertex. An exact
   rational 11-point `(5,5,4)` incidence model has an exact-four shell through
   every point while the uncovered-cap conclusion fails. It omits the full
   global geometry, so it is not a counterexample.

2. Critical-system provenance does not need restoration. The live object
   `LiveDangerousRetainingSystem` already retains one common source-indexed
   system.

3. One prescribed critical row need not provide two common-cap support points.
   Exact incidence shadows give zero or one such point. An exact seven-point
   local `Q(sqrt(3))` gadget also has two radius-four classes intersecting once.
   These models omit global K4, cardinality, MEC, or the common system.

Pure linear Kalmanson quotient information is also insufficient. A useful new
ingredient must use nonlinear metric geometry or a consequence of the retained
global system.

## Refined next target

The subsequent exact-five parent assembler sharpens this general direction to
a choice-free first-apex co-radial occurrence. The pinned contract and an exact
four-hit reduction are recorded in
`external-exact-five-occurrence-contract-2026-07-18.md`.

The best next path is a **source-flexible, retained-geometry descent lemma**:

> Under global four-equal-distance data, no removability, opposite MEC cap
> geometry, and one common source-indexed critical-shell system, either the full
> live data is contradictory or some critical source row supplies the required
> dangerous common-cap support. The source may depend on the configuration.

This is conjectural, not a theorem. Fixed-row versions have exact negative
controls. Acceptable outcomes are either an exact proof from all retained
hypotheses or an exact target-faithful Euclidean countermodel satisfying global
K4, strict convexity, no removability, MEC/cap geometry, and the common system.
An incidence SAT model, numerical near-miss, or timeout is not a verdict.

Recommended order:

1. Freeze one minimal full-hypothesis statement from the live data.
2. Let the critical source vary.
3. Seek a system-wide cap-excess or radius-order descent invariant.
4. Test it against the local block-6 family and external exact controls.
5. Formalize only the smallest surviving geometric lemma.

Local controls:

```bash
python scripts/check_fragile_hypergraph.py --blocks 2 --assert-ok --json
python scripts/check_bridge_negative_controls.py --assert-expected
```

The external repository is mutable. Re-run the audit against a fresh checkout.
A mismatch means "re-audit the frontier," not "the proof is better or worse."
