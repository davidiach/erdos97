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
- the two-parabola lens closure system as a structured future-search scaffold,
  not as evidence for a counterexample.

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

## Two-Parabola Lens Scaffold

A later output proposes a new structured search family using two opposite
parabolic chains

```text
L_a = (a, a^2),
U_b = (b, H - b^2).
```

The imported note is `docs/two-parabola-lens-closure.md`. It keeps only the
exact closure equations for the narrow ansatz where every lower center uses
four upper witnesses and every upper center uses four lower witnesses. For
`c = 1 - 2H`, a lower row selected by `a` must choose a 4-subset `Q_a` of upper
parameters satisfying

```text
sum(Q_a) = 0,
sum pairwise products in Q_a = c + 2a^2,
sum triple products in Q_a = 2a.
```

The upper rows obey the symmetric equations. This is useful because the
one-parabola square-sum descent becomes

```text
sum(q^2 for q in Q_a) = -2c - 4a^2,
```

which is not immediately contradictory when `c < 0`.

Triage: keep as a search scaffold only. It does not produce finite sets
`A,B`, does not verify strict convexity of a lens, and does not cover mixed
witness classes inside a two-parabola point set.

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

Another later output extracts a more concrete search scaffold from the
Barany--Roldan-Pensado construction: their proof of Theorem 1.1 starts with
`A1=(1000,0)`, `A2=(906,114)`, `A3=(645,359)`, `A4=(-498,871)`, applies
rotations by `2*pi/3` and `4*pi/3`, and adds a fifth point by Lemma 3.1 before
rotating again to form the 15-gon. This is worth keeping as a future
continuous-to-discrete search template, where edge parameters would satisfy
exact quadratic distance equations. It is still not imported as a
counterexample direction with evidence, because no finite invariant vertex set
or perturbation certificate is supplied.

The same source identifies the relevant chains more concretely: a neighbourhood
of `A4B1B2B3` supplies centers whose circles hit `C1C2C3C4` at least six times,
while the `A5` insertion handles centers on `[A3,A4]` outside that
neighbourhood via hits on `A3A4A5B1` plus two further boundary hits. These
chain names may be useful for a future edge-parameter closure model, but they
do not change the finite-vertex evidence level.

## Material Not Imported

Do not import broad "conic-based" wording as a theorem. This batch covers
circles, Euclidean ellipses, and affine parabolas only; it does not prove a
statement about arbitrary conics or arbitrary strictly convex polygons.

Do not import or promote formulations that suggest a general polygon can be
reduced to the elliptical or parabolic cases by affine or projective
transformations. Such maps do not preserve Euclidean centered equal-distance
relations.

Do not promote the two-parabola lens closure system to a counterexample route
with evidence unless it comes with exact finite sets, selected 4-subsets,
equal-distance verification, and a strict-convexity certificate.

This pass also does not update the official-status timestamp. Recheck the
official Erdos Problems page separately before any source-of-truth status
metadata update.
