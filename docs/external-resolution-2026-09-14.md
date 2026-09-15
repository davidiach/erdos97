# External negative resolution - 14 September 2026

Status: `EXTERNAL_NEGATIVE_RESOLUTION`. This is an attribution and status record,
not an original-discovery claim or an independent local Lean replay receipt.

## Result and attribution

**Liam Kruer, Jensen Kohlmeyer, and Liam Price**, *Unit distances in convex
polygons*, released 13 September 2026, provide the negative answer to the
unrestricted question. Their result includes a nonempty finite set
\(Q\subset\mathbb R^2\) in strictly convex position satisfying

\[
\forall p\in Q,\qquad
\#\{q\in Q:\|q-p\|=1\}\ge4.
\]

The distance is one at every vertex, so this meets the variable-radius target
with a common radius. Positive distance excludes the center, and cardinality
counts distinct witnesses. The minimum degree also precludes a degenerate
one- or two-point reading of the polygon condition.

Credit for the construction and its formalization belongs to the named authors.
This repository's earlier work is not presented as the source of their result.
No journal acceptance, DOI, arXiv identifier, or current canonical-website label
is asserted here.

## Pinned primary sources

The source revision is `0e98f5f9bdaf36007e3eb405cbefe2eda778a9b2` in
`Leeham06972452/erdos-96-97`.

- [Manuscript source](https://github.com/Leeham06972452/erdos-96-97/blob/0e98f5f9bdaf36007e3eb405cbefe2eda778a9b2/96-97.tex), Git blob `0fbcae0f51013559a6d1d4a842ec55ecc64719fe`.
- [Complete Lean source](https://github.com/Leeham06972452/erdos-96-97/blob/0e98f5f9bdaf36007e3eb405cbefe2eda778a9b2/Erdos9697Complete.lean), Git blob `95e01ec7efe395b7895f7495453e495a89c5b4c0`.
- [Authors' overview and verification instructions](https://github.com/Leeham06972452/erdos-96-97/blob/0e98f5f9bdaf36007e3eb405cbefe2eda778a9b2/README.md).

Relevant formal endpoints are `Proof.explicit_erdos_97_counterexample` and
`Proof.erdos_97_false`. The authors' stated upper bound is
`3432 * 2^36036` vertices. This is a finite existence bound using a generic
parameter argument, not an explicit coordinate list or a minimum-size claim.
No smaller bound from an informal local deduction is promoted by this update.

## Why the result addresses the original target

The manuscript's finite construction, with parameters `d=7` and `q=8`, has
`N = 3432 * 8^12012 = 3432 * 2^36036` points in strictly convex position and
at least `(49/16) * N > 3N` unordered unit-distance pairs.

Repeatedly delete any vertex with at most three remaining unit-distance
neighbours. If all vertices disappeared, each original edge would be charged
once, at the deletion of its first endpoint, for at most `3N` edges in total.
The strict inequality rules this out. A nonempty subgraph of minimum degree
at least four survives. Strict convex position is inherited by subsets.

The hard ingredient is the authors' exact dense geometric construction; the
peeling argument does not establish it independently. Both the construction
and its use belong to the cited external work. Their broader results also
address Problem 96 and unbounded fixed minimum unit-distance degree, but no
new proof of those results is supplied by this documentation update.

## Verification boundary

The manuscript/Lean source identities and author attribution were checked via
the connected GitHub service. The first upstream workflow
[run 34759460533](https://github.com/Leeham06972452/erdos-96-97/actions/runs/34759460533),
job `103729567616`, reports success; its job steps were checked on
14 September 2026. The preceding in-session audit inspected the original
compilation log and distinguished it from a later cached replay. This status
record does not treat repeated green or cached runs as independent verification.

The authors pin Lean `v4.33.1` and Mathlib
`0df444a360eaa60ab8c11dca51a86af692955474`. Their source-level axiom gate allows
only `propext`, `Classical.choice`, and `Quot.sound`, excluding `sorryAx`.
Upstream compilation and its disclosed dependency cache are not a fresh local
build of all dependencies or an independent second-kernel audit.

**No independent local Lean replay or independent mathematical acceptance
record is claimed by this repository update.** The editing environment lacks
`lean`/`lake`, and direct shell GitHub access failed DNS resolution. The existing
accepted local claims, pending reviews, and trust checks remain unchanged.
No active `metadata/status_transition.json` is introduced.

## Canonical website versus mathematical outcome

The canonical page could not be retrieved on 14 September 2026. Accordingly,
`metadata/erdos97.yaml` retains its last successfully checked website label,
`falsifiable/open`, and the date `2026-07-09`. That historical website record
is not the current mathematical outcome and is not a fresh status check.

The new [external metadata](../metadata/external-resolution-2026-09-14.json)
records the separately sourced external result and the unsuccessful refresh.
Keeping these records separate avoids both fabricating a website update and
silently promoting an external report to an independently accepted local result.

## Consequences for this repository

The unrestricted affirmative research objective and its automatic task queues
are retired. Existing small-case proofs, exact obstructions, partial
constructions, negative controls, failed approaches, and review records remain
at their published paths. Earlier open-status statements are historical context.
A negative global outcome does not automatically invalidate a correctly scoped
local theorem or validate an unreviewed one.

The live n=9 diagnostic generators date their canonical-website notes to the
2026-07-09 check and link the separate external record. Their regenerated JSON
keeps the same mathematical payload and review status. The n=8 release packet
remains a reproducible historical snapshot at its recorded source revision;
its dated website wording is not a current-status report.

This update does not delete code or artifacts, close issues, change repository
archival settings, or weaken verification requirements. Independent reproduction,
smaller explicit examples, or other research may be selected later, but this
record does not authorize or launch those projects.

## Reproduction reference, not a completed local run

In a separate network-enabled checkout of the upstream repository:

```sh
git checkout --detach 0e98f5f9bdaf36007e3eb405cbefe2eda778a9b2
lake env lean --version
lake exe cache get
lake build
lake env lean Erdos9697Complete.lean
```

Preserve the pinned toolchain and dependency lock. A direct elaboration and the
actual axiom output must be inspected; a cached badge or unrelated zero exit
code is insufficient. Local acceptance remains subject to the existing
[reviewed transition contract](status-transitions.md).
