# Exact-five first-apex occurrence contract (2026-07-18)

Status: `EXTERNAL_PROVENANCE_AUDIT_ONLY`,
`EXACT_FINITE_COMBINATORIAL_AUDIT`, `BRIDGE_ROADMAP_ONLY`, and
`SUPERSEDED_AS_PRIMARY_RESEARCH_TARGET`.

This packet freezes the then-current external all-reverse theorem contract and
records one exact choice-free reduction. It does not prove the missing
geometric producer, Erdos Problem #97, or any new finite case.
The snapshot below is historical. Upstream commit `b6f8af85` now contains a
production proof of the all-reverse exact-six slice, and later exact finite
work refutes incidence/radius-color data as a sufficient producer for the
analogous exact-seven co-radial occurrence. The four-hit lemma remains true,
but it is no longer the primary research target. See
`external-exact-six-frontier-audit-2026-07-18.md`.


## Pinned external contract

Repository:
[`mysticflounder/erdos-97-96-formalization`](https://github.com/mysticflounder/erdos-97-96-formalization)

```text
commit  5e43baeb6fb5f5c51745e05696a7f1b29bf52b0a

LargeOppositeCapsBiApexSurface.lean
LF-SHA256  f6ad84e10773d6298b775858889a07ebbbf63029306b7d45200cd982d38c593f

FirstApexShellRole.lean
LF-SHA256  ac0212e83499063557c9ccba0de6d33f794f49058cec927a4c2183581df455d6

LargeCapUniqueFivePhysicalOmissionTransitionGlobal.lean
LF-SHA256  d8f855b54355e49766bb11e5ff0864786cdd0770b3adcbfdad713f2f46fbd362

ParentExactFiveAssembler.lean
LF-SHA256  3e7d8bcdebd8a5c4f19cb49db3223eb17b9c3eb3970be544e2db2ba04cf00122
```

All four digests normalize checkout CRLF line endings to LF before hashing,
so the documented replay matches canonical Git blob bytes across platforms.

Reproduce the source audit with:

```bash
python scripts/audit_external_exact_five_contract.py \
  PATH/TO/erdos-97-96-formalization --assert-expected --json
```

This checks commit, digests, and named contract fields. It does not build Lean
or certify the external proof dependency closure.

## Frozen mathematical interface

The parent is
`FrontierLargeOppositeCapsBiApexRobustResidual B`. It retains both opposite-cap
bounds at six. Through its indices it also retains the original critical
frontier, common deletion, minimality, non-`IsM44`, and bi-apex robustness.

On the exact-five all-reverse arm,
`FullParentExactFiveAllReverseData L profile continuation` retains:

- the source-faithful first-apex role packet;
- the global physical omission transition;
- global reverse membership;
- a zero-entry period-three cycle containing both continuation sources;
- the cycle reverse incidences; and
- one shared strict-cap order for all sources and blockers.

For each transition source `q`, `transitionReverseOutsidePair` is an exact
two-point residual outside the physical second cap.

The missing occurrence is:

```text
there exist q and distinct a,b in transitionReverseOutsidePair(q)
such that dist(first apex,a) = dist(first apex,b).
```

The external theorem
`false_of_fullParentExactFiveAllReverseData_of_firstApexOccurrence` already
turns that occurrence into `False`. Thus no additional terminal theorem or
chosen-row normalization is required.

## Choice-free four-hit reduction

Restrict to the three reverse pairs on the period-three cycle. Label their
endpoint slots

```text
(x0,y0), (x1,y1), (x2,y2).
```

Partition the six slots by equality of distance from the first apex. A block
containing both endpoints of one pair is exactly the required co-radial
occurrence.

The exact finite audit enumerates all restricted-growth partitions:

```text
all partitions                         203
partitions with no complete pair        87
largest-class size 1                     1
largest-class size 2                    50
largest-class size 3                    36
largest occurrence-free class size      3
```

Therefore:

> If one complete first-apex radius class hits at least four of the six
> period-three reverse-pair slots, then it contains a complete reverse pair
> and feeds the proved external terminal.

The threshold is sharp for this argument: one class can hit slots
`x0,x1,x2` without containing a complete pair.

Run:

```bash
python scripts/check_period_three_radius_partition.py \
  --assert-expected --json
```

This is an exact finite pigeonhole reduction, not the missing geometric
four-hit producer.

## Why this was the better target at the pinned snapshot

The former sufficient condition placed a whole reverse pair in either of two
preselected first-apex four-rows. Exact marginal fixtures show that choice can
split or omit every reverse pair even when a larger complete radius class
would contain it.

The four-hit formulation instead quantifies over the complete first-apex
radius classes. It is invariant under the choice of selected four-subrow and
matches the external occurrence directly.

At the pinned snapshot, the proposed geometric target was:

```text
For some positive first-apex radius r,
the union of the three cycle reverse outside pairs has at least four
slot hits in SelectedClass(A, first apex, r).
```

Equivalently, under negation of the occurrence, every complete first-apex
radius class hits at most three cycle-pair slots. Current upstream work shows
that forcing the violation from incidence, radius colors, and abstract
minimality is not viable by itself.

## Historical proof split

The first-apex role packet gives the natural proof split.

1. If `doubleRadius = retainedRadius`, a complete first-apex class has at
   least six ambient points and survives deletion of both frontier sources.
   The open task is to force four reverse-pair hits in some complete class;
   membership in either selected four-subrow is unnecessary.

2. If `doubleRadius != retainedRadius`, the retained and double-deletion
   selected supports are disjoint. The open task is to use full CSS/minimality
   and the shared cap order to prevent all three reverse pairs from remaining
   bichromatic across complete first-apex classes.

Pure incidence, selected-row marginals, triangle/Kalmanson inequalities, and
the existing fully disjoint 25-role linear cell do not force this conclusion.
Any successful argument must add nonlinear planar/MEC geometry, full-fiber
critical-system provenance, or global minimality.

## Acceptance gate

Accept either:

- a source-faithful Lean proof of the four-hit producer or the original
  co-radial occurrence from the complete parent packet; or
- an exact Euclidean countermodel satisfying all retained parent, MEC/cap,
  global K4, total critical-system, and minimality hypotheses.

A finite incidence model, linear metric model, numerical near-miss, nonlinear
solver timeout, or bounded no-hit search is not a verdict.
