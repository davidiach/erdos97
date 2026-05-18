# GPT Pro Follow-Up Triage, 2026-05-19

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the two GPT Pro outputs supplied on 2026-05-19. It does not
promote any finite-case result, alter the source-of-truth status, or replace
the checked repository artifacts. The repository still claims no general proof
and no counterexample for Erdos Problem #97.

## Decision

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this batch.

Useful material to keep:

- the ellipse Vieta obstruction as a standalone restricted lemma;
- the parabolic Vieta descent as corroborating provenance for the already
  imported parabola model case.

## Ellipse Note

The first output contains a useful new obstruction:

```text
No finite point set on a Euclidean ellipse can be a counterexample.
```

The proof is exact and independent of the repository's incidence enumeration,
Kalmanson certificates, vertex-circle machinery, and base-apex diagnostics.
The imported version is `docs/ellipse-model-case.md`.

Triage: valid restricted lemma / failed search family. It rules out a natural
construction family, including distorted regular polygons that still lie on one
Euclidean ellipse. It is not a proof of Erdos Problem #97 and not evidence for
an arbitrary-polygon bridge.

## Parabola Notes

The parabolic descent argument in the supplied outputs appears consistent with
the existing conclusion:

```text
No finite point set on a nondegenerate affine parabola can be a counterexample.
```

The repository keeps `docs/parabola-model-case.md` as the proof-facing version
because the endpoint-quartic proof is shorter and covers the affine parabola
parameterization directly. The Vieta/moment proof is useful as an independent
way to recognize the same obstruction, but it is not imported as a duplicate
proof note.

## Material Not Imported

Do not import broad "conic-based" wording as a theorem. This batch covers
circles, Euclidean ellipses, and affine parabolas only; it does not prove a
statement about arbitrary conics or arbitrary strictly convex polygons.

Do not import or promote formulations that suggest a general polygon can be
reduced to the elliptical or parabolic cases by affine or projective
transformations. Such maps do not preserve Euclidean centered equal-distance
relations.

This pass also does not update the official-status timestamp. Recheck the
official Erdos Problems page separately before any source-of-truth status
metadata update.
