# GPT Pro Follow-Up Triage, 2026-05-19

Status: provenance and task-selection guidance only; not mathematical
evidence.

This note triages the GPT Pro outputs supplied on 2026-05-19. It does not
promote any finite-case result, alter the source-of-truth status, or replace
the checked repository artifacts. The repository still claims no general proof
and no counterexample for Erdos Problem #97.

## Decision

Do not update `README.md`, `STATE.md`, `RESULTS.md`, or
`metadata/erdos97.yaml` from this batch.

Useful material to keep:

- the ellipse Vieta obstruction as a standalone restricted lemma;
- the parabolic Vieta descent as corroborating provenance for the already
  imported parabola model case;
- the 3-fold pair-lift obstruction as a standalone failed search mechanism;
- the two-ring dihedral obstruction as duplicate provenance for the already
  recorded alternating two-radius regular-family obstruction;
- the closest-pair radius barrier as a standalone structural lemma;
- the convex-body boundary warning from Barany--Roldan-Pensado as literature
  risk, not as a finite-vertex counterexample route.

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

## Threefold Pair-Lift Note

One output gives a useful obstruction for a natural Danzer-style lift
mechanism. The imported note is `docs/threefold-pair-lift-obstruction.md`.

The mechanism assumes each point in a full 3-fold orbit uses its two same-orbit
mates as witnesses, so the selected radius is forced. If one other full 3-fold
orbit supplies the remaining two witnesses as an equidistant pair, then that
partner orbit must have the opposite phase and exactly twice the radius.
Following these forced radius doublings around a finite orbit-dependency cycle
is impossible.

Triage: valid narrow obstruction / failed search mechanism. It does not rule
out all 3-fold symmetric configurations, because the extra witnesses could
come from two different orbits, from a different selected radius, or from a
non-full-orbit construction.

## Closest-Pair Barrier

One output includes a useful exact lemma now recorded in
`docs/closest-pair-radius-barrier.md`:

```text
An endpoint of a globally closest pair cannot have four other vertices at the
globally closest distance.
```

The proof uses only the strict hull-vertex cone and the fact that four points
on a circle of radius `delta` with all mutual distances at least `delta` need
three angular gaps of size at least `pi/3`.

Triage: valid structural necessary condition. It does not prove Erdos #97, but
it separates closest-pair endpoints from minimum-distance four-ties in any
counterexample.

## Two-Ring Dihedral Note

One output gives an exact obstruction for alternating two-radius regular
polygons

```text
A_m = exp(2*pi*i*m/k),
B_m = r*exp((2m+1)*pi*i/k).
```

This is already covered in `docs/two-orbit-radius-propagation.md` under the
broader alternating two-radius family. That note records the same strict
convexity interval `cos(h) < b < sec(h)` and the endpoint-certificate
interlacing

```text
D_1 < D_2 < ... < D_{m-1}
```

throughout that interval, so each vertex has no four equal-distance neighbors
inside this ansatz.

Triage: useful corroboration, but not imported as a duplicate theorem. The
existing two-orbit note is the proof-facing source for this killed family.

## Continuous-Body Warning

One follow-up output points to Barany--Roldan-Pensado,
`A Question from a Famous Paper of Erdos`, Discrete & Computational Geometry
50, 253--261 (2013), DOI `10.1007/s00454-013-9507-z`. Their abstract states
that some convex bodies have `N(K)=6`, where `N(K)` is the least number such
that some boundary point has every centered circle meet the boundary in at
most that many points; the introduction records that their example is a
15-gon.

This is useful as a warning but not as an Erdos #97 counterexample. The
intersections are with the boundary of a convex body and may lie in edge
interiors, while Erdos #97 is about distances from a polygon vertex to other
vertices. A future construction attempt could try to discretize such a
boundary-intersection example, but this output does not provide a finite
selected-vertex closure or an exact certificate.

A later output also points to the acute-triangle failure of the older `N=2`
boundary-intersection conjecture. This belongs in the same warning bucket:
it shows that boundary-intersection richness is much easier than a finite
selected-vertex counterexample, not that Erdos #97 has a counterexample.

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
