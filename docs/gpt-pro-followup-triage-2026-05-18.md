# GPT Pro Follow-Up Triage, 2026-05-18

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the GPT Pro output batch supplied on 2026-05-18. It does not
promote any finite-case result, alter the source-of-truth status, or replace
the checked repository artifacts. The repository still claims no general proof
and no counterexample for Erdos Problem #97.

## Decision

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this batch.

Useful material to keep:

- the compact `n=9` recheck as corroborating audit evidence for the existing
  review-pending vertex-circle checker counts;
- the parabola model-case theorem as a standalone restricted lemma;
- the reminder that the next useful `n=9` artifact is a compact replay
  certificate for the 184 terminal assignments.

## `n=9` Recheck

The supplied dependency-free recheck reproduced the existing repository counts
for the review-pending exhaustive `n=9` vertex-circle checker:

```text
main search with vertex-circle pruning:
  row0 choices: 70
  nodes visited: 16752
  full assignments: 0
  partial self-edge prunes: 11271
  partial strict-cycle prunes: 11011

cross-check without vertex-circle pruning:
  row0 choices: 70
  nodes visited: 100817
  full assignments before terminal replay: 184
  terminal self-edge obstructions: 158
  terminal strict-cycle obstructions: 26
```

These counts match `scripts/check_n9_vertex_circle_exhaustive.py
--assert-expected --json`.

Triage: useful as an independent audit signal, but not a new proof object. The
script duplicates the current search logic at a compact scale; it does not
store the 184 terminal assignments, self-edge paths, or strict-cycle
certificates as replayable input data. Keep the `n=9` claim review-pending.

Recommended next artifact: a small certificate/replay format that treats the
184 post-incidence frontier assignments as input and stores, for each
assignment, a minimal selected-distance equality chain plus a self-edge or
directed strict cycle.

## Parabola Notes

Several files in the batch gave variants of a parabolic no-go theorem. The
cleanest formulation is now recorded in `docs/parabola-model-case.md`:

```text
A finite point set on a nondegenerate affine parabola has an endpoint vertex
with at most three other points at any positive Euclidean distance.
```

The endpoint proof is preferable to the longer Vieta/moment variants because it
is shorter and covers the affine parabola parameterization directly: a positive
radius equation at an endpoint is quartic, and one root is forced outside the
finite parameter interval, leaving at most three available vertex parameters.

Triage: valid restricted lemma / failed search family. It is not a proof of
Erdos Problem #97 and not evidence for an arbitrary-polygon bridge.

## Material Not Imported

The duplicate narrative result notes are not imported. Their useful content is
covered by the two entries above.

Do not import or promote formulations that suggest a general polygon can be
reduced to the parabolic case by affine or projective transformations. Such
maps do not preserve Euclidean centered equal-distance relations.

Do not import the `n=9` recheck as a replacement for the existing
review-pending checker. It is best used as corroborating provenance until a
replayable terminal-certificate artifact exists.
